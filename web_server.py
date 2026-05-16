import os
import json
import logging
import asyncio
import uuid
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全域設定
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# 全域狀態
ai_core = None
processing_tasks: dict = {}  # paper_id -> {'status': str, 'progress': dict}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """啟動時初始化"""
    global ai_core

    from ai_core import AICore

    ai_core = AICore()
    ai_core.init_rag_retriever(str(OUTPUT_DIR))

    # 載入已有論文的向量庫
    index_path = OUTPUT_DIR / "papers_index.json"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        for paper in papers:
            paper_id = paper['id']
            paths = paper.get('paths', {})
            vector_store = paths.get('rag_vector_store')
            rag_tree = paths.get('rag_tree')
            if vector_store:
                full_vector_path = OUTPUT_DIR / vector_store
                if full_vector_path.exists():
                    ai_core.add_paper_vector_store(paper_id, str(full_vector_path))
                    logger.info(f"[INFO] 預載向量庫: {paper_id}")
            if rag_tree:
                full_tree_path = OUTPUT_DIR / rag_tree
                if full_tree_path.exists():
                    ai_core.load_paper_cache(paper_id, str(full_tree_path))

    logger.info("Web server 初始化完成")
    yield


app = FastAPI(title="Mad Professor Web API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse

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
    index_path = OUTPUT_DIR / "papers_index.json"
    if not index_path.exists():
        return []
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ── 論文上傳 ──

@app.post("/api/papers/upload")
async def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """上傳 PDF 並開始處理"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只接受 PDF 檔案")

    paper_id = Path(file.filename).stem
    pdf_path = DATA_DIR / file.filename

    # 儲存上傳的 PDF
    with open(pdf_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # 初始化任務狀態
    processing_tasks[paper_id] = {
        'status': 'processing',
        'progress': {'stage': 'pdf2md', 'stage_name': 'PDF 轉 Markdown', 'index': 0, 'total': 8, 'progress': 0}
    }

    # 背景執行 pipeline
    background_tasks.add_task(run_pipeline, paper_id, str(pdf_path))

    return {'paper_id': paper_id, 'status': 'processing'}


async def run_pipeline(paper_id: str, pdf_path: str, doc_type: str = None):
    """在背景執行 pipeline"""
    try:
        from pipeline_core import PipelineCore

        def on_progress(info):
            processing_tasks[paper_id]['progress'] = info

        pipeline = PipelineCore(on_progress=on_progress)

        loop = asyncio.get_event_loop()

        if doc_type is None:
            # 第一階段：只跑 pdf2md，然後暫停等待確認
            output_paths = await loop.run_in_executor(
                None, lambda: pipeline.process(pdf_path, str(OUTPUT_DIR),
                    stages=['pdf2md'])
            )
            detection = output_paths.get('_doc_type_detection', {})
            processing_tasks[paper_id]['status'] = 'waiting_confirm'
            processing_tasks[paper_id]['detection'] = detection
            processing_tasks[paper_id]['_output_paths'] = output_paths
            processing_tasks[paper_id]['_pdf_path'] = pdf_path
            logger.info(f"偵測文件類型完成，等待確認: {paper_id} -> {detection.get('doc_type')}")
        else:
            # 第二階段：使用者確認後，繼續跑剩餘階段
            output_paths = processing_tasks[paper_id].get('_output_paths', {})
            output_paths['_confirmed_doc_type'] = doc_type
            processing_tasks[paper_id]['status'] = 'processing'

            remaining_stages = ['analyze', 'md2json', 'json_process', 'tiling',
                                'translate', 'md_restore', 'extra_info', 'rag']
            pipeline2 = PipelineCore(on_progress=on_progress, stages=remaining_stages)
            # 把已有的 output_paths 傳進去
            pipeline2.paper_info['paper_id'] = paper_id
            paper_dir = OUTPUT_DIR / paper_id
            pipeline2.paper_info['output_dir'] = paper_dir

            output_paths2 = await loop.run_in_executor(
                None, lambda: pipeline2.process(pdf_path, str(OUTPUT_DIR),
                    stages=remaining_stages, existing_paths=output_paths)
            )

            final = output_paths2.get('final', {})
            vector_store = final.get('rag_vector_store')
            rag_tree = final.get('rag_tree')

            if vector_store and Path(vector_store).exists():
                ai_core.add_paper_vector_store(paper_id, str(vector_store))
            if rag_tree and Path(rag_tree).exists():
                ai_core.load_paper_cache(paper_id, str(rag_tree))

            processing_tasks[paper_id]['status'] = 'done'
            logger.info(f"論文處理完成: {paper_id}")

    except Exception as e:
        processing_tasks[paper_id]['status'] = 'error'
        processing_tasks[paper_id]['error'] = str(e)
        logger.error(f"論文處理失敗: {paper_id} - {str(e)}")


# ── 處理進度（SSE） ──

@app.get("/api/papers/{paper_id}/status")
async def paper_status(paper_id: str):
    """取得論文處理進度（SSE）"""
    async def event_stream():
        while True:
            task = processing_tasks.get(paper_id)
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
    image_path = OUTPUT_DIR / paper_id / "images" / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="圖片不存在")

    from fastapi.responses import FileResponse
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
    history_path = OUTPUT_DIR / paper_id / "chat_history.json"
    if not history_path.exists():
        return []
    with open(history_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.post("/api/papers/{paper_id}/chat/history")
async def save_chat_history(paper_id: str, history: ChatHistory):
    """儲存對話紀錄"""
    paper_dir = OUTPUT_DIR / paper_id
    if not paper_dir.exists():
        raise HTTPException(status_code=404, detail="論文不存在")
    history_path = paper_dir / "chat_history.json"
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history.messages, f, ensure_ascii=False, indent=2)
    return {"status": "ok"}

# ── 文件類型確認 ──

class ConfirmTypeRequest(BaseModel):
    doc_type: str

@app.post("/api/papers/{paper_id}/confirm_type")
async def confirm_type(paper_id: str, request: ConfirmTypeRequest, background_tasks: BackgroundTasks):
    """使用者確認文件類型後，繼續處理"""
    task = processing_tasks.get(paper_id)
    if not task or task['status'] != 'waiting_confirm':
        raise HTTPException(status_code=400, detail="論文不在等待確認狀態")

    valid_types = ['academic', 'book', 'technical', 'slides', 'web', 'news']
    if request.doc_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"無效的文件類型，可選: {valid_types}")

    pdf_path = task.get('_pdf_path')
    if not pdf_path:
        raise HTTPException(status_code=500, detail="找不到原始 PDF 路徑")

    processing_tasks[paper_id]['status'] = 'processing'
    processing_tasks[paper_id]['progress'] = {
        'stage': 'analyze', 'stage_name': '文件結構分析',
        'index': 1, 'total': 8, 'progress': 10
    }

    background_tasks.add_task(run_pipeline, paper_id, pdf_path, request.doc_type)
    return {"status": "ok", "doc_type": request.doc_type}

# ── 刪除論文 ──

@app.delete("/api/papers/{paper_id}")
async def delete_paper(paper_id: str):
    """刪除論文及其所有相關檔案"""
    import shutil
    paper_dir = OUTPUT_DIR / paper_id
    if not paper_dir.exists():
        raise HTTPException(status_code=404, detail="論文不存在")

    # 刪除目錄
    shutil.rmtree(paper_dir)

    # 更新 papers_index.json
    index_path = OUTPUT_DIR / "papers_index.json"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        papers = [p for p in papers if p['id'] != paper_id]
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)

    return {"status": "ok", "deleted": paper_id}

# ── 健康檢查 ──

@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)