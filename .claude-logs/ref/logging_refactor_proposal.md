# Mad Professor: 容器化與雲原生日誌架構重構建議書

在將專案打包成 Docker 容器，甚至部署到雲原生環境（如 Kubernetes、AWS ECS、GCP Cloud Run）時，**日誌（Logging）架構**的設計將直接決定系統的可觀測性（Observability）、排障效率以及系統效能。

本建議書依據 **12-Factor App（雲原生開發要素）** 的日誌標準，針對本專案目前的日誌設計進行剖析，並提出一套生產級別（Production-ready）的日誌重構方案。

---

## ── 當前日誌架構的 4 大瓶頸 ──

目前專案的日誌設計在 `web_server.py` 的 `_setup_logging()` 中，使用 `RotatingFileHandler` 將日誌分流寫入本機磁碟的 `logs/pipeline.log` 與 `logs/chat.log`。這種設計在單機環境下十分直覺，但一旦進入 Docker 容器化環境，將面臨以下致命問題：

### 1. 容器臨時磁碟限制 (Ephemeral Storage)
Docker 容器的硬碟空間是「臨時且易逝的」。一旦容器因為發生異常重啟、或者部署新版映像檔（Image）而被銷毀，**所有保存在容器內部 `logs/` 目錄的日誌將會永久遺失**，無法進行事後排障（Post-mortem Analysis）。

### 2. 多實例日誌割裂 (Distributed Logging Gap)
當系統啟動多個容器副本（Replica）進行負載平衡時，每個容器只會記錄自己身上的日誌。開發人員無法獲得全域的系統視角，除非逐一 SSH 登入容器（這在生產環境是禁止的），否則根本無法追蹤跨容器的完整交易路徑。

### 3. 文字排版難以機器解析 (Plaintext vs. Structured Logs)
目前的日誌格式為純文字（Plaintext）：
```text
2026-05-22 11:45:33 - pipeline_core - INFO - 開始處理 PDF...
```
當日誌量極大並被收集到中央日誌平台（如 ELK, Grafana Loki, CloudWatch）時，純文字極難被搜尋、過濾或建立警報監控。例如，很難快速篩選出「所有針對特定 `owner_id` 且耗時大於 5 秒的 RAG 檢索請求」。

### 4. 併發請求的交錯干擾 (Context Trace Loss)
當多個使用者併發上傳論文並進行對話時，多個執行緒/協程的日誌會交叉寫入同一個目的地。在沒有「追蹤識別碼 (Trace ID)」的情況下，將無法把散落各處的日誌拼湊回同一個請求的完整執行脈絡中。

---

## ── 雲原生日誌改版藍圖 (The 12-Factor Logging) ──

雲原生架構的核心原則：**「應用程式本身不負責管理日誌檔案，而是將日誌視為事件串流（Event Streams）。」**

### 重構核心三箭：
1. **日誌輸出流化 (Streams to Stdout/Stderr)**：徹底拔除 `RotatingFileHandler` 與本機日誌目錄。所有日誌一律輸出至 `sys.stdout` (標準輸出) 與 `sys.stderr` (標準錯誤)。由容器引擎（如 Docker Daemon, K8s Caelum）負責捕捉並轉發至中央日誌中心。
2. **結構化 JSON 格式化 (Structured JSON Logging)**：在生產環境（Production）中，將日誌一律序列化為單行 JSON 字串，將時間、層級、模組、Trace ID、甚至錯誤堆疊（Traceback）作為獨立的 JSON 欄位輸出。
3. **上下文感知與追蹤 (Contextual Trace ID Middleware)**：引入 FastAPI Middleware 與 `contextvars`，自動為每個傳入的 HTTP 請求生成全域唯一的 `trace_id`，並在所有的 `logger` 呼叫中隱式注入，實現端到端的調用鏈追蹤。

---

## ── 具體改版程式碼設計 (Detailed Implementation Plan) ──

我們建議在專案中新增/修改為獨立的日誌管理模組 [`utils/logging_config.py`](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/utils/logging_config.py)，其設計如下：

### 1. 【新增】結構化日誌核心 [`utils/logging_config.py`](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/utils/logging_config.py)

```python
import json
import logging
import sys
import time
from contextvars import ContextVar
from typing import Any, Dict

import settings

# 定義執行緒/協程安全的上下文變數，用以存儲 Trace ID 與調用上下文
trace_context: ContextVar[Dict[str, Any]] = ContextVar("trace_context", default={})

class JSONFormatter(logging.Formatter):
    """將日誌格式化為單行 JSON 格式，方便 ELK / Loki 機器解析"""
    def format(self, record: logging.LogRecord) -> str:
        # 基本日誌元數據
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # 自動注入 ContextVars 中的 Trace 上下文 (如 trace_id, owner_id)
        ctx = trace_context.get()
        if ctx:
            log_data.update(ctx)

        # 若有 Exception，自動將 Traceback 格式化為 JSON 欄位而非多行 text
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 支援 extra 傳入的自訂欄位
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)

    def formatTime(self, record: logging.LogRecord, datefmt: str = None) -> str:
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            # 使用 ISO 8601 標準格式
            t = time.strftime("%Y-%m-%dT%H:%M:%S", ct)
            s = f"{t}.{int(record.msecs):03d}Z"
        return s


class ConsoleFormatter(logging.Formatter):
    """開發環境（Local Development）專用：彩色、易讀的終端機排版"""
    # ANSI Color Codes
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 綠色
        'WARNING': '\033[33m',   # 黃色
        'ERROR': '\033[31m',     # 紅色
        'CRITICAL': '\033[41m',  # 紅底
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        level_space = " " * (8 - len(record.levelname))
        ctx = trace_context.get()
        trace_str = f" [trace_id={ctx['trace_id']}]" if ctx and "trace_id" in ctx else ""
        
        # 建立美化的本機排版
        msg = (
            f"{color}[{record.levelname}]{level_space}{self.RESET} "
            f"{record.asctime} - \033[35m{record.name}\033[0m - "
            f"{record.getMessage()}{trace_str}"
        )
        if record.exc_info:
            msg += f"\n{self.formatException(record.exc_info)}"
        return msg


def setup_logging():
    """全域日誌初始化入口"""
    root_logger = logging.getLogger()
    
    # 清理舊的 Handlers
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # 決定使用 JSON 還是彩色 Console 格式
    if settings.ENVIRONMENT == "production":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root_logger.setLevel(logging.INFO)  # 生產環境預設 INFO
    else:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ConsoleFormatter()
        formatter.datefmt = "%Y-%m-%d %H:%M:%S"
        handler.setFormatter(formatter)
        root_logger.setLevel(logging.DEBUG) # 開發環境預設 DEBUG

    root_logger.addHandler(handler)

    # 針對一些噪音較高的第三方庫（如 uvicorn / sqlalchemy）進行層級調整
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

---

### 2. 【修改】FastAPI 全域 Trace 中間件 [`web_server.py`](file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/web_server.py)

在 FastAPI 核心中加入 Trace Middleware，自動為每個請求上色（標記 `trace_id`）：

```python
import uuid
from fastapi import Request
from utils.logging_config import trace_context, setup_logging

# 在 Web Server 啟動最早期執行日誌初始化，替換原先的 _setup_logging()
setup_logging()

@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    # 1. 嘗試從 Header 讀取前端或 API Gateway 傳入的 Trace ID，無則自動生成
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    
    # 2. 解析當前使用者 Context
    owner_id = None
    # （可選）從 session 或是 JWT token 內嘗試解析出 owner_id
    if "user" in request.session:
        owner_id = request.session["user"].get("id")

    # 3. 綁定上下文至當前協程 ContextVar
    token = trace_context.set({
        "trace_id": trace_id,
        "owner_id": owner_id,
        "path": request.url.path,
        "method": request.method
    })

    try:
        response = await call_next(request)
        # 將 Trace ID 附在 Response Header，方便前端與客服對齊問題
        response.headers["X-Trace-ID"] = trace_id
        return response
    finally:
        # 4. 請求結束後清理 ContextVar，避免污染執行緒池
        trace_context.reset(token)
```

---

### 3. 【修改】在 Pipeline 背景處理中傳遞 Trace Context

對於 FastAPI 的背景任務（Background Tasks），協程上下文會在新執行緒中丟失。我們需要在背景 Pipeline 啟動時，顯式將 `trace_id` 傳入並綁定，以確保長任務（PDF 解析）日誌不失聯：

```python
# pipeline_core.py 或是 web_server.py 的背景啟動點

def run_pipeline_in_background(owner_id: int, paper_uuid: str, trace_id: str):
    """非同步背景任務包裝器"""
    # 綁定原請求的 trace_id 至背景執行緒的 ContextVar 中
    token = trace_context.set({
        "trace_id": trace_id,
        "owner_id": owner_id,
        "paper_uuid": paper_uuid,
        "job": "pdf_pipeline"
    })
    try:
        pipeline = PipelineCore()
        pipeline.process(owner_id, paper_uuid)
    finally:
        trace_context.reset(token)
```

---

## ── 重構後帶來的好處 (Business & Dev Benefits) ──

### 1. 機器友好的日誌格式 (Production)
在 Docker 生產環境中，系統輸出的日誌將自動轉化為標準的單行 JSON，完全符合雲端排障與搜尋需求：
```json
{
  "timestamp": "2026-05-22T11:45:33.123Z",
  "level": "INFO",
  "logger": "pipeline_core",
  "message": "開始執行第 4 階段：段落層級 RAG 樹狀建構",
  "trace_id": "8bfa2e41-6925-4c07-827d-94c6f3796d11",
  "owner_id": 42,
  "paper_uuid": "paper-992ad34b",
  "job": "pdf_pipeline"
}
```

### 2. 人類友好的日誌格式 (Development)
在本機開發環境（`ENVIRONMENT=development`）中，終端機會以色彩斑斕、層級分明的 Console 格式渲染，提升開發調試體驗。

### 3. 動態日誌分流與動態過濾
不再需要透過 Python 程式碼複雜地將日誌分流到 `pipeline.log` 或 `chat.log`。
*   在中央日誌平台（如 Kibana/Loki）中，您只需輸入：`logger: "AI_professor_chat"` 即可秒級篩選出所有對話日誌。
*   輸入 `trace_id: "8bfa2e41..."` 即可看到這個請求從**「FastAPI 接收 -> PDF 上傳 -> 呼叫 MinerU -> 雙語翻譯 -> 向量化 -> RAG 檢索 -> AI 對答輸出」**的全部呼叫軌跡，實現**一鍵全鏈路排障**！
