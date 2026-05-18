import os
import json
import logging
import asyncio
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import time
import bcrypt

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import settings
import paper_manager
from pipeline_core import PipelineCore
from ai_core import AICore
from processor.slides_processor import SlidesProcessor

load_dotenv()

def _setup_logging():
    """終端機只顯示 WARNING/ERROR；pipeline 與 chat log 分流寫入檔案。"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(fmt)
    root_logger.addHandler(console)

    def _rotating(filename):
        h = RotatingFileHandler(
            log_dir / filename, maxBytes=10 * 1024 * 1024,
            backupCount=5, encoding='utf-8'
        )
        h.setLevel(logging.DEBUG)
        h.setFormatter(fmt)
        return h

    pipeline_handler = _rotating("pipeline.log")
    for name in ('pipeline_core', 'paper_manager', 'processor'):
        lg = logging.getLogger(name)
        lg.setLevel(logging.DEBUG)
        lg.addHandler(pipeline_handler)

    chat_handler = _rotating("chat.log")
    for name in ('AI_professor_chat', 'ai_core', 'rag_retriever'):
        lg = logging.getLogger(name)
        lg.setLevel(logging.DEBUG)
        lg.addHandler(chat_handler)


_setup_logging()
logger = logging.getLogger(__name__)

# 全域設定
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 全域狀態
ai_core = None
processing_tasks: dict = {}  # paper_id -> {'status': str, 'progress': dict}
tasks_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """啟動時初始化"""
    global ai_core



    ai_core = AICore()
    ai_core.init_rag_retriever(str(OUTPUT_DIR))

    # 載入已有論文的向量庫
    paper_manager.preload_vector_stores(OUTPUT_DIR, ai_core)

    logger.info("Web server 初始化完成")
    yield


app = FastAPI(title="Mad Professor Web API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 登入 / Session ──

if settings.ENVIRONMENT != "production":
    logger.warning("執行於 development 模式，cookie 不強制 HTTPS")
else:
    logger.info("執行於 production 模式")

if not settings.SESSION_SECRET:
    logger.warning("SESSION_SECRET 未設定，使用臨時密鑰（重啟即失效，請於 .env 設定）")
if not settings.AUTH_PASSWORD_HASH:
    logger.warning("AUTH_PASSWORD_HASH 未設定，將無法登入（請用 scripts/generate_password_hash.py 產生）")

_login_attempts: dict = {}  # ip -> [失敗時間戳]
_login_lock = threading.Lock()

_PUBLIC_PREFIXES = ("/static/login",)
_PUBLIC_PATHS = {"/login", "/logout", "/api/health"}


def _is_public(path: str) -> bool:
    if path in _PUBLIC_PATHS:
        return True
    return any(path.startswith(p) for p in _PUBLIC_PREFIXES)


@app.middleware("http")
async def auth_guard(request: Request, call_next):
    path = request.url.path
    if _is_public(path) or request.session.get("auth"):
        return await call_next(request)
    # 未登入：API/SSE 回 401 JSON，其餘導向登入頁
    if path.startswith("/api/"):
        return JSONResponse(status_code=401, content={"error": "未登入"})
    return RedirectResponse(url="/login", status_code=302)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET or "insecure-dev-secret-change-me",
    session_cookie="session",
    https_only=(settings.ENVIRONMENT == "production"),
    same_site="strict",
    max_age=None,
)


@app.get("/login")
async def login_page():
    p = BASE_DIR / "static" / "login.html"
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>login.html not found</h1>", status_code=500)


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    with _login_lock:
        fails = [t for t in _login_attempts.get(ip, []) if now - t < 60]
        _login_attempts[ip] = fails
        if len(fails) >= 5:
            return RedirectResponse(url="/login?error=locked", status_code=303)

    ok = False
    if settings.AUTH_PASSWORD_HASH and username == settings.AUTH_USERNAME:
        try:
            ok = bcrypt.checkpw(
                password.encode("utf-8"),
                settings.AUTH_PASSWORD_HASH.encode("utf-8"),
            )
        except Exception as e:
            logger.warning(f"密碼驗證失敗: {str(e)}")
            ok = False

    if ok:
        with _login_lock:
            _login_attempts.pop(ip, None)
        request.session["auth"] = True
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=303)

    with _login_lock:
        _login_attempts.setdefault(ip, []).append(now)
    return RedirectResponse(url="/login?error=invalid", status_code=303)


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/")
async def root():
    html_path = BASE_DIR / "static" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding='utf-8'))
    return HTMLResponse("<h1>Frontend not found</h1>")

# ── 資料模型 ──

class ChatRequest(BaseModel):
    query: str
    paper_id: Optional[str] = None
    visible_content: Optional[str] = None


# ── 論文列表 ──

@app.get("/api/papers")
async def list_papers():
    """取得所有論文列表"""
    return paper_manager.load_papers_index(OUTPUT_DIR)


# ── 論文上傳 ──

@app.post("/api/papers/upload")
async def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """上傳 PDF 並開始處理"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只接受 PDF 檔案")

    content = await file.read()

    # 檔案大小上限 100 MB
    if len(content) > 100 * 1024 * 1024:
        return JSONResponse(status_code=413, content={"error": "檔案大小超過 100 MB 上限"})

    # PDF magic bytes 驗證（副檔名檢查之後）
    if content[:4] != b'%PDF':
        return JSONResponse(status_code=415, content={"error": "僅支援 PDF 格式"})

    paper_id = paper_manager.sanitize_paper_id(file.filename)
    paper_dir = OUTPUT_DIR / paper_id
    paper_dir.mkdir(exist_ok=True)
    pdf_path = paper_dir / "original.pdf"

    # 儲存上傳的 PDF
    with open(pdf_path, 'wb') as f:
        f.write(content)

    # 偵測是否為簡報，供前端預選文件類型（不阻塞事件迴圈）
    try:
        loop = asyncio.get_event_loop()
        suggested = await loop.run_in_executor(
            None, SlidesProcessor.is_slides_pdf, str(pdf_path)
        )
        suggested_doc_type = 'slides' if suggested else 'academic'
    except Exception:
        suggested_doc_type = 'academic'

    # 上傳完成，立即等待使用者選擇文件類型
    with tasks_lock:
        processing_tasks[paper_id] = {
            'status': 'waiting_confirm',
            'progress': {'stage': 'upload', 'stage_name': '上傳完成', 'index': 0, 'total': 10, 'progress': 0},
            '_pdf_path': str(pdf_path)
        }

    return {'paper_id': paper_id, 'status': 'waiting_confirm', 'suggested_doc_type': suggested_doc_type}


async def run_pipeline(paper_id: str, pdf_path: str, doc_type: str):
    """在背景執行 pipeline（使用者確認文件類型後觸發）"""
    try:
        def on_progress(info):
            with tasks_lock:
                processing_tasks[paper_id]['progress'] = info

        loop = asyncio.get_event_loop()
        output_paths = {'_confirmed_doc_type': doc_type}
        with tasks_lock:
            processing_tasks[paper_id]['status'] = 'processing'

        pipeline = PipelineCore(on_progress=on_progress)
        output_paths2 = await loop.run_in_executor(
            None, lambda: pipeline.process(pdf_path, str(OUTPUT_DIR),
                existing_paths=output_paths, paper_id=paper_id)
        )

        # 檢查是否在處理過程中被刪除
        with tasks_lock:
            if processing_tasks.get(paper_id, {}).get('status') == 'cancelled':
                logger.info(f"論文已被刪除，取消後續處理: {paper_id}")
                return

        final = output_paths2.get('final', {})
        paper_manager.load_paper_resources(OUTPUT_DIR, paper_id, final, ai_core)

        with tasks_lock:
            processing_tasks[paper_id]['status'] = 'done'
        logger.info(f"論文處理完成: {paper_id}")

    except Exception as e:
        with tasks_lock:
            processing_tasks[paper_id]['status'] = 'error'
            processing_tasks[paper_id]['error'] = str(e)
        logger.error(f"論文處理失敗: {paper_id} - {str(e)}")


# ── 處理進度（SSE） ──

@app.get("/api/papers/{paper_id}/status")
async def paper_status(paper_id: str):
    """取得論文處理進度（SSE）"""
    async def event_stream():
        while True:
            with tasks_lock:
                task = processing_tasks.get(paper_id)
                if task is not None:
                    task = dict(task)
            if not task:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break

            yield f"data: {json.dumps({k: v for k, v in task.items() if not k.startswith('_')})}\n\n"

            if task['status'] in ('done', 'error', 'waiting_confirm'):
                break

            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── 論文內容 ──

@app.get("/api/papers/{paper_id}/content")
async def paper_content(paper_id: str, lang: str = "zh"):
    """取得論文 Markdown 內容"""
    paper_dir = OUTPUT_DIR / paper_id
    lang_key = "zh" if lang == "zh" else "en"
    md_path = paper_dir / f"final_{paper_id}_{lang_key}.md"

    if not md_path.exists():
        raise HTTPException(status_code=404, detail="論文內容不存在")

    content = md_path.read_text(encoding='utf-8')
    return {'paper_id': paper_id, 'lang': lang_key, 'content': content}


# ── 圖片靜態檔案 ──

@app.get("/api/papers/{paper_id}/images/{filename}")
async def paper_image(paper_id: str, filename: str):
    """取得論文圖片"""
    # ① 去除任何目錄層級，只取純檔名
    safe_filename = Path(filename).name
    image_path = OUTPUT_DIR / paper_id / "images" / safe_filename

    # ② 確認解析後路徑仍位於 OUTPUT_DIR 之內（防止 ../ 逃逸）
    try:
        image_path.resolve().relative_to(OUTPUT_DIR.resolve())
    except ValueError:
        # ③ 路徑逃逸 OUTPUT_DIR
        return JSONResponse(status_code=400, content={"error": "無效的檔案路徑"})

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="圖片不存在")

    return FileResponse(str(image_path))


# ── AI 問答（SSE 串流） ──

@app.post("/api/papers/{paper_id}/chat")
async def chat(paper_id: str, request: ChatRequest):
    """AI 問答，SSE 串流回傳"""
    async def event_stream():
        try:
            loop = asyncio.get_event_loop()
            gen = ai_core.query_stream(
                query=request.query,
                paper_id=paper_id,
                visible_content=request.visible_content
            )

            for chunk in gen:
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)  # 讓出控制權，避免阻塞

        except Exception as e:
            yield f"data: {json.dumps({'sentence': str(e), 'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── 對話紀錄 ──

class ChatHistory(BaseModel):
    messages: list

@app.get("/api/papers/{paper_id}/chat/history")
async def get_chat_history(paper_id: str):
    """取得對話紀錄"""
    return paper_manager.load_chat_history(OUTPUT_DIR, paper_id)

@app.post("/api/papers/{paper_id}/chat/history")
async def save_chat_history(paper_id: str, history: ChatHistory):
    """儲存對話紀錄"""
    paper_dir = OUTPUT_DIR / paper_id
    if not paper_dir.exists():
        raise HTTPException(status_code=404, detail="論文不存在")
    paper_manager.save_chat_history(OUTPUT_DIR, paper_id, history.messages)
    return {"status": "ok"}

# ── 文件類型確認 ──

class ConfirmTypeRequest(BaseModel):
    doc_type: str

@app.post("/api/papers/{paper_id}/confirm_type")
async def confirm_type(paper_id: str, request: ConfirmTypeRequest, background_tasks: BackgroundTasks):
    """使用者選擇文件類型後，開始處理"""
    valid_types = ['academic', 'book', 'technical', 'slides', 'web', 'news']
    if request.doc_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"無效的文件類型，可選: {valid_types}")

    with tasks_lock:
        task = processing_tasks.get(paper_id)
        pdf_path = task.get('_pdf_path') if task else None
    if not pdf_path:
        raise HTTPException(status_code=500, detail="找不到原始 PDF 路徑")

    with tasks_lock:
        processing_tasks[paper_id]['status'] = 'processing'
    background_tasks.add_task(run_pipeline, paper_id, pdf_path, request.doc_type)
    return {"status": "ok", "doc_type": request.doc_type}

# ── 刪除論文 ──

@app.delete("/api/papers/{paper_id}")
async def delete_paper(paper_id: str):
    """刪除論文及其所有相關檔案"""
    paper_dir = OUTPUT_DIR / paper_id
    if not paper_dir.exists():
        raise HTTPException(status_code=404, detail="論文不存在")

    # 標記任務為已取消，避免 pipeline 完成後重新寫入
    with tasks_lock:
        if paper_id in processing_tasks:
            processing_tasks[paper_id]['status'] = 'cancelled'

    paper_manager.delete_paper(OUTPUT_DIR, paper_id)

    # 清理記憶體殘留（消除鬼魂論文）
    with tasks_lock:
        processing_tasks.pop(paper_id, None)
    ai_core.remove_paper(paper_id)

    return {"status": "ok", "deleted": paper_id}

# ── 對話紀錄匯出 ──

@app.get("/api/papers/{paper_id}/chat/export")
async def export_chat_history(paper_id: str):
    """匯出對話紀錄為 Markdown"""
    history = paper_manager.load_chat_history(OUTPUT_DIR, paper_id)
    if not history:
        raise HTTPException(status_code=404, detail="沒有對話紀錄")

    # 取得論文標題
    papers = paper_manager.load_papers_index(OUTPUT_DIR)
    paper = next((p for p in papers if p['id'] == paper_id), None)
    title = paper.get('translated_title') or paper.get('title', paper_id) if paper else paper_id

    # 產生 Markdown
    lines = [f"# {title} — 對話紀錄", ""]
    for msg in history:
        if msg['role'] == 'user':
            lines.append(f"**問：** {msg['content']}")
        else:
            lines.append(f"**答：**\n\n{msg['content']}")
        lines.append("")

    md_content = "\n".join(lines)

    from fastapi.responses import Response
    return Response(
        content=md_content.encode('utf-8'),
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={paper_id}_chat.md"}
    )

# ── 清理殘餘檔案 ──

@app.post("/api/cleanup")
async def cleanup_orphaned():
    """清理不在 papers_index 裡的殘餘目錄"""
    import shutil
    papers = paper_manager.load_papers_index(OUTPUT_DIR)
    valid_ids = {p['id'] for p in papers}

    removed = []
    for item in OUTPUT_DIR.iterdir():
        if item.is_dir() and item.name not in valid_ids:
            shutil.rmtree(item)
            removed.append(item.name)
            logger.info(f"清理殘餘目錄: {item.name}")

    return {"status": "ok", "removed": removed, "count": len(removed)}

# ── 健康檢查 ──

@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False, log_level="warning", access_log=False)