# PIPE-SECTION-BASE Tasks 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 03:58 |
| 任務代號 | PIPE-SECTION-BASE Tasks |
| 觸發 Commit | PIPE-SECTION-BASE-Tasks |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_tasks.md` |
| 觸發情境 | baron 同意 plan v2 規格（§9 六 OQ 全 🟢）、下達任務拆分指令 |
| 工作流類別 | BE-Refactor（tasks 階段）|

## 正文（原文摘要）
扮演 Claude Code、將 PIPE-SECTION-BASE plan v2 拆為可執行 Commit 清單。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / framework / TODO / plan / 母 plan v10 / SPEC / database SOP / logging SOP / template_tasks / template_execution
- 拆分鐵律：① 最後一個 Commit 必為 Checkout ② Checkout 才搬 plan + 執行報告（Run 階段 baton/ 暫存、git add 不含 baton）③ 本 tasks 階段不搬 plan ④ 各 Commit（含 Checkout）都產執行報告（套 template_execution）
- 工作目錄硬規則：唯一合法 worktree、嚴禁主 repo、嚴禁動業務代碼（除 plan 指明之 pipelines/section_engine.py + resume_pipeline.py）、產出先 baton/
- §0.5 成果盤點置開頭；§8 每 Commit 六維度表格（影響範圍/安全性/可逆性/驗收 grep/依賴/具體實作）；§1 TL;DR 中文括號命名
- 同步更新 TODO（高優先最前、🟡 WIP + Commit 清單）
- 提示詞中不給 commit 建議（由我自主拆分）
- 停止：產 tasks + 更新 TODO 後立即停;嚴禁產 _執行.md / 動業務代碼 / 自發 commit

## 偏差註記
- 讀檔清單之母 plan 路徑為 `plans/2026-06-01_PIPE_..._v10.md`、SPEC 在 baton/（長駐真理源）;BE-Refactor 故 database/logging SOP 一致性核查（§5）適用、tasks §6 須含。
- plan v2：§2.5 方案 A pure-function 模組;U3.1 meta header 純格式化器零 schema 耦合;U3.2 DFS 接子樹;Q5 模組名 `pipelines/section_engine.py`;Q6 §7.2 雙鎖（resume 既有 key-changing + base 層獨立 key-changing）。
