# MODEL-11 Embedding 模型換用 gemini-embedding-001 與真批次 plan

> 定義將 RAG embedding 模型由 `gemini-embedding-2`（多模態交錯、不支援文字 list 批次與 task_type）換為 `gemini-embedding-001`（文字 embedding、支援 ≤250 段/請求真批次 + task_type）的目標規格：一併修復「批次永遠退逐筆」效能病灶與「task_type 失效 → query/doc 非對稱性喪失」的 RAG 召回品質缺陷。純規格、不含實作細節。

---

## §0 改版規則
- 改版觸發：§1–§7 任一規格變動 → 直接改章節 + §99.2 加 Revision
- 完整治理規格 → §99

---

## §1 TL;DR（概要）
- **挑戰**：現用 `gemini-embedding-2` 是**多模態交錯**模型，對純文字 RAG 是錯誤選擇:
  1. **無文字 list 批次**：SDK 對 `gemini-embedding-2` 特例 `t_contents()` 把 list 併成單一 content → `embed_content(contents=[N段])` 只回 **1 個聚合向量** → `_embed_batch` 每批數量不符 → **永遠退逐筆**（序列、慢；log 誤標 `embedding_429`）。
  2. **不支援 task_type**：`embed_query`(RETRIEVAL_QUERY) 與 `embed_documents`(RETRIEVAL_DOCUMENT) 唯一差別被忽略 → **query/document 向量同質、非對稱性喪失 → RAG 召回品質被打折**（非僅效能）。
- **解法**：換 `EMBEDDING_MODEL_NAME=gemini-embedding-001`（文字 embedding GA、保留 768 維 MRL）：
  - `embed_documents` 改用**真批次**（`contents=[≤250 段]` 一次回 N 向量、受 20,000 token/請求 + 2,048 token/段約束），保留 `_embed_one` 為**真 fallback**（429/timeout）。
  - `task_type` 生效 → 文件 RETRIEVAL_DOCUMENT / 查詢 RETRIEVAL_QUERY 恢復非對稱 → 召回品質提升。
  - 移除「批次必數量不符」死路與誤導 `embedding_429` log。
- **影響**：改 `settings.py`（模型名）+ `config.py`（EmbeddingModel 批次/退避/log）。**向量值改變** → 須 `tools/regen_rag.py --all` 重嵌既有 paper（機制現成、index_meta 記 model 名）+ Golden Baseline 重捕。`embed_image`（多模態）**全專案 0 caller**、換模型不破壞現況。`_l2_normalize` / `retry_call` / `Semaphore` 不變。
- **實測佐證**（Dev API、`venv/bin/python` 探針）：`gemini-embedding-001: embeddings=3 dim=768`（真批次 ✓）；`gemini-embedding-2: embeddings=1 dim=768`（融合、證實現況）。

---

## §2 目標規格
- **U1 模型換用**：`EMBEDDING_MODEL_NAME` 預設 `gemini-embedding-001`（env 可覆寫）；輸出維度保留 768（MRL `output_dimensionality`）。
- **U2 文字真批次**：`embed_documents` 以 `embed_content(contents=[batch])` 一次取得 **N 個向量**（N=批次段數）；批次上限守 **≤250 段/請求** 且總 token ≤ 20,000、單段 ≤ 2,048（超限策略見 §7）。
- **U3 task_type 生效**：`embed_documents` 用 `RETRIEVAL_DOCUMENT`、`embed_query` 用 `RETRIEVAL_QUERY`，兩者向量**確實不同**（恢復 query/doc 非對稱）。
- **U4 移除死路 + 修 log**：刪除「批次必數量不符 → 退逐筆」的必然路徑；`embedding_429` 觀測 log 正名（區分真 429 / timeout / 數量不符）；保留 `_embed_one` 為**真 fallback**（429/timeout/數量不符時逐筆兜底）。
- **U5 向量正確性不變**：`_l2_normalize` + 768 維 + FAISS inner product = cosine 不變（僅模型來源換）。
- **U6 既有資料遷移**：提供/沿用 `regen_rag.py --all` 重嵌全量既有 paper（index_meta `embedding_model` 由 mismatch 偵測觸發）；遷移前後 chunk 數一致。
- **U7 Golden 重捕**：模型換用改變向量 → 與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 / RESUME-P3 合併重捕黃金基準後，D3 召回以新基準裁決。

---

## §3 現況與證據
- **`config.py` `EmbeddingModel`**：
  - `_embed_batch L112-131`：`embed_content(model=gemini-embedding-2, contents=batch, …)` → 對 -2 SDK 併成 1 → `len(result.embeddings)=1 != len(batch)` → raise → 退逐筆。
  - `embed_documents`：逐批呼 `_embed_batch`，except → **序列** `_embed_one` 逐筆（無並行）。
  - `embed_query L170-184` / `_embed_one`：`contents=[單段]` → 1 向量（對 -2 正確、但 task_type 被忽略）。
  - `embed_image L?`：多模態、**全專案 0 caller**（grep 證）。
- **`settings.py` L25**：`EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")`。
- **`processor/rag_processor.py`**：index_meta 記 `embedding_model=EMBEDDING_MODEL_NAME`、`dim`；切 chunk 用 `MarkdownHeaderTextSplitter`（與模型無關）。
- **`tools/regen_rag.py:57`**：`p['embedding_model'] == settings.EMBEDDING_MODEL_NAME` → mismatch 即判定 stale、`--all` 重嵌（遷移機制現成）。
- **SDK 行為（google-genai 2.3.0）**：`embed_content` 內 `if not vertexai: if 'gemini-embedding-2' in model: contents = t.t_contents(contents)` → **併合特例只針對 -2**；-001 不併、list 直通 → N→N。

### §3.1 grep / 實測鋼鐵證據
```bash
$ venv/bin/python - <<'PY'   # Dev API 實測（測試機）
... probe(gemini-embedding-001) / probe(gemini-embedding-2) ...
PY
gemini-embedding-001: embeddings=3  dim=768     # 真批次 ✓
gemini-embedding-2:   embeddings=1  dim=768     # 融合 ✓（現況根因）

$ grep -rn "embed_image" --include=*.py . | grep -v "def embed_image"   # → 0 caller（換模型安全）
$ grep -n "EMBEDDING_MODEL" settings.py        # L25 預設 gemini-embedding-2
$ grep -n "embedding_model.*EMBEDDING_MODEL_NAME" tools/regen_rag.py    # L57 stale 偵測
```
**官方文件依據**（§5）：5 篇 GCP/Dev API embeddings 文件交叉佐證——`gemini-embedding-2`=多模態交錯（contents 融成 1、不支援 task_type）；`gemini-embedding-001`=文字（≤250 段/請求、支援 task_type）。

---

## §4 不可動清單
- [ ] `config.py` `EmbeddingModel._l2_normalize`（768 維正規化）— 不改（保 cosine 等價）。
- [ ] `llm/retry.py` `retry_call` / `_api_semaphore` 機制 — 不改（沿用）。
- [ ] `processor/rag_processor.py` 切 chunk（`MarkdownHeaderTextSplitter`）+ `_is_chunk_meaningful` 過濾 — 不改。
- [ ] `embed_image` 多模態介面 — 不刪（保留、但本任務不啟用；若未來用須另議模型）。
- [ ] A 軌 / pipelines / contracts / 母提示詞 / DB Schema — 不改（本任務僅 settings + config + 既有 regen_rag 遷移）。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §5 規格依據
| 依據名稱 | 來源位置 |
|---|---|
| 工作流 / 六階段 / SOP 核查 | `ref/WORKFLOW_SOP.md §1 / §3 / §5` |
| 進度框架（雙軌制 / 不過早優化心法） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 / §4.1` |
| logging / database SOP | `sop/2026-05-23_logging_SOP_手冊.md` / `sop/2026-05-23_database_SOP_手冊.md` |
| 官方①：Gemini Embedding 2（contents=交錯單輸入、Batch API coming soon）| https://developers.googleblog.com/building-with-gemini-embedding-2/ |
| 官方②：多模態 embeddings（task_type 不支援 gemini-embedding-2、8192 token）| https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/get-multimodal-embeddings |
| 官方③：批次預測（非同步 job、Vertex/GCS、text-embedding-005）| https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/batch-prediction-genai-embeddings |
| 官方④：文字 embeddings（**≤250 段/請求真批次、gemini-embedding-001**、2048 token/段、20000 token/請求）| https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/get-text-embeddings |
| 官方⑤：task types（**支援清單含 gemini-embedding-001、不含 -2**、query/doc 非對稱）| https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/task-types |
| Dev API 實測探針 | 本檔 §3.1（embeddings=3 / 1）|

---

## §6 驗證計畫
### §6.1 自動化單元測試
- 既有：`venv/bin/python -m pytest tests/ -q`（防 Regression）。
- 新增（`tests/test_embedding_retry.py` 或新檔）：
  - 批次 mock 回 **N**（對齊 -001）→ `embed_documents` 不退逐筆、回 N 向量、保序。
  - 超批量（>250 段）→ 自動拆批、合併保序。
  - task_type：`embed_documents` 用 DOCUMENT、`embed_query` 用 QUERY（斷言傳入 config.task_type）。
  - 真 fallback：mock `_embed_batch` 拋 429 → 退逐筆 `_embed_one`（保留兜底）。
### §6.2 手動 E2E（測試機 VM、Dev API）
1. 換模型 → 上傳一份履歷 → 觀察 `embed_documents` **一次批次 200 OK 回 N**（不再「期望 N 實得 1 退逐筆」、無 `embedding_429`）。
2. `regen_rag.py --all` 重嵌既有 paper → chunk 數一致、index_meta `model=gemini-embedding-001`。
3. RAG 召回 A/B：同 query 對「換前 -2 向量庫」vs「換後 -001 向量庫」比召回，確認 query/doc 非對稱改善（主觀 + golden D3）。
4. Golden 重捕後 `golden_baseline.py diff` 裁決。

---

## §7 Open Questions

> **✅ baron 拍板核准（2026-06-06、階段 3 驗證）**：Q1-Q8 全數核准採推薦方案。**全數結案 → 本 plan 可進階段 2 拆 tasks。**
> - **Q1 維度**：✅ 保留 768（MRL 截斷、幾乎無損召回、免改 Schema/FAISS 參數、省儲存運算）。
> - **Q2 批量**：✅ 防禦性上限 ≤100 段 + 守 20,000 token + 超限自動拆批合併保序（防長文拼裝觸 400）。
> - **Q3 task_type**：✅ 整批 DOCUMENT / 單筆 QUERY（非對稱語意檢索標準實踐）。
> - **Q4 fallback**：✅ 保留 `_embed_one` 為真錯誤（429/逾時）兜底；換模型後 count-mismatch 常態錯誤消失。
> - **Q5 遷移**：✅ 各環境換模型後手動 `regen_rag.py --all` 重嵌 + 與 Golden 重捕合併（向量空間位移、不可跨模型比對）。
> - **Q6 embed_image**：✅ 保留為**無操作 stub 接口**（0 caller、最小修改、避免多模態混合 Scope Creep）。
> - **Q7 tiling 連動**：✅ TextTiling 內部相對餘弦自比對、統一 DOCUMENT 不扭曲邊界；履歷已 opt-out、風險為零。
> - **Q8 全域影響**：✅ 接受——`EmbeddingModel` 單例全域，全量重嵌 + 全路 Golden 重捕、不可半套（經 Q5 涵蓋）。

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| Q1 維度：保留 768 vs 改 3072？ | **保留 768（MRL）** | 既有 FAISS dim / index_meta / `_l2_normalize` 相容、儲存與檢索成本低；探針證 -001 + 768 可用；3072 品質增益對履歷/論文 RAG 邊際、且儲存翻 4 倍。 |
| Q2 批次上限策略？ | **預設批 ≤100 段且總 token 守 20,000、超限自動拆**；單段 >2,048 token 截斷或警告 | -001 上限 250 段 / 20,000 token / 2,048 段；保守批量避免 token 超限失敗；以 token 為硬約束、段數為軟上限。 |
| Q3 task_type 在批次內？ | `embed_documents` 整批 **RETRIEVAL_DOCUMENT**、`embed_query` 單筆 **RETRIEVAL_QUERY** | 索引語料皆 DOCUMENT、查詢皆 QUERY；同批共用 task_type 語意正確（官方⑤）。 |
| Q4 `_embed_one` fallback 去留？ | **保留為真 fallback**（429/timeout/數量不符）；僅移除「-2 必然數量不符」死路 | -001 正常回 N，count-mismatch 不再常態；但保留逐筆兜底防真暫時性錯誤（韌性不減）。 |
| Q5 既有 paper 遷移時機？ | **各環境（測試/正式）換模型後跑 `regen_rag.py --all`**；與 Golden 重捕同批 | index_meta stale 偵測現成；避免新舊向量混庫（同庫不可跨模型比對）。 |
| Q6 `embed_image`（多模態）？ | **本任務不動、保留現狀（0 caller）**；未來需圖片向量再以 -2/多模態模型單獨處理 | 換 -001 不破壞（無 caller）；強行統一文字+圖模型屬另一議題。 |
| Q7 與 TILING/RESUME-P3 的 task_type 連動？ | TextTiling 內部相似度用 `embed_documents`（DOCUMENT）對「邊界偵測」無害（兩側同 type 可比）；履歷已 opt-out tiling | tiling 向量僅供內部相似度、非檢索；-001 上 task_type 生效但同 type 比較仍有效。 |
| Q8 全域影響範圍確認？ | 換 `EMBEDDING_MODEL_NAME` 影響**所有路 + chat RAG + tiling**（共用 EmbeddingModel）→ 全量重嵌 + 全路 Golden 重捕 | EmbeddingModel 為單例全域；非僅 B 軌；須全量遷移、不可半套。 |

---

## §99 治理規格與 Revision
### §99.1 治理規格表
| 維度 | 內容 |
|---|---|
| **目的** | 定義 MODEL-11 Embedding 模型換用與真批次的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 MODEL-11 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 拍板過程；嚴禁 commit 拆分（屬 tasks 階段）；不改 _l2_normalize/retry/切 chunk 演算法 |
| **改版觸發條件** | §1–§7 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義 embedding 模型/批次技術規格；工作目錄與流程一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程
- v2 (2026-06-06)：**baron 拍板核准 §7 Open Questions Q1-Q8（階段 3 驗證）**——Q1 保留 768 MRL / Q2 ≤100 段+20k token 自動拆 / Q3 整批 DOCUMENT 單筆 QUERY / Q4 保留 _embed_one 真錯誤兜底 / Q5 各環境 regen_rag --all + Golden 合併重捕 / Q6 embed_image 保留無操作 stub / Q7 tiling 統一 DOCUMENT 自比對無副作用 / Q8 全域單例全量重嵌不可半套。全數結案 → 可進階段 2 拆 tasks。
- v1 (2026-06-06)：初版建立——根因＝`gemini-embedding-2` 為多模態交錯模型（contents list 融成 1、不支援 task_type）致「批次永遠退逐筆 + query/doc 非對稱喪失（RAG 召回品質打折）」；解法換 `gemini-embedding-001`（Dev API 實測 embeddings=3/dim=768、真批次 + task_type）；目標 U1-U7（換模型 / 真批次 / task_type 生效 / 移除死路+修 log / 向量正確性 / regen_rag 全量遷移 / Golden 重捕）；現況附 SDK 併合特例 + 探針 + 5 篇官方文件；Open Questions Q1-Q8（768 維 / 批量 token 上限 / task_type 批次 / fallback 去留 / 遷移時機 / embed_image / tiling 連動 / 全域影響）。
