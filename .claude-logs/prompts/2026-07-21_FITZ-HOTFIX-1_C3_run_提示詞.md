# FITZ-HOTFIX-1 C3 Run 階段提示詞

- **歸檔日期**：2026-07-22（任務代號日期沿 2026-07-21）
- **任務**：FITZ-HOTFIX-1（fitz 路標題救回與雜訊通則修復）
- **階段**：階段 4（執行 C3 — P3 Title & Figure Convergence）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-22 12:54 |
| **任務代號** | FITZ-HOTFIX-1 C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C3_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C3_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-1`
- **當前 Commit 代號**：`C3`
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

請依 `tasks.md §8 C3 具體實作細節` 修改程式，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 `processor/pdf_processor.py`（MinerU 處理器）、`pipelines/section_engine.py`、`pipelines/ingestion_engine.py`、以及 `web_server.py`（防重邏輯 `web_server.py:775` 已由 `SHADOW-HOTFIX-2` 落地，保持 byte 不動，本案零改）。
   - ⚠️ 翻譯譯題單元時，譯題第一參數必須改傳入去後綴的 `_title_bare`（現成 P3 變數），譯後若為影子軌且標題未帶後綴，才重新 append 一次 ` (測試)`。確保 LLM 不見後綴、防止多種後綴變體造成 web_server 防重失配。
   - ⚠️ R8 圖片過濾必須接線於 P3 `full_text = self._read_source_text(ctx)` 與 title echo strip 之後、`is_zh` 分支之前，以對 `full_text` 進行行級 `_FIGURE_RE` 的圖片判定過濾。
   - ⚠️ R8 過濾必須使用與 P1 `_build_tiles` **同一路徑基準**（`md_path.parent/"images"`），且在 `image_filter.py` 旗標關閉時整段 no-op，解析異常時 fail-open 保留，確保與現行架構零衝突。

2. **測試防線**（`tasks.md §6.3`）：
   - 擴充 `tests/test_litedoc_pipeline.py`，完整覆蓋：
     * R4 測試：斷言譯題單元輸入不含 ` (測試)`，成品中譯與原譯標題有且僅有唯一一個 ` (測試)` 後綴。
     * R8 測試：構造含有 4 張圖的 `full_text`（72×72×2 頭像、1456×5 分隔線、1456×1442 正文圖），啟用過濾時斷言 `final_en` 與 `final_zh` 中小圖均被剝除、僅剩正文圖；關閉 `IMG_FILTER_ENABLED` 時斷言四圖原樣保留（no-op 且 byte 等價）；過濾發生例外時 fail-open 全部保留。
     * **雙語圖片對稱性斷言**：在 section mode 下，強烈斷言 `final_en` 內文圖集與 `final_zh` 內文圖集完全相同，且等於 tiles 經過過濾後的圖集集合。
   - 執行 `pytest tests/` 確保全體通過（基線 920 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查（§6.5）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份：

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_litedoc_pipeline.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C3` 標記為 ✅ 已完成：`- ✅ C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）`。
   - 將 `checkout` 標記為 🟡 WIP：`- 🟡 WIP checkout — 成果收官歸檔（成果歸檔與移出暫存）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_C3_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C3)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C3 修改的 1 個實體檔案、1 個測試檔與備份的 2 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 R4 譯題 input 去測試後綴優化、以及 R8 圖片過濾掛載於 P3 `full_text` 對 is_zh/whole/en_text 通道與 RAG section 對稱性的治理細節）
- §5 測試與 Grep 結果（貼上真實終端輸出，包含 R4/R8 單元與雙語對稱測試結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 checkout 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C3 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C3_test_litedoc_pipeline.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-HOTFIX-1_C3_msg.txt）
cat > /tmp/FITZ-HOTFIX-1_C3_msg.txt << 'EOF'
BE-Refactor: FITZ-HOTFIX-1 C3 — P3 Title & Figure Convergence（P3 譯題與圖片過濾收斂）

1. 於 pipelines/litedoc_pipeline.py 實作 R4 譯題後綴防重：P3 L634 與 L647 兩處 translate_unit 參數改餵 _title_bare，LLM 翻譯時排除 (測試) 後綴，若為影子軌則於 P3 譯後重貼後綴，使 web_server 寫庫端 endswith 防重守衛精確生效一次，根治 (測試) (測試) 現象。
2. 實作 R8 P3 圖片過濾：於 P3 full_text 讀取與 title strip 後、is_zh 分支前，利用 image_filter 進行行級過濾，一次性剝除 is_zh、whole 與 en_text 等三通道原始 markdown 中被 DROP 的垃圾小圖。
3. 建立雙語圖片對稱性不變式，確保在 section 模式下，final_en 與 final_zh 輸出的圖片數量與內容完全對稱一致。
4. 擴充 tests/test_litedoc_pipeline.py，涵蓋譯題 input 去後綴驗證、R8 whole-mode 圖片行級過濾、關閉旗標等價回歸、以及雙語圖片對稱性斷言。
EOF

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-1_C3_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-21_FITZ-HOTFIX-1_C3_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達 checkout 提示詞）
- ❌ 修改任何未列入 C3 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
