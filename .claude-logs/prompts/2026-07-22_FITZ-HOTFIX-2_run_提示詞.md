# FITZ-HOTFIX-2 Run 階段提示詞

- **歸檔日期**：2026-07-22
- **任務**：FITZ-HOTFIX-2（報頭行界收窄與雙語圖片對稱）
- **階段**：階段 4（執行 HOTFIX-2 單一熱修補）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-22 17:00 |
| **任務代號** | FITZ-HOTFIX-2 |
| **觸發 Commit** | HOTFIX-2 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md` |
| **觸發情境** | baron 確認熱修復 plan 後，下達執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-22_FITZ-HOTFIX-2_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-2`
- **當前 Commit 代號**：`HOTFIX-2`
- **工作流類別**：`BE-Hotfix`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_plan.md  # 全局策略 plan
.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_報頭行界收窄與雙語圖片對稱_hotfix.md  # 本次執行的依據 hotfix 任務
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

### 🛠️ 執行命令

請依 `hotfix.md 熱修復修法` 修改程式，並嚴格遵守以下防線：

1. **物理防線**（`hotfix.md 不可動清單`）：
   - ⚠️ 嚴禁更動 `pipelines/image_filter.py`（三規則本體與門檻）、`processor/fitz_processor.py`、`pipelines/ingestion_engine.py`、`processor/rag_indexer.py` 等其他程式檔（本 Hotfix 僅改動 `pipelines/litedoc_pipeline.py` 單檔與對應測試）。
   - ⚠️ K1 報頭型別判定集合必須與 `mark_meta_lines` 同源（複用類別變數 `LiteDocPipeline._META_TYPES` 並與 `{"title"}` 做聯集），以防兩端常數漂移（drift）。
   - ⚠️ K2 `_filter_source_figures` 定位 sidecar 時，**嚴禁**以 `ctx.paper_id` 直接拼接檔名（因影子軌帶有 `_shadow` 後綴而實體檔沒有）。必須採用三級定位：首先嚐試 `Path(ctx.pdf_path).stem` 主路，其次以 `sorted(output_dir.glob("*_doc_structure.json"))` 備路 glob 檢索，最後以空集合 `set()` fail-open 兜底以保證雙語圖片對稱性同步停用。

2. **測試防線**（`hotfix.md §regression`）：
   - 擴充 `tests/test_litedoc_pipeline.py`，完整覆蓋：
     * K1 測試：以 SpaceX v3 的真實 `doc_structure` 做 fixture，斷言 `hdr_end == 10`（而非 119）；並斷言無 meta 區塊時回傳空集合 `set()`。
     * K2 測試：模擬 R8 原文過濾時傳入 K1 的 `header_srcs`，斷言 meta 區內圖片被 DROP，而區外的封面大圖與正文 Falcon 9 照片被 KEEP。
     * 影子後綴測試：模擬 `ctx.paper_id` 帶有 `_shadow` 後綴，斷言 `_load_header_srcs` 能透過主/備路成功讀取不帶後綴的 sidecar json。
     * **對稱不變式斷言**：在單元測試中構造「規則③會殺」的 mock 判型環境與圖片行，斷言 `final_en` 輸出的圖片行集合與 `final_zh` 完全相同（證明雙通道規則③已對齊）。
   - 執行 `pytest tests/` 確保全體通過（基線 968 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份：

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_litedoc_pipeline.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `TODO.md` 最上方進度表中的 `FITZ-HOTFIX-2` 熱修復項目標記為 ✅ 已完成。
   - 更新進度表下方的狀態及類別索引。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-22_FITZ-HOTFIX-2_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit HOTFIX-2)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格（填寫 HOTFIX-2 Commit 資訊，留空 Hash）
- §3 變動檔案清單（含修改的 1 個實體檔案、1 個測試檔與備份的 2 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 K1 報頭行界收窄與 `_HEADER_META_TYPES` 同源實作、K2 圖片過濾 `_load_header_srcs` 中 glob 動態定位與 R8 補傳接線細節）
- §5 測試與 Grep 結果（貼上真實終端輸出，包含 `litedoc` 測試與對稱斷言 pytest 結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 checkout 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 HOTFIX-2 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-22_FITZ-HOTFIX-2_test_litedoc_pipeline.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-HOTFIX-2_msg.txt）
cat > /tmp/FITZ-HOTFIX-2_msg.txt << 'EOF'
BE-Hotfix: FITZ-HOTFIX-2 — Header Boundary Narrowing & Bilingual Figure Symmetry（報頭行界收窄與雙語圖片對稱）

1. 於 pipelines/litedoc_pipeline.py 實作 K1 報頭行界收窄：`_collect_header_srcs` 行界判定調整為僅計與 `mark_meta_lines` 同源之 meta 型塊（類別常數 `_META_TYPES` 與 `title` 聯集）的最末 end，回歸報頭設計本意，使 SpaceX 樣本 hdr_end 從 119 收窄為 10，救回封面大圖與 Falcon 9 降落照片。
2. 實作 K2 R8 過濾對稱性修正：於 `_filter_source_figures` (P3) 新增 `_load_header_srcs` 私有方法，透過 `Path(ctx.pdf_path).stem` 主路與 `glob("*_doc_structure.json")` 備路動態定位不帶後綴之 sidecar，讀取判型並注入 `make_figure_filter`，確保雙通道規則③ DROP 行動同步，恢復雙語圖片對稱性不變式。
3. 於 tests/test_litedoc_pipeline.py 新增測試覆蓋 K1 SpaceX v3 真實 sidecar 收窄、K2 影子軌 sidecar 定位與 R8 過濾、以及強大的雙語圖片對稱性斷言。
EOF

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-2_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-22_FITZ-HOTFIX-2_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達 checkout 提示詞）
- ❌ 修改任何未列入 HOTFIX-2 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
