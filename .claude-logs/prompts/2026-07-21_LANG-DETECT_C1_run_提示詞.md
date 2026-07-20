# LANG-DETECT C1 Run 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：LANG-DETECT（F4、cover-prompt +language 欄語言偵測）
- **階段**：階段 4（執行 C1 — Language Field & Source-Lang Resolution）
- **來源**：baron 結構化提示詞

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 06:56 |
| **任務代號** | LANG-DETECT C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_tasks.md` |
| **觸發情境** | baron 確認上一個 任務/Tasks 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_LANG-DETECT_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_LANG-DETECT_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`LANG-DETECT`
- **當前 Commit 代號**：`C1`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_plan.md  # 全局策略 plan（v2）
.claude-logs/baton/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md  # 設計評審探索 spec
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🏢 工作目錄硬規則（必遵守）

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`（詳見 `CLAUDE.md §3 工作目錄硬規則`、唯一權威源）

### 🛠️ 執行命令

請依 `tasks.md §8 C1 具體實作細節` 修改代碼，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁更動 `pipelines/section_engine.py` 既有 `classify_source_lang` 本地啟發式偵測器，亦不得將其職責延伸（保持原職、繁中 bypass 權威不動搖，book 處理路徑共用零碰）。
   - ⚠️ 嚴禁更動 `models.py` 的 `GlobalGlossary` 表結構。
   - ⚠️ 嚴禁引入任何 `langdetect` 等第三方語言偵測套件，語言正名必須利用既有的 metadata LLM 呼叫順風車，零新增偵測器，零多一次 LLM 呼叫。
   - ⚠️ 嚴禁新增 `LITEDOC_LANG_DETECT_ENABLED` 等環境開關（內建安全網回退等同 100% 現行，違背 YAGNI）。

2. **測試防線**（`tasks.md §6.1`）：
   - 擴充 `tests/test_litedoc_pipeline.py`，完整覆蓋：
     * system prompt 契約包含 `language` 欄與其 system rules，JSON 輸出格式要求 keys 包含 language。
     * 合成矩陣單元測試（`_resolve_source_lang`）：啟發式為非 `en`（`zh`/`hans`/`ja`/`ko`）時，LLM 回傳值無論為何均維持原判；啟發式為 `en` 時，LLM 回傳 `it`/`de`/`fr` 等拉丁字母則採信，LLM 回傳 `IT` 進行 lower 採信，LLM 回傳 `zh`/`zh-tw`/`zho`/`Chinese`/`en-US` 包含 `zh` 前綴或非法格式則一律退回 `en` 確保繁中 bypass 不破口。
     * P1 端到端：mock LLM 帶 `"language":"it"` 輸出時，產出的 `spec.source_lang == "it"`。
     * **§7.2 跨 Phase 整合測試**（命名含 `integration`）：P1 mock 輸出語系為 `it`，傳入 P2 步驟三實體自癒流程中，斷言 `_heal_glossary`/`build_termmap` 實際收到的 `source_lang == "it"`（證明 single source of truth 對齊），且 P3 翻譯閘門不 bypass，對照組英文文件全鏈正常。
   - 修改完成後，執行 `pytest tests/` 確保全體通過（基線 875 passed 以上，零新 fail）。
   - 貼上驗收與 SOP 一致性核查（§6.2）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改檔案前，必須先備份：

```bash
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-07-21_LANG-DETECT_C1_litedoc_pipeline.py.bak
cp tests/test_litedoc_pipeline.py .claude-logs/archive/2026-07-21_LANG-DETECT_C1_test_litedoc_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C1` 標記為 ✅ 已完成：`- ✅ C1 — Language Field & Source-Lang Resolution（語言欄與 source_lang 合成）`。
   - 將 `checkout` 標記為 🟡 WIP：`- 🟡 WIP checkout — 成果收官歸檔（成果歸檔與移出暫存）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔、framework §2.1 雙層結構）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-21_LANG-DETECT_C1_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C1)`，Git hash 留空由 baron回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含 C1 修改的 2 個實體檔案與備份的 2 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 說明（說明 `_LITEDOC_META_SYSTEM_PROMPT` system prompt 修改，以及 `_resolve_source_lang` 合成時雙閘白名單與防繞過繁中 gate 設計）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 checkout 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C1 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-21_LANG-DETECT_C1_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_LANG-DETECT_C1_test_litedoc_pipeline.py.bak

# 3. commit message draft（已寫入 /tmp/LANG-DETECT_C1_msg.txt）
cat > /tmp/LANG-DETECT_C1_msg.txt << 'EOF'
BE-Refactor: LANG-DETECT C1 — Language Field & Source-Lang Resolution（語言欄與 source_lang 合成）

1. 修改 pipelines/litedoc_pipeline.py 既有元數據抽取 _LITEDOC_META_SYSTEM_PROMPT 提示詞，Fields 增列 language 欄（ISO 639-1 二位代碼），Rules 新增主體語言判定與 keys 強制包含 language 規定，搭乘既有 metadata LLM 便車，零多餘 API 呼叫。
2. 於 pipelines/litedoc_pipeline.py 實作私有 _resolve_source_lang 語系合成邏輯，啟發式判定非 en（zh/hans/ja/ko）時維持原判；啟發式為 en 時則透過正則 ^[a-z]{2,3}$ 且不帶 zh 前綴之雙重白名單過濾 LLM 語言碼，通過才予採信以防繞過繁中 gate。
3. 於 run_phase1 串接 source_lang 合成，使正名後 ISO 語系碼流入 IngestionMetadataSpec 以對齊 downstream glossary 語系分桶。
4. 擴充 tests/test_litedoc_pipeline.py，涵蓋 prompt 契約、合成矩陣參數化測試、P1 端到端 mock 測試、以及 §7.2 跨 Phase 整合測試。
EOF

# 4. baron 手動執行
git commit -F /tmp/LANG-DETECT_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-21_LANG-DETECT_C1_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達 checkout 提示詞）
- ❌ 修改任何未列入 C1 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
