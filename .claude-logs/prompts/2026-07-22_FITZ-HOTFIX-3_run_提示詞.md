# FITZ-HOTFIX-3 Run 階段提示詞

- **歸檔日期**：2026-07-23（任務代號日期沿 2026-07-22）
- **任務**：FITZ-HOTFIX-3（同位重繪去重、chrome 線索回收與 full_text meta 歸零）
- **階段**：階段 4（執行 HOTFIX-3 單一熱修補）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-23 06:53 |
| **任務代號** | FITZ-HOTFIX-3 |
| **觸發 Commit** | HOTFIX-3 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md` |
| **觸發情境** | baron 確認熱修復 plan 後，下達執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-3_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-3_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-3`
- **當前 Commit 代號**：`HOTFIX-3`
- **工作流類別**：`BE-Hotfix`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-22_FITZ-HOTFIX-3_同位重繪去重與chrome線索回收_hotfix.md  # 本次執行的依據 hotfix 任務
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

### 🛠️ 執行命令

請依 `hotfix.md 熱修復修法` 修改程式，並嚴格遵守以下防線：

1. **物理防線**（`hotfix.md 不可動清單`）：
   - ⚠️ 嚴禁更動 `processor/md_cleaner.py`（浮水印規則本體與閾值）、`pipelines/image_filter.py`、`pipelines/ingestion_engine.py`、`processor/rag_indexer.py` 等其他程式檔（本 Hotfix 僅改動 `processor/fitz_processor.py`、`pipelines/litedoc_pipeline.py` 及對應測試檔）。
   - ⚠️ K1 同位重繪去重 `dedup_key` 判定必須以頁為單位獨立初始化，只過濾**同頁同座標同字級同文字**的重疊行，嚴禁干涉跨頁重複 chrome 剝除判定（R2）。
   - ⚠️ K2 提示詞線索回收寫入 sidecar 時，檔名基準必須使用 `{pdf_file.stem}_source_hints.json`（嚴禁使用 `ctx.paper_id`，防範影子軌後綴污染）。
   - ⚠️ K2 注入 `_extract_litedoc_metadata` 時，`hints` 必須做為獨立參數傳入，且必須在**文首 4000 字元截斷之後**進行拼接，以防 hints 因長文截斷而靜默失效。
   - ⚠️ K3 `full_text` 行級 meta 歸零必須掛載在 `_read_source_text` 之後、**`echo-strip` 與 R8（圖片過濾）之前**，以保證與 sidecar 行號基準完全對齊。值比對必須為整行相等（ alphanumericcasefold）且排除圖片行，以防誤殺正文。

2. **測試防線**（`hotfix.md §regression`）：
   - 擴充 `tests/test_fitz_processor.py` 與 `tests/test_litedoc_pipeline.py`，完整覆蓋：
     * K1 測試：構造同頁同座標文字副本 fixture，斷言去重後僅剩 1 份；構造不同座標同文字行，斷言全保留；整合測試驗證經去重後標題成功存活（浮水印規則放行）。
     * K2 測試：驗證 `chrome_urls` 回收至 JSON 檔，模擬 `ctx.paper_id` 帶有 `_shadow` 後綴仍能成功加載，並設計**截斷窗斷言**（構造 >4000 字文字，斷言 `hints` 的 URL 仍在 messages 內）。
     * K3 測試：以 SpaceX 真實 meta 洩漏行做為測試靶，斷言 `en_text` 中 meta 行成功剝除，且正文提及作者行保留；設計**順序斷言**（以 mock 斷言 K3 先於 echo-strip 與 R8 執行）；設計**雙語文字對稱斷言**（`final_en` 與 `final_zh` 文字 meta 均為空對稱）。
   - 執行 `pytest tests/` 確保全體通過（基線 968 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份：

```bash
cp processor/fitz_processor.py .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_fitz_processor.py.bak
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_litedoc_pipeline.py.bak
cp tests/test_fitz_processor.py .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_test_fitz_processor.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `TODO.md` 最上方進度表中的 `FITZ-HOTFIX-3` 熱修復項目標記為 ✅ 已完成。
   - 更新進度表下方的狀態及類別索引。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-3_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit HOTFIX-3)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格（填寫 HOTFIX-3 Commit 資訊，留空 Hash）
- §3 變動檔案清單（含修改的 2 個實體檔案、2 個測試檔與備份的 4 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 K1 幾何去重算法、K2 截斷窗外 hints 注入、以及 K3 full_text 行級 meta 歸零的雙判據與掛載時序細節）
- §5 測試與 Grep 結果（貼上真實終端輸出，包含去重、線索回收與 K3 雙語文字對稱的 pytest 結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 checkout 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 HOTFIX-3 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add processor/fitz_processor.py
git add pipelines/litedoc_pipeline.py
git add tests/test_fitz_processor.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_test_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-3_test_litedoc_pipeline.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-HOTFIX-3_msg.txt）
cat > /tmp/FITZ-HOTFIX-3_msg.txt << 'EOF'
BE-Hotfix: FITZ-HOTFIX-3 — Overlap Dedup, Chrome Hint & Meta Zeroing（同位重繪去重、chrome 線索回收與 full_text meta 歸零）

1. 於 processor/fitz_processor.py 實作 K1 同位重繪去重：逐頁記錄看過的 bbox 坐標與字重複合 key，過濾列印 text-stroke 同座標重繪副本，防止 md_cleaner 浮水印規則誤殺 NHK 真標題。
2. 實作 K2 chrome URL 線索回收：在 fitz 剝除 chrome 時捕獲 URL 線索並落 source_hints sidecar JSON；於 pipelines/litedoc_pipeline.py 的 P3 加載線索並在 cover-prompt 4000 字元截斷窗之後拼接，補回 publisher NHK。
3. 實作 K3 full_text 行級 meta 歸零：於 P3 full_text 讀取後、echo-strip/R8 之前，依 sidecar 判型行號與 meta 值整行 alphanumeric 比對進行行級 meta 行剝除，防止 en_text 與 whole/is_zh 模式中原文 meta 洩漏，恢復雙語文字對稱不變式。
4. 擴充 tests/test_fitz_processor.py 與 test_litedoc_pipeline.py，完整覆蓋幾何去重、側邊 sidecar URL 加載、LLM 截斷 window 注入、K3 時序順序斷言與雙語文字對稱性斷言。
EOF

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-3_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-22_FITZ-HOTFIX-3_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達 checkout 提示詞）
- ❌ 修改 any 未列入 HOTFIX-3 實作細節的代碼 or 文件
- ❌ 自發執行 `git commit` 或 `git push`
