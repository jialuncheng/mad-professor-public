# META-NORM 封面元數據自癒飛輪與動態欄位登記 · tasks

> 依據 plan：`.claude-logs/baton/2026-06-11_META-NORM_..._plan_v1.md`（§99.2 **v1.2**、八 OQ + Q9/Q10 全定案、BS1-BS7 收編）
> 工作流類別：**BE-Refactor**（logging_SOP + database_SOP 強制 §5 核查；**含 DB schema 新增 2 表**——baron 已 §1.6 點頭）
> 範式繼承：DOMAIN-NORM（Domains/DomainMapping + normalize_to_lcc 飛輪）/ GLOSSARY-CORE（query_cascade→extract→upsert + 旗標閘門）——本任務實例化到 **metadata 欄名**。

---

## §0 改版規則
- 改版觸發：§8 拆分或 §6 驗收變動 → 改章節 + §99.2 Revision
- plan 續留 baton、唯 checkout 一次性歸檔

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 | `processor/meta_normalizer.py`（MetaNormalizer 飛輪）/ `tests/test_meta_norm.py`（單元 + §7.2 整合）|
| **修改檔案** | 5 | `models.py`（+MetaField/MetaFieldAlias 兩表）/ `settings.py`（+`LLM_USE_META_NORM` 旗標）/ `pipelines/slide_pipeline.py`（P1 開放抽取+封面放寬+normalize 接線、Vision schema +subtitle、P3 subtitle 渲染）/ `static/index.html`（通用 key-value 渲染器）/ 母 plan v10（**僅 checkout**：META-NORM 條目登記）|
| **目錄初始化** | 0 | （沿用既有 plans//tasks//executions//hotfixes/）|
| **狀態更新** | 2 | TODO.md / prompts/INDEX.md |
| **Commits** | 7 | C1 → C2 → C3 → C4 → C5 → C6 → checkout |
| **baton 歸檔** | 1 次 | checkout 一次性 mv（plan + tasks + C1-checkout 執行報告 → plans//tasks//executions/）+ git add |

---

## §1 TL;DR（概要）

7 commit，飛輪由底向上、旗標 off 全程線上 0 風險：

- **C1 — Schema & Flag（登記表與旗標）**：`MetaField`/`MetaFieldAlias` 兩表（繼承 Domains 範式、PK/Unique + FK CASCADE + sort_weight）+ `settings.LLM_USE_META_NORM`(False) + seed 種子註冊腳本/常數。
- **C2 — MetaNormalizer Flywheel（自癒飛輪）**：`normalize_fields` 三步（快取查 → 批次 LLM 比對既有 → on_conflict 動態註冊+label 提案）+ 泛用詞黑名單不快取（Q9）+ reserved 名單（BS1）+ 旗標閘門；LLM 交易外。
- **C3 — P1 Wire（開放抽取與封面放寬接線）**：Vision cover prompt 改開放抽取 + 封面判定放寬（容主視覺圖）+ `normalize_fields` → `raw_metadata` 三欄 dict（HOTFIX-1b 契約）+ reserved 回填凍結合約。
- **C4 — Subtitle（小標題結構化）**：Vision schema 加 `subtitle` 欄 + P3 還原渲染次級標題（D）。
- **C5 — Frontend Generic Renderer（前端通用渲染）**：`static/index.html` 通用 key-value 渲染器 + 排除集（BS2）+ 排序（BS7）。
- **C6 — Tests（測試補全）**：飛輪單元 + §7.2 key-changing 整合（raw_key≠canonical 仍對齊）+ 三欄 dict 契約。
- **checkout — 收官與文件歸檔**：Conformance + 母 plan 登記 + baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §2 現況

- 飛輪範式現成（plan §3.1 grep 證）：`models.py:230 Domains`/`255 DomainMapping` + `domain_normalizer.py:99/133`（快取→LLM→on_conflict）+ `glossary_extractor.py:78/122/177`（三步）。
- 儲存層本就開放：`context.py:62 raw_metadata: Dict[str,Any]={}` + `paper_manager` 整包存 `metadata_json`。
- 前端寫死 key：`static/index.html:1960-1961 user_tags`、扉頁 authors/venue/doi（動態欄不顯示之證）。
- C/D 實件暴露（`Ch37_Plant-Nutrition`）：封面課程/講師未進結構化 Meta、subtitle 掉正文。
- HOTFIX-2 已收 B/E/F（reading view 乾淨）→ 本任務專注 C+D 之結構化與顯示。

## §3 觀察問題

對齊 plan §3.2：C（封面 metadata 未進結構化 Meta，文件千百種不該寫死 schema）+ D（小標題無 subtitle 欄塞正文）；baron 構想＝LLM 開放抽取 + 二次 LLM 比對既有欄統一＝DOMAIN-NORM 飛輪搬到 metadata 欄名。

## §4 設計方案（對齊 plan §2 U1-U9 + U5.1/U7.1/U9.1/U9.2）

### §4.1 C1 — Schema & Flag
`models.py` 新增（繼承 Domains/DomainMapping 範式、既有表 byte 不動、create_all 自動建）：
- `MetaField`：`canonical_key`(PK/Unique)、`label_zh`/`label_en`、`category`(cover/page/general)、`source`(auto_register/manual)、`sort_weight:int`(預設 0、BS7)。
- `MetaFieldAlias`：`raw_key`(PK/Unique、寫入前 `.strip().lower()`)、`canonical_key`(FK→MetaField、`ondelete/onupdate=CASCADE`·BS6)。
`settings.py` 加 `LLM_USE_META_NORM = os.getenv(...) == "true"`（預設 False、U5）。
seed 小種子（Q1）：course/instructor/organization/date/venue/doi 連 i18n 標籤 + sort_weight，於 create_all 後冪等註冊（`on_conflict_do_nothing`）。

### §4.2 C2 — MetaNormalizer Flywheel
新建 `processor/meta_normalizer.py`：
- `normalize_fields(raw_fields: Dict[str,str], context: str="") -> Dict[canonical_key, str]`：
  ① `reserved` 名單（title/authors/venue/doi·BS1）命中 → 不進飛輪、回傳特殊標記交 P1 回填合約。
  ② 泛用詞黑名單（date/time/name/title/class/type/status/id/no/code/user·Q9/U5.1）→ **不查快取**、每次過 LLM 帶 context。
  ③ 非黑名單 → `_cache_lookup`(MetaFieldAlias、`.strip().lower()`)；命中直用。
  ④ 未命中 → **一次批次 LLM** 比對「自提欄名 vs 既有 MetaField 全集」→ 類似映既有、否則提新 canonical **+ label_zh/en 提案**（BS4）。
  ⑤ `on_conflict_do_nothing` 動態註冊 MetaField（含 label/sort_weight 預設）+ 寫 alias 快取（極短交易、冪等·BS5、**LLM 在交易外**）。
- 旗標 off → 直接回傳 raw_fields 原樣（不查 LLM、不寫表）。
- 誤併防護（U4/Q2）：比對 LLM temp=0 + 保守 prompt「僅明確同義才併、否則新欄」。

### §4.3 C3 — P1 Wire（slide_pipeline）
`run_phase1` 封面段：
- Vision cover prompt 改「**自由列出此封面所有 metadata（key-value、欄名自定）**」取代寫死 `{company,date,authors}`；**封面判定放寬**（容主視覺圖之學術封面、解 C 誤判·U6）。
- 抽出 raw_fields → `MetaNormalizer.normalize_fields`（旗標 on）→ canonical dict → 寫 `ctx.raw_metadata[canonical]`＝**三欄 dict `{value,source,confidence}`**（HOTFIX-1b 契約·U7）。
- reserved 命中（author/venue/doi）→ 回填 `IngestionMetadataSpec` 對應欄、不進旁路（U7.1）。
- 旗標 off → 退回現行 `{company,date}` 行為（向後相容）。

### §4.4 C4 — Subtitle
`_VISION_PROMPT`/`_COVER_PROMPT` schema 加 `subtitle` 欄（prompt 教分大/小標題）；P1 units 收 subtitle；P3 `_deliver`/`_page_source_md` 還原渲染 `### {subtitle}`（在 `## {title}` 後、圖前）；無內容差異分隔頁可用 subtitle 補 page title/key（U8、A 仍不主動去重）。

### §4.5 C5 — Frontend Generic Renderer
`static/index.html` 扉頁/toolbar 加通用 key-value 渲染器：讀 `metadata_json` canonical 欄、用 label 顯示（無 → 裸 key fallback·U9）；**排除集**過濾既有寫死欄（authors/venue/doi/translated_abstract/user_tags·U9.1、與 C3 reserved 共用清單）；**排序** sort_weight→字母序 fallback（U9.2）。

### §4.6 C6 — Tests
新建 `tests/test_meta_norm.py`：飛輪五步（快取命中 0 LLM / 比對映既有 / 無類似註冊新+label / 併發 on_conflict / 旗標 off 退原樣）+ Q9 黑名單不快取 + Q2 不誤併（date vs due_date）+ reserved 回填合約 + **§7.2 整合**（FakeVision 自提 `課程` → FakeLLM 映 `course` → upsert 式 `.get('course',{}).get('value')` 取值成功，raw_key≠canonical 仍對齊）+ 三欄 dict 契約（防 HOTFIX-1b 回歸）。slide_pipeline subtitle 渲染測試補入 `test_slide_pipeline.py`。

### §4.7 checkout — 收官與文件歸檔
Conformance（plan U1-U9+U*.1 / §6 驗收 / §7 不可動 / 提示詞稽核 / msg / §7.2 整合必驗）→ 母 plan v10 登記 META-NORM 條目（.bak + HTML 包裹）→ baton 一次性 mv（plan/tasks/C1-checkout 報告）+ git add → TODO 結案 + hash 自癒 → msg /tmp。

---

## §5 風險（對齊 plan §5）

| 風險 | 緩解 |
|---|---|
| DB schema 變動（2 表） | 純新增、既有 byte 不動、create_all；旗標 off 不用（baron 已 §1.6 點頭）|
| 誤併欄位 | C2 temp=0 + 保守 prompt + 寧分勿併（Q2）|
| 泛用詞快取誤路由 | C2 黑名單不快取（Q9/U5.1）|
| 凍結合約雙重表示 | C3 reserved 回填合約（U7.1/BS1）|
| 前端雙重渲染 | C5 排除集（U9.1/BS2）|
| 併發冪等 | C1/C2 PK/Unique + on_conflict（BS5）|
| 旗標 off 退化 | 各 commit 旗標閘門、預設 False 向後相容 |
| 三欄 dict 漏 | C3/C6 契約測試（防 HOTFIX-1b 回歸）|

## §6 測試計畫

### §6.1 C1 驗收
- pytest：create_all 後兩表存在、seed 6 欄註冊、FK CASCADE 設定、sort_weight 欄;旗標預設 False。
- grep：`grep -n "class MetaField\|class MetaFieldAlias" models.py`；`grep -n "LLM_USE_META_NORM" settings.py`。
- SOP：seed 註冊 `on_conflict_do_nothing`、無裸 commit。

### §6.2 C2 驗收
- pytest：§4.6 飛輪五步 + 黑名單 + 不誤併 + reserved + 旗標 off。
- grep：`grep -n "def normalize_fields\|on_conflict_do_nothing\|reserved\|黑名單" processor/meta_normalizer.py`；裸 commit grep 0（LLM 交易外）。

### §6.3 C3 驗收
- pytest：開放抽取→normalize→`raw_metadata[canonical]` 三欄 dict；reserved 回填合約;旗標 off 退現行。
- grep：`grep -n "normalize_fields\|raw_metadata\[" slide_pipeline.py`；封面 prompt 開放抽取措辭。

### §6.4 C4 驗收
- pytest：Vision schema 含 subtitle;P3 渲染 `### {subtitle}`;分隔頁 subtitle 補 key 不撞。
- grep：`grep -n "subtitle" slide_pipeline.py`。

### §6.5 C5 驗收
- pytest/grep：`static/index.html` 通用渲染器 + 排除集 + 排序;既有寫死欄不受影響（grep user_tags/authors 渲染保留）。

### §6.6 C6 驗收
- `pytest tests/test_meta_norm.py -v` 全綠 + **§7.2 整合通過** + 全套件不退化。

### §6.7 checkout 驗收
- Conformance 全維度（含 §7.2 必驗）;母 plan META-NORM 登記;baton 0 殘留（PIPE-SPEC 長駐除外）。

### §6.8 全任務 E2E（baron、plan §8.2）
影子重傳 `Ch37`：toolbar 顯課程/講師（canonical+中文標籤）/ 分隔頁 subtitle / 重跑 canonical key 一致（飛輪收斂）/ 換商業簡報自動長 company 欄不誤併。

## §7 不可動清單（對齊 plan §6）

- [ ] 既有 DB 表（Paper/PaperChunk/Domains/DomainMapping/GlobalGlossary…）schema byte 不動——僅**新增** 2 表。
- [ ] 凍結合約 `IngestionMetadataSpec`（extra='forbid'）——canonical 額外欄走 raw_metadata 旁路、不擴合約。
- [ ] DOMAIN-NORM/GLOSSARY-CORE/Translator 三真理源本體——只參照範式、不改。
- [ ] HOTFIX-1/1b/2 落地之 slide_pipeline 既有區塊（_safe_alt/_strip_master_date/_normalize_paragraph_breaks/_strip_title_echo/F2 旁路）——不重疊、不回退。
- [ ] A 軌 / rag_indexer / orchestrator / web_server 影子派發。
- [ ] 既有前端寫死欄（user_tags/translated_abstract/扉頁 authors/venue/doi）——保留、通用渲染為補充。
- [ ] 母 plan / PIPE-SPEC 本體（純引用；checkout 僅登記 META-NORM 條目一處）。

## §8 推薦 Commit 拆分

### C1 — Schema & Flag（登記表與旗標）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `models.py`（+MetaField/MetaFieldAlias）/ `settings.py`（+LLM_USE_META_NORM + seed 常數）/ `tests/test_meta_norm.py`（新建·schema 測試）|
| **安全性** | 🟢 高 — 純新增表/旗標、既有 byte 不動、旗標預設 False |
| **可逆性** | 🟢 高 — 刪表定義 + revert；create_all 不影響既有 |
| **驗收 grep 條件** | §6.1（class 兩表 grep + LLM_USE_META_NORM grep + pytest seed/CASCADE）|
| **依賴關係** | 無前置 |
| **具體實作細節** | 依 §4.1：繼承 Domains 範式定義兩表（PK/Unique/FK CASCADE/sort_weight）；settings 旗標；seed 6 欄 on_conflict_do_nothing 冪等註冊；`# === [META-NORM C1 ...] ===` 包裹 models/settings 修改處 |

### C2 — MetaNormalizer Flywheel（自癒飛輪）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `processor/meta_normalizer.py`；`tests/test_meta_norm.py` 追加 |
| **安全性** | 🟢 高 — 旗標 off 直接回傳原樣、LLM 交易外、on_conflict 冪等 |
| **可逆性** | 🟢 高 — 刪檔 |
| **驗收 grep 條件** | §6.2（normalize_fields/on_conflict/reserved/黑名單 grep + 裸 commit 0 + 飛輪 pytest）|
| **依賴關係** | 前置 C1（消費兩表）|
| **具體實作細節** | 依 §4.2 五步 + 黑名單（Q9）+ reserved（BS1）+ label 提案（BS4）+ 旗標閘門 + temp=0 保守比對（Q2）；鏡像 domain_normalizer 快取/註冊範式 |

### C3 — P1 Wire（開放抽取與封面放寬接線）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/slide_pipeline.py`（run_phase1 封面段 + cover prompt）；`tests/test_slide_pipeline.py` 追加 |
| **安全性** | 🟡 中 — 動 P1 封面邏輯；旗標 off 退現行向後相容、測試鎖 |
| **可逆性** | 🟢 高 — 包裹區塊 revert |
| **驗收 grep 條件** | §6.3（normalize_fields/raw_metadata[ grep + 三欄 dict pytest + reserved 回填）|
| **依賴關係** | 前置 C2 |
| **具體實作細節** | 依 §4.3：cover prompt 開放抽取 + 封面判定放寬 + normalize → 三欄 dict（HOTFIX-1b 契約）+ reserved 回填合約 + 旗標 off 退現行；`# === [META-NORM C3 ...] ===` 包裹 |

### C4 — Subtitle（小標題結構化）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/slide_pipeline.py`（Vision schema +subtitle + P3 渲染）；`tests/test_slide_pipeline.py` 追加 |
| **安全性** | 🟡 中 — 改 Vision prompt schema（影響輸出/golden）；測試鎖 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.4（subtitle grep + P3 ### 渲染 pytest）|
| **依賴關係** | 前置 C3（同 P1/Vision 區）|
| **具體實作細節** | 依 §4.4：schema 加 subtitle、prompt 教分大/小標題、P3 `### {subtitle}` 渲染、分隔頁補 key |

### C5 — Frontend Generic Renderer（前端通用渲染）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（通用 key-value 渲染器）|
| **安全性** | 🟡 中 — 前端；既有寫死欄保留、排除集防雙顯 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.5（渲染器 + 排除集 + 排序 grep；既有欄不受影響）|
| **依賴關係** | 前置 C1（讀 MetaField label）+ C3（canonical 欄存在）|
| **具體實作細節** | 依 §4.5：讀 metadata_json canonical 欄、label 顯示、排除集（U9.1 與 reserved 共用）、sort_weight→字母序排序（U9.2）；FE 手動 E2E 核查無 console error |

### C6 — Tests（測試補全）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_meta_norm.py` + `tests/test_slide_pipeline.py` |
| **安全性** | 🟢 高 — 純測試；嚴禁為過測試改業務碼（不符停下回報）|
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.6（全綠 + §7.2 整合 + 全套件不退化）|
| **依賴關係** | 前置 C1-C5 |
| **具體實作細節** | 依 §4.6：飛輪單元 + Q9 黑名單 + Q2 不誤併 + reserved 回填 + **§7.2 key-changing 整合**（raw_key≠canonical 對齊）+ 三欄 dict 契約 |

### checkout — 收官與文件歸檔（收官與文件歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 母 plan v10（META-NORM 條目登記、.bak）；歸檔/TODO/hash；零業務碼 |
| **安全性** | 🟢 高 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.7（Conformance 全維度含 §7.2 必驗 + 母 plan 登記 grep + baton 0 殘留）|
| **依賴關係** | 前置 C1-C6 全 commit |
| **具體實作細節** | 依 §4.7：Conformance → 母 plan 登記（HTML 包裹）→ baton 一次性 mv（plan/tasks/C1-checkout 報告 → plans//tasks//executions/）+ git add → TODO 完成表+索引 ✅ + hash 自癒 → msg /tmp |

> **各 Run 執行報告**：C1-C6 各產 `_執行.md`（template_execution、暫存 baton、嚴禁 mv/git add）；checkout 一次性歸檔。
> **E2E/golden（baron 運維、非 commit）**：§6.8；Vision schema 改（C3/C4）→ slides golden 重捕。

## §9 Open Questions

plan §9 八題 OQ + Q9/Q10 全定案（v1.2）；tasks 階段無新增 OQ。

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | META-NORM commit 拆分與驗收清單 |
| 權威源 | 本檔 §8（依 plan v1〔v1.2〕U1-U9+U*.1 + Q1-Q10 定案）|
| 引用方 | C1-checkout Run/Checkout 執行報告 |
| 不可動唯一源 | §7（對齊 plan §6）|
| 改版觸發 | §8/§6 變動 |
| 重複防護 | 飛輪範式唯一源在 DOMAIN-NORM；本 tasks 僅實例化 metadata 欄名 |

### §99.2 Revision 歷程
- v1 (2026-06-11)：初稿——7 commit（C1 schema+旗標+seed / C2 MetaNormalizer 飛輪〔五步+黑名單 Q9+reserved BS1+label BS4+旗標〕/ C3 P1 開放抽取+封面放寬接線〔三欄 dict+reserved 回填〕/ C4 subtitle / C5 前端通用渲染〔排除集 BS2+排序 BS7〕/ C6 測試〔含 §7.2 key-changing〕/ checkout 收官+母 plan 登記）+ §0.5 盤點 + §6 逐 commit 驗收 + §7 不可動（含 schema/合約/HOTFIX 區塊保護）+ §8 六維度表；依 plan v1.2 全定案規格
