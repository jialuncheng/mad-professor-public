# PIPE-SYNC-3 C2 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 15:35 |
| 任務代號 | PIPE-SYNC-3 C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-14_PIPE-SYNC-3_slides路落地經驗回灌_tasks.md` |
| 觸發情境 | baron 下達執行 C2 指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
執行單一 Commit C2（master plan 補註⁸）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C2）
- 依 tasks §8 C2 改 master plan v10：§8.5 PIPE-SLIDES 條目「B 軌另捕」措辭修正（capture 捕 A 軌、B 軌走 shadow diff + 改善豁免）+ §99.2 加補註⁸（不 bump 主版本、承 HOTFIX-6 A/B 軌更正）
- 三防線：① 物理（§7 不可動：只動 master plan 一檔、不碰 SPEC/contracts.py/業務碼/其他路次）② 測試（§6.2 grep「B 軌另捕」0 命中 + 全套件 pytest 基線）③ commit/push baron 手動
- 備份：cp plan_v10 → .claude-logs/archive/2026-06-14_PIPE-SYNC-3_C2_plan_v10.md.bak
- TODO：C2 ✅、C3 🟡 WIP + git log hash 自癒
- 產出：執行報告 baton/..._C2_執行.md（暫存、留 baton 至 C3）
- §8 baron 命令 + msg;停止：產報告 + TODO 後立即停;嚴禁自發 commit/push、嚴禁提前 mv

## 偏差註記（Claude Code）
- 提示詞 §8 msg 草稿無 Co-Authored-By 簽名行 → 報告補 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`;msg 路徑 `/tmp/`→`tmp/`（工作區根）
- master plan v10 已入版控（plans/）、非長駐 baton → C2 直接就地改 plans/ 檔（同 §8 git add 清單）
