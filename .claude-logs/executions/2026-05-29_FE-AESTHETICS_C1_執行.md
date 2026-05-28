# FE-AESTHETICS C1 — Backend Stepped Layout 執行報告

---

**任務代號**：FE-AESTHETICS C1
**執行日期**：2026-05-29
**依據規劃**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md`（v1.3）
**次級參考**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md`
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：worktree checkout `ef1c0b3`（`chore(.claude-logs): 手動歸檔重建之 OPTIMIZE-1`）。`_render_header_en/zh` academic path 採 BUG-B2 格式：`- **Authors**:` dash-list 包進 `<div class="paper-header-meta">` wrap，但 dash-list 在 `marked.js` GFM 中仍造成扉頁渲染層次不夠清晰。
- **完成狀態**：`processor/md_restore_processor.py` `_render_header_en/zh` academic path 全面改為置中對稱階梯式 HTML div 結構（`<div class="header-authors/venue-date/doi/keywords">`），並包進 `<div class="paper-header-meta">` wrap。resume path 100% 未動（禁區遵守）。pytest 59/59 全綠。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `_render_header_en/zh` academic path：dash-list → 階梯式 HTML div + 更新測試 assertions | [baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `processor/md_restore_processor.py` | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_md_restore_processor.py.bak` | `_render_header_en/zh` academic path 改為 HTML div 結構 |
| 修改 | `tests/test_bug_b2_paper_header_meta.py` | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_test_bug_b2_paper_header_meta.py.bak` | 更新 academic 後端 test assertions（dash-list → HTML div） |
| 修改 | `tests/test_md_restore_processor.py` | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_test_md_restore_processor.py.bak` | 更新 `test_render_header_*_academic_full` assertions |
| 新建 | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_md_restore_processor.py.bak` | — | pre-C1 備份 |
| 新建 | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_test_bug_b2_paper_header_meta.py.bak` | — | pre-C1 備份 |
| 新建 | `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_test_md_restore_processor.py.bak` | — | pre-C1 備份 |

> ⚠️ **備份欄位強制注意**：以上三份 `.bak` 備份檔必須在 C1 Commit 的 `git add` 清單中強制包含。

---

## §4 修法說明

### §4.1 `processor/md_restore_processor.py` — `_render_header_en` academic path 重塑

**修改前（BUG-B2 dash-list）**：
```python
# BUG-B2 Bug 10（v4 §B B10.3 / ui-fixes-batch B8.1）：
# `>` blockquote → `-` list（避免 marked.js GFM 單換行不分段、塌成單行）
meta_bits = []
if authors_list:
    meta_bits.append(f"- **Authors**: {', '.join(str(a) for a in authors_list)}")
if date:
    meta_bits.append(f"- **Date**: {date}")
if venue:
    meta_bits.append(f"- **Venue**: {venue}")
if doi:
    meta_bits.append(f"- **DOI**: {doi}")
if keywords:
    meta_bits.append(f"- **Keywords**: {', '.join(keywords)}")

if meta_bits:
    lines.append('<div class="paper-header-meta">')
    lines.append("")
    lines.extend(meta_bits)
    lines.append("")
    lines.append('</div>')
    lines.append("")
```

**修改後（FE-AESTHETICS C1 HTML div）**：
```python
# FE-AESTHETICS C1（2026-05-29）：重塑學術論文扉頁為置中對稱階梯式 HTML 排版（方案 A 不含 affiliation）
# `- **Authors**:` list → <div class="header-authors"> 等 HTML div 結構
# + 包進 <div class="paper-header-meta"> wrap（前端 CSS class hook 穩定 hide）
# venue + date 合併為 header-venue-date（用 · 分隔）；適用：academic 等非 resume doc_type
html_bits = []
if authors_list:
    html_bits.append(f'  <div class="header-authors">{", ".join(str(a) for a in authors_list)}</div>')
venue_date_bits = []
if venue:
    venue_date_bits.append(venue)
if date:
    venue_date_bits.append(date)
if venue_date_bits:
    html_bits.append(f'  <div class="header-venue-date">{" · ".join(venue_date_bits)}</div>')
if doi:
    html_bits.append(f'  <div class="header-doi">DOI: {doi}</div>')
if keywords:
    html_bits.append(f'  <div class="header-keywords">Keywords: {", ".join(keywords)}</div>')

if html_bits:
    lines.append('<div class="paper-header-meta">')
    lines.extend(html_bits)
    lines.append('</div>')
    lines.append("")
```

**設計亮點**：
- venue + date 合併為單一 `header-venue-date` div，以 ` · ` 分隔（semantic grouping）
- 缺項靜默省略（全空時不輸出 wrap div）
- resume path 100% 不動（`if doc_type == 'resume': ... return` 早返回不受影響）

### §4.2 `processor/md_restore_processor.py` — `_render_header_zh` academic path 重塑

相同結構改法，中文版差異：
- authors join 使用中文頓號 `、`
- `<div class="header-keywords">關鍵字：{...}</div>`（中文 label + 頓號 join）

### §4.3 `tests/test_bug_b2_paper_header_meta.py` — academic 後端 assertions 更新

`test_render_header_en_academic_uses_dash_list_and_wrap`（英文）：
```python
# 舊 assertions（已移除）
assert f"- **{label}**" in md  # dash-list 格式

# 新 assertions
assert "- **Authors**" not in md, '英文 academic 不應再用 - list'
assert '<div class="header-authors">Alice, Bob</div>' in md
assert '<div class="header-venue-date">ICML · 2024-01</div>' in md
assert '<div class="header-doi">DOI: 10.1234/xyz</div>' in md
assert '<div class="header-keywords">Keywords: k1, k2</div>' in md
```

`test_render_header_zh_academic_uses_dash_list_and_wrap`（中文）：
```python
assert "- **作者**" not in md, '中文 academic 不應再用 - list'
assert '<div class="header-authors">甲、乙</div>' in md
assert '<div class="header-venue-date">某會議 · 2024-01</div>' in md
assert '<div class="header-doi">DOI: 10.1234/xyz</div>' in md
assert '<div class="header-keywords">關鍵字：關鍵字1、關鍵字2</div>' in md
```

**C2 前端 test 不動**：`test_b10_frontend_media_screen_hides_h1_and_header_meta` 與 `test_b10_frontend_class_hook_not_in_print_media` 兩個 frontend 測試讀取 `STATIC_HTML`，待 C2 更新 `static/index.html` 後再調整（目前仍通過，因為 BUG-B2 的 @media screen CSS 已存在）。

### §4.4 `tests/test_md_restore_processor.py` — academic full assertions 更新

```python
# test_render_header_en_academic_full 更新
assert '<div class="paper-header-meta">' in h
assert '<div class="header-authors">Alice, Bob</div>' in h
assert '<div class="header-venue-date">Nature · 2024-05-20</div>' in h
assert '<div class="header-doi">DOI: 10.1038/x</div>' in h
assert '<div class="header-keywords">Keywords: AI</div>' in h

# test_render_header_zh_academic_full 更新
assert '<div class="header-authors">Alice、Bob</div>' in h
assert '<div class="header-venue-date">Nature · 2024-05-20</div>' in h
assert 'DOI' not in h  # 空 doi → 不輸出 div
assert '<div class="header-keywords">關鍵字：人工智慧</div>' in h
```

---

## §5 測試結果

### §5.1 pytest 實際輸出

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- .../venv/bin/python
cachedir: .pytest_cache
rootdir: .../hopeful-yalow-902c50
plugins: anyio-4.13.0, langsmith-0.8.5
collecting ... collected 59 items

tests/test_bug_b2_paper_header_meta.py::test_render_header_en_academic_uses_dash_list_and_wrap PASSED [  1%]
tests/test_bug_b2_paper_header_meta.py::test_render_header_zh_academic_uses_dash_list_and_wrap PASSED [  3%]
tests/test_bug_b2_paper_header_meta.py::test_render_header_en_resume_blockquote_preserved PASSED [  5%]
tests/test_bug_b2_paper_header_meta.py::test_render_header_zh_resume_blockquote_preserved PASSED [  6%]
tests/test_bug_b2_paper_header_meta.py::test_render_header_en_academic_no_meta_no_wrap PASSED [  8%]
tests/test_bug_b2_paper_header_meta.py::test_b10_frontend_media_screen_hides_h1_and_header_meta PASSED [ 10%]
tests/test_bug_b2_paper_header_meta.py::test_b10_frontend_class_hook_not_in_print_media PASSED [ 11%]
tests/test_md_restore_processor.py::test_blacklist_exact_match PASSED    [ 13%]
...（中間 46 tests）...
tests/test_md_restore_processor.py::test_render_header_en_academic_full PASSED [ 81%]
tests/test_md_restore_processor.py::test_render_header_zh_academic_full PASSED [ 83%]
tests/test_md_restore_processor.py::test_render_header_resume_simplified PASSED [ 84%]
tests/test_md_restore_processor.py::test_render_header_missing_fields_silently_omitted PASSED [ 86%]
...（剩餘 tests）...
tests/test_md_restore_processor.py::test_render_header_resume_no_abstract_block PASSED [100%]

============================== 59 passed in 0.06s ==============================
```

### §5.2 SOP 一致性核查

**logging 核查**（BE-Refactor 必跑）：
```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" processor/md_restore_processor.py
```
> 無命中（合規）——`_render_header_en/zh` 為純字串生成函數，無 exception handling 邏輯。

**database 核查**（BE-Refactor 必跑）：
```bash
grep -nE "\.commit\(\)" processor/md_restore_processor.py | grep -v "with .*session.*begin\(\)"
```
> 無命中（合規）——`_render_header_en/zh` 不涉及資料庫操作。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` 100% 不動 | ✅ 未觸碰 |
| `web_server.py` 100% 不動 | ✅ 未觸碰 |
| `paper_manager.py` 100% 不動 | ✅ 未觸碰 |
| `processor/md_restore_processor.py` `_clean_authors_info` 邏輯不動 | ✅ 未觸碰（L898-900 保留原樣）|
| `processor/md_restore_processor.py` `doc_type == 'resume'` 路徑不動 | ✅ 未觸碰（L450-458 en / L507-515 zh resume early return 保留）|
| 主 repo 目錄嚴禁讀寫 | ✅ 所有操作在 worktree 內 |

---

## §7 銜接

- **baton 狀態**：本執行報告暫存 `baton/`，不 mv、不 git add（WORKFLOW_SOP §3 baton 暫存鐵律）
- **下一步**：baron 驗收 C1 結果（手動 commit），確認後下達 C2 提示詞
- **C2 任務**：FE-AESTHETICS C2 — Frontend Full-Stack Refactor
  - `static/index.html` 新增 `#abstract-toolbar` DOM、`.paper-header-meta { display: flex }` CSS、更新 `renderTitleHeader` JS
  - 更新 `test_b10_frontend_*` 兩個前端 CSS tests
  - 更新 `tests/test_bug_f5_p2_inconsistencies.py` `#abstract-toolbar` print-hide 測試

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已在 §3 列出（3 份 .bak，archive/ 中）

# 2. git add 清單
git add processor/md_restore_processor.py
git add tests/test_bug_b2_paper_header_meta.py
git add tests/test_md_restore_processor.py
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_md_restore_processor.py.bak
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_test_bug_b2_paper_header_meta.py.bak
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C1_test_md_restore_processor.py.bak
git add .claude-logs/prompts/2026-05-29_FE-AESTHETICS_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/FE-AESTHETICS_C1_msg.txt）
# 執行：git commit -F /tmp/FE-AESTHETICS_C1_msg.txt
```

---

## §99 治理規格

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| 目的 | FE-AESTHETICS C1 執行紀錄；後端扉頁 HTML 重塑完整記錄 |
| 用途 | baron 驗收與 git commit 參考；C2 前端重構的上游基礎 |
| 權威源 | 本檔 §1–§8 |
| 引用方 | FE-AESTHETICS C2 執行報告 |
| 約束事項 | baton/ 暫存、不提前 mv；baron 手動 git commit |

### §99.2 Revision 歷程

- v1 (2026-05-29)：FE-AESTHETICS C1 初版
