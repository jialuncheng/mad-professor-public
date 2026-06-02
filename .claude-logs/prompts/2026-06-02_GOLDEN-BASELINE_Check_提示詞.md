`````markdown
# 2026-06-02 — GOLDEN-BASELINE Check 提示詞

> **收到時間**：2026-06-02 16:22（UTC+8）
> **任務代號**：GOLDEN-BASELINE Check
> **觸發 commit**：GOLDEN-BASELINE-Check
> **相關產出檔案**：baton/ plan_v2 / tasks / OP-1 / OP-2 / OP-3 執行報告（收官一次性歸檔）
> **觸發情境**：所有實作 OP ship 完畢且自比對歸零通過，baron 下達 Conformance 驗收與最終收官指令（OP-3 = Checkout 收官，一次性 mv plan/tasks/三報告至正式目錄 + git add + TODO 結案）。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-06-02 16:22`                                           |
| **任務代號**     | `GOLDEN-BASELINE Check`                                      |
| **觸發 Commit**  | `GOLDEN-BASELINE-Check`                                      |
| **相關產出檔案** | `baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`<br>`baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`<br>`baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md`<br>`baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md`<br>`baton/2026-06-02_GOLDEN-BASELINE_OP-3_執行.md` |
| **觸發情境**     | `所有實作 Commit ship 完畢且自比對歸零通過，baron 下達 Conformance 驗收與最終收官指令` |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**
1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_Check_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。
2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的 `## 依時間排序` 首行插入本條目：
   `- 2026-06-02 | GOLDEN-BASELINE | check | Conformance 驗收與收官歸檔`
   若超過 15 筆則自動刪除最舊一筆。
3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-02_GOLDEN-BASELINE_Check_提示詞.md`」，然後繼續執行後續步驟。
---
你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔動作。
### 📋 任務資訊
- **任務編碼**：`GOLDEN-BASELINE`
- **Plan 路徑**：`.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md`
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md
  .claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md
  ```
### 📖 強制讀檔清單
請在開始驗收前，必須完整閱讀以下文件（按順序）：
```
CLAUDE.md
.claude-logs/ref/WORKFLOW_SOP.md
.claude-logs/TODO.md
.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md
.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md
.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md
.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md
```
---
### ✅ Conformance 驗收流程
（三維度逐項交叉比對：目標規格 plan §2 / 驗收條件 tasks §6 / 不可動清單 tasks §7 / 提示詞歸檔稽核 / msg.txt 草稿完整性；產出 Conformance 表格，不合規即停止收官。）
### 🗃️ 收官歸檔動作（全部合規後立即執行）
1. 新建 OP-3 執行報告（baton/，套用 template_execution，暫存待移）。
2. 更新 TODO.md：✅ 已完成新增 GOLDEN-BASELINE 表格（Hash 留 待 baron 回填）+ 刪除 active 條目 + 索引標 ✅ + 歷史 Hash 全量自癒。
3. 一次性 mv baton/ plan_v2→plans/（保留 _v2）、tasks→tasks/、OP-1/OP-2/OP-3 報告→executions/ + git add；併 prompts Check + INDEX + TODO。
4. 確認 baton/ 僅剩 README.md。
### 🛑 停止指令
完成 TODO 更新與物理搬移歸檔後立即停止。嚴禁自發 git commit/push；嚴禁改動已移入正式目錄的檔案。
````

---

## 執行結果摘要

- ⏳ 進行中
- Conformance：三維度逐項驗收
- 收官歸檔：plan/tasks/OP-1/OP-2/OP-3 一次性 mv + git add
- 是否 commit / push：否（hash 待 baron 回填後手動 commit）

## 後續引用

承 OP-1（`..._OP-1_run_提示詞.md`）、OP-2（`..._OP-2_run_提示詞.md`）。本階段收官結案。
`````
