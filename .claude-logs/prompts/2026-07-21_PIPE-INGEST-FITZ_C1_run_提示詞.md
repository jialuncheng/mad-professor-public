# PIPE-INGEST-FITZ C1 Run 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：PIPE-INGEST-FITZ（F6、born-digital 文字層快速道 + 連字修復）
- **階段**：階段 4（執行 C1 — Fitz Processor）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 05:13 |
| **任務代號** | PIPE-INGEST-FITZ C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_born-digital文字層快速道與連字修復_tasks.md` |
| **觸發情境** | baron 確認上一個 任務/Tasks 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_PIPE-INGEST-FITZ_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`PIPE-INGEST-FITZ`
- **當前 Commit 代號**：`C1`
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

請依 `tasks.md §8 C1 具體實作細節` 修改及建立代碼，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 `processor/pdf_processor.py` 與 `processor/md_cleaner.py`（A 軌共用，本案 byte 不動）。
   - ⚠️ 嚴禁在 C1 階段於 `pipelines/litedoc_pipeline.py` 進行任何接線（本 Commit 為純加法新模組建立與單元測試，全鏈零 runtime 變化）。
   - ⚠️ 嚴禁在 `FitzProcessor` 內讀取 `fitz.metadata`（例如 `/Title` 等檔案屬性），以確保元數據抽取 100% 依賴純文字覆蓋層（cover-prompt）的純正文規則。
   - ⚠️ Fitz 抽出的圖片必須**限制為 PNG/JPEG 落地**，並命名為 `page_{page_idx}_{xref}.{ext}` 以防止跨頁衝突，確保與 `image_filter` stdlib 尺寸解析的基準相容性。

2. **測試防線**（`tasks.md §6.1`）：
   - 建立 `tests/test_fitz_processor.py`，使用 fitz 程式化生成 born-digital 測試 PDF（零網路、零 MinerU 呼叫），驗證：同形 .md 產出契約（`\n\n` 段落分隔、`#`/`##` 標題級別推導）、閱讀序座標排序、跨頁重複頁首尾剝除、圖片 PNG/JPEG 限定與檔名唯一性、`median_page_chars` 閘門輔助方法、以及壞檔 `PDFParseError` 異常型別拋出。
   - 執行 `pytest tests/` 確保全體通過（基線 831 passed 以上，零新 fail）。
   - 執行 `grep -rn "fitz_processor" pipelines/ web_server.py pipeline_core.py` 確保目前無任何接線。
   - 貼上驗收與 SOP 一致性核查（§6.4）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

本 commit 修改均為全新檔（`processor/fitz_processor.py` 與 `tests/test_fitz_processor.py`），**無須備份**既有代碼檔案。

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C1` 標記為 ✅ 已完成：`- ✅ C1 — Fitz Processor（Fitz 直抽處理器）`。
   - 將 `C2` 標記為 🟡 WIP：`- 🟡 WIP C2 — Ligature Repair（連字修復純函式）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-21_PIPE-INGEST-FITZ_C1_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C1)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C1 新增的 2 個實體檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 `FitzProcessor` 如何依據字級群推導標題、座標區塊排序、以及跨頁重複頂/底帶的頁首尾剝除邏輯）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C2）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（本 commit 新增檔、無須備份）

# 2. git add 清單（僅包含本次 C1 實質新增之代碼與新測試；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add processor/fitz_processor.py
git add tests/test_fitz_processor.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST-FITZ_C1_msg.txt）
cat > /tmp/PIPE-INGEST-FITZ_C1_msg.txt << 'EOF'
BE-Refactor: PIPE-INGEST-FITZ C1 — Fitz Processor（Fitz 直抽處理器）

1. 新增 processor/fitz_processor.py 繼承 PDFParser ABC 介面，履行其 parse(pdf_path, output_dir) 語意契約與 PDFParseError 異常規範。
2. 實作基於 PyMuPDF 的 born-digital PDF 本地文字直抽，包含座標塊閱讀序排序、字級分群推導標題等級（# / ##）、跨頁頂底帶重複行偵測以剝除列印頁首尾、以及原生 PNG/JPEG 落地與 unique 圖檔命名。
3. 建立 median_page_chars 模組級字元中位數統計輔助，作為後續攝入閘門依據。整個 FitzProcessor 保持零 fitz.metadata 檔案屬性讀取以防污染正文抽取。
4. 建立 tests/test_fitz_processor.py，程式化構造 born-digital PDF 測試 fixture，完整覆蓋同形 Markdown 契約、閱讀序、頁首尾清理、以及異常型別判定。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST-FITZ_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-21_PIPE-INGEST-FITZ_C1_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C2（必須等 baron 確認後另行下達 C2 提示詞）
- ❌ 修改 any 未列入 C1 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
