# MODEL-9-OPT Embedding連線與限流框架優化 plan

> 本計畫屬 **BE-Refactor** 工作流性質（涉及 `config.py` 與 `settings.py` 業務基建邏輯修改），旨在將 `EmbeddingModel` 的 API 呼叫、超時、連線防禦與**併發限流**，全面收攏並對齊統一的彈性防禦與限流框架。包含修改 `config.py` 與 `settings.py`，為 `EmbeddingModel` 引入全域並發限制（Semaphore），對 `embed_query` 與 `embed_image` 加上 `@retry_call` 裝飾器，並重構 `embed_documents` 與 `_embed_one`，消除既有硬編碼的線性等待，解決高頻檢索或並發呼叫時 API 429 資源耗盡進而連帶拖垮全域 LLM 連線的技術病灶。本計畫同時將建立 `tests/test_embedding_retry.py` 單元測試驗證其限流與重試行為。後續 tasks 拆分與執行時，必須強制套用 `logging SOP` 與 `database SOP` 核查。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：
  1. **全域配額共享（總量管控）**：Gemini API 的請求速率限制（RPM/TPM）通常是在 API key / GCP 專案層級進行總量管控（不分模型）。當前 `LLMClient` 設有 `LLM_MAX_CONCURRENT=6` 限流，但 `EmbeddingModel` **完全無任何併發限制**。在 RAG 檢索或大批次 Tiling 時，高頻的 Embedding 呼叫會瞬間打爆全域 API 配額，導致同帳號下的 LLM 對話也連帶因 429 崩潰。
  2. **基建端缺乏退避重試**：`EmbeddingModel.embed_query` 與 `embed_image` 內部完全沒有 429 等暫時性錯誤的重試機制，一旦撞上配額限制即立刻崩潰。
  3. **重試機制不統一**：既有 `embed_documents` 與 `_embed_one` 採用手動 linear 等待（15s/30s）且僅篩選 `'429'` 字串，未接入 unified `llm/retry.py` 的 Full Jitter 指數退避，無法防禦 `RemoteProtocolError` 或連線超時等其他暫時性網路異常。
- **解法**：
  1. **引入口動態限流（Semaphore）**：
     - 在 `settings.py` 新增 `EMBEDDING_MAX_CONCURRENT` 配置（預設為 `5`）。
     - 在 `EmbeddingModel` 實作 Class-level `_api_semaphore = threading.Semaphore(EMBEDDING_MAX_CONCURRENT)`。
     - 所有的 API 呼叫區塊（`embed_query`、`embed_image`、`_embed_batch`、`_embed_one`）內部皆使用 `with self._api_semaphore:` 包裹，**顯著降低** Embedding 呼叫造成的突發性 429（註：Semaphore 限的是「同時併發數」、非「每分鐘請求數 RPM」，僅削平突發、**不保證**不撞全域配額——詳 §7 OQ3）。
     - **429 可觀測點**：在退避重試命中時以結構化 `extra_fields`（`event: "embedding_429"`）記錄，供上線後觀察 429 命中率、據以調整 `EMBEDDING_MAX_CONCURRENT`（logging SOP）。
  2. **全面套用 `@retry_call` 裝飾器**：
     - 裝飾器置於方法外層（如 `@retry_call(retries=3, base=2.0)`）。
     - 當 API 呼叫失敗時，`with` 上下文結束會**釋放 Semaphore**，隨後才在裝飾器內進行 sleep 等待，確保重試期間不會佔用連線鎖（與 `LLMClient` 機制一致）。
  3. **重構批次與降級邏輯**：
     - 將 `embed_documents` 的批次 API 呼叫抽取為 `_embed_batch(self, batch)` 並套用裝飾器。
     - 重構 `_embed_one` 以套用裝飾器，移除手動 Linear 迴圈。
     - `embed_documents` 呼叫 `_embed_batch` 失敗後捕獲異常，退回逐筆呼叫 `_embed_one`，維持原有的優雅降級路徑。
  4. **新增單元測試**：
     - 建立 `tests/test_embedding_retry.py` 驗證 429 退避與 Semaphore 限流對齊行為。
- **影響**：修改 `config.py` 與 `settings.py`。新增 `tests/test_embedding_retry.py`。更新 `TODO.md`。無資料庫 Schema 變動，對 runtime 業務無迴歸影響。
  - **🔑 不改向量值、不觸發 Golden Baseline 重捕**：本任務僅動併發鎖 / 重試 / 退避（timing + 流控），`embed_content` 參數（model / task_type / batch=32 / `_l2_normalize`）一律不變 → 產出向量值逐一相同。故 MODEL-9-OPT **與 Golden Baseline 無關、可獨立先做**，不與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 / RESUME-P3 的重捕需求綁定。
  - **與 TILING-HOTFIX-1 相容**：`embed_documents(blocks)` 對外簽名與回傳（依序 normalized list）不變，`tiling_processor.py:425` 呼叫端**行為相容、無需改動**；惟其 inline 註解「線性退避 15s/30s」於本任務後過時，tasks 須帶一筆更新（見 §4）。

---

## §2 目標規格

### 1. 全域併發限流規格
- **配置參數化**：
  - `settings.py` 中新增 `EMBEDDING_MAX_CONCURRENT = int(os.getenv("EMBEDDING_MAX_CONCURRENT", "5"))`。
- **線程安全鎖**：
  - `config.py` 中 `EmbeddingModel` 新增 class 屬性 `_api_semaphore = threading.Semaphore(EMBEDDING_MAX_CONCURRENT)`。
  - 以下方法在發起 API 呼叫前必須獲取該 Semaphore：
    - `embed_query`
    - `embed_image`
    - `_embed_batch`
    - `_embed_one`
- **鎖釋放與重試時機**：
  - 必須確保 `@retry_call` 裝飾在方法外層，`with self._api_semaphore:` 包裹在方法內部 API 呼叫區塊。
  - 當呼叫發生異常觸發重試時，執行流退出 `with` 區塊，Semaphore 立即 release，隨後在 `llm/retry.py` 中 sleep 等待，防止 sleep 期間鎖死其他等待中的連線。

### 2. API 呼叫防禦與重構規格
- **統一退避裝飾**：
  - `embed_query` 裝飾 `@retry_call(retries=3, base=2.0)`。
  - `embed_image` 裝飾 `@retry_call(retries=3, base=2.0)`。
  - `_embed_one` 裝飾 `@retry_call(retries=2, base=2.0)`，內部刪除原有的手動 `for` 迴圈與 `time.sleep` 邏輯。**fallback 路徑刻意用 `retries=2`（非 3）**：`_embed_one` 是 `_embed_batch` 重試耗盡後的逐筆降級，避免「批次 3 次 → 每筆再 3 次」巢狀指數退避在持續 429 下尾巴過長。
- **批次解耦與防禦**：
  - 新增內部輔助方法 `@retry_call(retries=3, base=2.0)` 裝飾的 `_embed_batch(self, batch: list) -> list`，負責呼召 `self.client.models.embed_content` 處理單個批次（預設 32 筆），並回傳 normalized values。
  - `embed_documents` 內部不再有重試迴圈，改為逐批呼召 `self._embed_batch(batch)`。若拋出異常（代表重試耗盡），則捕獲異常，輸出 warning 日誌並退回逐筆呼召 `self._embed_one(text)`，保留順序對齊。
  - **worst-case 延遲說明**：持續 429 下，單批最壞為「`_embed_batch` retry 2 次（base=2.0 指數退避）→ 降級後該批每筆 `_embed_one` retry 1 次」；此為原有「batch→逐筆」降級路徑的延續（非新增 regression），指數退避尾巴較舊線性略長但更分散，已以 `retries=2` 收斂 fallback 深度。
- **異常捕獲範圍對齊**：
  - 所有 Embedding 方法現在統一支持對 `_RETRYABLE_TOKENS`（包括 429、5xx、timeout、disconnect、remote protocol 等）進行退避重試，而不僅限於 `'429'` 字串匹配。

### 3. 新增單元測試規格
- **測試路徑**：`tests/test_embedding_retry.py`。
- **測試案例 A (embed_query 429 退避)**：Mock `self.client.models.embed_content` 第一次拋出 `429` 錯誤，第二次成功。驗證 `embed_query` 能正確重試並最終回傳 normalized 向量。
- **測試案例 B (embed_image 503 重試)**：Mock API 第一次拋出 `503 Service Unavailable` 錯誤，第二次成功。驗證 `embed_image` 正確重試。
- **測試案例 C (embed_documents 批次降級)**：Mock `_embed_batch` 在呼叫時拋出 `429`（且重試耗盡），驗證 `embed_documents` 能正確補獲異常，輸出 warning 並調用 `_embed_one` 逐筆處理，最終合併回傳完整且順序正確的向量列表。
- **測試案例 D (Semaphore 限流驗證)**：驗證在高併發呼叫 `embed_query` 時，同一時間發送給底層 SDK 的 active 連線數不超過 `EMBEDDING_MAX_CONCURRENT`。

### 4. 進度與 TODO.md 規格
- **TODO 狀態稽核**：
  - 將 `TODO.md` 中新增 `MODEL-9-OPT` 項目，並在任務完成後將其移入已完成表格中，記錄落地 Commit Hash。

---

## §3 現況與證據

詳細盤點與本功能相關的現有程式碼邏輯與關鍵調用鏈（必須指出確切的檔案與行數，並附帶 `grep` 核查證據）：

- **`config.py`**：
  - `_embed_one L74-94`：內部手動寫了 `for attempt in range(3)` 的 retry 迴圈與 `time.sleep(15 * (attempt + 1))` 線性等待，且硬編碼判斷 `'429' in str(e)`。
  - `embed_documents L96-146`：同樣手動寫了 `for attempt in range(3)` 迴圈與線性等待，若失敗則退回 `_embed_one`。
  - `embed_query L148-158`：直接發起 `self.client.models.embed_content` 呼叫，無任何 retry 保護。
  - `embed_image L160-172`：直接呼叫 `self.client.models.embed_content`，無 any retry 保護。
- **`settings.py`**：
  - `L73`：已定義 `LLM_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "6"))`。但是目前沒有對應的 `EMBEDDING_MAX_CONCURRENT`。

### §3.1 grep 鋼鐵證據

```bash
# 檢索 config.py 中 embed_query 的定義與調用
grep -n -C 5 "def embed_query" config.py
# 輸出：
# 143-                        f"{start + len(batch)}/{total}）"
# 144-                    )
# 145-                    break
# 146-        return embeddings
# 147-
# 148:    def embed_query(self, text: str) -> list:
# 149-        """embed 單一查詢字串（用於搜尋）"""
# 150-        result = self.client.models.embed_content(
# 151-            model=self.model,
# 152-            contents=[text],
# 153-            config=types.EmbedContentConfig(
# 154-                task_type="RETRIEVAL_QUERY",
# 155-                output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS
# 156-            )
# 157-        )
# 158-        return self._l2_normalize(result.embeddings[0].values)

# 檢索 settings.py 中 CONCURRENT 相關的配置
grep -n "CONCURRENT" settings.py
# 輸出：
# 51:PIPELINE_MAX_CONCURRENT = int(os.getenv("PIPELINE_MAX_CONCURRENT", "1"))
# 73:LLM_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "6"))
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `llm/retry.py` 內部的 `_RETRYABLE_TOKENS`、`retry_call` 及 `retry_stream` 實作邏輯（維持 100% 穩定，防範全系統 LLM 重試機制 Regress）。
- [ ] `llm/client.py` 內部的 `LLMClient` 初始化與對話呼叫裝飾（維持穩定，包含其內部的 `LLM_MAX_CONCURRENT` 信號量控制）。
- [ ] `config.py` 內部的 `EmbeddingModel._l2_normalize` 邏輯（防範向量 norm 判定出錯）。
- [ ] 既有 RAG 檢索邏輯（如 `rag_retriever.py`）與雙軌 dispatch 流程。
- [ ] `processor/tiling_processor.py:425` 呼叫端（`embed_documents(blocks)`）：本任務僅重構 `embed_documents` **內部**，其**對外簽名與回傳（依序 normalized list）必須保持不變**，確保 TILING-HOTFIX-1 的呼叫端零改動、行為相容。
- [ ] `embed_content` 的呼叫參數（`model` / `task_type` / `output_dimensionality` / batch=32）— 不動（保證向量值不變、§1 Golden 無關前提成立）。

> **tasks 連帶待辦（非不可動、需主動更新）**：本任務後 `processor/tiling_processor.py` 內 TILING-HOTFIX-1 的 inline 註解「線性退避 15s/30s」將過時（`embed_documents` 改為 `retry_call` Full Jitter 指數退避）→ tasks 須帶一筆同步更新該註解文字（僅註解、不動邏輯）。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 專案工作流程規範 | `ref/WORKFLOW_SOP.md` |
| 專案進度管控框架 | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| 既有 MODEL-9 計畫檔 | `archive/2026-05-22_MODEL-9_連線彈性防禦_plan.md` |
| 日誌與資料庫手冊 | `sop/2026-05-23_logging_SOP_手冊.md` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**：
  ```bash
  orb venv/bin/pytest tests/test_embedding_normalize.py -v
  orb venv/bin/pytest tests/test_llm_retry.py -v
  ```
- **預計新增的測試**：
  在 `tests/test_embedding_retry.py` 中實作：
  - `test_embed_query_retry_success`
  - `test_embed_image_retry_success`
  - `test_embed_documents_fallback_on_error`
  - `test_embedding_semaphore_concurrency_limit`
  執行測試命令：
  ```bash
  orb venv/bin/pytest tests/test_embedding_retry.py -v
  ```

### §6.2 手動端到端（E2E）驗證流程

1. **單元測試回歸**：
   - 確保所有 embedding 相關的 pytest 全綠通過。
2. **SOP 合規核查**：
   - 執行 `logging SOP` 檢索（`grep -n "traceback.format_exc\|logger\.error\|logger\.exception" config.py`），確保無違規日誌輸出。
   - 執行 `database SOP` 檢索，確保無資料庫交易內 API 呼叫。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| OQ1：是否要將 `LLMClient` 與 `EmbeddingModel` 共享同一個全域 Semaphore 控制？ | **否，各自獨立控制（LLM 6，Embedding 5）** | 若共享同一個 Semaphore，會造成 LLM 呼叫與 Embedding 呼叫產生嚴重的死鎖與互相排隊（例如 Embedding 佔滿了鎖導致 LLM 無法呼叫）。各自獨立 Semaphore 可**降低**任一方單獨壟斷全域 Quota 的風險，又不產生跨模組死鎖依賴，是最安全的工程實踐。（注意：獨立上限不約束全域總量，見 OQ3。） |
| OQ2：是否要保留 `embed_documents` 對 `'429'` 特殊處理的 `time.sleep` 等待？ | **否，完全使用 `retry_call` 裝飾器接管** | 既有的手動 linear 退避（15s, 30s）非常僵硬且會阻塞當前線程。套用 unified `retry_call` 可以統一使用 Full Jitter 指數退避公式，打散並發，並享受到與 LLM 同等的彈性防禦能力，消除技術債。 |
| OQ3：併發 Semaphore vs 真正的 RPM 令牌桶（token bucket）——LLM 6 + Embedding 5 = 最多 11 併發，在全域配額（per API key/project 的 RPM/TPM）下是否足夠？ | **本任務先採「可觀測 + 可調」、暫不上令牌桶**：(1) `EMBEDDING_MAX_CONCURRENT` 預設 5、env 可調；(2) 加 429 命中率 log（§1）；(3) 上線實測觀察、撞 429 才調參；(4) 若調參後仍頻繁 429 → 另開任務上「全域 RPM 令牌桶」。 | **此題無法 a priori 測定**：429 是 GCP 專案層級的 RPM/TPM 限制，取決於實際配額方案、時段與其他流量，需上線實負載觀察（性質同 RAG-3 score 校準的「跑 1-2 週實測」）。且 **Semaphore 限的是併發數、非 RPM**——5 個快速併發仍可能超 RPM，故併發鎖只能削平突發、不能等同 rate limit。真正的 RPM 上限需 token bucket，屬更大工程，在確認併發鎖不足前不過早引入（避免過早優化）。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 MODEL-9-OPT Embedding連線與限流框架優化的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 MODEL-9-OPT tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v3 (2026-06-05)：review 補強 5 點——①§1/§2/OQ1 軟化「保證不打爆配額」為「降低突發」、釐清 Semaphore 限併發≠RPM 限流；②新增 OQ3（併發鎖 vs RPM 令牌桶、需上線實測、暫採可觀測+可調）+ §1 加 429 log 觀測點；③§1 影響欄明寫「不改向量值、不觸發 Golden Baseline 重捕」（可與 P3 解耦獨立先做）；④§1/§4 補與 TILING-HOTFIX-1 相容（embed_documents 簽名不變）+ tasks 帶更新其退避註解之待辦；⑤§2 `_embed_one` fallback 降為 `retries=2` 收斂巢狀退避尾巴 + worst-case 延遲說明。
- v2 (2026-06-05)：新增 Semaphore 限流規格。考慮到 Gemini 全域 Quota 總量管控，引入 `EMBEDDING_MAX_CONCURRENT` 並發鎖以防範 Embedding 呼叫壟斷配額，並設計鎖在重試 sleep 前釋放。
- v1 (2026-06-05)：初版建立，將 EmbeddingModel 呼叫 API 的重試機制全面接入 `llm/retry.py` 彈性防禦框架。
