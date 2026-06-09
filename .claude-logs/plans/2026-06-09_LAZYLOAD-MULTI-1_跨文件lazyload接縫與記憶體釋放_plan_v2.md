# LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放策略 · plan v2

> 工作流類別：**BE-Refactor**（改 rag_retriever / ai_core / web_server / settings 業務邏輯）
> 必讀 SOP：logging_SOP + database_SOP（§5 SOP 核查）
> 跨模組 + handoff（loader callback + rag_tree 重載）→ 適用 WORKFLOW_SOP §7 接縫契約（見 §4）

---

## §0 改版規則
- 改版觸發：§2 目標規格 / §4 接縫契約 / §9 OQ 任一變動 → 直接改章節 + §99.2 加 Revision
- 多輪 review 累積（§1.9）：v1 初稿 → Antigravity review（rag_tree 重載 handoff + C2/C3 邊界）→ **v2**

---

## §1 TL;DR（概要）

跨文件 hashtag 檢索（`#cv 比較…`）只召回「當前開著那一篇」、漏掉其餘 tagged 篇 → 答案誤判「只有一位候選人」。**根因＝ API-PERF C3 廢除啟動 preload、改 chat 端點只 lazy-load「當前 paper_id」一篇,但 `retrieve_multi_with_context` 需要「全部 tagged 篇」都已註冊**；未註冊者 `_get_vector_store` 回 None → `rag_retriever.py:260` 靜默 `continue` 跳過。

**修法（baron 拍板）**：
1. **③ retriever 自帶 lazy-load hook** —— `_get_vector_store` 完全 miss 時呼叫注入的 loader 自我載入。一處鎖點修好單篇/多篇/未來 attach 全部路。
2. **記憶體釋放策略改**：`RAG_MAX_CACHE` 5 → **100**（記憶體實測非瓶頸）+ **切換文章即釋放** + **60 分鐘閒置 TTL 釋放**。因選 ③（取庫即自載）、eager 釋放安全（誰被釋放下次自動重載）。

**非本任務**：RAG-MULTI-1 保底演算法（已落地、正確）；embedding 模型/regen（28 篇全 `-001`、無混用）。

---

## §2 目標規格（baron 已拍板項）

| # | 規格 | 狀態 |
|---|---|---|
| U1 | `RagRetriever` 新增 loader 註冊鎖點（`set_loader(fn)`）；`_get_vector_store` **完全 miss**（key 不在 vector_stores 亦不在 paper_vector_paths）且 loader 已設時自載後重試；**loader 未設時行為與現況完全一致（回 None）→ 向後相容** | 拍板（③）|
| U2 | web_server 啟動接線 `retriever.set_loader(lambda o,p: paper_manager.load_paper_resources(OUTPUT_DIR,o,p,ai_core))`；retriever **不** import paper_manager/web_server（僅存不透明 callable、零循環） | 拍板 |
| U3 | `#cv 比較…` 經 ③ 後 `retrieve_multi` 涵蓋全部 tagged 篇（每篇被搜→ RAG-MULTI-1 保底分配生效）；候選不再只剩當前篇；**重載後 `paper_title` 非空（引用不退化為 "摘自文件 (pid)"）** | 拍板（核心驗收）|
| U4 | `RAG_MAX_CACHE` 預設 5 → **100**（env 仍可覆寫） | 拍板 |
| U5 | 記憶體釋放：**(a) 切換文章即釋放** 前一工作集 + **(b) 60 分鐘閒置 TTL 釋放**；採**全清**（沿用 `remove_paper` 清 vector_stores + rag_trees + paper_vector_paths + ai_core._paper_cache 四者）→ 強制下次走 loader 全載路 | 拍板（機制細節見 §9 OQ）|
| U6 | 釋放後正確性靠 ③ 自載保證（被釋放篇下次檢索自動重載 vector **與** rag_tree、不回空、title 不退化） | 拍板 |

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
`_get_vector_store`（L88-105）**兩層**：① key 在 `vector_stores`（FAISS 已載）直接回；② key 在 `paper_vector_paths`（FAISS 被 LRU 淘汰、路徑留）→ **只重載 FAISS**。**缺第三層**：key 全 miss（未曾載）→ 回 None ＝本任務 ③ 要補。

**③ loader 已含 rag_tree 補載**（消解 Antigravity 疑慮、grep 實證）：
```
load_paper_resources (paper_manager.py:457)
  → ai_core.load_paper_cache (L466)
      → retriever.set_rag_tree(owner, pid, paper_data)   # ai_core.py:103
```
→ ③ 走 loader 全載時、vector + rag_tree **一併重設**。⚠️ **但 `_get_vector_store` 第二層（paper_vector_paths 命中→ 只重載 FAISS）不經 loader、不補 tree** → 若 rag_trees 被 TTL 釋放而 paper_vector_paths 仍留 → tree 空 → `retrieve_multi` L269 `load_rag_tree` 回 `{}` → `paper_title=""` → 引用退化。**故 U5 採全清、強制走 loader 全載路（見 §4）。**

**④ 線上 log（PaperRead-Lab）**：
- `[P2-2 hashtag] tags=['cv'] matched_papers=6`（上游比對 6 篇 OK）
- `[retrieve_multi] papers=6 candidates=14 cap=15 floor=2 chosen=[14× 'YuLun_Wu_CV']`（只搜到當前篇、其餘 5 篇 0 候選）

**⑤ 資料層健康（反證非模型/非演算法）**：
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
- `retriever.rag_trees` / `paper_vector_paths`：**永不淘汰**（`rag_retriever.py:24-26` 刻意）→ rag_trees 長跑慢累積；本任務 U5 全清一併根治。
- `remove_paper`（`rag_retriever.py:115-120`）：已同清 vector_stores + paper_vector_paths + rag_trees → **U5 釋放可直接複用此全清語意**。

---

## §4 跨 Phase 接縫契約（WORKFLOW_SOP §7）

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| lazy-load callback | web_server 啟動 `set_loader(λ o,p: load_paper_resources(OUTPUT_DIR,o,p,ai_core))` | `retriever._get_vector_store` 完全 miss 時呼 `self._loader(owner_id, paper_id)` | key＝`(owner_id, paper_uuid)`；consumer 傳給 loader 的 `paper_id` ≡ `retrieve_multi` 的 `paper_ids` 元素（來自 `list_paper_uuids_by_tag` 之 `paper_uuid`）≡ loader 寫回 `paper_vector_paths` 的 key——三者同為 **paper_uuid 原值、單一基準**，不轉換 |
| **rag_tree 重載（v2 補）** | loader（`load_paper_resources`→`load_paper_cache`→`set_rag_tree`，已含）；釋放採**全清** | `retrieve_multi` L269 `load_rag_tree(owner,pid)` 取 `paper_title` | 同 paper_uuid；**凍結：rag_tree 與 vector 之釋放/重載必同步**——TTL/切換**全清**（含 paper_vector_paths）以強制下次走 loader 全載、一併補 tree；**嚴禁**「evict rag_trees 卻留 paper_vector_paths」致 `_get_vector_store` 第二層只補 FAISS → title="" |

> 反例錨點（防 RAG-ASYNC #1 類）：① loader 載入用 sanitize 後檔名、retrieve_multi 查找用 raw uuid → key 不同基準 → 自載仍 miss。② 釋放 tree 不釋放 path → FAISS-only 重載路 → tree 空、title 退化。**契約凍結：全程 paper_uuid 原值、釋放全清四 dict（複用 remove_paper）。**

---

## §5 變動風險與相容性評估

| 風險 | 評估 | 緩解 |
|---|---|---|
| retriever 介面變動 | 新增 `set_loader` + `_get_vector_store` 守衛；**loader 未設＝現況行為（回 None）** | 向後相容預設、既有測試不破 |
| import 循環 | retriever 存不透明 callable、不 import paper_manager | 啟動接線注入 |
| cap 5→100 | 記憶體 13MB 語料無虞 | env 可回調；TTL 仍兜閒置 |
| 切換即釋放誤刪跨文件比較所需篇 | ③ 自載兜底（再用即重載） | U6；§8 整合測試驗 evict→重載 |
| **rag_tree 釋放後走 FAISS-only 重載路 → title=""（v2 補）** | `_get_vector_store` 第二層不補 tree | **U5 全清（含 path）強制走 loader 全載**；§8.1 加 title 非空測試 |
| TTL sweep 機制（背景 task vs 惰性檢查）| 影響複雜度/精度 | §9 OQ-Q2 拍板（推薦惰性）|
| 釋放後 reload I/O 抖動 | 跨文件迴圈逐篇 reload；全清使 loader 多一次 DB domain 查詢 | tagged 數天然有界（<20）、I/O 小、語料 13MB |

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

- `web_server.py:797-802`（C3 lazy-load 缺口）/ `:735`（GET /content 切換訊號掛點）
- `rag_retriever.py:88-105`（_get_vector_store 兩層、無自載）/ `:258-261`（靜默跳過）/ `:269`（load_rag_tree 取 title）/ `:37-40`（LRU）/ `:115-120`（remove_paper 全清）
- `ai_core.py:39-43`（add_paper_vector_store）/ `:94-103`（load_paper_cache→set_rag_tree）/ `:104-108`（_paper_cache LRU）
- `paper_manager.py:457-476`（load_paper_resources 含 vector + tree + domain）
- `settings.py:65`（RAG_MAX_CACHE）
- 線上 log：`[P2-2 hashtag] matched_papers=6` / `[retrieve_multi] chosen=[14× YuLun_Wu_CV]`

---

## §8 驗證計畫

### §8.1 自動化單元測試（新建 `tests/test_lazyload_multi.py`）
1. `test_get_vector_store_self_loads_on_miss`：key 完全 miss + loader 已設 → 呼 loader 後成功取庫。
2. `test_get_vector_store_loader_unset_returns_none`：loader 未設 → 回 None（向後相容、現況行為）。
3. `test_retrieve_multi_loads_all_tagged`（**§7.2 整合測試、key-changing**）：mock 6 篇,**只預註冊 1 篇**、其餘 5 篇靠 loader 自載 → 斷言 retrieve_multi 涵蓋全 6 篇（重現吳焴倫 bug 修復）。
4. `test_evict_then_reload_preserves_title`（**v2 補**）：載入→**全清**（TTL/切換模擬、含 path）→ 再檢索 → 自動重載 + **`paper_title` 非空**（U3/U6、防 FAISS-only 路退化）。
5. `test_ttl_eviction_releases_idle`：last-access 超 TTL → 惰性釋放;未逾時保留。
6. `test_switch_releases_previous`：切換文章訊號（content 端點）→ 前一工作集全清釋放。
7. `test_cap_100_default` + env override。
- 全套件不退化。

### §8.2 手動 E2E（baron · PaperRead-Lab）
1. 重啟 server（清空快取）→ 直接 `#cv 比較這幾位候選人的學歷背景`（不先逐篇開）→ 答案**涵蓋全部 6 位**（吳焴倫/黃忠偉/DeHunt/Priyal/林晉羽）。
2. log 驗 `[retrieve_multi] chosen=[…]` 含 ≥5 種不同 pid（非單一霸榜）；引用顯示《文件名》非「(pid)」（title 未退化）。
3. 切換文章 → log 見前篇全清釋放;閒置 60min → log 見 TTL 釋放;之後再問仍正確（自載 + title 正常）。

---

## §9 Open Questions（待 baron 拍板）

| # | 問題 | 推薦答案 | 理由 |
|---|---|---|---|
| Q1 | 「切換文章」訊號掛哪？ | `GET /api/papers/{paper_id}/content`（L735、開文章天然訊號）；記 owner 當前篇、切換時全清前篇工作集 | content 端點＝使用者真正切到該篇;chat 端點是問答非切換 |
| Q2 | 60min TTL 釋放機制？ | **惰性檢查**（每次 `_get_vector_store`/load 時順手掃逾時項）優先,不起背景 task | 無背景執行緒、無 lifespan 常駐 task（對齊 API-PERF 廢 preload 精神）;精度足夠 |
| Q3 | 釋放是否含 `rag_trees`？機制？ | **是,且採全清**——TTL/切換複用 `remove_paper` 全清四 dict（vector_stores+rag_trees+paper_vector_paths+_paper_cache）→ 強制下次走 loader 全載、tree 一併重設（**已 grep 證 loader 含 set_rag_tree**）。**禁**只清 tree 留 path（致 FAISS-only 路 title=""） | 根治 rag_trees 永不淘汰慢累積 + 避免 title 退化;③ 使全清安全 |
| Q4 | cap=100 + 切換 + TTL 三者優先序？ | cap 100＝安全天花板（幾乎不觸發）;主力＝切換釋放 + TTL;三者皆全清、靠 ③ 自載兜底 | 記憶體無虞、以「不再用就放」為主、cap 僅防爆 |
| Q5 | loader 注入單篇 attach 重連（`/chat/attach` L846）是否也走 ③？ | 是（自動受惠、無需額外碼——皆過 _get_vector_store） | ③ 鎖點咽喉、一處全收 |
| Q6 | 拆幾個 commit + C2/C3 web_server 邊界（Antigravity 補）？ | C1 retriever set_loader+自載守衛+全清 helper+單元 / C2 web_server 接線（set_loader 啟動段）+cap100 / C3 釋放策略（content 端點切換訊號 + TTL 惰性掃）+單元 / C4 整合測試 / C5 Checkout。**C2/C3 同改 web_server**：C2 只動「啟動接線段」、C3 只動「content 端點 + TTL 掃描點」,tasks §8 須明列各自 hunk 邊界、不重疊 | 風險分層、每步獨立可驗;明界防 diff 衝突 |

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
- v2 (2026-06-09)：Antigravity review 補強——§4 新增 **rag_tree 重載 handoff**（grep 證 loader 已含 set_rag_tree、釋放採全清強制走 loader 全載路、防 FAISS-only 重載致 title=""）+ §3.1③ tree 補載證據 + §3.3 remove_paper 全清複用 + §5 新增 title 退化風險列 + §8.1 加 evict→reload title 非空測試 + U3/U5/U6 補 title/全清語意 + Q3 細化全清機制 + Q6 補 C2/C3 web_server hunk 邊界
- v1 (2026-06-09)：初稿——根因（API-PERF C3 × RAG-1 P2-2 接縫）+ 證據鏈 + 記憶體實測 13MB + ③ 拍板 + cap100/切換+TTL 釋放 + §4 接縫契約 + §9 六 OQ
