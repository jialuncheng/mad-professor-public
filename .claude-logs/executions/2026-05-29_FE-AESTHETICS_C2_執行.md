# FE-AESTHETICS C2 — Frontend Full-Stack Refactor 執行報告

---

**任務代號**：FE-AESTHETICS C2
**執行日期**：2026-05-29
**依據規劃**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md`（v1.3）
**次級參考**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md`
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：worktree checkout `3cf8acf`（`BE-Refactor: FE-AESTHETICS C1 — Backend Stepped Layout`）。前端 `static/index.html` 仍保有 BUG-B2 的 `@media screen { display: none }` hide 規則，摘要區塊掛在 `#current-title .title-meta` / `details.title-abstract` 下，測試也仍驗證舊結構。
- **完成狀態**：`static/index.html` 全棧重構完成：
  - 新增 `#abstract-toolbar` 獨立 DOM 元素（全寬、置於 `#content-toolbar` 與 `#empty-state` 之間）
  - 刪除 `#current-title .title-meta` / `.title-meta-sep` / 舊 `details.title-abstract` CSS（掛在 `#current-title` 下的三組規則群）
  - 新增 `#abstract-toolbar { flex-shrink: 0; padding; border-bottom }` + `#abstract-toolbar details.title-abstract` 全套 CSS
  - 刪除 BUG-B2 `@media screen { #paper-content > h1:first-child, > .paper-header-meta { display: none; } }` 規則
  - 新增 `.paper-header-meta { display: flex; flex-direction: column; align-items: center; ... }` + 子 class CSS（`.header-authors/.header-venue-date/.header-doi/.header-keywords`）
  - 新增 `#paper-content > h1:first-child { text-align: center; font-size: var(--font-2xl); ... }` 置中樣式
  - 新增 word-wrap / overflow-x 防禦規則
  - `#abstract-toolbar,` 加入 `@media print` hide 清單
  - `renderTitleHeader` JS 完整重寫：abstract 移至 `#abstract-toolbar`，`#current-title` 只保留 title + tags
  - `deletePaper` JS 補充清除 `#abstract-toolbar`
  - `test_bug_b2_paper_header_meta.py` 前端兩個 CSS test 更新（舊 hide 規則 → 新 flex 規則）
  - `test_bug_f5_p2_inconsistencies.py` `test_b1_main_scale_tokens_in_current_title` 更新（title-meta 已刪 + abstract-toolbar selector）
  - pytest 67/67 全綠

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | `static/index.html` #abstract-toolbar DOM + CSS 全棧重構 + renderTitleHeader/deletePaper JS + 測試更新 | [baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `static/index.html` | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C2_index.html.bak` | DOM + CSS + JS 全棧重構 |
| 修改 | `tests/test_bug_b2_paper_header_meta.py` | — | 前端兩個 CSS test 更新（hide→flex） |
| 修改 | `tests/test_bug_f5_p2_inconsistencies.py` | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C2_test_bug_f5_p2_inconsistencies.py.bak` | title-meta 已刪 + abstract-toolbar selector |

---

## §4 修法說明

### §4.1 DOM — `#abstract-toolbar` 新增

在 `</div><!-- /content-toolbar -->` 之後、`<!-- BUG-F4 A2` 之前插入：

```html
<div id="abstract-toolbar" style="display:none"></div>
```

獨立全寬容器，預設 `display:none`，由 JS `renderTitleHeader` 按需顯示。

### §4.2 CSS — 舊 `#current-title` 子規則群刪除

以下三組 CSS 規則全數刪除（移至 `#abstract-toolbar` 下重建）：
1. `#current-title .title-meta { ... }` + `.title-meta-sep { ... }`
2. `#current-title details.title-abstract { max-height: 12rem; overflow-y: auto; ... }`
3. `#current-title details.title-abstract > summary { ... }` / `> summary::before` / `[open] > summary` / `.abstract-body { ... }`

### §4.3 CSS — `#abstract-toolbar` 新規則群

```css
#abstract-toolbar {
  flex-shrink: 0;
  padding: 0.5rem var(--pad-panel) 0.75rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-sidebar);
}
#abstract-toolbar details.title-abstract {
  font-size: var(--font-base);
  /* ... */
}
#abstract-toolbar details.title-abstract > summary { font-size: var(--font-xs); ... }
#abstract-toolbar details.title-abstract[open] > summary { ... }
#abstract-toolbar details.title-abstract .abstract-body {
  /* ... */
  width: 100%; box-sizing: border-box;
}
```

### §4.4 CSS — BUG-B2 `@media screen` hide 規則刪除

刪除：
```css
/* BUG-B2 Bug 10 ... */
@media screen {
  #paper-content > h1:first-child,
  #paper-content > .paper-header-meta { display: none; }
}
```

學術論文的 `<h1>` 標題與 `<div class="paper-header-meta">` 扉頁在 screen 模式下正常顯示。

### §4.5 CSS — `.paper-header-meta` 置中對稱 flex 排版

新增：
```css
.paper-header-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.25rem;
  padding: 0.5rem 0 1rem;
}
.header-authors { font-size: var(--font-sm); font-weight: 600; ... }
.header-venue-date { font-size: var(--font-xs); color: var(--color-muted); }
.header-doi { font-size: var(--font-xs); color: var(--color-muted); }
.header-keywords { font-size: var(--font-xs); color: var(--color-muted); }
```

### §4.6 CSS — `h1:first-child` 置中 + word-wrap 防禦

```css
#paper-content > h1:first-child {
  text-align: center;
  font-size: var(--font-2xl);
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 0.25rem;
  text-wrap: pretty;
}
#paper-content p, #paper-content li, #paper-content div, #paper-content span {
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}
#paper-content pre, #paper-content code {
  max-width: 100%;
  overflow-x: auto;
}
```

### §4.7 CSS — `@media print` 補入 `#abstract-toolbar`

```css
@media print {
  #content-toolbar, #abstract-toolbar, #chat-panel, ... { display: none !important; }
}
```

### §4.8 JS — `renderTitleHeader` 完整重寫

摘要邏輯從 `#current-title` 拆至 `#abstract-toolbar`：
- `#current-title`：只保留 `<h1 class="title-zh">` + `<p class="title-en">` + tag pills
- `#abstract-toolbar`：academic 文件有 abstract 時顯示 `<details class="title-abstract">`，resume / 無 abstract 時清空並 `display:none`

### §4.9 JS — `deletePaper` 補充清除

刪除 paper 且 `currentPaperId === paperId` 時，額外清除 `#abstract-toolbar`：
```javascript
const delAbstractToolbar = document.getElementById('abstract-toolbar');
if (delAbstractToolbar) {
  delAbstractToolbar.innerHTML = '';
  delAbstractToolbar.style.display = 'none';
}
```

### §4.10 tests/test_bug_b2_paper_header_meta.py 前端 CSS test 更新

- `test_b10_frontend_media_screen_hides_h1_and_header_meta`：`assert not pat.search(STATIC_HTML)`（舊 hide 規則應已刪除）
- `test_b10_frontend_class_hook_not_in_print_media`：改驗 `.paper-header-meta { display: flex }` 存在

### §4.11 tests/test_bug_f5_p2_inconsistencies.py 更新

- 移除 `pat_title_meta` assertion（`.title-meta` 已刪）→ 改為 `assert '#current-title .title-meta' not in STATIC_HTML`
- `pat_abstract` selector：`#current-title` → `#abstract-toolbar`
- `pat_summary` selector：`#current-title` → `#abstract-toolbar`

---

## §5 測試結果

### §5.1 pytest 實際輸出

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- .../venv/bin/python
rootdir: .../hopeful-yalow-902c50
plugins: anyio-4.13.0, langsmith-0.8.5
collected 67 items

tests/test_bug_b2_paper_header_meta.py::test_render_header_en_academic_uses_dash_list_and_wrap PASSED
tests/test_bug_b2_paper_header_meta.py::test_render_header_zh_academic_uses_dash_list_and_wrap PASSED
tests/test_bug_b2_paper_header_meta.py::test_render_header_en_resume_blockquote_preserved PASSED
tests/test_bug_b2_paper_header_meta.py::test_render_header_zh_resume_blockquote_preserved PASSED
tests/test_bug_b2_paper_header_meta.py::test_render_header_en_academic_no_meta_no_wrap PASSED
tests/test_bug_b2_paper_header_meta.py::test_b10_frontend_media_screen_hides_h1_and_header_meta PASSED
tests/test_bug_b2_paper_header_meta.py::test_b10_frontend_class_hook_not_in_print_media PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b1_no_legacy_font_tokens_in_css PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b1_main_scale_tokens_in_current_title PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b3_demo_bar_css_removed PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b3_state_btns_js_dead_code_removed PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b3_toggle_handlers_no_syncStateBar_call PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b4_setup_tooltip_iife_preserved_with_correct_timings PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b4_docs_components_aligned_with_setup_tooltip PASSED
tests/test_bug_f5_p2_inconsistencies.py::test_b4_docs_interaction_aligned_with_setup_tooltip PASSED
...（test_md_restore_processor.py 52 tests）...

============================== 67 passed in 0.04s ==============================
```

### §5.2 SOP 一致性核查

本次為 FE-Refactor 工作流，SOP §5 logging / database 核查僅適用 BE-Refactor；本次不適用。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` 100% 不動 | ✅ 未觸碰 |
| `web_server.py` 100% 不動 | ✅ 未觸碰 |
| `paper_manager.py` 100% 不動 | ✅ 未觸碰 |
| `#current-title` 雙語標題 + `#paper-tags` tag-pill 渲染邏輯不動 | ✅ `renderTitleHeader` 重寫僅移除 abstract 部分；`#current-title h1.title-zh` + `#paper-tags tag-pill` 邏輯保持完整 |
| 主 repo 目錄嚴禁讀寫 | ✅ 所有操作在 worktree 內 |

---

## §7 銜接

- **baton 狀態**：本執行報告暫存 `baton/`，不 mv、不 git add（WORKFLOW_SOP §3 baton 暫存鐵律）
- **下一步**：baron 驗收 C2 結果（手動 commit），確認後下達 Check 提示詞
- **Check 任務**：FE-AESTHETICS Check — Conformance 驗收 + baton/ 全量 mv 歸檔 + TODO.md 結案

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已在 §3 列出（archive/ 中）

# 2. git add 清單
git add static/index.html
git add tests/test_bug_b2_paper_header_meta.py
git add tests/test_bug_f5_p2_inconsistencies.py
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2_index.html.bak
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2_test_bug_f5_p2_inconsistencies.py.bak
git add .claude-logs/prompts/2026-05-29_FE-AESTHETICS_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/FE-AESTHETICS_C2_msg.txt）
# 執行：git commit -F /tmp/FE-AESTHETICS_C2_msg.txt
```

---

## §99 治理規格

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | FE-AESTHETICS C2 執行紀錄；前端全棧重構完整記錄 |
| 用途 | baron 驗收與 git commit 參考；Check 收官的上游基礎 |
| 權威源 | 本檔 §1–§8 |
| 引用方 | FE-AESTHETICS Check 執行報告 |
| 約束事項 | baton/ 暫存、不提前 mv；baron 手動 git commit |

### §99.2 Revision 歷程

- v1 (2026-05-29)：FE-AESTHETICS C2 初版

