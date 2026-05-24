# Components 設計規格 · MadPro UI

> 通用元件契約。所有新元件設計前先翻這份；既有元件不可偏離。

---

## 1. 按鈕（Button）

### 1.1 高度與內距
- 高度 `var(--btn-h)` = 32px（全域強制）
- 水平內距 `var(--btn-pad-x)` = 16px
- 最小寬度 `var(--btn-min-w)` = 64px（icon-only 例外，固定 32×32）

### 1.2 四類

**Primary（強調行為，每畫面 ≤ 1 個）**
- 底色 `--color-accent`、白字、同色邊
- hover：`--color-accent-hover`
- 用途：modal 主要按鈕、上傳、送出（舊版）

**Ghost（次要選項）**
- 透明底、`--color-text` 字、`--color-divider` 邊
- hover：`--color-surface` 淺底
- 用途：modal 取消、列表動作

**Icon-only（圖示鈕）**
- 32×32 容器、SVG 18×18
- 平常無框：`border: 1px solid transparent`
- hover：`--color-surface` 淺底
- :active：`--color-surface-2` 再深一階
- `.active` toggle：實心 `--color-text` 底 + 白 icon
- **詳細規範參見 `icon-spec.md`**

**Toggle（狀態切換）**
- 視覺：`.active` class 控；可加在 icon-only 或 ghost 上
- 例：`#web-search-toggle`（搜尋 icon + active 反白）

### 1.3 disabled
- `opacity: 0.5`
- `cursor: not-allowed`
- 若是 primary：底色降為 `--color-text-subtle`

### 1.4 群組間距
- 同族群：`--gap-btn-normal` 8px
- 不同族群：`--gap-btn-loose` 16px

---

## 2. Modal

### 2.1 結構
```
.modal-mask    全屏遮罩，rgba(0,0,0,0.4)
  └ .modal-box   內框
       ├ h3       標題
       ├ p/ol/ul  內容
       └ .modal-actions  按鈕列（靠右）
```

### 2.2 樣式契約
- mask 背景：`rgba(0, 0, 0, 0.4)`（不隨主題）
- box 背景：`--color-bg`
- box 邊框：1px `--color-divider`（與結構同色）
- box 圓角：`--radius-md`（目前主題皆 0）
- box 無陰影、無漸層
- box 最小寬 380、最大寬 480
- box 內距 `--space-6` 四邊
- 標題下 `--space-4` 內距

### 2.3 互動契約
- 點 mask 關閉：`.show` class 移除（**除非 `data-no-mask-close="true"`**）
- ESC 關閉（**除非 `data-no-esc="true"`**）
- Tab 焦點循環在 modal 內
- 開啟時記憶觸發元素，關閉時還原焦點
- `confirm-modal` 因關鍵流程，**同時帶 `data-no-esc` 與 `data-no-mask-close`**

### 2.4 內建通用 modal（取代瀏覽器原生）

| 函式 | 用途 | DOM |
|---|---|---|
| `customConfirm({ title, body, okLabel, cancelLabel, danger })` | 取代 `confirm()`；回傳 `Promise<boolean>` | `#action-modal` |
| `customAlert({ title, body, okLabel })` | 取代 `alert()`；回傳 `Promise<void>` | `#notice-modal` |

範例：
```js
const ok = await customConfirm({
  title: '刪除文件',
  body: '確定要刪除「Attention Is All You Need」？此操作無法還原',
  okLabel: '確定刪除', danger: true,
});
if (ok) { /* ... */ }
```

---

## 3. Popup（`.ctx-popup`）

### 3.1 用途
- per-item ⋯ 選單（資料夾、論文）
- 自訂 dropdown 選單

### 3.2 樣式契約
- `position: fixed`，append 到 `<body>`
- 不受捲動容器裁切
- 純白底（`--color-bg`）、1px `--color-divider` 邊
- 直角、無陰影
- 內距 `--space-1`、最小寬 140px、最大高 260（超出可捲）
- 內部 button：13px、無邊框、hover 淺底

### 3.3 z-index 層級

| 元件 | z-index |
|---|---|
| 一般 popup | 1000 |
| modal mask | 1500 |
| 在 modal 內的 popup（`.dropdown-popup`） | 1600 |
| tooltip | 2000 |

### 3.4 定位演算法
- 一般 popup：以觸發 item 右緣為錨；垂直貼按鈕下緣；下方放不下則往上翻
- dropdown popup：寬度跟 trigger 對齊；位置 `trigger.bottom - 1px`（重疊 1px 視覺貼齊）

### 3.5 關閉條件
- 點 popup 外任意處
- 視窗捲動或 resize
- 選擇其中一項後立即關閉

---

## 4. Tooltip

### 4.1 觸發
- 元素帶 `data-tip="<文字>"`
- 滑鼠停留 **200ms** 觸發顯示
- 顯示後 **800ms 自動消失**（即使仍 hover 在 icon 上）
  - **設計緣由（有意偏離標準）**：icon 圖形仍在打磨、tooltip 為輔助訊息；常駐 tooltip 會干擾閱讀。icon 系統穩定後可重評
- 自動消失後停同一 icon 不重觸發；須先離開
- mouseout 後 **100ms** 隱藏（相鄰 icon 接力不閃斷）

### 4.2 樣式
- `position: fixed`，append 到 `#tooltip` 容器
- 純白底（`--color-bg`）、1px `--color-divider` 邊
- 直角、無箭頭、無陰影
- 字級 `12px`、line-height 1.4
- 內距 `4px 10px`

### 4.3 位置
- 預設：icon 左側（右撇子鼠標習慣）
- 左側空間不足 → 自動翻右
- 上下邊界保護：min/max 4px

### 4.4 文案規則
- 2–6 個中文字
- 不重複按鈕已顯露的文字
- 詳見 `copywriting.md`（待寫）

---

## 5. Dropdown（自訂）

### 5.1 結構
```html
<div class="dropdown" data-value="...">
  <button class="dropdown-trigger" aria-haspopup="listbox" aria-expanded="false">
    <span class="dropdown-value">當前值</span>
    <svg class="dropdown-chevron">...</svg>
  </button>
</div>
```

### 5.2 行為
- 點 trigger → 開 `.ctx-popup.dropdown-popup`
- chevron 旋轉 180°（由 `aria-expanded` 切換）
- 選項點擊 → 寫回 `data-value`、更新 `.dropdown-value` 文字、關閉 popup
- 點外面 → 關閉
- **ESC 關閉**（BUG-F2 A6 ship、見 `interaction.md §4`）

### 5.3 動態新增選項 API（BUG-F2 A5、theme-dropdown 用）

`dropdownAPI` IIFE 暴露 `addTheme(name, label)` 與 `getThemeLabel(name)`、外部可動態註冊新選項：

```js
window.dropdownAPI.addTheme('foo', 'Foo Theme');   // 加入 THEMES 陣列、下次點開即可見
window.dropdownAPI.getThemeLabel('foo');           // → 'Foo Theme'
```

⚠️ **TDZ 注意**：`const dropdownAPI = (() => {...})();` 有 Temporal Dead Zone、IIFE 宣告之前的任何呼叫炸 `ReferenceError`。實作上 savedTheme 載入拆 3 段——themeLink 立即套用（IIFE 之前）+ dropdownAPI IIFE + dropdown 顯示值同步（IIFE 之後）；`theme-upload-input` change handler 註冊位置必須在 IIFE 之後。

### 5.4 鍵盤（建議實作）
- Enter / Space 開啟
- ↑↓ 切換選項
- Enter 選定
- ESC 關閉

---

## 6. 輸入框（Input / Textarea）

### 6.1 共通
- 高度 `var(--btn-h)` 32px（單行）；textarea 自動長高，min 32 / max 132
- 內距 `var(--space-2) var(--space-3)`
- 邊框 1px `--color-border`
- focus 邊框 `--color-accent`
- 直角、無陰影
- `font-family: inherit`、字級 `--font-base`

### 6.2 chat-input 特殊
- 寬度 `100%`（不再與送出鈕並排）
- 與 chat-messages 共用水平 padding `--chat-pad-x`（邊界對齊）
- 自動長高：min 32 / **max 240** / 隨內容增長

---

## 7. 列表項（List Item）

### 7.1 paper-item
- 內距 `--space-3`
- hover：`--color-border` 底
- `.active`：`--color-text` 底 + 白字 + 白 ⋯
- 結構：中文標題（13px / 500）+ 原文標題（12px / 2-line clamp / muted）+ 右上 ⋯ 按鈕（24×24）
- 觸控裝置：`@media (hover: none)` → ⋯ 永遠顯示

### 7.2 folder-item
- 內距 `--space-2 --space-3`
- 縮排：`12 + depth * 12` px
- chevron 14×10、`>` 形、靠 stroke-linejoin 圓化、open 時 rotate 90°

### 7.3 paper-item.uploading（占位）
- 永遠出現在 list 最頂端（不受 folder filter 影響）
- 背景脈動（1.6s）
- 標題義式 muted
- 底部 2px 進度條 `--color-accent`
- 點圓 6px 閃爍（1s）
- **`pointer-events: none`**：整列禁止點擊，避免誤觸

### 7.4 #content-toolbar 內 #current-title 擴充標題區（中欄）
Phase 4.7c 修正 3（修正 2 把 title 搬出 toolbar 是誤判，本輪搬回）。
`#current-title` 為 `#content-toolbar` 子元素，取原 `h2` 的 `flex:1 min-width:0`
槽位，與右側 `.toolbar-actions` 並列；toolbar 原本就是 multi-row 可變高度
設計（`align-items: flex-start` 允許 title 加高時 icon 仍貼齊頂部）。

`#current-title` 結構：
- `.title-zh`：22px / 600，always-show（fallback 同 `resolveDisplayTitle`，
  中文優先）
- `.title-en`：14px muted；當 title-zh 與 metadata.title (原文) 不同時才顯示
- `.title-meta`：12px muted，flex；authors · date · journal/publisher，
  分隔符 `.title-meta-sep` (`·`)
- `details.title-abstract`：摘要可摺疊（預設摺起），summary 文字「顯示摘要」；
  展開後 `.abstract-body` 為左側 3px border 卡片
- 整個 `#current-title[hidden]`：未選文件時隱藏
- 不重複設 padding / border-bottom（由 toolbar 提供）

doc_type 分支：
- academic / technical / book / news / web：完整顯示
- resume：candidate_name 為 .title-zh、organization 為 .title-meta；
  無 .title-en / authors / date / abstract
- slides：簡化（.title-zh，可能無 meta，abstract 通常空 → 靜默省略）

fallback：缺項靜默省略；只有 title 是 always-show。

---

## 8. 訊息泡泡（Message Bubble）

### 8.1 user
- 底色 `--color-accent`、白字
- 右對齊 `align-self: flex-end`
- 最大寬 75%
- `white-space: pre-wrap`

### 8.2 ai
- 底色 `--color-bg`、`--color-text` 字
- 1px `--color-border` 邊
- 左對齊 `align-self: flex-start`
- 最大寬 90%
- 內含 Markdown 渲染、可含 `.msg-sources` 來源列
- **右下浮現** `.msg-ai-actions` 動作鈕列（hover 顯示）：
  - `.msg-copy` — 複製內容到剪貼簿；成功後 1.5s 內 icon 變 accent 色
  - `.msg-regen` — 重新生成（待接 API）
  - 容器：`position: absolute; right: 6px; bottom: -14px`，浮出泡泡下緣 14px
  - 觸控裝置（`@media hover: none`）永遠顯示

### 8.3 system
- 13px subtle、置中
- 用於：「內容已可閱讀，AI 問答準備中…」

---

## 9. 收合 Rail

- 收合後欄寬 `--rail-w` 48px（非 0）
- 漢堡 icon 仍在標題列 DOM 中、貼齊分隔線
- 動畫 `width 180ms ease`

---

## 11. Tag Pill（`.tag-pill`、RAG-1 R2）

### 11.1 用途

顯示 paper 的 hashtag（user_tags）、用半透明磨砂玻璃效果區分內容區、視覺輕量不搶眼。

容器：`.paper-tags`（flex container、wrap、gap=8px）。

### 11.2 樣式契約

```css
.tag-pill {
    display: inline-flex;
    align-items: center;
    padding: var(--space-1) var(--space-2);
    background: rgba(255, 255, 255, 0.6);
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
    border: var(--divider-w) solid var(--color-divider);
    border-radius: var(--radius-sm);
    font-size: var(--font-sm);
    color: var(--color-text);
    transition: background 0.2s ease;
}
```

關鍵：
- `background: rgba(255,255,255,0.6)` 半透明白
- `backdrop-filter: blur(8px)` 磨砂玻璃效果
- 不用 box-shadow（依本文件 §10 反例規範）
- 圓角用既有 `--radius-sm`、不自創

### 11.3 互動契約

- **Hover**：`background` opacity 提升至 0.8、`transition 0.2s ease`
- **點擊**：當前無互動行為（未來可加 click → 跨文件過濾、屬 Phase 2 Hashtag Backend Plan 範圍）

### 11.4 深色主題

```css
[data-theme="dark"] .tag-pill {
    background: rgba(0, 0, 0, 0.4);
}
[data-theme="dark"] .tag-pill:hover {
    background: rgba(0, 0, 0, 0.55);
}
```

未來主題若用 `--color-bg-rgb` 等半透明 token、可改 `rgba(var(--color-bg-rgb), 0.6)`。

### 11.5 容器規範

通常放在 `.paper-tags` flex container 內：

```css
.paper-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    margin-top: var(--space-2);
}
```

### 11.6 內容規範

- 文字：**lowercase**（後端 `paper_manager._normalize_tag()` 強制標準化、RAG-1 R2 v3 強化）
- 顯示：加 `#` 前綴（如 `#plant`、`#machine_learning`、`#人資`）
- 中文 tag：原樣保留（`.lower()` 對中文無效）
- 來源：`paper.metadata_json.user_tags` 陣列
- 寫入路徑：`PATCH /api/papers/{paper_uuid}` body `{"tags": [...]}` → 後端 `set_paper_tags` 寫入

### 11.7 相關文件

- 後端：`paper_manager.py::set_paper_tags` + `_normalize_tag` helper
- 前端：`static/index.html#tag-modal`（編輯 Modal）+ `renderTitleHeader` 內 tag-pill 渲染
- 測試：`tests/test_paper_tags.py`（R1）+ `tests/test_normalize_tag.py`（R2 v3）

---

## 11.2 Hashtag Token（`.hashtag-token`、chat-input 內、RAG-1 Phase 2 P2-3）

> 註：跟 §11 Tag Pill 同屬「tag 視覺呈現」家族、但用途與互動完全不同——Tag Pill 是 paper toolbar 的**唯讀標籤**、Hashtag Token 是 chat-input 的**可拆卸藍色 token**（類似 Claude 對話框的 `/skill` 行為）。

### 11.2.1 用途

chat-input 內輸入 `#<prefix>` 後從 autocomplete dropdown 選定的 tag、會被轉成藍色不可編輯 token（一整塊原子單元）。Token 用來：
- 視覺化「此 tag 將觸發跨文獻 RAG 路由」、跟純文字 query 區分
- 讓用戶確認 tag 已被後端認得（autocomplete 來源 = `allPapers.metadata_json.user_tags`、Q9）
- 對應後端 `paper_manager.parse_query_hashtag` 解析路徑（P2-2 ship）

容器：`#chat-input`（contenteditable div、`#chat-input-area` 為定位錨點）。

### 11.2.2 樣式契約

```css
.hashtag-token {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: 0 var(--space-2);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-sm);
    font-size: var(--font-sm);
    user-select: none;
    cursor: default;
    vertical-align: baseline;
    line-height: 1.5;
}
.hashtag-token-remove {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.85);
    cursor: pointer;
    padding: 0;
    margin-left: 2px;
    line-height: 1;
}
.hashtag-token-remove:hover { color: white; }
```

關鍵：
- `background: var(--color-accent)`（藍色、跟 toolbar Tag Pill 半透明白形成對比）
- `user-select: none` + `contenteditable="false"`：用戶 selection 跳過、Backspace 一次刪整顆
- `vertical-align: baseline` + `line-height: 1.5`：跟周圍純文字基線對齊、不錯位
- 無 `box-shadow`、無漸層（依本文件 §10 反例規範）

### 11.2.3 互動契約

- **輸入 `#<prefix>`**：autocomplete dropdown 顯示前綴匹配的 user_tags（前 10 筆、超過顯示 `...更多 (N 筆)`、Q8）
- **鍵盤導覽**：`↑/↓` 切換 active、`Enter`/`Tab` 確認、`Esc` 關閉
- **滑鼠**：點 item（`mousedown`、非 `click`、避免失焦先觸發 close）確認
- **確認後**：`#<prefix>` 純文字被刪除、替換為 token span + 後綴空格（cursor 落在空格後）
- **刪除 token**：
  - 點 token 內 `×` 按鈕 → 整顆刪除（Q13 不二次確認）
  - Token 後 Backspace → contenteditable 把 token 視為原子單元、一次刪整顆
- **中文 IME（Q12）**：`compositionstart` 旗標關閉 autocomplete 觸發、`compositionend` 重新偵測
- **無 hover tooltip（Q10）**：首版簡單、未來 follow-up 可加「跨 N 篇 paper」提示

### 11.2.4 Autocomplete 定位（§3.3.5-#4 防護）

依 plan v2 §3.3.5-#4、autocomplete dropdown 定位錨點**綁容器、非綁 cursor**：

```css
#chat-input-area { position: relative; }                  /* 定位上下文 */
#hashtag-autocomplete.hashtag-popup {
    position: absolute;
    bottom: 100%;                                          /* 永遠在 input 正上方 */
    left:  var(--chat-pad-x, var(--space-5));              /* 對齊 input 左 padding */
    right: var(--chat-pad-x, var(--space-5));
    max-height: 240px;
    overflow-y: auto;
    margin-bottom: var(--space-2);
    z-index: 100;
}
```

好處：
- 永遠整齊懸浮、不抖動、不溢出
- 即使 chat-input 多行展開、dropdown 仍貼齊頂部、視覺穩定
- 對齊 Claude `/skill` autocomplete 行為

⚠️ **`#hashtag-autocomplete` HTML 用 `class="hashtag-popup"`、**不含** `.ctx-popup`**（BUG-F2 Bug 11 P2-3 latent fix ship 於 BUG-F2）：
- 既有 `closePopups()` 用 `document.querySelectorAll('.ctx-popup').forEach(p => p.remove())` 永久 .remove() 任何 `.ctx-popup` element；早期 P2-3 ship 時把 `#hashtag-autocomplete` 也加 `.ctx-popup` class、會被 closePopups 永久刪除、後續 `popup.hidden = false` 操作 detached node 即破。
- `#hashtag-autocomplete.hashtag-popup { ... }` CSS 自身完整（含 `position` / `background` / `border` / `box-shadow` / `border-radius`）、不依賴 `.ctx-popup` base style、移除 class 零視覺風險。
- BUG-F2 A6 ESC 加 `closePopups()` 同 commit 才安全（否則 ESC 會放大此 latent bug、永久刪 autocomplete element）。

### 11.2.5 跟 §11 Tag Pill 的區別

| 維度 | §11 Tag Pill | §11.2 Hashtag Token |
|---|---|---|
| 位置 | paper 標題下方 toolbar | chat-input 內 |
| 用途 | 顯示 paper 的 user_tags（唯讀） | query 內 hashtag 視覺糖 |
| 顏色 | 半透明白磨砂玻璃（`rgba(255,255,255,0.6)` + blur） | 純藍色（`var(--color-accent)`） |
| 互動 | 無互動（未來可 click 過濾） | 鍵盤/滑鼠選 + × 刪除 |
| contenteditable | N/A | 原子單元（`contenteditable="false"`） |
| 來源 | paper.metadata_json.user_tags | autocomplete from allPapers cache |

### 11.2.6 contenteditable 防護（§3.3.5 1-3 點）

- **#1 placeholder**：`#chat-input:empty::before { content: attr(data-placeholder); ... }`（contenteditable div 無原生 placeholder）
- **#2 disabled**：`#chat-input[contenteditable="false"]` 顯式設灰底 + `cursor: not-allowed` + `user-select: none`（disabled 屬性對 div 無效）
- **#3 全域替換**：`chatInput.value` → `chatInput.textContent.trim()`、`chatInput.disabled = true/false` → `chatInput.setAttribute('contenteditable', 'true'/'false')`、`textarea autosize listener` 移除（contenteditable 自然撐高 + `max-height: 240px`）

### 11.2.7 相關文件

- 後端：`paper_manager.py::parse_query_hashtag` + `list_paper_uuids_by_tag`（P2-2 ship）
- 前端：`static/index.html#chat-input`（contenteditable div）+ `#hashtag-autocomplete`（popup）+ `hashtagAutocomplete` JS 模組
- 測試：`tests/test_phase2_p2_3_hashtag_token_ui.py`（grep + 結構驗證）+ `tests/test_bug_f2_theme_dropdown_esc.py`（BUG-F2 Bug 11 latent fix grep）

---

## 12. 反例

- ❌ 自製按鈕用陰影或漸層
- ❌ Popup 寫 `position: absolute` → 被捲動容器裁切
- ❌ Tooltip 用 `title` 屬性 → 與自訂 tooltip 重疊
- ❌ Modal 用 border-radius > 0 → 違反主題承諾
- ❌ Icon-only 平常顯示邊框 → 違反「平常無框」規則
- ❌ 在主檔 HTML 寫死 z-index 數字 → 統一靠本文件層級表
