`````markdown
# 2026-06-06 — RESUME-PERF-1 Tasks（run_phase3 逐 section 翻譯並行化·任務拆分）提示詞

> **收到時間**：2026-06-06 17:00（UTC+8）
> **任務代號**：RESUME-PERF-1 Tasks（BE-Refactor 階段 2 拆 commit）
> **觸發 commit**：RESUME-PERF-1-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_tasks.md`
> **觸發情境**：baron 確認「不必等五路、現在就做」後核准 plan v2（§7 OQ Q1-Q7 拍板），下達拆分指令——拆 commit（§0.5 成果盤點 / §1 中文括號命名 / §8 六維度 / 末尾 Checkout 一次性歸檔）；中間報告留 baton；同步 TODO 高優先；tasks 階段只 view/grep/markdown、不動業務代碼、不歸檔 plan。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-06 17:00 | 任務 RESUME-PERF-1 Tasks | 觸發 Commit RESUME-PERF-1-Tasks | 依據 plan_v1（v2 內部、OQ 核准）|

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep）
寫入 prompts/2026-06-06_RESUME-PERF-1_Tasks_提示詞.md + 更新 INDEX（補條目 + 時間排序首行、超 15 刪最舊）。

你扮演 Claude Code，依指令將 plan 拆分為可執行 Commit 清單。

### 任務資訊
- 任務編碼 RESUME-PERF-1 / 工作流 BE-Refactor
- Plan：baton/2026-06-06_RESUME-PERF-1_..._plan_v1.md（§99.2 v2、Q1-Q7 核准）

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / template_tasks

### 工作目錄硬規則
唯一合法 worktree；嚴禁讀寫主 repo；tasks 階段只 view/grep/編輯文件、嚴禁動業務代碼；執行報告先放 baton/、收官前不 git add。

### Commit 拆分與歸檔硬規則
末尾必含 Checkout（Conformance 驗收+Hash 自癒+一次性歸檔）；plan/tasks/各 _執行.md 全留 baton、唯 Checkout 一次性 mv→plans//tasks//executions/+git add；tasks 階段嚴禁 mv plan.md；除 Checkout 外每 code commit 規劃對應 _執行.md（留 baton）。

### §0.5 成果盤點（強制置開頭）+ §8 六維度（每 commit）+ §1 TL;DR 中文括號命名

### 同步更新 TODO.md（即時）
高優先區最前新增 RESUME-PERF-1 條目（Tasks WIP + 各 commit + Checkout、工時、依賴）。

### 產出
baton/2026-06-06_RESUME-PERF-1_..._tasks.md；套用 template_tasks；命名依 WORKFLOW_SOP §6。

### 🛑 停止
產 tasks.md + 更新 TODO 後立即停止；不產 _執行.md、不動業務代碼、不自發 commit/push、不 mv baton plan.md。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：tasks.md（§0.5 成果盤點 + §8 六維度拆分含末尾 Checkout；對齊 plan v2 核准 OQ）
- 同步：TODO.md 高優先新增 RESUME-PERF-1 條目
- 是否動業務代碼：否（純 markdown）；是否 commit：否

## 後續引用

拆分方向：C1 Collect/Assemble 重構〔收集-組裝解耦、仍序列、行為等價〕→ C2 ThreadPool 並行翻譯〔序列→受限並行、受 LLMClient._api_semaphore 限流、單 unit 失敗退原文+warning〕→ C3 單元測試〔mock 確定化 byte 等拍/併發峰值≤LLM_MAX_CONCURRENT/異常隔離/退化路徑〕→ C4 Checkout。baron 拍板「不必等五路、現在做」（plan Q5 原寫 Flip 前、屬優先序非依賴）。
`````
