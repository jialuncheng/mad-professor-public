# FITZ-HOTFIX-1 C2 Run 階段提示詞

- **歸檔日期**：2026-07-22（任務代號日期沿 2026-07-21）
- **任務**：FITZ-HOTFIX-1（fitz 路標題救回與雜訊通則修復）
- **階段**：階段 4（執行 C2 — P1 Meta & Noise Cleanup）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-22 12:43 |
| **任務代號** | FITZ-HOTFIX-1 C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C2_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-1`
- **當前 Commit 代號**：`C2`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_plan.md  # 全局策略 plan（v4）
.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

### 🛠️ 執行命令

請依 `tasks.md §8 C2 具體實作細節` 修改程式，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 `processor/pdf_processor.py`（MinerU 處理器）、`pipelines/section_engine.py`、`web_server.py` 等其他程式檔（C2 僅改動攝入引擎與 litedoc P1 部分）。
   - ⚠️ `ingestion_engine.py` 之 `mark_meta_lines` 與 `assemble` 改動必須為**純加法可選參數** `meta_values: Optional[Set[str]] = None`，預設值為 `None` 以確保其他管線（resume/slides/book 等）byte 等價回歸。
   - ⚠️ `litedoc_pipeline.py` 時序調整必須僅將唯讀的 `_extract_litedoc_metadata` 移到 `_build_tiles` 之前，其餘下游 synthetic 欄位（`_resolve_title` 與 `source_lang` 合成）消費位置保持不變，並將 `meta_values` 傳入 `_build_tiles` 中。
   - ⚠️ R7 數字為主短行清理必須接線於清洗步（`MarkdownCleaner().clean` 後、與 `repair_ligatures` 同段），且**行首為 `#`／`!`／`>`／`-`／`*`／`|` 之一律跳過**（防誤殺列表中 Markdown 語法行）。
   - ⚠️ R7 之數字判定必須精確採用 `re.match(r"^\d+([.,]\d+)*$", token)`，使包含字母的 token（如 `v1.2`, `M1`）不被視為數字，更保守防誤殺。

2. **測試防線**（`tasks.md §6.2`）：
   - 擴充 `tests/test_ingestion_engine.py` 與 `tests/test_litedoc_pipeline.py`，完整覆蓋：
     * R6 測試：對 `MARC ANDREESSEN AND MICHAEL MCGUINESS` 的變體（casefold 且去除符號）進行比對剝除，並斷言正文中含有 `Marc Andreessen` 句子的行不被誤殺。
     * R6 時序測試：撰寫呼叫順序斷言（利用 mock），驗證 `_extract_litedoc_metadata` 被呼叫的順序確實先於 `assemble`，且 `meta_values=None` 時等價回歸。
     * R7 測試：斷言 `53 82 Share` / `561` 獨行被剝除（改為空行），斷言 `Chapter 5` / 完整正文句保留，斷言 Markdown 語法行首（`- 1`, `# 1`, `![alt](src)`, `| 1 |`）均不被剝除，斷言 `v1.2` / `M1` 不計為數字。
   - 執行 `pytest tests/` 確保全體通過（基線 920 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查（§6.5）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份：

```bash
cp pipelines/ingestion_engine.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_ingestion_engine.py.bak
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_litedoc_pipeline.py.bak
cp tests/test_ingestion_engine.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_test_ingestion_engine.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C2` 標記為 ✅ 已完成：`- ✅ C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）`。
   - 將 `C3` 標記為 🟡 WIP：`- 🟡 WIP C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_C2_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C2)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C2 修改的 2 個實體檔案、2 個測試檔與備份的 4 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 `mark_meta_lines` 比對算法、`_extract_litedoc_metadata` 時序前移接點、呼叫端 `meta_values` 構造與 date 變體轉換、以及 R7 `clean_short_number_lines` 的過濾與守衛規則）
- §5 測試與 Grep 結果（貼上真實終端輸出，包含 R6/R7 相關單元測試與呼叫序驗證結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C3）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C2 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/ingestion_engine.py
git add pipelines/litedoc_pipeline.py
git add tests/test_ingestion_engine.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_ingestion_engine.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_test_ingestion_engine.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C2_test_litedoc_pipeline.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-HOTFIX-1_C2_msg.txt）
cat > /tmp/FITZ-HOTFIX-1_C2_msg.txt << 'EOF'
BE-Refactor: FITZ-HOTFIX-1 C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）

1. 於 pipelines/ingestion_engine.py 的 mark_meta_lines 與 assemble 增設可選參數 meta_values: Optional[Set[str]]，以純加法正規化比對（casefold 且去除非 alphanumeric 字元）來兜底剝除重播的 meta 行。
2. 於 pipelines/litedoc_pipeline.py 的 run_phase1 調整時序，將 _extract_litedoc_metadata 前移至 _build_tiles 之前執行，提取 meta 後組合 authors/date(含 date format 變體如 June 15)/publisher 正規化值集合，注入 _build_tiles 與 assemble。
3. 實作 R7 數字為主短行清理：於清洗步新增 clean_short_number_lines，排除 Markdown 語法行首（#-!>|），對 token 長度 <=3 且數字 token（比對 ^\d+([.,]\d+)*$）過半的行進行剝除。
4. 擴充 tests/test_ingestion_engine.py 與 tests/test_litedoc_pipeline.py，涵蓋 meta_values 比對剝除、時序呼叫順序模擬斷言、以及 R7 短行過濾與 markdown 語法防誤殺守衛。
EOF

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-1_C2_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-21_FITZ-HOTFIX-1_C2_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C3（必須等 baron 確認後另行下達 C3 提示詞）
- ❌ 修改任何未列入 C2 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
