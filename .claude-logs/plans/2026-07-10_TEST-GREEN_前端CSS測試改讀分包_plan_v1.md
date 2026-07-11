# TEST-GREEN 前端 CSS 測試改讀 static/css 分包 plan

> 目的：修復 15 個因 CSS 拆檔而失效（stale）的前端測試，使其斷言對象由已淨空 inline 樣式的 `static/index.html` 改為現行的 `static/css/*.css` 分包，恢復測試套件綠燈基線。純 `tests/` 改動，零業務代碼、零前端資產、零渲染行為變更。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：`FE-CSS-GOV C1`（`32e3a1a`，2026-07-09）將 `static/index.html` 內 1,354 行 inline `<style>` 等價搬遷至 `static/css/*.css` 七分包，但 6 個前端測試檔仍僅 `read_text('static/index.html')` 後以 regex grep CSS 規則。CSS 規則已不在 index.html（改在分包），15 個斷言因搜尋對象落空而失敗——**CSS 本身完全正確、被斷言的每一條規則都在 `static/css/` 中存活，純屬測試 stale**。全套件現況 `15 failed / 690 passed / 3 skipped`，紅燈基線阻擋一切後續任務的乾淨驗證（framework §7 衝突仲裁：E2E 100% 通過方可 commit）。
- **解法**：將 6 個測試檔的模組級「被搜尋源字串」由「僅 index.html」擴為「index.html + 依檔名排序串接的 `static/css/*.css`」之聯集（rendered CSS surface）。既有 regex 斷言不改邏輯、對聯集重跑即通過；對檔案再次搬移（如 THEME-DEDUP 後續）具韌性。
- **影響**：僅 `tests/` 6 個測試檔；無 runtime 影響、無業務代碼、無 `static/` 資產、無 DB / API / 配置變動。

---

## §2 目標規格

達成後的最終狀態必須滿足以下可檢驗條件：

1. **綠燈基線**：`pytest tests/ -q` 結果為 `705 passed, 3 skipped, 0 failed`（現況 690 passed + 修復 15 = 705；3 skipped 不變）。
2. **15 個 stale 測試全數轉綠**，且其**斷言邏輯（regex pattern 本體、正/負向語意）一字不改**——僅改「被搜尋的源字串」的組成。清單：
   - `test_bug_b2_paper_header_meta.py::test_b10_frontend_class_hook_not_in_print_media`
   - `test_bug_f1_frontend_micro_fix.py::{test_bug3_placeholder_has_newline_entity_and_pre_wrap, test_bug4_export_btn_collapse_important, test_bug5_content_max_w_token_in_root, test_bug5_content_toolbar_and_paper_content_use_token_and_themes_override}`
   - `test_bug_f3_modal_input_css.py::{test_bug7_modal_input_css_defined, test_bug7_modal_input_focus_uses_color_mix_cross_theme}`
   - `test_bug_f5_p2_inconsistencies.py::test_b1_main_scale_tokens_in_current_title`
   - `test_phase2_p2_3_hashtag_token_ui.py::{test_chat_input_has_empty_before_placeholder_css, test_chat_input_disabled_visual_contract_via_contenteditable_false, test_hashtag_autocomplete_anchored_to_container, test_hashtag_token_css_defined}`
   - `test_rag14_c1_css_and_filter.py::{test_msg_user_has_sticky_positioning, test_msg_user_msg_ai_have_stretch_width, test_qa_group_css_block_exists}`
3. **零回歸**：6 個檔案中**現行通過的 20 個測試維持通過**（聯集為既有 index.html 之超集，JS/HTML 斷言仍命中；負向「全域不存在」斷言之目標於 index.html 與 css 皆確認不存在，故仍成立——見 §3、§5）。
4. **源字串組成具決定性**：`static/css/*.css` 串接順序固定（依檔名字典序或明列序），不因 glob 順序不定而使測試 flaky。
5. **搜尋源正確性**：凡斷言 CSS 規則之測試，其源字串必含全部 7 個 `static/css/*.css`（`globals / layout / sidebar / content / chat / overlays / print`）；凡另讀 `themes/*.css` 或 `design/docs/*.md` 之既有斷言，其對應源保持原樣、不併入 CSS 聯集。

### §2.5 候選方案（Diverse Rollout）

本任務屬「測試修復方式選型」，語意分散候選 ≥2，列表擇優：

| 方案 | 核心做法 | trade-offs（開發難易 / 對既有代碼衝擊 / 未來擴充性） |
|---|---|---|
| **方案 A（選定）統一聯集源** | 各測試檔模組級源字串改為 `index.html + 排序串接之 static/css/*.css` 聯集，regex 斷言本體不動 | 易；衝擊面＝各檔頂部源定義 1 處；對未來 CSS 檔再搬移（THEME-DEDUP 等）免疫（不綁定規則所在檔） |
| **方案 B（否決）逐斷言指向具體檔** | 每條斷言指向規則現所在的具體 css 檔（modal-input→overlays.css、msg-user→chat.css…） | 難；衝擊面＝15 條斷言逐一改；脆——下次搬移再度全紅，且測試須「知道」規則落在哪檔（與治理白名單耦合） |

- **選定理由**：測試意圖是「此 CSS 規則存在於出廠 CSS 表面」，而非「規則位於某特定檔」。聯集源精確表達該意圖、churn 最小、對後續分包重排具韌性。
- **否決留痕**：方案 B 使每個測試與「規則歸屬哪個分包」硬耦合，違反測試應驗行為而非驗檔案佈局之原則；FE-CSS-GOV / THEME-DEDUP 已數度搬移 CSS，方案 B 將週期性重蹈紅燈，留底防未來重踩。

---

## §3 現況與證據

- **CSS 拆檔來源**：`FE-CSS-GOV C1`（`32e3a1a`，2026-07-09「File Split」）將 index.html inline `<style>` 等價搬遷至 `static/css/` 七分包並以 `<link>` 序載入。
- **6 個測試檔共同 stale 模式**：模組頂 `STATIC_HTML = (ROOT/'static'/'index.html').read_text(...)`，其後以 `re.compile(...).search(STATIC_HTML)` grep CSS 規則。CSS 已遷出 index.html → 15 斷言落空。
- **被斷言規則於 static/css 存活性（逐一核實、無一被刪）**：
  - `.modal-box .modal-input` / `:focus` `color-mix` → `static/css/overlays.css:109,125`
  - `--content-max-w` token（`:root` 預設 760px）→ `static/css/globals.css:59`；消費 → `content.css:25,79,149,178`
  - `#chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle)` → `static/css/layout.css:129`
  - `hashtag-token` / `hashtag-autocomplete` / `chat-input` → `static/css/chat.css`、`layout.css`
  - `msg-user` sticky / `msg-ai` / `qa-group` → `static/css/chat.css`
  - `.paper-header-meta { display: flex }`（b10 現為正向斷言）→ `static/css/content.css:170-171`
  - `#current-title .title-zh`（`--font-2xl` + `font-weight:700`）→ `static/css/content.css:61-63`；`#abstract-toolbar` → `content.css`
  - `@media print` class hook → `static/css/print.css`
- **負向斷言安全性**：`test_b1` 含 `'#current-title .title-meta' not in STATIC_HTML`（全域不存在型）；grep 於 index.html 與全部 css 皆零命中 → 聯集後仍成立（見 §3.1）。

### §3.1 grep 鋼鐵證據

```bash
# 全套件現況：15 failed 全落在 6 檔
$ ./venv/bin/python -m pytest tests/ -q | tail -3
15 failed, 690 passed, 3 skipped, 3 warnings in 51.24s

# 6 檔皆僅讀 index.html
$ grep -nE "read_text|STATIC_HTML =" tests/test_bug_f3_modal_input_css.py
15:STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')

# 被斷言 CSS 已遷至分包（樣本）
$ grep -rn "modal-box .modal-input" static/css/overlays.css
109:  .modal-box .modal-input,
125:  .modal-box .modal-input:focus,
$ grep -rn "chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle)" static/css/layout.css
129:  #chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle) {
$ grep -rn -A1 ".paper-header-meta {" static/css/content.css | head -2
170:  .paper-header-meta {
171-    display: flex;

# 負向斷言目標於 index.html + css 皆不存在（負向仍成立）
$ grep -rn "current-title .title-meta" static/index.html static/css/*.css
(空輸出，全域不存在)

# CSS 拆檔來源 commit
$ git log --oneline --diff-filter=A -- static/css/globals.css | tail -1
32e3a1a FE-Refactor: FE-CSS-GOV C1 — File Split
```

---

## §4 跨 Phase 接縫契約

無。本任務單一模組（`tests/`）內改動，無 Phase/模組間資料 handoff。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 聯集源使某負向「不存在」斷言誤失敗（CSS 檔重新引入被斷言應缺席之字串） | 🟢 低 | 現存唯一負向斷言（`test_b1` 之 `#current-title .title-meta`）目標於 index.html 與全部 css 皆確認零命中（§3.1）；緩解＝執行階段對 6 檔**全量重跑**（含現通過的 20 個），確保 20+15 全綠、零回歸 |
| 串接順序不定導致 flaky | 🟢 低 | §2 規格 #4 明定排序串接（字典序或明列），移除 glob 不定序 |
| 誤改斷言 regex 本體，遮蓋真實前端缺陷 | 🟡 中 | §2 規格 #2 硬限「斷言邏輯一字不改、僅改源字串組成」；不可動清單 §6 明列；驗證以 diff 核對 pattern 未變 |
| 誤動 6 檔中另讀 themes / design docs 的既有斷言源 | 🟢 低 | §2 規格 #5：僅 CSS-斷言測試併 css 聯集，themes/*.css 與 design/docs/*.md 源保持原樣 |
| 引入 conftest / 共用 helper 擴大範圍 | 🟢 低 | 本任務不建 conftest；聯集源於各檔就地定義（見 §9 OQ3），共用化屬 DEV-INFRA 另案 |

對齊 framework §4.1 #5。

---

## §6 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] 任一測試斷言的 **regex pattern 本體、正/負向語意、期望值**（僅允許改「被搜尋源字串」的組成）——防遮蓋真實前端缺陷。
- [ ] `static/index.html`、`static/css/*.css`、`static/themes/*.css` 等**一切前端資產**（本任務只改 `tests/`、不碰被測物）。
- [ ] 任何**業務代碼**（`web_server.py` / `paper_manager.py` / `pipeline_core.py` / `processor/*` / `pipelines/*` 等）。
- [ ] 6 檔中**現行通過的 20 個測試**之斷言與其專用源（themes / design docs 讀取）。
- [ ] `requirements.txt` / `.env` / `data/`（測試環境與依賴屬 DEV-INFRA 另案、見 §9 OQ2）。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流分類（前端相關、非緊急 → FE-Refactor） | `CLAUDE.md §2` / `ref/WORKFLOW_SOP.md §1.1` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 六階段觸發鏈 / 命名 / §7.2 豁免 | `ref/WORKFLOW_SOP.md §3 / §6 / §7.2` |
| E2E 100% 通過方可 commit（綠燈基線動因） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §7` |
| CSS 拆檔前置任務 | `FE-CSS-GOV`（`32e3a1a` 起） |

備註：FE-Refactor 名義必讀 SOP 為 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`，惟本任務不觸及渲染 / 效能表面（純測試源字串修正），無實質適用面。

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **六檔定向重跑（須全綠、20+15 零回歸）**：
  ```bash
  ./venv/bin/python -m pytest \
    tests/test_bug_b2_paper_header_meta.py \
    tests/test_bug_f1_frontend_micro_fix.py \
    tests/test_bug_f3_modal_input_css.py \
    tests/test_bug_f5_p2_inconsistencies.py \
    tests/test_phase2_p2_3_hashtag_token_ui.py \
    tests/test_rag14_c1_css_and_filter.py -v
  ```
- **全套件綠燈基線（目標 `705 passed, 3 skipped, 0 failed`）**：
  ```bash
  ./venv/bin/python -m pytest tests/ -q
  ```
- **斷言未被竄改核對**：對 6 檔 `git diff` 確認變更僅落在源字串定義，regex pattern 行零改。
- **預計新增測試**：無（本任務為既有測試修復，不新增測項）。

### §8.2 手動端到端（E2E）驗證流程

無 runtime / 前端行為變更 → **無需瀏覽器 E2E**。驗證等同 §8.1 pytest 綠燈 + diff 核對。

> §7.2 跨 Phase 整合測試：本任務單一模組、無 Phase handoff（§4 標「無」），依 WORKFLOW_SOP §7.2 不適用；於 §9 OQ 顯式登記豁免、待 baron 拍板。

---

## §9 Open Questions

> **拍板狀態（2026-07-10，baron）**：OQ1–OQ5 全數採推薦方案定案，無方向變更 → 本 plan 進入 execution-ready，可拆 tasks。實作層串接寫法（`sorted(css_dir.glob('*.css'))` 聯集）屬實作細節、依 §99.1 約束不入 plan，於 tasks / 執行報告定之。

| 開放問題 | 推薦方案（＝拍板結果） | 推薦理由 |
|---|---|---|
| OQ1：測試修復方式？聯集源 vs 逐斷言指向具體檔 | **方案 A 聯集源** | 測試驗「規則存在於出廠 CSS 表面」而非「位於某檔」；churn 最小、對後續分包重排具韌性（見 §2.5） |
| OQ2：是否於本任務併入 `requirements-dev.txt` / `pytest` 設定 / `numpy` 上界 pin？ | **不併、留 DEV-INFRA 另案** | 本任務範圍經 baron 明定為「純 tests/ 改讀 static/css」；依賴與測試基建屬不同工作流面向，混入將擴大不可動邊界 |
| OQ3：聯集源於各檔就地定義 vs 抽 `tests/conftest.py` 共用 helper？ | **各檔就地定義** | 不新建 conftest、範圍最小；共用化（含 DB/temp fixture 收斂）屬 DEV-INFRA 另案，避免本任務越界 |
| OQ4：是否同步更新測試 docstring / 註解中「inline `<style>`」「index.html」等已過時措辭？ | **是，最小幅** | 僅更正會誤導後人的措辭（如「主檔 :root」改指分包），不改任何斷言邏輯；防同類 stale 復發 |
| OQ5：§7.2 跨 Phase 整合測試豁免 | **顯式豁免** | 單一模組、無資料 handoff，符合 WORKFLOW_SOP §7.2 特例；待 baron 拍板 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 TEST-GREEN 前端 CSS 測試改讀 static/css 分包 的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 TEST-GREEN tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-07-10)：初版建立（PROJECT-REVIEW 審查衍生第一任務；蒐證 15 stale 測試根因＝FE-CSS-GOV C1 CSS 拆檔、6 檔僅讀 index.html；選定聯集源方案 A、§7.2 豁免）
- v1.1 (2026-07-10)：baron review 拍板——§9 OQ1–OQ5 全數採推薦方案定案、標記 execution-ready；技術複核確認聯集串接寫法（sorted glob·存在性檢查故順序無關）與 §2 規格 #4/#5 相容；實作 snippet 屬實作細節不入 plan（§99.1 約束）；規格本體 §1–§8 零變動
