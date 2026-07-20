# LANG-DETECT plan 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：LANG-DETECT（F4、cover-prompt +language 欄語言偵測）
- **階段**：階段 1（plan）
- **來源**：baron 提示詞（PIPE-INGEST-FITZ checkout 收官後接續）

---

## 提示詞原文

```
LANG-DETECT（F4、cover-prompt +language 欄；義文樣本進場前必做）
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
以及其他上層規劃文件

不用給commit建議
```

---

## 備註

- 「上面內容」＝PIPE-INGEST-FITZ checkout 報告 §7 銜接所列後續佇列首項 **LANG-DETECT（F4）**；技術種子＝`baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` §F4（schema 已多語、破的是偵測層；cover-prompt +`language` ISO 欄 → 設 source_lang；`classify_source_lang` 保留原職不兼差；多語 glossary 前置、義文進場前必做）。
- 產出落點：`baton/`（依 WORKFLOW_SOP §3 Run 前暫存鐵律）。
- 明確排除 commit 拆分建議（屬階段 2 tasks）。
