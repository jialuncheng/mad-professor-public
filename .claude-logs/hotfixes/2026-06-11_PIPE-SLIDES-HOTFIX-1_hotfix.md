# PIPE-SLIDES HOTFIX-1 — 緊急熱修復：B 軌簡報實件三缺陷（同句多譯 / 譯題未接 / 段落黏連潛伏）

> 工作流類別：**BE-Hotfix**（必讀 logging_SOP + database_SOP；驗收=pytest 全通過 + §5 SOP 核查）
> 依據：PIPE-SLIDES C1-C7 收官後、baron A/B 軌同件實測（ST 簡報、2026-06-11 06:02 兩份列印實件）
> 決策：baron 拍板 **問題 1 選 C / 問題 2 選 B / 問題 3 選 C（接受、不修）/ 問題 4 移植 `_normalize_paragraph_breaks`**
> 受災檔：`pipelines/slide_pipeline.py`（單檔三點）+ `tests/test_slide_pipeline.py`（補測試）

---

## 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| HOTFIX-1 | `pipelines/slide_pipeline.py` 三修：F1 P1 物理去標題回聲（原文層、選 C）+ F2 P4 接譯題（複用 P3 既有封面譯題、選 B）+ F4 移植 `_normalize_paragraph_breaks`（pipe-table-safe）；F3 並列密度**顯式不修**（選 C、決策記錄）；補 4 回歸測試 | `待 baron 回填` |

---

## 阻斷性問題與真因

### F1. 同句多譯重複呈現（B 軌主要品質殘留）

**1. 現象（實件證據、B 軌列印版）**
- p1 封面：兩個近義標題並排——「適用於現代人工智慧資料中心 (AI Data Center) 的全面性供電…」＋「適用於現代 AI 資料中心 (Modern AI Data Center) 的完整電力傳輸解決方案…」。
- p6：「30 kW 三相維也納整流器」**同頁出現 3 次**（Three-Phase Vienna Rectifier ×2 大小寫變體 + three-phase ×1）。
- p8 LLC 轉換器 ×2、p16「我們的技術始於您／源自於您」×2。

**2. 真因（詳細）**
Vision 忠實轉錄鐵律（SPEC §1.3.1）要求「只忠實轉錄頁面實際出現的文字」→ 頁面大標題**物理上就在頁面上**，Vision 因此把它**同時**寫進 `title` 欄（prompt 要求抽標題）**和** `markdown_content` 首行（忠實轉錄正文）。P3 對 title／content 兩欄**各自獨立**送 Translator（不同 text_type 路由：title／content）→ 同一句原文得到**兩個略異譯文**，還原時 `## {zh_title}` 與正文首行相鄰渲染 → 視覺重複。×3 案例＝Vision 又把副標題行重抄一次（同機制疊加）。
本質＝**忠實轉錄（兩欄都對）與還原渲染（合起來重複）的接縫**——不是 Vision 錯、不是 Translator 錯，是兩欄合成時無去重。與 resume SHADOW-HOTFIX-2 doubling 同族。

**3. 為何選 C（P1 轉錄後物理去重、原文層）**
- 原文層比對**兩欄同源同字**（同一次 Vision 輸出）→ 幾乎精確匹配，遠比譯文層 fuzzy（兩次獨立翻譯、字面漂移）穩。
- 源頭修 → 閱讀視圖、`rag_sections`、chunk **三處同時乾淨**（P3 端去重只治閱讀視圖）。
- 物理確定、不依賴 LLM 遵守度（B 案 prompt 級的缺陷）。

### F2. translated_title 未接（前端列表顯示英文題 + (測試)）

**1. 現象**
B 軌實件檔名即證：`Comprehensive power delivery solution for modern AI data centers (測試)`——DB `translated_title` 缺、前端 fallback 原文題；A 軌同件顯示中文題。

**2. 真因（詳細）**
C5 落地時 `run_phase4` 註記「簡報譯後整份標題未另產 → title/translated_title 暫同取」。但事實上 **P3 已經翻譯了封面頁的 title**（`zh_fields[0][0]`＝封面題譯文、本實件 p1 第二個標題就是它）——譯文存在、只是沒有穿線到 P4 / 影子寫庫。屬「暫同取」技術債的直接償還。

**3. 為何選 B（複用 P3 既有譯題）**
- 譯文已存在 → **零增量 LLM**；只需旁路穿線（`ctx.raw_metadata` 先例、v9 已建）。
- A 案（P2 順產）要動合約傳遞、跨 Phase 工程大；C 案（不修）Flip 後不可接受。
- 影子寫庫端 `web_server` C8-hotfix/SHADOW-HOTFIX-2 已優先讀 `ctx.raw_metadata` 組 `metadata_json` 並補綴 `(測試)` → 旁路放入 `translated_title` 即自動流到 DB、**web_server 零改**。

### F3. 中英並列密度偏高 —— **顯式不修（選 C、決策記錄）**

**現象**：constraints 寫「首次出現並列」、實際每次出現都並列（p4 DC-DC 並列 ×8）。
**結構性根因**：P3 逐頁獨立並行翻譯、**頁間零記憶** → 「首次」跨頁無法定義，prompt 級約束注定部分失效。
**不修理由（baron 拍板）**：① RAG/BM25 召回受益（中英關鍵詞都進 chunk）；② 技術簡報讀者並列容忍度高；③ B 案 regex 去重誤殺風險＞收益。**列為觀察項**：若日後可讀性投訴，重啟 A 案（constraints 改「同頁內重複僅留中文」、以頁為界「首次」才可定義）。

### F4. 段落黏連潛伏（正文內部裸單 `\n`、soft break）

**1. 現象（潛伏、本實件未顯症）**
本實件正文多為 `1.` 編號與 `-` 條列（list 語法天然斷行）故未發病；**純文字連續行的頁**（架構圖標籤、敘述段）將黏成同段。

**2. 真因（詳細、碼證）**
CommonMark 規範：單 `\n`＝soft break（瀏覽器渲染為一個空格、同段）；須 `\n\n`（空行）才分段。B 軌還原三層：頁間 `"\n\n".join(zh_pages)`（L644 ✅）、同頁三塊間 `"\n\n".join(parts)`（L636 ✅）、**正文內部＝Vision 原樣裸單 `\n`、行尾無雙空格 ❌**。resume 同病已由 PARA-HOTFIX-1 修復（`_normalize_paragraph_breaks`、resume_pipeline.py L801 套用），**slides C4 落地時未移植**（grep 證 slide_pipeline.py 0 命中）。與 RAG-10／PARA-HOTFIX-1 同族病。

**3. 修法＝移植（不 import resume**、pipelines/ 內各策略私有重建原則**）**

---

## 熱修復修法 (Minimal Hotfix)

### `pipelines/slide_pipeline.py` — 三點最小改動（`# === [PIPE-SLIDES-HOTFIX-1 START/END] ===` 包裹）

#### F1：P1 物理去標題回聲（落點：`run_phase1` ④ units 構造、L161 前）

新增私有 helper（C2 區塊尾）：

```python
# === [PIPE-SLIDES-HOTFIX-1 F1 START] ===
@staticmethod
def _strip_title_echo(title: str, content: str) -> str:
    """P1 物理去標題回聲（問題 1 選 C、原文層）。

    Vision 忠實轉錄使頁大標題同時進 title 欄與 markdown_content 首行 →
    P3 兩欄各自翻譯 → 同句雙譯相鄰渲染（實件 p1/p6/p8/p16 實證、p6 ×3）。
    原文層比對（兩欄同源同字）：正規化（去空白/標點/lower）後 content 開頭
    連續行 ≈ title 即剔除（cap 2 行、防 ×3 案例之副標重抄）；正文其餘不動。
    """
    if not title or not content:
        return content
    def _norm(s: str) -> str:
        return re.sub(r"[\s\W]+", "", s).lower()
    t = _norm(title)
    if not t:
        return content
    lines = content.splitlines()
    stripped = 0
    while lines and stripped < 2:
        first = lines[0].strip()
        if not first:
            lines.pop(0); continue
        f = _norm(re.sub(r"^#+\s*", "", first))
        if f and (f == t or (len(f) >= 6 and (f in t or t in f))):
            lines.pop(0); stripped += 1
        else:
            break
    return "\n".join(lines).strip()
# === [PIPE-SLIDES-HOTFIX-1 F1 END] ===
```

units 構造處套用（原 L163-164）：

```python
            units.append({
                "page": n,
                "title": (r.get("title") or "").strip(),
                # === [PIPE-SLIDES-HOTFIX-1 F1] === 原文層去標題回聲（chunk/閱讀雙乾淨）
                "content": self._strip_title_echo(
                    (r.get("title") or "").strip(),
                    (r.get("markdown_content") or "").strip()),
                ...
```

#### F2：P4 接譯題（落點 ①：`_deliver` 正常路、L628 迴圈後；落點 ②：`run_phase4` L689）

`_deliver` 正常路（zh 來源與退化路不動——zh 原文即中文、退化無逐頁譯題）：

```python
            zh_text = "\n\n".join(zh_pages)          # U10：不渲染 meta header
            ctx.rag_sections = sections
            # === [PIPE-SLIDES-HOTFIX-1 F2 START] === 封面譯題穿旁路（問題 2 選 B、複用 P3 既有譯文零增量 LLM）
            # web_server 影子寫庫（C8-hotfix/SHADOW-HOTFIX-2）優先讀 ctx.raw_metadata 組
            # metadata_json 並補綴 (測試) → 此處放入即自動流到 DB、前端列表改顯中文題。
            cover_zh_title = zh_fields[0][0] if zh_fields else ""
            if cover_zh_title:
                ctx.raw_metadata["translated_title"] = cover_zh_title
            # === [PIPE-SLIDES-HOTFIX-1 F2 END] ===
```

`run_phase4`（原 L689 暫同取處）：

```python
        _title = (ctx.ingestion.title if ctx.ingestion else None) or ctx.paper_id
        # === [PIPE-SLIDES-HOTFIX-1 F2 START] === 譯題首選旁路（缺→暫同取向後相容）；
        # 影子後綴對齊：title 已含 (測試)、譯題同綴保 rag_tree 雙題一致
        _translated = ctx.raw_metadata.get("translated_title") or _title
        if ctx.paper_id.endswith("_shadow") and not _translated.endswith(" (測試)"):
            _translated = f"{_translated} (測試)"
        # === [PIPE-SLIDES-HOTFIX-1 F2 END] ===
        ...
            spec = rag_indexer.index(
                ...
                title=_title, translated_title=_translated,   # ← 原 translated_title=_title
            )
```

#### F4：移植 `_normalize_paragraph_breaks`（落點：新 helper + `_deliver` 兩處渲染套用）

helper（**逐字移植 resume PARA-HOTFIX-1 邏輯、pipelines/ 內私有重建、不 import resume/A 軌**）：

```python
# === [PIPE-SLIDES-HOTFIX-1 F4 START] ===
@staticmethod
def _normalize_paragraph_breaks(text: str) -> str:
    """段落邊界正規化（pipe-table-safe 單 \\n → \\n\\n；移植 resume PARA-HOTFIX-1、私有重建不跨策略 import）。

    真因：B 軌還原頁間/三塊間有 \\n\\n、但正文內部為 Vision 原樣裸單 \\n →
    CommonMark soft break 黏段（本實件多條列未顯症、純文字頁必發）。
    pipe table rows 之間單 \\n 保留（否則 table 渲染破碎）；進出 table 補空行邊界。
    """
    if not text:
        return text
    lines = text.split("\n")
    out_lines = []
    in_table = False
    for line in lines:
        is_table_row = bool(re.match(r"^\s*\|", line))
        if is_table_row:
            if not in_table and out_lines and out_lines[-1].strip():
                out_lines.append("")
            in_table = True
            out_lines.append(line)
        elif in_table:
            in_table = False
            if line.strip():
                out_lines.append("")
            out_lines.append(line)
        else:
            out_lines.append(line)
    text = "\n".join(out_lines)
    return re.sub(r"(?<!\|)(?<!\n)\n(?![\n\|])", "\n\n", text)
# === [PIPE-SLIDES-HOTFIX-1 F4 END] ===
```

套用兩處（zh／en 對稱）：

```python
# _deliver 正常路（原 L634-635）
                if zh_content:
                    parts.append(self._normalize_paragraph_breaks(zh_content))   # F4

# _page_source_md（en 版同病、原 L552-553）
        if (u.get("content") or "").strip():
            parts.append(SlidePipeline._normalize_paragraph_breaks(u["content"].strip()))   # F4
```

> 套用範圍註：`rag_sections` 的 merged text **不套**（chunk 對 soft break 無感、保原樣減少 diff 面）；條列/編號行不受影響（regex 只升級一般行、`|` 行保留）。

### `tests/test_slide_pipeline.py` — 補 4 回歸測試（`# === [PIPE-SLIDES-HOTFIX-1 START/END] ===`）

```python
def test_hf1_title_echo_stripped():
    """F1：content 首行（含 ×2 副標重抄）≈ title → 物理剔除；其餘正文不動。"""
    from pipelines.slide_pipeline import SlidePipeline
    c = SlidePipeline._strip_title_echo(
        "30 kW Three-Phase Vienna Rectifier",
        "30 kW three-phase Vienna rectifier\n30 kW Three-Phase Vienna Rectifier\n- spec A")
    assert c == "- spec A"
    # 非回聲首行不誤殺
    c2 = SlidePipeline._strip_title_echo("Agenda", "1. Infrastructure\n2. Grid to POL")
    assert c2.startswith("1. Infrastructure")

def test_hf2_translated_title_wired(monkeypatch, tmp_path):
    """F2：正常路封面譯題入 raw_metadata；run_phase4 傳 translated_title=譯題（非原文暫同取）。"""
    # 沿用既有 _run_p3 harness（FakeTranslator 譯文='譯'+原文）→
    # ctx.raw_metadata['translated_title'] == '譯' + 封面 title；
    # 再 mock rag_indexer.index 捕參斷言 translated_title 帶譯題 + 影子 (測試) 綴。

def test_hf4_paragraph_breaks_normalized(monkeypatch, tmp_path):
    """F4：純文字連續行 → final_zh 內升級 \\n\\n；pipe table rows 不拆散。"""
    # tiles content='今日\nAI 伺服器機櫃\n交流輸入' → final_zh 含 '今日\n\n'；
    # content 含 '| A | 1 |\n| B | 2 |' → 兩行間維持單 \n。

def test_hf1_rag_sections_no_echo(monkeypatch, tmp_path):
    """F1 下游驗證：rag_sections merged text 不含標題回聲（chunk 乾淨）。"""
```

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
```bash
venv/bin/python -m pytest tests/test_slide_pipeline.py -v   # 既有 24 + 新 4 全綠
venv/bin/python -m pytest tests/ -q                          # 全套件不退化（基準 580 passed）
```
既有 24 測試＝行為回歸網：`test_p3_alt_aligned_no_caption_segment_no_header`（F4 不得引入新段落破壞 alt 行）、`test_integration_p2_p3_p4_key_changing`（F1 改 content 不得動 key 契約——title 欄不動、`page_key` 不受影響）、`test_p1_cover_metadata_and_image_saved`（F1 不得吃掉封面 metadata）。

### §5 SOP 核查（BE-Hotfix 強制）
```bash
grep -nE "traceback.format_exc|logger\.error" pipelines/slide_pipeline.py   # 預期：無命中（本 hotfix 零新增 error 路）
grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v "session.begin"  # 預期：無命中（零 DB 寫）
```

### 2. 本地 E2E 快速復現與驗證（baron、非 commit）
1. 影子重傳同一份 ST 簡報 → B 軌列印對照本次實件：p1 單一標題、p6 標題僅 1 次、p8/p16 同；前端列表顯示**中文譯題 + (測試)**。
2. 找一頁純文字行（或構造）驗段落分行；pipe table 頁不破碎。
3. chat 引用仍顯「《簡報名》> p{N} 標題」（F1 不動 title 欄、key 不變）。

### ⚠️ 行為變更 + golden
F1/F4 改 B 軌 `final_zh`/`final_en` 內容與空行結構、F2 改 rag_tree translated_title → **衝擊 slides golden**。B 軌 slides golden 尚未首捕（PIPE-SLIDES Q8 排程中）→ **建議本 hotfix 落地後再首捕**（`venv/bin/python tools/golden_baseline.py capture slides --force`、一次到位、免捕兩次）。

---

## 回退與備案

```bash
# 單 commit 可逆
git revert <HOTFIX-1 hash>
# 或還原 .bak（修改前強制備份、隨 commit 入庫審計）：
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1_slide_pipeline.py.bak
#   .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1_test_slide_pipeline.py.bak
```
備案：F1 閾值若誤殺（首行恰為與標題近似的正文）→ 收緊為「完全相等（正規化後）」一檔即可、不需 revert 全件。

---

## commit message 草稿（落地時寫入 /tmp/PIPE-SLIDES-HOTFIX-1_msg.txt）

```
BE-Hotfix: PIPE-SLIDES HOTFIX-1 — B 軌簡報三缺陷（同句多譯/譯題未接/段落黏連）

baron A/B 軌同件實測（ST 簡報）發現三缺陷，單檔三點最小修：
- F1 P1 物理去標題回聲（選 C、原文層）：Vision 忠實轉錄使頁標題同入 title 欄與
  content 首行 → P3 兩欄各自翻譯 → 同句雙譯相鄰（實件 p1/p6×3/p8/p16）；
  _strip_title_echo 正規化比對剔除（cap 2 行）、閱讀視圖/rag_sections/chunk 三處同淨
- F2 P4 接譯題（選 B、零增量 LLM）：複用 P3 既有封面譯題穿 raw_metadata 旁路 →
  run_phase4 translated_title + 影子 (測試) 綴；償還 C5「暫同取」技術債、web_server 零改
- F4 移植 _normalize_paragraph_breaks（resume PARA-HOTFIX-1、私有重建不跨策略 import）：
  正文裸單 \n soft break 黏段潛伏 → pipe-table-safe 升級 \n\n、zh/en 對稱套用
- F3 中英並列密度顯式不修（選 C：BM25 召回受益、逐頁翻譯頁間零記憶致「首次」
  跨頁無法定義；列觀察項）
- 補 4 回歸測試；⚠️ 改 B 軌輸出 → slides golden 建議 hotfix 後一次首捕

Co-Authored-By: Claude Fable 5 (1M context) <noreply@anthropic.com>
```
