`````markdown
# 2026-06-06 — RESUME-P3 Check（Conformance 驗收與收官歸檔）提示詞

> **收到時間**：2026-06-06 00:15（UTC+8）
> **任務代號**：RESUME-P3 Check（BE-Refactor 階段 6 收官、commit 代號 C6）
> **觸發 commit**：RESUME-P3-Check / C6
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-P3_C6_執行.md`
> **觸發情境**：C1-C5 全 ship；baron 下達 Conformance 三維度驗收（目標規格 plan §2 U1-U8 / 測試 tasks §6 / 不可動清單）+ 提示詞稽核 + msg 完整性 → 全合規後建 C6 執行報告 + TODO 結案（C1-C6 完成表 + hash 全量自癒）+ 一次性 mv plan/tasks/C1-C6 報告 → plans//tasks//executions/ + git add；嚴禁自發 commit、msg 寫 /tmp；末尾粗體提醒 baron 重捕 Golden Baseline。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-06 00:15 |
| 任務代號 | RESUME-P3 Check |
| 觸發 Commit | RESUME-P3-Check |
| 相關產出檔案 | 所有執行報告路徑 |
| 觸發情境 | 所有 Commit (C1-C5) ship 完畢，baron 下達 Conformance 驗收與歸檔指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-06_RESUME-P3_Check_提示詞.md + 更新 INDEX（RESUME-P3 系列 + 時間排序首行、超 15 刪最舊 PIPE-RESUME_C4）。

你現在扮演 Claude Code，對 RESUME-P3 執行 Conformance 驗收，全合規後收官歸檔。

### 任務資訊
- 任務編碼 RESUME-P3
- Plan：baton/2026-06-05_RESUME-P3_..._plan_v1.md；Tasks：baton/..._tasks.md；C1-C5 報告 baton/

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1 / tasks / C1-C5 報告

### Conformance 驗收（三維度 + 稽核）
1. 目標規格（plan §2 U1-U8）vs 各報告完成狀態。
2. 測試計畫（tasks §6）pytest + grep 全通過。
3. 不可動清單 §6「✅ 未觸碰」。
4. 提示詞歸檔稽核：ls prompts | grep RESUME-P3（tasks/C1-C5 run/Check 齊全）。
5. msg.txt 完整性（C1-C5 報告 §8）。
→ 全合規進收官；任一不符即停回報。

### 收官（全合規後）
1. 建 C6 執行報告 baton/2026-06-06_RESUME-P3_C6_執行.md（template_execution、Completed C6）。
2. TODO.md：✅ 完成新增 RESUME-P3 C1-C6 表（hash 全量自癒）+ 移除 active + 索引 ✅。
3. mv baton plan_v1→plans/、tasks→tasks/、C1-C6 報告→executions/ + git add。
4. ls baton/ 確認只剩 README + 非本任務檔。
5. 末尾粗體提醒 baron 重捕 Golden Baseline（capture --all）。

### §8 baron 命令與 msg
msg 寫 /tmp/RESUME-P3_C6_msg.txt；§8 列 git add（TODO+prompts+plans+tasks+executions）+ baron 手動 commit。

### 🛑 停止指令
TODO 更新 + baton 歸檔後立即停止；嚴禁自發 commit/push、嚴禁改已歸檔文件。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：Conformance 三維度驗收（U1-U8 / tasks §6 / 不可動清單 / 提示詞稽核 / msg 完整性）+ C6 執行報告 + TODO 結案 + baton 一次性歸檔
- 驗收：全綠（唯一紅燈為既存 env flake、非本任務）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

RESUME-P3（C1-C6）全案結案——B軌履歷逐 heading section 翻譯 + opt-out TextTiling + U4 停用 + 退化 fallback；改 B軌輸出 → **須與 TILING-HOTFIX-1/SHADOW-HOTFIX-2 合併一次重捕 Golden Baseline**；通用化 chunking 歸 INFRA-3。
`````
