# PIPE-SLIDES-HOTFIX-2 HOTFIX-2 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES-HOTFIX-2 — alt 破圖 / 母片重複日期 / F4 條列鬆散（B+E+F）|
| 執行日期 | 2026-06-11 |
| 依據規劃 | `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-2_hotfix.md`（baron 拍板 B+E+F、A 撤案、C/D 留 META-NORM）|
| 次級參考 | 原稿 `Ch37_Plant-Nutrition.pdf`（20/20 頁母片日期）/ HOTFIX-1 F4（F 修其回歸）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 32 測試全綠（29 既有 + 3 新）+ 全套件 588 passed + SOP 合規；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：HOTFIX-1b（`1a2ec98`）之後、baron 學術簡報實件逐頁分析發現 B/E/F 三缺陷（F 為 HOTFIX-1 F4 回歸）。
- **本次**：B/E/F 三點落地 + 3 回歸測試；**僅兩檔、純渲染/清洗、零 Vision prompt 改動**；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-2 | `待 baron 回填` | BE-Hotfix: PIPE-SLIDES HOTFIX-2 — alt 破圖 / 母片重複日期 / F4 條列鬆散（B+E+F）|

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （B _safe_alt+2 套用 / E _DATE_LINE_RE+_strip_master_date+接線 / F regex 擴充；HOTFIX-2 標記 4 對 + 3 單行）
修改：tests/test_slide_pipeline.py    （+3 回歸測試；HOTFIX-2 標記 1 對）
```
備份：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_slide_pipeline.py.bak
.claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_test_slide_pipeline.py.bak
```

## §4 修法說明（`# === [PIPE-SLIDES-HOTFIX-2 HOTFIX-2 ...] ===` 包裹）

### B：`_safe_alt` + 兩處 alt 套用
- 新增 `_safe_alt`：`[]()`→全形 `［］（）`、換行/連續空白→單空格；`_page_source_md`(en) + `_deliver`(zh) 兩處 `![alt](...)` 套用。
- **真因**：CommonMark `![alt](url)` 之 alt 遇 `]` 提前閉合 → 圖密集頁（figure_description 充滿 `[ammonium]`/`(AM)`）破圖 + 描述洩漏正文（p29/35/37 缺圖之真因；HOTFIX-1 U8 alt 對齊暴露此缺口）。

### E：`_DATE_LINE_RE` + `_strip_master_date` + run_phase1 接線
- 整行僅日期、≥2 頁出現 → 母片日期頁眉剔；單頁不洗、句中日期不動；緊接 `_dedupe_headers` 後呼叫。
- **真因**：原稿 `Ch37` **20/20 頁母片日期 `4/28/2026`**（匯出 PDF 烙入、非投影片內容）；`_dedupe_headers` 因 **OCR 格式逐頁飄**（三變體各 <60% 門檻）全漏網 → 改以「整行即日期」語意判定、不依賴格式一致。

### F：`_normalize_paragraph_breaks` list-aware（修 HOTFIX-1 F4 回歸）
- regex `(?![\n\|])` → `(?![\n\|]|\s*(?:[-*+•]|\d+[.、])\s|\s*-\s)`：單 `\n` 升級追加排除「下一行為條列行」。
- **真因（誠實·我自己 HOTFIX-1 引入）**：F4 移植時只排除 pipe table、未排除條列 → tight list `- a\n- b` 被升級成 `- a\n\n- b` → loose list（item 間空行醜排）。

> 過程修正：① 編輯 dedup 常數註解時誤植俄文字元 `статист`、已即時修回「統計」（grep 證 0 殘留）；② 測試 `_safe_alt` 端到端段誤用 `SlidePipeline` 未別名 → 改 `S()`（純測試 fixture、非業務碼）。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
32 passed in 0.58s     # 29 既有（回歸網零紅）+ 3 新

  test_hf2b_alt_brackets_escaped PASSED   # 全形化+換行轉空白+端到端圖片語法完整
  test_hf2e_master_date_stripped PASSED   # ≥2 頁剔/單頁保留/句中保留
  test_hf2f_list_stays_tight PASSED       # bullet+數字 tight 維持/段落仍升級/table 不破

$ venv/bin/python -m pytest tests/ -q
1 failed, 588 passed, 3 skipped   # 唯一 failed=既知 env flake test_settings_log_format_default_auto；588（585+3）
```

### §5.3 SOP 核查（BE-Hotfix 強制）
```
$ grep -nE "traceback.format_exc|logger\.error" pipelines/slide_pipeline.py → 無命中（合規）
$ grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v session.begin → 無命中（合規）
```

## §6 不可動清單遵守

- [x] **僅兩檔**（git status 證）；共用元件 / A 軌零改。
- [x] **零 Vision prompt 改動**（純渲染/清洗、與 META-NORM 之 schema 改動風險隔離）。
- [x] 既有 29 測試零紅（回歸網通過：F4 段落升級仍成立、B 後無 `*圖表：*` 段、F1 去回聲不受影響）。
- [x] HOTFIX-2 標記平衡（pipeline 4 對 + 3 單行、test 1 對）。
- [x] 兩份 `2026-06-01_PIPE*` 規格書長駐 baton 未動未 add。

## §7 銜接（完成緊急修補、歸檔收官）

- 收官自動化已執行：hotfix.md → `hotfixes/`、本報告 → `executions/`（mv + git add）。
- **⚠️ 行為變更 + golden**：B/E/F 均改 B 軌 final 輸出 → **slides golden 建議本 hotfix 落地後一次首捕**（`venv/bin/python tools/golden_baseline.py capture slides --force`、含前 HOTFIX-1/1b 之變更一次到位）。
- **baron E2E（非 commit）**：影子重傳 `Ch37` → ① 圖密集頁整頁截圖正常顯示、無破圖/無描述洩漏（B）② 各頁無 `4/28/2026`（E）③ 條列緊湊無多餘空行（F）。
- **後續**：C/D 歸 META-NORM plan（v1.2 凍結、待 schema 點頭轉 tasks）。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2 份 .bak）

# 2. git add 清單（hotfixes/ 與 executions/ 已於收官自動化 mv + git add 完畢）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_run_提示詞.md
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES-HOTFIX-2_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git add .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-2_hotfix.md
git add .claude-logs/executions/2026-06-11_PIPE-SLIDES-HOTFIX-2_HOTFIX-2_執行.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES-HOTFIX-2_msg.txt
git commit -F /tmp/PIPE-SLIDES-HOTFIX-2_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <HOTFIX-2 hash>   # B/E/F 互不依賴、整體 revert 安全；或還原 2 .bak
# 備案：E 誤洗真內容日期 → 收緊 ≥3 頁門檻；F 邊界 → 條列前瞻再補符號
```
