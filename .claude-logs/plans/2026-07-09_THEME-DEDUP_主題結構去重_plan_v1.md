# THEME-DEDUP 主題規格凍結與結構去重 plan

> 凍結主題完整規格（19 必備 token / 16 必備選擇器〔統一骨架·裝飾層槽可空〕/ 屬性白名單 / 進階 chrome 覆寫層），將 `static/themes/` 全 9 支主題（4 內建 + 5 上傳）正規化至此規格（先 baseline commit 原樣 → 結構去重 + 死碼清除 + token 補登），並改寫 theme-guide 為目錄級權威凍結規格源。FE-CSS-GOV C3 外溢之結構續集升級為主題規格治理。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：主題規格未凍結——(1) **9 支主題**（4 內建 + 5 上傳〔apple/corbusier/fuller/google/gropius·baron 已 copy 入 `static/themes/`〕）殘留**非白名單結構屬性**（padding/margin/border-width 等）；(2) 5 支上傳全帶 `#demo-bar` 死碼（拷貝自 C3 前舊樣板）+ 全缺 `--content-max-w`；(3) 白名單內屬性集跨主題分歧 + `text-align` 未登記；(4) 無權威凍結規格 → 未來新主題必再現不一致（上傳 5 支即活證）。
- **解法**：**凍結主題完整規格**（§2.2：19 必備 token + 16 必備選擇器〔含裝飾層槽·全主題必在可空〕+ 屬性白名單 + 進階 chrome 覆寫層 + 統一檔案骨架 + 禁止清單）→ **9 支主題全數正規化**（baron 拍板一併處理；先 commit 上傳原樣為 baseline、再正規化）→ **改寫 `theme-guide.md` 為權威凍結規格源（目錄級）** + `css-architecture` 對照登記。視覺 100% 等價（含保留 apple/google chrome re-skin 設計本體）。
- **影響**：`static/themes/*.css` **全 9 支**（正規化·目錄級）+ `static/css/content.css`（承接共用結構）+ `static/css/globals.css` tokens 層（異值 token）+ `design/docs/{theme-guide,css-architecture}.md`（目錄級凍結規格 + 對照）+ `design/docs/theme-template.css`（新增·模板）+ `.claude-logs/tools/check_css_governance.py`（新增·常駐契約檢查腳本）。**前置：5 支上傳先 commit 原樣入版控（baseline·baron 手動）**。無 JS / 後端 / DB / API；無 golden（純前端 CSS·腳本為 tools 治理工具非業務碼）。

---

## §2 目標規格

### §2.1 最終狀態目標

1. **主題規格凍結為目錄級契約**（§2.2 定義·適用 `static/themes/*.css` **任何主題**、非僅現役 4 支）——成為 `theme-guide.md` 權威內容：必備 token / 必備選擇器 / 每選擇器屬性白名單 / 可選裝飾層 / 禁止清單。**規格是 prescriptive（任何 conformant 主題應符）；現役 4 支＝descriptive 實例、本任務正規化之。**
2. **全 9 支主題「全檔改寫」至凍結規格**（`static/themes/*.css`·baron 拍板一併處理；每支主題的改寫項逐一）：
   - **骨架重排**：全檔重排至 §2.2-B 標準 9 段序 + 補 2 槽（裝飾層 `.ph::before { }` 空規則〔kahn 已有內容者原樣入槽〕+ chrome 覆寫層 marker〔apple/google 既有覆寫整塊原序入槽、其餘 7 支僅留 marker〕）——重排安全前提已驗：9 支皆無重複選擇器（cascade 不翻轉）；驗收＝規則內容 multiset 對帳（C1/C2 同法）；
   - **結構去重**：15 內容選擇器之非白名單結構屬性 = 0（共用→base／異值→token 或保留〔Q1〕）；
   - **Token 補齊**：上傳 5 支補 `--content-max-w`（值＝globals 預設 760px·零視覺變）→ 9 支各 19；
   - **死碼清除**：`#demo-bar` 系（上傳 5 支各 4-6 條·同 C3 待遇）→ 9 支 = 0；
   - **chrome 覆寫內容原樣保留**（apple/google·設計本體·僅移入槽不改一字）。
3. **前置 baseline（序位鐵則）**：5 支上傳**先 commit 原樣入版控**（baron 手動·凍結可追溯基線）→ 正規化 diff 乾淨可讀可回退；**tasks 階段必以 baseline 為首個 commit、任何正規化改寫嚴禁先於 baseline**；run 期 `.bak` 鐵律照做（雙保險）。
4. **視覺 100% 等價**：**9 主題** × 閱讀視圖 E2E 逐款零差（只搬結構 / token 化 / 清死碼 / 補 token、**不改任何視覺值**；apple/google chrome re-skin 零觸）。
5. **base / token 承接結構**：共用結構上移 `content.css`（填既有空 placeholder）；異值結構 token 化至 `globals.css` tokens 層（主題僅覆 token 值）。
6. **docs 權威化（目錄級語言·單一規格）**：`theme-guide.md` 重寫為凍結規格源、**以「任何 `static/themes/` 主題」為對象**、**只描述一種主題**（統一骨架 + 兩可空槽·無「兩型」語言）+ 附新主題 checklist；`css-architecture` 新增「主題結構→base/token 對照表」。`design/new/themes/` mockup 副本同步與否見 §9 Q_mock。
7. **主題模板產出**（baron v5 拍板）：`design/docs/theme-template.css`——完整統一骨架（19 token 佔位 + 16 選擇器 + 裝飾層空槽 + chrome 覆寫層空槽 marker、每段附註解說明）；新主題＝copy 模板填值。**落點嚴禁 `static/themes/`**（`/api/themes:1286` 掃該目錄任何非內建 `.css` 入下拉選單 → 模板會變假主題；`design/docs/` 不被 served/掃描·安全）。theme-guide Step-by-step 改指向模板（取代「拷貝 mies」）。
8. **CSS 契約檢查腳本常駐化**（baron v6 拍板）：`§8.1 驗收腳本升格為 `.claude-logs/tools/check_css_governance.py` 常駐版`（非一次性）——確定性檢查四類契約：① 主檔系無 unlayered 規則／themes 無 `@layer`（C2 A1 鐵律）；② token 唯一定義於 globals 對應層（防散落重定義）；③ 9 主題符合凍結骨架（必備 token 數〔隨 Q1 定 19/~24〕+ 16 選擇器 + 2 槽 marker + 15 內容選擇器屬性白名單）；④ 主題無死碼選擇器（`#demo-bar` 系）。**用途**：THEME-DEDUP 每 commit 驗收 + 未來任何 AI 動 CSS 後的機器可驗契約（ClawVM harness enforcement 哲學·WORKFLOW-5 一脈）；退出碼 0/1、輸出違規清單。**實作約束（baron review 拍板）**：純 Python 標準函式庫（`re`/`sys`/`pathlib`/`json`）、**嚴禁外部依賴**（cssutils 等）——任何乾淨環境直接可跑。是否掛 PreToolUse/SessionEnd hook 見 §9 Q_hook（定：不掛）。

### §2.2 凍結主題規格（本任務核心產出·草案·待 §9 OQ 定案）

**A. 必備 Token（19·主題 `:root` 必供、不多不少）**
- 色票 13：`--color-{bg,bg-served,surface,surface-2,border,border-strong,divider,text,text-muted,text-subtle,accent,accent-hover,danger}`
- 結構數值 4：`--divider-w`、`--radius-sm`、`--radius-md`、`--content-max-w`
- 字族 2：`--font-display`、`--font-body`
- **異值結構 token 7（Q1-A 定案·凍結）**：`--pc-pad`（#paper-content padding shorthand）/ `--figure-margin-y`（.figure 垂直 margin）/ `--byline-margin-b` / `--byline-pad-b` / `--byline-border-w` / `--figcaption-margin-t` / `--ph-border-w`——globals tokens 層給 default（＝多數派值）、base 讀 token、主題僅覆寫異值。
- → **必備 Token 合計 26**（19 + 7）·主題必覆寫異值 token 才保各自間距（不覆寫＝default）；模板/checklist/`check_css_governance.py` 檢查數同步 26。

**B. 必備選擇器（16·統一骨架·全主題必在）**
- **內容選擇器 15**（必 style、值自訂、屬性限白名單）：`body` / `.display-font` / `#content-area` / `#content-toolbar h2` / `#sidebar h1 .title, #chat-header > .h-title` / `#paper-content` / `#paper-content h1` / `#paper-content h2` / `#paper-content h3` / `#paper-content p` / `#paper-content em` / `#paper-content .byline` / `#paper-content .figure` / `#paper-content .figure .ph` / `#paper-content .figure figcaption`
- **裝飾層槽 1**（**必在、可空**·baron 拍板統一模型）：`#paper-content .figure .ph::before { }`——**所有主題視為有裝飾層**：用者填幾何（如 kahn 天窗光線）、不用者留**空規則**（空偽元素無 `content` 不渲染、完全惰性、合法 CSS）→ 選擇器級一致、機器可驗（每主題恰 16）。
- **統一檔案骨架**（**單一規格·無「兩型」之分**·baron 拍板 v5：section 順序固定 + 兩個標準可空槽·AI 產主題可機械 diff）：
  1. header 註解（主題名/語彙）
  2. `@import` 字體（選）
  3. `:root` 19 token
  4. body / `.display-font`
  5. chrome 標題（`#content-area` / `#content-toolbar h2` / 三欄標題）
  6. `#paper-content` 系（h1/h2/h3/p/em/.byline）
  7. figure / `.ph`
  8. **裝飾層槽**（`.ph::before { }`·必在可空）
  9. **chrome 覆寫層槽**（標準 section 註解 marker `/* ══ 進階 chrome 覆寫層 ══ */`·必在可空——填者如 apple/google、未用者僅留 marker）
  → **每支主題（含模板）骨架完全相同**；差異只在「槽有沒有填」。機器可驗：16 選擇器 + 2 槽 marker 每主題必在。

**C. 每選擇器屬性白名單（只能用·外觀/字體類）**
`color`／`background`／`background-color`／`background-image`／`border-color`／`box-shadow`／`font-family`／`font-size`／`font-weight`／`font-style`／`letter-spacing`／`text-transform`／`line-height`／`text-align`／`content`／`--token` 覆寫
- **補登 `text-align`**（figcaption 置中用·現況已用未登記）；**是否收斂 `font-style`/`letter-spacing`/`font-weight` 等允許自由度見 §9 Q2**。

**D. figure 佔位裝飾——普世 + 統一裝飾層槽（baron 拍板 v4：全主題視為有、未用者空）**
- **佔位裝飾＝普世**：每支主題都裝飾 `#paper-content .figure .ph`，經**白名單 `background`/`background-image`**（漸層）達成——kahn 光暈/kandinsky 三原色/mies 水平線/nara 角色頭/上傳 5 支各自手法。此屬 C 白名單外觀、**非例外**。
- **裝飾層槽＝全主題必在、可空**（B 之第 16 選擇器）：`.ph::before` 幾何裝飾（`position/top/left/right/bottom/width/height/transform/pointer-events + background/content`；搭 `.ph { position: relative }`）——用者填（kahn）、未用者**留空規則**。此槽之幾何屬性屬**允許例外**（僅限佔位裝飾用途）。
- ~~v3「用則寫、不用則省」~~ → **v4 改統一骨架**（baron 拍板）：空規則惰性無副作用、換取選擇器級一致與機器可驗。

**F. chrome 覆寫層槽（骨架標準段·必在可空·v5 統一版）**
- **不分「兩型」**：所有主題同一骨架，chrome 覆寫層是**骨架第 9 段標準槽**——填者（apple/google：`.btn-*`/`.modal-*`/`.msg-*`/`.paper-item`/`.folder-item`/`.ctx-popup`/`#tooltip`/`#chat-input:focus`/`#web-search-toggle.active` 等）、未用者僅留 section marker（內建 4 支 + corbusier/fuller/gropius——chrome 經 token 自動套色、**留空為推薦預設**）。
- **規範**：槽內**建議**色值經 `var(--color-*)`（維護性）、不強制（§9 Q_chrome）；**unlayered 恆勝 components 層**＝覆寫必生效。
- **正規化待遇**：既有填充內容**原樣保留**（設計本體、嚴禁去重/剝除/改寫）；僅補 section marker 使 9 支骨架一致；死碼（#demo-bar）不屬此槽、照清。

**E. 禁止**
- 15 內容選擇器上之非白名單結構屬性（`padding`／`margin`／`width`／`height`／`display`／`gap`／`border`(width/shorthand)／`border-style`／`max-width`／`min-width`／`margin-inline`〔除裝飾層槽〕）；
- 死碼選擇器（`#demo-bar` 系·HTML 早移除）；
- `@layer`（主題須 unlayered）；DOM id / JS / `renderMarkdownWithMath` 觸碰。

### §2.5 候選方案（Diverse Rollout·高風險決策）

| 面向 | 方案 A | 方案 B |
|---|---|---|
| **異值結構（Group C）** | 全 token 化（themes structure-free） | 只上移共用 B、異值保留主題 |
| **白名單內分歧（font-style/letter-spacing/font-weight）** | 明文「允許自由度」（各主題可自選是否設） | 標準化（每選擇器固定必設屬性集） |

- **定案（baron 2026-07-09 review）**：結構＝**A 全 token 化**（7 個異值 token、必備清單 19→26·§2.2-A）；白名單分歧＝**允許自由度**。
- **否決留痕**：結構方案 B（異值保留主題）——contract 不徹底、themes 殘結構、與統一骨架/腳本檢查不搭；白名單分歧全標準化——過度僵化、抹平 kahn 義式 byline / kandinsky 寬字距 h2 等識別。共用 B 上移 base 為所有方案共識。

---

## §3 現況與證據（全 4 主題完整重審·grep + 腳本實測）

**基準**：主題檔為 FE-CSS-GOV C3(`0fbafeb`) 後現態（demo-bar 死碼已除）。

**目錄現況與上傳機制**：
- `/api/themes`（`web_server.py:1258`）：內建 4 支 hardcode（mies/kahn/kandinsky/nara）；**自訂主題＝掃 `static/themes/` 目錄下非內建的 `.css`**（`custom=True`）。上傳 endpoint（`web_server.py:1243`）亦寫入此目錄。
- **`static/themes/` 現 9 支**：4 內建（tracked）+ 5 上傳（apple/corbusier/fuller/google/gropius·**baron 已 copy 入、現 untracked、待 baseline commit**）。
- `design/new/themes/` 有 4 支設計 mockup 副本（非 served·§9 Q_mock）。

### §3.0 上傳 5 支稽核（腳本實測·untracked 現態）

| 主題 | 型 | Token | 缺 | `#demo-bar` 死碼 | 15 內容選擇器結構屬性 |
|---|---|---|---|---|---|
| apple | 🔴 全 re-skin（+chrome 覆寫 `.btn-*`/`.modal-*`/`.msg-*`/`.paper-item`/`.ctx-popup`/`#tooltip` 等） | 18 | `--content-max-w` | 6 條 | 同內建範式（h2 border/padding/margin 等）+ 部分（`max-width`/`margin` 於 #paper-content） |
| google | 🔴 全 re-skin（同上型） | 18 | `--content-max-w` | 6 條 | 同上 |
| corbusier | token 驅動（同內建範式） | 18 | `--content-max-w` | 4 條 | 同內建範式 |
| fuller | token 驅動（+`body font-feature-settings`） | 18 | `--content-max-w` | 4 條 | 同內建範式 |
| gropius | token 驅動 | 18 | `--content-max-w` | 4 條 | 同內建範式 |

- **共同病**：全帶 `#demo-bar` 死碼（拷貝自 **C3 清除前的舊樣板**——正是「無凍結規格→不一致再生產」的活證）+ 全缺 `--content-max-w`（用 globals 760px 預設 → 補登同值＝零視覺變）。
- **兩型定調**：token 驅動型＝正規化同內建；全 re-skin 型＝15 內容選擇器正規化同內建 + **chrome 覆寫層原樣保留**（§2.2-F）。
- 全 9 支皆無 `@layer` 誤用（unlayered ✓）。

### §3.1 覆蓋一致性（已一致·維持凍結）
```bash
# Token：4 主題各 19、交集 19（完全一致）
for f in kahn kandinsky mies nara; do grep -cE '^\s*--[a-z0-9-]+:' static/themes/$f.css; done   # 19/19/19/19
# 選擇器：15 必備全 4 共有 + kahn 用 .ph::before（可選裝飾層）
comm -3 <sel_kahn> <sel_mies>   # 僅差 #paper-content .figure .ph::before
```
→ **必備 token（19）與必備選擇器（15）現況已一致**、凍結為規格即可（§2.2 A/B）。

### §3.1b figure 佔位裝飾＝普世（grep 證·非 kahn 專屬）
```bash
grep -A3 '\.figure \.ph {' static/themes/{kandinsky,mies,nara}.css | grep -iE 'background|gradient'
# kandinsky: background-color + background-image（三原色圓/點/線）
# mies:      background-image: repeating-linear-gradient（水平線）
# nara:      background: radial-gradient（角色頭/嘴點）
# kahn:      background 漸層 + .ph::before 天窗光線（唯一用偽元素技法）
```
→ **4 主題全裝飾 `.ph`**（經白名單 background）；kahn 額外用 `.ph::before` 幾何。故裝飾**普世**、`::before` 為**可選技法**（§2.2 D·非 kahn 專屬、非「必空」）。

### §3.2 非白名單結構屬性（違反白名單·需正規化）
腳本 `{selector: property-keys}` 跨主題比對，非白名單結構屬性（🔴）：

| 選擇器 | 非白名單結構屬性 | 分類 |
|---|---|---|
| `#paper-content h2` | `border-bottom`、`padding-bottom`（4 主題**同值** `var(--divider-w)`/`var(--space-2)`） | **B 共用→base** |
| `#paper-content` | `padding`（kahn `--space-8` / 其餘 `--space-6 --space-8`） | **C 異值→token/保留** |
| `#paper-content .figure` | `margin`（mies `--space-5 0` / 其餘 `--space-6 0`） | **C 異值** |
| `#paper-content .byline` | `margin-bottom`（mies 落單）/ `padding-bottom`（四值分歧）/ `border-bottom` width（mies 0） | **C 異值** |
| `#paper-content .figure figcaption` | `margin-top`（mies 落單）/ `max-width`（kahn 560/mies none）/ `margin-inline`（kahn） | **C 異值 + D**（見 §9 Q3） |
| `#paper-content .figure .ph` | `border`（4 主題·width 1/2px 分歧）/ `position`（kahn 裝飾） | **C 異值 + D** |
| `#paper-content .figure .ph::before`（kahn） | `position/top/left/width/height/transform/pointer-events` | **D 裝飾·保留** |

### §3.3 白名單內屬性集分歧（新發現·§9 Q2 定調）
| 選擇器 | 分歧 | 性質 |
|---|---|---|
| `body` | nara 多設 `font-weight` | 主題美學（字重） |
| `#paper-content h2` | kandinsky/mies 設 `letter-spacing`、kahn/nara 未設 | 主題美學（字距） |
| `#paper-content .byline` | kahn 多設 `font-style`（義式 byline） | 主題美學（義式） |
| `#paper-content .figure .ph` | kahn/nara `background` shorthand vs kandinsky/mies `background-color`+`background-image` | 背景手法（皆白名單·等效） |
| `figcaption` | **`text-align: center` 4 主題皆用·但未登記白名單** | **補登白名單（§2.2-C）** |

### §3.4 base 交互關鍵發現（content.css 已預留 h2 槽·低風險）
```bash
grep -nA2 '#paper-content h2 {' static/css/content.css
# 233:  #paper-content h2 {
# 234:    /* border-bottom 由主題透過 --divider-w + --color-divider 控制 */
# 235:  }
```
- `content.css:233-235` 已有空 `#paper-content h2` placeholder + 註 → Group B 上移＝填既有空槽（設計早預留）。
- `content.css:239-248` `.slide-head h2 { border-bottom: none }`（HOTFIX-3）特異度 1,1,1 > 1,0,1 → 上移後 override 不破。

---

## §4 跨 Phase 接縫契約

**無。** 純前端 CSS 靜態重構、無跨 Phase / 模組執行期資料 handoff。§7.2 顯式豁免申請見 §9 Q5。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 4 主題視覺回歸 | 🟡 中 | 只搬結構/token 化/補登白名單、**零視覺值改動**；base/token 值 byte 對照原主題值；4 主題 × E2E 逐款（§8.2） |
| base h2 交互（slide-head override） | 🟢 低 | §3.4 證：空 placeholder 已預留 + 特異度 override 不破 |
| 抹平主題個性（過度標準化白名單分歧） | 🟢 低（Q2 已定） | 「允許自由度」定案——保留 font-style/letter-spacing 等主題美學、腳本不驗屬性集齊平 |
| 裝飾佔位藝術受損 | 🟢 低 | D 類明確保留（§2.2-D）、不動 `.ph`/`.ph::before` |
| token sprawl（Q1-A 定案） | 🟢 低（清單已凍結） | 恰 7 個異值 token、名單凍結（§2.2-A 26 個封頂）、集中 globals tokens 層（C4 三層分區有家）；腳本驗 26 上限防再膨脹 |
| 未來新主題再不一致 | 🟢 低（本任務治本） | theme-guide 凍結規格 + 建議附「新主題 checklist / 樣板」 |
| 上傳 5 支正規化誤傷 chrome 覆寫層（apple/google 設計本體） | 🟡 中 | §2.2-F 明定**原樣保留**；正規化僅及 15 內容選擇器 + 死碼 + token 補登；baseline commit 凍結原樣可逐行 diff 驗「chrome 層零觸」 |
| baseline 未先 commit 即正規化（審計斷鏈） | 🟢 低 | §2.1-3 前置鐵則：**先 commit 原樣再動**（baron 手動）；run 期 `.bak` 照做（雙保險） |

對齊 framework §4.1 #5。

---

## §6 不可動清單

- [ ] **視覺值零改動**：色/字/間距/線寬解析結果逐款 byte 等價（9 主題）。
- [ ] **裝飾佔位幾何**（kahn `.ph position` + `.ph::before`）嚴禁改動/上移（§2.2-D）。
- [ ] **apple/google 進階 chrome 覆寫層**（`.btn-*`/`.modal-*`/`.msg-*`/`.paper-item`/`.ctx-popup` 等段）**原樣保留、嚴禁去重/剝除/改寫**（§2.2-F·設計本體）；驗收 diff vs baseline == 空。
- [ ] **主題美學自由度**（§9 Q2 採「允許」時）：font-style/letter-spacing/font-weight 等既有主題選擇不被強制齊平。
- [ ] **JS / DOM id / 27+ JS 契約 class / `renderMarkdownWithMath`**——純 CSS、`index.html` 零觸。
- [ ] **themes / 自訂主題 unlayered**——嚴禁 `@layer`。
- [ ] **content.css `.slide-head` override / globals `@layer tokens` + T1/T3 既有 token**——不破壞、只填/加對應處。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 主題白名單/§8 方向（升格凍結規格） | `design/docs/theme-guide.md §1 / §8`（FE-CSS-GOV C3 立·本任務重寫為權威） |
| CSS 架構 / cascade / token 三層 / 作用域 | `design/docs/css-architecture.md §4 / §5 / §6` |
| 前端效能與渲染紅線 | `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` |
| 工作流 / 命名 / §7.2 | `ref/WORKFLOW_SOP.md` |
| 進度管控 / 雙軌 / 不可動 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |

---

## §8 驗證計畫

### §8.1 自動化 / 靜態驗收
- **pytest**：純前端無 Python 邏輯 → 無新增；跑既有 `pytest tests/ -v` sanity（預期全綠·零波及）。
- **腳本驗收**（tasks 每 commit·**以 §2.1-8 常駐腳本 `tools/check_css_governance.py` 執行**、非拋棄式 one-liner；下列 ①-⑧ 為其檢查項）：
  ```bash
  # ① 覆蓋：9 主題各 19 token / 16 必備選擇器全在（含裝飾層槽·可空）（凍結規格）
  # ② 白名單合規：9 主題 15 內容選擇器之非白名單結構屬性 = 0（腳本 {selector:props} 掃描·排裝飾槽/chrome 層）
  # ③ 死碼：9 主題 #demo-bar = 0
  # ④ 值等價：主題覆寫值/base 承接值 == 原結構值（byte 對照 baseline commit / .bak）
  # ⑤ base 承接：content.css #paper-content h2 含 border-bottom+padding-bottom
  # ⑥ chrome 層零觸（apple/google）：chrome 覆寫段 diff vs baseline == 空
  # ⑦ unlayered 鐵律擴至 9 支：grep '^@layer' static/themes/*.css = 0（FE-CSS-GOV C2 A1 鐵律·上傳一併驗）
  # ⑧ 骨架重排對帳：每支重排前後規則內容 multiset 相等（僅位置/marker/空槽差·C1/C2 同法）
  ```

### §8.2 手動 E2E（baron·瀏覽器）
1. 逐一切換 **9 主題** × 閱讀視圖，比對正規化前：h2 底線 / `#paper-content` 內距 / `.figure` 間距 / `.byline` / `figcaption`（含置中/寬度）。
2. kahn 裝飾「天窗光線」`.ph::before` 完好；**apple/google 之 chrome re-skin（按鈕/訊息泡/modal/側欄 item）完好**。
3. slide 視圖 `.slide-head` 底線正常、內層 h2 無重複底線。
4. （選）再上傳一支新主題：unlayered 恆勝、繼承 base 結構無破。

---

## §9 Open Questions（**全數定案 🟢·baron 2026-07-09 review 拍板**）

| # | 問題 | 定案 | 備註 |
|---|---|---|---|
| **Q1** | 異值結構處置 | 🟢 **A·全 token 化（structure-free）** | 徹底落實「主題只管外觀、結構歸 base」；異值 token 實數 **7 個**（reviewer 稱 5-6 係低估·含 Q4 兩線寬）→ 必備 token **19→26**（§2.2-A 凍結清單）；契約檢查腳本可寫得極乾淨。 |
| **Q2** | 白名單內屬性分歧 | 🟢 **允許自由度** | font-style/letter-spacing/font-weight 是設計個性核心、不機械對齊；腳本只驗「所用屬性均在白名單內」、不驗屬性集齊平。 |
| **Q3** | figcaption `max-width`/`margin-inline` | 🟢 **保留主題·列裝飾例外** | figure 專屬裝飾排版（edge case）、不強行 token 化；歸主題自由排版。 |
| **Q4** | byline/ph 線寬 | 🟢 **隨 Q1-A token 化** | 立 `--byline-border-w`/`--ph-border-w`、主題僅覆值；border-color 屬白名單、主題自由（如 kandinsky byline 用 divider 色）。 |
| **Q5** | Group B 上移位置 | 🟢 **是·content.css L233 既有預留槽** | 符合原架構預期。 |
| ~~Q6~~ | 模板 | 🟢 已拍板（v5）：`design/docs/theme-template.css` + checklist | 落點避開 `/api/themes` 掃描。 |
| **Q7** | §7.2 整合測試 | 🟢 **顯式豁免** | 純前端 CSS、無後端 handoff。 |
| **Q8** | 相容底線 | 🟢 **Safari 18+（沿 FE-CSS-GOV 既定案·非新議題）** | 本任務純搬移/token 化、不引入任何新 CSS 特性 → 底線零新增需求。 |
| ~~Q_dir~~ | 上傳主題 | 🟢 已拍板（v4）：一併處理、baseline 先行 | 9 支全治理。 |
| ~~Q_decor~~ | 裝飾層模型 | 🟢 已拍板（v4）：全主題有槽、未用者空 | 統一骨架。 |
| **Q_chrome** | chrome 槽內色值 | 🟢 **建議 var(--token)、不強制** | 文件引導級；apple/google 既有硬編碼零干擾。 |
| **Q_mock** | `design/new/themes/` mockup | 🟢 **不動·theme-guide 標示 stale mockup 非 served** | served 唯一目錄＝`static/themes/`；無同步負擔。 |
| **Q_hook** | 腳本掛 hook | 🟢 **本任務不掛·僅 tools/ 常駐** | 保持純 FE 邊界；先手跑累積誤報率/速度經驗、掛載屬 WORKFLOW-5 部署另議。 |

> **全 OQ 結清 → plan 定稿、可進 tasks（階段 2）。**

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 THEME-DEDUP 主題規格凍結與結構去重目標規格，作為 tasks 拆分與原子執行唯一基準 |
| **用途** | 供 baron 審查、tasks 拆分引用；階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9（凍結規格草案 §2.2·落地後權威移至 theme-guide.md） |
| **引用方** | 後續 THEME-DEDUP tasks / 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁含設計脈絡/拍板過程/commit 拆分；凍結規格落地後唯一源 theme-guide.md |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision |
| **刪除條件** | 任務完成、baron 同意歸檔 archive/ |
| **重複防護** | 凍結規格唯一權威落地於 theme-guide.md；token 三層/作用域唯一源 css-architecture.md；本 plan 僅定技術規格 |

### §99.2 Revision 歷程

- v7 (2026-07-09)：**baron review 全 OQ 拍板 → plan 定稿**——Q1=A 全 token 化〔修正 reviewer「5-6 個」低估：異值 token 實數 **7**（含 Q4 `--byline-border-w`/`--ph-border-w`）→ 必備 token **19→26**、§2.2-A 凍結名單：`--pc-pad`/`--figure-margin-y`/`--byline-margin-b`/`--byline-pad-b`/`--byline-border-w`/`--figcaption-margin-t`/`--ph-border-w`〕；Q2 允許自由度／Q3 figcaption 保留（裝飾例外）／Q4 隨 A／Q5 是／Q7 豁免／Q8 Safari 18+／Q_chrome 建議 var 不強制／Q_mock 不動+標 stale／Q_hook 不掛。另採 reviewer 三補強：①腳本**純標準庫**（re/sys/pathlib/json·禁 cssutils 等外部依賴）②模板隔離確認③ **baseline 序位鐵則**（tasks 必以 baseline 為首 commit、正規化嚴禁先於之）。§2.5 定案留痕、§5 風險降級（Q1/Q2 定案項）。**可進 tasks。**
- v6 (2026-07-09)：baron 拍板「驗收腳本升格 tools/ 常駐」——新增 §2.1-8 交付物 `.claude-logs/tools/check_css_governance.py`（四類契約確定性檢查：unlayered 鐵律/token 唯一定義/9 主題凍結骨架/死碼；退出碼 0/1）＝THEME-DEDUP 每 commit 驗收 + 未來 AI 動 CSS 之機器可驗契約（ClawVM enforcement·替代已否決的 token-scoping 改造〔評估結論：8/13 共用 token+modal 在欄外+混合模型靜默失敗 → 不做〕）；§8.1 改以常駐腳本執行；新增 Q_hook（本任務不掛 hook、先手跑累積誤報率再議）。
- v5.2 (2026-07-09)：FE-CSS-GOV 未做項盤點後補 2 缺口——(1) §2.2-A 加 **Q1 連動**（Q1-A 時必備 token 19→~24/25、主題必覆寫新結構 token 才保異值、清單隨 Q1 凍結）；(2) §8.1 補 ⑦ unlayered 鐵律擴 9 支驗收 + ⑧ 骨架重排 multiset 對帳。盤點結論：C3 外溢（結構去重/theme-guide）＝本 plan 核心已涵蓋；C4 真解耦（元件選擇器 scope）/C5 D 類共用 class／`/api/themes` hardcode+上傳 label＝不屬本 plan（各為獨立架構案/已判正當/後端 .py 越權）。
- v5.1 (2026-07-09)：§2.1-2 明確化「**9 支全檔改寫**」五項（骨架重排〔9 支無重複選擇器已驗·cascade 安全·multiset 對帳〕/ 結構去重 / token 補齊 / 死碼清除 / chrome 內容原樣入槽）。
- v5 (2026-07-09)：baron 拍板「統一 + 模板」——(1) **廢「兩型」分類 → 單一統一骨架**：chrome 覆寫層由「進階可選型」改為**骨架第 9 段標準槽（必在可空·section marker）**，與裝飾層槽同邏輯；每支主題（含模板）骨架完全相同、差異只在槽有沒有填；機器可驗＝16 選擇器 + 2 槽 marker 每主題必在。(2) **文件統一**：theme-guide 只描述一種主題（無兩型語言）。(3) **模板產出**：`design/docs/theme-template.css`（統一骨架+逐段註解；**嚴禁落 static/themes/**——`/api/themes:1286` 會掃入下拉變假主題、design/docs/ 不被 served 安全）；Q6 結案。
- v4 (2026-07-09)：baron 三拍板——(1) **上傳 5 支一併處理**（已 copy 入 `static/themes/`）：scope 4→**9 支全治理**；§3.0 上傳稽核（兩型：apple/google 全 re-skin / corbusier/fuller/gropius token 驅動；共同病＝#demo-bar 死碼〔拷貝 C3 前舊樣板·不一致再生產活證〕+ 全缺 --content-max-w）；新增 §2.2-F 進階 chrome 覆寫層（合法化 re-skin 型·正規化原樣保留）+ Q_chrome。(2) **裝飾層統一模型**：全主題視為有裝飾層、未用者空規則（`.ph::before {}` 惰性）→ 必備選擇器 15→**16**（統一骨架·機器可驗）；v3「用則寫不用則省」廢。(3) **兩段 commit**：先 commit 上傳原樣 baseline → 正規化 → 再 commit（§2.1-3 前置鐵則）；Q_dir/Q_decor 結案。
- v3 (2026-07-09)：baron 兩指正 + 上傳查證——(1) **規格目錄級化**：§2.1/§2.2/§1/§3 改「規格適用 `static/themes/*.css` 任何主題」（非硬編 4 檔）、theme-guide 目錄級語言、+ Q_dir + Q_mock。**上傳位置查證**（baron 截圖見 5 支自訂主題 fuller/gropius/corbusier/google/apple）：`/api/themes:1258` 掃 `static/themes/` 非內建 .css＝自訂；本 server `find`/`ls` 0 命中 → 上傳為 baron 環境 runtime 未追蹤檔、未同步本 server；THEME-DEDUP 無法從本 server 正規化該 5 支、但 unlayered 恆勝保證 base/token 改動不破壞之（§3/§5）；Q_dir 升為 (a) best-effort /(b) baron commit 後納入之抉擇。(2) **裝飾普世化**：§2.2 D + §3.1b 改「figure 佔位裝飾＝普世〔4 主題皆經 background 裝飾〕、`.ph::before` 幾何為**標準可選技法**〔非 kahn 專屬、非『必空』〕」（grep 證 kandinsky/mies/nara 以 background-image 漸層裝飾、kahn 額外用 ::before）。
- v2 (2026-07-09)：baron 要求「訂死主題規格」——scope 由「結構去重」升級為「主題完整規格凍結 + 4 主題全正規化 + doc 權威化」；新增 §2.2 凍結規格草案 + §3.1 覆蓋一致性 + §3.3 白名單內分歧全審 + §9 Q2/Q6 新 OQ
- v1 (2026-07-09)：初版——FE-CSS-GOV C3 外溢結構去重；§3.1 結構屬性審 + §3.2 base placeholder + §2.5 A/B + 六 OQ
