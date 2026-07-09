# 主題開發指南 · MadPro UI

> 主題 = `static/themes/*.css` 單檔。切換主題只改 `#theme-link` 的 `href`。
> 本檔為**主題契約權威源**：主題能碰什麼（允許屬性白名單）、必供什麼（必備 token）、為何恆勝主檔（unlayered 優先級）、以及從 0 寫出新主題。
> 架構全景（檔案分層 / @layer 層序）見 `css-architecture.md`；跨檔設計理念見 `principles.md §6.5`。
>
> **建置狀態**：C3（FE-CSS-GOV）已重寫本契約 + 清除 `#demo-bar` 死碼；主題**結構去重**（殘留 padding/margin/figure 等上移 base）由後續 **THEME-DEDUP** plan 完整審計後落地（見 §8）。

---

## 1. 允許屬性白名單（Q8 契約·硬規則）

主題的職責是**外觀與字體**，不是**佈局結構**。結構歸主檔系 `static/css/*.css`（base 層），主題只給「長什麼樣」。

### ✅ 允許（主題可寫）
| 類別 | 屬性 |
|---|---|
| 色 | `color` / `background` / `background-color` / `background-image` / `border-color` |
| 陰影 | `box-shadow` |
| 字體 | `font-family` / `font-size` / `font-weight` / `font-style` / `letter-spacing` / `text-transform` / `line-height` |
| Token 覆寫 | 任何 `--token`（見 §2 必備清單） |

- ⚠️ **字族硬規範**：`--font-display` / `--font-body` 必須非襯線（sans-serif）。詳 `typography.md §0`。

### ✅ 允許的例外——figure 佔位裝飾幾何（baron 2026-07-09 拍板）
`#paper-content .figure .ph` 及其 `::before` 用於**純裝飾佔位藝術**的幾何（`position` / `width` / `height` / `top` / `left` / `transform`）**視為主題自有外觀**（與已允許的背景漸層同性質——它是視覺識別、非共用佈局）。例：Kahn 的「拱頂天窗光線」`.ph::before`。這類裝飾幾何**保留於主題**、不上移 base。

### ❌ 禁止（屬主檔 base、主題不得寫）
- **佈局結構**：`margin` / `padding` / `width` / `height` / `display` / `gap` / 非裝飾用途的 `position` / `border-width`（`border` shorthand 的粗細分量）/ `border-style`
- DOM 結構、JS 邏輯
- 按鈕尺寸、容器尺寸、間距模矩、icon 規格（元件級 token，由主檔 base 提供）
- `z-index` 層級表（共用契約）

> 判準一句話：**「改的是它長怎樣」→ 主題**；**「改的是它多大／擺哪／佔多少空間」→ 主檔 base**。裝飾佔位藝術是唯一登記在案的結構例外。

---

## 2. 必備 token 覆寫清單

主題 `:root` 必供以下 token，否則主檔 base 的 fallback 啟動、視覺斷裂：

```css
:root {
  /* 色票（13） */
  --color-bg:            ...;
  --color-bg-served:     ...;     /* 可同 bg 或略亮 */
  --color-surface:       ...;
  --color-surface-2:     ...;
  --color-border:        ...;
  --color-border-strong: ...;
  --color-divider:       ...;
  --color-text:          ...;
  --color-text-muted:    ...;
  --color-text-subtle:   ...;
  --color-accent:        ...;
  --color-accent-hover:  ...;
  --color-danger:        ...;

  /* 結構厚度 / 圓角（結構「數值」由主題經 token 供給、規則本體在 base） */
  --divider-w: 1px | 2px;
  --radius-sm: 0;                  /* 目前所有主題皆 0 */
  --radius-md: 0;

  /* 字體 */
  --font-display: ...;             /* sans-serif 硬規範 */
  --font-body:    ...;

  /* 中欄共軌最大寬度（BUG-F1 Bug 5 / ui-fixes-batch B7）
     toolbar + paper-content + abstract 同軌；不覆寫則沿主檔 760px。
     現況：kahn 720 / nara 800 / kandinsky 820 / mies 860 */
  --content-max-w: 720px | 760px | 800px | 820px | 860px;
}
```

> **元件級 token**（`--btn-*` / `--rail-w` / `--chat-pad-x` 等）由主檔提供、**非主題調校面**，主題不需也不應覆寫（FE-CSS-GOV C4 後歸各元件檔 `:root`）。

---

## 3. 為何主題恆勝主檔——unlayered 優先級（C2 後·取代舊 source-order 說）

C1 拆檔、C2 層化後，主檔系以 `@layer reset, tokens, base, components;` 串接（見 `css-architecture.md §4`）。**主題檔（及使用者自訂上傳）維持 unlayered（不包進任何 `@layer`）**。

- 依 CSS Cascade Layers L5 規範：**unlayered author styles > 任何 layered styles**。故主題**恆勝**主檔四層——換膚必生效、`--color-*`/`--font-*` 覆寫 base fallback 必成功。
- **鐵律**：主題檔**嚴禁**寫 `@layer`（包進層 = 自降優先權、可能被主檔蓋過）。
- **RAG-13 使用者自訂上傳零破**（§7）：上傳的 CSS 不含 `@layer` → 天然 unlayered → 同樣恆勝，無需知道層機制。
- ❌ **舊說作廢**：早期「主題 `<link>` 必須排在 `</style>` 之後、靠 source-order 後出者勝」已過時（CSS 已外檔化 + 層化）；現在靠 **unlayered>layered**、與 `<link>` 相對次序脫鉤（但 `#theme-link` 仍建議殿後，供多主題切換時後載者勝）。

---

## 4. Step-by-step：建立 `themes/wright.css`

以 Frank Lloyd Wright 風格為例：

### Step 1：拷貝既有主題作起點
```bash
cp static/themes/mies.css static/themes/wright.css
```

### Step 2：替換 header 註解
- 主題名、核心信念、視覺語彙（5 行內描述）

### Step 3：色票 + token 替換（§2 必備清單）
```css
:root {
  --color-bg: #d2c4a8;            /* Cherokee red 沙暖底 */
  --color-bg-served: #efe6cc;
  --color-surface: #c1b393;
  --color-surface-2: #a99771;
  --color-border: #8a7656;
  --color-border-strong: #604a2c;
  --color-divider: #2e2418;        /* deep oak 結構 */
  --color-text: #1d1610;
  --color-text-muted: #5a4830;
  --color-text-subtle: #8a7656;
  --color-accent: #b13a2a;         /* Cherokee red */
  --color-accent-hover: #8c2d20;
  --color-danger: #6c1f1a;

  --divider-w: 2px;                /* 厚水平線 — prairie 屋簷 */
  --radius-sm: 0;
  --radius-md: 0;

  --font-display: "DM Sans", "PingFang TC", "Microsoft JhengHei", sans-serif;
  --font-body: "DM Sans", "PingFang TC", "Microsoft JhengHei", sans-serif;

  --content-max-w: 800px;
}
```

### Step 4：字體載入
若用 Google Font，主題檔最上方（`:root` 之前）加：
```css
@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap");
```

### Step 5：印刷規則調整（**只碰白名單屬性**）
參考 mies/kahn 樣本，按主題語彙修 `font-*` / `letter-spacing` / `text-transform`：
- Wright 偏好水平強調 → `letter-spacing: 0.04em`
- 標題字重 600（介於 Mies 700 與 Kahn 500 之間）
- figure 佔位可用 Wright 風 stained-glass 幾何紋（`.ph` / `.ph::before` 裝飾幾何屬允許例外，見 §1）

### Step 6：掛載
```html
<link id="theme-link" rel="stylesheet" href="themes/wright.css">
```

### Step 7：驗證 checklist
- [ ] 三欄分隔線清晰可見（`--divider-w` / `--color-divider` 生效）
- [ ] icon 在新色票下仍可辨識（特別是 active 反白：`--color-accent` 與 `#fff` 對比 ≥ 4.5）
- [ ] 中欄標題與 h1 字級相符
- [ ] dropdown popup、tooltip、modal 樣式正常繼承
- [ ] 字體載入完成前 fallback 不破版（`font-display: swap`）
- [ ] **未寫任何佈局結構屬性**（`margin`/`padding`/`width`… 除 §1 裝飾例外外＝0）

---

## 5. 常見陷阱

### 5.1 主題被主檔蓋過？→ 檢查是否誤包 `@layer`
主題恆勝的前提是 **unlayered**（§3）。若某主題規則失效、被 base 蓋過，第一嫌疑是該規則被包進了 `@layer`——移出層即恢復。

### 5.2 字體載入時序（FOUT）
`@import` 必須在 `:root` 之前；放後面會「無樣式閃爍」（FOUT）。

### 5.3 反白 icon 對比
`--color-accent` 太淺（如淡米色）時，active toggle 的白 icon 反白看不見。檢查 `--color-accent` 與 `#fff` 對比 ≥ 4.5。

### 5.4 直角承諾
`--radius-md > 0` 與現行主題不一致；破例（柔軟風格）須在主題檔註明並修 `principles.md`。

### 5.5 別在主題寫佈局結構
不要寫 `width` / `padding` / `margin` / `display`（§1 裝飾佔位幾何為唯一例外）。要改佈局 = 改主檔 base。**現存主題仍殘留少量結構屬性**（`#paper-content` padding、`.figure` margin、`.byline` 間距等）＝ 歷史遺留、待 §8 THEME-DEDUP 上移；新主題勿再新增。

### 5.6 主題 localStorage 持久化
主檔已實作切換的 localStorage 持久化（key: `madpro-theme`），新主題只要按本指南定義 token，無需寫 JS。切換流程：用戶於 `#theme-modal` 選主題 → JS 改 `#theme-link.href` + `localStorage.setItem` → 下次載入自動套用。

---

## 6. 多主題切換

runtime 切換：JS 改 `#theme-link.href = 'themes/kahn.css'` + `localStorage`。兩主題只要都符合本指南（unlayered + 必備 token），切換無痛。切換 UI 見風格 Modal（§7）。

---

## 7. 使用者自訂 CSS 上傳與後端連動規格（RAG-1 R2 子項 B/D/H）

> 對應：`web_server.py::upload_theme` + `static/index.html` 風格 Modal 上傳連動
> **相容保證**：上傳的 CSS 不含 `@layer` → 天然 unlayered → 恆勝主檔 base（§3），無需了解層機制。

### 7.1 API 規格
**Endpoint**：`POST /api/themes/upload`
**Request**：`multipart/form-data`；`file`：`.css`（≤ 100KB）
**Response 200**：
```json
{ "filename": "<sanitized_name>.css", "url": "/static/themes/<name>.css" }
```
**Error**：`400`（副檔名非 `.css` / sanitize 後空 / 路徑無效）、`413`（> 100KB）

### 7.2 安全性過濾（5 道防線）
1. **副檔名限制**：僅 `.css`（`file.filename.lower().endswith(".css")`）
2. **檔名 sanitize**：`re.sub(r"[^a-zA-Z0-9_-]", "_", base_stem)` + 連續底線壓縮 + 前後 strip
3. **MIME 檢查**：依副檔名（FastAPI / Starlette 內部）
4. **大小限制**：100KB 上限（防 DoS）
5. **路徑強制**：寫入 `static/themes/`、`resolve()` 後確保未離開目錄

### 7.3 前端整合
- 風格 Modal 內「上傳 CSS」按鈕 → 觸發隱藏 `<input type="file" accept=".css">` → 上傳 endpoint
- 成功：`#theme-link.href = response.url` + `localStorage.setItem(THEME_KEY, themeName)` + 更新 dropdown
- 失敗：`alert()` 顯示 error.detail

### 7.4 資源目錄
- 上傳目標：`static/themes/<sanitized>.css`；自動 `mkdir(parents=True, exist_ok=True)`
- 既有預設主題 `kahn/kandinsky/mies/nara.css` 不受影響

### 7.5 相關文件
- 後端：`web_server.py::upload_theme` / 前端：`static/index.html#theme-modal` 內 `theme-upload-btn` / `theme-upload-input` / 測試：`tests/test_themes_upload.py`（5 pytest）

---

## 8. 結構去重方向（THEME-DEDUP·後續 plan）

> FE-CSS-GOV C3 縮版只立契約（本檔）+ 清 `#demo-bar` 死碼；**主題結構去重整包移交 THEME-DEDUP**（因 C3 舊審計未涵蓋後補的裝飾 CSS、需完整重審）。

THEME-DEDUP 將對**全部**主題 CSS 完整審計，依本契約落地：
- **共用結構**（4 主題完全同值，如 `#paper-content h2 { border-bottom: var(--divider-w) solid var(--color-divider); padding-bottom: var(--space-2) }`）→ **上移 base**（`content.css`），主題刪除。
- **異值結構**（如 `#paper-content` padding、`.figure` margin、`.byline` 間距、`figcaption` margin-top）→ **token 化**（`--token` 入 globals tokens 層、base 讀 token、主題僅覆 token 值）。
- **裝飾佔位幾何**（§1 例外，如 Kahn `.ph::before`）→ **保留於主題**、不上移。
- 完成後主題檔＝純白名單屬性 + token 覆寫 + 裝飾幾何；`css-architecture.md` 登記主題白名單全量表。
