# LAZYLOAD-MULTI-1 跨文件 lazy-load 接縫修復與記憶體釋放 · tasks

> 依據 plan：`.claude-logs/baton/2026-06-09_LAZYLOAD-MULTI-1_跨文件lazyload接縫與記憶體釋放_plan_v5.md`
> 工作流類別：**BE-Refactor**（logging_SOP + database_SOP 強制 §5 核查）
> Commit 拆分忠實轉自 plan v5 §9 Q6（5 commit，不自行增刪重排）

---

## §0 改版規則
- 改版觸發：§8 Commit 拆分或 §6 驗收變動 → 改章節 + §99.2 Revision
- 本檔產出後 plan v1-v5 續留 baton、唯 C5 Checkout 一次性歸檔

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 | `tests/test_lazyload_multi.py`（10 單元/整合/並發測試）|
| **修改檔案** | 4 | `rag_retriever.py`（U1/U7 自載+is_ready·C1；U8 RLock·C2）/ `ai_core.py`（U8 _paper_cache 鎖·C2；P4 docstring·C4）/ `web_server.py`（U2 接線·C3；U5/U9 釋放·C4）/ `settings.py`（U4 cap100·C3；RELEASE_ON_UPLOAD·C4）|
| **狀態更新** | 2 | TODO.md / prompts/INDEX.md |
| **Commits** | 5 | C1 → C2 → C3 → C4 → C5(Checkout) |
| **baton 歸檔** | 1 次 | C5 收官一次性 mv（plan v1-v5 + tasks + C1-C5 執行報告 → plans//tasks//executions/）+ git add |

---

## §1 TL;DR（概要）

修跨文件 hashtag 檢索只召回當前篇之漏召（根因＝ API-PERF C3 lazy-load 只載當前 paper、retrieve_multi 需全 tagged 篇）。5 commit：

- **C1 — Retriever loader 接縫（自載咽喉）**：`set_loader` + `_get_vector_store` 完全 miss 自載 + `is_ready` loader-aware（U1/U7）。
- **C2 — Cache 併發鎖純硬化（行為不變防 race）**：RLock 包 in-memory cache 全 mutation（U8）。
- **C3 — 啟動接線與容量（核心 LIVE）**：web_server 啟動 `set_loader` 接線 + `RAG_MAX_CACHE`=100（U2/U4，純加法）。
- **C4 — 記憶體釋放策略（換篇/上傳全清跳過活躍）**：`/content` 換篇 gate + `/upload` 開關 + 跳過 active_streams + gc + docstring（U5/U9/P4）。
- **C5 — Checkout 收官（Conformance 與歸檔）**。

---

## §2 現況

- `web_server.py:797-802` chat 端點只 lazy-load 當前 `paper_id`；`rag_retriever.py:258-261` retrieve_multi 對未註冊篇 `vs is None: continue` 靜默跳過。
- `_get_vector_store`(88-105) 兩層（vector_stores / paper_vector_paths 命中只重載 FAISS）、缺「完全 miss 自載」第三層。
- `is_ready()`(111-113)=`bool(paper_vector_paths)`、全清後 False 致 retrieve_multi 繞過。
- retriever/ai_core 無任何 Lock（`grep Lock` 全空）；retrieve_multi 跑 `to_thread`（web_server.py:124）。
- 釋放：vector_stores/_paper_cache LRU cap5+gc；rag_trees/paper_vector_paths 永不淘汰。
- 前端 `/content` 切換文章（index.html:2634→2678→2698）**及語言切換同篇**（2761-2766）皆打；`/content` 端點(735-749) display-only 零向量。
- 詳見 plan v5 §3.1-§3.6 全證據。

## §3 觀察問題

對齊 plan v5：① 跨文件漏召（核心）② is_ready 全清繞過 ③ in-memory cache 併發 race ④ 切換抽掉進行中串流 ⑤ 語言切換誤放（F1）⑥ 上傳釋放未必即還 OS（M1·gc）。

## §4 設計方案

### §4.1 C1 — Retriever loader 接縫（自載咽喉）
`rag_retriever.py`：`__init__` 加 `self._loader=None`；新增 `set_loader(fn)`；`_get_vector_store` 於兩層之後加第三層「完全 miss 且 `self._loader` → 呼 `self._loader(owner_id, paper_id)` 後重試取庫」；`is_ready()` 改 `return bool(self.paper_vector_paths) or self._loader is not None`。`# === [LAZYLOAD-MULTI-1 C1] ===` 包裹。對齊 U1/U7、§4 lazy-load callback + rag_tree handoff（loader 已含 set_rag_tree）。

### §4.2 C2 — Cache 併發鎖純硬化（行為不變防 race）
`rag_retriever.py`：`import threading`、`__init__` 加 `self._lock=threading.RLock()`；以 `with self._lock:` 包 `add_paper`/`_evict_vector_lru`/`_get_vector_store` 自載段/`remove_paper`/`set_rag_tree` 之 dict mutation。`ai_core.py`：加 `self._cache_lock=threading.RLock()`、包 `load_paper_cache` LRU 段 + `remove_paper` 的 `_paper_cache` mutation。**行為不變**（RLock 可重入、各 class 鎖 own dict、無跨 class 鎖序→無死鎖）。對齊 U8、§4 鎖不變式（涵蓋端點 L800 + 自載兩路）。

### §4.3 C3 — 啟動接線與容量（核心 LIVE）
`settings.py`：`RAG_MAX_CACHE` 預設 `"5"`→`"100"`。`web_server.py` 啟動 lifespan（API-PERF C3 區 ~L224-229 之後）：`ai_core.retriever.set_loader(lambda o,p: paper_manager.load_paper_resources(OUTPUT_DIR,o,p,ai_core))`。`# === [LAZYLOAD-MULTI-1 C3] ===` 包裹。對齊 U2/U4。**此 commit 後核心跨文件修復 LIVE**。

### §4.4 C4 — 記憶體釋放策略（換篇/上傳全清跳過活躍）
`settings.py`：加 `RELEASE_ON_UPLOAD`（預設 on）。`web_server.py`：
- 模組級 `_owner_current_paper: Dict[int,str]={}`（owner→當前 paper_uuid）。
- helper `_release_caches_except_active(owner_id)`：由 `active_streams` 收 `done==False` 之 `session.paper_uuid` 集；逐一對該 owner 之 cached 篇（`ai_core._paper_cache` + `retriever.paper_vector_paths` 該 owner key）呼 `ai_core.remove_paper(owner,uuid)`、**skip 活躍 uuid**；末 `gc.collect()`。
- `/content`(735)：服務後比對 `paper_id != _owner_current_paper.get(uid)` → 釋放 + 更新當前篇（**語言切換同篇不觸發**·F1）。
- `/upload`(448)：`if settings.RELEASE_ON_UPLOAD: _release_caches_except_active(uid)`。
- `# === [LAZYLOAD-MULTI-1 C4] ===` 包裹。
`ai_core.py`：修 `remove_paper` docstring 移除「當前對話上下文」誤述（P4）。對齊 U5/U9。

---

## §5 風險

對齊 plan v5 §5：P0 race→C2 RLock；is_ready→C1；P2 串流→C4 跳過 active_streams；F1 語言切換→C4 換篇 gate；title 退化→C1/C4 全清強制 loader 全載；M1→C4 gc；DB 安全（✅已解、與 cache 鎖兩層）。每 commit 行為界線見 §8。

## §6 測試計畫（逐 Commit；對齊 plan v5 §8.1 十項 + §5 SOP + §8.2 E2E）

### §6.1 C1 驗收
- pytest（新建 `tests/test_lazyload_multi.py`）：`test_get_vector_store_self_loads_on_miss` / `test_get_vector_store_loader_unset_returns_none`（向後相容）/ `test_retrieve_multi_loads_all_tagged`（**整合**、6 篇只註冊 1、其餘自載）/ `test_evict_then_reload_preserves_title` / `test_is_ready_after_full_evict`。
- grep：`grep -n 'def set_loader\|LAZYLOAD-MULTI-1 C1' rag_retriever.py`（有命中）；`grep -n 'self._loader is not None' rag_retriever.py`（is_ready loader-aware）。

### §6.2 C2 驗收
- pytest：`test_concurrent_lazyload_no_corruption`（多 thread 自載+evict 無 KeyError/corruption）；**既有全套件全綠**（行為不變回歸網）。
- grep：`grep -n 'threading.RLock\|with self._lock' rag_retriever.py`（有命中）；`grep -n '_cache_lock' ai_core.py`（有命中）。
- SOP：logging `grep -nE 'logger.error' rag_retriever.py ai_core.py`（新增者須 exc_info）；database `grep -nE '\.commit\(\)' ...`（無裸 commit）。

### §6.3 C3 驗收
- pytest：`test_cap_100_default`（+ env override）。
- grep：`grep -n 'set_loader\|LAZYLOAD-MULTI-1 C3' web_server.py`（接線有命中）；`grep -n 'RAG_MAX_CACHE.*100' settings.py`（預設 100）。

### §6.4 C4 驗收
- pytest：`test_release_skips_active_stream`（done==False 不清）/ `test_release_only_on_actual_switch`（同 paper_id 不放、不同才放·F1）/ `test_release_on_upload_toggle`（on/off）。
- grep：`grep -n '_release_caches_except_active\|_owner_current_paper\|RELEASE_ON_UPLOAD\|gc.collect\|LAZYLOAD-MULTI-1 C4' web_server.py`（有命中）；`grep -n 'RELEASE_ON_UPLOAD' settings.py`；確認 `ai_core.remove_paper` docstring 無「當前對話上下文」。
- SOP：釋放 log 結構化；database 無裸 commit（loader 唯讀）。

### §6.5 全任務 E2E（baron · plan v5 §8.2）
直接 `#cv 比較…` 涵蓋全 6 位 + 引用顯《文件名》 / chosen ≥5 pid / 並發兩 paper 無錯亂 / 串流中切篇不斷 / 語言切換不釋放 / 上傳釋放+RAM 降 / shadow pid 入 chosen。

## §7 不可動清單（對齊 plan v5 §6）

- [ ] `retrieve_multi_with_context` 保底演算法（RAG-MULTI-1 C2）/ `retrieve_with_context` 單篇邏輯（除共用 `_get_vector_store` 鎖點/RLock）。
- [ ] context 格式 `## 摘自文件《…》` / 向量資料 / FAISS / index_meta / embedding 模型 / RAG_SCORE_THRESHOLD / 上游 hashtag 解析。
- [ ] `/content` 端點 display 讀檔回傳（只加釋放 hook、不改回傳）。
- [ ] shadow UI 可見性（list_papers/status）；retrieve_multi 不加 shadow 過濾。
- [ ] 禁無鎖 mutate in-memory cache（C2 後）。

## §8 推薦 Commit 拆分（依 plan v5 §9 Q6）

### C1 — Retriever loader 接縫（自載咽喉）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `rag_retriever.py`（set_loader + _get_vector_store 第三層自載 + is_ready loader-aware）；新增 `tests/test_lazyload_multi.py`（5 測試） |
| **安全性** | 🟢 高 — 行為由 loader 閘門：未設＝現況回 None、既有測試不破；單檔 |
| **可逆性** | 🟢 高 — 純新增方法 + 守衛，`git revert` 或移除 `# === [LAZYLOAD-MULTI-1 C1] ===` 段 |
| **驗收 grep 條件** | `grep -n 'def set_loader\|self._loader is not None\|LAZYLOAD-MULTI-1 C1' rag_retriever.py`（有命中）；`pytest tests/test_lazyload_multi.py -k 'self_loads or loader_unset or loads_all_tagged or preserves_title or is_ready' -q`（全綠） |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `__init__` 加 `self._loader=None`；② `def set_loader(self,fn): self._loader=fn`；③ `_get_vector_store` 末（兩層後、`return None` 前）加：`if self._loader is not None: self._loader(owner_id,paper_id); ` 再重試 `if key in self.vector_stores: return ...; if key in self.paper_vector_paths: store=load_vector_store(...); ...`；④ `is_ready` 改 `return bool(self.paper_vector_paths) or self._loader is not None`。對齊 U1/U7 + §4 lazy-load callback（key=paper_uuid 原值）+ rag_tree handoff（loader 已含 set_rag_tree） |

### C2 — Cache 併發鎖純硬化（行為不變防 race）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `rag_retriever.py`（RLock + 包三 dict mutation）/ `ai_core.py`（_cache_lock + 包 _paper_cache mutation）；`tests/test_lazyload_multi.py` 追加並發測試 |
| **安全性** | 🟡 中 — 鎖範圍需正確包全 mutation；RLock 可重入避免自鎖；各 class 鎖 own dict 無跨鎖序 → 無死鎖；**行為不變**（既有全套件即回歸網） |
| **可逆性** | 🟢 高 — 移除鎖即回 C1 狀態 |
| **驗收 grep 條件** | `grep -n 'threading.RLock\|with self._lock\|LAZYLOAD-MULTI-1 C2' rag_retriever.py`；`grep -n '_cache_lock' ai_core.py`；`pytest tests/test_lazyload_multi.py -k concurrent -q`；**全套件全綠** |
| **依賴關係** | 前置 C1（鎖包含 C1 自載段） |
| **具體實作細節** | rag_retriever：`import threading`、`self._lock=threading.RLock()`；`with self._lock:` 包 `add_paper`（[key]=/move_to_end/_evict）、`_evict_vector_lru`（popitem 迴圈）、`_get_vector_store` 自載寫段、`remove_paper`、`set_rag_tree`。ai_core：`self._cache_lock=threading.RLock()`、包 `load_paper_cache`（_paper_cache[key]=/move_to_end/popitem）、`remove_paper`（del _paper_cache）。對齊 U8 + §4 鎖不變式（in-memory dict、與 §3.1⑥ DB 安全兩層、涵蓋端點 L800 + 自載） |

### C3 — 啟動接線與容量（核心 LIVE）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（**僅啟動 lifespan 接線段**）/ `settings.py`（RAG_MAX_CACHE 預設）；`tests/test_lazyload_multi.py` 追加 cap 測試 |
| **安全性** | 🟢 高 — 純加法 2-3 行；接線後 ③ 生效、核心修復 LIVE |
| **可逆性** | 🟢 高 — 移除接線行 / 還原預設 |
| **驗收 grep 條件** | `grep -n 'set_loader\|LAZYLOAD-MULTI-1 C3' web_server.py`；`grep -n 'RAG_MAX_CACHE.*"100"\|RAG_MAX_CACHE.*100' settings.py`；`pytest tests/test_lazyload_multi.py -k cap -q` |
| **依賴關係** | 前置 C1（set_loader 存在）；建議 C2 後（接線即上線、先有鎖較穩） |
| **具體實作細節** | settings：`RAG_MAX_CACHE = int(os.getenv("RAG_MAX_CACHE","100"))`。web_server lifespan（`# === [API-PERF C3] ===` 區附近、ai_core 與 retriever 就緒後）：`ai_core.retriever.set_loader(lambda o,p: paper_manager.load_paper_resources(OUTPUT_DIR,o,p,ai_core))`，`# === [LAZYLOAD-MULTI-1 C3] ===` 包裹。**僅動啟動段、不碰任何端點 handler**（與 C4 hunk 不重疊）。對齊 U2/U4 |

### C4 — 記憶體釋放策略（換篇/上傳全清跳過活躍）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（**僅 `/content` + `/upload` 端點段 + 模組級 helper/狀態**）/ `ai_core.py`（remove_paper docstring）/ `settings.py`（RELEASE_ON_UPLOAD）；`tests/test_lazyload_multi.py` 追加 3 釋放測試 |
| **安全性** | 🟡 中 — 新增釋放行為；靠 ③ 重載兜底、跳過 active_streams 防抽串流、換篇 gate 防語言切換誤放 |
| **可逆性** | 🟢 高 — 移除 hook/helper 回不釋放狀態 |
| **驗收 grep 條件** | `grep -n '_release_caches_except_active\|_owner_current_paper\|gc.collect\|LAZYLOAD-MULTI-1 C4' web_server.py`；`grep -n 'RELEASE_ON_UPLOAD' settings.py`；`grep -nc '當前對話上下文' ai_core.py`（期望 0）；`pytest tests/test_lazyload_multi.py -k 'release' -q` |
| **依賴關係** | 前置 C3（接線後釋放才有 ③ 兜底）|
| **具體實作細節** | settings：`RELEASE_ON_UPLOAD = os.getenv("RELEASE_ON_UPLOAD","true").lower()=="true"`。web_server：模組級 `_owner_current_paper={}`；`def _release_caches_except_active(owner_id)`：`active={s.paper_uuid for s in active_streams.values() if not s.done}`；列該 owner cached uuid（`{p for (o,p) in list(ai_core._paper_cache)+list(retriever.paper_vector_paths) if o==owner_id}`）；逐一 `if uuid not in active: ai_core.remove_paper(owner_id,uuid)`；末 `gc.collect()`。`/content`：回傳前/後 `if paper_id != _owner_current_paper.get(current_user.id): _release_caches_except_active(current_user.id); _owner_current_paper[current_user.id]=paper_id`。`/upload`：`if settings.RELEASE_ON_UPLOAD: _release_caches_except_active(current_user.id)`。`# === [LAZYLOAD-MULTI-1 C4] ===` 包裹。ai_core：remove_paper docstring 移「當前對話上下文」。對齊 U5/U9/P4 + §4 跳過活躍串流 handoff（paper_uuid 基準）+ §4 當前篇狀態 handoff（F1）|

### C5 — Checkout 收官（Conformance 與歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 無業務碼；Conformance 驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒 |
| **安全性** | 🟢 高 — 純文件 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | Conformance 三+二維度（plan v5 §2 U1-U9 / §6 各 commit grep+pytest / §7 不可動 / 提示詞稽核 / msg 完整）；`ls baton/ \| grep LAZYLOAD`（歸檔後 0 殘留）|
| **依賴關係** | 前置 C1-C4 全 commit |
| **具體實作細節** | Conformance 全綠 → baton 一次性 mv：plan v1-v5 → plans/、tasks → tasks/、C1-C4 執行報告 → executions/、C5 報告直寫 executions/；TODO 完成表（C1-C5）+ active 移除 + 索引 ✅ + 全量 hash 自癒；msg → /tmp |

---

## §9 Open Questions

plan v5 §9 已全定案（Q1 換篇 gate / Q2 砍 TTL / Q3 全清四 dict+gc / Q4 cap 天花板 / Q5 attach 受惠 / Q6 本拆分 / Q7 RELEASE_ON_UPLOAD=on / P3 不設篇數上限 / P4 修 docstring）；tasks 階段無新增 OQ。

> **銜接（各階段執行報告）**：C1-C4 每個 Commit 執行時各產一份 `_執行.md`（套 `template_execution.md`、暫存 baton/、嚴禁 mv/git add）；C5 Checkout 一次性歸檔 plan v1-v5 + tasks + C1-C5 執行報告。

---

## §99 治理規格與 Revision

### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| 目的 | LAZYLOAD-MULTI-1 commit 拆分與驗收清單 |
| 權威源 | 本檔 §8（轉自 plan v5 §9 Q6）|
| 引用方 | C1-C5 Run/Checkout 執行報告 |
| 不可動唯一源 | §7（對齊 plan v5 §6）|
| 改版觸發 | §8/§6 變動 |

### §99.2 Revision 歷程
- v1 (2026-06-10)：初稿——依 plan v5 §9 Q6 拆 5 commit（C1 loader 接縫 / C2 RLock 純硬化 / C3 接線+cap100 / C4 釋放策略 / C5 Checkout）+ §0.5 成果盤點 + §6 逐 commit 驗收（plan v5 §8.1 十項）+ §7 不可動 + §8 六維度表（含 C3/C4 web_server hunk 邊界）
