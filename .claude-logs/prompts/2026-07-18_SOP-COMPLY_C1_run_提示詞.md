# 2026-07-18 — SOP-COMPLY C1 提示詞

> **收到時間**：2026-07-18 05:17（UTC+8）
> **任務代號**：SOP-COMPLY C1
> **觸發 commit**：SOP-COMPLY C1（Logging Hardening）
> **相關產出檔案**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_C1_執行.md`
> **觸發情境**：SEC-HARDEN 收官後，baron 下達 SOP-COMPLY（logging 與 DB SOP 合規清帳）首個 Commit——C1 日誌合規補齊：9 檔業務碼 except 區 25 處 `logger.error` 補 `exc_info=True` + `llm/client.py:181` 吞例外改 warning 留痕 + 新建 AST 守衛測試 `tests/test_sop_comply_guard.py` 防回歸；BE-Refactor 工作流、依 tasks §8 實作、執行報告暫存 baton/。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-18 05:17 |
| **任務代號** | SOP-COMPLY C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-18_SOP-COMPLY_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-18_SOP-COMPLY_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`SOP-COMPLY`
- **當前 Commit 代號**：`C1`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md  # 全局策略 plan
.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🛠️ 執行命令

請依 `tasks.md §8 C1 具體實作細節` 進行代碼修改，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁改動 logger.error 訊息文字語意與控制流本身，僅限補上 `exc_info=True`。
   - ⚠️ 嚴禁對「非-except 區塊的守衛日誌」（例如 `rag_retriever.py:96` 等）加載 `exc_info`。
   - ⚠️ 嚴禁改動 `llm/client.py` 中除了 L181 吞例外以外的任何程式碼。

2. **測試防線**（`tasks.md §6.1`）：
   - 修改完成後，建立 `tests/test_sop_comply_guard.py`（AST 守衛測試），驗證業務程式碼 except 區內的 `logger.error` 全數含有 `exc_info` 以防止日後回歸。
   - 執行 `pytest tests/` 確保全體通過（無 regression），並貼上驗收與 SOP 一致性核查（§6.5）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改 10 檔既有檔案前，必須先執行備份：

```bash
cp AI_professor_chat.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_AI_professor_chat.py.bak
cp processor/extra_info_processor.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_extra_info_processor.py.bak
cp pipeline_core.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_pipeline_core.py.bak
cp ai_core.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_ai_core.py.bak
cp rag_retriever.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_rag_retriever.py.bak
cp processor/rag_processor.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_rag_processor.py.bak
cp processor/resume_processor.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_resume_processor.py.bak
cp web_server.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_web_server.py.bak
cp paper_manager.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_paper_manager.py.bak
cp llm/client.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_client.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C1` 標記為 ✅ 已完成：`- ✅ C1 — Logging Hardening（日誌合規補齊）`。
   - 將 `C2` 標記為 🟡 WIP：`- 🟡 WIP C2 — Self-Owned Transaction Guard（自持交易守護）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_C1_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C1)`，Git hash 留空由 baron 回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（需包含備份的 10 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 修法說明（附關鍵代碼片段）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C2）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C1 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add AI_professor_chat.py
git add processor/extra_info_processor.py
git add pipeline_core.py
git add ai_core.py
git add rag_retriever.py
git add processor/rag_processor.py
git add processor/resume_processor.py
git add web_server.py
git add paper_manager.py
git add llm/client.py
git add tests/test_sop_comply_guard.py
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_AI_professor_chat.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_extra_info_processor.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_pipeline_core.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_ai_core.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_rag_retriever.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_rag_processor.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_resume_processor.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_web_server.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_paper_manager.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C1_client.py.bak

# 3. commit message 草稿（已寫入 /tmp/SOP-COMPLY_C1_msg.txt）
cat > /tmp/SOP-COMPLY_C1_msg.txt << 'EOF'
BE-Refactor: SOP-COMPLY C1 — Logging Hardening（日誌合規補齊）

1. 補齊 9 檔業務程式碼 except 區內共計 25 處 logger.error 的 exc_info=True 參數，以完整保留異常 traceback。
2. 修改 llm/client.py:181 處對 grounding 來源解析的 exception 靜默吞例外，改為 logging.warning(..., exc_info=True) 留痕降級。
3. 建立 tests/test_sop_comply_guard.py，利用 AST 靜態掃描確保全域 except 塊內的 logger.error 接合 exc_info，作為 Grep-gate 防回歸測試。
EOF

# 4. baron 手動執行
git commit -F /tmp/SOP-COMPLY_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-18_SOP-COMPLY_C1_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C2（必須等 baron 確認後另行下達 C2 提示詞）
- ❌ 修改任何未列入 C1 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ✅ 完成（C1 落地、未 commit·由 baron 手動）
- pytest baseline 745 passed → final **748 passed / 3 skipped / 0 failed**（+3 AST 守衛測試）
- 改動：9 檔 25 處 except 內 logger.error 補 exc_info（AST 位元組精確插入·訊息零動）+ llm/client.py:181 吞例外改 warning + 新 tests/test_sop_comply_guard.py + 10 `.bak`
- 範圍外發現：`tools/regen_rag.py:252` 同類違規（tools/ 非清帳範圍·不動·報告 §4.3 提請 baron）
- hash 自癒：SEC-HARDEN checkout `e287347` 雙源回填；全庫佔位符歸零
- 執行報告：`.claude-logs/baton/2026-07-18_SOP-COMPLY_C1_執行.md`；msg 草稿 `/tmp/SOP-COMPLY_C1_msg.txt`
- commit / push：未執行（依 CLAUDE.md §1.3 待 baron）

## 後續引用

- 無
