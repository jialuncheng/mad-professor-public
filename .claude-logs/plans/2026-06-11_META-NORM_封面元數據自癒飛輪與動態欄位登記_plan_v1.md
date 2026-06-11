# META-NORM 封面元數據自癒飛輪與動態欄位登記 plan v1

> 工作流類別：**BE-Refactor**（新增 DB 表 + 自癒器 + Vision 接線 + 前端通用渲染；含 schema 變動）
> 必讀 SOP：logging_SOP + database_SOP
> 任務代號：**META-NORM**（PIPE 共用真理源家族第 4 員：DOMAIN-NORM / GLOSSARY-CORE / TRANSLATOR → **META-NORM**）
> 定位：解 PIPE-SLIDES 學術簡報實測暴露之 **C（封面 metadata 未抽進結構化 Meta）+ D（小標題 subtitle 未抓）**；以 baron 構想之「LLM 開放抽取 + 第二次 LLM 比對既有欄位統一」＝**DOMAIN-NORM 知識飛輪範式搬到 metadata 欄名**。

---

## §0 改版規則
- 改版觸發：§2 / §4 / §9 任一變動 → 改章節 + §99.2 加 Revision
- 多輪 review 累積（§1.9）：v1 初稿（baron 設計討論：滾動式動態欄位 + 二次 LLM 比對統一）→ **v1.1 baron review 八 OQ 定案 + 盲點掃描 BS1-BS4 + Q9/Q10** → **v1.2 Q9/Q10 定案 + BS5-BS7 補強 → 凍結、可進 tasks**

---

## §1 TL;DR（概要）

不把封面 metadata 欄位**寫死**（文件千百種：學術簡報有課程/講師、商業簡報有公司/日期、論文有 venue/DOI…），改用**自癒飛輪**：

1. **P1 開放抽取**：Vision 對封面**自由判斷有哪些 metadata、自提欄位**（不限定 schema）。
2. **第二次 LLM 比對統一**（baron 構想核心）：把 LLM 自提的欄名，比對**既有欄位登記表**——語意類似 → **統一用既有 canonical key**；無類似 → **動態註冊新 canonical 欄**。
3. **持久化 + 顯示**：canonical 欄（+ 未映射 extras）走既有 `raw_metadata` 旁路存 `metadata_json`；前端**通用 key-value 渲染器**顯示（標準欄帶 i18n 標籤）。
4. **subtitle（D）併入**：同屬「Vision 結構化豐富化」，Vision schema 加 `subtitle` 欄、還原渲染為次級標題。

**範式直接繼承 DOMAIN-NORM**（`models.py:230 Domains`/`255 DomainMapping` + `domain_normalizer.normalize_to_lcc` 快取→LLM→`on_conflict_do_nothing` 動態註冊）——抄三步飛輪、抄冪等併發、抄交易外 LLM。**新增僅「欄位登記表」一張 + 一個 `MetaNormalizer`**。

**架構零阻力證據**：`raw_metadata: Dict[str,Any]={}`（context.py:62）本就開放、`upsert_paper` 整包存 `metadata_json`（freeform）——動態欄**儲存端零改**；真正工作量在「比對統一飛輪 + 前端通用渲染」。

---

## §2 目標規格

### A. 欄位登記表（DB schema、繼承 Domains 範式）

| # | 規格 |
|---|---|
| U1 | 新增 `MetaField`（canonical 欄位登記）表：`canonical_key`(**PK / Unique**、如 `course`/`instructor`/`organization`)、`label_zh`/`label_en`(顯示標籤)、`category`(cover/page/general)、`source`(auto_register/manual)、**`sort_weight: int`(顯示排序權重、預設 0、seed 欄給序、無則前端 fallback 字母序·BS7)**；__既有 Paper 等表 byte 不動、create_all 自動建表__ |
| U2 | 新增 `MetaFieldAlias`（別名→canonical 快取、繼承 DomainMapping 範式）：`raw_key`(**PK / Unique**、LLM 自提原始欄名、**寫入前一律 `.strip().lower()` 正規化**防 `Date`/`date` 重複註冊)、`canonical_key`(**FK→MetaField、`ondelete=CASCADE` / `onupdate=CASCADE`**·BS6 便利未來欄位合併/清理)；命中即**快取免重複問 LLM**。**併發**：`on_conflict_do_nothing` 寫入（PK/Unique 保證多 worker 同時提同新欄不拋 IntegrityError、不中斷管線·BS5，抄 DOMAIN-NORM）|

### B. MetaNormalizer 自癒器（繼承 DomainNormalizer 範式）

| # | 規格 |
|---|---|
| U3 | `processor/meta_normalizer.py`：`normalize_fields(raw_fields: Dict[str,str]) -> Dict[canonical_key, value]`——① 快取查 `MetaFieldAlias`（命中直用）② 未命中 → **一次批次 LLM** 比對「LLM 自提欄名 vs 既有 `MetaField` 全集」→ 類似則映既有、否則提新 canonical（**比對 LLM 同時回傳新欄之 `label_zh/label_en` 提案**·盲點 BS4，否則自動註冊欄無標籤、前端只能 fallback 裸 key）③ `on_conflict_do_nothing` 動態註冊 MetaField（含 label）+ 寫回 alias 快取（極短交易、冪等、**LLM 在交易外**） |
| U4 | 誤併防護：比對 LLM temp=0 + 保守 prompt（「僅在語意明確同義時合併、否則視為新欄」）+ 信心門檻；模糊者寧可註冊新欄（可後續手動合併、勝過錯併） |
| U5 | 旗標閘門 `LLM_USE_META_NORM`（預設 False）：off 時退回「extras 原樣存、不正規化、不查 LLM」→ 線上 0 風險、可漸進開啟（同 DOMAIN-NORM `LLM_USE_GLOSSARY_ALIGN` 先例） |
| **U5.1**（Q9 定案·泛用詞不快取） | **泛用單字黑名單**（`date/time/name/title/class/type/status/id/no/code/user` 等）：此類 raw_key **不寫 alias 快取、每次強制過 LLM 帶 cover 上下文判定**（cover 抽取每文件僅一次、低頻、正確性收益遠大於延遲）；非泛用詞照 U2 快取。黑名單比對亦走 `.strip().lower()` |

### C. P1 接線（開放抽取 + 正規化）

| # | 規格 |
|---|---|
| U6 | `slide_pipeline.run_phase1` 封面判定：Vision prompt 改「**自由列出此封面所有 metadata 欄位（key-value，欄名自定）**」取代寫死 `{company,date,authors}`；**並放寬封面判定**（容許含主視覺圖之學術封面、解 C 之封面誤判）|
| U7 | 抽出之 raw_fields → `MetaNormalizer.normalize_fields`（旗標 on）→ canonical dict → 寫 `ctx.raw_metadata`（**三欄 dict 格式** `{value,source,confidence}`、對齊 HOTFIX-1b 修正之 upsert 契約）；title/authors 仍走凍結合約 `IngestionMetadataSpec`、其餘 canonical 欄走旁路 |
| **U7.1**（盲點 BS1·凍結合約邊界） | **凍結合約已擁有之欄位（title/authors/venue/doi）不得再註冊為動態 canonical 欄**：MetaNormalizer 內置「保留名單（reserved）」——LLM 自提之 `作者/author/venue/期刊/DOI…` 比對命中 reserved → **回填凍結合約欄、不進登記表、不進旁路**；防同一資料雙重表示（重蹈 RAG-MULTI-1「同人 A+B 軌重複代表」式設計副作用）|

### D. subtitle 結構化（併入）

| # | 規格 |
|---|---|
| U8 | Vision schema 加 `subtitle` 欄（prompt 教分大/小標題）；P3 還原渲染為次級標題（`### {subtitle}` 或樣式化）；**無內容差異之分隔頁可用 subtitle 補 page title/key**（順帶弱化重複大標題、但 A 仍不主動去重——忠實轉錄） |

### E. 前端通用渲染（顯示飛輪產物）

| # | 規格 |
|---|---|
| U9 | 前端扉頁/toolbar 新增**通用 key-value 渲染器**：讀 `metadata_json` 之 canonical 欄、用 `MetaField.label_zh/en` 顯示（無對應標籤 → 原 key fallback）；既有寫死欄（user_tags/translated_abstract/authors/venue/doi）保留、新欄通用渲染補充 |
| **U9.1**（盲點 BS2·防雙重渲染） | 通用渲染器**必須排除「已由既有寫死路徑渲染之 canonical 欄」**（authors/venue/doi/translated_abstract/user_tags）——以一份「hardcoded-rendered 排除集」過濾，避免扉頁 venue + 通用器 venue 雙顯；與 U7.1 reserved 名單共用同一份清單（單一真理源）|
| **U9.2**（BS7·顯示穩定排序） | 通用渲染器之動態欄**必排序**：優先 `MetaField.sort_weight` 升序、tie/缺則 `canonical_key` 字母序 fallback；防同一文件每次重傳欄序跳動、保視覺穩定 |

---

## §3 現況與證據

### §3.1 grep 鋼鐵證據
```
# 儲存層本就開放（動態欄零阻力）
pipelines/context.py:62  raw_metadata: Dict[str, Any] = {}
paper_manager.py:213/254 metadata 整包存 metadata_json（freeform JSON）

# 飛輪範式現成可抄
models.py:230 class Domains / :255 class DomainMapping / :282 class GlobalGlossary
processor/domain_normalizer.py:99 _cache_lookup / :133 _register_and_cache（on_conflict_do_nothing 冪等、LLM 交易外）
processor/glossary_extractor.py:78 query_cascade / :122 extract_terms / :177 upsert_terms（飛輪三步）

# 前端寫死 key（動態欄不顯示之證）
static/index.html:1960-1961 p.metadata.user_tags / p.metadata_json.user_tags（寫死）
# 扉頁 authors/venue/doi 由 _render_header 寫死（C 之動態欄無處顯示）

# C/D 實件暴露（植物營養 Ch37）
封面課程 LS1005/普通生物學甲/講師鄭佳宜 → 留正文、未進結構化 Meta
分隔頁小標題 availability+accessibility+retention → 塞 markdown_content 當普通段落
```

### §3.2 動因（PIPE-SLIDES 實測收斂）
HOTFIX-2 收 B（alt 破圖）/ E（母片日期）/ F（條列鬆排）後，reading view 已乾淨；**剩 C（結構化 metadata）+ D（subtitle）屬 Vision schema 豐富化、同根** → baron 拍板用「滾動式動態欄位 + 二次 LLM 比對統一」一次設計（本 plan）。A（重複標題）已撤案（忠實轉錄）。

---

## §4 跨 Phase 接縫契約（WORKFLOW_SOP §7）

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| 封面 canonical metadata | P1 `MetaNormalizer.normalize_fields` 產 `{canonical_key: {value,source,confidence}}` | web_server 影子寫庫 `upsert_paper` → `metadata_json` → 前端通用渲染 | key＝**MetaField.canonical_key**（登記表唯一收斂）；P1 寫入與前端讀取**同以 canonical_key 為基準**、不得各自用 LLM 原始自提名（否則重蹈 key-drift） |
| alias→canonical 映射 | `MetaNormalizer` 二次 LLM 比對 + 寫 `MetaFieldAlias` | 下次同 raw_key 之 `_cache_lookup` | raw_key（LLM 自提原名）→ canonical_key；**一旦註冊即凍結**、後續同 raw_key 必映同 canonical（快取保證收斂、同 DomainMapping） |
| subtitle | P1 Vision `subtitle` 欄 | P3 還原 `### {subtitle}` + 可選補 page key | subtitle 為頁級顯示字串；若補 page key 則與 `page_key()` 同基準（沿 PIPE-SLIDES §4 契約） |
| 三欄 dict 格式 | P1 寫 `raw_metadata[canonical_key]` | `upsert_paper` L231 `.get('value')` / web_server L714 `['value']` | **必為 `{value,source,confidence}` dict**（HOTFIX-1b 血淚契約、裸 str 會炸影子寫庫）|

> 反例錨點：① 前端直接顯示 LLM 自提原名 → 同概念多名（課程/course/class_code）漂移（DOMAIN-NORM 已證）。② raw_metadata 塞裸 str → AttributeError（HOTFIX-1b 已證）。**凍結：canonical_key 收斂 + 三欄 dict。**

---

## §5 變動風險與相容性評估

| 風險 | 評估 | 緩解 |
|---|---|---|
| **DB schema 變動**（新 2 表） | 中、§1.6 強制問 baron | 純新增表、既有表 byte 不動、create_all 自動建；旗標 off 時不建/不用 |
| 二次 LLM 比對成本/延遲 | 低（cover 1 頁低頻） | 批次比對（一次比全部提欄）+ alias 快取命中 0 呼叫（同 DOMAIN-NORM）|
| **誤併欄位**（date vs due_date） | 中、影響資料正確性 | U4 temp=0 + 保守 prompt + 信心門檻 + 模糊註冊新欄（寧分勿錯併）|
| 決定性/golden（登記表演進 → 同件 T1/T2 映不同） | 低、可接受（DOMAIN-NORM 同性質、收斂） | golden meta 區改「canonical key 集合比對」或豁免；登記表收斂後穩定 |
| 前端通用渲染未做 → 動態欄存了不顯示 | 中 | U9 同 plan 交付（否則飛輪半截、C 顯示面未解）|
| 併發冪等 | 低 | `on_conflict_do_nothing` 抄 DOMAIN-NORM |
| 旗標 off 行為退化 | 低 | U5 預設 False、extras 原樣存、線上 0 風險 |
| **凍結合約欄位雙重表示**（BS1） | 中、資料重複 | U7.1 reserved 名單回填合約、不進旁路 |
| **前端雙重渲染**（BS2） | 低、視覺 | U9.1 排除集過濾、與 reserved 共用清單 |
| **泛用模糊 raw_key 快取誤路由**（BS3·review 漏點）：`date`/`name`/`title` 等單字欄極依語境，alias 快取一旦 `date→publish_date` 釘死，後續「date 實為 due_date」之件**走快取直接誤映、不再問 LLM** | 中、跨件語意污染（DOMAIN-NORM 領域字串較不歧義故未顯，metadata 單字欄歧義高） | 見 §9 Q9：泛用單字 raw_key **不快取**（每次過 LLM 帶 cover 上下文）或加 context 維度；保守起見先「黑名單泛用詞不快取」（Q9 定案、落 U5.1）|
| **欄位合併/清理 FK 報錯**（BS6） | 低、維運 | U2 `MetaFieldAlias` FK `ondelete/onupdate=CASCADE` |
| **動態欄顯示順序跳動**（BS7） | 低、視覺 | U1 `sort_weight` + U9.2 排序、fallback 字母序 |

---

## §6 不可動清單

- [ ] 既有 DB 表（Paper / PaperChunk / Domains / DomainMapping / GlobalGlossary 等）schema byte 不動——僅**新增** MetaField/MetaFieldAlias。
- [ ] 凍結合約 `IngestionMetadataSpec`（title/authors/venue/doi/source_lang/tiles、extra='forbid'）——canonical 額外欄走 `raw_metadata` 旁路、不擴凍結合約。
- [ ] DOMAIN-NORM / GLOSSARY-CORE / Translator 三真理源本體——只參照範式、不改。
- [ ] HOTFIX-2 落地之 B/E/F（_safe_alt/_strip_master_date/_normalize_paragraph_breaks）——不重疊、不回退。
- [ ] A 軌全部 / rag_indexer / orchestrator。
- [ ] 既有前端寫死欄（user_tags/translated_abstract/扉頁 authors/venue/doi）——保留、通用渲染為**補充**非取代。

---

## §7 規格依據

- 母 plan v10：§8.5 PIPE-SLIDES（C/D 為其實測暴露之後續）/ 五路絞殺；PIPE 共用真理源家族
- PIPE-SPEC：§1.1 四凍結合約（raw_metadata 旁路定位）/ §1.3.1 Vision 共用規格（subtitle 擴充歸此）
- 範式先例：DOMAIN-NORM plan（Domains/DomainMapping + normalize_to_lcc 飛輪）/ GLOSSARY-CORE plan（query_cascade→extract→upsert + 旗標閘門）
- 血淚契約：HOTFIX-1b（raw_metadata 三欄 dict）/ RAG-ASYNC #1（key 不漂移）
- 實件：`Ch37_Plant-Nutrition.pdf`（封面課程/講師未進 Meta、subtitle 掉正文）

---

## §8 驗證計畫

### §8.1 自動化單元測試
1. `MetaNormalizer`：快取命中 0 LLM；未命中 → 比對映既有 canonical；無類似 → 註冊新 + 寫 alias；併發 `on_conflict_do_nothing` 不炸；旗標 off 退 extras 原樣。
2. 二次比對：`課程`/`course`/`class_code` → 同一 canonical；`date` vs `due_date` 不誤併（保守 prompt 測試）。
3. 交易邊界：LLM 在 `session.begin()` 外（database SOP §5.2 grep 無裸 commit）。
4. P1 接線：開放抽取 → normalize → `raw_metadata[canonical]` 為**三欄 dict**（防 HOTFIX-1b 回歸）。
5. subtitle：Vision `subtitle` 欄 → P3 `### ` 渲染；分隔頁補 key 不撞（沿 page_key）。
6. **§7.2 跨 Phase 整合測試**：P1 開放抽取（FakeVision 自提 `課程`）→ MetaNormalizer（Fake LLM 映 `course`）→ upsert_paper 式消費 `.get('course',{}).get('value')` 取值成功（key-changing：raw_key≠canonical_key 仍對齊）。
7. 前端通用渲染：canonical 欄 + label 顯示、未知 key fallback、既有寫死欄不受影響。

### §8.2 手動 E2E（baron）
影子重傳 `Ch37`：① toolbar/扉頁顯示**課程 LS1005 / 普通生物學甲 / 講師 鄭佳宜**（canonical 欄 + 中文標籤）② 分隔頁顯示小標題（subtitle）③ 重跑兩次 canonical key 一致（飛輪收斂）④ 換不同類型簡報（商業/論文）→ 自動長出 company/venue 等欄、不誤併。

---

## §9 Open Questions

### §9.1 八題定案（2026-06-11 baron review 拍板、八題 100% 認同）

| # | 問題 | 定案 |
|---|---|---|
| ~~Q1~~ | 登記表粒度 | **✅ 預植小 seed（course/instructor/organization/date/venue/doi）+ 動態長**——常見欄即時有中文標籤、冷門飛輪補、避免冷啟裸 key |
| ~~Q2~~ | 誤併門檻 | **✅ 保守（明確同義才併、模糊註冊新欄）+ temp=0**——誤併破壞語意難回溯、寧分勿併、後續可手動合併 |
| ~~Q3~~ | subtitle 併入 | **✅ 併入**——同內聚於 P1 prompt + P3 渲染、一次重捕 golden |
| ~~Q4~~ | 前端通用渲染同 plan | **✅ 同 plan 做**——否則 baron 無法 E2E 驗飛輪產物、不符 end-to-end |
| ~~Q5~~ | golden meta 策略 | **✅ canonical key 集合比對 + value 模糊**——登記表動態生長、字元級必誤報紅燈 |
| ~~Q6~~ | 旗標預設 | **✅ `LLM_USE_META_NORM=False`、漸進開**——含 schema 新增、影子先驗 Flip |
| ~~Q7~~ | 適用範圍 | **✅ 合約+模組五路通用、production 先 slides 接線**——MetaNormalizer doc_type-agnostic 作底座、絞殺序漸接 |
| ~~Q8~~ | 二次比對獨立/合併 | **✅ 獨立批次呼叫**——比對純文字可快取、alias 命中達 0 LLM、與昂貴 Vision 圖像呼叫職責分離 |

### §9.2 v1.1/v1.2 盲點掃描（§1.9 獨立對抗式 review、2026-06-11 baron 二輪拍板·全定案）

| # | 問題 | 定案 |
|---|---|---|
| ~~Q9~~ | 泛用模糊 raw_key 快取策略（BS3） | **✅ 黑名單不快取**——`date/time/name/title/class/type/status/id/no/code/user` 等泛用單字每次過 LLM 帶 cover 上下文（cover 低頻、正確性 > 微延遲）；非泛用詞照快取。配套：raw_key 一律 `.strip().lower()`（落 U5.1 + U2）|
| ~~Q10~~ | MetaNormalizer 落 P1 或 P2 | **✅ 落 P1**——cover 是 P1 Vision 產物、就地正規化使輸出即 canonical 乾淨字典、P2/影子寫庫免二次對齊；reserved（U7.1）亦於 P1 第一時間回填合約、避免傳髒結構。配套：LLM 必在 DB session 外、僅比對後極短交易 `on_conflict_do_nothing`（database SOP；**本專案 P1 走 thread/`asyncio.to_thread`、非 celery**）|

> BS1（凍結合約邊界·U7.1）、BS2（雙重渲染·U9.1）、BS4（自動註冊欄缺 label·U3）、**BS5（併發冪等·U2 on_conflict）、BS6（FK CASCADE·U2）、BS7（顯示排序·U1 sort_weight + U9.2）** 已直接補入規格、非待拍板項；§5 風險表同步登錄。
> **正向綜效（review 未提）**：本飛輪把封面結構化欄位（含 email/phone/課程）收斂進 canonical-keyed 旁路 → **直接餵養 CHAT-STRUCT-1（backlog #5 結構化欄位確定性回答）**——CHAT-STRUCT-1 之意圖路由可改查 canonical key、不必各自猜欄名；兩任務天然對接。

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 封面/頁面 metadata 自癒飛輪（動態欄位登記 + 二次 LLM 比對統一）+ subtitle 結構化 |
| 權威源 | 本檔 §2 / §4；範式繼承 DOMAIN-NORM / GLOSSARY-CORE |
| 引用方 | tasks / executions（待產）；PIPE-SLIDES C/D 後續 |
| 不可動唯一源 | §6 |
| 改版觸發 | §2/§4/§9 變動 |
| 重複防護 | 飛輪範式唯一源在 DOMAIN-NORM；本 plan 僅實例化到 metadata 欄名、不重寫飛輪定義 |

### §99.2 Revision 歷程
- v1.2 (2026-06-11)：baron 二輪拍板**Q9/Q10 全定案** + 細部補強——Q9 黑名單不快取（落 **U5.1** + U2 `.strip().lower()`）/ Q10 落 P1（LLM 交易外、**校正 review「celery worker」誤述：本專案 P1 走 thread/asyncio.to_thread**）；新增 **BS5 併發冪等**（U2 PK/Unique + on_conflict_do_nothing）/ **BS6 FK CASCADE**（U2 ondelete/onupdate）/ **BS7 顯示排序**（U1 `sort_weight` + U9.2 字母序 fallback）+ §5 兩風險列；§9 全題定案、**plan 凍結可進 tasks**（schema 新增 2 表待 §1.6 最終點頭）
- v1.1 (2026-06-11)：baron review 拍板**八題 OQ 全定案**（§9.1）+ **獨立盲點掃描補強**（§1.9 對抗式）——新增 **U7.1 凍結合約邊界**（BS1：title/authors/venue/doi reserved 名單回填合約、防雙重表示）/ **U9.1 防雙重渲染**（BS2：通用器排除既有寫死欄、與 reserved 共用清單）/ **U3 補 label 提案**（BS4：自動註冊欄需 LLM 回傳 label_zh/en）+ §5 三風險列 + §9.2 **Q9 泛用模糊 raw_key 快取策略**（BS3·review 漏點：黑名單不快取防跨件語意污染）/ **Q10 P1 vs P2 落點** + **正向綜效註：餵養 CHAT-STRUCT-1**；可進 tasks（Q9/Q10 待拍板、schema 變動待 §1.6 點頭）
- v1 (2026-06-11)：初稿——baron 構想（LLM 開放抽取 + 第二次 LLM 比對既有欄位統一）＝DOMAIN-NORM 飛輪搬到 metadata 欄名；U1-U9（MetaField/MetaFieldAlias 兩表 + MetaNormalizer 三步飛輪 + P1 開放抽取/封面判定放寬 + subtitle 併入 + 前端通用渲染）+ §4 四接縫契約（含 HOTFIX-1b 三欄 dict 血淚契約 + key-changing 整合）+ §9 八 OQ；解 PIPE-SLIDES 實測之 C+D，A 撤案、B/E/F 歸 HOTFIX-2
