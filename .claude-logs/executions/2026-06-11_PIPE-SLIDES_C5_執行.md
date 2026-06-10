# PIPE-SLIDES C5 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES C5 — P4 Wire（RAG 接線）|
| 執行日期 | 2026-06-11 |
| 依據規劃 | `baton/2026-06-11_PIPE-SLIDES_..._tasks.md §8 C5`（plan v1〔v1.1〕U11）|
| 次級參考 | resume `run_phase4`（RAG-ASYNC C6 + HOTFIX-2 範式、鏡像）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 21 測試全綠（19 前置 + 2 C5）+ 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C4（P3）之上。
- **本次**：`run_phase4` 接線 `rag_indexer` 共用真理源（U11）+ 2 mock 測試；**四 Phase stub 全清、SlidePipeline 全功能落地**；僅兩檔；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C5 | `待 baron 回填` | BE-Refactor: PIPE-SLIDES C5 — P4 Wire |

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （+~50 行 run_phase4；C5 標記 1 對）
修改：tests/test_slide_pipeline.py    （+2 測試 + stub 測試改「四 Phase 皆已覆寫」；C5 標記 2 對）
```
備份：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C5_slide_pipeline.py.bak
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C5_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES C5 START/END] ===` 包裹）

### `run_phase4`（鏡像 resume RAG-ASYNC C6 + HOTFIX-2 範式）
```python
spec = rag_indexer.index(
    rag_sections, section_summaries, "slides", vectors_dir,
    paper_db_id=paper_db_id,
    rag_tree_path=str(rag_tree_path),       # HOTFIX-2 四產物：rag_tree.json
    title=_title, translated_title=_title,  # 暫同取（同 resume 先例、註記）
)
```
- 輸入＝**P3 旁路 `ctx.rag_sections` + P2 `section_summaries`**（summary_key=page_key 三方同基準閉環、不餵 reading-view md）。
- `doc_type='slides'` → rag_indexer 內 `is_chunk_meaningful` ≥3 門檻生效（`rag_char_threshold=3`、C1 已設）。
- **四產物**：FAISS + paper_chunks + index_meta + `final_{paper}_rag_tree.json`。
- 錯誤隔離：異常 `warning(exc_info=True)` 後**拋出**、Orchestrator 標 `rag_status='failed'`、不阻 reading_ready；`paper_db_id=None` → rag_indexer 內部優雅降級。
- **零 A 軌**：grep `rag_processor` 僅 2 處註解宣告、import 0。
- stub 測試改驗「四 Phase 皆已覆寫」（NotImplementedError 全清、stub 時代收官）。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
21 passed in 0.56s     # 4 C1 + 6 C2 + 4 C3 + 5 C4 + 2 C5

C5 二測試：
  test_p4_wires_rag_indexer_with_contract_args  # sections/summaries 同 key 直餵、doc_type='slides'、
                                                 # rag_tree_path 含 rag_tree.json、title=封面題
  test_p4_failure_raises_not_swallowed          # rag_indexer 失敗 → 拋出不吞

$ §6.5：grep 'rag_processor' → import 0（2 命中皆註解宣告）✅；rag_indexer.index 接線 L697 ✅

$ venv/bin/python -m pytest tests/ -q
1 failed, 577 passed, 3 skipped   # 唯一 failed=既知 env flake；577（575+2 新）
```

### §5.3 SOP 核查
```
database：無裸 commit（paper_chunks 寫庫委由 rag_indexer→paper_manager 既有極短交易）
logging：失敗路 logger.warning(exc_info=True) 合規
```

## §6 不可動清單遵守

- [x] **僅兩檔**；A 軌 `rag_processor` 零 import；`rag_indexer` 本體零改（純消費）。
- [x] C5 標記平衡（pipeline 1/1、test 2/2）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本報告暫存；plan + tasks + C1-C4 報告續留。
- **SlidePipeline 四 Phase 全落地**（P1 存圖轉錄 → P2 六步 → P3 逐頁譯+還原 → P4 RAG）。
- **下一步＝C6**（Unit & Integration Tests：補全 plan §8.1 缺口 + **§7.2 key-changing 整合測試**〔P2→P3→P4 串接、FakeTranslator 真改寫頁標題〕），待 baron 下達 C6 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2 份 .bak）

# 2. git add 清單（嚴禁 baton/ 執行報告）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C5_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C5_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES_C5_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES_C5_msg.txt
git commit -F /tmp/PIPE-SLIDES_C5_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <C5 hash>   # 或還原 2 .bak → 回 C4；P4 僅影子 B 軌觸發、無副作用
```
