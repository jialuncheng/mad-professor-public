# Phase 4.7d Commit 17-1b — Hotfix（chat 殘留 + 載入中卡死）

> 基準：17-1（修正版）後 worktree 狀態
> 完成：本地改檔完成，**尚未 commit、未 push**

---

## Commit Hash

**尚未 commit**——依 baron 指示，純改檔、等確認後再決定何時 commit。

| # | Hash | Subject |
|---|---|---|
| 17-1b | _（pending）_ | fix(chat): 切 paper 立即清 chat + SSE 改 asyncio.to_thread 避免阻塞 event loop |

---

## diff stat（uncommitted）

```
 static/index.html |  4 ++++
 web_server.py     | 13 +++++++++++--
 2 files changed, 15 insertions(+), 2 deletions(-)
```

---

## 兩個 bug 的真因（含診斷過程）

### Bug 1：切 paper 時 chat 殘留

**診斷**：
- 看 `loadPaper(paperId)` (L2114-2144) 流程：
  1. 設 `currentPaperId`
  2. 切 `.paper-item.active`
  3. 清 `#paper-content` 為「載入中...」
  4. **沒清 `#chat-messages`**
  5. `await fetchContent(paperId, currentLang)` ← 可能等很久（見 Bug 2）
  6. 跑到 `await loadChatHistory(paperId)`（L2142）→ 內部 L2263 `messages.innerHTML = ''`

**真因**：`chat-messages` 只在 `loadChatHistory` 內清空，但 `loadChatHistory` 排在 `fetchContent` 之後。若 `fetchContent` 卡住（Bug 2 後端 event loop 被 SSE 阻塞、queue 排隊），舊 paper 的 user query + 閃爍泡泡會殘留可見直到 `loadChatHistory` 終於跑完。

console 證實 baron 觀察：跑 console 時點 chat-messages 已清空（loadChatHistory 已執行）；但**中間狀態**（fetchContent 還在 await）就會看到殘留。

### Bug 2：stream 中切 paper、文章內容載入不出來

**診斷階段**：

確認 `ai_core.query_stream` 是 **sync generator**（`ai_core.py:39` 使用 `def` + `yield`、不是 `async def`）：
```python
def query_stream(self, query, ...):  # sync def
    for chunk in self.ai_chat.process_query_stream(...):
        yield {'sentence': ..., 'done': False}
    yield {'sentence': '', 'done': True, ...}
```

確認 `web_server.event_stream`（17-1 後）：
```python
async def event_stream():    # async def
    gen = ai_core.query_stream(...)  # 拿 sync gen
    for chunk in gen:                # 對 sync gen 跑 for 迴圈
        yield f"data: ...\n\n"
        await asyncio.sleep(0)        # 想讓出 event loop
```

**關鍵**：`for chunk in gen:` 對 sync generator 跑、每次 `next(gen)` 是 blocking call（在 Gemini SDK 內 `requests.get` 等回應）；`await asyncio.sleep(0)` 在每個 chunk 拿到**之後**才執行——但 chunk 之間（等 LLM 回應的 30s）event loop 完全被卡住、其他 endpoint 排隊。

**獨立診斷腳本驗證**（venv/bin/python 跑、見任務 diagnostic）：

模擬「sync gen + async def + asyncio.sleep(0)」+ 並行 task：
```
t=0.00 stream start
t=1.00 stream yield chunk 0
t=2.00 stream yield chunk 1
t=3.01 stream yield chunk 2
t=3.01 stream done
t=3.01 parallel task start    ← 排隊到 stream 完才能跑
t=3.11 parallel task done
```

確認 parallel task（模擬 GET /content）等了整整 3 秒——**證實 Bug 2 真因**。

修法驗證：把 `for chunk in gen:` 改 `chunk = await asyncio.to_thread(next, gen, sentinel)`：
```
t=0.00 stream start
t=0.05 parallel task start    ← 立刻進場、不被 stream 卡
t=0.15 parallel task done
t=1.00 stream yield chunk 0
t=2.01 stream yield chunk 1
t=3.01 stream yield chunk 2
```

parallel task 0.15s 內完成（不再等 3s）、stream 仍正常工作。

---

## 修法

### Bug 1（前端 race）— `static/index.html` `loadPaper`

在 `loadPaper` 開頭、`await fetchContent` **之前**立即清空 `#chat-messages`：

```js
document.getElementById('paper-content').innerHTML = '<p style="color:#94a3b8">載入中...</p>';
// Phase 4.7d Commit 17-1b：立即清空 chat-messages（不等 loadChatHistory）
// 切走的舊 paper user query + 閃爍泡泡會殘留到 loadChatHistory 跑完才清；
// 切 paper 是用戶意圖、UI 應該瞬間反映、不該卡在前一個 paper 的訊息
document.getElementById('chat-messages').innerHTML = '';
```

切 paper 是用戶意圖、UI 應該瞬間反映、不該卡在前一個 paper 的訊息。`loadChatHistory` 之後仍會 render 該 paper 的歷史對話（或 empty placeholder）—— 流程不變、只是清空時機提前。

### Bug 2（後端 event loop block）— `web_server.event_stream`

把對 sync generator 的 `for chunk in gen:` 改為 `asyncio.to_thread(next, gen, sentinel)` 迴圈：

```python
# 之前
for chunk in gen:
    yield f"data: {json.dumps(chunk, ...)}\n\n"
    await asyncio.sleep(0)   # ← 無效、chunk 之間的 blocking 在 next(gen) 內

# 之後
_SENTINEL = object()
while True:
    chunk = await asyncio.to_thread(next, gen, _SENTINEL)   # ← blocking 移到 threadpool
    if chunk is _SENTINEL:
        break
    if chunk.get('sentence'):
        accumulated.append(chunk['sentence'])
    if chunk.get('done') and chunk.get('grounding_sources'):
        grounding_sources = chunk['grounding_sources']
    yield f"data: {json.dumps(chunk, ...)}\n\n"
```

`asyncio.to_thread` 把 `next(gen)` 丟給預設 ThreadPoolExecutor、event loop 在等的同時自由處理其他 endpoint。**`for...in gen` + `asyncio.sleep(0)` 模式**對 sync generator **無用**。

`next(gen, sentinel)` 用 sentinel 取代 `StopIteration`——避免 `asyncio.to_thread` 內 raise `StopIteration` 變 RuntimeError（asyncio 不允許 generator 透過 StopIteration 結束）。

### 為什麼不選其他方案

| 方案 | 評估 |
|---|---|
| 改 ai_core.query_stream 為 async generator | 範圍大、要動 ai_chat / LLMClient 內部、不在不可動清單 |
| event_stream 改為 sync `def`（starlette 會自動跑在 threadpool） | 可行、但要動更多（包含 try/except/finally 流程、async-only API 如 `paper_manager` 也要審）；asyncio.to_thread 範圍小 |
| uvicorn `--workers 2` | 治標、單 worker 仍會卡；且 process model 改變影響 LLMClient semaphore 範圍 |
| `for chunk in gen:` + `await asyncio.sleep(0.01)` | 無效；blocking 在 `next(gen)` 內、加多少 sleep 都沒用 |

---

## 端到端驗證

### 靜態驗證

```bash
venv/bin/python -m py_compile web_server.py
# OK

# JS 語法（內嵌 script 抽取）
node --check ...
# rc=0

venv/bin/pytest tests/ -q
# 116 passed 3 skipped（無回歸）
```

### 行為驗證（虛擬環境模擬）

獨立腳本（任務 diagnostic）已證實：
- 修前：parallel task 等 3 秒
- 修後：parallel task 0.15 秒完成、stream 仍正常

實際 OrcStack 端驗證（push 後）：
- paper 1 提問、stream 跑到一半
- 切到 paper 2
- **Bug 1 預期**：chat panel **瞬間清空**（不再看到 paper 1 殘留）
- **Bug 2 預期**：paper 2 文章內容**幾百 ms 內**載入（不再卡「載入中...」直到 stream 跑完）
- paper 1 stream 仍在後端跑、結束時 DB append assistant（17-1 後端寫 DB 邏輯保留）
- 切回 paper 1：loadChatHistory 從 DB 讀完整對話、立刻顯示

---

## 不可動清單（已遵守）

- [x] `ai_core.query_stream`：未動（簽名 / 內部 LLM 呼叫不變、仍是 sync gen）
- [x] LLMClient / EmbeddingModel：未動
- [x] rag_retriever / processor/*：未動
- [x] DB schema：未動
- [x] `paper_manager.append_chat_message`：未動（17-1 剛 ship）
- [x] commit / push：未動

僅動 2 檔：
- `static/index.html`（+4 行、loadPaper 加 chat-messages 清空）
- `web_server.py`（+11/-2、event_stream 改 to_thread 迴圈）

---

## 回退方式

未 commit、直接：
```bash
git checkout web_server.py static/index.html
```

若已 commit：
```bash
git revert <hash> --no-edit
```

---

## 狀態

**本地改檔完成、未 commit、未 push**——等 baron 確認後再決定何時 commit。

commit 時建議：
```bash
git add web_server.py static/index.html
git commit -m "..."
```

本 hotfix 跟 17-1 修正版**功能正交**：17-1 修「對話保存」、17-1b 修「並發體驗」。可獨立 commit / push。

後續 17-2 / 17-3 / 17-4 final 仍按原 plan：broker → 前端 attach → 移除舊 POST endpoint。本 hotfix 解掉的「event loop block」**並非 broker 必要前提**——broker 主要解「閃爍泡泡無縫銜接 / 切走後 reload 仍見」；event loop block 是另一條獨立問題、本 commit 已解。
