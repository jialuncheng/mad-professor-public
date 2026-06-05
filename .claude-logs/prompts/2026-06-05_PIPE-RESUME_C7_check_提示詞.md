`````markdown
# 2026-06-05 — PIPE-RESUME C7 Check（Conformance 驗收與收官歸檔）提示詞

> **收到時間**：2026-06-05 11:04（UTC+8）
> **任務代號**：PIPE-RESUME C7（v9 整合批次、Checkout）
> **觸發 commit**：C7（Conformance 驗收 + baton 一次性歸檔收官）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C7_執行.md`
> **觸發情境**：C1-C6 全 ship；baron 下達 Conformance 三維度驗收（目標規格 plan_v1 §2 / 驗收條件 tasks §6 / 不可動清單 tasks §7）+ 提示詞歸檔稽核 + msg 完整性 → 全合規後一次性 mv plan_v1〔保留 _v1〕/tasks/C1-C7 報告 → plans//tasks//executions/ + 母 plan v10/PIPE-SPEC 就地 git add（不 mv）+ TODO 結案（C1-C7 完成表 + 移除 active + 索引 ✅）。嚴禁自發 commit、msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 11:04` |
| **任務代號** | `PIPE-RESUME C7` |
| **觸發 Commit** | `C7` |
| **相關產出檔案** | 所有執行報告與計畫檔案路徑 |
| **觸發情境** | `所有實作 Commit 已 ship，baron 下達 Conformance 驗收與收官歸檔指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_C7_check_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，對 PIPE-RESUME v9 批次執行 Conformance 驗收，全合規後收官歸檔。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / Checkout C7 / 工作流 BE-Refactor
- Plan：baton/2026-06-01_PIPE-RESUME_..._plan_v1.md；Tasks：baton/2026-06-05_PIPE-RESUME_..._tasks.md
- 執行報告：baton/ C1-C6 執行.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan_v1 / tasks / C1-C6 報告

### ✅ Conformance 驗收（三維度 + 稽核）
1. 目標規格（plan_v1 §2）vs 各報告完成狀態。
2. 驗收條件（tasks §6）pytest + grep 結果。
3. 不可動清單（tasks §7）✅ 未觸碰。
4. 提示詞歸檔稽核：ls prompts | grep PIPE-RESUME（plan/tasks/run/check 齊全）。
5. msg.txt 草稿完整性（各報告 §8）。
→ 全合規進收官；任一不合規即停回報。

### 🗃️ 收官（全合規後）
1. TODO.md：✅ 完成新增 v9 影子整合 C1-C7 表（Hash 待回填）+ 移除 active + 索引 ✅。
2. mv baton plan_v1（保留 _v1）→ plans/、tasks → tasks/、C1-C7 報告 → executions/（mkdir -p）+ git add；母 plan v10 + PIPE-SPEC 就地不 mv、僅 git add。
3. ls baton/ 確認本批次移清。

### 🛑 停止指令
TODO 更新 + baton mv/staging 後立即停止。嚴禁自發 commit/push、嚴禁改已移入正式目錄文件。

### 📝 §8 baron 命令與 msg
msg 寫 /tmp/PIPE-RESUME_C7_msg.txt；§8 列剩餘 git add（TODO + prompts）+ baron 手動 commit。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：C7 Conformance 三維度驗收報告 + TODO 結案 + baton 一次性歸檔（plan_v1→plans/、tasks→tasks/、C1-C7 報告→executions/、母 plan/PIPE-SPEC 就地 git add）
- 驗收：目標規格 / tasks §6 pytest+grep / 不可動清單 / 提示詞稽核 / msg 完整性
- 報告：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C7_執行.md`（本身於收官時 mv→executions/）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

PIPE-RESUME v9 影子整合批次（C1-C7）全案結案；PIPE 縱向五路第 1 路影子整合完成。
`````
