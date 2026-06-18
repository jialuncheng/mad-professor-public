# PIPE-SYNC-3 Check 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 16:10 |
| 任務代號 | PIPE-SYNC-3 Check |
| 觸發 Commit | PIPE-SYNC-3-Check |
| 相關產出檔案 | C1/C2 執行報告 + 待產 C3 |
| 觸發情境 | 所有 Commit ship 完畢，baron 下達 Conformance 驗收指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
對 PIPE-SYNC-3 執行 Conformance 驗收 + 收官歸檔。
- SOP 校正：先 mv master plan v10 回 baton（Run 階段 plan 暫存鐵律）
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / tasks / C1 / C2 執行報告
- Conformance 三維度：目標規格（plan §2 U1-U8/D1-D7）/ 驗收條件（tasks §6）/ 不可動清單（tasks §7）+ 提示詞稽核 + msg 完整性
- C3 執行報告（template_execution）+ §8 msg
- 收官：TODO 移完成表 + 移除 WIP + 索引 + hash 全量自癒;baton mv 歸檔（plan×2〔任務 plan + master v10〕→plans/、tasks→tasks/、C1-C3 報告→executions/）+ SPEC 就地 git add + 5 prompts + INDEX git add;確認 baton 只剩 README/SPEC/pdf
- 停止：TODO + baton 歸檔後立即停;嚴禁自發 commit/push、嚴禁改已歸檔文件

## 偏差註記（Claude Code）
- master plan v10 自 v10 補註⁷ 已長駐 plans/ 入版控（非 baton task artifact）→ 提示詞「mv 回 baton 再 mv 回 plans」為無意義往返;淨結果相同（最終 plans/、git add、內容＝C2 修改），照做無害;SPEC 才是真長駐 baton 就地 git add 者
- 提示詞 §8 C3 msg 草稿無 Co-Authored-By 行 → 報告補 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`;msg 路徑 `/tmp/`→`tmp/`
