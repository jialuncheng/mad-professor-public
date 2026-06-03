# 2026-05-29 — FE-AESTHETICS HOTFIX-1 Tasks 提示詞

> **收到時間**：2026-05-29 16:19
> **任務代號**：FE-AESTHETICS HOTFIX-1 Tasks
> **觸發 commit**：FE-AESTHETICS-HOTFIX-1-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md
> **觸發情境**：baron 確認 Hotfix 計畫書 (v1.2) 完備，下達任務拆分指令，準備進行 FE-AESTHETICS 靠左斷行與自癒緊急修補

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-29 16:19 |
| **任務代號** | FE-AESTHETICS HOTFIX-1 Tasks |
| **觸發 Commit** | FE-AESTHETICS-HOTFIX-1-Tasks |
| **當前 Checkout Commit** | 75ab18acb2ddb570bef0d4142719be11119ce756 |
| **相關產出檔案** | .claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md |
| **觸發情境** | baron 確認 Hotfix 計畫書 (v1.2) 完備，下達任務拆分指令，準備進行 FE-AESTHETICS 靠左斷行與自癒緊急修補 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行 any 讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-05-29_FE-AESTHETICS_HOTFIX-1_Tasks_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-05-29_FE-AESTHETICS_HOTFIX-1_Tasks_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請依以下指令將 hotfix 計畫拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：FE-AESTHETICS (子代號 HOTFIX-1)
- **工作流類別**：FE-Hotfix
- **Hotfix 計畫路徑**：.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix.md (v1.2)

### 📖 強制讀檔清單

CLAUDE.md                                              # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                       # 工作流規範（已自動載入）
.claude-logs/TODO.md                                   # 任務狀態真理源（已自動載入）
.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix.md  # 本次熱修補的依據計畫 (v1.2)
.claude-logs/templates/template_tasks.md               # tasks 模板（套用結構）
.claude-logs/templates/template_execution.md           # 執行報告模板（未來執行參考）

### 🏢 工作目錄硬規則與暫存限制

- **唯一合法工作目錄**：`.claude/worktrees/hopeful-yalow-902c50/`
- **嚴禁改動業務後端代碼**（此為 FE-Hotfix，僅修改 static/index.html 前端資源與對應前端測試，後端 .py 為不可動禁區）
- **執行中產出文件與計畫書必須先放 `baton/`**：
  - **計畫書 `2026-05-29_FE-AESTHETICS_hotfix.md` 目前必須留在 `baton/` 中**。
  - **只有到最後收官（Check / Checkout）階段，才允許將計畫書 `mv` 到正式歸檔目錄 `hotfixes/`**。WIP 執行階段嚴禁移動計畫書。
  - 所有拆分產出的 `_tasks.md` 與未來執行報告都必須先暫存在 `baton/`。

### 📊 成果盤點約束（§0.5 必置文件開頭）

在 tasks.md 的 `## §0.5 成果盤點` 章節，強制列出本熱修復的物理全量產出：

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | N 個 | <檔案 1> / <檔案 2> / ... |
| **修改檔案** | N 個 | <檔案 1>（改動簡述）/ ... |
| **目錄初始化** | N 個 | <目錄>（用途）|
| **狀態更新** | N 個 | TODO.md / prompts/INDEX.md |
| **Commits** | N 個 | <Commit代號 1> → ... → <最後 Commit代號> |
| **baton 歸檔** | N 次 | 結案收官（Check）時一併 mv 歸檔至 hotfixes/ + executions/ + tasks/ |

### ⚙️ Commit 拆分與執行報告規格

- **自主拆分**：基於計畫書規格進行科學、合理的任務拆分與 Commit 規劃，無須提供冗長的 Commit 細節預先建議。
- **強制作出執行報告**：
  - **本任務拆分出的每一個實作 Commit，在未來執行時都必須產出獨立的執行報告（`_執行.md`），且必須嚴格套用 `template_execution.md` 模板**。
  - 執行報告需詳實記載基準狀態、備份檔軌跡（每個 C2-hotfix 程式碼修改前必須進行 .bak 備份且納入 `git add`）、修法代碼、pytest 全量實測結果（基準目標 `387 passed` 自癒）與手動 E2E 核查。

### 🔄 同步更新 TODO.md（必做、即時）

在產出 tasks.md 的同時，**立即**於根目錄 `TODO.md` 的 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方，新增本熱修復條目：

- 🟡 **FE-AESTHETICS HOTFIX-1 前端學術扉頁自癒與排版靠左優化**（`.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix.md`）
  - [/] 🟡 WIP: <Commit代號 1> — <Commit名稱>（<中文括號命名>）
  - ...（依實際 Commit 數量）
  - 工時：N 個 commits
  - 依賴：FE-AESTHETICS

### 📁 產出規格

- **產出路徑**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md`（暫存 baton/）
- **套用模板**：`.claude-logs/templates/template_tasks.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 🛑 停止指令

**產出 tasks.md 並更新 TODO.md 後必須立即停止。**

嚴禁：

- ❌ 繼續產出 `_執行.md`（執行階段由 baron 下達獨立提示詞觸發）
- ❌ 修改任何業務代碼與測試（tasks 拆分階段僅進行文件編輯）
- ❌ 自發執行 `git commit` 或 `git push`
```

---

## 執行結果摘要

- ✅ 提示詞歸檔完成
- ✅ INDEX.md 更新完成
- ✅ tasks.md 產出完成（baton/ 暫存）
- ✅ TODO.md 更新完成（FE-AESTHETICS HOTFIX-1 加入 WIP）
- 等待 baron 下達 C2-hotfix Run 指令
