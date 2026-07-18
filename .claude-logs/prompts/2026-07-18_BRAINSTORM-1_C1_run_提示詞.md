````markdown
# 2026-07-18 — BRAINSTORM-1 C1 提示詞

> **收到時間**：2026-07-18 22:37（UTC+8）
> **任務代號**：BRAINSTORM-1 C1
> **觸發 commit**：C1
> **相關產出檔案**：.claude-logs/baton/2026-07-18_BRAINSTORM-1_C1_執行.md
> **觸發情境**：baron 同意 tasks.md，下達第一個 Commit（C1 — Brainstorming SOP & Visual Companion）執行指令。

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-07-18 22:37` |
| **任務代號** | `BRAINSTORM-1 C1` |
| **觸發 Commit** | `C1` |
| **相關產出檔案** | `.claude-logs/baton/2026-07-18_BRAINSTORM-1_C1_執行.md` |
| **觸發情境** | `baron 同意 tasks.md，下達第一個 Commit 執行指令` |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-18_BRAINSTORM-1_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的 `## 依時間排序` 首行插入以下新條目，若超過 15 筆則刪除最舊一筆：
   `- 2026-07-18 — `2026-07-18_BRAINSTORM-1_C1_run_提示詞.md`（C1 Run·DOC-Refactor：Brainstorming SOP & Visual Companion——導入 `.claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md` 及 `.claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md`；路徑改為完整根路徑防呆；執行報告暫存 baton 不入 git；同步 TODO C1→✅/C2→WIP）`

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-18_BRAINSTORM-1_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`BRAINSTORM-1`
- **當前 Commit 代號**：`C1`
- **工作流類別**：`DOC-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

​```
CLAUDE.md                                                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                                                       # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md  # 全局策略 z
.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md         # 本次執行的依據 tasks
​```

### 🛠️ 執行命令

請依 `tasks.md §8 C1 — Brainstorming SOP & Visual Companion（作業 SOP 與視覺伴讀指引導入）具體實作細節` 進行代碼修改，並嚴格遵守以下三個防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：逐項確認，不越界。
2. **測試防線**（`tasks.md §6 測試計畫`）：執行對應驗收 grep 條件。
3. **文件防線**（`CLAUDE.md §1.3`）：所有 commit / push 由 baron 手動執行，嚴禁自發。

### 💾 備份規則

- **注意**：本 Commit 僅新增檔案，無修改任何既有檔案，因此不需要進行備份。

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入（此修改暫不 `git add`，待 Checkout 收官階段一次性提交）：**

1. **WIP 狀態更新**：
   - 將本任務當前 Commit 標記為 ✅ 已完成：
     `- ✅ 已完成: C1 — Brainstorming SOP & Visual Companion（作業 SOP 與視覺伴讀指引導入）`
   - 將下一個 Commit 標記為 🟡 WIP：
     `- 🟡 WIP: C2 — Vendored Scripts & Env Redirect（tools 腳本導入與環境變數改導）`

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`（完成史歸檔檔）** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-18_BRAINSTORM-1_C1_執行.md`（暫存於 baton/，**嚴禁在此階段 `git add`**）
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

執行報告必須包含：
- 頂部元數據塊（任務代號 / 執行日期 / 依據規劃 / 次級參考 / hash 留空 / 狀態）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含備份路徑，此處備份路徑填 `—`）
- §4 修法說明（附關鍵代碼片段）
- §5 測試結果（貼上真實 `grep` 終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供：

​```bash
# 1. 備份檔案已完成（本 Commit 僅新增檔案，無備份）

# 2. git add 清單（所有本次 Commit 涉及的改動）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
# ⚠️ 執行報告位於 baton/，且 plan 目前在 baton/，依規範在此階段絕對禁止 git add 這些暫存文件。
# commit 前以 `git diff --cached --name-only` 自檢 staged 集合＝本清單，多/少一檔即停。
git add .claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md
git add .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md

# 3. commit message 草稿（已寫入 /tmp/BRAINSTORM-1_C1_msg.txt）
cat > /tmp/BRAINSTORM-1_C1_msg.txt << 'EOF'
DOC-Refactor: C1 — Brainstorming SOP & Visual Companion

- 新建 .claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md
- 新建 .claude-logs/sop/2026-07-18_brainstorming_visual-companion_指引.md
- 規範問答與視覺伴讀落點，改寫相對引用為完整根路徑防呆
- 執行報告暫存於 baton/ 不入版控
EOF

# 4. baron 手動執行
git commit -F /tmp/BRAINSTORM-1_C1_msg.txt
​```

---

### 🛑 停止指令

**產出 `C1_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit/OP（必須等 baron 確認後另行下達提示詞）
- ❌ 修改任何未列入本 Commit §8 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
```

---

## 執行結果摘要

- ✅ 完成：新建 SOP 手冊 + 視覺伴讀指引兩份於 `.claude-logs/sop/`，全文完整根路徑防呆
- pytest baseline：748 passed（本任務零 .py、不影響）
- 改動檔案：2 新增（sop/）；執行報告暫存 baton；TODO C1→✅/C2→WIP
- commit / push：由 baron 手動執行

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
