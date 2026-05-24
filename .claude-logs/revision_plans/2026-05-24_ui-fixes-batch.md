# Claude Code 任務檔 · UI Fixes Batch v1

> **目的**：把過去稽核累積的 12 個 bug + 4 個 inconsistency + 7 個 polish 一次修完。
> **適用範圍**：`static/index.html`（主檔）、`static/themes/*.css`（5 個主題）、`processor/md_restore_processor.py`（後端）、`docs/*.md`（規範文件）。
>
> **執行原則（給 Claude Code）**
> 1. 嚴格照本檔程式碼修改；非必要不擴張範圍
> 2. 每個任務獨立可驗證；不要把多個任務的 diff 揉成一個 commit
> 3. 改完一個任務 → 跑一次冒煙測試（指定步驟）→ 進下一個
> 4. 文件更新（章節「設計文件同步」）必須跟程式碼同 commit
> 5. 如果發現本檔的 line number 與實際檔案不符（commit drift），以**模式比對**找位置，不要硬塞 line
> 6. 不准擅自增加 `!important`、不准動到本檔未列出的 token、不准刪除 `data-tip` 屬性

---

## 全域命名與檔名約定

| 短名 | 全路徑 |
|---|---|
| 主檔 | `static/index.html` |
| 主題檔 | `static/themes/mies.css`、`kahn.css`、`kandinsky.css`、`nara.css`、`apple.css`、`google.css` |
| 後端 markdown 還原 | `processor/md_restore_processor.py` |
| docs | `docs/` 下各 `.md` |

---

# Task A · P1 critical（修壞掉的）

## A1. `trackProgress` 完成後用 textContent 蓋掉 multi-row 標題結構

**檔案**：`static/index.html`

**症狀**：上傳處理完成後，中欄 toolbar 的 `<header id="current-title">` 內 h1 / p / details / tags 全被清成單行字串。

**位置找法**：grep `current-title').textContent = el.textContent`

**修改前**：
```js
loadPapers().then(() => {
  if (currentPaperId === paperId) {
    const el = document.querySelector(`.paper-item[data-id="${paperId}"] .paper-title-zh`);
    if (el) document.getElementById('current-title').textContent = el.textContent;
  }
});
```

**修改後**：
```js
loadPapers().then(() => {
  if (currentPaperId === paperId) {
    // 用 renderTitleHeader 重繪整個 multi-row 結構，保留 h1 / p / details / tags
    const p = allPapers.find(p => p.id === paperId);
    if (p) renderTitleHeader(p);
  }
});
```

**驗證**：上傳一篇 PDF → 等到處理完成 → 中欄標題應顯示完整 multi-row 結構（中文 + 英文 + 作者 + 摘要 details）。

---

## A2. `#empty-state` 預設 `display:none` → 初始畫面中欄空白

**檔案**：`static/index.html`

**症狀**：未選文件時中欄一片空白（toolbar 與 paper-content 都顯示但內容皆空）。

**位置**：HTML body 內。

**修改前**：
```html
<div id="empty-state" style="display:none">
  <svg width="16" height="16" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-6-6a1.5 1.5 0 0 1 0-2l6-6"/></svg>
  從左側選擇文件
</div>
<div id="paper-content"></div>
```

**修改後**：
```html
<div id="empty-state">
  <svg width="16" height="16" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-6-6a1.5 1.5 0 0 1 0-2l6-6"/></svg>
  從左側選擇文件
</div>
<div id="paper-content" style="display:none"></div>
```

`loadPaper` 內既有切換邏輯不變。

**驗證**：重整頁面 → 中欄顯示「從左側選擇文件」。點任一 paper → empty-state 消失、paper-content 顯示。

---

## A3. 統一對話框系統：native `alert/confirm/prompt` → `customConfirm/customAlert/customPrompt`

**檔案**：`static/index.html`

**位置**：grep `confirm(` `alert(` `prompt(` 找出所有呼叫點（folder 操作、paper 刪除、cleanup、upload 失敗、export 為空、focus listener）。

### A3.1 先新增 `customPrompt` 與其 modal DOM

在 `#notice-modal` 之後加入：

```html
<!-- 通用輸入 Modal — 取代瀏覽器原生 prompt() -->
<div id="prompt-modal" class="modal-mask">
  <div id="prompt-box" class="modal-box" role="dialog" aria-labelledby="prompt-title">
    <h3 id="prompt-title">輸入</h3>
    <p id="prompt-body"></p>
    <input type="text" id="prompt-input" class="modal-input">
    <div class="modal-actions">
      <button id="prompt-cancel" class="modal-btn">取消</button>
      <button id="prompt-ok" class="modal-btn primary">確定</button>
    </div>
  </div>
</div>
```

JS 在 `customAlert` 之後加：
```js
function customPrompt({ title = '輸入', body = '', defaultValue = '',
                        okLabel = '確定', cancelLabel = '取消',
                        validate = null } = {}) {
  return new Promise(resolve => {
    document.getElementById('prompt-title').textContent = title;
    document.getElementById('prompt-body').textContent = body;
    const input = document.getElementById('prompt-input');
    input.value = defaultValue;
    const okBtn = document.getElementById('prompt-ok');
    const cancelBtn = document.getElementById('prompt-cancel');
    okBtn.textContent = okLabel;
    cancelBtn.textContent = cancelLabel;
    const cleanup = () => {
      okBtn.onclick = null;
      cancelBtn.onclick = null;
      input.onkeydown = null;
      closeModal('prompt-modal');
    };
    const submit = () => {
      const v = input.value;
      if (validate) {
        const err = validate(v);
        if (err) { customAlert({ title: '輸入錯誤', body: err }); return; }
      }
      cleanup(); resolve(v);
    };
    okBtn.onclick = submit;
    cancelBtn.onclick = () => { cleanup(); resolve(null); };
    input.onkeydown = (e) => { if (e.key === 'Enter') submit(); };
    openModal('prompt-modal');
    setTimeout(() => input.focus(), 0);
  });
}
window.customPrompt = customPrompt;
```

### A3.2 替換所有 native 呼叫

**folderCreate**：
```js
async function folderCreate(parentId) {
  const name = await customPrompt({
    title: '新增資料夾',
    body: '輸入資料夾名稱（1–50 字元）',
    validate: (v) => {
      const n = (v || '').trim();
      if (!n || n.length > 50) return '名稱需 1–50 字元';
      return null;
    },
  });
  if (name == null) return;
  try { await createFolderApi(name.trim(), parentId); await loadFolders(); }
  catch (e) { customAlert({ title: '建立失敗', body: e.message }); }
}
```

**folderRename**：
```js
async function folderRename(node) {
  const name = await customPrompt({
    title: '改名',
    body: '輸入新名稱',
    defaultValue: node.name,
    validate: (v) => {
      const n = (v || '').trim();
      if (!n || n.length > 50) return '名稱需 1–50 字元';
      return null;
    },
  });
  if (name == null) return;
  try { await updateFolderApi(node.id, { name: name.trim() }); await loadFolders(); }
  catch (e) { customAlert({ title: '更新失敗', body: e.message }); }
}
```

**folderDelete**：
```js
async function folderDelete(node) {
  const ok = await customConfirm({
    title: '刪除資料夾',
    body: `刪除「${node.name}」？子資料夾會一併刪除，內部論文回到未分類`,
    okLabel: '確定刪除',
    danger: true,
  });
  if (!ok) return;
  try {
    await deleteFolderApi(node.id);
    if (currentFolderId === node.id) currentFolderId = 'all';
    await loadFolders();
    await loadPapers();
  } catch (e) { customAlert({ title: '刪除失敗', body: e.message }); }
}
```

**deletePaper**：
```js
async function deletePaper(paperId, title) {
  const ok = await customConfirm({
    title: '刪除文件',
    body: `確定刪除「${title}」？此操作無法還原`,
    okLabel: '確定刪除',
    danger: true,
  });
  if (!ok) return;
  try {
    const res = await fetch(`/api/papers/${paperId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('刪除失敗');
    if (currentPaperId === paperId) {
      currentPaperId = null;
      document.getElementById('content-toolbar').style.display = 'none';
      document.getElementById('empty-state').style.display = 'flex';
      document.getElementById('paper-content').style.display = 'none';
      document.getElementById('chat-messages').innerHTML = '<div class="chat-empty">選擇文件後開始提問</div>';
      document.getElementById('chat-input').setAttribute('contenteditable', 'false');
    }
    await loadPapers();
  } catch(e) {
    customAlert({ title: '刪除失敗', body: e.message });
  }
}
```

**cleanup-btn**：
```js
document.getElementById('cleanup-btn').addEventListener('click', async (e) => {
  e.stopImmediatePropagation();
  if (isProcessing) return;
  const ok = await customConfirm({
    title: '清除殘檔',
    body: '確定要清理殘餘檔案？此操作會刪除所有不在論文列表中的目錄',
    okLabel: '確定清除',
    danger: true,
  });
  if (!ok) return;
  try {
    const res = await fetch('/api/cleanup', { method: 'POST' });
    const data = await res.json();
    if (data.count === 0) {
      customAlert({ title: '清理結果', body: '沒有殘餘檔案需要清理' });
    } else {
      customAlert({
        title: '清理結果',
        body: `已清理 ${data.count} 個殘餘目錄：\n${data.removed.join('\n')}`
      });
    }
  } catch(e) {
    customAlert({ title: '清理失敗', body: e.message });
  }
});
```

**upload 失敗、confirm_type 失敗、export 為空、movePaper 失敗**：對應 `alert(...)` 改為 `customAlert({ title: '...', body: msg })`。

**chat-input focus listener** 整段刪除（contenteditable=false 已防護，dead code）。

**驗證**：每個操作觸發點都該顯示 modal 而非瀏覽器原生對話框。

---

## A4. 兩個 popup-close 函式並存

**檔案**：`static/index.html`

**症狀**：`closePopups()` 與 `closeBizPopups()` 兩個函式都選 `.ctx-popup` 全移除；兩個 document click listener 每次點擊都跑。

**位置**：grep `closeBizPopups`

**做法**：
1. 刪除 `function closeBizPopups() { ... }` 整個函式
2. 刪除其後的 `document.addEventListener('click', ...)` listener
3. 在 `openPopup(x, y, items)` 內把所有 `closeBizPopups()` 呼叫改為 `closePopups()`

**驗證**：所有 ⋯ 選單仍能開／關；點外面仍能關。

---

## A5. 上傳 CSS 後新主題不出現在下拉選單

**檔案**：`static/index.html`

**症狀**：使用者上傳自訂 CSS 主題後，重開下拉選單仍只有預設四個（IIFE 內 `const THEMES = [...]` 寫死）。

**做法**：把 `setupDropdown` IIFE 改為暴露 API；外層在啟動載入 / 上傳成功時呼叫 `addTheme`。

**修改前**：
```js
(function setupDropdown() {
  const DOC_TYPES = [...];
  const THEMES = [
    ['mies', 'Mies van der Rohe'],
    ['kahn', 'Kahn · Kimbell 美術館'],
    ['kandinsky', 'Kandinsky · Bauhaus'],
    ['nara', '奈良美智 · Yoshitomo Nara'],
    ['apple', 'Apple · Human Interface'],
    ['google', 'Google · Material You'],
  ];
  setupOne(document.getElementById('doc-type-dropdown'), DOC_TYPES);
  setupOne(document.getElementById('theme-dropdown'), THEMES);
  function setupOne(dd, items) { ... }
})();
```

**修改後**：
```js
const dropdownAPI = (() => {
  const DOC_TYPES = [...];                    // 不變
  const THEMES = [
    ['mies', 'Mies van der Rohe'],
    ['kahn', 'Kahn · Kimbell 美術館'],
    ['kandinsky', 'Kandinsky · Bauhaus'],
    ['nara', '奈良美智 · Yoshitomo Nara'],
    ['apple', 'Apple · Human Interface'],
    ['google', 'Google · Material You'],
  ];
  const themeLabels = Object.fromEntries(THEMES);
  setupOne(document.getElementById('doc-type-dropdown'), DOC_TYPES);
  setupOne(document.getElementById('theme-dropdown'), THEMES);
  function setupOne(dd, items) { /* 原邏輯不變 */ }

  return {
    addTheme(name, label) {
      label = label || name;
      if (themeLabels[name]) return;
      themeLabels[name] = label;
      THEMES.push([name, label]);   // 內部陣列 push，setupOne 內的 closure 持有相同 reference，下次點開即生效
    },
    getThemeLabel(name) { return themeLabels[name] || name; },
  };
})();
window.dropdownAPI = dropdownAPI;
```

**啟動載入處同步補**（**重要：執行順序**）：

⚠️ **TDZ 警告**：`const dropdownAPI = (() => {...})();` 有 Temporal Dead Zone，在它之前的任何 `dropdownAPI.xxx` 呼叫都會炸 `ReferenceError`。現行 `static/index.html` 中 savedTheme localStorage 載入（早）→ setupDropdown（晚），若把 `addTheme` 直接塞進早段就壞。

**正確做法**：把 savedTheme 載入**拆兩段**——themeLink 立即套用、dropdown 同步延後到 IIFE 之後執行：

```js
// === 第一段：savedTheme 立即套用 themeLink（在 dropdownAPI IIFE 之前）===
// 放在現行「切換風格 modal + 套用」區塊頂端
const THEME_KEY = 'madpro-theme';
const savedTheme = localStorage.getItem(THEME_KEY);
if (savedTheme) {
  document.getElementById('theme-link').href = `/static/themes/${savedTheme}.css`;
}

// ... 其他既有 JS ...

// === 第二段：dropdownAPI IIFE（原 setupDropdown 改名）===
const dropdownAPI = (() => {
  // ... 內容如 A5 提供 ...
})();
window.dropdownAPI = dropdownAPI;

// === 第三段：savedTheme 同步 dropdown 顯示值（必須在 dropdownAPI 之後）===
if (savedTheme) {
  dropdownAPI.addTheme(savedTheme);   // 若是自訂 theme 動態註冊
  const dd = document.getElementById('theme-dropdown');
  dd.dataset.value = savedTheme;
  dd.querySelector('.dropdown-value').textContent = dropdownAPI.getThemeLabel(savedTheme);
}
```

**理由**：themeLink 必須在頁面渲染前就決定，否則閃一下 fallback；但 dropdown 顯示值是 UI 細節，晚個幾行 JS 才同步無感。

**上傳成功處同步補**（theme-upload-btn handler，若還沒寫補上）：

⚠️ **執行順序**：此 handler 也呼叫 `dropdownAPI.addTheme(...)`，必須**註冊在 `dropdownAPI` IIFE 之後**。實務上 handler 是 `addEventListener` 註冊、執行在使用者點擊時，順序不會撞 TDZ；但**註冊綁定語句本身**若放在 IIFE 之前的 `addEventListener` 內可能還沒問題（因 closure 延後求值）。為保險，**整段放在 dropdownAPI 區塊之後**。

```js
document.getElementById('theme-upload-btn').addEventListener('click', () => {
  document.getElementById('theme-upload-input').click();
});
document.getElementById('theme-upload-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  try {
    const res = await fetch('/api/themes/upload', { method: 'POST', body: formData });
    if (!res.ok) throw new Error('上傳失敗');
    const data = await res.json();
    const themeName = data.filename.replace(/\.css$/, '');
    dropdownAPI.addTheme(themeName);     // ← 新主題進選單
    const dd = document.getElementById('theme-dropdown');
    dd.dataset.value = themeName;
    dd.querySelector('.dropdown-value').textContent = themeName;
    // 立即套用
    document.getElementById('theme-link').href = `/static/themes/${themeName}.css`;
    localStorage.setItem(THEME_KEY, themeName);
  } catch (err) {
    customAlert({ title: '上傳失敗', body: err.message });
  } finally {
    e.target.value = '';
  }
});
```

**驗證**：上傳 `foo.css` → 重開下拉應看到 `foo` 選項；重整頁面後仍在。

**順序驗證**：完成後在 console 跑 `typeof dropdownAPI` → 應為 `'object'`；網頁載入無 `ReferenceError`。

---

## A6. ESC 關 modal 留下 popup 殘影

**檔案**：`static/index.html`

**症狀**：開啟 `#theme-modal` 內的 dropdown popup 後按 ESC，modal 關但 popup 留在畫面。

**位置**：document keydown handler

**修改前**：
```js
document.addEventListener('keydown', (e) => {
  const open = [...document.querySelectorAll('.modal-mask.show')].pop();
  if (!open) return;
  if (e.key === 'Escape' && open.dataset.noEsc !== 'true') {
    e.preventDefault();
    closeModal(open);
    return;
  }
  // ... Tab handler 略
});
```

**修改後**：
```js
document.addEventListener('keydown', (e) => {
  // ESC 先處理 popup（含 dropdown 內展開的 list），再處理 modal
  if (e.key === 'Escape') {
    const hasPopup = document.querySelector('.ctx-popup');
    if (hasPopup) {
      e.preventDefault();
      closePopups();
      return;       // 一次 ESC 只關一層
    }
    const open = [...document.querySelectorAll('.modal-mask.show')].pop();
    if (open && open.dataset.noEsc !== 'true') {
      e.preventDefault();
      closeModal(open);
      return;
    }
  }
  // Tab 焦點循環略（保留原邏輯）
});
```

**驗證**：開 theme-modal → 點 dropdown → 按 ESC → popup 消失、modal 還在；再按 ESC → modal 消失。

---

## A7. LaTeX 公式無法渲染

**檔案**：`static/index.html`、`processor/md_restore_processor.py`

### A7.1 後端：placeholder 保護

**檔案**：`processor/md_restore_processor.py`

在處理 markdown 前後加保護層：
```python
import re

_LATEX_PLACEHOLDER_PREFIX = '\x00LATEX'

def _protect_latex(text):
    """抽出所有 LaTeX block / inline，換成 placeholder。返回 (處理過的文字, 還原表)。"""
    blocks = []
    def block_repl(m):
        idx = len(blocks); blocks.append(m.group(0))
        return f'{_LATEX_PLACEHOLDER_PREFIX}_BLOCK_{idx}\x00'
    def inline_repl(m):
        idx = len(blocks); blocks.append(m.group(0))
        return f'{_LATEX_PLACEHOLDER_PREFIX}_INLINE_{idx}\x00'
    text = re.sub(r'\$\$([\s\S]+?)\$\$', block_repl, text)
    # 行內：兩側不可緊鄰數字（避免誤匹配 $100~$200 之類）；不跨換行
    text = re.sub(r'(?<![\d\\])\$([^\$\n]+?)\$(?!\d)', inline_repl, text)
    return text, blocks

def _restore_latex(text, blocks):
    for i, src in enumerate(blocks):
        text = text.replace(f'{_LATEX_PLACEHOLDER_PREFIX}_BLOCK_{i}\x00', src)
        text = text.replace(f'{_LATEX_PLACEHOLDER_PREFIX}_INLINE_{i}\x00', src)
    return text
```

把現有 markdown 處理函式包裹：
```python
def process(text):
    text, blocks = _protect_latex(text)
    # ... 原本所有 markdown 清洗 / 還原邏輯 ...
    return _restore_latex(text, blocks)
```

### A7.2 前端：載入 KaTeX + auto-render

`<head>` 加（在 marked.js 之後）：
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
```

### A7.3 前端：marked.js extensions 抽 math token（即便後端沒改也能跑）

在 `marked.use({ extensions: [{ name:'del'...` 那個 use 之後（或合進去），加：
```js
marked.use({
  extensions: [
    /* 既有 del extension */,
    {
      name: 'mathInline',
      level: 'inline',
      start(src) { return src.indexOf('$'); },
      tokenizer(src) {
        const m = src.match(/^\$([^\$\n]+?)\$/);
        if (m) return { type: 'mathInline', raw: m[0], text: m[1] };
      },
      renderer(t) { return `<span class="math-inline">$${t.text}$</span>`; }
    },
    {
      name: 'mathBlock',
      level: 'block',
      start(src) { return src.indexOf('$$'); },
      tokenizer(src) {
        const m = src.match(/^\$\$([\s\S]+?)\$\$/);
        if (m) return { type: 'mathBlock', raw: m[0], text: m[1] };
      },
      renderer(t) { return `<div class="math-block">$$${t.text}$$</div>`; }
    },
  ]
});
```

### A7.4 前端：渲染後呼叫 KaTeX

新增工具函式：
```js
function renderMath(container) {
  if (typeof renderMathInElement !== 'function') return;
  renderMathInElement(container, {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '$',  right: '$',  display: false },
      { left: '\\(', right: '\\)', display: false },
      { left: '\\[', right: '\\]', display: true },
    ],
    throwOnError: false,
  });
}
```

在以下位置呼叫：
- `fetchContent` 結尾（`paper-content.innerHTML = marked.parse(content)` 之後）：
  ```js
  renderMath(document.getElementById('paper-content'));
  ```
- `loadChatHistory` 內每個 ai 訊息 render 完之後（迴圈內）：
  ```js
  div.innerHTML = marked.parse(formatted);
  renderMath(div);
  ```
- `sendMessage` 內 SSE chunk done 之後：
  ```js
  aiMsg.innerHTML = marked.parse(formatted);
  renderMath(aiMsg);
  ```
- `attachToStream` 內 chunk done 之後同樣補

### A7.5 CSS

```css
.katex-display {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.5em 0;
  margin: 1em 0;
}
.math-inline, .math-block { font-family: KaTeX_Main, 'Latin Modern', serif; }
```

**驗證**：開啟一篇含公式的論文 → 公式以向量數學排版顯示，不再裸露文字。

---

# Task B · P2 inconsistencies（規範與視覺對齊）

## B1. `--font-h1 / --font-h2 / --font-small` 不在主 token scale

**檔案**：`static/index.html`

**修改前**（CSS `#current-title` 區塊）：
```css
#current-title .title-zh { font-size: var(--font-h1, 22px); }
#current-title .title-en { font-size: var(--font-h2, 14px); }
#current-title .title-meta { font-size: var(--font-small, 12px); }
#current-title details.title-abstract { font-size: var(--font-base, 13px); }
```

**修改後**：
```css
#current-title .title-zh { font-size: var(--font-2xl); font-weight: 700; }
#current-title .title-en { font-size: var(--font-sm); }
#current-title .title-meta { font-size: var(--font-xs); }
#current-title details.title-abstract { font-size: var(--font-base); }
```

---

## B2. 主題層仍寫 `#content-toolbar h2`（HTML 已無 h2）

**檔案**：6 個 `static/themes/*.css`

**現況**：每個主題都有
```css
#content-toolbar h2 { font-size: 28px; ... }
```
HTML 改成 `<header id="current-title">` 後此規則不命中。

**修改**：把每個主題的 `#content-toolbar h2` 改為 `#current-title .title-zh`：
```css
#current-title .title-zh {
  font-family: var(--font-display);
  font-size: 28px;            /* 各主題自己的數值，不變 */
  font-weight: 500;
  letter-spacing: -0.01em;
  line-height: 1.25;
  color: var(--color-text);
}
```

每個主題各自保留原本字級／字重，只改 selector。

---

## B3. demo-bar CSS 死代碼

**檔案**：`static/index.html`

**做法**：刪除 CSS 段 `#demo-bar` `.label` `.name` `.seg` `.seg button` `.spacer` 整段（約 30 行）；同時刪除 JS 中：
```js
const stateBtns = document.querySelectorAll('#demo-bar .seg button');
function syncStateBar() { ... }
stateBtns.forEach(b => b.addEventListener('click', ...));
```
保留呼叫點 `syncStateBar()`：把它在 `sidebar-toggle` / `chat-toggle` handler 內的呼叫一併移除。

---

## B4. tooltip JS 不見了

**檔案**：`static/index.html`

**做法**：找位置「`syncCollapseTips`」附近，在後面加上：

```js
// Tooltip：data-tip 屬性觸發、200ms 出現、800ms 自動消失、100ms 隱藏延遲
(function setupTooltip() {
  const tip = document.getElementById('tooltip');
  const SHOW_DELAY = 200, VISIBLE_DURATION = 800, HIDE_DELAY = 100;
  let showTimer = null, autoHideTimer = null, hideTimer = null;
  let visibleEl = null, dismissedEl = null;
  function position(el) {
    const r = el.getBoundingClientRect(), tr = tip.getBoundingClientRect();
    const gap = 8;
    let left = r.left - tr.width - gap;
    let top = r.top + r.height / 2 - tr.height / 2;
    if (left < 4) left = r.right + gap;
    top = Math.max(4, Math.min(top, window.innerHeight - tr.height - 4));
    tip.style.left = left + 'px'; tip.style.top = top + 'px';
  }
  function show(el) {
    [showTimer, hideTimer, autoHideTimer].forEach(t => t && clearTimeout(t));
    showTimer = hideTimer = autoHideTimer = null;
    tip.textContent = el.getAttribute('data-tip') || '';
    tip.classList.add('visible'); position(el); visibleEl = el;
    autoHideTimer = setTimeout(() => {
      tip.classList.remove('visible'); dismissedEl = visibleEl;
      visibleEl = null; autoHideTimer = null;
    }, VISIBLE_DURATION);
  }
  function hideNow() {
    if (autoHideTimer) clearTimeout(autoHideTimer);
    if (hideTimer) clearTimeout(hideTimer);
    autoHideTimer = hideTimer = null;
    tip.classList.remove('visible'); visibleEl = null;
  }
  document.addEventListener('mouseover', (e) => {
    const el = e.target.closest('[data-tip]');
    if (!el) return;
    if (el === dismissedEl) return;
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
    if (visibleEl === el) return;
    if (visibleEl) { show(el); }
    else {
      if (showTimer) clearTimeout(showTimer);
      showTimer = setTimeout(() => {
        showTimer = null;
        if (document.contains(el)) show(el);
      }, SHOW_DELAY);
    }
  });
  document.addEventListener('mouseout', (e) => {
    const el = e.target.closest('[data-tip]');
    if (!el) return;
    if (e.relatedTarget && el.contains(e.relatedTarget)) return;
    dismissedEl = null;
    if (showTimer) { clearTimeout(showTimer); showTimer = null; }
    if (visibleEl === el) {
      if (hideTimer) clearTimeout(hideTimer);
      hideTimer = setTimeout(() => { hideTimer = null; hideNow(); }, HIDE_DELAY);
    }
  });
  window.addEventListener('scroll', hideNow, true);
  window.addEventListener('blur', hideNow);
})();
```

**驗證**：停留任一 icon ≥200ms → 左側出現 tooltip；停 800ms 後自動消失；移到下個 icon 立即接力。

---

## B5. `.modal-input` CSS 完全沒定義

**檔案**：`static/index.html`

**位置**：CSS `.modal-box select:focus` 之後加入。

```css
.modal-box .modal-input,
.modal-box input[type="text"] {
  width: 100%;
  height: var(--btn-h);
  padding: 0 var(--space-3);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  color: var(--color-text);
  font-family: inherit;
  font-size: var(--font-base);
  outline: none;
  margin-bottom: var(--space-2);
  box-sizing: border-box;
  transition: border-color var(--transition);
}
.modal-box .modal-input:focus,
.modal-box input[type="text"]:focus {
  border-color: var(--color-accent);
  /* color-mix 計算 accent 18% 透明度光環，跨主題自動跟色 */
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-accent) 18%, transparent);
}
```

**驗證**：打開 tag-modal → input 應 100% 寬、與 select 同樣質感、focus 時主題色光環。

---

## B6. `#export-btn` 收合殘留

**檔案**：`static/index.html`

**位置**：CSS `.collapsed` 規則區。

**修改前**：
```css
#chat-panel.collapsed > #chat-header > .h-title,
#chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle),
#chat-panel.collapsed > #chat-messages,
#chat-panel.collapsed > #chat-input-area { display: none; }
```

**修改後**：
```css
#chat-panel.collapsed > #chat-header > .h-title,
#chat-panel.collapsed > #chat-messages,
#chat-panel.collapsed > #chat-input-area { display: none; }
/* 拆出單獨 rule + !important，蓋過 enableChat() 用 inline style 設的 display:block */
#chat-panel.collapsed > #chat-header > #chat-header-actions > :not(#chat-toggle) {
  display: none !important;
}
```

**驗證**：載入 paper（觸發 enableChat）→ 點右欄漢堡 → export-btn 應消失、漢堡居中於 48px rail。

---

## B7. details 不撐滿 + toolbar/正文軸線不對齊

**檔案**：`static/index.html`

**做法**：抽 `--content-max-w` token + toolbar 跟著置中。

**主檔 `:root` 加**：
```css
--content-max-w: 760px;          /* 預設；各主題自行覆寫 */
```

**主檔 CSS**：
```css
#content-toolbar {
  /* 既有 padding / border 不變 */
  max-width: var(--content-max-w);
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
#paper-content {
  /* 既有 padding 不變 */
  max-width: var(--content-max-w);
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
#current-title details.title-abstract {
  width: 100%;
  box-sizing: border-box;
}
```

**每個主題 css 同步**：把原本 `#paper-content { max-width: 720px; }` / `860px` / 等改成覆寫 token：
```css
:root { --content-max-w: 720px; }      /* kahn 用這個值，其他主題依自己原本 max-width */
```
並刪除主題內 `#paper-content { max-width: ... }`（避免重複定義）。

---

## B8. 中欄正文與 toolbar 重複的標題＋元數據

**檔案**：`processor/md_restore_processor.py` + `static/index.html`

### B8.1 後端：把 metadata block 用 div + class 標記

`_render_header_en` / `_render_header_zh` 內：
```python
def _render_header_en(meta):
    meta_bits = []
    if authors_list: meta_bits.append(f"- **Authors**: {', '.join(...)}")
    if date: meta_bits.append(f"- **Date**: {date}")
    if venue: meta_bits.append(f"- **Venue**: {venue}")
    if doi: meta_bits.append(f"- **DOI**: {doi}")
    if keywords: meta_bits.append(f"- **Keywords**: {', '.join(keywords)}")
    meta_md = "\n".join(meta_bits)
    return (
        f"# {title}\n\n"
        f"<div class=\"paper-header-meta\">\n\n"
        f"{meta_md}\n\n"
        f"</div>\n\n"
    )
```
中文版同理（`> **作者**：` → `- **作者**：` 並包進 `<div class="paper-header-meta">`）。

### B8.2 前端：`@media screen` 隱藏

CSS：
```css
@media screen {
  #paper-content > h1:first-child,
  #paper-content > .paper-header-meta {
    display: none;
  }
}
```

**驗證**：螢幕上正文開頭乾淨；按 Cmd/Ctrl+P 列印預覽會看到 h1 + metadata 列表。

---

# Task C · P3 polish（清理 + 重構）

## C1. placeholder 兩行顯示

**檔案**：`static/index.html`

**HTML**：
```html
<div id="chat-input"
     ...
     data-placeholder="輸入問題（Ctrl+Enter 送出）&#10;輸入 # 可加入 hashtag 跨文獻搜尋"></div>
```

**CSS**：
```css
#chat-input {
  min-height: 56px;          /* 預留兩行 placeholder 高度，避免 type 時跳動 */
  /* 其他屬性不變 */
}
#chat-input:empty::before {
  content: attr(data-placeholder);
  white-space: pre-wrap;     /* 讓 &#10; 顯示為實際換行 */
  color: var(--color-text-subtle);
  pointer-events: none;
  display: block;
}
```

---

## C2. `<link href>` theme 路徑

**檔案**：`static/index.html`

由於本檔由 Flask 從 `/static/` 提供，路徑 `href="/static/themes/kahn.css"` 是對的。**不動。**

但 prototype 純前端開啟時會 404 — 在文件層註明：
- 開發 prototype 用 `themes/kahn.css`（相對）
- 部署 Flask 用 `/static/themes/kahn.css`（絕對）

或寫成 base href / build-time 替換。**現階段保留現狀**。

---

## C3. `useWebSearch` 隱式全域 → 顯式宣告

**檔案**：`static/index.html`

**修改前**：
```js
(() => {
  const wsBtn = document.getElementById('web-search-toggle');
  wsBtn.addEventListener('click', () => {
    useWebSearch = wsBtn.classList.contains('active');
  });
  useWebSearch = wsBtn.classList.contains('active');
})();
```

**修改後**：把 `let useWebSearch = false;` 移到 script 上方的全域變數區（與 `currentPaperId` / `isProcessing` 並列），IIFE 內直接賦值即可。

---

## C4. 內部 ticket 註解清理

**做法**：grep `Phase 4\.7` `RAG-1` `Commit 1[0-9]` 找到所有 ticket 註解，**改寫成「為什麼」而非「哪個 ticket」**。例：

```js
// 改前
/* Phase 4.7c 修正 4：沒 paper 時清空但保留元素 */

// 改後
/* 沒 paper 時清空 innerHTML 但保留元素，維持 toolbar flex:1 槽位 */
```

不必逐字修，只要把「Phase x.x.x / Commit N」這類**內部編號**抽掉即可。

---

## C5. marked strikethrough hack 註解強化

**檔案**：`static/index.html`

**現況**：有一段 `marked.use({ extensions: [{ name: 'del', ... }] })` 關掉 GFM strikethrough。

**做法**：在該段前加更清楚的註解，說明「為何要關 + 何時可移除」：

```js
// 關閉 GFM strikethrough（~~text~~ 與單 ~ 撞線）
//
// 為何：marked.js 預設啟用 GFM strikethrough、單 ~ 也會匹配。論文 / 履歷
//       常見「100~500 人」「2003/8~ 仍在職」這類數值範圍會被誤判為刪除線。
// 何時可移除：marked.js 升到能精準區分「波浪號範圍」與「strikethrough」之後；
//             或全文清掃確認無合法 ~~text~~ 用法時。
```

---

## C6. focus listener dead code

**檔案**：`static/index.html`

刪除這段（contenteditable=false 已防護，永不觸發）：
```js
document.getElementById('chat-input').addEventListener('focus', () => {
  if (!currentPaperId) {
    alert('請先選擇文件');
    document.getElementById('chat-input').blur();
  }
});
```

---

## C7. paper-menu-btn / folder menu-btn ⋯ icon SVG 化

**檔案**：`static/index.html`

**位置**：`renderPapers` 內 innerHTML 模板 + `renderFolderTree` 內 row.innerHTML 模板。

**修改前**：
```js
<button class="paper-menu-btn icon-only" title="更多">⋯</button>
```

**修改後**：
```js
<button class="paper-menu-btn icon-only" data-tip="文件選單">
  <svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1" fill="currentColor" stroke="none"/></svg>
</button>
```

folder menu-btn 同理（`data-tip="資料夾選單"`）。

---

## C8. inline `style.display = ...` 重構為 class（**選做**）

**範圍**：grep `\.style\.display = ` 找出所有點。

**建議改法**：每個 toggle 點改用 `classList.add/remove` + CSS class 控 display。屬於技術債清理，可獨立 PR。

本任務檔**列出但不要求做**；若 Claude Code 時間充裕，可順手做；否則跳過。

---

# 設計文件同步

完成程式碼修改後，**同 commit** 更新以下 docs：

| 文件 | 章節 | 改動 |
|---|---|---|
| `docs/principles.md` | §2 視覺承諾表 | 補一行「`<-` 列表取代 `>` blockquote 作為 metadata（避免 marked 單行合併）」 |
| `docs/principles.md` | §8 範圍外 | 「螢幕閱讀器」項補一句「不規範 aria-label，但保留 `data-tip` 系統」 |
| `docs/typography.md` | §1 字級階梯表 | `--font-h1 / h2 / small` 不存在；改寫文章寫死成 `--font-2xl / sm / xs` |
| `docs/color-tokens.md` | §1 Token 清單 | 補一條 `--content-max-w` |
| `docs/spacing.md` | §1 階梯 | 補一條 `--content-max-w`（雖然是寬度 token 不是間距） |
| `docs/components.md` | §2.4 內建通用 modal | 加 `customPrompt` 第三個函式說明、prompt-modal DOM 結構 |
| `docs/components.md` | §4.1 Tooltip 觸發 | 確認 200ms / 800ms / 100ms 數值跟 setupTooltip 一致 |
| `docs/components.md` | §6.1 共通 | 補 `.modal-input` 規格（同 select） |
| `docs/components.md` | §10 反例 | 補一條「inline `el.style.display = ...` 在 .collapsed 規則前 → 用 class toggle」 |
| `docs/icon-spec.md` | §4 標準 icon 集 | paper-menu-btn / folder menu-btn 從「⋯ 文字」改為「3 個 circle SVG」 |
| `docs/icon-spec.md` | §5 Tooltip 規範 | 補一句「`data-tip` 取代 `title` 屬性，所有 paper-menu / folder menu 同步」 |
| `docs/interaction.md` | §3 Tooltip 觸發 | 數值與 §4.1 同步 |
| `docs/interaction.md` | §4 Popup 關閉 | 補一條「ESC 鍵先關 popup、再關 modal（兩層獨立）」 |
| `docs/interaction.md` | §5 Modal | 加 customPrompt 流程 |
| `docs/dom-reference.md` | §6 彈出層 | 補 `#prompt-modal` + `#prompt-box` + `#prompt-input` 結構 |
| `docs/dom-reference.md` | §7.3 paper-item.uploading | 確認 `pointer-events: none` 仍在 |
| `docs/api-integration.md` | §12 規劃中 | 把「自訂 CSS 主題上傳」從規劃中移到正式章節（已實作） |
| `docs/copywriting.md` | §4.2 tooltip 對照表 | paper-menu / folder menu 對應「文件選單」/「資料夾選單」 |
| `docs/theme-guide.md` | §3 必填覆寫規則 | `#content-toolbar h2` → `#current-title .title-zh`（selector 改名） |
| `docs/theme-guide.md` | §2 必填 token | 補 `--content-max-w` |

---

# 執行順序

1. **Task A1 + A2**（5 分鐘）— 救最致命的 bug
2. **Task A4**（5 分鐘）— 清掉重複 close
3. **Task A3**（30 分鐘）— customPrompt + 全面替換
4. **Task A5 + A6**（15 分鐘）— theme upload + ESC
5. **Task A7**（45 分鐘）— LaTeX 渲染
6. **Task B 全部**（1 小時）— 規範對齊
7. **Task C 全部**（30 分鐘）— polish
8. **設計文件同步**（30 分鐘）

**總計**：約 3.5 小時。

每個 task 完後跑驗證步驟、commit；不要把多個 task 揉一起。

---

# 驗證 checklist（最終）

完成所有 task 後，逐項勾核：

- [ ] 上傳一篇 PDF → 處理完成 → 中欄標題顯示完整 multi-row
- [ ] 重整頁面 → 中欄顯示「從左側選擇文件」
- [ ] 點刪除文件 → 自訂 confirm modal、非 native confirm
- [ ] 點清除殘檔 → 自訂 confirm modal
- [ ] 點新增資料夾 → 自訂 prompt modal
- [ ] 上傳自訂 .css → 重整後下拉選單仍可見
- [ ] 開 theme-modal → 點 dropdown → 按 ESC → popup 關但 modal 還在
- [ ] 開含公式論文 → 公式正確渲染（KaTeX）
- [ ] 螢幕上看正文 → 不重複出現 h1 標題
- [ ] Cmd+P 列印預覽 → h1 + metadata 列表顯示
- [ ] 收合右欄 → 只有漢堡居中於 48px rail
- [ ] tag-modal 內 input → 100% 寬 + accent 色 focus 光環
- [ ] 中欄 toolbar 與正文軸線對齊（寬螢幕觀察）
- [ ] hover icon ≥200ms → tooltip 出現左側
- [ ] hover 800ms 後 → tooltip 自動消失
- [ ] 移到下一個 icon → 立即接力
- [ ] 切到任一主題 → toolbar 標題字級正確跟隨
- [ ] 切到任一主題 → modal input focus 光環顏色跟主題 accent
- [ ] paper-menu-btn / folder menu-btn → 顯示 SVG 三點而非文字 ⋯
- [ ] grep `Phase 4\.7` / `RAG-1` → 註解都改為描述性語言
- [ ] DevTools console → 無 error / warning

---

**任務檔結束。** 完成後請回報哪幾個 task 已 commit、哪幾個遇到問題。
