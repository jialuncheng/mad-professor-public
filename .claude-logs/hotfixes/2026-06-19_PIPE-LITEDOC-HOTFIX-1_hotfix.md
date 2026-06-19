# PIPE-LITEDOC-HOTFIX-1 — 緊急熱修復：litedoc 標題/Meta 重複 + 日文/簡體未翻譯

> **警示**：本文件為 **BE-Hotfix** 紀錄（doc 階段、**程式碼 diff 已寫入本文件、實檔未改、待 Run**）。
> **修復原則**：只改 `pipelines/litedoc_pipeline.py` + `pipelines/section_engine.py` 兩受災/共用檔，嚴禁夾帶無關功能。
> **依據**：`templates/template_hotfix.md` / `ref/WORKFLOW_SOP.md`（§1.5 BE-Hotfix + §5 SOP 核查）/ `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.3 logging / §4.4 database）

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-1** | `待 baron 回填` | BE-Hotfix: PIPE-LITEDOC-HOTFIX-1 — litedoc 標題回聲剝除 + P1 二元繁中偵測（日文/簡體轉繁） |

---

## §0 定性與範圍

| 維度 | 內容 |
|---|---|
| 工作流 | BE-Hotfix（後端業務邏輯、非計畫性）|
| 動因 | litedoc 落地後 baron QA 三實件（LLM 知識庫 / 環義 Giro / 大谷 NHK + book 封面 I and Thou）暴露雙缺陷 |
| 受災檔 | `pipelines/litedoc_pipeline.py`（P1 偵測 / P3 還原）+ `pipelines/section_engine.py`（共用：新增偵測器 + 剝回聲 helper）|
| 不碰 | A 軌 / rag_indexer / contracts.py / 其他策略管線本體（resume/slide：僅共用 gate 語意不變，見 §不可動）|
| 階段 | **doc-only**：本文件含完整 diff、實檔未改、含 commit 草稿、存 baton 待 Run |

---

## 阻斷性問題與真因

### 問題一：標題與 Meta 重複（全 litedoc、與語言無關）

#### 1. 現象（LLM 知識庫 / Giro 圖）
繁中閱讀視圖開頭出現**兩套標題＋Meta**：
- **第一套**：P3 顯式 prepend 的置中 HTML 扉頁（`# 標題` + `<div class="paper-header-meta">` 作者/日期）。
- **第二套**：body 自身的靠左 H1（如 `# 2026年環義大利賽…`）＋緊接的 byline 行（`由 Rúben Silva 撰寫，2026年5月16日…`）。

（連同前端閱讀視圖 chrome 顯示的 `Paper.title`，畫面實為**三處標題**——chrome / 扉頁 / body H1。）

#### 2. 真因（Root Cause）
- `full_text` 直接讀整份 MinerU markdown（含文章自身起首標題行）：
  - 定位：[litedoc_pipeline.py:441 `full_text = self._read_source_text(ctx)`](pipelines/litedoc_pipeline.py:441) → [:349 讀 `{pdf_stem}.md`](pipelines/litedoc_pipeline.py:349)
- P3 在 body **前面** prepend `# {translated_title}` + 扉頁、但**全程無去標題回聲機制**：
  - 定位：[litedoc_pipeline.py:498 `zh_text = header_zh + zh_text`](pipelines/litedoc_pipeline.py:498) / [:546 扉頁含 `# 標題`](pipelines/litedoc_pipeline.py:546)
- **grep 證**：litedoc 全檔無 body 去標題機制（[:265 `lstrip("#")`](pipelines/litedoc_pipeline.py:265) 只用於 `_resolve_title` 讀取、非剝除）。對比 A 軌 md_restore 有標題三軸融合/黑名單（[`_title_in_blacklist`:46](processor/md_restore_processor.py:46) / [`_title_sim`:59](processor/md_restore_processor.py:59)）；slides 有 `_strip_title_echo`；litedoc 兩者皆無。

#### 3. blast radius 界定（重要）
RAG **不**受扉頁污染——`rag_sections` 在 header prepend **之前**就建好（[:476/484 早於 :498](pipelines/litedoc_pipeline.py:476)）→ 扉頁不進 chunk。**問題一是純閱讀視圖渲染缺陷**，修法只動 reading-view 組裝、不碰 RAG 旁路、不需重嵌。

---

### 問題二：日文/簡體未翻譯（語系誤判）

#### 1. 現象（大谷 NHK 圖）
日文新聞除頂部 `(測試)` 後綴外，**扉頁標題 / 正文 / 日期全是日文**，完全未譯成繁中。

#### 2. 真因（Root Cause）
- `_detect_source_lang` **只數共用漢字區 `一–鿿`（一–鿿）**，而**日文漢字與中文漢字共用此 Unicode 區塊**：
  - 定位：[litedoc_pipeline.py:271 `cjk = sum(... if "一" <= ch <= "鿿")`](pipelines/litedoc_pipeline.py:271)
  - 日文假名（`぀–ヿ`）不在漢字區、亦非 ASCII letters → **不計入任何一邊** → 高漢字日文 `cjk ≥ 20 且 cjk ≥ letters*0.2` 成立 → **誤判 `"zh"`**。
- 誤判後觸發**雙重跳譯 gate**（grep 證二者同吃 `source_lang`）：
  - [P3 :439 `is_zh = source_lang.startswith("zh")`](pipelines/litedoc_pipeline.py:439) → [:455 `zh_text = full_text`](pipelines/litedoc_pipeline.py:455)（正文不譯、標題不譯）
  - [P2 section_engine:122 `if source_lang.startswith("zh"): return 原文`](pipelines/section_engine.py:122)（**節點摘要也不譯** → 灌進 RAG chunk 的 Chapter Summary 是日文）
- **連帶潛在 bug（簡體）**：`_detect_source_lang` 對**簡體中文**同樣回 `"zh"` → bypass → 簡體原封輸出、**不轉繁中**（系統目標語為 zh-tw）。

#### 3. blast radius 界定
問題二比表象大——**不只閱讀視圖未譯，P2 節點摘要亦未譯 → RAG 召回品質連帶劣化**。但兩道 gate **同讀 `source_lang`** → **在 P1 源點判對、即一次解 P2+P3**（不必逐路 plumb）。

---

## 設計決策（多輪分析收斂、含三鎖）

### OQ(a) 二元判斷走純啟發式 vs LLM 一欄 → **拍板：純啟發式（零 LLM）**
- 收斂為二元「**是不是繁中（is_zh_tw）**」：bypass 旁路存在的唯一理由就是「原文已繁中」；其餘（en/ja/ko/**简**）一律譯成繁中。
- 繁/簡是唯一難點，靠**高頻簡體專有字**（们/这/个/国/会/与/东/义/业/应…）命中即斷簡；ja 靠假名、ko 靠諺文、en 靠 ASCII 佔比——Regex < 1ms、零 API 抖動、可純函式單測。
- **非對稱容錯**：誤判「非繁」→ 重譯繁→繁（近冪等、僅費 token）；誤判「繁」→ 非繁原封漏譯（即本 bug）。故**存疑一律譯、只在高信心繁中才 bypass**。

### 🔒 鎖一（關鍵實作契約）：簡體**絕不可**給 `zh*` 字串
grep 證**四處** gate 都是 `startswith("zh")`：[litedoc:439](pipelines/litedoc_pipeline.py:439) / [section_engine:122](pipelines/section_engine.py:122)〔共用〕/ [resume:537](pipelines/resume_pipeline.py:537) / [slide:708](pipelines/slide_pipeline.py:708)。
→ 若簡體編成 `"zh-cn"`/`"zh-hans"`，`"zh-cn".startswith("zh")==True` → **四 gate 全部又把簡體當繁中 bypass、bug 復活**。
**契約**：P1 吐的 `source_lang` 只有**繁中＝`"zh"`**；簡體/ja/ko/en 一律給**非 `zh` 前綴** token（本案用 `"hans"`/`"ja"`/`"ko"`/`"en"`，皆不 startswith `"zh"`）。→ **四個既有 gate 一字不改**即全對。

### 🔒 鎖二（架構歸屬）：偵測器放 `section_engine` 共用
`I and Thou` 是 **book**、非 litedoc；resume/slide/litedoc 各有一份 source_lang 偵測 + 都餵進共用 section_engine gate。偵測邏輯若埋進 litedoc，book/academic 將各自重造 → 違反共用真理源家族。
→ 新增 `section_engine.detect_zh_tw()`（純函式、零 doc_type/A 軌耦合），各路 P1 呼叫、口徑一致。

### 🔒 鎖三（取樣不取封面）：`I and Thou` 封面無語境
封面頁（標題/作者/年份）看不出內文語言。→ 偵測**取內文樣本**：**按 tiles 文字節點**（非 raw 字元 offset、避開圖片/URL 區塊）、跳前段封面、短文兜底取整篇。

### OQ(b) 扉頁保留 vs 廢除 → **拍板：保留扉頁 + 原文層剝標題回聲**
- 理由（**已校正**）：① 前端 chrome 已顯 `Paper.title`、扉頁提供作者/出處/日期的**視覺分層**；② 與 academic-family **共用 `paper-header-meta` 結構**（grep 證 `render_meta_header_html` 本就 [section_engine:481「byte 對齊 A 軌」](pipelines/section_engine.py:481)、A 軌 academic header 即同一 [`<div class="paper-header-meta">`:md_restore:480](processor/md_restore_processor.py:480)）。
- **不採**原分析「對齊 A 軌 golden 0%」之理由——專案口徑（SPEC §1.3.1 / PIPE-SLIDES-HOTFIX-6）已釘 **B 軌走影子 E2E + 改善豁免、非 0% 硬 gate**。
- 剝回聲**必在原文層（翻譯前）**：譯後 body H1 ≠ 原 title 字串、post-string-match 會漏剝；複用 `_title_sim` 模糊比對（容標點/空白）、找**首個 ≈ title 的標題行**（非盲剝 line 1）、連 byline/日期一起（cap 1~3 行）。

---

## 熱修復修法（Minimal Hotfix · 程式碼 diff）

> 所有新增以 `# === [PIPE-LITEDOC-HOTFIX-1 START/END] ===` 包裹；改前產 `.bak`（兩檔）。

### F1 ── `pipelines/section_engine.py`：新增共用「二元繁中偵測」+「剝標題回聲」純函式

```diff
@@ pipelines/section_engine.py  （模組級、緊接 import 區後）@@
+# === [PIPE-LITEDOC-HOTFIX-1 START] 共用語系偵測 + 標題回聲剝除（零 doc_type / 零 A 軌耦合）===
+import re as _re  # 若檔頭已 import re 則複用、不重複
+from difflib import SequenceMatcher as _SM
+
+# 高頻「簡體專有字」（與繁中字形不同；命中即非繁中）。刻意不含繁簡同形字（如「的」）。
+_SIMPLIFIED_MARKERS = set("们这个国会与东义业应对话说时实発门问题战节单类")
+_KANA = (0x3040, 0x30FF)        # 平假名 + 片假名 → 日文
+_HANGUL = (0xAC00, 0xD7A3)      # 諺文 → 韓文
+_CJK = (0x4E00, 0x9FFF)         # CJK 統一表意（中日韓共用）
+_ZH_TW_MIN_CJK = 8              # 樣本中至少這麼多漢字才談繁中
+_SIMP_HIT_THRESHOLD = 1         # 命中 ≥1 個簡體專有字 → 判簡（非繁）
+
+
+def detect_zh_tw(sample: str) -> bool:
+    """二元判斷：sample 是否「已是繁體中文」（高信心才 True；存疑一律 False＝需翻譯）。
+
+    判準（任一不成立即非繁）：含 CJK 且漢字達門檻、無假名、無諺文、無簡體專有字、非 ASCII 主導。
+    純函式、零 doc_type/A 軌耦合；供五路 P1 共用（litedoc/book/academic…）。
+    """
+    if not sample:
+        return False
+    kana = hangul = cjk = ascii_letters = simp = 0
+    for ch in sample:
+        o = ord(ch)
+        if _KANA[0] <= o <= _KANA[1]:
+            kana += 1
+        elif _HANGUL[0] <= o <= _HANGUL[1]:
+            hangul += 1
+        elif _CJK[0] <= o <= _CJK[1]:
+            cjk += 1
+            if ch in _SIMPLIFIED_MARKERS:
+                simp += 1
+        elif ch.isascii() and ch.isalpha():
+            ascii_letters += 1
+    if kana or hangul:            # 日文/韓文 → 非繁
+        return False
+    if simp >= _SIMP_HIT_THRESHOLD:  # 簡體專有字 → 非繁（簡）
+        return False
+    if cjk < _ZH_TW_MIN_CJK:       # 漢字太少（en/西文/封面無語境）→ 非繁
+        return False
+    if ascii_letters > cjk * 3:    # ASCII 主導 → 非繁（en）
+        return False
+    return True                    # 高信心繁中 → 可 bypass
+
+
+def classify_source_lang(sample: str) -> str:
+    """P1 用：回傳 source_lang token。**繁中＝'zh'；其餘一律非 'zh' 前綴**（鎖一契約）。
+
+    回傳 ∈ {'zh'(繁), 'hans'(簡), 'ja', 'ko', 'en'}；下游 startswith('zh') gate 僅繁中 bypass。
+    """
+    if detect_zh_tw(sample):
+        return "zh"
+    if any(_KANA[0] <= ord(c) <= _KANA[1] for c in sample):
+        return "ja"
+    if any(_HANGUL[0] <= ord(c) <= _HANGUL[1] for c in sample):
+        return "ko"
+    if any(c in _SIMPLIFIED_MARKERS for c in sample):
+        return "hans"   # ⚠️ 不可寫 'zh-cn'/'zh-hans'（會被 startswith('zh') 誤 bypass）
+    return "en"
+
+
+def sample_body_text(
+    tiles: List[Dict[str, Any]], *, skip_head_ratio: float = 0.15, sample_chars: int = 800
+) -> str:
+    """鎖三：自 tiles **文字節點**取內文樣本（跳前段封面、非 raw 字元 offset）。
+
+    短文兜底：可用文字不足時退整篇正文。供語系偵測，避開圖片/URL/封面干擾。
+    """
+    texts: List[str] = []
+    for sec in tiles or []:
+        if isinstance(sec, dict):
+            for item in sec.get("content", []) or []:
+                if isinstance(item, dict) and item.get("type") == "text":
+                    t = str(item.get("content", "")).strip()
+                    if t:
+                        texts.append(t)
+    body = "\n".join(texts)
+    if len(body) <= sample_chars:        # 短文兜底：整篇
+        return body
+    start = int(len(body) * skip_head_ratio)
+    return body[start:start + sample_chars]
+
+
+def _title_echo_match(a: str, b: str) -> bool:
+    """標題相似（複用 A 軌 _title_sim 範式、但 section_engine 自帶不 import A 軌）。"""
+    if not a or not b:
+        return False
+    A = _re.sub(r"\s+", "", a).casefold()
+    B = _re.sub(r"\s+", "", b).casefold()
+    if A == B or A in B or B in A:
+        return True
+    return _SM(None, A, B).ratio() >= 0.7
+
+
+def strip_title_echo(markdown_text: str, title: str, *, cap: int = 3) -> str:
+    """**原文層（翻譯前）** 剝除 body 起首與 title 同源的標題回聲 + 緊隨 byline/日期行。
+
+    僅在前 cap 個「非空行」內找首個 ≈ title 的標題行（# 開頭或純標題行）；命中則連同
+    其後 1~2 行 byline/日期（含 '撰寫'/'By'/日期樣式）一併剝除。找不到則原樣返回（不誤剝）。
+    """
+    if not markdown_text or not title:
+        return markdown_text
+    lines = markdown_text.splitlines()
+    out: List[str] = []
+    seen = 0
+    i = 0
+    stripped = False
+    while i < len(lines):
+        ln = lines[i]
+        s = ln.strip()
+        if not stripped and s:
+            seen += 1
+            head = s.lstrip("#").strip()
+            if seen <= cap and _title_echo_match(head, title):
+                # 命中標題回聲 → 跳過此行 + 緊隨 1~2 行 byline/日期
+                i += 1
+                skipped = 0
+                while i < len(lines) and skipped < 2:
+                    nxt = lines[i].strip()
+                    if nxt and (_re.search(r"撰寫|報導|By\b|\d{4}[-/年]", nxt)):
+                        i += 1
+                        skipped += 1
+                    else:
+                        break
+                stripped = True
+                continue
+            if seen >= cap:
+                stripped = True  # 過了前 cap 行還沒命中 → 停止偵測（不誤剝下文）
+        out.append(ln)
+        i += 1
+    return "\n".join(out)
+# === [PIPE-LITEDOC-HOTFIX-1 END] ===
```

> 並將既有 [section_engine.py:122 `translate_section_summaries` 的 `startswith("zh")`](pipelines/section_engine.py:122) **保持不動**——鎖一契約下 P1 已保證簡體不給 `zh*`、此 gate 語意自動正確（resume/slide 亦不受影響）。

### F2 ── `pipelines/litedoc_pipeline.py` P1：改用共用偵測器（鎖一/二/三）

```diff
@@ pipelines/litedoc_pipeline.py  run_phase1 @@（約 L166-168）
         meta = self._extract_litedoc_metadata(markdown_text)
         title = self._resolve_title(meta, markdown_text, paper_name)
-        source_lang = self._detect_source_lang(markdown_text)
+        # === [PIPE-LITEDOC-HOTFIX-1 START] 二元繁中偵測（取內文樣本不取封面；簡體不給 zh* 契約）===
+        _sample = section_engine.sample_body_text(tiles) or markdown_text[:2000]
+        source_lang = section_engine.classify_source_lang(_sample)  # 繁→'zh'、其餘非 zh
+        # === [PIPE-LITEDOC-HOTFIX-1 END] ===
         publisher = str(meta.get("publisher") or "").strip()
```

> 舊 `_detect_source_lang`（[:269](pipelines/litedoc_pipeline.py:269)）保留為**降級 fallback**：可改 `classify_source_lang` 內 LLM 缺席時的後備，本案純啟發式不依賴它、但不刪除（向後相容、零風險）。

### F3 ── `pipelines/litedoc_pipeline.py` P3：**雙剝**標題回聲（pre full_text + post zh_text，覆蓋 whole/section/is_zh 全模式）

> **時序設計（修正：原 v1 單剝 full_text 在 section 模式無效）**：`zh_text` 來源因模式而異——whole/is_zh 來自 `full_text`、**section 來自 `ctx.ingestion.tiles`（不經 full_text）**。故採**雙剝**：
> - **pre-strip `full_text`**（原文層、翻譯前）：以**原標題** exact 比對 → 負責 `en_text`（全模式、`en_text=full_text`）+ `zh_text`（whole/is_zh、由 full_text 翻出）。
> - **post-strip `zh_text`**（還原後、prepend 扉頁前）：以**譯後標題** `translated_title` 比對 → 補 **section 模式**（zh_text 由 tiles 重建、pre-strip 無效）；該模式 `translated_title`＝頂層 title slot 譯後、body H1＝同 slot 還原 → **同一份譯文、exact**。
>
> 此雙剝使**每個模式都落在 exact 比對**（en/whole/is_zh 用原文、section 用同 slot 譯文），**無任一模式依賴 whole 模式那種「translate_unit vs translate_whole 兩獨立譯文」的發散模糊比對**。

```diff
@@ pipelines/litedoc_pipeline.py  run_phase3 @@（① pre-strip：約 L441-442，讀 full_text 後）
         sections = (ctx.ingestion.tiles if ctx.ingestion else []) or []
-        full_text = self._read_source_text(ctx)
+        full_text = self._read_source_text(ctx)
+        # === [PIPE-LITEDOC-HOTFIX-1 START] ① pre-strip：原文層剝回聲（en 全模式 + zh whole/is_zh，exact）===
+        _title_bare = ((ctx.ingestion.title if ctx.ingestion else "") or "").replace(" (測試)", "").strip()
+        full_text = section_engine.strip_title_echo(full_text, _title_bare)
+        # === [PIPE-LITEDOC-HOTFIX-1 END] ===
         title = (ctx.ingestion.title if ctx.ingestion else "") or ""
```

```diff
@@ pipelines/litedoc_pipeline.py  run_phase3 @@（② post-strip：約 L488-491，還原後、扉頁 prepend 前）
         en_text = full_text
         ctx.rag_sections = rag_sections
 
+        # === [PIPE-LITEDOC-HOTFIX-1 START] ② post-strip：補 section 模式（zh_text 由 tiles 重建、譯後標題 exact）===
+        zh_text = section_engine.strip_title_echo(zh_text, (translated_title or "").replace(" (測試)", "").strip())
+        # en_text 已由 ① pre-strip 處理（=full_text）；此處不重複剝
+        # === [PIPE-LITEDOC-HOTFIX-1 END] ===
+
         # ⑥ translated_title handoff → P4（既有 raw_metadata 旁路、PIPE-SLIDES-HOTFIX-1b 三欄 dict 範式）
         ctx.raw_metadata["translated_title"] = {
             "value": translated_title or title, "source": "litedoc_p3", "confidence": "high",
         }
```

> **RAG 隔離不變**：`rag_sections` 在 [:489 `ctx.rag_sections = rag_sections`](pipelines/litedoc_pipeline.py:489) 即定、**早於** ② post-strip 與扉頁 prepend → 兩剝皆不影響已收集之 rag_sections（扉頁不進 chunk、body 標題去留對 chunk 無害）。
> **設計取捨記錄**：baron 提案純 post-restore（單剝 zh_text/en_text）可覆蓋全模式且代碼最簡，但 whole 模式以 `translated_title`(translate_unit) 剝 body H1(translate_whole) 屬**兩獨立譯文模糊比對**、有漏剝風險；本案改 **pre+post 雙剝** 使每模式 exact、僅多 1 行 ①、消除該風險（採 baron 時序後移之核心 + 補原文層精確性）。

---

## §5 SOP 一致性核查（BE-Hotfix 強制）

### §5.1 logging 核查
```bash
grep -nE "logger\.(error|warning|exception)|traceback\.format_exc" pipelines/litedoc_pipeline.py pipelines/section_engine.py
# 規則：本 hotfix 新增碼**無新增 logger.error**；soft-fail 沿用既有 logger.warning(..., exc_info=True) 範式。
# 既有命中（如 litedoc P1 metadata soft-fail :252）皆已 exc_info=True、合規。
```
新增之 `detect_zh_tw`/`classify_source_lang`/`sample_body_text`/`strip_title_echo` 為**純函式、不拋例外、無 logging**（存疑回 False/原樣、非致命）→ 無 logging SOP 違規面。

### §5.2 database 核查
```bash
grep -nE "\.commit\(\)" pipelines/litedoc_pipeline.py pipelines/section_engine.py | grep -v "with .*session.*begin"
# 預期：無命中（合規）——本 hotfix 零 DB 操作（純文字偵測 / markdown 字串處理）。
```

---

## 不可動清單

- [ ] **A 軌**（`pipeline_core.py` / `processor/md_restore_processor.py` 等）— 不碰（`_title_sim` 僅參照範式、section_engine 自帶實作、零 import）。
- [ ] **`rag_indexer` / `contracts.py` 四凍結合約** — 零碰（問題一不污染 RAG、問題二僅改 source_lang 值域）。
- [ ] **`resume_pipeline.py` / `slide_pipeline.py` 本體** — 不碰；共用 `section_engine` 既有 gate（`startswith("zh")`）語意**不變**（鎖一保證簡體不給 zh*、繁中仍 'zh'）。
- [ ] **`render_meta_header_html` / 扉頁結構** — 不碰（OQ-b 保留扉頁）。
- [ ] **主 repo 目錄** — 嚴禁讀寫。

---

## regression 預防與 E2E 驗證（Run 階段執行、本 doc 列方向）

### 1. 新增單元測試（純函式、可離線）
```bash
$ venv/bin/python -m pytest tests/test_litedoc_pipeline.py tests/test_section_engine.py -v
```
- `test_detect_zh_tw_traditional` — 純繁中樣本 → True。
- `test_detect_zh_tw_japanese_kana` — 含假名日文 → False（修問題二）。
- `test_detect_zh_tw_simplified` — 含簡體專有字 → False（修簡體 bypass 潛在 bug）。
- `test_detect_zh_tw_english` — ASCII 主導 → False。
- `test_classify_never_returns_zh_prefix_for_nonzh` — **鎖一**：ja/ko/簡/en 之回傳皆 `not startswith("zh")`（堵四 gate 復活）。
- `test_sample_body_text_skips_cover` — 封面稀疏 + 後段繁中正文 → 取到正文（鎖三、防 I and Thou 誤判）。
- `test_strip_title_echo_removes_first_heading` — body 首行=title → 剝；非 title 行 → 不誤剝；byline/日期連帶剝。
- `test_strip_title_echo_original_layer` — 譯前比對（title=原文）能命中（非譯後字串）。
- `test_p3_dedup_whole_mode` — whole（<15k）：pre-strip full_text → zh/en body 無標題回聲、扉頁唯一。
- `test_p3_dedup_section_mode` — **section（≥15k）：post-strip zh_text（同 slot 譯文 exact）→ 去重生效**（堵原 v1 漏洞）。
- 回歸：真繁中 litedoc 仍 `is_zh` 跳譯不退化；en litedoc 仍正常翻譯；雙剝對「body 無標題回聲」之文件空轉不誤刪正文。

### 2. baron 影子 E2E（非 commit）
- 重傳大谷 NHK（日文）→ 扉頁/正文/節點摘要**皆繁中**、`source_lang=ja`、log `mode=whole/section`（非 zh）。
- 重傳簡體樣本 → 轉繁中（不再原封）。
- 重傳 LLM 知識庫 / Giro → **標題只剩扉頁一處**、body 無重複 H1 + byline；真繁中件仍 bypass。
- golden：B 軌改動**走影子 E2E + 改善豁免、不需 A 軌 golden 重捕**（SPEC §1.3.1 / HOTFIX-6 口徑）。

---

## §8 baron 執行命令（Run 階段）

```bash
# 1. 改前備份（兩受災檔）
cp pipelines/litedoc_pipeline.py .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_litedoc_pipeline.py.bak
cp pipelines/section_engine.py   .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_section_engine.py.bak

# 2. 套用 F1/F2/F3 diff + 補單元測試（見上）後驗證
venv/bin/python -m pytest tests/test_litedoc_pipeline.py tests/test_section_engine.py -v
venv/bin/python -m pytest tests/ -q   # 全套件不退化（686 基線）

# 3. SOP §5 grep（貼回執行報告）
grep -nE "logger\.(error|warning)" pipelines/litedoc_pipeline.py pipelines/section_engine.py
grep -nE "\.commit\(\)" pipelines/litedoc_pipeline.py pipelines/section_engine.py | grep -v "with .*session.*begin"

# 4. git add（業務碼 + 測試 + 兩 .bak；hotfix 文件與執行報告依收官鐵律處理）
git add pipelines/litedoc_pipeline.py pipelines/section_engine.py
git add tests/test_litedoc_pipeline.py tests/test_section_engine.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_section_engine.py.bak

# 5. commit message 草稿（/tmp/PIPE-LITEDOC-HOTFIX-1_msg.txt）
cat > /tmp/PIPE-LITEDOC-HOTFIX-1_msg.txt << 'EOF'
BE-Hotfix: PIPE-LITEDOC-HOTFIX-1 — litedoc 標題回聲剝除 + P1 二元繁中偵測（日文/簡體轉繁）

兩缺陷（同檔、互不耦合）：
1. 標題與 Meta 重複（全 litedoc）：body 自身標題 H1 與 P3 HTML 扉頁物理共存、litedoc 無去回聲機制。
   修：section_engine.strip_title_echo（複用 _title_sim 範式、剝首個 ≈title 標題行 + byline/日期）；P3 **雙剝**——① pre-strip full_text（原文層、en 全模式 + zh whole/is_zh exact）② post-strip zh_text（還原後、補 section 模式、同 slot 譯文 exact）→ 扉頁成唯一標題、每模式 exact。RAG 不受影響（rag_sections 早於兩剝定案、扉頁不進 chunk）。
2. 日文/簡體未翻譯：_detect_source_lang 僅數共用漢字區 → 日文誤判 zh → P3 is_zh + P2 section_summaries 雙 gate 跳譯；簡體亦誤 bypass 不轉繁。
   修：P1 改用 section_engine.classify_source_lang（二元「是不是繁中」、取 tiles 內文樣本不取封面）。

三鎖：
- 鎖一：簡體絕不給 zh* 字串（四處 startswith("zh") gate 復活風險）→ 非繁回 ja/ko/hans/en、四 gate 零改。
- 鎖二：偵測器放 section_engine 共用（book/academic 將共用）。
- 鎖三：取 tiles 文字節點樣本、跳封面、短文兜底（解 I and Thou 封面無語境）。

扉頁保留（OQ-b）：理由＝前端 chrome 分層 + academic-family 共用 paper-header-meta 結構（非 A 軌 golden 0%）。
SOP：logging 無新增 error/純函式無 logging；database 無命中（合規）。零碰 A 軌/rag_indexer/contracts/resume/slide 本體。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 6. baron 手動 commit
git commit -F /tmp/PIPE-LITEDOC-HOTFIX-1_msg.txt
```

---

## 回退與備案

```bash
# 自 .bak 還原兩受災檔（純函式新增 + P1/P3 三 hunk、可逆）
cp .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_litedoc_pipeline.py.bak pipelines/litedoc_pipeline.py
cp .claude-logs/archive/2026-06-19_PIPE-LITEDOC-HOTFIX-1_section_engine.py.bak   pipelines/section_engine.py
# 或 commit 後：
git revert <HOTFIX-1 hash>
```

---

### 結論
litedoc 雙缺陷同檔、互不耦合、最小侵入：**問題二**＝P1 二元繁中偵測（section_engine 共用、取內文樣本、簡體不給 zh* 契約、一次解 P2+P3 雙 gate）；**問題一**＝原文層剝標題回聲（扉頁保留為唯一標題、RAG 不受影響）。doc-only、實檔未改、待 baron 下 Run。
