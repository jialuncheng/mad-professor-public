# 2026-05-20 Stage A：AIProfessorChat 改 stateless 完整分析

純讀分析。未動任何檔案、未 commit。

> **核心發現先講**：`AIProfessorChat` 共 **5 個對話狀態 attribute**（含
> `conversation_history` / `last_grounding_sources` / `current_paper_id`
> / `current_paper_data` / 隱含 `last_grounding_sources` 中介）+ 3 個服務
> attribute（logger / base_path / llm_client / retriever）。**對話狀態
> 全可移除**：`conversation_history` 改參數、`last_grounding_sources` 改
> generator yield、`current_paper_*` 純冗餘（已被 paper_id/paper_data 參
> 數取代）；`set_paper_context` 與 `cancel()` 為**死碼**。DB 持久化路徑
> 已成熟（Phase 1.6 conversations 表 + 前端 POST /chat/history 整包覆寫），
> 不需新增 DB 寫邏輯——caller 只需在 chat endpoint 入口**多讀一次 DB
> conversation_history** 傳給 stateless 函式。Stage A 真實工程量
> **90–120 分**，可拆 4 commits。

---

## A. AIProfessorChat mutable 狀態完整盤點

### A-1 所有 self.* 賦值點

| 行 | attribute | 賦值 method | 類型 |
|---|---|---|---|
| 16 | `self.logger` | `__init__` | **服務（保留）** |
| 17 | `self.base_path` | `__init__` | **服務（保留）** |
| 18 | `self.conversation_history = []` | `__init__` | **對話狀態（→ 改參數）** |
| 19 | `self.current_paper_id = None` | `__init__` | **對話狀態（→ 移除，由 paper_id 參數取代）** |
| 20 | `self.current_paper_data = None` | `__init__` | **對話狀態（→ 移除，由 paper_data 參數取代）** |
| 21 | `self.retriever = None` | `__init__` | **服務（保留）**（後續由 ai_core 注入） |
| 22 | `self.llm_client = None` | `__init__` | **服務（保留）** |
| 23 | `self.last_grounding_sources = None` | `__init__` | **對話狀態（→ 改 yield）** |
| 25 | `self.llm_client = LLMClient.get_instance()` | `__init__` | 服務 init |
| 40 | `self.current_paper_id = paper_id` | `set_paper_context` | **死碼（method 0 caller）** |
| 41 | `self.current_paper_data = paper_data` | `set_paper_context` | **死碼** |
| 56 | `self.last_grounding_sources = None` | `process_query_stream` | reset |
| 69 | `self.conversation_history = self.conversation_history[-10:]` | `process_query_stream` | 滑動窗 truncate |
| 106 | `self.last_grounding_sources = getattr(self.llm_client, '_last_grounding_sources', None)` | `process_query_stream` | 寫入 |
| 110 | `self.conversation_history.append({"role": "assistant", "content": full_response})` | `process_query_stream` | append assistant reply |

### A-2 method × self.* 矩陣

| method | 讀 self.* | 寫 self.* | 可改為參數 / 處置 |
|---|---|---|---|
| `__init__` | – | 全部 init | 保留 logger / base_path / llm_client / retriever；其餘 init 移除 |
| `set_paper_context(paper_id, paper_data)` | – | current_paper_id / current_paper_data | **整個 method 刪除（dead code，grep 全 repo 0 caller，除 _deprecated/AI_manager.py）** |
| `process_query_stream(query, visible_content, owner_id, paper_id, paper_data, use_web_search)` | conversation_history（line 63–69, 110）/ llm_client / logger | conversation_history（append × 2、truncate）/ last_grounding_sources（reset + assign）| **conversation_history 改參數**；**改 generator yield 結構**（含 grounding_sources 在 done event 內） |
| `_make_decision(query, paper_id, paper_data)` | conversation_history（line 134–135 拿 last 4 turns 格式化進 router prompt）/ llm_client / logger | – | **加 conversation_history 參數** |
| `_get_macro_context(query, paper_data)` | logger（僅 log）| – | 無 self state；保留簽名 |
| `_get_rag_context(query, owner_id, paper_id)` | retriever / logger | – | 服務型，保留 |
| `_prepare_final_messages(query, context_info, function_name, paper_id, paper_data)` | conversation_history（line 238–239 把前 N-1 turns extend 進 messages）/ logger | – | **加 conversation_history 參數** |

### A-3 conversation_history 真實生命週期

```
init: self.conversation_history = []        (line 18)
─── chat 來了 ───
[entry] if 上一筆 != 本 query:
          append({"role":"user", "content": query})       (line 66)
        if len > 10: history = history[-10:]              (line 68-69) ← 滑動窗
─── 進 _make_decision ───
        recent = history[:-1][-4:]                        (line 135) ← 給 router 看
─── 進 _prepare_final_messages ───
        messages.extend(history[:-1])                     (line 239) ← 給 LLM 對話脈絡
─── LLM streaming ───
        full_response 累積
─── 串流結束 ───
        append({"role":"assistant", "content": full_response})  (line 110)
─── 下一次 chat 進來時，history 仍存在 self 內 ───
```

**關鍵觀察**：
- 「滑動窗 max 10 turns」純粹是**短期 LLM context 控制**，與 DB
  conversations 表（**全量**對話歷史，前端 POST /chat/history 整包覆寫）
  **是兩條獨立軌道**。
- self.conversation_history 為**單例**——所有 user、所有 paper **共用同一條
  rolling window**（前 Phase 0 lock 分析報告 §A-4 已指出此問題）。
- 無 reset、無 summarization、無 paper-切換清空——所以開啟新文件繼續 chat
  時，**舊文件的對話脈絡會殘留在 LLM 上下文裡**（10 turns 內）。

### A-4 last_grounding_sources / current_paper_id / current_paper_data

| attribute | 寫端 | 外部讀端 | 處置 |
|---|---|---|---|
| `last_grounding_sources` | `process_query_stream:106` | `ai_core.query_stream:87` 拿來放進 SSE 最後一個 `done` chunk | **改 yield**：`process_query_stream` 直接 yield `{'type':'done', 'grounding_sources': [...]}`，ai_core 不再讀此 self |
| `current_paper_id` | `set_paper_context:40` (dead code)；`ai_core.remove_paper:123` 比對後設 None | `ai_core.remove_paper:123` | **刪除**——set_paper_context 為 dead code；ai_core.remove_paper 的「if current_paper_id == paper_id 重設」邏輯只在「使用者刪除當前正在看的論文」場景下才有意義，且因 self 不再 keep paper context，整段可刪 |
| `current_paper_data` | 同上 | 同上 | **刪除**，理由同上 |

---

## B. caller 端影響

### B-1 ai_core.query_stream 使用 ai_chat 的點

| ai_core.py 行 | 用法 | stateless 化後 |
|---|---|---|
| 44 | `set_paper_context` 透傳 | **刪除 ai_core.set_paper_context method（已 0 caller）** |
| 74 | `for sentence in self.ai_chat.process_query_stream(...)` | 改為 `for chunk in ...`；解析 chunk['type'] 為 'sentence' / 'done' |
| 87 | `'grounding_sources': self.ai_chat.last_grounding_sources or []` | **刪除**：grounding_sources 由 process_query_stream yield 'done' event 帶出 |
| 123–125 | `if ai_chat.current_paper_id == paper_id: 重設` | **整段刪除**（current_paper_id 已不存在）|

並 ai_core 端可一併移除：
- `self._generating_lock`（line 19、59、95）
- `self.is_generating`（line 18、64、79、94）
- `def cancel(self)`（line 99，0 caller）

**單帳號雙 tab 並發**：stateless 後兩個並發 chat 各自獨立、不再交錯
（因每個 chat 各自帶獨立 conversation_history 參數）；無需鎖。代價：UI 上
兩 tab 各跑各的 response，不再「請稍候再試」。

### B-2 對話歷史 DB 持久化（現況盤點）

**Schema**（`models.py:152–175`）：
```python
class Conversation(Base):
    __tablename__ = "conversations"
    id, paper_id FK→papers.id CASCADE, user_id FK→users.id, session_id,
    role String(20),  # 'user' | 'assistant'
    content Text,
    grounding_sources JSON,  # 可選
    tokens_used Integer, created_at
    Index ix_conversations_paper_id (paper_id, id)
```

**現有讀寫鏈**：
- `paper_manager.load_chat_history(paper_db_id, user_id)`（line 325）：
  query Conversation by paper_id order by id → list of {role, content,
  grounding_sources?, created_at?}
- `paper_manager.save_chat_history(paper_db_id, user_id, history)`
  （line 350）：**整包覆寫**：先 DELETE 該 paper 全部 conversations，再
  批次 INSERT
- `web_server.get_chat_history`（line 458）：GET /api/papers/{id}/chat/history
  → 回傳前端展開的對話列表
- `web_server.save_chat_history`（line 468）：POST 同路徑，**前端負責呼叫**
  （每次 chat done 後）
- 既有持久化機制完整，**無需新增 DB 寫邏輯**——stateless 化後依然由前端
  在 chat done 後 POST /chat/history 寫回 DB

**stateless 後新增的 DB 讀**：
- `web_server.chat`（line 423，POST /api/papers/{id}/chat）入口需要**多讀
  一次** DB conversation_history 傳給 ai_core.query_stream
- 既有：
  ```python
  db_id = paper_manager.get_paper_db_id(current_user.id, paper_id)
  ```
  - **可加**：
  ```python
  if db_id is not None:
      history = paper_manager.load_chat_history(db_id, current_user.id)
  else:
      history = []
  ```
- 每次 chat 多一次 SELECT（毫秒級 + index hit），可接受

### B-3 web_server chat endpoint 變化

當前（簡化）：
```python
gen = ai_core.query_stream(
    query=request.query, owner_id=current_user.id, paper_id=paper_id, ...)
for chunk in gen:
    yield f"data: {json.dumps(chunk)}\n\n"
```

stateless 後：
```python
# 1. 入口多讀對話歷史
db_id = paper_manager.get_paper_db_id(current_user.id, paper_id)
history = paper_manager.load_chat_history(db_id, current_user.id) if db_id else []
# 2. 傳給 ai_core
gen = ai_core.query_stream(
    query=request.query,
    conversation_history=history,
    owner_id=current_user.id, paper_id=paper_id, ...)
# 3. SSE forward（不變）
```

**DB 寫**：仍由前端 POST /chat/history 觸發（既有），ai_core / chat 不寫。
這保留「stateless：state 由 caller 管」精神。

---

## C. 介面設計提案

### C-1 process_query_stream 新簽名

```python
def process_query_stream(
    self,
    query: str,
    conversation_history: List[Dict[str, str]] = None,  # caller 傳入；None 視同 []
    paper_id: Optional[str] = None,
    paper_data: Optional[Dict[str, Any]] = None,
    owner_id: Optional[int] = None,
    visible_content: Optional[str] = None,
    use_web_search: bool = False,
) -> Generator[Dict[str, Any], None, None]:
    """
    Yields:
        {'type': 'sentence', 'text': str}           # 串流出單句
        {'type': 'done',
         'reply': str,                              # 完整 assistant reply（讓 caller 可選擇 DB 寫）
         'grounding_sources': List[Dict]}           # 來源（可能為空）
    """
```

備註：
- `conversation_history` 為**caller 對話歷史**（全量或 caller 截好的窗）；
  本函式內**只讀**、永不 mutate（caller 的 list 安全）
- 函式內部把 `[user query]` 接到結尾建一個 local working_history 給
  LLM context 使用；滑動窗（max 10）也在 local 處理、不動 caller 的 list
- yield 結構從原本「str 為主」改成統一 `dict`，**caller 端必須同步調整**
- `reply` 欄位讓 caller 可選擇直接寫 DB（目前不需，因前端負責；但留欄位
  方便日後抽 package）

### C-2 ai_core.query_stream yield 結構調整

當前 ai_core.query_stream：
```python
yield {'sentence': sentence, 'done': False}        # streaming
yield {'sentence': '', 'done': True, 'grounding_sources': [...]}  # end
```

stateless 改造後：
```python
for chunk in self.ai_chat.process_query_stream(
        query, conversation_history=history, ...):
    if chunk['type'] == 'sentence':
        yield {'sentence': chunk['text'], 'done': False}
    elif chunk['type'] == 'done':
        yield {'sentence': '', 'done': True,
               'grounding_sources': chunk.get('grounding_sources') or []}
```

**對前端 SSE 格式：零變化**（仍 `{sentence, done, grounding_sources?}`），
僅 ai_core 內部如何取得 grounding_sources 的鏈路改了。

不需要新增 result aggregator。

---

## D. 工程量重估與風險

### D-1 真實檔案影響清單

| 檔 | 改動性質 | 估改 |
|---|---|---|
| `AI_professor_chat.py` | __init__ 縮減 / set_paper_context 刪除 / process_query_stream 簽名+邏輯改 / _make_decision 加參數 / _prepare_final_messages 加參數 / `self.conversation_history.*` 改 local var | **+40 / -35 行**（淨 +5；簽名變更貢獻多數）|
| `ai_core.py` | _generating_lock 整移除 / is_generating / cancel / set_paper_context method 移除 / query_stream 加 conversation_history 參數 + 解析新 yield 結構 / remove_paper 內 current_paper_* reset 區塊刪除 | **+15 / -30 行**（淨 -15；簡化大量）|
| `web_server.py` | chat endpoint 入口加 `load_chat_history` 讀取邏輯 + 傳 conversation_history 進 query_stream | **+5 / -0 行** |
| `paper_manager.py` | 無改動（load_chat_history / save_chat_history 既有，已符 stateless caller 需求）| 0 |
| 其他 | 無 | 0 |

合計：**5 檔內 4 檔有動**（paper_manager / models / pipeline_core / processor 全不動）；總約 **+60 / -65 行**（淨 -5）。

### D-2 風險點

1. **_make_decision 的 router prompt 內 conversation_history 格式**
   （line 134–145）：目前 format 為「USER: ...\nASSISTANT: ...\n」連接；
   stateless 化後改傳參數，**格式邏輯不變**，僅來源改成 param。**風險低**。

2. **_get_macro_context / _get_rag_context 是否依賴 conversation 上下文**
   - `_get_macro_context`：純看 paper_data；**不依賴歷史**。安全。
   - `_get_rag_context`：純做 RAG vector search；**不依賴歷史**。安全。
   - 兩者皆 stateless-friendly。

3. **滑動窗 max 10 邏輯移到 local**：當前 `history[-10:]` 截斷後**取代**
   self.conversation_history（line 69）。stateless 化後：caller 傳的
   history 可能任意長，函式內 `working = (conversation_history or [])
   [-10:] + [{"role":"user","content":query}]` local 處理即可。**不動
   caller 的 list**。風險低。

4. **streaming 中段拋例外的 partial reply**：當前
   `full_response = "".join(sentences seen so far)`；例外時 line 113
   只 log、不 append assistant reply 進 history。stateless 後同樣處理：
   yield 'done' 前 raise → 不 yield 'done'，caller 收 generator 終止 →
   前端不會 POST /chat/history（前端 saveChatHistory 在 chunk.done
   觸發）→ DB 不會殘留破裂訊息。**現有錯誤路徑語意保留**。

5. **既有「同 query 重複觸發跳過 append」邏輯**（line 63–65）：
   ```
   if not (last == query): append
   ```
   stateless 化後此邏輯**消失**——因 self.conversation_history 不再存在。
   caller 傳的 history 內最後一筆**不會是當下這個 query**（caller 從 DB
   讀，DB 還沒有當下這筆）。**正向影響**：去除了一個歷史包袱判斷。

6. **`self.ai_chat.current_paper_id` 用於 ai_core.remove_paper 的「if
   currently viewed 重設」**：刪除後若使用者**正在 chat 時** paper 被刪除
   → 原本會被「reset 為 None」打斷；stateless 後 chat 不關心 self 狀態、
   會繼續跑完當下這個 chat。**輕微 UX 差異**：使用者可能收到「被刪除的
   論文」的最後一段 chat reply。可接受（罕見場景、且 chat 短暫）。

### D-3 測試覆蓋

- `tests/test_metadata_extractor.py`：**不覆蓋 chat 流程**（純 PDF
  metadata 抽取測試）；改動後預期仍 18 passed 3 skipped。
- 全 repo 無 chat 相關 unit test（`grep -rn "process_query_stream\|
  query_stream" tests/`：0 命中）。
- **驗證主要靠端到端**：上傳 paper → chat → 看 SSE 與 DB conversations
  寫入。需 OrcStack 手動驗。
- **新增單元測試可選**：mock LLMClient + Retriever、傳入 fake history、
  assert yield 結構正確、assert 無 self state 殘留。建議下輪做（不阻擋
  Stage A）。

---

## E. 推薦執行順序（拆 4 commit）

### Step 1（commit 1）：conversation_history 改參數
- AIProfessorChat：
  - `__init__`：移除 `self.conversation_history = []`
  - `process_query_stream`：簽名加 `conversation_history: List[Dict] = None`；
    內部用 local var `working`，不寫 self；移除 line 63–69、110 對 self 的操作
  - `_make_decision`：加 `conversation_history` 參數，調 line 134–135 從 param 讀
  - `_prepare_final_messages`：同上，line 238–239 從 param 讀
- ai_core.query_stream：暫時傳 `conversation_history=None`（caller 端尚未補 DB 讀；本步維持單 user 行為等效，等 Step 4 補）
- 不動 _generating_lock、is_generating、cancel、set_paper_context、current_paper_*（這些在後續 step 處理）

**獨立可驗**：py_compile 通過、pytest 不回歸；功能上等效（caller 仍傳 None → ai_chat 內部當空 list）

工程量：**30–40 分**

### Step 2（commit 2）：last_grounding_sources 改 yield + 統一 dict yield
- AIProfessorChat.process_query_stream：
  - 移除 `self.last_grounding_sources` 三處（init / reset / 寫入）
  - yield 改 dict 結構：`{'type':'sentence','text':...}` 串流中；最後
    `{'type':'done','reply': full_response, 'grounding_sources': [...]}`
- ai_core.query_stream：
  - 解析新 yield 結構，組成原本對前端的 `{sentence, done, grounding_sources}` SSE chunk
  - 移除 `self.ai_chat.last_grounding_sources` 讀取（line 87）

**獨立可驗**：py_compile、pytest；前端 SSE 格式不變 → 端到端等效

工程量：**20–30 分**

### Step 3（commit 3）：刪除 set_paper_context + current_paper_* + ai_core 對應
- AIProfessorChat：刪除 `set_paper_context` method（line 38–46）；
  `__init__` 移除 `self.current_paper_id` / `self.current_paper_data`
- ai_core：移除 `set_paper_context` method（line 40–42）；
  `remove_paper` 內 line 123–125 三行刪除

**獨立可驗**：grep 證實全 repo 0 caller；pytest；上傳/刪除 paper 流程不變

工程量：**10–15 分**

### Step 4（commit 4）：移除 _generating_lock + caller 補 DB read
- ai_core：移除 `self._generating_lock` / `self.is_generating` /
  `cancel()` / acquire/release 與 `if not is_generating: break` 流程
- web_server.chat endpoint：加 `load_chat_history` 讀取、傳給
  `ai_core.query_stream(conversation_history=history, ...)`
- ai_core.query_stream 簽名加 `conversation_history` kwarg、forward 給
  ai_chat

**獨立可驗**：py_compile、pytest；端到端：上傳 paper → chat 多輪 → DB
conversations 表正確累積、LLM 能引用前文

工程量：**20–30 分**

### 合計
- 4 commits、**80–115 分**
- 不阻擋 GCP 單帳號部署（Stage A 是為 Phase 2 鋪路）
- 風險：低（每 step 獨立可驗、語意等效或正向改進）

### 互相依賴關係
- Step 1 是基礎；Step 2/3 可並行於 Step 1 之後
- Step 4 依賴 Step 1（conversation_history 為參數）；可在 Step 2/3 之後做
- 推薦線性執行（避免 merge conflict）

---

## F. 未來抽 package 預備（Stage B 鋪路）

雖然 Stage A 不抽 package，但設計要避免「綁定 mad-professor 特定邏輯」：

### F-1 應抽象的介面
| 介面 | 當前綁定 | Stage B 建議 |
|---|---|---|
| `Retriever` | `rag_retriever.RagRetriever`（綁定 FAISS / Gemini embedding） | abstract `Retriever` Protocol：`retrieve(owner_id, query, paper_id, top_k) -> str`、`is_ready() -> bool`。Stage A 可先把 `self.retriever` 的 typing 改為 `Optional[Any]`（已是），標註「需符合 Retriever 介面」 |
| `LLMClient` | `config.LLMClient`（綁定 google-genai）| abstract `LLMClient` Protocol：`chat_stream_by_sentence(messages, temperature, use_web_search) -> Iterator[str]`、`chat(messages, temperature, stream) -> str` |
| Prompt 路徑 | hardcode `AI_CHARACTER_PROMPT_PATH / AI_EXPLAIN_PROMPT_PATH / AI_ROUTER_PROMPT_PATH` 為模組層常數 | 改 dependency injection：`AIProfessorChat(character_prompt, explain_prompt, router_prompt)`，caller 注入字串（不是路徑） |
| `_read_file` | 模組內讀檔 | Stage B 抽離：prompts 直接接受字串內容，避免 file IO 綁 mad-professor 目錄結構 |

### F-2 不影響 Stage A 但應留意
- **不要**在 Stage A 階段就引入 abstract base class / Protocol——保持
  最小變動原則。只在 method 簽名注意「不在介面表達 mad-professor 特定
  概念」（如不要在簽名出現 `Paper` ORM 物件，已是用 paper_id str + dict）。
- `domain` 透過 `paper_data.get('_domain', '')` 取用——`paper_data` 為純
  dict，Stage B 抽離時 dict 結構即介面契約，無 ORM 依賴。✓

### F-3 標註但不實作
建議 Stage A commit 1 在 docstring 加註：
```python
class AIProfessorChat:
    """文件閱讀 AI 對話模組（stateless）。

    Stage A：將狀態（conversation_history / grounding_sources）外部化、
    self 只保留服務（LLMClient / Retriever / prompt 路徑）。

    Stage B（規劃）：抽離為獨立 package。屆時：
      - prompt 改 caller 注入字串（不再讀檔）
      - LLMClient / Retriever 走 Protocol 介面
      - 介面不出現任何 mad-professor 特定型別（Paper ORM / DB session）
    """
```
讓未來 Stage B 接手者一眼看出設計意圖。

---

## 限制（已遵守）
- 純讀分析；未動任何檔案
- 未 git add / commit
- 未 stub / mock
- 全部依 grep + view + git history 實證；未憑記憶
