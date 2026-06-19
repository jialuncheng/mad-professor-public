# PIPE-SYNC-4 C1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 13:54 |
| 任務代號 | PIPE-SYNC-4 C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-SYNC-4_C1_執行.md` |
| 觸發情境 | baron 確認 tasks 後、下達 C1 執行指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
扮演 Claude Code、執行單一 Commit C1（master plan v10 回灌·D1-D4）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP / **plan（全局策略 z）** / tasks（§8 C1）
- 三防線：物理（§7 不可動·零業務碼）/ 測試（§6.1 grep）/ 文件（不自發 commit）
- 備份：`cp plans/...PIPE_..._plan_v10.md archive/2026-06-19_PIPE-SYNC-4_C1_PIPE_plan_v10.md.bak`
- 實作（tasks §8 C1）：D1 L72 technical 排除矯正〔news/web/未知 + technical 歸深結構家族〕/ D2 L260 §8.5 LiteDoc ✅+hash+順序 / D3 L18/L74/§8.4 三大→共用真理源家族〔roster 補 META-NORM+section_engine〕/ D4 L86/L222/L253 絞殺順序實況註 / §99.2 加 Revision;`<!-- === [PIPE-SYNC-4 C1] === -->` 包裹
- 驗收：§6.1 grep + 零業務代碼旁證
- TODO：C1 ✅ / C2 🟡 + hash 自癒
- 產出：`baton/..._C1_執行.md`（template_execution、§1 對齊欄 + §自評、嚴禁 git add baton）;msg → `/tmp/PIPE-SYNC-4_C1_msg.txt`（**簽名補 Opus 4.8 (1M context)**）
- 停止：報告 + TODO 後立即停;嚴禁下一 Commit / 動非本 Commit 文件 / 自發 commit

## 偏差註記
- master plan v10 為版控檔（tracked）→ C1 直接 git add + .bak→archive。
- 提示詞 msg 草稿缺 Co-Authored-By → 補 `Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
