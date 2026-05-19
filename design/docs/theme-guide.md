# 主題開發指南 · MadPro UI

> 主題 = `themes/*.css` 單檔。切換主題只需改主檔 `<link href>`。
> 本檔教你**從 0 寫出新主題**。

---

## 1. 主題能控制什麼、不能控制什麼

### ✅ 主題可控
- 色票（所有 `--color-*`）
- 字體（`--font-display` / `--font-body`）、字級、字重、字距、行高
  - ⚠️ **硬規範**：必須是非襯線（sans-serif）字族。詳 `typography.md` §0
- 圓角（`--radius-*`）
- 結構線粗細（`--divider-w`）
- 各標題列／文章區的印刷規則（uppercase / letter-spacing / italic）
- Demo bar 的 credo 文字（用 `::before { content }`）
- 文章 figure 佔位的視覺風格（背景紋路、邊框）
- 中欄 `served` 背景色（Kahn 用 radial-gradient 模擬天光）

### ❌ 主題不可控
- DOM 結構（任何結構性改變屬主檔工作）
- JS 邏輯
- 按鈕尺寸、容器尺寸、間距模矩、icon 規格（屬結構層）
- z-index 層級表（共用契約）

---

## 2. 必填 token 清單

主題 `:root` 必須提供以下 token，否則 fallback 啟動但視覺斷裂：

```css
:root {
  /* 色票 */
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

  /* 結構 */
  --divider-w: 1px | 2px;
  --radius-sm: 0;                  /* 目前所有主題皆 0 */
  --radius-md: 0;

  /* 字體 */
  --font-display: ...;
  --font-body:    ...;
}
```

---

## 3. 必填覆寫規則

主題還須覆寫以下選擇器，否則會繼承主檔 fallback（system-ui 預設不好看）：

```css
body { font-family: var(--font-body); font-size: ... ; }

#content-area { background: var(--color-bg-served); }

#demo-bar { ... font-family ... }
#demo-bar .credo::before { content: "<主題座右銘>"; }

#sidebar h1 .title,
#chat-header > .h-title { font-family / size / weight / spacing / case }
#content-toolbar h2 { 同上，須與 #paper-content h1 同字級 }

#paper-content { max-width / padding }
#paper-content h1 / h2 / h3 / p { font / size / weight / spacing / margin }
#paper-content .byline { font / case / spacing }
#paper-content .figure .ph { 佔位視覺：background / border / font }
#paper-content .figure figcaption { font / italic / center }
```

---

## 4. Step-by-step：建立 `themes/wright.css`

以 Frank Lloyd Wright 風格為例（假設想做）：

### Step 1：拷貝既有主題作起點
```bash
cp themes/mies.css themes/wright.css
```

### Step 2：替換 header 註解
- 主題名、核心信念、視覺語彙（5 行內描述）

### Step 3：色票替換
```css
:root {
  --color-bg: #d2c4a8;           /* Cherokee red 沙暖底 */
  --color-bg-served: #efe6cc;
  --color-surface: #c1b393;
  --color-surface-2: #a99771;
  --color-border: #8a7656;
  --color-border-strong: #604a2c;
  --color-divider: #2e2418;       /* deep oak 結構 */
  --color-text: #1d1610;
  --color-text-muted: #5a4830;
  --color-text-subtle: #8a7656;
  --color-accent: #b13a2a;        /* Cherokee red */
  --color-accent-hover: #8c2d20;
  --color-danger: #6c1f1a;

  --divider-w: 2px;               /* 厚水平線 — prairie 屋簷 */
  --radius-sm: 0;
  --radius-md: 0;

  --font-display: "DM Sans", "PingFang TC", "Microsoft JhengHei", sans-serif;
  --font-body: "DM Sans", "PingFang TC", "Microsoft JhengHei", sans-serif;
}
```

### Step 4：字體載入
若用 Google Font，主題檔最上方加：
```css
@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap");
```

### Step 5：印刷規則調整
參考 mies/kahn 樣本，按主題語彙修：
- Wright 偏好水平強調 → `letter-spacing: 0.04em`、單字寬距
- 標題字重 600（介於 Mies 700 與 Kahn 500 之間）
- 文章 figure 佔位可用 Wright 風的 stained glass 幾何紋（用 CSS grid 或 SVG mask）

### Step 6：Credo 文字
```css
#demo-bar .credo::before { content: "form and function are one"; }
```

### Step 7：掛載
```html
<link rel="stylesheet" href="themes/wright.css">
```

### Step 8：驗證 checklist
- [ ] 三欄分隔線清晰可見
- [ ] icon 在新色票下仍可辨識（特別是 active 反白）
- [ ] 中欄標題與 h1 字級相符
- [ ] dropdown popup、tooltip、modal 樣式正常繼承
- [ ] Credo 文字出現在 demo-bar
- [ ] 字體載入完成前 fallback 不破版（用 `font-display: swap`）

---

## 5. 常見陷阱

### 5.1 CSS 順序問題
主檔 `<style>` 內也定義 `:root`（為 fallback）。**主題 `<link>` 必須在 `</style>` 之後**，靠 CSS 後出者勝覆寫 fallback。

### 5.2 字體載入時序
`@import` 必須在 `:root` 之前；放在後面會出現「無樣式閃爍」（FOUT）幾秒。

### 5.3 反白 icon 對比
若 `--color-accent` 太淺（例如淡米色），active toggle 的「反白」就看不見白 icon。檢查：`--color-accent` 與 `#fff` 對比 ≥ 4.5。

### 5.4 直角承諾
任何 `--radius-md > 0` 都與目前兩個主題不一致；若新主題想破例（例如做柔軟風格），須在主題檔註明並修 `principles.md`。

### 5.5 主題不可影響 layout 數值
不要在主題裡寫 `width:`、`padding:`、`margin:`（少數印刷相關內距除外，如 `#paper-content` `padding`）。改 layout = 改主檔。

### 5.5 主題 localStorage 持久化

`Mad Professor Redesign.html` 主檔已實作主題切換的 localStorage 持久化（key: `madpro-theme`），新主題只要按本指南規範定義 token，無需額外撰寫 JS。

切換流程：
1. 用戶在 `#theme-modal` 選擇主題 → 點「確認切換」
2. JS 改 `#theme-link.href` + `localStorage.setItem('madpro-theme', themeName)`
3. 下次載入時讀 localStorage、自動套用

---

## 6. 多主題並存

若想讓使用者在 runtime 切換：
1. HTML 改為 `<link id="theme-link" rel="stylesheet" href="themes/mies.css">`
2. JS 切換 `themeLink.href = 'themes/kahn.css'`
3. 兩個主題只要都符合本指南，切換無痛
4. 持久化：`localStorage.setItem('theme', 'kahn')` 由你決定

本 prototype **未提供切換 UI**；只示範靜態載入。
