`````markdown
# 2026-06-05 — PIPE-RESUME Tasks（v9 影子整合）提示詞

> **收到時間**：2026-06-05 03:35（UTC+8）（精修再下達、取代 03:15 版）
> **任務代號**：PIPE-RESUME Tasks（v9 後續整合批次）
> **觸發 commit**：PIPE-RESUME-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`
> **觸發情境**：baron 同意 plan（§99.2 至 v11）規格，下達 v9 整合任務拆分。**精修點**：C1 改為同步**三份**系統文件（PIPE-RESUME plan_v1 + 母 plan v10 + PIPE-SPEC）、明列 Phase 2 流程異動（摘要先行）與六項細節；後續依四 Phase 拆分實作；最後 Checkout 一次性歸檔。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 03:35` |
| **任務代號** | `PIPE-RESUME Tasks` |
| **觸發 Commit** | `PIPE-RESUME-Tasks` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | `baron 同意 plan 規格，下達任務拆分指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_Tasks_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，將 plan 拆分為可執行 Commit 清單。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 工作流 BE-Refactor
- Plan 路徑 `.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1 / template_tasks.md

### 🏢 工作目錄硬規則
唯一合法工作目錄 worktree；嚴禁讀寫主 repo；嚴禁改業務代碼（pipeline_core/web_server/paper_manager/processor/static）；產出先放 baton/。

### 📊 §0.5 成果盤點（必置開頭）

### ⚙️ Commit 拆分原則與關鍵限制
1. **第一個 Commit（C1）**：[MODIFY] 三檔——`PIPE-RESUME plan_v1`（同步至最新規劃）/ `PIPE_…plan_v10.md`（母 plan 同步寫入）/ `PIPE-SPEC_…specification.md`（同步寫入）。內容：C7/C8-hotfix 歷史寫入規格及 Revision；P1 影子標題後綴規格 + Flip Cleanup 待辦；`ctx.raw_metadata` 穿線設計（取代 custom_metadata-in-Spec、定義 PipelineContext.raw_metadata 基建欄承載完整履歷及論文元數據、對齊 A 軌寫庫保真）；P3 constraints 業務翻譯規則（中英對照/公司名/期刊專利例外）以 InjectionContext 逐路注入共用 Translator 之自主隔離規格；Phase 2 流程異動（先做整份原文摘要前置消除前向依賴 → 依領域 LCC 雙參分類 → 術語自癒 → DEEP_THINK 翻摘要）；登記 Revision + 新增 §7.1 Cleanup 清單（含 Flip 移除 P1 影子後綴待辦）。**C1 不含 Python 業務代碼改動、純三文件同步對齊。**
2. **後續 Commit**：依 plan 四 Phase 規格正常拆分實作（C2 實作 P1、C3 實作 P2、C4 實作 P3、C5 實作 P4、C6 撰寫單元測試 等）；每實作 commit 產執行報告（template_execution）。
3. **收官 Checkout（最後 commit）**：唯 Checkout 才 mv baton 的 plan_v1/tasks/各執行報告 → plans//tasks//executions/ + git add。

### 📋 §8 六維度 Commit 拆分表格（每 Commit 必填：影響範圍/安全性/可逆性/驗收 grep/依賴/實作細節）
### 🔄 同步更新 TODO.md（高優先最前方、C1 WIP 其餘未開始、工時以 commit 數計）
### 📦 歸檔 baton plan：本階段禁止 mv，留至 Checkout

### 📁 產出規格
產出 `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`；套用 template_tasks；命名依 WORKFLOW_SOP §6。

### 🛑 停止指令
產 tasks.md + 更新 TODO 後立即停止。嚴禁產 _執行.md / 動業務代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`（v9 整合 7 Commit：C1 三文件規格同步 + C2 P1/Context + C3 P2 + C4 P3 + C5 影子寫庫保真 + C6 測試 + C7 Checkout）
- 同步：TODO.md 高優先 PIPE-RESUME v9 影子整合 🟡 WIP（7 commits）
- 是否 commit / push：否

## 後續引用

承 plan §99.2 v11（六項 v9 + v10 P2 步序 + v11 表格保留）。本批次 commit 代號 C1-C7 為 v9 整合內部序、與原 PIPE-RESUME C1-C7（已收官）區別。03:35 精修版取代 03:15 版（C1 由 2 檔擴為 3 檔含 plan_v1）。
`````
