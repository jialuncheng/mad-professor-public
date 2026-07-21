# PIPE-SYNC-5 PIPE-INGEST 與 GLOSSARY-TERMMAP 回灌母 plan 與 SPEC plan

> 治理債回灌：將 **PIPE-INGEST**（litedoc 攝入自有化：`ingestion_engine` 新真理源、借用鏈退場、譯題單一源）與 **GLOSSARY-TERMMAP**（`build_termmap` 事前定案術語表五路共用 builder、旗標開啟）兩案落地經驗，回灌兩真理源（母 plan v10 / PIPE-SPEC v8）；並更正 design spec **F7 門檻**（IMG-FILTER 實測校正、廢長邊軸）。純文件、零業務代碼。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-INGEST 與 GLOSSARY-TERMMAP 兩案已落地並 ship，但兩真理源（母 plan v10、PIPE-SPEC v8）尚未回灌——`ingestion_engine`（B 軌自有攝入組裝引擎、家族新成員）無契約章；`build_termmap`（事前定案五路共用 builder）未登記於 GLOSSARY-CORE 契約；litedoc 借用鏈退場／譯題單一源之現況未反映；且 design spec F7 仍載**已作廢的門檻數字**（`MIN_LONG_SIDE 600`／`MIN_AREA 200k`），與 IMG-FILTER 實測校正值（面積 100k／長寬比 4.0／廢長邊軸）矛盾，恐誤導後續。
- **解法**：沿 PIPE-SYNC-2/3/4 前例——**就地 HTML 註解補註**（`<!-- [PIPE-SYNC-5 Dn] -->`）+ Revision 一行、**不 bump 檔名**、**四凍結合約結構零變動**。PIPE-SPEC v8→v9 新增 `ingestion_engine` 契約章（§1.2.6、家族第 6 員）+ GLOSSARY-CORE §1.2.2 補 `build_termmap` 事前定案 builder 規格 + litedoc P1 借用鏈退場／譯題單一源註 + 旗標預設 true 註；母 plan 同步 U8 家族 roster 補第 6 員、§8.5 表三案 ⬜→✅、U7 LiteDoc 行補現況；design spec F7 門檻更正。
- **影響**：僅三份治理文件（PIPE-SPEC〔baton 長駐〕／母 plan v10〔tracked〕／design spec〔baton〕）；零業務代碼、零 schema、零測試。

---

## §2 目標規格

### §2.1 PIPE-SPEC v8→v9（`baton/2026-06-01_PIPE-SPEC_..._specification.md`）

1. **D1 新增 §1.2.6 `ingestion_engine` 契約章（共用真理源家族第 6 員、litedoc 首個消費）**：模組 `pipelines/ingestion_engine.py`；純函式引擎、**零文體字面量**（文體差異如 meta 判型集 `meta_types` 一律呼叫端注入）、不 import A 軌 processor、不讀 PipelineContext；公開介面 `assemble(markdown_text, structure, *, meta_types=("title","authors","publication_info"), figure_filter=None) -> {"title","meta","sections"}`（含 `extract_title`／`mark_meta_lines`／`split_blocks`／`build_sections` 分解）；行為鐵律——① title 抽取不丟（首個 `#`）；② meta 行非連續分離（不受段落連續性限制、依 `meta_types` 判型）；③ figure block 重建帶 `content=![alt](src)`＋caption；④ **可選 `figure_filter(src,alt)->bool` 純加法 hook**（IMG-FILTER C2 注入點、預設 None 時 byte 等價、DROP 時連帶 caption `used` 標記防孤兒）；consumer＝litedoc（借用鏈退場後之自有攝入組裝）、五路皆可注入。
2. **D2 §1.2.2 GLOSSARY-CORE 補 `build_termmap` 事前定案 builder 規格**：模組 `processor/glossary_extractor.py::GlossaryManager.build_termmap(full_text, abstract, translated_abstract, source_lang, target_lang, domain, ...)`；五路共用 builder 五步——N1 段落邊界切塊（`GLOSSARY_CENSUS_CHUNK_CHARS`）→ N2 並行 census **只認詞不翻**→ N3 `_normalize_key` 去重 + query_cascade 分流已知∪未知（**廢飛輪早退**）→ N4 **只翻未知**→ N5 定案 `upsert`（`source="termmap_decided"`、永不吃收割）；三路 `_heal_glossary`（resume／slides／litedoc）**收斂委派單一實作源 build_termmap**、雙廢 `if existing` 早退鏈；**事前定案保證全文單一譯法**（§2.7「全文單一譯法」可硬驗收）。
3. **D3 家族 roster 補第 6 員**：§1.2 標題段「家族（第 4 MetaNormalizer + 第 5 section_engine）」→ 增列 **第 6 `ingestion_engine`（契約見 §1.2.6）**；§0.3 三度對稱段同步。
4. **D4 litedoc P1 借用鏈退場／譯題單一源註**：§1.3 策略管線 LiteDoc 行（或 §1.2.6 附註）補——P1 攝入組裝改走自有 `ingestion_engine`、**A 軌 md2json／行級分塊借用鏈退場**（`_structured.json` 不再產）；P3 譯題單一源＝P1 title（`translate_unit(P1 title)`、廢 slot 撈題、根治扉頁/分頁名/PDF `/Title` 三受害者）。
5. **D5 旗標預設註**：`LLM_USE_GLOSSARY_ALIGN` 預設 false→**true**（GLOSSARY-TERMMAP C5 末位點火、全五路 B 軌術語注入啟用、env 單點關回）——註於 §1.2.2 或 §3 邊界。
6. **D6 Revision v9**：§4 Change Log + §99.2 加列。
7. **不改鐵律（對齊 PIPE-SYNC-4 D8.1）**：四凍結合約（§1.1）型別/欄位結構零變動；§1.3 L140 news/web/未知 fallback、§3.3 15k、§2/§3.1 ≥10 等既有不改項逐字守；HTML 註解包裹所有增修；不 bump 檔名。

### §2.2 母 plan v10 回灌（`plans/2026-06-01_PIPE_..._plan_v10.md`、就地 `<!-- [PIPE-SYNC-5 Dn] -->`）

1. **U8 三大共用真理源 roster 補第 6 員 `ingestion_engine`**（契約見 SPEC §1.2.6）；GLOSSARY-CORE 條補「`build_termmap` 事前定案 builder」一句（契約見 SPEC §1.2.2）。
2. **§8.5 表三案狀態回填**：PIPE-INGEST／GLOSSARY-TERMMAP／IMG-FILTER 三列（或補列）標 ✅ 已落地 + hash + 產出檔（`pipelines/ingestion_engine.py`／`pipelines/image_filter.py`／`glossary_extractor.build_termmap`）。
3. **U7 LiteDoc 行補現況註**：借用鏈退場／自有攝入組裝／譯題單一源（就地補註、原規劃句保留作軌跡）。
4. **Revision 加列**（沿 PIPE-SYNC-4 C1「不 bump 主版本、加 Revision 記 PIPE-SYNC-5」範式）。

### §2.3 design spec F7 門檻更正（`baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md`）

- L123 規則① **`max(w,h) < MIN_LONG_SIDE(預設 600)` 或 `area < MIN_AREA(預設 200k)`** → 更正為 **`area < IMG_FILTER_MIN_AREA(預設 100000)`（廢長邊軸）**；規則② `MAX_ASPECT 4.0` 不變；補一句實測校正註（廢長邊軸理由＝誤殺 481×369 內容 chart；規則③收窄報頭判型行界）+ 指向 IMG-FILTER plan v2/settings。原探索脈絡保留、僅更正作廢數字。

### §2.5 候選方案（Diverse Rollout）

單一方案，無多方案需求——回灌手段（就地 HTML 註解 + Revision、不 bump 檔名、不改凍結合約）為 PIPE-SYNC-2/3/4 三度沿用之定式，本案照搬、無架構級決策。

---

## §3 現況與證據

- **PIPE-SPEC v8**（`baton/2026-06-01_PIPE-SPEC_..._specification.md`）：
  - §1.2 家族 roster（L52 §0.3、L75 §1.2）：現列 5 員（三大 + §1.2.4 MetaNormalizer + §1.2.5 section_engine）——**無 ingestion_engine**。
  - §1.2.2 GLOSSARY-CORE（L90）：標準自癒演算法——**無 build_termmap 事前定案**。
  - §99.2 至 **v8**（PIPE-SYNC-4 C2）。
- **母 plan v10**（`plans/2026-06-01_PIPE_..._plan_v10.md`）：
  - U8（L74-77）：三大真理源 + 家族第 4 MetaNormalizer/第 5 section_engine——**無第 6**。
  - §8.5（L265）：PIPE-LITEDOC ✅（PIPE-SYNC-4 C1 D2 補）；**PIPE-INGEST／GLOSSARY-TERMMAP／IMG-FILTER 未登記**。
  - Revision 至 v11（2026-06-05）+ PIPE-SYNC-4 C1 就地補註（2026-06-19、標 v6 屬既有編號碰撞、不溯及）。
- **design spec F7**（`baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md` L123）：規則① 仍載 `MIN_LONG_SIDE 600`／`MIN_AREA 200k`——**與 IMG-FILTER 實測校正（100k/廢長邊軸）矛盾**。
- **落地代碼契約**（回灌來源）：
  - `pipelines/ingestion_engine.py`：`assemble(md, structure, meta_types=DEFAULT_META_TYPES, figure_filter=None) -> {"title","meta","sections"}`；`DEFAULT_META_TYPES=("title","authors","publication_info")`（L27/289/307）。
  - `processor/glossary_extractor.py:331`：`build_termmap(full_text, abstract, translated_abstract, source_lang, target_lang, domain, ...)`。
  - `settings.py`：`LLM_USE_GLOSSARY_ALIGN` 預設 "true"（L114）；`IMG_FILTER_MIN_AREA=100000`／`IMG_FILTER_MAX_ASPECT=4.0`（L130/132）。

### §3.1 grep 鋼鐵證據

```bash
grep -n "第 4\|第 5\|MetaNormalizer\|section_engine\|家族" .../PIPE-SPEC_...specification.md
# L52/L75：家族 5 員止於 section_engine（第 5）；無 ingestion_engine

grep -n "def assemble\|DEFAULT_META_TYPES\|return {" pipelines/ingestion_engine.py
# 27:DEFAULT_META_TYPES=("title","authors","publication_info") / 285:def assemble / 307:return {"title","meta","sections"}

grep -rn "def build_termmap" processor/glossary_extractor.py
# 331:    def build_termmap(  → 簽名 full_text/abstract/translated_abstract/source_lang/target_lang/domain

grep -n "MIN_LONG_SIDE\|MIN_AREA(預設 200k\|預設 600" .../2026-07-19_PIPE-INGEST-REVIEW_design_spec.md
# L123：max(w,h) < MIN_LONG_SIDE(預設 600) 或 area < MIN_AREA(預設 200k)  ← 待更正

grep -n "IMG_FILTER_MIN_AREA\|LLM_USE_GLOSSARY_ALIGN" settings.py
# 130:IMG_FILTER_MIN_AREA=100000 / 114:LLM_USE_GLOSSARY_ALIGN 預設 "true"
```

---

## §4 跨 Phase 接縫契約

無。（純文件回灌任務、無跨 Phase 資料 handoff；被回灌之落地案自身接縫契約已於各案 plan/§7.2 驗證。）

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| 誤動四凍結合約結構 | 🟢 低 | §2.1 不改鐵律（對齊 PIPE-SYNC-4 D8.1）；HTML 註解包裹增修、逐字守既有不改項 |
| 版本標號碰撞（母 plan 既有 v6/v11 混亂） | 🟡 中 | 沿 PIPE-SYNC-4「不 bump 主版本、加 Revision 記 PIPE-SYNC-5」；不溯及既往修既有編號（WORKFLOW_SOP §2）；§9 OQ 確認標號 |
| 契約章與現役代碼 doc-drift | 🟢 低 | §3 契約逐一對照落地 grep（assemble 簽名/build_termmap 簽名/DEFAULT_META_TYPES 實貼） |
| 回灌範圍蔓延（FITZ/LANG-DETECT） | 🟢 低 | 本案範圍鎖 baron 明點三項；FITZ/LANG-DETECT 留 PIPE-SYNC-6（§9 OQ） |
| design spec 為 baton 探索檔、非正式 spec | 🟢 低 | F7 僅更正作廢數字防誤導、保留探索脈絡；不升格為正式契約 |

---

## §6 不可動清單

- [ ] PIPE-SPEC §1.1 四份凍結 Phase 交接合約（型別/欄位/簽名結構）——零變動
- [ ] PIPE-SPEC §1.2.1/§1.2.3/§1.2.4/§1.2.5 既有契約章本體——僅家族 roster 增列、章節本體不改
- [ ] PIPE-SPEC §1.3 L140 news/web/未知 fallback、§3.3 15k、§2/§3.1 ≥10——逐字守
- [ ] 母 plan §1/§2 U1-U6/U9-U11、§8.1-§8.4 既有規劃本體——僅 U7/U8/§8.5 就地補註
- [ ] design spec F7 探索脈絡（實測鴻溝數據、Vision 反直覺、規則②③）——僅更正規則①作廢門檻
- [ ] 一切業務代碼（`pipelines/`／`processor/`／`settings.py`）——DOC-Refactor 零碰
- [ ] 既有 Revision 歷程既有列——只增不刪、不溯及既往修既有編號

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| PIPE-SYNC 回灌前例（就地註解 + Revision + 不 bump） | PIPE-SPEC §99.2 v6/v7/v8、母 plan §99.2 PIPE-SYNC-4 C1 |
| 落地契約真理源 | `pipelines/ingestion_engine.py`／`processor/glossary_extractor.py`／`settings.py`（§3 grep） |
| PIPE-INGEST／GLOSSARY-TERMMAP 成果 | `archive/TODO_done_archive.md` 對應完成表格 + `plans/`/`tasks/` 歸檔 |
| IMG-FILTER F7 校正 | IMG-FILTER plan v2 §2.5（實測 23 圖廢長邊軸）+ `settings.py` L128-132 註 |
| 文件歸屬／改版規則 | `ref/WORKFLOW_SOP.md §2`／framework §5 SPEC 撰寫規則 |
| 跨 Phase 整合測試豁免 | `ref/WORKFLOW_SOP.md §7.2`（純 DOC 無 code handoff） |

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試執行**：`venv/bin/python -m pytest tests/ -q`（純文件改動、預期 **920 passed 零回歸**、作 DOC 未誤觸代碼之防呆）。
- **預計新增**：無（零業務代碼、零測試新增）。

### §8.2 手動端到端（E2E）驗證流程（DOC 驗收清單）

1. **契約對照**：PIPE-SPEC §1.2.6 assemble 簽名 = `ingestion_engine.py` 實貼；§1.2.2 build_termmap 簽名 = `glossary_extractor.py:331` 實貼（grep diff 零落差）。
2. **家族計數一致**：§0.3 與 §1.2 roster 皆列 6 員（三大 + MetaNormalizer + section_engine + ingestion_engine）；母 plan U8 同步。
3. **F7 門檻更正**：design spec L123 `grep "MIN_LONG_SIDE\|200k"` 零命中（作廢數字已除）、`grep "100000\|100k"` 命中。
4. **不改項守恆**：`git diff` PIPE-SPEC §1.1 四合約區塊零改；母 plan §1/§2 U1-U6 零改。
5. **HTML 註解包裹**：所有增修 `grep -c "PIPE-SYNC-5"` 與 Revision 記述數一致。
6. **Revision 完備**：三文件各加 PIPE-SYNC-5 Revision 一行、hash 待回填。

---

## §9 Open Questions（五問全數拍板 2026-07-21·baron 採納推薦、無翻案）

| 開放問題 | 拍板方案 | 理由 |
|---|---|---|
| Q1 回灌範圍：是否納入 PIPE-INGEST-FITZ／LANG-DETECT | ✅ **不納入、留 PIPE-SYNC-6** | 單一職責與原子增量；FITZ（FitzProcessor/閘門/連字）與 LANG-DETECT（language 欄合成）剛落地、契約面獨立、分批回灌避免 commit 膨脹與檢索失焦 |
| Q2 母 plan 版本標號（既有 v6 碰撞、Revision 已到 v11、檔名 v10） | ✅ **沿 PIPE-SYNC-4：不 bump 檔名、加 Revision 一行記「PIPE-SYNC-5 回灌」、就地 `<!-- [PIPE-SYNC-5 Dn] -->`** | 既有編號碰撞不溯及（WORKFLOW_SOP §2）；PIPE-SYNC-4 已立範式；prompt「v10→v11」理解為批次標籤、非嚴格 SemVer、保原名助歷史 trace |
| Q3 ingestion_engine 契約章編號（§1.2.6 vs 併入 §1.2.5） | ✅ **獨立 §1.2.6**（家族第 6 員、與 section_engine 平級） | 攝入組裝與 section 機制職責正交、平級並列最符 SPEC 模組化結構、便於後續管線單獨引用 |
| Q4 IMG-FILTER 是否需獨立 PIPE-SPEC 契約章 | ✅ **不需**（figure_filter hook 併入 §1.2.6 assemble 契約 + F7 更正 design spec 即足） | 契約面＝`ingestion_engine.assemble` 之 `figure_filter` 注入參數（已於 D1 涵蓋）；三規則門檻屬實作常數、非介面契約、不應膨脹介面規格書 |
| Q5 build_termmap 回灌落點（§1.2.2 內 vs 新 §1.2.2.1） | ✅ **§1.2.2 內補一段（事前定案 builder）** | 事前定案是 GLOSSARY-CORE 自癒演算法自然演進（取代舊收割法）、內聚同章保脈絡完整、防碎片化 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SYNC-5 回灌任務的目標規格（PIPE-INGEST＋GLOSSARY-TERMMAP 落地經驗回灌母 plan/PIPE-SPEC + F7 門檻更正），作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 PIPE-SYNC-5 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（DOC-Refactor）；嚴禁改動四凍結合約結構；嚴禁 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義回灌範圍與落點；被回灌之落地契約唯一源＝現役代碼；回灌手段唯一源＝PIPE-SYNC-2/3/4 前例 |

### §99.2 Revision 歷程

- v2 (2026-07-21)：review 定稿——外部 review 無結構性缺失、無新增規格項（肯認回灌決策/就地補註策略/F7 更正三點）；§9 五 OQ 全數拍板採納推薦（無翻案）；§1–§8 規格本體無異動
- v1 (2026-07-21)：初版——依 PIPE-SYNC-2/3/4 前例定義 PIPE-INGEST（ingestion_engine §1.2.6 家族第 6 員/借用鏈退場/譯題單一源）＋GLOSSARY-TERMMAP（build_termmap §1.2.2 事前定案/旗標 true）回灌 PIPE-SPEC v8→v9 + 母 plan 就地補註 + design spec F7 門檻更正（廢長邊軸）；五 OQ 待 baron 拍板（範圍不納 FITZ/LANG-DETECT、版本標號沿前例、§1.2.6 獨立章、IMG-FILTER 不獨立章、build_termmap 內聚 §1.2.2）
