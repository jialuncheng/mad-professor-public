# CSS 架構與 ownership map · MadPro UI

> 本檔為 **CSS 檔案架構、cascade 層序、命名作用域** 的權威 ownership map——回答「**某段樣式該寫哪支檔、哪一層**」。
> 由 `FE-CSS-GOV` 任務建立與維護；治理高度定案源見 `baton/frontend_css_governance_audit.md`。
> 最後現況對照：2026-07-09、基準 `static/index.html@d4ce75a`（FE-CSS-GOV C1 File Split）。
>
> **建置狀態（漸進落地）**：C1 拆檔（本篇初版）✅ ／ C2 @layer 層序 ⬜ ／ C3 主題去重白名單 ⬜ ／ C4 token 歸屬 ⬜ ／ C5-C7 命名前綴+白名單表 ⬜。未打勾章節為**規劃、尚未落地**。

---

## 1. 技術棧前提

- **無 build step**：純 `static/index.html` + `static/css/*.css`（主檔系）+ `static/themes/*.css`（換膚）+ `static/vendor/`（第三方），FastAPI 直接 served。
- 相容底線：**Safari 18+**（baron 2026-07-09 定案）——`@layer` / `:has()` / `content-visibility` 皆在基線內。
- ❌ 不採 Tailwind / CSS Modules / SPA / build——作用域隔離靠**命名紀律 + @layer**（build-less 等價解）。

---

## 2. 檔案職責表（C1 落地）

`static/index.html` head 以固定序 `<link>` 載入（**載入序＝原 inline source 序、cascade 等價**）；`#theme-link` 殿後（主題後出者勝）。

| # | 檔 | 職責 | 原 inline 段 |
|---|---|---|---|
| 1 | `globals.css` | `@layer` 宣告位（C2）／`:root` tokens／reset（`*,::before,::after`/`body,h1…`）／base 元素通則／未掛主題 fallback | 1–89 |
| 2 | `overlays.css` | Tooltip／Modal 七家族／`.modal-input`＋廣義 input／自訂 dropdown | 90–267 |
| 3 | `layout.css` | 三欄框架（`#app`）／共用按鈕系統（`.btn-*`）／`.icon-only`／**收合態 rail/collapse**／全域 scrollbar | 268–355 ＋ 1227–1285 |
| 4 | `sidebar.css` | 左欄 sidebar／上傳中占位列／**`.ctx-popup` 浮層**／左欄底部 | 356–641 |
| 5 | `content.css` | 中欄 `#paper-content`／META-NORM 動態 metadata／PIPE-SLIDES／FE-RHYTHM margin-flow／KaTeX 顯示式防禦 | 642–945 |
| 6 | `chat.css` | 右欄 chat／訊息泡泡（`.msg-*`、含 FE-PERF-2 `content-visibility` 遺產）／輸入區／hashtag autocomplete | 946–1226 |
| 7 | `print.css` | `@media print`（列印只印中欄、19 個 `!important` 原樣、**unlayered**） | 1286–1354 |

**對帳（C1 驗證）**：7 檔非空行 multiset ＝原 1,354 行 CSS 塊 byte-identical；`{`/`}` 各 234、每檔 brace 平衡。

### 2.1 歸屬判例（C1 判定，供未來一致）
- **`.ctx-popup` 浮層 → sidebar.css**：物理原生於左欄段（原 569-603）、觸發源為 `.paper-menu-btn`/`.folder-item .menu-btn`（左欄）。`.dropdown-popup` 變體則隨 modal/dropdown 於 overlays.css。屬**跨切面候選**（未來可獨立 popup.css）、C1 依物理原生歸 sidebar。
- **收合態/scrollbar → layout.css（第二段 1227-1285）**：與 layout 第一段非連續、但同屬「框架/欄行為」；載入序提前經驗證零 cascade 翻轉（全 `.collapsed` 複合高特異度或 `*::-webkit-scrollbar` 唯一偽元素）。

---

## 3. 「新樣式寫哪」決策樹（C1 版）

```
新增/修改一段 CSS：
├─ 是 :root token（全域色/間距/字級/radius）？        → globals.css（C4 後：tokens 層）
├─ 是元件級變數（--btn-*/--rail-w/--chat-pad-x…）？    → 該元件所屬檔頂 :root（C4 落地）
├─ 是 @media print？                                   → print.css
├─ 是 Modal/Tooltip/Popup/Dropdown？                   → overlays.css（.ctx-popup base 例外→sidebar.css）
├─ 是三欄框架/按鈕系統/icon/收合/scrollbar？           → layout.css
├─ 作用於左欄（sidebar/folder/paper-list/上傳）？       → sidebar.css
├─ 作用於中欄（#paper-content/current-title/abstract）？→ content.css
├─ 作用於右欄（chat/msg/input/hashtag）？               → chat.css
└─ 主題外觀覆寫（色/字/陰影/token）？                   → themes/*.css（結構屬性禁·見 theme-guide）
```

---

## 4. Cascade 層序（C2 規劃、尚未落地）

> ⬜ **待 C2**：`globals.css` 首行將宣告 `@layer reset, tokens, base, components;`；主檔系 7 檔（除 print）內容入對應層；**`themes/*.css`、自訂主題上傳、`print.css` 維持 unlayered**——依 CSS Cascade L5「unlayered > layered」→ 主題與 print 永遠贏 base，且 RAG-13 自訂主題上傳契約零變。主檔系**嚴禁 unlayered 規則**（否則會意外蓋過主題）。

## 5. 命名作用域與白名單（C5-C7 規劃、尚未落地）

> ⬜ **待 C5-C7**：chrome UI 之 ID 後代選擇器收斂為單 class（前綴 `.sb-*`/`.chat-*`/`.ct-*`）；**內容渲染容器白名單**（`#paper-content`/`#chat-messages`/`#current-title`/`#abstract-toolbar` 之後代規則保留——內容為 marked/後端/renderTitleHeader 產物、無 class 可掛）；**DOM id 與 JS 契約 class 零改名**（見 `dom-reference.md §8`）。前綴表與白名單全量表於 C5-C7 落地。

---

## §99 治理

- **權威源**：本檔＝CSS 檔案架構/層序/作用域 ownership 唯一源；治理高度定案在 `baton/frontend_css_governance_audit.md`；視覺 token/元件契約在 `color-tokens.md`/`components.md`/`dom-reference.md`；主題契約在 `theme-guide.md`；效能紅線在 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`。
- **維護**：FE-CSS-GOV 各 commit 同步更新對應章節（建置狀態勾選 + 基準戳）。
