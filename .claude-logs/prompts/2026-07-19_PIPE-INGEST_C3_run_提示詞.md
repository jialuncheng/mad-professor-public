# PIPE-INGEST C3 Run 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-19 19:44 |
| **任務代號** | PIPE-INGEST C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-19_PIPE-INGEST_C3_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-19_PIPE-INGEST_C3_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`PIPE-INGEST`
- **當前 Commit 代號**：`C3`
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

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

### 🛠️ 執行命令

請依 `tasks.md §8 C3 具體實作細節` 進行代碼修改，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 A 軌處理器（`processor/md_processor.py`、`processor/json_processor.py`）與 `pipelines/section_engine.py` 的代碼。
   - ⚠️ 嚴禁向 litedoc `InjectionContext.constraints` 注入任何括號/術語約束。
   - ⚠️ 本 Commit 改動僅限於譯題單一源改造、cover-prompt 正規化規則、dead code 清除與新增整合測試。

2. **測試防線**（`tasks.md §6.3`）：
   - 必須於 `tests/test_ingestion_engine.py` 新增 **§7.2 跨 Phase 整合測試**，實測並斷言：圖片 Figure 全數穿透至輸出、標題不重複入內文、meta 行零重播、且 section 標題 node key 與 `section_summaries` 正確對位。
   - 修改完成後，執行 `pytest tests/` 確保全體通過（基線 748 passed 以上，零新 fail）。
   - 執行 `grep -n "_extract_translated_title\|_detect_source_lang" pipelines/litedoc_pipeline.py` 預期命中為 0。
   - 貼上驗收與 SOP 一致性核查（§6.5）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份（C3 僅修改 `litedoc_pipeline.py` 與 `test_litedoc_pipeline.py` 兩檔；`test_ingestion_engine.py` 延續 C1 新建無 bak）：

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_litedoc_pipeline.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C3` 標記為 ✅ 已完成：`- ✅ C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）`。
   - 將 `checkout` 標記為 🟡 WIP：`- 🟡 WIP checkout — 成果收官歸檔（成果歸檔與移出暫存）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-19_PIPE-INGEST_C3_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C3)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C3 修改的 3 個實體檔案與備份的 2 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 修法說明（附關鍵代碼片段）
- §5 測試結果（貼上真實終端輸出）
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
git add tests/test_ingestion_engine.py
git add .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-19_PIPE-INGEST_C3_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-INGEST_C3_msg.txt）
cat > /tmp/PIPE-INGEST_C3_msg.txt << 'EOF'
BE-Refactor: PIPE-INGEST C3 — Title Single-Source & P1 Cleanups（譯題單一源與 P1 清理）

1. 修改 pipelines/litedoc_pipeline.py，使 section 與 whole 翻譯模式下的譯題 translated_title 一律統一經由 translate_unit 翻譯 P1 true title，並廢除與清理舊的 _extract_translated_title 插槽提取方法，根治瀏覽器與 PDF Title 錯置。
2. 增補 _LITEDOC_META_SYSTEM_PROMPT 出版方（publisher）正規化 OCR 自癒規則與作者 Title Case 格式化指令。
3. 清理 pipelines/litedoc_pipeline.py 中的 _detect_source_lang 棄用死碼（已全數由 classify_source_lang 接替）。
4. 於 tests/test_ingestion_engine.py 新增 §7.2 跨 Phase 整合測試，全面斷言非 text elements 穿透、meta 不重複、及 node key 基準對齊。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-INGEST_C3_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-19_PIPE-INGEST_C3_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達 checkout 提示詞）
- ❌ 修改 any 未列入 C3 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
