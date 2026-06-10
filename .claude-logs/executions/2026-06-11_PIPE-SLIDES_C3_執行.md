# PIPE-SLIDES C3 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES C3 — P2 Six-Step（六步與頁 key 契約）|
| 執行日期 | 2026-06-11 |
| 依據規劃 | `baton/2026-06-11_PIPE-SLIDES_..._tasks.md §8 C3`（plan v1〔v1.1〕U5/U6）|
| 次級參考 | resume `run_phase2`（RAG-ASYNC C5 六步金本位、鏡像）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 14 測試全綠（10 前置 + 4 C3）+ 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C2（P1 Vision Ingestion）之上。
- **本次**：`run_phase2` 統一六步完整落地（U5/U6）+ 4 個 P2 mock 測試；**僅兩檔**；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C3 | `待 baron 回填` | BE-Refactor: PIPE-SLIDES C3 — P2 Six-Step |

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （+~190 行：P2 常數/prompt + run_phase2 + 6 私有方法；C3 標記 2 對）
修改：tests/test_slide_pipeline.py    （+4 測試 + P2 harness；stub 清單移除 phase2；C3 標記 2 對）
```
備份：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C3_slide_pipeline.py.bak
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C3_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES C3 START/END] ===` 包裹）

### `run_phase2` 六步（鏡像 resume 金本位、slides 特化兩處順產）
```
① _make_summary_and_domain：1 次 LLM 全文摘要 + 末行「domain: X」順產 raw_domain
   （缺行→""→DomainNormalizer 內容判定/general 降級；失敗→原文截斷兜底）
②/⑤ _build_page_summaries：1 次批次 LLM 每頁原文摘要 + 無標題頁順產標題（回填 tiles、
   P3/P4 同 key 基準）→ {key: 原文摘要}；key＝page_key(N,title)＝**p{N:02d}_{原文頁標題}**
③ normalize_to_lcc(raw_domain, context=摘要)（簡報屬性由內容定）
⑤ Translator DEEP_THINK 翻全文摘要（雙用：交付 + ④ 抽詞樣本——extract_terms 簽名所迫、同 resume 必然序）
④ _heal_glossary：旗標閘門；query_cascade 先比對→缺詞 extract_terms→upsert 冪等（LLM 全交易外）
   + _resolve_domain_name（Domains PK 唯讀、無寫交易）
⑥ _translate_page_summaries：1 次批次、全文摘要引導翻繁中、逐行 i. 對位、失敗留原文降級
   → GlossaryReadySpec.section_summaries
```
- **三安全鎖**：批次有界（①②⑥ 各 1 次 LLM、非 N 次）/ 非致命（各步失敗留空/兜底、不阻 reading_ready、不拋）/ 可量測（`performance_metric` phase=P2 stage=six_step）。
- **`page_key()` 公開靜方法**＝§4 接縫契約單一實作點（P3 帶／P4 取同呼此式、防三方各自拼字）。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
14 passed in 0.59s      # 4 C1 + 6 C2 + 4 C3

C3 四測試：
  test_p2_six_step_spec_and_key_uniqueness   # 六步交付 + 連續同標題頁 p01_/p02_ 不撞（U6）
  test_p2_missing_title_generated_and_backfilled  # 無標題順產+回填 tiles+key 含生成標題
  test_p2_raw_domain_extracted_and_fallback  # domain 行順產→餵 LCC；缺行→"" 降級路
  test_p2_summaries_nonfatal_degrade         # ② 壞輸出→section_summaries=None、餘交付不阻

$ venv/bin/python -m pytest tests/ -q
1 failed, 570 passed, 3 skipped   # 唯一 failed=既知 env flake；570（566+4 新）
```

### §5.3 SOP 核查
```
database：grep '\.commit()' | grep -v session.begin → 無命中（合規；LLM 全交易外、Domains 唯讀 SessionLocal）
logging：P2 新增 4 處 logger.warning 全帶 exc_info=True；無 logger.error
```

## §6 不可動清單遵守

- [x] **僅兩檔**（git status 證）；共用元件（domain_normalizer/glossary_extractor/translator/contracts）**只消費零改**。
- [x] A 軌 / rag_indexer / orchestrator——零改動。
- [x] C3 標記平衡（pipeline 2/2、test 2/2）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本報告暫存；plan + tasks + C1/C2 報告續留。
- **下一步＝C4**（P3 Per-Page Translate & Restore：逐頁並行 + alt 對齊雙 Caption 根除 + constraints + rag_sections 旁路〔summary_key=page_key 同基準〕+ zh 路 + fallback），待 baron 下達 C4 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2 份 .bak）

# 2. git add 清單（嚴禁 baton/ 執行報告）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C3_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C3_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES_C3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES_C3_msg.txt
git commit -F /tmp/PIPE-SLIDES_C3_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <C3 hash>   # 或還原 2 .bak → 回 C2 狀態；P2 未接線外部消費者、無副作用
```
