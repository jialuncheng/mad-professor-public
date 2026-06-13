# PIPE-SLIDES-HOTFIX-5 執行報告 — 有標題過場頁未踢除

> BE-Hotfix 落地報告。依 `.claude-logs/baton/2026-06-14_PIPE-SLIDES-HOTFIX-5_hotfix.md §修法`。

---

## §1 基準與完成狀態

- **基準**：`gemini-refactor`、worktree `hopeful-yalow-902c50`；RAG-12-HOTFIX-1 剛落地。
- **完成狀態**：代碼落地、grep + SOP §5 + pytest 通過。**尚未 commit**（baron 手動，§8）。

## §2 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| HOTFIX-5 | （待 baron 回填）| BE-Hotfix: PIPE-SLIDES-HOTFIX-5 — 有標題過場頁未踢除（is_blank 跳過放寬 + Vision prompt 釐清）|

## §3 diff stat

```
 pipelines/slide_pipeline.py    | Vision prompt 第5條釐清（過場頁納 is_blank=true）+ 跳過邏輯放寬（is_blank 且 markdown_content 空）
 tests/test_slide_pipeline.py   | +5 回歸測試（hf5）
```
備份：`.claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-5_slide_pipeline.py.bak`（納入 git add）。

## §4 真因（對應 hotfix.md）

HOTFIX-4 跳過判定採雙保險（is_blank 且 **title 與 markdown_content 皆空**）;過場頁被 Vision 忠實轉錄出標題「過場投影片 (Transition Slide)」→ title 非空 → 雙保險不成立 → 不跳;既有三欄全空規則亦因 figure_description 非空（描述生態球裝飾圖）而不跳 → 漏網（Ch37 page-32）。過場頁與純圖表頁結構同型（title + figure_description + 無正文），唯 is_blank 可分。

## §5 修法（落地）

`pipelines/slide_pipeline.py`（`# === [PIPE-SLIDES-HOTFIX-5 HOTFIX-5 ...] ===` 包裹）：
1. **跳過邏輯放寬**（P1 `_process` ④）：`if r.get("is_blank") and not ((title or content) 皆空)` → **`if r.get("is_blank") and not (markdown_content).strip()`**。容許 title/figure_description 非空（過場頁特徵）;安全網＝is_blank 但有實質 markdown_content（自相矛盾）→ 不跳防誤殺;真圖表頁 is_blank=false → 第一項不成立 → 不跳;舊 golden 無 is_blank → falsy → 不跳。保留第二道「三欄全空」後盾。
2. **Vision prompt 第5條釐清**（既有 HOTFIX-4 包裹內）：明訂純過場/章節分隔/裝飾頁（即使判讀出「過場/Transition/Section」標題）仍 is_blank=true;保留「含真實圖表/照片/示意圖/資料/條列正文一律 is_blank=false」防誤殺真圖頁。

## §6 不可動清單遵守狀態

- [x] ✅ RAG 隔離：`ctx.rag_sections` / `merged` 未碰（僅 P1 `_process` ④ 過濾邏輯 + prompt 字串）。
- [x] ✅ 未碰 `web_server.py` / 其餘四路管線 / 渲染層。
- [x] ✅ 保留既有「三欄全空」過濾為後盾。
- [x] ✅ 主 repo 目錄未讀寫。

## §7 端到端驗證計畫結果

### §7.1 grep 核查
```
PIPE-SLIDES-HOTFIX-5 包裹/標記：2
新跳過邏輯 is_blank && not markdown_content：1
prompt 第5條釐清「過場/Transition/Section」：1
hf5 回歸測試：5
```

### §7.2 §5 SOP 一致性核查（BE-Hotfix 強制）
```
[logging] grep "traceback.format_exc|logger.error|logger.exception" 於本次改動：無命中（合規、純 prompt+過濾、無 logging）
[database] grep "\.commit(" pipelines/slide_pipeline.py：無命中（合規、本檔不涉 DB/交易）
```

### §7.3 pytest
```
tests/test_slide_pipeline.py：67 passed（既有 62 + hf5 新 5）
全套件：1 failed, 636 passed, 3 skipped
```
- **636 passed = 基線（631）+ 5 新測試**;唯一 failed＝`test_logging_config.py::test_settings_log_format_default_auto`（既有 `.env LOG_FORMAT=json` env flake、與本次零關係）。
- 既有 4 個 HOTFIX-4 is_blank 測試**全數仍通過**（safety_belt 用 title+content 皆非空 → 我的 content-based 安全網保住、不退化）。

### §7.4 5 新回歸測試（hf5）
| 測試 | 情境 | 斷言 |
|---|---|---|
| `test_hf5_transition_slide_skipped_with_title` | is_blank=true + 標題「過場投影片」+ 無正文 + 裝飾 desc | **跳過**（治本：有標題過場頁）|
| `test_hf5_decorative_blank_skipped` | is_blank=true + 僅裝飾橫條 | 跳過（沿用 HOTFIX-4 案）|
| `test_hf5_real_figure_page_kept` | is_blank=false + 標題 + 真圖 desc + 無正文 | **保留**（同型真圖不誤踢）|
| `test_hf5_is_blank_but_has_content_kept` | is_blank=true + 有 markdown_content 正文 | 保留（安全網防誤殺）|
| `test_hf5_legacy_no_is_blank_kept` | 無 is_blank 欄（舊 golden）| 保留（向後相容）|

### §7.5 ⚠️ golden 重捕 + baron 影子 E2E（重跑管線、headless 不可替代）
- **改 Vision prompt → slides golden 須重捕**;搭既有待捕批次（HOTFIX-1/1b/2/3/3b/3c/3d/4 + META-NORM C3/C4 + 本 HOTFIX-5）一次首捕（`venv/bin/python tools/golden_baseline.py capture slides --force`）。
- 影子重傳 `Ch37_Plant-Nutrition.pdf` → page-32 生態球過場頁**不再產 reading 頁**、頁序順移;真圖表頁（氮循環圖、土壤剖面、PCoA 等）**未被誤踢**。

## §8 baron 執行命令

```bash
# 1. 備份已完成（§3）

# 2. git add（代碼 + 測試 + 備份 + 移出 baton 之正式歸檔 + run 提示詞）
git add pipelines/slide_pipeline.py tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-5_slide_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-5_hotfix.md
git add .claude-logs/executions/2026-06-14_PIPE-SLIDES-HOTFIX-5_執行.md
git add .claude-logs/prompts/2026-06-14_PIPE-SLIDES-HOTFIX-5_run_提示詞.md .claude-logs/prompts/2026-06-14_PIPE-SLIDES-HOTFIX-5_doc_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 tmp/PIPE-SLIDES-HOTFIX-5_msg.txt；簽名已更正網域）
mkdir -p tmp
cat > tmp/PIPE-SLIDES-HOTFIX-5_msg.txt << 'EOF'
BE-Hotfix: PIPE-SLIDES-HOTFIX-5 — 有標題過場頁未踢除（is_blank 跳過放寬 + Vision prompt 釐清）

真因：HOTFIX-4 跳過要求 is_blank 且 title+content 皆空（防誤殺保守設計）；過場/分隔頁被 Vision
忠實轉錄出標題（如「過場投影片 (Transition Slide)」）→ title 非空 → 不跳；既有三欄全空規則亦因
figure_description 非空（描述裝飾圖）而不跳 → 漏網（Ch37 page-32 生態球過場頁）。

修法（雙管齊下）：
1. 跳過邏輯放寬：is_blank 且 markdown_content 空即跳（容許 title/figure_description 非空，
   過場頁＝裝飾圖+可能標題但無條列正文）；安全網＝is_blank 但有實質正文則不跳，防誤殺。
2. Vision prompt 釐清：純過場/章節分隔/裝飾頁即使有「過場/Transition」標題仍 is_blank=true；
   保留「含真實圖表/照片/示意圖/資料/條列正文之頁一律 is_blank=false」→ 真圖表頁不誤踢。

結構同型困境：過場頁與純圖表頁同型（title+裝飾/真圖 figure_description+無正文），唯 is_blank 可分；
故信任 is_blank 並強化 prompt 使其對過場頁可靠。RAG/渲染層/四路零碰。

SOP 核查：logging + database 皆無命中（合規）。
驗證：5 新回歸測試（過場頁跳/裝飾頁跳/真圖頁保留/有正文保留/舊無欄相容）；slide 67 passed、全套件 636 passed
（基線維持、唯一 fail＝既有 .env LOG_FORMAT flake）。既有 HOTFIX-4 四測試全數仍通過。
⚠️ 改 Vision prompt → slides golden 須重捕，搭既有批次（HOTFIX-1..4 + META-NORM C3/C4）一次首捕。
baron 影子 E2E：重傳 Ch37 → page-32 不產頁、真圖表頁未誤踢。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F tmp/PIPE-SLIDES-HOTFIX-5_msg.txt
```

> 簽名更正：提示詞原給 `<noreply@anthreply.com>`（網域誤）→ 更正 `<noreply@anthropic.com>`（型號 Opus 4.8 正確）。

## §9 回退方式
`git revert <HOTFIX-5 hash>`（單檔、prompt + 跳過兩 hunk、一步還原）或 `cp .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-5_slide_pipeline.py.bak pipelines/slide_pipeline.py`。

---

### 結論
🟢 跳過放寬 + prompt 釐清落地、5 hf5 測試通過、既有 HOTFIX-4 四測試不退化、slide 67 / 全套件 636 passed、SOP 合規。**有標題過場頁治本。** ⚠️ baron 須 slides golden 重捕（搭批次）+ 影子重傳 Ch37 驗證。
