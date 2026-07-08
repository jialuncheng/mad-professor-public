# 2026-07-09 — FE-PERF-2 Tasks 提示詞

> **收到時間**：2026-07-09 04:06（UTC+8）
> **任務代號**：FE-PERF-2 Tasks
> **觸發 commit**：FE-PERF-2-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_tasks.md`
> **觸發情境**：baron 核准 plan v3（八 OQ 定案 + 相容底線上調 Safari 18+）後，下達階段 2 任務拆分指令；FE-Refactor、修改邊界限 `static/index.html` + 新增 `static/vendor/marked/**`、最後一顆 commit 為 checkout、過程文件暫存 baton、同步 TODO 🟡 WIP。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 04:06 |
| **任務代號** | FE-PERF-2 Tasks |
| **觸發 Commit** | FE-PERF-2-Tasks |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_tasks.md |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-PERF-2_Tasks_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，依指令將 plan 拆為可執行 Commit 清單。

### 📋 任務資訊
- 任務編碼：FE-PERF-2 / 工作流：FE-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1（v3） / template_tasks.md / template_execution.md

### 🏢 工作目錄與修改邊界規則
- 唯一合法工作目錄：`.claude/worktrees/hopeful-yalow-902c50/`（※歸檔註：此為模板殘留、CLAUDE.md §3 v5 已改主 repo 雙視圖，依 CLAUDE.md 為準）
- 嚴禁改後端業務代碼（pipeline_core / web_server / paper_manager / processor/*.py）
- 前端修改限制：僅 `static/index.html` + 新增 `static/vendor/marked/**`（不改 login.html）
- 過程文件先放 baton/、checkout 才 mv + git add

### 📊 成果盤點約束（§0.5 必置文件開頭）

### ⚙️ Commit 拆分與執行限制原則
- 不給預設 Commit 建議、自設最小可逆原子 commits；最後一顆必為 checkout。
- 各實作階段產執行報告 → `.claude-logs/baton/2026-07-09_FE-PERF-2_<名稱>_<階段>_執行.md`（套 template_execution）。
- checkout 才 mv 過程文件 → plans//tasks//executions/ + git add。

### 📋 §8 六維度 Commit 拆分表格（每 Commit 必填）
（影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節）

### 📝 §1 TL;DR 中文括號命名要求

### 🔄 同步更新 TODO.md（必做、即時）
於 `## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先` 最前方新增 FE-PERF-2 條目、🟡 WIP。

### 📁 產出規格
- 產出路徑：`.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_tasks.md`（baton）
- 套用模板：template_tasks；命名依 WORKFLOW_SOP §6。

### 🛑 停止指令
產出 tasks.md + 更新 TODO.md 後立即停止。嚴禁：續產 _執行.md / 動後端業務代碼 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：tasks.md 產出 + TODO 🟡 WIP
- 拆分：C1 marked 自託管換源 → C2 defer+DOMContentLoaded 包裹 → C3 串流 rAF 節流+滾動同批 → C4 字型 preload+scroll passive+content-visibility → checkout（5 commits）
- 改動檔案數：本階段僅新增 tasks.md（baton）+ 更新 TODO/INDEX（純規劃、零代碼）
- 是否 commit / push：否（baron 手動）

## 後續引用

執行階段 C1–C4/checkout Run 由 baron 另下獨立提示詞觸發。
