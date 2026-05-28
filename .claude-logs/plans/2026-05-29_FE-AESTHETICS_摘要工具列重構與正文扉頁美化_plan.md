# FE-AESTHETICS 摘要工具列重構與正文扉頁美化 plan

> 本計畫旨在重構摘要工具列（#abstract-toolbar）以提供 100% 滿寬與無內部滾動條的高自適應排版、廢除中欄標題區冗餘的中繼資料列（移除 .title-meta）、加入正文主動防禦性折行機制，並解鎖且重塑正文最上方的學術扉頁為經典階梯式學術 PDF 排版，一併解決作者隱藏而機構懸空的視覺 Bug。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：當前中欄摘要文字展開寬度僅為標題欄之一半左右，高度受限於 `max-height: 12rem` 與 `overflow-y: auto` 並產生內部滾動條，極不美觀。此外，由於螢幕模式隱藏了正文最上方的學術扉頁（`.paper-header-meta`），導致 raw `authors_info` 中未隱藏的機構單位懸空於正文最上方，產生嚴重視覺 Bug；標題下方之作者、日期、出處等元數據列排版緊湊、重疊度高；且正文大容器缺乏防禦性折行，長字串常擠爆版面。
- **解法**：
  1. **摘要重構**：新增獨立滿寬摘要容器 `#abstract-toolbar`，寬度 100% 與 `#content-toolbar` 等寬且對稱。徹底解鎖高度與寬度限制（無內部滾動條、100% 自然撐開，寬度撐滿 100%）。
  2. **廢除標題中繼資料列**：完全廢除並移除 `#current-title` 內部的 `.title-meta` 與相關 JS 渲染與 CSS，使導航列徹底乾淨。
  3. **防禦性折行**：為 `#paper-content` 及其文字與 code 子元素設定主動防禦性折行與局部自主橫向滾動。
  4. **學術扉頁重塑**：後端重塑 `.paper-header-meta` 為類似實體學術 PDF 的經典中心對稱階梯式排版（標題 ➡️ 帶上標作者群 ➡️ 日期與出處 ➡️ DOI ➡️ 關鍵字），前端解鎖並重新顯示該區塊。此時作者群與元數據正常置中排版，消除了原本因為螢幕隱藏扉頁導致 raw `authors_info` 機構單位單獨懸空的視覺 Bug。
- **影響**：影響前端靜態頁面 `static/index.html` 的 HTML DOM 結構、CSS 樣式與 JS 渲染邏輯，影響後端 Markdown 還原處理器 `processor/md_restore_processor.py` 的元數據渲染，並需同步重構 `tests/test_bug_b2_paper_header_meta.py`、`tests/test_bug_f5_p2_inconsistencies.py` 與 `tests/test_md_restore_processor.py` 單元測試。

---

## §2 目標規格

### §2.1 前端 UI 規格 (#abstract-toolbar & Word Wrap)

1. **中欄摘要重構 (`#abstract-toolbar`)**：
   - 摘要容器寬度 100% 與 `#content-toolbar` 相同（最大寬度為 `var(--content-max-w)`），居中對稱，背景與中欄底色同色或略暗。
   - 移除摘要高度限制 `max-height` 與內部捲軸 `overflow-y: auto`，展開後根據 DOM 內容高度 100% 自然撐開，不產生內部滾動條。
   - 展開後的 `.abstract-body` 寬度為 `#abstract-toolbar` 的 100%（撐滿滿寬）。
2. **中繼資料列廢除**：
   - 完全移除 `#current-title` 內部的 `.title-meta` 與 `.title-meta-sep` 的相關 CSS 樣式與 JS 渲染代碼。
3. **防禦性折行與防溢出**：
   - `#paper-content` 加入 `overflow-x: hidden`。
   - 其子元素 `p, li, div, span` 啟用 `overflow-wrap: break-word`、`word-wrap: break-word` 與 `word-break: break-word`，進行防禦性斷行。
   - `pre, code` 設定 `max-width: 100%` 與 `overflow-x: auto`，使其在寬度不足時自主進行局部橫向滾動，不破壞正文版面。

### §2.2 後端扉頁規格 (.paper-header-meta & Stepped Layout)

1. **解除螢幕隱藏**：
   - 徹底移除 `@media screen { #paper-content > h1:first-child, #paper-content > .paper-header-meta { display: none; } }`，使扉頁在螢幕上直接呈現。
2. **階梯式經典排版**：
   - 重塑後端 `_render_header_en` 與 `_render_header_zh` 在 `.paper-header-meta` 中輸出的 HTML 結構，呈經典階梯式學術排版：
     - **標題**：置中顯示。
     - **作者群**：置中顯示，字體適中。
     - **日期與出處**：置中顯示，以圓點（·）或空格分隔。
     - **DOI / 關鍵字**：置中顯示。
     - *(註：依據 v1.2 方案 A，因 MinerU organization 語意衝突，本版本暫不引入 affiliation 機構單位欄位)*
3. **完美列印**：
   - 列印時直接沿用重塑後的學術扉頁。`#abstract-toolbar` 在列印模式下設為 `display: none !important`。

---

## §3 現況與證據

詳細盤點與本功能相關的現有程式碼邏輯與關鍵調用鏈（確切的檔案與行數，附帶 `grep` 核查證據）：

- **`static/index.html`**：
  - `CSS 規則 L716-L738`：定義了 `.title-meta` 與 `details.title-abstract` 的舊版寬度、高度與滾動條限制。
  - `JS 渲染 L2436-L2463`：在 `renderTitleHeader` 函數中動態渲染 `.title-meta` 與 `details.title-abstract`。
  - `DOM 結構 L1387-L1414`：中欄 toolbar 佈局，尚無獨立的 `#abstract-toolbar`。
  - `CSS Hiding 規則 L803-L808`：在螢幕模式下隱藏 `h1:first-child` 與 `.paper-header-meta`。
- **`processor/md_restore_processor.py`**：
  - `_render_header_en L435-489` 與 `_render_header_zh L492-544`：使用單純的 `- list` 格式將元數據串接輸出為 markdown，未進行階梯式 HTML 排版。
- **`tests/test_bug_b2_paper_header_meta.py`**：
  - `test_b10_frontend_media_screen_hides_h1_and_header_meta L149-163`：驗證了螢幕隱藏規則的存在。
- **`tests/test_bug_f5_p2_inconsistencies.py`**：
  - `test_b1_main_scale_tokens_in_current_title L52-95`：驗證了雙語標題中舊版 `.title-meta` 樣式與 `#current-title` 摘要寬度限制。

### §3.1 grep 鋼鐵證據

```bash
$ grep -n "class=\"title-meta\"" static/index.html
2438:    if (org) parts.push(`<p class="title-meta">${_esc(org)}</p>`);
2449:      parts.push(`<p class="title-meta">${bits.join('<span class="title-meta-sep">·</span>')}</p>`);

$ grep -n "details.title-abstract" static/index.html
728:  #current-title details.title-abstract {
765:  #current-title details.title-abstract > summary {
773:  #current-title details.title-abstract > summary::before { content: "▸ "; }
774:  #current-title details.title-abstract[open] > summary::before { content: "▾ "; }
775:  #current-title details.title-abstract[open] > summary {
779:  #current-title details.title-abstract .abstract-body {
3295:        // h1.title-zh / p.title-en / p.title-meta / details.title-abstract / .paper-tags

$ grep -n "def test_" tests/test_bug_b2_paper_header_meta.py
31:def test_render_header_en_academic_uses_dash_list_and_wrap():
92:def test_render_header_zh_academic_uses_dash_list_and_wrap():
82:def test_render_header_en_resume_blockquote_preserved():
104:def test_render_header_zh_resume_blockquote_preserved():
125:def test_render_header_en_academic_no_meta_no_wrap():
149:def test_b10_frontend_media_screen_hides_h1_and_header_meta():
165:def test_b10_frontend_class_hook_not_in_print_media():
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `static/index.html` 中的 `#current-title` 雙語標題與 `#paper-tags` 的 tag-pill 渲染邏輯嚴禁刪除（必須保留常駐導航）。
- [ ] `processor/md_restore_processor.py` 中的 `RestoreProcessor._clean_authors_info` 邏輯（核心 authors_info 清理，為核心邏輯防 Regress）。
- [ ] `RestoreProcessor` 對 `doc_type == 'resume'` 的 `_resolve_candidate_extras` 與 `blockquote` Preservation 邏輯嚴禁改動（維持履歷特例路徑）。

---

## §5 規格依據

| 依據名稱     | 來源位置                                    |
| ------------ | ------------------------------------------- |
| 既有專案框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 工作流程規範 | `ref/WORKFLOW_SOP.md`                       |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有與重構後的測試執行**：
  In OrbStack 的 `claude-lab` 環境中執行所有的單元測試，確保完全通過且沒有 Regression：

  ```bash
  orb -m claude-lab ./venv/bin/pytest tests/ -v
  ```

- **覆蓋率驗證**：
  本次重構與修正直接影響以下單元測試檔案，執行時將針對這些檔案進行精準驗證：

  - `tests/test_bug_b2_paper_header_meta.py`
  - `tests/test_bug_f5_p2_inconsistencies.py`
  - `tests/test_md_restore_processor.py`

### §6.2 手動端到端（E2E）驗證流程

1. **基本呈現驗證**：
   - 開啟系統，從左側點選一篇學術論文（例如 `800-vdc-architecture-for-ai-infrastructure`）。
   - 觀察中欄上方：
     - `#content-toolbar` 內僅顯示雙語標題與標籤，不再顯示作者、日期與出處等元數據資訊。
     - `#abstract-toolbar` 完整顯示，展開摘要時寬度為中欄主體的 100%，高度自動撐滿，沒有任何內部垂直滾動條。
2. **扉頁美化驗證**：
   - 滾動中欄正文區 `#paper-content`，最上方應呈現居中對稱的經典學術 PDF 階梯式扉頁。
   - 檢查扉頁內容，應依序置中排列：標題 ➡️ 作者群 ➡️ 日期與出處 ➡️ DOI ➡️ 關鍵字。
3. **防禦性斷行驗證**：
   - 匯入或預覽包含超長字串（如超長等號分隔線 `=======`）或超長程式碼區塊的文件。
   - 觀察正文邊界，文字元素（`p`, `li`, `div`, `span`）應自動折行，程式碼與預格式化區塊（`pre`, `code`）應出現局部橫向滾動條，整體版面絕不橫向撐破或溢出中欄。
4. **列印預覽驗證**：
   - 點選列印按鈕（或按下 Cmd+P）。
   - 預覽中欄正文，學術扉頁完美呈現，`#abstract-toolbar` 應自動隱藏（`display: none !important`），列印版面整潔，無 any 樣式混亂。

---

## §7 Open Questions

| 開放問題                                           | 推薦方案                     | 推薦理由                                                     |
| -------------------------------------------------- | ---------------------------- | ------------------------------------------------------------ |
| 是否有任何懸空元數據在 Resume 履歷類型中需要處理？ | **維持現狀（履歷路徑不變）** | 履歷（Resume）類型的排版與結構不同於一般的學術論文，現有履歷路徑（`doc_type == 'resume'`）在前後端均有特殊的簡化渲染與樣式，應將其列入不可動清單以防 Regression。 |
| 列印時摘要是否應該被保留？                         | **不保留，直接隱藏**         | 學術 PDF 的列印標準通常僅要求列印文章主體與扉頁資訊，摘要已於網頁端提供獨立開關且不屬於實體正文必要列印項目，隱藏摘要能保證列印結果與傳統學術 PDF 完全一致。 |

---

## §8 變動前與變動後程式碼 (Pre-Change & Post-Change Diffs)

### §8.1 `static/index.html` - DOM 佈局變更

#### 【異動前】 (L1387-L1414)

```html
    <div id="content-toolbar">
      <!-- title 區放 toolbar 內、取 flex:1 槽位（多行可自然展開）。
           沒 paper 時走 innerHTML='' 清空、不用 hidden 屬性（hidden 會 display:none
           退出 flex layout、actions 會滑左）；元素永遠佔 flex:1 槽位 -->
      <header id="current-title"></header>
      <div class="toolbar-actions">
        <button id="lang-toggle" class="icon-only" data-tip="語言切換">
          <!-- 切換符號：水平 ⇄；兩條短橫線錯位、不重疊 -->
          <svg viewBox="0 0 24 24"><path d="M17 4l3 3-3 3M20 7H10"/><path d="M7 14l-3 3 3 3M4 17h10"/></svg>
        </button>
        <button id="print-btn" class="icon-only" data-tip="列印文件">
          <svg viewBox="0 0 24 24"><path d="M7 9V3h10v6"/><path d="M7 18H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2"/><path d="M7 14h10v7H7z"/></svg>
        </button>
        <!-- # 標籤編輯按鈕（toolbar-actions 末尾、極小 icon-only、開啟 #tag-modal） -->
        <button id="edit-tags-btn" class="icon-only" data-tip="編輯標籤">
          <svg viewBox="0 0 24 24"><path d="M4 9h16M4 15h16M10 3L8 21M16 3l-2 18"/></svg>
        </button>
      </div>
    </div>
    <!-- BUG-F4 A2（ui-fixes-batch A2）：預設顯示反轉——empty-state 預設顯示、paper-content 預設 hide
         既有 loadPaper 內 toggle 邏輯不變（hide empty / show paper）；
         初始無 paper 時中欄顯示「從左側選擇文件」、不再空白 -->
    <div id="empty-state">
      <svg width="16" height="16" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-6-6a1.5 1.5 0 0 1 0-2l6-6"/></svg>
      從左側選擇文件
    </div>
    <div id="paper-content" style="display:none"></div>
```

#### 【異動後】

```html
    <div id="content-toolbar">
      <!-- title 區放 toolbar 內、取 flex:1 槽位（多行可自然展開）。
           沒 paper 時走 innerHTML='' 清空、不用 hidden 屬性（hidden 會 display:none
           退出 flex layout、actions 會滑左）；元素永遠佔 flex:1 槽位 -->
      <header id="current-title"></header>
      <div class="toolbar-actions">
        <button id="lang-toggle" class="icon-only" data-tip="語言切換">
          <!-- 切換符號：水平 ⇄；兩條短橫線錯位、不重疊 -->
          <svg viewBox="0 0 24 24"><path d="M17 4l3 3-3 3M20 7H10"/><path d="M7 14l-3 3 3 3M4 17h10"/></svg>
        </button>
        <button id="print-btn" class="icon-only" data-tip="列印文件">
          <svg viewBox="0 0 24 24"><path d="M7 9V3h10v6"/><path d="M7 18H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2"/><path d="M7 14h10v7H7z"/></svg>
        </button>
        <!-- # 標籤編輯按鈕（toolbar-actions 末尾、極小 icon-only、開啟 #tag-modal） -->
        <button id="edit-tags-btn" class="icon-only" data-tip="編輯標籤">
          <svg viewBox="0 0 24 24"><path d="M4 9h16M4 15h16M10 3L8 21M16 3l-2 18"/></svg>
        </button>
      </div>
    </div>
    <div id="abstract-toolbar" style="display:none"></div>
    <!-- BUG-F4 A2（ui-fixes-batch A2）：預設顯示反轉——empty-state 預設顯示、paper-content 預設 hide
         既有 loadPaper 內 toggle 邏輯不變（hide empty / show paper）；
         初始無 paper 時中欄顯示「從左側選擇文件」、不再空白 -->
    <div id="empty-state">
      <svg width="16" height="16" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-6-6a1.5 1.5 0 0 1 0-2l6-6"/></svg>
      從左側選擇文件
    </div>
    <div id="paper-content" style="display:none"></div>
```

---

### §8.2 `static/index.html` - CSS 樣式變更

#### 【異動前】 (L716-L738, L765-L786, L803-L808, L1174-L1182)

```css
  #current-title .title-meta {
    font-size: var(--font-xs);
    color: var(--color-text-subtle);
    margin: var(--space-1) 0 0 0;
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
    align-items: baseline;
  }
  #current-title .title-meta-sep {
    color: var(--color-border);
  }
  #current-title details.title-abstract {
    /* 摘要展開最大高度 + 滾動條、防超長摘要把 toolbar 整個撐爆
       BUG-F1 / BUG-F5：撐滿 #current-title 剩餘寬度、box-sizing 防 padding 撐爆、font-size 走主 scale */
    margin-top: var(--space-2);
    font-size: var(--font-base);
    color: var(--color-text);
    max-height: 12rem;
    overflow-y: auto;
    width: 100%;
    box-sizing: border-box;
  }
  ...
  #current-title details.title-abstract > summary {
    cursor: pointer;
    /* BUG-F5 B1（ui-fixes-batch B1）：--font-small 廢 token → 主 scale --font-xs */
    font-size: var(--font-xs);
    color: var(--color-text-subtle);
    user-select: none;
    list-style: none;
  }
  #current-title details.title-abstract > summary::before { content: "▸ "; }
  #current-title details.title-abstract[open] > summary::before { content: "▾ "; }
  #current-title details.title-abstract[open] > summary {
    color: var(--color-text);
    margin-bottom: var(--space-2);
  }
  #current-title details.title-abstract .abstract-body {
    line-height: 1.6;
    white-space: pre-wrap;
    padding: var(--space-2) var(--space-3);
    background: var(--color-surface, var(--color-bg));
    border-left: 3px solid var(--color-border);
    border-radius: 0 var(--radius-sm, 4px) var(--radius-sm, 4px) 0;
  }
  ...
  @media screen {
    #paper-content > h1:first-child,
    #paper-content > .paper-header-meta {
      display: none;
    }
  }

  /* 既有列印模式隱藏清單 */
  @media print {
    #sidebar,
    #chat-panel,
    #content-toolbar,
    #empty-state,
    #tooltip,
    .modal-mask,
    .ctx-popup {
      display: none !important;
    }
  }
```

#### 【異動後】

```css
  /* #abstract-toolbar 獨立摘要容器，滿寬居中且對稱 */
  #abstract-toolbar {
    flex-shrink: 0;
    padding: 0 var(--pad-panel) var(--space-2) var(--pad-panel);
    border-bottom: 1px solid var(--color-border);
    max-width: var(--content-max-w);
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
  }
  #abstract-toolbar details.title-abstract {
    margin-top: var(--space-2);
    font-size: var(--font-base);
    color: var(--color-text);
    width: 100%;
    box-sizing: border-box;
  }
  #abstract-toolbar details.title-abstract > summary {
    cursor: pointer;
    font-size: var(--font-xs);
    color: var(--color-text-subtle);
    user-select: none;
    list-style: none;
  }
  #abstract-toolbar details.title-abstract > summary::before { content: "▸ "; }
  #abstract-toolbar details.title-abstract[open] > summary::before { content: "▾ "; }
  #abstract-toolbar details.title-abstract[open] > summary {
    color: var(--color-text);
    margin-bottom: var(--space-2);
  }
  #abstract-toolbar details.title-abstract .abstract-body {
    line-height: 1.6;
    white-space: pre-wrap;
    padding: var(--space-2) var(--space-3);
    background: var(--color-surface, var(--color-bg));
    border-left: 3px solid var(--color-border);
    border-radius: 0 var(--radius-sm, 4px) var(--radius-sm, 4px) 0;
    width: 100%;
    box-sizing: border-box;
  }

  #paper-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden; /* 防止橫向溢出撐破中欄 */
    margin: 0 auto;
    width: 100%;
    max-width: var(--content-max-w);
    box-sizing: border-box;
  }
  
  /* 正文防禦性折行與防溢出機制 */
  #paper-content p,
  #paper-content li,
  #paper-content div,
  #paper-content span {
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;
  }
  #paper-content pre,
  #paper-content code {
    max-width: 100%;
    overflow-x: auto;
  }

  /* 學術 PDF 經典扉頁排版 */
  .paper-header-meta {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin: var(--space-4) auto var(--space-6) auto;
    padding-bottom: var(--space-4);
    border-bottom: var(--divider-w) solid var(--color-border);
    max-width: var(--content-max-w);
  }
  .paper-header-meta .header-authors {
    font-size: var(--font-base);
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: var(--space-1);
  }
  .paper-header-meta .header-venue-date {
    font-size: var(--font-sm);
    color: var(--color-text-subtle);
    margin-bottom: var(--space-1);
  }
  .paper-header-meta .header-doi {
    font-size: var(--font-xs);
    color: var(--color-text-subtle);
    margin-bottom: var(--space-2);
  }
  .paper-header-meta .header-keywords {
    font-size: var(--font-sm);
    color: var(--color-text-subtle);
    margin-top: var(--space-2);
  }
  #paper-content > h1:first-child {
    text-align: center;
    font-size: var(--font-2xl);
    font-weight: 700;
    color: var(--color-text);
    margin-top: var(--space-4);
    margin-bottom: var(--space-2);
    text-wrap: pretty;
  }

  /* 擴充列印模式隱藏清單，加入 #abstract-toolbar，防止摘要出現在印稿上 */
  @media print {
    #sidebar,
    #chat-panel,
    #content-toolbar,
    #abstract-toolbar,
    #empty-state,
    #tooltip,
    .modal-mask,
    .ctx-popup {
      display: none !important;
    }
  }
```
```

---

### §8.3 `static/index.html` - JS 邏輯變更 (`renderTitleHeader` & `deletePaper`)

#### 【異動前】 (L2418-L2473, L2682-L2690)

```javascript
function renderTitleHeader(p) {
  const el = document.getElementById('current-title');
  if (!el) return;
  // 沒 paper 時清空 innerHTML 但保留元素（占 toolbar flex:1 槽位、
  // 避免 actions 滑到左邊）。不再用 hidden 屬性。
  if (!p) { el.innerHTML = ''; return; }
  const m = p.metadata || {};
  const v = (k) => (m[k] && m[k].value) || null;
  const isResume = p.doc_type === 'resume';

  // title-zh：同 resolveDisplayTitle 中文優先；title-en：原文（避免重複）
  const titleZh = resolveDisplayTitle(p);
  const titleEnRaw = isResume ? '' : (v('title') || p.title || '');
  const titleEn = (titleEnRaw && titleEnRaw !== titleZh) ? titleEnRaw : '';

  const parts = [`<h1 class="title-zh">${_esc(titleZh)}</h1>`];
  if (titleEn) parts.push(`<p class="title-en">${_esc(titleEn)}</p>`);

  if (isResume) {
    const org = v('organization');
    if (org) parts.push(`<p class="title-meta">${_esc(org)}</p>`);
  } else {
    const bits = [];
    const authors = v('authors');
    if (Array.isArray(authors) && authors.length)
      bits.push(_esc(authors.join('、')));
    const date = v('publication_date');
    if (date) bits.push(_esc(date));
    const venue = v('journal_or_conference') || v('publisher') || v('organization');
    if (venue) bits.push(_esc(venue));
    if (bits.length)
      parts.push(`<p class="title-meta">${bits.join('<span class="title-meta-sep">·</span>')}</p>`);
    // 雙語摘要 fallback（中文模式優先取 translated_abstract、缺則 fallback 英文 abstract）
    // 繁中優先 → translated_abstract、無中譯則防禦性回退至英文 abstract
    const abstractEn = v('abstract');
    const abstractZh = v('translated_abstract') || abstractEn;
    const abstract = currentLang === 'zh' ? abstractZh : abstractEn;
    if (abstract) {
      parts.push(
        `<details class="title-abstract">`
        + `<summary>顯示摘要</summary>`
        + `<div class="abstract-body">${_esc(abstract)}</div>`
        + `</details>`
      );
    }
  }
  // tag-pill 渲染（半透明磨砂玻璃、依 components.md §11 規範）
  // BUG-F1 Bug 1：fallback chain 防禦（同 tag-modal 載入、PATCH 後 local 寫 metadata_json、API 回 metadata）
  const userTags = (p.metadata && p.metadata.user_tags) ||
                   (p.metadata_json && p.metadata_json.user_tags) || [];
  if (Array.isArray(userTags) && userTags.length) {
    const pills = userTags.map(t => `<span class="tag-pill">#${_esc(t)}</span>`).join('');
    parts.push(`<div class="paper-tags">${pills}</div>`);
  }
  el.innerHTML = parts.join('');
}
```
And inside `deletePaper` L2682-L2690:
```javascript
    if (currentPaperId === paperId) {
      currentPaperId = null;
      document.getElementById('content-toolbar').style.display = 'none';
      document.getElementById('empty-state').style.display = 'flex';
      document.getElementById('paper-content').style.display = 'none';
      document.getElementById('chat-messages').innerHTML = '<div class="chat-empty">選擇文件後開始提問</div>';
      document.getElementById('chat-input').setAttribute('contenteditable', 'false');
    }
```

#### 【異動後】

```javascript
function renderTitleHeader(p) {
  const el = document.getElementById('current-title');
  const abstractToolbar = document.getElementById('abstract-toolbar');
  if (!el) return;
  // 沒 paper 時清空 innerHTML 但保留元素，並清空隱藏摘要列
  if (!p) { 
    el.innerHTML = ''; 
    if (abstractToolbar) {
      abstractToolbar.innerHTML = '';
      abstractToolbar.style.display = 'none';
    }
    return; 
  }
  const m = p.metadata || {};
  const v = (k) => (m[k] && m[k].value) || null;
  const isResume = p.doc_type === 'resume';

  // title-zh：同 resolveDisplayTitle 中文優先；title-en：原文（避免重複）
  const titleZh = resolveDisplayTitle(p);
  const titleEnRaw = isResume ? '' : (v('title') || p.title || '');
  const titleEn = (titleEnRaw && titleEnRaw !== titleZh) ? titleEnRaw : '';

  const parts = [`<h1 class="title-zh">${_esc(titleZh)}</h1>`];
  if (titleEn) parts.push(`<p class="title-en">${_esc(titleEn)}</p>`);

  // 渲染獨立滿寬摘要容器
  if (abstractToolbar) {
    if (isResume) {
      abstractToolbar.innerHTML = '';
      abstractToolbar.style.display = 'none';
    } else {
      const abstractEn = v('abstract');
      const abstractZh = v('translated_abstract') || abstractEn;
      const abstract = currentLang === 'zh' ? abstractZh : abstractEn;
      if (abstract) {
        abstractToolbar.innerHTML = 
          `<details class="title-abstract">`
          + `<summary>顯示摘要</summary>`
          + `<div class="abstract-body">${_esc(abstract)}</div>`
          + `</details>`;
        abstractToolbar.style.display = 'block';
      } else {
        abstractToolbar.innerHTML = '';
        abstractToolbar.style.display = 'none';
      }
    }
  }

  // tag-pill 渲染
  const userTags = (p.metadata && p.metadata.user_tags) ||
                   (p.metadata_json && p.metadata_json.user_tags) || [];
  if (Array.isArray(userTags) && userTags.length) {
    const pills = userTags.map(t => `<span class="tag-pill">#${_esc(t)}</span>`).join('');
    parts.push(`<div class="paper-tags">${pills}</div>`);
  }
  el.innerHTML = parts.join('');
}
```
And inside `deletePaper`:
```javascript
    if (currentPaperId === paperId) {
      currentPaperId = null;
      document.getElementById('content-toolbar').style.display = 'none';
      const abstractToolbar = document.getElementById('abstract-toolbar');
      if (abstractToolbar) {
        abstractToolbar.innerHTML = '';
        abstractToolbar.style.display = 'none';
      }
      document.getElementById('empty-state').style.display = 'flex';
      document.getElementById('paper-content').style.display = 'none';
      document.getElementById('chat-messages').innerHTML = '<div class="chat-empty">選擇文件後開始提問</div>';
      document.getElementById('chat-input').setAttribute('contenteditable', 'false');
    }
```

---

### §8.4 `processor/md_restore_processor.py` - 後端扉頁渲染變更

#### 【異動前】 (L435-L489, L492-L544)

```python
def _render_header_en(
    title: str,
    doc_type: str,
    authors_list: list,
    date: str,
    venue: str,
    doi: str,
    keywords: list,
    candidate_extras: dict,
    domain: str,
    abstract: str = '',
) -> str:
    """產出 final_*_en.md 的 header（# title + meta block + abstract）。缺項靜默省略。"""
    lines = [f"# {title}", ""]

    if doc_type == 'resume':
        org = candidate_extras.get('organization', '')
        if org:
            lines.append(f"> **Organization**: {org}")
        if domain:
            lines.append(f"> **Domain**: {domain}")
        if lines and lines[-1] != "":
            lines.append("")
        return "\n".join(lines)

    # BUG-B2 Bug 10（v4 §B B10.3 / ui-fixes-batch B8.1）：
    # `>` blockquote → `-` list（避免 marked.js GFM 單換行不分段、塌成單行）
    # + 包進 <div class="paper-header-meta"> wrap（前端 CSS class hook 穩定 hide）
    # 適用：academic / book / technical / slides / news / web 等非 resume doc_type
    meta_bits = []
    if authors_list:
        meta_bits.append(f"- **Authors**: {', '.join(str(a) for a in authors_list)}")
    if date:
        meta_bits.append(f"- **Date**: {date}")
    if venue:
        meta_bits.append(f"- **Venue**: {venue}")
    if doi:
        meta_bits.append(f"- **DOI**: {doi}")
    if keywords:
        meta_bits.append(f"- **Keywords**: {', '.join(keywords)}")

    if meta_bits:
        lines.append('<div class="paper-header-meta">')
        lines.append("")
        lines.extend(meta_bits)
        lines.append("")
        lines.append('</div>')
        lines.append("")

    if abstract:
        lines.append("## Abstract")
        lines.append("")
        lines.append(abstract)
        lines.append("")
    return "\n".join(lines)


def _render_header_zh(
    title_zh: str,
    doc_type: str,
    authors_list: list,
    date: str,
    venue: str,
    doi: str,
    keywords: list,
    candidate_extras: dict,
    domain: str,
    abstract: str = '',
) -> str:
    """產出 final_*_zh.md 的 header（中文 label）。缺項靜默省略。"""
    lines = [f"# {title_zh}", ""]

    if doc_type == 'resume':
        org = candidate_extras.get('organization', '')
        if org:
            lines.append(f"> **機構**：{org}")
        if domain:
            lines.append(f"> **領域**：{domain}")
        if lines and lines[-1] != "":
            lines.append("")
        return "\n".join(lines)

    # BUG-B2 Bug 10（v4 §B B10.3 / ui-fixes-batch B8.1）：中文版同上
    # `>` blockquote → `-` list + 包 <div class="paper-header-meta"> wrap
    meta_bits = []
    if authors_list:
        meta_bits.append(f"- **作者**：{'、'.join(str(a) for a in authors_list)}")
    if date:
        meta_bits.append(f"- **日期**：{date}")
    if venue:
        meta_bits.append(f"- **出處**：{venue}")
    if doi:
        meta_bits.append(f"- **DOI**：{doi}")
    if keywords:
        meta_bits.append(f"- **關鍵字**：{'、'.join(keywords)}")

    if meta_bits:
        lines.append('<div class="paper-header-meta">')
        lines.append("")
        lines.extend(meta_bits)
        lines.append("")
        lines.append('</div>')
        lines.append("")

    if abstract:
        lines.append("## 摘要")
        lines.append("")
        lines.append(abstract)
        lines.append("")
    return "\n".join(lines)
```

#### 【異動後】

```python
def _render_header_en(
    title: str,
    doc_type: str,
    authors_list: list,
    date: str,
    venue: str,
    doi: str,
    keywords: list,
    candidate_extras: dict,
    domain: str,
    abstract: str = '',
) -> str:
    """產出 final_*_en.md 的 header（# title + meta HTML block + abstract）。缺項靜默省略。"""
    lines = [f"# {title}", ""]

    if doc_type == 'resume':
        org = candidate_extras.get('organization', '')
        if org:
            lines.append(f"> **Organization**: {org}")
        if domain:
            lines.append(f"> **Domain**: {domain}")
        if lines and lines[-1] != "":
            lines.append("")
        return "\n".join(lines)

    # 重塑學術經典扉頁：階梯式 HTML 排版（方案 A 不含 affiliation）
    html_bits = []
    if authors_list:
        html_bits.append(f'  <div class="header-authors">{", ".join(str(a) for a in authors_list)}</div>')
    
    venue_date_bits = []
    if venue:
        venue_date_bits.append(venue)
    if date:
        venue_date_bits.append(date)
    if venue_date_bits:
        html_bits.append(f'  <div class="header-venue-date">{" · ".join(venue_date_bits)}</div>')
        
    if doi:
        html_bits.append(f'  <div class="header-doi">DOI: {doi}</div>')
    if keywords:
        html_bits.append(f'  <div class="header-keywords">Keywords: {", ".join(keywords)}</div>')

    if html_bits:
        lines.append('<div class="paper-header-meta">')
        lines.extend(html_bits)
        lines.append('</div>')
        lines.append("")

    if abstract:
        lines.append("## Abstract")
        lines.append("")
        lines.append(abstract)
        lines.append("")
    return "\n".join(lines)


def _render_header_zh(
    title_zh: str,
    doc_type: str,
    authors_list: list,
    date: str,
    venue: str,
    doi: str,
    keywords: list,
    candidate_extras: dict,
    domain: str,
    abstract: str = '',
) -> str:
    """產出 final_*_zh.md 的 header（中文標籤）。缺項靜默省略。"""
    lines = [f"# {title_zh}", ""]

    if doc_type == 'resume':
        org = candidate_extras.get('organization', '')
        if org:
            lines.append(f"> **機構**：{org}")
        if domain:
            lines.append(f"> **領域**：{domain}")
        if lines and lines[-1] != "":
            lines.append("")
        return "\n".join(lines)

    # 重塑學術經典扉頁：階梯式 HTML 排版（方案 A 不含 affiliation）
    html_bits = []
    if authors_list:
        html_bits.append(f'  <div class="header-authors">{"、".join(str(a) for a in authors_list)}</div>')
        
    venue_date_bits = []
    if venue:
        venue_date_bits.append(venue)
    if date:
        venue_date_bits.append(date)
    if venue_date_bits:
        html_bits.append(f'  <div class="header-venue-date">{" · ".join(venue_date_bits)}</div>')
        
    if doi:
        html_bits.append(f'  <div class="header-doi">DOI: {doi}</div>')
    if keywords:
        html_bits.append(f'  <div class="header-keywords">關鍵字：{"、".join(keywords)}</div>')

    if html_bits:
        lines.append('<div class="paper-header-meta">')
        lines.extend(html_bits)
        lines.append('</div>')
        lines.append("")

    if abstract:
        lines.append("## 摘要")
        lines.append("")
        lines.append(abstract)
        lines.append("")
    return "\n".join(lines)
```

#### 【呼叫端異動說明】 (L879-L888)

*(方案 A：呼叫端完全無需異動，維持原樣即可。不需提取 affiliation_val 或傳入，降低 Regression 風險。)*

---

### §8.5 `tests/test_bug_b2_paper_header_meta.py` - 測試 assertions 重構

#### 【異動前】 (L31-L77, L149-L178)

```python
def test_render_header_en_academic_uses_dash_list_and_wrap():
    """B10 後端：英文 academic path 用 `- **Authors**`（不再 `> **Authors**`）+ 包進 paper-header-meta wrap。"""
    md = _render_header_en(
        title="Some Paper",
        doc_type="academic",
        authors_list=["Alice", "Bob"],
        date="2024-01",
        venue="ICML",
        doi="10.1234/xyz",
        keywords=["k1", "k2"],
        candidate_extras={},
        domain="ml",
    )
    # 不應再有 `> **Authors**` blockquote
    assert "> **Authors**" not in md, '英文 academic 不應再用 > blockquote'
    # 應有 `- **Authors**` list（5 條 meta_bits 全部）
    for label in ("Authors", "Date", "Venue", "DOI", "Keywords"):
        assert f"- **{label}**" in md, f'應有 `- **{label}**` list item'
    # wrap div 含 5 meta_bits
    assert '<div class="paper-header-meta">' in md
    assert '</div>' in md
    # wrap 順序：div open → bits → div close
    open_idx = md.find('<div class="paper-header-meta">')
    close_idx = md.find('</div>')
    authors_idx = md.find('- **Authors**')
    assert open_idx < authors_idx < close_idx, 'wrap 順序：<div> → meta-bits → </div>'


def test_render_header_zh_academic_uses_dash_list_and_wrap():
    """B10 後端：中文 academic path 用 `- **作者**`（不再 `> **作者**`）+ 包進 paper-header-meta wrap。"""
    md = _render_header_zh(
        title_zh="某論文",
        doc_type="academic",
        authors_list=["甲", "乙"],
        date="2024-01",
        venue="某會議",
        doi="10.1234/xyz",
        keywords=["關鍵字1", "關鍵字2"],
        candidate_extras={},
        domain="機器學習",
    )
    assert "> **作者**" not in md, '中文 academic 不應再用 > blockquote'
    for label in ("作者", "日期", "出處", "DOI", "關鍵字"):
        assert f"- **{label}**" in md, f'應有 `- **{label}**` list item'
    assert '<div class="paper-header-meta">' in md
    assert '</div>' in md
...
def test_b10_frontend_media_screen_hides_h1_and_header_meta():
    """B10 前端：@media screen 區塊 hide #paper-content > h1:first-child 與 > .paper-header-meta、
    @media print 模式不受此規則影響。"""
    # @media screen { #paper-content > h1:first-child, #paper-content > .paper-header-meta { display: none; } }
    pat = re.compile(
        r'@media\s+screen\s*\{[^}]*'
        r'#paper-content\s*>\s*h1:first-child\s*,\s*'
        r'#paper-content\s*>\s*\.paper-header-meta\s*\{[^}]*display:\s*none',
        re.DOTALL,
    )
    assert pat.search(STATIC_HTML), (
        '前端 CSS 應有 @media screen { #paper-content > h1:first-child, '
        '#paper-content > .paper-header-meta { display: none; } } 結構'
    )


def test_b10_frontend_class_hook_not_in_print_media():
    """B10 前端：hide 規則必須包在 @media screen、不能裸寫（否則列印也會 hide、破壞列印模式恢復標題契約）。"""
    # 找所有 #paper-content > .paper-header-meta { display: none } 出現的位置
    occurrences = [m.start() for m in re.finditer(
        r'#paper-content\s*>\s*\.paper-header-meta', STATIC_HTML)]
    assert occurrences, '應有 .paper-header-meta selector'

    # 第一個 occurrence 之前 200 字必須含 @media screen（保證在 media query 內）
    first = occurrences[0]
    context_before = STATIC_HTML[max(0, first - 200):first]
    assert '@media screen' in context_before, (
        'hide 規則必須包在 @media screen 內、避免影響 @media print 列印模式'
    )
```

#### 【異動後】

```python
def test_render_header_en_academic_uses_dash_list_and_wrap():
    """B10 後端：英文 academic path 改用置中對稱階梯式 HTML 排版 + 包進 paper-header-meta wrap。"""
    md = _render_header_en(
        title="Some Paper",
        doc_type="academic",
        authors_list=["Alice", "Bob"],
        date="2024-01",
        venue="ICML",
        doi="10.1234/xyz",
        keywords=["k1", "k2"],
        candidate_extras={},
        domain="ml",
    )
    # 不應再有 `> **Authors**` 或是 `- **Authors**` markdown
    assert "> **Authors**" not in md, '英文 academic 不應再用 > blockquote'
    assert "- **Authors**" not in md, '英文 academic 不應再用 - list'
    # wrap div
    assert '<div class="paper-header-meta">' in md
    assert '</div>' in md
    # 應含對應 HTML 排版標記（不含 affiliation）
    assert '<div class="header-authors">Alice, Bob</div>' in md
    assert '<div class="header-venue-date">ICML · 2024-01</div>' in md
    assert '<div class="header-doi">DOI: 10.1234/xyz</div>' in md
    assert '<div class="header-keywords">Keywords: k1, k2</div>' in md


def test_render_header_zh_academic_uses_dash_list_and_wrap():
    """B10 後端：中文 academic path 改用置中對稱階梯式 HTML 排版 + 包進 paper-header-meta wrap。"""
    md = _render_header_zh(
        title_zh="某論文",
        doc_type="academic",
        authors_list=["甲", "乙"],
        date="2024-01",
        venue="某會議",
        doi="10.1234/xyz",
        keywords=["關鍵字1", "關鍵字2"],
        candidate_extras={},
        domain="機器學習",
    )
    assert "> **作者**" not in md, '中文 academic 不應再用 > blockquote'
    assert "- **作者**" not in md, '中文 academic 不應再用 - list'
    assert '<div class="paper-header-meta">' in md
    assert '</div>' in md
    assert '<div class="header-authors">甲、乙</div>' in md
    assert '<div class="header-venue-date">某會議 · 2024-01</div>' in md
    assert '<div class="header-doi">DOI: 10.1234/xyz</div>' in md
    assert '<div class="header-keywords">關鍵字：關鍵字1、關鍵字2</div>' in md
...
def test_b10_frontend_media_screen_hides_h1_and_header_meta():
    """B10 前端已解鎖，@media screen 不應再隱藏 #paper-content 的扉頁，此處驗證前端已移除該 display: none 隱藏規則。"""
    pat = re.compile(
        r'@media\s+screen\s*\{[^}]*'
        r'#paper-content\s*>\s*h1:first-child\s*,\s*'
        r'#paper-content\s*>\s*\.paper-header-meta\s*\{[^}]*display:\s*none',
        re.DOTALL,
    )
    assert not pat.search(STATIC_HTML), (
        '前端 CSS 不應再有螢幕模式隱藏 h1 與 paper-header-meta 規則'
    )


def test_b10_frontend_class_hook_not_in_print_media():
    """B10 前端：.paper-header-meta 置中對稱佈局定義存在。使用 regex 斷言 display: flex（問題 3 強化修正）。"""
    assert '.paper-header-meta' in STATIC_HTML
    pat = re.compile(r'\.paper-header-meta\s*\{[^}]*display:\s*flex', re.DOTALL)
    assert pat.search(STATIC_HTML), '.paper-header-meta 應使用 display: flex 居中佈局'
```

---

## §8.6 `tests/test_bug_f5_p2_inconsistencies.py` - 測試 assertions 重構

#### 【異動前】 (L70-L94)

```python
    # title-meta: --font-xs
    pat_title_meta = re.compile(
        r'#current-title\s+\.title-meta\s*\{[^}]*font-size:\s*var\(--font-xs\)',
        re.DOTALL,
    )
    assert pat_title_meta.search(STATIC_HTML), '#current-title .title-meta 應 font-size: var(--font-xs)'

    # details.title-abstract: --font-base（no fallback）
    pat_abstract = re.compile(
        r'#current-title\s+details\.title-abstract\s*\{[^}]*font-size:\s*var\(--font-base\)\s*;',
        re.DOTALL,
    )
    assert pat_abstract.search(STATIC_HTML), (
        '#current-title details.title-abstract 應 font-size: var(--font-base);（無 fallback）'
    )

    # details.title-abstract > summary: --font-xs
    pat_summary = re.compile(
        r'#current-title\s+details\.title-abstract\s*>\s*summary\s*\{[^}]*font-size:\s*var\(--font-xs\)',
        re.DOTALL,
    )
    assert pat_summary.search(STATIC_HTML), (
        '#current-title details.title-abstract > summary 應 font-size: var(--font-xs)'
    )
```

#### 【異動後】

```python
    # title-meta 已被完全廢除與移除
    assert '#current-title .title-meta' not in STATIC_HTML, '#current-title .title-meta 應已被完全廢除與移除'

    # details.title-abstract: --font-base（no fallback、已移至 #abstract-toolbar）
    pat_abstract = re.compile(
        r'#abstract-toolbar\s+details\.title-abstract\s*\{[^}]*font-size:\s*var\(--font-base\)\s*;',
        re.DOTALL,
    )
    assert pat_abstract.search(STATIC_HTML), (
        '#abstract-toolbar details.title-abstract 應 font-size: var(--font-base);（無 fallback）'
    )

    # details.title-abstract > summary: --font-xs（已移至 #abstract-toolbar）
    pat_summary = re.compile(
        r'#abstract-toolbar\s+details\.title-abstract\s*>\s*summary\s*\{[^}]*font-size:\s*var\(--font-xs\)',
        re.DOTALL,
    )
    assert pat_summary.search(STATIC_HTML), (
        '#abstract-toolbar details.title-abstract > summary 應 font-size: var(--font-xs)'
    )
```

---

## §8.7 `tests/test_md_restore_processor.py` - 測試 assertions 重構

#### 【異動前】 (L392-L418)

```python
def test_render_header_en_academic_full():
    h = _render_header_en(
        title='AlphaFold-2', doc_type='academic',
        authors_list=['Alice', 'Bob'], date='2024-05-20',
        venue='Nature', doi='10.1038/x', keywords=['AI'],
        candidate_extras={}, domain='Protein folding',
    )
    assert h.startswith('# AlphaFold-2')
    assert 'Authors' in h and 'Alice, Bob' in h
    assert 'Date' in h and '2024-05-20' in h
    assert 'Venue' in h and 'Nature' in h


def test_render_header_zh_academic_full():
    h = _render_header_zh(
        title_zh='阿爾法摺疊-2', doc_type='academic',
        authors_list=['Alice', 'Bob'], date='2024-05-20',
        venue='Nature', doi='', keywords=['人工智慧'],
        candidate_extras={}, domain='',
    )
    assert h.startswith('# 阿爾法摺疊-2')
    assert '作者' in h and 'Alice、Bob' in h
    assert '日期' in h and '2024-05-20' in h
    assert '出處' in h and 'Nature' in h
    assert 'DOI' not in h  # 缺項省略
    assert '關鍵字' in h and '人工智慧' in h
```

#### 【異動後】

```python
def test_render_header_en_academic_full():
    h = _render_header_en(
        title='AlphaFold-2', doc_type='academic',
        authors_list=['Alice', 'Bob'], date='2024-05-20',
        venue='Nature', doi='10.1038/x', keywords=['AI'],
        candidate_extras={}, domain='Protein folding',
    )
    assert h.startswith('# AlphaFold-2')
    assert '<div class="paper-header-meta">' in h
    assert '<div class="header-authors">Alice, Bob</div>' in h
    assert '<div class="header-venue-date">Nature · 2024-05-20</div>' in h
    assert '<div class="header-doi">DOI: 10.1038/x</div>' in h
    assert '<div class="header-keywords">Keywords: AI</div>' in h


def test_render_header_zh_academic_full():
    h = _render_header_zh(
        title_zh='阿爾法摺疊-2', doc_type='academic',
        authors_list=['Alice', 'Bob'], date='2024-05-20',
        venue='Nature', doi='', keywords=['人工智慧'],
        candidate_extras={}, domain='',
    )
    assert h.startswith('# 阿爾法摺疊-2')
    assert '<div class="paper-header-meta">' in h
    assert '<div class="header-authors">Alice、Bob</div>' in h
    assert '<div class="header-venue-date">Nature · 2024-05-20</div>' in h
    assert 'DOI' not in h  # 缺項省略
    assert '<div class="header-keywords">關鍵字：人工智慧</div>' in h
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度             | 內容                                                         |
| ---------------- | ------------------------------------------------------------ |
| **目的**         | 定義 FE-AESTHETICS 摘要工具列重構與正文扉頁美化的目標技術規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途**         | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源**       | 本檔 §1–§7                                                   |
| **引用方**       | 後續 FE-AESTHETICS tasks / 執行報告                          |
| **被引用方**     | <由 Antigravity 自動掃描注入>                                |
| **約束事項**     | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動                                       |
| **改版規則**     | 直接修改對應章節 + §99.2 加 Revision 紀錄                    |
| **刪除條件**     | 任務全部完成，經 baron 同意且歸檔至 archive/                 |
| **重複防護**     | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-05-29)：初版建立，針對摘要工具列重構、元數據清理、防溢出折行與扉頁重塑進行全套規劃。
- v1.1 (2026-05-29)：配合 baron 反饋進行第一輪修正。
- v1.2 (2026-05-29)：配合 baron 反饋進行第二輪修正，解決殘骸與一致性問題：
  1. 徹底移除舊版 L683-801 與中途的 Python 矛盾定義殘骸 (方案 A 徹底化)。
  2. 補上因被截斷而損壞的前端 `renderTitleHeader` JS 【異動後】完整實現。
  3. 刪除 CSS 【異動後】中的死代碼 `.header-affiliation` 規則，達成與方案 A 在代碼層級 of 100% 一致。
  4. 修改 TL;DR 與 E2E 驗收中殘留的 "Affiliation / 機構單位" 描述，保證文檔邏輯自洽。
- v1.3 (2026-05-29)：配合 baron 的新發現，將 `#abstract-toolbar` 納入 `@media print` 的 `display: none !important` 隱藏清單（採用優雅的 Option 2），確保列印樣式完美一致。