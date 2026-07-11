# TEST-GREEN 前端CSS測試改讀分包 — Tasks

> 本文件為 TEST-GREEN 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md`（v1.1 execution-ready）產出，含 2 個 Commit（C1 + checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | 本案無任何新增檔案（純 tests/ 修改） |
| **修改檔案** | 6 個 | `tests/test_bug_b2_paper_header_meta.py` / `tests/test_bug_f1_frontend_micro_fix.py` / `tests/test_bug_f3_modal_input_css.py` / `tests/test_bug_f5_p2_inconsistencies.py` / `tests/test_phase2_p2_3_hashtag_token_ui.py` / `tests/test_rag14_c1_css_and_filter.py` |
| **目錄初始化** | 0 個 | 無 |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 2 個 | C1 → checkout |
| **baton 歸檔** | 1 次 | checkout 收官：`mv` baton plan + tasks + C1 執行報告 → `plans/` + `tasks/` + `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：`FE-CSS-GOV C1`（`32e3a1a`）將 index.html inline `<style>` 拆至 `static/css/*.css` 七分包，6 個測試檔仍僅讀 index.html grep CSS，致 15 個斷言 stale 失敗、全套件紅燈（690 passed / 15 failed / 3 skipped），阻擋後續任務乾淨驗證。
- **解法**：兩個原子 commit——
  - **C1 — CSS Surface Repoint（測試源改讀 CSS 分包聯集）**：於 6 檔各新增模組級「聯集源」（index.html + 依檔名排序串接之 `static/css/*.css`），僅將 15 個**當前失敗**斷言的頂層搜尋目標 repoint 至聯集源；現行通過的 20 個測試（含逐行掃描 / JS / 負向斷言）一律不動、續讀 index.html-only 源。
  - **checkout — 收官與成果歸檔**：baton plan + tasks + C1 執行報告一次性 `mv` 歸檔 + `git add`，產 checkout 執行報告（Conformance 五維度 + staged-set 自檢）。
- **影響範圍**：100% FE-Refactor（tests/ 純測試碼）；零業務代碼、零前端資產、零 runtime / 渲染行為變更。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `tests/test_bug_b2_paper_header_meta.py` | `STATIC_HTML=(ROOT/'static'/'index.html')`（L26） | `test_b10_frontend_class_hook_not_in_print_media` 斷言 `.paper-header-meta{display:flex}`（今在 `content.css:170`）失敗 |
| `tests/test_bug_f1_frontend_micro_fix.py` | `STATIC_HTML`（L19）+ `THEMES` 讀 themes（L21） | 4 測試失敗：bug3 pre-wrap / bug4 `#chat-panel.collapsed>...`（今 `layout.css:129`）/ bug5 `--content-max-w`（今 `globals.css:59`）/ bug5 toolbar+themes-override（token 半段今在 `content.css`） |
| `tests/test_bug_f3_modal_input_css.py` | `STATIC_HTML`（L15） | 2 測試失敗：`modal-input` 雙 selector + `:focus color-mix`（今 `overlays.css:109,125`） |
| `tests/test_bug_f5_p2_inconsistencies.py` | `STATIC_HTML`（L19）+ COMPONENTS/INTERACTION md | `test_b1_main_scale_tokens_in_current_title` 斷言 `#current-title .title-zh` 等（今 `content.css:61`）失敗 |
| `tests/test_phase2_p2_3_hashtag_token_ui.py` | `STATIC_HTML`（L24）+ COMPONENTS md | 4 測試失敗：chat-input empty-before / disabled contenteditable / hashtag-autocomplete anchored / hashtag-token defined（今 `chat.css` / `layout.css`） |
| `tests/test_rag14_c1_css_and_filter.py` | `_html()` helper 讀 index.html（L19-20） | 3 測試失敗：msg-user sticky / msg-user+msg-ai stretch / qa-group（今 `chat.css`） |

---

## §3 觀察問題

### 問題 #1：測試源與被測物脫節（stale）
- **證據**：`tests/test_bug_f3_modal_input_css.py#L15`（僅讀 index.html）vs `static/css/overlays.css:109`（規則實際所在）；拆檔 commit `32e3a1a`（FE-CSS-GOV C1 File Split）。
- **影響**：15 個斷言對已淨空 CSS 的 index.html grep → 全落空；全套件紅燈違反 framework §7「E2E 100% 通過方可 commit」，阻擋 SEC-SECRET 等後續任務的綠燈基線。被斷言的 15 條規則於 `static/css/` **無一被刪**（plan §3.1 逐一核實）→ 純測試 stale、非前端缺陷。

### 問題 #2：共用模組級源不可整體替換（零回歸約束）
- **證據**：`tests/test_bug_f5_p2_inconsistencies.py#L39,L107`（`for line in STATIC_HTML.split('\n')` 逐行掃描，屬**通過**的 `test_b1_no_legacy_font_tokens_in_css` / `test_b3_demo_bar_css_removed`）；`tests/test_rag14_c1_css_and_filter.py#L76`（`_html()` 用於**通過**的 JS 測試 `test_sendmessage_filters_hashtag_token_remove`）。
- **影響**：若直接把模組級 `STATIC_HTML` / `_html()` 改為聯集，將波及同檔 20 個通過測試（逐行掃描行數變動、掃描面擴大）→ 違反 plan §2 #3 零回歸。故 C1 必須**新增獨立聯集源**、只 repoint 失敗斷言。

---

## §4 設計方案

### §4.1 C1 — CSS Surface Repoint（測試源改讀 CSS 分包聯集）

**核心規則（對 6 檔一致套用）：**

1. **新增聯集源（每檔一處，模組級、import 期計算一次）**：
   - 一般檔（b2 / f1 / f3 / f5 / phase2）：於既有 `STATIC_HTML` 定義後新增
     ```python
     _CSS_DIR = ROOT / 'static' / 'css'
     CSS_SURFACE = STATIC_HTML + '\n' + '\n'.join(
         f.read_text(encoding='utf-8') for f in sorted(_CSS_DIR.glob('*.css'))
     )
     ```
   - rag14（helper 型）：新增並列 helper
     ```python
     def _css_surface() -> str:
         css_dir = STATIC_HTML.parent / 'css'
         css = '\n'.join(f.read_text(encoding='utf-8') for f in sorted(css_dir.glob('*.css')))
         return _html() + '\n' + css
     ```
   - `sorted(...glob('*.css'))` 保證決定性順序；存在性檢查（`re.search` / `in`）對串接順序不敏感（plan §2.5）。
2. **只 repoint 15 個失敗斷言的「頂層源搜尋目標」**：將該斷言中 `pat.search(STATIC_HTML)` / `content = _html()` 的**源**改為 `CSS_SURFACE` / `_css_surface()`。body-scoped 子斷言（如 f3 `body=m.group(1)` 後之 border-color/color-mix/rgba 檢查）自動繼承、無需個別改。
3. **一律不動**：斷言的 `re.compile` pattern 本體、正/負向語意、期望值、count 門檻；同檔所有**通過**的測試（逐行掃描 / JS / markdown `md` / themes-override `THEMES[...]` / 全域負向）續讀原 `STATIC_HTML` / `_html()`。
4. **OQ4 最小幅措辭校正（選作、同 commit）**：僅更正 docstring / 註解中會誤導的舊敘述（如「主檔 :root」→「分包 css」、「inline `<style>`」字樣），**不改任何斷言與 pattern**。

**逐檔 repoint 清單（15 斷言）：**

| 檔 | 失敗測試（repoint 頂層源→聯集） | 負向安全性 |
|---|---|---|
| b2 | `test_b10_frontend_class_hook_not_in_print_media`（1 正向） | 無負向 |
| f1 | `test_bug3_placeholder_has_newline_entity_and_pre_wrap` / `test_bug4_export_btn_collapse_important` / `test_bug5_content_max_w_token_in_root` / `test_bug5_content_toolbar_and_paper_content_use_token_and_themes_override`（後者 4 個 `search(STATIC_HTML)` 全 repoint；主題迴圈 `THEMES[...]` 不動） | f1 無涉聯集之負向 |
| f3 | `test_bug7_modal_input_css_defined` / `test_bug7_modal_input_focus_uses_color_mix_cross_theme`（各 repoint 頂層 `pat.search`；`rgba not in body` 為 body-scoped、安全） | body-scoped、安全 |
| f5 | `test_b1_main_scale_tokens_in_current_title`（repoint 3 正向 regex：title-zh / title-en / abstract；`'#current-title .title-meta' not in STATIC_HTML` 為全域負向、title-meta 於 css 亦不存在、留 STATIC_HTML 不動） | 全域負向、css 無命中、安全 |
| phase2 | `test_chat_input_has_empty_before_placeholder_css` / `test_chat_input_disabled_visual_contract_via_contenteditable_false` / `test_hashtag_autocomplete_anchored_to_container` / `test_hashtag_token_css_defined` | 該 4 測試 CSS 存在性斷言、無涉聯集之破壞性負向 |
| rag14 | `test_msg_user_has_sticky_positioning` / `test_msg_user_msg_ai_have_stretch_width` / `test_qa_group_css_block_exists`（`content=_css_surface()`；`align-self: flex-end/flex-start not in content` 已驗 css 不存在、安全） | flex-end/flex-start 於 css 不存在、安全 |

### §4.2 checkout — 收官與成果歸檔

- `mv` baton 之 plan（`2026-07-10_TEST-GREEN_..._plan_v1.md`）→ `plans/`、tasks（本檔）→ `tasks/`、C1 執行報告 → `executions/`；逐檔 `git add`。
- 產 `executions/2026-07-11_TEST-GREEN_checkout_執行.md`（CHECKOUT-GUARD 鐵律）：含 Conformance 五維度驗收 + `git diff --cached --name-only` staged-set 自檢實貼 + baton 歸檔確認 + §8 一行 commit 指令。
- 無任何測試碼改動；不 `git add .`／`-A`／`<目錄>`，逐檔顯式列名。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 直接替換共用 `STATIC_HTML` 波及 20 個通過測試（逐行掃描 / JS） | 🟢 低 | §4.1 硬性規定「新增獨立聯集源、只 repoint 失敗斷言」；通過測試續讀原源；C1 後對 6 檔全量重跑驗零回歸（§6.1） |
| repoint 後失敗測試內之負向斷言誤破 | 🟢 低 | 逐一預驗（§4.1 表）：rag14 flex-end/flex-start 於 css 不存在、f5 title-meta 留原源、f3 rgba 為 body-scoped → 全安全 |
| 誤改斷言 regex 本體、遮蓋真前端缺陷 | 🟡 中 | §7 不可動；驗收以 `git diff` 核對 pattern 行零改（§6.1 步驟 3） |
| 串接順序不定致 flaky | 🟢 低 | `sorted(glob)` 固定序；存在性檢查對順序不敏感 |
| 誤動 themes / design-docs 既有源 | 🟢 低 | §4.1 #3 明列 `THEMES[...]` / COMPONENTS_MD / INTERACTION_MD 不動 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# 1) 六檔定向重跑：須 35 passed（20 原通過 + 15 修復）、0 failed
./venv/bin/python -m pytest \
  tests/test_bug_b2_paper_header_meta.py \
  tests/test_bug_f1_frontend_micro_fix.py \
  tests/test_bug_f3_modal_input_css.py \
  tests/test_bug_f5_p2_inconsistencies.py \
  tests/test_phase2_p2_3_hashtag_token_ui.py \
  tests/test_rag14_c1_css_and_filter.py -q
# 期望結尾：35 passed（0 failed）

# 2) 全套件綠燈基線：705 passed / 3 skipped / 0 failed
./venv/bin/python -m pytest tests/ -q
# 期望：705 passed, 3 skipped

# 3) 斷言未被竄改核對：diff 僅落在源字串定義/repoint 與註解，pattern（re.compile 內文）零改
git diff -- tests/ | grep -E "^\+" | grep -E "re\.compile|r'|r\"" | head
# 期望：無「新增/改動 pattern 內文」之行（僅源變數與 .search(...) 目標變動）

# 4) 聯集源已加入六檔
grep -rl "CSS_SURFACE\|_css_surface" tests/ | wc -l   # 期望：6
```

### §6.2 checkout 驗收

```bash
# baton 已清空（僅 README）
ls .claude-logs/baton/    # 期望：僅 README.md

# 歸檔落位
ls .claude-logs/plans/2026-07-10_TEST-GREEN_*_plan_v1.md \
   .claude-logs/tasks/2026-07-11_TEST-GREEN_*_tasks.md \
   .claude-logs/executions/2026-07-11_TEST-GREEN_*_執行.md

# staged 白名單自檢（checkout 報告內實貼）
git diff --cached --name-only
```

---

## §7 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] **業務代碼**：`web_server.py` / `paper_manager.py` / `pipeline_core.py` / `processor/*` / `pipelines/*` 等 — 100% 不動。
- [ ] **前端資產**：`static/index.html` / `static/css/*.css` / `static/themes/*.css` 等一切 `static/**` — 只讀不改（本任務僅改 tests/）。
- [ ] 任一測試斷言的 **`re.compile` pattern 本體、正/負向語意、`count` 門檻、期望值** — 僅允許改「被搜尋源字串」的組成與斷言的源目標。
- [ ] 6 檔中**現行通過的 20 個測試**及其專用源讀取（`THEMES` / `COMPONENTS_MD` / `INTERACTION_MD` / 逐行掃描之 `STATIC_HTML` / rag14 JS 測試之 `_html()`）。
- [ ] `requirements.txt` / `.env` / `data/` / 任何依賴或 pytest 設定（屬 DEV-INFRA 另案、plan §9 OQ2）。
- [ ] **主 repo 授權範圍外檔案** — 嚴禁讀寫（僅 `tests/` + baton 暫存 + TODO/INDEX 狀態）。

---

## §8 推薦 Commit 拆分

### C1 — CSS Surface Repoint（測試源改讀 CSS 分包聯集）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_bug_b2_paper_header_meta.py` / `tests/test_bug_f1_frontend_micro_fix.py` / `tests/test_bug_f3_modal_input_css.py` / `tests/test_bug_f5_p2_inconsistencies.py` / `tests/test_phase2_p2_3_hashtag_token_ui.py` / `tests/test_rag14_c1_css_and_filter.py`（＋各檔 `.bak` 備份）；baton C1 執行報告**嚴禁**列入 git 追蹤、待 checkout 歸檔 |
| **安全性** | 🟢 高 — 純測試碼、零 runtime、零業務/前端資產；只擴源不改斷言邏輯 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；六檔各留 `.bak` |
| **驗收 grep 條件** | 見 §6.1（六檔 35 passed / 全套件 705 passed / diff 無 pattern 改動 / 6 檔含聯集源） |
| **依賴關係** | 無前置（THEME-DEDUP 已完成、CSS 分包已定位；本 commit 為 checkout 前置） |
| **具體實作細節** | 依 §4.1 對 6 檔逐一：① 於 `STATIC_HTML` 定義後（rag14 於 `_html()` 後）新增聯集源 `CSS_SURFACE`（rag14 為 `_css_surface()`），寫法：`STATIC_HTML + '\n' + '\n'.join(f.read_text(encoding='utf-8') for f in sorted((ROOT/'static'/'css').glob('*.css')))`；② 依 §4.1 逐檔清單，將 15 個失敗測試的頂層源搜尋目標由 `STATIC_HTML`/`_html()` 改為 `CSS_SURFACE`/`_css_surface()`（f1 bug5-themes 測試僅改 4 個 `search(STATIC_HTML)`、`THEMES` 迴圈不動；f5 test_b1 僅改 3 正向 regex 之源、`title-meta not in STATIC_HTML` 負向不動；f3 各改頂層 `pat.search`、body-scoped 子斷言自動繼承）；③ 選作 OQ4 最小幅校正誤導性 docstring/註解，不碰 pattern；④ 逐檔先產 `.bak`；⑤ 跑 §6.1 驗 35 + 705 passed |

### checkout — 收官與成果歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：`.claude-logs/plans/2026-07-10_TEST-GREEN_前端CSS測試改讀分包_plan_v1.md`、`.claude-logs/tasks/2026-07-11_TEST-GREEN_前端CSS測試改讀分包_tasks.md`、`.claude-logs/executions/2026-07-11_TEST-GREEN_C1_執行.md`、`.claude-logs/executions/2026-07-11_TEST-GREEN_checkout_執行.md`；狀態：`TODO.md`（🟡→✅ 雙層結案）、`prompts/INDEX.md`（已於 tasks 階段登記） |
| **安全性** | 🟢 高 — 純文件搬移 + 狀態更新、零代碼 |
| **可逆性** | 🟢 高 — 文件層 `git revert` / `mv` 復位 |
| **驗收 grep 條件** | 見 §6.2（baton 僅存 README / 四文件落位 / `git diff --cached --name-only` 白名單自檢） |
| **依賴關係** | 前置 C1 綠燈（705 passed） |
| **具體實作細節** | ① 產 `executions/2026-07-11_TEST-GREEN_checkout_執行.md`（Conformance 五維度：plan §2 目標達成 / 不可動清單逐項打勾 / staged-set 自檢實貼 / baton 歸檔確認 / §7.2 純測試無 handoff 顯式豁免）；② `mv` baton plan/tasks/C1 報告至正式目錄（標準 `mv`、**禁 `git mv`**）；③ 逐檔顯式 `git add`（plan + tasks + 兩份執行報告 + 6 個 `.bak` + `TODO.md` + `prompts/INDEX.md` + `prompts/2026-07-11_TEST-GREEN_Tasks_提示詞.md`），**禁 `git add .`/`-A`/`<目錄>`**；④ commit 前 `git diff --cached --name-only` 自檢＝宣告清單、多一少一即停；⑤ 更新 TODO.md 雙層結案（active 移除 + `archive/TODO_done_archive.md` 追加表格 + 索引一行）；⑥ 附一行 commit 指令（baron 手動執行） |

---

## §9 Open Questions

無。（plan v1.1 §9 OQ1–OQ5 已於 baron review 全數拍板結案：方案 A 聯集源 / DEV-INFRA 另案 / 各檔就地定義 / OQ4 最小幅校正 / §7.2 顯式豁免。）

> 附記（非 OQ、供未來 backlog）：`test_b1_no_legacy_font_tokens_in_css`、`test_b3_demo_bar_css_removed` 等現「掃 index.html（已無 CSS）而平凡通過」之測試，其守備效力已因拆檔而空洞化，但**不在本 15 個失敗清單、且現為綠燈** → 本任務不觸及（避免 scope creep）；提升其效力屬另案。

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 TEST-GREEN 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 TEST-GREEN executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼與前端資產；嚴禁改斷言 pattern 本體；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-07-11)：初版拆分完成（依 plan v1.1；2 commit＝C1 CSS Surface Repoint〔6 檔新增獨立聯集源、只 repoint 15 失敗斷言、零回歸〕+ checkout；蒐證逐檔 repoint 清單與負向斷言安全性；§7.2 純測試豁免）
