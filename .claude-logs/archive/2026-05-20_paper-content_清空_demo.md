# 2026-05-20 清空 #paper-content prototype demo 內容

只動 `static/index.html` 一處：#paper-content 內所有 demo HTML（環義自由車
demo 文章）清空，容器保留。其他容器、CSS、JS、後端皆未動。

## 修改 diff（純刪除）
```diff
@@ -1071,23 +1071,7 @@
       <svg width="16" height="16" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-6-6a1.5 1.5 0 0 1 0-2l6-6"/></svg>
       從左側選擇文件
     </div>
-    <div id="paper-content">
-      <h1>2026 年環義自由車賽第九站前瞻、路線分析、奪冠熱門與預測：10% 陡坡考驗，Jonas Vingegaard 有望縮小與粉紅衫的差距</h1>
-      <p class="byline">by Rúben Silva ·&nbsp;Saturday, 17 May 2026</p>
-
-      <figure class="figure">
-        <div class="ph">FIGURE 1 — 頒獎台合影（Picture: Sirotti）</div>
-        <figcaption>這張照片呈現了職業自行車手在賽事頒獎典禮上的場景，左側可見具代表性的冠軍獎盃，中間的運動員身著印有贊助商標誌的黃色領騎衫。</figcaption>
-      </figure>
-
-      <p>2026 年環義自由車賽（Giro d'Italia）將於 5 月 8 日至 31 日舉行。這是本賽季的第一場大環賽（Grand Tour），共設有 21 個賽段，車手們將穿越義大利眾多標誌性城市、傳奇的阿爾卑斯山脈（Alps），以及許多險峻的賽段——每一個賽段都可能改寫總成績榜的位置。</p>
-
-      <h2>第九站路線概覽</h2>
-      <p>本日賽段全長 215 公里，最後 18 公里連續爬坡，最大坡度達到 10%。冠軍極可能在最後 5 公里的單飛中產生，而陡坡也將是粉紅衫競爭者拉開差距的關鍵舞台。</p>
-
-      <h3>賽段重點</h3>
-      <p>過去三年於同樣賽段勝出的選手中，有兩位都是後段加速能力突出的爬坡型車手；今年 <em>Jonas Vingegaard 已展現出在中海拔的回升狀態</em>，他將是頭號奪冠熱門。</p>
-    </div>
+    <div id="paper-content"></div>
   </main>
```
net: −16 行（17 行 demo 內容 → 0；容器折成單行 +1）。

## 順帶確認 — 其他容器掃描結果（**僅回報，不自行刪改**）

逐一檢視內含文字的容器（行號為改動後）：

| 容器 | 內容 | 判定 | 處置（待 baron） |
|---|---|---|---|
| **`#current-title`**（h2，行 1059）| 「2026 年環義自由車賽第九站前瞻、路線分析…粉紅衫的差距」（同 Giro demo 文章標題的長串）| **🔴 DEMO 內容** | 業務 JS `loadPaper()` 會以 `textContent = title` 覆寫；但**初次載入未選文件前**，工具列 h2 會直接秀此 demo 標題（content-toolbar 在 prototype 預設可見、無 `display:none`）。屬此次漏清的同類問題，**未自行處置**。|
| `#empty-state`（行 1070–1073）| 圖示 + 「從左側選擇文件」| ✅ 真實 UI 文字 | 保留 |
| `#help-title` / `#help-box` 內 ol/step-note（行 935–946）| 上傳流程說明、PDF 限制、Ctrl+Enter 提示 | ✅ 真實 UI 文字（help modal 內容）| 保留 |
| `#theme-title` / `#theme-box` 內文 + dropdown 預設值（行 956–964）| 「切換風格 / 選擇介面美學風格…」、預設 `Kandinsky · Bauhaus`、「後端尚未實作」註記 | ✅ 真實 UI 文字（theme modal）| 保留（dropdown 預設標籤 `Kandinsky · Bauhaus` 與 `data-value="kandinsky"` 一致；行為在 prototype `setupDropdown` 範圍）|
| `#confirm-title` / `#confirm-desc` / `#doc-type-dropdown` 預設（行 976–982）| 「選擇文件類型 / 請選擇文件類型…」、預設 `學術論文` | ✅ 真實 UI 預設 | 保留（業務 `showConfirmModal` 會依偵測結果覆寫）|
| `#paper-list` / `#folder-tree` / `#chat-messages`（行 1030/1032/1109）| 三者皆已先前清空為空容器 | ✅ 已清 | — |
| 三 modal 容器 `#action-modal` / `#notice-modal`（其後行）| body 為空 `<p id="action-body"></p>` / `<p id="notice-body"></p>` | ✅ 由 `customConfirm/customAlert` 動態填 | 保留 |

→ **唯一另一處仍含 demo 內容 = `#current-title` h2**。**未自行刪除**（依「不自選刪不刪」），列此待 baron 決定是否一併清空（清空後初次載入工具列會空白／不顯示，需配合 content-toolbar 可見性策略；本身 CSS/inline style 不在本回合可動範圍）。

## 驗證
- **diff stat**：static/index.html 2372 → **2356** 行（−16，與預估一致）
- **node --check**：抽出主 `<script>` body **語法通過**（純 HTML 改動不影響 JS）
- **後端**：`py_compile web_server / paper_manager / pipeline_core` 通過（後端未動）
- 未刪 #paper-content 容器本身、未動其前後任何 HTML、未動 CSS / JS / .py、
  未引入新檔案。

## 推薦 commit message
```
fix(ui): 清空 #paper-content 漏刪的 prototype demo 文章

整檔替換時清單漏列 #paper-content，prototype 內塞了環義自由車 demo
文章，reload 後第一眼會看到此 demo 直到使用者點真文章被覆寫。

清空容器內所有子元素（h1 / byline / figure / 多段內文）為單行
<div id="paper-content"></div>；容器保留供業務 JS marked.parse
動態填入。其他容器、CSS、JS、後端皆未動。

附帶確認其他容器：#current-title h2 仍含同 Giro demo 標題
（loadPaper 後會被覆寫，但首次載入會短暫顯示）— 屬同類漏清，
本次不自行處置，待後續決策。

node --check JS 語法通過；py_compile / pytest 後端不變。
diff：−16 行（純刪除）。
```

## 不可動清單（已遵守）
- 不改 #paper-content 容器本身（保留）／不動其前後 HTML
- 不改其他容器（#folder-tree / #paper-list / #chat-messages / 各 modal）
- 不改任何 CSS
- 不改任何 JS
- 不動任何 .py
- 未引入新檔案
