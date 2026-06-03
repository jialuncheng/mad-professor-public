`````markdown
# 2026-06-03 — DOMAIN-NORM Check（C5 收官）提示詞

> **收到時間**：2026-06-03 18:59（UTC+8）｜（前置 18:46 Check 提示詞經 baron 拍板「先補 C4 Unit Tests 再收官」重導，本則為正式 C5 收官）
> **任務代號**：DOMAIN-NORM Check
> **觸發 commit**：DOMAIN-NORM-Check (C5)
> **相關產出檔案**：baton/ plan_v2 / tasks / C1~C5 執行報告（收官一次性歸檔）
> **觸發情境**：C1–C4 實作與測試完畢，baron 下達 C5 Conformance 驗收與收官歸檔指令（三維度驗收 §6.1-§6.4 + 一次性 mv plan_v2/tasks/C1~C5 報告至正式目錄 + TODO 結案 + 歷史全量 Hash 自癒）。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 18:59 |
| **任務代號** | DOMAIN-NORM Check |
| **觸發 Commit** | DOMAIN-NORM-Check (C5) |
| **相關產出檔案** | 所有執行報告路徑（C1/C2/C3/C4 + 本 C5） |
| **觸發情境** | C1–C4 實作與測試完畢，下達 C5 Conformance 驗收與收官歸檔指令 |
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
- 執行報告 baton/ C1~C4 執行.md
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v2 / tasks / C1~C4 執行報告
### ✅ Conformance 驗收流程
三維度逐項交叉比對：目標規格（plan §2 U1-U4）/ 驗收條件（tasks §6.1-§6.4 grep+pytest）/ 不可動清單（各報告 §6 ✅ 未觸碰）+ 提示詞歸檔稽核（ls prompts/ grep DOMAIN-NORM 缺則自癒）+ msg.txt 草稿完整性 → 產 Conformance 報告；全合規才收官，不符項中斷列例外等 baron。
### 🗃️ 收官自動化動作（全部合規後）
1. 更新 TODO.md：✅ 已完成新增 BE-Refactor DOMAIN-NORM 表（C1-C5，Hash 待 baron 回填）+ 移除 active 條目 + 索引標 ✅ + 歷史全量 Hash 自癒。
2. 一次性 mv baton/（plan_v2/tasks/C1-C5 報告）→ plans//tasks//executions/ + git add。
3. 確認 baton/ 僅剩 README.md。
4. ls prompts/ grep DOMAIN-NORM 確認各階段 md 齊全。
### 🛑 停止指令
完成 TODO 更新與 baton/ 歸檔後立即停止。嚴禁自發 git commit/push；嚴禁改已歸檔 executions//plans//tasks/ 文件。
````

---

## 執行結果摘要

- ⏳ 進行中
- Conformance：U1-U4 / 測試 §6.1-§6.4 / 不可動清單三維度驗收
- 收官歸檔：plan_v2/tasks/C1-C5 報告一次性 mv + git add；baton/ 僅剩 README
- 是否 commit / push：否（hash 待 baron 回填後手動 commit）

## 後續引用

承 C1~C4 run 提示詞。本階段 C5 收官結案（DOMAIN-NORM 全案 5 commit；PIPE 大改版三大共用真理源之一 DomainNormalizer 就緒）。
`````
