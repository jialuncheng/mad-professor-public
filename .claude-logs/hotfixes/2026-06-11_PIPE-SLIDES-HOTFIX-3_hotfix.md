# PIPE-SLIDES HOTFIX-3 — 緊急熱修復：簡報閱讀視圖排版打磨（圖序 / 副標併標題塊 / 子標題層級 / 巢狀縮排）

> 工作流類別：**BE-Hotfix**（必讀 logging_SOP + database_SOP；驗收=pytest 全通過 + §5 SOP 核查）
> 依據：baron 前端逐頁檢視 `Ch37_Plant-Nutrition` 簡報，發現 4 項閱讀視圖排版問題；經 **design/docs 設計意圖核對** + 多輪設計決策定案
> 北極星：**閱讀視圖盡量還原投影片的視覺層級**（baron 拍板）
> 受災檔：`pipelines/slide_pipeline.py`（P3 渲染三點）+ `static/index.html`（base CSS 兩點）+ `tests/test_slide_pipeline.py`（既有斷言更新 + 新測試）

---

## 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-3 | P3 渲染：**一-a 圖在上** + **C 副標併 `.slide-head` 標題塊**（順帶解 一-b 夾線）+ **A/B/C 內文子標題 `**X**`→`### X`(h3)**；base CSS：`.slide-head`/`.slide-sub` 樣式 + **二 巢狀 ul 縮排**；更新既有斷言 + 新測試 | `待 baron 回填` |

---

## 阻斷性問題與真因

### 設計意圖核對（design/docs，先確立「什麼是對的」）

| 文件 | 規範 | 對本 hotfix 的意義 |
|---|---|---|
| `typography.md` L36-37 | 文章 **h2** 有底線（1px Mies / 2px Kahn）、**h3** 無底線、**h4 未規範** | h2 底線是**設計明文意圖**、不可在 base 偷蓋；A/B/C 子標題該用 h3（h4 會是無樣式孤兒）|
| `principles.md` L12/L24 | 結構性分隔由 `--color-divider`/`--divider-w` 控制；主題=外觀、**結構/間距歸主檔** | 巢狀縮排=結構 → 放 base；底線用主題變數保各主題吻合 |
| `theme-guide.md` L86/L179 | 主題不寫 width/padding/margin（印刷內距除外）；DOM 結構屬主檔 | `.slide-head` 結構 + base CSS 是正途、不動 4 主題檔 |

### 一-a. 版面順序（投影片該先看到圖）

**現象**：閱讀每頁順序為 `## 標題 → ### 小標題 → 整頁截圖 → 內文`；baron 希望**先看投影片原圖、標題在下**。
**真因**：P3 `_page_source_md`/`_deliver` 之 `parts` 組裝順序把標題置前、圖置後。

### 一-b. 大標題與小標題間夾一條底線（被 C 一併解決）

**現象**：`植物營養` 與 `可用性 + 可存取性 + 留存` 之間隔著一條橫線（觀感突兀）。
**真因**：slide 頁標題用 `## h2`（典型主題給「章節標題」加 border-bottom 分隔線），小標題用 `### h3` 緊接其後 → h2 的章節分隔線夾在「標題/小標題」這對之間。**底線本身是設計要的**（typography.md）、錯在我們把「標題+副標一對」拆成 h2+h3 觸發了章節語意。

### C. 小標題形式（baron 定案：副標併入標題塊）

**決策**：小標題不該是 h3 章節（它是副標、不是子章節）。改成**與大標題同框的 `.slide-head` 標題塊、底線移到整塊之下** → 最還原投影片（標題+副標一體）、且 h2 章節分隔線不再夾在中間（**一-b 隨之消失**）。

### A/B/C. 內文子標題（粗體黏 bullet + 扁平）

**現象**（紅框）：`A 層 (A horizon)` / `B 層` / `C 層` 等內文小節標題以 `**粗體**` 呈現、緊貼自己的 bullet（無間距）、層級扁平不像子標題。
**真因（碼證 + md 實證）**：Vision 把投影片內小節標題忠實轉錄為 `**bold**`；HOTFIX-2 F 之 `_normalize_paragraph_breaks` 對「bold 行→其下 bullet」之轉場不補空行（保 tight list 規則誤傷）。`**粗體**` 非真標題 → 無 heading 樣式/間距。
**修法**：整行純 `**X**` 之內文子標題 → 升 `### X`（h3、設計已規範·無底線·19px/600）→ 真子標題、有樣式間距、且擁有自己的 bullet 群（heading 自帶 margin）。**不升 h4**（設計未規範會成孤兒）。

### 二. 子項目沒縮排（純前端 CSS）

**現象**：`水分 / pH / 質地` 等第二層項目顯示為 `◦` 空心點、但**水平位置與第一層幾乎相同**、無縮排。
**真因（md 實證）**：md 巢狀**正確**（`* 父\n    - 子` 4 空格 + `-`）、前端也判成巢狀 `ul ul`（空心點為證）；缺的只是**巢狀 `ul` 的左縮排 CSS**。`#paper-content ul/li` 縮排由主題提供、無人給 nested → 連自訂主題也會塌。
**修法**：base 加 `ul ul { padding-left }` 結構性 fallback（縮排=結構、`principles.md` 結構歸主檔；含自訂主題受益）。

### ✅ RAG 安全性驗證（C 改 subtitle 渲染前置確認，碼證）

`_deliver` 建 `rag_sections`（RAG 真正索引結構）時 subtitle 僅兩處 fallback：
```python
"title": zh_title or zh_subtitle or f"page {N}",     # 僅 zh_title 空時才用 subtitle
"summary_key": self.page_key(N, self._key_title(u)), # _key_title=title or subtitle（吃欄位非渲染）
"content": [{"type":"text","content": merged}],      # merged=content+desc，【不含 subtitle】
```
- subtitle **文字不進 RAG chunk body**（merged 無 subtitle）。
- subtitle 只當「無大標題頁」之 title/key **fallback、吃欄位值不吃 `### ` 渲染形式**。
- RAG 餵 `ctx.rag_sections` 旁路、**不餵 final_zh.md**（碼證 run_phase4「不餵 reading-view final_zh.md」）。
→ **C 把閱讀視圖 `### subtitle` 改 `.slide-head` HTML，對 RAG 零影響**；本 hotfix 只動 `parts`（渲染），`sections.append({...})` 原封不動。

---

## 熱修復修法 (Minimal Hotfix)

### `pipelines/slide_pipeline.py` — P3 渲染三點（`# === [PIPE-SLIDES-HOTFIX-3 ...] ===` 包裹）

#### 新增兩個私有 helper（放 `_page_source_md` 前）

```python
# === [PIPE-SLIDES-HOTFIX-3 START] ===
@staticmethod
def _slide_head_html(title, subtitle) -> str:
    """C：標題+副標併入單一 .slide-head 標題塊（raw HTML、底線由 CSS 移整塊下）。

    還原投影片「大標題 + 緊貼副標」一體感；h2 仍為 h2（語意/RAG 不變）、副標降 .slide-sub
    （不再 h3、不觸發 h2 章節分隔線夾在中間 → 一-b 隨之消失）。title/subtitle escape 防破版。
    """
    import html as _html
    t = (title or "").strip()
    s = (subtitle or "").strip()
    if not t and not s:
        return ""
    rows = []
    if t:
        rows.append(f"<h2>{_html.escape(t)}</h2>")
    if s:
        rows.append(f'<p class="slide-sub">{_html.escape(s)}</p>')
    return '<div class="slide-head">\n' + "\n".join(rows) + "\n</div>"

@staticmethod
def _promote_subheadings(text: str) -> str:
    """A/B/C：整行純 **X** 之內文子標題 → ### X（升設計內 h3、無底線、有間距）。

    Vision 把投影片內小節標題（A horizon/B horizon…）忠實轉錄為 **bold**；扁平且黏 bullet。
    升 h3（typography 已規範）→ 真子標題擁有自己 bullet 群；前補空行確保 heading 解析。
    """
    out = []
    for line in (text or "").split("\n"):
        # \r? 相容 Windows 換行（split('\n') 殘留 \r 會使 $ 匹配失敗·盲點1）
        m = re.match(r"^\s*\*\*(.+?)\*\*\s*\r?$", line)
        if m:
            if out and out[-1] != "":          # 前一行非空才補（避免連續多餘空行·盲點2）
                out.append("")
            out.append(f"### {m.group(1).strip()}")
        else:
            out.append(line)
    return "\n".join(out)
# === [PIPE-SLIDES-HOTFIX-3 END] ===
```

#### `_page_source_md`（en）— 重排 + 標題塊 + 子標題升級

```python
    @staticmethod
    def _page_source_md(u: dict) -> str:
        """單頁原文 markdown（en 版還原與整檔 fallback 共用）。"""
        parts = []
        # === [PIPE-SLIDES-HOTFIX-3 START] === 一-a 圖在上
        alt = (u.get("figure_description") or u.get("title") or f"page {u['page']}").strip()
        parts.append(f"![{SlidePipeline._safe_alt(alt)}]({u['image_file']})")
        # C 副標併標題塊（取代原 ## title / ### subtitle）
        head = SlidePipeline._slide_head_html(u.get("title"), u.get("subtitle"))
        if head:
            parts.append(head)
        if (u.get("content") or "").strip():
            # A/B/C 子標題升 h3 → 再段落正規化（zh/en 對稱）
            body = SlidePipeline._promote_subheadings(u["content"].strip())
            parts.append(SlidePipeline._normalize_paragraph_breaks(body))
        # === [PIPE-SLIDES-HOTFIX-3 END] ===
        return "\n\n".join(parts)
```

> 原 `## {title}` / `### {subtitle}`（META-NORM C4 + 既有）由 `_slide_head_html` 取代；原 alt/F4 邏輯保留、只是順序改（圖先）。

#### `_deliver`（zh）正常路 — 同款重排（`sections.append` 不動）

```python
            zh_pages, sections = [], []
            for i, u in enumerate(tiles):
                zh_title, zh_subtitle, zh_content, zh_desc = zh_fields[i]
                parts = []
                # === [PIPE-SLIDES-HOTFIX-3 START] === 一-a 圖在上 + C 標題塊 + A/B/C h3
                alt = zh_desc or zh_title or f"page {u['page']}"
                parts.append(f"![{self._safe_alt(alt)}]({u['image_file']})")
                head = self._slide_head_html(zh_title, zh_subtitle)
                if head:
                    parts.append(head)
                if zh_content:
                    body = self._promote_subheadings(zh_content)
                    parts.append(self._normalize_paragraph_breaks(body))
                # === [PIPE-SLIDES-HOTFIX-3 END] ===
                zh_pages.append("\n\n".join(parts))
                # Q3 同頁短 items 合併（rag_sections，原封不動·RAG 安全）
                merged = "\n\n".join(x for x in (zh_content, zh_desc) if x)
                sections.append({
                    "title": zh_title or zh_subtitle or f"page {u['page']}", "level": 2,
                    "summary_key": self.page_key(u["page"], self._key_title(u)),
                    "content": [{"type": "text", "content": merged}], "children": [],
                })
```

> **`sections.append({...})` / `merged` / 譯題旁路 / `ctx.rag_sections` 完全不動** —— RAG 鏈零衝擊（§驗證已證）。退化路（whole_zh）不含逐頁結構、本就無標題塊、不受影響。

### `static/index.html` — base CSS 兩點（`/* === [PIPE-SLIDES-HOTFIX-3 ...] === */`，接 `#paper-content h2` 區後）

```css
  /* === [PIPE-SLIDES-HOTFIX-3 START] === */
  /* C：簡報標題塊——底線移到「標題+副標」整塊之下（用主題 divider 變數、各主題自動吻合）；
     內層 h2 不再各自畫線（覆寫主題 #paper-content h2 border、特異度 1,1,1 > 1,0,1） */
  #paper-content .slide-head {
    border-bottom: var(--divider-w) solid var(--color-divider);
    padding-bottom: var(--space-2);
    margin: var(--space-6) 0 var(--space-3);
  }
  #paper-content .slide-head h2 {
    border-bottom: none;
    padding-bottom: 0;
    margin: 0;
  }
  #paper-content .slide-sub {
    font-size: 15px;
    color: var(--color-text-secondary);
    margin: 4px 0 0;
    line-height: 1.5;
  }
  /* 二：巢狀清單縮排（結構性 fallback、主題無關、含自訂主題受益） */
  #paper-content ul ul, #paper-content ol ol,
  #paper-content ul ol, #paper-content ol ul {
    padding-left: 1.5em;
  }
  /* === [PIPE-SLIDES-HOTFIX-3 END] === */
```

> `--divider-w`/`--color-divider`/`--space-*` 皆主題既有變數（principles.md）→ `.slide-head` 底線自動套用當前主題的分隔線粗細/色,不動 4 主題檔。

### `tests/test_slide_pipeline.py` — 既有斷言更新 + 新測試（`# === [PIPE-SLIDES-HOTFIX-3 ...] ===`）

**⚠️ 既有測試需更新**（輸出由 `## title`/`### subtitle` 改為 `.slide-head` HTML）：
- `test_c4_subtitle_extraction_and_rendering`：`'## Plant Nutrition'`→`'<h2>Plant Nutrition</h2>'`、`'### availability'`→`'<p class="slide-sub">availability'`；無大標題 fallback 斷言（rag_sections key）不變。
- `test_c4_subtitle_translated_in_parallel`：`'### 譯sub-label'`→`'<p class="slide-sub">譯sub-label'`。
- `test_p3_alt_aligned_no_caption_segment_no_header`：`'## 譯Arch'`→`'<h2>譯Arch</h2>'`；`not zh.startswith('# ')` 改為驗首元素為圖（`![`）。
- `test_hf4_*`/`test_c4_*` 等含 `## `/`### ` 斷言者同步調整。

**新測試**：
```python
def test_hf3_image_first_and_slide_head():
    """一-a + C：圖在 .slide-head 之前；標題塊為 <div class="slide-head"> 含 <h2>+.slide-sub。"""
    # run_phase3（FakeTranslator）→ final_zh：![ 先於 <div class="slide-head">；
    # 含 <h2>譯Arch</h2> 與 <p class="slide-sub">譯sub</p>；無 ## / ### 標題行。

def test_hf3_subheading_promoted_to_h3():
    """A/B/C：content 整行 **X** → ### X；非整行 bold 不動；\\r 相容；不產連續空行。"""
    from pipelines.slide_pipeline import SlidePipeline as S
    assert "### B層" in S._promote_subheadings("* a\n**B層**\n* b")
    assert S._promote_subheadings("這是 **強調** 句") == "這是 **強調** 句"   # 句中 bold 不誤升
    assert "### B層" in S._promote_subheadings("* a\r\n**B層**\r\n* b")        # 盲點1：\r 相容
    assert "\n\n\n" not in S._promote_subheadings("* a\n\n**B層**\n* b")       # 盲點2：不產連續空行

def test_hf3_slide_head_escapes():
    """C：title/subtitle 含 <>& 須 escape 防破版。"""
    from pipelines.slide_pipeline import SlidePipeline as S
    h = S._slide_head_html("A<b> & C", "x>y")
    assert "&lt;b&gt;" in h and "&amp;" in h and '<p class="slide-sub">' in h

def test_hf3_rag_sections_unaffected(monkeypatch, tmp_path):
    """RAG 安全：rag_sections 仍以 title/欄位建、不受 .slide-head 渲染影響。"""
    # run_phase3 後 ctx.rag_sections[0]['summary_key']=='p01_Arch'、content 不含 subtitle。
```

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
```bash
venv/bin/python -m pytest tests/test_slide_pipeline.py -v   # 既有更新後 + 新 4 測試全綠
venv/bin/python -m pytest tests/ -q                          # 全套件不退化（基準 601 passed）
```
回歸網重點：`test_hf3_rag_sections_unaffected`（rag 鏈零變）、META-NORM C4 之 subtitle 提取/key fallback 仍成立、HOTFIX-1/2 之 alt/段落/譯題不受順序改影響。

### §5 SOP 核查（BE-Hotfix 強制）
```bash
grep -nE "traceback.format_exc|logger\.error" pipelines/slide_pipeline.py   # 預期：無命中
grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v session.begin # 預期：無命中
```

### 2. 本地 E2E 快速復現與驗證（baron、非 commit）
影子重傳 `Ch37` → 每頁：① **整頁截圖在上、標題塊在下**（一-a）② 標題+副標**同框、中間無夾線**、底線在整塊下（C/一-b）③ A 層/B 層/C 層為**有間距的子標題**、bullet 群組其下（A/B/C）④ water/pH/texture 等**明顯往右縮排**（二）。chat 引用「《簡報名》> p{N} 標題」不變（RAG 未動）。

### ⚠️ 行為變更 + golden
改 B 軌 `final_zh`/`final_en` 渲染結構 → **衝擊 slides golden**（與前 HOTFIX-1/1b/2 + META-NORM C3/C4 同屬 B 軌輸出變更）。slides golden 尚未首捕 → **維持原計畫：全部 Vision/渲染變更落地後一次首捕**（`tools/golden_baseline.py capture slides --force`、且 slides fixture 需先補齊·見運維備忘）。

---

## 回退與備案

```bash
git revert <HOTFIX-3 hash>          # 三點互不依賴、整體 revert 安全（回到 META-NORM C4 渲染）
# 或還原 .bak：
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-3_slide_pipeline.py.bak
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-3_index.html.bak
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-3_test_slide_pipeline.py.bak
```

---

## 範圍註記（誠實邊界）

- **一-b 不在 base 用 `:has()` 蓋主題底線** —— typography.md 證 h2 底線是設計意圖；改由 C 從根源（標題塊重構）解，不違設計、不碰 4 主題檔。
- **A/B/C 升 h3、非 h4** —— h4 設計未規範、會是無樣式孤兒。
- **二 放 base** —— 縮排=結構（principles.md），結構歸主檔、含自訂主題受益;非挖東牆。
- **raw HTML in md** —— marked 9.1.6 預設通過 HTML（無 sanitize、grep 證 index.html:2778）;title/subtitle escape 防特殊字元破版。
- **HTML 區塊內 markdown 失效（盲點3）** —— `.slide-head` 為 raw HTML 塊,marked 不解析塊內文字之 markdown 標記（若標題含 `**粗體**` 會原樣顯示 `**…**` 而非粗體）。簡報 title/subtitle 極少含 markdown 語法、影響極小;但若日後出現,需知此限制（避免誤判為 bug）。
- **RAG 零影響** —— 已碼證（subtitle 不進 chunk body、rag 餵旁路不餵 md）;`sections.append` 原封不動。
- **不動**：A 軌 / rag_indexer / orchestrator / 4 個主題檔 / META-NORM 飛輪 / HOTFIX-1/1b/2 既有區塊。

---

## commit message 草稿（落地時寫入 /tmp/PIPE-SLIDES-HOTFIX-3_msg.txt）

```
BE-Hotfix: PIPE-SLIDES HOTFIX-3 — 簡報閱讀視圖排版打磨（圖序/副標併標題塊/子標題/縮排）

baron 前端逐頁 QA（Ch37 簡報）+ design/docs 設計意圖核對後，4 項閱讀視圖排版修：
- 一-a 圖在上標題在下：P3 _page_source_md/_deliver parts 重排（圖 → 標題塊 → 內文）
- C 副標併標題塊：_slide_head_html 產 <div class="slide-head"><h2>+<p class="slide-sub">
  （取代 ## title/### subtitle）；底線由 base CSS 移整塊下（用主題 --divider-w 變數）→
  順帶解 一-b（h2 章節分隔線不再夾在標題/副標之間）；h2 仍 h2、副標降 .slide-sub
- A/B/C 內文子標題：_promote_subheadings 整行 **X** → ### X（升設計內 h3、非孤兒 h4、
  修 HOTFIX-2 F 粗體黏 bullet）
- 二 巢狀縮排：base CSS #paper-content ul ul { padding-left }（結構 fallback、含自訂主題）
- 設計對齊：h2 底線是 typography.md 明文意圖（不在 base 蓋）、改 C 從根源解；不動 4 主題檔
- RAG 安全：subtitle 不進 chunk body、rag 餵 ctx.rag_sections 不餵 final_zh.md、
  sections.append 原封不動 → C 改渲染零影響（已碼證）
- 更新既有 ##/### 斷言 + 4 新測試（圖序/標題塊/h3 升級/escape/rag 不變）
- ⚠️ 改 B 軌輸出 → slides golden 全變更落地後一次首捕

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
