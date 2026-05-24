# Phase 4.7d Commit 12 — Plan：Gemini retry + LLMClient 解耦

> 純分析報告、零檔案改動（除本 .md）。

## TL;DR

- **問題**：`2601_16502v2.pdf` 在 translate stage 撞 Gemini 502 → pipeline 整支死。`chat / chat_stream_by_sentence` 無 retry；`chat_with_image` 僅擋 429。
- **建議方案**：**α**（retry decorator）+ **β**（LLMClient 拆到 `llm/client.py`、EmbeddingModel 留 config.py）。
- **理由**：retry decorator 對 4 個 method 套用（3 LLM + EmbeddingModel 兩個 retry 點亦可順手換）；β 拆檔比 α 拆全部更精準——EmbeddingModel 跟 LangChain `Embeddings` 介面緊耦合、跟 LLM client 是兩條獨立路徑，拆出來反而打亂。
- **不改接口語意**：caller 只動 import path（10 處）；retry 透明、existing grounding fallback 保留。

---

## 1. 現況盤點（grep 結果）

### 1a. 誰 import config.LLMClient / EmbeddingModel

```
AI_professor_chat.py:6:                          from config import LLMClient
processor/doc_analyzer.py:7:                     from config import LLMClient
processor/domain_detector.py:17:                 from config import LLMClient
processor/extra_info_processor.py:7:             from config import LLMClient
processor/image_caption_processor.py:7:          from config import LLMClient
processor/metadata_extractor.py:395 / 557:       from config import LLMClient   (延遲 import)
processor/slides_processor.py:7:                 from config import LLMClient
processor/translate_processor.py:4:              from config import LLMClient, TRANSLATE_MODEL
processor/rag_processor.py:8:                    from config import EmbeddingModel
processor/tiling_processor.py:7:                 from config import EmbeddingModel
rag_retriever.py:6:                              from config import EmbeddingModel
```

**LLMClient 直接 caller：9 個檔**（含 2 處 metadata_extractor 延遲 import 算同檔 1 個）：
- `AI_professor_chat.py`
- `processor/doc_analyzer.py`
- `processor/domain_detector.py`
- `processor/extra_info_processor.py`
- `processor/image_caption_processor.py`
- `processor/metadata_extractor.py`
- `processor/slides_processor.py`
- `processor/translate_processor.py`
- _(`translate_processor.py` 同時 import `TRANSLATE_MODEL`——一個 import line)_

**EmbeddingModel 直接 caller：3 個檔**：
- `rag_retriever.py`
- `processor/rag_processor.py`
- `processor/tiling_processor.py`

### 1b. LLMClient 內部結構（config.py L13-192）

3 個 public method：
- `chat(messages, temperature=0.5, stream=True, model=None) -> str`：**無 retry**
- `chat_stream_by_sentence(messages, temperature, model, use_web_search) -> Generator[str, None, None]`：**無 retry**（grounding 失敗時 fallback 一次「無 search 重試」、但不是 transport-level retry）
- `chat_with_image(messages, image_data, mime_type, model) -> str`：**429 retry 3 次、固定 sleep 2s/4s/6s**（其他例外即拋）

singleton 模式（`_instance` + `threading.Lock()`）；建構時 `genai.Client(api_key=GEMINI_API_KEY)`。

### 1c. EmbeddingModel 內部結構（config.py L196-313）

繼承 `langchain.Embeddings`。retry 邏輯：
- `_embed_one`：429 retry 3 次、linear sleep 15s/30s（L216-237）
- `embed_documents`：每批 429 retry 3 次、固定 sleep 15s/30s；非 429 退回逐筆（L242-281）

### 1d. config.py 模組層

```
L1-11: imports（含 settings 取常數）
L13-192: class LLMClient
L196-313: class EmbeddingModel
```
**無 module-level 常數**——常數都在 `settings.py`，`config.py` 只 re-export 給 caller（`from config import TRANSLATE_MODEL` 等）。
實際 module-level 變數 grep 顯示只有兩個 class 的內部 `_instance` / `_lock`。

### 1e. 既有 `llm/` 模組

```
llm/__init__.py
llm/message_utils.py    # _convert_messages（OpenAI msg → Gemini format）
```
新檔放這裡天然整齊。

### 1f. 測試 import 狀況

```bash
$ grep -l "LLMClient\|config\." tests/*.py
（無結果）
```
**沒有測試直接 import LLMClient / config**——所有現存測試走 mock 注入 LLM。改 import path 不會破測試。

`pytest tests/ -q` 當前：75 passed 3 skipped。

---

## 2. 設計提案：3 個方案對比

| 方案 | 拆法 | 影響檔數（caller import 改） | 解耦徹底度 |
|---|---|---|---|
| **α** | 新增 `llm/client.py`、把 LLMClient + EmbeddingModel **整組搬過去**；config.py 只保留設定 re-export | **12 個檔** 改 import path | 高 |
| **β** | 新增 `llm/client.py` **只搬 LLMClient**；EmbeddingModel 留 config.py | **9 個檔** 改 import path | 中（EmbeddingModel 仍與 config 同檔） |
| **γ** | 不拆檔、retry 純 decorator 加在 config.py 既有 LLMClient 上 | **0 個檔** 改 import | 低（只解 retry、未解耦） |

### 各方案優缺點

#### α — LLMClient + EmbeddingModel 都搬到 `llm/`

**優**：
- 解耦最徹底，`llm/` 變成「對外 LLM SDK adapter」單一職責
- 未來換 LLM provider（OpenAI / Anthropic / Claude）時，只動 `llm/` 內部

**缺**：
- EmbeddingModel 繼承 `langchain.Embeddings`、跟 LangChain 介面緊耦合；放 `llm/` 比放 config.py 沒明顯加分
- 改動範圍最大、12 處 import 改、回歸風險最高
- EmbeddingModel 的設計責任更接近「RAG 子系統的元件」——放 `rag/` 都比放 `llm/` 合理；強放 `llm/` 是為了名稱整齊而非語意整齊

#### β — 只搬 LLMClient ✅ **推薦**

**優**：
- 解耦對的東西：LLMClient 才是「對 Gemini chat API 的 adapter」
- EmbeddingModel 留 config.py 維持現狀（caller 3 個檔不改）
- 9 個檔 import 改、可一次到位
- 跟 `llm/message_utils.py` 共用 `_convert_messages`，後者本來就在 `llm/`、新檔自然整齊
- 為 Phase 4.7e 之後若做「換 LLM provider」鋪好路（EmbeddingModel 不必同步處理、責任不同）

**缺**：
- 解耦不完全——但完不完全沒差，EmbeddingModel 本來就沒人覺得它跟 config 糾纏
- config.py 由 313 行降到 ~120 行（仍有 EmbeddingModel），不算「乾淨檔」

#### γ — 不拆檔、只加 retry

**優**：
- 改動最小、0 個 caller 改
- 純粹解決 502 問題、最小風險

**缺**：
- 沒處理 baron 明確指定的「解耦」需求——「兩件事一起一個 commit」這句話明示要拆
- 後續 Phase 4.7e 若想換 provider 仍要拆、現在做還是要做
- LLMClient 跟 EmbeddingModel 混在同檔，責任不單一

### 跟 `llm/message_utils.py` 的關係

`llm/message_utils.py` 已存在、含 `_convert_messages`。新 `llm/client.py` 自然 `from .message_utils import _convert_messages`——本來就同一邏輯群。

config.py 內 LLMClient 有 `system_instruction, contents = _convert_messages(messages)`（L40, L74, L166），是從 `llm/message_utils` import 進來（grep `from llm`）：

```python
$ grep -n "from llm" config.py
# 預期見：from llm.message_utils import _convert_messages
```
（沒查就先假設、實作時 grep）。

### 跟 Phase 4.7e leverage

baron 之後若要：
- 換 LLM provider（OpenAI / Anthropic）→ 只動 `llm/client.py`、caller 不改
- 加 LLM call 統一 metrics / observability → 只動 `llm/client.py`
- 改 retry 策略 → 只動 decorator（無論 α/β）

α / β 都 leverage；γ 完全沒。

---

## 3. retry 策略設計

### 形式：decorator 還是 class method？

**推薦 decorator**——理由：
- 對 3 個 chat method 共用、避免重複 try/except
- 對 stream（generator）需要特殊處理（見 §5 風險評估），decorator 可分兩個版本（`@retry_call` / `@retry_stream`）
- 也能套到 EmbeddingModel 既有 429 retry 點，統一行為（可選、見後段）

### 重試的錯誤分類

| 例外 / 狀態碼 | 行為 | 理由 |
|---|---|---|
| **5xx**（500 / 502 / 503 / 504） | retry | 後端暫時性、重試通常有救 |
| **429**（rate limit） | retry | 既有行為延續、token bucket 等待後可過 |
| **連線錯誤 / 超時**（`ConnectionError` / `TimeoutError` / `requests.exceptions.ConnectionError` 等） | retry | 網路抖動、暫時性 |
| **4xx**（400 / 401 / 403 / 404） | **不** retry | caller bug / 認證錯 / 路徑錯，重試也沒用、白燒 token |
| Gemini SDK 內部例外（`google.api_core.exceptions.ServiceUnavailable` 等） | retry（依 status code 分流） | SDK 例外有可能不帶 HTTP code、依 type 分 |
| 其他（如 ValueError、TypeError） | **不** retry | 程式邏輯錯，重試只是把錯誤延後 |

實作策略：**字串匹配**（grep `str(e)` 找 '429' / '500' / '502' / '503' / '504'）。原因：
- google-genai SDK 例外型別變來變去、`isinstance` 不穩
- 既有 EmbeddingModel / chat_with_image 都是字串匹配 '429'、新 helper 沿用此 style 一致
- 後續若 SDK 提供穩定 status code attribute，再升級成 isinstance

### 重試次數與退避

- **次數**：3 次（總 4 次 attempt）
- **退避**：指數 + jitter
  - 基準 `base = 2.0` 秒
  - delay = `base * 2 ** attempt + random.uniform(0, 1)`
  - attempt 0 → ~2-3s；attempt 1 → ~4-5s；attempt 2 → ~8-9s
  - 比既有 chat_with_image 固定 `2*(attempt+1)` 略長、給 502 更多窗口
- **EmbeddingModel 既有 429 retry**：base 較大（15s）、保留；不改

### 既有 429 retry 整合策略

兩個選項：
1. **chat_with_image 換上新 decorator**：刪舊 try/except、套 `@retry_call(retries=3)`——簡潔
2. **不動既有 retry，新 decorator 只對 chat / chat_stream_by_sentence 套**：保守

**推薦 1**（換掉）：減少 duplicate；既有 chat_with_image 退避 2s/4s/6s vs 新 2-3s/4-5s/8-9s 差不多；EmbeddingModel 不動（base 不一樣、邏輯複雜）。

### 偽碼

```python
# llm/retry.py（新檔，或併入 llm/client.py）
import time, random, logging, functools
logger = logging.getLogger(__name__)

_RETRYABLE_TOKENS = ('429', '500', '502', '503', '504', 'timeout',
                     'unavailable', 'connection', 'deadline')

def _is_retryable(e: Exception) -> bool:
    s = str(e).lower()
    return any(tok in s for tok in _RETRYABLE_TOKENS)

def retry_call(retries: int = 3, base: float = 2.0):
    """裝飾同步 callable、依例外文字判斷重試。"""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if attempt == retries or not _is_retryable(e):
                        raise
                    delay = base * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"[{fn.__name__}] {type(e).__name__}: {e} — "
                        f"retry {attempt+1}/{retries} after {delay:.1f}s"
                    )
                    time.sleep(delay)
        return wrapper
    return deco

def retry_stream(retries: int = 3, base: float = 2.0):
    """裝飾 generator-returning function。
    僅在「尚未 yield 任何元素前」失敗才重試；已 yield 後失敗直接 raise
    （避免重複輸出已產出片段給下游）。"""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(retries + 1):
                yielded_any = False
                try:
                    for item in fn(*args, **kwargs):
                        yielded_any = True
                        yield item
                    return
                except Exception as e:
                    if yielded_any:
                        raise  # 已開始輸出、不重試（避免重複片段）
                    if attempt == retries or not _is_retryable(e):
                        raise
                    delay = base * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"[{fn.__name__}] stream pre-yield {type(e).__name__}: "
                        f"{e} — retry {attempt+1}/{retries} after {delay:.1f}s"
                    )
                    time.sleep(delay)
        return wrapper
    return deco
```

### 套用點

```python
# llm/client.py
class LLMClient:
    @retry_call(retries=3, base=2.0)
    def chat(self, ...): ...

    @retry_call(retries=3, base=2.0)
    def chat_with_image(self, ...):  # 同時刪除既有 429 retry 內迴圈
        ...

    @retry_stream(retries=3, base=2.0)
    def chat_stream_by_sentence(self, ...):
        ...  # 但 existing grounding fallback 在 generator 內部、本身不裝飾
              # 此 decorator 只 cover「進 generator 前 / 第一 yield 前」例外
```

---

## 4. 接口設計

baron 偏好：**本 commit 純 retry 引入 + 拆檔，不改接口語意**。caller 邏輯保留、只改 import path。signature 整理留下次。

具體：
- 3 個 method 簽名 1:1 等效
- 例外型別 1:1 等效（retry 用盡後 raise 原例外、不包成新 type）
- `_last_grounding_sources` side-channel attr 保留（caller 取此值）
- singleton get_instance 保留
- 簽名整理（如把 stream/non-stream 合一）留下次

caller 端改動範例：
```python
# Before
from config import LLMClient

# After
from llm.client import LLMClient
```

`translate_processor.py` 例外：同時 import `TRANSLATE_MODEL`。建議：
- `from llm.client import LLMClient`
- `from settings import TRANSLATE_MODEL`（直接從 settings 取、不經 config re-export）
- 或：保留 `from config import TRANSLATE_MODEL`（config.py 仍 re-export 設定）—— 推薦此選項（不擴大改動）

---

## 5. 風險評估

### 5.1 caller 漏改 import 路徑
- 9 個檔、grep 全部找出（§1a 已列）
- 加 `processor/metadata_extractor.py` 內 2 處延遲 import（L395, L557）
- 風險低：grep 可機械找完；CI（如有）import error 立刻爆
- **保險**：留 `config.py` 內 `from llm.client import LLMClient` 一行作為 shim 期（一個 release 內），降級為 deprecation warning；下個 commit 移除

### 5.2 decorator 包裝後例外型別洩漏
- decorator 用盡重試後 raise 原例外、**型別 / message 不變**
- caller 端既有 except 條件（如 `except Exception as e:`）行為等效
- 風險低

### 5.3 generator 裝 decorator 的特殊處理
- 同步 generator 不能用 `@retry_call` 直接包（generator 是 lazy、`return fn(*args)` 拿到 generator object、無法在外面 try）
- 解法：拆 `retry_stream`（§3 偽碼）：在內部 `for item in fn(*args): yield item`、catch 例外、重啟 generator
- **重啟風險**：fn 內部如有副作用（寫檔 / 改狀態），重啟會重複執行；LLMClient 內無此問題、純讀取
- 已 yield 任何元素後失敗 → 不重啟（避免重複片段給 caller）
- 風險中：需仔細測試

### 5.4 既有 grounding fallback 跟新 retry 共存
- `chat_stream_by_sentence` 內部已有「grounding 失敗、無 yield 時 fallback to no-search」邏輯（config.py L143-159）
- 此 fallback 在 generator 內、不被 `@retry_stream` 影響
- 順序：`@retry_stream` 包整個 method → 進入 method 後跑既有 grounding logic → fallback to no-search（仍在同一次 generator call 內）→ 若 no-search 也炸、退到 `@retry_stream` 層、重啟整個 method
- 風險低：兩層獨立、行為疊加

### 5.5 EmbeddingModel 內 429 retry 衝突
- 本 commit β 方案 **不動 EmbeddingModel**（留 config.py）
- 既有 429 retry 邏輯保留
- 風險：無

### 5.6 retry 用盡耗時
- 3 retries 最壞 ~2 + 4 + 8 = 14s 退避時間 + 4 次 API call
- 比直接失敗多 ~14s 但比整支 pipeline 重跑划算
- 風險低

---

## 6. 測試規劃

### 6.1 既有測試影響

- `tests/test_metadata_extractor.py`：mock LLM 注入、不 import LLMClient → 不受影響
- `tests/test_md_restore_processor.py`：純單元、無 LLM → 不受影響
- `tests/test_restore_processor.py`：grep 確認

**預期**：既有 75 passed 3 skipped → 仍 75 passed 3 skipped（除非新增測試）。

### 6.2 新增測試（`tests/test_llm_retry.py`）

| 測試 | 模擬 | 驗證 |
|---|---|---|
| `test_retry_call_5xx_then_success` | mock fn raise `Exception('502 Bad Gateway')` 1 次後 return | 應重試 1 次、最終回正常 |
| `test_retry_call_4xx_no_retry` | mock fn raise `Exception('400 Bad Request')` | 立刻 raise、不重試 |
| `test_retry_call_exhausts` | mock fn 永遠 raise `Exception('503')` | 重試 3 次後 raise（總 4 attempt） |
| `test_retry_call_429_retries` | mock fn raise `Exception('429')` 1 次後 return | 應重試（既有 chat_with_image 行為延續） |
| `test_retry_stream_pre_yield_retry` | mock generator 第一次 yield 前 raise '502' | 重啟 generator、最終成功 |
| `test_retry_stream_mid_stream_no_retry` | mock generator yield 1 個後 raise '502' | 立刻 raise、不重啟（避免重複） |
| `test_retry_call_non_retryable` | mock fn raise `ValueError('foo')` | 立刻 raise |
| `test_retry_call_backoff_timing` | 用 monkeypatch 攔 `time.sleep`、檢查 delay 序列 | 確認指數 + jitter |

### 6.3 整合 smoke test

- 上 OrcStack 後手動：
  - 重跑 `2601_16502v2.pdf`（baron 原案）
  - 觀察 logs 是否看到 retry log（`[chat] 502 — retry 1/3 after 2.3s`）
  - 觀察最終是否跑完（不再因 502 整支死）

---

## 7. 推薦方案

### α / β / γ 的選擇

**推薦 β**：
1. 解耦對的東西（LLMClient 是 Gemini chat adapter）
2. EmbeddingModel 留 config.py 維持現狀、不擴大改動範圍（caller 3 個檔不改）
3. 跟既有 `llm/message_utils.py` 共用 `_convert_messages` 自然
4. caller 改動 9 處可控、grep 找得到
5. 為 Phase 4.7e 換 provider 鋪好路

**為何不選 α**：EmbeddingModel 跟 `langchain.Embeddings` 緊耦合、放 `llm/` 比 config.py 沒明顯加分；硬放只是「整齊強迫症」。

**為何不選 γ**：baron 明確說「兩件事一起一個 commit」，γ 只解 retry、不滿足。

### retry 策略

**推薦**：
- 新增 `llm/retry.py`（或併入 `llm/client.py` 內，看 baron 偏好）
- 兩個 decorator：`retry_call`（同步 callable）+ `retry_stream`（generator）
- 字串匹配 retryable token、3 次、指數退避 + jitter、base=2.0
- `chat / chat_with_image / chat_stream_by_sentence` 全套上
- 既有 chat_with_image 429 retry 內迴圈刪掉、換 decorator
- EmbeddingModel 不動

### 整體 commit 範圍預估

| 動作 | 檔 | 行數估算 |
|---|---|---|
| 新增 `llm/retry.py` | 1 | +60 |
| 新增 `llm/client.py`（從 config.py L13-192 搬+貼上） | 1 | +180 |
| 刪除 `config.py` 內 LLMClient class | 1 | -180 |
| 9 個 caller import path 改 | 9 | +9 / -9 |
| 新增 `tests/test_llm_retry.py` | 1 | +120 |
| `config.py` 可選 shim line（`from llm.client import LLMClient`） | 1 | +1（過渡用） |

**總計**：~13 個檔、+370 / -190。

---

## 8. 待 baron 決策的 open questions

1. **retry decorator 放哪裡？**
   - 選項 A：`llm/retry.py`（獨立檔、單一職責、可被其他模組複用）
   - 選項 B：`llm/client.py` 內 module-level function（與 client 共置、一個檔搞定）
   - **推薦 A**（後續 EmbeddingModel 若改 retry 也可共用）

2. **config.py 是否留 shim**？
   - 保險：`from llm.client import LLMClient`（一行 re-export）
   - 風險：caller 不會被強迫改 import path，技術債延續
   - **推薦不留 shim**——caller 9 處同一 commit 改完、grep 容易驗、不留半套狀態

3. **`chat_with_image` 既有 429 retry 是否拔掉**？
   - 推薦：拔掉、套 `@retry_call` 統一
   - 風險：固定 2s/4s/6s 退避變指數 2-3s/4-5s/8-9s——差不多
   - **推薦拔**（避免雙重 retry）

4. **EmbeddingModel 既有 429 retry 是否同步換 decorator**？
   - 推薦：**本 commit 不動**——EmbeddingModel 退避基數較大（15s）、邏輯複雜（含批次 retry + fallback 逐筆）；同 commit 動會擴大範圍
   - 留 Phase 4.7e 或更後

5. **retry log level**？
   - 選項：`warning`（明顯但不報警）/ `info`（淡化）
   - **推薦 warning**：retry 是異常路徑、應該被監控（logs/pipeline.log 可看）

6. **是否引入 jitter**？
   - 純指數退避 vs 指數 + jitter（雷霆群效應規避）
   - mad-professor 是單使用者場景、雷霆群效應風險低；jitter 主要好處在多客戶端並打 API 時
   - **推薦加** jitter（成本低、行為更穩；future-proof）

7. **單元測試框架使用 `unittest.mock` 還是 pytest fixture**？
   - 既有測試混用（`tests/test_metadata_extractor.py` 用 fixture / parametrize / monkeypatch；無 unittest.mock）
   - **推薦** `monkeypatch` + 自製 fake class（風格一致）

8. **是否本 commit 順帶解 `metadata_extractor.py` 兩處延遲 import？**
   - 延遲 import 是為避免「模組載入即需金鑰」（comment L380）
   - 改 path 後仍可延遲、無需改邏輯
   - **推薦只改 path、不動延遲機制**

---

## 9. 不可動清單（執行階段適用、本輪未做）

- ❌ 業務檔（config.py / processor/ / web_server.py 等）：未動
- ❌ 新建業務檔（llm/client.py / llm/retry.py）：未動
- ❌ commit / push：未動
- ✅ 跑 grep / pytest 只讀命令：已執行
- ✅ 本報告 `.md`：唯一新增檔

---

## 狀態

**Plan 完成、等 baron 確認後再進入 Execute 階段**。

執行階段建議：
- 拆 sub-commits（如 baron 需要更細粒度）：
  - 12-1 新增 `llm/retry.py` + 測試（純新檔、0 caller 改）
  - 12-2 新增 `llm/client.py`（從 config.py 搬）+ 9 caller import 改 + 刪 config.py 內 LLMClient
- 或一個 commit 完成（baron 原指示）：12 一次到位

執行前需 baron 回答 §8 open questions（特別是 #1 / #2 / #3 / #4）。
