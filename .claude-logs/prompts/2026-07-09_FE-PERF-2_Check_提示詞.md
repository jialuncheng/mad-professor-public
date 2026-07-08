# 2026-07-09 — FE-PERF-2 Check 提示詞

> **收到時間**：2026-07-09 06:34（UTC+8）
> **任務代號**：FE-PERF-2 Check（checkout）
> **觸發 commit**：checkout
> **相關產出檔案**：baton C1–C4 執行報告 → 歸檔 executions/；直產 `executions/2026-07-09_FE-PERF-2_checkout_執行.md`
> **觸發情境**：C1–C4 ship 完畢，baron 下達 Conformance 驗收與 checkout 收官；五維度驗收 + baton 一次性歸檔 + TODO 雙層結案 + 鐵律 checkout 報告（含 staged 白名單自檢）。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 06:34 |
| **任務代號** | FE-PERF-2 Check |
| **觸發 Commit** | checkout |
| **相關產出檔案** | baton C1–C4 執行報告（4 份） |
| **觸發情境** | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與 checkout 收官指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_FE-PERF-2_Check_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行 Conformance 驗收，全部合規後收官歸檔 + checkout。

### ✅ Conformance 驗收（五維度）
目標規格（plan §2 U1–U8）/ 驗收條件（tasks §6）/ 不可動清單（tasks §7）/ 提示詞歸檔與版控稽核（實體 + git add）/ msg.txt 草稿完整性 → 產驗收報告。

### 🗃️ 收官自動化
1. 更新 TODO + hash 自癒（C1–C4 真實 hash + 殘留佔位；active 移除、索引標 ✅）。
2. mv baton 過程檔（plan/tasks/C1–C4 報告）→ plans//tasks//executions/ + 逐檔 git add。
3. 確認 baton 僅剩 README.md（本任務檔全出）。
4. **直產 checkout 執行報告**（WORKFLOW_SOP §3 鐵律）：`executions/2026-07-09_FE-PERF-2_checkout_執行.md`，含 Conformance 總驗 + `git diff --cached` staged 白名單自檢輸出。

### 📝 §8 checkout 命令
git add checkout 報告 + prompts（Tasks/C1–C4/Check·⚠️ 逐檔、禁廣義 add）+ TODO.md；msg /tmp/FE-PERF-2_checkout_msg.txt；baron 手動 commit。

### 🛑 停止指令
完成 TODO 更新、baton 搬移、直產報告、輸出命令後立即停止。嚴禁：自發 git commit/push / 改已歸檔目錄。
````

---

## 執行結果摘要

- ✅ 完成狀態：Conformance 五維度全綠（U1–U8 跨 commit 覆蓋）→ baton 一次性歸檔（6 檔）+ **TODO 雙層結案**（framework §2.5 v5：完整表→archive/TODO_done_archive.md + TODO 一行索引）+ hash 自癒（C1–C4）+ 鐵律 checkout 報告直產 executions/（含 staged 白名單自檢實貼）
- 收官註：提示詞模板之「TODO ✅ 已完成新增完整表格」為 CONTEXT-1 前舊制、依 framework §2.5 v5 雙層結案執行（tasks §4.5 已凍結此流程）
- 是否 commit / push：否（baron 手動）

## 後續引用

FE-PERF-2 全案結案；audit 兩份（browser/css governance）長駐 baton；BE 包（Gzip+快取）與 CSS 治理（FE-CSS-GOV）屬另案候選。
