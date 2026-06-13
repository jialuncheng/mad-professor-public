# FE-RHYTHM-UNIFY C2 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 23:04 |
| 任務代號 | FE-RHYTHM-UNIFY C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-13_FE-RHYTHM-UNIFY_閱讀視圖垂直節奏統一_tasks.md` |
| 觸發情境 | baron 確認 C1 後下達 C2 執行指令 |
| 工作流類別 | FE-Refactor |

## 正文（原文摘要）
執行單一 Commit C2（統一垂直節奏模型落地·atomic）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C2）/ C1 執行報告（凍結 token 與特殊塊）
- 註解包裹：index.html `/* === [FE-RHYTHM-UNIFY C2 START/END] === */`；主題檔 `/* FE-RHYTHM-UNIFY：垂直 margin 移交 base */`
- 三防線：① 物理——僅改 index.html + 4 主題之垂直 margin、保色票/字族/字級/border/padding ② 測試——grep（FE-RHYTHM-1 0 殘留 / 模型 4 條落地 / :has 0 / 主題垂直 margin 移除）+ 全套件 pytest 綠 ③ 文件——commit/push baron 手動、嚴禁自發
- 備份：5 檔 .bak → .claude-logs/archive/、納入 C2 git add
- TODO：C2 標 ✅、C3 標 🟡 WIP + git log hash 自癒回填
- 產出：執行報告 → baton/2026-06-13_FE-RHYTHM-UNIFY_C2_執行.md（暫存、不入 Git）
- §8 baron 命令：git add 5 檔 + 5 .bak；msg 草稿寫 tmp/；baron 手動 `git commit -F`
- 停止：產報告 + TODO 後立即停；嚴禁執行 C3 / 自發 commit/push

## 偏差註記（Claude Code）
- 提示詞 §8 commit msg 草稿簽名為 `Claude Sonnet 4.6 <noreply@anthreply.com>`（型號+網域皆誤）→ 執行報告更正為當前模型 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
