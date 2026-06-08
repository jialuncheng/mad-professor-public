# RAG-ASYNC HOTFIX-2 — 緊急熱修復：B 軌不產 rag_tree.json → 章節引用/paper_title/公式相鄰降級（#2·選 B 完整版）

> **警示**：本文件為**緊急熱修復 (Hotfix) 計畫（doc-only）**。程式碼以 diff 寫入本文件、**尚未落地實檔**；待 baron 過目後下「HOTFIX-2 Run」才套用。
> **修復原則**：只補「P4 產出 rag_tree.json」這一缺口，不碰 #1/#4/#5、不改 A 軌、不改檢索演算法。
> **選項**：baron 拍板 **B（完整產 rag_tree：key_map + 巢狀節點 + translated_title + 公式相鄰結構）**。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-2** | `待 baron 回填` | feat(rag): RAG-ASYNC-HOTFIX-2 — B 軌 rag_indexer 補產完整 rag_tree.json（章節引用對等 A 軌） |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)
- **現象描述**：B 軌履歷在 AI 對話檢索時，**召回正常但引用降級**——無法顯示「出自《paper_title》> 章節 > 子章節」、references 無 paper_title 前綴、無公式相鄰節點擴展。A 軌論文有、B 軌履歷沒有（功能不對等）。
- **受災範圍**：B 軌（影子/將來 Flip 後正式）所有履歷的 RAG-4 章節引用 UX；**非崩潰**（`load_rag_tree` 缺檔回 `{}` → 優雅降級），故易被忽略。
- **首發證據**（第一性原理體檢 grep）：
  ```
  rag_indexer 寫 rag_tree：0（不產）
  BilingualMarkdownSpec.rag_tree_json = None
  rag_retriever：26 處用 rag_tree（key_map / _get_node_from_path / _build_section_title / translated_title）
  A 軌 rag_processor.process：有寫 output_tree_json_path
  ```

### 2. 真因診斷 (Root Cause)
- **技術細節**：A 軌 `rag_processor.process` 會 `_restructure_tree` + `_generate_key_map` 產 `rag_tree` 並寫 `final_{paper}_rag_tree.json`；`ai_core` 載入後 `set_rag_tree` 註冊給 retriever。B 軌 RAG-ASYNC C4 `rag_indexer.index` **只產 FAISS + paper_chunks + index_meta、未產 rag_tree** → retriever `load_rag_tree` 回 `{}` → 三項引用功能全空。
- **為何漏**：RAG-ASYNC plan v2 §U5 將 ④ 輸出列為「FAISS + paper_chunks + index_meta」，**遺漏 rag_tree.json**（SPEC §1.4 index_meta 其實含 `tree_json_file`、A 軌有產）；C4 conformance 測試只驗 `load_vector_store + similarity_search`（不需 rag_tree）→ 沒照出。
- **定位**：
  - 寫端缺口：`file:///processor/rag_indexer.py`（`index()` 無 rag_tree 產出）。
  - 載入鏈（不需改、僅佐證對接）：`file:///paper_manager.py#L101`（`rag_tree_path`）/ `file:///ai_core.py#L95`（讀檔 `set_rag_tree`）/ `file:///rag_retriever.py#L160-185`（`key_map` / `_get_node_from_path` / `_build_section_title`）。

### 3. 對接合約（retriever 實讀欄位，B 軌須照產）
```
rag_tree = {
  "title": <原文標題>,
  "translated_title": <顯示標題>,           # _build_section_title 前綴、references paper_title
  "sections": [
    { "title": <原文>, "translated_title": <譯後>, "level": <int>,
      "content": [ {"type":"text","index":0,"content":<原文>,"translated_content":<譯後>} ],
      "children": [...] }
  ],
  "key_map": { <chunk Header> : <json_path 如 "/sections/{i}/content/0"> }
}
```
- **關鍵不變式**：`key_map` 的 **key 必須等於 B 軌 chunk 的 Header**（＝`# {chunk_key}` 之 chunk_key＝`rag_indexer` 之 `node_key`），否則 retriever `doc.metadata['Header'] in key_map` 對不上 → 引用仍空。
- retriever 取 node 後讀 `node['type']`、`node['translated_content'] or node['content']`；`_build_section_title` 讀 `sections[i].translated_title/title`（故每 section 與 content node 都要帶 translated）。

---

## 熱修復修法 (Minimal Hotfix)

**在 `rag_indexer` 依 P3 `ctx.rag_sections` 自建完整 rag_tree（key_map 以 B 軌 chunk_key 為 key、指向 `/sections/{i}/content/0`），寫 `rag_tree.json`；run_phase4 傳入寫入路徑。** 零依賴 A 軌、零改檢索端。

### `processor/rag_indexer.py` — 新增 `build_rag_tree` + `index()` 寫 rag_tree
```diff
+ import json
+ from pathlib import Path as _Path
+
+ # === [RAG-ASYNC-HOTFIX-2] #2-B 完整 rag_tree（key_map + 巢狀 + translated_title + 公式結構）===
+ def build_rag_tree(sections, doc_type, title="", translated_title=""):
+     """依 P3 譯後 rag_sections 自建完整 rag_tree（對等 A 軌、供 rag_retriever 章節引用）。
+
+     key_map 之 key＝B 軌 chunk Header（= node_key，與 build_chunk_markdown 同式），
+     value＝該節點 text content 的 json_path（/sections/{i}/content/0），使
+     retriever `doc.metadata['Header'] → key_map → _get_node_from_path` 對得上。
+     """
+     tree_sections = []
+     key_map = {}
+     _walk_tree(sections or [], doc_type, "", tree_sections, key_map, "/sections")
+     return {
+         "title": title or "",
+         "translated_title": translated_title or title or "",
+         "summary": "",
+         "abstract": {"content": "", "translated_content": ""},
+         "sections": tree_sections,
+         "key_map": key_map,
+     }
+
+
+ def _walk_tree(sections, doc_type, path_prefix, out_sections, key_map, json_base):
+     for i, sec in enumerate(sections or []):
+         if not isinstance(sec, dict):
+             continue
+         title = (sec.get("title") or "").strip()
+         node_key = f"{path_prefix}/{title}" if (path_prefix and title) else (title or path_prefix)
+         body = _node_content_text(sec)
+         json_path = f"{json_base}/{i}"
+         node = {
+             "title": title, "translated_title": title, "level": sec.get("level", 1),
+             "summary": "",
+             # 內文收斂為單一 text content node（譯後內文 = chunk body；index 0）
+             "content": ([{"type": "text", "index": 0, "content": body,
+                           "translated_content": body}] if body.strip() else []),
+             "children": [],
+         }
+         # key_map：chunk Header(node_key) → 該 text content node（與 build_chunk_markdown 之 # {node_key} 對應）
+         if title and is_chunk_meaningful(body, doc_type) and body.strip():
+             key_map[node_key] = f"{json_path}/content/0"
+         # 巢狀子節點（resume rag_sections 為扁平、children 多為空；保留遞迴供 academic/book）
+         if sec.get("children"):
+             _walk_tree(sec["children"], doc_type, node_key, node["children"], key_map,
+                        f"{json_path}/children")
+         out_sections.append(node)
```
```diff
  def index(sections, section_summaries, doc_type, vectors_dir,
-           paper_db_id=None, size_cap_tokens=_SIZE_CAP_TOKENS):
+           paper_db_id=None, size_cap_tokens=_SIZE_CAP_TOKENS, rag_tree_path=None,
+           title="", translated_title=""):
      ...
      meta = _write_index_meta(vectors_dir, len(meaningful))
+     # === [RAG-ASYNC-HOTFIX-2] 寫 rag_tree.json（缺路徑則略；不阻斷交付）===
+     if rag_tree_path:
+         try:
+             tree = build_rag_tree(sections, doc_type, title, translated_title)
+             _Path(rag_tree_path).write_text(
+                 json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
+             logger.info("[RAG-ASYNC] rag_tree 已寫入 %s（sections=%d key_map=%d）",
+                         rag_tree_path, len(tree["sections"]), len(tree["key_map"]))
+         except Exception as e:
+             logger.error("[RAG-ASYNC] rag_tree 寫入失敗（不阻斷）: %s", e, exc_info=True)
+     # === [RAG-ASYNC-HOTFIX-2 END] ===
      return RagDbSpec(vectors_path=str(vectors_dir), paper_chunk_count=paper_chunk_count, index_meta=meta)
```

### `pipelines/resume_pipeline.py` — `run_phase4` 傳 rag_tree 路徑 + 標題
```diff
  def run_phase4(self, ctx):
      from processor import rag_indexer
      rag_sections = ctx.rag_sections or []
      section_summaries = (ctx.glossary_ready.section_summaries if ctx.glossary_ready else None) or {}
      vectors_dir = paper_manager.vectors_path(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
+     # === [RAG-ASYNC-HOTFIX-2] rag_tree 寫入路徑（A 軌同位 final_{paper}_rag_tree.json）+ 標題 ===
+     rag_tree_path = paper_manager.rag_tree_path(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
+     _title = ctx.ingestion.title if ctx.ingestion else ctx.paper_id
+     # === [RAG-ASYNC-HOTFIX-2 END] ===
      paper_db_id = paper_manager.get_paper_db_id(ctx.owner_id, ctx.paper_id)
      ...
      spec = rag_indexer.index(
          rag_sections, section_summaries, "resume", vectors_dir,
-         paper_db_id=paper_db_id)
+         paper_db_id=paper_db_id, rag_tree_path=str(rag_tree_path),
+         title=_title, translated_title=_title)
```
> `title`/`translated_title` 暫同取 `ctx.ingestion.title`（履歷以姓名為標題、無雙語標題）；後續若有譯後標題可改傳。

---

## regression 預防與 E2E 驗證（Run 階段執行）

### 1. 受影響模組單元測試（新增）
```bash
$ venv/bin/python -m pytest tests/test_rag_indexer.py tests/test_resume_pipeline.py -q
```
- `test_build_rag_tree_keymap_matches_chunk_header`：對同一 rag_sections，`build_rag_tree` 之 `key_map` key 與 `build_chunk_markdown` 之 `# {chunk_key}` Header **逐一相等**（核心不變式）。
- `test_rag_tree_node_has_translated_content`：每 text content node 帶 `translated_content`、`type=text`、json_path 可由 `/sections/{i}/content/0` 導航取得。
- `test_run_phase4_writes_rag_tree`：mock `rag_indexer.index` 驗 run_phase4 傳入 `rag_tree_path`（= `paper_manager.rag_tree_path`）+ title。

### 2. 接縫整合測試（對接 retriever）
- `test_rag_tree_consumed_by_retriever`：B 軌產之 rag_tree → `RagRetriever.set_rag_tree` → 以一個 chunk Header 走 `key_map → _get_node_from_path → _build_section_title` → **得到「{paper_title} > {section}」非空引用**（證對接成功）。

### 3. 本地 E2E（baron 影子）
```
影子上傳履歷 → output/{owner}/{paper}/final_{paper}_rag_tree.json 存在且 key_map 非空
→ AI 對話檢索 → references 顯示「《姓名》> 章節」（修復前為空）
```

### SOP 核查（Run 時補）
```
database：build_rag_tree / index 寫 rag_tree 無 DB 操作、無裸 commit ✅
logging：rag_tree 寫入失敗 logger.error(exc_info=True) ✅
```

### 不可動遵守
- `rag_processor.py` / `rag_retriever.py`（檢索演算法、key_map 消費）/ `ai_core.py` 載入鏈 — 零改動（B 軌只是補產 retriever 已會讀的檔）。
- `vectors/` FAISS / paper_chunks / index_meta — 不變（rag_tree 為**新增**旁檔、不動既有 ④ 產物）。
- 主 repo 目錄 — 未讀寫。

---

## ⚠️ 依賴與邊界（誠實說明）

1. **依賴 #1（RAG-ASYNC-HOTFIX-1）**：`key_map` key＝chunk Header＝`node_key`；#1 修的是 summary 對位（summary_key），不直接衝突，但**兩者都圍繞 node_key 的一致性**，建議 **#1 先落地或與本 hotfix 合併**，避免 node_key 語意在兩個未落地 hotfix 間漂移。
2. **重複葉標題邊界**：B 軌 `rag_sections` 為扁平、`node_key` 取譯後葉標題；若兩 section 同名（履歷罕見，如多家公司皆有「工作職責」子段）→ `key_map` 後者覆蓋前者 → 該 chunk 引用指向錯 section。**根治需 chunk_key 改用路徑（node_key path）**，屬與 #1 同源的「穩定 key」議題；本 hotfix 先以扁平葉標題交付（履歷實務 section 標題多唯一），並於 §regression 加同名偵測 warning。
3. **公式相鄰（B「完整」之一）**：結構上保留 `content[].type` 與 `_add_adjacent_formulas` 可導航之 json_path，但**履歷無公式 → 此路徑實務 inert**；對 academic/book 將來才實際生效（共用模組一次到位之價值）。
4. **⚠️ 重捕**：本 hotfix 只**新增** rag_tree.json 旁檔、不動 FAISS/chunk 內容 → **不衝擊 golden D2/D3**；但會新增 D 維度外的引用行為，baron E2E 觀察即可、無需重捕向量。

---

## baron 執行命令與 Commit Message 草稿（Run 落地後）

```bash
# 改前 .bak（Run 時備）；入庫：2 業務碼 + 測試 + .bak（baton 下 hotfix.md 收官移 hotfixes/）
git add processor/rag_indexer.py pipelines/resume_pipeline.py tests/test_rag_indexer.py tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_*.bak
git add .claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md
git add .claude-logs/prompts/2026-06-08_RAG-ASYNC-HOTFIX-2_doc_提示詞.md .claude-logs/prompts/INDEX.md .claude-logs/TODO.md
git commit -F /tmp/RAG-ASYNC-HOTFIX-2_msg.txt
```

### Commit message 草稿
```
feat(rag): RAG-ASYNC-HOTFIX-2 — B 軌 rag_indexer 補產完整 rag_tree.json（章節引用對等 A 軌）

#2（選 B 完整版）：RAG-ASYNC C4 B 軌 rag_indexer 只產 FAISS+paper_chunks+index_meta、未產 rag_tree.json，
致 rag_retriever load_rag_tree 回 {} → 章節引用/paper_title/公式相鄰全降級（A 軌有、B 軌無）。
修法：rag_indexer 新增 build_rag_tree，依 P3 ctx.rag_sections 自建完整 rag_tree
（key_map 以 B 軌 chunk Header=node_key 為 key 指向 /sections/{i}/content/0、巢狀節點帶 translated_content、translated_title）；
index() 加 rag_tree_path 參數寫 final_{paper}_rag_tree.json；run_phase4 傳 paper_manager.rag_tree_path + 標題。
零依賴 A 軌、零改 rag_retriever/ai_core（僅補產 retriever 已會讀之檔）。
新增單元 + 對接 retriever 整合測試（key_map↔chunk Header 不變式、_build_section_title 非空引用）。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```
> ⚠️ 本檔 doc-only，msg 寫進文件（Run 落地時才寫 /tmp）。

---

## 回退與備案

```bash
git revert <HOTFIX-2 hash>          # 或還原 .bak；或刪 final_{paper}_rag_tree.json
```
rag_tree.json 為**新增旁檔**、retriever 缺檔自動降級（回原狀）、無資料遷移 → 回退無副作用。

---

## 後續（非本 hotfix）
- 與 **#1** 合併或先後落地（node_key 一致性同源）。
- **chunk_key 改用路徑**（根治重複葉標題 + 統一 #1 summary_key）→ 可併入 #1 或另排「穩定 key 統一」小任務。
- **#4 zh per-section / #5 聯絡資訊** 仍 backlog。
- **治本（流程）**：DOC-Refactor 補 WORKFLOW_SOP「④ 輸出完整性清單（含 rag_tree）+ 收官前整合測試」——本 #2 正是 plan ④ 輸出漏列 rag_tree 所致。
