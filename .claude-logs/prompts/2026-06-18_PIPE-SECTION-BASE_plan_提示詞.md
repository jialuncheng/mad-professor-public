# PIPE-SECTION-BASE plan 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 |
| 任務代號 | PIPE-SECTION-BASE |
| 觸發 Commit | plan（階段 1）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_plan_v1.md` |
| 觸發情境 | 第 3 路（litedoc）設計評估收斂後，baron 拍板「先抽 shared section base、再做 litedoc」（選二·共用真理源先行）|
| 工作流類別 | BE-Refactor（plan 階段）|

## 正文（原文）
先開 shared-section-base 的 plan。針對上面對話內容做一個 plan、存 baton/。
依據 template/template_plan.md + ref/WORKFLOW_SOP.md + ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md。不用給 commit 建議。

## 設計脈絡（對話收斂結論·plan 規格依據）
- **動因**：resume_pipeline 的「遞迴走標題樹 → 逐節點摘要/翻譯/還原」section 機制，technical/academic/book/litedoc 四路都會用 → 再 copy 第 3/4/5 次＝多份重複。baron 拍板本路就抽 shared base。
- **選二定序**（共用真理源先行、同 DOMAIN-NORM/GLOSSARY/TRANSLATOR 先例）：① PIPE-SECTION-BASE plan → ② 執行（從 resume 抽、行為等價、既有測試鎖死、獨立 ship）→ ③ litedoc plan → ④ 執行 → ⑤ PIPE-SYNC-4 回灌真理源。
- **抽取範圍**：`_collect_summary_targets` / `_build_section_summaries` / `_collect_render_slots` / `_restore_sections_markdown` / 並行翻譯骨架（RESUME-PERF-1）/ `_normalize_paragraph_breaks` / heading-degraded fallback / zh edge / `_render_meta_header`。
- **硬約束**：① §規格依據必須對齊「所有已知 consumer」（resume 現狀 + litedoc 草案 + technical/academic/book 的 A 軌特徵），非只 resume，防抽錯抽象。② 行為等價（resume 既有 33 測試全綠＝安全網，RESUME-PERF-1 C1 範式）。③ 接縫契約 key=原文標題 path（RAG-ASYNC-HOTFIX-1）。
- **deviation 誠實列**：屬「抽 shared mixin」、INFRA-3 提及但本案另立 PIPE-SECTION-BASE 代號（INFRA-3 主題為 chunking/TextTiling 解耦、不同）。
