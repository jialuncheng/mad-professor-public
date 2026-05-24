# 2026-05-20 RAG 檢索 distance_strategy 對齊修復

只動 `rag_retriever.py` 三處（1 行 import、1 行 kwarg、1 行門檻 + 4 行
註解）。未動 `processor/rag_processor.py`（建立端已正確）、未動
`AI_professor_chat.py` / `config.py` / 前端 / 其他 .py。

## 真因（轉述）
- 建立端 `rag_processor.py:103` 用 `distance_strategy=
  DistanceStrategy.MAX_INNER_PRODUCT`。
- 載入端 `rag_retriever.py:48` `FAISS.load_local` **未指定**
  distance_strategy → LangChain wrapper 預設 L2 → 對 IP-index 解讀錯誤 →
  `similarity_search_with_score` 回的 score 方向亂套。
- `rag_retriever.py:100` 門檻 `> 0.6` 是為「L2/cosine 距離 0~1」設計，對
  IP（值依 vector norm，不固定 0–1）無意義。

實測（手動傳 MAX_INNER_PRODUCT 載入後）：
- 相關 query：top score 0.23–0.27
- 無關 query：top score 0.17–0.20
門檻 0.22 完美區分；原本（無 strategy）兩者皆 0.19–0.25 重疊。

## 修改 diff
```diff
@@ rag_retriever.py
 from langchain_community.vectorstores.faiss import FAISS
+from langchain_community.vectorstores.utils import DistanceStrategy
 from config import EmbeddingModel

@@ load_local
             store = FAISS.load_local(
                 vector_store_path,
                 EmbeddingModel.get_instance(),
-                allow_dangerous_deserialization=True
+                allow_dangerous_deserialization=True,
+                distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,  # 對齊建立端（rag_processor）
             )

@@ similarity_search_with_score 過濾
             docs_with_scores = vector_store.similarity_search_with_score(query=query, k=top_k)
-            filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > 0.6]
+            # IP metric 下 score 為 inner product 值（越大越相似），與建立端
+            # MAX_INNER_PRODUCT 對齊。實測 Gemini embedding 768 dim 下：
+            # 相關 query top score 約 0.23-0.27，無關 query 約 0.17-0.20。
+            # 門檻 0.22 可有效區分。
+            filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > 0.22]
```
淨變動：+7 行（1 import + 1 kwarg + 4 行註解 + 1 行條件式取代原 1）。

## 驗證
- **py_compile** `rag_retriever.py`：通過。
- **import 解析**：
  `python -c "from langchain_community.vectorstores.utils import
  DistanceStrategy; print(DistanceStrategy.MAX_INNER_PRODUCT)"`
  → `DistanceStrategy.MAX_INNER_PRODUCT`（既有套件，與建立端同源）。
- **pytest** `tests/test_metadata_extractor.py -q`：**18 passed, 3 skipped**
  （metadata 測試與 RAG 無關，符合不變預期）。
- **不需要重建任何 vector store**：建立時 index 已用 IP；只是載入端讀錯。
- **端到端**（待 OrcStack 重啟）：
  - DeHunt 履歷「請分析這位候選人職涯主要的領域變化」→ AI 應引用
    Novatek / Focaltech / Targetek / Viewtrix 等公司名。
  - 「你好」→ router 仍判 direct_answer（router prompt 已修，與此修
    互補）。

## 推薦 commit message
```
fix(rag_retriever): 對齊 MAX_INNER_PRODUCT 並調整過濾門檻

processor/rag_processor.py 建立 FAISS index 時用 distance_strategy=
MAX_INNER_PRODUCT，但 rag_retriever.py 的 FAISS.load_local 未指定
distance_strategy → LangChain wrapper 預設 L2 → 對 IP-index 解讀錯誤
→ similarity_search_with_score 回的 score 方向亂套，相關/無關 query
分不開。

修法：
- 加 import：from langchain_community.vectorstores.utils
  import DistanceStrategy
- load_local 傳 distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
- 過濾門檻 0.6（L2 距離邏輯）→ 0.22（IP score 邏輯）
  依實測 Gemini embedding 768 dim：相關 query top score 0.23-0.27、
  無關 query 0.17-0.20，0.22 完美區分。

不需重建 vector store（建立端早已用 IP）。未動 rag_processor /
AI_professor_chat / config / 前端 / 其他 .py。

py_compile 通過；metadata 測試 18 passed 3 skipped 無回歸。
端到端待 OrcStack 重啟：履歷/簡報應能引用文件具體內容（與 router
prompt 修正互補）。
```

## 不可動清單（已遵守）
- processor/rag_processor.py：未動（建立端正確）
- AI_professor_chat.py：未動
- config.py（EmbeddingModel task_type）：未動
- 前端：未動
- 其他 .py / prompt：未動
