# LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放策略 · plan v1

> 工作流類別：**BE-Refactor**（改 rag_retriever / ai_core / web_server / settings 業務邏輯）
> 必讀 SOP：logging_SOP + database_SOP（§5 SOP 核查）
> 跨模組 + handoff（loader callback）→ 適用 WORKFLOW_SOP §7 接縫契約（見 §4）

---

## §0 改版規則
- 改版觸發：§2 目標規格 / §4 接縫契約 / §9 OQ 任一變動 → 直接改章節 + §99.2 加 Revision
- 多輪 review 累積（§1.9）：v1 初稿 → 待 baron 過目 §9 OQ → v2

---

## §1 TL;DR（概要）

跨文件 hashtag 檢索（`#cv 比較…`）只召回「當前開著那一篇」、漏掉其餘 tagged 篇 → 答案誤判「只有一位候選人」。**根因＝ API-PERF C3 廢除啟動 preload、改 chat 端點只 lazy-load「當前 paper_id」一篇,但 `retrieve_multi_with_context` 需要「全部 tagged 篇」都已註冊**；未註冊者 `_get_vector_store` 回 None → `rag_retriever.py:260` 靜默 `continue` 跳過。

**修法（baron 拍板）**：
1. **③ retriever 自帶 lazy-load hook** —— `_get_vector_store` miss 時呼叫注入的 loader 自我載入。一處鎖點修好單篇/多篇/未來 attach 全部路。
2. **記憶體釋放策略改**：`RAG_MAX_CACHE` 5 → **100**（記憶體實測非瓶頸）+ **切換文章即釋放** + **60 分鐘閒置 TTL 釋放**。因選 ③（取庫即自載）、eager 釋放安全（誰被釋放下次自動重載）。

**非本任務**：RAG-MULTI-1 保底演算法（已落地、正確）；embedding 模型/regen（28 篇全 `-001`、無混用）。

---

## §2 目標規格（baron 已拍板項）

| # | 規格 | 狀態 |
|---|---|---|
| U1 | `RagRetriever` 新增 loader 註冊鎖點（`set_loader(fn)`）；`_get_vector_store` miss 且 loader 已設時自載後重試；**loader 未設時行為與現況完全一致（回 None）→ 向後相容** | 拍板（③）|
| U2 | web_server 啟動接線 `retriever.set_loader(lambda o,p: paper_manager.load_paper_resources(OUTPUT_DIR,o,p,ai_core))`；retriever **不** import paper_manager/web_server（僅存不透明 callable、零循環） | 拍板 |
| U3 | `#cv 比較…` 經 ③ 後 `retrieve_multi` 涵蓋全部 tagged 篇（每篇被搜→ RAG-MULTI-1 保底分配生效）；候選不再只剩當前篇 | 拍板（核心驗收）|
| U4 | `RAG_MAX_CACHE` 預設 5 → **100**（env 仍可覆寫） | 拍板 |
| U5 | 記憶體釋放：**(a) 切換文章即釋放** 前一工作集 + **(b) 60 分鐘閒置 TTL 釋放**；vector_stores + ai_core._paper_cache 一致套用 | 拍板（機制細節見 §9 OQ）|
| U6 | 釋放後正確性靠 ③ 自載保證（被釋放篇下次檢索自動重載、不回空） | 拍板 |

---

## §3 現況與證據

### §3.1 grep 鋼鐵證據

**① 根因——chat 端點只載當前一篇**（`web_server.py:797-802`）：
```python
# === [API-PERF C3] U3 按需 Lazy Load ===
if (current_user.id, paper_id) not in ai_core._paper_cache:
    paper_manager.load_paper_resources(OUTPUT_DIR, current_user.id, paper_id, ai_core)
```
→ 只載 URL 的 `paper_id`；tagged 其餘篇未載。

**② 跨文件檢索靜默跳過未載篇**（`rag_retriever.py:258-261`）：
```python
for pid in paper_ids:
    vs = self._get_vector_store(owner_id, pid)
    if vs is None:
        continue          # ← 未註冊篇靜默跳過
```
`_get_vector_store`（L88-105）：key 不在 `paper_vector_paths` → 回 None（無自載能力＝本任務要補的缺口）。

**③ 線上 log（PaperRead-Lab）**：
- `[P2-2 hashtag] tags=['cv'] matched_papers=6`（上游比對 6 篇 OK）
- `[retrieve_multi] papers=6 candidates=14 cap=15 floor=2 chosen=[14× 'YuLun_Wu_CV']`（只搜到當前篇、其餘 5 篇 0 候選）

**④ 資料層健康（反證非模型/非演算法）**：
- 28 篇 index_meta `embedding_model` 全 `gemini-embedding-001`（零混用、`.env` 同）。
- 獨立載入 6 篇履歷跑同 query：每篇 top 0.6-0.75、全 chunk >0.22（候選都在、是 server 沒搜）。

### §3.2 記憶體實測（du，PaperRead-Lab）
| 量級 | 代表 | 載入記憶體 |
|---|---|---|
| 最大書籍 | Mistakes Were Made 845 chunks（faiss 2.5M+pkl 1.2M）| 3.64 MB |
| 次大 | On Human Nature 479 | 2.08 MB |
| 履歷 | 5-24 chunks | 0.02-0.10 MB |
| **全 28 篇相加** | 整語料庫 | **≈ 13 MB** |
→ 向量（faiss）佔大頭、非 docstore；記憶體非瓶頸 → 支持 U4 cap=100。

### §3.3 現有釋放機制（待改）
- `retriever.vector_stores`：LRU cap 5 + `gc.collect()`（`rag_retriever.py:37-40`）✅ 釋放大宗。
- `ai_core._paper_cache`：LRU cap 5 + gc（`ai_core.py:104-108`）✅。
- `retriever.rag_trees` / `paper_vector_paths`：**永不淘汰**（`rag_retriever.py:24-26` 刻意）→ rag_trees 為長跑慢累積（附帶觀察、見 §9 OQ-Q4）。

---

## §4 跨 Phase 接縫契約（WORKFLOW_SOP §7）

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| lazy-load callback | web_server 啟動 `set_loader(λ o,p: load_paper_resources(OUTPUT_DIR,o,p,ai_core))` | `retriever._get_vector_store` miss 時呼 `self._loader(owner_id, paper_id)` | key＝`(owner_id, paper_uuid)` tuple；**consumer 傳給 loader 的 `paper_id` ≡ `retrieve_multi` 的 `paper_ids` 元素（來自 `list_paper_uuids_by_tag` 之 `paper_uuid`）≡ loader 寫回 `paper_vector_paths` 的 key**——三者同為 **paper_uuid 字串、單一基準**，不得各自決定 |
| 釋放/重載循環 | 釋放策略（切換/TTL）evict `vector_stores[key]` | 下次 `_get_vector_store(key)` 自載 | 同上 key；釋放只動記憶體 FAISS、`paper_vector_paths`/loader 保證可重載原篇 |

> 反例錨點（防 RAG-ASYNC #1 類）：若 loader 載入用 sanitize 後檔名、而 retrieve_multi 查找用 raw uuid → key 不同基準 → 自載後仍 miss。**契約凍結：全程 paper_uuid 原值、不轉換。**

---

## §5 變動風險與相容性評估

| 風險 | 評估 | 緩解 |
|---|---|---|
| retriever 介面變動 | 新增 `set_loader` + `_get_vector_store` 守衛；**loader 未設＝現況行為（回 None）** | 向後相容預設、既有測試不破 |
| import 循環 | retriever 存不透明 callable、不 import paper_manager | 啟動接線注入 |
| cap 5→100 | 記憶體 13MB 語料無虞 | env 可回調；TTL 仍兜閒置 |
| 切換即釋放誤刪跨文件比較所需篇 | ③ 自載兜底（再用即重載） | U6；§8 整合測試驗 evict→重載 |
| TTL sweep 機制（背景 task vs 惰性檢查）| 影響複雜度/精度 | §9 OQ-Q2 拍板 |
| 釋放後 reload I/O 抖動 | 跨文件迴圈逐篇 reload | tagged 數天然有界（<20）、I/O 小 |

---

## §6 不可動清單

- [ ] `retrieve_multi_with_context` **保底演算法**（RAG-MULTI-1 C2、`# === [RAG-MULTI-1 C2] ===`）——本任務只補「篇有沒有被載」、不碰「載到後怎麼分配」。
- [ ] `retrieve_with_context` 單篇邏輯（除 `_get_vector_store` 鎖點共用自載外、不改其檢索/格式）。
- [ ] context 輸出格式 `## 摘自文件《…》`。
- [ ] 向量資料 / FAISS / index_meta（不重嵌、不動建庫端）。
- [ ] embedding 模型 / RAG_SCORE_THRESHOLD / 上游 hashtag 解析（parse_query_hashtags / list_paper_uuids_by_tag）。
- [ ] A 軌 / shadow 過濾邏輯（維 U7 可見性）。

---

## §7 規格依據（grep 行號）

- `web_server.py:797-802`（C3 lazy-load 缺口）/ `rag_retriever.py:88-105`（_get_vector_store 無自載）/ `:258-261`（靜默跳過）/ `:37-40`（LRU）
- `ai_core.py:39-43`（add_paper_vector_store）/ `:104-108`（_paper_cache LRU）/ `paper_manager.py:457`（load_paper_resources 簽名）
- `settings.py:65`（RAG_MAX_CACHE）
- 線上 log：`[P2-2 hashtag] matched_papers=6` / `[retrieve_multi] chosen=[14× YuLun_Wu_CV]`

---

## §8 驗證計畫

### §8.1 自動化單元測試（新建 `tests/test_lazyload_multi.py`）
1. `test_get_vector_store_self_loads_on_miss`：key 不在 paper_vector_paths + loader 已設 → 呼 loader 後成功取庫。
2. `test_get_vector_store_loader_unset_returns_none`：loader 未設 → 回 None（向後相容、現況行為）。
3. `test_retrieve_multi_loads_all_tagged`（**§7.2 整合測試、key-changing**）：mock 6 篇,**只預註冊 1 篇**、其餘 5 篇靠 loader 自載 → 斷言 retrieve_multi 涵蓋全 6 篇（重現吳焴倫 bug 修復）。
4. `test_evict_then_reload`：載入→evict（切換/TTL 模擬）→ 再檢索自動重載、不回空（U6）。
5. `test_ttl_eviction_releases_idle`：last-access 超 TTL → sweep/惰性釋放;未逾時保留。
6. `test_switch_releases_previous`：切換文章訊號 → 前一工作集釋放。
7. `test_cap_100_default` + env override。
- 全套件不退化。

### §8.2 手動 E2E（baron · PaperRead-Lab）
1. 重啟 server（清空快取）→ 直接 `#cv 比較這幾位候選人的學歷背景`（不先逐篇開）→ 答案**涵蓋全部 6 位**（吳焴倫/黃忠偉/DeHunt/Priyal/林晉羽）。
2. log 驗 `[retrieve_multi] chosen=[…]` 含 ≥5 種不同 pid（非單一霸榜）。
3. 切換文章 → log 見前篇釋放;閒置 60min → log 見 TTL 釋放;之後再問仍正確（自載）。

---

## §9 Open Questions（待 baron 拍板）

| # | 問題 | 推薦答案 | 理由 |
|---|---|---|---|
| Q1 | 「切換文章」訊號掛哪？ | `GET /api/papers/{paper_id}/content`（L735、開文章天然訊號）；記 owner 當前篇、切換時 evict 前篇工作集 | content 端點＝使用者真正切到該篇;chat 端點是問答非切換 |
| Q2 | 60min TTL 釋放機制？ | **惰性檢查**（每次 `_get_vector_store`/load 時順手掃逾時項）優先,不起背景 task | 無背景執行緒、無 lifespan 常駐 task（對齊 API-PERF 廢 preload 精神）;精度足夠 |
| Q3 | 釋放是否含 `rag_trees`？ | **是**——選 ③ 後樹也可自載重建,故 TTL/切換一併釋放 rag_trees（根治 §3.3 慢累積）；但需確認 set_rag_tree 重載路徑完整 | 否則 rag_trees 永不釋放、長跑漏；③ 讓它安全可釋 |
| Q4 | cap=100 + 切換釋放 + TTL 三者優先序？ | cap 100＝安全天花板（幾乎不觸發）;主力＝切換釋放 + TTL;三者皆 evict vector_stores+_paper_cache、靠 ③ 自載兜底 | 記憶體無虞、以「不再用就放」為主、cap 僅防爆 |
| Q5 | loader 注入單篇 attach 重連（`/chat/attach` L846）是否也走 ③？ | 是（自動受惠、無需額外碼——皆過 _get_vector_store） | ③ 鎖點咽喉、一處全收 |
| Q6 | 拆幾個 commit？ | C1 retriever set_loader+自載守衛+單元 / C2 web_server 接線+cap100 / C3 釋放策略（切換+TTL）+單元 / C4 整合測試 / C5 Checkout（暫議、tasks 階段定） | 風險分層、每步獨立可驗 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 修跨文件 hashtag 檢索漏召（lazy-load 接縫）+ 記憶體釋放策略改 |
| 權威源 | 本檔 §2 目標規格 / §4 接縫契約 |
| 引用方 | tasks（待產）/ executions（待產）|
| 不可動唯一源 | §6 |
| 改版觸發 | §2/§4/§9 變動 |

### §99.2 Revision 歷程
- v1 (2026-06-09)：初稿——根因（API-PERF C3 × RAG-1 P2-2 接縫）+ 證據鏈 + 記憶體實測 13MB + ③ 拍板 + cap100/切換+TTL 釋放 + §4 接縫契約 + §9 六 OQ；待 baron 過目 OQ → v2
