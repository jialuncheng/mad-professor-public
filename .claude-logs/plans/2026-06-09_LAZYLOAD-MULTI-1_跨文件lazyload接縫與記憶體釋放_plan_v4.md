# LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放策略 · plan v4

> 工作流類別：**BE-Refactor**（改 rag_retriever / ai_core / web_server / settings 業務邏輯）
> 必讀 SOP：logging_SOP + database_SOP（§5 SOP 核查）
> 跨模組 + handoff（loader callback + rag_tree 重載 + 釋放跳過活躍串流 + cache 鎖）→ WORKFLOW_SOP §7（見 §4）

---

## §0 改版規則
- 改版觸發：§2 / §4 / §9 任一變動 → 改章節 + §99.2 加 Revision
- 多輪 review（§1.9）：v1 → v2 Antigravity(rag_tree handoff+C2/C3) → v3 Antigravity(is_ready+DB安全+shadow) → **v4 合併（baron 釋放策略決策 P1/P2 + Claude 深 review P0 併發鎖 + 校正 v3 DB安全≠cache安全）**

---

## §1 TL;DR（概要）

跨文件 hashtag 檢索（`#cv 比較…`）只召回「當前開著那一篇」、漏其餘 tagged 篇 → 答案誤判「只有一位候選人」。**根因＝ API-PERF C3 廢啟動 preload、chat 端點只 lazy-load「當前 paper_id」,但 `retrieve_multi` 需「全部 tagged 篇」已註冊**；未註冊者 `_get_vector_store` 回 None → `rag_retriever.py:260` 靜默 `continue` 跳過。

**修法（baron 拍板）**：
1. **③ retriever 自帶 lazy-load hook**——`_get_vector_store` 完全 miss 時呼注入 loader 自載。一鎖點修單篇/多篇/attach 全路。
2. **`is_ready()` loader-aware（U7）**：全清後 paper_vector_paths 空、`is_ready()` 不可回 False 繞過 ③。
3. **併發安全（U8·P0）**：③ 把 cache **寫入**從序列化 endpoint 搬進並行 `to_thread` worker → in-memory cache mutation **持鎖**（`threading.RLock`）。注意：與「DB 連線 thread 安全」（§3.1⑥、已由 db.py 解）**是兩層、不可混為一談**。
4. **釋放策略（v4 簡化）**：cap 5→**100**（安全天花板）+ **切換文章釋放** + **上傳文件釋放（開關 `RELEASE_ON_UPLOAD`）**（騰 RAM 給同 VM MinerU Docker）；**砍 60min TTL**（切換即放+ ③ 重載已足、零背景執行緒）。釋放一律**跳過 active_streams 活躍 paper**（U9·P2）。

**非本任務**：RAG-MULTI-1 保底演算法（已落地）；embedding/regen（28 篇全 `-001`）。

---

## §2 目標規格（baron 已拍板項）

| # | 規格 | 狀態 |
|---|---|---|
| U1 | `RagRetriever` 加 `set_loader(fn)`；`_get_vector_store` 完全 miss 且 loader 設時自載重試；**loader 未設＝現況回 None → 向後相容** | 拍板（③）|
| U2 | web_server 啟動接線 `set_loader(λ o,p: load_paper_resources(OUTPUT_DIR,o,p,ai_core))`；retriever 不 import paper_manager（存不透明 callable、零 import 循環） | 拍板 |
| U3 | `#cv…` 經 ③ 後 retrieve_multi 涵蓋全 tagged 篇；**重載後 `paper_title` 非空（引用不退化）** | 拍板（核心驗收）|
| U4 | `RAG_MAX_CACHE` 5→**100**（env 可覆寫；釋放策略主導、cap 僅安全天花板） | 拍板 |
| **U5（v4 改）** | 釋放時機：**(a) 切換文章**（`GET /content`）+ **(b) 上傳文件**（`POST /upload`、開關 `RELEASE_ON_UPLOAD`）；**砍 60min TTL**。**釋放對象＝所有 cached 篇，唯一豁免＝ active_streams 仍在生成（`done==False`）者**（連剛切到的當前篇亦清、靠 ③ 重載；不保留「當前篇」例外）。釋放＝**全清**（複用 `ai_core.remove_paper` 清 _paper_cache + retriever 三 dict）→ 強制下次走 loader 全載路 | 拍板 |
| U6 | 釋放後正確性靠 ③ 自載（重載 vector **與** rag_tree、不回空、title 不退化） | 拍板 |
| **U7（Antigravity v3）** | **`is_ready()` 改判 loader 已設即 ready**：全清後 paper_vector_paths 空 → 原 `is_ready()` 回 False → retrieve_multi 直接回空繞過 ③；修：loader 已設亦視 ready | 拍板 |
| **U8（Claude·P0）** | in-memory cache mutation **全程持鎖**（`RagRetriever` 加 `threading.RLock` 包 vector_stores/paper_vector_paths/rag_trees 全 mutation：add_paper/_evict/自載/remove_paper；ai_core._paper_cache 同鎖或自有鎖）。**注意：此為 in-memory dict race、與 §3.1⑥ DB 連線安全是兩層** | 拍板（正確性）|
| **U9（baron·P2）** | 釋放（切換/上傳）**必跳過 `active_streams` 活躍 paper**（`session.done==False`）→ 不抽進行中 SSE 串流向量庫 | 拍板（硬規格）|

---

## §3 現況與證據

### §3.1 grep 鋼鐵證據

**① 根因——chat 端點只載當前一篇**（`web_server.py:797-802`）：`if (uid,paper_id) not in _paper_cache: load_paper_resources(...paper_id...)`。

**② 跨文件檢索靜默跳過未載篇**（`rag_retriever.py:258-261`）：`vs=_get_vector_store; if vs is None: continue`。`_get_vector_store`(L88-105) 兩層（vector_stores 命中 / paper_vector_paths 命中只重載 FAISS）；**缺第三層 miss 回 None ＝ ③ 補**。

**③ loader 已含 rag_tree 補載**：`load_paper_resources`(457)→`load_paper_cache`(466)→`set_rag_tree`(**ai_core.py:103**)。⚠️ 但 `_get_vector_store` 第二層（path 命中→只重載 FAISS）不補 tree → 釋放 tree 留 path → `retrieve_multi` L269 `load_rag_tree` 回 {} → `title=""`。**故 U5 全清強制走 loader 全載（§4）。**

**④ `is_ready()` 全清繞過 ③**（Antigravity v3）：
```python
def is_ready(self): return bool(self.paper_vector_paths)   # rag_retriever.py:111-113，全清後 False
# retrieve_multi 開頭 if not self.is_ready(): return ""    # → 繞過 ③ 直接回空
```
→ 全部全清後 retrieve_multi 直接回空。**修：U7 is_ready 改判 loader 已設即 ready。**

**⑤ in-memory cache 併發 race（Claude·P0、必修）**：
- `grep -n 'Lock|threading|Semaphore' rag_retriever.py ai_core.py` → **全空（無鎖）**。
- `retrieve_multi` 跑在 `to_thread` worker（`web_server.py:124`）；並發守衛只擋同 owner 同 paper（L807-809）→ 不同 paper/owner 多 worker 並行。
- ③ 後 retrieve_multi 內 `_get_vector_store` 會**寫**（loader→`add_paper`：`vector_stores[key]=` + `move_to_end` + `_evict_vector_lru` 的 `popitem`）。兩 worker 並發時：A 剛 set key、B 的 `_evict` popitem 淘汰同 key → A `move_to_end(key)` 拋 `KeyError`；或 `while len>cap: popitem` 與另一 thread `[key]=` 交錯 → 狀態不一致。**GIL 只保單一 op 原子、不保此複合序列**。③ 把寫從序列化 endpoint 搬進並行 worker 才放大此窗。→ **U8 RLock 包全 mutation。**

**⑥ DB 連線 thread 安全（Antigravity v3、✅ 已解、與 ⑤ 不同層）**：loader 在 to_thread 呼 `db.SessionLocal()`；`db.py:29 check_same_thread=False` + `QueuePool(5,+10)` + WAL + `busy_timeout=30000` + 唯讀 `s.query(Paper.domain).one_or_none()` → DB 層安全。**但此僅 DB 連線、不涵蓋 ⑤ 的 in-memory OrderedDict race**（v4 校正 v3 把兩者混為「已解除」）。

**⑦ active_streams 跳過依據（baron·P2）**：`active_streams: Dict[(owner,paper_db_id), StreamSession]`(L85)，`StreamSession.paper_uuid`(L826)、`.done`(L134/146) → 釋放由活躍 session 取 `paper_uuid` 集合跳過、免 db_id 映射。

**⑧ 線上 log**：`[P2-2 hashtag] matched_papers=6` / `[retrieve_multi] chosen=[14× 'YuLun_Wu_CV']`（只搜當前篇）。

**⑨ 資料層健康**：28 篇全 `-001`；獨立載入 6 篇每篇 top 0.6-0.75、全 >0.22（候選都在、server 沒搜）。

### §3.2 記憶體實測（du）
全 28 篇 ≈ **13 MB**（最大書 3.64MB / 履歷 0.02-0.10MB；faiss 佔大頭）→ 支持 cap=100、釋放主導。

### §3.3 現有釋放機制（待改）
- vector_stores/_paper_cache：LRU cap 5+gc（將改 cap100 + 切換/上傳全清主導）。
- rag_trees/paper_vector_paths：永不淘汰 → U5 全清根治。
- `ai_core.remove_paper`(116-123)：清 _paper_cache + 轉呼 retriever.remove_paper（清三 dict）＝全清四 dict；⚠️ docstring 寫「清當前對話上下文」但 **body 未清對話**（stale 註解、行為安全、§9 P4 順手修）→ U5 可安全複用。

### §3.4 上傳場景（baron）
`POST /api/papers/upload`(web_server.py:448) → 觸發同 VM MinerU Docker（重 RAM）；U5(b) 在此釋放 vector cache 騰 RAM、開關 `RELEASE_ON_UPLOAD`（§9 Q7）。

---

## §4 跨 Phase 接縫契約（WORKFLOW_SOP §7）

| handoff | producer | consumer | key 精確身份 + 同基準保證 |
|---|---|---|---|
| lazy-load callback | web_server 啟動 `set_loader(λ o,p: load_paper_resources(...))` | `_get_vector_store` 完全 miss 呼 `self._loader(o,p)` | key＝`(owner_id, paper_uuid)`；consumer 傳 loader 的 `paper_id` ≡ `retrieve_multi.paper_ids`（源 `list_paper_uuids_by_tag` 之 paper_uuid）≡ loader 寫回 `paper_vector_paths` key——三者同 **paper_uuid 原值、不轉換** |
| rag_tree 重載 | loader（已含 set_rag_tree）；釋放全清 | `retrieve_multi` L269 `load_rag_tree` 取 title | 同 paper_uuid；**tree 與 vector 釋放/重載必同步**——全清（含 path）強制 loader 全載補 tree；禁「evict tree 留 path」致 FAISS-only 路 title="" |
| 釋放跳過活躍串流（P2） | 切換/上傳釋放端 | active_streams 活躍 session（`.done==False`）`paper_uuid` | 釋放前收集活躍 `paper_uuid` 集、逐篇釋放 skip 之；凍結：釋放端與串流端同以 **paper_uuid** 基準（非 db_id） |
| cache 鎖不變式（P0） | 所有 mutation（add/evict/自載/remove）| 所有 read（_get_vector_store/retrieve_*）| 同一 `RLock`；凍結：任何 vector_stores/paper_vector_paths/rag_trees 之寫**必持鎖**；**此鎖管 in-memory dict、與 DB 連線安全（§3.1⑥）正交、不可互相替代** |

> 反例錨點：① loader 用 sanitize 檔名、retrieve 用 raw uuid → 自載仍 miss。② 釋放 tree 不釋 path → FAISS-only 路 title 退化。③ 釋放端用 db_id、串流端用 uuid → 跳過錯位。④ 誤以 DB thread-safe ＝ cache thread-safe → 漏補 RLock。**凍結：全程 paper_uuid 原值、釋放全清四 dict、跳過活躍 uuid、mutation 持鎖、is_ready loader-aware。**

---

## §5 變動風險與相容性評估

| 風險 | 評估 | 緩解 |
|---|---|---|
| retriever 介面變動 | set_loader + 自載守衛；loader 未設＝現況回 None | 向後相容、既有測試不破 |
| **P0 in-memory cache race（Claude）** | ③ 把寫推進並行 worker、OrderedDict 無鎖、複合 mutation 有 KeyError 窗 | **U8 RLock 包全 mutation**；§8 並發測試 |
| **is_ready 全清回 False 繞過 ③（Antigravity）** | paper_vector_paths 空 → retrieve_multi 回空 | **U7 is_ready loader-aware**；§8 `test_is_ready_after_full_evict` |
| **P2 切換抽掉進行中串流（baron）** | 釋放砍活躍串流向量庫 | **U9 跳過 active_streams**；§8 測試 |
| rag_tree 釋放後 FAISS-only 路 title="" | 第二層不補 tree | U5 全清強制 loader 全載；§8.1 title 非空測試 |
| **DB 連線 thread 安全（Antigravity、✅已解）** | to_thread 呼 db.SessionLocal、唯讀 | `db.py` check_same_thread=False+WAL+pool+busy_timeout；**僅此層、不替代 U8** |
| import 循環 / 物件循環參考 | retriever 存 callable；loader closure ai_core→retriever→loader→ai_core | 啟動注入；GC 處理物件環（誠實列）|
| cap5→100 / 釋放頻繁 reload I/O | 13MB 無虞、tagged 實務有界（§9 P3）| 切換+上傳釋放、③ 兜底 |
| docstring stale（ai_core.remove_paper）| 寫「清對話」實未清 | §9 P4 順手修註解 |

---

## §6 不可動清單

- [ ] `retrieve_multi_with_context` **保底演算法**（RAG-MULTI-1 C2）——只補「篇有沒有被載」、不碰分配。
- [ ] `retrieve_with_context` 單篇邏輯（除共用 `_get_vector_store` 鎖點自載/RLock 外）。
- [ ] context 格式 `## 摘自文件《…》` / 向量資料 / FAISS / index_meta（不重嵌）。
- [ ] embedding 模型 / RAG_SCORE_THRESHOLD / 上游 hashtag 解析。
- [ ] **shadow 過濾**——指不改現有 **UI 可見性**邏輯（list_papers/status 等）；**非指在 retrieve_multi 加 shadow 過濾**（shadow 應參與 retrieve_multi 驗 B 軌 RAG、見 §5/§3）。
- [ ] **禁無鎖 mutate in-memory cache**（U8）。

---

## §7 規格依據（grep 行號）

- `web_server.py:797-802`（lazy-load 缺口）/ `:735`（content 切換）/ `:448`（upload 釋放）/ `:85,124,807-829`（active_streams/to_thread/409）
- `rag_retriever.py:88-105`（_get_vector_store 兩層）/ `:111-113`（is_ready）/ `:258-261`（靜默跳過）/ `:269`（title）/ `:37-40`（LRU）/ `:49-67`（add_paper 含 _evict）/ `:115-121`（remove_paper）；`grep Lock` 全空
- `ai_core.py:94-103`（load_paper_cache→set_rag_tree）/ `:104-108`（_paper_cache LRU）/ `:116-123`（remove_paper·stale docstring）
- `db.py:29`（check_same_thread=False）/ `:39-41`（QueuePool）/ `:59-61`（WAL+busy_timeout）
- `paper_manager.py:336`（get_paper_db_id）/ `:457-476`（load_paper_resources）；`settings.py:65`（RAG_MAX_CACHE）

---

## §8 驗證計畫

### §8.1 自動化單元測試（新建 `tests/test_lazyload_multi.py`）
1. `test_get_vector_store_self_loads_on_miss`：完全 miss + loader 設 → 自載成功。
2. `test_get_vector_store_loader_unset_returns_none`：loader 未設 → 回 None（向後相容）。
3. `test_retrieve_multi_loads_all_tagged`（**§7.2 整合測試**）：mock 6 篇、只預註冊 1 篇、其餘靠 loader 自載 → 涵蓋全 6 篇（吳焴倫 bug）。
4. `test_evict_then_reload_preserves_title`：載入→全清→再檢索→自動重載 + title 非空。
5. **`test_is_ready_after_full_evict`（U7）**：全清（paper_vector_paths 空）+ loader 設 → `is_ready()` 仍 True → retrieve_multi 不繞過、走 ③。
6. **`test_concurrent_lazyload_no_corruption`（U8·P0）**：多 thread 並發 `_get_vector_store`/自載 + 觸發 evict → 無 KeyError/corruption、cache 完整。
7. **`test_release_skips_active_stream`（U9·P2）**：active_streams 含某 paper（done=False）→ 切換/上傳釋放 → 不清；done=True 才清。
8. `test_release_on_switch_clears_inactive` + `test_release_on_upload_toggle`（開關 on/off）。
9. `test_cap_100_default` + env override。
- 全套件不退化。

### §8.2 手動 E2E（baron · PaperRead-Lab）
1. 重啟 → 直接 `#cv 比較這幾位候選人的學歷背景`（不先逐篇開）→ 涵蓋全 6 位 + 引用顯《文件名》非「(pid)」。
2. log 驗 chosen 含 ≥5 種 pid。
3. **並發**：兩 owner（或兩 tab 不同 paper）同時 `#cv` → 無 500/錯亂（U8）。
4. **串流不中斷**：一邊跑 chat 串流、一邊切到別篇 → 串流不斷（U9）；切後前篇釋放（log）。
5. **上傳**：上傳文件 → 釋放 log + MinerU 期間 RAM 降；之後問答仍正確（③ 重載）。
6. **shadow**：B 軌完成後 `#cv` → chosen 含 `_shadow` pid（驗 B 軌 RAG）。

---

## §9 Open Questions（待 baron 拍板）

| # | 問題 | 推薦答案 | 理由 |
|---|---|---|---|
| Q1 | 切換訊號掛哪？ | `GET /api/papers/{paper_id}/content`（L735）；切換時**全清所有 cached 篇、唯一豁免 active_streams 仍生成者**（當前篇亦清、③ 重載；不留「當前篇」例外——baron 定案語意） | content＝真正切到該篇 |
| ~~Q2~~ | ~~TTL 機制~~ | **已定案：砍 60min TTL**（切換+上傳釋放 + ③ 重載已足、零背景 task） | baron v4 拍板 |
| Q3 | 釋放含 rag_trees？ | 是、**全清**（複用 `ai_core.remove_paper` 四 dict）強制 loader 全載補 tree | 根治慢累積 + 防 title 退化 |
| Q4 | cap+切換+上傳優先序 | cap100＝安全天花板（幾乎不觸發）；主力＝切換+上傳全清；皆 ③ 兜底 | 記憶體無虞、不再用就放 |
| Q5 | attach 重連走 ③？ | 是（過同一 `_get_vector_store` 咽喉） | 一鎖點全收 |
| Q6 | 拆 commit（**baron：以降低 AI 亂改風險為前提自行評估**）| **定案 5 commit、行為不變硬化與改行為分離、盡量單檔**：<br>**C1**（`rag_retriever.py` + 單元）loader 接縫：`set_loader` + `_get_vector_store` 自載 + `is_ready` loader-aware + 單元（含整合 `test_retrieve_multi_loads_all_tagged`，retriever 層 mock loader、不需 web_server）<br>**C2**（`rag_retriever.py` + `ai_core.py` + 單元）**RLock 純硬化**（兩 class 各自鎖 own dict、無跨 class 鎖序→無死鎖）+ 並發測試；**行為不變**（驗收＝既有測試全綠 + 並發測試）<br>**C3**（`web_server.py` 啟動段 + `settings.py`）`set_loader` 接線 + `RAG_MAX_CACHE=100`（純加法 2-3 行）→ **核心跨文件修復此刻 LIVE、E2E 檢查點**<br>**C4**（`web_server.py` 端點 + `ai_core.py` docstring + `settings.py` + 單元）釋放策略：`/content` 切換 + `/upload`（`RELEASE_ON_UPLOAD`）+ 跳過 active_streams + 修 stale docstring + 單元<br>**C5** Checkout | **風險分層**：① C1/C2 分離→RLock 出事可獨立 bisect/revert ② C2 行為不變→既有測試即回歸網 ③ C3 純加法 2-3 行→上線風險最低點 ④ C4 隔離最多新行為。**web_server 只 C3（啟動段）+ C4（端點）動、不同 function 區段、hunk 天然不重疊**（tasks §8 明列） |
| **Q7** | `RELEASE_ON_UPLOAD` 預設 on/off？ | ✅ **定案 on**（baron 拍板：上傳即釋放騰 RAM 給 MinerU；env/設定可關）；釋放仍跳過 active_streams | 同 VM MinerU 重 RAM、釋放安全（③ 重載）；保留關閉彈性 |
| **P3 結案（非 OQ）** | 廣 tag 無界 lazy-load | **不設硬上限**——實務有界（一篇所有引用 / 同領域 ≤10 本書都還好）；retrieve_multi 既有 cap=15 截最終 context | baron 拍板場景無虞 |
| **P4 結案（非 OQ）** | ai_core.remove_paper stale docstring | C1 順手修註解（移除「當前對話上下文」誤述）| 行為本就安全、僅文字 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | 修跨文件 hashtag 漏召（lazy-load 接縫）+ 併發安全 + 記憶體釋放策略 |
| 權威源 | §2 / §4 |
| 引用方 | tasks / executions（待產）|
| 不可動唯一源 | §6 |
| 改版觸發 | §2/§4/§9 變動 |

### §99.2 Revision 歷程
- **v4 (2026-06-10)**：合併雙線 review——(1) **baron 釋放策略決策**：砍 60min TTL（U5 重寫）、改切換+上傳釋放、新增 `RELEASE_ON_UPLOAD` 開關（U5b/§3.4/Q7）、P2 跳過 active_streams 升硬規格（U9/§4 handoff/§8）；(2) **Claude 深 review P0**：in-memory cache OrderedDict 併發 race（U8 RLock/§3.1⑤/§4 鎖不變式/§8 並發測試）；(3) **校正 v3**：明分「DB 連線 thread 安全（✅已解、§3.1⑥）」vs「in-memory cache race（仍需 RLock、§3.1⑤）」兩層，反例錨點④；(4) **保留 Antigravity v3**：U7 is_ready loader-aware、shadow 定調（§6 括號+§8.2）；(5) P3/P4 結案
- v3 (2026-06-10)：Antigravity——U7 is_ready 改判 + §3.1④ + DB thread 安全 §3.1⑤（v4 校正為兩層）+ shadow 定調（§5/§6/§8.2）
- v2 (2026-06-09)：Antigravity——§4 rag_tree 重載 handoff（loader 含 set_rag_tree、全清強制 loader 全載防 title=""）+ C2/C3 hunk 邊界
- v1 (2026-06-09)：初稿——根因 + 證據鏈 + 記憶體 13MB + ③ + cap100/切換+TTL + §4 + 六 OQ
