# RAG-ASYNC HOTFIX-1 — 緊急熱修復：section_summaries 跨譯 key 對位失效 + dead code

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正 RAG-ASYNC 收官後第一性原理體檢發現之 #1（嚴重·靜默）+ #3（清理）。
> **修復原則**：只改受災點（summary key 穿線 + dead code），不夾帶 #2/#4/#5（分流 backlog）。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-1** | `待 baron 回填` | fix(rag): RAG-ASYNC-HOTFIX-1 — section_summaries 跨譯 key 穿線 + 移除 dead code |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)
- **現象描述**：RAG-ASYNC 七 commit 全綠結案，但 **C5 辛苦批次產+翻的 `section_summaries` 在真實 en→zh 履歷流程中 100% 取不到** → P4 chunk 的 `Chapter Summary:` 行**永遠不出現** → Strategy B 摘要增強**靜默退化成 Strategy A**（只有 `# + Context + 內文`）。C5 整個 commit 等於白做（浪費 LLM 成本、零效益）。
- **受災範圍**：B 軌履歷 P4 向量庫的**召回品質**（少了設計該有的章節摘要語意增強）；非崩潰（chunks 數正常、retrieval 仍可用），故影子 E2E 看 `chunks≥20` 會**誤判成功**。
- **首發證據（live repro）**：
  ```
  rag_sections      = [{"title":"工作經歷", ...}]          # P3 譯後 title
  section_summaries = {"Working Experience":"...摘要"}      # P2 原文 key
  build_chunk_markdown(...) → "Chapter Summary 有進去嗎？ False"
  ```

### 2. 真因診斷 (Root Cause)
- **技術細節**：三處 key basis 不一致——
  - **P2** `_collect_summary_targets` 走 `ctx.ingestion.tiles`（**原文樹**）→ `section_summaries` key＝**原文標題 path**（如 `"Working Experience"`）。
  - **P3** `_collect_rag_sections` 用 `zh_by_index`（**譯文**）當 section title（如 `"工作經歷"`）。
  - **P4** `rag_indexer._walk` 以**譯後 title** 算 node_key 去查 summaries → `summaries.get("工作經歷")` 對 `{"Working Experience":...}` → **MISS**。
- **為何 6 個 commit + Conformance 全綠卻漏掉**：plan v2 §U3/D1 只寫「`section_summaries: Dict[node_key]`、key 對位巢狀樹」，**從未凍結「key＝何物、且 P2 產／P3 帶／P4 取必須同一基準」之跨 Phase 接縫契約**；C5/C6 各自孤立實作（原文 key／譯文 title）單元測試皆自洽全綠；**全程無一條 P2→P3→P4 串接 + 真翻譯器的整合測試**能照出此接縫斷裂。
- **定位程式碼**：`file:///pipelines/resume_pipeline.py`（`_collect_summary_targets` 原文 key vs `_collect_rag_sections` 譯文 title）/ `file:///processor/rag_indexer.py`（`_walk` 以譯文查 summaries）。

---

## 熱修復修法 (Minimal Hotfix)

**核心：穿一個穩定 key（原文標題 path）貫穿 P2／P3／P4。**

### `pipelines/resume_pipeline.py` — `_collect_render_slots`（title slot 帶原文 key）
```diff
- def _collect_render_slots(self, sections, depth, out):
+ def _collect_render_slots(self, sections, depth, out, path_prefix=""):
      for sec in sections or []:
          title = (sec.get("title") or "").strip()
+         node_key = f"{path_prefix}/{title}" if (path_prefix and title) else (title or path_prefix)
          if title:
-             out.append({"kind":"title","text":title,"level":min(2+depth,6)})
+             out.append({"kind":"title","text":title,"level":min(2+depth,6),"key":node_key})
          ...
          for child in sec.get("children", []) or []:
-             self._collect_render_slots([child], depth+1, out)
+             self._collect_render_slots([child], depth+1, out, node_key)
```
> `slot["text"]` 為**原文**（slots 在翻譯前收集、譯文在 `zh_by_index`），故 `node_key` 即原文標題 path、與 P2 `_collect_summary_targets` 之 node_key **同式同基準**。slot 加 `key` 為附加欄、不影響 RESUME-PERF-1 組裝（rendering 用 text/level）。

### `pipelines/resume_pipeline.py` — `_collect_rag_sections`（存 summary_key）
```diff
  if kind == "title":
-     cur = {"title": text, "level": slot.get("level",2), "content": [], "children": []}
+     cur = {"title": text, "level": slot.get("level",2),
+            "summary_key": slot.get("key",""),   # 原文標題 path（譯後 title 仍存於 "title" 供顯示）
+            "content": [], "children": []}
      sink.append(cur)
```

### `processor/rag_indexer.py` — `_walk`（summary_key 首選查找）
```diff
  if title and is_chunk_meaningful(content, doc_type):
-     summary = (summaries.get(node_key) or summaries.get(title) or "").strip()
+     skey = sec.get("summary_key") or ""
+     summary = (summaries.get(skey) or summaries.get(node_key) or summaries.get(title) or "").strip()
```
> 無 `summary_key`（C3/C4 既有單元呼叫）→ 自動退回 node_key/title，**向後相容**。

### `pipelines/resume_pipeline.py` — #3 移除 dead code
```diff
- @staticmethod
- def _load_index_meta(vectors_dir):
-     ...讀 index_meta.json...   # C6 後 run_phase4 改呼 rag_indexer.index、已無 caller
```

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試 + 補「接縫整合測試」
```bash
$ venv/bin/python -m pytest tests/test_rag_indexer.py tests/test_resume_pipeline.py -q
53 passed
```
新增測試：
- `test_summary_key_lookup_crosslang`：譯後 title + 原文 key summaries + `summary_key` → Chapter Summary 貼上。
- `test_summary_key_absent_falls_back`：無 summary_key → 退回 node_key/title（向後相容 C3/C4）。
- **`test_seam_p3_to_p4_section_summary_attaches`（先前缺的接縫整合測試）**：`run_phase3`（FakeTr 真翻譯使譯文≠原文 key）→ `ctx.rag_sections` 帶 `summary_key`＝原文 path → 以 P2 原文 key 的 summaries 餵 P4 → **Chapter Summary 真的貼上**（含巢狀子節點 path）。

### 2. 本地 E2E 快速復現與驗證（#1 修復鐵證）
```
# 修復前：Chapter Summary 有進去嗎？ False
# 修復後：
Chapter Summary 進得去嗎？ True
# 工作經歷
Context: resume > 工作經歷
Chapter Summary: 候選人工作經歷摘要

OLED 主管
```
全套件：`1 failed, 528 passed, 3 skipped`——528 passed（HOTFIX 前 525 + 3 新測試）；唯一 failed＝既知 `LOG_FORMAT` env flake。

### SOP 核查
```
database：grep .commit() 非 with session.begin → 無命中 ✅（hotfix 無 DB 操作）
logging：移除之 _load_index_meta 含 logger.warning(exc_info)、整方法刪；新增碼無 logger.error ✅
```

### 不可動遵守
- `rag_processor.py` / `rag_retriever.py` / `pipeline_core.py` / `config.EmbeddingModel` — 零改動。
- `_collect_render_slots` rendering 輸出（RESUME-PERF-1 byte 等價）/ run_phase3 final_zh/en 輸出 — 不變（既有 P3 測試全綠）。
- 主 repo 目錄 — 未讀寫。

---

## baron 執行命令與 msg

```bash
# 改前 .bak 已備（archive/）；入庫：4 業務/測試代碼 + 4 .bak（baton 下 hotfix.md 嚴禁 git add）
git add pipelines/resume_pipeline.py processor/rag_indexer.py tests/test_rag_indexer.py tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_rag_indexer.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_test_rag_indexer.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_test_resume_pipeline.py.bak
git commit -F /tmp/RAG-ASYNC-HOTFIX-1_msg.txt
```
> msg 已寫入 `/tmp/RAG-ASYNC-HOTFIX-1_msg.txt`（署名校正為 Claude Opus 4.8 (1M context)）。
> **baton hotfix.md 收官時併入歸檔**（本檔留 baton、由 baron 後續移至 `hotfixes/`）。

---

## 回退與備案

```bash
git revert <HOTFIX-1 hash>          # 或還原 4 支 .bak
```
summary_key 為附加欄、無 summary_key 時自動 fallback、無資料遷移 → 回退無副作用。

---

## 後續（非本 hotfix）
- **#2 rag_tree.json**（B 軌不產、章節引用降級）→ 看 RAG-4 roadmap，建議於 rag_indexer 補最小 key_map+title（共用模組值得）。
- **#4 zh 履歷 per-section**（is_zh 單一容器）→ 修法小（zh 走 tiles 不翻譯建 per-section），可隨後續排入。
- **#5 聯絡資訊不入向量** → RAG 非結構化欄位正解；要做走 chat router 確定性回答，非 chunk PII。
- **治本（流程）**：建議另開 DOC-Refactor，於 WORKFLOW_SOP 加「跨 Phase 接縫契約」章節 + 收官前強制「P1→P4 整合測試（真翻譯器）」，杜絕接縫缺陷一路全綠到結案。
