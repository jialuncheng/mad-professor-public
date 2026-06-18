# PIPE-LITEDOC plan 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 |
| 任務代號 | PIPE-LITEDOC |
| 觸發 Commit | plan（階段 1）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_PIPE-LITEDOC_litedoc路策略管線_plan_v1.md` |
| 觸發情境 | PIPE-SECTION-BASE（第 4 共用真理源）收官後，baron 下達第 3 路 litedoc plan |
| 工作流類別 | BE-Refactor（plan 階段）|

## 正文（原文）
litedoc plan。針對上面對話內容做一個 plan、存 baton/。
依據 template/template_plan.md + ref/WORKFLOW_SOP.md + ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md + baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md。不用給 commit 建議。

## 設計脈絡（對話收斂結論·plan 規格依據）
- **範圍**：第 3 路 litedoc = news / web / unknown（factory 既有 fallback）;technical 移出本路（深結構家族、歸 academic/book 路 4/5）。
- **本質**：academic-lite——P1 MinerU+md_cleaner（非 Vision）、消費已落地 section_engine（PIPE-SECTION-BASE）+ 三大真理源（DomainNormalizer/Glossary/Translator）+ rag_indexer。
- **P1-1 合約阻擋**：IngestionMetadataSpec（extra=forbid）無 date/publisher/url/org → 走 raw_metadata 旁路 + META-NORM 飛輪欄名（publisher 可順手 venue）;INFRA-4 後統一收合。OQ-1 降為「照 resume/slides 慣例」。
- **扁平風險**：news/web 短、退化 1-2 節點可接受（OQ-A 移交下一路技術文件、本路非 blocker）;A 軌不設 flat_structure=True、用 structure_news/web.txt 抽層級。
- **A 軌移植清單**：structure_news/web.txt（P1/P2 sectioning）/ rag_indexer:69 門檻加 news/web / STYLE_HINTS（translator.py:38-39 已有、免移）/ extra_info 簡化（P2 abstract+section_summaries 天然涵蓋、免移）。
- **§7.2**：BE-Refactor + 真 code handoff（P2 產 section_summaries→P4 取）→ 不豁免、key-changing transform 測試。
- **接縫契約**：key=原文標題 path、P2 產/P3 帶/P4 取同基準（RAG-ASYNC-HOTFIX-1）。
