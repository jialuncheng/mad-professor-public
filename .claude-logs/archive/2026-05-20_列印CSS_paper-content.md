# 2026-05-20 @media print：只印 #paper-content

只動 `static/index.html` `<style>` 區塊末尾、`</style>` 之前**新增** 47 行
`@media print` 規則。未動既有 CSS、未動 JS、未動 HTML DOM、未動後端。

## 新增 CSS diff（純新增）
```diff
@@
   *::-webkit-scrollbar-track { background: transparent; }

+  /* ── 列印：只印中欄文章 ──
+     業務 JS 已將 #current-title 寫進 document.title（print-btn handler），
+     瀏覽器列印時頁眉/頁尾自動帶入；此 CSS 僅負責隱藏非文章 UI。 */
+  @media print {
+    /* 隱藏所有非文章區塊 */
+    #sidebar,
+    #chat-panel,
+    #content-toolbar,
+    #empty-state,
+    #tooltip,
+    .modal-mask {
+      display: none !important;
+    }
+
+    /* 中欄全寬輸出 */
+    body, html, main {
+      background: white !important;
+      margin: 0 !important;
+      padding: 0 !important;
+    }
+    #paper-content {
+      width: 100% !important;
+      max-width: none !important;
+      margin: 0 !important;
+      padding: 16px !important;
+      color: black !important;
+      font-size: 12pt;
+      line-height: 1.6;
+    }
+
+    /* 文章內元素列印優化 */
+    #paper-content h1,
+    #paper-content h2,
+    #paper-content h3 {
+      page-break-after: avoid;
+    }
+    #paper-content img,
+    #paper-content figure {
+      max-width: 100% !important;
+      page-break-inside: avoid;
+    }
+    #paper-content p,
+    #paper-content li {
+      orphans: 3;
+      widows: 3;
+    }
+  }
 </style>
```
位置：插在 `*::-webkit-scrollbar-track` 之後、`</style>` 之前（CSS 區塊末尾）。
規則放主檔 `<style>` 內、`<link id="theme-link">` 之前——後者按既有「主題
CSS 後出者勝」覆寫色彩 token，但 @media print 內所有屬性皆帶 `!important`
（含 color/background/margin/padding/width/max-width/font-size/line-height），
覆寫順序不受主題影響。

## 確認所有 id / class 都存在
| 選擇器 | grep 計數 | 備註 |
|---|---|---|
| `id="sidebar"` | 1 | ✓ |
| `id="chat-panel"` | 1 | ✓ |
| `id="content-toolbar"` | 1 | ✓ |
| `id="empty-state"` | 1 | ✓ |
| `id="tooltip"` | 1 | ✓ |
| `id="paper-content"` | 1 | ✓ |
| `class="modal-mask"` | 5 | ✓（help/theme/confirm/action/notice 五個 modal）|
| `<main` | 1 | ✓（`<main id="content-area">`）|

## 額外建議的隱藏目標（**回報，未自行加**）
1. **`.ctx-popup`** — 動態建立的「論文 ⋯ / 資料夾 ⋯ / dropdown 列表」浮層
   （CSS 行 575；`.ctx-popup.dropdown-popup` 行 252）。**屬會出現於畫面上的
   floating 元件**，列印當下若仍開著就會被一起印出來。建議加入隱藏清單
   `display: none !important;`。實務上印之前通常會關掉 popup，但保險起見值
   得隱藏。**未自行加**，待 baron 決定。
2. **`#demo-bar` CSS 殘留**（行 97–128，9 條規則）— prototype 遺留，HTML 已
   刪 → CSS 不命中、列印零影響。**無需加入隱藏**（沒對應 DOM）。為求完整列出。
3. 其他既有 floating：`#tooltip` 已加入；無其他 floating/overlay 元件。
4. `<aside>`（`#sidebar`、`#chat-panel` 皆是 `<aside>`）已被 id 規則涵蓋，
   無需另外用標籤選擇器。

→ **僅 #1（`.ctx-popup` / `.ctx-popup.dropdown-popup`）值得納入**，待 baron。

## 驗證
- **py_compile**：`web_server / paper_manager / pipeline_core /
  processor/md_processor` 通過（後端零改動）。
- **id/class 存在**：上表 8 條全 ✓。
- **CSS only**：未動既有 CSS（純插入新區塊）、未動 JS、未動 HTML DOM、
  未動 .py。
- **端到端**（待 OrcStack 重啟）：開任一論文 → 點 `#print-btn` → 預期列印
  預覽僅顯示 `#paper-content` 內容，全白底、12pt 黑字、頁眉自動帶
  `document.title`（業務 JS print-btn handler 已設）。

## 推薦 commit message
```
feat(ui): 新增 @media print，列印只輸出 #paper-content

業務 JS print-btn handler 已將 #current-title 寫進 document.title，
瀏覽器列印頁眉/頁尾自動帶入；CSS 端只需隱藏非文章 UI。

新增 47 行 @media print（插於 <style> 末尾、</style> 之前）：
- 隱藏 #sidebar / #chat-panel / #content-toolbar / #empty-state /
  #tooltip / .modal-mask（五個 modal 容器統一是 .modal-mask）
- #paper-content 全寬黑白輸出（12pt / line-height 1.6 / 16px padding）
- h1–h3 page-break-after: avoid；img/figure page-break-inside: avoid；
  p/li orphans/widows: 3

未動既有 CSS / JS / HTML DOM / 後端。所有 id/class 已 grep 確認存在。

附帶建議（未自行加）：.ctx-popup（動態建立的論文/資料夾 ⋯ 與 dropdown
列表）為畫面 floating 元件，列印時若開著仍會印出；待後續決策是否
加入隱藏清單。
```

## 不可動清單（已遵守）
- 既有 CSS：未動（純新增 @media print 一段）
- JS / HTML DOM：未動
- 後端 .py：未動
- 未引入新檔案
