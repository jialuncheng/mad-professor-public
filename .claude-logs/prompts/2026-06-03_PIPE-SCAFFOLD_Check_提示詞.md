`````markdown
# 2026-06-03 — PIPE-SCAFFOLD Check 提示詞

> **收到時間**：2026-06-03 06:11（UTC+8）
> **任務代號**：PIPE-SCAFFOLD Check
> **觸發 commit**：PIPE-SCAFFOLD-Check
> **相關產出檔案**：baton/ plan_v3 / tasks_v3 / OP-1 / OP-2 / OP-3 執行報告（收官一次性歸檔）
> **觸發情境**：OP-1/OP-2 全落地，baron 下達 Conformance 驗收與 OP-3 收官歸檔指令（產 OP-3 執行報告 + 一次性 mv plan_v3/tasks_v3/三報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒）。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 06:11 |
| **任務代號** | PIPE-SCAFFOLD Check |
| **觸發 Commit** | PIPE-SCAFFOLD-Check |
| **相關產出檔案** | 所有執行報告路徑（見下方清單） |
| **觸發情境** | 所有 Commit/OP 落地完畢，baron 下達 Conformance 驗收與收官歸檔指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_Check_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-03_PIPE-SCAFFOLD_Check_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔動作（將所有暫存 baton/ 下的檔案徹底移出）。

### 📋 任務資訊

- **任務編碼**：PIPE-SCAFFOLD
- **Plan 路徑**：`.claude-logs/baton/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md`
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-06-03_PIPE-SCAFFOLD_OP-1_執行.md
  .claude-logs/baton/2026-06-03_PIPE-SCAFFOLD_OP-2_執行.md
  .claude-logs/baton/2026-06-03_PIPE-SCAFFOLD_OP-3_執行.md  (待本次 Conformance 比對後建立產出)
  ```

### 📖 強制讀檔清單

請在開始驗收前，必須完整閱讀以下文件（按順序）：
```
CLAUDE.md
.claude-logs/ref/WORKFLOW_SOP.md
.claude-logs/TODO.md
.claude-logs/baton/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md
.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md
.claude-logs/baton/2026-06-03_PIPE-SCAFFOLD_OP-1_執行.md
.claude-logs/baton/2026-06-03_PIPE-SCAFFOLD_OP-2_執行.md
.claude-logs/templates/template_execution.md
```

### ✅ Conformance 驗收流程

第一步：三維度逐項交叉比對（目標規格 plan §2 U1-U9 / 驗收條件 tasks §6 5 測試 / 不可動清單 tasks §7 A 軌本體 / 提示詞歸檔稽核 / msg.txt 草稿完整性）。
第二步：產出 Conformance 驗收報告（即 OP-3 執行報告）依 template_execution.md 在 baton/ 產出 `2026-06-03_PIPE-SCAFFOLD_OP-3_執行.md`，含 Conformance 表格。不符項則拒絕收官、停止等待 baron。

### 🗃️ 收官自動化動作（全部合規後才執行）

1. 更新 TODO.md：✅ 已完成新增 PIPE-SCAFFOLD 表（OP-1~OP-3，Hash 待 baron 回填）+ 移除 active 條目 + 索引標 ✅ + 歷史全量 Hash 自癒。
2. 一次性 mv baton/ 5 份（plan_v3→plans/、tasks_v3→tasks/、OP-1~OP-3 報告→executions/）+ git add（維持 _v3）。
3. 確認 baton/ 清空。
4. 本 Check 提示詞歸檔 + INDEX 登記。

### 🛑 停止指令
完成 TODO 更新與 baton/ 移出歸檔後立即停止。嚴禁自發 git commit/push；嚴禁改動已歸檔 executions/ 報告。
````

---

## 執行結果摘要

- ⏳ 進行中
- Conformance：三維度逐項驗收（目標規格 U1-U9 / 測試 5 項 / 不可動清單 A 軌 byte 不動）
- 收官歸檔：plan_v3/tasks_v3/OP-1~OP-3 一次性 mv + git add
- 是否 commit / push：否（hash 待 baron 回填後手動 commit）

## 後續引用

承 OP-1/OP-2 run 提示詞。本階段 OP-3 收官結案。階段二（移／Flip）屬 PIPE-FLIP plan。
`````
