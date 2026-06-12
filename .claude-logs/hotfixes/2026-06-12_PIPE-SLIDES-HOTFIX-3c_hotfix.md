# PIPE-SLIDES-HOTFIX-3c — 簡報「標題+重點」節奏正規化（保留原始符號·硬換行收緊）

> 工作流：**BE-Hotfix**（動 `pipelines/slide_pipeline.py` 渲染層、零後端 API/DB）
> 依據：`templates/template_hotfix.md` / `ref/WORKFLOW_SOP.md §1.5 + §5` / `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.3/§4.4`
> 必讀 SOP：`sop/2026-05-23_logging_SOP_手冊.md` + `sop/2026-05-23_database_SOP_手冊.md`（本修零 logging/db 變更，§5 核查見 §7.5）
> 代號：延續 `PIPE-SLIDES-HOTFIX-3`（slide 閱讀視圖節奏家族；3/3b 為前端 CSS、**3c 為管線端結構正規化**）

---

## 1. 基準與完成狀態

- 基準 Commit：`HOTFIX-3b`（top-level 清單凸排修補）
- 完成狀態：**未 commit**（baton 暫存、待 baron 過目 → Run）
- 改檔範圍：`pipelines/slide_pipeline.py` 單檔（新增 1 私有 helper + 2 渲染注入點）
- 不動：後端 API / DB / RAG 載入端 / `ctx.rag_sections` 建構 / `static/*` / 其餘四路 pipeline

---

## 2. 真因（Root Cause）

### 2.1 症狀（兩頁、兩種不一致節奏）
baron 前端逐頁 QA `Ch37_Plant-Nutrition` 影子件，「標題+重點群」節奏每頁不同：
- **頁 A（土壤顆粒）**：母項→子項縫大、子項→下一母項貼緊。
- **頁 B（氮素形態）**：標題貼第一項（小）、項目彼此散開（大）。

### 2.2 原文鐵證（PaperRead-Lab `final_Ch37_..._zh.md`、含空行）

頁 A（L176-188）—— `*` 清單、母項被空行隔開（loose list）：
```
176: * 礫石 (Gravel) (> 2.0 mm)
177:   * -> 極大孔隙 (pores) -> 排水迅速、保水力低
178: (空行)              ← 母項群組間有空行
179: * 砂粒 (Sand) (0.02–2.0 mm)
...
```

頁 B（L271-285）—— `###` 標題 + `→` 散段落：
```
271: ### NH₄⁺ (銨離子 / ammonium)
272: (空行)
273: → 帶正電 (positively charged)     ← → 非 markdown 清單符號 → 獨立 <p>
274: (空行)
275: → 與帶負電的土壤顆粒結合
276: (空行)
277: → 保留在土壤中
278: (空行)
279: ### NO₃⁻ ...
```

### 2.3 機制（CommonMark × 主題 CSS margin）
| 結構 | marked 渲染 | 吃到的 margin（kahn 為例） |
|---|---|---|
| 頁 A 外層 `*`（空行隔開）= loose list | 母項文字包 `<p>` | `#paper-content p { margin-bottom: space-4 }`(16px) → 母項下大縫 |
| 頁 A 內層 `* ->`（無空行）= tight | 不包 `<p>` | `li` 零 margin → 貼緊下一母項 |
| 頁 B `→`（空行隔開）= 獨立段落 | 各自 `<p>` | 段落間 16px |
| 頁 B `### 標題` | h3 | `margin-bottom: space-2`(8px) → 貼第一項 |

→ 根源非 CSS、是 **Vision 對「標題+重點」每頁吐不同 markdown 結構**（時而 `*` 清單、時而 `→` 散段落）；CSS 對「loose `<p>` / tight `<li>` / 散段落」給不同節奏，每頁就長不一樣。

### 2.4 解法決策（baron 拍板）
- **走管線端正規化（非 CSS）**：頁 B 的 `→` 是散段落，CSS 抹平只能調全域 `#paper-content p`/`h3` margin → **滲進學術論文**（slide 正文無 wrapper class 可隔離；`.slide-head` 只包標題塊）。管線端把重點群收緊 → 全 slides 節奏一致、零論文外溢。
- **保留 `→` 原始符號（非轉 bullet）**：baron 拍板「`→` 在原稿就是文字、原樣保留、只修排版」。
  - **採用「硬換行收緊」**：連續行首 `→` 行合併為**單一段落 + 行間兩尾隨空格硬換行（`<br>`）** → tight 群、`→` 原樣保留為文字。
  - **不採 review 的「轉 `-` + scoped CSS `list-style-type:"→ "`」**：① 會把頁 A 原本的 `•` 一併變 `→`（轉 `-` 後失去「原箭頭/原點」身分）→ 破壞保真；② 需新增 `.slide-body` wrapper 才能 scope（否則全域滲入論文/履歷）。硬換行案**天然保留各頁原始符號、不需 wrapper/新 CSS**。
  - **權衡（已知）**：氮素群組是 `<p>`+`<br>` 而非 `<ul>`（語意略弱於 list）；對「投影片閱讀視圖、貼原稿」之保真取捨，baron 已拍板接受。

### 2.5 RAG 零影響（碼層自證）
`pipelines/slide_pipeline.py:865`：
```python
merged = "\n\n".join(x for x in (zh_content, zh_desc) if x)   # rag_sections 用「原始 zh_content」
sections.append({... "content": [{"type": "text", "content": merged}] ...})
```
`rag_sections` content 取**原始 `zh_content`**，**非**經 `_promote_subheadings`/`_normalize_paragraph_breaks`/`_tighten_point_groups` 的渲染 `body`。本修只加在**渲染路 `body`** → `merged`/`rag_sections` 不碰 → **RAG 召回零影響**（slides RAG 走 `ctx.rag_sections` 旁路 + `rag_indexer`、不從 final_zh 切）。

---

## 3. 修法（程式碼）

### 3.1 新增私有 helper `_tighten_point_groups`（slide_pipeline.py、`_promote_subheadings` 之後）

```python
    # === [PIPE-SLIDES-HOTFIX-3c HOTFIX-3c START] ===
    @staticmethod
    def _tighten_point_groups(text: str) -> str:
        """簡報「標題+重點」節奏正規化（保留原始符號、不轉 bullet）。

        ① 連續『行首箭頭 → / ->』行 → 合併為單一段落、行間兩尾隨空格硬換行（<br>）→ tight 群、
           箭頭原樣保留為文字；行中箭頭（如「吸收 NH₄⁺ → 釋放 H⁺」連接詞）不碰。
        ② 『- * + • / 數字.』清單之相鄰項間空行收緊（loose→tight）；清單↔標題/圖/段落 邊界留白。

        **殿後於 _normalize_paragraph_breaks**（其單 \\n→\\n\\n 不再拆我的硬換行群）。
        **只動渲染 body、不碰 rag_sections（RAG 零影響）。** \\r? 相容 CRLF（對齊 _promote_subheadings 風格）。
        """
        if not text:
            return text
        lines = text.split("\n")
        ARROW_RE = re.compile(r"^(\s*)(?:→|->)\s+(.+?)\s*\r?$")
        LIST_RE = re.compile(r"^\s*(?:[-*+•]|\d+[.、])\s+")
        # ① 合併連續行首箭頭群（群內空行跳過、遇非箭頭非空行斷群）
        merged = []
        i, n = 0, len(lines)
        while i < n:
            if ARROW_RE.match(lines[i]):
                group = [lines[i].rstrip("\r")]
                j = i + 1
                while j < n:
                    if ARROW_RE.match(lines[j]):
                        group.append(lines[j].rstrip("\r"))
                        j += 1
                    elif lines[j].strip() == "":
                        k = j + 1
                        while k < n and lines[k].strip() == "":
                            k += 1
                        if k < n and ARROW_RE.match(lines[k]):
                            j = k          # 跳過群內空行、續併
                        else:
                            break          # 群尾（下一個非空非箭頭）→ 斷
                    else:
                        break
                # ≥2 行才合併硬換行（單行箭頭保持原樣、屬獨立點）
                merged.append("  \n".join(group) if len(group) >= 2 else group[0])
                i = j
            else:
                merged.append(lines[i])
                i += 1
        # ② 相鄰清單項間空行收緊（兩側皆清單才丟、邊界留白）
        out, m = [], len(merged)
        for idx, line in enumerate(merged):
            if line.strip() == "":
                prev = next((merged[p] for p in range(idx - 1, -1, -1)
                             if merged[p].strip()), "")
                nxt = next((merged[q] for q in range(idx + 1, m)
                            if merged[q].strip()), "")
                if LIST_RE.match(prev) and LIST_RE.match(nxt):
                    continue   # 兩側皆清單 → 丟此空行（tight）
            out.append(line)
        return "\n".join(out)
    # === [PIPE-SLIDES-HOTFIX-3c HOTFIX-3c END] ===
```

### 3.2 注入點一 `_page_source_md`（en + 退化 fallback 共用、L766-769）

```python
        if (u.get("content") or "").strip():
            body = SlidePipeline._promote_subheadings(u["content"].strip())
            body = SlidePipeline._normalize_paragraph_breaks(body)
            # === [PIPE-SLIDES-HOTFIX-3c HOTFIX-3c] === 重點群收緊（殿後、硬換行不被 normalize 拆）
            body = SlidePipeline._tighten_point_groups(body)
            parts.append(body)
```

### 3.3 注入點二 `_deliver`（zh 正常路、L858-861）

```python
                if zh_content:
                    body = self._promote_subheadings(zh_content)
                    body = self._normalize_paragraph_breaks(body)
                    # === [PIPE-SLIDES-HOTFIX-3c HOTFIX-3c] === 重點群收緊（殿後、硬換行不被 normalize 拆）
                    body = self._tighten_point_groups(body)
                    parts.append(body)
```

> **順序鐵則**：`_tighten_point_groups` **必須殿後**（在 `_normalize_paragraph_breaks` 之後）。否則 normalize 的 `單 \n → \n\n` 會把硬換行（`  \n`）拆回 `\n\n` 雙段落、群組失效。
> `merged`（L865，rag_sections content）**不套任何渲染 helper** → RAG 零影響。

### 3.4 渲染後預期

頁 B（氮素，保留 `→`）：
```
### NH₄⁺ (銨離子 / ammonium)
→ 帶正電 (positively charged)␣␣        （␣␣ = 硬換行）
→ 與帶負電的土壤顆粒結合␣␣
→ 保留在土壤中
                                       （群尾留白、下一 ### 前）
### NO₃⁻ ...
```
→ `<h3>` + `<p>→ 帶正電<br>→ …<br>→ 保留</p>` + `<h3>`：標題貼群 8px、項↔項 `<br>` 行高（緊湊）、群→下個標題 16px。

頁 A（土壤，保留 `•`）：外層 `*` 母項間空行收緊 → 全清單 tight、節奏均勻；內層 `* -> 極大孔隙` 不動（`->` 在 `* ` 之後＝項目文字、非行首箭頭）。

> **行中箭頭保留**：`### 對土壤化學的耦合效應` 下 `吸收 NH₄⁺ → 釋放 H⁺ → 土壤酸化`（整句、行中箭頭、行首為「吸收」）→ ARROW_RE 不匹配 → 續段落（語意正確、非短點）。

### 3.5 與既有 helper 互動（不衝突）
- 順序：`_promote_subheadings`（`**X**`→`### X`）→ `_normalize_paragraph_breaks`（單 \n 正規化、list-aware）→ `_tighten_point_groups`（殿後、箭頭群硬換行 + `*` loose 收緊）。
- 殿後保證硬換行（`  \n`）為最終輸出、直送 marked、不被 normalize 反向拆段。

---

## 4. 不可動清單遵守狀態

- [x] 不動後端 API（`web_server.py`）/ DB / models
- [x] 不動 `ctx.rag_sections` 建構（`merged` 沿用原始 `zh_content`）→ RAG 召回零影響
- [x] 不動 RAG 載入端（`rag_retriever` / `ai_core` / `rag_indexer`）
- [x] 不動 `static/*`（與 3/3b CSS 正交）
- [x] 不動其餘四路 pipeline（resume/academic/litedoc/book）與 A 軌
- [x] 不動 `_promote_subheadings` / `_normalize_paragraph_breaks` / `_slide_head_html` 既有邏輯（僅前後串接新 helper）
- [x] 保留各頁原始符號（`•` 仍 `•`、`→` 仍 `→`、不轉換）

---

## 5. 端到端驗證計畫

### 5.1 靜態 grep
```bash
grep -n "_tighten_point_groups" pipelines/slide_pipeline.py        # 定義 1 + 注入 2 = 3 命中
grep -n "HOTFIX-3c" pipelines/slide_pipeline.py                    # START/END + 2 注入 = 4 命中
grep -n "merged = " pipelines/slide_pipeline.py                    # 確認 merged 仍取原始 zh_content（未套 tighten）
```

### 5.2 pytest（新增回歸 + 全套件）
新增於 `tests/test_slide_pipeline.py`（≥6）：
- `test_hf3c_arrow_group_hardbreak`：連續 `→ a` / `→ b` / `→ c` → 單段落含 `  \n`（兩空格硬換行）、**不含** bullet `- `、`→` 保留。
- `test_hf3c_inline_arrow_preserved`：`吸收 A → 釋放 B`（行首非箭頭）不合併、續段落。
- `test_hf3c_single_arrow_unchanged`：孤行 `→ x` 不加硬換行（保持原樣獨立點）。
- `test_hf3c_loose_list_tightened`：`* a\n\n* b` → `* a\n* b`（相鄰清單空行收緊、`*` 保留）。
- `test_hf3c_list_heading_boundary_blank_kept`：`- a\n\n### H` 空行保留（標題不被吸入清單）。
- `test_hf3c_crlf_compat`：`→ a\r\n→ b\r` 經 split('\n') 殘 `\r` 仍正確合併、無 `\r` 殘於輸出。
- `test_hf3c_rag_sections_unaffected`：跑 `_deliver`、斷言 `ctx.rag_sections[i]["content"][0]["content"]`（= merged）**等同原始 `zh_content`**、不含硬換行/收緊痕跡（RAG 隔離鐵證）。
- `test_hf3c_nitrogen_end_to_end`：頁 B 擬真輸入 → `zh_text` 含 `### NH₄⁺...` 後緊接 `→ ...  \n→ ...` 硬換行群、群與下個 `###` 間留 `\n\n`。

全套件：`venv/bin/python -m pytest tests/ -q`（維持綠；已知 `.env LOG_FORMAT=json` env flake 1 例不計）。

### 5.3 baron E2E（前端、非 commit）
- 影子重傳 Ch37 → 頁 B（氮素）`NH₄⁺` 標題下三點為**均勻緊湊群、`→` 原樣保留**、`NH₄⁺` 群與 `NO₃⁻` 群間有留白。
- 頁 A（土壤）母項/子項節奏均勻、`•` 保留、無「母項下大縫 / 子項貼下一母項」。
- 行中箭頭句（耦合效應）維持段落、未變群。
- chat 對該頁提問召回正常（RAG 未受影響佐證）。

### 5.4 ⚠️ Golden
改 B 軌 final_zh 渲染（箭頭群硬換行 + `*` 收緊）→ **slides golden 變更**；併入既有「slides golden 待 fixture 補齊後一次首捕」批次（HOTFIX-1/1b/2/3 + META-NORM C3/C4 + 本 3c），不另捕。

### 5.5 §5 SOP 一致性核查（BE 強制）
```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/slide_pipeline.py
# 本修新增碼段（_tighten_point_groups + 2 注入）零 logging 呼叫 → 無命中（合規）

grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v "with .*session.*begin\(\)"
# 本修零 DB → 無命中（合規）
```
（落地後貼真實輸出；空輸出註「無命中（合規）」。）

---

## 6. 回退方式（Rollback）

移除 `# === [PIPE-SLIDES-HOTFIX-3c ...] ===` 包裹的 helper + 2 注入區塊，或 `git revert <HOTFIX-3c hash>`。不涉 DB/向量/schema；rag_sections 本就未受影響，回退僅還原 final_zh 渲染。

---

## 7. Commit

**git add 清單**：
```
pipelines/slide_pipeline.py
tests/test_slide_pipeline.py
.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3c_HOTFIX-3c_slide_pipeline.py.bak
.claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3c_HOTFIX-3c_test_slide_pipeline.py.bak
.claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md     # 收官階段才 add，Run 階段留 baton
```

**commit message 草稿**（`/tmp/PIPE-SLIDES-HOTFIX-3c_msg.txt`）：
```
BE-Hotfix: PIPE-SLIDES-HOTFIX-3c — 簡報「標題+重點」節奏正規化（保留原始符號·硬換行收緊）

真因：Vision 對「標題+重點群」每頁吐不同 markdown 結構（頁 A `*` loose list / 頁 B
`###`+`→` 散段落），CSS 對 loose `<p>`(16px) / tight `<li>`(0) / 散段落(16px) 給不同
margin → 每頁節奏不一（頁 A 母項下大縫·子項貼母項；頁 B 標題貼首項·項目散開）。

修法：pipelines/slide_pipeline.py 新增私有 _tighten_point_groups（① 連續行首箭頭 →/->
合併為單一段落+兩空格硬換行<br>、tight 群、箭頭原樣保留為文字、行中箭頭不碰 ② 相鄰清單項
間空行收緊 loose→tight、清單↔標題/圖/段落邊界留白；\r? 相容 CRLF）；_page_source_md +
_deliver 渲染 body 殿後注入（於 _promote_subheadings + _normalize_paragraph_breaks 之後，
硬換行不被 normalize 單\n→\n\n 拆回段落）。全 slides 節奏一致、各頁原始符號（•/→）保留。

RAG 零影響：rag_sections content 取原始 zh_content（merged，L865）、未套 tighten；
slides RAG 走 ctx.rag_sections 旁路、不從 final_zh 切。零後端/DB/models/static 改動。
SOP 核查：新增碼段零 logging/commit → logging+database 皆無命中（合規）。

驗證：grep helper 3 命中 / HOTFIX-3c 4 命中 / merged 仍取原始 zh_content；新增回歸
（箭頭硬換行群/行中不碰/孤行不變/loose 收緊/邊界留白/CRLF/rag_sections 隔離/頁 B 端到端）
+ 全套件維持綠。⚠️ 改 B 軌 final_zh → slides golden 併既有批次一次首捕；baron E2E 影子重傳 Ch37。

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
