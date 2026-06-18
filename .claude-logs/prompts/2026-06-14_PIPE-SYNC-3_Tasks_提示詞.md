# PIPE-SYNC-3 Tasks 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 15:00 |
| 任務代號 | PIPE-SYNC-3 Tasks |
| 觸發 Commit | PIPE-SYNC-3-Tasks |
| 相關產出檔案 | `.claude-logs/baton/2026-06-14_PIPE-SYNC-3_slides路落地經驗回灌_tasks.md` |
| 觸發情境 | baron 同意 plan v3 規格（D1-D7、六 OQ 全定案），下達任務拆分指令 |
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
依 plan v3 拆 commit。
- 任務 PIPE-SYNC-3 / DOC-Refactor / plan：baton/2026-06-14_PIPE-SYNC-3_..._plan_v1.md
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / template_tasks.md
- 工作目錄硬規則：只動 SPEC + master plan 兩說明真理源、嚴禁動 .py/.html/.css 程式;產出留 baton/
- tasks.md §0.5 成果盤點 + §1 TL;DR（中文括號命名）+ §8 六維度 Commit 拆分表格
- 最後 Commit 必為 Checkout;每 Commit 語意完整可逆
- 同步更新 TODO.md（高優先區最前、🟡 WIP）
- Plan 歸檔時機警告：baton/ 一律 Checkout 才一次性 mv + git add
- 產出 tasks.md + 更新 TODO.md 後立即停止;嚴禁產執行.md/改代碼/提前 mv/commit/push

## 拆分要點（D1-D7、兩真理源）
- SPEC sync（D1 slides P3 drift / D2 golden A/B 軌 §1.3.1 / D3 alt LaTeX R3.2 / D4 is_blank §1.3.1+L242 / D6 rag_sections §1.1.2 / D7 rag_tree_json §1.1③ / D5 清洗層至多一行 / bump v7）
- master plan sync（D2 §8.5「B 軌另捕」措辭修正 + 補註⁸ 不 bump 主版本）
- Checkout 收官（§7.2 DOC 豁免、同 PIPE-SYNC-2）
- 四凍結合約型別欄位零變動、不改 contracts.py 程式
