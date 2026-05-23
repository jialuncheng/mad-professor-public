# 2026-05-23 — logging-refactor 評估報告 v4（3 生產健壯性建議）

> **收到時間**：2026-05-23（UTC+8）
> **任務代號**：logging-refactor（評估補強 v4）
> **觸發 commit**：無
> **相關產出檔案**：`.claude-logs/2026-05-23_logging_refactor_可行性評估.md`（覆寫 v4）
> **觸發情境**：v3 完成致命陷阱修正後、baron 再提 3 點生產級健壯性建議——針對 SQL log spam / ContextVar LookupError / 序列化降級 3 個實際痛點

---

## 完整提示詞

```
請更新 .claude-logs/2026-05-23_logging_refactor_可行性評估.md、納入 baron 提供的 3 點生產級健壯性建議：
SQLAlchemy 噪聲分流 + ContextVar LookupError 防禦 + JSONFormatter 序列化降級。
直接覆寫既有評估報告（v4 revision）、TODO 不動、業務代碼不動。

建議 1: SQLAlchemy / Uvicorn logger 噪聲分流
  - INFO 模式下 sqlalchemy.engine 會逐行 INFO 印 SQL
  - baron 場景 10 本書 = 數千 SQL log
  - 修正：SQLAlchemy hardcode DEBUG-only / Uvicorn 動態 min(WARNING, root)
  - 強烈採納

建議 2: ContextVar 讀取 LookupError 防禦
  - 無 default 時 .get() 拋 LookupError
  - 觸發場景：CLI / pytest / 背景任務
  - Formatter 內崩潰會被吞、日誌完全失去
  - 修正：定義 default=None + 讀取 .get(None) 雙保險
  - 強烈採納

建議 3: JSONFormatter json.dumps 序列化降級
  - datetime / set / Decimal / UUID / Pydantic / SQLAlchemy ORM instance 拋 TypeError
  - 修正：json.dumps(..., default=str)
  - 採納

評估報告變動：TL;DR v4 + §4.X.2 分流 + §4.X.4 ContextVar 安全 + §4.Y default=str + §5 風險表 3 行 +
§6 工時微升 + §8 Q20-Q22 + 附錄新增「v4 生產健壯性建議納入對照表」

完成後不 commit、不 push。
```

---

## 執行結果摘要

- ✅ 完成狀態：v4 覆寫、3 點建議全納入
- grep 證據：
  - active codebase `logger.x(..., extra={...})` **0 處**（建議 3 影響面極小、未來預防性質）
  - 既有 v3 範例第三方 logger hardcode 統一動態降噪、未分流（建議 1 必要）
  - 既有評估報告 ContextVar 範例引用提案 L59 `default={}`，但本 plan 規範化為 `default=None` 雙保險（建議 2 必要）
- 工時更新：LOGGING-1 +10 min / LOGGING-2 +5 min / 總計 +15 min
- 整體結論不變：🟡 部分採納

## 後續引用

- 4 輪 review 累積完成（v0 / v2 / v3 / v4）、評估報告已達「不缺漏任何已知陷阱」成熟度
- pytest 新增 case：test_sqlalchemy_logger_silent_under_info_mode / test_contextvar_safe_in_cli_without_middleware / test_jsonformatter_handles_unserializable_datetime
