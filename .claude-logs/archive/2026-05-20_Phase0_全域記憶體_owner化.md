# 2026-05-20 Phase 0 三件事一輪：全域記憶體 owner 化（α / β / γ）

依 `2026-05-20_Phase0_多使用者隔離_重新盤點.md`。5 檔改動、+108/-83 行。
**未 commit**，等 baron 確認。0-δ（`_generating_lock`）依 baron 決策**未動**。

| 任務 | 對象 | 鍵改動 |
|---|---|---|
| 0-α | `ai_core._paper_cache` | `Dict[str, ...]` → `Dict[Tuple[int, str], ...]` |
| 0-β | `rag_retriever.{paper_vector_paths, rag_trees, vector_stores}` | 同上（三 dict 同步）|
| 0-γ | `web_server.processing_tasks` | 同上；移除 `_owner_id` 欄事後比對 workaround |

diff stat：
```
 AI_professor_chat.py | 10 ++++----
 ai_core.py           | 48 ++++++++++++++++++++++++--------------
 paper_manager.py     | 14 +++++------
 rag_retriever.py     | 58 +++++++++++++++++++++-----------------
 web_server.py        | 61 +++++++++++++++++++++++++++----------------
 5 files changed, 108 insertions(+), 83 deletions(-)
```

---

## 0-α `ai_core._paper_cache`（含 cache 鍵與 5 個簽名）

### 鍵改 tuple
```diff
-        self._paper_cache: Dict[str, Any] = {}
+        # Phase 0: 鍵改 (owner_id, paper_uuid) tuple，避免跨 owner 撞名
+        self._paper_cache: Dict[Tuple[int, str], Any] = {}
```

### 5 個方法簽名 +`owner_id`
| 方法 | before | after |
|---|---|---|
| `add_paper_vector_store` | `(paper_id, vector_store_path)` | `(owner_id, paper_id, vector_store_path)` |
| `load_paper_cache` | `(paper_id, rag_tree_path)` | `(owner_id, paper_id, rag_tree_path)` |
| `query_stream` | `(query, paper_id=None, …)` | `(query, owner_id, paper_id=None, …)` |
| `remove_paper` | `(paper_id)` | `(owner_id, paper_id)` |
| `set_paper_context` | **未改**（dead code，只 `_deprecated/AI_manager.py` 呼叫）| 同 |

cache 取值：
```diff
-paper_data = self._paper_cache.get(paper_id) if paper_id else None
+paper_data = (self._paper_cache.get((owner_id, paper_id))
+              if paper_id else None)
```

cache 寫入：
```diff
-self._paper_cache[paper_id] = paper_data
+self._paper_cache[(owner_id, paper_id)] = paper_data
```

cache 刪除：
```diff
-if paper_id in self._paper_cache:
-    del self._paper_cache[paper_id]
+key = (owner_id, paper_id)
+if key in self._paper_cache:
+    del self._paper_cache[key]
```

domain 注入路徑（caller paper_manager）對齊新鍵：
```diff
-cache = ai_core._paper_cache.get(paper_uuid)
+cache = ai_core._paper_cache.get((owner_id, paper_uuid))
```
domain 寫入邏輯（`if cache is not None and domain: cache['_domain'] = domain`）
**邏輯保留，僅鍵跟著改**。

---

## 0-β `rag_retriever` 三 dict + 6 個簽名

### 鍵改 tuple
```diff
-        self.vector_stores: Dict[str, FAISS] = {}
-        self.paper_vector_paths: Dict[str, str] = {}
-        self.rag_trees: Dict[str, Dict] = {}
+        # Phase 0: 鍵改 (owner_id, paper_uuid) tuple，避免跨 owner 相同 sanitize 撞名
+        self.vector_stores: Dict[Tuple[int, str], FAISS] = {}
+        self.paper_vector_paths: Dict[Tuple[int, str], str] = {}
+        self.rag_trees: Dict[Tuple[int, str], Dict] = {}
```

### 6 個方法簽名 +`owner_id`
| 方法 | before | after |
|---|---|---|
| `set_rag_tree` | `(paper_id, tree)` | `(owner_id, paper_id, tree)` |
| `add_paper` | `(paper_id, vector_store_path)` | `(owner_id, paper_id, vector_store_path)` |
| `_get_vector_store` | `(paper_id)` | `(owner_id, paper_id)` |
| `load_rag_tree` | `(paper_id)` | `(owner_id, paper_id)` |
| `remove_paper` | `(paper_id)` | `(owner_id, paper_id)` |
| `retrieve_with_context` | `(query, paper_id, top_k=5)` | `(owner_id, query, paper_id, top_k=5)` |

`is_ready()` 不需 owner_id（只判斷「全機是否有任何 vector store」）— **未改**。

每方法內 `key = (owner_id, paper_id)` 局部變數，所有 dict 操作（set/get/pop/in）
全部對齊。`distance_strategy=MAX_INNER_PRODUCT` / 過濾門檻 `0.22` **未動**
（前輪已修）。

---

## 0-γ `web_server.processing_tasks`（含 5 endpoint）

### 鍵改 tuple
```diff
-processing_tasks: dict = {}  # paper_id -> {'status': str, 'progress': dict}
+processing_tasks: dict = {}  # (owner_id, paper_id) -> {'status': str, 'progress': dict, ...}
+                              # Phase 0：鍵改 tuple，跨 owner 隔離；不再需要 _owner_id 欄事後比對
```

### 5 endpoint 改動
| 位置 | 改動 |
|---|---|
| upload（line 298）| `processing_tasks[(current_user.id, paper_id)] = {...}`；**移除 `_owner_id` 欄**（dict 內已無此鍵）|
| `run_pipeline`（line 309–352）| 入口 `task_key = (owner_id, paper_id)`；`on_progress` / status 更新 / cancel 檢查 / done / error 全用 task_key；`if task_key in processing_tasks` 守門避免 race |
| `paper_status` SSE（line 360）| `task_key = (current_user.id, paper_id)`；移除 `task.get('_owner_id') != current_user.id` 比對（tuple key 已隔離） |
| `confirm_type`（line 493）| 同上，移除 `_owner_id` 比對 |
| `delete_paper`（line 519）| 同上，移除 `_owner_id` 比對；末尾 `ai_core.remove_paper(current_user.id, paper_id)`（對齊 0-α 簽名）|

### `_owner_id` workaround 移除
`grep _owner_id web_server.py`：剩 4 命中皆為 Phase 0 註解（「Phase 0：tuple
key 隔離 owner，不再用 `_owner_id` 欄」），**無任何 active code** 讀寫此鍵。

### chat endpoint（line 435）
```diff
 gen = ai_core.query_stream(
     query=request.query,
+    owner_id=current_user.id,
     paper_id=paper_id,
     visible_content=request.visible_content,
     use_web_search=request.use_web_search
 )
```

---

## AI_professor_chat 連動（thread-through 必要）

`process_query_stream` 與 `_get_rag_context` 加 `owner_id` 為 thread-through
參數，傳給 `retriever.retrieve_with_context`：
```diff
 def process_query_stream(self, query, visible_content=None,
+                         owner_id: int = None,
                          paper_id=None, paper_data=None, use_web_search=False):
     ...
-    elif function_name == 'rag_retrieval' and effective_paper_id:
-        context_info = self._get_rag_context(optimized_query, effective_paper_id)
+    elif function_name == 'rag_retrieval' and effective_paper_id:
+        context_info = self._get_rag_context(optimized_query, owner_id, effective_paper_id)

 def _get_rag_context(self, query, owner_id=None, paper_id=None):
     ...
-    if not paper_id or not query or not self.retriever:
-        return ""
+    if not paper_id or not query or not self.retriever or owner_id is None:
+        return ""
     ...
     context = self.retriever.retrieve_with_context(
+        owner_id=owner_id,
         query=query, paper_id=paper_id, top_k=5
     )
```

`set_paper_context` 簽名**保留**（只 `_deprecated/AI_manager.py` 呼叫；active
code 無 caller）。`_make_decision` / `_get_macro_context` 不碰快取 dict，
無需改。

---

## 跨檔 caller 連動清單

| caller | callee | 改動 |
|---|---|---|
| `paper_manager.preload_vector_stores`（line 396, 399, 401）| `ai_core.add_paper_vector_store / load_paper_cache / _paper_cache.get` | 傳 `p.owner_id` 為首參；cache 取值改 tuple |
| `paper_manager.load_paper_resources`（line 413, 415, 422）| 同上 | 傳 `owner_id`（既有 scope）；cache 取值改 tuple |
| `web_server.chat`（line 435）| `ai_core.query_stream` | 加 `owner_id=current_user.id` |
| `web_server.delete_paper`（line 535）| `ai_core.remove_paper` | 加 `current_user.id` 首參 |
| `ai_core.add_paper_vector_store` | `retriever.add_paper` | 透傳 owner_id |
| `ai_core.load_paper_cache` | `retriever.set_rag_tree` | 透傳 owner_id |
| `ai_core.remove_paper` | `retriever.remove_paper` | 透傳 owner_id |
| `ai_core.query_stream` | `ai_chat.process_query_stream` | 透傳 owner_id |
| `AI_professor_chat.process_query_stream` | `self._get_rag_context` | 傳入 owner_id |
| `AI_professor_chat._get_rag_context` | `retriever.retrieve_with_context` | 傳入 owner_id |

**`_deprecated/AI_manager.py` 未動**（已 _deprecated）。

---

## 驗證

| 項 | 結果 |
|---|---|
| `py_compile` 5 個 .py（ai_core / rag_retriever / web_server / paper_manager / AI_professor_chat）| ✓ |
| `pytest tests/test_metadata_extractor.py -q` | **18 passed, 3 skipped**（無回歸）|
| `python tools/check_doc_type_registry.py` | **exit 0**（Phase 0 不影響 doc_type 對齊）|
| 0-α grep `_paper_cache\[/.\.get/.\.pop`：全 tuple 鍵 | **6 命中皆 `(owner_id, paper_id)`** ✓ |
| 0-β grep `paper_vector_paths/rag_trees/vector_stores` 操作：全 tuple 鍵 | **10 命中皆透過 `key = (owner_id, paper_id)` 局部變數** ✓ |
| 0-γ grep `processing_tasks\[/.\.get/.\.pop/in processing_tasks`：全 tuple 鍵 | **15 命中皆透過 `task_key = (owner_id, paper_id)`** ✓ |
| 0-γ grep `_owner_id` 殘留 | **4 命中，皆為 Phase 0 informative 註解**；active code 0 ✓ |
| 5 個 ai_core 簽名 / 6 個 retriever 簽名 / 2 個 chat 簽名 對齊 | ✓ |
| 所有 caller 傳 owner_id（paper_manager ×4、web_server ×2、ai_core 內透傳 ×4、AI_chat 內 ×1） | ✓ |
| domain 注入路徑保留（`cache['_domain']`）| ✓（line 403 / 425 邏輯不變，鍵跟著改）|

端到端（待 OrcStack 重啟手動驗）：
- 單帳號 admin：上傳 PDF → confirm → pipeline 跑完 → 開 AI 對話 → 問問題 → 走 RAG → 回引用內容（與改前等效）
- 刪除論文：cache / vector / rag_tree / processing_tasks 都按 (owner_id, paper_id) 清理乾淨
- Phase 2 多帳號上線後：不同 user 上傳同 sanitize 結果不再撞 key

---

## 推薦合併 commit message（**單一 commit**，3 task 一次完成）

```
refactor(phase0): 全域記憶體鍵改 (owner_id, paper_id) tuple（α/β/γ）

依 Phase 0 多使用者隔離重新盤點：DB schema / 檔案系統 / API endpoint 均
已 owner-aware（Phase 1.x + 4.7 完成），剩餘 3 個全域記憶體狀態
（_paper_cache / rag_retriever 三 dict / processing_tasks）以 paper_id
為單鍵，跨 owner 相同 sanitize 結果會撞名。本輪鍵全改 (owner_id, paper_id)
tuple，配合所有 setter / getter / deleter 簽名加 owner_id 並 thread 至
所有 caller。

0-α  ai_core._paper_cache: Dict[str, Any] → Dict[Tuple[int, str], Any]
     5 簽名：add_paper_vector_store / load_paper_cache / query_stream /
     remove_paper / cache 取存改 tuple key。
     set_paper_context 簽名未改（dead code，僅 _deprecated/ 呼叫）。
     domain 注入邏輯保留、僅鍵跟著改。

0-β  rag_retriever.{paper_vector_paths, rag_trees, vector_stores}:
     三 dict 同步改 Dict[Tuple[int, str], ...]。
     6 簽名：set_rag_tree / add_paper / _get_vector_store / load_rag_tree
     / remove_paper / retrieve_with_context。is_ready() 不需 owner_id
     （全機判斷）保留。distance_strategy=MAX_INNER_PRODUCT 與門檻 0.22
     未動（前輪已修）。

0-γ  web_server.processing_tasks: 鍵改 tuple，移除 _owner_id 欄事後
     比對 workaround。5 endpoint（upload / run_pipeline / paper_status
     SSE / confirm_type / delete_paper）改用 task_key = (current_user.id,
     paper_id)。chat endpoint 加 owner_id=current_user.id 傳給
     query_stream。delete_paper 末尾 ai_core.remove_paper(current_user.id,
     paper_id)。

連動 AI_professor_chat：process_query_stream 與 _get_rag_context 加
owner_id 為 thread-through 參數；_get_rag_context 守門
`owner_id is None → return ""`。

0-δ（_generating_lock per-user）依 baron 決策**延 Phase 2 前再做**，本輪未動。
DB schema / auth / 前端 / prompt / pipeline_core stages / processor / 主題
皆未動。

py_compile 5 檔通過；pytest metadata 18 passed 3 skipped 無回歸；
check_doc_type_registry.py exit 0；grep 三 dict 鍵 100% tuple 化；
_owner_id 殘留 0 active code（僅 Phase 0 informative 註解 4 條）。
+108/-83 行跨 5 檔。
```

---

## 不可動清單（已遵守）
- 0-δ `_generating_lock` per-user：未動（baron 決策延 Phase 2 前）
- DB schema：未動
- 認證（session / auth_guard）：未動
- 前端：未動
- prompt：未動
- `distance_strategy` / 過濾門檻：未動
- domain 注入邏輯：保留（僅鍵跟著改）
- `_deprecated/AI_manager.py`：未動
- pipeline_core / processor：未動
- **未 git add / 未 commit**
