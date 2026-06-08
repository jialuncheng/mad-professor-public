# WORKFLOW-3 Check（C4 Checkout 收官）提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-08 18:22 |
| 任務代號 | WORKFLOW-3 Check |
| 觸發 Commit | WORKFLOW-3-Check（C4 Checkout）|
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | plan_v1/v2/v3 + tasks + C1/C2/C3 執行報告（baton/）|
| 觸發情境 | C1/C2/C3 全部 commit 完畢，baron 下達 Conformance 驗收與收官指令 |

---

## 正文（原始提示詞全文摘要）

### 任務資訊
- 任務編碼：WORKFLOW-3 / Checkout（C4）/ 工作流類別：DOC-Refactor
- Plan：`baton/2026-06-08_WORKFLOW-3_..._plan_v3.md`；Tasks：`baton/..._tasks.md`
- 執行報告：baton/ C1/C2/C3 執行.md

### Conformance 五維度驗收
1. 目標規格（plan_v3 §2 U1-U5）逐項對應 C1-C3 報告。
2. 驗收條件（tasks §6.1-§6.4）每條 grep 在 C1/C2/C3 報告 §5 有通過記錄。
3. 不可動清單（tasks §7）全報告 §6 標 ✅ 未觸碰。
4. 提示詞歸檔稽核：`ls prompts/ | grep WORKFLOW-3` 確認 Tasks/C1/C2/C3/Check 實體存在、缺則補建。
5. 整合測試豁免聲明：本任務 DOC-Refactor + 不跨 Phase handoff → 依 §7.2 + plan §8 Q2-Q3 顯式豁免、C4 報告明載。

### §6.4 Checkout grep
- plan v3 / tasks / C1-C4 報告歸檔到位；baton 清空；TODO ✅。

### 收官動作（Conformance 全綠後）
1. TODO：新增 `### DOC-Refactor WORKFLOW-3` 完成表（C1-C4 + Hash）+ 自 active 移除 + 索引 ✅ + 全量 hash 自癒。
2. baton 一次性 mv + git add：plan v1/v2/v3 → plans/ + tasks → tasks/ + C1-C3 報告 → executions/。
3. 確認 baton 無 WORKFLOW-3 殘留。
4. C4 執行報告**直寫 executions/**（不過 baton）+ git add。
5. msg 草稿寫 `/tmp/WORKFLOW-3_C4_msg.txt`。
   ⚠️ 署名校正：依 CLAUDE.md 全局規範用 `Claude Opus 4.8 (1M context)`（提示詞模板誤寫 Sonnet 4.6、以全局規範為準）。

### 停止指令
完成 TODO/baton 歸檔/C4 報告後立即停止；不自發 commit/push、不改已歸檔文件。
