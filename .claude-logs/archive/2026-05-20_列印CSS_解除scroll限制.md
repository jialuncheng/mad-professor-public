# 2026-05-20 @media print：解除 viewport 高度與 scroll 限制

只在現有 `@media print {` 區塊**最前面**新增 3 個規則塊（19 行）。既有規則
順序與內容皆未動；未動其他 CSS / JS / HTML / 後端。

## 真因（轉述）
`#content-area { overflow: hidden }` + `#paper-content { flex: 1; overflow-y: auto }`
使 `#paper-content` 為 scroll 容器；列印時瀏覽器以容器當前 viewport 截圖，
整篇 markdown 被截到一頁可見區。

## 修改 diff（純新增於 @media print 區塊開頭）
```diff
@@ @media print {
+    /* 解除 viewport 高度與 scroll 限制，讓 #paper-content 展開到實際內容高度
+       （否則 #content-area overflow:hidden + #paper-content flex:1+overflow-y:auto
+       會把列印限制在當前可見範圍）。 */
+    html, body {
+      height: auto !important;
+      overflow: visible !important;
+    }
+    main, #content-area {
+      height: auto !important;
+      overflow: visible !important;
+      display: block !important;     /* 解除 flex 限制 */
+    }
+    #paper-content {
+      height: auto !important;
+      max-height: none !important;
+      overflow: visible !important;
+      flex: none !important;          /* 解除 flex: 1 */
+    }
+
     /* 隱藏所有非文章區塊 */
     #sidebar,
```
位置：原 `@media print {` 之後立即、隱藏選擇器之前。既有
`body, html, main { background; margin; padding }` 與 `#paper-content {
width/padding/color/font }` 規則**不變、未重複**——本次新增僅 height /
overflow / display / flex / max-height 這 5 個屬性，與既有屬性集**不重疊**。

## 為何 3 個規則塊都需要
- `html, body`：解除文件根層的高度/捲動上限。
- `main, #content-area`：原本 `display:flex` 並把子節點切版；列印改 block 讓
  `#paper-content` 不被 flex 容器高度約束（`overflow:hidden` 也一併解除）。
- `#paper-content`：自身 `flex:1`（讓主 flex 容器把它撐高）+ `overflow-y:auto`
  → 改 `flex:none`、`height/max-height:auto`、`overflow:visible`，內容自然
  撐開到完整 markdown 高度，瀏覽器分頁正常。

## 驗證
- 純 CSS 改動；`py_compile` / `pytest` 不需跑（後端零變動）。
- 端到端（待 OrcStack 重啟）：開長文（800-vdc / ALi 簡報多頁）→ `#print-btn`
  → 預期列印預覽顯示**完整內容跨多頁**，不再只印一頁可見區。
- 短文：行為等同前版（內容本就不超一頁時無視覺差異）。

## 推薦 commit message
```
fix(ui/print): 解除 viewport 高度與 scroll 限制，列印完整文章

前一輪 @media print 隱藏非文章 UI 後仍只印「當前可見範圍」：
#content-area overflow:hidden + #paper-content flex:1+overflow-y:auto
使 #paper-content 為 scroll 容器，瀏覽器列印只截可視 viewport。

在現有 @media print 區塊開頭補 3 個規則塊（純新增、既有規則順序不變）：
- html, body：height:auto + overflow:visible
- main, #content-area：同上 + display:block（解 flex 限制）
- #paper-content：height/max-height:auto + overflow:visible + flex:none

不重疊既有 body/html/main padding/margin 與 #paper-content width/padding/
color/font 規則。未動 JS / HTML / 其他 CSS / 後端。

驗證：純 CSS；端到端待瀏覽器列印長文（800-vdc / ALi 簡報）→ 預期完整
分頁，而非單頁截斷。
```

## 不可動清單（已遵守）
- 既有 @media print 規則：未動（純插於最前）
- 其他 CSS：未動
- JS / HTML DOM / 後端 .py：未動
- 未引入新檔案 / 新 CDN
