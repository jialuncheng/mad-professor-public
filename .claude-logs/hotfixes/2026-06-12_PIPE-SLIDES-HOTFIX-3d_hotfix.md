# PIPE-SLIDES-HOTFIX-3d — 字面 `**` 未渲染粗體 + 裸 URL 破版（slide 渲染層清洗）

> 工作流：**BE-Hotfix**（動 `pipelines/slide_pipeline.py` 渲染層、零後端 API/DB）
> 依據：`templates/template_hotfix.md` / `ref/WORKFLOW_SOP.md §1.5 + §5` / `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.3/§4.4`
> 必讀 SOP：`sop/2026-05-23_logging_SOP_手冊.md` + `sop/2026-05-23_database_SOP_手冊.md`（本修零 logging/db 變更，§5 核查見 §7.5）
> 代號：延續 `PIPE-SLIDES-HOTFIX-3` 家族（3/3b CSS、3c 節奏正規化、**3d 行內標記清洗**）

---

## 1. 基準與完成狀態

- 基準 Commit：`HOTFIX-3c`（簡報重點群節奏正規化；若 3c 尚未落地，本修可獨立落地、與 3c 互不依賴、僅共用同一渲染鏈）
- 完成狀態：**未 commit**（baton 暫存、待 baron 過目 → Run）
- 改檔範圍：`pipelines/slide_pipeline.py` 單檔（新增 2 私有 helper + 2 渲染注入點）
- 不動：後端 API / DB / RAG 載入端 / `ctx.rag_sections` 建構 / `static/*` / 其餘四路 pipeline

---

## 2. 真因（Root Cause）

### 2.1 症狀（B 軌 reading view + 原稿比對）
掃 `植物營養 (Plant Nutrition) (測試).pdf` 並與原稿 `Ch37_Plant-Nutrition.pdf` 比對，兩類渲染破版（**原稿無、B 軌引入**）：

**A. 字面 `**` 未渲染成粗體**（p27 根圈）：
```
**根際細菌 (rhizobacteria)生活在緊鄰植物根部之處…即根際 (rhizosphere)**中。
植物從這些**互利共生關係 (mutualistic associations)**中獲得…
部分根際細菌是**自由生活 (free-living)**，而其他則是內生菌 (endophytes)**。
```
`**` 直接顯示為星號、未轉 `<strong>`。

**B. 裸 URL 破版**（p6 / p18 / p27 / p35）：投影片來源/縮圖網址被 Vision 轉錄成**整行裸連結**，渲染成超長 `<a>` 撐破版面：
```
p6 : https://i.ytimg.com/vi/6rqqt9LM3AQ/hq720.jpg?sap=…
p18: https://fieldreport.caes.uga.edu/publications/C1040/…
p27: https://www.biorender.com/template/components-of-the-rhizosphere
p35: https://plantrevolution.com/…?srsltid=AfmBOooTo5FlEl8kkB4mzgk9wH…（超長 query string）
```

### 2.2 機制

**A. CommonMark CJK 緊貼 `**` emphasis 判定失效**：
CommonMark 的「右側界定符（right-flanking）」規則——閉合 `**` 若**前接標點**（此處 `）` 全形括號），則僅在**後接空白或標點**時才算合法閉合。但這些 span 後面緊接**中文字**（`中`／`，`半形等非空白非標點 letter）→ `**` 不被視為合法 closer → 保持字面星號。
原稿為**英文**（`**bold** ` 後接空白、閉合合法）故無症；**翻成中文後 CJK 緊貼 `**`** 才觸發 → B 軌翻譯引入。

**B. 裸 URL 自動連結 + 溢出**：
bare `https://…` 在 marked（`gfm:true`）下自動連結成 `<a>`；超長 query string 無斷點 → 撐破 `#paper-content`。原稿是嵌入連結/細小出處、B 軌攤成可見裸連結。

### 2.3 解法
**slide 渲染層清洗**（與 3c 同層、純渲染 body）：
- **A**：行內 `**X**` → `<strong>X</strong>`（raw HTML）。marked 9.x 不 sanitize、原樣輸出 `<strong>`（同 `.slide-head` 既有 raw HTML 先例），**繞過 CommonMark CJK emphasis 解析**、不論前後字元一律正確粗體。
- **B**：剝除「**整行僅一個 URL**」之行（純出處/縮圖噪聲、破版主因）；**行內 URL**（同行有其他文字）**保留**、`![alt](images/…)` 圖片行**保留**（不以 `http` 開頭、天然不匹配）。

### 2.4 RAG 零影響（碼層自證）
兩 helper 只套在**渲染路 `body`**；`pipelines/slide_pipeline.py:865` `merged = "\n\n".join(... zh_content ...)`（rag_sections content）取**原始 `zh_content`**、不套任何渲染 helper → `<strong>`/URL 剝除**只在顯示層**、`rag_sections` byte 不變 → **RAG 召回零影響**（slides RAG 走 `ctx.rag_sections` 旁路）。

---

## 3. 修法（程式碼）

### 3.1 新增兩私有 helper（slide_pipeline.py、`_promote_subheadings` 之後）

```python
    # === [PIPE-SLIDES-HOTFIX-3d HOTFIX-3d START] ===
    @staticmethod
    def _render_inline_bold(text: str) -> str:
        """行內 **X** → <strong>X</strong>（raw HTML、繞過 CommonMark CJK emphasis 失效）。

        真因：閉合 `**` 前接全形標點、後接中文字（非空白非標點）→ CommonMark 不認 closer →
        字面星號。轉 raw <strong> 後 marked 原樣輸出、不論 CJK 緊貼皆正確粗體。
        於 _promote_subheadings 之後跑（整行 **X** 已升 ### → 此處只剩行內 span）；非貪婪成對匹配、
        落單 `**` 保留原樣。只動渲染 body、不碰 rag_sections。
        """
        if not text:
            return text
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    @staticmethod
    def _strip_bare_url_lines(text: str) -> str:
        """剝除『整行僅一個 URL』之行（投影片來源/縮圖網址、破版噪聲）。

        僅匹配整行純 URL（前後容空白、容 <...> autolink 括號）；行內 URL（同行有其他文字）
        與 ![alt](images/…) 圖片行（非 http 開頭）一律保留。只動渲染 body、不碰 rag_sections。
        """
        if not text:
            return text
        url_line = re.compile(r"^\s*<?https?://\S+>?\s*\r?$")
        return "\n".join(ln for ln in text.split("\n") if not url_line.match(ln))
    # === [PIPE-SLIDES-HOTFIX-3d HOTFIX-3d END] ===
```

### 3.2 注入點一 `_page_source_md`（en + 退化 fallback 共用）

```python
        if (u.get("content") or "").strip():
            body = SlidePipeline._promote_subheadings(u["content"].strip())
            # === [PIPE-SLIDES-HOTFIX-3d HOTFIX-3d] === 行內粗體轉 <strong> + 剝除整行裸 URL
            body = SlidePipeline._render_inline_bold(body)
            body = SlidePipeline._strip_bare_url_lines(body)
            body = SlidePipeline._normalize_paragraph_breaks(body)
            body = SlidePipeline._tighten_point_groups(body)   # ← HOTFIX-3c（若已落地）
            parts.append(body)
```

### 3.3 注入點二 `_deliver`（zh 正常路）

```python
                if zh_content:
                    body = self._promote_subheadings(zh_content)
                    # === [PIPE-SLIDES-HOTFIX-3d HOTFIX-3d] === 行內粗體轉 <strong> + 剝除整行裸 URL
                    body = self._render_inline_bold(body)
                    body = self._strip_bare_url_lines(body)
                    body = self._normalize_paragraph_breaks(body)
                    body = self._tighten_point_groups(body)    # ← HOTFIX-3c（若已落地）
                    parts.append(body)
```

> **順序**：`_promote_subheadings`（整行 `**X**`→`### X`）→ **`_render_inline_bold`**（剩餘行內 `**X**`→`<strong>`）→ **`_strip_bare_url_lines`**（去整行 URL）→ `_normalize_paragraph_breaks` → `_tighten_point_groups`(3c)。
> 3d 兩 helper 只改「行內容 / 刪整行」、不碰行首標記與 `\n` 結構 → 與 normalize/tighten 不衝突；**若 3c 未落地**，刪掉 `_tighten_point_groups` 那行即可、3d 獨立成立。
> `merged`（L865，rag_sections content）**不套任何渲染 helper** → RAG 零影響。

### 3.4 渲染後預期
- p27：`<strong>根際細菌 (rhizobacteria)…</strong>中。`（正確粗體、無字面 `**`）；底部 biorender 整行 URL **消失**。
- p6/p18/p35：整行來源/縮圖 URL **消失**、版面不再被超長連結撐破。
- 行內 URL（若有「見 https://… 說明」同行情境）與 `![alt](images/page-N.jpg)` 圖片**保留**。

### 3.5 決策註（baron 可否決）
- **B 取「剝除」而非「保留短連結」**：整行裸 URL＝投影片出處/縮圖噪聲、對閱讀視圖無資訊價值且破版；若日後要保留出處，可改為轉 `[來源](url)` 短連結（本修預設剝除、較乾淨）。

---

## 4. 不可動清單遵守狀態

- [x] 不動後端 API（`web_server.py`）/ DB / models
- [x] 不動 `ctx.rag_sections` 建構（`merged` 沿用原始 `zh_content`）→ RAG 召回零影響
- [x] 不動 RAG 載入端（`rag_retriever` / `ai_core` / `rag_indexer`）
- [x] 不動 `static/*`（與 3/3b CSS 正交）
- [x] 不動其餘四路 pipeline 與 A 軌
- [x] 不動 `_promote_subheadings` / `_normalize_paragraph_breaks` / `_tighten_point_groups` / `_slide_head_html` 既有邏輯（僅串接新 helper）
- [x] 保留圖片行 `![alt](images/…)` 與行內 URL

---

## 5. 端到端驗證計畫

### 5.1 靜態 grep
```bash
grep -n "_render_inline_bold\|_strip_bare_url_lines" pipelines/slide_pipeline.py   # 定義 2 + 注入 4 = 6 命中
grep -n "HOTFIX-3d" pipelines/slide_pipeline.py                                    # START/END + 2 注入 = 4 命中
grep -n "merged = " pipelines/slide_pipeline.py                                    # 確認 merged 仍取原始 zh_content（未套 3d）
```

### 5.2 pytest（新增回歸 + 全套件）
新增於 `tests/test_slide_pipeline.py`（≥7）：
- `test_hf3d_inline_bold_to_strong`：`前 **粗體** 後` → `<strong>粗體</strong>`、無字面 `**`。
- `test_hf3d_inline_bold_cjk_adjacent`：`**根際細菌（X）**中` → `<strong>根際細菌（X）</strong>中`（CJK 緊貼失效案根除）。
- `test_hf3d_whole_line_bold_still_heading`：整行 `**X**` 仍由 `_promote_subheadings` 升 `### X`（不被 `<strong>` 攔）。
- `test_hf3d_strip_bare_url_line`：整行 `https://a.com/x?y=z` 被剝除。
- `test_hf3d_inline_url_preserved`：`見 https://a.com 說明`（同行有字）**保留**。
- `test_hf3d_image_line_preserved`：`![alt](images/page-1.jpg)` **保留**。
- `test_hf3d_rag_sections_unaffected`：跑 `_deliver`、斷言 `ctx.rag_sections[i]["content"][0]["content"]`（= merged）**等同原始 `zh_content`**、仍含 `**` 與 URL（RAG 隔離鐵證）。
- `test_hf3d_rhizosphere_end_to_end`：p27 擬真輸入 → `zh_text` 含 `<strong>`、不含字面 `**`、不含 biorender 整行 URL。

全套件：`venv/bin/python -m pytest tests/ -q`（維持綠；已知 `.env LOG_FORMAT=json` env flake 1 例不計）。

### 5.3 baron E2E（前端、非 commit）
- 影子重傳 Ch37 → p27 根圈：粗體詞正確顯示、無字面 `**`；該頁底部無 biorender 裸連結。
- p6/p18/p35：無超長裸 URL、版面不再被撐破。
- 圖片正常、行內連結（若有）保留。
- chat 對該頁提問召回正常（RAG 未受影響佐證）。

### 5.4 ⚠️ Golden
> ⚠️ **更正（PIPE-SLIDES-HOTFIX-6 回溯）**：本文件下方「slides golden 須重捕/首捕」之敘述**作廢**。
> `golden_baseline.py capture slides` 捕的是 **A 軌**（`PipelineCore`/`slides_processor`、shadow=False 正本基準）；
> 本 hotfix 改的是 **B 軌**（`slide_pipeline.py`）→ **A 軌 golden 不受影響、不需重捕**。
> B 軌驗證走**影子重傳 E2E**（+ 未來 PIPE Flip 時 B 軌 diff A 軌 golden、改善豁免 Q8）。

改 B 軌 final_zh 渲染（`<strong>` + 去 URL 行）→ **slides golden 變更**；併入既有「slides golden 待 fixture 補齊後一次首捕」批次（HOTFIX-1/1b/2/3/3b/3c + META-NORM C3/C4 + 本 3d），不另捕。

### 5.5 §5 SOP 一致性核查（BE 強制）
```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/slide_pipeline.py
# 本修新增碼段（2 helper + 注入）零 logging 呼叫 → 無命中（合規）

grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v "with .*session.*begin\(\)"
# 本修零 DB → 無命中（合規）
```
（落地後貼真實輸出；空輸出註「無命中（合規）」。）

---

## 6. 回退方式（Rollback）

移除 `# === [PIPE-SLIDES-HOTFIX-3d ...] ===` 包裹的 2 helper + 各注入點的 2 行呼叫，或 `git revert <HOTFIX-3d hash>`。不涉 DB/向量/schema；rag_sections 未受影響，回退僅還原 final_zh 顯示層。

---

## 7. Commit

**git add 清單**：
```
pipelines/slide_pipeline.py
tests/test_slide_pipeline.py
.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3d_HOTFIX-3d_slide_pipeline.py.bak
.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3d_HOTFIX-3d_test_slide_pipeline.py.bak
.claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md     # 收官階段才 add，Run 階段留 baton
```

**commit message 草稿**（`/tmp/PIPE-SLIDES-HOTFIX-3d_msg.txt`）：
```
BE-Hotfix: PIPE-SLIDES-HOTFIX-3d — 字面 ** 未粗體 + 裸 URL 破版（slide 渲染層清洗）

真因（B 軌 vs 原稿 Ch37 比對、原稿無 B 軌引入）：
A 字面 **：CommonMark 右側界定符規則下，閉合 ** 前接全形標點、後接中文字（非空白非
標點）→ 不認 closer → 字面星號（p27 根圈）。原稿英文 **bold** 後接空白故無症、翻中後
CJK 緊貼 ** 才觸發。
B 裸 URL：投影片來源/縮圖網址被 Vision 轉錄成整行裸連結，gfm 自動連結 + 超長無斷點
→ 撐破 #paper-content（p6/p18/p27/p35）。

修法：pipelines/slide_pipeline.py 新增 _render_inline_bold（行內 **X**→<strong>X</strong>、
raw HTML 繞過 CommonMark CJK emphasis、marked 不 sanitize 原樣輸出）+ _strip_bare_url_lines
（剝除整行純 URL、行內 URL 與 ![](images/…) 圖片行保留）；_page_source_md + _deliver
於 _promote_subheadings 後注入（promote→inline_bold→strip_url→normalize→tighten[3c]）。

RAG 零影響：rag_sections content 取原始 zh_content（merged，L865）、未套 3d；slides RAG
走 ctx.rag_sections 旁路、不從 final_zh 切。零後端/DB/models/static 改動。
SOP 核查：新增碼段零 logging/commit → logging+database 皆無命中（合規）。

驗證：grep helper 6 命中 / HOTFIX-3d 4 命中 / merged 仍取原始 zh_content；新增回歸
（行內粗體/CJK 緊貼/整行 ** 仍升標題/剝整行 URL/行內 URL 保留/圖片行保留/rag_sections
隔離/p27 端到端）+ 全套件維持綠。⚠️ 改 B 軌 final_zh → slides golden 併既有批次一次首捕；
baron E2E 影子重傳 Ch37 驗 p27 粗體正常無裸連結。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
