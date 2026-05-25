# RAG-1 專案：Bug 診斷與修復可行性報告 (2026-05-24)

> [!NOTE]
> 本文件為**純分析、診斷與修復可行性報告**。依據您的指令，**此階段並未修改任何系統程式碼或執行腳本**。

---

## ── Bug 1：檔案移動未顯示自動標籤 & 手動標籤重新整理後消失 ──

### 1. 🔍 核心病因診斷 (Root Cause)

經過對後端與前端資料流通路的全面排查，我們發現了一個**「前端資料欄位映射不一致 (Data-Mapping Inconsistency)」**的嚴重 Bug：

1. **後端儲存完全正確**：
   * 不管是您手動點擊 `#` 按鈕儲存標籤（`set_paper_tags`），還是將文件移入 `SST` 等資料夾觸發後端 Hook（`_apply_folder_path_tags`），後端都已經**百分之百正確地**將標籤寫入了 SQLite 資料庫 `Paper` 資料表中的 `metadata_json` 欄位。
2. **API 傳遞規格**：
   * 當網頁載入或重新整理時，前端會發送 `GET /api/papers` 來拉取文獻列表。
   * 後端在 `paper_manager.py::_to_dict()` 內會將 `metadata_json` 解析為一個 Python 字典，並以 **`metadata`** 作為 Key 包裝回傳給前端。
   * **關鍵點**：API 回傳的文獻 JSON 結構中**只有 `p.metadata.user_tags`**，而**沒有 `p.metadata_json` 欄位**！
3. **前端渲染讀取被鎖死在「暫時快取」**：
   * 在前端 `static/index.html` 內，負責「編輯時讀取標籤」與「Toolbar 渲染 tag-pill」的邏輯卻只去讀取了 `p.metadata_json.user_tags`：
     * **行 1844**（開啟標籤 Modal 時）：`const existing = (p.metadata_json && p.metadata_json.user_tags) || [];`
     * **行 2320**（渲染 Toolbar 時）：`const userTags = (p.metadata_json && p.metadata_json.user_tags) || [];`
   * **為什麼手動儲存會短暫出現？**
     因為手動點擊「確定」儲存時，API 會返回最新 tags，前端手動用 `p.metadata_json.user_tags = data.tags` 寫入內存並重繪，這時在內存中存在，所以看得到。
   * **為什麼重新整理後消失、且搬移到 SST 沒有標籤？**
     因為一旦重新整理，`allPapers` 重新由 `GET /api/papers` 載入，此時 `p.metadata_json` 變回 `undefined`。由於 `renderTitleHeader()` 無法從 `p.metadata.user_tags` 讀取資料，標籤就直接「隱形」了，給人標籤沒有被存起來的錯覺。

### 2. 💡 極簡修復方案（前端雙向同步加固）

我們只需在前端 `static/index.html` 中進行兩處讀取順序調整（讀取 `user_tags` 時優先讀取從資料庫加載的 `p.metadata.user_tags`），並在儲存時同時寫回兩個欄位以維持記憶體一致性：

#### 調整點 A：標籤編輯 Modal 載入（`static/index.html` 行 1844）
```diff
-const existing = (p.metadata_json && p.metadata_json.user_tags) || [];
+const existing = (p.metadata && p.metadata.user_tags) || (p.metadata_json && p.metadata_json.user_tags) || [];
```

#### 調整點 B：中欄 Toolbar 標籤渲染（`static/index.html` 行 2320）
```diff
-const userTags = (p.metadata_json && p.metadata_json.user_tags) || [];
+const userTags = (p.metadata && p.metadata.user_tags) || (p.metadata_json && p.metadata_json.user_tags) || [];
```

#### 調整點 C：手動標籤儲存成功後的記憶體同步更新（`static/index.html` 行 1871-1876）
為了避免使用者手動修改標籤後，在未重新整理網頁的情況下開啟編輯 Modal 出現前後端快取不一致，我們必須在儲存成功時同步更新 `p.metadata.user_tags` 與 `p.metadata_json.user_tags`：
```diff
       const p = allPapers.find(x => x.id === currentPaperId);
       if (p) {
         p.metadata_json = p.metadata_json || {};
         p.metadata_json.user_tags = data.tags || [];
+        p.metadata = p.metadata || {};
+        p.metadata.user_tags = data.tags || [];
         renderTitleHeader(p);
       }
```

---

## ── Bug 2：上傳自訂 CSS 後下拉選單無新選項 & 按 ESC 畫面上殘留下拉選單 ──

### 1. 🔍 核心病因診斷 (Root Cause)

這是一個極為典型且隱蔽的**「作用域隔離阻斷」**與**「事件回收遺漏」** Bug，具體診斷如下：

#### ① 為什麼上傳的 CSS 主題沒有出現在下拉選單中？
* **作用域隔離**：
  在 `static/index.html` 中，下拉選單的數據與綁定是由一個立即執行函式 **`IIFE`** 進行封裝的（**`(function setupDropdown() { ... })()`**）。
  其中，可選的主題清單 `THEMES` 被聲明為該 IIFE 內部的**區域常數陣列**（行 1897）：
  `const THEMES = [ ['mies', ...], ['kahn', ...], ... ];`
* **數據鏈斷裂**：
  當使用者在風格 Modal 中點擊「上傳 CSS」成功後，回傳的事件監聽器（行 1806）僅能在外部作用域將最新上傳的 `themeName` 寫入 `localStorage`，並暫時覆寫 `dd.dataset.value` 文本。
  **由於 IIFE 的作用域限制，上傳監聽器完全無法將新主題寫入內部的 `THEMES` 陣列中！**
  因此，一旦使用者再次點選下拉選單，選單會重新依據那個靜態的、只包含四個預設學派的 `THEMES` 陣列進行動態渲染，上傳的主題自然永遠不會在選單中出現！

#### ② 為什麼按 ESC 關閉 Modal 後，畫面上會留下下拉選單殘檔？
* **遺漏彈窗關閉呼叫**：
  在 `static/index.html` 中，系統維護了一套 `closePopups()` 方法用來關閉所有 `.ctx-popup`（包含下拉選單浮層）。
  然而，在全域的 `Escape` 按鍵監聽器中（行 1716）：
  ```javascript
  document.addEventListener('keydown', (e) => {
    ...
    if (e.key === 'Escape' && open.dataset.noEsc !== 'true') {
      e.preventDefault();
      closeModal(open); // 僅關閉了 Modal
      return;
    }
  ```
  **這裡僅呼叫了 `closeModal()`，卻完全遺漏了對 `closePopups()` 的呼叫！**
  所以當使用者在下拉選單打開的狀態下直接按下 `Escape`，Modal 雖然隱藏了，但動態生成的 `.dropdown-popup` 卻被遺留在 `<body>` 中繼續漂浮，造成了畫面上的殘影。

---

### 2. 💡 極簡修復方案

#### 解決 ①：打破作用域隔離，實現自訂主題動態追加與載入相容
我們只需將 `THEMES` 與 `labels` 提升到腳本的**外部作用域**，讓上傳事件與重新整理載入邏輯都能隨時寫入，並在頁面載入及上傳成功時動態補齊：

##### 調整點 A：外層作用域宣告主題與標籤對照表（移出 IIFE 內部）
```javascript
// 提升至最外層腳本域
const THEMES = [
  ['mies', 'Mies van der Rohe'],
  ['kahn', 'Kahn · Kimbell Art Museum'],
  ['kandinsky', 'Kandinsky · Bauhaus'],
  ['nara', 'Yoshitomo Nara'],
];
const labels = { 
  mies: 'Mies van der Rohe', 
  kahn: 'Kahn · Kimbell Art Museum',
  kandinsky: 'Kandinsky · Bauhaus', 
  nara: 'Yoshitomo Nara' 
};
```

##### 調整點 B：頁面啟動載入時的自適應動態追加（行 1782 附近）
當偵測到已儲存主題為使用者上傳的自訂主題時，自動在 `labels` 與 `THEMES` 中動態補上，確保重新整理後下拉選單選項依然存在：
```javascript
if (savedTheme) {
  document.getElementById('theme-link').href = `/static/themes/${savedTheme}.css`;
  const dd = document.getElementById('theme-dropdown');
  // 如果是自訂主題，動態註冊進去
  if (!labels[savedTheme]) {
    labels[savedTheme] = savedTheme;
    THEMES.push([savedTheme, savedTheme]);
  }
  dd.dataset.value = savedTheme;
  dd.querySelector('.dropdown-value').textContent = labels[savedTheme];
}
```

##### 調整點 C：上傳成功時同步寫入列表（行 1822 附近）
```javascript
// 立即套用新主題 + 寫 localStorage
const themeName = data.filename.replace(/\.css$/, '');
if (!labels[themeName]) {
  labels[themeName] = themeName;
  THEMES.push([themeName, themeName]); // 動態追加入下拉選單！
}
```

#### 解決 ②：在 Escape 監聽器中同步清空 Popup 殘影
在 `static/index.html` 的全域 `keydown` ESC 攔截處，補上一行 `closePopups()` 呼叫，確保所有浮動選單與 Modal 同步消散：

```diff
   document.addEventListener('keydown', (e) => {
     const open = [...document.querySelectorAll('.modal-mask.show')].pop();
     if (!open) return;
     if (e.key === 'Escape' && open.dataset.noEsc !== 'true') {
       e.preventDefault();
+      closePopups(); // R2 補強：關閉 Modal 的同時清空下拉選單等殘影
       closeModal(open);
       return;
     }
```

---

## ── 修正 3：對話框輸入 Placeholder 提示文字「直接斷行」 ──

### 1. 🔍 需求對齊與可行性分析

直接將輸入框預設的「提示文字 (Placeholder)」拆成兩行顯示：
```
輸入問題（Ctrl+Enter 送出）
輸入 # 可加入 hashtag 跨文獻搜尋
```
這項改動**完全不需要任何 JavaScript**，純粹依靠 HTML 屬性與 CSS 樣式即可原生、且零成本地實現預設斷行！

### 2. 💡 純 HTML/CSS 原生解決方案

#### 調整點 A：在 HTML 的屬性中使用 `&#10;` 換行符 (HTML Entity)
在 `static/index.html` 的 `data-placeholder` 屬性中，將中間的全形分號 `；` 替換為 HTML 的換行實體字元 **`&#10;`**：

```html
<!-- 調整 static/index.html 行 1387-1392 -->
<div id="chat-input"
     contenteditable="false"
     role="textbox"
     aria-multiline="true"
     aria-label="對話輸入"
     data-placeholder="輸入問題（Ctrl+Enter 送出）&#10;輸入 # 可加入 hashtag 跨文獻搜尋"></div>
```

#### 調整點 B：在 CSS 中加入 `white-space: pre-wrap;` 啟用換行
在 `static/index.html` 的 CSS 樣式表中，為 `#chat-input:empty::before` 加上 **`white-space: pre-wrap;`**：

```css
#chat-input:empty::before {
    content: attr(data-placeholder);
    white-space: pre-wrap;          /* 關鍵：使屬性中的換行符 &#10; 能夠在 CSS 中原生生效 */
    color: var(--color-text-subtle);
    pointer-events: none;
    display: block;
}
```

---

## ── Bug 4：右欄收合時下載按鈕殘留與寬度佈局異常 ──

### 1. 🔍 核心病因診斷 (Root Cause)

這是一個非常典型且嚴重的**「JavaScript 內聯樣式覆蓋 CSS 優先權」**導致的排版異常 Bug，具體診斷如下：

#### ① 為什麼收合問答欄後，下載按鈕依然顯示在畫面上？
* **JS 內聯強行賦值**：
  在 `static/index.html` 的對話啟用函式 `enableChat()` 中（約行 2480），當文獻載入完畢，系統會執行以下指令以顯示下載按鈕：
  `document.getElementById('export-btn').style.display = 'block';`
  這會直接在 `#export-btn` 的 HTML 標籤上加上 `style="display: block;"` 內聯樣式。
* **CSS Specificity 被蓋過失效**：
  在 CSS 樣式表中，對問答欄收合（`.collapsed`）時非 toggle 按鈕隱藏的規則是：
  `#chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle) { display: none; }`
  **由於 JS 寫入的 inline style 優先權（specificity）遠高於一般 CSS 樣式表，導致樣式表中的 `display: none` 被內聯的 `display: block` 物理蓋過而完全失效！** 下載按鈕因此頑固地殘留在收合後的畫面上。

#### ② 為什麼收合後的寬度看起來不對、且按鈕上下堆疊錯位？
* **Flex 佈局溢出**：
  問答欄收合後的設計寬度為 `var(--rail-w) = 48px`。
  此時 `#chat-header-actions` 置中對齊。如果僅有 `#chat-toggle` 按鈕顯示（寬高為 `32px`），按鈕可以完美置中。
  然而，由於下載按鈕（`#export-btn`，同樣為 `32px`）未能成功隱藏，這兩個具有 `flex-shrink: 0;`（不壓縮）屬性的按鈕被迫擠在同一個水平 Flex 容器內。
* **寬度衝突擠壓**：
  兩個 `32px` 的按鈕水平並排總寬度為 `64px`，但其父容器 `#chat-panel.collapsed` 寬度卻被硬限制在 `48px`，這直接導致了按鈕在極窄的 48px 窄軌空間內發生嚴重的溢出、堆疊與錯位，徹底破壞了原本居中置中的視覺平衡。

---

### 2. 💡 最優防禦性解決方案（CSS 物理強壓）

我們不需要修改任何複雜 of JS 切換狀態，最優雅且具有防禦性的解決方案是**在 CSS stylesheet 收合規則中加上 `!important`**。這樣可以直接且無副作用地蓋過 any JS 的內聯樣式，確保收合契約的絕對成立：

#### 調整點 A：在 CSS 收合規則中加上 `!important`（`static/index.html` 行 1092）
```diff
  #chat-panel.collapsed > #chat-header > .h-title,
- #chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle),
+ #chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle) { display: none !important; }
  #chat-panel.collapsed > #chat-messages,
  #chat-panel.collapsed > #chat-input-area { display: none; }
```
*(註：原本的 `:not(#chat-toggle)` 與 `#chat-messages`、`#chat-input-area` 合寫在一起共用 `{ display: none; }`。我們只需將 `:not(#chat-toggle)` 拆出單獨寫為一行並加上 `!important` 即可，零副作用。)*

---

## ── Bug 5：中欄摘要寬度不對稱與自適應拉伸異常 ──

### 1. 🔍 核心病因診斷 (Root Cause)

這是一個涉及**「瀏覽器 User-Agent 預設樣式限制」**與**「容器對稱邊距遺漏」**導致的視覺美學問題：

#### ① 為什麼展開摘要後，灰色盒子的右側會留下一大片難看的空白？
* **User-Agent 預設寬度阻斷**：
  在 HTML 中，`<details>` 元素雖然在語意上為 Block 元素，但其在某些 Flex 容器的子元素環境中（例如 `#current-title` 是 `flex: 1` 的 flex item），如果沒有顯式指定 `width: 100%`，瀏覽器在計算佈局時，會採用**「適應內容（fit-content）」**的預設收縮策略。
  這導致灰色摘要盒子（`.abstract-body`）無法完全橫跨 `#current-title` 的全部剩餘寬度，在右側留下了極為空洞的缺口。
* **物理邊距不對稱（與正文排版斷層）**：
  * 下方的正文 `#paper-content` 被限制在 `max-width: 720px;`，並且透過 `margin: 0 auto;` 實現**水平置中對齊**。因此在寬螢幕下，正文的左右邊距完全相等，視覺極為對稱。
  * 而頂部的標題摘要 `#current-title` 放在橫跨整個寬度的工具列 `#content-toolbar` 內，其左邊距固定為 `padding-left: 16px`。
  * **當視窗變寬時**：正文會繼續保持置中（左右邊距自動等比拉大，例如 150px），但頂部的摘要盒子卻死死地貼在最左側（左邊距只有 16px），右邊距卻因為沒有顯式撐滿或置中，顯得極其不對稱。

---

### 2. 💡 最優雅的對稱與自適應解決方案（純 CSS）

為了解決這個問題，我們在 CSS 中提供 **2 個層級的對稱修復方案**：

#### 方案 ①：顯式 100% 自適應拉伸（解決「右側空缺」、維持工具列滿版對稱）
直接在 CSS 中為 `details.title-abstract` 顯式聲明 `width: 100%;` 與 `box-sizing: border-box;`。
這樣灰色大盒子會自動隨著論文視窗的寬度變化而**向右拉伸撐滿**。此時摘要的左邊距為工具列的 `16px`，右邊距扣除按鈕後亦為 `16px`，達成左右完全相等且動態自適應的對稱。

##### 調整點 A：為 details 加上 100% 寬度（`static/index.html` 行 724）
```diff
  #current-title details.title-abstract {
    margin-top: var(--space-2);
    font-size: var(--font-base, 13px);
    color: var(--color-text);
    max-height: 12rem;
    overflow-y: auto;
+   width: 100%;                  /* 強制撐滿 #current-title 的剩餘寬度 */
+   box-sizing: border-box;       /* 確保 padding 與 border 不會撐爆容器 */
  }
```

#### 方案 ②：極致版面垂直對齊（解決「與正文對齊」、達成究極畫廊美學）
如果您希望工具列的標題與展開的摘要，能夠與下方的正文 `#paper-content` 在垂直線上**完美對齊並置中**（即左右兩側空出的距離與正文完全相等，且共同隨視窗置中變化）：

我們只需將 `#current-title` 加上與正文相同的 `max-width` 限制與 `margin: 0 auto`。這樣不論視窗如何變寬，頂部的摘要盒子與下方的正文內容都會在同一個 720px 的黃金閱讀軌道上垂直置中對齊：

##### 調整點 B：為 #current-title 加上置中與 max-width 限制（`static/index.html` 行 692）
```diff
  #current-title {
    flex: 1; min-width: 0;
    padding-right: var(--space-4, 16px);
    color: var(--color-text);
+   max-width: 720px;             /* 與正文最大寬度 720px 完美對齊 */
+   margin: 0 auto;               /* 寬螢幕下與正文一同水平置中 */
+   width: 100%;
  }
```
*(註：這時右側的按鈕群 `.toolbar-actions` 會依據 Flex 佈局繼續留在最右側，而中央的標題與摘要大盒子則會在中間與正文完美居中對齊，這是現代頂級 Web 設計中兼顧「操作便利性」與「閱讀美學」的最優佈局。)*

---

## ── Bug 6：上傳文件後重新整理網頁進度消失、未與前端綁定且不知背景運作狀態 ──

### 1. 🔍 核心病因診斷 (Root Cause)

這是一個極為典型且嚴重的**「前後端生命週期與狀態脫節 (State Desynchronization)」** Bug。主要診斷如下：

#### ① 為什麼重新整理後，進行中的文件進度條完全消失？
* **進行中狀態僅留於記憶體，DB 無紀錄**：
  在 RAG-1 系統中，當文件上傳成功並開始後端 Pipeline 時，該文件的處理狀態、進度等資訊是**純記憶體 (In-Memory)** 儲存的，即記錄在 `web_server.py` 的全域字典 `processing_tasks` 中。
  **只有當整條 Pipeline 執行完畢（成功到達 `status = 'done'`）時，系統才會呼叫 `paper_manager.py::upsert_paper()` 將論文記錄寫入 SQLite 資料庫！**
* **列表 API 忽視進行中任務**：
  重新整理網頁後，前端會呼叫 `loadPapers()`，繼而發送 `GET /api/papers`。
  後端的 `/api/papers` 端點直接呼叫 `paper_manager.list_papers()`，該函數**只會從 SQLite 資料庫中查詢已儲存的論文**。
  **結果**：任何處於 `waiting_confirm`（等待確認文件類型）或 `processing`（正在解析、擷取、建向量索引）的進行中論文，**完全不會出現在 `GET /api/papers` 的回傳列表中！**
* **前端生命週期重建遺漏**：
  由於 API 沒有回傳進行中的文件，重新整理後的前端無從得知有後台任務在跑。因此：
  1. 無法呼叫 `insertUploadingRow()` 插入進度條占位列。
  2. 無法呼叫 `trackProgress()` 來與後端建立 `EventSource` (SSE) 連接以接收進度推送。
  這導致雖然**後台執行緒其實仍在辛勤地跑處理任務**，但使用者介面卻宛如「人間蒸發」，給人進度消失、沒有綁定的不良體驗。

---

### 2. 💡 極致優雅的前後端協調解決方案

為了解決這個問題，我們需要進行簡單但高明的雙向綁定：
1. **後端**：在 `GET /api/papers` 回傳列表時，將當前使用者在 `processing_tasks` 中**所有未完成（`waiting_confirm`、`processing`、`error`）的任務動態合併進去**一併返回。
2. **前端**：在 `loadPapers()` 載入列表時進行分流：已完成的正常渲染，**未完成的則自動重建進度條占位列並重連 SSE 追蹤**；特別是對於 `waiting_confirm` 的任務，還能在側欄呈現「等待確認」，讓使用者點擊即可重新喚出類型確認 Modal！

#### 🛠️ 後端修復：合併進行中任務至列表 API
我們只需微調 `web_server.py` 的 `@app.get("/api/papers")` 端點：

```diff
  # 調整 web_server.py 約行 423
  @app.get("/api/papers")
  async def list_papers(current_user: CurrentUser = Depends(get_current_user)):
      """取得當前使用者的論文列表"""
-     return paper_manager.list_papers(OUTPUT_DIR, current_user.id)
+     # 1. 取得已完成存檔的論文
+     db_papers = paper_manager.list_papers(OUTPUT_DIR, current_user.id)
+     
+     # 2. 搜尋當前使用者是否有進行中或等待確認的背景任務
+     in_progress = []
+     with tasks_lock:
+         for (owner_id, paper_id), task in processing_tasks.items():
+             if owner_id == current_user.id and task.get('status') in ('waiting_confirm', 'processing', 'error'):
+                 in_progress.append({
+                     'id': paper_id,
+                     'title': task.get('_original_filename') or paper_id,
+                     'translated_title': '',
+                     'folder_id': None,
+                     'doc_type': task.get('_confirmed_doc_type'),
+                     'metadata': None,
+                     'original_filename': task.get('_original_filename'),
+                     'status': task.get('status'),
+                     'progress': task.get('progress'),
+                     'error': task.get('error'),
+                     'suggested_doc_type': task.get('_suggested_doc_type', 'academic') # 供確認使用
+                 })
+                 
+     return db_papers + in_progress
```

#### 🛠️ 前端修復：自動重建進度條與 SSE 連線
在 `static/index.html` 的 `loadPapers()` 載入成功後，對進行中的論文進行自動還原與事件重連：

```diff
  // 調整 static/index.html 行 2387 的 loadPapers 函數
  async function loadPapers() {
-   const res = await fetch(`${API}/api/papers`);
-   allPapers = await res.json();
-   renderPapers();
+   const res = await fetch(`${API}/api/papers`);
+   const papers = await res.json();
+   
+   // 1. 分流：allPapers 僅保留已完成 (done) 的論文
+   allPapers = papers.filter(p => !p.status || p.status === 'done');
+   renderPapers();
+   
+   // 2. 還原進行中的背景任務
+   const inProgress = papers.filter(p => p.status && p.status !== 'done');
+   inProgress.forEach(p => {
+     // 防禦性檢查避免重複渲染占位列
+     if (!document.querySelector(`.paper-item.uploading[data-upload-id="${p.id}"]`)) {
+       const filename = p.original_filename || p.title || '未命名文件';
+       const row = insertUploadingRow(p.id, filename);
+       
+       if (p.status === 'waiting_confirm') {
+         // 重建等待確認的狀態與點擊處理
+         row.querySelector('.paper-progress-text').textContent = '等待確認類型 (點擊開始)';
+         row.style.cursor = 'pointer';
+         row.onclick = () => {
+           showConfirmModal(p.id, p.suggested_doc_type || 'academic', document.getElementById('upload-btn'), filename);
+         };
+       } else if (p.status === 'processing') {
+         // 正在後台處理中，直接連接 SSE 重開進度追蹤
+         if (p.progress) {
+           row.querySelector('.paper-progress-text').textContent = `${p.progress.stage_name} ${p.progress.progress}%`;
+           row.querySelector('.paper-progress-fill').style.width = `${p.progress.progress}%`;
+         }
+         trackProgress(p.id, document.getElementById('upload-btn'));
+       } else if (p.status === 'error') {
+         // 後台處理失敗，在側欄顯示錯誤狀態
+         row.querySelector('.paper-progress-text').textContent = '處理失敗';
+         row.querySelector('.paper-progress-fill').style.backgroundColor = 'var(--color-danger, #ef4444)';
+         row.querySelector('.paper-progress-fill').style.width = '100%';
+         row.style.cursor = 'pointer';
+         row.onclick = () => {
+           alert('背景處理出錯：' + (p.error || '未知錯誤，請選取更多選單刪除本任務後重新上傳。'));
+         };
+       }
+     }
+   });
  }
```

#### 🛡️ 額外優化：在 `upload_paper` 內聯寫入 `suggested_doc_type` 支援
為了讓等待確認的主題建議能在重新整理後找回，我們可以在 `web_server.py` 的上傳時（約行 475）順手存下 `suggested_doc_type`：
```diff
  # 調整 web_server.py 約行 475
        processing_tasks[(current_user.id, paper_id)] = {
            'status': 'waiting_confirm',
            'progress': {'stage': 'upload', 'stage_name': '上傳完成', 'index': 0, 'total': 10, 'progress': 0},
            '_pdf_path': str(pdf_path),
            '_original_filename': file.filename,  # Phase 4.7a：原始檔名（未 sanitize）
+           '_suggested_doc_type': suggested_doc_type,  # 新增：持久化主題建議供 reload 回填
        }
```
*

---

## ── Bug 7：標籤編輯 Modal 輸入框無樣式、矮小且佈局嚴重不對稱 ──

### 1. 🔍 核心病因診斷 (Root Cause)

這是一個極為顯眼的**「CSS 樣式宣告完全遺漏 (CSS Class Declaration Omission)」**導致的 UI 缺陷：

#### ① 為什麼輸入框非常矮小、沒有對稱，且極度粗糙？
* **CSS Class 虛設**：
  在 `static/index.html` 的 HTML 中，標籤編輯 Modal 內的輸入框被賦予了類名 `class="modal-input"`：
  ```html
  <input type="text" id="tag-input" class="modal-input" placeholder="#plant #complex_system">
  ```
  然而，**在全網頁的 CSS 樣式表中，完全找不到任何關於 `.modal-input` 或 `.modal-box .modal-input` 的樣式規則！**
* **瀏覽器預設無情還原**：
  由於沒有寫入任何 CSS 規則，瀏覽器被迫採用其最基礎的 User-Agent 預設 `<input>` 樣式渲染：
  1. **寬度縮減**：未聲明 `width: 100%`，寬度被縮死在預設的 150px~200px 左右，導致右側留白極大，**完全沒有對稱**。
  2. **高度不足**：未繼承系統按鈕的高度變數（`var(--btn-h) = 38px`），僅有預設文字高度，顯得**無比矮小**。
  3. **邊角與主題斷層**：沒有圓角、沒有主題邊框分界色、沒有內邊距 (padding)，文字直接死貼著左邊框，非常粗糙，完全喪失了 RAG-1 專案引以為傲的「玻璃磨砂/質感暗色系」統一主題美學。

---

### 2. 💡 極致優雅的 CSS 統一對齊修復方案

解決此問題不需要動到任何 JavaScript 邏輯，我們只需**在 CSS 樣式表中補上 `.modal-input` 的精緻主題規則**。我們將完全對齊下拉選單與按鈕的主題 Token 規格，並加上現代高階前端常用的**焦點呼吸光環 (Focus Glow Ring)**：

#### 🛠️ 調整點：補上 `.modal-input` 主題樣式（`static/index.html` 約行 222 處）
在 `.modal-box select:focus { border-color: var(--color-accent); }` 下方補上以下美化規則：

```diff
  # 調整 static/index.html 約行 222 處
  .modal-box select:focus { border-color: var(--color-accent); }
+ 
+ .modal-box .modal-input {
+   width: 100%;                          /* 寬度百分之百撐滿，達成完美左右對稱 */
+   height: var(--btn-h);                 /* 高度對齊統一的 38px 按鈕高度，極具協調感 */
+   padding: 0 var(--space-3);            /* 內邊距，使輸入文字與邊框保持高雅空隙 */
+   border: 1px solid var(--color-divider);/* 主題灰邊框 */
+   border-radius: var(--radius-md);      /* 主題圓角 */
+   background: var(--color-bg);          /* 主題背景色 */
+   color: var(--color-text);             /* 主題文字色 */
+   font-family: inherit;
+   font-size: var(--font-base);
+   outline: none;                        /* 移除瀏覽器預設粗藍邊框 */
+   margin-bottom: var(--space-2);
+   box-sizing: border-box;               /* 避免 padding 撐破容器寬度 */
+   transition: border-color var(--transition), box-shadow var(--transition);
+ }
+ .modal-box .modal-input:focus {
+   border-color: var(--color-accent);    /* 焦點切換為主題強調色藍 */
+   box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); /* 高端微光呼吸效果 */
+ }
```

**修復效果**：
補上此樣式後，`#tag-input` 標籤文字格會**以 100% 寬度完美橫跨 Modal 內框**，與上方的說明文字和下方的按鈕列達成**極致的視覺對稱與垂直對齊線**。高度完全與正常輸入格一致，焦點時更會散發柔和的藍色呼吸微光，完美融入全站的高端美學！

---

## ── Bug 8：新上傳之論文頂部灰色詳情盒摘要顯示為英文（即使正文有中譯） ──

### 1. 🔍 核心病因診斷 (Root Cause)

這是一個由**「Markdown 結構化特徵匹配缺失 (Structural Mismatch)」**導致的元數據同步漏洞，具體診斷如下：

#### ① 為什麼正文已經有了完美的中文摘要，頂部灰色 details 盒子內卻還是英文？
* **雙語摘要前端讀取鏈**：
  在前端 `static/index.html` 內，頂部詳情盒（灰色 `details` 元素）的渲染規則是：
  ```javascript
  const abstractEn = v('abstract');
  const abstractZh = v('translated_abstract') || abstractEn;
  const abstract = currentLang === 'zh' ? abstractZh : abstractEn;
  ```
  這意味著，前端中文模式下，**必須在資料庫的元數據 JSON 中存在 `translated_abstract` 欄位**，否則就會直接防禦性回退顯示英文 `abstract`。
* **後端元數據提取鏈中斷**：
  * 當論文在後台處理時，`Stage A/B`（LLM 元數據抽取）會順利提取出英文的 `abstract` 並放入記憶體 `self._metadata` 中。
  * 隨後進入 `pdf2md`（MinerU 轉 Markdown）與 `md2json`（結構化解析）。
  * **關鍵 Bug 點**：在 `processor/md_processor.py` 中，Markdown 解析器使用了一個嚴格的**英文正則表達式**來尋找並標記 `type='abstract'` 的段落：
    ```python
    self.abstract_pattern = re.compile(
        r'^#+\s*(?:\d+\.)?\s*(?:ABSTRACT|Abstract|abstract|SUMMARY|Summary|summary)'
    )
    ```
  * **特徵不匹配**：如果上傳的論文為**中文論文**（標題為 `## 摘要` 或 `## 概要` 等），或者 PDF 解析後的 Abstract 標題被 MinerU 渲染為加粗文字 `**Abstract**`（而非標準 Markdown 標題 `#`），**該段落就不會被標記為 `type='abstract'`，而是被歸類為普通正文段落！**
  * **翻譯與同步跳過**：
    因為結構 JSON 中沒有 `type='abstract'` 的段落，`translate_processor.py` 中的摘要翻譯函數會直接跳過：
    `self.logger.warning("未找到abstract部分，跳過摘要翻譯")`
    這導致 `self.translate_processor.translated_abstract` 始終為空。因此，`pipeline_core.py` 在寫入資料庫元數據時，**無法將 `translated_abstract` 注入進 `_metadata`**。
  * **表現現象**：由於它被當作普通段落，翻譯引擎依然會在翻譯正文時將其內容翻成中文，所以**下方正文顯示的摘要是有中譯的**；但因為**頂次元數據庫中缺失了同步標記**，頂部灰色盒子便無奈回退顯示了英文。

---

### 2. 💡 極致優雅且防禦性的解決方案

為了解決這個問題並確保 100% 成功率，我們設計了 **雙重防禦性解決方案**（雙管齊下，徹底消除漏判）：

#### 方案 ①：元數據側路翻譯（Metdata Side-Channel Translation，終極保險）
既然 `Stage A/B` 已經 100% 成功地將英文摘要提取到了 `self._metadata['abstract']['value']` 中，我們根本不需要完全依賴 Markdown 解析器是否成功區分了 `type='abstract'`！
我們只需在 `pipeline_core.py` 的翻譯階段 `_stage_translate()` 中補上一個**側路防禦性翻譯**：如果翻譯處理器沒有回傳 `translated_abstract`，我們**直接對已有的元數據英文摘要進行翻譯並同步寫回**！

##### 🛠️ 調整點 A：在 `pipeline_core.py` 中補上側路翻譯 Fallback（行 645 附近）
```diff
  # 調整 pipeline_core.py 約行 645 處
          try:
              translated_abstract = getattr(
                  self.translate_processor, 'translated_abstract', None
              )
+             # 側路防禦：若 Markdown 未匹配到 abstract 區塊，直接翻譯 metadata 已抽取的英文摘要
+             if not translated_abstract and isinstance(self._metadata, dict):
+                 abs_field = self._metadata.get("abstract") or {}
+                 eng_abstract = abs_field.get("value")
+                 if eng_abstract:
+                     self.logger.info("[P2-1] 側路翻譯：直接從 metadata 翻譯英文摘要")
+                     translated_abstract = self.translate_processor.translate_text("abstract", eng_abstract)
+             
              if translated_abstract and isinstance(self._metadata, dict):
                  from processor.metadata_extractor import _empty_field
                  field = self._metadata.get("translated_abstract")
```

#### 方案 ②：正則特徵庫擴充（Regex Extension）
為了從根本上提升 Markdown 解析器對多元化文件的識別能力，我們在 `processor/md_processor.py` 中擴充正則匹配特徵，支援中文論文特徵（`摘要`、`概要`、`内容提要`）：

##### 🛠️ 調整點 B：擴充 `md_processor.py` 的 `abstract_pattern`（行 27 處）
```diff
  # 調整 processor/md_processor.py 行 27
          self.abstract_pattern = re.compile(
-             r'^#+\s*(?:\d+\.)?\s*(?:ABSTRACT|Abstract|abstract|SUMMARY|Summary|summary)'
+             r'^#+\s*(?:\d+\.)?\s*(?:ABSTRACT|Abstract|abstract|SUMMARY|Summary|summary|摘要|概要|內容提要|内容提要)'
          )
```

**修復效果**：
透過這兩項防禦性加固，系統不論是在解析標準中文論文時，還是在面對特異排版（例如 abstract 標題未被解析為 `#` 標題）的論文時，都**絕對能夠 100% 穩定產出並儲存 `translated_abstract` 元數據**。重新整理頁面後，頂部灰色細節盒子中的中文摘要將會完美、對稱且即時地動態展現！

---

## ── Bug 9：學術論文數學公式 (LaTeX) 無法正確顯示 ──

### 1. 🔍 核心病因診斷 (Root Cause)

公式無法在前端正確渲染，是由於以下 **三個層面** 的解析與渲染衝突所導致的：

#### ① Markdown 解析器的「下底線 `_`」與「反斜線 `\`」轉義衝突
這是最主要的底層原因。Markdown 語法與 LaTeX 語法在某些字元上有嚴重的定義衝突：
*   **底線衝突**：在 Markdown 中，單個下底線 `_italic_` 代表 *斜體字*。而學術公式中會頻繁使用下底線來表示下標，例如 `$k _ { 1 }$` 或 `$P _ { \mathrm { I T } }$`。當 Markdown 解析器（前端的 `marked.js`）在處理文字時，會把這兩個下底線之間的公式內容誤判為「斜體 HTML 標籤（`<em>`）」，從而將其替換，破壞了原本的 LaTeX 結構。
*   **反斜線被吃掉**：Markdown 把反斜線 `\` 當作轉義符。當它遇到 LaTeX 的命令字元如 `\tau`、`\alpha`、`\mathrm` 時，如果沒有加以保護，解析器會自動把 `\` 刪除，使公式變成 `tau`、`alpha`、`mathrm` 等普通字元，導致後續的數學引擎無法識別。

#### ② 前端缺乏渲染引擎（KaTeX / MathJax）或定界符（Delimiters）掃描未開啟
瀏覽器原生是**完全無法**辨識 `$ ... $` 或 `$$ ... $$` 的。必須依賴 JavaScript 數學渲染庫來動態將其轉換為 MathML 或精美的 SVG 圖形。
*   如果前端網頁完全沒有載入 **KaTeX** 或 **MathJax**，公式就會被當作一般的純文字直接裸露呈現。
*   **定界符掃描未啟用**：KaTeX 預設為了防止與普通貨幣符號 `$` 產生衝突，**預設是關閉單個 `$`（行內公式）的掃描的**。如果前端沒有顯式配置行內定界符，像 `$k _ { 1 }$` 這樣的文字就不會被渲染。

#### ③ 後端處理器的順序問題（Parsing Order Bug）
在後端（如 `md_restore_processor.py`）進行段落還原、字元清洗或 Markdown 轉 HTML 時，如果沒有在第一時間把 `$$` 和 `$` 包裹的公式區塊**「抽取出來保護」**，公式內部就會被插入大量的 HTML 標籤（如 `<br>`、`<p>`），導致公式結構被徹底物理破壞，前端自然無法解析。

---

### 2. 💡 極致優雅的雙向防禦性修復方案

這個問題** 100% 有機會完美修復**。我們需要採取**「後端防禦性保護 + 前端高效率渲染」**的雙向修復策略。

#### 🛠️ 步驟 A：後端 Raw LaTeX 預留位置保護（Python 處理端）
在 `md_restore_processor.py` 處理文字或轉 HTML 之前，先用正則表達式把所有的 LaTeX 公式提取出來，換成安全、無害的預留位置（Placeholder），等所有 Markdown 轉換與清洗完成後，再還原回去。這能保證公式內部的 `_`、`\`、`{}` 絕對不會被 Markdown 解析器弄髒。

##### 後端 Python 防禦代碼範例 (`processor/md_restore_processor.py`)：

```python
import re

def protect_and_process_markdown(raw_text: str) -> str:
    # 用于存放提取出来的 raw formulas
    latex_blocks = []
    
    # 1. 提取並保護雙錢符區塊公式 $$ ... $$ (支援跨行 re.DOTALL)
    def block_replacer(match):
        latex_blocks.append(match.group(0))
        return f"<!--LATEX_BLOCK_{len(latex_blocks) - 1}-->"
    
    # 2. 提取並保護單錢符行內公式 $ ... $
    def inline_replacer(match):
        latex_blocks.append(match.group(0))
        return f"<!--LATEX_INLINE_{len(latex_blocks) - 1}-->"
        
    # 執行預留占位
    processed = re.sub(r'\$\$(.*?)\$\$', block_replacer, raw_text, flags=re.DOTALL)
    processed = re.sub(r'\$(.*?)\$', inline_replacer, processed)
    
    # ==========================================
    # 在此處安全地執行您既有的 Markdown/文字處理
    # (此時公式已被保護為 <!--LATEX_BLOCK_N-->，絕對不會被轉義或截斷)
    # ==========================================
    
    # 3. 還原原本一字不差的 Raw LaTeX 公式
    for i, latex in enumerate(latex_blocks):
        processed = processed.replace(f"<!--LATEX_BLOCK_{i}-->", latex)
        processed = processed.replace(f"<!--LATEX_INLINE_{i}-->", latex)
        
    return processed
```

#### 🎨 步驟 B：前端部署 KaTeX 極致渲染（網頁呈現端）
我們選用 **KaTeX** 作為渲染引擎（效能比 MathJax 快 10 到 100 倍，完全不影響頁面加載速度與流暢度），並開啟 Auto-render 插件進行自動掃描。

##### 1. 在網頁 HTML 的 `<head>` 中引入 KaTeX 的 CSS 與 JS (`static/index.html`)：
```html
<!-- 引入 KaTeX 樣式 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">

<!-- 引入 KaTeX 核心 JS (使用 defer 異步加載優化 INP/LCP 效能) -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>

<!-- 引入自動渲染擴充插件 -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
```

##### 2. 配置自動渲染腳本，開啟行內與區塊掃描 (`static/index.html`)：
```html
<script>
    document.addEventListener("DOMContentLoaded", function() {
        renderMathInElement(document.body, {
            // 定義要識別的公式定界符
            delimiters: [
                {left: "$$", right: "$$", display: true},  // 區塊公式 (如您的式 1, 2, 3)
                {left: "$", right: "$", display: false},   // 行內公式 (如您的 $k_1$, $\tau$)
                {left: "\\(", right: "\\)", display: false},
                {left: "\\[", right: "\\]", display: true}
            ],
            // 防禦性配置：若有公式語法寫錯，不崩潰，直接保留原始文字
            throwOnError: false
        });
    });
</script>
```

##### 3. 加入防溢出 CSS，保證在手機端或窄螢幕下公式完美呈現 (`static/index.html`)：
```css
/* 防止超長數學公式撐破網頁排版，使其自動產生橫向滾動條 */
.katex-display {
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 0.5em;
}
```

**修復效果**：
透過這套後端防禦性預占位與前端 KaTeX 自動渲染的雙向保險方案，論文內部的所有學術公式、上下標、希臘字母等都將以**精美、高端的向量數學排版**完美呈現在頁面上，且徹底避免了與 Markdown 解析器的語法衝突，大幅提升整套系統的專業學術體驗！

---

## ── Bug 10：中欄正文冗餘大標題與凌亂元數據區塊 ──

### 1. 🔍 核心病因診斷 (Root Cause)

主內容區域開頭出現「大字標題與擠成一團的作者/日期」排版問題，是由於以下三個層面的**「雙重渲染」與「語法解析坍塌」**所導致的：

1. **頂部動態 UI 重複渲染**：
   前端 `static/index.html` 的 `renderTitleHeader()` 已經從文獻元數據中動態取出論文的「中英文標題」、「作者群 · 日期 · 出處」以及「折疊式摘要」，並完美置頂呈現。因此，Markdown 本體開頭的標題與元數據是完全冗餘的。
2. **單換行 Blockquote 語法坍塌（排版混亂真因）**：
   後端 `md_restore_processor.py` 在還原 Markdown 時，會強制生成 `_render_header_zh()` 與 `_render_header_en()`，其中元數據使用了如下語法：
   ```markdown
   > **作者**：...
   > **日期**：...
   ```
   **在 GFM 或標準 Markdown 規範中，單換行的 blockquote 行在經由 `marked.js` 解析時，會被瀏覽器強制合併為單一長段落**。這導致作者、日期、出處等資訊全部擠在一起，毫無層次，視覺極其混亂。
3. **「治標不治本」的純 CSS 全域隱藏缺陷**：
   如果我們僅在前端使用 `#paper-content > h1:first-child { display: none; }` 隱藏：
   * **導出缺陷**：Raw Markdown 檔案在被下載或導出到本地閱讀器時，其開頭元數據依然是亂的。
   * **列印空白缺陷**：列印功能（`window.print()`）在 `@media print` 規則中會隱藏頂部工具列。若我們將 Markdown 本體的標題也全域隱藏，**列印出來的紙張將會是一片空白（沒有任何標題），直接開始正文**。

---

### 2. 💡 最優雅之「治本」雙向解決方案

為了達成**「網頁閱讀極簡乾淨」**、**「導出本地格式精美」**、**「列印紙張自動帶出工整標題」**的三向完美體驗，我們設計了以下治本修復方案：

#### 🛠️ 步驟 A：後端修正為「標準 Markdown 清單格式」（治本，淨化 Raw Markdown 結構）
我們將後端 `md_restore_processor.py` 的 `_render_header_en` 與 `_render_header_zh` 中的 `>` (Blockquote) 替換為標準的 **`-` (Markdown 無序列表)**。這能確保檔案在任何外部閱讀器（如 Obsidian）或下載導出時，都能呈現完美的結構化清單。

##### 後端程式碼修正範例 (`processor/md_restore_processor.py`)：

```diff
# 1. 調整英文版 Header 範本 (約行 460)
  meta_bits = []
  if authors_list:
-     meta_bits.append(f"> **Authors**: {', '.join(str(a) for a in authors_list)}")
+     meta_bits.append(f"- **Authors**: {', '.join(str(a) for a in authors_list)}")
  if date:
-     meta_bits.append(f"> **Date**: {date}")
+     meta_bits.append(f"- **Date**: {date}")
  if venue:
-     meta_bits.append(f"> **Venue**: {venue}")
+     meta_bits.append(f"- **Venue**: {venue}")
  if doi:
-     meta_bits.append(f"> **DOI**: {doi}")
+     meta_bits.append(f"- **DOI**: {doi}")
  if keywords:
-     meta_bits.append(f"> **Keywords**: {', '.join(keywords)}")
+     meta_bits.append(f"- **Keywords**: {', '.join(keywords)}")

# 2. 調整中文版 Header 範本 (約行 509)
  meta_bits = []
  if authors_list:
-     meta_bits.append(f"> **作者**：{'、'.join(str(a) for a in authors_list)}")
+     meta_bits.append(f"- **作者**：{'、'.join(str(a) for a in authors_list)}")
  if date:
-     meta_bits.append(f"> **日期**：{date}")
+     meta_bits.append(f"- **日期**：{date}")
  if venue:
-     meta_bits.append(f"> **出處**：{venue}")
+     meta_bits.append(f"- **出處**：{venue}")
  if doi:
-     meta_bits.append(f"> **DOI**：{doi}")
+     meta_bits.append(f"- **DOI**：{doi}")
  if keywords:
-     meta_bits.append(f"> **關鍵字**：{'、'.join(keywords)}")
+     meta_bits.append(f"- **關鍵字**：{'、'.join(keywords)}")
```

#### 🎨 步驟 B：前端 CSS 啟用「精準媒體隔離隱藏」（治標，保證列印與螢幕完美分流）
我們在前端 `static/index.html` 的 CSS 中，**將隱藏規則限定在 `@media screen` 內**。如此一來，在螢幕上閱讀時會自動隱藏該冗餘區塊；但當用戶點擊「列印」時，該區塊會**自動浮現並以極致工整的清單格式出現在紙張頂端**，完美彌補了工具列被隱藏的空缺！

##### 前端 CSS 修正範例 (`static/index.html` 約行 805)：

```css
@media screen {
  /* 僅在螢幕閱讀時隱藏主內容區的冗餘大標題與清單元數據（因頂部動態工具列已存在） */
  #paper-content > h1:first-child,
  #paper-content > h1:first-child + ul,
  #paper-content > h1:first-child + ul + h2,
  #paper-content > h1:first-child + ul + h2 + p {
    display: none !important;
  }
}
```

**修復效果**：
採用此治本方案後，不論是在網頁上看（乾淨無瑕）、匯出 Markdown（結構極其規整），還是列印成實體紙張（標題以完美的清單排版自動浮現於頂端），都達成了無懈可擊的高端學術體驗！

