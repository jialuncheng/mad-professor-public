# FITZ-ANCHOR C1 Run 階段提示詞

- **歸檔日期**：2026-07-23
- **任務**：FITZ-ANCHOR（LLM 錨定前移與 fitz 幾何整形）
- **階段**：階段 4（執行 C1 — Fitz Geometry Refinement）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-23 11:35 |
| **任務代號** | FITZ-ANCHOR C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md` |
| **觸發情境** | baron 確認任務 tasks 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-ANCHOR`
- **當前 Commit 代號**：`C1`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md  # 全局策略 plan（v2）
.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

### 🛠️ 執行命令

請依 `tasks.md §8 C1 具體實作細節` 修改程式，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 `processor/pdf_processor.py`（MinerU 處理器）、`pipelines/section_engine.py`、`pipelines/litedoc_pipeline.py`、`pipelines/ingestion_engine.py` 等其他程式檔（C1 必須高度內聚於 fitz 幾何整形改動）。
   - ⚠️ K1′ ε 容差去重邏輯在 `_collect_page` 中實作時，對重疊行的比對必須以**頁**為單位獨立初始化，且必須精確控制在 `(text, round(size, 1))` 同群組下，x0/y0 的偏移容差 |dx| ≤ ε 且 |dy| ≤ ε（ε 讀自 `settings.FITZ_DEDUP_EPSILON`）。
   - ⚠️ `_repeated_band_keys` 跨頁重複剝除的比例門檻必須改為 `need = max(2, math.ceil(len(pages) * 0.5))`，下限設為 2 以完全相容 2-3 頁極短 PDF 的現行行為。

2. **測試防線**（`tasks.md §6.1`）：
   - 擴充 `tests/test_fitz_processor.py`，完整覆蓋：
     * U4 容差去重測試：構造帶有 ±0.84pt 的同頁 4 個重疊行副本，斷言其去重後僅存 1 份；構造 3pt 外的同頁同文字行，斷言其全被保留；跨頁同文字同座標則不誤合。
     * U5 比例門檻測試：構造 10 頁 PDF，在頂部 band 出現 10/10 次的行被判定為 chrome 並剝除，僅出現 2/10 次的內容段落行被判定為非 chrome 並完整保留；同時驗證 2 頁 PDF 的等價回歸。
     * **§3.1 模擬表全項轉正式測試**：利用 fitz 動態構造含有「描邊 ×4 標題與 Q 行」的 PDF 實體，斷言經處理與真 `MarkdownCleaner().clean` 清洗後，標題 heading 存活 ×1、14 組 QA 完整成對且無殘缺、且 `(3 次)` / `(4 次)` 的浮水印誤殺告警零觸發。
   - 執行 `pytest tests/test_fitz_processor.py` 與 `pytest tests/` 確保全體通過（基線 993 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份：

```bash
cp processor/fitz_processor.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_fitz_processor.py.bak
cp tests/test_fitz_processor.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_test_fitz_processor.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C1` 標記為 ✅ 已完成：`- ✅ C1 — Fitz Geometry Refinement（fitz 幾何整形與容差去重）`。
   - 將 `C2` 標記為 🟡 WIP：`- 🟡 WIP C2 — Meta Anchor & Title Reinjection（LLM 錨定前移、標題回注與 sidecar 退場）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-23_FITZ-ANCHOR_C1_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C1)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C1 修改的 1 個實體檔案、1 個測試檔、1 個 settings 常數、1 個 .env.example 檔與備份的 2 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 U4 容差去重算法的坐標聚類實現、以及 U5 跨頁 chrome 剝除改為比例門檻的判定方式）
- §5 測試與 Grep 結果（貼上真實終端輸出，包含 R1 容差去重與 NHK 模擬 fixture 之 pytest 結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C2）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C1 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add settings.py
git add .env.example
git add processor/fitz_processor.py
git add tests/test_fitz_processor.py
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C1_test_fitz_processor.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-ANCHOR_C1_msg.txt）
cat > /tmp/FITZ-ANCHOR_C1_msg.txt << 'EOF'
BE-Refactor: FITZ-ANCHOR C1 — Fitz Geometry Refinement（fitz 幾何整形與容差去重）

1. 於 settings.py 新增 FITZ_DEDUP_EPSILON = 3.0 常數，於 .env.example 中補註解。
2. 於 processor/fitz_processor.py 的 _collect_page 實作 U4 容差同位去重，同頁內同 (text, round(size,1)) 且 x0/y0 坐標距離 <= 3.0pt 的重疊行視為 text-stroke 描邊副本並予以去重，防標題被 md_cleaner 浮水印規則誤殺。
3. 實作 U5 跨頁重複比例門檻：將 _repeated_band_keys 判定門檻由常數 >=2 改為 >= max(2, math.ceil(len(pages) * 0.5))，保護少數頁重複之內容段落不被當作 chrome 頁首尾誤殺。
4. 擴充 tests/test_fitz_processor.py，涵蓋 epsilon 坐標容差去重、chrome 比例門檻劃分、以及 NHK 標題與 QA 對位模擬重演實體 PDF fixture 測試。
EOF

# 4. baron 手動執行
git commit -F /tmp/FITZ-ANCHOR_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-23_FITZ-ANCHOR_C1_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C2（必須等 baron 確認後另行下達 C2 提示詞）
- ❌ 修改任何未列入 C1 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
