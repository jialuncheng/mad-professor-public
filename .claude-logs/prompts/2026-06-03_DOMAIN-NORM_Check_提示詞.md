`````markdown
# 2026-06-03 — DOMAIN-NORM Check（C4 收官）提示詞

> **收到時間**：2026-06-03 18:46（UTC+8）
> **任務代號**：DOMAIN-NORM Check
> **觸發 commit**：DOMAIN-NORM-Check (C4)
> **相關產出檔案**：baton/ plan_v2 / tasks / C1~C4 執行報告（收官一次性歸檔）
> **觸發情境**：C1–C3 實作完畢，baron 下達 C4 Conformance 驗收與收官歸檔指令（三維度驗收 + 一次性 mv plan_v2/tasks/C1~C4 報告至正式目錄 + TODO 結案 + 歷史全量 Hash 自癒）。
> **重要偏差**：baron 此提示詞將 **C4 重定義為 Check 收官 commit**（完成表僅 C1-C4、C4=Conformance 驗收與歸檔），原 tasks v1 規劃之「C4 Unit Tests（tests/test_domain_normalizer.py 4 pytest）+ C5 Check」收斂為 4 commit；驗收矩陣僅含 §6.1-§6.3（不含 §6.4 單元測試檔）。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 18:46 |
| **任務代號** | DOMAIN-NORM Check |
| **觸發 Commit** | DOMAIN-NORM-Check (C4) |
| **相關產出檔案** | 所有執行報告路徑（C1/C2/C3 + 本 C4） |
| **觸發情境** | C1–C3 實作完畢，下達 C4 Conformance 驗收與收官歸檔指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_Check_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，對 DOMAIN-NORM 執行 Conformance 驗收，全部合規後收官歸檔。
### 📋 任務資訊
- 任務編碼 `DOMAIN-NORM`
- Plan `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md`
- Tasks `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md`
- 執行報告 baton/ C1~C3 執行.md
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v2 / tasks / C1~C3 執行報告
### ✅ Conformance 驗收流程
三維度逐項交叉比對：目標規格（plan §2 U1-U4）/ 驗收條件（tasks §6.1-§6.3 grep+pytest）/ 不可動清單（各報告 §6 ✅ 未觸碰）+ 提示詞歸檔稽核（ls prompts/ grep DOMAIN-NORM 缺則自癒）+ msg.txt 草稿完整性 → 產 Conformance 報告；全合規才收官，不符項中斷列例外等 baron。
### 🗃️ 收官自動化動作（全部合規後）
1. 更新 TODO.md：✅ 已完成新增 DOMAIN-NORM 表（C1-C4，Hash 待 baron 回填）+ 移除 active 條目 + 索引標 ✅ + 歷史全量 Hash 自癒。
2. 一次性 mv baton/（plan_v2/tasks/C1-C4 報告）→ plans//tasks//executions/ + git add。
3. 確認 baton/ 僅剩 README.md。
4. ls prompts/ grep DOMAIN-NORM 確認各階段 md 齊全。
### 🛑 停止指令
完成 TODO 更新與 baton/ 歸檔後立即停止。嚴禁自發 git commit/push；嚴禁改已歸檔 executions//plans//tasks/ 文件。
````

---

## 執行結果摘要

- ⏳ 進行中
- Conformance：U1-U4 / 測試 §6.1-§6.3 / 不可動清單三維度驗收
- 偏差待 baron 確認：原 C4 Unit Tests（tests/test_domain_normalizer.py、plan §6.1 4 pytest）未產出，本 prompt 將 C4 重定義為 Check 收官
- 收官歸檔：plan_v2/tasks/C1-C4 報告一次性 mv + git add
- 是否 commit / push：否（hash 待 baron 回填後手動 commit）

## 後續引用

承 C1~C3 run 提示詞。本階段 C4 收官結案（DOMAIN-NORM 全案 4 commit；PIPE 大改版三大共用真理源之一就緒）。
`````
