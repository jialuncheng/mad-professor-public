# PIPE-SYNC-3 slides 路落地經驗回灌母 plan 與 SPEC — plan

> 將 slide hotfix 全集（PIPE-SLIDES-HOTFIX-1~6 + RAG-12-HOTFIX-1）之落地經驗與更正，回灌兩大真理源（PIPE master plan v10 / PIPE-SPEC）。同 PIPE-SYNC-2 對 resume 路之回灌、輕量版（D1-D7：3 必改〔D1/D2/D6〕+ 2 補〔D3/D4〕+ 2 小/可選〔D5/D7〕、僅動 SPEC + master plan 兩檔）。純文件治理（DOC-Refactor）。**含「四層交接 + 旁路」對稱性補全**（D6 rag_sections 旁路登記）。

---

## §0 改版規則
- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：slides 路（B 軌 SlidePipeline）自 PIPE-SLIDES 收官後歷經 7 次 hotfix（HOTFIX-1~6 + RAG-12-HOTFIX-1），暴露並更正了多項與兩真理源不一致之處——其中 **2 項為真理源錯誤/drift**（D1 SPEC 仍寫 slides P3「100% Bypass」、D2「B 軌另捕」之 A/B 軌 golden 混淆只進了 hotfix 文件未進真理源），若不回灌，**下一路 PIPE-ACADEMIC 等會被 SPEC 誤導重蹈覆轍**。
- **解法**：DOC-Refactor 就地回灌兩真理源——SPEC（`baton/2026-06-01_PIPE-SPEC_..._specification.md`）+ master plan v10（`plans/2026-06-01_PIPE_..._plan_v10.md`），HTML 註解包裹、不變動四凍結合約欄位結構、不 bump master 主版本（SPEC bump v6→v7、對齊 sync 慣例）。
- **影響範圍**：100% DOC-Refactor、零業務代碼、零 .py、零 golden（且本案正是釐清 golden）；僅兩真理源文件。
- **不可動清單**：見 §6。

---

## §2 目標規格

達成下列可檢驗最終狀態（U1=D1…U5=D5、U7=D6、U8=D7）：

1. **U1🔴（D1 drift 矯正）**：SPEC §1.3 五路策略表 `SlidePipeline` 列之 P3 欄由 **`100% Bypass 一鍵`** 更正為 **`逐頁翻譯與排版還原`**（對齊 PIPE-SLIDES C4 現實 + master plan v10 補註⁷ L70/L258；消除 SPEC↔master plan↔現實三方矛盾）。
2. **U2🔴（D2 A/B 軌 golden 釐清·進真理源）**：
   - master plan v10 §8.5 PIPE-SLIDES 條目「Golden Diff 通過（**B 軌另捕**、改善豁免＝plan Q8）」措辭更正——**`capture` 僅捕 A 軌（`PipelineCore`/`slides_processor`、正本基準）；B 軌不另捕、走「B 軌 shadow 輸出 diff A 軌 golden + 改善豁免」**。
   - SPEC 加一處 golden A/B 軌權威釐清（§1.3.1 #3 golden 段或 §2.4 golden 處）：**`golden_baseline.py capture <route>` 一律捕 A 軌舊單體;B 軌策略管線之變更不需、亦無法經 `capture` 重捕 A 軌 golden（A 軌未變）→ B 軌驗證走影子 E2E + diff A 軌 golden**。承 PIPE-SLIDES-HOTFIX-6 之回溯更正。
3. **U3🟡（D3 alt LaTeX 跨軌契約）**：SPEC R3.2（alt 對齊根除雙 Caption）後補跨軌契約註——**圖說 alt 可能含 LaTeX `$...$` / 特殊字元 `][()` → 前端 `renderMarkdownWithMath` 須抽 math 前保護 markdown 圖片整段（RAG-12-HOTFIX-1）、B 軌 P1 `_safe_alt` 全形化 `][()`+換行（HOTFIX-2）防破圖**（B 軌 alt 產出 ↔ 前端渲染之 handoff 不變式）。
4. **U4🟡（D4 is_blank 頁面類型判定）**：SPEC §1.3.1 補一原則 或 L242（is_cover 處）補一行——**Vision 輸出 `is_blank`：空白/裝飾/純過場/章節分隔頁（含被賦予「過場/Transition」標題之過場頁）→ is_blank=true → 管線跳過該單位；含真實圖表/資料/條列正文一律 false**（HOTFIX-4 引入 + HOTFIX-5 放寬「is_blank 且 markdown_content 空即跳」+ prompt 釐清）。與既有 is_cover 對稱。
5. **U5🟢（D5 清洗層·可選、見 §9 Q4）**：SPEC SlidePipeline 列或 §1.3.1 一行帶過「**B 軌 P3 render 含專屬清洗層**（母片日期單頁/雙Caption/點群節奏/行內粗體/裸URL/title echo/段落 `\n\n` 正規化）」——altitude 偏低、是否收錄待 baron 拍板。
6. **U7🔴（D6 rag_sections 旁路登記·對稱補全）**：SPEC §1.1 新增 **§1.1.2 `PipelineContext.rag_sections`（P3→P4 旁路欄、五路共用）**——對稱 §1.1.1 raw_metadata：**P3 產譯後 section 結構（`summary_key`＝原文標題 path／slides `page_key`）、P4 `rag_indexer` 消費自生 Strategy B 分塊；非凍結合約欄、屬 `PipelineContext` 可變狀態層（同 raw_metadata/pdf_path/owner_id）**。承 RAG-ASYNC C6;治本「真 P3→P4 交接物只散在 §1.4.1 功能描述、未在『四合約+旁路』登記表、與 raw_metadata §1.1.1 不對稱」。
7. **U8🟢（D7 rag_tree_json 點名·極小）**：SPEC §1.1③ `BilingualMarkdownSpec` 之「對應 JSON 節點」含糊處，點名為 **`rag_tree_json`（可選欄、對齊 contracts.py 實際欄位）**——消除合約③ 文件與 contracts.py 之微小指稱落差。
8. **U6（治理）**：SPEC bump v6→v7、master plan 加補註⁸（不 bump 主版本、對齊 PIPE-SYNC-2 慣例）；HTML 註解包裹（`<!-- === [PIPE-SYNC-3 ...] === -->`）；**四凍結合約「型別欄位結構」零變動**（U7 為 §1.1 旁路登記文件、U8 為既有 contracts.py 欄位之文件點名，皆不改 contracts.py 程式、不改凍結欄位）。

---

## §3 現況與證據

### §3.1 回灌清單（findings 對照）

| # | 檔案:行 | 現況（grep 實證） | 應為 | 來源 hotfix |
|---|---|---|---|---|
| D1 | SPEC L134 | `\| SlidePipeline \| slides \| Vision 每頁，無 cleaner \| 100% Bypass 一鍵 \| ≥ 3 \|` | P3 欄＝`逐頁翻譯與排版還原` | PIPE-SLIDES C4 |
| D2 | master plan L258 | 「Golden Diff 通過（**B 軌另捕**、改善豁免＝plan Q8）」 | capture 捕 A 軌、B 軌走 diff + 改善豁免、無另捕 | HOTFIX-6 |
| D2 | SPEC §1.3.1 #3 (L147) / §2.4 | 無 A/B 軌 capture 釐清（僅 golden 重捕清快取通則） | 加 golden A/B 軌權威釐清 | HOTFIX-6 |
| D3 | SPEC R3.2 (L210) | 「強制對齊 native alt…根除雙 Caption」、無 alt 特殊字元後果 | 補 alt LaTeX/`][()` 前端保護 + _safe_alt 契約 | RAG-12-HOTFIX-1 + HOTFIX-2 |
| D4 | SPEC §1.3.1 / L242 | 只記 `is_cover==false → title 置空` | 補 `is_blank` 判定 + 跳過規則 | HOTFIX-4/5 |
| D5 | SPEC SlidePipeline 列 | 無清洗層描述 | （可選）一行帶過 B 軌 P3 清洗層 | HOTFIX-2/3c/3d/6 |
| **D6** | **SPEC §1.1（旁路登記）** | 僅 §1.1.1 登記 `raw_metadata`;**`rag_sections` 無對等 §1.1.x 登記**（只在 §1.4.1/zh edge path 功能性提及） | 新增 §1.1.2 `PipelineContext.rag_sections`（P3→P4 旁路、五路共用、對稱 §1.1.1） | RAG-ASYNC C6 |
| **D7🟢** | **SPEC §1.1③ (L66)** | 「與對應 JSON 節點」含糊（contracts.py 實為 `rag_tree_json` 欄） | 點名 `rag_tree_json`（可選欄） | — |

> **旁路稽核結論**：contracts.py 四凍結合約「型別欄位」皆最新（venue/doi＝META-NORM C3、section_summaries＝RAG-ASYNC C2、domain_name＝TRANSLATOR C1）、與 SPEC §1.1 一致、無 drift;context.py 旁路 4 欄（pdf_path/owner_id＝編排輸入、raw_metadata＝§1.1.1 已登記、**rag_sections＝未登記**）→ 唯一缺口＝rag_sections 旁路（D6）。

### §3.2 grep 鋼鐵證據
```bash
SPEC=".claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md"
PLAN=".claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md"
sed -n '134p' "$SPEC"          # D1：SlidePipeline 列 100% Bypass 一鍵（stale）
sed -n '208,211p' "$SPEC"      # D3：R3.2 alt 對齊
sed -n '141,147p' "$SPEC"      # D4：§1.3.1 三原則（無 is_blank）+ #3 golden
sed -n '242p' "$SPEC"          # D4：is_cover（無 is_blank）
sed -n '66,69p' "$SPEC"        # D7 §1.1③ rag_tree_json 含糊 + D6 §1.1.1 raw_metadata（無 §1.1.2 rag_sections）
grep -n "rag_sections" "$SPEC" # D6：僅 §1.4.1/zh edge path、無 §1.1.x 登記
grep -nE "raw_metadata|rag_sections|pdf_path|owner_id" pipelines/context.py  # 旁路 4 欄實證
grep -n "B 軌另捕" "$PLAN"       # D2：master plan L258
```
### §3.3 旁證（master plan golden 模型本即正確）
master plan L87/L239 golden 模型＝「舊系統存盤為基準、每路打通後比對」＝capture A 軌 baseline + B 軌 diff，**本即正確**;唯 L258「B 軌另捕」措辭與此自相矛盾 → D2 只修措辭、不動模型。

---

## §4 跨 Phase 接縫契約
無跨 Phase 程式 handoff（純文件回灌）。
> 註：D3 記錄的是既有「B 軌 alt 產出 ↔ 前端 renderMarkdownWithMath 渲染」之跨軌 handoff 不變式（本案僅將其文件化、非新增 handoff）。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 緩解 |
|---|---|---|
| 改真理源誤動四凍結合約 | 🟡 中 | U6 明令四凍結合約欄位結構零變動;僅改敘述欄/加註;diff 自審合約 JSON 段未動 |
| 兩真理源指標互相懸掛（檔名/版本） | 🟢 低 | SPEC bump v7、master plan 補註⁸ 不 bump 主版本（同 PIPE-SYNC-2）;不動其他下游指標 |
| D2 釐清與既有 GOLDEN-BASELINE plan 衝突 | 🟢 低 | GOLDEN-BASELINE plan 本即 A 軌 baseline + diff 模型、D2 與其一致（只是把 §8.5 條目措辭對齊） |
| 過度回灌（D5 altitude 過低汙染 SPEC） | 🟢 低 | D5 列 §9 Q4 由 baron 拍板收不收;預設傾向不收或一行帶過 |
| 純文件、零 .py/golden/業務 | 🟢 低 | DOC-Refactor;§6 不可動清單鎖死 |

對齊 `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單
- [ ] **四凍結 JSON Schema 合約**（IngestionMetadataSpec / GlossaryReadySpec / BilingualMarkdownSpec / RagDbSpec 欄位結構）— 零變動。
- [ ] **業務代碼 / pipeline / .py / static** — 零碰（純文件）。
- [ ] **slides 以外路次之既有規格**（academic/book/resume/litedoc 條款）— 不動（僅 slides 相關 + golden 通則）。
- [ ] **resume 路 PIPE-SYNC-2 已回灌之 §1.3 還原細則 / key 接縫契約** — 不動。
- [ ] **GOLDEN-BASELINE plan / 其他下游 plan** — 不動（本案只動 SPEC + master plan 兩檔）。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §7 規格依據
| 依據 | 來源 |
|---|---|
| 工作流定義（DOC-Refactor） | `ref/WORKFLOW_SOP.md §1.3` |
| plan 結構 SSOT | `templates/template_plan.md` |
| 回灌先例（resume） | PIPE-SYNC-2 plan（`plans/2026-06-10_PIPE-SYNC-2_..._plan_v1.md`）+ master plan 補註⁶ / SPEC v6 |
| D1-D5 來源 | hotfixes/ PIPE-SLIDES-HOTFIX-{1,2,3c,3d,4,5,6} + RAG-12-HOTFIX-1 |
| golden A/B 軌權威 | `tools/golden_baseline.py` `_run_old_monolith`（L88-94 A 軌 PipelineCore）+ HOTFIX-6 |

---

## §8 驗證計畫
### §8.1 自動化
- 純文件、零 .py → 全套件 pytest 維持基線（旁證未誤動代碼）。
- 靜態 grep（§6.1 驗證清單）：
```bash
sed -n '134p' "$SPEC" | grep -q "逐頁翻譯與排版還原"          # U1 已矯正、無「100% Bypass」
grep -c "B 軌另捕" "$PLAN"                                    # U2 期望 0（措辭已改）
grep -q "PIPE-SYNC-3" "$SPEC" && grep -q "PIPE-SYNC-3" "$PLAN" # 註解包裹存在
grep -nE "renderMarkdownWithMath|_safe_alt" "$SPEC"           # U3 alt 契約已補
grep -n "is_blank" "$SPEC"                                    # U4 已補
grep -q "v7" "$SPEC"                                          # U6 SPEC bump
```
### §8.2 內容核對（人工/Antigravity）
- D1-D5 逐項對照 §3.1 表「應為」欄落地。
- 四凍結合約 JSON 段 diff 為空（未誤動）。
- slides 以外路次條款 diff 為空。
### §8.3 §7.2 跨 Phase 整合測試
**顯式豁免**（依 WORKFLOW_SOP §7.2 特例）：本案 100% DOC-Refactor、無 code handoff、無資料傳遞物 → 不適用整合測試;同 PIPE-SYNC-2 §7.2 豁免先例。

---

## §9 Open Questions（🟢 baron 拍板全定案）

| 問題 | 定案 | 理由 |
|---|---|---|
| **Q1** SPEC 版本 bump？ | **🟢 定案：bump v6→v7** | SPEC 作為技術合約隨 sync 進度逐版推進;§99.2 記 v7 條目 |
| **Q2** master plan bump 主版本 or 補註？ | **🟢 定案：補註⁸、不 bump 主版本** | master plan 為全局母案、局部回灌頻繁 bump 會致下游子 plan（academic/book）指標級聯漂移;補註尾隨為防禦性維護策略 |
| **Q3** D2 golden 釐清放 SPEC 何處？ | **🟢 定案：SPEC §1.3.1 #3 golden 句擴充 + master plan §8.5 措辭修正**（雙處呼應） | §1.3.1 是 SPEC 記載 Golden 基準核心 SSOT、後續 academic 開發者第一時間掌握 capture 正確邊界、消除 SPEC↔master plan 歷史陳述衝突 |
| **Q4** D5（清洗層）收錄否？ | **🟢 定案：不收 / 至多一行帶過「P3 含 slides 專屬排版噪聲清洗層」** | SOC：SPEC 定位＝架構與 Ingestion 數據合約;清洗正則/CSS 補丁細節留 hotfix.md + Git 即可、過度收錄＝低高度細節污染 |
| **Q5** D4 放 §1.3.1（共用原則）還是 L242（slides 專屬）？ | **🟢 定案：§1.3.1 提煉第 4 原則「頁面類型判定（is_blank/is_cover）供過濾」+ slides L242 一句指回** | is_blank/is_cover 為 Vision 階段通用頁面元數據屬性、提煉共用層建立 extensibility（未來他路複用）;slides 專屬跳過細則留 slides 章節、層次分明 |
| **Q6** 是否一併修其他 slide drift（如 page_key 變體 `p{N}_{標題}`）？ | **🟢 定案：本案不擴** | 防 scope creep;SPEC §1.4.1 key 契約已語意涵蓋 handoff 同基準保證、無須羅列實作級變體 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| **目的** | 定義 slides 路落地經驗回灌兩真理源之規格，作為 tasks 拆分與執行基準 |
| **用途** | 供 baron 審查 §9 後拆 tasks；Antigravity 階段 3/5 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 PIPE-SYNC-3 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁動四凍結合約欄位結構 / 業務代碼 / slides 以外路次條款；只動 SPEC + master plan 兩檔 |
| **改版觸發條件** | §1–§9 規格變動 / baron 拍板（尤 §9 Q4/Q5） |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務收官歸檔，經 baron 同意移至 archive/ |
| **重複防護** | 回灌內容唯一源為各 hotfix 文件；本 plan 僅定義「回灌哪些、改哪行」；不重寫 hotfix 細節 |

### §99.2 Revision 歷程
- v3 (2026-06-14)：四層交接稽核後補 **U7🔴（D6 rag_sections 旁路 §1.1.2 登記·對稱 §1.1.1 raw_metadata、承 RAG-ASYNC C6）** + **U8🟢（D7 §1.1③ rag_tree_json 點名）**;§3.1 加 D6/D7 列 + 旁路稽核結論（contracts.py 四合約型別欄位皆最新無 drift、唯 rag_sections 旁路未登記）;§6 釐清「型別欄位結構零變動、U7/U8 為旁路登記/文件點名不改 contracts.py 程式」;§9 既有六 OQ 定案不受影響（D6/D7 無新 OQ、方案明確）
- v2 (2026-06-14)：baron review 通過、§9 六 OQ 全 🟢 定案（Q1 SPEC v7 / Q2 master 補註⁸ 不 bump / Q3 §1.3.1+§8.5 雙處呼應 / Q4 D5 不收·至多一行 / Q5 D4 §1.3.1 第4原則+L242 指回 / Q6 不擴）；U1-U6 結構不變，進入可拆 tasks 狀態
- v1 (2026-06-14)：初版（DOC-Refactor；D1 SPEC slides P3 drift 矯正 / D2 A/B 軌 golden 釐清進真理源〔承 HOTFIX-6〕/ D3 alt LaTeX 跨軌契約 / D4 is_blank 頁面類型判定 / D5 清洗層可選；六 OQ，核心 Q4 D5 收不收、Q5 D4 放共用 or 專屬）
