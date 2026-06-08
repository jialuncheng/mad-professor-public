`````markdown
# 2026-06-08 — RAG-ASYNC-HOTFIX-3 doc（#4 zh 履歷 per-section·選 B）提示詞

> **收到時間**：2026-06-08（UTC+8）
> **任務代號**：RAG-ASYNC-HOTFIX-3（BE-Hotfix·**doc-only**）
> **觸發情境**：第一性原理體檢 #4（zh 來源履歷 run_phase3 is_zh 路 → 單一容器、無 per-section chunk）；baron 選 **B（zh 走 tiles 不翻譯、建 per-section rag_sections）**，要 doc-only。

---

## 完整提示詞

````
#4, B

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

### 背景（#4 / 選 B）
- **#4**：`run_phase3` `is_zh` 路 → `zh_text=full_text`（原文已中文、跳翻譯），順帶**跳過結構化** → `rag_sections`=單一容器 → P4 只能 size-cap 切任意 token 窗、喪失 section 邊界；en 履歷有 per-section、zh 沒有（不對稱）。
- **選 B**：is_zh 有 section → 走 `ctx.ingestion.tiles`（不翻譯）建 per-section `rag_sections`（複用 `_collect_render_slots` + `_collect_rag_sections(translate=False)`、summary_key=原文 zh 標題 path、與 P2/#1 天然對齊）。

### 產出要求（doc-only）
- 依 template_hotfix；程式碼以 diff 寫進文件、不動實檔；含 commit 草稿（寫文件）；存 baton/。

### 🛑 停止
產文件後立即停止；不動實際碼、不自發 commit。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成（hotfix doc 產 baton/、純文件）
- 是否動業務代碼：否（diff 僅寫進文件）；是否 commit：否
- 待 baron 過目 → 下 Run 執行

## 後續引用

RAG-ASYNC-HOTFIX-3 doc：#4 選 B——is_zh 走 tiles 不翻譯建 per-section rag_sections（複用既有 helper、summary_key 天然對齊）；依賴 #1 slot key；doc-only 待 Run。
`````
