# Phase 4.7d Commit 17 — Plan：chat 對話持久化 + stream reattach

> 純分析報告、零業務檔案改動（除本 .md）。

## TL;DR

- **Bug**：paper A stream 中切 B 再切回 A → 該輪 user query + 半成品 AI 回答完全消失。**根因**：DB 寫入靠**前端** `saveChatHistory(currentPaperId)` 在 stream done 時整包覆寫；切走後 `currentPaperId` 已變、AI chunks 寫不到 DOM、最後 POST 把 paper B 的（空）歷史覆寫到 B 的 DB。
- **方案**（baron 拍板 c 原方案）：**後端 stream broker** —— stream 是全域資源、任何 client 都能 attach；後端寫 DB；前端只「訂閱」而非「擁有」stream。
- **拆 4 commits**：17-1 DB 寫入時機改後端 → 17-2 broker + attach endpoint → 17-3 前端處理 in_progress + attach → 17-4 前端清理（廢 saveChatHistory POST）。
- **核心風險**：17-2 asyncio + StreamingResponse + 多 subscriber 廣播的並發陷阱（deadlock / race / queue overflow）；17-1 user query 與 AI response 寫入順序錯亂時的恢復。
- **4 個 open questions** 待 baron 決策（並發 query / restart partial / 多 browser / 失敗訊息寫不寫）。

---

## 1. 現況盤點

### 1.1 後端

**`web_server.py:428-458` `POST /api/papers/{id}/chat`**（單 chat endpoint）：
```python
db_id = paper_manager.get_paper_db_id(current_user.id, paper_id)
conversation_history = paper_manager.load_chat_history(db_id, current_user.id) if db_id is not None else []

async def event_stream():
    gen = ai_core.query_stream(query=..., conversation_history=..., ...)
    for chunk in gen:
        yield f"data: {json.dumps(chunk, ...)}\n\n"
        await asyncio.sleep(0)

return StreamingResponse(event_stream(), media_type="text/event-stream")
```
**關鍵觀察**：endpoint **不寫 DB**——chunk 從 ai_core 直接 SSE 給前端、結束時也不持久化。完全靠前端 POST `/chat/history` 整包覆寫。

**`web_server.py:466-483`**：GET / POST `/chat/history`：
- GET：`paper_manager.load_chat_history(db_id, user.id)` → list（依 id 排序、即寫入順序）
- POST：`paper_manager.save_chat_history(db_id, user.id, history.messages)` → 整包 delete + bulk insert

**`paper_manager.save_chat_history` (L371-391)**：
```python
s.query(Conversation).filter_by(paper_id=paper_db_id).delete()
for m in history or []:
    s.add(Conversation(paper_id=..., user_id=..., role=..., content=..., grounding_sources=...))
s.commit()
```
**整包覆寫** — 不是 append。前端必須帶上完整歷史。

**`ai_core.query_stream`**（已 stateless、Phase 4.7d Stage A 落地）回傳 generator，yield `{'sentence': str, 'done': bool, 'grounding_sources': list}` 等 dict。**不寫 DB**。

### 1.2 前端

**`sendMessage`（L2318-2385）**：
```js
isStreaming = true;
// 建 userMsg + aiMsg DOM 元素並 append 到 #chat-messages
const res = await fetch(`/api/papers/${currentPaperId}/chat`, {...});
const reader = res.body.getReader();
while (true) {
  const {done, value} = await reader.read();
  // parse SSE chunks
  // chunk.sentence → accumulated += ..., aiMsg.innerHTML = marked.parse(...)
  // chunk.done → await saveChatHistory(currentPaperId);  ← BUG
}
```

**`saveChatHistory(paperId)`（L2294-2316）**：
```js
const msgs = document.querySelectorAll('#chat-messages .msg-user, .msg-ai');
const history = Array.from(msgs).map(...);
await fetch(`/api/papers/${paperId}/chat/history`, {method:'POST', body: JSON.stringify({messages:history})});
```
**從 DOM 抽 messages 整包 POST**。

**`loadChatHistory(paperId)`（L2261-2291）**：
```js
messages.innerHTML = '';      // 清空 DOM
const res = await fetch(`/api/papers/${paperId}/chat/history`);
const history = await res.json();
// 渲染 user / ai msg 到 DOM
```

**`loadPaper(paperId)`（L2115-2144）**：
```js
currentPaperId = paperId;
// ... 切 paper UI
await loadChatHistory(paperId);   // 清 DOM + 重新渲染 B 的歷史
```

---

## 2. Bug 時序圖

```
時間 → ▼

paper A 提問
  T0  前端：currentPaperId='A'、isStreaming=true、push userMsg_A + aiMsg_A 到 DOM
  T0  POST /chat 啟動、後端 event_stream gen 開始 yield chunk
  T0  前端 reader 開始 read

進 stream 約 5%
  T1  收到 chunk → accumulated += sentence
      → aiMsg_A.innerHTML = marked.parse(accumulated)
      （前端 DOM 持續更新中）

切到 paper B
  T2  前端：loadPaper('B')
      → currentPaperId='B'
      → loadChatHistory('B') → messages.innerHTML=''（清掉 userMsg_A + aiMsg_A）
      → render B 的歷史
  T2  reader 沒中止、後端 stream 繼續

stream 繼續、但 aiMsg_A 已被 GC（DOM 從 #chat-messages 移除、JS 變數仍持有但無 DOM）
  T3  chunk 仍到、accumulated += sentence
      → aiMsg_A.innerHTML = marked.parse(...) （寫到 detached DOM、看不見）

stream done
  T4  chunk.done → isStreaming=false
      → await saveChatHistory(currentPaperId)   ← currentPaperId='B'！
      → POST /chat/history paper=B body=[B 的歷史]（DOM 上是 B 的訊息、不含 A 那輪）
      → paper_manager.save_chat_history delete B 既有 + insert B 的歷史
      → paper A 那輪【永遠沒被寫進 DB】

切回 paper A
  T5  loadChatHistory('A') → 從 DB 拿 → 沒那輪
      → 用戶看到「我剛問的問題不見了」
```

**根因關鍵**：
1. `saveChatHistory(currentPaperId)` 用「live」`currentPaperId`，而非 stream 啟動時的 paperId
2. DB 寫入時機在前端 stream done 時、不在後端 chunk 流動時
3. 整包覆寫設計讓「A 那輪沒在 DOM」等同「A 那輪沒在 DB」

---

## 3. 設計方案

### 3.1 後端 stream broker（核心）

**結構**：
```python
# web_server.py（或新檔 chat_broker.py）

@dataclass
class StreamSession:
    owner_id: int
    paper_db_id: int
    paper_uuid: str                  # 給前端對齊
    query: str
    chunks_buffer: List[str]         # 已產生的 sentence
    grounding_sources: List[dict]    # 結束時填
    subscribers: List[asyncio.Queue] # 目前 attach 的 client queue
    done: bool = False
    error: Optional[str] = None
    started_at: datetime

active_streams: Dict[Tuple[int, int], StreamSession] = {}
streams_lock = asyncio.Lock()
```

**chat endpoint 改造**：
```python
@app.post("/api/papers/{paper_id}/chat")
async def chat(paper_id, request, user):
    db_id = paper_manager.get_paper_db_id(user.id, paper_id)
    key = (user.id, db_id)

    # Q1 處理（見 §9）：並發 query 策略 → 暫定「拒絕」
    async with streams_lock:
        if key in active_streams and not active_streams[key].done:
            raise HTTPException(409, "已有進行中的對話、請等待")
        # 寫 user query 進 DB（Commit 17-1 即可立刻寫）
        paper_manager.append_chat_message(db_id, user.id, 'user', request.query)
        # 創 session
        history = paper_manager.load_chat_history(db_id, user.id)  # 含剛寫的 user query
        session = StreamSession(
            owner_id=user.id, paper_db_id=db_id, paper_uuid=paper_id,
            query=request.query, chunks_buffer=[], grounding_sources=[],
            subscribers=[], started_at=datetime.utcnow()
        )
        active_streams[key] = session

    # background task 跑 ai_core
    asyncio.create_task(_run_stream(session, history, request))

    # 為本次 caller 創 subscriber
    sub_q = asyncio.Queue()
    session.subscribers.append(sub_q)
    return StreamingResponse(_pump_to_client(session, sub_q), media_type="text/event-stream")
```

**`_run_stream(session, history, request)`**（background task）：
```python
try:
    gen = ai_core.query_stream(query=session.query, conversation_history=history, ...)
    for chunk in gen:
        if chunk.get('sentence'):
            session.chunks_buffer.append(chunk['sentence'])
        if chunk.get('done'):
            session.grounding_sources = chunk.get('grounding_sources', [])
            session.done = True
        # 廣播給所有 subscriber
        await _broadcast(session, chunk)
        await asyncio.sleep(0)
except Exception as e:
    session.error = str(e)
    await _broadcast(session, {'sentence': f'(生成失敗) {e}', 'done': True})
finally:
    # 寫 DB（完整 AI 回答）
    full = ''.join(session.chunks_buffer)
    paper_manager.append_chat_message(
        session.paper_db_id, session.owner_id,
        'assistant', full,
        grounding_sources=session.grounding_sources or None
    )
    # 從 active 移除
    async with streams_lock:
        active_streams.pop((session.owner_id, session.paper_db_id), None)
```

**`_pump_to_client(session, q)`**：
```python
async def _pump():
    try:
        # 已產生的 buffer 一次回放（給 attach late client）
        if session.chunks_buffer:
            for s in session.chunks_buffer:
                yield f"data: {json.dumps({'sentence': s, 'done': False})}\n\n"
        # 持續從 queue read 新 chunk
        while True:
            chunk = await q.get()
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            if chunk.get('done'):
                break
    finally:
        if q in session.subscribers:
            session.subscribers.remove(q)
return _pump()
```

**`_broadcast(session, chunk)`**：
```python
async def _broadcast(session, chunk):
    for q in list(session.subscribers):
        try:
            q.put_nowait(chunk)
        except asyncio.QueueFull:
            logger.warning("subscriber queue full、drop chunk")
```

### 3.2 attach endpoint

```python
@app.get("/api/papers/{paper_id}/chat/attach")
async def attach(paper_id, user):
    db_id = paper_manager.get_paper_db_id(user.id, paper_id)
    key = (user.id, db_id)
    async with streams_lock:
        session = active_streams.get(key)
        if session is None or session.done:
            raise HTTPException(404, "無進行中的對話")
        sub_q = asyncio.Queue()
        session.subscribers.append(sub_q)
    return StreamingResponse(_pump_to_client(session, sub_q), media_type="text/event-stream")
```

### 3.3 in_progress flag in `GET /chat/history`

回傳結構改：
```json
{
  "messages": [{"role":"user","content":"..."},  {"role":"assistant","content":"..."}, ...],
  "in_progress": {
    "query": "他在 VIEWTRIX 做什麼？",
    "partial": "他擔任 OLED 顯示驅動 IC..."
  }
}
```
- `in_progress` 為 None 表示無 active stream
- `messages` **已包含本輪 user query**（17-1 起 endpoint 寫 DB 時就寫了）
- `in_progress.partial` = `''.join(session.chunks_buffer)`

### 3.4 paper_manager.append_chat_message（新 helper）

取代 `save_chat_history` 的整包覆寫；單筆 append：
```python
def append_chat_message(paper_db_id, user_id, role, content, grounding_sources=None) -> int:
    """新增單筆對話、回傳 conversation.id。順序＝插入序＝id 序。"""
    _ensure_db()
    with db.SessionLocal() as s:
        c = Conversation(
            paper_id=paper_db_id, user_id=user_id, role=role,
            content=content, grounding_sources=grounding_sources or None,
        )
        s.add(c); s.commit()
        return c.id
```

### 3.5 前端改造

#### `loadChatHistory` 改造
```js
async function loadChatHistory(paperId) {
  const messages = document.getElementById('chat-messages');
  messages.innerHTML = '';
  const res = await fetch(`/api/papers/${paperId}/chat/history`);
  const data = await res.json();
  const history = data.messages || data;  // 向下相容舊格式
  // ... 渲染既有 messages ...

  if (data.in_progress) {
    // 渲染進行中對話
    const userMsg = renderUserMsg(data.in_progress.query);
    const aiMsg = renderAiMsg(data.in_progress.partial + '▋');
    // attach to live stream
    attachToStream(paperId, aiMsg);
  }
}

function attachToStream(paperId, aiMsg) {
  const es = new EventSource(`/api/papers/${paperId}/chat/attach`);
  let accumulated = aiMsg.dataset.accumulated || '';
  es.onmessage = (ev) => {
    const chunk = JSON.parse(ev.data);
    if (chunk.sentence) {
      accumulated += chunk.sentence;
      aiMsg.innerHTML = marked.parse(accumulated.replace(/\n(?!\n)/g, '\n\n'));
    }
    if (chunk.done) {
      if (chunk.grounding_sources?.length) renderSources(aiMsg, chunk.grounding_sources);
      es.close();
    }
  };
  es.onerror = () => es.close();
}
```

#### `sendMessage` 改造
重點：不要呼叫 saveChatHistory（後端會寫 DB）；改用 EventSource attach 而非 fetch + reader，邏輯統一：
```js
async function sendMessage() {
  // ... 既有 input / userMsg / aiMsg 建立 ...
  isStreaming = true;
  const paperId = currentPaperId;   // snapshot、避免後續切走時 currentPaperId 變

  // 1. 啟動 stream（POST + 不讀 body、只觸發後端 active_streams 建立）
  await fetch(`/api/papers/${paperId}/chat`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({query, use_web_search: useWebSearch})
  });
  // 後端 POST 直接返回 SSE 流；EventSource 走 attach
  // 或：直接讀 POST 回傳的 SSE（更精準）—— 兩種設計：

  // 設計 A：POST 回 SSE、本次 caller 直接讀
  //   - 一致性高、但切走後 reader 被中斷或仍跑
  //   - 切回需 attach 拉新 reader 銜接

  // 設計 B：POST 只啟動、不回 SSE；本次 caller 走 GET attach
  //   - 對稱、所有 client（包含 sender）都走 attach
  //   - sender 體驗多一個 round-trip

  attachToStream(paperId, aiMsg);
}
```
**推薦設計 B**（對稱性）：POST `/chat` 啟動、回 `{stream_id, ...}` 簡易 ACK；GET `/chat/attach` 拿 SSE。**避免 POST 同時做啟動 + SSE 的雙職責**。

---

## 4. UX 對比表

| 操作 | 既有（bug） | c 原方案（本 plan） | c1（partial 寫 DB） | d（前端切走中止 stream） |
|---|---|---|---|---|
| 切走切回 | 該輪消失 | 閃爍泡泡繼續、無縫 | 看到 partial、無 stream | 切走就斷、損失內容 |
| 切走後 reload | 該輪消失 | reload 後仍閃爍 | 看到 partial | 損失內容 |
| 多瀏覽器同時開 | 各自獨立 | 兩邊都看到閃爍（subscribers 廣播） | 各自看到 DB partial | 各自獨立 |
| stream 結束 | DB 沒寫 → 消失 | DB 完整、跟「沒切走」一樣 | DB 完整 | DB 完整（如有完整寫） |
| 實作複雜度 | — | **中-高**（asyncio broker） | 中（DB partial 寫入） | 低（中止 stream + 棄該輪） |

**baron 選定 c 原方案** —— 完整體驗、可接受實作複雜度。

---

## 5. 邊角 case 處理

### 5.1 並發 query（同 paper、同 user、前一個未結束就發第二個）
**推薦：拒絕** — chat endpoint 檢 active_streams、若已有 active 拋 409。理由：
- 簡單、邏輯清楚
- 前端可顯示「請等待目前對話完成」
- 若排隊，broker 狀態變複雜（chunks_buffer 跨多 query？session 樹？）
- 若覆寫，前一個 partial 進 DB 變半成品；用戶意圖不明

**未來可選**：排隊（FIFO queue）—— 但本 commit 不做。**baron 決策 Q1**。

### 5.2 同 paper、不同 user
key 是 `(user.id, paper_db_id)`、天然隔離 —— 不同 user 各自一個 session。

### 5.3 web_server restart 時、active_streams 全清
**推薦：partial 丟棄、不寫 DB**（baron 決策 Q2）。理由：
- restart 是異常狀況、用戶通常重試
- 寫進 DB 變半成品、用戶誤以為 AI 回答完整
- 前端 attach 拿 404 → render「對話中斷、請重試」
**或選**：finally 區段強制寫 partial 進 DB + 標記 `[interrupted]`。**baron 決策**。

### 5.4 同一 user 同 paper 多瀏覽器分頁
session.subscribers 是 list、每個分頁進來 attach 都加一個 queue → 廣播自然送達兩邊。**無需特別處理、設計即內建支援**。

### 5.5 ai_core.query_stream 內部 exception
- `_run_stream` finally 寫 DB：`'(生成失敗) {e}'` 或截斷的 partial
- subscriber 收到 `{'sentence': '(生成失敗) ...', 'done': True}`
- 前端 attach 也會收到、UI 顯示錯誤訊息
- **是否寫進 DB**：baron 決策 Q4。**推薦：寫**（用戶可看到 error trace、避免「消失」感）

### 5.6 用戶切走、stream 結束很久才切回
- broker `_run_stream` finally 已寫 DB + 從 active_streams 移除
- 切回 → `GET /chat/history` 拿到完整對話、`in_progress = None`
- 體驗：看到完整對話 ✅

### 5.7 stream 還沒結束就刪除 paper
- 既有 `DELETE /papers/{id}` endpoint 已清 conversations cascade
- 但 active_streams[(user, db_id)] 仍存在、`_run_stream` finally 試寫 DB 會炸（paper_id 不存在）
- **處理**：delete endpoint 內檢 active_streams、若有 → 標記 session.cancelled、broadcast cancel 後拋出
- 或：finally 區段 try/except 寫 DB（最簡）

### 5.8 subscriber queue overflow
- 若 client 連線慢、chunk 累積無 limit → memory 漲
- **緩解**：`asyncio.Queue(maxsize=200)` + `put_nowait` 配合 try/except QueueFull → log warning + drop
- partial chunks 在 session.chunks_buffer 仍完整、後續 attach 仍能補

---

## 6. commit 拆分

### 17-1 後端 DB 寫入時機改後端、加 `append_chat_message`
**範圍**：
- `paper_manager.append_chat_message(db_id, user_id, role, content, gs=None)` 新 helper
- `web_server.chat` endpoint 加入：
  - endpoint 進入時寫 user query（一筆 append）
  - event_stream 結尾累積 AI 完整回答後寫一筆
- `saveChatHistory` POST endpoint 暫保留（舊 client 兼容）但**不依賴**
- 廢「切走切回消失」依賴：DB 寫入不再靠前端

**改動**：`paper_manager.py` + `web_server.py` 局部
**工時**：30-45 分鐘
**Bug 修復**：本 commit 已**部分**修 bug（DB 不會被前端覆寫成空），但前端仍可能誤讀 stream chunks 到錯的 DOM；UX「閃爍泡泡銜接」需 17-2/17-3 完成

**測試**：
- `tests/test_paper_manager.py` 加 `append_chat_message` 測試
- 整合：上傳 paper → POST chat → DB 有 user + assistant 各一筆

### 17-2 後端 stream broker + `/chat/attach` endpoint
**範圍**：
- 新 `chat_broker.py`（或 `web_server.py` 內）含 `StreamSession` + `active_streams` + helpers
- `web_server.chat` 改用 broker（POST 啟動 + SSE 回 caller）
- 新 `GET /chat/attach` endpoint
- `GET /chat/history` 改回傳含 `in_progress`
- 邊角 case 處理（cancel / restart / queue overflow）

**改動**：`web_server.py`（大改）+ 可能新檔
**工時**：3-4 小時（核心）
**風險**：**中-高**——asyncio broker 並發陷阱

**測試**：
- `tests/test_chat_broker.py`（新檔）
  - 單 subscriber 收到完整 stream
  - 多 subscriber 同時 attach、都收到完整 stream
  - subscriber 中途 attach、能收到 buffer 回放
  - 並發 chat 拒絕（409）
  - stream 結束、active_streams 清空

### 17-3 前端 `loadChatHistory` + attach
**範圍**：
- `loadChatHistory` 讀 `{messages, in_progress}` 新格式（向下相容舊 list 格式）
- 看到 `in_progress` 時 render partial + 開 EventSource attach
- 新 `attachToStream(paperId, aiMsg)` helper
- 切 paper 時 EventSource.close() 中止（若有）

**改動**：`static/index.html`
**工時**：1-2 小時
**風險**：低（EventSource 標準 API）

### 17-4 前端清理
**範圍**：
- 廢 `saveChatHistory` 函式 + `POST /chat/history` endpoint（後端先廢 endpoint、確認舊 client 不打）
- `sendMessage` 改用 broker（POST 啟動、走 attach；設計 B）
- 移除 `chunk.done → await saveChatHistory()` 那一段

**改動**：`static/index.html` + `web_server.py`（廢 endpoint）
**工時**：30-45 分鐘

---

## 7. 風險評估

| Commit | 風險 | 主要陷阱 | 緩解 |
|---|---|---|---|
| 17-1 | 🟡 低-中 | user query 與 AI response 寫入順序錯亂、event_stream 失敗時 partial 丟失 | try/finally 強制寫；DB transaction 內保 user 一定先寫 |
| 17-2 | 🔴 中-高 | asyncio.Queue race、deadlock（subscriber 沒消費 → broadcast 卡）、 background task 例外被吞 | put_nowait + maxsize 200 + drop on full；`asyncio.create_task` 包 try/except；測試覆蓋 |
| 17-3 | 🟢 低 | EventSource auto-reconnect 行為（瀏覽器預設重連）、attach 失敗後狀態 | 顯式 es.close() 在 done；onerror handler |
| 17-4 | 🟢 低 | 舊 client 仍 POST `/chat/history` | 17-4 同時廢前端呼叫 + endpoint 暫保留一段時間做兼容 |

---

## 8. 測試規劃

### 既有測試影響
- `pytest tests/ -q` 當前 **112 passed 3 skipped**（含 15-1 後）
- 無 chat / conversation 相關測試 — 本 commit 是好機會補

### 新增測試（建議分 commit）

**17-1**：
- `test_append_chat_message_inserts_one`：append 後 DB 有一筆
- `test_append_chat_message_order_preserved`：多次 append 依 id 順序排列
- `test_chat_endpoint_writes_user_query_immediately`（整合 test）

**17-2**：
- `test_stream_session_buffer_accumulates`
- `test_multiple_subscribers_receive_same_chunks`
- `test_late_subscriber_gets_replay`：late attach 拿到 buffer 回放
- `test_concurrent_chat_rejected_409`
- `test_stream_done_clears_active_streams`
- `test_subscriber_queue_full_drops_safely`

**17-3 / 17-4**：純前端、單元測試難。手動端到端為主。

### 端到端驗證計畫（給 baron）

跑 baron 觀察的 bug 流程：
1. paper A 提問、stream 跑到一半
2. 切到 paper B
3. **預期（修好後）**：DB 內 paper A 已有 user query；切回 A 時看到 `in_progress` 並 attach 接續 partial 串流
4. 等 stream done → 切回 A → 看到完整對話

額外驗證：
- 切走後 reload 整頁 → 仍看到 partial 閃爍泡泡 + 後續 SSE
- 開第二個瀏覽器分頁同 paper → 兩邊都看到閃爍（subscribers 廣播）
- web_server restart → 切回 paper A 拿 404、顯示「對話中斷」

---

## 9. open questions（baron 決策）

### Q1 — 並發 query（同 paper、同 user）怎麼處理？
- 推薦：**拒絕 409**「請等待目前對話完成」
- 替代：排隊（複雜）/ 取消舊 + 啟動新（用戶意圖不明）

### Q2 — web_server restart 時、active 中斷的 partial 要寫 DB 嗎？
- 推薦：**不寫**（restart 是異常、partial 進 DB 變半成品）
- 替代：寫並加 `[interrupted]` 後綴

### Q3 — 多瀏覽器同時開、兩邊都看到閃爍——是否要做？
- 設計上**內建支援**（subscribers list 廣播）
- baron 確認：是要做（內建即可）/ 限制單分頁（需鎖 session）

### Q4 — stream 失敗時、DB 寫不寫「(生成失敗) ...」訊息？
- 推薦：**寫**（用戶可見錯誤、避免「消失」感）
- 替代：不寫、前端顯示但 DB 乾淨

### Q5 — saveChatHistory POST endpoint 何時廢？
- 推薦：17-1 落地後就**廢前端呼叫**、endpoint 留 1-2 commit 緩衝期；17-4 移除 endpoint
- 替代：endpoint 永久保留（給未來編輯歷史功能？）

### Q6 — POST `/chat` 設計 A vs B？
- A：POST 直接回 SSE，sender 一路讀；其他 client 走 attach
- B：POST 只啟動、回 ACK；所有 client（含 sender）走 GET attach
- 推薦：**B**（對稱、職責清楚；sender 多一個 round-trip 可接受）

### Q7 — 是否需要「取消進行中對話」功能？
- 用戶按 Esc / cancel button 中止 stream
- 後端 broker 支援 cancel：session.cancelled = True → `_run_stream` 檢查
- **本 commit 不做、留 4.7e**

---

## 10. 不可做（已遵守）

- ❌ 業務檔（web_server / paper_manager / AI_professor_chat / static/* 等）：未動
- ❌ 新建業務檔：未動
- ❌ commit / push：未動
- ✅ grep / cat / pytest 只讀命令：已執行
- ✅ 本報告 `.md`：唯一新增檔

---

## 狀態

**Plan 完成、等 baron 確認後再進入 Execute 階段**。

執行階段建議：
- **17-1 先做**（30-45 分鐘、修一半 bug、低風險）
- **17-2 再做**（3-4 小時、broker 核心）
- **17-3 + 17-4**（前端 + 清理）

執行前需 baron 回答 §9 open questions（特別 Q1 / Q2 / Q4 / Q6）。
