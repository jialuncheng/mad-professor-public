`````markdown
# 2026-06-08 — RAG-ASYNC-HOTFIX-2 doc（#2 B 軌補產 rag_tree.json·選 B 完整版）提示詞

> **收到時間**：2026-06-08（UTC+8）
> **任務代號**：RAG-ASYNC-HOTFIX-2（BE-Hotfix·**doc-only**）
> **觸發情境**：第一性原理體檢 #2（B 軌不產 rag_tree.json → 檢索端章節引用/paper_title/公式相鄰降級）；baron 選 **B（完整產）**，要 doc-only（程式碼寫進文件、不動實檔）。

---

## 完整提示詞

````
#2 選 B

針對以上面內容做一個 hotfix 文件
存檔路徑 baton/

依據
template_hotfix.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

詳細說明原因
程式碼也加入文件
包含 commit
````

### 背景（#2 / 選 B）
- **#2**：A 軌 `rag_processor.process` 產 `rag_tree.json`（key_map / 巢狀節點 / translated_title / 公式）；rag_retriever 26 處用它做 section_path 引用、references paper_title、公式相鄰擴展。B 軌 `rag_indexer` 不產 → `load_rag_tree` 回 {} → 優雅降級（retrieval 正常、引用/標題/公式擴展缺）。
- **選 B（完整產）**：在 B 軌 `rag_indexer` 依 P3 `ctx.rag_sections` 自建**完整 rag_tree**（key_map + 巢狀節點 + translated_title + 公式相鄰），寫 `rag_tree.json`，使 B 軌履歷的章節引用/paper_title 與 A 軌對等。

### 產出要求（doc-only）
- 依 template_hotfix 結構：阻斷現象/真因/修法 diff/regression 驗證/回退。
- **程式碼以 diff 寫進文件、不動實檔**（碼還原狀態保持）。
- 含 baron commit 命令 + msg 草稿（寫入文件、不寫 /tmp）。
- 存 baton/。

### 🛑 停止
產 hotfix 文件後立即停止；不動實際碼、不自發 commit。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成（hotfix doc 產出 baton/、純文件）
- 是否動業務代碼：否（diff 僅寫進文件、待 Run 才落地）；是否 commit：否
- 待 baron 過目 → 下 Run 執行

## 後續引用

RAG-ASYNC-HOTFIX-2 doc：#2 選 B——B 軌 rag_indexer 補產完整 rag_tree.json（key_map+巢狀+translated_title+公式），對等 A 軌章節引用/paper_title；doc-only、待 Run。
`````
