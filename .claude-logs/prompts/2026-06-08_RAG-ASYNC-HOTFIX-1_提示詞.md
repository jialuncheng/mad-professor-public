`````markdown
# 2026-06-08 — RAG-ASYNC-HOTFIX-1（#1 section_summaries key 穿線 + #3 dead code）提示詞

> **收到時間**：2026-06-08（UTC+8）
> **任務代號**：RAG-ASYNC-HOTFIX-1（BE-Hotfix）
> **觸發情境**：RAG-ASYNC 收官後第一性原理體檢，發現 #1（section_summaries 原文 key vs 譯文 key 對不上 → Chapter Summary 永遠進不了 chunk、C5 白做）+ #3（_load_index_meta dead code）。baron 指定只修 #1+#3。

---

## 完整提示詞

````
#1, #3

針對以上面內容做一個 hotfix
存檔路徑 baton/

依據
template_hotfix.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

詳細說明原因
程式碼也加入
包含 commit
````

### 背景（第一性原理體檢之 #1/#3）
- **#1（🔴 嚴重）**：P2 `_collect_summary_targets` 走 `ctx.ingestion.tiles`（原文樹）→ section_summaries key=原文標題 path；P3 `_collect_rag_sections` 用 zh_by_index 譯文當 title；P4 `rag_indexer._walk` 用譯文 title 查 summaries → **MISS** → Chapter Summary 永遠不進 chunk → Strategy B 靜默退化成 A、C5 白做。live repro 證實 `"Chapter Summary 有進去嗎？ False"`。
- **#3（🟢 清理）**：C6 後 run_phase4 改呼 rag_indexer（自帶 index_meta），`resume_pipeline.py::_load_index_meta` 已無 caller、dead code。
- **不修**：#2 rag_tree（看 RAG-4 roadmap 另排）/ #4 zh per-section（backlog）/ #5 聯絡資訊（延後）。

### 修法
- **#1 穩定 key 穿線**：`_collect_render_slots` 加 `path_prefix`、title slot 帶 `key`=原文標題 path（與 P2 同式）；`_collect_rag_sections` 把該 key 存為 rag_section 的 `summary_key`；`rag_indexer._walk` 改以 `sec["summary_key"]` 為首選查 summaries（保留 node_key/title fallback、向後相容）。
- **#3**：移除 `_load_index_meta`。
- 補**接縫整合測試**（P3 譯後 rag_sections + 原文 key summaries → P4 Chapter Summary 真的貼上）。

### 防線
- BE-Hotfix：logging/database SOP；改前 .bak；`# === [RAG-ASYNC-HOTFIX-1 START/END] ===` 包裹；不自發 commit、msg 寫 /tmp。

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（_collect_render_slots/_collect_rag_sections + 移除 _load_index_meta）+ rag_indexer.py（_walk summary_key 首選）+ test；各 .bak
- 驗收：接縫整合測試（Chapter Summary 貼上）+ 全套件不退化
- 是否動業務代碼：是；是否 commit：否（待 baron）

## 後續引用

RAG-ASYNC-HOTFIX-1 修 #1（穩定 summary_key 原文標題 path 穿線 P2/P3/P4 → Chapter Summary 真正生效）+ #3（dead code）；補接縫整合測試。#2/#4/#5 分流 backlog。
`````
