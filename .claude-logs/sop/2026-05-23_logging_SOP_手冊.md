# Mad Professor 專案 — 日誌編寫標準作業手冊 (Logging SOP)

> **版本**：2026-05-23 (v1)
> **類型**：專案開發規範與技術手冊 (Reference Guide)
> **適用範圍**：所有業務模組開發、CLI 工具開發、背景任務設計、單元測試編寫

本手冊旨在為 Mad Professor 專案建立一套**標準化的日誌編寫規範**。自 `LOGGING-1/2/3` 日誌重構落地後，本專案已擁有統一的雙軌日誌基建（本機 Console / 雲端單行 JSON）與 Trace ID 全鏈路追蹤機制。為了維持此基建的健全度，未來任何開發人員（或 AI 協同開發 Agent）修改或新增程式碼時，**必須嚴格遵守本手冊規範**。

---

## ── 1. 日誌初始化三鐵律 (The Three Golden Rules) ──

### 鐵律一：嚴禁調用 `logging.basicConfig(...)` 或 `logging.config.dictConfig(...)`
* **原因**：調用這些方法會重設或覆蓋已經由 `utils/logging_config.py::setup_logging()` 配置好的 Root Logger 及其 Handlers，導致生產環境 JSON 格式失效、日誌回退為純文字、或重複掛載多倍 Handler。
* **正確做法**：
  * **FastAPI Server 入口**：已在 `web_server.py` 最早期呼叫 `setup_logging()`。
  * **CLI 工具入口**：已在 `tools/regen_rag.py` 的 `__main__` block 內呼叫 `setup_logging()`。
  * **未來新增入口**：直接導入並調用即可，利用其內置的遞增式（Idempotency）防護：
    ```python
    if __name__ == '__main__':
        from utils.logging_config import setup_logging
        setup_logging()
        main()
    ```

### 鐵律二：永遠使用模組級或類別級 Logger 命名空間
* **正確做法**：
  * **模組級 (Module-level)**：在檔案最頂部定義：
    ```python
    import logging
    logger = logging.getLogger(__name__)
    ```
  * **類別級 (Class-level)**：在類別構造函數內定義（便於精確識別階段）：
    ```python
    class MyProcessor:
        def __init__(self):
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    ```

### 鐵律三：第三方 Logger 必須顯式劫持
* **場景**：如果引入了新的第三方庫（如 `httpx`、`langchain`、`starlette` 等），其內部自定義的 Handler 會污染 `stdout`，造成 JSON 與純文字混雜，進而破壞 Loki / ELK 解析。
* **正確做法**：必須在 `utils/logging_config.py` 的 `setup_logging()` 中將其納入劫持列表，清空其 handlers 並設 `propagate=True`，使其統一走 root 輸出。

---

## ── 2. 日誌級別定義與規範 (Log Levels Spec) ──

專案嚴格遵循以下 4 個日誌級別的劃分。**嚴禁隨意調用級別，避免日誌噪聲淹沒業務日誌。**

| 級別 | 適用場景 | 噪聲級別 | 生產環境預設行為 |
|---|---|---|---|
| **`DEBUG`** | 演算法內部迭代細節、資料庫詳細 SQL 執行語句（SQLAlchemy）、LLM 原始提示詞與補全回應、RAG 檢索相似度原始分值。 | 🔴 極高 | 隱藏。僅在顯式指定 `LOG_LEVEL=DEBUG` 時開啟。 |
| **`INFO`** | 服務生命週期事件（啟動/關閉）、論文處理階段完成事件（OCR 完成、翻譯完成、寫入 RAG 完成）、快取命中（Cache Hit）提醒。 | 🟡 中等 | **預設開啟。** 必須保持簡潔、單行。 |
| **`WARNING`** | 可容忍的非致命異常（如 LLM 連線超時已觸發 MODEL-9 彈性重試）、使用者輸入不合法已被 Filter 攔截並安全拒絕。 | 🟢 低 | **預設開啟。** 用於潛在系統健康度診斷。 |
| **`ERROR`** | 導致論文處理中斷的未捕獲例外（如 PDF 損毀無法解析）、外部 API 密鑰失效、資料庫寫入失敗。 | 🟢 極低 | **預設開啟。** 必定附帶 Stacktrace 結構化數據。 |

---

## ── 3. 異常與堆疊追蹤編寫標準 (Exception Logging) ──

當我們在 `try...except` 區塊中捕獲錯誤並希望記錄時，必須保證 Stacktrace 能夠被結構化地捕獲，且**絕不能將多行文字直接拼接在 message 中**（會破壞單行 JSON 解析）。

### ❌ 錯誤寫法
```python
try:
    process_pdf(file)
except Exception as e:
    # 錯誤 1：手動格式化 exception，導致 Loki 無法解析 exception.type
    # 錯誤 2：產生多行字串，日誌代理（promtail）會將其切碎為多行日誌
    logger.error(f"解析 PDF 失敗: {e}\n{traceback.format_exc()}")
```

### ✅ 正確寫法
```python
try:
    process_pdf(file)
except Exception:
    # 正確 1：使用 exc_info=True（或 logger.exception），由 Formatter 自動提取
    # 正確 2：JSONFormatter 會自動將其結構化為子字典：
    #        "exception": {"type": "ValueError", "message": "...", "stacktrace": "..."}
    # 正確 3：json.dumps 會自動將 \n 轉義為 \\n，結果保證為「單行 JSON」，極其安全
    logger.error("解析 PDF 失敗", exc_info=True)
```

---

## ── 4. 結構化擴充欄位標準 (`extra_fields` Spec) ──

當我們需要輸出「機器可分析的效能指標、快取命中率、或特定論文特徵」時，**嚴禁直接拼裝在字串中**。必須使用 `extra_fields`。

### ❌ 錯誤寫法
```python
# 機器無法提取 duration_seconds、cached，無法在 GCP Cloud Monitoring 繪製折線圖
logger.info(f"論文 {paper_id} 翻譯完成，耗時 {duration} 秒，是否使用快取: {is_cached}")
```

### ✅ 正確寫法
```python
# 業務訊息保持精簡，數值化指標封裝在 extra_fields 內
logger.info(
    f"階段 {paper_id} translate 完成",
    extra={
        "extra_fields": {
            "event": "performance_metric",
            "paper_id": paper_id,
            "owner_id": owner_id,
            "doc_type": "academic",
            "stage": "translate",
            "duration_seconds": round(duration, 2),
            "cached": is_cached
        }
    }
)
```
* **注意**：
  * **效能監控事件**：必須指定 `"event": "performance_metric"`，這是本地 `analyze_performance.py` 統計腳本與雲端 Log-based Metrics 篩選的**唯一憑證**。
  * **時間/數值**：時間必須使用 `round(x, 2)` float 保留兩位小數，不要傳遞帶有 "秒" 字樣的字串，便於指標聚合計算。

---

## ── 5. Trace ID 與安全上下文感應 (ContextVars) ──

自 `LOGGING-2` 起，我們定義了全域協程安全的 `trace_context: ContextVar`。

### 5.1 雙保險讀取原則
由於 Formatter 格式化日誌時會調用 `trace_context.get()`，當我們在沒有 HTTP 請求的中間件背景下（例如執行 CLI 腳本或跑 Pytest）記錄日誌時，ContextVar 內部尚未被 `set`，會引發 `LookupError` 拋出，導致日誌丟失。
* **開發鐵律**：任何時候讀取 `trace_context`，**必須**使用 `trace_context.get(None)`（傳入預設值 `None`）進行雙保險防禦！

### 5.2 跨 Thread / Background Task 的傳播原則
* **自動傳播（ async generator / asyncio.to_thread）**：
  * 適用於：SSE Chat Broker 等。
  * 原理：Python 3.9+ 內置 `asyncio.to_thread` 會自動實施 `contextvars.copy_context().run(...)` 語義，**我們不需要做額外處理，trace_id 會自動繼承**。
* **手動傳播（ ThreadPoolExecutor / run_in_executor）**：
  * 適用於：`pipeline_core.py` 耗時長任務等。
  * 原理： thread pool 不會自動傳播 ContextVar。如果未來需要將 trace_id 深入傳播到 `PipelineCore` 內部，必須在進入 executor 前拷貝 Context，並使用 wrapper 運行：
    ```python
    import contextvars
    
    # 1. 拷貝當前協程的上下文
    ctx = contextvars.copy_context()
    
    # 2. 在背景線程池內以該上下文執行函數
    #    這能保證線程池內部 logger.info 依然能印出正確的 trace_id
    loop.run_in_executor(executor, ctx.run, pipeline.process, owner_id, paper_uuid)
    ```

---

## ── 6. 單元測試日誌規範 (Pytest Logging Specs) ──

為了防止編寫單元測試時對系統日誌基建造成永久污染，我們必須遵循以下規範：

1. **嚴禁在測試函數中直接修改 Root Logger 的 handlers。**
2. **重置狀態**：如果測試中需要測試 `setup_logging()` 的格式化行為，必須在測試前與測試後調用 `utils.logging_config::reset_logging()` 重置冪等性狀態，或使用專屬 fixture：
   ```python
   @pytest.fixture
   def clean_logging():
       from utils.logging_config import reset_logging
       reset_logging()
       yield
       reset_logging()
   ```
3. **日誌攔截**：測試業務功能是否印出特定日誌時，優先使用 Pytest 內建的 `caplog` fixture：
   ```python
   def test_my_feature(caplog):
       with caplog.at_level(logging.INFO):
           run_my_business()
       assert "特定步驟完成" in caplog.text
   ```

---

## ── 7. 統一日誌事件規格字典 (Unified Event Schema) ──

為了讓本機 `scripts/analyze_performance.py` 看板分析器與雲端大屏能持續正常解讀，日誌事件規格**絕不允許隨意更改欄位名稱**。

### A. 階段耗時事件 (`event: "performance_metric"`)
```json
{
  "timestamp": "ISO-8601 String",
  "level": "INFO",
  "logger": "...",
  "event": "performance_metric",
  "trace_id": "8 char hex",
  "owner": "Username string or None",
  "paper_id": "Paper UUID string",
  "doc_type": "academic | slides | resume",
  "stage": "pdf2md | md2json | translate | rag | image_caption | md_restore",
  "duration_seconds": 45.28,
  "cached": false
}
```

### B. Pipeline 完工事件 (`event: "pipeline_finished"`)
```json
{
  "timestamp": "ISO-8601 String",
  "level": "INFO",
  "logger": "...",
  "event": "pipeline_finished",
  "trace_id": "8 char hex",
  "owner": "Username string or None",
  "paper_id": "Paper UUID string",
  "doc_type": "academic | slides | resume",
  "total_duration_seconds": 158.45,
  "status": "success | failed",
  "stages_breakdown": {
    "pdf2md": 45.28,
    "translate": 98.50,
    "rag": 11.55
  }
}
```

---
*本手冊由 Mad Professor 專案架構委員會制定。對日誌配置的修改須經評估報告（Implementation Plan）批准後方可執行。*
