# mad-professor 前端設計交接文件

> 本文件為**現況描述**，供設計師（Claude Design 或人類）在不看程式碼的前提下，
> 完整理解現有介面結構、命名、規範、行為與邏輯，作為重新設計版面的依據。
> 文件只描述「現在是什麼」與「現況痛點」，不含程式碼修改建議。
> 來源：`static/index.html`（單檔，內嵌 CSS 於 `<style>`、JS 於 `<script>`；
> 外部依賴僅 `marked.js` CDN 用於 Markdown 轉 HTML）。

---

## 1. 系統總覽

**mad-professor** 是一套「論文 / 文件 AI 閱讀與問答」單頁 Web 應用：
使用者上傳 PDF → 後端 pipeline 自動解析、翻譯成繁體中文、建立 RAG 向量索引 →
左欄選文件、中欄閱讀全文、右欄對該文件做 AI 問答（可選「開啟搜尋」做
Google grounding）。文件可用資料夾分類。

### 三欄佈局

```
┌────────────┬───────────────────────────┬──────────────────┐
│  #sidebar  │      #content-area        │   #chat-panel    │
│  左：文件   │      中：文章閱讀          │   右：AI 問答     │
│  260px     │      flex:1（自適應）      │   420px          │
│  可收合     │                           │   可收合          │
└────────────┴───────────────────────────┴──────────────────┘
        body: display:flex; height:100vh
```

| 欄 | 容器 id | 寬度 | 彈性 | 收合 |
|---|---|---|---|---|
| 左欄 文件列表 | `#sidebar` | `260px` 固定 | `flex-shrink:0` | `.collapsed` → `width:0;overflow:hidden` |
| 中欄 文章閱讀 | `#content-area` | `flex:1` | 吸收剩餘寬度 | 不可收合 |
| 右欄 AI 問答 | `#chat-panel` | `420px` 固定 | `flex-shrink:0` | `.collapsed` → `width:0;overflow:hidden` |

- 左右欄之間以 `border-right / border-left: 2px solid var(--color-divider)` 分隔。
- 收合行為：點該欄的 `.panel-toggle`（漢堡 icon），對該欄根容器 toggle `.collapsed` class，CSS 寬度 0；無顯式 transition（瞬間收合，`--transition` 僅用於背景色）。
- 整體視覺語彙：Mies van der Rohe 極簡——黑白灰、細邊框、無陰影、極小圓角（2–4px）。

---

## 2. 元件清單（核心章節）

> 「位置」以三欄與其頂部/中部/底部標示。「類型」：容器 / 標題列 / 按鈕 / 輸入 / 清單 / 彈窗 / 動態渲染。

### 2.1 根容器與三欄骨架

| 元件 | DOM id / class | 位置 | 類型 | 功能 |
|---|---|---|---|---|
| 左欄根 | `#sidebar` | 左 | 容器 | 文件列表欄；`.collapsed` 收合 |
| 中欄根 | `#content-area` | 中 | 容器 | 文章閱讀欄 |
| 右欄根 | `#chat-panel` | 右 | 容器 | AI 問答欄；`.collapsed` 收合 |

### 2.2 三欄標題列（皆 `height: var(--toolbar-h)` = 48px）

| 元件 | DOM id / class | 位置 | 類型 | 功能 |
|---|---|---|---|---|
| 左欄標題列 | `#sidebar h1` | 左·頂 | 標題列 | 含 `.title`（「文件列表」）+ `#new-folder-btn`；右側 padding 44px 讓位浮動漢堡 |
| 左欄標題文字 | `#sidebar h1 .title` | 左·頂 | 文字 | 「文件列表」；`flex:1`、單行 ellipsis |
| 中欄工具列 | `#content-toolbar` | 中·頂 | 標題列 | 預設 `display:none`，選文件後顯示；含標題 + 兩 icon 鈕 |
| 中欄文件標題 | `#current-title` (`h2`) | 中·頂 | 文字 | 顯示當前論文標題；`flex:1` 單行 ellipsis |
| 右欄標題列 | `#chat-header` | 右·頂 | 標題列 | 左側 padding 16、右側 padding 44 讓位浮動漢堡；含「AI 問答」+ 動作群 |
| 右欄標題文字 | `#chat-header > span` | 右·頂 | 文字 | 固定文字「AI 問答」 |
| 右欄動作群 | `#chat-header-actions` | 右·頂 | 容器 | flex，間距 `--gap-btn-loose`；含搜尋開關 + MD |

### 2.3 收合按鈕（浮動，`position:fixed; top:8px; 32×32`）

| 元件 | DOM id / class | 位置 | 類型 | 功能 |
|---|---|---|---|---|
| 左欄收合（漢堡） | `#sidebar-toggle` `.panel-toggle` | 浮動，`left:216px` | 按鈕 | toggle `#sidebar.collapsed` |
| 右欄收合（漢堡） | `#chat-toggle` `.panel-toggle` | 浮動，`right:12px` | 按鈕 | toggle `#chat-panel.collapsed` |

### 2.4 左欄內容

| 元件 | DOM id / class | 位置 | 類型 | 功能 |
|---|---|---|---|---|
| 新增資料夾 | `#new-folder-btn` `.icon-only` | 左·頂（h1 右） | icon 按鈕 | 在當前資料夾或根新增資料夾 |
| 資料夾樹容器 | `#folder-tree` | 左·上段 | 清單 | `max-height:38%` 可捲；含固定節點 + 動態樹 |
| 資料夾節點 | `.folder-item`（動態） | 左·上段 | 清單列 | 「全部」「未分類」+ 使用者資料夾；點擊切換 filter |
| └ 展開箭頭 | `.folder-item .chevron` | 同上 | 文字 icon | `▸/▾` 切換子節點顯示（有子才顯示） |
| └ 名稱 | `.folder-item .fname` | 同上 | 文字 | 資料夾名稱，單行 ellipsis |
| └ 選單鈕 | `.folder-item .menu-btn` | 同上 | icon 按鈕 | `⋯`，hover 顯示；開資料夾操作 popup |
| 論文列表容器 | `#paper-list` | 左·中段 | 清單 | `flex:1` 可捲；當前資料夾的論文 |
| 論文項 | `.paper-item`（動態） | 左·中段 | 清單列 | 點擊載入該論文；`.active` 選中 |
| └ 中文標題 | `.paper-title-zh` | 同上 | 文字 | 翻譯標題 |
| └ 原文標題 | `.paper-title-en` | 同上 | 文字 | 原文，最多 2 行 ellipsis、muted |
| └ 操作鈕 | `.paper-menu-btn .icon-only` | 同上 | icon 按鈕 | `⋯`，hover 顯示；開論文操作 popup |
| 左欄底部 | `#sidebar-bottom` | 左·底 | 容器 | flex column；上排次要鈕 + 下排上傳鈕 |
| └ 次要鈕排 | `#sidebar-bottom .sb-row` | 左·底·上排 | 容器 | 三鈕等寬平分，間距 `--gap-btn-tight` |
| └ 說明 | `#help-btn` `.icon-only` | 同上 | icon 按鈕 | 開 `#help-modal` |
| └ 清理殘檔 | `#cleanup-btn` `.icon-only` | 同上 | icon 按鈕 | 呼叫 `/api/cleanup`（先 confirm） |
| └ 登出 | `#logout-btn` `.btn-ghost .icon-only` | 同上 | icon 按鈕 | `/logout` 後導回 `/login` |
| └ 上傳文件 | `#upload-btn` | 左·底·下排 | 主按鈕 | 全寬；選 PDF → 上傳 → 類型確認 |

### 2.5 中欄內容

| 元件 | DOM id / class | 位置 | 類型 | 功能 |
|---|---|---|---|---|
| 切換中英文 | `#lang-toggle` `.icon-only` | 中·頂 | icon 按鈕 | 中/英內容切換；以 `title` 提示下一步 |
| 列印 | `#print-btn` `.icon-only` | 中·頂 | icon 按鈕 | `window.print()`（@media print 隱藏側欄） |
| 空狀態 | `#empty-state` | 中 | 提示 | 未選文件時「從左側選擇文件」 |
| 文章內容 | `#paper-content` | 中 | 動態渲染 | marked 轉出的 HTML；`max-width:860px` 置中 |

### 2.6 右欄內容

| 元件 | DOM id / class | 位置 | 類型 | 功能 |
|---|---|---|---|---|
| 開啟搜尋（toggle） | `#web-search-toggle` `.btn-ghost` | 右·頂 | toggle 文字鈕 | toggle `.active`；控制 chat 是否帶 grounding |
| 匯出 MD | `#export-btn` | 右·頂 | 文字+icon 鈕 | 預設隱藏；下載對話 Markdown（較小字 xs） |
| 訊息區 | `#chat-messages` | 右·中 | 動態渲染 | `flex:1` 可捲；訊息泡泡列 |
| └ 使用者訊息 | `.msg-user` | 同上 | 泡泡 | 黑底白字、右對齊、`max-width:80%` |
| └ AI 訊息 | `.msg-ai` | 同上 | 泡泡 | 白底細框、左對齊、`max-width:95%`、marked HTML |
| └ 來源 | `.msg-sources` | 同上 | 連結列 | grounding 來源；虛線分隔、muted、底線連結 |
| └ 系統訊息 | `.msg-system` | 同上 | 提示 | 置中 muted（如「內容已可閱讀，AI 問答準備中…」） |
| └ 空提示 | `.chat-empty` | 同上 | 提示 | 「選擇文件後開始提問」/「針對文件提問」 |
| 輸入區 | `#chat-input-area` | 右·底 | 容器 | flex，`align-items:flex-end` |
| └ 輸入框 | `#chat-input` (`textarea`) | 同上 | 輸入 | 自動長高（1 行→132px 後捲） |
| └ 送出 | `#send-btn` | 同上 | 主按鈕 | 送出問題；disabled 有專屬灰底 |

### 2.7 彈窗（Modal）

| 元件 | DOM id / class | 類型 | 功能 |
|---|---|---|---|
| 說明框 | `#help-modal` / `#help-box` | 全屏遮罩 Modal | 上傳流程說明；`.show` 顯示；點遮罩或「了解了」關閉 |
| 文件類型確認框 | `#confirm-modal` / `#confirm-box` | 全屏遮罩 Modal | 上傳後選文件類型（下拉 `#doc-type-select`）→「確認，開始處理」 |

> 註：規格曾提到 `type-confirm-modal`，實際只有 `#confirm-modal`（即文件類型選擇框，
> 無另一個獨立 modal）。`#confirm-reason`、`#confirm-desc` 在 CSS 有樣式，
> markup 內僅有 `#confirm-desc`（`#confirm-reason` 為僅存樣式、未使用之殘留）。

### 2.8 浮動選單（Popup，共用 `.ctx-popup`）

| 元件 | 觸發 | 內容 | 說明 |
|---|---|---|---|
| 資料夾操作選單 | `.folder-item .menu-btn`（⋯） | 改名 / 新增子資料夾 / 刪除 | 由 `openPopup()` 動態生成 |
| 論文操作選單 | `.paper-menu-btn`（⋯） | 刪除文件（紅）/ 移動到資料夾 ▸ / 刪除對話（disabled） | 同上 |
| 移動到資料夾 picker | 上者「移動到資料夾」 | 未分類 + 各資料夾（縮排表階層） | 取代上一個 popup |

`.ctx-popup`：`position:fixed; z-index:100; min-width:160px; max-height:260px; 可捲;
細粗邊框`。點選單外任意處關閉（排除 `.ctx-popup / .menu-btn / .paper-menu-btn`）。

---

## 3. 視覺規範（:root design tokens）

> 全部取自 `static/index.html` 的 `:root {}`。設計時請以 token 為單一事實來源。

### 色彩

| Token | 數值 | 用途 |
|---|---|---|
| `--color-bg` | `#ffffff` | 全域背景、泡泡/輸入背景 |
| `--color-surface` | `#fafafa` | 次級表面（ghost 按鈕 hover、panel-toggle 底） |
| `--color-border` | `#e5e5e5` | 一般邊框、清單列 hover 底、分隔線 |
| `--color-border-strong` | `#d4d4d4` | 強邊框（Modal/popup 邊、收合鈕邊） |
| `--color-divider` | `#d4d4d4` | 三欄之間 2px 分隔線 |
| `--color-text` | `#171717` | 主文字色；**亦為選中態實心底色** |
| `--color-text-muted` | `#737373` | 次要文字（原文標題、來源連結） |
| `--color-text-subtle` | `#a3a3a3` | 更弱文字（空提示、系統訊息、disabled 文字） |
| `--color-accent` | `#171717` | 主按鈕底、使用者訊息泡泡底（與 text 同值） |
| `--color-accent-hover` | `#404040` | 主按鈕 hover |
| `--color-danger` | `#dc2626` | 危險操作（刪除文件文字） |

> 注意：`--color-text` 與 `--color-accent` 同為 `#171717`。選中態（folder/paper/
> btn-ghost.active、user 泡泡）統一用「實心 `--color-text`（或 accent）+ 白字」。

### 間距（4px 基準）

| Token | 數值 | 典型用途 |
|---|---|---|
| `--space-1` | 4px | 最小間隙、tight gap 基礎 |
| `--space-2` | 8px | 一般 gap、清單 padding |
| `--space-3` | 12px | 卡片/列 padding、loose gap 基礎 |
| `--space-4` | 16px | 面板內距 `--pad-panel` |
| `--space-5` | 24px | Modal 內距、訊息區 padding |
| `--space-6` | 32px | Modal 大內距、文章上下內距 |
| `--space-8` | 48px | 文章左右內距、空提示上距 |

### 按鈕 / 版面系統（Phase 3.3 規範）

| Token | 數值 | 用途 |
|---|---|---|
| `--btn-h` | `32px` | 所有按鈕高度 |
| `--btn-pad-x` | `var(--space-4)`=16px | 文字按鈕水平內距 |
| `--btn-min-w` | `64px` | 文字按鈕最小寬 |
| `--btn-icon` | `32px` | icon-only 方形邊長、收合鈕邊長 |
| `--toolbar-h` | `48px` | 三欄標題列統一高度 |
| `--pad-panel` | `var(--space-4)`=16px | 面板內距（標題列、底部、輸入區） |
| `--gap-btn-tight` | `var(--space-1)`=4px | 密集（左欄底部三鈕之間） |
| `--gap-btn` | `var(--space-2)`=8px | 一般族群（sidebar-bottom 上下排之間、輸入區） |
| `--gap-btn-loose` | `var(--space-3)`=12px | 標題列按鈕族群之間 |

### 圓角 / 字級 / 過渡

| Token | 數值 | 用途 |
|---|---|---|
| `--radius-sm` | `2px` | 清單列、小圓角 |
| `--radius-md` | `4px` | 按鈕、Modal、輸入框 |
| `--font-xs` | `12px` | 原文標題、step-note、MD 鈕 |
| `--font-sm` | `13px` | ghost 鈕、資料夾名、來源 |
| `--font-base` | `14px` | 內文、主按鈕、標題列 |
| `--font-lg` | `16px` | Modal h3、文章 h3 |
| `--font-xl` | `20px` | 文章 h2 |
| `--font-2xl` | `28px` | 文章 h1 |
| `--transition` | `150ms ease` | 背景/透明度過渡（**收合無 transition**） |

---

## 4. 按鈕系統

共四大類，皆 `height:32px`、`border-radius:4px`、`inline-flex` 置中、`cursor:pointer`。

### 4.1 主按鈕 primary
選擇器群組：`.btn-primary, #upload-btn, #send-btn, #confirm-ok-btn, #help-close-btn`

| 狀態 | 樣式 |
|---|---|
| 預設 | 底 `--color-accent`、白字、同色邊、`font-base`、`min-width:64`、`padding 0 16` |
| hover | 底 `--color-accent-hover`（#404040） |
| disabled | `.btn-primary:disabled` → `opacity:.5; not-allowed`；**但** `#send-btn:disabled` 另有專屬：底/邊 `--color-text-subtle`、not-allowed（覆蓋 opacity 規則） |

代表：上傳文件（全寬、含 `＋` icon）、送出、Modal 的「確認/了解了」（全寬）。

### 4.2 次要按鈕 ghost
選擇器群組：`.btn-ghost, #help-btn, #cleanup-btn, #lang-toggle, #print-btn, #export-btn`

| 狀態 | 樣式 |
|---|---|
| 預設 | 透明底、`--color-text` 字、`--color-border` 邊、`font-sm`、`min-width:64`、`padding 0 16` |
| hover | 底 `--color-surface`（#fafafa） |
| active/selected | `.btn-ghost.active` → 實心 `--color-text` 底 + 白字 + 同色邊（用於 `#web-search-toggle` 開啟態） |
| disabled | `.btn-ghost:disabled` → `opacity:.5; not-allowed` |

### 4.3 Icon-only 按鈕（`.icon-only`）
規範：`width/height: var(--btn-icon)`=32×32、`min-width:0`、`padding:0`、`flex-shrink:0`，
靠 ghost/flex 置中對齊；內含 `<svg width=16 height=16 stroke-width=2 stroke=currentColor>`
（線性風格、`stroke-linecap/linejoin=round`，viewBox `0 0 24 24`）。

**所有 icon-only / 浮動 icon 按鈕清單與圖示：**

| 按鈕 | id / class | icon 語義 | 群組規範 |
|---|---|---|---|
| 左欄漢堡 | `#sidebar-toggle .panel-toggle` | 三橫線 ☰ | 浮動 fixed，32×32，`--color-surface` 底、強邊 |
| 右欄漢堡 | `#chat-toggle .panel-toggle` | 三橫線 ☰ | 同上 |
| 新增資料夾 | `#new-folder-btn .icon-only` | 資料夾＋加號 | 在 h1 右，gap `--gap-btn-loose` |
| 切換中英文 | `#lang-toggle .icon-only` | 文 A 翻譯狀（弧線＋筆畫） | 中欄工具列，gap `--gap-btn-loose` |
| 列印 | `#print-btn .icon-only` | 印表機 | 同上 |
| 說明 | `#help-btn .icon-only` | 圓圈問號 | sidebar-bottom 上排，gap `--gap-btn-tight`，等寬平分 |
| 清理殘檔 | `#cleanup-btn .icon-only` | 垃圾桶 | 同上 |
| 登出 | `#logout-btn .btn-ghost .icon-only` | 登出箭頭 | 同上（注意：同時帶 btn-ghost 與 icon-only） |
| 上傳文件 | `#upload-btn`（**保留 `＋` icon + 文字**） | 加號＋「上傳文件」 | 下排全寬主按鈕 |
| 論文操作 | `.paper-menu-btn .icon-only` | `⋯`（文字字元，非 SVG）24×24 | hover 顯示，列右端 |
| 資料夾操作 | `.folder-item .menu-btn` | `⋯`（文字字元）| hover 顯示，列右端 |
| 匯出 MD | `#export-btn`（icon + 「MD」文字，font-xs） | 下載箭頭 | 右欄標題列 |

> 一致性現況：SVG 多為 `16×16`、`stroke-width:2`；但 `.paper-menu-btn`/`.menu-btn`
> 的 `⋯` 是**文字字元**非 SVG（視覺重量、對齊與 SVG 鈕不同）。`.paper-menu-btn`
> 為 24×24（其餘 icon 鈕 32×32）。

### 4.4 Toggle 按鈕

| 按鈕 | 行為 | 視覺 |
|---|---|---|
| `#web-search-toggle`（「開啟搜尋」） | 點擊 toggle `useWebSearch` 與 `.active` class | 未選＝ghost；選中＝實心黑白字（A2 規範） |
| `#lang-toggle`（中/英） | 點擊切換 `currentLang`，重抓內容；只改 `title` 不改外觀 | 無視覺狀態差（icon 固定，靠 title 提示） |

### 4.5 危險操作
無獨立 danger 按鈕類；「刪除文件」為 popup 內項目，文字色 `--color-danger`（紅）。
刪除動作前一律 `confirm()` 原生對話框。

---

## 5. 互動狀態與行為

### 5.1 Sidebar 收合（左欄）
- 觸發：點 `#sidebar-toggle`（浮動漢堡，`left:216px`）。
- 行為：`#sidebar` toggle `.collapsed` → `width:0; overflow:hidden`（瞬間，無動畫）。
- 影響/現況：`#sidebar-toggle` 為 `position:fixed left:216px`，**展開時**約對齊側欄
  標題列右端；**收合時**側欄寬 0，按鈕仍固定在 `left:216px`，會浮在中欄內容上方
  （非貼齊任何邊），屬已知痛點。

### 5.2 Chat panel 收合（右欄）
- 觸發：點 `#chat-toggle`（浮動漢堡，`right:12px; top:8px`）。
- 行為：`#chat-panel` toggle `.collapsed` → `width:0`。
- 現況：`#chat-toggle` `right:12px` 固定，收合後仍在視窗右上角。

### 5.3 資料夾切換（filter 模型）
- 點 `.folder-item` → `selectFolder(key)` 設 `currentFolderId` ∈ `'all'|'uncategorized'|<int>`。
- 「全部」=所有論文；「未分類」=`folder_id==null`；使用者資料夾=該夾＋所有子孫遞迴。
- 選中列加 `.active`（實心 `--color-text` 底、白字、白 chevron）；未選透明。
- 重渲染 `#paper-list` 只顯示符合的論文。

### 5.4 資料夾展開/摺疊
- 點 `.chevron`（僅有子資料夾時 `▸/▾`）→ toggle `foldersOpen` Set。
- 持久化：`localStorage['foldersOpen']`（id 陣列）；重整後沿用。
- 樹由後端 flat list（含 `parent_id/sort_order`）前端 `buildTree` 組成，依
  `sort_order` 再 `id` 排序；每層縮排 `padding-left = 12 + depth*12 px`。

### 5.5 Paper-item 操作選單
- hover `.paper-item` → 右端 `.paper-menu-btn`（⋯）淡入。
- 點 ⋯ → `openPopup` 於按鈕 `getBoundingClientRect().left/bottom`：
  1. **刪除文件**（紅字）→ `confirm` → `DELETE /api/papers/{id}` → 重載列表。
  2. **移動到資料夾 ▸** → 換另一個 popup：未分類 + 全部資料夾（全形空白縮排表階層）→ 選擇即 `PATCH /api/papers/{uuid}`。
  3. **刪除對話**（`disabled`，灰字 not-allowed，`title="即將上線（Phase 3.4）"`）——無動作（後端 API 尚未實作）。
- 現況痛點：popup 以「⋯ 按鈕左/下緣」為錨點定位，於窄欄常顯得未貼齊列右邊緣。

### 5.6 資料夾操作選單
- hover `.folder-item` → `.menu-btn`（⋯）淡入。
- 點 ⋯ → popup：改名（prompt 預填）/ 新增子資料夾（prompt）/ 刪除（confirm，警告「子資料夾一併刪除、論文回未分類」）。

### 5.7 Web Search 開關
- 點 `#web-search-toggle` → `useWebSearch = !useWebSearch`，toggle `.active`。
- `.active` 時 `sendMessage` 的 fetch body 帶 `use_web_search:true`，AI 回答結尾可能附 `.msg-sources` 來源連結（持久化於訊息 `dataset.groundingSources`）。

### 5.8 上傳 → 類型確認 → 處理進度（核心流程）
1. 點 `#upload-btn` → 隱藏 file input 選 PDF → `POST /api/papers/upload` → 得 `paper_id`。
2. 開 `#confirm-modal`：`#doc-type-select` 預選偵測類型（slides 有特別提示）→「確認，開始處理」→ `POST /api/papers/{id}/confirm_type`。
3. `trackProgress` 開 `EventSource /api/papers/{id}/status`（SSE）：
   - `processing`：上傳鈕文字顯示「{階段名}... {n}%」。
   - 進度 `index>=10`（extra_info/rag 階段）→ 標記 `paperReadiness=reading_ready`，若使用者未在看別篇則自動 `loadPaper`（**文件閱讀提前**）。
   - `done`：`paperReadiness=done`、重載列表並回填標題；若正在看該篇 → 展開右欄、解鎖問答、載入對話。
   - `error`：alert 錯誤；`onerror` 復原上傳鈕。

### 5.9 「文件閱讀提前 / AI 問答延後」
- `reading_ready`：中欄內容可讀，但右欄 `#chat-panel` 加 `.collapsed`、`disableChat()`、顯示 `.msg-system`「內容已可閱讀，AI 問答準備中…」。
- `done`：移除系統訊息、移除 `.collapsed`、`enableChat()`、載入對話歷史。
- `loadPaper` 依 `paperReadiness.get(id)` 決定上述兩態（不在 map 視為 done）。

### 5.10 Modal 開關
| Modal | 開 | 關 |
|---|---|---|
| `#help-modal` | 點 `#help-btn` 加 `.show` | 點 `#help-close-btn` 或點遮罩本身移除 `.show` |
| `#confirm-modal` | 上傳成功後 `showConfirmModal()` 加 `.show` | 點「確認，開始處理」移除 `.show`（無取消鈕、不可點遮罩關閉） |

### 5.11 其他行為
- **列印** `#print-btn`：暫存標題→`window.print()`→還原；`@media print` 隱藏 `#sidebar/#chat-panel/#content-toolbar/#print-btn/#lang-toggle`，只印 `#paper-content`。
- **切換中英文** `#lang-toggle`：toggle `currentLang`，重抓 `/content?lang=`；只更新 `title`（icon 不變、無外觀狀態）。
- **匯出 MD** `#export-btn`：`location.href = /chat/export`（瀏覽器下載）；選文件解鎖後 `display:block`。
- **清理** `#cleanup-btn`：confirm → `POST /api/cleanup` → alert 結果。
- **登出** `#logout-btn`：`POST /logout` → 轉 `/login`。
- **對話持久化**：`saveChatHistory` 以 **DOM 抓取**（`.msg-user/.msg-ai` 的文字 + `dataset.groundingSources`）POST 回 `/chat/history`；`loadChatHistory` 反向渲染。
- **送出**：`Ctrl+Enter` 或點 `#send-btn`；SSE 串流逐塊 `marked.parse` 進 `.msg-ai`，游標字元 `▋` 佔位。
- **輸入框自動長高**：`autosizeChatInput`（input 事件）以 `scrollHeight` 撐高，上限 132px（CSS `max-height`）後出 scroll；送出後重置。

---

## 6. 內容區塊

### 6.1 中欄文章閱讀 `#paper-content`
- `flex:1; overflow-y:auto; max-width:860px; margin:0 auto; padding:32px 48px`。
- 由 `marked.parse(markdown)` 產生 HTML（圖片路徑改寫為 `/api/papers/{id}/images/...`）。
- 排版樣式（皆 `--color-text`）：
  - `h1` 28px/700、`h2` 20px/600（底部 1px 邊線）、`h3` 16px/600。
  - `p` 14px、`line-height:1.8`。
  - `img` 最大滿寬、小圓角；`em` muted 13px；`table` 全寬、`td/th` 1px 邊框。
- 未選文件：`#empty-state`（置中 subtle 文字 +左箭頭 icon）；選後 `#paper-content` 顯示。

### 6.2 右欄聊天訊息 `#chat-messages`
- `flex column; gap:24px; padding:24px; overflow-y:auto`。
- `.msg-user`：黑底白字、`align-self:flex-end`、`max-width:80%`、`pre-wrap`、圓角 4。
- `.msg-ai`：白底、1px 邊、`align-self:flex-start`、`max-width:95%`、`line-height:1.8`；內部 `p/ul/ol/li` 有間距規範。
- `.msg-sources`：AI 泡內底部，虛線上邊界，「來源：」+ 底線連結（muted→hover text）。
- `.msg-system`：置中 subtle（流程等待提示）。
- 串流：先插入 `▋` 佔位的 `.msg-ai`，SSE 逐塊覆寫 innerHTML；結束附來源、存歷史。

---

## 7. 已知問題與待解（現況痛點，客觀陳述）

1. **收合後漢堡跑位**：`#sidebar-toggle` `position:fixed; left:216px`，側欄收合（width:0）後按鈕仍停在 216px，浮在中欄文章上方，未貼齊任何邊。
2. **漢堡與標題列關係**：展開時漢堡靠 `left:216px` 概估對齊側欄右端，依賴側欄固定 260px；非以 DOM 結構對齊，視覺上與 `#new-folder-btn` 可能過近。
3. **右欄標題列三鈕間距**：「開啟搜尋／MD／漢堡（浮動）」分屬 `#chat-header-actions` 與浮動 `#chat-toggle`，浮動鈕不在 flex 流內，與其他兩鈕間距非由同一 token 控制。
4. **per-item / folder 選單定位**：popup 以 `⋯` 按鈕的 `left/bottom` 為錨點，於 260px 窄欄常顯得未貼齊列右邊緣；`min-width:160px` 在窄欄偏寬。
5. **icon 一致性**：SVG icon 多為 16×16/stroke 2 置於 32×32 方框（靠 flex 置中，非 padding）；但 `⋯` 為文字字元（`.paper-menu-btn` 24×24、`.menu-btn` 0 padding），與 SVG 鈕的視覺重量、盒尺寸不一致。
6. **`#logout-btn` 雙 class**：同時 `btn-ghost` 與 `icon-only`，且在 `.sb-row` 內被 `width:auto;flex:1` 覆寫——尺寸來源多重，易不一致。
7. **`.sb-row` 等寬**：三鈕 `flex:1`，但各為 icon-only（內容 16px icon），實際視覺寬度感受依賴 flex 計算，icon 是否完全置中、與上傳全寬鈕的對齊一致性需設計確認。
8. **lang-toggle 無狀態回饋**：中/英目前只改 `title`，使用者無法從畫面看出當前是中或英（icon 固定）。
9. **底部/輸入區可視性**：`#sidebar-bottom`、`#chat-input-area` 採 `--pad-panel` 內距；多行輸入時輸入框長高需確認按鈕底邊與訊息區不被遮（曾回報切邊/遮擋）。
10. **殘留樣式**：`#confirm-reason` 有 CSS 無對應 DOM；`.chat-empty` 兩種文案（「選擇文件後開始提問」「針對文件提問」）語境並存。
11. **收合無動畫**：`.collapsed` 直接 `width:0`，無 transition，收合/展開為瞬間跳變。
12. **Modal 無關閉一致性**：`#help-modal` 可點遮罩關閉，`#confirm-modal` 不可（也無取消鈕），互動不一致。
13. **命名與術語**：訊息類別為 `.msg-user/.msg-ai`（非 `.chat-message.user/.assistant`）；文章容器為 `#paper-content`（非 `#article-container`）；類型確認 modal 為 `#confirm-modal`（無獨立 type-confirm）。設計溝通時以本文件實際命名為準。
14. **無 RWD**：固定 260/420 與 flex:1；窄視窗時三欄會擠壓，僅靠收合緩解；行動裝置未處理。

---

## 8. 設計約束（必須遵守）

1. **DOM 結構盡量不動**：JS 以 `document.getElementById(id)` 綁定事件，移動節點可，但 **id 必須保留**。
2. **必保留的 id 清單**（移除/改名會破壞 JS）：
   `sidebar`、`sidebar-toggle`、`new-folder-btn`、`folder-tree`、`paper-list`、
   `sidebar-bottom`、`help-btn`、`cleanup-btn`、`logout-btn`、`upload-btn`、
   `content-area`、`content-toolbar`、`current-title`、`lang-toggle`、`print-btn`、
   `empty-state`、`paper-content`、`help-modal`、`help-box`、`help-close-btn`、
   `confirm-modal`、`confirm-box`、`confirm-desc`、`doc-type-select`、`confirm-ok-btn`、
   `chat-panel`、`chat-header`、`chat-header-actions`、`chat-toggle`、
   `web-search-toggle`、`export-btn`、`chat-messages`、`chat-input-area`、
   `chat-input`、`send-btn`。
   （另：JS 會建立/讀 `reading-ready-msg`；class `paper-item / paper-title-zh /
   paper-menu-btn / folder-item / chevron / fname / menu-btn / msg-user / msg-ai /
   msg-sources / msg-system / chat-empty / ctx-popup / sb-row / .title / active /
   collapsed / icon-only / btn-ghost / btn-primary` 皆被 JS 或樣式邏輯依賴）。
3. **既有 toggle / popup / modal 邏輯不變**：`.collapsed`、`.show`、`.active`、
   `.ctx-popup` 的開關機制與 class 名維持；可改其外觀，不可改其觸發與 class 契約。
4. **視覺語彙**：Mies 極簡，黑白灰（沿用色票），細邊框、無陰影、極小圓角；可調 token 數值但維持風格。
5. **語言**：介面以繁體中文為主；論文原文標題（英文）可保留。
6. **平台**：桌面瀏覽器優先；RWD 暫不要求（但歡迎提出策略建議）。
7. **不得引入**：重型 UI 框架/大量資產（現為單檔內嵌、僅 marked.js CDN）；維持輕量。

---

## 9. 期待設計師輸出

1. **重設計 mockup**：三欄佈局與各元件的視覺稿（Figma 或等效），涵蓋
   - 一般狀態（已選文件、有資料夾樹、有對話）。
   - 空狀態（未選文件、無對話、無資料夾）。
2. **狀態示意**：每類元件的 預設 / hover / active(selected) / disabled / collapsed
   五態，特別是：按鈕四類、folder-item、paper-item、web-search-toggle、收合前後三欄。
3. **針對痛點的解法**：對應第 7 節逐項——尤其
   - 收合後漢堡定位策略（展開/收合皆合理）。
   - 三欄標題列按鈕族群的間距/對齊統一規範。
   - per-item / folder popup 的定位與寬度。
   - icon 系統一致化（SVG 尺寸/stroke、`⋯` 是否改 SVG、盒尺寸統一）。
   - lang-toggle 的狀態可視化（如何讓使用者看出當前中/英）。
4. **token 調整建議**：哪些 `--color-* / --space-* / --btn-* / --gap-*` 該新增或改值
   （以表格列出 token、現值、建議值、理由），維持單一事實來源原則。
5. **新增元件建議（如需要）**：例如收合後的迷你側邊條、麵包屑、批次操作列等，
   需註明對既有 id/邏輯的影響（不破壞契約）。
6. **互動規格**：收合是否加動畫（時長/緩動）、popup 出現方式、modal 關閉一致化建議。

> 交付後，重設計仍須在第 8 節約束內落地（保留 id 與 toggle/popup/modal 契約、
> 維持單檔輕量、Mies 風格、中文桌面優先）。

---

## 附錄 A：版面 ASCII 示意（展開態）

```
 ☰(fixed,left216)                                              ☰(fixed,right12)
┌─────────────┬────────────────────────────────┬────────────────────────┐
│ 文件列表  ＋ │  論文標題           [文][印]    │ AI 問答  [開啟搜尋][MD] │ 48px 標題列
├─────────────┼────────────────────────────────┼────────────────────────┤
│ ▸ 全部       │                                │  ┌────────────────┐    │
│ ▸ 未分類     │   # H1 標題                    │  │ 使用者訊息(右,黑)│   │
│ ▾ 研究  ⋯   │   段落文字 line-height1.8 …    │  └────────────────┘    │
│   ▸ LLM ⋯   │   ![圖]                        │ ┌──────────────────┐   │
│ ──folder──── │   ## H2（底線）                 │ │ AI 訊息(左,白框)  │  │
│ 論文A     ⋯ │   …                            │ │ 來源：a、b（虛線）│   │
│ 論文B(選中) ⋯│                                │ └──────────────────┘   │
│ …(捲動)      │   (max-width 860 置中)         │   …(捲動)               │
├─────────────┤                                ├────────────────────────┤
│[?][清][登出] │                                │ [textarea 自動長高][送出]│ 輸入區
│[ ＋ 上傳文件]│                                │                          │
└─────────────┴────────────────────────────────┴────────────────────────┘
   260px              flex:1                         420px
```

## 附錄 B：收合態示意

```
☰216(浮中欄上)                                          ☰12
│(sidebar width:0)│         中欄 flex:1 變寬          │(chat width:0)│
                  │  論文標題      [文][印]           │
                  │  文章內容…                        │
```
（痛點：左漢堡 216px 浮在中欄；右漢堡 12px 仍在視窗右上）

## 附錄 C：元件 → 後端 API 對照（供理解資料流，非設計範圍）

| 互動 | 後端 |
|---|---|
| 載入論文列表 | `GET /api/papers`（回含 `folder_id`） |
| 資料夾 CRUD | `GET/POST/PATCH/DELETE /api/folders` |
| 移動論文 | `PATCH /api/papers/{uuid}` `{folder_id}` |
| 文件內容 | `GET /api/papers/{id}/content?lang=` |
| 上傳/類型/進度 | `POST /upload`、`POST /confirm_type`、SSE `GET /status` |
| 問答串流 | `POST /api/papers/{id}/chat`（SSE，`use_web_search`） |
| 對話存取/匯出 | `GET/POST /chat/history`、`GET /chat/export` |
| 清理/登出 | `POST /api/cleanup`、`POST /logout` |

---

文件結束。本文件為現況快照，供設計重構參考；如與最新程式碼有出入，以程式碼為準。
