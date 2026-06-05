# Phase 3 Commit TILING-HOTFIX-1 — 緊急熱修復：TextTiling Embedding 速率超限 (429) 修復

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門用於修正進行 TextTiling 時，因遍歷呼叫 API 造成 429 RESOURCE_EXHAUSTED 速率超限的阻斷性 Bug。
> **修復原則**：只改動受災點 `processor/tiling_processor.py` 程式碼，不改動過濾演算法或大改架構。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **TILING-HOTFIX-1** | `待回填` | fix(tiling): batch compute block embeddings using embed_documents to prevent 429 rate limit |

---

## 阻斷性問題與真因

詳細記錄發生的 Regression 或 Block 問題，以及造成此問題的直接真因：

### 1. 阻斷現象 (Block Issue)
- **現象描述**：當上傳長文件或履歷進行 Tiling (TextTiling) 時，系統拋出 `ClientError: 429 RESOURCE_EXHAUSTED` 異常阻斷，導致向量化與 RAG 階段直接崩潰，AI Chat 面板無法解鎖。
- **受災範圍**：所有依賴 `TextTiling` 演算法進行分段的管線（包括 Resume、Academic 等）的 RAG 向量化落地功能。
- **🔑 連帶受災：測試套件併發 Flaky 頑疾（主要成果之一）**：先前 PIPE-RESUME C5–C7 在**全套件負載**下偶發失敗的 `tests/test_tiling_paragraph.py`（每次失敗子測試不同、隔離單跑卻通過），其真正 Traceback 即為本 bug 的 `httpx 429 Too Many Requests`——**並非單純的負載/時序型 flaky**。隔離單跑因瞬間 Request 數少而僥倖通過、併發全套件跑則必然爆發配額。故本 Hotfix 不僅修復影子/正式管線，**一併根治整個測試套件的 429 併發 Flaky**（修正先前「純環境性 flaky」的誤判）。
- **首發日誌/錯誤堆疊**：
  ```
  google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Resource exhausted. Please try again later. Please refer to https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429 for more details.', 'status': 'RESOURCE_EXHAUSTED'}}
  
   [embedding_model.embed_query(block) for block in blocks]
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/home/baroncheng/mad-professor-public/config.py", line 150, in embed_query
      result = self.client.models.embed_content(
  ```

### 2. 真因診斷 (Root Cause)
- **技術細節**：
  在 `tiling_processor.py` 第 425 行中，使用了 List Comprehension 同步遍歷計算所有分塊的 Embedding。
  如果文本較長、分塊 (`blocks`) 數量多時，該循環會在極短時間（毫秒級）內發起數十個乃至上百個獨立的 API 網路請求。這直接超出了 Vertex AI / Gemini API 的**每分鐘請求數 (RPM)** 限制，從而觸發配額耗盡；且 `config.py` 的 `embed_query` 原生設計僅作單一查詢，**內部無任何 429 退避與重試機制**，導致異常直接拋出。
- **定位程式碼**：`file:///home/baroncheng/mad-professor-public/processor/tiling_processor.py#L425`

---

## 熱修復修法 (Minimal Hotfix)

本修復採取**最小侵入式**解決方案，將逐筆遍歷改為**批次 (Batching) 呼叫**：

### `processor/tiling_processor.py` — 最小改動
```diff
         # 计算每个块的嵌入向量 - 使用统一 of EmbeddingModel
         embedding_model = self.embedder
-        block_embeddings = [embedding_model.embed_query(block) for block in blocks]
+        # === [TILING-HOTFIX-1 START] ===
+        # 改用批次計算 embed_documents（每批 32 筆），並承接內部的 429 線性退避重試保護
+        block_embeddings = embedding_model.embed_documents(blocks)
+        # === [TILING-HOTFIX-1 END] ===
         
         # 计算相邻块之间的相似度
```

**修法效益說明**：
1. **大幅度降低請求量**：改用 `embed_documents` 會以 Batch Size = 32 進行分批，將 API 請求數直接降為原本的 **1/32**。
2. **重試與退避保護**：`embed_documents` 內部已封裝了 **3 次線性退避**重試（`config.py L130-133`：`wait = 15 * (attempt + 1)` → 15s、30s）與**重試耗盡退回逐筆**的安全機制（`config.py L139-140`），能有效吸收並平滑處理 429 速率限制。
3. **順序保證（正確性前提）**：`embed_documents` docstring 明訂「依索引順序拼接，保證回傳順序與輸入完全一致」（`config.py L99`），故 `block_embeddings[i]` 與原逐筆版本逐一對齊，**相鄰塊 Cosine 相似度計算（L428）不因批次化而錯位**。

### ⚠️ 行為變更聲明：task_type 語意位移（RETRIEVAL_QUERY → RETRIEVAL_DOCUMENT）
- **變更本質**：原 `embed_query` 以 `task_type="RETRIEVAL_QUERY"` 呼叫（`config.py L154`）；改用 `embed_documents` 後改以 `task_type="RETRIEVAL_DOCUMENT"`（`config.py L115`）。兩者 Gemini Embedding API 會施以不同的 Task-Type 語意導向，產生的向量值**略有差異**。
- **潛在影響**：相鄰塊 Cosine 相似度將**微幅浮動**，**極可能使 TextTiling 的分段邊界發生些許位移** → 連帶改變 `PaperChunk` 切割內容與 RAG 召回。
- **取捨評估**：對「文件內部塊」（Document-Blocks）而言 `RETRIEVAL_DOCUMENT` 的語意**更為正確**（原 `RETRIEVAL_QUERY` 本即誤用為查詢型）；但這確屬**非純 batching 的行為變更**，故於此明確聲明，並由下方驗證計畫強制 Golden Baseline 重捕防線承接。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試
修改後，執行 RAG 與 Tiling 測試套件，確保功能完好且無 Regression：
```bash
$ pytest tests/test_tiling_paragraph.py tests/test_tiling_formula.py tests/test_tiling_env_overrides.py -v
# [驗收通過日誌：7 passed / 4 passed / 3 passed]
```

### 2. 本地 E2E 快速復現與驗證
手動觸現有 RAG 向量化，確認分塊計算流暢，並在 logs 中看到 Batch 批次處理日誌：
```
[INFO] config: 批次 1 完成（32 筆，32/120）
[INFO] config: 批次 2 完成（32 筆，64/120）
...
[INFO] pipelines: [PIPE-RESUME P4] RAG 完成 chunks=120
```

### 3. 🛡️ Golden Baseline 重捕防線（強制、Flip/結案前置）
本 Hotfix 的 task_type 語意位移會改變 TextTiling 分段邊界 → 衝擊五路既有黃金基準（D2 譯文相似度 0.95 / D3 RAG 召回 Jaccard 0.90）。故定調流程防線：

- **強制步驟**：Hotfix 落地後、PIPE Flip（或本批次結案）**之前**，必須由 **baron 於 MinerU 實跑機**重新捕捉五路黃金基準（對齊 GOLDEN-BASELINE OP-1 既有 SOP）：
  ```bash
  baron@MinerU$ venv/bin/python tools/golden_baseline.py capture --all
  ```
- **裁決**：重捕後以 `golden_baseline.py diff` 對既有基準比對，確認分段位移落在容差內（D2 ≥0.95 / D3 ≥0.90）；逾容差則需 baron 復核分段品質是否仍可接受後，方以新基準覆蓋存盤。
- **理由**：舊基準是以誤用的 `RETRIEVAL_QUERY` 向量產生；切換至語意更正確的 `RETRIEVAL_DOCUMENT` 後，新分段即為新真理源，須重新凍結以免後續 Regression 比對全面誤報。

---

## 回退與備案

若此 Hotfix 依然未能完全解決問題，或引發更大的 Regression，請立即執行備份回退：

```bash
# 還原受災檔案
git restore processor/tiling_processor.py
```
