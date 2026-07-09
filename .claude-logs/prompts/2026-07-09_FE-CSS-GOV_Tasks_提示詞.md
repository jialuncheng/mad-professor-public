# 2026-07-09 — FE-CSS-GOV Tasks 提示詞

> **收到時間**：2026-07-09 09:31（UTC+8）
> **任務代號**：FE-CSS-GOV Tasks
> **觸發 commit**：FE-CSS-GOV-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md`
> **觸發情境**：baron 核准 plan v2（八 OQ 定案+符合性審查三項通過）後下達階段 2 拆分；FE-Refactor、**每 commit 文獻同步硬性綁定**（嚴禁累積至收官）、修改邊界＝index.html（CSS 遷出+class 純加法）/static/css（新 7 檔）/themes/design docs；JS 邏輯/DOM id/27+ 契約 class/渲染管線四鐵防線。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 09:31 |
| **任務代號** | FE-CSS-GOV Tasks |
| **觸發 Commit** | FE-CSS-GOV-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-CSS-GOV_Tasks_提示詞.md`、更新 INDEX、回覆確認後繼續；原文第 3 步確認字串誤植 FE-PERF-2、以本檔正名）

你現在扮演 Claude Code，依指令將 plan 拆為可執行 Commit 清單。

### 📋 任務資訊
- 任務編碼：FE-CSS-GOV / 工作流：FE-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1（v2）/ template_tasks / template_execution / **FE 效能渲染 SOP**

### 🏢 工作目錄與修改邊界（必遵守）
- worktree 路徑（※模板殘留、依 CLAUDE.md §3 v5 主 repo 為準）
- 嚴禁後端 `*.py`
- 允許：`static/index.html`（CSS 遷出+HTML class 純加法）/ 新增修改 `static/css/**` 7 檔 / `static/themes/**` / `design/docs/**`（含新增 css-architecture.md + principles 補 margin-flow）
- **四鐵防線**：JS 邏輯零改 / DOM ID 零改 / 27+ JS 契約 class 零改名 / `renderMarkdownWithMath` 七步管線零改
- 過程文件先 baton/、checkout 才 mv+git add

### 📊 §0.5 成果盤點必置開頭
### ⚙️ 拆分原則
- 不給預設 Commit；末 commit=checkout；各階段產執行報告暫存 baton
- **各階段文獻同步硬性綁定**（拆檔+層級 commit 含 css-architecture+principles；主題去重 commit 含 theme-guide 改寫；嚴禁累積收官統一改）
### 📋 §8 六維度表（含文獻同步配套細節）/ 📝 §1 中文括號命名 / 🔄 同步 TODO 🟡 WIP
### 📁 產出：`baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_tasks.md`；套 template_tasks；命名依 §6

### 🛑 停止指令
產出 tasks.md + 更新 TODO.md 後立即停止。嚴禁：續產 _執行.md / 動後端 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：tasks.md 產出 + TODO 🟡 WIP
- 拆分（B1 兩段式）：**段一等價搬遷** C1 拆檔七件套（無層、行數對帳）→ C2 @layer 化（含 2 條 !important 個案）；**段二行為改造** C3 主題去重 → C4 :root 瘦身 → C5 sidebar 收斂 → C6 content/toolbar chrome 收斂 → C7 chat+overlays 收斂 → checkout（共 8 commits）
- 85 行 ID 後代式分區分佈表已凍結入 tasks §3（收斂 vs 白名單逐區計數）
- 每 commit 文獻配套矩陣綁定（css-architecture/principles/theme-guide/components/dom-reference）
- 是否 commit / push：否（baron 手動）

## 後續引用

C1 Run 起由 baron 逐顆下獨立提示詞觸發。
