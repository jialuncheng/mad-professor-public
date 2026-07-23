# FITZ-ANCHOR C2 Run 階段提示詞

- **歸檔日期**：2026-07-23
- **任務**：FITZ-ANCHOR（LLM 錨定前移與 fitz 幾何整形）
- **階段**：階段 4（執行 C2 — Meta Anchor & Title Reinjection）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-23 12:02 |
| **任務代號** | FITZ-ANCHOR C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入提示詞歸檔檔 `.claude-logs/prompts/2026-07-23_FITZ-ANCHOR_C2_run_提示詞.md`（格式依 README §3）。
2. 更新 INDEX.md（對應分類補登 + `## 依時間排序` 首行插入、超過 15 筆刪最舊）。
3. 確認完成後回覆「✅ 提示詞已歸檔」。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-ANCHOR`
- **當前 Commit 代號**：`C2`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md`

### 📖 強制讀檔清單

```
CLAUDE.md
.claude-logs/ref/WORKFLOW_SOP.md
.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md（v2）
.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_tasks.md（§8 實作細節）
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md
.claude-logs/sop/2026-05-23_database_SOP_手冊.md
```

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3）

### 🛠️ 執行命令

依 `tasks.md §8 C2 具體實作細節` 修改程式，嚴守：

1. **物理防線**（tasks §7 不可動清單）：
   - 嚴禁更動 `processor/md_cleaner.py`（浮水印規則本體與閾值）、`pipelines/image_filter.py`、`pipelines/ingestion_engine.py` 等其他程式檔（C2 僅改 `pipelines/litedoc_pipeline.py`、`processor/fitz_processor.py` 寫端退場、`pipelines/section_engine.py` 守衛一行與各自測試檔）。
   - U1 錨定文字裸抽前 `settings.LITEDOC_ANCHOR_MAX_PAGES` 頁邏輯先定案；裸抽為空 fallback 現行 md 文首、100% 語意等價。
   - U2 標題回注接點於 P1 `_reinject_title`，在 cleaner/連字/R7 之後、**DocAnalyzer 判型之前**執行，就地升級 `# ` 行時避免重複標題注入。
   - U3 sidecar 退場於 `fitz_processor.py`（生產端）與 `litedoc_pipeline.py`（消費端）**同刀移除**，含 JSON 寫檔塊與 `_load_source_hints` 讀端，恢復 `_extract_litedoc_metadata` 為單參數。
   - U6 echo 守衛在 `pipelines/section_engine.py` 比對 `sa in sb or sb in sa` 時加 `min(len)/max(len) >= 0.5` 比例判定。

2. **測試防線**（tasks §6.2）：
   - U1：斷言錨定文字含裸文字與 chrome URL 行、空則等價 fallback、頁數截斷。
   - U2：覆蓋 heading 已在（不動）、正文行（promote 升級 + warning）、全文缺席（inject + warning）三分支，`title` 空白時跳過。
   - U3：移除舊 hints 產生與加載測試、斷言 sidecar 代碼完全清除、publisher 在裸文字 hints 注入下仍可正確解析。
   - U6：斷言 4 字 ⊂ 88 字（0.045 比值）不判回聲、整行相似照剝。
   - §7.2 跨 Phase 整合測試：以 C1 幾何整形為前段、實體 PDF（描邊標題/跨頁重複/chrome/頁尾 URL）經 `FitzProcessor` 直抽→`_reinject_title` 回注→Tiles 組裝至 P3 翻譯鏈，斷言標題存活、QA 成對、內容完整、meta 零重播、中英圖片與文字對稱。
   - `pytest tests/` 全綠（基線 993+、零新 fail），貼終端輸出 + SOP 核查。

3. **文件防線**（CLAUDE.md §1.3）：baton 暫存嚴禁 mv/git add；commit/push 由 baron 手動。

### 💾 備份規則

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_litedoc_pipeline.py.bak
cp processor/fitz_processor.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_fitz_processor.py.bak
cp pipelines/section_engine.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_section_engine.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_litedoc_pipeline.py.bak
cp tests/test_fitz_processor.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_fitz_processor.py.bak
cp tests/test_section_engine.py .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_section_engine.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填

1. C2 → ✅；checkout → 🟡 WIP。
2. 雙源 hash 自癒回填（TODO.md + archive/TODO_done_archive.md）。

### 📁 產出規格

- 執行報告 `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_C2_執行.md`（暫存 baton/）
- 套用 `.claude-logs/templates/template_execution.md`
- 含元數據塊（Completed (Commit C2)、hash 留空）/ §1-§8（§3 含 3 實體檔 + 3 測試檔 + settings 常數 + .env.example + 6 `.bak`；baton 報告 plan/tasks 不列 git add）

### 📝 §8 baron 執行命令格式

```bash
git add settings.py
git add .env.example
git add pipelines/litedoc_pipeline.py
git add processor/fitz_processor.py
git add pipelines/section_engine.py
git add tests/test_litedoc_pipeline.py
git add tests/test_fitz_processor.py
git add tests/test_section_engine.py
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_section_engine.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-23_FITZ-ANCHOR_C2_test_section_engine.py.bak
# commit message → /tmp/FITZ-ANCHOR_C2_msg.txt；baron 手動 git commit -F
```

### 🛑 停止指令

產出 `2026-07-23_FITZ-ANCHOR_C2_執行.md` 並更新 TODO.md 後必須立即停止。嚴禁繼續 checkout、改 C2 外代碼、自發 commit/push。
