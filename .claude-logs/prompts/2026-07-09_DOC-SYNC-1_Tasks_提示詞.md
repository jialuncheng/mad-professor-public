# 2026-07-09 — DOC-SYNC-1 Tasks 提示詞

> **收到時間**：2026-07-09 07:36（UTC+8）
> **任務代號**：DOC-SYNC-1 Tasks
> **觸發 commit**：DOC-SYNC-1-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_tasks.md`
> **觸發情境**：baron 核准 plan v2（六 OQ 定案、Q6 規模釘死＝1 實作 commit + 1 checkout）後，下達階段 2 拆分指令；DOC-Refactor、僅動 design/docs（token 三檔限頂部驗證註）、index.html 唯讀對照、過程文件暫存 baton、同步 TODO 🟡 WIP。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 07:36 |
| **任務代號** | DOC-SYNC-1 Tasks |
| **觸發 Commit** | DOC-SYNC-1-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_DOC-SYNC-1_Tasks_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，依指令將 plan 拆為可執行 Commit 清單。

### 📋 任務資訊
- 任務編碼：DOC-SYNC-1 / 工作流：DOC-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1（v2）/ template_tasks.md / template_execution.md

### 🏢 工作目錄與修改邊界
- worktree 路徑（※模板殘留、依 CLAUDE.md §3 v5 主 repo 為準）
- 僅允許修改 design/docs/ 文檔（含 Q3 拍板之 token 檔驗證註）；嚴禁改任何代碼/靜態資源；index.html 唯讀對照
- 過程文件先放 baton/、checkout 才 mv + git add

### 📊 §0.5 成果盤點必置開頭 / ⚙️ 拆分原則（不給預設、末 commit=checkout、各階段產報告暫存 baton）/ 📋 §8 六維度表 / 📝 §1 中文括號命名 / 🔄 同步 TODO 🟡 WIP

### 📁 產出規格
- `.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_tasks.md`（baton）；套 template_tasks；命名依 WORKFLOW_SOP §6

### 🛑 停止指令
產出 tasks.md + 更新 TODO.md 後立即停止。嚴禁：續產 _執行.md / 動代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：tasks.md 產出 + TODO 🟡 WIP
- 拆分（依 Q6 釘死）：C1 — Docs Truth Sync（components 去毒 + dom-reference 補 48 ID + 同步戳 + token 三檔驗證註、5 檔一 commit）→ checkout
- 是否 commit / push：否（baron 手動）

## 後續引用

C1 Run / checkout 由 baron 另下獨立提示詞觸發。
