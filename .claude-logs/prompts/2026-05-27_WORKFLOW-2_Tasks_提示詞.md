# 2026-05-27 — WORKFLOW-2 Tasks 提示詞

> **收到時間**：2026-05-27 00:40
> **任務代號**：WORKFLOW-2 Tasks
> **觸發 commit**：WORKFLOW-2-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md`
> **觸發情境**：baron 同意 WORKFLOW-2 plan 規格，下達任務拆分與 TODO.md 登記指令

---

## 完整提示詞

```
### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-27 00:40 |
| **任務代號** | WORKFLOW-2 Tasks |
| **觸發 Commit** | WORKFLOW-2-Tasks |
| **相關產出檔案** | `.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md` |
| **觸發情境** | baron 同意 plan 規格，下達 WORKFLOW-2 任務拆分與 TODO.md 登記指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

（本提示詞包含第一步歸檔區塊 — 此為 R1 新防線首次實戰驗證）

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

任務編碼：WORKFLOW-2
工作流類別：DOC-Refactor
Plan 路徑：.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md

強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / TODO.md（已載入）+ plan.md + template_tasks.md

關鍵設計決策注入：
Q1：9 份歷史提示詞以「摘要重建」補建，標明「歷史補建版本」
Q3：草稿完整性稽核列為獨立「維度五」

成果盤點 §0.5 必置文件開頭。
每個 Commit 六維度表格。
同步更新 TODO.md 高優先最前方。

產出：.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md
停止：tasks.md + TODO.md 完成後立即停止。
```

---

## 執行結果摘要

- ✅ 完成：產出 `baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md`
- ✅ 完成：更新 `TODO.md` 高優先新增 WORKFLOW-2 WIP 條目
- 改動檔案：2 個（新建 tasks.md + TODO.md 修改）
- 業務代碼：零改動
- commit / push：由 baron 手動執行

## 後續引用

本提示詞為 WORKFLOW-2 Tasks 階段依據，後續各 Run Commit 執行報告均引用此拆分清單。
