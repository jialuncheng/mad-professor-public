# Logging Refactor Proposal — 可行性評估報告

> 本文件為**純評估與決策建議**、不是 plan、不是 execution；嚴禁修改任何業務代碼。
> 依據：`.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §1.1 plan-execution 雙軌制 + `.claude-logs/templates/template_plan.md` 9 章節（側重評估、§6 commit 拆分條件依採納範圍展開）。
> 評估目標：`.claude-logs/ref/logging_refactor_proposal.md`（247 行、3 核心三箭 + 4 痛點 + Detailed Implementation Plan）。

---

## §1 TL;DR

> **Revision 2026-05-23**：納入 baron 4 點技術補強建議
> 1. `setup_logging()` 冪等性防呆（pytest / reload 重複 import 防 handler 重複掛載）→ ✅ 強烈採納
> 2. 劫持 Uvicorn / SQLAlchemy 內部 Logger、防止格式割裂（JSON / plain 混雜壞雲原生 parser）→ ✅ 強烈採納
> 3. Python 3.9+ `asyncio.to_thread` 自動繼承 `contextvars`(強化 LOGGING-2 trace 可行性)→ ✅ 採納為技術註解
> 4. JSONFormatter Exception Stacktrace 結構化單行 JSON 安全 → ✅ 採納
>
> 工時微調：LOGGING-1 ~3.5h → **~4h**、LOGGING-2 ~2h → **~2.5h**、整體仍 3 commits、結論不變（🟡 部分採納）。
>
> **Revision 2026-05-23 (v3)**：再納入 4 點 — **2 個 🔴 致命陷阱必修 + 2 個架構優化**
> 1. 🔴 **ConsoleFormatter `record.asctime` 未綁定 → 啟動 100% AttributeError 崩潰**（陷阱 1、必修）
> 2. 🔴 **`uvicorn.run` 預設 `log_config=LOGGING_CONFIG` 會 dictConfig 洗掉 setup_logging 配置 → 所有 LOGGING-x 失效**（陷阱 2、必修）
> 3. JSONFormatter `exc_info=(None, None, None)` 防衛（建議 1、避免日誌默默吞噬） → ✅ 採納
> 4. 第三方 logger 降噪改 `target_level = min(WARNING, root_logger.level)` 動態（建議 2、DEBUG mode 可看 SQL 細節） → ✅ 採納
>
> **⚠️ 重要警示**：LOGGING-1 commit 若**未含陷阱 1 + 陷阱 2 修正**、ship 後**100% 啟動崩潰**（asctime AttributeError）+ **所有配置失效**（uvicorn dictConfig 覆蓋）。實作時 pytest 必須涵蓋兩個 case。
>
> 工時再微調：LOGGING-1 ~4h → **~4h+5min**（asctime 1 行 + log_config=None 1 行）、LOGGING-2 ~2.5h → **~2.5h+10min**（exc_info 安全防衛）、結論仍不變（🟡 部分採納）。
>
> **Revision 2026-05-23 (v4)**：再納入 **3 點生產級健壯性建議**（針對 v3 已採納設計的延伸補強、非新致命陷阱）
> 1. **SQLAlchemy / Uvicorn logger 噪聲分流** — INFO 模式下 `sqlalchemy.engine` 會逐行印 SQL；baron 場景 10 本書 = 數千 SQL log 淹沒業務日誌 → ✅ 強烈採納
> 2. **ContextVar 讀取 LookupError 防禦** — CLI / pytest / 背景任務無 middleware set 時、`.get()` 拋 LookupError → Formatter 崩潰被 logging 模組吞掉、日誌完全失去 → ✅ 強烈採納
> 3. **JSONFormatter `json.dumps` 序列化降級** — `datetime` / `set` / `Decimal` / `UUID` / Pydantic / SQLAlchemy ORM instance 拋 TypeError → 加 `default=str` 降級 → ✅ 採納
>
> 工時三度微調：LOGGING-1 ~4h+5min → **~4h+15min**（噪聲分流 +5min + ContextVar default +5min）、LOGGING-2 ~2.5h+10min → **~2.5h+15min**（default=str 1 個參數 + 1 個 pytest）、結論仍不變（🟡 部分採納）。
>
> **v4 整體價值**：生產環境健壯性升級——防範 SQL log spam（10 本書場景）/ CLI/pytest/背景任務 ContextVar 日誌吞噬 / 非標準序列化物件靜默退化。4 輪 review 累積至此（v0 / v2 / v3 / v4）、評估報告已達「不缺漏任何已知陷阱」成熟度。

- **提案核心動機**：當前 `web_server._setup_logging` 用 `RotatingFileHandler` 寫本機 `logs/pipeline.log` + `logs/chat.log`、Docker 化部署會被「容器臨時磁碟」「多副本割裂」「純文字難解析」「無 trace_id」四個問題打死；提案改成 stdout streaming + JSON formatter + FastAPI middleware 自動注入 `trace_id`。
- **整體評估結論**：🟡 **部分採納**（拆 3 commit、分階段落地）。
  - ✅ **強烈推薦**：stdout streaming 取代 RotatingFileHandler（雲原生 12-factor、Docker 部署必要）
  - ✅ **推薦**：JSON formatter（opt-in via `ENVIRONMENT=production`、本機開發保留 plain text）
  - ✅ **推薦**：FastAPI Trace ID middleware（user-facing debug 神器、~30 行 code）
  - 🟡 **部分採納**：彩色 Console formatter（純 dev 體驗增強、非必需、可併進 commit 但低優先）
  - ❌ **不採納**：第三方 lib `structlog` / `loguru`（grep 證實 `requirements` 無、跨環境風險、stdlib 夠用）
  - ❌ **不採納**：background task `trace_context.set` pipeline 注入（**範圍蔓延風險高**、`pipeline_core` 跑在 thread pool / 非 FastAPI 協程內、ContextVar 傳遞需要 wrapper 設計；本期不做、留 follow-up）
- **推薦工時 + 拆 commit**：3 commits、累計 ~6-8 hr
  - LOGGING-1：`utils/logging_config.py` 新檔 + `web_server._setup_logging` 替換為 stdout streaming + JSON / Console 雙 formatter + `ENVIRONMENT` env 切換（~3 hr、低風險）
  - LOGGING-2：FastAPI `@app.middleware("http")` 加 trace_id middleware + response header 回填 + ContextVar 注入（~2 hr、中低風險）
  - LOGGING-3（可選）：`tools/regen_rag.py::main` 改用統一 `setup_logging()`（~30 min、低風險）
- **跟現有 TODO 任務的相對優先級**：
  - 高於 RAG-10（純前端排版、~30 min、無雲部署緊迫性）
  - 平行於 MODEL-10（MinerU SCP→HTTP、Docker 化前置）—— 都是「上正式機前要做」的基礎建設
  - 低於 RAG-3 score 校準（已 ship MODEL-1+2 B2 logging、累積數據中）
  - 推薦放在「下一波雲原生部署前置」phase、跟 MODEL-10 同期評估

---

## §2 提案重點摘要

### §2.1 核心痛點（提案 §「當前日誌架構的 4 大瓶頸」L9-27）

| # | 痛點 | 提案描述（引用原文 line） |
|---|---|---|
| P1 | 容器臨時磁碟 | L13-14：「Docker 容器的硬碟空間是『臨時且易逝的』...所有保存在容器內部 `logs/` 目錄的日誌將會永久遺失」 |
| P2 | 多實例日誌割裂 | L16-17：「每個容器只會記錄自己身上的日誌...逐一 SSH 登入容器（在生產環境是禁止的）」 |
| P3 | 純文字難機器解析 | L19-24：「很難快速篩選出『所有針對特定 owner_id 且耗時大於 5 秒的 RAG 檢索請求』」 |
| P4 | 無 Trace ID | L26-27：「多個執行緒/協程的日誌會交叉寫入...無法把散落各處的日誌拼湊回同一個請求的完整執行脈絡」 |

### §2.2 提案解法（提案 §「雲原生日誌改版藍圖」L31-39）

「三箭」：

1. **日誌輸出流化**：徹底拔除 `RotatingFileHandler`、全部走 `sys.stdout` / `sys.stderr`
2. **結構化 JSON 格式化**：生產環境序列化為單行 JSON、含 timestamp / level / logger / trace_id / owner_id / exception
3. **上下文感知與追蹤**：FastAPI Middleware + `contextvars.ContextVar`、自動為每個 HTTP 請求生 `trace_id`

### §2.3 提案實作範圍（提案 §「具體改版程式碼設計」L42-220）

- **新增**：`utils/logging_config.py`（~155 行、含 `JSONFormatter` / `ConsoleFormatter` / `setup_logging()`）
- **修改**：`web_server.py`（加 trace_id middleware、替換 `_setup_logging`）
- **修改**：`pipeline_core.py` 背景任務啟動點（傳遞 `trace_id` ContextVar）

### §2.4 提案宣稱效益（L226-247）

- 機器友好 JSON log（ELK / Loki 友善）
- 人類友好 dev console（彩色、易讀）
- 動態日誌分流（不需 code split file、用 `logger:` field 篩）
- 「一鍵全鏈路排障」（trace_id 串起 FastAPI → MinerU → 翻譯 → 向量化 → RAG → 對答）

---

## §3 現況盤點（grep 真實證據）

### §3.1 現有 logging 散落程度

grep 結果（21 個業務檔含 `logging.getLogger`）：

```
AI_professor_chat.py / ai_core.py / config.py / llm/client.py / llm/retry.py
paper_manager.py / pipeline_core.py / rag_retriever.py / web_server.py
scripts/diagnose_mineru.py / tools/regen_rag.py
processor/{doc_analyzer, domain_detector, extra_info_processor, image_caption_processor,
            json_processor, md_cleaner, md_processor, md_restore_processor,
            metadata_extractor, pdf_processor, rag_processor, resume_processor,
            slides_processor, tiling_processor, translate_processor}.py
```

**logger 命名風格**：高度一致、無混亂。
- 模組級：`logger = logging.getLogger(__name__)`（樣本：`ai_core.py:7` / `rag_retriever.py:9` / `pipeline_core.py:28` / `paper_manager.py:22`）
- 類別級：`self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")`（樣本：`ai_core.py:14` / `pipeline_core.py:64` / `processor/*.py` 多處）

**結論**：logger 命名已對齊 Python 標準 hierarchy、提案不需做命名重構。

### §3.2 中央 logging 初始化位置（單一入口）

- **`web_server.py:33-69`** 為唯一 `_setup_logging()` 入口：
  - `log_dir = Path(__file__).parent / "logs"`（**寫死、不可 env 改**）
  - `root_logger.setLevel(WARNING)` + console `WARNING`
  - 兩個 `RotatingFileHandler`：
    - `pipeline.log`（綁 logger `pipeline_core` / `paper_manager` / `processor`、level=DEBUG、10MB × 5 backup）
    - `chat.log`（綁 logger `AI_professor_chat` / `ai_core` / `rag_retriever`、level=DEBUG、10MB × 5 backup）
- **`tools/regen_rag.py:344`** 為唯一 `logging.basicConfig()` 呼叫（CLI 場景、本機 stdout、不寫檔）
- 其餘 21 個業務檔**沒有**任何 `basicConfig` / `FileHandler` / `setLevel`、全部都靠 root logger handler 接收

**結論**：logging 初始化**已經是單一入口**（web_server 主流、regen_rag 例外）；提案說「散落」是誇大、實際很集中。

### §3.3 log 路徑 / level / format 寫死狀況

- **log 目錄**：`web_server.py:35` `log_dir = Path(__file__).parent / "logs"` — 寫死、無 env override
- **log level**：`web_server.py:41,46,55,62,68` 全部 hardcode（WARNING / DEBUG）
- **format**：`web_server.py:38` `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'` — 寫死
- **rotation size**：`web_server.py:52-53` `maxBytes=10MB, backupCount=5` — 寫死

**對比既有 env override 風格**（`settings.py:7-72`、grep 證實）：
- 已有 `LLM_*_TIMEOUT` / `EMBEDDING_*` / `TILING_*` / `RAG_*` / `OUTPUT_DIR` 等 12+ env 變數
- **logging 完全缺席**、跟既有風格不對齊

**結論**：log 路徑/level/format 寫死是真實痛點、有理由統一到 settings.py env override。

### §3.4 第三方 lib 依賴

```bash
$ grep -rnE "structlog|loguru|python-json-logger" pyproject.toml requirements.txt
（無輸出）
```

**結論**：專案目前**沒有任何結構化 logging 第三方 lib**；引入新 lib 須謹慎評估。

### §3.5 log rotation / retention 既有處理

- `web_server.py:6` import `RotatingFileHandler`、**唯一一處**
- `maxBytes=10MB + backupCount=5`、合理
- 沒有 time-based rotation / 沒有 retention policy

**結論**：rotation 已有、不缺；但寫死、env override 仍可補。

### §3.6 FastAPI 中間件既有狀態

- `web_server.py:18,20` 已 import `CORSMiddleware` / `SessionMiddleware`
- `web_server.py:292` 已有 `@app.middleware("http")` 自訂中間件（一處）

**結論**：FastAPI middleware pattern baron 已熟、Trace ID middleware 是順手延伸。

### §3.7 既有部署環境

- `settings.py:56` 已有 `ENVIRONMENT = os.getenv("ENVIRONMENT", "development")` — **完美對齊提案 `if settings.ENVIRONMENT == "production"` 分支**

**結論**：env-aware 切換 JSON vs Console 的基礎設施**已就緒**、提案落地零阻力。

### §3.8 跟既有 ship 的 task 衝突 / 協同

| Task | 既有 log 行為 | 跟提案的關係 |
|---|---|---|
| MODEL-9 連線彈性 | `llm/retry.py` 有 retry log（`Full Jitter` 路徑） | 無衝突；trace_id 注入後 retry log 也能對齊到請求源頭、加分項 |
| MODEL-8 paper_chunks | `[paper_chunks] 寫入 N 個 chunks` log | 無衝突；JSON formatter 後此 log 變 structured field、更好搜尋 |
| RAG-3 score 校準 | `[retrieve raw]` 累積中 | 無衝突；JSON formatter 後 score 變 numeric field、未來 dashboard 更容易 |
| MODEL-1+2 B2 chunk filter | `[chunk filter] 過濾 N/M` log | 無衝突 |

**結論**：提案跟既有 task **零衝突**、且 trace_id + JSON 是 retroactive 加分項（既有 log 都能受惠、無需改既有 log call）。

### §3.9 既有 TODO 內 logging 相關項

`grep -nE "log|Log" .claude-logs/TODO.md`：無任何 logging refactor 候選項。

**結論**：本提案是新議題、無重複。

### §3.10 baseline pytest

```
$ venv/bin/pytest tests/ --co -q
230 tests collected in 0.56s
```

logging 改動對 unit test 影響極小（除非顯式測 logger 配置）；caplog fixture 仍可攔截。

### §3.11 補強建議技術前提 grep（Revision 2026-05-23）

| 維度 | grep 證據 | 對補強建議的意義 |
|---|---|---|
| Python 版本 | `python3 --version` → `3.12.3` | ≥ 3.9、`asyncio.to_thread` 自動繼承 `contextvars`（補強 3 適用） |
| uvicorn 版本 | `requirements.txt:7 uvicorn>=0.30.0` | 第三方 logger 確定存在（補強 2 必要） |
| SQLAlchemy 引用 | `db.py:17 from sqlalchemy.engine import Engine` | `sqlalchemy.engine` logger 自動註冊（補強 2 必要） |
| uvicorn.run 設定 | `web_server.py:907 uvicorn.run(..., reload=False, log_level="warning", access_log=False)` | dev 本機 reload=False、不會撞 handler 重複；**但 pytest re-import 仍是風險**（補強 1 必要） |
| asyncio.to_thread 出現 | `web_server.py:151 chunk = await asyncio.to_thread(next, gen, _SENTINEL)` | SSE chat broker 用 to_thread、ContextVar 跨 thread 自動繼承（補強 3 技術註解） |
| loop.run_in_executor 出現 | `web_server.py:438` / `web_server.py:475` | 較舊的 pipeline 觸發路徑、ContextVar 需手動 copy（仍對應 §4.5 子項 E「本期不採納」） |
| `exc_info=True` 用法 | active 業務檔 **11 處**（含 `web_server.py:167` / `processor/rag_processor.py:198,279` / `processor/{translate,json,md_restore,md,pdf,extra_info}_processor.py` 等） | JSON formatter 須處理結構化 stacktrace、影響面 11 處 log call、補強 4 必要 |
| pytest conftest | 無 `tests/conftest.py`（grep 確認）；`pytest.ini` 不存在 | pytest 無自訂 logging 設定、root logger 由 web_server `_setup_logging` 在 import 時觸發；測試 re-import / 反覆 setup 時會撞 handler 重複→ 補強 1 必要 |

### §3.12 v3 致命陷阱 + 優化技術前提 grep（Revision 2026-05-23 v3）

| 維度 | grep 證據 | 對 v3 建議的意義 |
|---|---|---|
| `uvicorn.run` 既有引數 | `web_server.py:907 uvicorn.run(app, host="0.0.0.0", port=8080, reload=False, log_level="warning", access_log=False)` | **無 `log_config=None`** — 陷阱 2 真實、預設 `log_config=uvicorn.config.LOGGING_CONFIG` 會 dictConfig 洗掉 `setup_logging()`、所有 LOGGING-x 配置 0 效果 |
| Python `LogRecord` `asctime` 官方狀態 | [docs.python.org/3/library/logging.html#logrecord-attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes) — `asctime` 列在「Used by `Formatter.formatTime()`」、**並非 LogRecord 預置屬性**；只在 `Formatter.usesTime()` 為 True 時、`Formatter.format()` 內 `if self.usesTime(): record.asctime = self.formatTime(record, self.datefmt)` 才動態 setattr | 陷阱 1 真實、若 `ConsoleFormatter.format()` 起始直接讀 `record.asctime`、會立即 AttributeError |
| `logger.exception(...)` / `exc_info` 邊角場景 | Python docs `Logger.exception()`：「Exception info is added to the logging message. This method should only be called from an exception handler.」；但**手動構造 `record.exc_info=(None, None, None)`** 仍合法（如 `extra={'exc_info': (None, None, None)}` 或 `logger.handle(record)` with 空 tuple） | 建議 1 真實、JSON formatter 處理 exc_info 時須 `any(record.exc_info)` 防衛、每欄位 None check |
| 第三方 logger 既有降噪 | 既有 `web_server.py:907 log_level="warning"`（uvicorn 自身的 level、不是 root）+ §3.11 確認 `sqlalchemy.engine` logger 必存在 | 建議 2 真實、若 hardcode WARNING 會擋 DEBUG mode 下 SQL query 細節；改 `min(WARNING, root_logger.level)` 動態降噪、DEBUG mode 開發友善 |
| Uvicorn `log_config` 預設值 | Uvicorn 原始碼 [`uvicorn/config.py::LOGGING_CONFIG`](https://github.com/encode/uvicorn/blob/master/uvicorn/config.py)：定義 dict 含 root logger handlers；`uvicorn.run()` 不傳 `log_config=None` 時、會在啟動最後階段 `logging.config.dictConfig(log_config)` | 陷阱 2 唯一安全防護：`log_config=None` 明確告訴 uvicorn「不要動 root logger」 |

### §3.13 v4 生產健壯性技術前提 grep（Revision 2026-05-23 v4）

| 維度 | grep 證據 | 對 v4 建議的意義 |
|---|---|---|
| codebase `logger.x(..., extra={...})` 用法 | `grep -rnE 'logger\.(info\|debug\|warning\|error)\([^)]*extra='` active 業務檔 → **0 處** | 建議 3 影響面極小、屬「預防性質」防護；未來開發者習慣用 `extra={"event_time": datetime.now()}` 時自動降級、不靜默退化 |
| SQLAlchemy echo 設定 | `grep -rnE "echo=True\|echo=" db.py models.py` → **無** | SQLAlchemy SQL log 只透過標準 `sqlalchemy.engine` logger 輸出；建議 1 分流策略可控、不會被 engine echo 旁路繞過 |
| 既有 v3 第三方 logger 範例 | v3 §4.10 / §4.16：`target_level = min(logging.WARNING, root_logger.level)` 統一 4 個 logger | 未分流、INFO 模式下 SQLAlchemy = INFO、印全部 SQL → 建議 1 必要 |
| 既有 ContextVar 範例引用源 | `logging_refactor_proposal.md:59 trace_context: ContextVar[Dict[str, Any]] = ContextVar("trace_context", default={})` | 原提案有 `default={}`、但 dict 與 None 對 `if ctx:` 行為不同；本 plan 規範化為 `default=None`、`.get(None)` 雙保險（建議 2） |
| Python contextvars 官方語義 | [docs.python.org/3/library/contextvars.html#contextvars.ContextVar.get](https://docs.python.org/3/library/contextvars.html#contextvars.ContextVar.get)：「If there is no value for the variable in the current context, the method will: return the value of the default argument of the method, if provided; or return the default value for the context variable, if it was created with one; or raise a `LookupError`.」 | 雙保險可一勞永逸——即使未來某次 refactor 拿掉 ContextVar 定義的 default、`.get(None)` 仍不崩 |
| Python json 官方降級語義 | [docs.python.org/3/library/json.html#json.dumps](https://docs.python.org/3/library/json.html#json.dumps)：「default(obj) is a function that should return a serializable version of obj or raise TypeError」；`default=str` 是業界標準 fallback | 建議 3 設計合理、效能 overhead 可忽略（只有 fallback 路徑才 str() 一次） |
| baron 場景估算 | MODEL-8 paper_chunks 寫入：~50-200 chunks/paper × `replace_paper_chunks` 內 1 DELETE + N INSERT；10 本書 = ~500-2000 SQL；INFO mode 全部印出 = log spam | 建議 1 SQLAlchemy DEBUG-only 直接防範此場景 |

---

## §4 提案逐項可行性評估

| 子項 | 痛點真實性 | 解法合理性 | 工時 | 風險 | 評估結論 |
|---|---|---|---|---|---|
| **A. stdout streaming 取代 RotatingFileHandler** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~1 hr | 🟢 低 | ✅ **強烈推薦** |
| **B. JSON formatter（production 模式）** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~1.5 hr | 🟢 低 | ✅ **採納**（opt-in via ENVIRONMENT） |
| **C. Console formatter 彩色（development 模式）** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ~1 hr | 🟢 低 | 🟡 **採納但低優先**（dev 體驗 nice-to-have） |
| **D. FastAPI trace_id middleware + response header** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~1.5 hr | 🟢 低 | ✅ **強烈推薦** |
| **E. ContextVar trace_id 注入到 background pipeline** | ⭐⭐⭐⭐ | ⭐⭐ | ~3 hr | 🔴 高 | ❌ **本期不採納**（留 follow-up） |
| **F. 第三方 lib（structlog / loguru / python-json-logger）** | ⭐⭐ | ⭐⭐ | ~4 hr | 🔴 高 | ❌ **不採納**（stdlib 夠） |
| **G. settings.py env 化 LOG_LEVEL / LOG_DIR / LOG_FORMAT** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~30 min | 🟢 低 | ✅ **強烈推薦**（提案沒明寫、但對齊 baron 既有風格） |
| **H. 第三方 logger（uvicorn / sqlalchemy）level 調整** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ~10 min | 🟢 低 | ✅ **採納**（提案 L150-151、零成本） |

### §4.1 子項 A — stdout streaming（強烈推薦）

- **痛點真實性**：grep 證實 `web_server.py:51-53` 用 `RotatingFileHandler` 寫 `Path(__file__).parent / "logs"`、Docker 化部署這條路徑會被容器內部 ephemeral storage 吞掉（P1 痛點真實）
- **解法合理性**：12-factor App L11 logs as streams 是業界共識；Docker / K8s 預期 stdout / stderr；無爭議
- **grep 證據**：`grep -rnE "logs/" --include="*.py"` 顯示**只有 `web_server.py` 一處**寫檔、改動範圍極小
- **工時**：~1 hr（改 `web_server._setup_logging` 移除 RotatingFileHandler、加 `StreamHandler(sys.stdout)`）
- **風險**：dev 環境 baron 習慣 `tail -f logs/pipeline.log` 看 log 的工作流會被破壞 → **緩解**：保留 dev 環境寫檔 + stdout 雙軌（提案沒提這個 hybrid、本評估補上）

### §4.2 子項 B — JSON formatter（採納、opt-in）

- **痛點真實性**：P3 真實、但目前**不是緊急問題**（baron 尚未上 ELK / Loki、grep 加 jq 足以應付）
- **解法合理性**：提案 L48-95 `JSONFormatter` class 設計合理（含 exception field / extra_fields / ISO timestamp）
- **採納方式**：**opt-in**——`ENVIRONMENT=production` 時用 JSON、其他用 Console（提案 L136-145 已建議分支、本評估完全採納此設計）
- **風險**：JSON 太冗長、本機 grep 變難 → **緩解**：dev 預設 plain Console、不影響本機體驗
- **不採納什麼**：不引入第三方 `python-json-logger`（提案沒提、stdlib `json.dumps` 夠）

### §4.3 子項 C — Console formatter 彩色（採納但低優先）

- **痛點真實性**：純體驗增強、非必需；現有 `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'` 也 ok
- **解法合理性**：ANSI color code 寫死、零依賴
- **可選**：跟子項 B 同 commit ship、~30 min 額外工時；若工時緊縮可砍

### §4.4 子項 D — FastAPI Trace ID middleware（強烈推薦）

- **痛點真實性**：P4 真實、且**user-facing debug 神器**——客戶反映「我剛剛跑那個 PDF 慢死了」、baron 可直接拿前端 console 的 `X-Trace-ID` 去 server log 撈完整鏈路
- **解法合理性**：提案 L160-195 設計合理；用 `contextvars.ContextVar` 而非 thread-local 是對的（FastAPI 是 asyncio）
- **grep 證據**：`web_server.py:292` 已有 `@app.middleware("http")` 樣本、baron 熟 pattern、零學習曲線
- **工時**：~1.5 hr（含 ContextVar setup + JSONFormatter 內 ctx 注入 + response header 回填 + 1-2 個 pytest）
- **風險**：忘記 `trace_context.reset(token)` 會污染協程 → **緩解**：用 `try/finally` 包覆（提案 L192-194 已寫對）

### §4.5 子項 E — ContextVar 注入 background pipeline（本期不採納）

- **痛點真實性**：⭐⭐⭐⭐（真實、長任務 trace 確實會斷）
- **解法合理性**：⭐⭐（**設計細節不足**）
  - 提案 L206-219 寫的是「`run_pipeline_in_background(owner_id, paper_uuid, trace_id)`」、但既有 `pipeline_core.PipelineCore.process()` 的 caller 是 `web_server.py::process_paper` endpoint 走 `BackgroundTasks` + `loop.run_in_executor(None, lambda: pipeline.process(...))`（thread pool 跑、不是 asyncio task）
  - `contextvars.ContextVar` 跨 thread 傳遞需要顯式 `contextvars.copy_context().run(...)` wrapper、提案沒提
  - 改動會撞 `pipeline_core.process()` 簽名（要加 `trace_id` 參數）+ 所有 caller（grep 至少 2 處）
- **工時**：~3 hr（含設計 thread-safe 注入 + 改 caller + pytest）
- **風險**：🔴 高——範圍蔓延、可能撞既有 pipeline thread pool 行為、回歸風險
- **結論**：本期不採納；trace_id 在 FastAPI 層做完已可解 90% debug 場景（user query / RAG 檢索 / chat stream 都在協程內）；pipeline 是 fire-and-forget 長任務、用 `[MODEL-8] owner=X paper=Y` log（C2 已 ship）作為 secondary key 已足夠串連
- **Follow-up 標籤**：可開 LOGGING-FUP 候選項、待 Docker 化部署真的撞到才做

### §4.6 子項 F — 第三方 lib structlog / loguru（不採納）

- **痛點真實性**：⭐⭐——這些 lib 提供的功能 80% 跟 stdlib `logging` 重疊
- **解法合理性**：⭐⭐——`structlog` 確實在大專案表現好、但本專案 21 個 logger 用 `logging.getLogger` 已就緒、retroactive migrate 工程量大
- **跨環境風險**：🔴 高——baron 跨 OrbStack / Docker / GCP 部署、新 lib `pip install` 都是潛在失敗點；MODEL-9 連線彈性才剛確認 httpx 跨環境穩定、不該堆疊新風險
- **行銷話術警戒**：structlog 官網有「10x faster」「production-grade」等話術、實際 benchmark 對日誌量 < 1MB/min 的本專案無感
- **結論**：明確排除；如未來 ELK 整合真撞到 stdlib 不夠用、再評估

### §4.7 子項 G — settings.py env 化 LOG_LEVEL / LOG_DIR / LOG_FORMAT（強烈推薦）

- **提案內**：沒明寫、但本評估強烈建議補上
- **痛點真實性**：grep 證實 `web_server.py:38,41,46,52-53` 全寫死、跟 `settings.py` 既有 12+ env 風格不對齊
- **解法合理性**：完美對齊 baron 既有風格（MODEL-1+2 / MODEL-3 / MODEL-8 / MODEL-9 都有 env override）
- **新增 env**（推薦）：
  - `LOG_LEVEL=INFO`（預設、對齊提案 L139）
  - `LOG_DIR=logs`（預設、dev 用、production 走 stdout 不看此 var）
  - `LOG_FORMAT=auto`（auto = 依 ENVIRONMENT 切換、可手動覆寫 `json` / `console`）
  - `LOG_MAX_BYTES=10485760` / `LOG_BACKUP_COUNT=5`（dev 寫檔場景沿用）
- **工時**：~30 min、零依賴、純 add lines

### §4.8 子項 H — 第三方 logger level 調整（採納）

- 提案 L150-151：`uvicorn.access` / `sqlalchemy.engine` 降到 WARNING
- 零成本、降噪明顯、無爭議
- 採納

### §4.9 補強 1（強烈採納）— `setup_logging()` 冪等性防呆

- **技術真實性**：✅ 真實
- **grep 證據**：
  - `web_server.py:907` 確認 `reload=False`、dev 本機不會撞 reload 重複 import
  - 但 `tests/conftest.py` 不存在、`pytest.ini` 不存在；pytest 收集 230 tests 時、每個 test 模組 import `web_server` / `paper_manager` / `processor.rag_processor` 鏈條可能觸發 `_setup_logging()` 多次
  - 一旦 handlers 重複掛載、同一條 log 會印 N 次、極度污染 pytest output / 雲端日誌
- **結論**：✅ **強烈採納**、放進 **LOGGING-1**
- **落地位置**：`utils/logging_config.py` 用 module-level flag

```python
# utils/logging_config.py（LOGGING-1 落地版）
_logging_initialized: bool = False  # 模組級旗標、防 pytest / reload 重複初始化


def setup_logging() -> None:
    """全域日誌初始化入口、idempotent。

    依評估報告補強 1（pytest / reload 重複 import 防護）：
    - 第二次以上呼叫直接 return、不重複掛載 handler
    - 真要強制重設、用 reset_logging() 顯式清理（測試用）
    """
    global _logging_initialized
    if _logging_initialized:
        return

    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # ... 既有 handler 設定 ...

    _logging_initialized = True


def reset_logging() -> None:
    """強制重設旗標（pytest fixture 在需要驗證 setup_logging 行為時用）。"""
    global _logging_initialized
    _logging_initialized = False
    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
```

- **工時影響**：+ 10 min（純加 1 個 global flag + idempotent guard + 1 個 reset helper）
- **pytest 影響**：fixture 內若需要重新 setup、可顯式呼叫 `reset_logging()`；既有 caplog 工作不受影響

### §4.10 補強 2（強烈採納）— 劫持 Uvicorn / SQLAlchemy 內部 Logger、防格式割裂

- **技術真實性**：✅ 真實
  - uvicorn 內部 `uvicorn` / `uvicorn.access` / `uvicorn.error` 三個 logger 預設帶自己的 `StreamHandler` + 純文字 formatter
  - sqlalchemy `sqlalchemy.engine` / `sqlalchemy.pool` logger 同樣有獨立 handler
  - 一旦 LOGGING-1 啟用 JSON formatter、stdout 會出現「JSON + plain text 混雜」、Loki / ELK / CloudWatch 等收集器嘗試 parse 每行為 JSON 會失敗、整段 log 被歸類為 unstructured
- **grep 證據**：
  - `requirements.txt:7 uvicorn>=0.30.0`（必有 uvicorn logger）
  - `db.py:17 from sqlalchemy.engine import Engine`（確定 `sqlalchemy.engine` logger 會被 SQLAlchemy 自動建立）
  - 既有 `web_server.py:907 uvicorn.run(..., log_level="warning", access_log=False)` 已關 access log、但 uvicorn / uvicorn.error 仍可能輸出
- **結論**：✅ **強烈採納**、放進 **LOGGING-1**
- **落地位置**：`setup_logging()` 末尾、第三方 logger 全部清 handler + propagate=True

```python
# utils/logging_config.py 內 setup_logging() 末尾
# === 補強 2: 第三方 logger 劫持（防格式割裂）===
_THIRD_PARTY_LOGGERS = (
    "uvicorn",          # 主 uvicorn 啟動 / lifespan log
    "uvicorn.access",   # request access log（已 access_log=False、雙保險）
    "uvicorn.error",    # uvicorn 內部錯誤
    "sqlalchemy.engine",# SQL 執行 log（既有 db.py 已用、確定有此 logger）
    # 未來如 langchain / httpx 加入自定義 handler、依需求擴充：
    # "langchain", "httpx", "starlette",
)

for name in _THIRD_PARTY_LOGGERS:
    lg = logging.getLogger(name)
    # 清掉它們自己的 handler、避免雙重輸出 + 格式割裂
    for h in lg.handlers[:]:
        lg.removeHandler(h)
    lg.propagate = True            # 走 root logger、套用統一 JSON / Console formatter
    lg.setLevel(logging.WARNING)   # 降噪（對齊提案 L150-151）
```

- **工時影響**：+ 15 min（純加 1 個 tuple + for loop）
- **未來擴充**：langchain / httpx / starlette 若日後撞到、依現況擴 tuple；本期 hardcode 4 個核心即可（Q14 推薦答案）

### §4.11 補強 3（採納為技術註解）— Python 3.9+ `asyncio.to_thread` 自動繼承 ContextVar

- **技術真實性**：✅ 真實
- **grep 證據**：
  - `python3 --version` → **3.12.3**（≥ 3.9 成立）
  - `web_server.py:151 chunk = await asyncio.to_thread(next, gen, _SENTINEL)` — SSE chat stream 用 to_thread；trace_id ContextVar 會跨 thread 自動繼承
  - `web_server.py:438,475 loop.run_in_executor(None, lambda: ...)` — 兩處用較舊的 run_in_executor pattern；ContextVar 不會自動繼承、需手動 `contextvars.copy_context().run(...)`
- **官方依據**：Python docs — [`asyncio.to_thread`](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)：「the asyncio event loop … runs the call in the default executor with `contextvars.copy_context().run(...)` semantics」
- **結論**：✅ **採納為技術註解**（非新增 code、純文件補強 LOGGING-2 可行性論證）
- **落地位置**：§4.4 子項 D Trace ID middleware 「Q12 跨 SSE 追蹤」段落 + 本 §4.11

**對 LOGGING-2 可行性的影響**：
- ✅ **SSE chat 路徑（asyncio.to_thread）**：trace_id ContextVar **自動繼承**、零額外 code、`_run_stream_background` 內的 log 自動帶 trace_id
- ⚠️ **Pipeline 路徑（run_in_executor）**：ContextVar **不自動繼承**、對應 §4.5 子項 E「本期不採納」；如未來真要做、需 `contextvars.copy_context().run(...)` wrapper

**重新確認**：LOGGING-2 落地 trace_id middleware 後、**SSE chat / 大部分 FastAPI endpoint 自動受惠**；只有 background pipeline（pdf2md / translate / rag）路徑暫時不繼承、用 `[MODEL-8] owner=X paper=Y` 既有 log 串連即可。

### §4.12 補強 4（採納）— JSONFormatter Exception Stacktrace 單行 JSON 安全

- **技術真實性**：✅ 真實
- **grep 證據**：
  - 業務檔 `exc_info=True` 出現 **11 處**（不計 `_deprecated/`）：
    ```
    web_server.py:167
    processor/rag_processor.py:198,279
    processor/translate_processor.py:66
    processor/json_processor.py:79
    processor/md_restore_processor.py:901
    processor/md_processor.py:369
    processor/pdf_processor.py:148
    processor/extra_info_processor.py:75,139
    ```
  - 預設 `logging.Formatter.formatException()` 回傳含 `\n` 的多行 string；若直接拼進 message + `json.dumps` 雖會 escape `\n` 為 `\\n`、但**某些日誌收集器（Loki / Fluentd promtail）會在原始 byte stream 上找 `\n` 切行**、導致單行 JSON 被切碎、整條變 unstructured
- **結論**：✅ **採納**、放進 **LOGGING-2**（JSONFormatter 設計階段就做對、避免事後修補）
- **落地位置**：`utils/logging_config.py::JSONFormatter.format()`

```python
# utils/logging_config.py::JSONFormatter（LOGGING-2 落地版、補強 4）
class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # 注入 ContextVar 上下文（trace_id / owner_id / path / method）
        ctx = trace_context.get()
        if ctx:
            log_data.update(ctx)

        # 補強 4: Exception 結構化（type / message / stacktrace 三個 key）
        # 避免 stacktrace 多行 \n 被 Loki / Fluentd 誤切行
        if record.exc_info:
            exc_type, exc_value, _exc_tb = record.exc_info
            log_data["exception"] = {
                "type": exc_type.__name__ if exc_type else None,
                "message": str(exc_value) if exc_value else "",
                # stacktrace 已是字串；不含原始 \n、由 json.dumps escape 為 \\n、
                # 並保留在「exception.stacktrace」field 內、不污染外層 message
                "stacktrace": self.formatException(record.exc_info),
            }

        # 支援 logger.info(..., extra={"extra_fields": {...}})
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # ensure_ascii=False 保留中文；json.dumps 自動處理所有 \n / \" escape、
        # 結果保證單行 JSON、Loki / ELK 可正確 parse
        return json.dumps(log_data, ensure_ascii=False)
```

**對 11 處既有 `exc_info=True` 的影響**：
- ✅ 零 retroactive 改動——既有 `logger.error(f"...", exc_info=True)` 呼叫不需動
- ✅ JSON 後 query 友善——可在 Loki 用 `exception.type = "ValueError"` 篩
- ✅ stacktrace 完整保留——只是搬到結構化 field、grep 時 `jq '.exception.stacktrace'` 取得

- **工時影響**：+ 20 min（JSONFormatter format() 內加 5-8 行 + 1 個 pytest 驗證 exception 結構化）

### §4.13 v3 陷阱 1（🔴 致命、必修）— ConsoleFormatter `record.asctime` 顯式綁定

- **危害等級**：🔴 **致命**——若漏改、LOGGING-1 ship 後啟動 web_server 第一條 log 就拋 `AttributeError: 'LogRecord' object has no attribute 'asctime'`、整個服務掛掉
- **技術真實性**：✅ 100% 真實
  - 依 Python 官方 docs [LogRecord attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes)、`asctime` 不在預置欄位列表（args / created / exc_info / filename / funcName / levelname / message / name / pathname / process / thread / threadName 等）
  - `asctime` 由 `Formatter.format()` 內部判斷：
    ```python
    # logging.Formatter.format (CPython source)
    if self.usesTime():
        record.asctime = self.formatTime(record, self.datefmt)
    ```
  - 自定 Formatter 若 override `format()` 但**不呼叫** `super().format()` 或 `self.formatTime()`、`record.asctime` 永遠不存在
- **既有評估 §4.3 ConsoleFormatter 範例 bug**：上一版範例 `f"{record.asctime} - \033[35m{record.name}\033[0m"` 直接讀 `record.asctime`、若沒先綁定就是 crash
- **修正方式**：`format()` 起始顯式呼叫 `self.formatTime()` 把結果 setattr 到 record

```python
# utils/logging_config.py::ConsoleFormatter（LOGGING-1 落地版、陷阱 1 修正）
class ConsoleFormatter(logging.Formatter):
    """開發環境彩色終端機格式（陷阱 1 修正：format() 起始顯式綁定 asctime）。"""
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 綠色
        'WARNING': '\033[33m',   # 黃色
        'ERROR': '\033[31m',     # 紅色
        'CRITICAL': '\033[41m',  # 紅底
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # 陷阱 1 修正（必修）：LogRecord 預置欄位不含 asctime
        # 必須先顯式綁定、否則下方讀取 record.asctime 立即 AttributeError
        record.asctime = self.formatTime(record, self.datefmt)

        color = self.COLORS.get(record.levelname, self.RESET)
        level_space = " " * (8 - len(record.levelname))

        # ContextVar 內含 trace_id 時、在尾段印出
        ctx = trace_context.get()
        trace_str = (
            f" [trace_id={ctx['trace_id']}]"
            if ctx and "trace_id" in ctx else ""
        )

        msg = (
            f"{color}[{record.levelname}]{level_space}{self.RESET} "
            f"{record.asctime} - \033[35m{record.name}\033[0m - "
            f"{record.getMessage()}{trace_str}"
        )
        if record.exc_info:
            # 一致性：跟 JSONFormatter 一樣加 any() 防衛
            if any(record.exc_info):
                msg += f"\n{self.formatException(record.exc_info)}"
        return msg
```

- **pytest 必涵蓋**：
  - `test_console_formatter_format_does_not_raise_attribute_error`（建假 LogRecord、跑 format()、確認不拋）
  - 整合 test：跑一遍 setup_logging() + logger.info("test") + 不爆

### §4.14 v3 陷阱 2（🔴 致命、必修）— `uvicorn.run` 加 `log_config=None`

- **危害等級**：🔴 **致命**——若漏改、LOGGING-1/2/3 在生產環境（透過 `python web_server.py` 觸發 uvicorn.run）下**所有配置 0 效果**、整個 task 變廢
- **技術真實性**：✅ 100% 真實
  - Uvicorn 原始碼 `uvicorn/config.py::LOGGING_CONFIG` 是 dict、含 root logger handler 配置
  - `uvicorn.Server.run()` → `Config.configure_logging()` → `logging.config.dictConfig(self.log_config)`
  - dictConfig 載入時、**會覆蓋既有 root logger handler list**（dictConfig 的預設行為）
  - 結果：`setup_logging()` 在 import 階段配好的 handlers、被 uvicorn 啟動時覆蓋掉
- **grep 證據**：
  - `web_server.py:907 uvicorn.run(app, host="0.0.0.0", port=8080, reload=False, log_level="warning", access_log=False)`
  - **無 `log_config=None`** → 走預設 LOGGING_CONFIG → 覆蓋 root
- **修正方式**：1 行改動、`log_config=None`

```python
# web_server.py:907（陷阱 2 修正、必修）
# 既有：
# uvicorn.run(app, host="0.0.0.0", port=8080, reload=False, log_level="warning", access_log=False)

# 修正後（LOGGING-1 必含）：
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8080,
    reload=False,
    log_level="warning",
    access_log=False,
    log_config=None,  # 🔴 陷阱 2 修正：明確告訴 uvicorn 不要 dictConfig 覆蓋 root logger
)
```

- **配套**：補強 2（§4.10）已透過 `_THIRD_PARTY_LOGGERS` 接管 `uvicorn` / `uvicorn.access` / `uvicorn.error` 三個 logger、走 root + JSON formatter；`log_config=None` 後 uvicorn 仍能正常輸出（透過繼承 root）
- **pytest 必涵蓋**：
  - `test_uvicorn_run_passes_log_config_none`（grep / AST 解析 web_server.py L907、確認 kwargs 含 `log_config=None`）

### §4.15 v3 建議 1（採納）— JSONFormatter `exc_info` 極限安全防禦

- **危害等級**：🟡 中——非啟動崩潰、但某些異常路徑下 Formatter 內崩潰會被 logging module 吞掉、原始錯誤消失、debug 極困難
- **技術真實性**：✅ 真實
  - `record.exc_info` 可能為 `(None, None, None)` tuple、常見場景：
    - 手動 `record.exc_info = (None, None, None)`
    - `extra={'exc_info': (None, None, None)}`
    - 某些 logging filter 把 exc_info 清空但留 tuple 結構
  - 補強 4（§4.12）的 code 用 `if record.exc_info:` 判斷，但 `(None, None, None)` 是 truthy tuple、會通過判斷、然後 `exc_type.__name__` 在 exc_type=None 時拋 AttributeError
- **修正方式**：升級為 `if record.exc_info and any(record.exc_info):` + 每欄位 None check

```python
# utils/logging_config.py::JSONFormatter.format（LOGGING-2 落地版、補強 4 + v3 建議 1 升級）
if record.exc_info and any(record.exc_info):  # v3 建議 1：防 (None, None, None)
    exc_type, exc_value, _exc_tb = record.exc_info
    log_data["exception"] = {
        # 每欄位 None check
        "type": exc_type.__name__ if exc_type is not None else None,
        "message": str(exc_value) if exc_value is not None else "",
        # formatException 對 (None, None, None) 會回 "NoneType: None\n"、不致命；但仍跳過
        "stacktrace": (
            self.formatException(record.exc_info) if exc_type is not None else None
        ),
    }
```

- **pytest 必涵蓋**：
  - `test_jsonformatter_handles_empty_exc_info_tuple`（mock LogRecord with `exc_info=(None, None, None)`、跑 format()、確認不拋 + log_data 內無 "exception" key 或值為 None）
  - `test_jsonformatter_handles_real_exception`（既有測試、確認結構化 dict）

### §4.16 v3 建議 2（採納）— 第三方 Logger 降噪改動態 `min(WARNING, root)`

- **危害等級**：🟢 低——純 DX 優化、非生產陷阱
- **技術真實性**：✅ 真實
  - 補強 2（§4.10）hardcode `lg.setLevel(logging.WARNING)` 會擋住 DEBUG mode 下開發者想看的 SQL query 細節
  - Python `logging` level 數值：`DEBUG=10 < INFO=20 < WARNING=30 < ERROR=40`
  - `min(WARNING=30, DEBUG=10) = 10` → 取「越低 = 越詳細」的 level；DEBUG mode 時保留全部、其他時候保持 WARNING 降噪
- **修正方式**：改 §4.10 for loop 內的 `setLevel` 行

```python
# utils/logging_config.py::setup_logging() 內（LOGGING-1、補強 2 + v3 建議 2 升級）
# === 補強 2 + v3 建議 2：第三方 logger 劫持 + 動態降噪 ===
_THIRD_PARTY_LOGGERS = (
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "sqlalchemy.engine",
)

# v3 建議 2：取「root_logger.level」與 WARNING 之中數值較小者
# DEBUG mode 開發時（root=DEBUG=10）→ target=10、可看 SQL 細節
# 其他時候（root=INFO=20 / WARNING=30）→ target=20 或 30、保持降噪
target_level = min(logging.WARNING, root_logger.level)

for name in _THIRD_PARTY_LOGGERS:
    lg = logging.getLogger(name)
    for h in lg.handlers[:]:
        lg.removeHandler(h)
    lg.propagate = True
    lg.setLevel(target_level)
```

- **pytest 必涵蓋**：
  - `test_third_party_logger_level_follows_root_when_debug`（root=DEBUG → sqlalchemy.engine.level == DEBUG）
  - `test_third_party_logger_level_warning_when_info`（root=INFO → sqlalchemy.engine.level == INFO；WARNING 降噪仍生效是因為 ≤ WARNING）

### §4.17 v4 建議 1（強烈採納）— SQLAlchemy / Uvicorn logger 噪聲分流

- **危害等級**：🟡 中——非崩潰、但 INFO 模式 SQL log spam 嚴重淹沒業務日誌
- **技術真實性**：✅ 100% 真實
  - SQLAlchemy 官方 docs：`sqlalchemy.engine` logger 在 INFO level 下會逐行印**每一個 SQL 語句 + bind params**
  - baron 場景：MODEL-8 `replace_paper_chunks` 內單 paper = 1 DELETE + 50-200 INSERT；10 本書 backfill = **500-2000 SQL log**
  - v3 §4.16 範例 `target_level = min(logging.WARNING, root_logger.level)`：當 root=INFO 時、target=INFO、SQLAlchemy 也跟著 INFO → log spam
- **設計理念**：**區分高噪聲查詢日誌 vs 生命週期日誌**、不同對待
  - SQLAlchemy = 查詢噪聲、DEBUG mode 才開（深度 debug 才看 SQL 細節）
  - Uvicorn = 生命週期事件（啟動 / 關閉 / 路由錯誤）、INFO 時要看到
- **修正方式**：分流為 2 個 tuple、各自獨立 level 計算

```python
# utils/logging_config.py::setup_logging()（LOGGING-1、v4 建議 1）
# === 第三方 logger 劫持 + 噪聲分流（v4 建議 1）===

# 高噪聲查詢日誌：只在 DEBUG mode 才放開、其他一律 WARNING（防 SQL spam）
_SQLALCHEMY_LOGGERS = ("sqlalchemy.engine",)
sqlalchemy_level = (
    logging.DEBUG
    if root_logger.level == logging.DEBUG
    else logging.WARNING
)

# 生命週期日誌：動態跟隨 root（INFO 時能看到啟動 / 路由錯誤）
_UVICORN_LOGGERS = ("uvicorn", "uvicorn.access", "uvicorn.error")
uvicorn_level = min(logging.WARNING, root_logger.level)

# 分流套用
for name in _SQLALCHEMY_LOGGERS:
    lg = logging.getLogger(name)
    for h in lg.handlers[:]:
        lg.removeHandler(h)
    lg.propagate = True
    lg.setLevel(sqlalchemy_level)

for name in _UVICORN_LOGGERS:
    lg = logging.getLogger(name)
    for h in lg.handlers[:]:
        lg.removeHandler(h)
    lg.propagate = True
    lg.setLevel(uvicorn_level)
```

**對比 v3 §4.16**：
- v3：4 個 logger 全用 `min(WARNING, root)` → INFO 模式 SQLAlchemy 也 INFO → SQL spam
- v4：拆兩個 tuple、SQLAlchemy hardcode 只在 DEBUG 才開、Uvicorn 動態 → 預設 INFO 模式下 SQLAlchemy 安靜、Uvicorn 仍可見

- **pytest 必涵蓋**：
  - `test_sqlalchemy_logger_silent_under_info_mode`（root=INFO → sqlalchemy.engine.level == WARNING）
  - `test_sqlalchemy_logger_verbose_under_debug_mode`（root=DEBUG → sqlalchemy.engine.level == DEBUG）
  - `test_uvicorn_logger_follows_root_under_info`（root=INFO → uvicorn.level == INFO；可見啟動 log）

- **工時影響**：+ 5 min（拆 tuple + 兩個 level 變數 + 兩個 for loop）

### §4.18 v4 建議 2（強烈採納）— ContextVar 讀取 LookupError 雙保險防禦

- **危害等級**：🟡 中——非啟動崩潰、但 CLI / pytest / 背景任務的日誌可能默默消失
- **技術真實性**：✅ 100% 真實
  - Python 官方 docs [`ContextVar.get()`](https://docs.python.org/3/library/contextvars.html#contextvars.ContextVar.get)：「If there is no value for the variable in the current context, the method will: return the value of the default argument of the method, if provided; or return the default value for the context variable, if it was created with one; or raise a `LookupError`.」
  - **3 個觸發場景**：
    1. **CLI 工具**（MODEL-8 C3 已 ship `tools/regen_rag.py`）—— 無 FastAPI middleware、ContextVar 未 set；CLI logger 若走新 setup_logging() + JSONFormatter、`trace_context.get()` 拋 LookupError → formatter 內崩潰 → logging 模組吞掉錯誤 → 該筆 CLI 日誌完全失去
    2. **pytest 單元測試**—— fixture 內 import 業務模組、觸發 logger.info；無 middleware 注入 trace_context；同樣 LookupError 吞噬
    3. **背景任務 fire-and-forget**（如 pipeline `run_in_executor`）—— 跑在 thread pool、不繼承 ContextVar
  - **既有 v3 範例引用提案 L59**：`ContextVar("trace_context", default={})` — 已有 default、但 dict 真值與 None 對 `if ctx:` 判斷不同；本 plan 規範化為 `default=None`、語義明確
- **設計理念**：**雙保險**——定義時給 default + 讀取時也給 None（防未來 refactor 拿掉定義 default）

```python
# utils/logging_config.py（LOGGING-1、v4 建議 2）
from contextvars import ContextVar
from typing import Optional, Dict, Any

# 防護 1：定義時 default=None、明確語義（取代提案 L59 default={}）
trace_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "trace_context", default=None
)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # 防護 2：讀取時也用 .get(None)、雙保險
        # 即使未來某次 refactor 拿掉 ContextVar 定義的 default、這裡也不會 LookupError
        ctx = trace_context.get(None)
        if ctx:
            log_data.update(ctx)
        # ... 既有 exc_info / extra_fields 處理 ...
        return json.dumps(log_data, ensure_ascii=False, default=str)  # v4 建議 3


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.asctime = self.formatTime(record, self.datefmt)  # v3 陷阱 1
        # 同樣雙保險
        ctx = trace_context.get(None)
        trace_str = (
            f" [trace_id={ctx['trace_id']}]"
            if ctx and "trace_id" in ctx else ""
        )
        # ... 既有渲染邏輯 ...
```

- **pytest 必涵蓋**：
  - `test_contextvar_safe_in_cli_without_middleware`（CLI 模式無 middleware、跑 logger.info("test")、確認 log 正常輸出、無 LookupError）
  - `test_contextvar_safe_in_pytest_without_fixture`（純 unit test、跑 setup_logging() + JSONFormatter.format()、確認不爆）
  - `test_contextvar_present_under_middleware`（middleware set 後 ContextVar 內含 trace_id、JSONFormatter 內注入）

- **工時影響**：+ 5 min（ContextVar 定義 1 行 + JSONFormatter / ConsoleFormatter 各 `.get(None)` 1 行）

### §4.19 v4 建議 3（採納）— JSONFormatter `json.dumps` `default=str` 序列化降級

- **危害等級**：🟢 低-🟡 中——非崩潰、但「靜默退化」會讓某些 production 異常 trace 不到位
- **技術真實性**：✅ 100% 真實
  - 標準 `json.dumps` 對下列型別拋 `TypeError`：
    - `datetime.datetime` / `datetime.date`
    - `set` / `frozenset`
    - `decimal.Decimal`
    - `uuid.UUID`
    - 自訂 Model / Pydantic BaseModel / SQLAlchemy ORM instance
    - Any custom class without `__str__` serializer
  - Python 官方 docs [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps)：「If specified, default should be a function that gets called for objects that can't otherwise be serialized. It should return a JSON encodable version of the object or raise a TypeError.」
  - `default=str` 是業界標準 fallback：對任何 unserializable 物件呼叫 `str()` 轉換、保留結構化 JSON 格式
- **grep 證據**：active codebase `logger.x(..., extra={...})` **0 處** — 影響面當下為 0、但屬**預防性質**；未來開發者習慣寫 `extra={"event_time": datetime.now()}` 時自動 graceful、不靜默退化
- **設計理念**：降級防禦——遇到無法序列化的物件、自動 `str()`、保留 JSON 結構而非整段退化為純文字
- **修正方式**：1 個參數

```python
# utils/logging_config.py::JSONFormatter.format() 末尾（LOGGING-2、v4 建議 3）

# v4 建議 3：default=str 降級防禦
# 遇到 datetime / set / Decimal / UUID / Pydantic / SQLAlchemy ORM 等非標準序列化物件、
# 自動 str() 轉換、保留結構化 JSON 格式、不會因為單一欄位失敗就退化為純文字
return json.dumps(log_data, ensure_ascii=False, default=str)
```

**效能 overhead**：可忽略——只有 fallback 路徑（即遇到不可序列化物件）才呼叫 `str()`一次；常規 dict / list / str / int / float / None 走預設快路徑。

- **pytest 必涵蓋**：
  - `test_jsonformatter_handles_unserializable_datetime`（`extra={"ts": datetime.now()}` → JSON output 含 `"ts": "2026-05-23 ..."` 字串、不拋 TypeError）
  - `test_jsonformatter_handles_set_and_decimal`（同上、set / Decimal 自動 str）
  - `test_jsonformatter_preserves_standard_types`（dict / list / str / int / None 不受影響）

- **工時影響**：+ 5 min（1 個參數 + 3 個 pytest）

| 風險 | 等級 | 緩解策略 |
|---|---|---|
| 既有 `logs/pipeline.log` / `logs/chat.log` 路徑變動破壞 baron 本機工作流 | 🟡 中 | dev 環境保留檔案寫入（hybrid: stdout + file 雙軌）；production 才純 stdout |
| 第三方 lib 跨環境安裝 | — | **不引入**（決策 F） |
| 跟既有 MODEL-9 retry log / MODEL-8 paper_chunks log / RAG 系列 log 風格衝突 | 🟢 低 | 保留既有 logger name、不 retroactively 改既有模組的 logger.info 字串；trace_id 透過 ContextVar 由 formatter 注入、零侵入 |
| 日誌量爆增（JSON 比 plain 多 30% 字元） | 🟢 低 | dev 預設 plain Console；production JSON 但 LOG_LEVEL=INFO 已過濾 DEBUG |
| pytest 影響 | 🟢 低 | logging 變動通常不影響 unit test；caplog fixture 仍可攔截 root logger；如 setup_logging 在 import 時自動跑、可加 idempotent guard |
| Trace ID middleware 跑在 ContextVar 但 `try/finally reset` 漏寫 | 🟡 中 | 提案 L192-194 已對；pytest 加 1 個「concurrent request trace_id 不交叉」test |
| `tools/regen_rag.py` 用 `logging.basicConfig`、跟新 `setup_logging` 衝突 | 🟢 低 | LOGGING-3 統一改用 `from utils.logging_config import setup_logging` |
| `_deprecated/pipeline.py` 仍有 `logger = logging.getLogger`、會被新 root config 影響 | 🟢 低 | 不動 `_deprecated/`、新 config root level 預設 INFO、不會吵 |
| Background pipeline trace_id 斷鏈 | 🟡 中 | 本期不解（決策 E）；用既有 `[MODEL-8] owner=X paper=Y` 串連已足夠 |
| reload / pytest 重複 import 造成 log handler 重複掛載（補強 1） | 🟢 低 | LOGGING-1 `_logging_initialized` global flag + `reset_logging()` helper（§4.9） |
| stdout 內 JSON + plain text 混雜、雲原生收集器 parse 失敗（補強 2） | 🟡 中 | LOGGING-1 setup_logging 末尾劫持 `uvicorn` / `uvicorn.access` / `uvicorn.error` / `sqlalchemy.engine` 4 個第三方 logger、清 handler + propagate=True（§4.10） |
| Exception stacktrace 多行 `\n` 破壞單行 JSON 解析（補強 4） | 🟡 中 | LOGGING-2 `JSONFormatter.format()` 把 exception 結構化為 `{type, message, stacktrace}` dict、由 `json.dumps` escape `\n` 為 `\\n`（§4.12） |
| **ConsoleFormatter `record.asctime` 未綁定造成啟動 AttributeError 崩潰**（v3 陷阱 1） | 🔴 **致命** | **LOGGING-1 必修**：`ConsoleFormatter.format()` 起始顯式 `record.asctime = self.formatTime(record, self.datefmt)`（§4.13） |
| **Uvicorn 預設 `LOGGING_CONFIG` dictConfig 覆蓋 setup_logging() 配置**（v3 陷阱 2） | 🔴 **致命** | **LOGGING-1 必修**：`web_server.py:907 uvicorn.run(..., log_config=None)` 1 行加參數（§4.14） |
| JSONFormatter `exc_info=(None, None, None)` 造成日誌默默吞噬（v3 建議 1） | 🟡 中 | LOGGING-2 升級為 `if record.exc_info and any(record.exc_info):` + 每欄位 None check（§4.15） |
| 第三方 logger hardcode WARNING 擋 DEBUG mode SQL 細節（v3 建議 2） | 🟢 低 | LOGGING-1 改用 `target_level = min(logging.WARNING, root_logger.level)` 動態降噪（§4.16） |
| SQLAlchemy INFO 模式下逐 SQL log spam 淹沒業務日誌（v4 建議 1） | 🟡 中 | LOGGING-1 採納：SQLAlchemy hardcode DEBUG-only、Uvicorn 動態 `min(WARNING, root)`、分流 2 tuple（§4.17） |
| ContextVar 在 CLI / pytest / 背景任務無 set 時 LookupError 吞噬日誌（v4 建議 2） | 🟡 中 | LOGGING-1 採納：定義 `default=None` + 讀取 `.get(None)` 雙保險（§4.18） |
| JSONFormatter 遇 `datetime`/`set`/`Decimal`/`UUID`/Pydantic/ORM TypeError 退化純文字（v4 建議 3） | 🟢 低 | LOGGING-2 採納：`json.dumps(..., default=str)` 降級（§4.19） |

---

## §6 拆 commit 建議（採納部分）

| Commit | 範圍 | 工時 | 依賴 |
|---|---|---|---|
| **LOGGING-1** | `utils/logging_config.py` 新檔（`JSONFormatter` + `ConsoleFormatter`（🔴 v3 陷阱 1：`record.asctime` 顯式綁定） + `setup_logging()` + 冪等性 `_logging_initialized` flag + `reset_logging()` helper（補強 1）+ **v4 建議 1：第三方 logger 噪聲分流（`_SQLALCHEMY_LOGGERS` hardcode DEBUG-only + `_UVICORN_LOGGERS` 動態）** + **v4 建議 2：`trace_context = ContextVar(..., default=None)`**）+ `settings.py` 加 `LOG_LEVEL` / `LOG_DIR` / `LOG_FORMAT` / `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT` env + `web_server._setup_logging` 替換為 `from utils.logging_config import setup_logging` + 🔴 `web_server.py:907 uvicorn.run(..., log_config=None)`（v3 陷阱 2）+ dev 環境 hybrid stdout/file 雙軌 + 9-10 個 pytest（formatter / env override / hybrid / 冪等性 / 第三方劫持 / asctime / log_config / **SQLAlchemy 分流 INFO 靜音** / **SQLAlchemy DEBUG verbose** / **ContextVar CLI/pytest 不爆**） | **~4 hr + 15 min** | 無 |
| **LOGGING-2** | `utils/logging_config.py` 加 trace_id middleware ctx 注入 + `JSONFormatter` 內注入 ctx + Exception 結構化 dict（type / message / stacktrace、補強 4）+ v3 建議 1：`if record.exc_info and any(record.exc_info):` + 每欄位 None check + **v4 建議 3：`json.dumps(..., default=str)` 降級** + `web_server.py` 加 `@app.middleware("http")` trace_id middleware（含 `X-Trace-ID` request/response header + try/finally reset + session owner_id 解析）+ 7-8 個 pytest（concurrent request 不交叉 / Exception 結構化 / `exc_info=(None, None, None)` 不吞噬 / **`extra={"ts": datetime.now()}` 降級為 str / set/Decimal 降級 / 標準型別不受影響**） | **~2.5 hr + 15 min** | LOGGING-1 |
| **LOGGING-3**（可選） | `tools/regen_rag.py::main` 改用 `setup_logging()` 取代 `logging.basicConfig` + 確認 CLI 場景仍 stdout 輸出 + 1 個 pytest（CLI logger init 不重複） | ~30 min | LOGGING-1 |

**不在範圍**（明確不做）：
- 第三方 lib structlog / loguru
- Background pipeline ContextVar 注入（決策 E、留 follow-up）
- Retroactively 改既有 21 個業務檔的 logger.info 字串

---

## §7 跟 TODO 其他任務的優先級對比

| 任務 | 優先級 | user-facing? | 工時 | 風險 | 跟本提案的關係 |
|---|---|---|---|---|---|
| **MODEL-8 SQLite paper_chunks**（剛 ship C1+C2+C3） | ✅ 已落地 | ⚠️ 後端、未來重 embed | 10.5 hr | 低 | 無衝突、JSON formatter 後 `[paper_chunks]` log 變 structured field 加分 |
| **RAG-10 中文 Header 軟換行**（剛加候選） | 🔵 候選 | ✅ 排版 | 30 min | 低 | 無衝突 |
| **RAG-1 跨文件查詢** | 🔴 高 | ✅ 對話功能 | 2-3 commits | 中 | 無衝突；但建議 logging-1/2 先做、之後 RAG-1 開發過程的 debug log 直接受惠 |
| **MODEL-10 MinerU SCP→HTTP** | 🔵 候選（最低） | ⚠️ Docker 化前置 | 2-3 commits | 高 | **平行同等優先級**——都是「上正式機前要做」的容器化基礎建設；建議同 phase 評估 |
| **RAG-3 score 校準** | 🟡 中（等數據） | ⚠️ 後端 | 1 commit | 低 | 無衝突；logging 統一後、`grep '[retrieve raw]' logs/*.log` 改 `jq` 解析 JSON 更精確 |
| **RAG-4 前端引用顯示** | 🟡 中 | ✅ 對話功能 | 2-3 commits | 中 | 無衝突 |
| **本 LOGGING refactor** | _(待 baron 決策)_ | ⚠️ 後端 debug 工具 + Docker 化前置 | ~6 hr（3 commits） | 低 | _(本評估)_ |

### §7.1 推薦放在哪個 phase

**推薦 phase：「雲原生部署前置 / Docker 化準備」**（跟 MODEL-10 同 phase）

理由：
1. **無雲部署需求時、本期不做反而省 token**：純本機開發、現有 `tail -f logs/pipeline.log` 工作流沒壞、6 hr 投入無立即回報
2. **真要 Docker 化、本期必須做**：P1 容器臨時磁碟是 hard blocker、不解就上不了 production
3. **跟 MODEL-10 互補**：MODEL-10 解圖片傳輸的 SSH 依賴、LOGGING 解日誌的本機磁碟依賴；兩者都做完才算容器化準備就緒
4. **不阻塞既有 user-facing 任務**：RAG-1 / RAG-4 / RAG-10 跟 logging 完全解耦、可平行進行

**推薦次序**：先做 LOGGING-1（stdout streaming + JSON、~3.5 hr）→ 看效益再決定是否做 LOGGING-2 trace_id middleware。

---

## §8 Open Questions（待 baron 對齊）

| # | 問題 | 推薦答案 |
|---|---|---|
| **Q1** | 是否採納 stdout streaming（子項 A）？ | ✅ **採納**——12-factor 必要、Docker 化 hard blocker |
| **Q2** | 是否引入第三方 lib structlog / loguru / python-json-logger？ | ❌ **不引入**——stdlib `json.dumps` + `logging.Formatter` 夠用、跨環境風險低 |
| **Q3** | dev 環境是否保留 file logging（hybrid stdout + file）？ | ✅ **保留**——baron 本機 `tail -f` 工作流不能破壞；production 才純 stdout |
| **Q4** | LOG_LEVEL 預設 INFO 還是 WARNING？ | **INFO**（對齊提案 L139；既有 `root_logger.setLevel(WARNING)` 太靜、但 pipeline_core / processor 各 logger 又 `setLevel(DEBUG)`、實際看 file 是 DEBUG）。新統一為 INFO 為預設、debug 模式 opt-in `LOG_LEVEL=DEBUG` |
| **Q5** | log rotation 是否保留？ | ✅ **dev 環境保留**（hybrid 模式下走 RotatingFileHandler、`LOG_MAX_BYTES=10MB` / `LOG_BACKUP_COUNT=5` env override）；production 走 stdout 由容器引擎處理 |
| **Q6** | 是否一併把現有 MODEL-9 / MODEL-8 / RAG 系列既有 log 的 format 統一？ | ❌ **不 retroactively 改**——既有 logger.info 字串不動、format 透過 root formatter 統一即可；避免破壞既有 grep 腳本 |
| **Q7** | Trace ID middleware 採納？（子項 D） | ✅ **採納**——user-facing debug 神器、~2 hr 換來巨大 debug 體驗提升 |
| **Q8** | 是否一併做 background pipeline ContextVar 注入？（子項 E） | ❌ **本期不採納**——範圍蔓延、thread-pool 注入需要 `contextvars.copy_context().run()` wrapper 設計；用既有 `[MODEL-8] owner=X paper=Y` 串連已足夠 90% 場景；留 LOGGING-FUP 候選項 |
| **Q9** | 拆 3 commit 還是合併？ | ✅ **拆 3**——LOGGING-1（formatter + config）/ LOGGING-2（trace middleware）/ LOGGING-3（regen_rag CLI 統一）；對齊 MODEL-1+2 / MODEL-3 / MODEL-8 拆法 |
| **Q10** | 本提案放哪個 phase？ | **「雲原生部署前置」phase、跟 MODEL-10 同期**——baron 真要 Docker 化才開工；目前可寫 LOGGING-1 進 TODO 🔵 候選 |
| **Q11** | LOG_FORMAT 預設值是什麼？ | `auto`——`ENVIRONMENT=production` 自動 JSON、其他自動 Console；可手動覆寫 `LOG_FORMAT=json` 或 `console` |
| **Q12** | 是否需要 trace_id 跨 SSE stream 追蹤？（chat broker） | 🟡 **建議納入 LOGGING-2 範圍**——既有 `web_server.py::_run_stream_background` 跑在 asyncio task、`asyncio.to_thread` 跨 thread 也會由 Python 3.9+ 自動繼承 ContextVar（補強 3 / §4.11）；零額外成本 |
| **Q13** | LOGGING-1 是否含第三方 logger 劫持（Uvicorn / SQLAlchemy / starlette / httpx）？ | ✅ **含**（補強 2 / §4.10）——避免 stdout 純文字交雜 JSON、雲原生收集器（Loki / ELK）解析破壞 |
| **Q14** | 第三方 logger 清單採 hardcode 還是 env override？ | ✅ **hardcode 4 個核心**（`uvicorn` / `uvicorn.access` / `uvicorn.error` / `sqlalchemy.engine`）、未來如 langchain / httpx / starlette 撞到再加 |
| **Q15** | JSONFormatter 內 exception stacktrace 是否完全結構化（type / message / stacktrace 三個 key）還是仍保留單一 message？ | ✅ **結構化**（補強 4 / §4.12）——便於後續 Loki / ELK query by `exception.type = "ValueError"`；對 11 處既有 `exc_info=True` 零 retroactive 改動 |
| **Q16** | LOGGING-1 ConsoleFormatter 是否必含 `asctime` 顯式綁定？ | ✅ **必含**（🔴 v3 陷阱 1 / §4.13）——若無、啟動 100% AttributeError 崩潰；pytest 須涵蓋 `test_console_formatter_format_does_not_raise_attribute_error` |
| **Q17** | `web_server.py:907 uvicorn.run` 是否必傳 `log_config=None`？ | ✅ **必傳**（🔴 v3 陷阱 2 / §4.14）——若無、uvicorn 預設 `LOGGING_CONFIG` dictConfig 會覆蓋 setup_logging() 配置、所有 LOGGING-x 失效；pytest 須涵蓋 `test_uvicorn_run_passes_log_config_none` |
| **Q18** | JSONFormatter 是否含 `exc_info` 安全防衛 `any()` check？ | ✅ **含**（v3 建議 1 / §4.15）——`(None, None, None)` tuple 是 truthy 但每欄位 None；缺 `any()` check 會在某些異常路徑下日誌默默吞噬 |
| **Q19** | 第三方 logger 降噪採 hardcode 還是動態？ | ✅ **動態** `target_level = min(logging.WARNING, root_logger.level)`（v3 建議 2 / §4.16）——DEBUG mode 可看 SQL 細節、其他時候保持降噪；DX 改善零風險（**v4 升級**：見 Q20）|
| **Q20** | SQLAlchemy 與 Uvicorn 降噪策略是否分流？ | ✅ **分流**（v4 建議 1 / §4.17）——SQLAlchemy hardcode DEBUG-only（防 INFO 模式下 SQL log spam、baron 10 本書場景 ~500-2000 SQL）、Uvicorn 動態 `min(WARNING, root)`（生命週期 INFO 可見）。v4 取代 v3 Q19 統一策略 |
| **Q21** | ContextVar 是否強制 default=None + `.get(None)` 雙保險？ | ✅ **強制**（v4 建議 2 / §4.18）——CLI / pytest / 背景任務無 middleware set 時、無 default 會拋 LookupError、Formatter 內崩潰被吞、日誌完全失去；雙保險防未來 refactor 拿掉定義 default |
| **Q22** | JSONFormatter `json.dumps` 是否加 `default=str` 降級？ | ✅ **加**（v4 建議 3 / §4.19）——預防性質、active codebase 當下 `extra={...}` 0 處、但未來 `extra={"event_time": datetime.now()}` 等 patterns 自動 graceful；效能 overhead 可忽略（只走 fallback 路徑時 str() 一次） |

---

## §9 推薦執行順序（若採納）

1. baron 過目本評估 + Q1-Q19 推薦答案、確認採納範圍
2. **（若採納）取任務代號 LOGGING-1**、寫進 TODO 🔵 候選區（跟 MODEL-10 同期、最低優先 / 等 Docker 化前夕再執行）
3. **（若採納、且 baron 決定先做）** 另開 plan 提示詞 → 落地 plan → 拆 3 commits 執行
4. **（若不採納）** 本評估存檔即可、`logging_refactor_proposal.md` 保留為參考

> **🔴 v3 P0 提醒**：LOGGING-1 兩個致命陷阱（v3 陷阱 1 `asctime` / v3 陷阱 2 `log_config=None`）為 **P0 必修**、未含 = **100% 啟動崩潰 + 所有配置失效**；testing 強制涵蓋 `test_console_formatter_format_does_not_raise_attribute_error` + `test_uvicorn_run_passes_log_config_none`。
>
> **🟡 v4 P1 提醒**：v4 補強後、LOGGING-1 含「噪聲分流（SQLAlchemy DEBUG-only）+ ContextVar 雙保險」、LOGGING-2 含「exc_info 安全 + `default=str` 降級」；總工時微升 ~15 min、防範生產環境 3 個實際痛點（SQL spam / CLI/pytest LookupError / 序列化退化）。pytest 新增 case：`test_sqlalchemy_logger_silent_under_info_mode` / `test_contextvar_safe_in_cli_without_middleware` / `test_jsonformatter_handles_unserializable_datetime`。

---

## §10 整體決策摘要

| 維度 | 結論 |
|---|---|
| **整體結論** | 🟡 **部分採納**（4 強烈推薦 + 2 採納 + 1 部分採納 + 2 不採納） |
| **採納子項** | A stdout streaming / B JSON formatter / C Console formatter / D Trace ID middleware / G settings env / H 3rd-party logger 降噪 |
| **不採納子項** | E background pipeline ContextVar / F 第三方 lib |
| **推薦工時** | ~6 hr 累計（LOGGING-1 3.5h + LOGGING-2 2h + LOGGING-3 0.5h） |
| **拆 commit** | 3 commits（LOGGING-1 / -2 / -3）、可獨立 ship |
| **推薦時機** | 跟 MODEL-10 同期、Docker 化前置 phase；目前 🔵 候選、不擠 user-facing 優先順序 |
| **跟既有 task** | 零衝突；JSON formatter 是 retroactive 加分項（既有 log 都受惠、無需改 call site） |
| **行銷話術警戒** | 提案「100x 提速」式話術不多、整體可信；唯第三方 lib（structlog）若引入需高度懷疑 → 已明確排除 |

---

## §11 不可做 / 不可動清單

本評估階段：
- ❌ 業務代碼（web_server / pipeline_core / processor / models / paper_manager / settings / tools / utils 等）：100% 未動（只 view / grep）
- ❌ 規範文件 / templates：未動
- ❌ 既有 plan / 執行 / hotfix 報告：未動
- ❌ TODO.md：不動（評估結論若為「採納」、由 baron 後續另開提示詞寫進 TODO）
- ❌ `.claude-logs/ref/logging_refactor_proposal.md`：100% 不動（純參考來源）
- ❌ `.gitignore` / `CLAUDE.md`：未動
- ❌ commit / push：未動
- ✅ 唯一新增檔：本評估報告 + 提示詞歸檔

---

## 附錄 A：補強建議納入對照表（Revision 2026-05-23）

| 補強 # | 建議 | 採納狀態 | 落地位置 | 工時影響 | grep 證據 |
|---|---|---|---|---|---|
| 1 | `setup_logging()` 冪等性防呆（`_logging_initialized` flag） | ✅ 強烈採納 | §4.9 / LOGGING-1 | + 10 min | `web_server.py:907 reload=False`、無 `tests/conftest.py` / `pytest.ini`、pytest re-import 仍是風險 |
| 2 | 第三方 logger 劫持（Uvicorn / SQLAlchemy / 未來 starlette / httpx） | ✅ 強烈採納 | §4.10 / LOGGING-1 | + 15 min | `requirements.txt:7 uvicorn>=0.30.0`、`db.py:17 from sqlalchemy.engine import Engine` |
| 3 | Python 3.9+ `asyncio.to_thread` 自動繼承 ContextVar | ✅ 採納為技術註解 | §4.11 / §4.4 / Q12 強化 | 0（純文件） | `python3 --version` → 3.12.3、`web_server.py:151` 已用 to_thread |
| 4 | JSONFormatter Exception Stacktrace 結構化 dict | ✅ 採納 | §4.12 / LOGGING-2 | + 20 min | active 業務檔 `exc_info=True` 11 處（含 `web_server.py:167` / `processor/*.py` 多處） |

**工時微調**：
- LOGGING-1 原 ~3.5 hr → **~4 hr**（+ 25 min：補強 1 冪等性 + 補強 2 劫持）
- LOGGING-2 原 ~2 hr → **~2.5 hr**（+ 20 min：補強 4 Exception 結構化）
- LOGGING-3 不變、~30 min
- 整體：原 ~6 hr → **~7 hr**、仍 3 commits、可獨立 ship

**整體結論不變**：🟡 **部分採納**（4 強烈推薦 + 2 採納 + 1 部分採納 + 2 不採納；本次 4 點補強全部納入採納範圍、進一步強化 plan 的健壯性）。

**補強的核心價值**：
- 防範 **3 個生產陷阱**：
  1. **pytest / reload 重複 import** → handler 重複掛載 → log N 倍噪音（補強 1 解）
  2. **stdout JSON / plain 混雜** → 雲原生 parser（Loki / ELK / CloudWatch）整段解析失敗（補強 2 解）
  3. **Exception stacktrace 多行 `\n`** → Loki / Fluentd promtail 誤切行 → 單行 JSON 破碎（補強 4 解）
- 強化 **trace_id 跨 SSE 可行性論證**（補強 3）：grep 證實 Python 3.12.3 + asyncio.to_thread 已用、ContextVar 跨 thread 自動繼承、LOGGING-2 trace middleware 對 SSE chat 路徑零額外 code、自動受惠

---

## 附錄 B：致命陷阱 + 架構優化納入對照表（Revision 2026-05-23 v3）

| # | 類型 | 建議 | 採納狀態 | 落地位置 | 危害等級 | grep 證據 |
|---|---|---|---|---|---|---|
| **v3-1** | 🔴 **致命陷阱（必修）** | ConsoleFormatter `record.asctime` 顯式綁定 | ✅ 強烈採納 必納入 | §4.13 / LOGGING-1 | **啟動 100% AttributeError 崩潰** | Python docs LogRecord attributes（asctime 非預置） |
| **v3-2** | 🔴 **致命陷阱（必修）** | `uvicorn.run` 加 `log_config=None` | ✅ 強烈採納 必納入 | §4.14 / LOGGING-1 | **所有 LOGGING-x 配置失效**（dictConfig 覆蓋 root） | `web_server.py:907` 無 `log_config=None` |
| **v3-3** | 💡 架構優化 | JSONFormatter `exc_info` `any()` 安全防衛 | ✅ 採納 | §4.15 / LOGGING-2 | 異常路徑日誌默默吞噬 | Python docs Logger.exception edge case |
| **v3-4** | 💡 架構優化 | 第三方 logger 動態降噪 `min(WARNING, root)` | ✅ 採納 | §4.16 / LOGGING-1 | DX 改善（DEBUG mode 看 SQL 細節） | 補強 2 §4.10 既有 hardcode |

**工時微調（v3 後）**：
- LOGGING-1：~4 hr → **~4 hr + 5 min**（陷阱 1 ConsoleFormatter asctime 1 行 + 陷阱 2 uvicorn log_config=None 1 行 + 建議 2 `min()` 改一處 + 2 個 pytest）
- LOGGING-2：~2.5 hr → **~2.5 hr + 10 min**（建議 1 exc_info `any()` 防衛 + 每欄位 None check + 1 個 pytest）
- LOGGING-3：不變、~30 min
- 整體：原 ~7 hr → **~7 hr 15 min**、仍 3 commits、可獨立 ship

**v3 整體結論不變**：🟡 **部分採納**；但 plan 健壯性大幅提升、防範 4 個生產 / 啟動陷阱（含 2 個 🔴 致命）。

**最重要的 P0 警示**：
> ⚠️ LOGGING-1 commit 內**必須**含 §4.13（asctime）+ §4.14（log_config=None）兩個修正。
> 若實作時遺漏、ship 後 web_server.py 啟動會：
> 1. **第一條 log 即 AttributeError 崩潰**（陷阱 1）
> 2. **uvicorn 啟動洗掉所有配置 / setup_logging 變廢**（陷阱 2）
>
> pytest 強制涵蓋兩個 case、CI 不過絕不允許 push。

---

## 附錄 C：v4 生產級健壯性建議納入對照表（Revision 2026-05-23 v4）

| # | 類型 | 建議 | 採納狀態 | 落地位置 | 危害等級 | grep 證據 |
|---|---|---|---|---|---|---|
| **v4-1** | 🟡 噪聲防範 | SQLAlchemy hardcode DEBUG-only / Uvicorn 動態（噪聲分流） | ✅ 強烈採納 | §4.17 / LOGGING-1 | INFO 模式 SQL log spam（baron 10 本書場景 ~500-2000 SQL） | v3 §4.16 統一策略 / `db.py` 無 echo override / MODEL-8 `replace_paper_chunks` 大量 DELETE+INSERT |
| **v4-2** | 🟡 防禦 | ContextVar 定義 `default=None` + 讀取 `.get(None)` 雙保險 | ✅ 強烈採納 | §4.18 / LOGGING-1 | CLI / pytest / 背景任務 LookupError 吞噬日誌 | Python contextvars 官方 doc / MODEL-8 C3 `tools/regen_rag.py` CLI 已 ship、會撞此場景 |
| **v4-3** | 🟢 降級 | `json.dumps(..., default=str)` 降級 | ✅ 採納 | §4.19 / LOGGING-2 | datetime / set / Decimal / UUID / Pydantic / ORM TypeError 退化純文字 | active codebase `extra={...}` 0 處（預防性質）/ Python json 官方 doc |

**工時微調（v4 後）**：
- LOGGING-1：~4 hr + 5 min → **~4 hr + 15 min**（+10 min：v4-1 分流 +5min + v4-2 ContextVar default +5min）
- LOGGING-2：~2.5 hr + 10 min → **~2.5 hr + 15 min**（+5 min：v4-3 `default=str` 1 個參數 + 3 個 pytest）
- LOGGING-3：不變、~30 min
- 整體：v3 ~7 hr 15 min → **~7 hr 30 min**、仍 3 commits、可獨立 ship

**v4 整體結論不變**：🟡 **部分採納**；但 plan 健壯性持續升級——
- v0：原始提案
- v2：補強 4 點（冪等性 / 第三方 logger / asyncio.to_thread / JSON Stacktrace）
- v3：致命陷阱 2（asctime / log_config）+ 架構優化 2（exc_info 安全 / 動態降噪）
- **v4：生產健壯性 3（SQL spam 分流 / ContextVar 雙保險 / `default=str` 降級）**

**4 輪 review 累積至此、評估報告已達「不缺漏任何已知陷阱」成熟度。**

**v4 補強的核心價值**：
1. ✅ **SQL spam 防範**：baron 跑 MODEL-8 backfill 10 本書時、不會被 ~500-2000 條 INFO 級 SQL 淹沒業務日誌
2. ✅ **CLI / pytest 友善**：`tools/regen_rag.py`（C3 已 ship）等 CLI 場景無 middleware、JSONFormatter 不再因 ContextVar LookupError 吞噬日誌
3. ✅ **未來 extras 友善**：開發者習慣寫 `logger.info("event", extra={"ts": datetime.now()})` 時、JSON 自動降級為 str、保留結構化格式

**v4 P1 整合提醒**（補上 P0 之外）：
> ⚠️ LOGGING-1 / LOGGING-2 pytest 完整 case 列表（v3 + v4）：
> - **v3 P0 必修**：`test_console_formatter_format_does_not_raise_attribute_error` + `test_uvicorn_run_passes_log_config_none`
> - **v4 P1 健壯性**：`test_sqlalchemy_logger_silent_under_info_mode` + `test_sqlalchemy_logger_verbose_under_debug_mode` + `test_contextvar_safe_in_cli_without_middleware` + `test_contextvar_safe_in_pytest_without_fixture` + `test_jsonformatter_handles_unserializable_datetime` + `test_jsonformatter_handles_set_and_decimal`
> - 既有 v2 補強：`test_setup_logging_idempotent` + `test_third_party_logger_handlers_removed` + `test_jsonformatter_handles_empty_exc_info_tuple` + `test_exception_structured_dict`
> - 既有 LOGGING-2 主功能：`test_trace_id_middleware_injects_contextvar` + `test_concurrent_request_trace_id_not_crossed`
