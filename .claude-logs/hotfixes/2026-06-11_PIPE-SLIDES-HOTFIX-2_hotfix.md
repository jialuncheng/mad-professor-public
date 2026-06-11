# PIPE-SLIDES HOTFIX-2 — 緊急熱修復：alt 括號破圖 / 母片重複日期 / F4 條列鬆散醜排（B+E+F）

> 工作流類別：**BE-Hotfix**（必讀 logging_SOP + database_SOP；驗收=pytest 全通過 + §5 SOP 核查）
> 依據：baron 學術簡報實件實測（`Ch37_Plant-Nutrition.pdf`、44/38 頁、迄今最大件）逐頁分析
> 決策：baron 拍板 **B（alt 轉義）+ E（母片日期洗除）+ F（修 HOTFIX-1 F4 條列回歸）三者合一**；A（重複標題）**撤案**（忠實轉錄、非 bug）；C/D（Vision schema）留 HOTFIX-3/後話
> 受災檔：`pipelines/slide_pipeline.py`（單檔三點）+ `tests/test_slide_pipeline.py`（補測試）

---

## 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-2 | `slide_pipeline.py` 三點：**B `_safe_alt`**（alt 內 `[]()` / 換行轉義、根除破圖）+ **E `_strip_master_date`**（P1 純日期母片頁眉 ≥2 頁直接洗、補統計去重格式變異漏網）+ **F `_normalize_paragraph_breaks` list-aware**（條列行單 `\n` 不升級、修 HOTFIX-1 鬆散回歸）；補回歸測試 | `待 baron 回填` |

---

## 阻斷性問題與真因

### B. alt 括號破壞 markdown 圖片語法（3 頁缺圖 + 全簡報圖說洩漏正文）

**1. 現象（實件證據）**
B 軌 `植物營養` 件 p29/p35/p37 **整頁截圖不顯示**（破圖 🖼️），且該頁長圖說以正文形式洩漏；封面頁亦見木桶圖描述大段洩漏。

**2. 真因（碼證）**
渲染 `![{alt}]({image_file})`（`slide_pipeline.py:622`/`706`），`alt` = Vision `figure_description` 譯文。圖密集頁描述充滿 `(Arbuscular mycorrhizae, AM)`、`[ammonium]` 這類**括號 + 中括號**。CommonMark `![alt](url)` 的 alt 段遇 **`]`** 提前閉合 → 圖片語法破裂 → ① 圖不顯示 ② `]` 後文字洩成可見正文。圖密集頁描述最長、括號最多 → 最易中招（純條列頁描述短 → 倖免，故偏偏那 3 頁）。

**3. 連帶**：HOTFIX-1 U8 alt 對齊（雙 Caption 根除）把描述塞進 alt，反而暴露此轉義缺口——B 修好後，破圖復原 + 描述縮回 alt 隱藏（C 之「圖說灌入」可見症狀一併消失）。

### E. 母片重複日期未洗除（`4/28/2026` 散落多頁正文）

**1. 現象**
B 軌正文多頁出現 `4/28/2026`；baron 核對**原稿 `Ch37_Plant-Nutrition.pdf` 20/20 頁每頁第一行皆為 `4/28/2026`**——係投影片匯出 PDF 時**母片日期欄位**烙進每頁，**非投影片內容**。Vision 忠實轉錄 → 每頁照抄。

**2. 真因（碼證 + 實測）**
Q2 統計去重 `_dedupe_headers`（`_DEDUPE_PAGE_RATIO=0.6`）格式一致時**確實能洗**（單元測試證：5 頁同格式 → 全洗）；但實測殘留——真因＝**Vision OCR 日期格式逐頁飄**（`4/28/2026` / `2026/4/28` / `4/28/26`），每變體各自 <60% 門檻 → 全躲過。
（驗證實測：4 頁三種變體 → `_dedupe_headers` 後三種全殘留。）

**3. 修法**：加 P1 **純日期行偵測**——整行僅日期（regex 比對、不依賴格式一致統計）、出現於 ≥2 頁 → 視母片頁眉剔除；正文中夾帶日期的句子不動（只剔「獨立成行且整行就是日期」者）。

### F. F4 `_normalize_paragraph_breaks` 把緊湊條列炸成鬆散條列（HOTFIX-1 回歸·誠實認）

**1. 現象**
土壤分層頁等條列密集頁，bullet 之間出現大量空行、視覺鬆散醜排（loose list）。

**2. 真因（碼證 + 實測）**
HOTFIX-1 F4 移植之 `_normalize_paragraph_breaks` 末行 `re.sub(r"(?<!\|)(?<!\n)\n(?![\n\|])", "\n\n", text)` **只排除 pipe table（`|`）、未排除條列行**。tight list `- a\n- b` 之 `\n` 後面是 `-`（非 `\n`/`|`）→ 被升級成 `- a\n\n- b` → CommonMark **loose list**（每 item 包 `<p>`、item 間插空行）。
（驗證實測：`- 富含有機質\n- 擁有...\n- 壤土...` → F4 後變 `\n\n` 分隔的 loose list。）
resume 未爆＝履歷正文多段落散文；簡報條列密集正好踩中。

**3. 修法**：F4 的單 `\n`→`\n\n` 升級**追加排除「下一行為條列行」**（`- `/`* `/`+ `/`• `/`數字. `/縮排子項）→ 條列維持 tight、段落仍正規化。**修我自己 HOTFIX-1 引入的 list 副作用。**

---

## 熱修復修法 (Minimal Hotfix)

### `pipelines/slide_pipeline.py` — 單檔三點（`# === [PIPE-SLIDES-HOTFIX-2 ...] ===` 包裹）

#### B：新增 `_safe_alt` + 兩處 alt 套用

新增私有 helper（P1/P3 共用）：

```python
# === [PIPE-SLIDES-HOTFIX-2 B START] ===
@staticmethod
def _safe_alt(text: str) -> str:
    """alt 文字轉義（HOTFIX-2 B）：CommonMark ![alt](url) 之 alt 內 ] [ ( ) 換行會破壞
    語法 → ① 破圖 ② 文字洩成正文。中括號/括號轉全形（語意可讀不損）、換行轉空白。"""
    if not text:
        return text
    trans = str.maketrans({"[": "［", "]": "］", "(": "（", ")": "）"})
    return " ".join(text.translate(trans).split())
# === [PIPE-SLIDES-HOTFIX-2 B END] ===
```

兩處渲染套用（原 L621-622 `_page_source_md` en 版 / L705-706 `_deliver` zh 版）：

```python
# _page_source_md（en）
        alt = (u.get("figure_description") or u.get("title") or f"page {u['page']}").strip()
        parts.append(f"![{SlidePipeline._safe_alt(alt)}]({u['image_file']})")   # HOTFIX-2 B

# _deliver（zh）
                alt = zh_desc or zh_title or f"page {u['page']}"
                parts.append(f"![{self._safe_alt(alt)}]({u['image_file']})")    # HOTFIX-2 B
```

#### E：新增 `_strip_master_date` + `run_phase1` 套用（緊接 `_dedupe_headers` 後）

```python
# === [PIPE-SLIDES-HOTFIX-2 E START] ===
import re  # 模組頂已 import；此處示意
_DATE_LINE_RE = re.compile(
    r"^\s*\d{1,4}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{1,4}\s*$")

@staticmethod
def _strip_master_date(units: list) -> None:
    """母片日期頁眉洗除（HOTFIX-2 E）：整行僅為日期、且出現於 ≥2 頁 → 母片日期欄位
    （非投影片內容）剔除。補 _dedupe_headers 之不足——日期 OCR 格式逐頁飄、各變體
    <60% 門檻全漏網；本法以「整行即日期」語意判定、不依賴格式一致。剔除清單入 log。"""
    hit_pages = 0
    for u in units:
        if any(SlidePipeline._DATE_LINE_RE.match(ln) for ln in u["content"].splitlines()):
            hit_pages += 1
    if hit_pages < 2:
        return                       # 單頁日期可能是真內容（如時間軸）、不洗
    removed = 0
    for u in units:
        kept = [ln for ln in u["content"].splitlines()
                if not SlidePipeline._DATE_LINE_RE.match(ln)]
        removed += len(u["content"].splitlines()) - len(kept)
        u["content"] = "\n".join(kept).strip()
    logger.info("[PIPE-SLIDES P1] 母片日期頁眉洗除 pages=%d lines=%d", hit_pages, removed)
# === [PIPE-SLIDES-HOTFIX-2 E END] ===
```

`run_phase1` ⑥ 去重後套用（原 L191）：

```python
        self._dedupe_headers(units)
        # === [PIPE-SLIDES-HOTFIX-2 E] === 母片日期頁眉洗除（補統計去重格式變異漏網）
        self._strip_master_date(units)
```

#### F：`_normalize_paragraph_breaks` list-aware（原 L361 末行 regex 前增條列保護）

```python
        text = "\n".join(out_lines)
        # === [PIPE-SLIDES-HOTFIX-2 F START] === 單 \n→\n\n 升級追加排除「下一行為條列行」
        # （修 HOTFIX-1 F4 把 tight list 炸成 loose list 之回歸；條列維持緊湊、段落仍正規化）
        # 負向前瞻擴充：下一行為 - / * / + / • / 數字. / 縮排子項 時，不升級該 \n。
        return re.sub(
            r"(?<!\|)(?<!\n)\n(?![\n\|]|\s*(?:[-*+•]|\d+[.、])\s|\s*-\s)",
            "\n\n", text)
        # === [PIPE-SLIDES-HOTFIX-2 F END] ===
```

> 原 regex `(?![\n\|])` → 擴為 `(?![\n\|]|<條列前瞻>)`。pipe table 保護（既有 `\|`）不動。

### `tests/test_slide_pipeline.py` — 補 3 回歸測試（`# === [PIPE-SLIDES-HOTFIX-2 ...] ===`）

```python
def test_hf2b_alt_brackets_escaped():
    """B：alt 內 ] [ ( ) → 全形、換行→空白，圖片語法不破。"""
    from pipelines.slide_pipeline import SlidePipeline as S
    a = S._safe_alt("木桶 (barrel)（李比希 [Liebig's]）\n第二行")
    assert "]" not in a and ")" not in a and "\n" not in a
    # 端到端：圖密集頁 final_zh 含完整 ![...](images/page-NN.jpg)、無裸 ] 破壞

def test_hf2e_master_date_stripped():
    """E：≥2 頁整行日期（含格式變異）洗除；單頁日期保留；句中日期不動。"""
    units = [{"content": "4/28/2026\n內容A", "is_cover": False},
             {"content": "2026/4/28\n內容B", "is_cover": False},
             {"content": "活動於 4/28/2026 舉行", "is_cover": False}]  # 句中不剔
    SlidePipeline._strip_master_date(units)
    assert units[0]["content"] == "內容A" and units[1]["content"] == "內容B"
    assert "4/28/2026" in units[2]["content"]   # 句中日期保留
    # 單頁日期不洗
    one = [{"content": "2026/1/1\nx", "is_cover": False}]
    SlidePipeline._strip_master_date(one)
    assert "2026/1/1" in one[0]["content"]

def test_hf2f_list_stays_tight():
    """F：tight bullet list 不被升級成 loose；純段落仍升級 \\n\\n；table 不破。"""
    from pipelines.slide_pipeline import SlidePipeline as S
    assert S._normalize_paragraph_breaks("- a\n- b\n- c") == "- a\n- b\n- c"   # tight 維持
    assert S._normalize_paragraph_breaks("第一段\n第二段") == "第一段\n\n第二段"  # 段落仍升級
    assert "| A | 1 |\n| B | 2 |" in S._normalize_paragraph_breaks("| A | 1 |\n| B | 2 |")
    # 巢狀數字 + 縮排子項
    assert S._normalize_paragraph_breaks("1. 甲\n2. 乙") == "1. 甲\n2. 乙"
```

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
```bash
venv/bin/python -m pytest tests/test_slide_pipeline.py -v   # 既有 29 + 新 3 全綠
venv/bin/python -m pytest tests/ -q                          # 全套件不退化（基準 585 passed）
```
回歸網重點：`test_hf4_paragraph_breaks_normalized`（F 改 regex 後純段落升級仍須成立）、`test_p3_alt_aligned_no_caption_segment_no_header`（B 改 alt 後仍無 `*圖表：*` 段）、`test_hf1_*`（F1 去回聲不受影響）。

### §5 SOP 核查（BE-Hotfix 強制）
```bash
grep -nE "traceback.format_exc|logger\.error" pipelines/slide_pipeline.py   # 預期：無命中
grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v session.begin # 預期：無命中
```

### 2. 本地 E2E 快速復現與驗證（baron、非 commit）
1. 影子重傳 `Ch37_Plant-Nutrition.pdf` → ① p29/p35/p37 等圖密集頁**整頁截圖正常顯示**、無破圖、無長描述洩漏正文（B）；② 各頁**無 `4/28/2026`**（E）；③ 條列**緊湊、item 間無多餘空行**（F）。

### ⚠️ 行為變更 + golden
B/E/F 均改 B 軌 `final_zh`/`final_en` 輸出 → **衝擊 slides golden**。slides golden 尚未首捕（前 HOTFIX-1/1b 已宣告待首捕）→ **維持原計畫：本 HOTFIX-2 落地後一次首捕**（`venv/bin/python tools/golden_baseline.py capture slides --force`、免捕多次）。

---

## 回退與備案

```bash
git revert <HOTFIX-2 hash>          # 單 commit 可逆（B/E/F 三點互不依賴、整體 revert 安全）
# 或還原 .bak：
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-2_slide_pipeline.py.bak
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-2_test_slide_pipeline.py.bak
# 備案：E 若誤洗真內容日期（罕見）→ 收緊為 ≥3 頁門檻；F 若仍有邊界 → 條列前瞻再補符號
```

---

## 範圍註記（誠實邊界）

- **A（多頁重複標題「植物營養」）撤案**：原稿章節分隔頁本就重複大標題，忠實轉錄正確、去重反不忠實——非 bug、不處理（baron 拍板）。
- **C（封面 metadata 進結構化 DB）/ D（小標題 subtitle 抓取）**：屬 Vision schema 擴欄、動 prompt 輸出，**不在本 hotfix**；B 修好後 C 之可見症狀（圖說洩漏）已消、reading view 乾淨；D 留 HOTFIX-3（或 schema plan）獨立處理。
- 本 hotfix **零 Vision prompt 改動**（純渲染/清洗層）→ 與 D 的 schema 改動風險隔離。

---

## commit message 草稿（落地時寫入 /tmp/PIPE-SLIDES-HOTFIX-2_msg.txt）

```
BE-Hotfix: PIPE-SLIDES HOTFIX-2 — alt 破圖 / 母片重複日期 / F4 條列鬆散（B+E+F）

baron 學術簡報實件（Ch37_Plant-Nutrition）逐頁分析，單檔三點純渲染/清洗修：
- B _safe_alt：alt 內 ][() 轉全形、換行轉空白 → 根除 CommonMark ![alt](url) 之 ]
  提前閉合致破圖 + 描述洩漏正文（圖密集頁 p29/35/37 缺圖之真因；HOTFIX-1 U8
  alt 對齊暴露此轉義缺口）
- E _strip_master_date：原稿母片日期欄位（4/28/2026 烙進 20/20 頁、非投影片內容）
  Vision 逐頁抄入 → P1 純日期行偵測 ≥2 頁直接洗（補 _dedupe_headers 格式變異漏網：
  4/28/2026 vs 2026/4/28 各變體 <60% 門檻全躲過）
- F _normalize_paragraph_breaks list-aware：修 HOTFIX-1 F4 回歸——單 \n→\n\n 升級
  未排除條列行致 tight list 炸成 loose list（item 間空行醜排）；追加「下一行為
  - * + • 數字.」負向前瞻、條列維持緊湊、段落仍正規化
- A 重複標題撤案（忠實轉錄非 bug）；C/D Vision schema 留後話
- 補 3 回歸測試；⚠️ 改 B 軌輸出 → slides golden 本 hotfix 後一次首捕

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
