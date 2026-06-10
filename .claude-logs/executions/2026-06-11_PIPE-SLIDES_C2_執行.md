# PIPE-SLIDES C2 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES C2 — P1 Vision Ingestion（每頁存圖與視覺解析）|
| 執行日期 | 2026-06-11 |
| 依據規劃 | `baton/2026-06-11_PIPE-SLIDES_..._tasks.md §8 C2`（plan v1〔v1.1〕U1-U4、Q1/Q2 定案）|
| 次級參考 | SPEC §1.3.1 Vision 共用規格；A 軌 `slides_processor.py` 渲染演算法（參照自建、零 import）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 10 測試全綠（4 C1 + 6 C2）+ 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C1（Skeleton & Register）之上。
- **本次**：`run_phase1` 完整落地（U1-U4）+ 6 個 P1 mock 測試；**僅兩檔**；零 A 軌 import；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C2 | `待 baron 回填` | BE-Refactor: PIPE-SLIDES C2 — P1 Vision Ingestion |

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （+~200 行：常數/prompt + run_phase1 + 6 私有方法；C2 標記 2 對）
修改：tests/test_slide_pipeline.py    （+6 測試 + harness；stub 測試清單移除 phase1；C2 標記 2 對）
```
備份：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C2_slide_pipeline.py.bak
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C2_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES C2 START/END] ===` 包裹）

### `run_phase1` 七步流
```
① _render_pages：fitz Matrix(2,2) 逐頁 get_pixmap → jpeg（直向 A4 上下裁半／橫向整頁——參照 A 軌 L94-117 自建）
② ThreadPool(LLM_MAX_CONCURRENT) 並行 _transcribe_page（首單位帶 _COVER_PROMPT 封面判定）
③ Q1 滾動補救：_needs_rolling（標題含 (續)/cont'd 或 前頁尾+當頁首皆表格列）→ 該頁注入前頁重轉錄（序列、少量）
④ 空白單位跳過（三欄皆空、A 軌同款）+ 存圖 images/page-{N:02d}.jpg（頁序連續重編）
⑤ U2 封面：cover.title→spec.title／authors；company/date → ctx.raw_metadata 旁路；非封面 → title=檔名 stem fallback
⑥ U3/Q2 _dedupe_headers：短行（≤20 字）≥60% 非封面頁 → 全剔（封面排除統計與剔除、清單入 logger.info）
⑦ source_lang CJK 啟發式（鏡像 resume 常數）+ 影子 (測試) 後綴 → IngestionMetadataSpec(title/authors/source_lang/tiles)
```
### 關鍵合規點
- **§1.3.1**：每次 Vision 呼叫 `temperature=settings.LLM_VISION_TEMPERATURE`（預設 0）；prompt 忠實轉錄鐵律 + **U9 cell 禁 `###`**（提前於 P1 prompt 層生效）。
- **tiles 內部形狀**（P2/P3 自家消費、文檔化）：`{page, title, content, figure_description, image_file, is_cover}`——`image_file=images/page-{N}.jpg` 與頁序同基準（§4 接縫契約④）。
- Vision 失敗非致命（壞頁 `logger.warning` 跳過、不阻整份）；P1 零衍生語境、零 Embedding。

### 測試（6 個、mock `_render_pages` + `LLMClient.get_instance`、零真 API）
封面 metadata+存圖／無封面 fallback 檔名／去重排除封面／空白跳過+頁序重編／**滾動預設關+觸發雙場景**（呼叫數 2 vs 3、prompt 注入斷言）／temperature 接線。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
10 passed in 0.55s        # 4 C1 + 6 C2

$ grep §6.2：
  LLM_VISION_TEMPERATURE → _transcribe_page 呼叫處命中 ✅
  get_pixmap → L185 命中（自建）✅
  slides_processor import → 0（零 A 軌耦合）✅

$ venv/bin/python -m pytest tests/ -q
1 failed, 566 passed, 3 skipped
  唯一 failed = 既知 env flake test_settings_log_format_default_auto；566 passed（560+6 新）
```
> ⚠️ 過程修正：測試 harness 初版漏 `PipelineContext.doc_type` 必填欄 → 6 測試 ValidationError；補 `doc_type='slides'` 後全綠（純測試 fixture 修正、非業務碼）。

### §5.3 SOP 核查
```
logging：無 logger.error（僅 warning〔Vision 壞頁跳過〕/info、合規）
database：無 .commit()（P1 純檔案/記憶體、合規）
```

## §6 不可動清單遵守

- [x] **僅兩檔**（git status 證）；A 軌 slides_processor **零 import**（grep 0）。
- [x] rag_indexer / contracts / orchestrator / factory / web_server / resume_pipeline——零改動。
- [x] C2 標記平衡（pipeline 2/2、test 2/2）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本報告暫存；plan + tasks + C1 報告續留。
- **下一步＝C3**（P2 Six-Step：統一六步、① 順產 raw_domain、② 順產缺失頁標題、key=`p{N}_{原文頁標題}`），待 baron 下達 C3 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2 份 .bak）

# 2. git add 清單（嚴禁 baton/ 執行報告）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C2_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C2_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES_C2_msg.txt
git commit -F /tmp/PIPE-SLIDES_C2_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <C2 hash>   # 或還原 2 .bak → 回 C1 stub；P1 未接線任何外部消費者、無副作用
```
