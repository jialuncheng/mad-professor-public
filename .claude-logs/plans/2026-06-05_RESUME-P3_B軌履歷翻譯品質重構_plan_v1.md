# RESUME-P3 B軌履歷翻譯品質重構 plan

> 定義 PIPE-RESUME v9 B軌（影子）P3 翻譯階段的品質目標規格：消除整檔單次翻譯（100% Bypass）造成的結構行漏翻、原文/譯文重複、技術詞翻譯不一致，使 B軌履歷雙語輸出品質對齊 A軌水準。純規格、不含實作細節。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：B軌（`pipelines/resume_pipeline.py::run_phase3`）對履歷採「100% Bypass：整份 .md 一次性丟給 LLM 翻譯、譯文直寫、不切 Section、不做結構還原」（C4 設計）。實測多段（公司名、學歷、關鍵技能）品質系統性低於 A軌逐區塊翻譯：結構標題行漏翻、原文行與譯文行重複、技術詞翻譯不一致、地點行錯亂。
- **解法**：將 B軌 P3 由「整檔單發」改為**逐 heading section（`###`）翻譯 + 結構還原**（對齊 A軌 `translate_processor` 已驗證的 per-section/per-item 模式），翻譯單元＝`md_processor` 的 heading section（標題/正文/caption 分流），重組雙語 Markdown。**履歷 opt-out TextTiling**：P3 不消費 TextTiling 後的 char-split tiles，履歷不套用字數門檻、純 `###` 區塊翻譯（戰術 opt-out，通用化機制歸 INFRA-3）。prompt 層矛盾（公司/技能詞）已由 SHADOW-HOTFIX-2 收斂、本任務對齊其結果。
- **影響**：僅改 B軌 `pipelines/resume_pipeline.py::run_phase3`（及其私有輔助、P1 履歷 tiling opt-out）與翻譯單元拼接；可能新增 `pipelines/` 內部還原輔助。**不動** A軌、不動 `contracts.py` 凍結合約欄、不動 `translator.py` 雙模式引擎核心、不動 `TilingProcessor` 演算法本體、不動 P4 RAG 切 chunk（`MarkdownHeaderTextSplitter` 獨立）、不動 DB Schema。旗標/影子隔離下線上 0 風險（B軌僅影子驗證）。**改 B軌輸出 → 須重捕 Golden（與 TILING/SHADOW-HOTFIX-2 合併一次）**。

---

## §2 目標規格

本次改動必須達到的「最終狀態」（可量化、可檢驗）：

- **U1 結構標題不漏翻**：履歷各層 Markdown 標題（如 `# Key Skills`、子段標題）在 B軌中文輸出中均被翻譯（標題政策對齊 A軌 `translate_section_titles`），無整行英文標題殘留。
- **U2 無原文/譯文重複**：B軌中文輸出**不得**同時保留原文行與譯文行（學歷段 doubling 歸零）；每個來源單元對應單一譯文單元。
- **U3 地點/多行結構不錯亂**：地名、日期、巢狀條列維持原始行結構，不因譯文行數壓縮而合併或前後綴錯置。
- **U4 公司/機構翻譯一致**：公司、機構、大學名稱統一「中文 (原文)」（對齊母提示詞 `content_translate_prompt.txt` L5），不留英文原文。
- **U5 技術詞保留一致**：技術名詞（display algorithms / R&D / technology roadmaps / ISP / DNN 等）與技能工具詞（Python/Docker 等）一致**保留英文**，不被過度翻譯（對齊 A軌觀感）。
- **U6 A軌對齊度可量測**：同一履歷 B軌 vs A軌（或 vs 重捕 Golden Baseline）的譯文相似度 D2 ≥ 0.95、結構一致；以 `tools/golden_baseline.py diff` 裁決。
- **U7 契約與隔離不變**：`run_phase3` 仍交付既有凍結合約 `BilingualMarkdownSpec`（欄位不變）；A軌 byte 不動；影子隔離與旗標行為不變。
- **U8 履歷 opt-out TextTiling、翻譯單元＝heading section**：履歷 P1/P3 **不執行 TextTiling embedding 切塊**、**不套用** `TILING_BYPASS_CHAR_LIMIT(5000)` / `TILING_MAX_LENGTH(2500)` / `TILING_PARAGRAPH_THRESHOLD(30000)`；翻譯/還原單元為 `md_processor` 的 `###` heading section（含巢狀 children）。此舉同步消滅履歷的 TextTiling embedding 429 來源（TILING-HOTFIX-1 根源）。

---

## §3 現況與證據

- **`pipelines/resume_pipeline.py`（B軌 P3、受災主體）**：
  - `run_phase3 L443-509`：100% Bypass——`L461 full_text = self._read_source_text(ctx)` 取整份 .md，`L480 Translator().translate(full_text, inj, NORMAL, "content")` **一次翻整檔**，`L492 zh_path.write_text(zh_text)` **原文/譯文直寫、無結構還原**。
  - `_RESUME_CONSTRAINTS L108-113`：履歷專屬約束（公司保留矛盾已由 SHADOW-HOTFIX-2 移除、改產品-only）。
- **Tiles 消費現況（關鍵：P3 現未吃 tiles）**：
  - `run_phase3` 翻譯讀的是 **`.md` 原檔**（`_read_source_text` → `output_dir/<stem>.md`），**非** `ctx.ingestion.tiles`。
  - `ctx.ingestion.tiles` 目前僅在 `_read_source_text` 讀 .md **失敗時的 fallback**（`resume_pipeline.py:375-376 _tiles_to_text`）被消費。
  - P4 RAG 用 `MarkdownHeaderTextSplitter` 讀**最終 .md** 切 chunk（`rag_processor.py:6`）、亦不吃 tiles。
  - → 履歷的 P1 TextTiling embedding 切塊**目前無實質下游**；DeHunt 等 >5000 字履歷會觸發 TextTiling，但對 P3 翻譯**無任何影響**（doubling 純由 P3 整檔翻譯造成，與 tiling 無關）。本任務改 P3 吃 heading section 後，履歷 P1 應一併 opt-out TextTiling（U8）。
- **`processor/translator.py`（共用引擎）**：
  - `translate() L157-196`：單次 LLM 呼叫；`U4 L188-193` 當「譯文行數 < 原文行數」時按 `。！？` 重切——對英文/結構化履歷幾乎切不動 → 行結構壓縮、地點錯亂。
  - `_STYLE_HINTS['resume'] L40`：A軌 `translate_processor.py:235` 的逐字複製殘渣，與母提示詞反向覆寫。
- **`prompt/translate/content_translate_prompt.txt`（A/B 共用母提示詞）**：
  - `L3 姓名不翻 / L4 地名翻譯附原文 / L5 機構名稱翻譯附原文`：通用政策正確，A軌好結果來源。
- **`processor/translate_processor.py`（A軌、品質對照基準、即將捨棄）**：
  - `translate_section_content L142-170`：`for section → for item` **逐單元** `translate_text`、結果寫 `item["translated_content"]`。
  - `translate_section_titles L87-98`：**逐標題**翻譯。
  - → A軌每個翻譯單元小而明確、結構保全後 md_restore 重組，故公司/學歷/技能段乾淨。

### §3.1 grep 鋼鐵證據

```bash
$ grep -nE "def run_phase3|Translator\(\)\.translate|full_text|write_text" pipelines/resume_pipeline.py
443:    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
461:        full_text = self._read_source_text(ctx)
480:            zh_text = Translator().translate(full_text, inj, TranslateMode.NORMAL, "content")
492:        zh_path.write_text(zh_text, encoding="utf-8")          # 整檔譯文直寫、無結構還原

$ grep -nE "translate_section_content|translate_section_titles|for item in section" processor/translate_processor.py
87:    def translate_section_titles(self, sections):
142:    def translate_section_content(self, sections):
149:                    for item in section["content"]:          # A軌逐單元翻譯

$ grep -nE "U4 多行|original_lines|re.sub" processor/translator.py
188:        # U4 多行重分行容錯：原文多行但譯文行數較少時、按句末標點重分行
193:                translated = re.sub(r"([。！？])\s*", r"\1\n", translated).strip()

$ grep -nE "機構名稱翻譯|地名翻譯|姓名不要翻譯" prompt/translate/content_translate_prompt.txt
3:姓名不要翻譯
4:地名翻譯後要附上原文
5:機構名稱翻譯後要附上原文
```

---

## §4 不可動清單

- [ ] **A軌全鏈**（`pipeline_core.py` resume 分支、`processor/translate_processor.py`）— byte 不動（棄修中、不得連帶改）。
- [ ] **`pipelines/contracts.py` 四凍結合約**（`BilingualMarkdownSpec` 欄位）— 不改（P3 交付欄不變）。
- [ ] **`processor/translator.py` 雙模式引擎核心**（`translate()` 雙模式路由 / `_build_system_prompt` 五步骨架）— 不重構（僅可在 resume 範疇調整 `_STYLE_HINTS['resume']` 與 U4 對 resume 的適用，屬 §7 開放問題裁決）。
- [ ] **`prompt/translate/content_translate_prompt.txt`** — 不動（A/B 共用、L3-L5 已正確）。
- [ ] **`processor/tiling_processor.py` TextTiling 演算法本體** — 不改（履歷僅 opt-out 不呼叫、不動演算法；通用化歸 INFRA-3）。
- [ ] **`processor/rag_processor.py` P4 RAG 切 chunk**（`MarkdownHeaderTextSplitter`）+ embedding 參數 — 不動。
- [ ] **`models.py` / `db.py` / 既有 API 與前端** — 不動。
- [ ] **P2/P4**（`run_phase2/4`）與 `ctx.raw_metadata` 穿線 — 不動；**P1（`run_phase1`）僅限履歷 tiling opt-out 閘門**（U8/Q3）、其餘 ingestion 步驟不動。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流定義 / 六階段 / SOP 核查 | `ref/WORKFLOW_SOP.md §1 / §3 / §5` |
| 專案進度管控框架（雙軌制 / plan 結構） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 / §4.1` |
| logging / database SOP（落地前強制） | `sop/2026-05-23_logging_SOP_手冊.md` / `sop/2026-05-23_database_SOP_手冊.md` |
| Golden Baseline 三維度裁決（D2 ≥ 0.95） | `tools/golden_baseline.py`（GOLDEN-BASELINE） |
| B軌 P3 既有設計（100% Bypass 來源） | `plans/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（C4 §2 U4） |
| 母 plan 五路與翻譯隔離原則 | `baton/2026-06-01_PIPE-SPEC_…_specification.md §1.2.3.1` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**：
  ```bash
  venv/bin/python -m pytest tests/ -q   # 防 Regression（既存 env flake 不計）
  ```
- **預計新增測試**（`tests/test_resume_pipeline.py`）：
  - 結構標題翻譯：mock 翻譯下，斷言各層標題單元均經翻譯（無整行英文標題殘留）。
  - 無 doubling：斷言單一來源單元 → 單一譯文單元（無原文行回顯）。
  - 公司/機構翻譯 + 技術詞保留：以小型 fixture 斷言公司走「中文 (原文)」、技術詞保英文。
  - 契約不變：`run_phase3` 仍回 `BilingualMarkdownSpec`、欄位齊備。

### §6.2 手動端到端（E2E）驗證流程

1. 上傳 `DeHunt_CTO_Tzung-Yuan_Lee.pdf`（既有 fixture），啟用影子（`SHADOW_LAUNCH_ENABLED`）。
2. 檢視 B軌（測試）中文 Markdown：學歷段單一譯文行、無原文重複、地點不錯亂（對應 U2/U3）；公司「中文 (原文)」（U4）；技能段標題已翻、技術詞保英文（U1/U5）。
3. 以 `venv/bin/python tools/golden_baseline.py diff` 對 B軌 vs 重捕 Golden Baseline 裁決 D2 ≥ 0.95、結構一致（U6）。
4. 確認 A軌正本輸出 byte 不變、影子隔離與前端列表 (測試) 顯示不受影響（U7）。

---

## §7 Open Questions

> **✅ baron 拍板核准（2026-06-05、階段 3 驗證）**：Q1/Q2/Q3/Q4/Q9/Q10 核准採推薦方案（見下）；Q5（tiles 稽核）/Q7（範疇僅 resume）/Q8（重捕 golden）採推薦；Q6（SHADOW-HOTFIX-2）已落地 `3d2778a`。**全數結案 → 本 plan 可進階段 2 拆 tasks。**
> - **Q1 粒度**：✅ 逐 heading section 翻譯、廢除 100% Bypass（最利結構化履歷語意完整）。
> - **Q2 代碼解耦**：✅ 在 `pipelines/` 內獨立重建輕量逐單元拼接、不耦合將棄的 A 軌 `translate_processor`（避免架構債）。
> - **Q3 Tiling Bypass**：✅ 履歷 P1 強制 bypass TextTiling（避免攪亂標題結構 + 源頭滅 429）、P3 直接以標題切分與還原。
> - **Q4 停用 U4**：✅ resume 停用 `translator.py` 的 `。！？` 重切（U4）、保留條列式行結構與日期/地點對齊。
> - **Q9 退化 Fallback**：✅ 履歷退化為單一巨型 section 時設計降級防護、保障極限情況仍可完整翻譯。
> - **Q10 邊界劃分**：✅ 本任務先對履歷戰術性 bypass；通用化動態 Tiling 開關交 INFRA-3。

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| Q1 翻譯粒度：整檔單發 vs 逐單元？ | **逐單元（per-section/per-item）+ 結構還原**，廢除 run_phase3 的 100% Bypass | A軌逐單元（`translate_processor` L142-170）已驗證能產生乾淨的公司/學歷/技能輸出；小單元語意明確、降低 LLM hedging 與整檔重排；U4 行壓縮問題消失。整檔單發是品質系統性差的根因。 |
| Q2 逐單元邏輯：直接重用 A軌 `translate_processor` vs 在 B軌新架構內重建？ | **在 `pipelines/` 內重建輕量逐單元翻譯/還原**，消費 `processor/translator.py` 引擎，不 import 即將捨棄的 `translate_processor` | A軌全鏈將隨五路改完捨棄，直接 import 會產生對 dying code 的耦合；B軌應擁有自己的結構化翻譯流程，僅復用「Translator 引擎 + Tiles 結構」兩個長期資產。 |
| Q3 翻譯輸入來源：整份 .md vs char-split tiles vs heading section？ | **改吃 heading section（`md_processor` 的 `###` 結構、TextTiling 之前）**；履歷 P1 **opt-out TextTiling**、不消費 char-split tiles | tiles 是 TextTiling **之後**的 char-split 產物（>5000 觸發語意切），對履歷無實質下游且自找 429；履歷只需 `###` 區塊。改吃 heading section（structured.json / 履歷 tiling 永遠 bypass）即天然保全標題/段落邊界、單元語意完整、無 char 門檻干擾。**實作偏好**：履歷 P1 對 `doc_type=='resume'` 強制 tiling bypass（改動最小、順帶滅 429）。 |
| Q4 `translator.py` U4 重分行對 resume 是否停用？ | **resume 路徑停用 U4 的 `。！？` 重切**（或改為不依賴中文句末標點的對齊） | U4（L188-193）為中文長句設計，對英文/條列式履歷切不動、反而壓縮行結構造成 §U3 錯亂；逐單元翻譯後本就行對行、不需 U4。 |
| Q5 prompt 雙管道（②STYLE_HINTS / ⑤constraints）是否在此收斂？ | **本任務內收斂 resume 的矛盾**（公司交回母提示詞、技術詞範圍對齊），但**不拆整個 STYLE_HINTS 機制**（academic/book 仍用） | 與本任務「翻譯品質」同源、應一併解；但全域拆 STYLE_HINTS 屬更大架構債，超出 resume P3 範疇，留待 A軌死後另議。 |
| Q6 與 SHADOW-HOTFIX-2 的關係？ | **SHADOW-HOTFIX-2 已落地**（`3d2778a`：title (測試) + 公司矛盾移除）；本 plan U4/U5 **對齊其結果**、聚焦結構性品質（U1-U3/U8） | hotfix 已快速止血（title 顯示 + 公司翻譯），公司/技能詞矛盾已收斂；本任務不重做 prompt 矛盾、只處理需重構的結構問題（逐 heading 翻譯 + opt-out tiling）。 |
| Q7 範疇：僅 resume 還是含其他四路？ | **僅 resume（B軌 run_phase3 + 履歷 P1 tiling opt-out）** | 100% Bypass 是 resume P3 專屬決策（C4）；其他路 P3/chunking 策略不同、各有 plan，不在本任務一併處理（避免範疇蔓延）。 |
| Q8 Golden Baseline 基準：vs A軌 還是 vs 重捕 golden？ | **vs 重捕 golden**（A軌死後 golden 即新真理源） | A軌即將捨棄、不宜當長期基準；改善後須重捕 golden（**與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 的重捕合併一次**），之後比對以 golden 為準。 |
| Q9 fallback：heading 抓不到（履歷無 `#`）怎麼辦？ | **heading 退化偵測**：section 數異常少 / 單一巨 section（= heading 沒抓到）→ 退回整檔翻譯或先補 heading；依賴 P1 `DocAnalyzer` heading fix 品質 | 履歷常用粗體/全大寫當標題、非 `#` → `md_processor ^(#+)` 抓不到 → 塌成單一巨 section、逐單元退化為整檔（doubling 回歸）。fallback 不是「tiling 失敗」而是「heading 退化」，tasks 須加偵測 + 退路。 |
| Q10 與 INFRA-3 的邊界？ | **本任務做 resume 戰術 opt-out**（履歷 P1 tiling bypass）；**通用化機制歸 INFRA-3**（各路 chunking opt-in、五路收完+A軌死後執行） | RESUME-P3 是翻譯品質即時需求、可先做；履歷 opt-out 為個案實作，INFRA-3 之後將其收斂為全五路統一的 opt-in 機制（見 `baton/2026-06-05_INFRA-3_…_plan_v1.md`）。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RESUME-P3 B軌履歷翻譯品質重構的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 RESUME-P3 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v3 (2026-06-05)：**baron 拍板核准 §7 Open Questions（階段 3 驗證）**——Q1 逐 heading section 廢 Bypass / Q2 pipelines/ 內重建不耦合 A 軌 / Q3 履歷 P1 強制 bypass TextTiling + P3 以標題切分還原 / Q4 resume 停用 U4 重切 / Q9 單一巨 section 退化降級防護 / Q10 戰術 bypass、通用化歸 INFRA-3；Q5/Q7/Q8 採推薦、Q6 已落地 `3d2778a`。全數結案 → 可進階段 2 拆 tasks。
- v2 (2026-06-05)：調查補強 5 點——①§1/§2 明訂「逐 heading section 翻譯 + 履歷 opt-out TextTiling」（新增 U8、字數門檻對履歷 N/A）；②§3 補「P3 現讀 .md 非 tiles、tiles 僅 fallback、DeHunt >5000 觸發 TextTiling 但對 P3 無效」現況；③Q3 由「吃 char-split tiles」改正為「吃 heading section / 履歷 P1 tiling bypass」；④新增 Q9（heading 退化偵測 fallback）+ Q10（與 INFRA-3 邊界：本任務戰術 opt-out、通用化歸 INFRA-3）；⑤Q6 更新 SHADOW-HOTFIX-2 已落地 `3d2778a`、§4 補 TilingProcessor 演算法/P4 RAG 不動、P1 僅履歷 tiling opt-out 例外。
- v1 (2026-06-05)：初版建立——B軌 P3 100% Bypass 整檔單發致公司/學歷/技能段翻譯品質系統性低於 A軌；目標規格 U1-U7；現況附 grep 證據（run_phase3 vs translate_processor 逐單元）；Open Questions Q1-Q8。
