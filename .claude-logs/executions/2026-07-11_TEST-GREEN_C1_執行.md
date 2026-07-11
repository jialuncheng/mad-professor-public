# TEST-GREEN C1 — CSS Surface Repoint（測試源改讀 CSS 分包聯集）執行報告

---

**任務代號**：TEST-GREEN C1
**執行日期**：2026-07-11
**依據規劃**：`.claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md`（v1.1 execution-ready）
**次級參考**：`.claude-logs/baton/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md`
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C1)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 THEME-DEDUP C4（`3cad5f0`）之後、THEME-DEDUP checkout 已備好待 baron commit。全套件紅燈基線 `690 passed / 15 failed / 3 skipped`——15 個失敗全落在 6 個前端測試檔，根因為 FE-CSS-GOV C1（`32e3a1a`）將 index.html inline `<style>` 拆至 `static/css/*.css` 七分包，測試仍僅讀 index.html grep CSS。執行前六檔定向重跑實測：`15 failed, 20 passed`（與 tasks §2 完全一致）。
- **完成狀態**：6 個測試檔各新增獨立 CSS 分包聯集源（`CSS_SURFACE` / `_css_surface()`），15 個 stale 斷言之頂層搜尋目標 repoint 至聯集源；斷言 pattern 本體、正/負向語意、期望值、count 門檻零改寫；現行通過的 20 個測試續讀原 `STATIC_HTML` / `_html()` 零回歸。六檔定向重跑 **35 passed / 0 failed**、全套件 **705 passed / 3 skipped / 0 failed**（plan §2 #1 目標達成）。**業務代碼與前端資產零改動**（僅 tests/ 6 檔 + TODO/INDEX 狀態文件）。
- **與全局策略對齊**：本 commit conditioned on plan §2 #1（705 綠燈基線）+ #2（15 stale 全轉綠、斷言邏輯一字不改）+ #3（20 通過測試零回歸）+ #4（sorted glob 決定性順序）+ #5（聯集含全部 7 分包、themes/design-docs 源原樣）；無偏離。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | CSS Surface Repoint——6 測試檔新增 CSS 分包聯集源、repoint 15 個 stale 斷言、零回歸 | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `tests/test_bug_b2_paper_header_meta.py` | `.claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_b2_paper_header_meta.py.bak` | 新增 `CSS_SURFACE` 聯集源 + repoint 1 測試（1 處 search） |
| 修改 | `tests/test_bug_f1_frontend_micro_fix.py` | `.claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_f1_frontend_micro_fix.py.bak` | 新增 `CSS_SURFACE` + repoint 4 測試（10 處 search）；`THEMES` 迴圈不動 |
| 修改 | `tests/test_bug_f3_modal_input_css.py` | `.claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_f3_modal_input_css.py.bak` | 新增 `CSS_SURFACE` + repoint 2 測試（3 處頂層 search；body-scoped 子斷言自動繼承） |
| 修改 | `tests/test_bug_f5_p2_inconsistencies.py` | `.claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_f5_p2_inconsistencies.py.bak` | 新增 `CSS_SURFACE` + repoint 1 測試（4 正向 search；`title-meta` 全域負向留原源） |
| 修改 | `tests/test_phase2_p2_3_hashtag_token_ui.py` | `.claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_phase2_p2_3_hashtag_token_ui.py.bak` | 新增 `CSS_SURFACE` + repoint 4 測試（9 處 search） |
| 修改 | `tests/test_rag14_c1_css_and_filter.py` | `.claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_rag14_c1_css_and_filter.py.bak` | 新增 `_css_surface()` 並列 helper + repoint 3 測試；JS 測試續用 `_html()`；模組 docstring OQ4 最小幅校正 |
| 修改 | `.claude-logs/TODO.md` | —（狀態文件，依 run 流程免備份） | TEST-GREEN C1 → ✅、checkout → 🟡 WIP |
| 修改 | `.claude-logs/prompts/INDEX.md` | — | 補登 C1 run 提示詞條目 + 新增 TEST-GREEN 分類 |
| 新建 | `.claude-logs/prompts/2026-07-11_TEST-GREEN_C1_run_提示詞.md` | — | 本階段提示詞歸檔（§1.2 先歸檔後執行） |
| 新建 | `.claude-logs/baton/2026-07-11_TEST-GREEN_C1_執行.md` | — | 本報告；**暫存 baton、本階段嚴禁 git add**、checkout 歸檔 |

> ⚠️ **備份欄位強制注意**：上列 6 個 `.bak` 備份檔已全數列入 §8 `git add` 清單。
> ⚠️ **deviation 標註（備份路徑）**：run 提示詞備份指令寫 `archive/<檔名>.bak`（repo 根層），惟 repo 根層 `archive/` **不存在**（`ls` 實證 `No such file or directory`）；本專案 `.bak` 既有慣例一律落 `.claude-logs/archive/`（THEME-DEDUP / FE-PERF-2 等全部先例）。故本次 6 份 `.bak` 依慣例落 `.claude-logs/archive/`、命名格式與提示詞完全一致（`2026-07-11_TEST-GREEN_C1_<檔名>.bak`），避免新開頂層目錄污染 repo 結構。§8 git add 清單已同步為實際路徑。

---

## §4 修法說明

### §4.1 聯集源計算方式（6 檔一致）

- **一般檔（b2 / f1 / f3 / f5 / phase2）**：於既有 `STATIC_HTML` 定義後新增模組級聯集源（import 期計算一次）：
  ```python
  # TEST-GREEN C1：CSS 已由 FE-CSS-GOV C1 拆至 static/css/ 分包，CSS 存在性斷言改讀聯集源
  _CSS_DIR = ROOT / 'static' / 'css'
  CSS_SURFACE = STATIC_HTML + '\n' + '\n'.join(
      f.read_text(encoding='utf-8') for f in sorted(_CSS_DIR.glob('*.css'))
  )
  ```
- **rag14（helper 型）**：新增並列 helper（`STATIC_HTML` 於該檔為 `Path`）：
  ```python
  def _css_surface() -> str:
      css_dir = STATIC_HTML.parent / 'css'
      css = '\n'.join(f.read_text(encoding='utf-8') for f in sorted(css_dir.glob('*.css')))
      return _html() + '\n' + css
  ```
- `sorted(glob)` 保證決定性串接順序（chat / content / globals / layout / overlays / print / sidebar 七分包，`ls static/css/` 實證 7 檔齊備）；存在性檢查對順序不敏感（plan §2 #4）。
- 聯集為 index.html 之**超集**：失敗測試內混雜的 HTML/JS 斷言（f1 bug3 之 data-placeholder 與 JS 字面值）repoint 後仍命中、語意不變。

### §4.2 逐檔 repoint 行號（15 測試、修改後行號）

| 檔 | repoint 測試 | 聯集源定義行 | repoint 行號 |
|---|---|---|---|
| b2 | `test_b10_frontend_class_hook_not_in_print_media` | L28-31 | L178 |
| f1 | `test_bug3_placeholder…pre_wrap` / `test_bug4_export_btn…` / `test_bug5_content_max_w…` / `test_bug5_content_toolbar…themes_override` | L21-24 | L60 / L68 / L77 / L85（bug3 四處）、L98（bug4）、L112（bug5-root）、L123 / L130 / L137 / L144（bug5-toolbar 四處） |
| f3 | `test_bug7_modal_input_css_defined` / `test_bug7_modal_input_focus_uses_color_mix_cross_theme` | L17-20 | L31 / L42（defined 兩處頂層）、L67（focus 頂層） |
| f5 | `test_b1_main_scale_tokens_in_current_title` | L21-24 | L64 / L73 / L85 / L94（4 正向） |
| phase2 | `test_chat_input_has_empty_before…` / `test_chat_input_disabled…` / `test_hashtag_autocomplete_anchored…` / `test_hashtag_token_css_defined` | L26-29 | L74 / L79（empty-before 兩處）、L93（disabled）、L152 / L156 / L160（anchored 三處）、L169 / L170 / L176（token 三處） |
| rag14 | `test_msg_user_has_sticky_positioning` / `test_msg_user_msg_ai_have_stretch_width` / `test_qa_group_css_block_exists` | L24-29（helper） | L36 / L47 / L66（`content = _css_surface()`） |

### §4.3 f5 / rag14 / f3 負向斷言安全核查（執行期 grep 實證）

```bash
$ grep -rn "align-self: flex-end\|align-self: flex-start" static/css/ static/index.html
（空輸出——rag14 兩條負向於聯集仍成立）
$ grep -rn "current-title .title-meta" static/css/ static/index.html
（空輸出——f5 全域負向即使入聯集亦安全；仍依 tasks §4.1 留 STATIC_HTML 原源不動）
$ grep -c "align-self: stretch" static/css/chat.css
2   # rag14 count >= 2 正向於聯集滿足
```

- **f5**：`'#current-title .title-meta' not in STATIC_HTML` 為全域負向，依 tasks 明文**留原源不動**（css 亦零命中、雙保險）。
- **rag14**：`test_msg_user_msg_ai_have_stretch_width` 之 `flex-end` / `flex-start` 負向隨 `content = _css_surface()` 擴面至聯集，上列 grep 實證 css 全域零命中 → 仍成立。
- **f3**：`rgba(59, 130, 246` 負向為 **body-scoped**（`m.group(1)` 取 focus rule body），repoint 僅換頂層 search 源、body 範圍語意不變。
- **phase2**：`test_chat_input_no_residual_textarea_value_refs`（負向 JS 掃描）屬通過測試、**未動**、續讀 `STATIC_HTML`。

### §4.4 OQ4 最小幅措辭校正（不碰任何斷言 pattern）

- `test_bug_f1_frontend_micro_fix.py::test_bug5_content_max_w_token_in_root` docstring：「主檔 :root」→「出廠 CSS（分包 globals.css）:root」+ 註解同步。
- `test_rag14_c1_css_and_filter.py` 模組 docstring：「讀 static/index.html」→ 標明 CSS 測試讀聯集、JS 測試讀 index.html。
- 各檔聯集源定義處統一加一行「TEST-GREEN C1」註解說明改讀緣由。

---

## §5 測試結果

### §5.1 本地改動狀態確認

```bash
$ git status -s | grep -v "^??"
 M .claude-logs/TODO.md
 M .claude-logs/archive/TODO_done_archive.md      # ← THEME-DEDUP checkout 遺留（非本任務）
 M .claude-logs/executions/2026-07-09_FE-CSS-GOV_checkout_執行.md  # ← 同上（非本任務）
 M .claude-logs/prompts/INDEX.md
 M tests/test_bug_b2_paper_header_meta.py
 M tests/test_bug_f1_frontend_micro_fix.py
 M tests/test_bug_f3_modal_input_css.py
 M tests/test_bug_f5_p2_inconsistencies.py
 M tests/test_phase2_p2_3_hashtag_token_ui.py
 M tests/test_rag14_c1_css_and_filter.py
```

> 註：`TODO_done_archive.md` 與 `FE-CSS-GOV_checkout_執行.md` 為 session 啟動前既有之 THEME-DEDUP checkout 未 commit 改動、本任務零觸碰、**不在 §8 git add 清單**。

### §5.2 驗收腳本實際輸出（tasks §6.1 四步）

```bash
# 0) 執行前基準（六檔定向）
$ ./venv/bin/python -m pytest tests/test_bug_b2_paper_header_meta.py tests/test_bug_f1_frontend_micro_fix.py \
    tests/test_bug_f3_modal_input_css.py tests/test_bug_f5_p2_inconsistencies.py \
    tests/test_phase2_p2_3_hashtag_token_ui.py tests/test_rag14_c1_css_and_filter.py -q
15 failed, 20 passed in 0.07s

# 1) 修改後六檔定向重跑
$ ./venv/bin/python -m pytest <同上六檔> -q
35 passed in 0.07s

# 2) 全套件綠燈基線
$ ./venv/bin/python -m pytest tests/ -q
705 passed, 3 skipped, 3 warnings in 84.09s (0:01:24)

# 3) 斷言未被竄改核對（新增行含 re.compile / raw-string pattern 之行數）
$ git diff -- tests/ | grep -E "^\+" | grep -E "re\.compile|r'|r\"" | head
（空輸出——無任何新增/改動之 pattern 行）
$ git diff -- tests/ | grep -E "^-" | grep -cE "re\.compile"
0（零 re.compile 行被移除）

# 4) 聯集源已加入六檔
$ grep -rl "CSS_SURFACE\|_css_surface" tests/*.py | wc -l
6
```

diff stat：

```bash
$ git diff --stat -- tests/
 tests/test_bug_b2_paper_header_meta.py     |  7 ++++++-
 tests/test_bug_f1_frontend_micro_fix.py    | 29 +++++++++++++++++------------
 tests/test_bug_f3_modal_input_css.py       | 11 ++++++++---
 tests/test_bug_f5_p2_inconsistencies.py    | 13 +++++++++----
 tests/test_phase2_p2_3_hashtag_token_ui.py | 23 ++++++++++++++---------
 tests/test_rag14_c1_css_and_filter.py      | 17 +++++++++++++----
 6 files changed, 67 insertions(+), 33 deletions(-)
```

### §5.3 SOP 一致性核查

FE-Refactor 工作流、純 tests/ 測試碼改動、無 `.py` 業務代碼改動，logging / database 核查不適用（合規）。FE SOP（`sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`）已依必讀規範完整閱讀；本任務零前端資產改動、無 runtime / 渲染表面 → §2 紅線與 §3 陷阱無實質適用面（plan §7 備註已預告）、§4 檢查表全數 N/A。

### §5.4 TODO hash 自癒掃描結果

`grep "待回填" TODO.md` 唯一命中＝THEME-DEDUP 索引行「checkout 待回填」；`git log` 實查最新 commit 為 THEME-DEDUP C4（`3cad5f0`）、checkout commit **尚未 ship**（工作區仍有其未 commit 改動）→ 無可回填之真實 hash、佔位符保留待其 ship 後自癒。本次自癒回填數：0（無假 hash、不虛構）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| 業務代碼（`web_server.py` / `paper_manager.py` / `pipeline_core.py` / `processor/*` / `pipelines/*`） | [x] ✅ 未觸碰 |
| 前端資產（`static/index.html` / `static/css/*.css` / `static/themes/*.css` 等 `static/**`） | [x] ✅ 只讀未改（`git status` 零 static 條目） |
| 斷言 `re.compile` pattern 本體 / 正負向語意 / count 門檻 / 期望值 | [x] ✅ 零改寫（§5.2 步驟 3 實證） |
| 6 檔現行通過之 20 測試及其專用源（`THEMES` / `COMPONENTS_MD` / `INTERACTION_MD` / 逐行掃描 `STATIC_HTML` / rag14 JS `_html()`） | [x] ✅ 未動、35 passed 含 20 原通過零回歸 |
| `requirements.txt` / `.env` / `data/` / pytest 設定 | [x] ✅ 未觸碰 |
| baton/ 過程文件（plan / tasks / 本報告）不入本階段版控 | [x] ✅ 未 git add、§8 清單不含 |

---

## §自評（策略對齊自我審查）

- **(a) 越界?**：否。變更僅落 6 個授權測試檔 + TODO/INDEX 狀態文件 + 提示詞歸檔；唯一 deviation＝`.bak` 落 `.claude-logs/archive/`（非提示詞字面 `archive/`），已於 §3 標註理由（根層 archive/ 不存在、循全部既有先例）。
- **(b) 無關 / 違規?**：否。OQ4 docstring 校正屬 plan 明文選作項、最小幅；無冗餘代碼。
- **(c) 推進哪個 U-N?**：plan §2 #1–#5 全數——705 綠燈基線恢復（#1）、15 stale 全轉綠且 pattern 零改（#2）、20 通過零回歸（#3）、sorted glob 決定性（#4）、聯集含 7 分包且 themes/docs 源原樣（#5）。

無 Flagged 項。

---

## §7 銜接

- **baton/ 狀態**：本報告暫存 `baton/`；plan（`2026-07-10_..._plan_v1.md`）與 tasks（`2026-07-11_..._tasks.md`）同駐 baton；**三者均待 checkout 階段一次性 `mv` + `git add` 歸檔**（plans/ + tasks/ + executions/）。
- **下一步**：tasks §4.2 **checkout — 收官與成果歸檔**（Conformance 五維度 + staged-set 自檢 + TODO 雙層結案 + baton 歸檔；待 baron 確認 C1 並另行下達提示詞）。
- **消化歸檔之 baton 檔**：無（本階段零歸檔動作，依 WORKFLOW_SOP §3 baton 暫存鐵律）。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列出，落 .claude-logs/archive/、見 deviation 標註）

# 2. git add 清單（⚠️ 逐檔顯式列名，嚴禁 `git add .` / `-A` / `<目錄>`；嚴禁將 baton/ 暫存檔加入；
#    commit 前以 `git diff --cached --name-only` 自檢＝本清單）
git add tests/test_bug_b2_paper_header_meta.py
git add tests/test_bug_f1_frontend_micro_fix.py
git add tests/test_bug_f3_modal_input_css.py
git add tests/test_bug_f5_p2_inconsistencies.py
git add tests/test_phase2_p2_3_hashtag_token_ui.py
git add tests/test_rag14_c1_css_and_filter.py
git add .claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_b2_paper_header_meta.py.bak
git add .claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_f1_frontend_micro_fix.py.bak
git add .claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_f3_modal_input_css.py.bak
git add .claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_bug_f5_p2_inconsistencies.py.bak
git add .claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_phase2_p2_3_hashtag_token_ui.py.bak
git add .claude-logs/archive/2026-07-11_TEST-GREEN_C1_test_rag14_c1_css_and_filter.py.bak

# 3. commit message draft（已寫入 /tmp/TEST-GREEN_C1_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/TEST-GREEN_C1_msg.txt
```

### §8.2 commit message 草稿

（已寫入 `/tmp/TEST-GREEN_C1_msg.txt`，以下為完整展示）

```
FE-Refactor: TEST-GREEN C1 — CSS Surface Repoint

為 6 個測試檔案新增 CSS 聯集源，並將 15 個 stale 的 CSS 存在性斷言改讀此聯集
以修復測試紅燈。現行通過的 20 個測試續讀原 index.html 源以確保零回歸。

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

> 備註：TODO.md / prompts/INDEX.md / 本次 run 提示詞歸檔檔之 git add 時機依既有慣例由 checkout 階段一併納入白名單；若 baron 欲隨 C1 一起 commit，可自行追加（`git add .claude-logs/TODO.md .claude-logs/prompts/INDEX.md .claude-logs/prompts/2026-07-11_TEST-GREEN_C1_run_提示詞.md`）。⚠️ 注意工作區另有 THEME-DEDUP checkout 未 commit 改動（`TODO_done_archive.md` / `FE-CSS-GOV_checkout_執行.md` / executions 未追蹤檔），**不得混入本 commit**。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 TEST-GREEN C1 的測試碼變更與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；checkout 收官時 Conformance 核對原始 plan；核對後移動歸檔至 executions/ 併入版控 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | checkout 收官提示詞 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存於 baton/，checkout 收官前不入版控 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為本 Commit 執行唯一源，不重複 tasks 六維度細節與 plan 全局規格 |

### §99.2 Revision 歷程

- v1 (2026-07-11)：C1 執行完畢產出報告（六檔 35 passed / 全套件 705 passed, 3 skipped, 0 failed；pattern 零改實證；`.bak` 路徑 deviation 標註）
