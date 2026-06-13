# FE-RHYTHM-1 — 閱讀視圖「清單前寬後窄」垂直節奏治本（base CSS · :has() 交界修正）

> 工作流：**FE-Hotfix**（純 `static/index.html` base CSS、零 `.py`、零後端、零 themes）
> 依據：`templates/template_hotfix.md` / `ref/WORKFLOW_SOP.md §1.4` / `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1.2`
> 代號：`FE-RHYTHM-1`（**非 slide 專屬**——全文體閱讀視圖共用 base CSS 之垂直節奏治本；由 PIPE-SLIDES QA 暴露、治本歸此）
> 涵蓋：**#1 清單前寬後窄**（段落標籤↔清單反轉節奏）+ **#2 投影片「結尾條列→下頁圖」黏字**——
> 同一條 `ul:has(+ p)` 規則一併解（slide 末清單後接的下張圖即 `<p><img>`、得 `margin-bottom` 留白）；
> 採 baron 拍板 **(a) 不額外加 CSS**：靠既有兩條 `:has()` 涵蓋主要情境，**純圖頁→下頁圖之邊角**（前一張結尾為 `.slide-head`、間距偏小但非黏）**暫留**、E2E 真礙眼再議。

---

## 1. 基準與完成狀態

- 基準 Commit：`HOTFIX-3d`（slide 渲染層清洗）後。
- 完成狀態：**未 commit**（baton 暫存、待 baron 過目 → Run）。
- 改檔範圍：`static/index.html` base CSS（新增兩條 `:has()` 規則）。
- 不動：`static/themes/*.css` / 後端 / pipeline / RAG / final_zh 產物 / chat（`.msg-ai`）。

---

## 2. 真因（Root Cause）

### 2.1 症狀
baron 前端 QA `Ch37_Plant-Nutrition`（B 軌）施肥頁，發現「標題+清單」節奏**反轉**：
- **標籤段落 → 其下清單：間距過寬**（紅框1）
- **清單末項 → 下一個標籤段落：間距過窄**（紅框2）

不符排版邏輯（該緊的反鬆、該鬆的反緊）；且 baron 指出此問題**反覆出現、之前擱置未修**。

### 2.2 B 軌 markdown 實況（`Ch37_Plant-Nutrition_shadow` final_zh、repr 實測）
```
322 '施肥 (Fertilization)：補充營養素與管理流失'   ← 純段落標籤（緊接清單、無空行）
323 '* 收成 (Harvest) 會帶走土壤中的營養素'         ← 清單緊貼
324 '* 肥料 (Fertilizers) 可補充 N、P、K…'
325 ''                                            ← 空行
326 '權衡關係 (Trade-offs)：'                        ← 純段落標籤
327 '* 太少 → 生長受限'
…
```
標籤皆**純段落行**、緊接 `*` 清單。marked：清單中斷段落 → `<p>標籤</p><ul>…</ul>`。

### 2.3 根因（兩層、與 doc-type 無關）
**第一層（真正的根·base CSS 垂直節奏）**：
1. `static/index.html:79` 全域 reset `body, h1, h2, h3, p, ol, ul { margin: 0; padding: 0; }` → **歸零 `<ul>`/`<ol>` 瀏覽器預設上下 margin**。
2. 主題只給段落**單向下邊距**（`#paper-content p { margin-bottom: var(--space-4) }`、**無 margin-top**）；四主題對 `#paper-content ul/ol` **margin 0 命中**（不補）。

→ 整份垂直間距**只靠「段落 margin-bottom 往下推」**、無「margin-top 往上頂」。故 **`<ul>` 成單向黑洞**：前面有間距（吃前一 `<p>` 的 margin-bottom）、**後面無間距**（自身 margin=0 + 下一 `<p>` 無 margin-top）。

**第二層（觸發條件）**：Vision 把區段標籤吐成**純段落**緊接清單、且**交替重複**（標籤→清單→標籤→清單）→ 第一層的單向特性顯現為「標籤→清單寬、清單→標籤窄」系統性反轉。

> 對照：若標籤是 `<h3>`（雙向 margin `space-5 0 space-2`）→ 自然「上留白、下緊貼清單」= 正確；HOTFIX-3 把 `**X**` 升 `###` 即此理。本問題是該升未升的「`X：` 純段落標籤」+ 清單黑洞共同造成。

### 2.4 範圍與方案抉擇
- `#paper-content` 為**全文體閱讀視圖共用**（履歷/論文/書籍/litedoc/簡報）；**chat 走 `.msg-ai`、不受影響**；slide 正文無 wrapper class → **無 slide-only CSS scope**。
- 任一 base CSS 修皆全域作用於閱讀視圖；故**治本**（一次解全文體「清單前寬後窄」通病）優於 slide-only（需 wrapper + golden 重捕）。
- baron 拍板 **A（`:has()` 全域、最小 delta、須驗三軌）**；否決 B（slide-only wrapper、成本高）。

---

## 3. 修法（程式碼）

於 `static/index.html` base CSS（`#paper-content` 區、HOTFIX-3 清單 padding 規則附近）新增**兩條 `:has()` 規則**，**只打「段落↔清單」交界**：

```css
  /* === [FE-RHYTHM-1 START] === 閱讀視圖清單垂直節奏治本（全文體共用 base）
     根因：base 只用 margin-bottom 做節奏 + L79 reset 歸零清單 margin →
     清單「前寬（吃前段 mb）後窄（自身 0、後段無 mt）」。
     僅修「段落↔清單」交界、不碰巢狀清單與「清單接標題」（最小波及）：*/
  #paper-content p:has(+ ul),
  #paper-content p:has(+ ol) {
    margin-bottom: var(--space-1);   /* 標籤段落貼緊其下清單（收窄過寬） */
  }
  #paper-content ul:has(+ p),
  #paper-content ol:has(+ p) {
    margin-bottom: var(--space-4);   /* 清單與後續段落/標籤間補留白（補足過窄） */
  }
  /* === [FE-RHYTHM-1 END] === */
```

### 3.1 為何是「外科級」（最小波及）
- `p:has(+ ul/ol)`：只命中**緊接清單的段落**（即區段標籤）→ 收其 margin-bottom；一般段落（後面非清單）不動。
- `ul/ol:has(+ p)`：只命中**緊接段落的清單**（清單→下個標籤/段落/圖）→ 補 margin-bottom；
  - **巢狀清單不中**（其後接 `<li>` 非 `<p>`）；
  - **清單接標題不中**（`<h2/h3>` 非 `<p>`、標題本有上向 margin、自然留白）。
- 結果：標籤→清單 `space-1`（貼緊）、清單→下個標籤 `space-4`（留白）= 正確節奏。
- **同時解 #2（投影片黏字）**：slide 末清單緊接下一張投影片圖（`![](…)` 渲為 `<p><img></p>`、其右上角即烤進圖的母片日期）時，`ul:has(+ p)` 命中（`+ p` ＝該圖段落）→ 補 `space-4` → 前頁結尾條列與下頁圖（含日期）之間有留白、**不再黏**。
  - 涵蓋範圍（(a) 方案）：前一張**結尾為條列**（最常見、baron 報的主要情境）→ 已解；前一張**結尾為段落** → 段落本有 `margin-bottom: space-4`、本就有間距。
  - **暫留邊角**：純圖頁（無內文、結構 `[圖][.slide-head]`）→ 下一張圖，前者結尾為 `.slide-head`（`mb space-3`、間距偏小但非黏）；不額外加 CSS（(a)），E2E 真礙眼再補 `img { margin-top }`（(b)）。

### 3.2 相容性
- `:has()`：Safari 15.4+（2022）/ Chromium 105+（含 Dia）/ Firefox 121+ 皆支援；baron 環境（Dia/Safari）OK。舊瀏覽器：`:has()` 規則整條被忽略（不報錯）→ 降級為現況節奏（不致破版、僅回到修前）。

---

## 4. 不可動清單

- [ ] `static/themes/*.css`（四主題 + 自訂上傳主題）—— 縮排/節奏歸 base、不動 themes
- [ ] `static/index.html:79` 全域 reset、既有 `#paper-content p`（主題）/ HOTFIX-3/3b 清單 padding 規則 —— 不改（僅**新增** :has 規則）
- [ ] 後端 / pipeline / RAG / final_zh 產物 —— 零碰（純 CSS）
- [ ] chat `.msg-ai` —— 不在選擇器範圍、不受影響
- [ ] 主 repo 目錄 —— 嚴禁讀寫

---

## 5. 端到端驗證計畫

### 5.1 靜態 grep
```bash
grep -n "FE-RHYTHM-1" static/index.html                      # START/END = 2 命中
grep -n "p:has(+ ul)\|ul:has(+ p)" static/index.html         # 兩條規則命中
for f in static/themes/*.css; do grep -c "paper-content ul\|paper-content ol\|:has" "$f"; done  # 皆 0（未動 themes）
```

### 5.2 pytest
- 純 base CSS、零 `.py` diff → 不新增 pytest；全套件維持綠（`venv/bin/python -m pytest tests/ -q`、與基線一致、僅既存 env flake）。

### 5.3 ⚠️ baron E2E（三軌必驗、非 commit）
> CSS 視覺、無法 headless 驗；本修全文體共用故**三軌都要看**：
1. **簡報（Ch37）**：施肥頁「標籤→清單貼緊、清單→下個標籤留白」、節奏一致；氮素頁、土壤頁等亦正常。**#2 黏字**：前一張結尾條列 → 下一張投影片圖之間有留白、不黏其右上日期；純圖頁→下頁圖之邊角間距是否可接受（暫留、礙眼再議 (b)）。
2. **履歷**：技能/經歷區「小標 + 條列」節奏正常、無過鬆/過擠；巢狀條列未被過度撐開。
3. **論文（2601 / byz）**：段落↔清單交界正常；**巢狀清單未被 `ul:has(+p)` 誤撐**（驗證外科級假設）；清單接章節標題留白正常。
4. **chat**：AI 回答清單**不受影響**（確認 `.msg-ai` 未被波及）。
5. 四主題（kahn/mies/kandinsky/nara）逐一掃一遍（`var(--space-*)` 各主題值不同、確認皆合理）。

### 5.4 Golden
- **不涉**：純 CSS、final_zh byte 不變、RAG 不動 → **無需 golden 重捕**。

---

## 6. 回退方式（Rollback）

移除 `/* === [FE-RHYTHM-1 START/END] === */` 包裹的兩條 `:has()` 規則，或 `git revert <FE-RHYTHM-1 hash>`。純 CSS、無資料/向量/schema 影響、回退即還原修前節奏。

---

## 7. Commit

**git add 清單**：
```
static/index.html
.claude-logs/archive/2026-06-13_FE-RHYTHM-1_index.html.bak
.claude-logs/baton/2026-06-13_FE-RHYTHM-1_hotfix.md     # 收官移出後 add
.claude-logs/executions/2026-06-13_FE-RHYTHM-1_執行.md  # 收官移出後 add
.claude-logs/prompts/2026-06-13_FE-RHYTHM-1_doc_提示詞.md
.claude-logs/prompts/2026-06-13_FE-RHYTHM-1_run_提示詞.md
.claude-logs/TODO.md
.claude-logs/prompts/INDEX.md
```

**commit message 草稿**（`/tmp/FE-RHYTHM-1_msg.txt`）：
```
FE-Hotfix: FE-RHYTHM-1 — 閱讀視圖「清單前寬後窄」垂直節奏治本（:has() 交界修正）

真因（全文體 base CSS 通病、非 slide 專屬）：static/index.html:79 全域 reset 歸零 ul/ol margin、
主題只給 #paper-content p 單向 margin-bottom（無 margin-top）→ 整份垂直節奏只靠段落往下推、
清單成「前有間距（吃前段 mb）後無間距（自身 0、後段無 mt）」單向黑洞；Vision 把區段標籤吐成
純段落緊接清單且交替重複 → 顯現「標籤→清單寬、清單→下個標籤窄」反轉（Ch37 施肥頁）。

修法：static/index.html base CSS 新增兩條 :has()，僅打「段落↔清單」交界——
p:has(+ ul/ol){margin-bottom:space-1}（標籤貼緊其清單）+ ul/ol:has(+ p){margin-bottom:space-4}
（清單後補留白）。巢狀清單（後接 li 非 p）與「清單接標題」（後接 h 非 p）不中、波及最小。
全文體共用閱讀視圖一次治本；chat（.msg-ai）不受影響；不動 themes。

同時解 #2（投影片「結尾條列→下頁圖」黏字）：slide 末清單後接的下張圖渲為 <p><img>、
ul:has(+ p) 命中補 space-4 → 前頁條列與下頁圖（含烤進右上角的母片日期）間留白、不黏；
採 (a) 不額外加 CSS，純圖頁→下頁圖邊角（前者結尾為 .slide-head、間距小但非黏）暫留。

範圍：static/index.html 單檔 base CSS、零 .py、零後端、零 final_zh、無 golden 重捕。
:has() 相容 Safari 15.4+/Chromium 105+（Dia OK）、舊瀏覽器整條忽略降級為現況。
驗證：grep 兩規則命中 + themes 0；全套件零 Python diff 維持綠；
⚠️ baron 三軌 E2E（簡報 Ch37 施肥頁 / 履歷 / 論文 2601-byz〔尤巢狀清單未誤撐〕+ 四主題 + chat 不受影響）。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
