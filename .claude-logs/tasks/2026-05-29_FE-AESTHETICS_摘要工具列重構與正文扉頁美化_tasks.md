# FE-AESTHETICS 摘要工具列重構與正文扉頁美化 — Tasks

> 本文件為 FE-AESTHETICS 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md` (v1.3) 計畫產出，含 2 個業務 Commit + 1 個 Check。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 5 個 | `archive/2026-05-29_FE-AESTHETICS_C1_md_restore_processor.py.bak` / `archive/2026-05-29_FE-AESTHETICS_C1_test_bug_b2_paper_header_meta.py.bak` / `archive/2026-05-29_FE-AESTHETICS_C1_test_md_restore_processor.py.bak` / `archive/2026-05-29_FE-AESTHETICS_C2_index.html.bak` / `archive/2026-05-29_FE-AESTHETICS_C2_test_bug_f5_p2_inconsistencies.py.bak` |
| **修改檔案** | 5 個 | `processor/md_restore_processor.py`（`_render_header_en/zh` HTML 重塑）/ `tests/test_bug_b2_paper_header_meta.py`（assertions 更新）/ `tests/test_md_restore_processor.py`（assertions 更新）/ `static/index.html`（DOM + CSS + JS 全棧重構）/ `tests/test_bug_f5_p2_inconsistencies.py`（assertions 更新）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（FE-AESTHETICS 🟡 WIP 條目）/ `prompts/INDEX.md`（FE-AESTHETICS Tasks 登錄）|
| **Commits** | 3 個 | C1（後端） → C2（前端） → Check（收官） |
| **baton 歸檔** | 1 次 | Check 收官：`mv baton/plan + baton/tasks + baton/C1執行 + baton/C2執行 → plans/ + tasks/ + executions/` |

---

## §1 TL;DR（概要）

- **挑戰**：①摘要在 `#current-title` 內受 `max-height: 12rem` + `overflow-y: auto` 限制，視覺欠佳；②`@media screen` 隱藏了正文最上方學術扉頁 `.paper-header-meta`，導致 raw `authors_info` 機構單位懸空；③`#paper-content` 缺乏防禦性折行，長字串撐爆版面。
- **解法**：
  - C1 — Backend Stepped Layout（後端扉頁 HTML 重塑）：將 `_render_header_en/zh` 從 markdown dash-list 改為階梯式 HTML div 結構（方案 A，不含 affiliation）。
  - C2 — Frontend Full-Stack Refactor（前端全棧重構）：新增 `#abstract-toolbar` 滿寬摘要容器、廢除 `.title-meta`、解鎖 `.paper-header-meta`、補 word-wrap 防禦、更新 JS 渲染邏輯、更新 `@media print`。
- **影響範圍**：`processor/md_restore_processor.py`（後端）、`static/index.html`（前端）、3 個 pytest 測試檔。不影響 `pipeline_core.py` / `web_server.py` / `paper_manager.py` / 任何 API 端點。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 待處理 |
|---|---|---|
| `processor/md_restore_processor.py` L435–L544 | `_render_header_en/zh` 輸出 `- **Authors**:` dash-list + `<div class="paper-header-meta">` wrap | 改為 `<div class="header-authors">` 等 HTML div 階梯結構（方案 A 不含 affiliation） |
| `static/index.html` L716–L738 | `.title-meta` + `.title-meta-sep` CSS 規則存在 | 完全刪除（廢除 `.title-meta` 顯示） |
| `static/index.html` L728–L787 | `#current-title details.title-abstract*` 四個 CSS 規則塊 | 完全刪除，改由 `#abstract-toolbar details.title-abstract*` 接管 |
| `static/index.html` L803–L808 | `@media screen { display: none }` 隱藏 `h1:first-child` 與 `.paper-header-meta` | 刪除此規則，解鎖學術扉頁螢幕顯示 |
| `static/index.html` L1174–L1182 | `@media print` hide 清單含 `#content-toolbar` 但不含 `#abstract-toolbar` | 在 `#content-toolbar,` 後加入 `#abstract-toolbar,` |
| `static/index.html` L2418–L2472 | `renderTitleHeader` 在 `#current-title` 渲染 `.title-meta` + `details.title-abstract` | 重寫：`.title-meta` 廢除；摘要移至 `#abstract-toolbar` 渲染 |
| `static/index.html` L2682–L2689 | `deletePaper` 未清空 `#abstract-toolbar` | 加入 `#abstract-toolbar` 的 `innerHTML = ''` + `display = 'none'` |
| `tests/test_bug_b2_paper_header_meta.py` L31–L87, L149–L178 | assertions 驗證 `- **Authors**` dash-list 格式與舊 screen-hide 規則存在 | 改驗 HTML div 格式 + 驗 screen-hide 規則**不**存在 |
| `tests/test_md_restore_processor.py` L392–L418 | assertions 驗證 `'Authors' in h` + `'Alice, Bob' in h` | 改驗 `<div class="header-authors">Alice, Bob</div>` |
| `tests/test_bug_f5_p2_inconsistencies.py` L70–L94 | assertions 驗證 `#current-title .title-meta` 與 `#current-title details.title-abstract` CSS | 改驗 `.title-meta` **不**存在 + `#abstract-toolbar details.title-abstract` CSS 存在 |

---

## §3 觀察問題

### 問題 #1：摘要容器高度被鎖死
- **證據**：`static/index.html` L728-L738：`max-height: 12rem; overflow-y: auto;`
- **影響**：長摘要出現內部垂直滾動條，視覺破碎

### 問題 #2：`.paper-header-meta` 被 `@media screen` 整個隱藏
- **證據**：`static/index.html` L803-L808：`@media screen { ... display: none; }`
- **影響**：raw `authors_info` 中的 organization 欄位（機構）懸空於正文最上方，視覺 bug

### 問題 #3：`#paper-content` 缺乏防禦性折行
- **證據**：`static/index.html` 無 `overflow-wrap: break-word` 規則
- **影響**：長 URL、超長等號分隔線等字串溢出撐破版面

---

## §4 設計方案

### §4.1 C1 — 後端扉頁 HTML 重塑

`_render_header_en` L435-L489 與 `_render_header_zh` L492-L544 的 academic 路徑：
- 將 `meta_bits` 從 `f"- **Authors**: ..."` 格式改為 `html_bits`，每項為 `<div class="header-*">` 結構
- resume 路徑（`if doc_type == 'resume':` 提前 return）維持不變
- 呼叫端（L879-L888 附近）無需改動（方案 A）

### §4.2 C2 — 前端全棧重構

DOM：在 `#content-toolbar` 與 `#empty-state` 之間插入 `<div id="abstract-toolbar" style="display:none"></div>`

CSS 刪除：
- L716-L727：`#current-title .title-meta` + `#current-title .title-meta-sep`
- L728-L787：`#current-title details.title-abstract` 四個規則塊
- L803-L808：`@media screen { ... display: none }`

CSS 新增（插入於被刪 CSS 的位置）：
- `#abstract-toolbar` 容器樣式
- `#abstract-toolbar details.title-abstract*` 四個規則塊
- `#paper-content` overflow-x + `p, li, div, span` word-wrap + `pre, code` overflow-x:auto
- `.paper-header-meta` 置中 flex column 扉頁樣式
- `#paper-content > h1:first-child` 置中標題樣式

CSS 更新：L1174-L1182 `@media print` 清單加入 `#abstract-toolbar,`

JS：
- `renderTitleHeader`：摘要渲染邏輯搬至 `#abstract-toolbar`，`#current-title` 只留雙語標題 + tag-pill
- `deletePaper`：加入 `abstractToolbar.innerHTML = ''` + `display = 'none'`

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| `_render_header_en/zh` 呼叫端有 `affiliation` 參數殘留 | 🟢 低 | 方案 A 呼叫端完全無需改動；grep 驗證確認 L879 附近無 `affiliation` 傳入 |
| 舊 paper（無 `<div class="header-authors">` 格式）正文顯示異常 | 🟡 中 | 已知既有 paper 用舊 dash-list 格式，螢幕解鎖後會直接顯示 markdown list；不影響新上傳 paper；不做 backfill（依 plan §3） |
| `renderTitleHeader` 重寫後 `lang-toggle` 切語言路徑失效 | 🟢 低 | `lang-toggle` L2617 呼叫 `renderTitleHeader(currentPaper)` 不變；`abstractToolbar` 在函數內重新渲染摘要，語言切換自動觸發 |
| `@media print` 更新後舊 paper 列印出現亂排 | 🟢 低 | 只新增 `#abstract-toolbar` 隱藏規則，不移除既有任何印規則 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# 後端函數確認：新格式存在
grep -n "header-authors\|header-venue-date\|header-doi\|header-keywords" processor/md_restore_processor.py
# 期望：435 行附近有 4 個命中

# 舊格式消失
grep -n '"\- \*\*Authors\*\*"\|"\- \*\*作者\*\*"' processor/md_restore_processor.py
# 期望：0 命中

# pytest 精準驗收
./venv/bin/pytest tests/test_bug_b2_paper_header_meta.py tests/test_md_restore_processor.py -v
# 期望：全 passed，0 failed
```

### §6.2 C2 驗收

```bash
# DOM 新增確認
grep -n "abstract-toolbar" static/index.html
# 期望：多個命中（DOM + CSS + JS）

# 舊 CSS 廢除確認
grep -n "title-meta\b" static/index.html
# 期望：0 命中（或只有 JS 渲染的舊 comment 若有殘留需清除）

# @media screen 隱藏規則消失
grep -n "display: none" static/index.html | grep -v "style=" | head -20
# 期望：L803 舊規則不在輸出中

# @media print 包含 abstract-toolbar
grep -A 15 "@media print" static/index.html
# 期望：#abstract-toolbar, 出現在 hide 清單中

# pytest 全棧驗收
./venv/bin/pytest tests/test_bug_b2_paper_header_meta.py tests/test_bug_f5_p2_inconsistencies.py tests/test_md_restore_processor.py -v
# 期望：全 passed，0 failed

# 全套 regression 保障
./venv/bin/pytest tests/ -v
# 期望：全 passed（含既有 383+ 測試）
```

---

## §7 不可動清單

- [ ] `pipeline_core.py` — 100% 不動
- [ ] `web_server.py` — 100% 不動
- [ ] `paper_manager.py` — 100% 不動
- [ ] `processor/md_restore_processor.py` 的 `_clean_authors_info` 邏輯 — 不動（核心清理邏輯）
- [ ] `processor/md_restore_processor.py` 的 `doc_type == 'resume'` 路徑（`_resolve_candidate_extras` + blockquote preservation） — 不動（履歷特例路徑）
- [ ] `static/index.html` 的 `#current-title` 雙語標題 + `#paper-tags` tag-pill 渲染邏輯 — 不動（保留常駐導航）
- [ ] 主 repo 目錄 — 嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C1 — Backend Stepped Layout（後端扉頁 HTML 重塑）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改：`processor/md_restore_processor.py` / `tests/test_bug_b2_paper_header_meta.py` / `tests/test_md_restore_processor.py`；新建：`archive/2026-05-29_FE-AESTHETICS_C1_md_restore_processor.py.bak` / `archive/2026-05-29_FE-AESTHETICS_C1_test_bug_b2_paper_header_meta.py.bak` / `archive/2026-05-29_FE-AESTHETICS_C1_test_md_restore_processor.py.bak` |
| **安全性** | 🟢 高 — 純後端 Markdown 生成邏輯，不影響 API 端點、DB schema 或任何 runtime 服務路徑；fulfills 不動清單（呼叫端 L879 無需改動） |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；`.bak` 備份亦可手動還原 |
| **驗收 grep 條件** | 見 §6.1：`grep -n "header-authors" processor/md_restore_processor.py` 期望命中 + `pytest tests/test_bug_b2_paper_header_meta.py tests/test_md_restore_processor.py -v` 全 passed |
| **依賴關係** | 無前置（可獨立執行） |
| **具體實作細節** | **① 備份**：`cp processor/md_restore_processor.py archive/2026-05-29_FE-AESTHETICS_C1_md_restore_processor.py.bak`；同理備份 2 個 test 檔。**② 修改 `processor/md_restore_processor.py` L435-L489（`_render_header_en` academic 路徑）**：刪除 `meta_bits = []` ... `lines.extend(meta_bits)` 舊邏輯，替換為 `html_bits = []` 結構：`if authors_list: html_bits.append(f'  <div class="header-authors">{", ".join(str(a) for a in authors_list)}</div>')`；venue/date 合併為 `venue_date_bits` 後 `html_bits.append(f'  <div class="header-venue-date">{" · ".join(venue_date_bits)}</div>')`；`if doi: html_bits.append(f'  <div class="header-doi">DOI: {doi}</div>')`；`if keywords: html_bits.append(f'  <div class="header-keywords">Keywords: {", ".join(keywords)}</div>')`；`if html_bits: lines.append('<div class="paper-header-meta">'); lines.extend(html_bits); lines.append('</div>'); lines.append("")`。resume 路徑（L440-L452 `if doc_type == 'resume':` 提前 return 區塊）維持不變。**③ 同理修改 `_render_header_zh` L492-L544**：academic 路徑替換為 `html_bits`，中文版 `<div class="header-authors">{"、".join(...)}</div>`；`<div class="header-venue-date">`；`<div class="header-doi">DOI: {doi}</div>`；`<div class="header-keywords">關鍵字：{"、".join(keywords)}</div>`。resume 路徑不動。**④ 修改 `tests/test_bug_b2_paper_header_meta.py`**：L31 `test_render_header_en_academic_uses_dash_list_and_wrap`——刪除 `for label in ("Authors", ...)` 舊 assert，改為 `assert "- **Authors**" not in md` + `assert '<div class="paper-header-meta">' in md` + `assert '<div class="header-authors">Alice, Bob</div>' in md` + `assert '<div class="header-venue-date">ICML · 2024-01</div>' in md` + `assert '<div class="header-doi">DOI: 10.1234/xyz</div>' in md` + `assert '<div class="header-keywords">Keywords: k1, k2</div>' in md`；L59 同理更新中文版 assertions；L149 `test_b10_frontend_media_screen_hides_h1_and_header_meta`——assertion 從 `assert pat.search(...)` 改為 `assert not pat.search(...)`，並更新 docstring 說明「不應再隱藏」；L165 `test_b10_frontend_class_hook_not_in_print_media`——移除舊 context_before 邏輯，改為 `pat = re.compile(r'\.paper-header-meta\s*\{[^}]*display:\s*flex', re.DOTALL)` + `assert pat.search(STATIC_HTML)`。**⑤ 修改 `tests/test_md_restore_processor.py`**：L392 `test_render_header_en_academic_full`——移除 `assert 'Authors' in h and 'Alice, Bob' in h` 等舊 assertions，替換為 `assert '<div class="paper-header-meta">' in h` + `assert '<div class="header-authors">Alice, Bob</div>' in h` + `assert '<div class="header-venue-date">Nature · 2024-05-20</div>' in h` + `assert '<div class="header-doi">DOI: 10.1038/x</div>' in h` + `assert '<div class="header-keywords">Keywords: AI</div>' in h`；L405 同理更新中文版（含 `assert 'DOI' not in h` 空值省略驗證）。**⑥ 執行 pytest 驗收**：`./venv/bin/pytest tests/test_bug_b2_paper_header_meta.py tests/test_md_restore_processor.py -v`，全 passed 後繼續。 |

---

### C2 — Frontend Full-Stack Refactor（前端全棧重構）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改：`static/index.html` / `tests/test_bug_f5_p2_inconsistencies.py`；新建：`archive/2026-05-29_FE-AESTHETICS_C2_index.html.bak` / `archive/2026-05-29_FE-AESTHETICS_C2_test_bug_f5_p2_inconsistencies.py.bak` |
| **安全性** | 🟡 中 — FE-Refactor 工作流；修改 `static/index.html` CSS/DOM/JS 三層，需手動 E2E 核查；後端 Python 已 C1 落地，CSS class hook（`header-authors` 等）已存在 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾；`.bak` 備份可手動還原 `index.html` |
| **驗收 grep 條件** | 見 §6.2：`grep -n "abstract-toolbar" static/index.html` 多個命中 + `pytest tests/ -v` 全 passed + 手動 E2E 核查 4 項（§6.2 plan 中 E2E 清單） |
| **依賴關係** | C1 前置（`_render_header_en/zh` HTML 格式須已落地，CSS `.header-authors` 才有意義顯示） |
| **具體實作細節** | **① 備份**：`cp static/index.html archive/2026-05-29_FE-AESTHETICS_C2_index.html.bak`；`cp tests/test_bug_f5_p2_inconsistencies.py archive/2026-05-29_FE-AESTHETICS_C2_test_bug_f5_p2_inconsistencies.py.bak`。**② DOM 修改**：在 `static/index.html` `#content-toolbar` 閉合 `</div>` 後（L192-L224 區間）、`<!-- BUG-F4 A2` 注釋前，插入一行 `    <div id="abstract-toolbar" style="display:none"></div>`。**③ CSS 刪除**：移除 L716-L727 `#current-title .title-meta { ... }` + `#current-title .title-meta-sep { ... }` 兩個規則；移除 L728-L787 `#current-title details.title-abstract { ... }` 四個規則塊（含 summary / [open] summary / .abstract-body）。移除 L803-L808 整個 `@media screen { #paper-content > h1:first-child, #paper-content > .paper-header-meta { display: none; } }` 區塊。**④ CSS 新增**（插入於被刪 CSS 的位置，即 L716 前後，或在 `/* tag-pill */` 注釋前）：依 plan §8.2 【異動後】完整插入：`#abstract-toolbar` 容器規則（padding / border-bottom / max-width / margin / width / box-sizing）+ `#abstract-toolbar details.title-abstract` 四個規則塊 + `#paper-content { overflow-x: hidden; ... }` + `#paper-content p, li, div, span { overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; }` + `#paper-content pre, code { max-width: 100%; overflow-x: auto; }` + `.paper-header-meta { display: flex; flex-direction: column; align-items: center; text-align: center; ... }` + `.paper-header-meta .header-authors / .header-venue-date / .header-doi / .header-keywords { ... }` + `#paper-content > h1:first-child { text-align: center; font-size: var(--font-2xl); ... }`。**⑤ CSS print 更新**：找到 L1174 `@media print {` 區塊中 `#content-toolbar,` 這行，在其後加入 `    #abstract-toolbar,`（保持縮排一致）。**⑥ JS 重寫 `renderTitleHeader`** L2418-L2472：依 plan §8.3 【異動後】完整替換。核心邏輯：取得 `abstractToolbar = document.getElementById('abstract-toolbar')`；null paper 時同時清空 abstractToolbar（`innerHTML = ''`, `display = 'none'`）；`parts` 只含雙語標題 h1/p；`if (abstractToolbar)` 區塊處理摘要渲染（isResume → hide；else → abstract → show/hide）；tag-pill 維持不變（直接 push 到 parts）；`el.innerHTML = parts.join('')`。**⑦ JS 更新 `deletePaper`** L2682-L2689：在 `document.getElementById('content-toolbar').style.display = 'none';` 後插入 3 行：`const abstractToolbar = document.getElementById('abstract-toolbar'); if (abstractToolbar) { abstractToolbar.innerHTML = ''; abstractToolbar.style.display = 'none'; }`。**⑧ 修改 `tests/test_bug_f5_p2_inconsistencies.py`** L70-L94：移除 `pat_title_meta` assertion（`#current-title .title-meta` 舊規則），替換為 `assert '#current-title .title-meta' not in STATIC_HTML`；將 `pat_abstract` 的 selector 從 `r'#current-title\s+details\.title-abstract\s*\{'` 改為 `r'#abstract-toolbar\s+details\.title-abstract\s*\{'`；同理 `pat_summary` 從 `#current-title` 改為 `#abstract-toolbar`。**⑨ 執行 pytest 全套驗收**：`./venv/bin/pytest tests/test_bug_b2_paper_header_meta.py tests/test_bug_f5_p2_inconsistencies.py tests/test_md_restore_processor.py -v` 全 passed；再跑 `./venv/bin/pytest tests/ -v` regression 全通過。 |

---

### Check — Conformance 驗收 + baton/ 收官歸檔（FE-AESTHETICS 結案）

| 維度 | 內容 |
|---|---|
| **影響範圍** | mv：`baton/plan` → `plans/` / `baton/tasks` → `tasks/` / `baton/C1執行` → `executions/` / `baton/C2執行` → `executions/`；修改：`TODO.md`（FE-AESTHETICS ✅ 結案） |
| **安全性** | 🟢 高 — 純文件整理，零業務代碼 |
| **可逆性** | 🟢 高 — 只有文件 mv，`git revert Check` 可回滾 |
| **驗收 grep 條件** | `ls .claude-logs/baton/` 期望：FE-AESTHETICS 相關暫存全清空；`grep "FE-AESTHETICS" .claude-logs/TODO.md` 期望：`✅` 狀態 |
| **依賴關係** | C1 + C2 全部 commit 完成且 baron 手動 commit 後 |
| **具體實作細節** | ①5 維度 Conformance 驗收：目標規格 / 測試計畫 / 不可動清單 / 提示詞歸檔 / msg.txt 草稿完整性。②TODO.md 結案：FE-AESTHETICS WIP 條目 → ✅ 完成表格（含 C1/C2 hash 回填）。③baton/ 4 份 mv 歸檔：plan → plans/ / tasks → tasks/ / C1執行 → executions/ / C2執行 → executions/。④Check 執行報告直寫 executions/。⑤寫 /tmp/FE-AESTHETICS_Check_msg.txt。 |

---

## §9 Open Questions

無。（plan §7 Open Questions 已在 v1.3 全部結案，方案 A 不含 affiliation 確認，列印隱藏規則補入）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-AESTHETICS 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 C1 → C2 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 FE-AESTHETICS 的 executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混合不同優先級文件；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | 任務計畫（plan）規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複計畫書中的設計脈絡，不重複 CLAUDE.md 中的全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-05-29)：初版拆分完成，依 plan v1.3 規格拆分 C1（後端）+ C2（前端）+ Check（收官）三個 commit
