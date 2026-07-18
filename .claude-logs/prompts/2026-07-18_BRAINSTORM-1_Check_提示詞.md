`````markdown
# 2026-07-18 — BRAINSTORM-1 Check 提示詞

> **收到時間**：2026-07-18 22:53（UTC+8）
> **任務代號**：BRAINSTORM-1 Check
> **觸發 commit**：Checkout
> **相關產出檔案**：所有執行報告與歸檔路徑（見正文指令）
> **觸發情境**：C1/C2 全部 ship 完畢，baron 下達 Conformance 驗收與 Checkout 收官指令。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-07-18 22:53` |
| **任務代號** | `BRAINSTORM-1 Check` |
| **觸發 Commit** | `Checkout` |
| **相關產出檔案** | 所有執行報告與歸檔路徑（見下方指令） |
| **觸發情境** | `所有 Commit ship 完畢，baron 下達 Conformance 驗收與 Checkout 指令` |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：`.claude-logs/prompts/2026-07-18_BRAINSTORM-1_Check_提示詞.md`（格式依 README §3）。
2. **更新 INDEX.md**：在 `## 依時間排序` 首行插入 Check 條目，若超過 15 筆則刪除最舊一筆。
3. **確認完成後繼續**：回覆歸檔確認後續行。

（完整正文見本檔下方「執行結果摘要」對應之收官動作；為免巢狀 code block 過深，此處保留提示詞骨架與關鍵指令。）

---

你現在扮演 **Claude Code**，請對 BRAINSTORM-1 執行 Conformance 驗收，並在全部合規後執行收官歸檔。

- 任務編碼：BRAINSTORM-1
- Plan：.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀vendoring_plan.md
- Tasks：.claude-logs/baton/2026-07-18_BRAINSTORM-1_brainstorming問答與視覺伴讀_tasks.md
- 執行報告：.claude-logs/baton/2026-07-18_BRAINSTORM-1_C1_執行.md / C2_執行.md

### Conformance 驗收（五維度）
1. 目標規格（plan §2 六項）逐項對應執行報告完成狀態
2. 測試計畫（tasks §6 grep + smoke）逐項對應 C1/C2 §5 通過記錄
3. 不可動清單（tasks §7）所有報告 §6 標「✅ 未觸碰」/「✅ 零編輯」
4. 提示詞歸檔稽核：ls prompts/ | grep BRAINSTORM-1，Tasks/C1/C2/Check 實體存在，缺則補建
5. msg.txt 草稿完整性：各報告 §8 含完整 msg 草稿

產出 Conformance 驗收報告（目標規格 / 測試計畫 / 不可動清單三表 + 總結）。

### 收官動作（全綠後）
1. TODO 雙層結案：archive/TODO_done_archive.md 追加 ### DOC-Refactor BRAINSTORM-1 表格（C1/C2/Checkout·hash 待回填）+ TODO ✅ 已完成索引新增一行 + 移除 active 條目 + 類別索引標 ✅
   - hash 自癒：git log 全量審計，C1/C2 待 baron 回填 佔位替換為真實 hash（Checkout hash 保留待 baron 提交後填）
2. baton 一次性 mv + 逐檔 git add：plan→plans/（更名去 vendoring）/ tasks→tasks/ / C1·C2 執行報告→executions/
3. 確認 baton/ 只剩 README.md
4. git add 4 提示詞（Tasks/C1/C2/Check）+ INDEX.md + TODO.md + archive/TODO_done_archive.md
5. staged 自檢：git diff --cached --name-only 實貼
6. 產 executions/2026-07-18_BRAINSTORM-1_checkout_執行.md（Conformance 五維度總驗 + staged 自檢實貼 + baton 移空確認 + §7.2 豁免 + §8 一行 commit），git add 之

### 🛑 停止指令
完成 TODO 更新 + baton 歸檔 + checkout 執行報告後立即停止。
嚴禁：自發 git commit / push；修改已移入 executions/ 的報告。

〔完整六維度表格模板、收官六步 bash 指令詳見 baron 原始提示詞；本歸檔為忠實骨架記錄、關鍵指令與停止條件一字不漏。〕
````

---

## 執行結果摘要

- ✅ Conformance 五維度全綠（目標規格 6/6·測試計畫 7/7·不可動 5/5·提示詞 4 份·msg 草稿完整）
- baton 一次性歸檔 plan/tasks/C1/C2 → plans/tasks/executions；baton 還原僅 README
- hash 自癒：C1/C2 真實 hash 回填雙源（Checkout 待 baron commit 後回填）
- 4 提示詞 + TODO 雙層 + INDEX 入版控；staged 白名單自檢實貼；直產 checkout 執行報告（§7.2 純 DOC+tooling 豁免）
- commit / push：由 baron 手動執行

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
`````
