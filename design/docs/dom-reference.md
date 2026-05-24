# DOM 元件參考字典 · MadPro UI

> 給 Claude Code、新加入的工程師、設計改版者使用。
> 不杜撰、不臆測。每個 id / class 的「**用途、JS 依賴、狀態組合、不可違反的契約**」一次寫清楚。
> 若實際程式碼與本文件衝突 → 以**原 `index.html`** 為準，本文件需更新。

---

## 0. 圖例

- 🔒 **id 契約**：JS 用 `getElementById` 依賴，**改名會破壞功能**
- 🎯 **class 契約**：JS 用 `querySelector` / `classList` 依賴
- 📦 **動態插入**：執行時由 JS 建立的元素
- 🧪 **prototype-only**：本原型為了演示加的；**接入正式 app 時應移除或重綁**
- 🔁 **重複出現**：同類元素多次存在於 DOM

---

## 1. 三欄根容器

| 元素 | 標籤 | id | 角色 | 寬度策略 | 收合 class |
|---|---|---|---|---|---|
| 左欄 文件列表 | `#sidebar` | `240px` 固定 | `flex-shrink:0` | `.collapsed` → 48px rail |
| 中欄 文章閱讀 | `#content-area` | `flex:1` | 吸收剩餘寬度 | 不可收合 |
| 右欄 AI 問答 | `#chat-panel` | `380px` 固定 | `flex-shrink:0` | `.collapsed` → 48px rail |

**契約**
- 三欄之間以 `border-right` / `border-left: var(--divider-w) solid var(--color-divider)` 分隔
- `.collapsed` 切換由各欄的漢堡按鈕觸發；無條件可關 = 中欄
- 收合後內容不消失，只變窄為 rail；漢堡 icon 永遠可點

---

## 2. 三欄標題列

### 2.1 左欄 `<h1>` （`#sidebar > h1`）

```
┌────────────────────────────────────────┐
│ 文件列表          [+]            [☰]   │  toolbar-h = 48px
└────────────────────────────────────────┘
```

| 元素 | id | 用途 |
|---|---|---|
| 標題文字 | `.title` | 「文件列表」固定 |
| 新資料夾 | 🔒 `new-folder-btn` | 在當前資料夾或根新增 |
| 收合 | 🔒 `sidebar-toggle` | toggle `#sidebar.collapsed` |

按鈕群容器：`.toolbar-actions`（flex normal gap）

### 2.2 中欄 `#content-toolbar`

Phase 4.7c 修正 3：`#current-title` 為 toolbar 子元素，取原 h2 的 `flex:1`
槽位；toolbar 為 flex row + `align-items: flex-start`，允許 title 多行展開
時 icon 仍貼齊頂部。

```
┌────────────────────────────────────────────────────┐
│ <title-zh / title-en / meta / abstract>  [⇄] [🖨] │  min-height 48px，可多行
└────────────────────────────────────────────────────┘
```

| 元素 | id | 用途 |
|---|---|---|
| 擴充標題區 | 🔒 `current-title` (`<header>`) | multi-row：title-zh / title-en / title-meta / details.title-abstract（詳見 §4.2 / `components.md §7.4`） |
| 切換中/英 | 🔒 `lang-toggle` | toggle `currentLang` 並重抓內容 |
| 列印 | 🔒 `print-btn` | `window.print()`；瀏覽器標題取 `#current-title .title-zh` |

**契約**
- 未選文件時 `#content-toolbar { display: none }`（loadPaper 內設 `display:flex`）
- `align-items: flex-start` + `.toolbar-actions { padding-top:4px }` 使 icon 與 title 第一行對齊
- title 區與 actions 區於 toolbar 內為 flex row 並列

### 2.3 右欄 `#chat-header`

```
┌────────────────────────────────────────┐
│ AI 問答      [🔍]  [⬇]            [☰]   │  48px
└────────────────────────────────────────┘
```

| 元素 | id | 用途 |
|---|---|---|
| 標題 | `.h-title` | 「AI 問答」固定 |
| 搜尋 toggle | 🔒 `web-search-toggle` | `.active` 控 `useWebSearch` boolean |
| 匯出 MD | 🔒 `export-btn` | `location.href = export` |
| 收合 | 🔒 `chat-toggle` | toggle `#chat-panel.collapsed` |

按鈕群容器：🔒 `chat-header-actions`

---

## 3. 左欄內容

### 3.1 資料夾樹 🔒 `#folder-tree`

容器：`max-height: 40%`、可捲、底部 1px 邊。

#### 子元素：📦 `.folder-item`

🔁 多筆。每筆結構：
```html
<div class="folder-item [active] [open]">
  <span class="chevron [empty]">
    <svg>...</svg>            <!-- chevron 圖形；empty 時隱藏 -->
  </span>
  <span class="fname">名稱</span>
  <button class="menu-btn">⋯</button>
</div>
```

| 元件 | 用途 |
|---|---|
| `.active` | 當前選中（filter 模型，唯一） |
| `.open` | 子層展開；持久化於 `localStorage['foldersOpen']` |
| `.chevron.empty` | 沒有子資料夾時隱藏箭頭 |
| `.fname` | flex:1 ellipsis 單行 |
| `.menu-btn` | hover 才顯示；點開 ⋯ popup |

**特殊節點**：「全部」「未分類」是寫死的兩列，無 `.menu-btn`、無 chevron。

### 3.2 論文列表 🔒 `#paper-list`

容器：`flex:1`、可捲。

#### 子元素：📦 `.paper-item`

🔁 多筆。dataset `data-id` 帶論文 UUID。
```html
<div class="paper-item [active]" data-id="{uuid}">
  <div class="paper-item-header">
    <div class="paper-item-titles">
      <div class="paper-title-zh">中文標題</div>
      <div class="paper-title-en">原文標題</div>
    </div>
    <button class="paper-menu-btn">⋯</button>
  </div>
</div>
```

| class | 用途 |
|---|---|
| `.active` | 當前選中 |
| `.paper-title-zh` | 13px / 500 |
| `.paper-title-en` | 12px muted / 2-line clamp |
| `.paper-menu-btn` | hover 才顯示；點開 ⋯ popup |

#### 子元素：📦 `.paper-item.uploading` 🧪
**僅供 prototype 演示**。實際 app 需在上傳開始時由 JS 建立。

```html
<div class="paper-item uploading" data-upload-id="{tempId}">
  <div class="paper-item-header">
    <div class="paper-item-titles">
      <div class="paper-title-zh">{檔名}</div>
      <div class="paper-progress">
        <span class="paper-progress-dot"></span>
        <span class="paper-progress-text">{stage_name} {pct}%</span>
      </div>
    </div>
  </div>
  <div class="paper-progress-bar">
    <div class="paper-progress-fill" style="width:{pct}%"></div>
  </div>
</div>
```

| 行為 |
|---|
| 永遠出現在 `#paper-list` 最頂端，**不受 folder filter 影響**（filter 跳過此列） |
| 背景脈動動畫 `paperUploadingPulse` 1.6s |
| `.paper-progress-dot` 點閃動畫 `paperUploadingBlink` 1s |
| **整列 `pointer-events: none`，禁止點擊** |
| 處理完成（SSE `done`）→ 移除此列，重抓 `GET /api/papers` 替換 |

### 3.3 左欄底部 🔒 `#sidebar-bottom`

```
┌────────────────────────────┐
│  [⤺]  [🗑]  [?]  [↑]        │
└────────────────────────────┘
```

容器 class：`.sb-row`（flex, justify-content: space-between）

| id | tooltip | 行為 |
|---|---|---|
| 🔒 `logout-btn` | 退出系統 | `POST /logout` → 導 `/login` |
| 🔒 `cleanup-btn` | 清除殘檔 | confirm → `POST /api/cleanup` → alert |
| 🔒 `help-btn` | 系統介紹 | 開 `#help-modal` |
| 🧪 `theme-btn` | 切換風格 | 開 `#theme-modal`，內部切 `themes/*.css` 連結（**後端未實作**） |
| 🔒 `upload-btn` | 上傳文件 | 選 PDF → `POST /upload` → 開 `#confirm-modal` |

**契約**：四個 icon-only 容器**全部 32×32**，與標題列其他 icon 一致。

---

## 4. 中欄內容

### 4.1 空狀態 🔒 `#empty-state`

未選文件時顯示「← 從左側選擇文件」；選後 `display: none`。

### 4.2 擴充標題區 🔒 `#current-title`（toolbar 子元素）

Phase 4.7c 修正 3。`#current-title` 為 `#content-toolbar` 子元素（取原 h2
的 `flex:1 min-width:0` 槽位），不是獨立區塊。未選文件時 `hidden`；
選後由 `renderTitleHeader(p)` 渲染。

**結構契約**（依 doc_type 分支，缺項靜默省略）
```html
<div id="content-toolbar">
  <header id="current-title">
    <h1 class="title-zh">{titleZh|candidate_name}</h1>
    <p class="title-en">{title 原文}</p>
    <p class="title-meta">{authors}·{date}·{venue}</p>
    <details class="title-abstract">
      <summary>顯示摘要</summary>
      <div class="abstract-body">{abstract}</div>
    </details>
  </header>
  <div class="toolbar-actions">…icon 按鈕…</div>
</div>
```

詳見 `components.md §7.4`。

列印時 `#content-toolbar` 一同隱藏；瀏覽器列印標題取 `.title-zh` 文字。

### 4.3 文章 🔒 `#paper-content`

容器：`flex:1`、可捲。內容由 `marked.parse()` 渲染 Markdown。

**結構契約**
- `max-width` 由主題決定（Mies 860 / Kahn 720）
- 圖片相對路徑會被改寫為 `/api/papers/{id}/images/...`
- h1 / h2 / h3 / p / img / table 樣式由主題定義

---

## 5. 右欄內容

### 5.1 訊息區 🔒 `#chat-messages`

`flex:1`、可捲。內含三種泡泡：

#### 📦 `.msg-user`
```html
<div class="msg-user">{純文字、pre-wrap}</div>
```
- 底色 `--color-accent`、白字、右對齊、max-width 75%

#### 📦 `.msg-ai`
```html
<div class="msg-ai" data-grounding-sources='[...]'>
  <!-- marked 渲染後的 HTML -->
  <div class="msg-sources">來源：<a>...</a></div>   <!-- 可選 -->
  <div class="msg-ai-actions">
    <button class="msg-copy" data-tip="複製"><svg>...</svg></button>
    <button class="msg-regen" data-tip="重新生成"><svg>...</svg></button>
  </div>
</div>
```
- 底色 `--color-bg`、1px border、左對齊、max-width 90%
- `.msg-sources` 用 dashed top border 區隔
- `.msg-ai-actions` 浮在泡泡右下緣 -14px，hover 顯示
- `dataset.groundingSources` 為 JSON 字串，給 `saveChatHistory` 序列化用

#### 📦 `.msg-system`
- 13px subtle 置中提示
- 特殊 id：🔒 `reading-ready-msg` 用於「內容已可閱讀，AI 問答準備中…」

#### 📦 `.chat-empty`
- 「選擇文件後開始提問」或「針對文件提問」二態文案

### 5.2 輸入區 🔒 `#chat-input-area`

`position: relative`（autocomplete dropdown 定位錨點、RAG-1 Phase 2 P2-3 §3.3.5-#4）

| 元素 | 用途 |
|---|---|
| 🔒 `chat-input` (div, contenteditable) | width 100%；Ctrl+Enter 送出；自然撐高 max 240px；輸入 `#` 觸發 hashtag autocomplete；token 為 `.hashtag-token`（contenteditable=false）。**P2-3 後從 textarea 改 contenteditable div**、`.value` → `.textContent.trim()`、`.disabled` → `contenteditable` 屬性、placeholder 改 `data-placeholder` 配對 CSS `:empty::before`。 |
| 🔒 `hashtag-autocomplete` (.ctx-popup.hashtag-popup) | 輸入 `#<prefix>` 觸發；綁容器（`bottom: 100%`）；前 10 筆 + 「...更多」；鍵盤 ↑↓ Enter/Tab Esc + 滑鼠 mousedown 選擇。 |
| ~~`send-btn`~~ | 🧪 **prototype 已移除**，純鍵盤送出；正式 app 是否補回看後續決策 |

---

## 6. 彈出層

### 6.1 Tooltip 🔒 `#tooltip` 🧪

單例元素，由 JS 切換內容與位置。Mies 美學：純白底、1px 黑線、直角。

**契約**
- 任何按鈕加 `data-tip="<2-6 字>"` 即生效
- mouseenter 300ms 後出現於目標**左側**
- 不可同時掛 `title` 屬性（會雙提示）

### 6.2 Popup 📦 `.ctx-popup`

`position: fixed`、append 到 `<body>`，z-index 1000。

兩種觸發源：
1. `.paper-menu-btn` → 論文操作（刪除 / 移動 / 刪除對話 disabled）
2. `.folder-item .menu-btn` → 資料夾操作（改名 / 新增子 / 刪除）

#### Popup 內 button
```html
<button>標籤</button>
<button class="danger">刪除文件</button>    <!-- 紅字 -->
<button class="has-sub">移動到資料夾 ▸</button>
<button disabled>刪除對話</button>           <!-- Phase 3.4 規劃 -->
```

關閉條件：點 popup 外、scroll、resize。

### 6.3 Dropdown Popup 📦 `.ctx-popup.dropdown-popup` 🧪

特殊變體：z-index 1600（蓋過 modal-mask）。位置貼齊 `dropdown-trigger.bottom - 1px`。

### 6.4 Modal

兩個固定 modal：

#### `#help-modal` 🔒 + `#help-box` 🔒
| 元素 | 用途 |
|---|---|
| 🔒 `help-close-btn` | 關閉 |
| 點 mask | 關閉 |

#### `#confirm-modal` 🔒 + `#confirm-box` 🔒
| 元素 | 用途 |
|---|---|
| 🔒 `confirm-desc` | 描述文字（`slides` 偵測時會替換） |
| `#doc-type-dropdown` 🧪 | **prototype 自訂 dropdown**；原版用 `#doc-type-select` (native) |
| 🔒 `confirm-ok-btn` | 推進流程 |
| 點 mask | **不關閉**（流程關鍵 modal） |

#### `#prompt-modal` 🔒 + `#prompt-box` 🔒（BUG-F4 A3 新增、取代瀏覽器原生 `prompt()`）
| 元素 | 用途 |
|---|---|
| 🔒 `prompt-title` | 標題（由 customPrompt({title}) 設定） |
| 🔒 `prompt-body` | 描述文字（由 customPrompt({body}) 設定） |
| 🔒 `prompt-input` | 輸入框（class `.modal-input`、套 §6.3 樣式）；Enter = 確定 |
| 🔒 `prompt-cancel` | 取消（回 `Promise<null>`） |
| 🔒 `prompt-ok` | 確定（回 `Promise<string>`、有 validate 失敗則 customAlert 後不關閉） |
| 點 mask | 關閉（取消） |

**原版相容**：若要還原為 native select，把 `.dropdown` 區塊換回：
```html
<select id="doc-type-select">
  <option value="academic">學術論文</option>
  ...
</select>
```

---

## 7. JS 全域狀態（重要變數）

來自原 index.html，**本 prototype 未實作**全部，僅參考：

| 變數 | 型別 | 用途 |
|---|---|---|
| `currentPaperId` | string \| null | 當前看的論文 UUID |
| `currentLang` | `'zh' \| 'en'` | 中欄當前語言 |
| `isProcessing` | bool | 是否有上傳正在進行（鎖按鈕用） |
| `useWebSearch` | bool | 與 `#web-search-toggle.active` 同步 |
| `paperReadiness` | `Map<paperId, 'reading_ready' \| 'done'>` | 上傳半完成 / 全完成兩態 |
| `currentFolderId` | `'all' \| 'uncategorized' \| number` | 當前資料夾 filter |
| `folders` | flat list | server 回的資料夾 |
| `allPapers` | flat list | server 回的論文 |
| `foldersOpen` | `Set<number>` | 展開的資料夾 id；持久化 localStorage |
| `isStreaming` | bool | SSE 串流中（鎖送出鈕） |

---

## 8. 不可違反的契約（speedrun）

1. **保留所有 🔒 id**：JS 用 `getElementById` 綁定，改名 = 壞
2. **`.collapsed` / `.show` / `.active` 三個 class 名不可改**
3. **`.ctx-popup` 開關機制**：append 到 body、點外面關、scroll 關
4. **訊息泡 class**：`.msg-user` / `.msg-ai` / `.msg-system` / `.msg-sources` / `.chat-empty` 是 `saveChatHistory` 抓取 DOM 的依據
5. **dataset 名稱**
   - `.paper-item[data-id]` = 論文 UUID
   - `.msg-ai[data-grounding-sources]` = JSON 字串
   - `.dropdown[data-value]` = 當前值
6. **paper-readiness 兩態**：`reading_ready` 收合 chat 顯示等候訊息；`done` 展開 chat 解鎖
7. **SSE 結束格式**：`{ done: true, grounding_sources? }` 必須有 `done: true` 才收尾

---

## 9. Prototype 特有（接入時請刪除或重綁）🧪

| 項目 | 位置 | 處理建議 |
|---|---|---|
| `#demo-bar` | body 第一個元素 | 整段刪除 |
| `.paper-item.uploading` 寫死範例 | `#paper-list` 開頭 | 改由 JS 動態插入 |
| `#upload-btn` 點擊 demo 開 confirm-modal | JS 中 `addEventListener` | 改回實際 upload 流程 |
| `#help-btn` 直接開 modal | 同上 | 保留行為 |
| 自訂 `.dropdown` 取代 native select | `#confirm-modal` 內 | 視團隊偏好決定保留或還原 |
| 預設掛載 `themes/mies.css` | `<head>` `<link>` | 視 app 是否支援主題切換決定 |
| `#tooltip` + `data-tip` 系統 | 全域 | 可直接保留進正式 app |
| `#theme-btn` + `#theme-modal` | 左欄底部 + body 末 | **後端未支援前**：localStorage 持久化已實作（key `madpro-theme`）；接後端 API 後改為登入時從 user preferences 讀取 |
| Tooltip 顯示／隱藏延遲 | JS `SHOW_DELAY = 200` / `VISIBLE_DURATION = 800` / `HIDE_DELAY = 100` | 可調整 |

---

## 10. 元件樣式 token 對照

新元件設計時，盡量沿用既有 token。詳見：
- `docs/icon-spec.md` — Icon
- `docs/typography.md` — 字體
- `docs/color-tokens.md` — 色彩
- `docs/spacing.md` — 間距
- `docs/components.md` — 按鈕／Modal／Popup／Tooltip／Dropdown／輸入框
- `docs/api-integration.md` — 後端串接
