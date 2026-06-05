`````markdown
# 2026-06-05 — MODEL-9-OPT Tasks（Embedding 連線與限流框架優化·任務拆分）提示詞

> **收到時間**：2026-06-05 17:15（UTC+8）
> **任務代號**：MODEL-9-OPT Tasks（BE-Refactor 階段 2 拆 commit）
> **觸發 commit**：MODEL-9-OPT-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_tasks.md`
> **觸發情境**：baron 同意 plan（v3）規格後下達拆分指令——依 plan 拆 commit（含 §0.5 成果盤點 / §1 TL;DR 中文括號命名 / §8 六維度表格 / 末尾強制 Checkout commit）；中間 commit 報告留 baton、唯 Checkout 一次性 mv 歸檔；同步更新 TODO.md 高優先；tasks 階段只 view/grep/編輯 markdown、不動業務代碼、不歸檔 plan。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 17:15 |
| 任務代號 | MODEL-9-OPT Tasks |
| 觸發 Commit | MODEL-9-OPT-Tasks |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_tasks.md |
| 觸發情境 | baron 同意 plan 規格，下達任務拆分指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_MODEL-9-OPT_Tasks_提示詞.md + 更新 INDEX（時間排序首行、超 15 刪最舊）+ 回覆已歸檔。

你現在扮演 Claude Code，依指令將 plan 拆分為可執行 Commit 清單。

### 任務資訊
- 任務編碼 MODEL-9-OPT / 工作流 BE-Refactor
- Plan：baton/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_plan.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / template_tasks / framework / database_SOP / logging_SOP / template_execution

### 工作目錄硬規則
唯一合法 worktree；嚴禁讀寫主 repo；tasks 階段只 file view/grep/markdown 編輯；執行報告先放 baton/。

### 歸檔硬規則（必含 Checkout Commit）
1. 末尾必獨立規劃 Checkout（收官/驗收）commit。
2. 各代碼 commit 階段完成後產 _執行.md 暫存 baton/。
3. 唯 Checkout 一次性 mv plan/執行報告 → 正式目錄 + git add；本 tasks 階段勿移動/歸檔 plan。

### §0.5 成果盤點（強制置開頭）
列：新增檔案 / 修改檔案 / 目錄初始化 / 狀態更新 / Commits / baton 歸檔。

### Commit 拆分原則
彈性數量、語意完整、可逆、優先序（配置/結構→核心重構→測試）。

### §8 六維度表格（每 commit 必填）
影響範圍 / 安全性 / 可逆性 / 驗收 grep 條件 / 依賴關係 / 具體實作細節。

### §1 TL;DR 中文括號命名（每 commit 引用須含中文括號子標題）

### 同步更新 TODO.md（即時）
高優先區最前新增 MODEL-9-OPT 條目（各 commit + Checkout、工時、依賴）。

### 產出規格
baton/2026-06-05_MODEL-9-OPT_..._tasks.md；套用 template_tasks；命名依 WORKFLOW_SOP §6。

### 🛑 停止指令
產 tasks.md + 更新 TODO 後立即停止；不產 _執行.md、不動 Python、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：tasks.md（§0.5 成果盤點 + §8 六維度拆分含末尾 Checkout commit）
- 同步：TODO.md 高優先新增 MODEL-9-OPT 條目
- 是否動業務代碼：否（純 markdown）；是否 commit：否

## 後續引用

承 MODEL-9-OPT plan v3（review 5 點補強定稿）；拆分後依序逐 commit Run（基建地基、不碰 golden、可獨立先做）；對齊排序 hotfix → MODEL-9-OPT → RESUME-P3。
`````
