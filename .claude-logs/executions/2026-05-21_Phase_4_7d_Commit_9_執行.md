# Phase 4.7d Commit 9 — 執行報告（cleanup_orphaned 同步清記憶體 cache）

> 基準：`1a605fa`（Phase 4.7d Commit 8）
> 完成：本地改檔完成，**尚未 commit、未 push**

---

## Commit Hash

**尚未 commit**——依 baron 指示，純改檔、等確認後再決定何時 commit。

| # | Hash | Subject |
|---|---|---|
| 9 | _（pending）_ | fix(cleanup): cleanup_orphaned 同步清記憶體 cache |

---

## diff stat（uncommitted）

```
 paper_manager.py | 23 +++++++++++++++++++++--
 web_server.py    | 13 +++++++++++--
 2 files changed, 32 insertions(+), 4 deletions(-)
```

---

## 真因

baron 盤點清理功能後發現「鬼魂 paper」風險：

### 單一刪除（`DELETE /api/papers/{id}`）：完整清理
- 檔案目錄、papers DB、conversations cascade、processing_tasks、ai_core._paper_cache、retriever 三 dict（vector_stores / paper_vector_paths / rag_trees）

### 清理殘檔（`POST /api/cleanup`）：**只刪檔案、沒清記憶體**
- `paper_manager.cleanup_orphaned` (L295-312) 只跑 `shutil.rmtree`
- 不清 `processing_tasks` / `ai_core._paper_cache` / retriever 三 dict

### 鬼魂 paper 觸發路徑
1. paper 上傳跑壞、pipeline 中途呼叫 `paper_manager.load_paper_resources` → ai_core / retriever 已有 cache
2. pipeline 最終失敗、DB 沒寫進 papers row、檔案留下成殘檔
3. user 點「清理殘檔」→ 檔案刪了、但 cache 還在
4. AI 對話時還記得這個 paper、vector 路徑指向已刪目錄 → 後續查詢炸 / 給亂結果

---

## 修法

### 1. `paper_manager.cleanup_orphaned`（L295-330）

- 簽名加 optional `ai_core=None` 參數
- docstring 註明 Phase 4.7d Commit 9 的「同步清 cache」契約
- 每筆殘檔 `shutil.rmtree` 後，若 `ai_core is not None` → 呼叫 `ai_core.remove_paper(owner_id, item.name)`
- soft try / except：失敗只 log warning、不中斷整批清理
- 成功 log：`清理殘檔 cache 完成: owner={owner_id} {item.name}`
- `processing_tasks` 由 caller 負責清（不傳進 paper_manager，因 paper_manager 不該知道 web_server 內部 state）

複用 `ai_core.remove_paper(owner_id, paper_uuid)` 既有實作（ai_core.py:99），已 cover：
- `_paper_cache.pop((owner_id, paper_uuid))`
- `retriever.remove_paper(owner_id, paper_uuid)`（內部清 vector_stores / paper_vector_paths / rag_trees 三 dict）

### 2. `web_server` `/api/cleanup` endpoint（L582-595）

- 改傳 `ai_core=ai_core` 給 `paper_manager.cleanup_orphaned`
- 殘檔清完後加一段：
  ```python
  if removed:
      with tasks_lock:
          for paper_uuid in removed:
              processing_tasks.pop((current_user.id, paper_uuid), None)
  ```
- docstring 註明同步清 ai_core._paper_cache + retriever 三 dict + processing_tasks

---

## 不可動清單（已遵守）

- [x] `ai_core.remove_paper`：未動（既有實作已完整）
- [x] `rag_retriever.remove_paper`：未動（既有實作已完整）
- [x] DB schema：未動
- [x] 前端：未動
- [x] `delete_paper` 單一刪除路徑：未動（caller `web_server.delete_paper` endpoint 自行 cover）
- [x] `_deprecated/`：未動
- [x] 未引入新 CDN / 套件
- [x] 本 commit 未新增測試（diff 純函式內部改動）

---

## 端到端驗證計畫（給 baron）

### 1. 確認本地改動

```bash
git diff --stat
# 應看到：
# paper_manager.py | 23 ++++++--
# web_server.py    | 13 ++++--
```

### 2. 確認改動內容

```bash
git diff paper_manager.py web_server.py
```

### 3. 靜態驗證

```bash
venv/bin/python -m py_compile paper_manager.py web_server.py
venv/bin/pytest tests/ -q      # 應 75 passed 3 skipped（無新增測試、既有不應受影響）
```

### 4. OrcStack 部署後手動驗證（端到端）

```bash
# 改檔完成、commit 後：
# git push origin HEAD:gemini-refactor
# git pull on OrcStack
pkill -f web_server
# 重啟
```

#### Test A — 鬼魂 paper 復現與修復
1. 上傳一份故意會失敗的 paper（或在 pipeline 中途斷網）→ 製造殘檔
2. 觀察 logs/pipeline.log：確認 `paper_manager.load_paper_resources` 已被呼叫（ai_core / retriever 已 cache）
3. 點前端「清理殘檔」按鈕
4. 預期 logs/pipeline.log（新增的 log 行）：
   - `清理殘餘目錄: {owner_id}/{paper_uuid}`
   - `清理殘檔 cache 完成: owner={owner_id} {paper_uuid}`
5. 開 AI 對話、嘗試引用該 paper：
   - 預期：找不到（rag_retriever 已清）
   - **不應**：拿到亂結果或炸 FileNotFoundError

#### Test B — 殘檔目錄存在但 cache 無資料
- 手動建一個 `output/{owner_id}/dummy-uuid/` 空目錄（不跑 pipeline）
- 點清理殘檔
- 預期：`shutil.rmtree` 刪檔成功；`ai_core.remove_paper` no-op（key 不在 cache）但**不炸**
- 預期 logs：`清理殘檔 cache 完成` 仍 log（remove_paper 不會 raise）

#### Test C — 沒殘檔
- 點清理殘檔（無待清項目）
- 預期：`removed=[]`、不動 cache / tasks、不 log 任何清理訊息

### 5. logs / console（不應出現）
- `AttributeError: ... 'remove_paper'`（簽名不對）
- `TypeError: cleanup_orphaned() got an unexpected keyword argument 'ai_core'`
- 後續對話時的 `FileNotFoundError` / `KeyError` 指向已刪 paper

---

## 回退方式

未 commit、直接：
```bash
git checkout paper_manager.py web_server.py
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
git add paper_manager.py web_server.py
git commit -m "..."
```
（不要 `git add .` 連同 `.DS_Store` 一起 stage——該檔是先前已存在的本地噪音、非本次改動。）
