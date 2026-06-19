# PIPE-SYNC-4 Check 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 14:45 |
| 任務代號 | PIPE-SYNC-4 Check |
| 觸發 Commit | PIPE-SYNC-4-Check（C4 Checkout 收官）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-SYNC-4_C4_執行.md` + 收官歸檔 |
| 觸發情境 | C1-C3 ship 完畢、baron 下達 Conformance 驗收與 Checkout 收官指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行 Conformance 驗收 + Checkout 收官。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / TODO / plan / tasks / C1-C3 執行報告
- **第一步 Conformance 驗收報告**（Chat 輸出）：對照 plan §2 D1-D9（含 D5b）+ tasks §6 測試計畫 + §7 不可動清單，審查 C1-C3 報告——
  - 目標規格：D1 technical 排除矯正 / D2 LiteDoc 狀態順序 / D3 三大→家族 / D4 順序補註 / D5 section_engine 契約 / D5b MetaNormalizer 契約 / D6 litedoc 旁路 / D7 家族措辭 / D8 SPEC v8 + D8.1 不改項 / D9 HOW_TO_ADD B 軌範式
  - 測試：C1/C2/C3 各 grep 驗收
  - 不可動：業務代碼 / 測試 / contracts.py 全「✅ 未觸碰」
- **全綠後收官**：① TODO 移完成〔新增 ## ✅ 已完成 § DOC-Refactor PIPE-SYNC-4 表（C1-C4 hash 待回填）+ 移除進行中條目 + 索引 ✅ + 全量 hash 自癒〕② 產 C4 執行報告 ③ baton 一次性 mv（plan→plans/、tasks→tasks/、C1-C4 報告→executions/）④ git add（plan/tasks/C1-C4 報告/5 提示詞/INDEX/TODO）⑤ 確認 baton 僅剩 README.md ⑥ msg→`/tmp/PIPE-SYNC-4_C4_msg.txt`
- **§7.2**：純 DOC-Refactor、無 code handoff → 顯式豁免
- 停止：TODO + baton 歸檔 + git add 後立即停;嚴禁自發 commit/push、嚴禁改已歸檔文件

## 偏差註記
- SPEC 本體長駐 baton 不版控（不隨 Checkout mv）、其 .bak 已於 C2 入 archive、git add。
- msg 草稿補 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
