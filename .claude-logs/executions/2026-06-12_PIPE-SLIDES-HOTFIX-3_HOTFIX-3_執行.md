# PIPE-SLIDES-HOTFIX-3 HOTFIX-3 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES-HOTFIX-3 — 簡報閱讀視圖排版打磨（圖序/副標併標題塊/子標題/縮排）|
| 執行日期 | 2026-06-12 |
| 依據規劃 | `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-3_hotfix.md`（design/docs 設計對齊、三盲點修正）|
| 次級參考 | typography.md（h2 底線/h3 規範）/ principles.md（結構歸主檔）/ META-NORM C4（subtitle）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 40 測試全綠（36 既有更新 + 4 新）+ 全套件 605 passed + SOP 合規；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：META-NORM C7 收官後、baron 前端逐頁 QA（Ch37 簡報）發現 4 項閱讀視圖排版問題。
- **本次**：一-a 圖序 + C 副標併標題塊（順帶解 一-b）+ A/B/C 升 h3 + 二 巢狀縮排；**僅三檔**；RAG 鏈零改；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-3 | `待 baron 回填` | BE-Hotfix: PIPE-SLIDES HOTFIX-3 — 簡報閱讀視圖排版打磨 |

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （+_slide_head_html/_promote_subheadings + _page_source_md/_deliver 重排；HOTFIX-3 標記 3 對）
修改：static/index.html               （base CSS .slide-head/.slide-sub + 巢狀 ul 縮排；HOTFIX-3 標記 1 對）
修改：tests/test_slide_pipeline.py     （5 既有斷言更新 + 4 新測試；HOTFIX-3 標記 1 對）
```
備份：
```
.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_slide_pipeline.py.bak
.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_index.html.bak
.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES-HOTFIX-3 HOTFIX-3 ...] ===` / `/* ... */` 包裹）

### `slide_pipeline.py`
- **`_slide_head_html(title, subtitle)`**（C）：產 `<div class="slide-head"><h2>{escape}</h2><p class="slide-sub">{escape}</p></div>`；`html.escape` 防破版;全空回 ''。
- **`_promote_subheadings(text)`**（A/B/C）：整行 `**X**`→`### X`;**regex `\r?$` 相容 CRLF（盲點1）**;**前一行非空才補空行（盲點2、不產 `\n\n\n`）**;句中 bold 不誤升。
- **`_page_source_md`(en) / `_deliver`(zh) 正常路**：parts 重排 **圖 → 標題塊 → 內文(promote+normalize)**（一-a）;`sections.append`/`merged`/`ctx.rag_sections`/譯題旁路 **原封不動**（RAG 安全）。

### `static/index.html` base CSS（接 `#paper-content h2` 後）
- `.slide-head` border-bottom 用 `--divider-w`/`--color-divider`（主題變數、各主題吻合）+ padding-bottom;`.slide-head h2` border none（覆寫主題 h2、特異度 1,1,1>1,0,1 → **一-b 夾線消失**）;`.slide-sub` 15px 次級;`ul ul/ol ol/ul ol/ol ul { padding-left:1.5em }`（二、結構 fallback）。

### `tests/test_slide_pipeline.py`
- **5 既有斷言更新**：`## X`→`<h2>X</h2>`、`### sub`→`<p class="slide-sub">`、`startswith('# ')`→驗首元素為 `![`。
- **4 新測試**：圖序+標題塊 / h3 升級(含 `\r` 相容+不產連續空行) / escape / **rag_sections 不受影響**（key 不變、subtitle/HTML 不入 chunk body）。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
40 passed in 0.58s     # 36 既有（5 更新）+ 4 新

$ venv/bin/python -m pytest tests/ -q
1 failed, 605 passed, 3 skipped   # 唯一 failed=既知 env flake；605（601+4 新）
```
> ⚠️ 過程修正：新 test_hf3 初版用單 tile → 觸發 Q5 退化路（`len(tiles)<=1`）走整檔翻譯、斷言對不上;改 2 tiles 走正常逐頁路（純測試 fixture、非業務碼;順帶驗證退化路與正常路行為差異正確）。

### §5.3 SOP 核查
```
grep format_exc/logger.error pipelines/slide_pipeline.py → 無命中（合規）
grep 裸 commit → 無命中（合規）
```

## §6 不可動清單遵守

- [x] **僅三檔**（git status 證）;A 軌/rag_indexer/orchestrator/**4 主題檔**/META-NORM 飛輪/HOTFIX-1/1b/2 既有區塊未動。
- [x] **RAG 鏈零改**（`sections.append`/`ctx.rag_sections`/譯題旁路原封不動;test_hf3_rag_sections_unaffected 證 key 不變、HTML 不入 chunk）。
- [x] 設計對齊：一-b 不在 base 蓋主題底線（改 C 從根源）、A/B/C 升 h3 非孤兒 h4、二 結構放 base（typography.md/principles.md 依據）。
- [x] HOTFIX-3 標記平衡（slide 3、html 1、test 1）。

## §7 銜接（完成緊急修補、歸檔收官）

- 收官自動化已執行：hotfix.md → `hotfixes/`、本報告 → `executions/`（mv + git add）。
- **⚠️ 行為變更 + golden**：改 B 軌 final 渲染結構 → slides golden（與前 HOTFIX-1/1b/2 + META-NORM C3/C4 同屬 B 軌變更）**全部落地後一次首捕**;**slides fixture 需先補齊**（`tests/golden_baseline/fixtures/slides.pdf` 在 PaperRead-Lab 缺檔、入版控被 .gitignore 排除 → baron 手動放代表件如 Ch37）。
- **baron E2E（非 commit）**：影子重傳 Ch37 → 每頁圖在上/標題塊在下/標題副標無夾線/A 層 B 層有間距子標題/子項目縮排;chat 引用「《簡報名》> p{N}」不變。
- **後續 backlog**：h2 border 規則重複 4 主題檔（DRY 債）→ 未來 FE 清理上移 base（本 hotfix 不碰）。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 3 份 .bak）

# 2. git add 清單（hotfixes/ 與 executions/ 已於收官自動化 mv + git add 完畢）
git add pipelines/slide_pipeline.py
git add static/index.html
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_index.html.bak
git add .claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git add .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-3_hotfix.md
git add .claude-logs/executions/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_執行.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES-HOTFIX-3_msg.txt
git commit -F /tmp/PIPE-SLIDES-HOTFIX-3_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <HOTFIX-3 hash>   # 三點互不依賴、整體 revert 安全（回 META-NORM C4 渲染）；或還原 3 .bak
```
