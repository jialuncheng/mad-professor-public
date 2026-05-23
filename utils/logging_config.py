"""統一日誌配置（LOGGING-1）。

依據:
- .claude-logs/2026-05-23_logging_refactor_可行性評估.md v4
- §4.3 ConsoleFormatter（v3 陷阱 1 asctime 顯式綁定）
- §4.8 setup_logging + settings env 整合
- §4.9 補強 1：冪等性 _logging_initialized + reset_logging
- §4.10 補強 2：第三方 logger 劫持
- §4.12 補強 4：JSONFormatter Exception 結構化
- §4.13 v3 陷阱 1：ConsoleFormatter.format() 起始 record.asctime 顯式綁定（必修）
- §4.15 v3 建議 1：JSONFormatter exc_info=(None, None, None) any() 安全防衛
- §4.16 v3 建議 2：第三方 logger 動態降噪 min(WARNING, root)
- §4.17 v4 建議 1：SQLAlchemy / Uvicorn 噪聲分流（SQLAlchemy hardcode DEBUG-only / Uvicorn 動態）
- §4.18 v4 建議 2：ContextVar default=None + .get(None) 雙保險
- §4.19 v4 建議 3：JSONFormatter json.dumps default=str 降級
"""
from __future__ import annotations

import json
import logging
import os
import sys
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional


# ─────────────────── ContextVar（v4 建議 2 雙保險之一）───────────────────
# LOGGING-2 ship 後、@app.middleware("http") 才會在每 request 開頭 set
# LOGGING-1 階段保持 None、Formatter 走 `if ctx:` 分支跳過 trace_id 注入
# default=None 防 CLI / pytest / 背景任務無 set 時 .get() 拋 LookupError
trace_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "trace_context", default=None
)


# ─────────────────── Formatters ───────────────────


class JSONFormatter(logging.Formatter):
    """生產環境結構化 JSON 日誌（單行、機器可解析）。

    特性:
    - exc_info 結構化為 {type, message, stacktrace} 三 key dict（補強 4）
    - exc_info=(None, None, None) 安全防衛、any() check（v3 建議 1）
    - ContextVar 雙保險讀取 .get(None)（v4 建議 2）
    - json.dumps default=str 降級防 TypeError（v4 建議 3）
    - extra_fields 支援（提案 L77-79）
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # v4 建議 2：ContextVar 雙保險 .get(None)、永不拋 LookupError
        ctx = trace_context.get(None)
        if ctx:
            log_data.update(ctx)

        # 補強 4 + v3 建議 1：Exception 結構化 + (None, None, None) 安全防衛
        if record.exc_info and any(record.exc_info):
            exc_type, exc_value, _exc_tb = record.exc_info
            log_data["exception"] = {
                "type": exc_type.__name__ if exc_type is not None else None,
                "message": str(exc_value) if exc_value is not None else "",
                "stacktrace": (
                    self.formatException(record.exc_info)
                    if exc_type is not None else None
                ),
            }

        # 支援 logger.info("...", extra={"extra_fields": {...}})
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # v4 建議 3：default=str 降級防禦
        # 遇 datetime / set / Decimal / UUID / Pydantic / SQLAlchemy ORM 等自動 str()
        return json.dumps(log_data, ensure_ascii=False, default=str)


class ConsoleFormatter(logging.Formatter):
    """開發環境彩色終端機格式。

    特性:
    - 🔴 v3 陷阱 1：format() 起始顯式綁定 record.asctime（必修、否則 AttributeError 啟動崩潰）
    - ContextVar 雙保險讀取 .get(None)（v4 建議 2）
    - exc_info any() 防衛（一致性、跟 JSONFormatter 對齊）
    """

    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 綠色
        'WARNING': '\033[33m',   # 黃色
        'ERROR': '\033[31m',     # 紅色
        'CRITICAL': '\033[41m',  # 紅底
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # 🔴 v3 陷阱 1 修正（必修）：LogRecord 預置欄位不含 asctime
        # 必須先顯式綁定、否則下方讀取 record.asctime 立即 AttributeError、服務啟動掛
        record.asctime = self.formatTime(record, self.datefmt)

        color = self.COLORS.get(record.levelname, self.RESET)
        level_space = " " * (8 - len(record.levelname))

        # v4 建議 2：ContextVar 雙保險
        ctx = trace_context.get(None)
        trace_str = (
            f" [trace_id={ctx['trace_id']}]"
            if ctx and "trace_id" in ctx else ""
        )

        msg = (
            f"{color}[{record.levelname}]{level_space}{self.RESET} "
            f"{record.asctime} - \033[35m{record.name}\033[0m - "
            f"{record.getMessage()}{trace_str}"
        )
        # 一致性：跟 JSONFormatter 同樣 any() 防衛
        if record.exc_info and any(record.exc_info):
            msg += f"\n{self.formatException(record.exc_info)}"
        return msg


# ─────────────────── setup_logging（冪等性 + 劫持 + 噪聲分流）───────────────────

# 補強 1：模組級旗標、防 pytest / reload 重複掛 handler
_logging_initialized: bool = False


def setup_logging() -> None:
    """統一初始化 Root Logger + handlers + 第三方劫持。

    冪等性（補強 1）：多次呼叫只有第一次生效；pytest 場景如需重設、顯式呼叫 reset_logging()。

    依 .claude-logs/2026-05-23_logging_refactor_可行性評估.md v4 §4.8-4.18：
    - 依 LOG_FORMAT env 選 Formatter（auto / json / console）
    - stdout streaming 為主軸（12-factor 雲原生）
    - dev 環境保留 RotatingFileHandler hybrid 雙軌（baron 本機 tail -f 工作流）
    - v4 建議 1：SQLAlchemy hardcode DEBUG-only / Uvicorn 動態 min(WARNING, root)
    """
    global _logging_initialized
    if _logging_initialized:
        return

    # 延遲 import 避免循環依賴 + 確保 settings reload 生效
    from settings import (
        LOG_BACKUP_COUNT,
        LOG_DIR,
        LOG_FORMAT,
        LOG_LEVEL,
        LOG_MAX_BYTES,
    )

    # === 1. Formatter 選擇（依 LOG_FORMAT env、Q11）===
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if LOG_FORMAT == "json":
        formatter: logging.Formatter = JSONFormatter()
    elif LOG_FORMAT == "console":
        formatter = ConsoleFormatter()
    else:  # auto
        formatter = (
            JSONFormatter() if environment == "production"
            else ConsoleFormatter()
        )

    # === 2. Root Logger 配置 ===
    root_logger = logging.getLogger()
    level_value = getattr(logging, LOG_LEVEL, logging.INFO)
    root_logger.setLevel(level_value)

    # 清掉既有 handler（補強 1 防呆、確保重設後乾淨）
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # === 3. stdout Handler（雲原生 12-factor 主軌）===
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(level_value)
    root_logger.addHandler(stdout_handler)

    # === 4. Hybrid: dev 環境保留 file logging（Q3、Q5）===
    if environment != "production":
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                LOG_DIR / "pipeline.log",
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
                encoding='utf-8',
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level_value)
            root_logger.addHandler(file_handler)
        except OSError:
            # LOG_DIR 不可寫（如 read-only filesystem）、降級為純 stdout
            root_logger.warning(
                f"[logging_config] LOG_DIR={LOG_DIR} 不可寫、降級為純 stdout"
            )

    # === 5. v4 建議 1：第三方 logger 噪聲分流 ===
    # 高噪聲查詢日誌：SQLAlchemy 只在 DEBUG mode 才開（防 INFO 模式 SQL spam）
    sqlalchemy_loggers = ("sqlalchemy.engine",)
    sqlalchemy_level = (
        logging.DEBUG
        if root_logger.level == logging.DEBUG
        else logging.WARNING
    )

    # 生命週期日誌：Uvicorn 動態跟隨 root（INFO 時能看到啟動 / 路由錯誤）
    uvicorn_loggers = ("uvicorn", "uvicorn.access", "uvicorn.error")
    uvicorn_level = min(logging.WARNING, root_logger.level)

    for name in sqlalchemy_loggers:
        lg = logging.getLogger(name)
        for h in lg.handlers[:]:
            lg.removeHandler(h)
        lg.propagate = True
        lg.setLevel(sqlalchemy_level)

    for name in uvicorn_loggers:
        lg = logging.getLogger(name)
        for h in lg.handlers[:]:
            lg.removeHandler(h)
        lg.propagate = True
        lg.setLevel(uvicorn_level)

    _logging_initialized = True


def reset_logging() -> None:
    """強制重設冪等性旗標 + 清 root handlers。

    用途：pytest fixture 需要重新 setup_logging 時、顯式呼叫此 helper。
    其他場景不應使用。
    """
    global _logging_initialized
    _logging_initialized = False
    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
