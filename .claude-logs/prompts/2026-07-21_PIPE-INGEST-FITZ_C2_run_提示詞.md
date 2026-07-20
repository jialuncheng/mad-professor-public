# PIPE-INGEST-FITZ C2 Run 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：PIPE-INGEST-FITZ（F6、born-digital 文字層快速道 + 連字修復）
- **階段**：階段 4（執行 C2 — Ligature Repair）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 05:15 |
| **任務代號** | PIPE-INGEST-FITZ C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_C2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_C2_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`PIPE-INGEST-FITZ`
- **當前 Commit 代號**：`C2`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_plan.md  # 全局策略 plan（v2）
.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md  # 設計評審探索 spec
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

### 🛠️ 執行命令

請依 `tasks.md §8 C2 具體實作細節` 修改及建立代碼，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 `processor/md_cleaner.py`（A 軌共用，本案連字修復不得寫入或修改此檔，必須獨立於新模組）。
   - ⚠️ 本 Commit 僅限進行新模組與其單元測試之純加法建立，嚴禁於 `litedoc_pipeline` 等處進行任何接線（本階段仍維持零 runtime 影響）。
   - ⚠️ 嚴禁引入任何第三方字典/NLP 依賴。
   - ⚠️ **行數不變式**：連字修復必須採用「行內替換」的純函式實現，嚴禁增刪或折疊行，以保證與 downstream doc_structure 的行索引對齊。

2. **測試防線**（`tasks.md §6.2`）：
   - 建立 `tests/test_ligature_repair.py`，覆蓋：
     * 連字正修：`Pro1les -> Profiles`、`;rst -> first`、`de1ning -> defining`。
     * 雙閘守門（防誤殺）：`1st`、`2nd`、`v1`、`v1.2`、`M1 晶片`、中文行等合法數字與字串在過濾後維持不動。
     * 行數不變式斷言。
     * 系統字典缺失時，Lazy 快取的內建常見連字字彙兜底機制驗證（使用 monkeypatch 驗證）。
   - 執行 `pytest tests/` 確保全體通過（基線 831 passed 以上，零新 fail）。
   - 執行 `grep -rn "ligature_repair" pipelines/litedoc_pipeline.py processor/` 確保目前無任何接線。
   - 貼上驗收與 SOP 一致性核查（§6.4）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

本 commit 修改均為全新檔（`pipelines/ligature_repair.py` 與 `tests/test_ligature_repair.py`），**無須備份**既有代碼檔案。

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C2` 標記為 ✅ 已完成：`- ✅ C2 — Ligature Repair（連字修復純函式）`。
   - 將 `C3` 標記為 🟡 WIP：`- 🟡 WIP C3 — Litedoc P1 Gate Wiring（litedoc P1 閘門與修復接線）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_C2_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C2)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C2 新增的 2 個實體檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 `repair_ligatures` 純函式內如何通過「第一閘正則排查」與「第二閘詞形校正」雙防線以精確修復壞映射並杜絕誤殺）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C3）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（本 commit 新增檔、無須備份）

# 2. git add 清單（僅包含本次 C2 實質新增之代碼與新測試；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/ligature_repair.py
git add tests/test_ligature_repair.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST-FITZ_C2_msg.txt）
cat > /tmp/PIPE-INGEST-FITZ_C2_msg.txt << 'EOF'
BE-Refactor: PIPE-INGEST-FITZ C2 — Ligature Repair（連字修復純函式）

1. 新增 pipelines/ligature_repair.py，實作 repair_ligatures(text: str) -> str 純函式，以行內替換（行數不變式）修復 ToUnicode 字型映射缺陷。
2. 建立雙閘防誤防誤殺機制：第一閘為替換前對縮寫與版本號（\b\d+(st|nd|rd|th|s)?\b / v\d+）進行正則排除；第二閘為替換後使用系統字典（/usr/share/dict/words 一次性快取）及內建連字詞庫（profiles / first / defining 等）對候選連字（fi/fl/ff/ffi/ffl）進行有效性檢驗。
3. 新建 tests/test_ligature_repair.py，完整覆蓋壞字修復、數字版本防誤殺、行數不變式、以及字典缺席時兜底語意斷言。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST-FITZ_C2_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-21_PIPE-INGEST-FITZ_C2_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C3（必須等 baron 確認後另行下達 C3 提示詞）
- ❌ 修改任何未列入 C2 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
