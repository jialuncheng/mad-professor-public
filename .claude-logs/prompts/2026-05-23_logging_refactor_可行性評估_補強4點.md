# 2026-05-23 — logging-refactor 評估報告補強 4 點 提示詞

> **收到時間**：2026-05-23（UTC+8）
> **任務代號**：logging-refactor（評估補強、無業務代號）
> **觸發 commit**：無（純評估報告更新）
> **相關產出檔案**：`.claude-logs/2026-05-23_logging_refactor_可行性評估.md`（覆寫）
> **觸發情境**：baron 在初版評估報告後、提出 4 點技術補強建議（冪等性 / 第三方 logger 劫持 / asyncio.to_thread / JSON Stacktrace）；要求納入評估報告、不新建版本

---

## 完整提示詞

```
請更新 .claude-logs/2026-05-23_logging_refactor_可行性評估.md、納入 baron 提供的 4 點技術補強建議。
直接覆寫既有評估報告（不新建版本號）、TODO 不動、業務代碼不動。

第一步：讀取規範與既有評估報告（framework / 既有評估 / 原始提案）
第二步：grep 確認 4 點補強建議的技術前提
  - 補強 1: reload=True / pytest 內 logging 配置（冪等性風險）
  - 補強 2: uvicorn / sqlalchemy logger 引用點
  - 補強 3: Python 版本 + asyncio.to_thread 既有路徑
  - 補強 4: exc_info=True 用法 + JSON log 場景

第三步：4 點補強建議逐項評估（強烈採納 / 採納 / 部分採納 / 不採納）+ 落地位置
  - 補強 1: setup_logging() 冪等性防呆（_logging_initialized global flag）→ 強烈採納
  - 補強 2: 劫持 Uvicorn / SQLAlchemy 內部 Logger、防止格式割裂 → 強烈採納
  - 補強 3: Python 3.9+ asyncio.to_thread 自動繼承 contextvars → 採納為技術註解
  - 補強 4: JSONFormatter Exception Stacktrace 單行 JSON 安全 → 採納

第四步：評估報告內具體位置變動總覽
  - TL;DR 加 Revision note
  - §3 grep 補
  - §4 LOGGING-1 加冪等性 + 第三方 logger 劫持
  - §4 LOGGING-2 加 asyncio.to_thread 註解 + JSON Stacktrace 安全
  - §5 風險表加 2 行
  - §8 Q13-Q15 新增
  - 附錄加「補強建議納入對照表」

第五步：grep 證據要求（所有技術論證必須有 grep 支撐）
第六步：嚴格不可動清單（業務代碼 / TODO / proposal / commit / push 100% 不動）

完成後不 commit、不 push。
```

---

## 執行結果摘要

- ✅ 完成狀態：評估報告覆寫、4 點補強建議全納入
- grep 證據確認：
  - reload=False（web_server.py:907）；pytest 重複 import 仍是風險
  - Python 3.12.3 ≥ 3.9（asyncio.to_thread 自動繼承 ContextVar 適用）
  - uvicorn>=0.30.0 在 requirements、SQLAlchemy 在 db.py:17 import
  - asyncio.to_thread 在 web_server.py:151 使用、loop.run_in_executor 在 L438/L475
  - exc_info=True 11 處（active 業務檔、不計 _deprecated）
- 工時更新：LOGGING-1 ~3.5h → ~4h、LOGGING-2 ~2h → ~2.5h、整體仍 3 commits
- 整體結論不變：🟡 部分採納

## 後續引用

- 補強後的 plan 更健壯、防範 reload / pytest / 雲原生收集器 3 個生產陷阱
