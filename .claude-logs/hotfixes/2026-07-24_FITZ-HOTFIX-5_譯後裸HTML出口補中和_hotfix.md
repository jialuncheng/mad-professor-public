# FITZ-HOTFIX-5 — 緊急熱修復：譯後裸 HTML 標籤出口補中和

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正 FITZ-HOTFIX-4（`5756219`）落地後 Browsers 樣本 E2E 仍未痊癒之殘留缺陷：B 軌閱讀視圖仍 **46 頁塌成 3 頁**。
> **修復原則**：只改動受災點程式碼（`pipelines/litedoc_pipeline.py` 單檔＋測試），嚴禁夾帶任何無關的新功能或大型重構。
> **依據**：`templates/template_hotfix.md`／`ref/WORKFLOW_SOP.md §1.5 BE-Hotfix`（logging_SOP + database_SOP 必讀、pytest + §5 SOP 核查）／`ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1.1 雙軌制・§4.2 執行報告契約`。
> **與 HOTFIX-4 之關係**：HOTFIX-4 K1 在 **P1 源頭**把裸 HTML 中和（給翻譯 LLM「這是代碼」信號）；本案補上 **P3 出口保證**——治「K1 有效但譯後復活」之充分性缺口。K1＝源頭給信號、HOTFIX-5＝出口保證乾淨，成雙保險。
> **證據包**：`baton/litedoc_shadow_artifacts/Browsers_v3/`（B 軌中繼 `{stem}.md` + `final_..._shadow_zh.md`）＋逐檔裸標籤掃描（見下 §真因診斷 證據鏈）。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **HOTFIX-5** | `[留空，由 baron 回填]` | BE-Hotfix: FITZ-HOTFIX-5 — Post-Translation Inline HTML Re-Neutralization（譯後裸 HTML 標籤出口補中和） |

落地時（依 CLAUDE.md §1.3、Claude Code 不 commit）：
- commit message 草稿寫 `/tmp/FITZ-HOTFIX-5_msg.txt`
- `git add` 白名單（逐檔顯式、含 `.bak`）：`pipelines/litedoc_pipeline.py`／`tests/test_litedoc_pipeline.py`／對應 `.bak` ×2（archive/）

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：HOTFIX-4 落地並**重啟 pipeline 進程**（03:55 新進程、新 code）後重傳 Medium「How modern browsers work」（46 頁），B 軌影子閱讀視圖／列印**仍只剩 ~3 頁**。
- **受災範圍**：所有含字面 HTML 標籤之技術文章（MDN／CSS-Tricks／技術部落格通案），B 軌 `final_..._shadow_zh.md` 消費者（前端閱讀視圖）。
- **管線無罪證明（關鍵）**：B 軌 P3 log 明載 `mode=section source_lang=en sections=11 zh=34820chars`、`[RAG-ASYNC] sections_in=22`——**B 軌管線輸出完整（zh 3.4 萬字、22 章節，一字未掉）**，蒸發發生在**前端渲染層**。

### 2. 真因診斷 (Root Cause)

**逐階段裸標籤掃描（`output/1/{stem}[_shadow]/` 實測、`code span 之外`計數）：**

| 檔案 | 段外裸標籤 | 意義 |
|---|---|---|
| A 軌 MinerU 中繼 `{stem}.md`（無 K1）| 27 | 對照組（A 軌不跑 K1） |
| **B 軌中繼 `{stem}_shadow/{stem}.md`（K1 後）** | **0** | **HOTFIX-4 K1 完全生效**（源頭 27→0 全包 `` `<script>` ``） |
| B 軌 `final_..._shadow_zh.md`（前端讀） | **5** | 3 扉頁 div ＋ **2 body 譯後復活** |
| B 軌 `final_..._shadow_en.md` | 3 | 全為扉頁 div（body 乾淨） |

**逐行定位 `final_..._shadow_zh.md` 之裸標籤（實測輸出）：**

```
L2   <div class="paper-header-meta">          ← 扉頁（合法 raw HTML，DOMPurify 保留 div）✓
L3   <div class="header-authors">Addy Osmani</div>    ← 扉頁 ✓
L4   <div class="header-venue-date">Medium · 2026-07-01</div>  ← 扉頁 ✓
L57  <script  ||  ...允許...預先渲染包含 Java<script...   ← ★ 兇手：body 裸 <script>
L137 <p       ||  ...JavaScript 稍後變更了 <p> 元素的大小...  ← body 裸 <p>（次要）
```

- **技術細節**：HOTFIX-4 K1（`_neutralize_inline_html`）在 **P1 ②' 清洗步**把中繼 md 的裸標籤 27→0 全包反引號。但 P3 **section 模式**走 `restore_sections_markdown` **逐 tile 呼叫翻譯 LLM**——LLM 翻譯含 `` `<script>` `` 之段落時**不保證保留反引號**（L57「Java<script>」即 LLM 把 `包含 JavaScript` 與後續 `` `<script>` `` 硬接、拆掉反引號之痕跡），tiling 也可能把一對 `` ` `` 拆到兩個 tile → **裸標籤在譯後成品復活**。
- 前端 `marked` 解析到 body 之**首個裸 `<script>`（L57）** → 當成真 `<script>` 開標籤（無閉合）→ 把其後全部內容當 script 內文 → DOMPurify（SEC-XSS、行為正確）移除整個 script 元素**連同內文** → L57 之後全蒸發（22 章節塌成 ~3 頁）。
- **定位程式碼**：`pipelines/litedoc_pipeline.py` `run_phase3`——`zh_text`／`en_text` 於 `restore_sections_markdown`／`translate_whole` 產出、echo-strip 後、**扉頁 prepend（L1163-1164）之前**尚未再次中和。
- **定性**：K1-at-P1 為**必要但不充分**——源頭中和給了 LLM 信號、卻無法保證 LLM 譯後輸出仍守反引號。需在**確定性層（出口）**補一道冪等中和作結構性保證，不依賴 LLM 是否配合。

---

## 熱修復修法 (Minimal Hotfix)

**原則**：在 P3 **body 定案後、扉頁注入前**，對 `zh_text`／`en_text` 各補跑一次 `_neutralize_inline_html`（HOTFIX-4 既有模組層純函式、零新增）。冪等（反引號守衛→只包新復活的裸標籤、已包的不動）＋行數不變＝零副作用；覆蓋 whole／section／is_zh 三模式 × zh／en 雙側。**扉頁 `paper-header-meta` div（全庫唯一合法 raw HTML）在 body 中和之後才 prepend、天然不被包。**

### 修法定位（P1–P4 架構，釐清「改哪裡」）

本案改的是 **B 軌 P3（`run_phase3`）階段本身**，具體在 **P3 的最後一步「組裝最終交付 md」處**——**不是**改前端、**不是**新開階段、**不是**改 P1/P2/P4。

| 階段 | 方法 | 職責 | 產出 | 本案是否觸碰 |
|---|---|---|---|---|
| P1 | `run_phase1` | 攝入（fitz/MinerU）→ 清洗（**HOTFIX-4 K1 源頭中和在此**）→ tiles + meta | `IngestionMetadataSpec` | ✗（K1 保留、零改） |
| P2 | `run_phase2` | 摘要 / glossary / domain | `GlossaryReadySpec` | ✗ |
| **P3** | `run_phase3` | **翻譯還原 → 組裝交付 md → 寫檔** | `final_..._zh.md` / `final_..._en.md` | ✓ **本案改此階段尾段** |
| P4 | `run_phase4` | RAG 索引 | FAISS chunks | ✗（`ctx.rag_sections` 早於本剝定案） |

**P3 尾段組裝流程（★＝本案插入點）**：

```
翻譯/重組 body（restore_sections_markdown [section] / translate_whole [whole] / full_text [is_zh]）
      ↓
echo-strip 剝標題回聲（strip_title_echo）
      ↓
★ HOTFIX-5：body 補中和 zh_text = _neutralize_inline_html(zh_text) / en_text 同（新增 2 行）
      ↓
扉頁 prepend（header_zh + zh_text / header_en + en_text）   ← L1163-1164
      ↓
寫檔 final_zh.md / final_en.md                              ← L1169-1170（前端之後讀此檔）
```

**為何是「後端 P3 出口」而非「前端」**：P3 尾段產出的 `final_zh.md` **就是**前端閱讀視圖要吃的檔。選擇在**供給端（後端 P3 出口）治本**，讓交付給前端的 md body 本身零裸 `<script>`——前端 `static/`（marked/DOMPurify、行為正確）**一行不動**。「改 P1–P4」與「組裝給前端的文件」在此指**同一個點**：P3 尾段＝組裝交付文件＝後端產出前端消費的 md。

### `pipelines/litedoc_pipeline.py` `run_phase3` — 最小改動

```diff
         # === [PIPE-LITEDOC-HOTFIX-1 END] ===

         # ⑥ translated_title handoff → P4（既有 raw_metadata 旁路、PIPE-SLIDES-HOTFIX-1b 三欄 dict 範式）
         ctx.raw_metadata["translated_title"] = {
             "value": translated_title or title, "source": "litedoc_p3", "confidence": "high",
         }

+        # === [FITZ-HOTFIX-5] 譯後/重組復活之裸 HTML 標籤出口補中和（結構性保證）===
+        # HOTFIX-4 K1（P1 源頭）已把中繼 md 27→0，但 P3 section 逐 tile 翻譯時 LLM 拆掉部分
+        # 反引號（實證 final_zh L57「Java<script>」）→ 成品 body 復活裸 <script> 致前端
+        # marked+DOMPurify 撞首個即吞其後全部內容。此處對 body 補跑冪等中和（行數不變、
+        # 反引號守衛→只包新復活者）；**必在扉頁 prepend 之前**——扉頁 paper-header-meta div
+        # 為合法 raw HTML、不可包反引號。覆蓋 whole/section/is_zh 三模式 × zh/en 雙側。
+        zh_text = _neutralize_inline_html(zh_text)
+        en_text = _neutralize_inline_html(en_text)
+        # === [FITZ-HOTFIX-5 END] ===
+
         # ⑤ HTML 扉頁（# 標題：zh 用譯題 / en 用原題；render_meta_header_html 純格式化器）
         header_zh, header_en = self._render_meta_headers(ctx, title, translated_title)
         zh_text = header_zh + zh_text
         en_text = header_en + en_text
```

（`_neutralize_inline_html`／`_INLINE_TAG_RE` 為 HOTFIX-4 既有模組層函式、零改；本案僅新增兩行呼叫接線。）

### 不可動清單

- `_neutralize_inline_html`／`_INLINE_TAG_RE` 本體（HOTFIX-4 K1、零改——僅新增呼叫）
- HOTFIX-4 K1 之 P1 ②' 接線（源頭中和保留、與本案雙保險）
- HOTFIX-4 K2（`_pristine_header_srcs`／`_filter_source_figures` 基準）本體與語意
- HOTFIX-3 K3（`_strip_meta_source_lines`）／FITZ-ANCHOR U1-U6／FITZ-HOTFIX-1 C3 R8 全部語意
- `render_meta_header_html`／扉頁 `paper-header-meta` 結構（body 中和在前、扉頁 prepend 在後）
- `section_engine`／`ingestion_engine`／`image_filter`／`fitz_processor`／`md_cleaner`／`rag_indexer`
- 前端 `static/`（DOMPurify／marked 零改——本案屬供給端治本、消毒層行為正確不動）
- A 軌全鏈／resume／slides；既有旗標語意；DB schema／API 簽名；`ctx.rag_sections`（早於本剝定案、RAG 不受影響）

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（落地時實貼輸出）

- **譯後復活 fixture**：構造 section 模式 P3，令 `restore_sections_markdown` 回傳含**裸 `<script>`**之 zh body（模擬 LLM 拆反引號）→ 斷言 P3 出口中和後 `final_zh` body **段外裸標籤 = 0**、`` `<script>` `` 已包、L57 型內容字面存活。
- **扉頁豁免**：斷言 `final_zh`／`final_en` 之 `<div class="paper-header-meta">`／`header-authors`／`header-venue-date` 扉頁 div **原封保留**（未被反引號包裹）——證明中和作用於 body、扉頁在其後 prepend。
- **冪等**：對已中和文本再跑一次 `_neutralize_inline_html` → 完全相等（反引號守衛）。
- **行數不變式**：`zh_text`／`en_text` 中和前後行數全等（sidecar 行號/下游零擾動）。
- **whole 模式對稱**：whole 模式（<15k）下 zh/en 共用通道亦補中和、body 零裸標籤。
- **旗標/回歸**：既有 R8／K2／K3／對稱測試全綠不退（本案純加法、不動既有語意）。
- SOP §5 雙 grep（logging／database）照跑實貼（本案零 DB、應「無命中（合規）」）。
- 全套件基線 **1021 passed** 不退。

```bash
$ pytest tests/ -v
# [落地時貼上真實輸出]
```

### 2. 本地 E2E 快速復現與驗證（baron 影子軌）

1. **Browsers 重傳**：B 軌 zh／en 閱讀視圖**全文顯示**（~35k 字、22 標題到「延伸閱讀」）；`<script>`／`<p>`／`<link>` 以 **code 樣式可見**（讀者視角＝Medium 原文 inline-code）；列印頁數回到全文量級。
2. **成品自檢**（決定性）：
   ```bash
   F=$(find output -type f -name "final_*modern_browsers*shadow_zh.md" | head -1)
   # body 段外裸標籤應僅剩扉頁 div（L2-4）、L57/L137 型 <script>/<p> 已包
   grep -nE '</?script|</?link|</?img' "$F"   # 應僅出現於反引號內
   ```
3. **NHK／SpaceX 回歸**：標題／圖片／meta／雙語對稱各項不退化（本案不碰 K2/K3/R8）。

```
[落地後貼上成功日誌]
```

---

## 回退與備案

```bash
# 單 commit 可逆：
git revert [HOTFIX-5 hash]

# 本案無旗標——出口中和為設計定調之確定性行為（同 K1）、回退僅 git revert。
# 極端降級：git revert 後回到 HOTFIX-4 狀態（K1 源頭中和仍在、僅失去譯後出口保證）。
```

---

## 附：溯源、追蹤項與 Revision

- **溯源**：FITZ-HOTFIX-4 K1（`5756219`、P1 源頭裸 HTML 中和——本案補其譯後充分性缺口、`_neutralize_inline_html` 函式零改）；SEC-XSS（DOMPurify 行為正確、不動）；診斷鏈見對話證據（B 軌逐階段裸標籤掃描 27→0→5、L57 裸 `<script>` 逐行定位、`mode=section` P3 log）。
- **設計拍板（承 HOTFIX-4）**：baron 2026-07-23「專案屬性就是處理 PDF、碰到 HTML 標籤應該就要當一般文字處理」——本案將此原則從 P1 源頭推進到 **P3 出口**，使「標籤＝字面文字」在**最終交付物**上有結構性保證、不受翻譯 LLM 行為影響。
- **候選否決留痕**：
  - 改 translate 提示詞要求 LLM 保留 code span——否決：依賴 LLM 配合、非確定性、L57 已證 LLM 會拆；出口冪等中和才是結構性保證。
  - 前端 marked 前 escape raw HTML——否決：會毀掉 P3 自注入之 `paper-header-meta` 扉頁（全庫唯一合法 raw HTML）；供給端治本零副作用。
  - 移除 P1 K1、只留出口中和——否決：P1 K1 給翻譯 LLM「這是代碼」信號、改善譯文品質（tiles 源頭乾淨）；雙保險成本趨零。
- **追蹤項**：本案為「裸 HTML 標籤」家族之出口封閉；若未來 whole 模式或其他消費者（如 A 軌 md_restore）另有裸標籤路徑，屬另案（A 軌不在 litedoc、本案零碰）。
- **命名債註記（承 HOTFIX-4、純留痕不動刀）**：`en_text`／`final_..._en.md` 之「en」為 A 軌歷史命名、實際語意＝原文側（日文樣本原文裝於 en 容器）；本案 zh/en 雙側均補中和、功能零影響。
- **Revision**：
  - v2 (2026-07-24)：新增 §修法定位（P1–P4 架構）——以階段表 + P3 尾段組裝流程圖釐清「本案改 P3 尾段之交付文件組裝步、非前端、非新階段」（回應 baron「到底改 P1-P4 還是組裝給前端」之澄清）；修法本體、真因、測試計畫、commit 皆未動。
  - v1 (2026-07-24)：初版——單刀 P3 出口補中和（承 HOTFIX-4 K1、治譯後裸標籤復活）＋譯後復活/扉頁豁免/冪等/行數不變測試計畫；commit 表待 baron 回填。
