# 2026-05-23 — logging-refactor 評估報告 v3（2 致命陷阱 + 2 優化）

> **收到時間**：2026-05-23（UTC+8）
> **任務代號**：logging-refactor（評估補強 v3）
> **觸發 commit**：無
> **相關產出檔案**：`.claude-logs/2026-05-23_logging_refactor_可行性評估.md`（覆寫）
> **觸發情境**：baron 在補強 4 點後、再提 4 點建議——其中 2 個是 🔴 致命陷阱（不修就 100% 崩潰）、2 個是架構優化

---

## 完整提示詞

```
請更新 .claude-logs/2026-05-23_logging_refactor_可行性評估.md、納入 baron 提供的 4 點建議：
2 個致命陷阱修正（必納入）+ 2 個架構優化建議（評估後納入）。
直接覆寫既有評估報告（不新建版本號）、TODO 不動、業務代碼不動。

致命陷阱 1: ConsoleFormatter 觸發 AttributeError
  - Python LogRecord 預置屬性無 asctime
  - asctime 只在 Formatter 內 usesTime() 為 True 時動態 setattr
  - 若 ConsoleFormatter.format() 第一行就 record.asctime、立即崩潰
  - 修正：format() 起始顯式 record.asctime = self.formatTime(record, self.datefmt)

致命陷阱 2: Uvicorn 啟動洗掉自訂日誌
  - uvicorn.run 預設 log_config=LOGGING_CONFIG
  - 該 dict 內 dictConfig 載入時覆蓋 root logger handler list
  - setup_logging() 配置失效
  - 修正：uvicorn.run(app, ..., log_config=None)

建議 1: JSONFormatter exception 極限安全防禦
  - record.exc_info 可能為 (None, None, None)
  - 直接 exc_type.__name__ 拋 AttributeError
  - 修正：if record.exc_info and any(record.exc_info): + 每欄位 None check

建議 2: 第三方 Logger 降噪支援動態 DEBUG 覆寫
  - hardcode WARNING 擋住 DEBUG mode SQL 細節
  - 修正：target_level = min(logging.WARNING, root_logger.level)
  - min 取數值小者（DEBUG=10 < WARNING=30）= 取較詳細 level

評估報告變動：TL;DR v3 標記 + §4 改寫 ConsoleFormatter / JSONFormatter / 加 Uvicorn log_config / 改第三方 logger 動態降噪 +
§5 風險表加 4 行（含 2 個 🔴 致命）+ §8 Q16-Q19 + 附錄新增「致命陷阱 + 架構優化納入對照表」

完成後不 commit、不 push。
```

---

## 執行結果摘要

- ✅ 完成狀態：評估報告覆寫、4 點建議全納入
- grep 證據：`web_server.py:907 uvicorn.run(..., reload=False, log_level="warning", access_log=False)` — **無 log_config=None**（陷阱 2 真實）
- 既有 Q1-Q15 → 新增 Q16-Q19
- 工時更新：LOGGING-1 ~4h → ~4h+5min（陷阱 1+2 修正極小）、LOGGING-2 ~2.5h → ~2.5h+10min（exception 安全防衛）
- 整體結論不變：🟡 部分採納
