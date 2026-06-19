# PIPE-SYNC-4 plan 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-19 |
| 任務代號 | PIPE-SYNC-4 |
| 觸發 Commit | plan（階段 1）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-19_PIPE-SYNC-4_litedoc與section_engine落地回灌母plan與SPEC_plan_v1.md` |
| 觸發情境 | PIPE-SECTION-BASE + PIPE-LITEDOC 收官後，baron 拍板「全部回灌」真理源 |
| 工作流類別 | DOC-Refactor（plan 階段）|

## 正文（原文）
PIPE-SYNC-4 plan：litedoc 落地 + technical 排除分歧 + section_engine HTML formatter 全部回灌母 plan 與 SPEC。
針對前面 drift 盤點做一個 plan、存 baton/。
依據 template/template_plan.md + ref/WORKFLOW_SOP.md + ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md + baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md。不用給 commit 建議。

## 設計脈絡（grep 盤點之 drift 清單·plan 規格依據）
### master plan v10（plans/、版控）
- L72：LiteDoc「news/web/**technical**/未知」→ 矯正 news/web/unknown、technical 歸深結構家族
- L260 §8.5 表：PIPE-LITEDOC ⬜ 待建立 + 依賴 academic → ✅ 已落地〔C1-C8 hash〕、先於 academic、去 technical
- L18/L74/§8.4：「**三大**共用真理源」→ 升「共用真理源家族」〔含 META-NORM 第 4 + section_engine 第 5〕
- L86/L222/L253：絞殺順序註（實際 Resume→Slides→LiteDoc 早於 Academic）
- L183：≥10 門檻 **已正確、不改**
### PIPE-SPEC v7（baton/、不版控、就地 git add 同 PIPE-SYNC-3 先例）
- §1.2：**最大新增** section_engine 共用契約章〔build_section_summaries/collect_render_slots/restore_sections_markdown/render_meta_header(_html)/collect_rag_sections·key=原文標題 path〕
- §1.1.1：litedoc 補 date/url/publisher/translated_title 旁路登記〔同 D6 登 rag_sections〕
- L140 §1.3 表：**SPEC 已正確**（news/web/未知無 technical）→ 不改該格
- 三大措辭〔L4/L15/L52/L75〕→ 家族
- bump v8
### 次要（全部回灌、納入）
- docs/HOW_TO_ADD_DOC_TYPE.md：B 軌加 doc_type 範式（@register + 消費 section_engine）
- 資料流程 doc（resume/slides·baton point-in-time）：OQ 評估是否非目標
- 版控差異：master plan 版控 commit;SPEC 就地 git add + .bak→archive
- §7.2 純 DOC 顯式豁免（無 code handoff）
