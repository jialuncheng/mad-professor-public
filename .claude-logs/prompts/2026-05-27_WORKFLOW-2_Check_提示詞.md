# 2026-05-27 — WORKFLOW-2 Check 提示詞

> **收到時間**：2026-05-27 05:00
> **任務代號**：WORKFLOW-2 Check
> **觸發 Commit**：WORKFLOW-2-Check
> **相關產出檔案**：
> - `.claude-logs/plans/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`
> - `.claude-logs/tasks/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md`
> - `.claude-logs/executions/2026-05-26_WORKFLOW-2_Tasks_執行.md`
> - `.claude-logs/executions/2026-05-27_WORKFLOW-2_C1_執行.md`
> - `.claude-logs/executions/2026-05-27_WORKFLOW-2_C2_執行.md`
> - `.claude-logs/executions/2026-05-27_WORKFLOW-2_C3_執行.md`
> - `.claude-logs/executions/2026-05-27_WORKFLOW-2_C4_執行.md`
> - `.claude-logs/executions/2026-05-27_WORKFLOW-2_C5_執行.md`
> **觸發情境**：WORKFLOW-2 所有 C1~C4 原子 Commit 已手動提交，baron 下達 C5 INDEX 雙向對齊、全量 Hash 自愈與 baton 收官歸檔指令

---

## 完整提示詞

```
### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-27 05:00 |
| **任務代號** | WORKFLOW-2 Check |
| **觸發 Commit** | WORKFLOW-2-Check |
| **相關產出檔案** | .claude-logs/plans/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md 等 8 份 |
| **觸發情境** | WORKFLOW-2 所有 C1~C4 原子 Commit 已手動提交，baron 下達 C5 INDEX 雙向對齊、全量 Hash 自愈與 baton 收官歸檔指令 |

套用 5 維度 Conformance 驗收表格：
1. 目標規格（plan.md §2）逐項比對執行報告完成狀態
2. 驗收條件（tasks.md §6）逐項確認 grep 通過記錄
3. 不可動清單（tasks.md §7）確認全部「✅ 未觸碰」
4. 提示詞歸檔（prompts/ 物理目錄）ls grep WORKFLOW-2 確認 plan/tasks/run(s)/check 各階段存在
5. msg.txt 草稿完整性（各執行報告 §8）確認含完整 cat > /tmp/... 展示

C5 收官動作（全部合規後執行）：
1. 建立 C5 執行報告 .claude-logs/baton/2026-05-27_WORKFLOW-2_C5_執行.md
2. prompts/INDEX.md 幽靈索引自癒：
   - 刪除 WORKFLOW-1 C1~C5 + TODO-HOTFIX-1 文字描述塊（L16~26）
   - 替換為 9 份補建提示詞實體 Markdown 連結
   - 補齊 WORKFLOW-2 本身 Plan/Tasks/C1~C4/Check 條目
   - 依時間排序保持最新 15 筆
   - 最後更新行更新為「2026-05-27（WORKFLOW-2 全案收官）」
3. TODO.md 更新：
   - 移除 WORKFLOW-2 WIP 段落
   - ✅ 已完成頂部新增 WORKFLOW-2 完成表格（Tasks+C1~C5）
   - git log 全量 Hash 審計，替換所有「待 baron 回填」
4. baton/ 全量歸檔（mv + git add）：
   - plan → plans/
   - tasks → tasks/
   - Tasks_執行.md + C1~C5_執行.md → executions/（共 6 份）
5. 確認 baton/ 只剩 README.md

嚴禁 git commit/push。
```

---

## 執行結果摘要

（待執行後填入）

## 後續引用

（WORKFLOW-2 全案完工，無後續引用）

> 本文件為 WORKFLOW-2 Check 提示詞歸檔，記錄 baron 下達 C5 INDEX 雙向對齊與全案收官指令的完整意圖。
