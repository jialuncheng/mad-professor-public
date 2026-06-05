# MODEL-9-OPT Embedding連線與限流框架優化 — Tasks

> 本文件為 MODEL-9-OPT 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-05_MODEL-9-OPT_Embedding連線與限流框架優化_plan.md`（§99.2 v3）產出，含 4 個 Commit（C1 設定 + C2 核心重構 + C3 測試 + C4 Checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `tests/test_embedding_retry.py`（429 退避 / 503 重試 / 批次降級 / Semaphore 限流 4 測試）|
| **修改檔案** | 3 個 | `settings.py`（新增 `EMBEDDING_MAX_CONCURRENT`）/ `config.py`（EmbeddingModel Semaphore + @retry_call + 重構 embed_documents/_embed_batch/_embed_one + 429 log）/ `processor/tiling_processor.py`（僅更新 TILING-HOTFIX-1 退避註解文字）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1 → C2 → C3 → C4（Checkout）|
| **baton 歸檔** | 1 次 | C4 收官：`mv` baton plan → `plans/` + C1-C4 `_執行.md` → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：`EmbeddingModel`（`config.py`）完全無併發限制、且 `embed_query`/`embed_image` 無 429 退避、`embed_documents`/`_embed_one` 用僵硬手動 linear 等待（15s/30s、僅匹配 `'429'` 字串），高頻 Embedding 會削爆全域 API 配額連帶拖垮 LLM。
- **解法**（原子化拆 4 commit）：
  - `C1 — Settings Knob（限流參數初始化）`：`settings.py` 新增 `EMBEDDING_MAX_CONCURRENT`（預設 5、env 可調）。
  - `C2 — Embedding Resilience Core（限流與退避框架重構）`：`config.py` EmbeddingModel 引入 class-level Semaphore + 全面套 `@retry_call` + 重構 `embed_documents`/`_embed_batch`/`_embed_one` 降級 + 429 觀測 log；附帶同步 `tiling_processor.py` 過時註解。
  - `C3 — Unit Tests（限流與重試契約測試）`：新建 `tests/test_embedding_retry.py` 4 測試。
  - `C4 — Checkout（收官與 baton 檔案歸檔）`：Conformance 驗收 + 一次性 mv 歸檔 + TODO 結案。
- **影響範圍**：`settings.py` + `config.py` + 1 測試檔 + `tiling_processor.py` 註解；**不改 embedding 向量值（embed_content 參數不變）→ 不觸發 Golden Baseline 重捕、可與 RESUME-P3 解耦獨立先做**；無 DB Schema 變動。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `config.py` `_embed_one` L74-94 | 手動 `for attempt in range(3)` + `time.sleep(15*(attempt+1))` linear 等待、硬編碼 `'429' in str(e)` | 僵硬、阻塞、僅防 429 字串、無 Semaphore |
| `config.py` `embed_documents` L96-146 | 手動 retry 迴圈 + linear 等待、失敗退 `_embed_one` | 同上；批次邏輯與重試耦合、無 Semaphore |
| `config.py` `embed_query` L148-158 | 直接 `embed_content`、無任何 retry | 撞 429/5xx 即崩、無 Semaphore |
| `config.py` `embed_image` L160-172 | 直接 `embed_content`、無任何 retry | 同上 |
| `settings.py` L73 | 有 `LLM_MAX_CONCURRENT=6`、無 `EMBEDDING_MAX_CONCURRENT` | Embedding 無併發上限 |
| `llm/retry.py` L58 | `retry_call(retries,base)` 裝飾器工廠（Full Jitter 指數退避）已就緒 | 既有資產、直接複用（不改） |
| `llm/client.py` L49 | `_api_semaphore = threading.Semaphore(LLM_MAX_CONCURRENT)` + `with` 用法 | 既有對齊範例（不改） |
| `processor/tiling_processor.py:425` | TILING-HOTFIX-1 呼叫 `embed_documents(blocks)`、註解寫「線性退避 15s/30s」 | C2 後該註解過時、需同步更新文字 |

---

## §3 觀察問題

### 問題 #1：Embedding 無併發限流、削爆全域配額
- **證據**：`file:///config.py#L96`（embed_documents 無 Semaphore）、`file:///llm/client.py#L49`（LLM 有 Semaphore、Embedding 無對應）。
- **影響**：高頻 Embedding 瞬間佔滿全域 API quota → 同帳號 LLM 對話連帶 429 崩潰。

### 問題 #2：基建端無統一退避，手動 linear 等待僵硬
- **證據**：`file:///config.py#L92`（`time.sleep` linear）、`file:///config.py#L148`（embed_query 無 retry）。
- **影響**：撞暫時性錯誤（429/5xx/timeout/disconnect）即崩；linear 等待阻塞線程、未享 Full Jitter 指數退避。

---

## §4 設計方案

### §4.1 C1 — Settings Knob（限流參數初始化）
`settings.py` 新增 `EMBEDDING_MAX_CONCURRENT = int(os.getenv("EMBEDDING_MAX_CONCURRENT", "5"))`（緊鄰 L73 `LLM_MAX_CONCURRENT`、風格一致）。`# === [MODEL-9-OPT C1 START/END] ===` 包裹 + 改前 `.bak`。

### §4.2 C2 — Embedding Resilience Core（限流與退避框架重構）
`config.py` `EmbeddingModel`：
1. import `threading` + `from llm.retry import retry_call` + `from settings import EMBEDDING_MAX_CONCURRENT`。
2. class 屬性 `_api_semaphore = threading.Semaphore(EMBEDDING_MAX_CONCURRENT)`。
3. `embed_query` / `embed_image`：裝 `@retry_call(retries=3, base=2.0)`、內部 `with self._api_semaphore:` 包 API 呼叫。
4. 新增 `@retry_call(retries=3, base=2.0)` 的 `_embed_batch(self, batch)`：`with semaphore:` 呼 `embed_content`（batch 32、task_type/dim 不變）+ 數量驗證 + `_l2_normalize`，回 normalized list。
5. `embed_documents`：移除手動 retry/sleep 迴圈，逐批呼 `_embed_batch`；捕獲耗盡異常 → warning + 逐筆 `_embed_one` 降級（保序）。
6. `_embed_one`：裝 `@retry_call(retries=2, base=2.0)`（fallback 收斂巢狀深度）、移除手動 `for`/`sleep`、`with semaphore:` 包 API。
7. 429 觀測：退避命中以 `logger.warning(..., extra={'extra_fields': {'event': 'embedding_429', ...}})` 記錄（logging SOP）。
8. 同步更新 `tiling_processor.py:425` 的 TILING-HOTFIX-1 退避註解文字（線性→Full Jitter）。
`# === [MODEL-9-OPT C2 START/END] ===` 包裹 + 二檔（config.py / tiling_processor.py）改前 `.bak`。

### §4.3 C3 — Unit Tests（限流與重試契約測試）
新建 `tests/test_embedding_retry.py` 4 測試（mock `client.models.embed_content`、不實打 API）：A embed_query 429 退避成功 / B embed_image 503 重試成功 / C embed_documents 批次降級逐筆保序 / D Semaphore 併發上限。

### §4.4 C4 — Checkout（收官與 baton 檔案歸檔）
Conformance 三維度驗收 + SOP 核查 → 一次性 `mv` baton plan→`plans/`、C1-C4 `_執行.md`→`executions/` + `git add` + TODO 結案。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C2 改 `embed_documents` 破壞 TILING-HOTFIX-1 呼叫端 | 🟡 中 | 對外簽名與回傳（依序 normalized list）byte 不變；跑 `test_tiling_paragraph` 防 Regression |
| Semaphore 與 retry 互動死鎖 | 🟢 低 | `@retry_call` 外層 + `with semaphore` 內層 → 重試 sleep 前先 release（對齊 `llm/client.py` 既有範例） |
| 改動意外變更向量值 → 污染 Golden | 🟢 低 | `embed_content` 參數（model/task_type/dim/batch=32）+ `_l2_normalize` 一律不動；C3 斷言 normalized 行為 |
| 巢狀重試（batch→逐筆）尾巴過長 | 🟢 低 | `_embed_one` fallback 用 `retries=2` 收斂深度 |
| 全域配額仍撞 429（併發≠RPM） | 🟡 中 | env 可調 + 429 log 觀測；plan §7 OQ3 記錄「撞不過才上 token bucket」 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
grep -nE "EMBEDDING_MAX_CONCURRENT" settings.py            # 期望：命中 + 預設 5
grep -nE "MODEL-9-OPT C1" settings.py                      # 期望：標記包裹
```

### §6.2 C2 驗收
```bash
grep -nE "_api_semaphore|threading.Semaphore" config.py    # 期望：class-level Semaphore
grep -nE "@retry_call" config.py                           # 期望：embed_query/image/_embed_batch/_embed_one 命中
grep -nE "def _embed_batch" config.py                      # 期望：新輔助方法
grep -nE "time\.sleep|for attempt in range" config.py      # 期望：0 命中（手動 linear 已移除）
grep -nE "embedding_429|extra_fields" config.py            # 期望：429 觀測 log
grep -nE "Full Jitter|retry_call|指數退避" processor/tiling_processor.py  # 期望：註解已更新（不再「線性退避」）
# SOP 核查
grep -nE "logger\.error|traceback.format_exc" config.py | grep -v exc_info=True   # 期望：無不合規
grep -nE "\.commit\(\)" config.py                          # 期望：0（無 DB 交易）
```

### §6.3 C3 驗收
```bash
venv/bin/python -m pytest tests/test_embedding_retry.py -q          # 期望：4 passed
venv/bin/python -m pytest tests/test_embedding_normalize.py tests/test_llm_retry.py tests/test_tiling_paragraph.py -q  # 期望：不退化
venv/bin/python -m pytest tests/ -q                                  # 期望：僅既存 env flake
```

### §6.4 C4 驗收（Checkout）
```bash
ls .claude-logs/plans/ | grep MODEL-9-OPT                  # plan 已歸檔
ls .claude-logs/executions/ | grep MODEL-9-OPT             # C1-C4 報告已歸檔
ls .claude-logs/baton/ | grep MODEL-9-OPT || echo 已移清
```

---

## §7 不可動清單

- [ ] `llm/retry.py`（`_RETRYABLE_TOKENS` / `retry_call` / `retry_stream`）— 100% 不動（僅複用）。
- [ ] `llm/client.py`（`LLMClient` 初始化與 `LLM_MAX_CONCURRENT` 信號量）— 不動。
- [ ] `config.py` `EmbeddingModel._l2_normalize` 邏輯 — 不動（防向量 norm 出錯）。
- [ ] `embed_content` 呼叫參數（`model`/`task_type`/`output_dimensionality`/batch=32）— 不動（保證向量值不變、Golden 無關前提成立）。
- [ ] `processor/tiling_processor.py:425` 邏輯本體 — 不動（僅改 inline 註解文字）。
- [ ] 既有 RAG 檢索（`rag_retriever.py`）與雙軌 dispatch — 不動。
- [ ] `pipeline_core.py` / `web_server.py` 等業務代碼 — 100% 不動。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — Settings Knob（限流參數初始化）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `settings.py`（新增 `EMBEDDING_MAX_CONCURRENT`）+ `.claude-logs/archive/2026-06-05_MODEL-9-OPT_C1_settings.py.bak` |
| **安全性** | 🟢 高 — 純新增常數、預設值等價無行為改變（C2 才消費） |
| **可逆性** | 🟢 高 — `git revert C1` |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | 1) `cp settings.py .bak`。2) 於 `settings.py:73 LLM_MAX_CONCURRENT` 下一行新增 `# === [MODEL-9-OPT C1 START] ===` / `EMBEDDING_MAX_CONCURRENT = int(os.getenv("EMBEDDING_MAX_CONCURRENT", "5"))` / `# === [MODEL-9-OPT C1 END] ===`。3) 產 `baton/2026-06-05_MODEL-9-OPT_C1_執行.md`。**不動 config.py。** |

### C2 — Embedding Resilience Core（限流與退避框架重構）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `config.py`（EmbeddingModel 重構）+ `processor/tiling_processor.py`（僅註解）+ 二檔 `.bak` |
| **安全性** | 🟡 中 — 重構核心 embedding 呼叫；以「對外簽名/回傳/向量值不變」+ Semaphore-retry 對齊 client 範例緩解 |
| **可逆性** | 🟢 高 — `git revert C2`（自 `.bak` 可還原） |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | C1（消費 `EMBEDDING_MAX_CONCURRENT`） |
| **具體實作細節** | 1) `cp config.py` / `cp processor/tiling_processor.py` → `.bak`。2) `config.py` import `threading`（若缺）+ `from llm.retry import retry_call` + `from settings import EMBEDDING_MAX_CONCURRENT`。3) `EmbeddingModel` 加 class 屬性 `_api_semaphore = threading.Semaphore(EMBEDDING_MAX_CONCURRENT)`。4) `embed_query`/`embed_image`：頂裝 `@retry_call(retries=3, base=2.0)`、body API 呼叫包 `with self._api_semaphore:`。5) 新增 `@retry_call(retries=3, base=2.0)` 的 `_embed_batch(self, batch)`：`with self._api_semaphore:` 呼 `self.client.models.embed_content(...)`（**model/task_type=RETRIEVAL_DOCUMENT/output_dimensionality/batch 維持原值**）+ 數量驗證 + `[self._l2_normalize(e.values) ...]` 回傳。6) `embed_documents`：刪手動 `for attempt`/`time.sleep`，改 `for start in range(0,total,32): batch=...; try: embeddings.extend(self._embed_batch(batch)) except Exception: logger.warning(...); embeddings.extend(self._embed_one(t) for t in batch)`（保序）。7) `_embed_one`：頂裝 `@retry_call(retries=2, base=2.0)`、刪手動 `for`/`sleep`、body 包 `with self._api_semaphore:`。8) 429 觀測：retry 命中點（或降級 warning）以 `logger.warning("...", extra={'extra_fields': {'event': 'embedding_429'}})`。9) `processor/tiling_processor.py:425` 區塊內 inline 註解「線性退避 15s/30s」改述為「`embed_documents` 內部經 `retry_call` Full Jitter 指數退避（MODEL-9-OPT 後）」——**僅改註解文字、不動該行邏輯**。10) 全 `config.py` 變更 `# === [MODEL-9-OPT C2 START/END] ===` 包裹；tiling 註解用 `# === [MODEL-9-OPT C2 START/END] ===` 標記。11) 產 `baton/..._C2_執行.md`（貼 §6.2 grep + SOP 核查結果）。 |

### C3 — Unit Tests（限流與重試契約測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_embedding_retry.py`（新建）|
| **安全性** | 🟢 高 — 純測試、mock 隔離不實打 API |
| **可逆性** | 🟢 高 — `git revert C3` |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | C1 + C2 |
| **具體實作細節** | 新建 `tests/test_embedding_retry.py`（`# === [MODEL-9-OPT C3 START/END] ===` 包裹、mock `EmbeddingModel.client.models.embed_content`）：A `test_embed_query_retry_success`（首呼拋 429、次呼成功 → 回 normalized）；B `test_embed_image_retry_success`（首呼 503、次成功）；C `test_embed_documents_fallback_on_error`（mock `_embed_batch` 拋 429 耗盡 → 斷言 warning + 逐筆 `_embed_one` + 合併保序）；D `test_embedding_semaphore_concurrency_limit`（高併發呼 embed_query、斷言同時 active ≤ `EMBEDDING_MAX_CONCURRENT`）。產 `baton/..._C3_執行.md`。 |

### C4 — Checkout（收官與 baton 檔案歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`；`mv` baton plan→`plans/`、C1-C4 報告→`executions/`；無業務代碼 |
| **安全性** | 🟢 高 — 純驗收 + 歸檔 |
| **可逆性** | 🟢 高 — mv 可逆 |
| **驗收 grep 條件** | §6.4 + Conformance（目標規格 plan §2 / §6 pytest+grep / 不可動清單 git 證據）+ SOP 核查 |
| **依賴關係** | C1-C3 全 ship |
| **具體實作細節** | 1) Conformance 三維度驗收 + SOP 核查貼 grep。2) `TODO.md`：MODEL-9-OPT 移入 ✅ 完成表（Hash 待回填）+ 移除 active + 索引。3) 一次性 `mv` baton plan→`plans/`、C1-C4 `_執行.md`→`executions/`（`mkdir -p`）+ `git add`。4) 確認 baton/ 無本任務殘留。5) msg 寫 `/tmp/`、嚴禁自發 commit/push。 |

---

## §9 Open Questions

無。（plan §7 OQ1-OQ3 已於 plan v3 審核結案：OQ1 各自獨立 Semaphore；OQ2 全用 retry_call；OQ3「併發≠RPM、暫採可觀測+可調、撞不過才上 token bucket」屬上線觀察項、非拆分阻斷。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 MODEL-9-OPT 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 MODEL-9-OPT executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改業務代碼（除 plan 授權的 config.py/settings.py/tiling 註解）；嚴禁自動 commit/push |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務收官歸檔、經 baron 同意移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡與 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：初版拆分——依 plan v3 拆 4 commit（C1 settings 限流參數 / C2 config EmbeddingModel Semaphore+retry_call 重構+tiling 註解同步+429 log / C3 test_embedding_retry 4 測試 / C4 Checkout）；§0.5 成果盤點 + §8 六維度；明載「不改向量值、不觸發 Golden 重捕、可獨立先做」+ `_embed_one` fallback retries=2。
