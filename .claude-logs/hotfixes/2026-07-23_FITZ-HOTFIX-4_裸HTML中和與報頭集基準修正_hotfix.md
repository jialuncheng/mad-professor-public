# FITZ-HOTFIX-4 — 緊急熱修復：裸 HTML 中和與報頭集行號基準修正

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正 FITZ-ANCHOR（`b48961a`…`38cb68e`）落地後兩份樣本 E2E 暴露之缺陷：Medium 技術文章 **95% 內容前端蒸發**（K1）＋ NHK 樣本 **en 側首圖誤殺**（K2）。
> **修復原則**：只改動受災點程式碼（`pipelines/litedoc_pipeline.py` 單檔＋測試），嚴禁夾帶任何無關的新功能或大型重構。
> **依據**：`templates/template_hotfix.md`／`ref/WORKFLOW_SOP.md` §1.5 BE-Hotfix（logging_SOP + database_SOP 必讀、pytest + §5 SOP 核查）／`ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §1.1 雙軌制・§4.2 執行報告契約。
> **設計定調（baron 2026-07-23 拍板、K1 之授權源）**：「**專案屬性就是處理 PDF——碰到 HTML 標籤應該就要當一般文字處理**」。輸入面不存在「合法 HTML」；全庫唯一有意之 raw HTML＝P3 自注入的扉頁 `paper-header-meta` div。
> **證據包**：`baton/litedoc_shadow_artifacts/Browsers_v1/`＋`Ohtani_v1/`（sidecar_v3／md_v3／processed_v3／tiled_v3／final_zh・en_v3）＋源／成品 PDF（gitignored 長駐審計）。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-4** | `[留空，由 baron 回填]` | BE-Hotfix: FITZ-HOTFIX-4 — Inline HTML Neutralization & Header-Srcs Basis Fix（裸 HTML 中和與報頭集行號基準修正） |

落地時（依 CLAUDE.md §1.3、Claude Code 不 commit）：
- commit message 草稿寫 `/tmp/FITZ-HOTFIX-4_msg.txt`
- `git add` 白名單（逐檔顯式、含 `.bak`）：`pipelines/litedoc_pipeline.py`／`tests/test_litedoc_pipeline.py`／對應 `.bak` ×2（archive/）

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

**現象 A（K1）**：Medium「How modern browsers work」（46 頁、83,339 字元）B 軌閱讀視圖／列印僅剩 **4 頁 4,363 字元（~5%）**。
**現象 B（K2）**：NHK 大谷樣本 v3——文字面 29/29 全勝後、**en 側首圖（1280×720 主視覺）消失**；log 實證 `[img-filter] DROP 規則③報頭區 src=images/page_0_9.png`（2026-07-23 18:16:47）。

- **受災範圍**：A＝**所有含字面 HTML 標籤之技術文章**（MDN／CSS-Tricks／技術部落格通案）、zh/en 雙側；B＝en 通道（`full_text` 路）之報頭區誤判。
- **管線無罪證明（A、關鍵）**：磁碟上 `final_..._shadow_zh.md`＝**22 個 heading、35,863 字元、en→zh 比率正常、內容完整**——蒸發發生在**前端渲染層**。

### 2. 真因診斷 (Root Cause)

**真因 A（K1）＝裸 `<script>` 吞文**：

1. 源文為瀏覽器原理文章、正文滿佈字面 `<script>`／`<link rel=…>`／`<img src=…>`（Medium 原文排為 inline code）；
2. **fitz 文字層抽取使 code 樣式蒸發**、只剩裸角括號；翻譯照抄（LLM 後段自行加了反引號、前段裸奔——一個裸標籤即滅團）；
3. 前端渲染：`<link>`／`<img>` 被消毒層**靜默拔除**（列印稿第 4 頁「遇到 ▢ 會促使」「而遇到 ▢ 則會觸發」兩個洞肉眼可見）；
4. 撞到首個裸 `<script>` 致命——HTML 解析把**其後全部內容當作 script 內文**（無閉合標籤）→ DOMPurify（SEC-XSS、正確運作）移除整個 script 元素**連同內文** → 31,000 字蒸發。
- **鐵證**：列印稿最後一詞「處理」；`final_zh` 同位置下一字＝`<script>`（`處理 <script> 標籤：…`）。
- **定位**：非單點 bug、屬**輸入面契約缺失**——PDF 抽出的角括號標籤未被宣告為字面文字。

**真因 B（K2）＝R8 報頭集「行號基準位移」**：

1. `_filter_source_figures`（R8、`full_text` 通道）內呼 `_load_header_srcs(ctx, output_dir, text)`——以 **sidecar 原封行號**（hdr_end）掃描**當下傳入的 text**；
2. 但 R8 執行時 `text` 已經過 **K3 刪行**（HOTFIX-3、剝 meta 行）——v3 實物：K3 刪掉 title 堆疊（行 0-4）＋date（行 6）→ **圖片行由第 8 行上移進 `[: hdr_end+1]=[:7]` 掃描窗** → 被誤收為報頭圖 → 規則③ DROP；
3. tiles 通道掃的是**原封 md**（圖在第 8 行、界外）→ 保留——兩通道基準不一致。
- **鐵證鏈**：`sidecar_v3.json`（title 0-4／publication_info 6／other 8＝圖）＋`md_v3.md` 行號地圖＋processed／tiled 皆含圖＋`final_en_v3.md` 第 6-10 行空洞＋單條③ log。
- **諷刺註**：HOTFIX-3 明文警告過「K3 行號位移陷阱」並把 K3 排在最前——堵了 K3 自己的輸入端、**漏了 R8 的邊界端**（同族錯誤第五例）。
- **定位程式碼**：`pipelines/litedoc_pipeline.py` `_filter_source_figures`（`_load_header_srcs(ctx, output_dir, text)` 之 `text` 基準）。

**現象 C（v3 定讞＝K2 同案傷員、不另動刀）**：同樣本 **zh 側**首圖亦缺。全窗 log（`ohtani_v3_full_log.txt`）定讞——`[PIPE-LITEDOC P3] mode=whole … zh=3601chars en=4424chars`：NHK 短文 en 僅 4,424 字元 **＜15k size gate → whole mode**，zh＝`translate_whole(full_text)` 與 en **共用同一條 full_text 素材**——R8 位移陷阱一刀殺雙語（log `DROP 1 行` 恰一次）。tiles 留圖（基準正確）但 whole mode 下 tiles 僅餵 RAG。**K2 落地 → zh/en 首圖同步回歸**（列 §E2E 直接驗收項、非觀察項）。
**診斷留痕（誠實）**：先前誤判 v3 為 section mode（由 final_zh 含 `##` 標題反推——whole mode 之 `translate_whole` 輸入本含 `##` 行、LLM 照譯、輸出同樣帶 section 標題、**此推斷面不可靠**）、致 restore／echo／`_load_tiles` 多輪本地重演追了一條未走之路；log Phase 行（`mode=`）為模式判定唯一可靠源。外部 review 之「前端雙語對齊器」理論維持否證（真機制＝whole-mode 共用通道、與前端無關）。

---

## 熱修復修法 (Minimal Hotfix)

### K1 — 裸 HTML 中和（litedoc P1 共用清洗步、通則）

**原則**：把 Medium 原文本有的 inline-code 樣貌在確定性層還原——包反引號、非刪除、非實體轉義：讀者看得見、marked 渲染 code span、DOMPurify 零觸發、翻譯 LLM 獲得明確「這是代碼」信號。

`pipelines/litedoc_pipeline.py` 模組層新增：

```python
# === [FITZ-HOTFIX-4 K1] 裸 HTML 標籤中和（baron 設計定調：PDF 專案、標籤＝一般文字）===
# 判定：`<`緊跟字母之標籤族（<script>/<link rel=…>/<img src=…>/</head>…）；`a < b` 不中。
_INLINE_TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>`\n]*?)?/?>")


def _neutralize_inline_html(text: str) -> str:
    """裸 HTML 標籤包反引號（行內替換、**行數不變式**——sidecar 行號零擾動）。

    - 反引號守衛：以 `` ` `` 切段、僅處理**段外**（已在 code span 內者不重包）；
    - 扉頁豁免天然成立：`paper-header-meta` div 為 P3 下游注入、P1 本步不可見；
    - fitz／MinerU 兩來源同享（接線於 P1 清洗步、與連字修復同段）。
    """
    out_lines = []
    for line in text.split("\n"):
        if "`" in line:
            segs = line.split("`")
            for i in range(0, len(segs), 2):          # 偶數段＝code span 之外
                segs[i] = _INLINE_TAG_RE.sub(lambda m: f"`{m.group(0)}`", segs[i])
            out_lines.append("`".join(segs))
        else:
            out_lines.append(_INLINE_TAG_RE.sub(lambda m: f"`{m.group(0)}`", line))
    return "\n".join(out_lines)
```

接線（P1 ②' 清洗鏈、連字修復同一寫檔塊）：

```diff
         if settings.LITEDOC_LIGATURE_REPAIR_ENABLED:
-            md_path.write_text(
-                ligature_repair.repair_ligatures(
-                    md_path.read_text(encoding="utf-8")
-                ),
-                encoding="utf-8",
-            )
+            _t = ligature_repair.repair_ligatures(md_path.read_text(encoding="utf-8"))
+            md_path.write_text(_t, encoding="utf-8")
+        # [FITZ-HOTFIX-4 K1] 裸 HTML 中和（無旗標——設計定調之確定性行為、回退＝git revert）
+        md_path.write_text(
+            _neutralize_inline_html(md_path.read_text(encoding="utf-8")),
+            encoding="utf-8",
+        )
```

（實作時以現行代碼為準取最小 diff；核心約束＝**在 ③ DocAnalyzer 之前、行數不變**。）

### K2 — R8 報頭集改「原封基準」單一源（行號位移陷阱關閉）

**原則**：報頭集必須在**原封 md 行序**上計算——P3 一進場（`_read_source_text` 剛讀、**K3 之前**）算好、傳給 R8；`_filter_source_figures` 不再自行以位移後 text 重算。

```diff
         full_text = self._read_source_text(ctx)
         title = (ctx.ingestion.title if ctx.ingestion else "") or ""
+        # [FITZ-HOTFIX-4 K2] 報頭集於**原封行序**上先算（K3 刪行之前）——
+        # R8 原以 sidecar 原封行號掃 K3 位移後 text、致界外圖上移入窗被③誤殺
+        # （NHK v3 en 側 page_0_9 實證）。與 tiles 路同基準、單一次計算雙通道共用。
+        _p3_output_dir = paper_manager.paper_dir(
+            settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id
+        )
+        _pristine_header_srcs = self._load_header_srcs(ctx, _p3_output_dir, full_text)
         full_text = self._strip_meta_source_lines(ctx, full_text)
         ...
-        full_text = self._filter_source_figures(ctx, full_text)
+        full_text = self._filter_source_figures(ctx, full_text, _pristine_header_srcs)
```

```diff
-    def _filter_source_figures(self, ctx: PipelineContext, text: str) -> str:
+    def _filter_source_figures(
+        self, ctx: PipelineContext, text: str,
+        header_srcs: Optional[set] = None,
+    ) -> str:
         ...
-            header_srcs = self._load_header_srcs(ctx, output_dir, text)
+            if header_srcs is None:               # 相容：未傳時退回自算（既有語意）
+                header_srcs = self._load_header_srcs(ctx, output_dir, text)
```

（`_load_header_srcs` 本體零改——修的是**餵給它的 text 基準**；簽名純加法預設 None。）

### 不可動清單

- `pipelines/image_filter.py` 三規則本體／門檻／`_collect_header_srcs`（tiles 路、基準本就原封）
- HOTFIX-3 K3（`_strip_meta_source_lines`）本體與時序／FITZ-ANCHOR U1-U6 全部語意
- `processor/fitz_processor.py`／`md_cleaner`／`section_engine`／`ingestion_engine`／`rag_indexer`
- 前端 `static/`（DOMPurify／marked 零改——K1 屬供給端治本、消毒層行為正確不動）
- A 軌全鏈／resume／slides；既有旗標語意；DB schema／API 簽名

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（落地時實貼輸出）

- K1：`<script>`／`</script>`／`<link rel="stylesheet" href="…">`／`<img src=…>` 全數包反引號；已在反引號內不重包（`` `<script>` `` 原樣）；`a < b`／`3 < 5 > 2` 不觸發；**行數不變式**斷言；**Browsers 實錄 fixture**——含裸 `<script>` 段落經 K1 後、模擬 marked+sanitize 語意斷言「後文不再被吞」（字面存活）；中文正文零擾動
- K2：**位移情境 fixture**（sidecar meta spans 0-6＋圖在行 8）——K3 刪行後、舊路徑（以位移 text 自算）誤收圖／新路徑（原封基準預算）圖存活；`header_srcs=None` 相容分支＝既有語意；**en/zh 圖集對稱斷言**（雙通道同基準之 E2E 化）
- SOP §5 雙 grep（logging／database）照跑實貼（本案零 DB、應「無命中（合規）」）
- 全套件基線 **1010 passed** 不退

```bash
$ pytest tests/ -v
# [落地時貼上真實輸出]
```

### 2. 本地 E2E 快速復現與驗證（baron 影子軌）

1. **Browsers 重傳**：zh／en 閱讀視圖全文顯示（~35k 字、22 標題到「延伸閱讀」）；`<script>`／`<link>` 以 **code 樣式可見**（讀者視角＝Medium 原文）；列印頁數回到全文量級
2. **NHK 重傳**：**zh／en 首圖（1280×720）雙側同步回歸**（C 定讞＝whole-mode 共用通道、K2 直接驗收項）；zh/en 圖集對稱；文字面 29/29 不退化
3. **SpaceX 回歸**：標題／21 圖／meta／termmap 各項不退化

```
[落地後貼上成功日誌]
```

---

## 回退與備案

```bash
# 單 commit 可逆：
git revert [HOTFIX-4 hash]

# K2 單獨降級（免 commit）：.env 設 IMG_FILTER_ENABLED=false 後重啟
#（圖片全保留、雙通道同步 no-op；K1 無旗標——設計定調之確定性行為、回退僅 git revert）
```

---

## 附：拍板、追蹤項與溯源紀錄

- **拍板**：K1 設計定調＝baron 2026-07-23「專案屬性就是處理 PDF、碰到 HTML 標籤應該就要當一般文字處理」（原則級、非個案修補）；包反引號（非轉義/非刪除）＝還原源文 inline-code 樣貌＋消毒零觸發雙贏
- **候選否決留痕**：前端層轉義（marked 前 escape raw HTML）——否決：會毀掉 P3 自注入之 `paper-header-meta` 扉頁（全庫唯一合法 raw HTML）；逐站點 prompt 修補——否決：技術文章通案、供給端一刀治本
- **追蹤項 C——已定讞結案（v3、全窗 log）**：`mode=whole`（en 4,424 字元＜15k gate）→ zh 與 en 共用 full_text 通道 → R8 位移陷阱一刀殺雙語（`DROP 1 行` 恰一次）；tiles 留圖但 whole mode 僅餵 RAG。**K2 即為 C 之修法**、zh/en 同步回歸列 E2E 直接驗收。證據檔：`Ohtani_v1/ohtani_v3_full_log.txt`。
- **⚠️ 外部 review「雙語對齊器」理論否證留痕（v2 攔截、v3 補真相）**——review 稱「final_zh 皆留有 page_0_9、前端 Bilingual Aligner 對齊濾除、K2 落地自癒」：前提假（`final_zh_v3.md` 磁碟檔 grep=0）、機制假（前端零對齊器、grep 證）；「K2 自癒」結論**碰巧為真**但機制全錯（真機制＝whole-mode 共用通道、與前端無關）——結論對而機制錯的理論若未攔截、下次故障必誤導方向。
- **命名債註記（baron 2026-07-23 拍板：純留痕、不動刀）**：`en_text`／`final_..._en.md`／P3 log `en=Nchars` 之「en」為 **A 軌時代歷史命名**（當年原文＝英文論文）、實際語意＝**原文側**——日文樣本之原文即裝在名為 en 的容器（`final_en` 內容＝日文、log `source_lang=ja` 判定正確、功能零影響）。誤導面真實存在（診斷者誤讀「英文版」／前端切換鈕標示／log 判讀），屬低優先正名債（`en`→`src` 類、牽動檔名慣例＋前端＋log 欄位）、留待未來獨立小案，本案零改。
- **族群註**：K2＝「行號基準位移」家族第五例（whole-mode 繞 filter／rule ③ 單通道／hint 截斷／meta 歸零單通道之後）——修法沿 HOTFIX-2「同一集合注入兩通道」精神、把「同一」推進到「同一**基準**」；PIPE-SYNC-6 回灌時併入雙通道鐵律
- **溯源**：FITZ-ANCHOR plan v2（U1-U6、本案零改其語意）；HOTFIX-3（K3 時序警告——本案關閉其漏網面）；HOTFIX-2 K2（header_srcs threading——本案修其基準）；SEC-XSS（DOMPurify 行為正確、不動）；診斷提示詞 `prompts/2026-07-23_FITZ-HOTFIX-4_診斷與plan_提示詞.md`
- **Revision**：
  - v3 (2026-07-23)：**現象 C 定讞結案**（baron 補證全窗 log）——`mode=whole`（<15k gate）→ zh/en 共用 full_text 通道、R8 一刀殺雙語；C 併入 K2 驗收、E2E 改列 zh/en 同步回歸；診斷留痕（「輸出含 ## ⇒ section mode」推斷面不可靠、模式判定唯一可靠源＝P3 log `mode=` 欄）；review「對齊器」理論補註「結論碰巧對、機制全錯」；附錄補 **en 命名債註記**（en＝原文側之 A 軌歷史命名、日文原文裝於 en 容器、功能零影響純誤導面、baron 拍板留痕不動刀）
  - v2 (2026-07-23)：外部 review 定稿——K1/K2 **全數肯認、零新增規格**；**現象 C「雙語對齊器」理論攔截否證**（前提假：final_zh 磁碟檔 grep=0／機制假：前端零對齊器 grep 證）——C 維持開放追蹤、嚴禁以「K2 自癒」推定結案（防 plausible-but-wrong 理論進入結案依據）
  - v1 (2026-07-23)：初版——兩刀 K1/K2＋追蹤項 C＋雙證據包全量測；commit 表待 baron 回填
