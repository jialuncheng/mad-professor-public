# IMG-FILTER Tasks 階段 提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-20 22:05 |
| **任務代號** | IMG-FILTER Tasks |
| **觸發 Commit** | IMG-FILTER-Tasks |
| **相關產出檔案** | `.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md` |
| **觸發情境** | baron 同意 plan 規格，下達任務拆分指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入 `.claude-logs/prompts/2026-07-20_IMG-FILTER_tasks_提示詞.md`（依 prompts/README.md §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、超 15 筆刪最舊）。
3. 回覆確認後繼續。

---

你現在扮演 **Claude Code**，請依以下指令將 plan 拆分為可執行的 Commit 清單。

### 📋 任務資訊

- **任務編碼**：`IMG-FILTER`／**工作流類別**：`BE-Refactor`
- **Plan 路徑**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_plan.md`（v2）

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md / FRAMEWORK（自動載入）+ plan（v2）+ design_spec + template_tasks + template_execution

### 🏢 工作目錄硬規則（必遵守）

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）
- 嚴禁讀寫授權範圍外檔案；嚴禁改動業務代碼（本階段僅 view/grep/文件編輯）
- 執行中產出文件必須先放 baton/（Checkout 才 mv + git add）

### 📊 成果盤點約束（§0.5 必置文件開頭）

（§0.5 成果盤點表格：新增/修改/目錄初始化/狀態更新/Commits/baton 歸檔）

### ⚙️ Commit 拆分與執行報告原則

1. **不給具體 commit 數量限制或指定拆分方式**——由執行者依 plan 規格（新建 `pipelines/image_filter.py` 過濾器本體、`ingestion_engine` 純加法注入、`litedoc_pipeline` pre-pass 接線及 `settings` 三常數）與代碼依賴彈性規劃最優原子 Commit 清單。
2. 各開發 commit 依 template_execution 產執行報告、暫存 baton/。
3. 最後一個 Commit 必須為 Checkout（收官）：才准 baton 搬移歸檔；中間 commit 嚴禁 mv/git add。
4. 可逆與最小干擾：每個 Commit 獨立可測試最小單元。

### 📋 §8 六維度 Commit 拆分表格（每個 Commit 必填）

（影響範圍/安全性/可逆性/驗收 grep 條件/依賴關係/具體實作細節）

### 📝 §1 TL;DR 中文括號命名要求

每個 Commit 引用必須含中文括號命名（例：`C1 — Build Image Filter（建立圖片過濾器模組）`）。

### 🔄 同步更新 TODO.md（必做、即時）

於 `### 🔴 高優先` 最前方新增本任務條目（🟡 WIP、子任務按 commit 列點、工時 N commits、依賴無）。

### 📁 產出規格

- 產出路徑：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`（暫存 baton/）
- 套用模板：template_tasks.md；命名依 WORKFLOW_SOP §6

### 🛑 停止指令

產出 tasks.md 並更新 TODO.md 後必須立即停止。嚴禁：產出 _執行.md / 改動業務代碼 / 自發 git commit・push。
