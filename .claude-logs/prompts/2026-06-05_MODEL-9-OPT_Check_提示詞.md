`````markdown
# 2026-06-05 — MODEL-9-OPT Check（Conformance 驗收與收官歸檔）提示詞

> **收到時間**：2026-06-05 17:57（UTC+8）
> **任務代號**：MODEL-9-OPT Check（BE-Refactor 階段 6 收官，commit 代號 C4）
> **觸發 commit**：MODEL-9-OPT-Check / C4
> **相關產出檔案**：C4 收官（無新執行報告，TODO 結案 + baton 歸檔）
> **觸發情境**：C1-C3 全 ship；baron 下達 Conformance 三維度驗收（目標規格 plan §2 / 驗收條件 tasks §6 / 不可動清單 tasks §7）+ 提示詞稽核 + msg 完整性 → 全合規後 TODO 結案（C1-C4 完成表 + hash 全量自癒）+ 一次性 mv plan→plans//tasks→tasks//C1-C3 報告→executions/ + git add；嚴禁自發 commit、msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 17:57 |
| 任務代號 | MODEL-9-OPT Check |
| 觸發 Commit | MODEL-9-OPT-Check |
| 相關產出檔案 | 所有執行報告路徑 |
| 觸發情境 | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與歸檔指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_MODEL-9-OPT_Check_提示詞.md + 更新 INDEX。

你現在扮演 Claude Code，對 MODEL-9-OPT 執行 Conformance 驗收，全合規後收官歸檔。

### 任務資訊
- 任務編碼 MODEL-9-OPT
- Plan：baton/..._plan.md；Tasks：baton/..._tasks.md；C1-C3 執行報告 baton/

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / tasks / C1-C3 報告

### Conformance 驗收（三維度 + 稽核）
1. 目標規格（plan §2）vs 各報告完成狀態。
2. 驗收條件（tasks §6）pytest + grep。
3. 不可動清單（tasks §7）✅ 未觸碰。
4. 提示詞歸檔稽核：ls prompts | grep MODEL-9-OPT（plan/tasks/run/check 齊全）。
5. msg.txt 草稿完整性（各報告 §8）。
→ 全合規進收官；任一不符即停回報。

### 收官（全合規後）
1. TODO.md：✅ 完成新增 BE-Refactor MODEL-9-OPT C1-C4 表（hash 自癒全量回填）+ 移除 active + 索引 ✅。
2. mv baton plan→plans/、tasks→tasks/、C1-C3 報告→executions/ + git add。
3. ls baton/ 確認只剩 README + 非本任務檔。
4. prompts/INDEX 確認。

### §8 baron 命令與 msg
msg 寫 /tmp/MODEL-9-OPT_C4_msg.txt；§8 列 git add（TODO+plans+tasks+executions+prompts）+ baron 手動 commit。

### 🛑 停止指令
TODO 更新 + baton 歸檔後立即停止；嚴禁自發 commit/push、嚴禁改已歸檔文件。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：Conformance 三維度驗收（目標規格 / tasks §6 / 不可動清單 / 提示詞稽核 / msg 完整性）+ TODO 結案 + baton 一次性歸檔
- 驗收：全綠
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

MODEL-9-OPT（C1-C4）全案結案；Embedding 限流與退避框架就緒（不改向量值、不觸發 Golden 重捕）；排序 hotfix ✓ → MODEL-9-OPT ✓ → 下一步 RESUME-P3（改輸出、最後）。
`````
