`````markdown
# 2026-06-02 — PIPE-CORE OP-3 run 提示詞

> **收到時間**：2026-06-02 18:48（UTC+8）
> **任務代號**：PIPE-CORE OP-3
> **觸發 commit**：OP-3
> **相關產出檔案**：.claude-logs/baton/2026-06-02_PIPE-CORE_OP-3_執行.md
> **觸發情境**：baron 確認 OP-2 落地後下達 OP-3 執行指令——Orchestrator 四 Phase DAG 調度（pipelines/orchestrator.py 宣告式 P1→P4 + 交接點驗證 + reading_ready/rag_status + Early Emit/Checkpoint/P4 派發掛點 + shadow 貫穿；grep doc_type== 須 0 命中）。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-02 18:48 |
| **任務代號** | PIPE-CORE OP-3 |
| **觸發 Commit** | OP-3 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md` |
| **觸發情境** | baron 確認 OP-2 落地，下達 OP-3 執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-02_PIPE-CORE_OP-3_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-02_PIPE-CORE_OP-3_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：PIPE-CORE
- **當前 Commit 代號**：OP-3
- **工作流類別**：BE-Refactor
- **Tasks 路徑**：`.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md # 本次執行的依據 tasks (§8 實作細節)
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md               # logging 標準規範
.claude-logs/sop/2026-05-23_database_SOP_手冊.md              # 數據庫交易規範
```

### 🛠️ 執行命令

請依 `tasks.md §8 OP-3 具體實作細節` 進行代碼修改，並嚴格遵守以下三個防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：逐項確認，絕不越界修改任何舊單體代碼（如 `pipeline_core.py` 舊單體）。
2. **測試防線**（`tasks.md §6.3 測試計畫`）：執行 `pipelines` 與 `context` 的 pytest 驗收，確保 Orchestrator 四 Phase DAG 順序、合約交接點驗證、P4 非阻塞容錯、影子貫穿路徑命名等測試全綠，且既有測試零迴歸。自核 `grep -nE "doc_type ==" pipelines/orchestrator.py` 必須 0 命中。
3. **文件防線**（`CLAUDE.md §1.3`）：所有 commit / push 由 baron 手動執行，嚴禁自發呼叫 git 工具進行 commit。

### 💾 備份規則

修改任何既有檔案前，必須先備份。
*(特別注意：本次 OP-3 需要再次修改既有測試檔 `tests/test_pipe_core.py`，必須在修改前先進行物理備份，備份檔必須納入 git add)*
```bash
cp tests/test_pipe_core.py .claude-logs/archive/2026-06-02_PIPE-CORE_OP-3_test_pipe_core.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將本任務當前 `OP-3` 標記為 ✅ 已完成：
     `- ✅ done: OP-3 — Orchestrator 四 Phase DAG 調度（宣告式狀態機 + 交接點驗證 + shadow 貫穿）`
   - 將下一個 `OP-4` 標記為 🟡 WIP：
     `- [/] 🟡 WIP: OP-4 — Checkout / 收官歸檔（一次性歸檔 plan_v2/tasks_v2/四報告 + TODO ✅）`

2. **歷史已提交 Hash 掃描與自愈回填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 `TODO.md` 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-06-02_PIPE-CORE_OP-3_執行.md`（暫存 baton/，**嚴禁在此時執行 git add**）
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

執行報告必須包含：

- 頂部元數據塊（任務代號 / 執行日期 / 依據規劃 / 次級參考 / hash 留空 / 狀態）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含備份路徑，注意：**本報告自身以及 baton/ 下的任何暫存檔案，絕對不得放入本次變動與 git add 清單中！**）
- §4 修法說明（附關鍵代碼片段）
- §5 測試結果（貼上真實終端輸出，包含 pytest 測試成功結果以及 grep 檢測結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步 OP-4 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供（確保無 `baton/` 暫存報告與 tasks 文件入 git，嚴守 baton 暫存鐵律與備份鐵律）：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）
# cp tests/test_pipe_core.py .claude-logs/archive/2026-06-02_PIPE-CORE_OP-3_test_pipe_core.py.bak

# 2. git add 清單（包含新增模組、測試修改與 .bak 備份檔，排除 baton/ 檔案）
git add pipelines/orchestrator.py
git add pipelines/__init__.py
git add tests/test_pipe_core.py
git add .claude-logs/archive/2026-06-02_PIPE-CORE_OP-3_test_pipe_core.py.bak
git add .claude-logs/prompts/2026-06-02_PIPE-CORE_OP-3_run_提示詞.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-CORE_OP-3_msg.txt）
cat > /tmp/PIPE-CORE_OP-3_msg.txt << 'EOF'
BE-Refactor: PIPE-CORE OP-3 — Orchestrator 四 Phase DAG 調度

新增 pipelines/orchestrator.py 實作宣告式四 Phase DAG 調度
交接點① R1.1 禁欄位驗證、交接點②③④ 必填欄位驗證
推進 P3 後 reading_ready 解鎖，P4 背景非同步派發與容錯
影子測試 shadow=True 時 paper_id 追加尾綴與產物路徑隔離
pipelines/__init__.py 導出 Orchestrator 調度層
tests/test_pipe_core.py 追加 Orchestrator 調度與合約驗證測試

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-CORE_OP-3_msg.txt
```

---

### 🛑 停止指令

**產出 `OP-3_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：

- ❌ 繼續執行下一個 OP-4 階段（必須等 baron 確認後另行下達提示詞）
- ❌ 修改 any 未列入本 OP-3 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（tests/test_pipe_core.py 追加 Orchestrator 測試）
- 改動檔案數：新增 `pipelines/orchestrator.py`；修改 `pipelines/__init__.py` / `tests/test_pipe_core.py`（先 .bak）；提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 OP-2（`2026-06-02_PIPE-CORE_OP-2_run_提示詞.md`，工廠與策略基類）。下一步 OP-4 Checkout 收官歸檔。
`````
