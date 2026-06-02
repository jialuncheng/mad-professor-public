`````markdown
# 2026-06-03 — PIPE-SCAFFOLD OP-2 run 提示詞

> **收到時間**：2026-06-03 05:57（UTC+8）
> **任務代號**：PIPE-SCAFFOLD OP-2
> **觸發 commit**：OP-2
> **相關產出檔案**：.claude-logs/baton/2026-06-03_PIPE-SCAFFOLD_OP-2_執行.md
> **觸發情境**：baron 確認 OP-1 落地並要求加入 `=== [PIPE-SCAFFOLD OP-N START/END] ===` 註解標記，下達 OP-2 執行指令——retry/confirm 派發點二旗標閘門納管 + 補標 OP-1 區塊註解 + 新建 tests/test_pipe_scaffold.py 雙軌測試。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 05:57 |
| **任務代號** | PIPE-SCAFFOLD OP-2 |
| **觸發 Commit** | OP-2 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md` |
| **觸發情境** | baron 確認 OP-1 落地並要求加入註解標記，下達 OP-2 執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_OP-2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_OP-2_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：PIPE-SCAFFOLD
- **當前 Commit 代號**：OP-2
- **工作流類別**：BE-Refactor
- **Tasks 路徑**：`.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md # 本次執行的依據 tasks (§8 實作細節)
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md               # logging 標準規範
.claude-logs/sop/2026-05-23_database_SOP_手冊.md              # 數據庫交易規範
```

### 🛠️ 執行命令與註解標記（強制遵守）

請依 `tasks.md §8 OP-2 具體實作細節` 進行代碼修改，並實施以下**雙層註解標記規範**：

1. **補標 OP-1 區塊**：請在本階段修改 `settings.py` 與 `web_server.py` 時，順便將上一階段（OP-1）新增的業務代碼用以下註解包裹：
   - **`settings.py` 旗標處**：
     ```python
     # === [PIPE-SCAFFOLD OP-1 START] 影子雙軌派發旗標 ===
     SHADOW_LAUNCH_ENABLED = os.getenv("SHADOW_LAUNCH_ENABLED", "false").lower() in (
         "1", "true", "yes",
     )
     # === [PIPE-SCAFFOLD OP-1 END] ===
     ```
   - **`web_server.py` 派發點一閘門處**（`upload_paper` 內）：
     ```python
     # === [PIPE-SCAFFOLD OP-1 START] 派發點一閘門 ===
     if settings.SHADOW_LAUNCH_ENABLED:
         background_tasks.add_task(
             run_pipeline_shadow, current_user.id, paper_id, str(pdf_path), doc_type, file.filename
         )
     # === [PIPE-SCAFFOLD OP-1 END] ===
     ```
   - **`web_server.py` 影子派發單元處**：
     ```python
     # === [PIPE-SCAFFOLD OP-1 START] 影子 B 軌派發單元 ===
     async def run_pipeline_shadow(...):
         ...
     # === [PIPE-SCAFFOLD OP-1 END] ===
     ```

2. **標記 OP-2 新增區塊**：
   - 在 `web_server.py` 的 retry/confirm endpoint（L756 左右的 `add_task(run_pipeline, ...)` 之後）新增的派發點二閘門，請使用以下註解包裹：
     ```python
     # === [PIPE-SCAFFOLD OP-2 START] 派發點二閘門 ===
     if settings.SHADOW_LAUNCH_ENABLED:
         background_tasks.add_task(
             run_pipeline_shadow, current_user.id, paper_id, pdf_path, request.doc_type,
         )
     # === [PIPE-SCAFFOLD OP-2 END] ===
     ```

3. **守護防線**：
   - **物理防線**：A 軌 `run_pipeline` 既有邏輯本體與 `PipelineCore.process` 調用全程 byte 不動。
   - **測試防線**：新建 `tests/test_pipe_scaffold.py` 驗證單軌等價、雙軌不碰撞、派發點二覆蓋、以及 A 軌未改的自檢測試。

### 💾 備份規則

修改任何既有檔案前，必須先備份。
*(特別注意：本次 OP-2 需要修改既有檔案 `settings.py` 與 `web_server.py`，必須在修改前先進行物理備份，備份檔必須納入 git add)*

```bash
cp settings.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_settings.py.bak
cp web_server.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_web_server.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將本任務當前 `OP-2` 標記為 ✅ 已完成：
     `- ✅ done: OP-2 — 派發點二納管 + 雙軌測試套件（全覆蓋）`
   - 將下一個 `OP-3` 標記為 🟡 WIP：
     `- [/] 🟡 WIP: OP-3 — Checkout / 收官歸檔（一次性歸檔 plan_v3/tasks_v3/三報告 + TODO ✅）`

2. **歷史已提交 Hash 掃描與自愈回填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 `TODO.md` 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-06-03_PIPE-SCAFFOLD_OP-2_執行.md`（暫存 baton/，**嚴禁在此時執行 git add**）
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

執行報告必須包含：

- 頂部元數據塊（任務代號 / 執行日期 / 依據規劃 / 次級參考 / hash 留空 / 狀態）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含備份路徑，注意：**本報告自身以及 baton/ 下的任何暫存檔案，絕對不得放入本次變動與 git add 清單中！**）
- §4 修法說明（附關鍵代碼片段，特別說明註解包裹的起始與結束行號位置）
- §5 測試結果（貼上真實終端輸出，包含 pytest 測試成功結果）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步 OP-3 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供（確保無 `baton/` 暫存報告與 tasks 文件入 git，嚴守 baton 暫存鐵律與備份鐵律）：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）
# cp settings.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_settings.py.bak
# cp web_server.py .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_web_server.py.bak

# 2. git add 清單（包含業務與測試修改及備份檔，排除 baton/ 檔案）
git add settings.py
git add web_server.py
git add tests/test_pipe_scaffold.py
git add .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_settings.py.bak
git add .claude-logs/archive/2026-06-03_PIPE-SCAFFOLD_OP-2_web_server.py.bak
git add .claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_OP-2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-SCAFFOLD_OP-2_msg.txt）
cat > /tmp/PIPE-SCAFFOLD_OP-2_msg.txt << 'EOF'
BE-Refactor: PIPE-SCAFFOLD OP-2 — 派發點二納管 + 雙軌測試套件

1. web_server.py retry/confirm 派發點二新增 shadow launch 閘門控制。
2. 補標 OP-1 修改區塊與 OP-2 新增區塊註解包裹，利於後續下線。
3. 新建 tests/test_pipe_scaffold.py 驗證雙軌派發閘門、不碰撞鍵與 A 軌本體未被改寫。
4. 全域 tests/ -q 零迴歸測試通過。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SCAFFOLD_OP-2_msg.txt
```

---

### 🛑 停止指令

**產出 `OP-2_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：

- ❌ 繼續執行下一個 OP-3 階段（必須等 baron 確認後另行下達提示詞）
- ❌ 修改任何未列入本 OP-2 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：待補（tests/test_pipe_scaffold.py）
- 改動檔案數：修改 `settings.py` / `web_server.py`（補標 OP-1 註解 + OP-2 派發點二閘門，先 .bak）；新建 `tests/test_pipe_scaffold.py`；提示詞歸檔；修改 TODO.md / INDEX.md
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

承 OP-1（`2026-06-03_PIPE-SCAFFOLD_OP-1_run_提示詞.md`）。下一步 OP-3 Checkout 收官歸檔。
`````
