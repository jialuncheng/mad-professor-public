# 2026-07-07 — RESCUE-1 Check 提示詞

> **收到時間**：2026-07-07 06:01（UTC+8）
> **任務代號**：RESCUE-1 Check（C5 Checkout 收官）
> **觸發 commit**：RESCUE-1 Check / C5
> **相關產出檔案**：`.claude-logs/executions/2026-07-01_RESCUE-1_C5_執行.md`（checkout 執行報告）+ baton 一次性歸檔（plan→plans/、tasks→tasks/、C1-C4 報告→executions/）
> **觸發情境**：所有 Commit（C1-C4）ship 完備，baron 下達 Conformance 驗收與歸檔收官指令。DOC-Refactor 階段 6。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-07-07 06:01 | 任務代號 | RESCUE-1 Check | 觸發 Commit | RESCUE-1-Check |
| 相關產出檔案 | 所有執行報告路徑 |
| 觸發情境 | 所有 Commit ship 完備，baron 下達 Conformance 驗收與歸檔收官指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准下一步）
1. 寫入 prompts/2026-07-07_RESCUE-1_Check_提示詞.md（格式依 README §3）。
2. 更新 INDEX.md（分類補登 + 依時間排序首行插入、>15 刪最舊）。
3. 回覆「✅ 提示詞已歸檔」後繼續。

對 RESCUE-1 執行 Conformance 驗收，全部合規後執行收官歸檔。
Plan：baton/2026-06-28_RESCUE-1_..._plan_v1.md / Tasks：baton/2026-07-01_RESCUE-1_..._tasks.md
執行報告清單：baton/2026-07-01_RESCUE-1_C1~C4_執行.md

### 📖 強制讀檔清單
CLAUDE.md / ref/WORKFLOW_SOP.md / TODO.md / plan / tasks / C1-C4 執行報告

### ✅ Conformance 驗收流程
第一步 逐項交叉比對五維度：
| 目標規格 | plan §2 | U1-U6 覆蓋率 |
| 驗收條件 | tasks §6 | §6.1-§6.4 grep 通過記錄 |
| 不可動清單 | tasks §7 | 各報告 §6「✅ 未觸碰」、業務碼 100% 零改 |
| 提示詞歸檔稽核 | prompts/ | ls grep RESCUE-1，plan/tasks/runs(C1-C4)/check 皆存在、缺則補建 |
| msg.txt 草稿完整性 | 各報告 §8 | 含完整 msg 指令與草稿 |
第二步 產 Conformance 驗收報告（三合規性 + 總結）。§7.2 純 DOC 顯式豁免、予認可。

### 🗃️ 收官自動化動作（全合規才執行）
第一步 更新 TODO.md：✅ 已完成新增「DOC-Refactor 遺失治理文件挽救」表（C1-C5 待 baron 回填）；進行中移除 RESCUE-1 條目；索引標 ✅；歷史全量 hash 自癒。
第二步 歸檔 baton（逐檔顯式 git add，嚴禁 git add ./-A/<目錄>）：
  mv plan→plans/ + git add;mv tasks→tasks/ + git add;mv C1-C4 報告→executions/ + git add。
  ⚠️ Q3：PIPE-SPEC v8 本體 + QUEUE-1 v2 本體維持 baton 長駐、不 git add。
第三步 確認 baton/ 只剩 README + 長駐（QUEUE-1 v2 plan + PIPE-SPEC specification）。
第四步 檢查 prompts/ RESCUE-1 皆 tracked，缺則補 git add（plan/tasks/C1-C4/check）。
第五步 commit 前 staged 自檢：git diff --cached --name-only。
第六步 產保存 executions/2026-07-01_RESCUE-1_C5_執行.md（Conformance 五維度 + staged 自檢輸出實貼 + §8 一行 commit）；git add 之。

### 🛑 停止指令
完成 TODO 更新與 baton 歸檔後立即停止。嚴禁自發 git commit/push（草稿寫 /tmp/RESCUE-1_C5_msg.txt 交 baron）/ 改已歸檔文件。
```

---

## 執行結果摘要

- ✅ Conformance 五維度全綠 → 收官歸檔（依 tasks §8 C5；主 repo 就地、無 deviation）
- baton 一次性歸檔：plan→plans/、tasks→tasks/、C1-C5 報告→executions/（逐檔 git add）；PIPE-SPEC v8 + QUEUE-1 v2 本體依 Q3 baton 長駐不歸檔
- TODO 結案：RESCUE-1 移入 ✅ 完成表 + 索引 + hash 自癒
- §7.2 純 DOC 顯式豁免（無 code handoff）
- checkout 執行報告 `executions/2026-07-01_RESCUE-1_C5_執行.md`（含 staged 自檢輸出實貼）
- commit / push：未執行（baron 手動、草稿 /tmp/RESCUE-1_C5_msg.txt）

## 後續引用

- 依據 plan：`plans/2026-06-28_RESCUE-1_..._plan_v1.md`（v1.2·收官歸檔）
- 依據 tasks：`tasks/2026-07-01_RESCUE-1_..._tasks.md`（§8 C5·收官歸檔）
