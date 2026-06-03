# [API-PERF] API 技術審計與效能防呆優化 plan

> **任務編碼**：API-PERF
> **執行日期**：2026-06-01
> **工作流類別**：BE-Refactor（包含 FE-Refactor 混合）
> **狀態**：🔵 plan 中
> **PIPE 定位**：基建前置（先於 PIPE 大改版落地），對齊 PIPE plan §2 U11「API-PERF（輕度修改）」

---

> 本計畫目的在於定義 Mad Professor 專案 API 接口的技術審計、安全防禦與極限高負載防呆規格。預期成果為實作高密度文檔處理的並發排隊信號量、子進程 CPU 優先級控制、動態 LRU 向量庫快取、流式大檔案上傳、真實 IP 獲取與 SQLite SQLAlchemy 連接池優化，並提供結構化耗時統計埋點與輕量日誌分析工具。本計畫為 PIPE 大改版的**基建前置**：信號量／LRU／流式上傳／連接池為新架構共用底座先行落地；監控埋點以**四 Phase 及內部原子子階段**為計時單元，前向相容 PIPE Orchestrator。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：高密度 PDF 上傳與 RAG 併發可能引發 Event Loop 奪取與 GIL 阻塞、大檔上傳 RAM 溢出引發 OOM 容器崩潰、SQLite 併發寫鎖造成 `database is locked` 錯誤、以及 FAISS 向量庫無上限 preload 導致的內存消耗枯竭。在 Docker/反向代理環境中，若直接獲取客戶端 IP 容易因解析錯誤而鎖死全網閘道。
- **解法**：
  1. 實施內存 `asyncio.Semaphore` 限制系統 Pipeline 並發執行數（並發閥門）。
  2. 於背景 PDF 解析子進程（如 MinerU 轉檔）啟動時，將子進程之 OS `nice` 值設為最低優先級。
  3. 廢除 lifespan preload，改為動態 Lazy Load，並為向量庫與 RAG cache 配備 LRU 快取機制。
  4. 將大檔案一次性 `read()` 改為 1MB 分塊流式寫入磁碟。
  5. 登入校驗優先解析 `X-Forwarded-For` 標頭以精確識別真實 IP。
  6. 優化 SQLAlchemy 與 SQLite 連接參數，配置 30 秒 busy_timeout 與 QueuePool。
  7. 處理耗時埋點以 **(phase, stage) 二維鍵**結構化記錄，計時單元對齊 PIPE 四 Phase 及內部原子子階段；提供無外部依賴之 CLI 分析工具 `scripts/analyze_performance.py`。
- **影響**：修改 `web_server.py`、`pipeline_core.py`、`ai_core.py`、`db.py`，新增性能監控腳本，無資料庫 Schema 變動，無既有 API 路由簽名變更。**與 PIPE 對齊**：U1 PIPELINE_SEMAPHORE 為 PIPE 廢除 QUEUE-1 Thread-level 避讓的並發底座；U7 監控埋點以 (phase, stage) 鍵設計，API-PERF 先行落地於現行 11-stage（phase 暫映射）、PIPE 重構後由 Orchestrator 以 P1–P4 + 原子子階段填入，零改埋點介面。

---

## §2 目標規格

### U1. 併發信號量任務隊列 (PIPELINE_SEMAPHORE)
*   **規格**：
    *   全系統同時運行的 Pipeline 運算任務數上限為 1（或由配置項指定），多餘的 Pipeline 任務必須進入內存佇列安全排隊。
    *   當任務排隊時，SSE 狀態查詢接口必須能夠正確推送 `queued` 進度狀態（`{"stage": "queue", "stage_name": "等待佇列中...（排隊中）", "progress": 0}`）。
    *   當前一個任務執行完成（或出錯終止）釋放信號量時，排隊中的下一個任務必須自動獲取許可並開始執行。
    *   **PIPE 對齊**：本信號量為 PIPE plan §2 U11「QUEUE-1 重構性廢除」的並發底座——配合 Early Emit 與 RAG 異步化後，取代 QUEUE-1 的 Thread-level 協同避讓機制（QUEUE-1 之廢除由 PIPE 收官執行，本計畫僅提供底座）。

### U2. 背景進程 OS 優先級控制 (Nice / Priority Control)
*   **規格**：
    *   在啟動背景文檔解析子進程（如調用 MinerU 轉檔的外部 CLI / Python 行程）時，系統必須將其 OS 的 `nice` 值設為最高（在 Linux/macOS 下代表最低 CPU 優先級，即 `Nice 19`）。
    *   即使背景解析任務將 CPU 佔滿，Web API 的 Event Loop 依然擁有絕對優先調度權，保持 API 反應延遲在毫秒級。

### U3. 向量庫與 RAG 快取動態 LRU 機制 (LRU Cache)
*   **規格**：
    *   **完全廢除啟動時載入所有 Done 論文的預載機制 (lifespan preload)**。
    *   改為 **按需加載 (Lazy Load)**：只有當使用者進入某篇論文並發起 RAG 問答或載入內容時，系統才動態從磁碟加載該論文的 FAISS 向量庫與 RAG tree cache 到記憶體。
    *   記憶體中同時加載活躍向量庫與 RAG cache 的上限各為 **5 個**。
    *   當加載新論文導致超過此上限時，系統必須自動釋放（`pop`）最久未使用（LRU）的論文向量與快取記憶體。

### U4. 大檔案上傳流式分塊寫入 (Streaming Write)
*   **規格**：
    *   `POST /api/papers/upload` 接口在讀取上傳檔案時，嚴禁一次性將整份檔案 `await file.read()` 加載至 RAM。
    *   必須採用 **1MB 流式分塊 (chunk-by-chunk)** 讀寫機制，每次僅讀取 1MB 緩衝區並直接 write 入磁碟臨時檔，將上傳時的內存開銷穩定在常數 (< 10MB)。
    *   檔案大小上限維持 100MB，超過時必須立刻截斷並返回 413 狀態碼；魔術位元組 `%PDF` 必須於首個 1MB 分塊讀入時立刻進行頭部校驗，非 PDF 立即中斷並返回 415 狀態碼。

### U5. 真實 IP 解析防閘道鎖死 (Real IP Middleware)
*   **規格**：
    *   在 `POST /login` 接口中，獲取客戶端 IP 時必須優先解析 `X-Forwarded-For` 標頭以獲取真實的 client IP，防範 Docker/Nginx/GCP Load Balancer 反向代理造成的 IP 混淆。
    *   當且僅當無 `X-Forwarded-For` 標頭時，才降級採用 `request.client.host`。
    *   此舉必須確保惡意用戶的密碼暴力破解僅會鎖死其專屬實體真實 IP，絕不影響反向代理網關 IP，防範全伺服器用戶集體登入失敗。

### U6. 數據庫併發池與 SQLite 防鎖死配置
*   **規格**：
    *   `db.py` 中 SQLite 連線的 `busy_timeout` 設定值必須由目前的 5000 毫秒調升至 **30000 毫秒 (30 秒)**，以包容高密度的併發寫鎖等待。
    *   SQLAlchemy 的 `create_engine` 必須正確配備併發連接池（如 `QueuePool`），設定合理池大小（如 `pool_size=5`）與最大溢出數（`max_overflow=10`），且開啟 `pool_pre_ping=True`。

### U7. 結構化處理耗時監控埋點與 CLI 分析工具（四 Phase 對齊）
*   **規格**：
    *   每個原子階段執行結束時，必須列印 event 為 `performance_metric` 的結構化 JSON 日誌，**計時鍵採 (phase, stage) 二維結構**，對齊 PIPE 四 Phase 及其內部原子子階段：
        `{"timestamp": "ISO-8601", "level": "INFO", "event": "performance_metric", "paper_id": "str", "owner_id": int, "doc_type": "str", "phase": "P1|P2|P3|P4", "stage": "str", "duration_seconds": float}`
    *   **前向相容**：API-PERF 先行落地於現行 11-stage 時，`phase` 欄位暫以現行 stage 群組映射填入；PIPE 重構後由 Orchestrator 以正式 P1–P4 + 原子子階段名填入，**埋點介面與 metric schema 零改動**。
    *   主鏈（P1–P3）全部完成達 `reading_ready` 時，必須列印 event 為 `pipeline_finished` 的全局彙總 JSON 日誌，包含成功狀態與**各 Phase 耗時細分（`phases_breakdown`，每 Phase 下含原子子階段 breakdown）**。
    *   **P4 異步 RAG 獨立記錄**：因 PIPE U6 將 RAG 移為非同步背景任務，其耗時必須以獨立 event `rag_finished` 記錄（含 `rag_status: ready|rag_failed`），**不阻塞、不併入主鏈 `pipeline_finished`**。
    *   必須提供一個獨立且無任何外部第三方庫依賴之 Python 監控腳本 `scripts/analyze_performance.py`。
    *   該腳本必須能流式解析 `logs/pipeline.log` 中的 JSON 行，並輸出包含各文件類型平均處理耗時、**各 Phase 與原子子階段效能剖析**（包含樣本數、平均耗時、最大耗時、標準差）、以及 P4 異步 RAG 獨立耗時統計的 ASCII 統計報表。

---

## §3 現況與證據

本專案與 API 效能防呆與監控相關的現有程式碼邏輯與關鍵調用鏈如下：

- **`web_server.py`**：
  - `upload_paper L448`：一次性 `await file.read()` 讀取整個檔案到記憶體，若上傳多個大 PDF 容易引發 OOM（另 L997 主題上傳同 pattern）。
  - `login L352`：直接獲取 `ip = request.client.host if request.client else "unknown"` 用於鎖定嘗試次數，在 Docker 或負載均衡器代理環境中會鎖死網關。
  - `lifespan L220`：在 server 啟動時直接調用 `paper_manager.preload_vector_stores(OUTPUT_DIR, ai_core)` 遍歷載入全部 Done 的向量庫。
- **`paper_manager.py`**：
  - `preload_vector_stores L429`：從 DB 查詢所有 `status='done'` 的 paper，並一口氣將其載入內存至 `ai_core` 中。
- **`ai_core.py`**：
  - `__init__`：宣告 `self._paper_cache` 快取，無容量限制與過期釋放機制。
  - `load_paper_cache`：讀取 RAG tree JSON 並無限載入到記憶體快取。
- **`rag_retriever.py`**：
  - `__init__`：宣告 `self.vector_stores: Dict[Tuple[int, str], FAISS]`，僅有動態加載，無自動 pop 釋放機制。
- **`pipeline_core.py`**：
  - `process L211`：主處理流程；stage 迴圈於 L416 `[stage] {pid} {stage} 開始`、L427 `[stage] {pid} {stage} 完成 耗時=...` 僅以文字 Logger 列印，缺少高價值的結構化 JSON 效能數據埋點，亦無 phase 維度。
- **`db.py`**：
  - `create_engine L28` / `PRAGMA busy_timeout=5000 L49`：現行連線參數，待升 30 秒 busy_timeout 與 QueuePool。

### §3.1 grep 鋼鐵證據

```bash
# 1. web_server.py 大檔案 read 讀取點
grep -n "await file.read()" web_server.py
# 輸出：448:        content = await file.read()
#       997:        content = await file.read()

# 2. web_server.py 客戶端 IP 獲取點
grep -n "request.client.host" web_server.py
# 輸出：352:        ip = request.client.host if request.client else "unknown"

# 3. lifespan preload 寫法（定義端 + 調用端）
grep -n "def preload_vector_stores" paper_manager.py
# 輸出：429: def preload_vector_stores(output_dir, ai_core) -> None:
grep -n "preload_vector_stores" web_server.py
# 輸出：220:        paper_manager.preload_vector_stores(OUTPUT_DIR, ai_core)

# 4. pipeline_core stage 迴圈現行純文字埋點（待升結構化 (phase, stage)）
grep -nE "\[stage\] .*開始|\[stage\] .*完成 耗時" pipeline_core.py
# 輸出：416:    self.logger.info(f"[stage] {pid} {stage} 開始")
#       427:        f"[stage] {pid} {stage} 完成 耗時={time.time() - _stage_t0:.2f}s"

# 5. db.py 現行 busy_timeout
grep -n "busy_timeout" db.py
# 輸出：49:        cursor.execute("PRAGMA busy_timeout=5000")
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次優化中嚴禁任何改動：**

- [ ] `rag_retriever.py` 既有的 RAG 核心檢索邏輯 `retrieve()`（必須維持 RAG 與 Embedding 檢索的正確性與閾值）。
- [ ] 既有 API 的路由與功能簽名必須 100% 保持相容，不可破壞前端調用。
- [ ] 既有的 `/api/papers/{paper_id}/images/{filename}` 接口中的實體路徑防逃逸穿越 `relative_to` 邊界校驗防線。
- [ ] `_normalize_tag` 全域小寫與標籤單一真理源邏輯。
- [ ] **PIPE 四 Phase 切分／三層解耦／策略管線本體**：本計畫僅做基建底座與監控埋點介面，嚴禁觸碰 PIPE 的 Orchestrator/Context/Stage 重構本身（屬 PIPE plan 範疇，避免兩計畫互踩）。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| plan 治理範本 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／SOP 核查 | `.claude-logs/ref/WORKFLOW_SOP.md §3 §5 §6` |
| 專案進度治理框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| PipelineCore 大改版（API-PERF 基建前置定位 U11／四 Phase 計時單元／Async RAG U6） | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v1.md §2 U6 U10 U11` |
| logging / database 程式碼級 SOP（BE-Refactor 強制） | `.claude-logs/sop/2026-05-23_logging_SOP_手冊.md` / `database_SOP_手冊.md` |
| 專案系統設計規範 | `mad-professor_design_spec.md` |
| SQLite WAL 連接規範 | `db.py L28 L49` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**：
  在 `tests/` 下新增一個測試檔 `tests/test_api_performance_and_robustness.py`：
  *   `test_upload_file_streaming_constant_ram`：模擬大檔案上傳，驗證記憶體是否保持常數級消耗，且魔術字節與大小上限過濾生效。
  *   `test_concurrency_semaphore_queue`：並發呼叫處理任務，驗證第二個任務是否自動進入 queued 狀態且前一個任務釋放後順序啟動。
  *   `test_lru_vector_store_eviction`：動態加載超過 5 個不同的向量庫，驗證最久未使用的向量庫是否正確被 `pop` 並從內存中移除。
  *   `test_x_forwarded_for_parsing`：傳入帶有不同 proxy 鏈的 `X-Forwarded-For` 標頭，驗證是否能精確解析出最左側的真實 client IP。
  *   `test_performance_metric_phase_keyed`：驗證 `performance_metric` 事件含 `phase` 與 `stage` 二維鍵、`pipeline_finished` 產出 `phases_breakdown`、P4 RAG 走獨立 `rag_finished` 事件不併入主鏈彙總。

### §6.2 手動端到端（E2E）驗證流程

1.  **分塊流式上傳測試**：
    使用 CLI 工具上傳一個約 80MB 的 PDF 檔案，監控 `web_server` 進程的內存佔用，確認無 RAM 陡增現象，且寫入正常。
2.  **一次性拖入 10 個文獻高載測試**：
    在前端同時選中 10 份論文上傳並一次性點擊確認處理。
    *   觀察 SSE 進度，確認只有 1 個任務顯示 `processing`，其餘 9 個任務皆正確顯示 `queued`（排隊中）。
    *   觀察 CLI logger 輸出，確認 nice 值修改正確，且主網頁端點依舊能夠以毫秒級延遲秒開。
3.  **效能 CLI 分析工具驗證**：
    執行 `python scripts/analyze_performance.py`，確認統計報告中各 **Phase 與原子子階段**的「平均耗時」、「最大耗時」與「標準差」在 ASCII 大屏上完美投射，且 P4 異步 RAG 耗時獨立呈現、排序正確。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Nice 值調整在 Windows 環境下失效問題** | 捕獲 `AttributeError` 或 `OSError` 進行軟降級 (soft-fail) | 在 macOS 和 Linux 容器環境下 Nice 完美支持，但在 Windows 下無此原生系統調用。軟降級能保證系統跨平台相容性。 |
| **LRU 內存回收是否需要配合 GC 顯式回收** | 移除 Dict 鍵後，調用 `gc.collect()` 顯式釋放記憶體 | FAISS 的底層 C++ 內存可能不會在 Python references 歸零時立刻歸還給 OS，加上顯式 GC 可提升單機環境的內存穩定度。 |
| **`performance_metric` 的 `phase` 在 API-PERF 先行期的暫映射策略** | 先行期以現行 stage 群組粗映射 P1–P4，PIPE 落地後由 Orchestrator 覆寫為正式 phase 名 | API-PERF 為基建前置、先於 PIPE 落地，此時尚無正式四 Phase；採暫映射確保埋點 schema 不變，PIPE 重構僅換填值、零改埋點介面，避免二次重工。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 [API-PERF] API 技術審計與效能防呆優化 的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 [API-PERF] tasks / 執行報告；PIPE plan §2 U6 U10 U11 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義 API 效能與基建技術規格；四 Phase 切分／三層解耦／策略管線唯一源在 PIPE plan，本計畫僅提供並發底座與監控埋點介面；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-01)：對齊 PIPE 大改版調整——明確定位為 PIPE「基建前置（輕度修改、先行落地）」；U1 PIPELINE_SEMAPHORE 補述為 PIPE 廢除 QUEUE-1 Thread-level 避讓的並發底座；U7 監控埋點計時單元由「每個 Stage（11-stage）」改為**四 Phase + 原子子階段（(phase, stage) 二維鍵）**，新增 `phases_breakdown` 彙總與 P4 異步 RAG 獨立 `rag_finished` 事件、CLI 報表對齊；§3 行號刷新（`await file.read()` L448、`process` L211 / stage 迴圈 L416 L427、`busy_timeout` L49、lifespan call L220）；§5 補 PIPE / framework / WORKFLOW_SOP / SOP 依據；§4 增列不可踩 PIPE 重構本體之邊界。U2–U6 規格本體不變（基建底座原樣複用）。檔名由 `2026-05-27_API-PERF_API技術審計與效能優化_plan.md` 更名而來。
- v1 (2026-05-27)：依據 template_plan.md 重新改寫與建立，任務代碼命名為 API-PERF，完成 top metadata 整合。
