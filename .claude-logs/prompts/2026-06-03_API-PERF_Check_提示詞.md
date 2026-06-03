`````markdown
# 2026-06-03 — API-PERF Check（C6 收官）提示詞

> **收到時間**：2026-06-03 16:07（UTC+8）
> **任務代號**：API-PERF Check
> **觸發 commit**：C6
> **相關產出檔案**：baton/ plan_v2 / tasks_v3 / C1~C6 執行報告（收官一次性歸檔）
> **觸發情境**：C1–C5 實作全部完成，baron 下達 Conformance 驗收與 C6 收官歸檔指令（產 C6 執行報告 + 一次性 mv plan_v2/tasks_v3/C1~C6 報告至正式目錄 + TODO 結案 + 歷史 Hash 全量自癒）。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-03 16:07` |
| **任務代號** | `API-PERF Check` |
| **觸發 Commit** | `C6` |
| **相關產出檔案** | 所有執行報告路徑（見下方清單） |
| **觸發情境** | `C1-C5 實作已全部完成，baron 下達 Conformance 驗收與 C6 收官歸檔指令` |
---
### 🗄️ 第一步：主動歸檔本提示詞（寫入 prompts/2026-06-03_API-PERF_Check_提示詞.md + 更新 INDEX）
---
你現在扮演 **Claude Code**，請對 API-PERF 執行 Conformance 驗收，並在全部合規後執行收官歸檔與文件移出動作。
### 📋 任務資訊
- **任務編碼**：`API-PERF`
- **Plan 路徑**：`.claude-logs/baton/2026-06-01_API-PERF_API技術審計與效能優化_plan_v2.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-03_API-PERF_API技術審計與效能優化_tasks_v3.md`
- **執行報告清單**：baton/ C1~C5 執行.md
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v2 / tasks_v3 / C1~C5 執行報告
### 🛠️ 執行命令與防線
1. 通用代碼註解防線（C6 為文件歸檔、不改業務代碼）。
2. **硬性要求：實體寫入 commit msg 草稿** 至 `/tmp/API-PERF_C6_msg.txt`。
3. **baton/ 檔案必須移出（收官歸檔鐵律）**：Conformance 合規並產出 C6_執行.md 後，一次性 mv plan→plans/（保留 _v2）、tasks→tasks/（保留 _v3）、C1-C6 報告→executions/ + git add；確認 baton/ 僅剩 README.md。
4. 文件與 Git 防線：git add 明確列檔、嚴禁 git add -A/.；commit/push 由 baron 手動。
### ✅ Conformance 驗收流程
逐項交叉比對目標規格 U1-U7 / 測試計畫 / 不可動清單 / 提示詞歸檔稽核 / msg 草稿完整性 → 寫入 C6_執行.md；全數合規才收官，不符項中斷列例外。
### 🗃️ 收官自動化動作（全部合規後）
1. 更新 TODO.md：✅ 已完成新增 API-PERF 表（C1-C6，Hash 待 baron 回填）+ 移除 active 條目 + 索引標 ✅ + 歷史全量 Hash 自癒。
2. 一次性 mv baton/（plan_v2/tasks_v3/C1-C6 報告）→ plans//tasks//executions/ + git add。
3. 確認 baton/ 僅剩 README.md。
### 📁 產出規格
收官報告 executions/2026-06-03_API-PERF_C6_執行.md（先建 baton/、歸檔時移動）；套用 template_execution.md。
### 📝 §8 baron 執行命令格式要求
git add 明確列檔（C1-C5 代碼 + 全部 .bak + plans/tasks/executions 歸檔 + prompts + INDEX + TODO）；commit msg 寫入 /tmp/API-PERF_C6_msg.txt：
DOC-Refactor: API-PERF C6 — Conformance 驗收與收官歸檔（4 點：全量驗收合規 / baton 一次性歸檔 / TODO 結案+Hash 自癒 / baton 僅剩 README 結案）。
### 🛑 停止指令
完成 TODO 更新與 baton/ 歸檔移出後立即停止。嚴禁自發 git commit/push；嚴禁改已歸檔 executions//plans//tasks/ 文件。
````

---

## 執行結果摘要

- ⏳ 進行中
- Conformance：U1-U7 / 測試計畫 / 不可動清單三維度驗收
- 收官歸檔：plan_v2/tasks_v3/C1-C6 報告一次性 mv + git add
- 是否 commit / push：否（hash 待 baron 回填後手動 commit）

## 後續引用

承 C1~C5 run 提示詞。本階段 C6 收官結案，API-PERF 全案完成（PIPE 大改版基建前置）。
`````
