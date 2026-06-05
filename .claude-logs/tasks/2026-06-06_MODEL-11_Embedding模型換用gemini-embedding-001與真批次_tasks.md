# MODEL-11 Embedding 模型換用 gemini-embedding-001 與真批次 — Tasks

> 本文件為 MODEL-11 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-06_MODEL-11_Embedding模型換用gemini-embedding-001與真批次_plan_v1.md`（v2、§7 OQ Q1-Q8 核准）產出，含 4 個 Commit（C1 → C2 → C3 → C4 Checkout）。
> 工作流類別：**BE-Refactor**（改 `.py` 業務邏輯）→ 落地前強制 logging + database SOP 核查（§5）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （C3 沿用既有 `tests/test_embedding_retry.py` 追加測試，不新建檔）|
| **修改檔案** | 3 個 | `settings.py`（換模型預設 + 新增批次/token 常數）/ `config.py`（`EmbeddingModel` 真批次 + token-aware 拆批 + 修 log 命名）/ `tests/test_embedding_retry.py`（追加 -001 真批次 / 拆批保序 / task_type / 真 fallback 測試）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（高優先新增 → Checkout 結案）/ `prompts/INDEX.md`（Tasks + 各階段提示詞登錄）|
| **Commits** | 4 個 | C1 → C2 → C3 → C4（Checkout）|
| **baton 歸檔** | 1 次 | C4 Checkout 收官：一次性 `mv` plan_v1 → `plans/` + tasks → `tasks/` + C1-C4 報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：現用 `gemini-embedding-2` 是**多模態交錯**模型——SDK 對其特例 `t_contents()` 把 `contents=[N 段]` 併成單一 content → `embed_content` 只回 **1 個聚合向量** → `_embed_batch` 數量不符必拋 → `embed_documents` **永遠退逐筆**（序列、慢、log 誤標 `embedding_429`）；且該模型**不支援 task_type** → `RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY` 被忽略 → query/document 向量同質、**RAG 召回非對稱性喪失（品質打折，非僅效能）**。
- **解法**：原子化拆 4 個 commit——
  - **C1 — Settings Config（配置常數調整）**：`settings.py` 換 `EMBEDDING_MODEL` 預設 `gemini-embedding-001` + 新增批次段數軟上限 / 請求 token 硬約束 / 單段 token 上限三常數。
  - **C2 — EmbeddingModel 真批次（批次語意重構）**：`config.py` `embed_documents` 改 token-aware 貪婪拆批（≤100 段且累計 token 守 20,000）一次回 N 向量；`_embed_batch` 沿用既有 N→N 數量校驗（-001 正常通過、不再必退逐筆）；保留 `_embed_one` 為**真 fallback**；`embedding_429` log 正名為批次降級觀測；`task_type` 程式碼**已正確**（換模型後自動生效、無需改）。
  - **C3 — Unit Tests（單元測試追加）**：`tests/test_embedding_retry.py` 追加 4 測試（真批次 N→N 不退逐筆 / 超量自動拆批保序 / task_type 斷言 DOCUMENT+QUERY / 真 429 fallback 兜底）。
  - **C4 — Checkout（收官驗收歸檔）**：Conformance 三維度驗收 + SOP 核查 + baton 一次性歸檔。
- **影響範圍**：3 檔（`settings.py` / `config.py` / 測試）；**向量值改變**（換模型）→ 各環境手動 `regen_rag.py --all` 重嵌 + resume 單路 Golden 重捕（**屬 baron 運維、非本任務 commit**，見 §8 各 commit「運維註」）。`embed_image`（0 caller）保留無操作 stub、不啟用。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `settings.py:25` | `EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")` | 預設多模態模型；無批次段數 / token 約束常數 |
| `settings.py:29` | `EMBEDDING_OUTPUT_DIMENSIONS = 768` | ✅ 保留（Q1 核准、MRL 不變）|
| `settings.py:79` | `EMBEDDING_MAX_CONCURRENT = 5` | ✅ 保留（Semaphore、不改）|
| `config.py:112-131` `_embed_batch` | `contents=batch` → 對 -2 SDK 併成 1 → `len != len(batch)` 必拋 RuntimeError | -2 下必退逐筆；換 -001 後 N→N 正常（校驗邏輯本身正確、可沿用）|
| `config.py:133-168` `embed_documents` | `BATCH_SIZE=32` 固定段數、無 token 約束；except → 序列 `_embed_one`；log `event:'embedding_429'` | 固定段數可能撞 20,000 token/請求上限；`embedding_429` 命名誤導（實際多為數量不符、非 429）|
| `config.py:94-110` `_embed_one` | `contents=[text]`、`task_type=RETRIEVAL_DOCUMENT` | ✅ 保留為真 fallback（Q4）|
| `config.py:170-182` `embed_query` | `task_type=RETRIEVAL_QUERY` | ✅ 程式碼已正確（換模型後生效、不改）|
| `config.py:184-197` `embed_image` | 多模態、`task_type=RETRIEVAL_DOCUMENT` | 全專案 0 caller（Q6）→ 保留無操作 stub、不啟用、不刪 |

---

## §3 觀察問題

### 問題 #1：批次永遠退逐筆（效能病灶）
- **證據**：`config.py:127-130`（`if len(result.embeddings) != len(batch): raise RuntimeError`）+ SDK `google-genai 2.3.0` `if 'gemini-embedding-2' in model: contents = t.t_contents(contents)`（list 併成 1）。
- **影響**：`embed_documents` 每批必拋 → `embed_documents:151-163` except 退序列逐筆 → 大量 chunk embed 無並行、慢；log 誤標 `embedding_429`（實為數量不符、HTTP 200）。

### 問題 #2：task_type 失效（召回品質缺陷）
- **證據**：plan §5 官方⑤——task_type 支援清單含 `gemini-embedding-001`、**不含 `-2`**；`config.py:106 / :123`（DOCUMENT）vs `:178`（QUERY）程式碼已分流、但 -2 忽略之。
- **影響**：query 與 document 向量同質、非對稱語意檢索喪失 → RAG 召回打折（非僅慢）。

### 問題 #3：固定 32 段批次無 token 約束（潛在 400 風險）
- **證據**：`config.py:139 BATCH_SIZE=32`；-001 約束 20,000 token/請求、2,048 token/段（plan §5 官方④）。
- **影響**：長 chunk 拼 32 段可能超 20,000 token → 換 -001 後該批 400 失敗退逐筆（雖有兜底、但喪失批次效益）。

---

## §4 設計方案

### §4.1 C1 — Settings Config（配置常數調整）
`settings.py`：① L25 預設 `gemini-embedding-2` → `gemini-embedding-001`（env `EMBEDDING_MODEL` 仍可覆寫）；② 於 embedding 區塊（L29 附近）追加三常數——`EMBEDDING_BATCH_MAX_ITEMS`（段數軟上限、預設 100，對齊 Q2）/ `EMBEDDING_BATCH_MAX_TOKENS`（請求 token 硬約束、預設 18000，對 20,000 留 buffer）/ `EMBEDDING_MAX_TOKENS_PER_ITEM`（單段 token 上限、預設 2048）。純常數新增、C2 才消費、行為等價（C1 自身不改任何呼叫）。

### §4.2 C2 — EmbeddingModel 真批次與 token-aware 拆批（批次語意重構）
`config.py` `EmbeddingModel`（`MODEL-9-OPT C2` 標記區內、以 `MODEL-11 C2` 子標記包裹改動）：
1. `embed_documents`：固定 `BATCH_SIZE=32` → **token-aware 貪婪拆批**——逐段累加，遇「段數達 `EMBEDDING_BATCH_MAX_ITEMS`」或「累計 token 估值將超 `EMBEDDING_BATCH_MAX_TOKENS`」即封批；單段估值超 `EMBEDDING_MAX_TOKENS_PER_ITEM` 記 warning（不截斷、交由 API/兜底）。token 估值用**保守字元代理**（`max(1, len(text))` 直接當 token 上界估計、CJK 安全；不呼叫 count_tokens 避免額外 API）。保序拼接不變。
2. `_embed_batch`：簽名/數量校驗**不變**（接收變長 batch；-001 回 N→N 正常通過、不再必拋）。
3. **真 fallback 不變**：except 仍退 `_embed_one` 逐筆（Q4）。
4. **log 正名**：`event:'embedding_429'` → `event:'embedding_batch_fallback'` + 加 `reason` 欄（`str(e)` 摘要、區分真 429/timeout/數量不符）。
5. `task_type`：**程式碼已正確、不改**（DOCUMENT 整批 / QUERY 單筆、Q3）；僅靠 C1 換模型後 API 生效。
6. `embed_image`：**保留無操作 stub、不改**（Q6、0 caller）。
7. 更新 `MODEL-9-OPT C2` 區塊頂部「batch=32」「不影響 Golden Baseline」過時註解——改註明「MODEL-11 起 token-aware 拆批 + 換 -001 → **向量值改變、須 regen_rag --all + Golden 重捕**」。

### §4.3 C3 — Unit Tests（單元測試追加）
`tests/test_embedding_retry.py` 追加 4 測試（mock `client.models.embed_content`，不打真 API）：
- `test_embed_documents_real_batch_no_fallback`：mock 回 N（對齊 -001）→ `embed_documents` 一次批次回 N 向量、`_embed_one` **0 呼叫**、保序。
- `test_embed_documents_auto_split_preserves_order`：>`EMBEDDING_BATCH_MAX_ITEMS` 段或長段觸 token 上限 → 自動拆多批、合併保序。
- `test_task_type_document_vs_query`：斷言 `embed_documents` 走批次傳入 `task_type=RETRIEVAL_DOCUMENT`、`embed_query` 傳入 `RETRIEVAL_QUERY`。
- `test_embed_batch_429_falls_back_to_one`：mock `_embed_batch` 拋 429 → 退 `_embed_one` 逐筆兜底、結果保序（真 fallback 不減）。

### §4.4 C4 — Checkout（收官驗收歸檔）
Conformance 三維度（目標規格 U1-U7 / tasks §6 / 不可動清單 git 證據）+ SOP 核查 + 提示詞稽核 + msg 完整性 + baton 一次性歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 換模型後向量空間位移、新舊混庫不可比 | 🟡 中 | Q5：各環境 `regen_rag.py --all` 全量重嵌（index_meta stale 偵測現成）；運維由 baron 手動、非 commit |
| token 估值過保守 → 批次偏小、效益縮水 | 🟢 低 | 字元代理為**上界**（實際 token ≤ 字元數）、僅偏安全；可 env 調 `EMBEDDING_BATCH_MAX_TOKENS` |
| token 估值過樂觀 → 撞 20,000 → 400 | 🟢 低 | 字元代理為上界、不會低估；且 `_embed_one` 兜底 |
| `embedding_429` 改名破壞既有 log 查詢/告警 | 🟢 低 | 該 event 為 MODEL-9-OPT 新增、無下游告警依賴（grep 證）；改名提升正確性 |
| Golden Baseline 失效誤報 | 🟡 中 | C2 註解明示須重捕；resume 單路 `capture resume --force`（baron 運維、非 commit）|

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
grep -n 'EMBEDDING_MODEL.*gemini-embedding-001' settings.py        # 期望：L25 命中（預設已換）
grep -nc 'gemini-embedding-2' settings.py                          # 期望：0（預設不再 -2）
grep -n 'EMBEDDING_BATCH_MAX_ITEMS\|EMBEDDING_BATCH_MAX_TOKENS\|EMBEDDING_MAX_TOKENS_PER_ITEM' settings.py  # 期望：3 常數命中
venv/bin/python -c "import settings; print(settings.EMBEDDING_MODEL_NAME, settings.EMBEDDING_BATCH_MAX_ITEMS, settings.EMBEDDING_BATCH_MAX_TOKENS, settings.EMBEDDING_MAX_TOKENS_PER_ITEM)"  # 期望：gemini-embedding-001 100 18000 2048
venv/bin/python -m pytest tests/ -q   # 期望：C1 純常數新增、不退化（全套件綠 / 僅 env flake）
```

### §6.2 C2 驗收
```bash
grep -n 'MODEL-11 C2' config.py                                    # 期望：START/END 子標記命中
grep -n "event': 'embedding_batch_fallback'" config.py             # 期望：命中（log 已正名）
grep -nc "event': 'embedding_429'" config.py                       # 期望：0（舊誤導命名已移除）
grep -n 'EMBEDDING_BATCH_MAX_ITEMS\|EMBEDDING_BATCH_MAX_TOKENS' config.py   # 期望：embed_documents 消費常數
grep -n 'BATCH_SIZE = 32' config.py                                # 期望：0（固定 32 已移除）
# SOP — logging：用 logger.error 須 exc_info=True
grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' config.py   # 期望：無不合規（降級用 logger.warning）
# SOP — database：無裸 commit
grep -nE '\.commit\(\)' config.py | grep -v 'with .*session.*begin'           # 期望：無命中（embedding 不碰 DB）
venv/bin/python -m pytest tests/test_embedding_retry.py -q          # 期望：既有測試不退化（C2 後若有依賴 32 的舊測試需 C3 對齊）
```

### §6.3 C3 驗收
```bash
grep -n 'def test_embed_documents_real_batch_no_fallback\|def test_embed_documents_auto_split_preserves_order\|def test_task_type_document_vs_query\|def test_embed_batch_429_falls_back_to_one' tests/test_embedding_retry.py  # 期望：4 新測試命中
venv/bin/python -m pytest tests/test_embedding_retry.py -q          # 期望：全綠（含 4 新測試）
venv/bin/python -m pytest tests/ -q                                # 期望：全套件綠（僅既知 env flake test_settings_log_format_default_auto）
```

### §6.4 C4 Checkout 驗收
- 三維度全綠（U1-U7：U6 遷移 / U7 Golden 屬 baron 運維、代碼層以 grep+測試自證機制就緒即達標）。
- baton 一次性歸檔；`ls .claude-logs/baton/` 僅餘 `README.md`。

---

## §7 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **`config.py` `_l2_normalize`**（768 維 L2 正規化）— 不改（保 cosine 等價、U5）
- [ ] **`llm/retry.py` `retry_call` / `_api_semaphore` 機制** — 不改（沿用）
- [ ] **`config.py` `embed_query` task_type / `_embed_one` 介面** — 不改邏輯（C2 僅 embed_documents 拆批 + log 命名）
- [ ] **`config.py` `embed_image`** — 不刪、不改（保留無操作 stub、Q6）
- [ ] **`processor/rag_processor.py`** 切 chunk（`MarkdownHeaderTextSplitter`）+ `_is_chunk_meaningful` 過濾 + index_meta 寫入 — 不改
- [ ] **A 軌（`pipeline_core.py` / `translate_processor.py`）/ `pipelines/` / `contracts.py` / 母提示詞 / `models.py` / `db.py` / API / 前端** — 100% 不動
- [ ] **`tools/regen_rag.py` / `tools/golden_baseline.py`** — 不改（遷移/重捕機制現成、屬 baron 運維）
- [ ] **主 repo 目錄** — 嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C1 — Settings Config（配置常數調整）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `settings.py`（L25 預設換模型 + L29 附近追加 3 常數）+ `.bak` 備份 `archive/2026-06-06_MODEL-11_C1_settings.py.bak`（修改既有檔鐵律）|
| **安全性** | 🟢 高 — 純常數新增 + 1 處預設字串換；C2 才消費；C1 自身行為等價（除預設模型名）|
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；env `EMBEDDING_MODEL=gemini-embedding-2` 可即時切回舊行為 |
| **驗收 grep 條件** | §6.1（4 條：預設換 -001 / 0 處 -2 / 3 常數存在 / import 印值正確 / pytest 不退化）|
| **依賴關係** | 無前置（首 commit）|
| **具體實作細節** | 1. **先備份**：`cp settings.py .claude-logs/archive/2026-06-06_MODEL-11_C1_settings.py.bak`（git add 納入）。2. `settings.py:25` 改 `EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")`；同行/上方註解補「MODEL-11：換文字 embedding GA、支援真批次 + task_type」。3. 於 L29（`EMBEDDING_OUTPUT_DIMENSIONS` 之後）追加：`# === [MODEL-11 C1] embedding 批次/token 約束（gemini-embedding-001：≤250 段 / 20,000 token/請求 / 2,048 token/段）===` + `EMBEDDING_BATCH_MAX_ITEMS = int(os.getenv("EMBEDDING_BATCH_MAX_ITEMS", "100"))`（段數軟上限、Q2 防禦保守值）+ `EMBEDDING_BATCH_MAX_TOKENS = int(os.getenv("EMBEDDING_BATCH_MAX_TOKENS", "18000"))`（請求 token 硬約束、對 20,000 留 buffer）+ `EMBEDDING_MAX_TOKENS_PER_ITEM = int(os.getenv("EMBEDDING_MAX_TOKENS_PER_ITEM", "2048"))`（單段上限）。4. 不動 `EMBEDDING_OUTPUT_DIMENSIONS` / `EMBEDDING_MAX_CONCURRENT` / `RAG_SCORE_THRESHOLD`。5. 產 `baton/2026-06-06_MODEL-11_C1_執行.md`。**運維註**：本 commit 落地後**尚未**改向量產生邏輯，無須重嵌。|

---

### C2 — EmbeddingModel 真批次與 task_type（批次語意重構）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `config.py`（`embed_documents` token-aware 拆批 + log 正名 + 過時註解更新；`_embed_batch` 簽名不變）+ `.bak` 備份 `archive/2026-06-06_MODEL-11_C2_config.py.bak` |
| **安全性** | 🟡 中 — 改批次切分與 log；**向量值改變**（源於 C1 換模型，非 C2 演算法）；`_l2_normalize`/task_type 程式碼/`_embed_one` 兜底皆不動 → 行為可預期 |
| **可逆性** | 🟢 高 — `git revert C2`（+ C1）完全回滾；MODEL-11 子標記包裹便於定位 |
| **驗收 grep 條件** | §6.2（子標記 / log 正名 / 0 處舊命名 / 消費常數 / 0 處 BATCH_SIZE=32 / SOP logging+database）|
| **依賴關係** | 前置 C1（消費 `EMBEDDING_BATCH_MAX_*` 常數）|
| **具體實作細節** | 1. **先備份** `config.py` → `.bak`（git add）。2. `embed_documents`（L133-168）：以 `# === [MODEL-11 C2 START] ===` / `END` 子標記包裹改動段；移除 `BATCH_SIZE = 32` 與 `range(0, total, BATCH_SIZE)` 固定切分，改為 **token-aware 貪婪封批 helper**——`from settings import EMBEDDING_BATCH_MAX_ITEMS, EMBEDDING_BATCH_MAX_TOKENS, EMBEDDING_MAX_TOKENS_PER_ITEM`（檔頭 import）；逐 `text` 累加進 `cur_batch`，估 token `est = max(1, len(text))`（保守上界、CJK 安全）；若 `est > EMBEDDING_MAX_TOKENS_PER_ITEM` → `logger.warning('單段 token 估值超上限', extra={'extra_fields':{'event':'embedding_oversized_item','est_tokens':est}})`（不截斷）；封批條件：`len(cur_batch) >= EMBEDDING_BATCH_MAX_ITEMS` 或 `cur_tokens + est > EMBEDDING_BATCH_MAX_TOKENS`（且 `cur_batch` 非空）→ 先 flush 再起新批；flush = `try: embeddings.extend(self._embed_batch(cur_batch))` `except: <逐筆兜底>`。3. **log 正名**：except 區塊的 `extra_fields` `'event': 'embedding_429'` → `'event': 'embedding_batch_fallback'` + 加 `'reason': str(e)[:200]`；warning 文案改「批次失敗（{e}）退逐筆」。4. `_embed_batch`（L112-131）：**不改**（變長 batch、N→N 校驗沿用）。5. `_embed_one`（L94-110）/ `embed_query`（L170-182）/ `embed_image`（L184-197）：**不改**。6. 更新 `MODEL-9-OPT C2` 區塊頂部 L88-92 過時註解：把「batch=32」「向量值逐一相同、不影響 Golden Baseline」改註「MODEL-11：token-aware 拆批；換 gemini-embedding-001 後**向量值改變、須各環境 regen_rag.py --all + Golden 重捕**」。7. 產 `baton/2026-06-06_MODEL-11_C2_執行.md`（**必貼 §5 SOP grep 結果**：logging 無不合規 / database 無裸 commit）。**運維註**：C2 落地後須由 baron 各環境跑 `regen_rag.py --all`、resume 單路 `golden_baseline.py capture resume --force`（非本 commit）。|

---

### C3 — Unit Tests（單元測試追加）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_embedding_retry.py`（追加 4 測試 + 對齊既有依賴 `BATCH_SIZE=32` 的舊測試〔若有〕）|
| **安全性** | 🟢 高 — 純測試、mock 隔離不打真 API、零 runtime 影響 |
| **可逆性** | 🟢 高 — `git revert C3` 完全回滾 |
| **驗收 grep 條件** | §6.3（4 新測試命中 + 檔級 pytest 全綠 + 全套件綠）|
| **依賴關係** | 前置 C1 + C2 |
| **具體實作細節** | 1. 讀既有 `tests/test_embedding_retry.py`（MODEL-9-OPT C3 建）確認 mock 模式（mock `EmbeddingModel.client.models.embed_content` 回 `types` 結構）。2. **先對齊**：若既有測試斷言固定 32 批次或舊 `embedding_429` event 名 → 改為對齊 C2（token-aware / `embedding_batch_fallback`）。3. 追加 4 測試（§4.3）：`test_embed_documents_real_batch_no_fallback`（mock embed_content 回 `len==len(batch)` → 斷言 `_embed_one` 未被呼叫〔用 `unittest.mock.patch.object` spy〕、回 N、保序）；`test_embed_documents_auto_split_preserves_order`（造 >100 段 或數筆超長段 → 斷言 embed_content 被呼叫 ≥2 次、合併結果順序＝輸入順序）；`test_task_type_document_vs_query`（捕 `embed_content` 的 `config.task_type`、斷言批次=RETRIEVAL_DOCUMENT、`embed_query`=RETRIEVAL_QUERY）；`test_embed_batch_429_falls_back_to_one`（`patch.object(model, '_embed_batch', side_effect=<429-like>)` → 斷言退 `_embed_one`、結果長度=輸入、保序）。4. 產 `baton/2026-06-06_MODEL-11_C3_執行.md`。|

---

### C4 — Checkout（收官驗收與一次性歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（結案）+ `prompts/INDEX.md` + baton 一次性 `mv` 歸檔（plan_v1 → `plans/` + tasks → `tasks/` + C1-C4 報告 → `executions/`）+ `git add`；無業務代碼 |
| **安全性** | 🟢 高 — 純驗收 + 文件搬移 |
| **可逆性** | 🟢 高 — 文件層級、git 可回滾 |
| **驗收 grep 條件** | §6.4（三維度全綠 + baton 僅餘 README.md）|
| **依賴關係** | 前置 C1 + C2 + C3 全 ship |
| **具體實作細節** | 1. **維度一目標規格**（plan §2 U1-U7）：U1 換模型〔grep settings 命中 -001〕/ U2 真批次〔C2 token-aware〕/ U3 task_type〔程式碼分流 + 換模型生效〕/ U4 移除死路+修 log〔grep 0 處 embedding_429〕/ U5 _l2_normalize 不變〔不可動清單 git diff〕/ U6 遷移〔regen_rag 機制現成、屬運維〕/ U7 Golden 重捕〔C2 註解明示、屬運維〕→ 逐項判定（U6/U7 標「機制就緒、屬 baron 運維」）。2. **維度二測試**（tasks §6）：貼 C1-C3 grep + `pytest tests/ -q` 真實輸出（全套件綠 / 僅 env flake）。3. **維度三不可動清單**（§7）：`git show --stat` 證 C1-C3 僅動 `settings.py`/`config.py`/`tests/test_embedding_retry.py`、A 軌/pipelines/_l2_normalize/embed_image/rag_processor 零命中。4. **SOP 核查**：貼 logging（config.py 無 logger.error 缺 exc_info）+ database（無裸 commit）grep 結果。5. **提示詞稽核**：`ls prompts | grep MODEL-11` ≥ Tasks + C1-C3 run + Check。6. **msg 完整性**：C1-C4 報告 §8.2 均含 msg 草稿。7. **baton 一次性歸檔**：`mv` plan_v1 → `plans/`、tasks → `tasks/`、C1-C4 `_執行.md` → `executions/` + `git add`。8. **TODO 結案**：MODEL-11 從 active 移除 → 寫入 ✅ 完成表（C1-C4 + hash 待回填）+ 同步索引。9. 產 `baton/2026-06-06_MODEL-11_C4_執行.md`（含收官清單 + msg）。**運維提醒（寫入報告 §7）**：baron 各環境 `git pull` 後跑 `venv/bin/python tools/regen_rag.py --all`（重嵌、chunk 數須一致、index_meta model=gemini-embedding-001）+ 視需要 `tools/golden_baseline.py capture resume --force`（單路重捕、其餘四路無 B 軌不捕）。|

---

## §9 Open Questions

無。（plan v2 §7 Q1-Q8 已於階段 3 由 baron 全數核准結案。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 MODEL-11 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 MODEL-11 executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改動不可動清單（§7）；嚴禁跨 Commit 混合；嚴禁自動 git commit/push；BE-Refactor 落地前強制 SOP 核查 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡與 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-06)：初版拆分——依 plan v2（§7 OQ Q1-Q8 核准）拆 4 commit：C1 Settings Config（換 -001 預設 + 批次/token 三常數）/ C2 EmbeddingModel 真批次（token-aware 貪婪拆批 + log 正名 embedding_batch_fallback + 過時註解更新；task_type/_embed_one/embed_image 不動）/ C3 Unit Tests（真批次 N→N / 拆批保序 / task_type / 真 fallback 4 測試）/ C4 Checkout（三維度驗收 + SOP 核查 + baton 一次性歸檔）。向量值改變、regen_rag --all + resume 單路 Golden 重捕屬 baron 運維、非 commit。
