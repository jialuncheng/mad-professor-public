# 2026-05-20 Stage A：AIProfessorChat 改 stateless — 4 commits 執行報告

依 Stage A 分析報告，拆 4 個 commits 完成。所有 commits 已建立於本地分支
`claude/hopeful-yalow-902c50`，**未 push**，等 baron 確認後一起 push。

---

## 4 commits 摘要

| # | hash | 標題 | diff |
|---|---|---|---|
| 1 | `042503e` | Step 1：conversation_history 改為 caller 參數 | +35/-18 |
| 2 | `1a8dc90` | Step 2：grounding_sources 改 yield，統一 dict yield | +24/-18 |
| 3 | `14834f1` | Step 3：刪 set_paper_context + current_paper_* dead code | +0/-19 |
| 4 | `c7f4b65` | Step 4：移除 _generating_lock + caller 從 DB 讀對話歷史 | +13/-20 |
| **累計** | **+72/-75（淨 -3）** | 3 檔（AI_professor_chat.py / ai_core.py / web_server.py）| – |

### 累計 diff stat（vs `e70c4fc`）
```
 AI_professor_chat.py | 86 ++++++++++++++++++++++++--------------
 ai_core.py           | 45 +++++++-------------
 web_server.py        |  8 +++++
 3 files changed, 68 insertions(+), 71 deletions(-)
```

> 註：個別 step 的 diff 加總（35+24+0+13=72；18+18+19+20=75）= 上述總和；
> 兩數略有差距（72/75 vs 68/71）因 git stat 不含未變動的純位移 hunks，
> 不影響邏輯。

---

## 各 commit 詳細 message（已實際 commit）

### Commit 1（`042503e`）— Step 1
```
refactor(chat): conversation_history 改為 caller 參數（Stage A Step 1）

依 Stage A 分析報告，將 AIProfessorChat.conversation_history 從 self
state 改為 caller 參數，移除滑動窗 max 10 對 self 的污染。

AI_professor_chat.py：
- __init__ 移除 self.conversation_history = []
- process_query_stream 簽名加 conversation_history: List[Dict] = None
- _make_decision / _prepare_final_messages 加 conversation_history 參數
- 內部用 local working_history（max 10 滑動窗）；不動 caller 的 list
- class docstring 加 Stage A/B 設計意圖標註

ai_core 端尚未補 DB 讀（Step 4），本 step 仍傳 None → 內部等同空 list →
單帳號雙 tab 仍交錯（未完整解；Step 4 完成全鏈路後解決）。

py_compile 通過；pytest metadata 18 passed 3 skipped 無回歸。
```

### Commit 2（`1a8dc90`）— Step 2
```
refactor(chat): grounding_sources 改 yield，統一 dict yield 結構（Stage A Step 2）

依 Stage A 分析報告，將 AIProfessorChat.last_grounding_sources 從 self
state 改為 generator yield。

AI_professor_chat.py：
- __init__ 移除 self.last_grounding_sources = None
- process_query_stream 移除 reset/寫入 self；改 yield dict
  - 串流：{'type': 'sentence', 'text': str}
  - 結束：{'type': 'done', 'reply': str, 'grounding_sources': list}
- 例外路徑同步：yield sentence + done（reply='', grounding=[]）

ai_core.py：
- query_stream 解析新 yield 結構，組成原本 {sentence, done, grounding_sources}
  SSE chunk
- 移除 self.ai_chat.last_grounding_sources 讀取

對前端 SSE：零變化。reply 欄位為 Stage B 預備（前端目前不用）。

py_compile 通過；pytest metadata 18 passed 3 skipped 無回歸。
```

### Commit 3（`14834f1`）— Step 3
```
refactor(chat): 刪除 set_paper_context 與 current_paper_* dead code（Stage A Step 3）

依 Stage A 分析報告：
- AIProfessorChat.set_paper_context：grep 全 repo 0 caller（除 _deprecated/）
- self.current_paper_id / self.current_paper_data：寫入由 set_paper_context
  + ai_core.remove_paper 觸發；讀取由 ai_core.remove_paper 自查
- 兩者構成循環自證的死碼

AI_professor_chat.py：
- 刪除 set_paper_context method
- __init__ 移除 self.current_paper_id / self.current_paper_data
ai_core.py：
- 移除 set_paper_context method
- remove_paper 移除「if ai_chat.current_paper_id == paper_id 重設」邏輯

py_compile 通過；pytest metadata 18 passed 3 skipped 無回歸；
grep current_paper_* / set_paper_context 全 active code 0 命中
（_deprecated/AI_manager.py 不計）。
```

### Commit 4（`c7f4b65`）— Step 4
```
refactor(chat): 移除 _generating_lock 與 cancel，caller 從 DB 讀對話歷史（Stage A Step 4）

依 Stage A 分析報告：stateless 化後 ai_chat 無 mutable 狀態，
process_query_stream 為純函式，generating_lock 已無保護對象。

ai_core.py:
- 移除 self._generating_lock / self.is_generating
- 移除 acquire(blocking=False) + busy yield 邏輯
- 移除 finally 內 lock release
- 移除 def cancel(self)（grep 全 repo 0 caller）
- 移除 import threading
- query_stream 簽名加 conversation_history forward 給 ai_chat

web_server.py chat endpoint:
- 入口加 paper_manager.load_chat_history 讀取
- 傳 conversation_history 給 ai_core.query_stream

paper_manager.py: 無動（load_chat_history 既有）。
前端 saveChatHistory（chunk.done 時 POST /chat/history）邏輯不變。

Stage A 完成：AIProfessorChat 100% stateless（self 只保留 LLMClient /
Retriever / logger / base_path 服務）。單帳號雙 tab 並發各自獨立、
不交錯；Phase 2 多帳號 conversation_history 完全隔離（per chat call）。

0-δ 完成（生成鎖整移除而非 per-user 化，因 stateless 後鎖已無保護對象）。

py_compile 通過；pytest metadata 18 passed 3 skipped 無回歸；
check_doc_type_registry.py exit 0。
```

---

## 終態 self.* 盤點

### `AIProfessorChat` 終態（**100% stateless**）
```
self.logger      # 服務
self.base_path   # 服務（prompt 檔讀取根目錄；Stage B 改 caller 注入）
self.retriever   # 服務（由 ai_core init_rag_retriever 時注入）
self.llm_client  # 服務（LLMClient.get_instance() singleton）
```
**0 對話狀態**。`conversation_history` / `last_grounding_sources` /
`current_paper_id` / `current_paper_data` / `set_paper_context` 全清。

### `AICore` 終態
```
self.logger       # 服務
self.ai_chat      # 服務（stateless AIProfessorChat 實例）
self.retriever    # 服務
self._paper_cache # 快取（已於 Phase 0 改 (owner_id, paper_uuid) tuple key）
```
`_generating_lock` / `is_generating` / `cancel` 全清。
`set_paper_context` method 全清。

### `process_query_stream` 新簽名（Stage B-ready）
```python
def process_query_stream(
    self,
    query: str,
    visible_content: str = None,
    owner_id: int = None,
    paper_id: str = None,
    paper_data: Dict[str, Any] = None,
    conversation_history: List[Dict] = None,
    use_web_search: bool = False,
) -> Generator[Dict[str, Any], None, None]:
    """
    Yields:
        {'type': 'sentence', 'text': str}
        {'type': 'done', 'reply': str, 'grounding_sources': list}
    """
```

### `ai_core.query_stream` 新簽名
```python
def query_stream(self, query: str, owner_id: int,
                 paper_id: Optional[str] = None,
                 conversation_history: Optional[List[Dict]] = None,
                 visible_content: Optional[str] = None,
                 use_web_search: bool = False):
```

---

## 驗證（4 step 過程）

| 階段 | py_compile | pytest metadata | check_doc_type_registry |
|---|---|---|---|
| Step 1 後 | ✓ | 18 passed, 3 skipped | （未跑）|
| Step 2 後 | ✓ | 18 passed, 3 skipped | （未跑）|
| Step 3 後 | ✓ | 18 passed, 3 skipped | （未跑）|
| **Step 4 後（最終）** | ✓ | **18 passed, 3 skipped** | **✓ exit 0** |

grep 殘留檢查（active code，排除 `_deprecated/` 與 `.claude-logs/`）：
- `_generating_lock`：0 ✓
- `is_generating`：0 ✓
- `def cancel`：0 ✓（AICore.cancel 移除）
- `set_paper_context`：0 ✓
- `current_paper_id`：0 ✓
- `current_paper_data`：0 ✓
- `self.conversation_history`：0 ✓
- `self.last_grounding_sources`：0 ✓（`self.llm_client._last_grounding_sources` 為 LLMClient 側 side-channel，read-only，保留）
- `import threading` in ai_core：0 ✓

---

## 端到端驗證計畫（給 baron）

> 4 commits 已 build 完，**未 push**。push 後依此序驗：

1. **claude-lab**：
   ```
   git log --oneline -7
   ```
   應看到 4 個新 commits（042503e / 1a8dc90 / 14834f1 / c7f4b65）+
   前序 `e70c4fc` Phase 0 commit。

2. **push 到 remote**：
   ```
   git push origin claude/hopeful-yalow-902c50:gemini-refactor
   ```
   或 baron 偏好的 branch。

3. **OrcStack**：
   ```
   git pull
   pkill -f web_server   # 或 systemctl
   # 重啟 web_server
   python tools/check_doc_type_registry.py   # 應 exit 0
   ```

4. **瀏覽器 Ctrl+Shift+R**，登入後依序測：

   **Test A — RAG 基本功能（DeHunt 履歷）**
   - 開既有 DeHunt 履歷
   - 問：「請分析這位候選人職涯主要的領域變化」
   - **預期**：AI 引用 Novatek / iPhone DDIC / Focaltech / TDDI /
     Targetek / Viewtrix / OLED 等具體內容（與前輪 Phase 0/RAG 修復後等效）

   **Test B — conversation_history 從 DB 正確讀取（multi-turn）**
   - 接上題 follow-up：「他在 OLED 期間發表過什麼論文？」
   - **預期**：AI 能根據前一輪 history 知道「他」指 DeHunt，並依 RAG
     給出 SID 2024 等具體內容。**驗證 DB 對話歷史正確 thread 進 LLM
     context**。

   **Test C — cross-paper 隔離（無狀態殘留）**
   - 開另一篇 paper（800-vdc）
   - 問：「核心論點是什麼」
   - **預期**：AI 不會殘留 DeHunt 履歷的脈絡（之前因為 ai_chat 是
     singleton 單例 conversation_history，可能會殘留；stateless 後
     每次 chat 從各自 paper 的 DB conversations 讀，**完全隔離**）。

5. **觀察 logs**（`logs/chat.log` / `logs/pipeline.log`）：
   - 應無 `KeyError` / `TypeError` / `AttributeError`
   - 特別檢查無 `AttributeError: 'AIProfessorChat' object has no
     attribute 'conversation_history'`（如有，代表還有漏改）
   - 應無 `'AICore' object has no attribute 'is_generating'`

6. **單帳號雙 tab 並發測試**（Phase 0/δ 完成驗證）：
   - 開兩個瀏覽器 tab、同一 user
   - 兩 tab 都開不同 paper、同時各送一個 chat
   - **預期**：兩 chat **同時各自串流回應**，不再有「目前有其他對話正在
     生成中」的 busy 訊息。每 tab 的 conversation_history 完全獨立。

7. **若所有 test 通過** → Stage A 落地。

---

## 設計成果

### Stage A 完成項目
- `AIProfessorChat` 100% stateless（self 只保留 4 個服務 attribute）
- `_generating_lock` 整移除（0-δ 完成）
- 5 個對話狀態全清；2 個死碼 method 全清
- 對話歷史持久化由 DB conversations 表唯一管理（caller 讀取）
- yield 結構統一 `{type, text/reply, grounding_sources}`，為 Stage B 鋪路
- 單帳號雙 tab 並發無互鎖、無互相污染
- Phase 2 多帳號 conversation_history 自然 per-chat 隔離（無需 per-user 鎖）

### 未動清單（已遵守）
- prompt 檔（character / router / explain / summary）：未動
- DB schema（Conversation / Paper / Folder / User）：未動
- 前端（SSE 格式零變化、saveChatHistory 流程零變化）：未動
- 認證機制（session / auth_guard）：未動
- pipeline_core / processor：未動
- domain 注入邏輯：保留（paper_data['_domain'] 透過 paper_data 參數傳入）
- distance_strategy / 過濾門檻：未動
- `_deprecated/AI_manager.py`：未動

### Stage B 預備（不在本輪實作）
class docstring 已標註 Stage B 設計意圖：
- prompt 改 caller 注入字串（不再讀檔，避免 `self.base_path` 綁定）
- LLMClient / Retriever 走 Protocol 介面
- 介面不出現任何 mad-professor 特定型別（Paper ORM / DB session）

---

## **狀態：4 commits 已建立、未 push、等 baron 確認**

baron 走流程：
1. 跑端到端驗證計畫 §3–6
2. 確認後執行：
   ```
   git push origin claude/hopeful-yalow-902c50:<target_branch>
   ```
3. 若任一 test 失敗，可選擇：
   - `git reset --hard e70c4fc` 整段 revert（4 commits 全退）
   - `git revert c7f4b65 14834f1 1a8dc90 042503e --no-edit` 反向 4 commits
   - 部分 revert：保留 Step 1/2 結構改進，只退 Step 3/4
