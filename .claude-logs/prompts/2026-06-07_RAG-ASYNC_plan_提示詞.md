`````markdown
# 2026-06-07 — RAG-ASYNC plan（P4 共用真理源·全 P2 摘要·Strategy B）提示詞

> **收到時間**：2026-06-07（UTC+8）
> **任務代號**：RAG-ASYNC（plan 階段·純規格）
> **觸發情境**：經 chunks=1 根因盤點 + SPEC/母計畫核對 + P1-P3 一致性盤點後，baron 拍板建 P4 共用真理源 plan。
> **相關產出檔案**：`baton/2026-07-…RAG-ASYNC…plan_v1.md`（本次產出）

---

## 完整提示詞

````
RAG-ASYNC plan
針對上面內容做一個 plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

不用給 commit 建議
把更新母 plan 和 specification 也加入 plan
````

### 對話前文鎖定的決策（baron AskUserQuestion 拍板）
1. **P4 = RAG-ASYNC 共用真理源**（新建 B 軌自有 P4 引擎、五路共用、首落地 resume、不 import rag_processor）。
2. **Strategy B**：chunk 格式 `# {chunk_key}` + Context + Chapter Summary + content（對齊 SPEC §1.4）。
3. **section summary 全部在 P2 同步產**（非 P4 async）；加三條安全鎖（並行 / 非致命 / 可量測）使其不踩 §U6 雷。
4. **規格可改**（baron 校準：plan/SPEC 當初空想、實務逼著改是常態；不可動清單只防程式碼 regression、規格非神聖）。
5. plan 不含 commit 拆分；含母 plan v10 + PIPE-SPEC 同步更新為 plan 目標。

### 盤點背景（plan 的事實基礎）
- chunks=1 根因：切塊器 `MarkdownHeaderTextSplitter([("#","Header")])` 只切 `#`；B 軌 P4 直接餵 `final_zh.md`（HEADING-HOTFIX 後 section 全 `##`、唯一 `#` 是 META header）→ 1 塊。
- SPEC §1.4 原設計：每 chunk `# {chunk_key}` + Context + Chapter Summary；母 plan R4.3：RAG 輸入＝P3 translate JSON。B 軌 P4 兩者皆違（抄捷徑餵閱讀 md）。
- P1-P3 一致性盤點：P1 符合；P2 符合（譯摘要因 extract_terms 簽名提前於 glossary、documented）；**P3 已背離 plan §U4「100% Bypass」→ 逐 section（RESUME-P3），但 SPEC §1.3 / plan §U4 從沒更新（doc-drift）**。

---

## 執行結果摘要

- ⏳ 進行中 → 完成（plan_v1 產出 baton/）
- plan 結構：§0/§1 TL;DR/§2 目標規格/§3 現況與證據/§4 不可動/§5 規格依據/§6 驗證/§7 Open Questions/§99
- 是否動業務代碼：否（plan 階段純文件）
- 待 baron 過目 → tasks 階段拆分

## 後續引用

RAG-ASYNC：P4 共用真理源（chunk-md 自生、Strategy B、不依賴 rag_processor A 軌邏輯）+ P2 全路 section_summaries（三安全鎖）+ SPEC/母 plan 同步（含順手修 §1.3 resume P3 doc-drift）。首落地 resume、修 chunks=1 退化。
`````
