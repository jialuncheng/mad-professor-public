# PIPE-INGEST C1 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-19 18:32 |
| **任務代號** | PIPE-INGEST C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-19_PIPE-INGEST_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-19_PIPE-INGEST_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`PIPE-INGEST`
- **當前 Commit 代號**：`C1`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-18_PIPE-INGEST_litedoc攝入自有化與品質根治_plan.md  # 全局策略 plan（v4）
.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md  # 設計評審探索 spec (v4定案選1)
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🛠️ 執行命令

請依 `tasks.md §8 C1 具體實作細節` 新增模組與測試，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 A 軌處理器（`processor/md_processor.py`、`processor/json_processor.py`）與 `pipelines/section_engine.py` 的代碼。
   - ⚠️ 嚴禁在 C1 階段與 litedoc 管線接線（`litedoc_pipeline.py` 仍需走舊鏈），本 Commit 必須是**純加法**新模組，零 runtime 行為變化。
   - ⚠️ 嚴禁在 `ingestion_engine.py` 中寫入任何 `doc_type` 字面量（如 `'litedoc'`、`'resume'` 等），以保持純粹的文體無關性與高繼承能力。
   - ⚠️ 嚴禁向 litedoc `InjectionContext.constraints` 注入 interim 括號/術語約束（定案移交 GLOSSARY-TERMMAP）。

2. **測試防線**（`tasks.md §6.1`）：
   - 建立並充實 `tests/test_ingestion_engine.py`，完整覆蓋：title 抽取、非連續型 meta 塊分離、soft-fail 容錯、figure content 重建與 caption 關聯、LaTeX/Table 結構、層級棧組裝、**零 doc_type 靜態掃描斷言**、以及與 `TilingProcessor` 接口相容斷言。
   - 執行 `pytest tests/` 確保全體通過（基線 748 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查（§6.5）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

- 本 Commit 僅**全新建立** `pipelines/ingestion_engine.py` 與 `tests/test_ingestion_engine.py`，不更動任何既有業務與測試檔案，故**無需進行備份備檔**。

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C1` 標記為 ✅ 已完成：`- ✅ C1 — Ingestion Engine（攝入引擎本體）`。
   - 將 `C2` 標記為 🟡 WIP：`- 🟡 WIP C2 — Litedoc P1 Switchover（litedoc P1 切換攝入引擎）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-19_PIPE-INGEST_C1_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C1)`，Git hash 留空由 baron 回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（僅包含新增的 2 個實體檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 實作說明（附關鍵代碼片段）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C2）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（本 Commit 僅新增，無需備份）

# 2. git add 清單（僅包含本次 C1 實質新增之模組與測試；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/ingestion_engine.py
git add tests/test_ingestion_engine.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST_C1_msg.txt）
cat > /tmp/PIPE-INGEST_C1_msg.txt << 'EOF'
BE-Refactor: PIPE-INGEST C1 — Ingestion Engine（攝入引擎本體）

1. 新增 B 軌自有攝入組裝引擎 pipelines/ingestion_engine.py，支援 title 提取、meta 欄位與正文分離（不受行連續性限制）、figure Markdown content 重建與 caption 關聯，且產出與 TilingProcessor 介面相容之 section 樹。
2. 秉持引擎設計紀律，模組中絕不寫入 doc_type 字面量，一律採用參數注入方式以利 academic/book 繼承。
3. 新增 tests/test_ingestion_engine.py 覆蓋引擎所有邊界與 soft-fail 容錯規格，並包含 doc_type 靜態掃描防護與 tiling 相容性測試。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-19_PIPE-INGEST_C1_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C2（必須等 baron 確認後另行下達 C2 提示詞）
- ❌ 修改 any 未列入 C1 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
