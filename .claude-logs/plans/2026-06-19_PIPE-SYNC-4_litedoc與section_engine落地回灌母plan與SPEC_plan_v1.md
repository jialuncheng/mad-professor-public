# PIPE-SYNC-4 litedoc 與 section_engine 落地經驗回灌母 plan 與 SPEC plan

> 將 PIPE-SECTION-BASE（section_engine 共用真理源）+ PIPE-LITEDOC（第 3 路）落地後，兩真理源（master plan v10 / PIPE-SPEC）之 drift 與缺口一次性回灌矯正；含 technical 排除分歧釐清、共用真理源家族成員補登、section_engine 契約新增。純文件回灌、零業務代碼。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-SECTION-BASE（第 4/5 共用真理源 section_engine）+ PIPE-LITEDOC（第 3 路 news/web/unknown）落地後，兩真理源未同步——master plan v10 與 PIPE-SPEC 仍寫「三大共用真理源」（漏 META-NORM + section_engine 兩員）、master plan L72/L260「LiteDoc 含 technical」與 baron re-eval（technical 歸深結構家族）分歧、section_engine 機制與 render_meta_header_html HTML 扉頁 formatter 全未入 SPEC 契約；不回灌則 PIPE-ACADEMIC/BOOK/SYNC 等下游被誤導（同 PIPE-SYNC-2/3 對 resume/slides 之回灌動因）。
- **解法**：DOC-Refactor 一次性回灌——① master plan v10 就地補註（technical 矯正 / LiteDoc ✅ / 三大→家族 / 絞殺順序）② PIPE-SPEC 新增 **section_engine（§1.2.5）+ MetaNormalizer（§1.2.4·為 INFRA-4 鋪規格）** 兩共用契約章 + litedoc raw_metadata 旁路登記 + 家族措辭 + bump v8 ③ docs/HOW_TO_ADD_DOC_TYPE.md 補 B 軌加 doc_type 範式（顯式 A/B 機制對比）。
- **影響**：改 master plan v10（版控）+ PIPE-SPEC（baton 長駐、就地 git add + .bak→archive、PIPE-SYNC-3 先例）+ docs/HOW_TO_ADD_DOC_TYPE.md（版控）;**零業務代碼、零測試、四凍結合約型別欄位零變動**。

---

## §2 目標規格

> 以下逐 drift（D1-D9）列「現況→回灌後」最終狀態；皆就地補註式（不重寫整檔、不刪既有審計），措辭引用本案 grep 證據（§3）。

### master plan v10（plans/、版控）
- **D1 technical 排除矯正**：L72「LiteDocPipeline（news/web/**technical**/未知 fallback）」→ 矯正為「news/web/未知 fallback」；補一句「technical 歸深結構家族（academic/book），與本路（扁平短文）分離——A 軌證 technical 非 FLAT/非 SHORT/有 abstract」。
- **D2 PIPE-LITEDOC 狀態 ✅ + 順序**：L260 §8.5 表 PIPE-LITEDOC 列「⬜ 待建立 / 依賴 PIPE-ACADEMIC 完成 / 含 technical」→ 改「✅ 已落地（C1-C8、hash b1012bc…ff16271）/ 實際先於 academic / news/web/未知」；補狀態註：縱向絞殺實際順序為 Resume→Slides→**LiteDoc**（先於 Academic）。
- **D3 三大→共用真理源家族**：L18/L74/§8.4「**三大**共用真理源（DomainNormalizer/GLOSSARY-CORE/Translator）」→ 升「共用真理源**家族**」，roster 補登 **META-NORM（第 4·封面元數據自癒飛輪）+ section_engine（第 5·section 機制）**；標明三大為「跨五路 LCC/術語/翻譯」原始核心、META-NORM/section_engine 為後續落地擴充成員。
- **D4 絞殺順序註**：L86/L222/L253「Resume → Visual → Academic → LiteDoc → Book」→ 補實況註（LiteDoc 先於 Academic 落地、與規劃順序差異、不改原規劃序句、僅加實況補註）。

### PIPE-SPEC（baton/、不版控、就地 git add + .bak→archive）
- **D5 section_engine 共用契約章（核心新增·§1.2.5）**：§1.2「三大共用真理源模組契約」後新增 `section_engine` 契約小節——公開介面（`collect_summary_targets`/`build_section_summaries`/`collect_render_slots`/`restore_sections_markdown`/`translate_whole`/`is_heading_degraded`/`collect_rag_sections`/`single_container_sections`/`render_meta_header`〔resume 列表〕/`render_meta_header_html`〔academic-family HTML 扉頁〕）+ 鐵律（零 doc_type 字面量·llm/translator/prompt 注入·Zero Schema Coupling·**接縫 key=原文標題 path**）+ consumer 對照（resume/litedoc 已消費、academic/technical/book 待）。
- **D5b MetaNormalizer 共用契約章（§1.2.4·Q1 翻案、為 INFRA-4 鋪規格依據）**：新增 `MetaNormalizer`（META-NORM 飛輪、第 4 共用真理源）契約小節——公開入口 `normalize_fields(raw_fields, context)`〔旗標 `LLM_USE_META_NORM` 閘門〕+ 三路分流〔reserved 映合約標記不入庫·BS1 / 泛用詞黑名單每次 LLM·Q9 / 非黑名單 快取→LLM 比對 canonical→on_conflict 註冊·BS4〕+ schema〔MetaField/MetaFieldAlias 兩表〕+ 交易邊界〔LLM 交易外·temp=0 保守比對〕+ consumer〔slides/litedoc 已消費〕。**動因**：下游 INFRA-4（raw_metadata 旁路收合進合約欄）之欄位對齊/自癒行為由 MetaNormalizer 決定〔grep INFRA-4 引用 34 處〕、補全契約省二次 sync。
- **D6 litedoc raw_metadata 旁路登記**：§1.1.1「raw_metadata 旁路欄」現登 phone/email/domain（resume）→ 補登 litedoc 之 **date/url/publisher/translated_title**（同 PIPE-SYNC-3 D6 補登 rag_sections §1.1.2 之對稱手法；translated_title 三欄 dict 範式 PIPE-SLIDES-HOTFIX-1b）。
- **D7 三大→家族措辭**：§本體 L4/L15/L52/L75「三大共用真理源」措辭 → 「共用真理源家族」（與 D3 同口徑、roster 含 META-NORM + section_engine）。
- **D8 bump v8**：§99.2 加 v8 Revision（PIPE-SYNC-4 C2）。
- **D8.1 不改項（明文）**：§1.3 表 L140「LiteDocPipeline | news/web/未知 fallback」**已正確（無 technical）→ 不動**；§3.3 15k 安全閥門 / §2 ≥10 門檻**已對齊本案落地 → 不動**；四凍結合約型別欄位結構**零變動**。

### docs/HOW_TO_ADD_DOC_TYPE.md（版控）
- **D9 B 軌加 doc_type 範式（顯式 A/B 機制對比·防誤導）**：現 0 提及 litedoc/section_engine（A 軌時代 doc、舊指南全是 `pipeline_core.py` 硬編碼分支）→ 補一節「B 軌（PIPE 五路）加 doc_type」：**顯式劃分「B 軌現代裝飾器機制」**〔`@PipelineFactory.register` 插件模式 + `pipelines/__init__` import 觸發 + 四 Phase 消費共用真理源〔section_engine + 三真理源 + rag_indexer〕+ raw_metadata 旁路 + §7.2 key-changing 整合測試〕**vs「A 軌單體硬分支機制」**〔pipeline_core.py 內 doc_type== 硬編碼分支、即將絞殺〕——**明示下游（academic/book）採 B 軌、嚴禁寫 A 軌分支**;**補「P1 DocAnalyzer doc_type 安全映射規範」**〔U2.1：扁平短文〔litedoc/unknown〕在 `run_phase1` 呼 `DocAnalyzer().analyze(md, doc_type)` 時、呼叫端應安全映射避免 fallback 至 academic 深層 prompt 偏位;指引下游深結構文體〔academic/book〕如何利用既有 structure/heading_fix prompts 對齊〕;不重寫 A 軌既有章。

<!-- === [WORKFLOW-4 C1 U4] === 選用章節：Diverse Rollout 多候選探索 -->
### §2.5 候選方案（Diverse Rollout）（選用）

> 單一方案、無多方案需求：本案為純文件回灌（drift 矯正），各 D 項之「現況→最終狀態」由 grep 證據唯一決定、無語意分散之替代設計。唯一決策點（META-NORM 契約深度 / 資料流程 doc 是否納入）以 §9 Open Questions 處理。
<!-- === [WORKFLOW-4 C1 U4 END] === -->

---

## §3 現況與證據

- **master plan v10**（`.claude-logs/plans/2026-06-01_PIPE_..._plan_v10.md`）：
  - L72：`LiteDocPipeline（news/web/technical/未知 fallback）`（technical 分歧）。
  - L260 §8.5 表：`PIPE-LITEDOC（第 4 步）… ⬜ 待建立 … 依賴 PIPE-ACADEMIC 完成`。
  - L18/L74/§8.4（L243）：`三大共用真理源`。
  - L86/L222/L253：絞殺順序 `Resume → Visual → Academic → LiteDoc → Book`。
  - L183：`RAG 字元門檻（Academic/Book/LiteDoc ≥10、Slides/Resume ≥3）`（**已正確**）。
- **PIPE-SPEC v7**（`.claude-logs/baton/2026-06-01_PIPE-SPEC_..._specification.md`、baton 長駐不版控）：
  - L4/L15/L52/L75：`三大共用真理源`。
  - §1.1.1（L69）：raw_metadata 登 phone/email/domain。
  - §1.3 表 L140：`LiteDocPipeline | news/web/未知 fallback`（**已正確、無 technical**）。
  - §3.3（L251）15k 安全閥門 / §2（L240）≥10：**已對齊**。
- **META-NORM 未回灌**：master plan grep META-NORM = 0、SPEC = 0（→ 家族 roster 須補）。
- **docs/HOW_TO_ADD_DOC_TYPE.md**：grep litedoc/section_engine = 0。

### §3.1 grep 鋼鐵證據

```bash
grep -nE "LiteDoc|technical|三大共用真理源|Resume → " .claude-logs/plans/2026-06-01_PIPE_*_plan_v10.md
grep -nE "三大共用|section_engine|render_meta_header|news/web/未知" .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md
grep -ciE "META-NORM|MetaNormalizer" .claude-logs/plans/2026-06-01_PIPE_*_plan_v10.md   # 0（未回灌）
grep -cE "litedoc|section_engine" docs/HOW_TO_ADD_DOC_TYPE.md                            # 0
```

---

## §4 跨 Phase 接縫契約

無。（純文件回灌、無 Phase/模組間資料 handoff;§7.2 豁免見 §9 Q3。）

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 真理源誤改既有正確內容（如 SPEC §1.3 L140 已正確的 litedoc 格）| 🟡 中 | D8.1 明文「不改項」清單；各 D 限就地補註、不重寫整檔、不刪既有審計 |
| 四凍結合約被誤動 | 🟢 低 | 純文字回灌、零 contracts.py / 零型別欄位變動（明列不可動）|
| 家族 roster 過度膨脹（META-NORM 契約深度）| 🟢 低 | §9 Q1 決 META-NORM 僅 roster 列入 vs 全 §1.2.x 契約章 |
| SPEC 版控誤入庫 | 🟢 低 | SPEC 長駐 baton 不版控、就地 git add + .bak→archive（PIPE-SYNC-2 195e12b / PIPE-SYNC-3 先例）|
| 進行中分支相容 | 🟢 低 | 純 .md、零代碼、不影響任何 pytest / 落地路次 |

對齊 `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §4.1 #5`。

---

## §6 不可動清單

- [ ] **所有業務代碼**（`pipelines/*` / `processor/*` / `web_server.py` / A 軌 / static）— 100% 不動（純文件）。
- [ ] **四凍結合約 `contracts.py` 型別/欄位** — 零變動（D5/D6 僅在 SPEC 文字描述、不改程式）。
- [ ] **PIPE-SPEC §1.3 表 L140 litedoc 格** — 已正確、嚴禁改（D8.1）。
- [ ] **PIPE-SPEC §3.3 15k / §2 ≥10 / 四凍結合約結構** — 已對齊、不動。
- [ ] master plan / SPEC 既有審計內容（Revision 史、既有 D1-D7 補註）— 只增不刪。
- [ ] 任何測試檔 — 不動。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 結構 SSOT | `.claude-logs/templates/template_plan.md` |
| 工作流規範 / §7.2 豁免條款 | `.claude-logs/ref/WORKFLOW_SOP.md §7.2` |
| 專案進度框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 回灌對象①（版控）| `.claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md` |
| 回灌對象②（baton 長駐）| `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md` |
| 回灌對象③（版控）| `docs/HOW_TO_ADD_DOC_TYPE.md` |
| 落地實證 | PIPE-SECTION-BASE（C1-C5）+ PIPE-LITEDOC（C1-C8）完成表 + section_engine.py / litedoc_pipeline.py |
| SPEC 版控先例 | PIPE-SYNC-2 195e12b（SPEC 就地 git add、.bak→archive）/ PIPE-SYNC-3 |

---

## §8 驗證計畫

### §8.1 自動化（純文件、無新增測試）
```bash
pytest tests/ -q   # 維持 686 passed 基線（純 .md、零代碼，應零影響）
# grep 驗收：
grep -c "technical" .claude-logs/plans/2026-06-01_PIPE_*_plan_v10.md   # litedoc 行 technical 已矯正
grep -c "共用真理源家族\|section_engine" .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md
grep -c "render_meta_header_html\|section_engine" .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md
grep -c "litedoc\|section_engine" docs/HOW_TO_ADD_DOC_TYPE.md          # 由 0 → ≥1
```

### §8.2 手動核查（DOC-Refactor §6.1）
1. master plan v10：technical 矯正、LiteDoc ✅+hash、三大→家族（含 META-NORM/section_engine）、順序註——逐項 grep 命中。
2. PIPE-SPEC v8：section_engine 契約章存在、§1.1.1 litedoc 旁路欄登記、§1.3 L140 未動、四凍結合約零變動、bump v8。
3. HOW_TO_ADD：B 軌範式節存在、A 軌既有章未動。

---

## §9 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1** 🟢 META-NORM 回灌深度：僅家族 roster 列入，還是全 §1.2.x 契約章? | **完整寫入 §1.2.4 契約章（D5b）**（review 翻案、原傾向另立已撤） | **下游 INFRA-4〔raw_metadata 旁路收合〕之欄位對齊/自癒行為由 MetaNormalizer 決定〔grep INFRA-4 引用 34 處〕**;飛輪 100% 落地、slides/litedoc 已消費;趁本案編 SPEC 一併補全契約、為 INFRA-4 提供規格依據、省二次 sync。MetaField/MetaFieldAlias 兩表 + 飛輪三路規模可控、純文件 |
| **Q2** docs/HOW_TO_ADD_DOC_TYPE.md（A 軌 doc）是否納入本案? | **納入（baron「全部回灌」）**：補 B 軌加 doc_type 範式一節、A 軌既有章不動 | 全部回灌涵蓋之;B 軌已 3 路落地、加 doc_type 範式對 academic/book 開發有實值;不重寫 A 軌章 → 低風險 |
| **Q3** resume/slides 資料流程 doc（baton point-in-time）是否回灌? | **不回灌（非目標、明文聲明）** | 該二 doc 為一次性快照、非真理源、未入版控;section_engine 抽取使 resume 那份描述輕微 stale 但無下游引用;回灌成本>價值;若要更新另作 |
| **Q4** §7.2 跨 Phase 整合測試是否豁免? | **顯式豁免**：純 DOC-Refactor、回灌 3 份 .md、零業務代碼、無 Phase handoff | 同 PIPE-SYNC-2/3 + WORKFLOW-3/4 先例（純 DOC 無 code handoff）;WORKFLOW_SOP §7.2 特例 |
| **Q5** master plan 是否 bump 主版本（v10→v11）? | **不 bump、補註式**（§99.2 加 Revision 紀錄即可） | 同 PIPE-SYNC-2 補註⁶ / PIPE-SYNC-3 補註⁸ 先例;就地補註不動主版本號、避免版本通膨 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SYNC-4（litedoc + section_engine 落地回灌母 plan 與 SPEC）之目標規格，作為 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查 + tasks 拆分引用;Antigravity 階段 3 驗證引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 PIPE-SYNC-4 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 拍板過程;嚴禁含 commit 拆分（屬 tasks 階段）;嚴禁改任何業務代碼 / 四凍結合約型別 |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成、經 baron 同意歸檔至 archive/ |
| **重複防護** | 僅定義回灌目標規格;真理源唯一源仍為 master plan / SPEC 本體;接縫契約引用 WORKFLOW_SOP §7 |

### §99.2 Revision 歷程

- v3 (2026-06-19)：review audit 採納 D9 微補強——HOW_TO_ADD 補「P1 DocAnalyzer doc_type 安全映射規範〔U2.1〕」、指引下游深結構文體對齊既有 structure/heading_fix prompts;audit 確認 D1-D9〔含 D5b〕對 translated_title 鏈 / DFS 子樹 / is_blank〔不適用·純文字〕無重大遺漏;Q1-Q5 全確認 v2
- v2 (2026-06-19)：review 採納兩項——**Q1 翻案**〔META-NORM 由「另立」改「完整寫入 SPEC §1.2.4 契約章·D5b」，動因下游 INFRA-4 對 MetaNormalizer/raw_metadata 34 處引用、補全省二次 sync〕+ **D9 強化**〔顯式劃分 B 軌裝飾器 vs A 軌硬分支、明示下游採 B 軌防誤導〕;§1 影響同步;finding ②〔TODO LiteDoc 結案〕評為 stale〔C8 已做、完成表+索引在〕、checkout TODO 自癒屬標準動作不入 §2;Q2-Q5 維持
- v1 (2026-06-19)：初版（DOC-Refactor;D1-D9 回灌——master plan〔D1 technical 排除 / D2 LiteDoc ✅+順序 / D3 三大→家族〔含 META-NORM+section_engine〕/ D4 絞殺順序註〕+ PIPE-SPEC〔D5 section_engine 契約章 / D6 litedoc raw_metadata 旁路登記 / D7 家族措辭 / D8 bump v8 / D8.1 不改項〕+ HOW_TO_ADD〔D9 B 軌範式〕;§9 五 OQ〔Q1 META-NORM 深度 / Q2 HOW_TO_ADD 納入 / Q3 資料流程 doc 非目標 / Q4 §7.2 豁免 / Q5 不 bump 主版本〕;SPEC 就地 git add 先例;零業務代碼）
