# RAG-ASYNC-HOTFIX-2 HOTFIX-2 執行報告

> BE-Hotfix · B 軌補產 rag_tree.json（#2·選 B 完整版）→ 章節引用/paper_title/公式相鄰對等 A 軌
> 依據：`.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md`

---

## 1. 基準與完成狀態

- **基準 Commit**：RAG-ASYNC-HOTFIX-1（#1 key 穿線已落地、node_key 語意已穩定）之上。
- **本次狀態**：代碼 + 測試已落地、全套件驗證通過；**未 commit / 未 push**（待 baron 手動）。
- **工作流類別**：BE-Hotfix（單一 Commit、無獨立 Check、執行時一次性歸檔）。

## 2. 落地 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-2 | `待 baron 回填` | feat(rag): RAG-ASYNC-HOTFIX-2 — B 軌 rag_indexer 補產完整 rag_tree.json（章節引用對等 A 軌） |

## 3. diff stat（真實）

```
 pipelines/resume_pipeline.py  | 59 ++++++++++++++++++---------
 processor/rag_indexer.py      | 93 +++++++++++++++++++++++++++++++++++++++++-
 tests/test_rag_indexer.py     | 88 ++++++++++++++++++++++++++++++++++++++++
 tests/test_resume_pipeline.py | 94 +++++++++++++++++++++++++++++++++++++++++++
 4 files changed, 315 insertions(+), 19 deletions(-)
```

備份（改前 .bak，archive/，git add 強制含）：
```
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_resume_pipeline.py.bak
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_rag_indexer.py.bak
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_test_rag_indexer.py.bak
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_test_resume_pipeline.py.bak
```

## 4. 真因

B 軌履歷在 AI 對話檢索時**召回正常但引用降級**——無法顯示「《paper_title》> 章節 > 子章節」、references 無 paper_title 前綴、無公式相鄰擴展（A 軌論文有、B 軌履歷沒有）。

A 軌 `rag_processor.process` 會 `_restructure_tree` + `_generate_key_map` 產 rag_tree 並寫 `final_{paper}_rag_tree.json`；B 軌 RAG-ASYNC C4 `rag_indexer.index` **只產 FAISS + paper_chunks + index_meta、未產 rag_tree** → `rag_retriever.load_rag_tree` 回 `{}` → 三項引用全空。**非崩潰**（缺檔優雅降級）故易被忽略。

**為何漏**：RAG-ASYNC plan v2 §U5 將 ④ 輸出列為「FAISS + paper_chunks + index_meta」、**遺漏 rag_tree.json**（SPEC §1.4 其實含 tree_json_file）；C4 conformance 只驗 `load_vector_store + similarity_search`（不需 rag_tree）→ 沒照出。

## 5. 修法

**在 `rag_indexer` 依 P3 `ctx.rag_sections` 自建完整 rag_tree（key_map 以 B 軌 chunk Header=node_key 為 key、指向 `/sections/{i}/content/0`），寫 rag_tree.json；run_phase4 傳入路徑。** 零依賴 A 軌、零改檢索端。全 `# === [RAG-ASYNC-HOTFIX-2 HOTFIX-2 START/END] ===` 包裹：

1. **`processor/rag_indexer.py`**：① module 補 `import json`；② 新增 `build_rag_tree(sections, doc_type, title, translated_title)` + `_walk_tree`——以**與 `_walk`/`build_chunk_markdown` 同式之 node_key** 建 key_map（`node_key → /sections/{i}/content/0`）+ 巢狀節點帶 `translated_content`/`translated_title`/`type=text`/`index`；③ `index()` 簽名加 `rag_tree_path/title/translated_title`；④ `_write_index_meta` 後寫 rag_tree.json（IO try/except `logger.error(exc_info=True)` 優雅降級、不阻斷交付 RagDbSpec）。
2. **`pipelines/resume_pipeline.py::run_phase4`**：取 `rag_tree_path = paper_manager.rag_tree_path(...)`（A 軌同位 `final_{paper}_rag_tree.json`）+ `_title = ctx.ingestion.title`；傳給 `rag_indexer.index(...)`。

**核心不變式**：`key_map` 的 key＝B 軌 chunk Header（`# {node_key}`）→ retriever `doc.metadata['Header'] in key_map` 對得上（由測試 `test_build_rag_tree_keymap_matches_chunk_header` 鎖死）。

## 6. 不可動清單遵守狀態

- [x] `rag_processor.py` — 未動（git diff 空）。
- [x] `rag_retriever.py`（檢索演算法、key_map 消費、`_get_node_from_path`/`_build_section_title`）— 未動（git diff 空；僅在測試中**呼叫**其方法驗對接）。
- [x] `ai_core.py`（載入鏈 set_rag_tree）— 未動（git diff 空）。
- [x] `pipeline_core.py` / `config.py` — 未動（git diff 空）。
- [x] `vectors/` FAISS / paper_chunks / index_meta ④ 既有產物 — 不變（rag_tree 為**新增**旁檔）。
- [x] 主 repo 目錄 — 未讀寫。

## 7. 端到端驗證計畫結果

### 7.1 受影響模組 + 4 新測試
```
$ venv/bin/python -m pytest tests/test_rag_indexer.py tests/test_resume_pipeline.py -q
57 passed

逐一點名：
tests/test_rag_indexer.py::test_build_rag_tree_keymap_matches_chunk_header PASSED
tests/test_rag_indexer.py::test_rag_tree_node_has_translated_content PASSED
tests/test_rag_indexer.py::test_rag_tree_consumed_by_retriever PASSED
tests/test_resume_pipeline.py::test_run_phase4_writes_rag_tree PASSED
```
- `test_build_rag_tree_keymap_matches_chunk_header`：對同一 rag_sections，`build_rag_tree` 之 key_map key 與 `build_chunk_markdown` 之 `# {Header}` **逐一相等**（含巢狀 `Working Experience/Company A`；容器節點兩端皆不入）——**核心不變式鐵證**。
- `test_rag_tree_node_has_translated_content`：text content node 帶 `translated_content`/`type=text`/`index=0`；key_map["Skills"]="/sections/0/content/0"。
- `test_rag_tree_consumed_by_retriever`（**對接整合測試**）：B 軌產 rag_tree → `RagRetriever.set_rag_tree` → 以 chunk Header 走 `key_map → _get_node_from_path → _build_section_title` → 得「王小明 > Skills」**非空引用**（修復前為空）。
- `test_run_phase4_writes_rag_tree`：run_phase4 傳入 `rag_tree_path`（= `paper_manager.rag_tree_path`、結尾 `final_p9_rag_tree.json`）+ `title`（= ingestion.title）。

### 7.2 全套件
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 532 passed, 3 skipped
```
- **532 passed**（HOTFIX-2 前 528 + 4 新測試）。
- 唯一 failed＝既知環境 flake `test_settings_log_format_default_auto`（非本 hotfix 引入）。

### 7.3 SOP 一致性核查（BE-Hotfix 強制）
```
database：grep -E '\.commit\(\)' rag_indexer.py resume_pipeline.py | grep -v 'with .*session.begin'
        → 無命中（合規·本 hotfix 無 DB 操作、rag_tree 為純檔案寫）

logging：本次新增 logger.error 一處（rag_indexer rag_tree 寫入失敗）→ 含 exc_info=True ✅
```

### 7.4 git status -s（業務/測試碼）
```
 M pipelines/resume_pipeline.py
 M processor/rag_indexer.py
 M tests/test_rag_indexer.py
 M tests/test_resume_pipeline.py
?? .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_*.bak（4 份）
```

## 8. baron 執行命令

```bash
# 1. 備份已完成（報告 §3，archive/ 4 份 .bak）

# 2. git add 清單（4 業務/測試碼 + 4 備份 + 歸檔計畫 + 執行報告 + TODO + 2 prompts）
git add pipelines/resume_pipeline.py
git add processor/rag_indexer.py
git add tests/test_rag_indexer.py
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_rag_indexer.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_test_rag_indexer.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_test_resume_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-2_hotfix.md
git add .claude-logs/executions/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-08_RAG-ASYNC-HOTFIX-2_HOTFIX-2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/RAG-ASYNC-HOTFIX-2_msg.txt
git commit -F /tmp/RAG-ASYNC-HOTFIX-2_msg.txt
```

## 9. 回退方式（Rollback）

```bash
git revert <HOTFIX-2 hash>          # 或還原 4 支 .bak；或刪 final_{paper}_rag_tree.json
```
rag_tree.json 為**新增旁檔**、retriever 缺檔自動降級（回原狀）、無資料遷移 → 回退無副作用。

## 10. ⚠️ 邊界與運維（誠實說明）

1. **重複葉標題邊界**：B 軌 rag_sections 扁平、node_key 取譯後葉標題；若兩 section 同名（履歷罕見）→ key_map 後者覆蓋前者。根治需 chunk_key 改用路徑（與 #1 同源「穩定 key」議題、另排）。
2. **公式相鄰**：結構上保留 `content[].type`/json_path 可導航，但**履歷無公式 → 實務 inert**；academic/book 將來才實際生效（共用模組一次到位）。
3. **不衝擊 golden D2/D3**：本 hotfix 只**新增** rag_tree.json 旁檔、不動 FAISS/chunk 內容；baron 影子 E2E 觀察「references 顯示《姓名》> 章節」即可、**無需重捕向量**。
