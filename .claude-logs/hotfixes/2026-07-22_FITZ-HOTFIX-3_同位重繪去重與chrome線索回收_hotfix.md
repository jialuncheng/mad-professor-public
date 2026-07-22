# FITZ-HOTFIX-3 — 緊急熱修復：同位重繪去重、chrome 線索回收與 full_text meta 歸零

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正日文樣本（NHK 新聞）影子 E2E 暴露之 B 軌標題全滅與 publisher 空白缺陷（K1/K2）＋族群掃描實證之 **en 側 meta 原文行洩漏／雙語文字不對稱**（K3、baron 拍板併入 2026-07-22）。
> **修復原則**：只改動受災點程式碼（`processor/fitz_processor.py` + `pipelines/litedoc_pipeline.py` 接點＋測試），嚴禁夾帶任何無關的新功能或大型重構。
> **依據**：`templates/template_hotfix.md`／`ref/WORKFLOW_SOP.md` §1.5 BE-Hotfix（logging_SOP + database_SOP 必讀、pytest + §5 SOP 核查）／`ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §1.1 雙軌制・§4.2 執行報告契約。
> **證據包**：`baton/litedoc_shadow_artifacts/Ohtani_v1/`（gitignored 長駐審計）＋源 PDF `baton/ドジャース 大谷翔平 二刀流復帰戦で先頭打者HR 投げては4勝目.pdf`。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-3** | `[留空，由 baron 回填]` | BE-Hotfix: FITZ-HOTFIX-3 — Overlap Dedup, Chrome Hint & Meta Zeroing（同位重繪去重、chrome 線索回收與 full_text meta 歸零） |

落地時（依 CLAUDE.md §1.3、Claude Code 不 commit）：
- commit message 草稿寫 `/tmp/FITZ-HOTFIX-3_msg.txt`
- `git add` 白名單（逐檔顯式、含 `.bak`）：`processor/fitz_processor.py`／`pipelines/litedoc_pipeline.py`／`tests/test_fitz_processor.py`／`tests/test_litedoc_pipeline.py`／對應 `.bak` ×4（archive/）

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：日文樣本（NHK）B 軌產出標題＝「大谷翔平 (測試)」——真標題「ドジャース 大谷翔平 二刀流復帰戦で先頭打者HR 投げては4勝目」**整個消失**（A 軌正確對照組：「道奇隊大谷翔平二刀流復出戰 敲出首打席全壘打、投球奪下第4勝」）；扉頁 meta 僅剩 date、publisher 空白。
- **受災範圍**：litedoc fitz 快速道之**標題鏈全滅**（P1 title → 譯題 → 檔名／扉頁／PDF Title）＋ publisher 欄；date 正確、authors=0 屬「正確的空」（NHK 無署名；對照 A 軌 `authors: Baron` 反而是 PDF `/Author` 檔案屬性污染——design spec F6「meta 純正文」決策之活教材）。
- **首發日誌（pipeline_log.txt 實貼）**：

  ```
  [PIPE-LITEDOC P1] ト_シ_ャース_..._shadow title='大谷翔平 (測試)' source_lang=ja
                    tiles=1 publisher='' authors=0
  [PIPE-LITEDOC P3] ..._shadow mode=whole source_lang=ja sections=1
                    zh=4499chars en=5669chars translated_title='大谷翔平 (測試)'
  ```

### 2. 真因診斷 (Root Cause)

**真因 A（標題全滅）＝四環因果鏈、每環實測**：

1. **NHK 標題帶文字描邊（text-stroke）效果** → 瀏覽器列印時同一行字在**同座標重繪 4 次**。源 PDF 第一頁實測：

   ```
   y0= 40.5 size=30.1 BAND | ドジャース 大谷翔平 二刀流復帰戦   ×4 份（同 y0 同 size）
   y0= 76.5 size=30.1      | で先頭打者HR 投げては4勝目          ×4 份（同 y0 同 size）
   （正文 15.4；頁首 chrome「科学•⽂化 | NHKニュース」7.0；頁尾 URL/頁碼 7.0）
   ```

2. **fitz 忠實抽出全部 4 份** → 字級 30.1 遠大於正文 15.4 → 全數判 h1 → md 出現「`# 標題上半`」×4＋「`# 標題下半`」×4。
3. **`md_cleaner` 浮水印規則誤殺**（`processor/md_cleaner.py:15` `_detect_watermark_headings`、RAG-7a 時代治 DeHunt 履歷浮水印之遺產）：「同一 heading 文字出現 ≥ `WATERMARK_HEADING_THRESHOLD`（=3）次＝浮水印、**全部移除**」→ 4 ≥ 3 → 標題八行全滅。fitz md 前 8 行空白即其屍痕（移除行後殘留之分隔空行）。
4. **cover-prompt 讀無標題 md** → 文首唯一像標題的 token＝date 行尾之 NHK 話題標籤「大谷翔平」→ title='大谷翔平' → 譯題原樣 → 檔名／扉頁全錯。

- **為何 A 軌沒中**：MinerU 對重疊文字自帶去重 → 標題只出 1 份 → 1 < 3 → 浮水印規則放行。
- **為何 R2（HOTFIX-1）沒防到**：R2 管**跨頁**重複（`≥2 頁`）；本案是**同頁同座標** ×4——不同物種。
- **定位程式碼**：`processor/fitz_processor.py` `_collect_page`（無同位去重）；`processor/md_cleaner.py:15`（規則本身不動——它治 MinerU 路浮水印有戰功、病根在 fitz 供給端）。

**真因 C（K3、族群掃描實證）＝meta 歸零單通道、en 側原文行洩漏**：

- R6 meta 歸零（HOTFIX-1）掛在 `assemble`（**tiles 路**）；而 P3 之 `en_text = full_text`（所有模式）與 whole／is_zh 之 zh 側素材＝**原始 md**、只經 echo-strip（僅剝標題+緊隨 2 行）與 R8 圖片過濾——**meta 原文行沒人管**。
- **SpaceX v3 實物鐵證**：`shadow_en.md` L13 `MARC ANDREESSEN AND MICHAEL MCGUINESS`／L15 `JUN 15, 2026` **原文重播**（扉頁已渲染一份）；`shadow_zh.md`（tiles 路）同 grep **零命中**——**雙語文字不對稱**（HOTFIX-2 修了圖片版、文字版仍開）。
- whole-mode 之 zh 側同理必中（Ohtani 恰被錯標題連坐蓋掉；換一份 meta 行不緊鄰標題的 whole-mode 文件即露）。
- **族譜**：與 whole-mode 繞過 filter（HOTFIX-1 R8）／rule ③ 單通道（HOTFIX-2 K2）／hint 截斷（本案 v2）同族——**tiles 路 vs full_text 路雙素材通道、淨化器只掛一條**。
- **定位程式碼**：`pipelines/litedoc_pipeline.py` P3 full_text 處理鏈（現僅 echo-strip + `_filter_source_figures`）。

**真因 B（publisher 空白）＝chrome 剝除丟掉唯一線索**：

- NHK 身份只存在兩處：logo **圖片** + 列印頁尾 **URL chrome**（`https://news.web.nhk/newsweb/...`、7pt、每頁重複）。
- R2 跨頁重複剝除**正確地**把 URL 行剝了 → cover-prompt 的「URL→publisher 解碼」規則（rule 1）無米之炊 → publisher=''。SpaceX 能解出 a16z 是因為該文 **body 首行**自帶 URL；NHK 沒有。
- **定位程式碼**：`processor/fitz_processor.py` `_assemble`（chrome 剝除點、線索未回收）＋ `pipelines/litedoc_pipeline.py` `_extract_litedoc_metadata`（LLM 輸入無 hint 通道）。

---

## 熱修復修法 (Minimal Hotfix)

### K1 — `_collect_page` 同位重繪去重（治標題）

```diff
             for line in block.get("lines", []):
                 text = "".join(s.get("text", "") for s in line.get("spans", [])).strip()
                 if not text:
                     continue
                 x0, y0, _x1, y1 = line["bbox"]
                 size = max(float(s.get("size", 0.0)) for s in line.get("spans", []))
+                # [FITZ-HOTFIX-3 K1] 同位重繪去重——text-stroke/shadow 列印產物為
+                # 「同頁同座標同字級同文字」之精確重疊副本（NHK 標題 ×4 實證）；
+                # 只留一份、防下游 md_cleaner 浮水印規則（heading 重複 ≥3 全殺）誤殺真標題。
+                # 合法重複文字（不同座標）key 不同、零影響。
+                dedup_key = (text, round(y0, 1), round(float(x0), 1), round(size, 1))
+                if dedup_key in seen_lines:
+                    continue
+                seen_lines.add(dedup_key)
                 lines.append({...})
```

（`seen_lines: set` 於 `_collect_page` 開頭初始化、**每頁獨立**——跨頁同文同座標屬列印 chrome、歸 R2 管轄、不越權。）

### K2 — chrome URL 線索回收（治 publisher）

**fitz 端**（`_assemble` 剝除點回收 + `parse()` 落 sidecar）：

```diff
                 if (line["in_band"]
                         and _repetition_key(line["text"], line["size"]) in repeated):
+                    # [FITZ-HOTFIX-3 K2] chrome 照剝、URL 線索回收（publisher 唯一線索
+                    # 常僅存於列印頁尾 URL——NHK 實證；SpaceX 類 body 自帶 URL 者不受影響）
+                    m_url = _URL_RE.search(line["text"])
+                    if m_url:
+                        chrome_urls.add(m_url.group(0))
                     continue  # 跨頁重複之列印頁首尾（R2：文字+字級複合 key）
```

```diff
         markdown_path.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")
+        # [FITZ-HOTFIX-3 K2] 線索 sidecar（best-effort、缺之無害）
+        if chrome_urls:
+            (out_dir / f"{pdf_file.stem}_source_hints.json").write_text(
+                json.dumps({"urls": sorted(chrome_urls)}, ensure_ascii=False),
+                encoding="utf-8",
+            )
```

**litedoc 端**（meta 抽取輸入附 hint、md 本體零污染）：

**⚠️ 截斷陷阱（v2 自查發現、外部 review 未察）**：`_extract_litedoc_metadata` 內部 `head = markdown_text[:_META_INPUT_CHARS]`（**只取文首 4000 字**、`litedoc:64`）——若把 hint 接在全文**尾端**（NHK md 15.1K）必被截掉、K2 靜默失效。故 hint 必須以**獨立參數**傳入、於**截斷之後**拼接：

```diff
-        meta = self._extract_litedoc_metadata(markdown_text)
+        meta = self._extract_litedoc_metadata(
+            markdown_text, hints=self._load_source_hints(output_dir, pdf_path)
+        )
```

```diff
-    def _extract_litedoc_metadata(self, markdown_text: str) -> Dict[str, Any]:
+    def _extract_litedoc_metadata(
+        self, markdown_text: str, hints: str = ""
+    ) -> Dict[str, Any]:
         ...
-        head = (markdown_text or "")[:_META_INPUT_CHARS]
+        # [FITZ-HOTFIX-3 K2] hint 於截斷「之後」拼接——保證必入 LLM 輸入窗
+        head = (markdown_text or "")[:_META_INPUT_CHARS] + (hints or "")
```

（簽名純加法、預設 `""` → 既有呼叫端／MinerU 路 byte 等價。）

```python
    @staticmethod
    def _load_source_hints(output_dir: Path, pdf_path: Path) -> str:
        """[FITZ-HOTFIX-3 K2] 讀 fitz 回收之 chrome URL hint、附進 cover-prompt 輸入。

        - 定位＝`{Path(pdf_path).stem}_source_hints.json`（與 md/sidecar 同 stem 基準、
          HOTFIX-2 影子後綴教訓：嚴禁 paper_id 組名）。
        - 缺檔／解析異常 → 回 ""（fail-open、行為與現行 100% 等價；MinerU 路無此檔天然 no-op）。
        """
        try:
            p = output_dir / f"{Path(pdf_path).stem}_source_hints.json"
            if not p.exists():
                return ""
            urls = json.loads(p.read_text(encoding="utf-8")).get("urls") or []
            if not urls:
                return ""
            return "\n\nSource URL (from page chrome): " + " ".join(urls[:3])
        except Exception as exc:  # noqa: BLE001 — hint 屬加分項、失敗零影響
            logger.warning("[PIPE-LITEDOC P1] source_hints 讀取失敗（略過）: %s",
                           exc, exc_info=True)
            return ""
```

（`_URL_RE = re.compile(r"https?://\S+")`；hint 只進 **LLM 輸入**、不寫 md——判型／tiles／行號基準零擾動。cover-prompt 既有 rule 1「URL→publisher 解碼」直接吃到 → NHK 域名 → publisher=NHK。）

### K3 — P3 full_text 行級 meta 歸零（治 en 側洩漏＋雙語文字對稱）

**接線點與順序（關鍵）**：P3 `_read_source_text` 之後、**echo-strip 與 R8 之前**——K3 以 sidecar **行號**比對，必須作用在與 sidecar 同基準的**原封 md 行序**上（echo-strip／R8 會刪行位移、K3 若排其後行號全錯——與 hint 截斷同款陷阱、設計期先堵）：

```diff
         full_text = self._read_source_text(ctx)
+        # [FITZ-HOTFIX-3 K3] full_text 行級 meta 歸零（單點、三消費者 is_zh/whole/en_text
+        # 同享）——R6 只掛 tiles 路致 en 側原文 meta 行重播（SpaceX v3 實證）；
+        # 必須在 echo-strip/R8 之前（行號與 sidecar 同基準、刪行位移前）。
+        full_text = self._strip_meta_source_lines(ctx, full_text)
         # ① pre-strip：原文層剝標題回聲 ...
         full_text = section_engine.strip_title_echo(full_text, _title_bare)
         full_text = self._filter_source_figures(ctx, full_text)
```

**實作草稿**（雙判據＝sidecar 判型 spans ∪ meta 值比對、**全部複用既有實作源**）：

```python
    def _strip_meta_source_lines(self, ctx: PipelineContext, text: str) -> str:
        """[FITZ-HOTFIX-3 K3] 對 P1 原始 md 全文剝 meta 原文行（行級、DROP 即刪行）。

        雙判據（同 R6 語意、複用 ingestion_engine 同一正規化源）：
        ① sidecar 判型 spans：type ∈ _META_TYPES ∪ {"title"} 之 blocks 行號區間
          （sidecar 三級定位＝HOTFIX-2 `_load_header_srcs` 同款：pdf_path stem 主路
          → glob 備路 → ∅；行號僅在「原封行序」上使用、故 K3 必排最前）；
        ② 值比對：`ingestion_engine.normalize_meta_values` 餵 P1 已抽 meta 值
          （ctx.ingestion.authors／venue ＋ ctx.raw_metadata date/url）、行文字
          `_normalize_meta_text` 後**整行相等**才剝（非子字串、R6 同約）。
        任一判據命中 → 刪行；sidecar 缺 → 僅值比對；值集空 → 僅 spans；兩者皆缺
        → no-op（fail-open、warning）。圖片行不在判據內（歸 R8 管、職責不重疊）。
        """
```

**效果**：en_text／whole zh／is_zh zh 三消費者一次乾淨；section-mode zh（tiles 路、R6）本已乾淨 → **雙語文字對稱恢復**（與 HOTFIX-2 圖片對稱成對）。echo-strip 的「標題+日期連坐」在 K3 之後多為 no-op、保留作兜底不動。

### 不可動清單

- `processor/md_cleaner.py` 浮水印規則本體／`WATERMARK_HEADING_THRESHOLD`——零改（規則治 MinerU 路有戰功、病根在 fitz 供給端）
- cover-prompt `_LITEDOC_META_SYSTEM_PROMPT` 六欄與規則——零改（K2 只增輸入、不改提示詞）
- HOTFIX-1 八刀／HOTFIX-2 兩刀語意——零改；`image_filter`／`ingestion_engine`／`section_engine`——零改
- A 軌全鏈／resume／slides；`PDFParser` ABC 簽名（sidecar 屬 side-effect、與 images/ 同類）——零改

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（落地時實貼輸出）

- K1：同頁同位 ×4 行 fixture → 收集後恰 1 份；**不同座標之同文字**（合法重複）全保留；跨頁 chrome 仍由 R2 剝（K1 不越權斷言）
- K1 整合：×4 標題 PDF（fitz 現造）→ md 恰一個 `#` 標題 → 真 `MarkdownCleaner().clean` 後**標題存活**（浮水印規則放行、對照組：未去重 ×4 會被殺）
- K2：sidecar 產出（chrome URL 命中回收、無 URL 頁零產出）；`_load_source_hints` 主路命中／缺檔回 ""／解析異常 fail-open；影子後綴情境（`paper_id` 帶 `_shadow`、hints 檔名無後綴 → 仍命中）；hint 不入 md 斷言（md byte 與無 hint 時等價）；**截斷窗斷言**——`markdown_text` >4000 字時 hint **仍在** LLM 輸入內（捕 messages 驗 `Source URL` 存在、堵 v1 尾接截斷陷阱）；`hints=""` 預設 byte 等價
- K3：SpaceX 型 fixture（meta 行隔著 epigraph/圖、逃 echo-strip cap）→ 歸零後 en_text 無 `MARC`/`JUN` 型行；**雙語文字對稱斷言**——en 之 meta 原文行集 == zh == ∅；**順序斷言**——K3 於 echo-strip/R8 **之前**執行（行號位移前、mock 呼叫序捕捉）；正文句含作者名**不剝**（整行相等約束）；sidecar 缺 → 值比對仍工作；兩判據皆缺 → no-op byte 等價；whole-mode zh 素材同乾淨
- 全套件基線不退（HOTFIX-2 落地後之最新綠燈數）；SOP 雙 grep（logging／database）照跑實貼

```bash
$ pytest tests/ -v
# [落地時貼上真實輸出]
```

### 2. 本地 E2E 快速復現與驗證（baron 影子軌）

1. 重傳 NHK 樣本：標題＝「ドジャース 大谷翔平 二刀流復帰戦で先頭打者HR 投げては4勝目」系譯題＋恰一個 `(測試)`；publisher=**NHK**；date=2026-05-21；authors=0（誠實空）
2. log 驗：P1 行 `title=` 為完整標題、`publisher='NHK'`；`[md_cleaner] 移除浮水印` **不再命中標題**
3. SpaceX 回歸重傳：標題／21 圖／meta 各項不退化（K1 對非描邊站零影響、K2 對 body 自帶 URL 站不改變結果）；**K3 驗**——`shadow_en.md` grep `MARC ANDREESSEN`/`JUN 15` 歸零（v3 洩漏點治癒）、zh/en meta 行雙零對稱

```
[落地後貼上成功日誌]
```

---

## 回退與備案

```bash
# 單 commit 可逆：
git revert [HOTFIX-3 hash]

# 或免 commit 單點降級（整條 fitz 快速道退回 MinerU 路）：
# .env 設 LITEDOC_FITZ_ENABLED=false 後重啟
```

---

## 附：拍板與溯源紀錄

- 候選方案留痕：改 `md_cleaner` 閾值／加同頁豁免——**否決**（規則治 MinerU 浮水印有戰功、cleaner 無座標資訊判不了「同位」；幾何去重只有 fitz 層做得到、供給端治本）；K2 改「hint 寫進 md」——**否決**（污染判型行號基準、違行數/行界不變式慣例）
- 診斷鏈：P1 log（title='大谷翔平' publisher='' authors=0）→ fitz md 前 8 行空白＋無標題 → 源 PDF 第一頁解剖（×4 同位重繪實測）→ `md_cleaner:15` 浮水印規則對質 → A 軌對照（MinerU 去重故 1 份存活）
- 溯源：design spec F6（meta 純正文——A 軌 `authors: Baron` 檔案屬性污染為其活教材）；HOTFIX-1 R2（跨頁 chrome 剝除、本案 K2 於其剝除點回收線索）；HOTFIX-2（sidecar 同 stem 基準教訓、K2 沿用）；診斷提示詞 `prompts/2026-07-22_FITZ-HOTFIX-3_診斷與plan_提示詞.md`
- **族群教訓（供 PIPE-SYNC-6 回灌 ingestion 契約章）**：litedoc 有**兩條輸出素材通道**（tiles 路 vs full_text 路）——四個同族缺陷（whole-mode 繞 filter／rule ③ 單通道／hint 截斷／meta 歸零單通道）共同根源＝**淨化器只掛一條通道**。鐵律候選：「凡對 tiles 做的淨化、必問 full_text 那條」；full_text 行級處理鏈之順序不變式＝「行號基準處理（K3）→ 文字基準處理（echo-strip）→ 圖片行處理（R8）」。
- **Revision**：
  - v3 定稿確認 (2026-07-22)——外部 review 二輪**全數肯認、零新增規格**（K3 接線順序／K2 截斷後拼接／K1 幾何去重／三拍板全數維持；一處標籤筆誤指正：`∪ {"title"}` 防禦性聯集屬 K3/行界設計、非 K2）；本案設計凍結、待執行
  - v3 (2026-07-22)——**K3 併入**（baron 拍板）：族群掃描實證 en 側 meta 原文行洩漏（SpaceX v3 `shadow_en` L13/L15 `MARC`/`JUN` vs zh 零、雙語文字不對稱）→ 真因 C＋K3 行級 meta 歸零（雙判據＝sidecar spans ∪ R6 值比對、複用 engine 同一正規化源；**接線必在 echo-strip/R8 之前**——行號位移陷阱設計期先堵）＋測試靶（對稱斷言/順序斷言/整行相等）＋E2E 補 SpaceX en 歸零驗；commit subject 更新三刀
  - v2 (2026-07-22)——外部 review 肯認 K1/K2 全案無異議（一處筆誤更正：meta 抽取在 **P1** 非 P3）；**自查補一真 bug**：v1 K2 接線 `markdown_text + hint` 尾接會被 `[:_META_INPUT_CHARS]`（4000 字文首截斷、`litedoc:64` grep 證）截掉而靜默失效 → 改 `hints` 獨立參數、**截斷後拼接**（簽名純加法預設 `""`）＋ §驗證補「截斷窗斷言」測試靶
  - v1 初版
