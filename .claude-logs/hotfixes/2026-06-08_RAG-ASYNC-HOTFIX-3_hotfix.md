# RAG-ASYNC HOTFIX-3 — 緊急熱修復：zh 來源履歷無 per-section chunk（#4·選 B）

> **警示**：本文件為**緊急熱修復 (Hotfix) 計畫（doc-only）**。程式碼以 diff 寫入本文件、**尚未落地實檔**；待 baron 過目後下「HOTFIX-3 Run」才套用。
> **修復原則**：只動 `run_phase3` 的 `is_zh` 分支（改建 per-section rag_sections），不碰 en 主路、不碰 #1/#2/#5、不改翻譯輸出。
> **選項**：baron 拍板 **B（is_zh 走 `ctx.ingestion.tiles` 不翻譯、建 per-section rag_sections）**。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-3** | `待 baron 回填` | fix(rag): RAG-ASYNC-HOTFIX-3 — zh 來源履歷 P3 改建 per-section rag_sections（修 #4 單一容器） |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)
- **現象描述**：**zh 來源**履歷（`source_lang` 以 `zh` 開頭）的 B 軌 P4 向量庫，chunk **不依 section 切**——整份履歷被當單一容器、僅由 P4 `size-cap` 切「任意 token 窗」，切點落在 section 中間 → 召回精度低於 en 履歷。
- **受災範圍**：zh 來源履歷的 RAG 召回粒度（en 履歷不受影響）；**非崩潰**（仍可召回），故易被忽略；en/zh **品質不對稱**。
- **首發證據**（第一性原理體檢 / live trace）：
  ```
  run_phase3 is_zh 路 → zh_text = full_text（跳 _restore_sections_markdown）
                      → rag_sections = _single_container_sections(整檔)   # 單一容器
  P4 → 對單一巨容器走 size-cap → 切點為任意 token 窗（非 section 邊界）
  ```

### 2. 真因診斷 (Root Cause)
- **技術細節**：`run_phase3` 的 `is_zh` 分支只做「`zh_text = full_text`」（原文已中文、**正確地跳過翻譯**），但**順帶也跳過了結構化**——en 路的 per-section 結構是 `_restore_sections_markdown` 內 `_collect_render_slots` + `_collect_rag_sections` 的副產物；is_zh 不走這條，故只剩 `_single_container_sections` 兜底。
- **為何漏**：RAG-ASYNC plan v2 只設計 **en→zh 主路** 的 per-section chunking，**未規範 is_zh 路的結構化**；C6 對 is_zh 給了「單一容器 fallback」這個**合理但粗**的選擇（當時聚焦 chunks=1 主修，未顧及 zh 對稱性）。
- **定位**：`file:///pipelines/resume_pipeline.py`（`run_phase3` is_zh 分支 → `_single_container_sections`）。

---

## 熱修復修法 (Minimal Hotfix)

**is_zh 有 section 時，走 `ctx.ingestion.tiles`（原文即 zh）建 per-section `rag_sections`——複用既有 `_collect_render_slots` + `_collect_rag_sections(translate=False)`，不翻譯、不新增 helper。** zh 路「原文＝譯文」，故 `summary_key`（原文標題 path）與 P2 `section_summaries` key、與 #1 之 chunk node_key **天然完全對齊**（無跨譯落差）。

### `pipelines/resume_pipeline.py` — `run_phase3` is_zh 分支
```diff
  rag_sections: List[Dict[str, Any]] = []
  if is_zh:
      zh_text = full_text
-     rag_sections = self._single_container_sections(full_text, ctx)
+     # === [RAG-ASYNC-HOTFIX-3] #4-B：zh 走 tiles 不翻譯、建 per-section rag_sections ===
+     # 原文即繁中：複用 en 路的收集器（translate=False → text=原文）；summary_key=原文標題 path，
+     # 與 P2 section_summaries（zh 不重譯）及 #1 chunk node_key 天然對齊（無跨譯落差）。
+     # 無 section（極少數無 # 標題）才退單一容器（size-cap 兜底）。
+     if sections:
+         _slots: List[Dict[str, Any]] = []
+         self._collect_render_slots(sections, 0, _slots)
+         self._collect_rag_sections(_slots, {}, False, rag_sections)
+     else:
+         rag_sections = self._single_container_sections(full_text, ctx)
+     # === [RAG-ASYNC-HOTFIX-3 END] ===
  elif sections and not degraded:
      zh_text = self._restore_sections_markdown(sections, inj, tr, translate=True, rag_sink=rag_sections)
  else:
      zh_text = self._translate_whole(full_text, inj, tr, translate=True)
      rag_sections = self._single_container_sections(zh_text, ctx)
```
> - `_collect_render_slots(sections, 0, _slots)`：收集原文 slots（含 #1 加的 `key`=原文標題 path）。
> - `_collect_rag_sections(_slots, {}, False, rag_sections)`：`translate=False` → `text = slot["text"]`（原文 zh）；`summary_key = slot["key"]`。
> - **不改** `zh_text = full_text`（閱讀視圖 final_zh 輸出 byte 不變）；degraded（en 退化）與 zh-無-section 仍走單一容器。

---

## regression 預防與 E2E 驗證（Run 階段執行）

### 1. 受影響模組單元測試（新增）
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
```
- `test_p3_zh_source_builds_per_section`：`source_lang="zh*"` + 多 section tiles → `run_phase3` 後 `ctx.rag_sections` **為 per-section（非單一「履歷全文」容器）**、title=原文 zh、`summary_key`=原文 path、內容未加任何譯文前綴（證未重譯）。
- `test_p3_zh_no_section_falls_back_single`：zh + 無 section（tiles=[]）→ 仍退單一容器（兜底不變）。
- `test_p3_zh_summary_attaches`（接 #1）：zh `section_summaries`（原文 key）→ `build_chunk_markdown(ctx.rag_sections, …)` Chapter Summary 貼上（zh 路 summary_key==P2 key、必中）。
- **不退化**：既有 `is_zh` 相關 P3 測試 + en 主路測試全綠（final_zh 輸出 byte 不變）。

### 2. 本地 E2E（baron 影子）
```
影子上傳 zh 來源履歷 → P4 log chunks 數 ≈ section 數量級（非 1 個巨容器被 size-cap 任意切）
→ retrieve 分數分布與 en 履歷對等（per-section 邊界）
```

### SOP 核查（Run 時補）
```
database：is_zh 分支無 DB 操作、無裸 commit ✅
logging：本分支無新增 logger.error；既有 _read_source_text 失敗 logger.warning(exc_info) 不變 ✅
```

### 不可動遵守
- en 主路（`elif sections and not degraded`）/ degraded fallback — **未動**。
- `run_phase3` 的 `zh_text = full_text`（final_zh/en 閱讀視圖輸出）— **byte 不變**。
- `_collect_render_slots` / `_collect_rag_sections` — 僅**複用**（不改其邏輯；本 hotfix 只在 is_zh 多呼叫一次）。
- `rag_processor.py` / `rag_retriever.py` / `rag_indexer.py` — 零改動。
- 主 repo 目錄 — 未讀寫。

---

## ⚠️ 依賴與邊界（誠實說明）

1. **依賴 #1（RAG-ASYNC-HOTFIX-1）**：本 hotfix 用 `_collect_render_slots` 的 slot `key` 與 `_collect_rag_sections` 的 `summary_key`——**這兩個欄位由 #1 引入**。若 #1 未落地，slot 無 `key` → `summary_key` 為空（per-section 結構仍成立、但 Chapter Summary 對位失效）。**故 #1 必須先於或與本 hotfix 同落地**；建議 **#1 + #4 合併一張 Run**（或 #1 先）。
2. **zh 路的 #1 落差不存在**：zh「原文＝譯文」，`summary_key`（原文 path）== P2 `section_summaries` key == chunk node_key，三者天生一致；故 zh 路是 #1 修法最乾淨的受益者。
3. **degraded（en 退化）不在本 hotfix 範圍**：en 無 `#` 標題塌成單一巨 section 的退化路，仍走 `_translate_whole` + 單一容器（屬另一議題、size-cap 兜底）。
4. **重捕**：本 hotfix 改變 **zh 來源履歷** 的 chunk 邊界（per-section）→ 衝擊該類文件 golden D2/D3；en 履歷 byte 不變。**zh 來源 golden 須重捕**（en 不需）。

---

## baron 執行命令與 Commit Message 草稿（Run 落地後）

```bash
# 改前 .bak（Run 時備）；入庫：1 業務碼 + 測試 + .bak（baton 下 hotfix.md 收官移 hotfixes/）
git add pipelines/resume_pipeline.py tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-3_*.bak
git add .claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md
git add .claude-logs/prompts/2026-06-08_RAG-ASYNC-HOTFIX-3_doc_提示詞.md .claude-logs/prompts/INDEX.md .claude-logs/TODO.md
git commit -F /tmp/RAG-ASYNC-HOTFIX-3_msg.txt
```

### Commit message 草稿
```
fix(rag): RAG-ASYNC-HOTFIX-3 — zh 來源履歷 P3 改建 per-section rag_sections（修 #4 單一容器）

#4（選 B）：run_phase3 is_zh 路只做 zh_text=full_text、順帶跳過結構化 → rag_sections 為單一容器
→ zh 來源履歷 P4 chunk 不依 section 切、size-cap 切任意 token 窗、召回粒度低於 en（不對稱）。
修法：is_zh 有 section 時走 ctx.ingestion.tiles（原文即 zh）建 per-section rag_sections——
複用 _collect_render_slots + _collect_rag_sections(translate=False)、不翻譯、不新增 helper；
zh「原文＝譯文」故 summary_key（原文標題 path）與 P2 section_summaries key、#1 chunk node_key 天然對齊。
不改 zh_text=full_text（final_zh 輸出 byte 不變）；degraded/zh-無-section 仍走單一容器兜底。
依賴 #1（slot key / summary_key）；建議與 #1 合併或先後落地。新增 zh per-section 單元 + 接 #1 摘要對位測試。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
> ⚠️ 本檔 doc-only，msg 寫進文件（Run 落地時才寫 /tmp）。

---

## 回退與備案

```bash
git revert <HOTFIX-3 hash>          # 或還原 .bak
```
僅改 is_zh 分支之 rag_sections 建構、不動翻譯輸出與其他路；回退即恢復單一容器、無資料遷移、無副作用。

---

## 後續（非本 hotfix）
- **與 #1（必要）+ #2（可選）合併落地**：三者同源（node_key / slot key / rag_sections 結構）；建議 **#1+#4 至少合併**，#2（rag_tree）可同批或緊接。
- **degraded（en 退化）per-section** → 另議（屬 heading 退化處理）。
- **#5 聯絡資訊** 仍 backlog。
- **治本（流程）**：DOC-Refactor 補 WORKFLOW_SOP「各路 edge path（zh 來源 / 退化 / 無 section）需在 plan 規範 + 收官前覆蓋測試」——本 #4 正是 plan 只設計 en 主路、未規範 zh edge 所致。
