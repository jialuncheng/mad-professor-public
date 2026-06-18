# PIPE-SYNC-3 C1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 15:21 |
| 任務代號 | PIPE-SYNC-3 C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-14_PIPE-SYNC-3_slides路落地經驗回灌_tasks.md` |
| 觸發情境 | baron 下達執行 C1 指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
執行單一 Commit C1（SPEC v7 同步）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C1）
- 依 tasks §8 C1 改 SPEC（D1 slides P3 drift / D2 golden A/B 軌 §1.3.1 / D3 alt LaTeX R3.2 / D4 is_blank §1.3.1+L242 / D6 rag_sections §1.1.2 / D7 rag_tree_json §1.1③ / D5 清洗層一行 / bump v7）
- 三防線：① 物理（§7 不可動：四凍結合約型別欄/contracts.py/業務代碼/其他路次零碰）② 測試（§6.1 grep + 全套件 pytest 維持基線）③ commit/push baron 手動
- 備份：cp SPEC → .claude-logs/archive/2026-06-14_PIPE-SYNC-3_C1_PIPE-SPEC.md.bak
- TODO：C1 ✅、C2 🟡 WIP + git log hash 自癒
- 產出：執行報告 baton/..._C1_執行.md（暫存、不入 Git）
- §8 baron 命令 + msg 草稿;停止：產報告 + TODO 後立即停;嚴禁自發 commit/push

## 偏差註記（Claude Code）
- 提示詞 §8 msg 草稿無 Co-Authored-By 簽名行 → 報告補 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`;msg 路徑 `/tmp/`→`tmp/`（工作區根、對齊慣例）
