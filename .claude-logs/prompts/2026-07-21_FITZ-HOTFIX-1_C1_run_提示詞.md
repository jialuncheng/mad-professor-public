# FITZ-HOTFIX-1 C1 Run 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：FITZ-HOTFIX-1（fitz 路標題救回與雜訊通則修復）
- **階段**：階段 4（執行 C1 — Fitz Processor Refinement）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 22:20 |
| **任務代號** | FITZ-HOTFIX-1 C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_fitz路標題救回與雜訊通則修復_tasks.md` |
| **觸發情境** | baron 確認上一個 任務/Tasks 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_FITZ-HOTFIX-1_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`FITZ-HOTFIX-1`
- **當前 Commit 代號**：`C1`
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

請依 `tasks.md §8 C1 具體實作細節` 修改 `processor/fitz_processor.py`，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 `processor/pdf_processor.py`（MinerU 處理器）、`pipelines/section_engine.py`、`pipelines/litedoc_pipeline.py`、`pipelines/ingestion_engine.py` 等其他程式檔（C1 必須高度內聚於單檔變更，全鏈路其他部分零代碼侵入）。
   - ⚠️ 標題 chrome 剝除的 `_repetition_key` 邏輯，字串數字歸一文字必須與字級大小 `round(size, 1)` 組合成複合 key 同步判斷（以保留 25.6pt 真標題的唯一性與存活）。
   - ⚠️ 標題第三階梯與 level=3 對位支援必須依序接在 R1 圖框文字剔除之後（待 heading 候選階梯淨化完畢，`###` 標題渲染才算成立，防止誤搶黏字）。

2. **測試防線**（`tasks.md §6.1`）：
   - 擴充 `tests/test_fitz_processor.py`，完整覆蓋：
     * R1 測試：構造落在影像邊界 rect 內重疊率 >50% 的文字行，斷言其被剔除；同時構造重疊率 <50% 的文繞圖文字行，斷言其被保留。
     * R2 測試：模擬 23 頁 7.0pt chrome 頂部 band 的誤殺，斷言 Chrome 被剝除，而 25.6pt 真標題行因複合 key 唯一性而成功存活。
     * R3 測試：輸入字級 `[25.6, 20.9, 17.1]` 對位候選，斷言其正確匹配為 `#` (H1) / `##` (H2) / `###` (H3) 三級標題；同時確保先前兩級文件回歸測試不受影響。
     * R5 測試：構造覆蓋率 84% 且具備 5 個獨立連結 rect 的 nav 導覽行，斷言其命中剔除；構造僅 1 個 link 覆蓋的標題行或 inline link 的正文句，斷言其不被剔除；確保無 link 註記時安全退回 no-op。
   - 執行 `pytest tests/test_fitz_processor.py` 與 `pytest tests/` 確保全體通過（基線 920 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查（§6.5）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份：

```bash
cp processor/fitz_processor.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_fitz_processor.py.bak
cp tests/test_fitz_processor.py .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_test_fitz_processor.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C1` 標記為 ✅ 已完成：`- ✅ C1 — Fitz Processor Refinement（Fitz 處理器標題救回與結構修復）`。
   - 將 `C2` 標記為 🟡 WIP：`- 🟡 WIP C2 — P1 Meta & Noise Cleanup（P1 元數據歸零與雜訊清理）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-21_FITZ-HOTFIX-1_C1_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C1)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C1 修改的 1 個實體檔案、1 個測試檔與備份的 2 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 `_repetition_key` 複合 key 設定、R1 重疊面積剔除算法、R3 第三階梯 ### 擴充、以及 R5 nav 導覽多 link 平鋪剔除邏輯）
- §5 測試與 Grep 結果（貼上真實終端輸出，包含 R1/R2/R3/R5 之 pytest 結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C2）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C1 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add processor/fitz_processor.py
git add tests/test_fitz_processor.py
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_fitz_processor.py.bak
git add .claude-logs/archive/2026-07-21_FITZ-HOTFIX-1_C1_test_fitz_processor.py.bak

# 3. commit message draft（已寫入 /tmp/FITZ-HOTFIX-1_C1_msg.txt）
cat > /tmp/FITZ-HOTFIX-1_C1_msg.txt << 'EOF'
BE-Refactor: FITZ-HOTFIX-1 C1 — Fitz Processor Refinement（Fitz 處理器標題救回與結構修復）

1. 於 processor/fitz_processor.py 實作 R1 圖框內文字排除：比對文字行與影像 bbox，重疊面積比 >0.5 者剔除，防止圖表內黏字干擾大綱與標題級別。
2. 實作 R2 頁首 chrome 剝除修復：`_repetition_key` 調整為 (數字歸一文字, round(size, 1)) 之複合 key，使 25.6pt 真標題行與 7.0pt 列印頁首標題跨頁 key 區隔以救回標題。
3. 實作 R3 三級標題對位：字級分群候選擴充至前三級，標題層級 `size >= h3` 回傳 3 以產出標準 `###` 小節標題。
4. 實作 R5 nav 導覽列通則剔除：行文字被 >=3 個獨立 link rects 覆蓋且面積比 >=60% 者判定為 nav 連結列並予以剝除，無 link 註記時自然 no-op 退回。
5. 於 tests/test_fitz_processor.py 撰寫單元測試覆蓋 R1 影像框排除、R2 Chrome chrome 剝除與真標題存活、R3 三級階梯標題、以及 R5 nav 導覽平鋪。
EOF

# 4. baron 手動執行
git commit -F /tmp/FITZ-HOTFIX-1_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-21_FITZ-HOTFIX-1_C1_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C2（必須等 baron 確認後另行下達 C2 提示詞）
- ❌ 修改任何未列入 C1 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
