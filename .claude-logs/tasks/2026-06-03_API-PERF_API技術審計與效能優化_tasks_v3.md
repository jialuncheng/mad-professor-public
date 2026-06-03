# API-PERF API 技術審計與效能優化 — Tasks（v3）

> 本文件為 API-PERF 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_API-PERF_API技術審計與效能優化_plan_v2.md` 計畫產出，含 6 個 Commit（C1–C5 實作 + C6 單一收官 Checkout）。
> commit / push 由 baron 手動執行（CLAUDE.md §1.3）；本檔不含 git commit 草稿。
> **收官歸檔鐵律**：C1–C5 執行期所有 plan／tasks／執行報告一律暫存 baton/、不移動、不入版控；**唯一在最後 C6（Checkout）一次性 `mv` + `git add`** 搬移 plan + tasks + 全部 `C*_執行.md`（WORKFLOW_SOP §3）。
> **新架構對齊**：U1 Semaphore 守 `Orchestrator.run(ctx)`（B 軌）+ `run_pipeline`（A 軌）雙派發點；U3 LRU 配 `ai_core.py`／`rag_retriever.py` 快取容器；U7 計時埋點對齊已落地 `PhaseEnum`(P1–P4) + Orchestrator 迴圈，(phase, stage) 二維鍵。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `scripts/analyze_performance.py`（U7 CLI 分析工具）/ `tests/test_api_performance_and_robustness.py`（5 測試） |
| **修改檔案** | 6+ 支 | `db.py`（U6）/ `web_server.py`（U4+U5+U3 lifespan+U1 雙軌 Semaphore）/ `ai_core.py`（U3 LRU）/ `rag_retriever.py`（U3 LRU）/ `paper_manager.py`（U3 廢 preload）/ `pipeline_core.py`（U2 nice+U7 埋點）/ `pipelines/orchestrator.py`（U7 附加埋點）/ `processor/pdf_processor.py`（U2 子進程 nice，視實作）/ `settings.py`（U1/U3 配置項） |
| **目錄初始化** | 1 個 | `scripts/`（CLI 工具目錄，若不存在） |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 6 個 | C1（DB 池）→ C2（流式上傳+真實 IP）→ C3（LRU 快取）→ C4（Semaphore+nice）→ C5（計時埋點+CLI）→ C6（收官 Checkout） |
| **執行報告** | 6 個 | `baton/2026-06-03_API-PERF_C1~C6_執行.md`（套用 template_execution.md、暫存 baton/） |
| **.bak 備份** | 每改既有檔前必備 | 各 Commit 修改 `db.py`/`web_server.py`/… 前產 `.bak`，納入該 Commit git add |
| **baton 歸檔** | 1 次 | **僅 C6 收官**一次性 `mv` plan_v2→`plans/` + tasks_v3→`tasks/` + 全部 `C*_執行.md`→`executions/` + git add |

> ⚠️ **業務代碼變動提示**：本任務修改多支業務代碼（`web_server.py`/`pipeline_core.py`/`ai_core.py`/`db.py`/`paper_manager.py`/`rag_retriever.py`），均在 CLAUDE.md §3 嚴禁清單內——本任務為 PIPE「基建前置」、plan v2 已 baron 核准；各 Commit 修改前 `.bak` 備份、嚴守 §7 不可動清單。
> ⚠️ **時序（本版修正）**：C1–C5 實作期 plan/tasks/報告**全留 baton/**；**僅 C6 收官一次性搬移 plan + tasks + 全部報告**（不在 C1 提前搬 plan）。

---

## §1 TL;DR（概要）

- **挑戰**：高密度上傳/RAG 併發引發 Event Loop 奪取與 GIL 阻塞、大檔 `read()` OOM、SQLite 寫鎖 `database is locked`、FAISS 無上限 preload 內存枯竭、Docker 代理下 IP 鎖死全網閘道；現行 stage 僅文字日誌、無結構化效能數據。
- **解法**（逐 Commit、中文括號命名）：
  - **C1（資料庫連接池與防鎖死）**：U6 `db.py` busy_timeout 5s→30s + QueuePool + pool_pre_ping。
  - **C2（流式上傳與真實 IP）**：U4 `upload_paper` 1MB 分塊流式寫 + 魔術字節/413/415 + U5 `login` X-Forwarded-For 真實 IP。
  - **C3（向量庫 LRU 動態快取）**：U3 廢 lifespan preload、`ai_core`/`rag_retriever` Lazy Load + 上限 5 + LRU pop。
  - **C4（並發信號量與子進程降優）**：U1 `PIPELINE_SEMAPHORE` 守 A 軌 `run_pipeline` + B 軌 `run_pipeline_shadow`/`Orchestrator.run`、queued SSE 狀態 + U2 子進程 `nice 19`。
  - **C5（結構化計時埋點與 CLI）**：U7 `(phase, stage)` 二維鍵 `performance_metric` + `pipeline_finished`(phases_breakdown) + `rag_finished` + `scripts/analyze_performance.py`；埋點同落 `pipeline_core`（A 軌 phase 群組映射）與已落地 `Orchestrator`（P1–P4 附加式）。
  - **C6（收官 Checkout）**：plan_v2 + tasks_v3 + 全部 C1–C6 執行報告一次性 baton→plans//tasks//executions/。
- **影響範圍**：6+ 支業務代碼 + 2 新增檔；無 DB Schema 變動、無 API 路由簽名變更。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀（plan §3 grep 行號） | 待處理 |
|---|---|---|
| `web_server.py` | `upload_paper L448` 一次性 `await file.read()`；`login L352` `request.client.host`；`lifespan L220` 調 `preload_vector_stores`；雙軌派發點 `run_pipeline`(L493)/`run_pipeline_shadow`(L541) | U4 流式 / U5 真實 IP / U3 廢 preload / U1 Semaphore 守雙軌 |
| `paper_manager.py` | `preload_vector_stores L429` 一口氣載入全部 done 向量庫 | U3 廢除（lifespan 不再呼叫；函式保留標棄用） |
| `ai_core.py` | `self._paper_cache` 無容量限制 | U3 LRU（上限 5 + pop） |
| `rag_retriever.py` | `self.vector_stores` 無自動 pop | U3 LRU（上限 5 + pop）；**`retrieve_*` 檢索演算法不動（§7）** |
| `pipeline_core.py` | `process L211`；stage 迴圈 `L416/L427` 純文字日誌 | U7 結構化 (phase,stage) 埋點；U2 子進程 nice |
| `pipelines/orchestrator.py` | PIPE-CORE 已落地、`run(ctx)` 宣告式 P1→P4 迴圈 | U7 對齊 PhaseEnum 加 (phase,stage) 計時（附加式埋點、非重構本體） |
| `db.py` | `create_engine L28`／`busy_timeout=5000 L49` | U6 30s + QueuePool + pool_pre_ping |
| `scripts/` | 無 `analyze_performance.py` | U7 新建 CLI |

---

## §3 觀察問題

### 問題 #1：大檔 OOM / IP 鎖閘道 / SQLite 寫鎖 / FAISS 無上限 preload
- **證據**：plan §3.1 grep——`await file.read()` L448；`request.client.host` L352；`preload_vector_stores` L429/L220；`busy_timeout=5000` L49。
- **影響**：高載/併發下 OOM、全網登入鎖死、`database is locked`、內存枯竭。

### 問題 #2：現行 stage 僅文字日誌、無結構化效能數據與 phase 維度
- **證據**：plan §3.1——`pipeline_core.py L416 [stage] 開始` / `L427 [stage] 完成 耗時=`。
- **影響**：無法量化各 Phase/子階段耗時；需 (phase,stage) 結構化埋點 + CLI。

---

## §4 設計方案

> 逐 Commit 落地概要；完整規格見 plan v2 §2（U1–U7）。

- **C1（U6）**：`db.py` busy_timeout 5000→30000；`create_engine` 配 QueuePool（pool_size=5/max_overflow=10/pool_pre_ping=True）。
- **C2（U4+U5）**：`upload_paper` 1MB 分塊流式寫磁碟（內存常數 <10MB）+ 首塊 `%PDF`（415）+ 100MB 上限（413）；`login` 優先 `X-Forwarded-For` 最左 IP，無則降級 `request.client.host`。
- **C3（U3）**：廢 `lifespan` preload（移除 `web_server.py L220` 呼叫）；`ai_core._paper_cache`、`rag_retriever.vector_stores`/`rag_trees` 改 `OrderedDict` + Lazy Load + 上限 5 + `popitem(last=False)` LRU（+ 可選 `gc.collect()`，§7 Q2）。**`retrieve_*` 檢索不動**。
- **C4（U1+U2）**：`PIPELINE_SEMAPHORE`（settings 配置、預設 1）守 A 軌 `run_pipeline` + B 軌 `run_pipeline_shadow`（`Orchestrator.run`）派發；等待期 SSE `queued`。U2 背景子進程 `nice 19`（Windows soft-fail）。
- **C5（U7）**：`(phase,stage)` 二維鍵 `performance_metric` 埋點落 ① `pipeline_core` 11-stage（A 軌、phase 群組映射）② 已落地 `orchestrator.run`（P1–P4 附加式）；`pipeline_finished`(phases_breakdown) + 獨立 `rag_finished`；新建零依賴 `scripts/analyze_performance.py`。
- **C6（收官）**：plan_v2 + tasks_v3 + C1–C6 報告一次性歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 修改 6+ 支業務代碼（CLAUDE.md §3 嚴禁清單） | 🟡 中 | plan v2 已 baron 核准基建前置；各 Commit 修改前 `.bak`；嚴守 §7；附加式為主 |
| U3 LRU 誤淘汰活躍向量庫致檢索失敗 | 🟡 中 | 命中即 `move_to_end`；上限 5；`retrieve_*` 演算法不動；test_lru 驗證 |
| U1 Semaphore 死鎖/未釋放 | 🔴 高 | `async with` 保證釋放；queued 僅標記不阻 SSE；test_semaphore_queue 驗證 |
| U7 埋點觸碰 `orchestrator.py`（PIPE-CORE 交付、§4 不可動 PIPE 重構本體） | 🟡 中 | **僅附加式計時 log、不改 DAG/合約/Strategy 本體**；C5 執行前 baron 確認；orchestrator 既有 20 pytest 維持全綠 |
| U2 nice 在 Windows 失效 | 🟢 低 | 捕 `AttributeError`/`OSError` soft-fail（§7 Q1） |
| 既有測試迴歸 | 🟡 中 | 每 Commit 跑 `pytest tests/ -q`；既有 `test_logging_config` LOG_FORMAT 失敗為 .env 環境誘發、非本任務 |
| baton 報告提早 mv/git add（含 plan） | 🔴 高 | C1–C5 全留 baton；**唯 C6 收官一次性搬 plan+tasks+報告** |

---

## §6 測試計畫

> 每個實作 Commit 在 `tests/test_api_performance_and_robustness.py` 追加對應測試（C1 建檔，C2–C5 追加；修改既有測試檔前 `.bak`）。

### §6.1 C1 驗收（U6）
```bash
grep -nE "busy_timeout=30000|QueuePool|pool_pre_ping" db.py   # 期望：有命中
pytest tests/test_api_performance_and_robustness.py -k db -q
```
### §6.2 C2 驗收（U4+U5）
```bash
grep -nE "1024\s*\*\s*1024|%PDF|X-Forwarded-For" web_server.py   # 期望：有命中
pytest tests/test_api_performance_and_robustness.py -k "streaming or forwarded" -q
```
### §6.3 C3 驗收（U3）
```bash
grep -nE "OrderedDict|popitem|move_to_end" ai_core.py rag_retriever.py   # 期望：有命中
grep -n "preload_vector_stores" web_server.py   # 期望：lifespan 不再呼叫（0 命中或已註記廢棄）
pytest tests/test_api_performance_and_robustness.py -k lru -q
```
### §6.4 C4 驗收（U1+U2）
```bash
grep -nE "PIPELINE_SEMAPHORE|Semaphore|os.nice|nice\(" web_server.py settings.py pipeline_core.py processor/pdf_processor.py
grep -n "queued" web_server.py   # 期望：有命中
pytest tests/test_api_performance_and_robustness.py -k "semaphore or queue" -q
```
### §6.5 C5 驗收（U7）
```bash
grep -nE "performance_metric|pipeline_finished|rag_finished|phases_breakdown" pipeline_core.py pipelines/orchestrator.py
ls scripts/analyze_performance.py && python scripts/analyze_performance.py --help 2>&1 | head
pytest tests/test_api_performance_and_robustness.py -k "performance or phase" -q
```
### §6.6 全 Commit 共通（零迴歸）
```bash
pytest tests/ -q   # 既有測試全綠（含 pipelines 20 pytest）；既有 LOG_FORMAT 失敗為 .env 環境誘發、非本任務
```

---

## §7 不可動清單

明確劃定修改邊界。**以下嚴禁任何改動：**

- [ ] `rag_retriever.py` 既有 RAG 核心檢索 `retrieve_with_context`／`retrieve_multi_with_context` 演算法與閾值（U3 僅改快取容器、不改檢索）。
- [ ] 既有 API 路由與功能簽名 100% 相容，不破壞前端調用。
- [ ] `/api/papers/{paper_id}/images/{filename}` 實體路徑防逃逸 `relative_to` 邊界校驗。
- [ ] `_normalize_tag` 全域小寫與標籤單一真理源。
- [ ] **PIPE 四 Phase 切分／三層解耦／策略管線本體**：U7 埋點僅**附加式計時 log** 至 Orchestrator，嚴禁觸碰 DAG 推進／合約驗證／Strategy 介面本體（屬 PIPE plan）。
- [ ] 舊單體 A 軌 `run_pipeline` 既有 process 調用本體（U1 僅在派發外層加 Semaphore 守護）。
- [ ] 主 repo 目錄（worktree 父目錄）。
- [ ] baton/ 暫存文件（C1–C5 期間嚴禁提早 mv/git add，含 plan；唯 C6 收官一次性搬移）。

---

## §8 推薦 Commit 拆分

### C1 — 資料庫連接池與防鎖死配置（U6 SQLite QueuePool）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `db.py`（+`.bak`）；`tests/test_api_performance_and_robustness.py`（建檔） |
| **安全性** | 🟢 高 — 連線參數調整、無 Schema 變動、無 API 簽名變更 |
| **可逆性** | 🟢 高 — 還原 `.bak` |
| **驗收 grep 條件** | `grep -nE "busy_timeout=30000\|QueuePool\|pool_pre_ping" db.py` # 期望：有命中 |
| **依賴關係** | 無前置 |
| **具體實作細節** | 1. `cp db.py .claude-logs/archive/2026-06-03_API-PERF_C1_db.py.bak`（納入 git add）。2. `db.py L49` `PRAGMA busy_timeout=5000`→`30000`。3. `create_engine`（L28）配 `poolclass=QueuePool, pool_size=5, max_overflow=10, pool_pre_ping=True`（SQLite 維持 `check_same_thread=False`；對齊 database SOP `pool_pre_ping`）。4. 新建 `tests/test_api_performance_and_robustness.py` + `test_db_busy_timeout_and_pool`（assert pool 配置 + busy_timeout PRAGMA）。5. database SOP 核查（grep 無裸 commit）。6. 產 C1 執行報告（baton/）。 |

### C2 — 流式上傳與真實 IP 解析（U4 Streaming + U5 Real IP）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（+`.bak`，`upload_paper`/`login`）；`tests/...`（追加，先 `.bak`） |
| **安全性** | 🟡 中 — 改上傳/登入入口；附加式、不改路由簽名 |
| **可逆性** | 🟢 高 — 還原 `.bak` |
| **驗收 grep 條件** | `grep -nE "1024\s*\*\s*1024\|%PDF\|X-Forwarded-For" web_server.py` # 期望：有命中 |
| **依賴關係** | C1 |
| **具體實作細節** | 1. `.bak` 備份 `web_server.py` + 測試檔。2. **U4** `upload_paper`（L448）：移除一次性 `await file.read()`，改 `while chunk := await file.read(1024*1024):` 迴圈 write 臨時檔；首塊校驗 `chunk[:5]` 含 `%PDF`（否則刪檔回 415）；累計 size>100MB 截斷刪檔回 413。3. **U5** `login`（L352）：`xff = request.headers.get("X-Forwarded-For"); ip = xff.split(",")[0].strip() if xff else (request.client.host if request.client else "unknown")`。4. 追加 `test_upload_file_streaming_constant_ram` + `test_x_forwarded_for_parsing`。5. **不動** images 路徑防逃逸（§7）。6. 產 C2 執行報告（baton/）。 |

### C3 — 向量庫與 RAG LRU 動態快取（U3 Lazy Load + LRU）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `ai_core.py`／`rag_retriever.py`／`paper_manager.py`／`web_server.py`(lifespan)／`settings.py`（各 +`.bak`）；`tests/...`（追加，先 `.bak`） |
| **安全性** | 🟡 中 — 改快取容器與啟動載入；`retrieve_*` 演算法不動 |
| **可逆性** | 🟢 高 — 還原 `.bak` |
| **驗收 grep 條件** | `grep -nE "OrderedDict\|popitem\|move_to_end" ai_core.py rag_retriever.py` # 期望：有命中；`grep -n "preload_vector_stores" web_server.py` # 期望：lifespan 不再呼叫 |
| **依賴關係** | C2 |
| **具體實作細節** | 1. `.bak` 備份四檔 + 測試檔。2. **廢 preload**：移除 `web_server.py L220` `paper_manager.preload_vector_stores(...)` 呼叫（函式保留標 `# deprecated by API-PERF U3`、不刪以免外部引用斷裂）。3. **`rag_retriever.py`**：`self.vector_stores`/`self.rag_trees` 改 `collections.OrderedDict`；`_MAX_CACHE=5`（settings 可配）；`_get_vector_store`/`add_paper`/`set_rag_tree` 命中 `move_to_end`、插入後 `len>5` 則 `popitem(last=False)` + log LRU 淘汰（可選 `gc.collect()`，§7 Q2）。**`retrieve_with_context`/`retrieve_multi_with_context` 檢索邏輯不動**。4. **`ai_core.py`**：`_paper_cache` 同改 OrderedDict + 上限 5 + LRU pop。5. 追加 `test_lru_vector_store_eviction`（加載 6 個、驗第 1 被 pop、活躍留存）。6. 產 C3 執行報告（baton/）。 |

### C4 — 並發信號量與子進程降優（U1 Semaphore + U2 Nice）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `settings.py`（+`PIPELINE_MAX_CONCURRENT`）／`web_server.py`（雙軌派發點 + queued SSE）／`pipeline_core.py` 或 `processor/pdf_processor.py`（子進程 nice）（各 +`.bak`）；`tests/...`（追加，先 `.bak`） |
| **安全性** | 🔴 中高 — 併發控制核心；附加式守護、A 軌 process 本體不動 |
| **可逆性** | 🟢 高 — 還原 `.bak` |
| **驗收 grep 條件** | `grep -nE "PIPELINE_SEMAPHORE\|os.nice\|queued" web_server.py settings.py` # 期望：有命中 |
| **依賴關係** | C3 |
| **具體實作細節** | 1. `.bak` 備份。2. **U1**：`web_server.py` 模組級 `PIPELINE_SEMAPHORE = asyncio.Semaphore(settings.PIPELINE_MAX_CONCURRENT)`（settings 預設 1）；**A 軌** `run_pipeline`（L493）將 `run_in_executor(...)` 包入 `async with PIPELINE_SEMAPHORE:`，acquire 前若 locked 設 `processing_tasks[task_key]['status']='queued'` + progress `{"stage":"queue","stage_name":"等待佇列中...（排隊中）","progress":0}`，acquire 後改 `'processing'`；**B 軌** `run_pipeline_shadow`（L541）同樣 `async with PIPELINE_SEMAPHORE:` 守 `Orchestrator().run(ctx)`（全系統並發上限統一）。**A 軌 `pipeline.process` 調用本體不動**。3. **U2**：背景 PDF 解析子進程（`processor/pdf_processor.py`）加 `preexec_fn=lambda: os.nice(19)` 或 psutil；`try/except (AttributeError, OSError)` soft-fail（§7 Q1）。4. 追加 `test_concurrency_semaphore_queue`（並發 2、驗第 2 queued、第 1 釋放後啟動）。5. 產 C4 執行報告（baton/）。 |

### C5 — 結構化計時埋點與 CLI 分析工具（U7 (phase,stage) 二維鍵）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipeline_core.py`（A 軌埋點）／`pipelines/orchestrator.py`（B 軌附加埋點）（各 +`.bak`）；新建 `scripts/analyze_performance.py`；`tests/...`（追加，先 `.bak`） |
| **安全性** | 🟡 中 — 埋點為附加 log；orchestrator 僅加計時、不改 DAG 本體 |
| **可逆性** | 🟢 高 — 還原 `.bak` + 刪 script |
| **驗收 grep 條件** | `grep -nE "performance_metric\|pipeline_finished\|rag_finished\|phases_breakdown" pipeline_core.py pipelines/orchestrator.py` # 期望：有命中 |
| **依賴關係** | C4 |
| **具體實作細節** | 1. `.bak` 備份。2. **A 軌 `pipeline_core.py`**（stage 迴圈 L416/L427）：每 stage 結束 `logger.info(..., extra={"extra_fields": {"event":"performance_metric","paper_id":..,"owner_id":..,"doc_type":..,"phase":<群組映射 P1-P4>,"stage":<stage 名>,"duration_seconds":<float>}})`（對齊 logging SOP `extra_fields`+`event`，數值 float 不加「秒」）；`reading_ready` 後印 `pipeline_finished`（含 `phases_breakdown`：各 phase 下原子子階段 breakdown）；RAG stage 以 `rag_finished`（含 `rag_status`）獨立印。3. **B 軌 `pipelines/orchestrator.py`**（`run()` 迴圈、**附加式**）：每 Phase（直接用 `PhaseEnum` P1–P4）結束印同 schema `performance_metric`（phase=正式 P1-P4、stage=phase 內子步驟名）；**不改 DAG 推進/合約驗證/Strategy 介面本體**（§7）。4. **`scripts/analyze_performance.py`**（零外部依賴）：流式逐行解析 `logs/pipeline.log` JSON，聚合各 doc_type 平均耗時 + 各 (phase,stage) 樣本數/平均/最大/標準差 + P4 `rag_finished` 獨立統計，輸出 ASCII 報表；支援 `--help`/`--log <path>`。5. 追加 `test_performance_metric_phase_keyed`（驗 phase+stage 二維鍵、`pipeline_finished` 產 `phases_breakdown`、P4 走獨立 `rag_finished` 不併主鏈）。6. **保持 orchestrator 既有 20 pytest 全綠**。7. logging SOP 核查（`logger.error` exc_info=True；無 traceback 拼接）。8. 產 C5 執行報告（baton/）。 |

### C6 — Checkout / 收官歸檔（一次性 Traceability 交接）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` baton/ plan_v2 → `plans/` + tasks_v3 → `tasks/` + C1–C6 全部 `_執行.md` → `executions/` + `git add`；修改 `.claude-logs/TODO.md` |
| **安全性** | 🟢 高 — 純文件搬移與版控 |
| **可逆性** | 🟢 高 — `git rm --cached` + `mv` 回 baton/ |
| **驗收 grep 條件** | `ls .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/ \| grep API-PERF`（齊全）；`ls .claude-logs/baton/ \| grep -c API-PERF` # 期望：0 |
| **依賴關係** | C1–C5（全部報告已產於 baton/） |
| **具體實作細節** | 1. 先產 `baton/2026-06-03_API-PERF_C6_執行.md`（Conformance + 歸檔清單 + diff stat）。2. **一次性歸檔**（WORKFLOW_SOP §3 收官歸檔鐵律）：`mv` plan_v2 baton→`plans/`（保留 `_v2`）；`mv` tasks_v3 baton→`tasks/`（保留 `_v3`）；`mv` C1/C2/C3/C4/C5/C6 `_執行.md` baton→`executions/`。3. `git add` 上述正式檔 + 全部業務代碼改動（db.py/web_server.py/ai_core.py/rag_retriever.py/paper_manager.py/pipeline_core.py/orchestrator.py/settings.py/pdf_processor.py）+ `scripts/analyze_performance.py` + `tests/test_api_performance_and_robustness.py` + 全部 `.bak` + prompts/INDEX + TODO（**git add 明確列檔、嚴禁 `git add -A`、排除範圍外既有未提交變動**）。4. **更新 TODO.md**：API-PERF 移入 ✅ 已完成表（Hash 待 baron 回填）+ 刪 active 條目 + 索引標 ✅ + 歷史 Hash 自癒。5. 驗收 baton/ 無 API-PERF 殘留。6. **嚴禁** `git commit`/`push`（CLAUDE.md §1.3）。 |

---

## §9 Open Questions

無。（plan v2 §7 之 3 項——Nice Windows soft-fail / LRU 配 `gc.collect()` / `phase` 先行期暫映射——皆已標推薦答案；本 tasks 階段不另增規劃層問題。唯 C5 觸碰 `orchestrator.py` 之附加埋點授權，已於 §5 風險列明，C5 執行前由 baron 最終確認。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 API-PERF 的 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 `baton/` → `executions/` C1–C6 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改既有檢索演算法/API 簽名/路徑防逃逸/PIPE 重構本體；嚴禁自動 git commit/push；C1–C5 報告與 plan/tasks 嚴禁移動、唯 C6 收官一次性搬移；修改既有檔案前 `.bak` |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；U1–U7 規格唯一源在 plan v2 §2；PIPE 重構本體唯一源在 PIPE plan |

### §99.2 Revision 歷程

- v3 (2026-06-03)：依 plan v2 §2（U1–U7）拆 6 Commit——C1 U6 DB 池 / C2 U4 流式上傳+U5 真實 IP / C3 U3 LRU 快取 / C4 U1 Semaphore+U2 nice / C5 U7 (phase,stage) 埋點+CLI / **C6 單一收官 Checkout**；對齊已落地 PIPE-CORE（U1 守 Orchestrator.run+A 軌 run_pipeline、U7 埋點對齊 PhaseEnum P1-P4 + Orchestrator 迴圈）與 PIPE-SCAFFOLD（雙軌派發點）；**時序修正**（對齊 baron 07:01 指令）：廢除初稿「C1 提前搬 plan」雙 Checkout，改為 C1–C5 全留 baton、唯 C6 一次性搬 plan+tasks+全部報告；不給 commit 建議；各實作 Commit 修改既有檔前 `.bak`；§5 標註業務代碼變動與 orchestrator 附加埋點授權提示。
