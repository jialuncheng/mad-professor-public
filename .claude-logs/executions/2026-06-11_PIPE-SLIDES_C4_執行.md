# PIPE-SLIDES C4 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES C4 — P3 Per-Page Translate & Restore（逐頁翻譯與排版還原）|
| 執行日期 | 2026-06-11 |
| 依據規劃 | `baton/2026-06-11_PIPE-SLIDES_..._tasks.md §8 C4`（plan v1〔v1.1〕U7-U10、Q3/Q4/Q5 定案）|
| 次級參考 | RESUME-PERF-1（並行範式）/ SPEC U4（zh 路）/ §4 key 契約 |
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 19 測試全綠（14 前置 + 5 C4）+ 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C3（P2 Six-Step）之上。
- **本次**：`run_phase3` 完整落地（U7-U10、本任務最大 commit）+ 5 個 P3 mock 測試；**僅兩檔**；rag_indexer 零污染；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C4 | `待 baron 回填` | BE-Refactor: PIPE-SLIDES C4 — P3 Per-Page Translate & Restore |

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （+~210 行：P3 常數 + run_phase3 + 4 私有方法；C4 標記 2 對）
修改：tests/test_slide_pipeline.py    （+5 測試 + P3 harness；stub 清單移除 phase3；C4 標記 2 對）
```
備份：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C4_slide_pipeline.py.bak
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C4_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES C4 START/END] ===` 包裹）

### `run_phase3` 主流
```
InjectionContext(lcc/glossary/zh_summary=P2 譯摘要/domain_name/doc_type='slides'/
                 constraints=_SLIDE_CONSTRAINTS〔Q4 四條：品牌原文/中英並列/cell 禁 ###/數字原樣〕)
分流：zh 來源（SPEC U4）→ 跳譯（原文≡譯文）仍建 per-section
　　　退化（Q5：頁≤1 或空頁>50%）→ _translate_whole 整檔單發 + 單一容器 section
　　　正常 → _translate_pages_parallel 逐頁三欄並行
→ _deliver 共用出口：還原雙語 final + ctx.rag_sections 旁路 + 寫檔
```
### 關鍵合規點
- **並行（RESUME-PERF-1 範式）**：ThreadPool(`LLM_MAX_CONCURRENT`)、(page,field) 鍵保序回填、限流靠既有 `_api_semaphore` 不新增鎖、**單欄失敗退原文** + `slide_translate_unit_fallback` warning。
- **U8 alt 對齊（雙 Caption 物理根除）**：`![{alt=description 譯文}](images/page-N.jpg)`——描述**單點呈現**、渲染路徑零 `*圖表：*` 段（grep 證 3 命中全為 prompt/註解）；en 版 alt=原文。
- **U10**：**不渲染 meta header**（final 首節即 `##`、封面頁內容天然呈現）。
- **§4 key 契約**：`summary_key = page_key(page, 原文標題)`（與 P2 同一實作點）；譯後 title 僅存 `title` 欄供顯示——**key-changing 不變式落地**。
- **Q3 同頁合併**：content+figure_description 併單一 text chunk（策略側、`rag_indexer` 零改、import 0）。
- section 元素形狀對齊 resume（`{title, level, summary_key, content:[{type,content}], children}`）→ C5 rag_indexer 直接可餵。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
19 passed in 0.54s     # 4 C1 + 6 C2 + 4 C3 + 5 C4

C4 五測試：
  test_p3_alt_aligned_no_caption_segment_no_header  # alt=譯 desc、零「圖表：」、無 header
  test_p3_rag_sections_key_from_source_title        # key=原文 p01_/p02_ 不撞、譯 title 僅顯示
  test_p3_unit_failure_falls_back_to_source         # 單欄退原文、他頁不污染
  test_p3_zh_source_skips_translate                 # zh 路零翻譯呼叫、仍建 per-section
  test_p3_degraded_single_page_whole_translate      # Q5 整檔 1 次 + 單一容器

$ §6.4 grep：_SLIDE_CONSTRAINTS 命中 ✅；渲染路徑「圖表：」=0（3 命中皆 prompt/註解）✅；rag_processor=0 ✅

$ venv/bin/python -m pytest tests/ -q
1 failed, 575 passed, 3 skipped   # 唯一 failed=既知 env flake；575（570+5 新）
```
> ⚠️ 過程修正：單欄失敗測試初版用 1 頁 → 誤入 Q5 退化路；改 2 頁走正常路（純測試 fixture、非業務碼）。

### §5.3 SOP 核查
```
database：無裸 commit（P3 純檔案/LLM、合規）
logging：無 logger.error；warning 含結構化 extra_fields（slide_translate_unit_fallback）
```

## §6 不可動清單遵守

- [x] **僅兩檔**；`rag_indexer` 零污染（import 0、Q3 合併在策略側）。
- [x] 共用元件（translator/contracts）只消費零改；A 軌零改。
- [x] C4 標記平衡（pipeline 2/2、test 2/2）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本報告暫存；plan + tasks + C1-C3 報告續留。
- **下一步＝C5**（P4 Wire：`run_phase4` 呼 `rag_indexer.index`、四產物、≥3 門檻），待 baron 下達 C5 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2 份 .bak）

# 2. git add 清單（嚴禁 baton/ 執行報告）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C4_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C4_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES_C4_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES_C4_msg.txt
git commit -F /tmp/PIPE-SLIDES_C4_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <C4 hash>   # 或還原 2 .bak → 回 C3 狀態；P3 輸出未被消費（C5 才接 P4）、無副作用
```
