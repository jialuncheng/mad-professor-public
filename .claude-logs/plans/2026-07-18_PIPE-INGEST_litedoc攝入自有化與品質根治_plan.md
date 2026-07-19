# PIPE-INGEST litedoc 攝入自有化與品質根治 plan

> 新建 B 軌自有攝入組裝引擎（文字攝入家族共用），litedoc P1 脫離 A 軌組裝鏈借用；併治 litedoc 影子輸出之標題錯置、圖片全滅、meta 重複、雙語括號噪音、術語不一致、publisher OCR 誤植六項品質缺陷。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：litedoc 影子輸出（實證樣本 `baton/litedoc_shadow_artifacts/SpaceX_the_Sentient_Sun_shadow/`）存在六項可根治缺陷：①文件標題錯置為內文首個章節標題、②圖片全數靜默丟失（19 figure blocks → 0 張入 final_zh）、③文首 meta 塊（epigraph/byline/publisher/標題/日期/tags）於內文重複、④「譯名＝原文」雙語括號大量重複（`SpaceX (SpaceX)` ×74）、⑤同一專名多譯不一致（sentient sun 三譯）、⑥publisher 照抄 OCR 錯字（`AI6Z NEWS`）。①②③之共同根因：litedoc P1 借用 A 軌組裝鏈（`md_processor` / `json_processor`），其產物 schema 內嵌 A 軌消費假設、與 B 軌 `section_engine` slot 契約不對齊。
- **解法**：新建 `pipelines/ingestion_engine.py`——B 軌自有攝入組裝引擎（零 doc_type 字面量、route-specific 注入、比照 `section_engine` 設計原則與 `rag_indexer` 自有重寫範式），litedoc P1 切換消費；P3 譯題改以 P1 title 為唯一源；P3 `InjectionContext.constraints` 注入括號/術語約束；P1 cover-prompt 補 publisher 正規化。
- **影響**：`pipelines/litedoc_pipeline.py`（P1 組裝呼叫、P3 譯題鏈、constraints、cover-prompt 常數）＋新增 `pipelines/ingestion_engine.py` 與對應測試。A 軌 / resume / slides 零碰；無 DB schema、無合約（contracts）簽名、無 API 簽名變動。litedoc B 軌輸出內容改變（走 golden 改善豁免 + 影子 E2E，同 PIPE-LITEDOC 慣例）。

---

## §2 目標規格

1. **ingestion_engine（新模組）**：輸入＝md_cleaner 清洗後 markdown 全文 + DocAnalyzer 產出之 `*_doc_structure.json` 判型；輸出＝section 樹（tiles 前身）＋分離之 meta 產物。硬規格：
   - **title 不丟**：文件標題（首個 `#` 行）以獨立欄位交付，且**不因此從輸出中隱匿其存在資訊**（呼叫端可取得）。
   - **meta 塊分離**：依 doc_structure 判型（`title` / `authors` / `publication_info` 型行）將文首 meta 行自內文剔除、以結構化欄位交付；**判型消費不受「行連續性」限制**（非 author 型行夾雜不得使後續判型作廢）。
   - **figure block 帶可重建 content**：`{"type":"figure","src":...,"alt":...,"content":"![alt](src)"}`；caption 若判定成功則一併關聯。
   - text / table / formula 分塊行為與現行 `json_processor` 產物語意等價（table 含 `content`、formula 含 `$$ ... $$`）。
   - **零 doc_type 字面量**；文體差異（meta 判型集、特殊區塊策略）一律由呼叫端參數注入。
   - 輸出 schema 與 `TilingProcessor` 現行輸入（processed.json）相容，TilingProcessor 零改續用。
2. **litedoc P1 切換**：`_build_tiles` 改走 ingestion_engine；`MarkdownProcessor` / `JsonProcessor` 於 litedoc 路退場（import 移除）。`PDFProcessor` / `MarkdownCleaner` / `DocAnalyzer` / `TilingProcessor` 續用零改。
3. **P3 譯題單一源**：所有模式下 `translated_title` 一律源自 P1 `ctx.ingestion.title`（section 模式改走 `translate_unit(title)`，與現行 whole 模式同式）；`_extract_translated_title` slot 撈取廢除。
4. **meta 重複歸零**：final_zh / final_en 文首（HTML 扉頁之後）不再出現 epigraph / byline / publisher / 標題文字 / 日期 / tags 之重複塊（驗收以 SpaceX 樣本重跑逐項檢查）。
5. **圖片全保留**：原文 markdown 之 `![...]()` 圖片於 zh 視圖全數保留、順序與所屬 section 不變（SpaceX 樣本：19 個 figure block 全數出現於 final_zh）。
6. **括號噪音收斂——移交 GLOSSARY-TERMMAP（PIPE-INGEST-REVIEW v4·baron 選 1）**：本案**不做 interim constraints**。括號決定（`SpaceX→不加括號` 等）由 **build_termmap 定案表順帶**（與本案前後腳做、空窗幾小時）。理由：不為短空窗蓋用完即丟的 constraints（YAGNI）。
7. **術語一致——移交 GLOSSARY-TERMMAP（v4·選 1）**：本案**不處理**術語一致；④⑤ 由 **build_termmap 定案表根治**（census→去重→只翻未知→定案→注入每段），因 termmap **保證**全文一致、**「全文單一譯法」為硬驗收（在 GLOSSARY-TERMMAP、非本案）**。⚠️ 原 v3「F1 軟化＝段內一致+量測 interim」**廢除**（該軟化前提＝沒有 build_termmap；選 1 已定 build_termmap 前後腳做，不需 interim）。短空窗期間 litedoc 有括號噪音＝測試產物、build_termmap 一上即全解。
8. **publisher 正規化**：P1 cover-prompt 增補規則——輸出出版方正式名稱、修正明顯 OCR 變形（例：`AI6Z` → `a16z`）、作者姓名正規化為 Title Case。驗收：SpaceX 樣本 venue＝`a16z`。
9. **dead code 清理**：移除 `litedoc_pipeline.py` `_detect_source_lang`（L272-279、已被 HOTFIX-1 `classify_source_lang` 取代、全庫零 caller）。
10. **已知限制（本案不修、明文記錄）**：
    - **MinerU 上游**：跨頁斷句（`SpaceX_the_Sentient_Sun.md:51` 斷於 "you have to go to the"，殘片遭 MinerU 當頁眉雜訊丟棄）、圖表圖片之 OCR 散行。
    - **PDF 字型層共病**（措辭修正 per PIPE-INGEST-REVIEW F6：非 MinerU 之過）：連字壞字（Pro1les / ;rst / Grion）源於原稿 PDF ToUnicode 映射損壞，**直抽（pypdf/fitz）與 MinerU 皆現、換工具不可修**；連字修復正規化屬另案（PIPE-INGEST-FITZ 附項）。
    - **索引欄依賴（C1 覆驗·2026-07-19）**：`ingestion_engine` **不補 figure `index`**——litedoc 靠 `collect_render_slots`「原 DFS pre-order」**list 順序**消費、**不讀 `(index, part)`**（`section_engine.py:207`；`(index,part)` 兩欄屬 **A軌 `md_restore`**、litedoc 不碰）。故 tiling **bypass 模式**（短文 <5000 字）圖片缺 `index` 對 litedoc 排序**零影響**（實測 figure 本無 index 鍵、非「保留原始 index」）。⚠️ **隱含依賴**：若未來 litedoc 有 consumer 改用 `(index,part)` 排序、或 tiles 須餵回 A軌式排序，此結論失效、須改由 ingestion_engine 或 bypass 路補 figure index。
11. **後續任務銜接（本案不含、依 PIPE-INGEST-REVIEW §3.1 選 1）**：**GLOSSARY-ON + GLOSSARY-TERMMAP**（build_termmap 術語④⑤/括號根治、本案移出項的接收方）依 baron 2026-07-19 **選 1** 與本案**前後腳做**（空窗幾小時、本案不做 interim constraints·YAGNI）；**IMG-FILTER**（三規則確定性垃圾圖過濾——尺寸/長寬比/meta 區位置，位置規則複用本案 meta 分離產物）接圖片保留後開案；**PIPE-INGEST-FITZ**（born-digital 文字層 + 連字修復）另案；**LANG-DETECT** 義文進場前必做；**清詞工具** 生產後期便利·非前提；book/academic 兩路各自後續、繼承共用 build_termmap。

### §2.5 候選方案（Diverse Rollout）

架構級決策（攝入組裝歸屬），列三案：

| 方案 | 核心做法 | trade-offs（開發難易 / 對既有代碼衝擊 / 未來擴充性） |
|---|---|---|
| 方案 A（選定） | 新建 B 軌自有 `ingestion_engine`、litedoc 單獨切換 | 開發量中（新模組＋測試）；A 軌 / resume / slides 零衝擊；book / academic B 軌化直接繼承、resume 可後續遷移；比照 `rag_indexer` 前例 |
| 方案 B（否決） | 定點 patch 三處（P3 譯題改源 + `section_engine` figure 分支 + 剝除增強） | 開發量最小；但 figure 分支 patch 動到 resume 共用之 `section_engine` 消費層、且 litedoc 仍踩 A 軌組裝假設，#3 meta 分離無從根治（`authors_info` 判型作廢問題留在 md_processor）；債留原地 |
| 方案 C（否決） | 直接修 `md_processor` / `json_processor` 共用碼 | 根治面最廣；但 A 軌全文體 + resume 同時受衝擊、A 軌 golden 全面重捕；A 軌處於絞殺期、投資即將陪葬 |

- **選定理由**：A 案唯一同時滿足「根治 schema 不對齊」與「A 軌 / 前兩路零衝擊」；與 §7 所列 `rag_indexer`（B 軌自有重寫、零 import A 軌）為同一既定範式。
- **否決留痕**：B、C 案留底如上（CLAUDE.md §1.9）。

---

## §3 現況與證據

- **pipelines/litedoc_pipeline.py**：
  - `run_phase1 L123-207`：P1 全鏈——`PDFProcessor().parse`（L146）→ `MarkdownCleaner().clean`（L148）→ `DocAnalyzer().analyze`（L154、doc_type 映射 web）→ `_build_tiles`（L163）→ LLM cover-prompt 抽 metadata（L166）。
  - `_build_tiles L210-220`：`MarkdownProcessor` → `JsonProcessor` → `TilingProcessor` 三段借用鏈。
  - `_load_tiles L222-233`：讀 tiled JSON，dict 時**只取 `sections`、丟棄 `title` 欄**（實證樣本該欄躺著正確的 `'SpaceX & the Sentient Sun'`）。
  - `_resolve_title L259-270`：P1 title 三段 fallback（meta.title → 首個 `#` 行 → paper_name）——P1 title 本身正確。
  - `run_phase3 L426-535`：size-gate；section 模式 L487-494 `translated_title = self._extract_translated_title(slots, zh_by_index)`——**取第一個 title slot、完全不消費 P1 title**；whole 模式 L486 已有 `translate_unit(title)` 正確範式。
  - `L447-450 / L499-505`：pre/post 兩道 `strip_title_echo`——post 道以錯置譯題為 key 必 miss；pre 道受 cap=3 限制（實測標題位於第 4 個非空行後）。
  - `L452-458`：`InjectionContext` 組裝，`constraints` 未使用、`preceding` 未設（並行架構下無前文滑窗）。**三路對照（PIPE-INGEST-REVIEW F1 實查）**：resume 有 `_RESUME_CONSTRAINTS`（`resume_pipeline.py:128` 定義、`:548` 注入）、slides 有 `_SLIDE_CONSTRAINTS`（`slide_pipeline.py:110`），**僅 litedoc 空缺**（現況）——**本案 v4 純結構、不補 constraints**；術語④⑤/括號移交 build_termmap（GLOSSARY-TERMMAP·前後腳做）。
  - `_LITEDOC_META_SYSTEM_PROMPT L60-71`：cover-prompt 僅有 URL→publisher 解碼，無 OCR 正規化規則。
  - `_detect_source_lang L272-279`：已被 HOTFIX-1 `classify_source_lang` 取代之 dead code。
- **processor/md_processor.py**：
  - `parse L237-265`：首個 `#` 前內容全丟；首個 `#` 抽為 `result['title']`、不入 sections。
  - `L325-336`：authors 收集——**遇首個非 author_lines 行即終止**；實證樣本 epigraph（doc_structure line 2、intro_text）位於 byline（line 6、authors）之前 → 收集立即結束、`authors_info=''`、整個 meta 塊落入無標題孤兒 section。
- **processor/json_processor.py**：
  - `L154-158`：figure block ＝ `{"type","src","alt"(,"caption")}`——**無 `content` 鍵**；`L183-185` table block 有 `content`。
  - `L26-40`：figure_caption_pattern 僅認 `Figure 1:` 型式，一般圖說不匹配 → 成一般 text（孤兒圖說）。
- **pipelines/section_engine.py**：
  - `collect_render_slots L229-238`：非 text 類型僅讀 `item.get("content")`、**空即靜默丟棄** → figure 全滅。
  - `strip_title_echo L615-651`：cap=3 非空行、僅剝「標題 + ≤2 行 byline」。
- **processor/doc_analyzer.py**：
  - `analyze L58-62`：先 `_fix_heading_levels`（LLM 改寫 heading 並**寫回磁碟**、L82 `write_text`）、後 `_analyze_document_structure`（L90 重新 `read_text` 同檔）——**doc_structure 行號與 heading-fix 後 md 快照天然吻合**（2026-07-18 review #C 驗證），§4 第一條契約之同基準保證有代碼順序背書。
- **processor/tiling_processor.py**：
  - `L253-258`：分塊時自動為所有 elements 補寫 `index` / `part`（`tiling_method` 同段管線補入、實證樣本 tiled.json figure block 三欄俱在）——ingestion_engine 僅需產基礎 blocks、索引屬性由 TilingProcessor 自癒補齊（review #D 驗證）。
- **prompt/translate/content_translate_prompt.txt**：三條「地名/機構名翻譯後附上原文」「新術語括號注明」規則，無「僅首次」限制、無「同字免注」防呆（A 軌共用母 prompt、本案不動）。
- **settings.py L112**：`LLM_USE_GLOSSARY_ALIGN` 預設 false → P2 glossary={}、術語強約束區塊不注入。
- **實證中間產物**（`baton/litedoc_shadow_artifacts/`）：
  - `SpaceX_the_Sentient_Sun_shadow/*_tiled.json`：`title` 欄正確；sections[0] 為無標題孤兒節（meta 塊 10 items）；首個有標題 section＝`'Working Back from the Future'`；figure block ×19、含 `content` 鍵者 0。
  - `final_*_shadow_zh.md`：0 張圖（A 軌 final 23 張）；文首 meta 塊重複；扉頁 venue＝`AI6Z NEWS`（A 軌同鏈自癒為 `a16z`）。
  - **錯譯題汙染至 PDF `/Title`（PIPE-INGEST-REVIEW F5 新證據）**：B 軌成品 PDF（`baton/從未來逆向推導 (測試).pdf`）文件屬性 `/Title='從未來逆向推導 (測試)'` 同錯——錯譯題**三受害者**：zh 扉頁 `# 標題`／前端 HTML `<title>`（瀏覽器分頁名）／PDF `/Title`（HTML 列印帶入）。本案「譯題單一源」修正連同文件屬性層一併矯正。
  - `*_doc_structure.json`：DocAnalyzer 判型正確（line 0/14 title、6 authors、12/16-18 publication_info）——判型資訊現況被 md_processor 消費邏輯作廢。

### §3.1 grep 鋼鐵證據

```bash
# figure block 無 content 鍵（本 session 實跑）
python3 - <<'EOF'
import json
d = json.load(open('.claude-logs/baton/litedoc_shadow_artifacts/SpaceX_the_Sentient_Sun_shadow/SpaceX_the_Sentient_Sun_tiled.json'))
figs = [it for s in d['sections'] for it in s.get('content', []) if it.get('type') == 'figure']
print(len(figs), sum(1 for f in figs if 'content' in f))   # → 19 0
print(repr(d.get('title')))                                 # → 'SpaceX & the Sentient Sun'
EOF

# final 圖片數對比（本 session 實跑）
grep -c '!\[' .claude-logs/baton/litedoc_shadow_artifacts/SpaceX_the_Sentient_Sun_shadow/final_SpaceX_the_Sentient_Sun_shadow_zh.md   # → 0
grep -c '!\[' .claude-logs/baton/litedoc_shadow_artifacts/SpaceX_the_Sentient_Sun_shadow/final_SpaceX_the_Sentient_Sun_zh.md          # → 23（A 軌）

# 譯題取自第一個 title slot（非 P1 title）
grep -n "_extract_translated_title" pipelines/litedoc_pipeline.py    # → L494, L538

# _load_tiles 丟 title 欄
grep -n "sections if isinstance" pipelines/litedoc_pipeline.py       # → L232

# 同字括號噪音量化（shadow PDF 抽字實測）：拉丁 pair 107、其中原文=譯文 106（SpaceX ×74）
```

---

## §4 跨 Phase 接縫契約

本案跨 P1（攝入）／P3（翻譯還原）兩 Phase、且新增引擎為多段 handoff 樞紐，逐條凍結：

| handoff | producer（誰產 / 欄位 key 名） | consumer（誰取 / 如何 match） | key 精確身份 + 同基準保證 |
|---|---|---|---|
| DocAnalyzer → ingestion_engine | `analyze()` 產 `*_doc_structure.json`：`structure[].{start,end,type}` 行號判型 | 引擎以**行號**對照 md 行剔除/歸類 meta 行 | 行號基準＝**DocAnalyzer heading-fix 改寫完成後之同一份 md 快照**；引擎必須讀同一檔案、不得於判型後再對 md 做行級增刪 |
| ingestion_engine → TilingProcessor | 引擎產 processed 相容 JSON（`type`/`content`/`src`/`alt`） | TilingProcessor 現行輸入邏輯零改消費 | block schema＝現行 processed.json 語意等價；figure 新增 `content` 鍵為**純加法**、不改既有鍵名 |
| ingestion_engine tiles → section_engine slots | 引擎產 section 樹：`title`＝**md heading 原文文字**、figure `content`＝`![alt](src)` | `collect_render_slots` 以 `type=='text'` 翻譯、其餘讀 `content` passthrough | figure 經 `content` 鍵走現行 raw slot 路徑（section_engine **零改**）；section title 文字＝md heading 原文（不加工），P2 `section_summaries` 與 P4 `summary_key` 之「原文標題 path」基準**零位移** |
| P1 title → P3 translated_title | P1 `IngestionMetadataSpec.title`（`_resolve_title` 產、shadow 後綴 ` (測試)` 於 P1 附加） | P3 各模式一律 `translate_unit(title)`（剝 ` (測試)` 後翻譯、依現行 pre-strip 慣例） | 譯題唯一源＝P1 title 字串本體；slot 撈取廢除、**不存在第二基準** |
| P1 meta 分離產物 → P3 扉頁 | 引擎交付 authors/publication_info 結構化欄位（經 P1 併入 spec.authors / venue / raw_metadata） | P3 `_render_meta_headers` 現行讀法零改 | 欄位命名沿用現行 `IngestionMetadataSpec` + `raw_metadata` 旁路、合約零動 |

填寫規範見 `ref/WORKFLOW_SOP.md §7`（唯一權威源）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| litedoc B 軌輸出內容大幅改變（標題/圖片/meta/括號） | 🟡 中 | 影子軌不影響 A 軌交付；走 golden 改善豁免 + baron 影子 E2E（同 PIPE-LITEDOC C8 慣例）；驗收清單見 §8.2 |
| DocAnalyzer heading-fix 為 LLM 改寫、doc_structure 行號可能與引擎讀檔漂移 | 🟢 低 | 代碼順序已驗證（`doc_analyzer.py:58-62`：fix 寫回**後**才判型同檔 → 行號與快照天然吻合、review #C）；§4 契約仍凍結「同一 md 快照」防未來順序變動；引擎對行號越界 / 判型缺失 soft-fail 退化為「無 meta 分離」（不阻斷、僅回到現況行為） |
| TilingProcessor 對新增 `content` 鍵之 figure block 的行為 | 🟢 低 | figure 屬 tiling 硬邊界 passthrough（`tiling_processor.py:21` HARD_BOUNDARY）；`index`/`part` 等索引欄由 tiling 自動補寫（`tiling_processor.py:253-258`、review #D）；純加法鍵不影響既有分支；整合測試覆蓋 |
| section_engine 若需任何調整、衝擊 resume | 🟢 低 | 目標規格已定為 section_engine **零改**（figure 走既有 `content`→raw slot 路徑）；若實作中發現必須動、升級為 plan 修訂 + baron 重審 |
| constraints 文字級約束改變 litedoc 譯文風格 | 🟢 低 | constraints 僅注入 litedoc 自身 InjectionContext、不動母 prompt、不及他路；效果以 SpaceX 樣本重跑量化驗收 |
| A 軌 / resume 對 md_processor、json_processor 之既有依賴 | 🟢 低 | 兩檔零改（§6 不可動）；litedoc 僅移除自身 import |

---

## §6 不可動清單

- [ ] `processor/md_processor.py`、`processor/json_processor.py` 本體（A 軌全文體 + resume 續用、防 golden 重捕）
- [ ] `pipeline_core.py` 及 A 軌鏈全體（`md_restore_processor` / `translate_processor` / `rag_processor` 等）
- [ ] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py`（前兩路零碰）
- [ ] `pipelines/section_engine.py` 既有函式簽名與行為（目標規格為零改；任何新增必須純加法）
- [ ] `prompt/translate/content_translate_prompt.txt` 等母翻譯提示詞（A 軌共用；本案約束一律走 litedoc `InjectionContext.constraints`）
- [ ] `pipelines/contracts.py` 四凍結合約簽名（`IngestionMetadataSpec` 等欄位零增刪）
- [ ] `processor/rag_indexer.py` 與 P2→P4 `summary_key`＝原文標題 path 基準
- [ ] `processor/pdf_processor.py`、`processor/md_cleaner.py`、`processor/doc_analyzer.py`、`processor/tiling_processor.py`（工具層續用零改）
- [ ] `settings.py` `LLM_USE_GLOSSARY_ALIGN` 預設值（旗標開啟另案評估、見 §9 Q1）
- [ ] 既有 tests 斷言本體（僅允許因 litedoc 行為變更而**新增**測試或依規格更新 litedoc 自身測試）

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 跨 Phase 接縫契約規範 | `ref/WORKFLOW_SOP.md §7` |
| BE-Refactor 必讀 SOP（logging / database） | `sop/2026-05-23_logging_SOP_手冊.md`、`sop/2026-05-23_database_SOP_手冊.md`；落地前 §5 SOP 一致性核查 |
| 進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`（§4.3 logging 規格、§4.4 database 規格） |
| B 軌自有重寫範式（前例） | RAG-ASYNC `processor/rag_indexer.py`——B 軌需 A 軌能力時自有重寫、零 import A 軌 |
| 引擎設計紀律（前例） | `pipelines/section_engine.py` L8-13 設計原則——零 doc_type 耦合純函式 + route-specific 注入 |
| **母 plan 分歧宣告** | `plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`——litedoc P1「消費既有 processor、零改」（U2/U3）條款由本案取代；母 plan 更新於收官後另案（PIPE-SYNC-5）回灌 v11 |
| **SPEC 分歧宣告** | `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（v8）——需新增 ingestion_engine 契約章（比照 §1.2.5 section_engine 立法式）+ §1.1.1 litedoc 攝入鏈改寫 + #8 MinerU 已知限制；一併於 PIPE-SYNC-5 回灌 v9 |
| 品質缺陷實證 | `baton/litedoc_shadow_artifacts/`（中間產物證據附件、不入版控）+ `prompts/2026-07-18_PIPE-LITEDOC-QA_分析_提示詞.md` |
| **PIPE-INGEST-REVIEW design spec** | `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md`——F1（**廢除**·術語④⑤/括號移交 build_termmap）/ F3（GLOSSARY-TERMMAP 接收方·§2.7 硬驗收）/ F5（PDF `/Title` 汙染新證據、真實產物驗證）/ F6-F7（後續任務銜接）/ **baron 2026-07-19 選 1：build_termmap 與本案前後腳、PIPE-INGEST 純結構、不做 interim constraints** |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**：
  ```bash
  pytest tests/ -v    # 基線 748 passed、不得低於基線
  ```
- **預計新增的測試**：
  - `tests/test_ingestion_engine.py`：title 不丟／meta 塊分離（含「判型行不連續」情境——epigraph 夾於 byline 前）／figure block 帶 `content=![alt](src)`／table、formula 語意等價／doc_structure 缺失或行號越界之 soft-fail 退化／零 doc_type 字面量（源碼掃描式斷言、比照 section_engine 慣例）／TilingProcessor 相容（產物直餵 tiling 不炸）。
  - `tests/test_litedoc_pipeline.py`（既有檔擴充）：P3 譯題唯一源自 P1 title（section 模式斷言不再讀 slot）／post-strip 以正確譯題 key 生效／cover-prompt publisher 正規化（mock LLM 驗 prompt 規則存在）。（constraints 注入斷言移除——v4 本案不做 constraints、術語括號歸 GLOSSARY-TERMMAP）
  - **§7.2 跨 Phase 整合測試**（Checkout 必驗）：cleaned md（含 meta 塊 + 圖片 + 多 section）→ ingestion_engine → tiles → `collect_render_slots` → mock 翻譯（**key-changing transform**：譯文≠原文）→ 組裝；斷言：figure 全數穿透至輸出、標題不入內文、meta 塊不重複、P2 `summary_key` 以原文標題 path 可對位查得。

### §8.2 手動端到端（E2E）驗證流程（baron、測試服）

1. 重新上傳 `SpaceX & the Sentient Sun.pdf` 走 litedoc 影子軌。
2. 檢查閱讀視圖（zh）逐項（**結構項**）：標題＝「SpaceX 與有感知的太陽」系（非「從未來逆向推導」）、**瀏覽器分頁名（HTML `<title>`）同步正確**；圖片全數顯示（≥19 張）；扉頁後無 epigraph/byline/publisher/日期/tags 重複塊；扉頁 venue＝`a16z`。若由閱讀視圖列印 PDF，抽查 PDF `/Title` 屬性同步正確（標題單一源·結構項）。
3. **術語④⑤/括號——不在本案驗收（移交 GLOSSARY-TERMMAP·前後腳做）**：本案（純結構）不驗術語一致/括號噪音；由 build_termmap 定案表根治後、於 GLOSSARY-TERMMAP 硬驗收「全文單一譯法」。短空窗期間 litedoc 括號噪音＝測試產物、不阻本案驗收。
4. 抽查另一 litedoc 樣本（如 `The_hidden_risks_in_Taiwan_s_boom`）確認無新退化。
5. 檢查 RAG 問答一輪，確認 chunks 量級與章節摘要對位無退化（P4 零改之迴歸確認）。

---

## §9 Open Questions

> **六項均已於 2026-07-18 由 baron 拍板、全數採納推薦方案**（review 併四項代碼驗證 #A-#D 全數吻合）；本節留痕為決策紀錄、後續 tasks 拆分直接引用。

| 開放問題 | 拍板方案（✅ 定案） | 理由 |
|---|---|---|
| Q1：術語一致性是否連動開啟 `LLM_USE_GLOSSARY_ALIGN`？ | ✅ **本案不開旗標、亦不做 interim constraints**（純結構）。**更新（2026-07-19 PIPE-INGEST-REVIEW·選 1）**：原 v3「本案 constraints 治理 / glossary 後移五路」**修正**——baron 選 1：**build_termmap（GLOSSARY-TERMMAP）與本案前後腳做**（空窗幾小時），術語④⑤/括號**移交** build_termmap；旗標由 GLOSSARY-ON 前後腳開；本案純結構不碰術語 | 旗標為全域 gate（`translator._build_system_prompt` 讀取、涉及 GlossaryManager DB 寫入與所有翻譯呼叫），影響面跨五路；測試期 DB 可丟、壞了清庫即可（清詞工具屬生產後期便利、非前提） |
| Q2：引擎歸屬——獨立 `pipelines/ingestion_engine.py` vs 併入 `section_engine` | ✅ **獨立新模組** | 與 resume 消費之 section_engine 物理隔離、審計與回歸面最小；職責亦不同（攝入組裝 vs 翻譯還原）；未來 book/academic 接入時 import 邊界清晰 |
| Q3：figure caption 翻譯策略 | ✅ **沿用現況**——caption 行若為一般 text 塊即自然翻譯，不另走 caption prompt | 現況 A 軌樣本顯示一般圖說已以 text 身分正常翻譯；另接 caption prompt 增加分支、收益未證 |
| Q4：`_extract_translated_title` 廢除 vs 降級 fallback | ✅ **廢除**（P1 title 為唯一源；`_resolve_title` 已保證非空） | 保留雙源即保留回歸空間（本次缺陷即雙源不同基準所致）；接縫契約單一基準原則 |
| Q5：`_detect_source_lang`（litedoc_pipeline L272-279）dead code 是否順手移除 | ✅ **是，本案內移除**（已列入 §2 目標規格第 9 條） | HOTFIX-1 已以 `classify_source_lang` 取代、全庫零 caller；留置徒增誤用風險 |
| Q6：resume 遷移 ingestion_engine 的觸發條件 | ✅ **登記 TODO 候選：book 路開案時**一併評估（第二 consumer 驗證時點） | resume 現況未引爆（Vision md 無圖、標題有 metadata_extractor 自源）、零急迫；屆時引擎契約已被 litedoc 實戰驗證 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-INGEST litedoc 攝入自有化與品質根治的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 PIPE-INGEST tasks / 執行報告；PIPE-SYNC-5 回灌案 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md；ingestion_engine 落地後之長期契約權威源為 PIPE-SPEC（PIPE-SYNC-5 回灌後） |

### §99.2 Revision 歷程

- v4 (2026-07-19)：PIPE-INGEST-REVIEW **選 1** 回灌——**§2.6/§2.7 interim constraints 移除**、術語④⑤+括號**移交 build_termmap（GLOSSARY-TERMMAP）**、與本案**前後腳做**（空窗幾小時·YAGNI 不為短空窗蓋臨時鷹架）；**F1「軟化 §2.7」路線廢除**、§2.7「全文單一譯法」改為 build_termmap 之**硬驗收**（termmap 保證）；§8.2 移除括號≤1次+術語量測 interim（本案僅驗結構項）；§2.11/§9 Q1 更新（glossary **非後移五路**·build_termmap 前後腳·清詞工具生產後期非前提·測試期清庫即可）；**PIPE-INGEST 定位＝純結構化**（標題/meta/圖片/publisher/dead-code）
- v3 (2026-07-19)：依 `baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` 回灌——§2.7 術語一致硬驗收軟化為「section 內一致 + constraints + 全文量測報告」（F1、拉平三路家族能力、constraints=補齊 resume/slides 同級）；§2.10 已知限制拆分「MinerU 上游」與「PDF 字型層共病」（F6 措辭修正、連字壞字換工具不可修）；新增 §2.11 後續任務銜接（IMG-FILTER 接圖片保留後 / PIPE-INGEST-FITZ 另案 / glossary 線後移至五路完成後）；§3 補三路 constraints 對照與 PDF `/Title` 汙染新證據（F5 三受害者）；§8.2 E2E 增分頁名檢查與術語量測報告步驟、移除全文唯一硬判；§7 增 design spec 依據列；§9 Q1 補 baron 兩階段決定註記
- v2 (2026-07-18)：review 定稿——§9 六 OQ 全數拍板採納推薦（Q1 不開旗標 / Q2 獨立模組 / Q3 caption 沿用 / Q4 廢除 slot 撈題 / Q5 移除 dead code / Q6 resume 遷移登記候選）；§2 增第 9 條 dead code 清理目標；§3 補 doc_analyzer 順序（fix 寫回後判型同檔、行號同基準有代碼背書）與 tiling 自動補欄兩證據（review #C/#D）；§5 行號漂移風險 🟡→🟢
- v1 (2026-07-18)：初版——依 PIPE-LITEDOC-QA 分析（九項缺陷歸因 + `litedoc_shadow_artifacts` 中間產物實證）立案；§2.5 三候選擇定 B 軌自有攝入組裝；§4 凍結五條 handoff 契約；§7 宣告母 plan v10 / PIPE-SPEC v8 分歧待 PIPE-SYNC-5 回灌
