# PIPE-SYNC-3 plan 產出提示詞

## 元數據
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 |
| 任務代號 | PIPE-SYNC-3（slides 路落地經驗回灌母 plan 與 SPEC）|
| 工作流 | DOC-Refactor |
| 觸發情境 | slide hotfix 全集（HOTFIX-1~6 + RAG-12-HOTFIX-1）落地後，評估兩真理源（PIPE-SPEC / PIPE master plan v10）需更新；同 PIPE-SYNC-2 對 resume 之回灌 |

## 正文（原文）
開 PIPE-SYNC-3 的 plan、把前面全部都加進去（D1-D5）
針對上面內容做一個 plan、baton/
依據 template/template_plan.md / ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
不用給 commit 建議

## 評估 findings（回灌清單）
- D1🔴：SPEC L134 SlidePipeline P3「100% Bypass 一鍵」→「逐頁翻譯與排版還原」（drift；master plan 補註⁷ 已改、SPEC 表漏改）
- D2🔴：master plan L258「B 軌另捕」+ SPEC 全域 → 釐清 `capture slides` 捕 A 軌（PipelineCore）、B 軌走 diff A 軌 golden + 改善豁免、無 B 軌另捕（HOTFIX-6 A/B 軌更正進真理源）
- D3🟡：SPEC R3.2 alt 對齊 → 補跨軌契約：alt 可能含 LaTeX/`][()` → 前端 renderMarkdownWithMath 保護圖片整段（RAG-12-HOTFIX-1）+ B 軌 _safe_alt 全形化（HOTFIX-2）
- D4🟡：SPEC §1.3.1 / L242 補 is_blank 頁面類型判定（空白/裝飾/過場頁、含有標題過場頁 → 跳過；HOTFIX-4/5）
- D5🟢：SlidePipeline P3 B 軌清洗層（母片日期/點群/行內粗體/裸URL/title echo/段落正規化）—altitude 低、可選收不收
- 偏差註記：不用 commit 建議；DOC-Refactor、兩真理源長駐 baton（SPEC）/ plans（master plan v10 已入版控）
