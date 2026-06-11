# PIPE-SLIDES-HOTFIX-3b — top-level 清單凸排修補（HOTFIX-3 二的補完）

> 工作流：**FE-Hotfix**（純 `static/index.html` base CSS、零 `.py`、零後端）
> 依據：`templates/template_hotfix.md` / `ref/WORKFLOW_SOP.md §1.4` / `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1.2`
> 代號：延續 `PIPE-SLIDES-HOTFIX-3`（同一缺陷類「清單縮排」之 top-level 漏網補完，故取 `-3b`）

---

## 1. 基準與完成狀態

- 基準 Commit：`HOTFIX-3`（slide reading-view 排版美化：圖先行 / 副標併入標題塊 / 子標題→h3 / **二：巢狀清單縮排**）
- 完成狀態：**未 commit**（baton 暫存待 baron 拍板 → Run）
- 改檔範圍：`static/index.html` 單檔、HOTFIX-3 既有 CSS 區塊內**擴充 selector 一組**（top-level `ul/ol`）
- **不動** `static/themes/*.css`（四主題 + 自訂上傳主題皆受益於 base 一處）

---

## 2. 真因（Root Cause）

### 2.1 症狀
ALi 簡報 reading-view，頁內第一層（top-level）`•` 條列**凸排**——bullet marker 跑到比同頁標題更左、落在內容框左外側：

```
  純積體電路公司 (Pure IC Company)        ← 標題（#paper-content padding 左緣）
• 來自中國…                                ← bullet 凸到標題左邊（凸排）
• 來自聯發科…
• 通用型…
• 在 AI 時代…
```

預期：bullet 應與標題左緣對齊或更內縮，不得凸出。

### 2.2 代碼證據（grep 實測、附真實行號）

**① 全域 reset 把 top-level 清單 padding 歸零**（`static/index.html:79`）：
```css
body, h1, h2, h3, p, ol, ul { margin: 0; padding: 0; }
```
`ul/ol` 的 `padding` 被歸零 → 預設 `list-style-position: outside` 下，bullet marker 繪製於 padding 區（現為 0）的**外側** → marker 溢出到 `#paper-content` 的左 padding（`var(--space-8)`，見 kahn.css:126 `#paper-content { padding: var(--space-8); }`）之內、視覺上比標題更左。

**② HOTFIX-3「二」只修了巢狀、漏 top-level**（`static/index.html:898-901`）：
```css
/* 二：巢狀清單縮排（結構性 fallback、主題無關、含自訂主題受益） */
#paper-content ul ul, #paper-content ol ol,
#paper-content ul ol, #paper-content ol ul {
  padding-left: 1.5em;
}
```
selector 只涵蓋 `ul ul / ol ol / ul ol / ol ul`（第二層以下），**第一層 `#paper-content ul` / `#paper-content ol` 未補** → 仍吃 L79 的 `padding: 0` → 第一層 bullet 凸排。

**③ 主題未涉入（grep 0 命中、改 themes 沒地方改）**：
```
static/themes/kahn.css:      #paper-content ul/ol/li → 0
static/themes/kandinsky.css: #paper-content ul/ol/li → 0
static/themes/mies.css:      #paper-content ul/ol/li → 0
static/themes/nara.css:      #paper-content ul/ol/li → 0
```
四主題完全不設清單縮排 → 縮排現由 base 的 L79 reset 單方面決定（歸零）。**主題端無 selector 可改**；自訂上傳主題同理（作者不會知道要補）。

### 2.3 歸屬：為何在 base、不在 themes
- **結構 vs 外觀**（`design/docs/principles.md`）：清單縮排是表達層級的**結構**，歸主檔（index.html）；主題只管色票/字族/分隔線粗細等**外觀**。
- **base 一處全涵蓋**：放 base → 4 內建主題 + 自訂上傳主題自動正確；放 themes → 改 4 檔且自訂主題永遠漏，治不乾淨。
- 與 HOTFIX-3「二（巢狀）」放 base 同一正當性 —— 本 hotfix 只是把同一條規則的 selector 從「只巢狀」擴成「**含 top-level**」，**同一區塊、同一處**。

---

## 3. 修法（程式碼）

`static/index.html` HOTFIX-3 區塊「二」的 selector 前置一行 top-level `ul/ol`，padding 值不變（`1.5em`，與巢狀一致）：

### Before（L897-901）
```css
  /* 二：巢狀清單縮排（結構性 fallback、主題無關、含自訂主題受益） */
  #paper-content ul ul, #paper-content ol ol,
  #paper-content ul ol, #paper-content ol ul {
    padding-left: 1.5em;
  }
```

### After
```css
  /* 二：清單縮排（結構性 fallback、主題無關、含自訂主題受益）
     L79 全域 reset 把 ul/ol padding 歸零 → list-style:outside 下 bullet 凸排；
     此處補回 top-level + 巢狀縮排（HOTFIX-3b：補 top-level、原僅巢狀） */
  #paper-content ul, #paper-content ol,
  #paper-content ul ul, #paper-content ol ol,
  #paper-content ul ol, #paper-content ol ul {
    padding-left: 1.5em;
  }
```

- 變動：selector 增 `#paper-content ul, #paper-content ol,` 一行 + 註解補因由；`padding-left: 1.5em` 值、區塊位置、HOTFIX-3 START/END 包裹**全不動**。
- 包裹標記沿用既有 `/* === [PIPE-SLIDES-HOTFIX-3 HOTFIX-3 START/END] === */`（同缺陷類補完、不另開新標記，避免區塊碎裂）。

---

## 4. 不可動清單遵守狀態

- [x] 不動任何 `.py`（純 base CSS）
- [x] 不動 `static/themes/*.css`（四主題 + 自訂主題受益於 base 一處）
- [x] 不動 HOTFIX-3 其餘規則（slide-head / slide-head h2 / slide-sub 三塊 byte 不變）
- [x] 不動 `padding-left` 值（沿用 `1.5em`）與 START/END 包裹
- [x] 不碰 RAG / pipeline / 後端（純前端渲染層）

---

## 5. 端到端驗證計畫

### 5.1 靜態 grep（落地後跑）
```bash
# top-level selector 已補
grep -n "#paper-content ul, #paper-content ol," static/index.html        # 應 1 命中
# 巢狀規則仍在（未誤刪）
grep -n "#paper-content ul ul, #paper-content ol ol," static/index.html  # 應 1 命中
# 主題仍 0 涉入（未越界）
for f in static/themes/*.css; do grep -c "paper-content ul\|paper-content ol\|paper-content li" "$f"; done  # 皆 0
```

### 5.2 pytest
- **無新增/修改 pytest**：本修為純 CSS 視覺縮排、現有測試套件不對 base CSS list padding 斷言（slide pipeline 測試驗 markdown/HTML 結構、不驗樣式）。
- 回歸網：全套件須維持綠（CSS-only、零 Python diff，理論上不可能影響任何 pytest）。落地後跑 `venv/bin/python -m pytest tests/ -q` 確認 passed 數與 HOTFIX-3 後一致。

### 5.3 baron E2E（前端、非 commit）
- 重整 ALi 簡報 reading-view → 第一層 `•` 與標題左緣對齊/內縮、**不再凸排**。
- 巢狀子項仍正確縮排（HOTFIX-3 二未退化）。
- 切換四主題（kahn/mies/kandinsky/nara）逐一確認清單縮排一致、無主題破版。
- 非 slides 文體（論文/履歷）清單顯示正常（base 規則全域、屬普遍改善、無負面）。

---

## 6. 回退方式（Rollback）

單檔單 hunk，移除新增的 `#paper-content ul, #paper-content ol,` 一行 selector + 還原註解即可；或 `git revert <HOTFIX-3b hash>`。不涉資料/向量/schema，零副作用回退。

---

## 7. Commit

**git add 清單**：
```
static/index.html
.claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3b_hotfix.md   # 收官階段才 add，Run 階段留 baton
```

**commit message 草稿**（`/tmp/msg.txt`）：
```
FE-Hotfix: PIPE-SLIDES-HOTFIX-3b — top-level 清單凸排修補（HOTFIX-3 二補完）

真因：static/index.html:79 全域 reset `ul/ol { padding:0 }` 歸零 top-level 清單
縮排，list-style:outside 下第一層 bullet marker 溢出到 #paper-content 左 padding
（var(--space-8)）外側→凸排（比同頁標題更左）。HOTFIX-3「二」只補了巢狀
（ul ul/ol ol/ul ol/ol ul），漏 top-level `#paper-content ul/ol`。

修法：HOTFIX-3 既有 CSS 區塊「二」selector 前置 `#paper-content ul, #paper-content ol,`
一行、padding-left 沿用 1.5em；含 top-level + 巢狀。不動 themes（四主題 grep 0 命中
清單、縮排=結構歸主檔 principles.md、base 一處含自訂上傳主題受益）。

範圍：static/index.html 單檔單 hunk、零 .py、零後端、零 RAG/pipeline。
驗證：grep top-level/巢狀 selector 各 1 命中、themes 仍 0；全套件零 Python diff 維持綠；
baron E2E ALi 簡報第一層 bullet 不凸排 + 四主題一致 + 巢狀未退化。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
