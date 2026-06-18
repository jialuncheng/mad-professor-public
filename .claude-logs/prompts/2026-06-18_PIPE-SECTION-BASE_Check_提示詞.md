# PIPE-SECTION-BASE Check 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 19:12 |
| 任務代號 | PIPE-SECTION-BASE Check |
| 觸發 Commit | PIPE-SECTION-BASE-Check |
| 相關產出檔案 | plan / tasks / C1-C4 執行報告（baton/）|
| 觸發情境 | C1-C4 ship 完畢、baron 下達 Conformance 驗收 + 收官指令 |
| 工作流類別 | BE-Refactor（Checkout）|

## 正文（原文摘要）
扮演 Claude Code、對 PIPE-SECTION-BASE 執行 Conformance 驗收、全綠後 C5 checkout 收官。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / TODO / plan / tasks（§6）/ C1-C4 _執行.md
- **5 維度 Conformance**：① 目標規格（plan §2 U1-U6 + U3.1）② 驗收條件（tasks §6 grep+pytest）③ 不可動清單（tasks §7）④ 提示詞歸檔稽核（ls prompts/ | grep）⑤ msg.txt §8 完整性
- **C5 收官**：① TODO 移除 WIP + 頂端完成表（C1-C5）+ 索引 ✅ + git log 全量 hash 自癒 ② baton 一次性 mv（plan→plans/、tasks→tasks/、C1-C5 報告→executions/）+ git add ③ git add 7 提示詞 + INDEX ④ ls baton 確認清空（README + 常駐 SPEC/pdf 留）⑤ C5 報告寫 executions/
- §7.2 整合測試：C4 base 層 key-changing + resume 既有整合存在且通過、**免豁免**（BE-Refactor 有真 handoff）
- 停止：TODO + mv + git add 後立即停;嚴禁自發 commit/push、嚴禁改已歸檔報告

## 偏差註記
- C1-C4 已 commit（e400789 / 24db977 / 4078a9e / C4 待回填）、hash 自癒回填完成表。
- §7.2 不豁免（與前 DOC-Refactor 任務不同）——本案 BE-Refactor、P2→P3→P4 真 handoff、C4 已寫 key-changing 整合測試滿足。
