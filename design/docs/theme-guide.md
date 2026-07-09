# 主題凍結規格與開發指南 · MadPro UI

> 主題 = `static/themes/*.css` 單檔。切換主題只改 `#theme-link` 的 `href`。
> 本檔為**目錄級主題凍結規格權威源**（THEME-DEDUP 定案）：適用 `static/themes/` 下**任何主題**（非僅內建 4 支）——必備 token（§2）、統一骨架與必備選擇器（§3）、屬性白名單（§4）、兩個可空槽（§5）、禁止清單（§6）、unlayered 優先級（§7）。
> 架構全景（檔案分層 / @layer / token 三層 / 結構→base 對照）見 `css-architecture.md`；跨檔設計理念見 `principles.md §6.5`。
>
> **落地進度**：C1 base 承接 ✅ ／ C2 內建 4 支正規化 + 本規格凍結 ✅ ／ C3 上傳 5 支正規化 ⬜ ／ C4 模板 `design/docs/theme-template.css` + 契約腳本 `tools/check_css_governance.py` ⬜。

---

## §1 核心模型：主題只給「長什麼樣」

- **結構歸 base**：佈局結構規則（padding/margin/border 寬…）一律在主檔 `static/css/content.css`（@layer components）；主題**不寫結構規則**。
- **數值經 token**：結構的「值」由主題在 `:root` 覆寫 26 必備 token 供給（§2）——主題徹底 structure-free、又保留各自間距美學。
- **外觀自由**：白名單屬性（§4）內主題完全自由；屬性選用不強制齊平（如 kahn 義式 byline、kandinsky 寬字距＝主題個性、規格不抹平）。
- 判準一句話：**「長怎樣」→ 主題白名單屬性；「多大／擺哪／佔多少」→ base 規則 + 主題 token 值**。

---

## §2 必備 Token（26·主題 `:root` 必供、不多不少）

```css
:root {
  /* ── 色票（13）── */
  --color-bg / --color-bg-served / --color-surface / --color-surface-2
  --color-border / --color-border-strong / --color-divider
  --color-text / --color-text-muted / --color-text-subtle
  --color-accent / --color-accent-hover / --color-danger

  /* ── 結構厚度 / 圓角 / 寬度（4）── */
  --divider-w: 1px | 2px;
  --radius-sm: 0;   --radius-md: 0;      /* 現行主題皆 0 */
  --content-max-w: 720px ~ 860px;        /* 中欄共軌最大寬度 */

  /* ── 異值結構 token（7·THEME-DEDUP·規則在 base、值在此覆）── */
  --pc-pad:              /* #paper-content padding（shorthand 可）*/
  --figure-margin-y:     /* .figure 垂直 margin */
  --byline-margin-b:     /* .byline margin-bottom */
  --byline-pad-b:        /* .byline padding-bottom */
  --byline-border-w:     /* .byline 底線寬（0＝無底線·如 mies）*/
  --figcaption-margin-t: /* figcaption margin-top */
  --ph-border-w:         /* .figure .ph 邊框寬 */

  /* ── 字族（2·硬規範：必須 sans-serif·詳 typography.md §0）── */
  --font-display / --font-body
}
```

- default 值（未覆寫時生效）定義於 `globals.css` T3 段；**主題顯式寫滿 26**（即使同 default）——機器可驗、骨架一致。
- **底線/邊框「色」**不 token 化：base 給 default（byline→border-strong、ph→divider），主題需異色時以白名單 `border-color` 覆（如 kandinsky byline 用 divider、kahn ph 用 border-strong）。
- 元件級 token（`--btn-*`/`--rail-w` 等）由主檔提供、**非主題調校面**（css-architecture §6.1 T2）。

---

## §3 統一骨架（9 段固定序）與必備選擇器（16）

**每支主題檔的段落結構完全相同**（AI 產主題可機械 diff；差異只在槽有沒有填）：

```
1. header 註解（主題名/核心語彙/設計轉譯）
2. @import 字體（選用）
3. /* ══ tokens（26 必備）══ */          :root
4. /* ══ base 字體 ══ */                 body / .display-font
5. /* ══ chrome 標題 ══ */               #content-area / 三欄標題 / #content-toolbar h2
6. /* ══ 內容（#paper-content 系）══ */   #paper-content + h1/h2/h3/p/em/.byline
7. /* ══ figure 佔位 ══ */               .figure / .figure .ph / figcaption
8. /* ══ 裝飾幾何層 ══ */                .ph::before（必在、可空·§5）
9. /* ══ 進階 chrome 覆寫層 ══ */         marker（必在、可空·§5）
```

**必備選擇器 16**（每主題必在；屬性限 §4 白名單）：
`body`／`.display-font`／`#content-area`／`#content-toolbar h2`／`#sidebar h1 .title, #chat-header > .h-title`／`#paper-content`／`#paper-content h1`／`h2`／`h3`／`p`／`em`／`.byline`／`.figure`／`.figure .ph`／`.figure figcaption`／**`.figure .ph::before`（第 16·可空規則）**

---

## §4 屬性白名單（主題選擇器只能用）

| 類別 | 屬性 |
|---|---|
| 色 | `color`／`background`／`background-color`／`background-image`／`border-color` |
| 陰影 | `box-shadow` |
| 字體 | `font-family`／`font-size`／`font-weight`／`font-style`／`letter-spacing`／`text-transform`／`line-height` |
| 排版 | `text-align`（figcaption 置中等） |
| 其他 | `content`（偽元素）／`--token` 覆寫 |

- **屬性選用自由**（Q2 定案）：白名單內設不設、設什麼值＝主題美學自由；規格只驗「所用屬性在白名單內 + 覆蓋齊備」。
- **排版例外（Q3·個案登記）**：figcaption `max-width`/`margin-inline`（kahn 560px+auto／mies none）＝圖說寬度美學、保留主題；`.ph { position: relative }`＝裝飾幾何定位基準（kahn）。

---

## §5 兩個可空槽（全主題必在）

**A. 裝飾幾何層 `#paper-content .figure .ph::before`**
- 每支主題**都有**此槽：用者填幾何裝飾（kahn 天窗光線：`position/top/left/width/height/transform/pointer-events + background/content`）、未用者留**空規則** `{ }`（空偽元素無 `content` 不渲染、完全惰性）。
- 槽內幾何屬性＝白名單外的**允許例外**（僅限此佔位裝飾用途）。
- 佔位裝飾本體（`.ph` 的 background 漸層）屬 §4 白名單、**每主題自由發揮**（kahn 光暈/kandinsky 三原色/mies 水平線/nara 角色頭）。

**B. 進階 chrome 覆寫層（section marker `/* ══ 進階 chrome 覆寫層 ══ */`）**
- 每支主題**都有**此 marker：要 re-skin chrome（`.btn-*`/`.modal-*`/`.msg-*`/`.paper-item` 等）的主題把覆寫規則放本段（如上傳 apple/google）、不用者僅留 marker。
- **建議**槽內色值經 `var(--color-*)`（維護性）、不強制（Q_chrome·既有主題硬編碼不動）。
- chrome 經 token 自動套色＝**推薦預設**（內建 4 支皆此型、槽空）。
- 細節與上傳主題章 → C3 補。

---

## §6 禁止清單

- ❌ 15 內容選擇器上之非白名單結構屬性（`padding`／`margin`／`width`／`height`／`display`／`gap`／`border`(width/shorthand)／`border-style`／`max-width`／`min-width`／`margin-inline`——§4 排版例外與 §5-A 裝飾槽除外）→ 結構歸 base、值走 token（§2）。
- ❌ 死碼選擇器（`#demo-bar` 系·HTML 早移除）。
- ❌ `@layer`（主題必 unlayered·§7）。
- ❌ DOM 結構、JS 邏輯、`z-index` 層級表（共用契約）。

---

## §7 為何主題恆勝主檔——unlayered 優先級

主檔系以 `@layer reset, tokens, base, components;` 串接（`css-architecture.md §4`）；**主題檔（含上傳）維持 unlayered**。

- CSS Cascade L5：**unlayered author styles > 任何 layered styles** → 主題恆勝主檔四層——token 覆寫、白名單外觀、chrome 覆寫全部必生效。
- **鐵律**：主題嚴禁寫 `@layer`（包層＝自降優先權）。
- 上傳主題（RAG-13）不含 `@layer` → 天然 unlayered → 零破；缺 token/結構者自動繼承 base default（§2）。
- ❌ 舊 source-order 說（「`<link>` 排 `</style>` 後靠後出者勝」）已作廢；`#theme-link` 殿後僅供多主題切換後載者勝。

---

## §8 Step-by-step：建立新主題

> C4 產出統一骨架模板 `design/docs/theme-template.css` 後、Step 1 改為「copy 模板」；目前以最簡 conformant 主題（mies）為起點。

1. **起點**：`cp static/themes/mies.css static/themes/<name>.css`（C4 後改 copy 模板）。
2. **header 註解**：主題名、核心信念、視覺語彙（5 行內）。
3. **26 token 填值**（§2）：13 色 + 4 結構寬 + 7 異值結構 + 2 字族——只改值、不增減。
4. **字體 `@import`**（選）：置 `:root` 前（防 FOUT）。
5. **白名單屬性調印刷**（§4）：16 選擇器內自由發揮 font/letter-spacing/text-transform…。
6. **兩槽**（§5）：要幾何裝飾填 `::before`、要 re-skin chrome 填 marker 段；不用留空。
7. **掛載**：`#theme-link href="themes/<name>.css"`（或經風格 Modal 上傳）。
8. **checklist**：
   - [ ] 26 token 齊（缺者 fallback 生效、視覺斷裂）
   - [ ] 16 選擇器 + 2 槽 marker 在
   - [ ] 零非白名單結構屬性（§6）、零 `#demo-bar` 死碼、零 `@layer`
   - [ ] 三欄分隔線可見、active icon 反白對比 ≥4.5、字體 fallback 不破版
   - [ ]（C4 後）`python3 .claude-logs/tools/check_css_governance.py` 全綠

---

## §9 常見陷阱

- **主題被主檔蓋過** → 第一嫌疑＝規則誤包 `@layer`（§7 鐵律）。
- **間距跑掉** → 檢查 7 異值結構 token 是否覆寫（未覆＝base default）。
- **底線/邊框色不對** → 色不走 token：以白名單 `border-color` 覆（§2 註）。
- **FOUT** → `@import` 必在 `:root` 前。
- **`--radius-* > 0`** 破直角承諾 → 須註明並修 `principles.md`。
- **localStorage 持久化**（key: `madpro-theme`）主檔已實作、新主題零 JS。

---

## §10 使用者自訂 CSS 上傳與後端連動規格（RAG-1 R2 子項 B/D/H）

> 對應：`web_server.py::upload_theme` + `static/index.html` 風格 Modal 上傳連動
> **相容保證**：上傳 CSS 不含 `@layer` → 天然 unlayered → 恆勝主檔 base（§7）；缺 token/結構自動繼承 base default。上傳主題正規化章 → C3 補。

### §10.1 API 規格
**Endpoint**：`POST /api/themes/upload`；`multipart/form-data`；`file`：`.css`（≤ 100KB）
**Response 200**：`{ "filename": "<sanitized>.css", "url": "/static/themes/<name>.css" }`
**Error**：`400`（非 .css / sanitize 後空 / 路徑無效）、`413`（>100KB）

### §10.2 安全性過濾（5 道防線）
1. 副檔名僅 `.css` 2. 檔名 sanitize（`re.sub(r"[^a-zA-Z0-9_-]", "_")`+壓縮+strip） 3. MIME 依副檔名 4. 100KB 上限 5. 路徑強制 `static/themes/`+`resolve()` 檢查

### §10.3 前端整合
風格 Modal「上傳 CSS」→ 隱藏 `<input type="file" accept=".css">` → 成功：`#theme-link.href`+`localStorage`+dropdown 更新；失敗 `alert(detail)`。

### §10.4 資源目錄
上傳目標 `static/themes/<sanitized>.css`；**served 主題唯一目錄＝`static/themes/`**（`design/new/themes/` 為 stale mockup、非 served）；相關：`web_server.py::upload_theme`／`#theme-modal`／`tests/test_themes_upload.py`（5 pytest）。
