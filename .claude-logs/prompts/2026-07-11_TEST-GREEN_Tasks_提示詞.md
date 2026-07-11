````markdown
# 2026-07-11 — TEST-GREEN Tasks 提示詞

> **收到時間**：2026-07-11 18:19（UTC+8）
> **任務代號**：TEST-GREEN Tasks
> **觸發 commit**：TEST-GREEN-Tasks
> **相關產出檔案**：.claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md
> **觸發情境**：baron 同意 plan 規格（`baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md` v1.1 execution-ready），下達階段 2 任務拆分指令，將 plan 拆為可執行 Commit 清單並同步 TODO。

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-07-11 18:19 |
| 任務代號 | TEST-GREEN Tasks |
| 觸發 Commit | TEST-GREEN-Tasks |
| 相關產出檔案 | .claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md |
| 觸發情境 | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
（寫入 .claude-logs/prompts/2026-07-11_TEST-GREEN_Tasks_提示詞.md、更新 INDEX.md、回覆歸檔完成後續行）

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊
- 任務編碼：TEST-GREEN
- 工作流類別：FE-Refactor
- Plan 路徑：.claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md

### 📖 強制讀檔清單
CLAUDE.md / .claude-logs/ref/WORKFLOW_SOP.md / .claude-logs/TODO.md /
.claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md /
.claude-logs/templates/template_tasks.md / .claude-logs/templates/template_execution.md /
.claude-logs/sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md

### 🏢 工作目錄與修改邊界規則
- 修改邊界：僅允許修改 tests/ 目錄下的測試代碼。嚴禁修改任何業務代碼與網頁前端資產（static/**、web_server.py 等）。
- 不可動測試契約防線：嚴禁改動任何測試斷言的 regex pattern 本體、正/負向語意或期望值。僅允許改動「被搜尋源字串」的組成。
- 執行中產出文件必須先放 baton/（checkout 收官後才 mv + git add 歸檔）

### 📊 成果盤點約束（§0.5 必置文件開頭）
（新增 0 / 修改 6 / 目錄 0 / 狀態更新 2〔TODO.md、prompts/INDEX.md〕/ Commits N / baton 歸檔 1 次）

### ⚙️ Commit 拆分與執行限制原則
- 不提供預設 Commit 建議：自行閱讀 Plan 設計最佳、最小且可逆的原子 Commits。
- 最後一個 Commit 必須是 checkout。
- 各階段（除 checkout）都必須產生執行報告，寫入 baton/ 暫存區，路徑 .claude-logs/baton/2026-07-11_TEST-GREEN_<名稱>_<執行階段>_執行.md，套用 template_execution.md。
- checkout 階段才搬移 plan 與執行報告：過程文件（plan/tasks/各執行報告）checkout 前全暫存 baton/，僅 checkout commit 才 mv 歸檔至 plans/ tasks/ executions/ 並 git add。

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）
影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節

### 📝 §1 TL;DR 中文括號命名要求
每個 Commit 引用必須含中文括號命名（如 C1 — Tests Source Update（測試源字串更新））

### 🔄 同步更新 TODO.md（必做、即時）
於 TODO.md ## 🟡 進行中 / ⬜ 未開始 → ### 🔴 高優先 最前方新增 TEST-GREEN 任務條目（含各 Commit、工時、依賴 THEME-DEDUP）

### 📁 產出規格
- 產出路徑：.claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md（暫存 baton/）
- 套用模板：.claude-logs/templates/template_tasks.md
- 命名格式：依 WORKFLOW_SOP §6

### 🛑 停止指令
產出 tasks.md 並更新 TODO.md 後必須立即停止。
嚴禁：繼續產出 _執行.md / 動任何主題檔案或正式 CSS 代碼 / 自發 git commit 或 push。
```

---

## 執行結果摘要

- ✅ 提示詞歸檔 + INDEX 更新完成
- ✅ 產出 tasks.md 至 baton/、同步 TODO.md 🟡 WIP
- pytest baseline：690 passed / 15 failed / 3 skipped（目標 705 passed / 0 failed）
- 改動檔案數（本階段）：2（prompts 歸檔 + INDEX）；tasks.md 暫存 baton/ 不入版控
- commit / push：無（tasks 階段不 commit；由 baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
