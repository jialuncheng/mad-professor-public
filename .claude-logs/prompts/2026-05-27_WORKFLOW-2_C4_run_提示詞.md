# 2026-05-27 — WORKFLOW-2 C4 提示詞

> **收到時間**：2026-05-27 04:45
> **任務代號**：WORKFLOW-2 C4
> **觸發 commit**：C4
> **相關產出檔案**：`.claude-logs/baton/2026-05-27_WORKFLOW-2_C4_執行.md`
> **觸發情境**：baron 審查 C3 執行報告無誤並已手動 Commit，下達 C4 歷史 9 份提示詞「摘要重建」物理補建指令

---

## 完整提示詞

```
C4 — R5a 歷史 9 份提示詞物理補建

任務：WORKFLOW-2 C4 / DOC-Refactor
Tasks 路徑：.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md

在 .claude-logs/prompts/ 依序物理補建 9 份歷史提示詞檔案（全為新建，不改動既有）：

1. 2026-05-26_WORKFLOW-1_C1_提示詞.md
2. 2026-05-26_WORKFLOW-1_C1.5_提示詞.md
3. 2026-05-26_WORKFLOW-1_C2+C3_提示詞.md
4. 2026-05-26_WORKFLOW-1_C4_提示詞.md
5. 2026-05-26_WORKFLOW-1_C5_提示詞.md
6. 2026-05-26_TODO-HOTFIX-1_Plan_提示詞.md
7. 2026-05-26_TODO-HOTFIX-1_Run_提示詞.md
8. 2026-05-26_TODO-HOTFIX-1_Tasks+Run-1b_提示詞.md
9. 2026-05-26_TODO-HOTFIX-1_Check_提示詞.md

每份以「摘要重建（非逐字重寫）」方式，依對應執行報告 §4/§1 還原提示詞意圖與技術規格。
格式：頂部元數據 + 完整提示詞正文 + 執行結果摘要 + 歷史補建聲明。

依據報告真理源：
- WORKFLOW-1 C1: executions/2026-05-26_WORKFLOW-1_C1_執行.md
- WORKFLOW-1 C1.5: executions/2026-05-26_WORKFLOW-1_C1.5_執行.md
- WORKFLOW-1 C2+C3: executions/2026-05-26_WORKFLOW-1_C2+C3_執行.md
- WORKFLOW-1 C4: executions/2026-05-26_WORKFLOW-1_C4_執行.md
- WORKFLOW-1 C5: executions/2026-05-26_WORKFLOW-1_C5_執行.md
- TODO-HOTFIX-1 Plan: hotfixes/2026-05-26_TODO-HOTFIX-1_hotfix.md
- TODO-HOTFIX-1 Run: executions/2026-05-26_TODO-HOTFIX-1_執行.md
- TODO-HOTFIX-1b: executions/2026-05-26_TODO-HOTFIX-1b_執行.md
- TODO-HOTFIX-1 Check: executions/2026-05-26_TODO-HOTFIX-1_Check_執行.md

物理寫入後，執行 git add 加入暫存區。
產出 baton/2026-05-27_WORKFLOW-2_C4_執行.md。
更新 TODO.md：C4 ✅ / C5 🟡 WIP。
停止指令：嚴禁繼續 C5，嚴禁 git commit/push。
```

---

## 執行結果摘要

- ✅ 第一步歸檔完成：本檔案
- ✅ 9 份歷史提示詞物理補建（摘要重建方式）
- ✅ TODO.md：C4 ✅ / C5 🟡 WIP
- ✅ C4 執行報告：`baton/2026-05-27_WORKFLOW-2_C4_執行.md`

## 後續引用

- C5 Run 提示詞（待建）：`.claude-logs/prompts/2026-05-27_WORKFLOW-2_C5_run_提示詞.md`

> 本文件為 C4 Run 提示詞歸檔，記錄 baron 下達歷史 9 份提示詞補建指令的完整意圖。
