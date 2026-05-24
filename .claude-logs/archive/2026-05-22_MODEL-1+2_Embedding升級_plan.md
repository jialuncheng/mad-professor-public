# Phase 4.7? MODEL-1+2 — Plan：Embedding 升級 + L2 正規化 + 短 chunk 過濾（含 baron 3 補充）

> 本文件為**純分析與設計計畫**，獲確認前嚴禁修改業務代碼。
> **依據**：`.claude-logs/ref/model_optimization_blueprint.md` §1 + `google_latest_models_guide.md` + baron 補充一/二/三

---

> **審查補充已納入（v3）**：4 個修正
> 1. **分數閾值 env 化**（漏洞 1）— `RAG_SCORE_THRESHOLD` 預設 0.22 + env override、不無腦升 0.40
> 2. **Markdown 噪聲過濾**（漏洞 2）— `_is_chunk_meaningful` 移除 `# * _ ~ ` 等符號再計字數
> 3. **`_l2_normalize` 防禦升級**（漏洞 3）— 空 list / None / float32 精度 1e-6 安全範圍 / 零向量回 `[0.0] * len`
> 4. **履歷結構化資訊保留**（合併 baron 補充二 + 審查精煉 regex）— 單一 helper 含 email / phone / url / 純數字 / markdown 噪聲 4 個防禦

## §1 TL;DR

- **問題與挑戰**：
  - (M-1) `EMBEDDING_MODEL_NAME` 預設**已是 `gemini-embedding-2`**（`settings.py:19`）但**無對應「升級驗證」測試**、是「預設改了、code 沒驗證」狀態
  - (M-2) **L2 normalize 完全缺**：`config.py` 4 處 `embed_content` call 直接 `.values` 回傳、無 normalize；FAISS `MAX_INNER_PRODUCT` 對未 normalize 向量 score 數學上 ≠ cosine（解釋為什麼 15-2 觀察到 0.22 + 區間窄 0.04 寬窗）
  - (短 chunk) **chunk-level filter 完全缺**：`rag_processor._create_vector_store` 直接把 `md_splitter.split_text` 結果丟 FAISS、無 < 10 字元 guard
- **核心根因**：embedding 預設升級了、但下游 L2 + chunk 防禦兩道閘缺；score 區間因此不穩定、是 RAG-3 校準的前置工作 = 本 commit
- **設計解法**：1 commit、~2 小時、3 項+ 3 補充：
  - **核心 4.1** `config.py` EmbeddingModel 強制 L2 normalize 所有產出（4 處 embed call）
  - **核心 4.2** `processor/rag_processor.py` 加 `_is_chunk_meaningful` filter
    - **baron 補充二**：resume/slides 放寬到 3 字元 + email/url/phone 保留 + 純數字過濾 + log 印前 15 字
  - **核心 4.3** raw score logging（baron 補充一前置、為 RAG-3 鋪路、不動 0.22 閾值）
  - **核心 4.4** 安全 backfill 3 步驟（baron 補充三、pkill → rm-rf → 重啟）
- **score 閾值**：**本 commit 不動**——LangChain FAISS score 轉換歧義（§3.5）、先 logging 等實測、留 RAG-3 校準
- **影響範圍**：
  - **動**：`config.py` / `processor/rag_processor.py` / `rag_retriever.py`（僅加 logging）/ `settings.py` + 2 個新 test 檔
  - **不動**：`pipeline_core` / `web_server` / 其他 processor / score 閾值 / BATCH_SIZE / vector store schema
- **既有 vector store**：baron 確認可清（< 10 份）、依 §4.4 三步驟手動執行

---

## §2 現況盤點

### 2.1 EmbeddingModel 配置

**`settings.py:19`**：
```python
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
```

→ **預設已是 `gemini-embedding-2`**；但無對應驗證 / 測試（「悄悄升級」狀態）。

**`config.py::EmbeddingModel`**（singleton + LangChain `Embeddings` 介面、MODEL-9 已注入共享 httpx.Client）：

| 行 | 用途 | 是否 normalize |
|---|---|---|
| `config.py:21-30` | `__init__` 共享 httpx.Client（MODEL-9）| N/A |
| `config.py:40-55` | `_embed_one` fallback、L48 `return result.embeddings[0].values` | ❌ |
| `config.py:62-107` | `embed_documents` 批次 + 429 retry、L84 `embeddings.extend(e.values ...)` | ❌ |
| `config.py:114-119` | `embed_query`、L118 `return result.embeddings[0].values` | ❌ |
| `config.py:121-130` | `embed_image`、L130 直接 `.values` | ❌ |

**所有 4 個 embed 路徑都無 L2 normalize**——MODEL-2 缺口。

**BATCH_SIZE**：`config.py:64 BATCH_SIZE = 32`（hardcoded、本 commit **不改**、屬 🚫 不做清單）。

### 2.2 RagProcessor chunk 處理

**`processor/rag_processor.py:103-114`** `_create_vector_store`：
```python
headers_to_split_on = [("#", "Header")]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
docs = md_splitter.split_text(content)
self.logger.info(f"分割后得到 {len(docs)} 个文档片段")

vector_store = FAISS.from_documents(
    documents=docs,
    embedding=self.embedder,
    distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
)
```

→ **md_splitter 切完直接丟 FAISS、零 chunk-level 過濾**。

⚠ 15-1 處理的是「同 section text item 合併」、是 markdown 生成階段；**chunk 入庫 filter 完全缺**。

### 2.3 FAISS 配置 + LangChain score（含 baron 補充一驗證）

**`processor/rag_processor.py:113` + `rag_retriever.py:55`**：
```python
distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
```

→ 建立端 + 檢索端對齊 `MAX_INNER_PRODUCT`、向量已 normalize 則 IP = cosine、score ∈ [-1, 1]。

**`rag_retriever.py:105`** 用 `similarity_search_with_score`：
```python
docs_with_scores = vector_store.similarity_search_with_score(query=query, k=top_k)
```

**baron 補充一驗證**（已查 langchain_community 0.4.1 源碼）：
- `similarity_search_with_score` 對 `MAX_INNER_PRODUCT` distance_strategy → **回 raw IP score**（不是 normalize 後 [0, 1]）
- 既有註解（`rag_retriever.py:107-110`）「相關 0.23-0.27、無關 0.17-0.20」與此一致——是 raw IP、區間窄因為**向量未 L2 normalize**
- 結論：本 commit L2 normalize 落地後、score 應該變寬到 cosine [-1, 1] 子集；但**寬度具體值需實測**（先加 logging、不動閾值）

維度：**768**（4 處 `output_dimensionality=768` 寫死、可抽常數）。

既有 vector store 位置：`output/{owner_id}/{paper}/vector_store/`。

### 2.4 Score 閾值現況

**`rag_retriever.py:108-120`**：
```python
# 相關 query top score 約 0.23-0.27，無關 query 約 0.17-0.20。
# 門檻 0.22 可有效區分。
...
filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > 0.22]
```

→ **0.22 寫死、註解明列 pre-normalize 觀察區間**。
→ L2 normalize 後預期區間擴展、但具體值需實測（§3.5）→ **本 commit 不動閾值、只加 logging**。

### 2.5 SDK probe 結果（已驗證）

```bash
$ venv/bin/python -c "from google.genai import types; c = types.EmbedContentConfig(output_dimensionality=768); print(c)"
OK http_options=None task_type=None title=None output_dimensionality=768 ...
```

→ SDK 接 snake_case `output_dimensionality` + camelCase `outputDimensionality`、Pydantic 自動轉換、既有 code 用 snake_case 正常運作。

---

## §3 觀察到的問題與證據

### 3.1 Embedding 模型「升了但未驗證」

- `settings.py:19` 預設 `gemini-embedding-2`、**0 個對應測試**
- 4 處 `output_dimensionality=768` 是 MRL 降維、官方文件指出降維後預設 **NOT pre-normalized**
- 推測：「降維 raw 向量直接進 FAISS」→ score 區間窄

### 3.2 未正規化 inner product

- `config.py:48/84/118/130` 4 處 `return ... .values`、無 `numpy.linalg.norm`
- 證據：rag_retriever.py:108 註解「相關 0.23-0.27、無關 0.17-0.20」(0.04 寬窗)正是未 normalize 的典型結果
- L2 normalize 後預期 cosine 區間（具體寬度待實測）

### 3.3 短 chunk 雜訊

- `_create_vector_store` 對 `md_splitter.split_text` 結果**零 filter**
- MarkdownHeaderTextSplitter 對 H1-only split 可能產出：
  - 純 header chunk（`# Education` 後空白）
  - 雜訊 chunk（`Skills` 下方只有「2024」）
- 影響：浪費 API call + 引入無關向量 / 召回噪聲

### 3.4 履歷 / slides 場景：短 chunk 過濾誤殺風險（baron 補充二）⭐

提案 `< 10 字元`過濾的誤殺風險表（baron 補充二）：

| chunk | 字元 | 該不該過濾？ | 規則 |
|---|---|---|---|
| `"Python"` | 6 | ❌ 技能詞、不該 | resume/slides 放寬到 ≥ 3 |
| `"Docker"` | 6 | ❌ 同 | resume/slides 放寬到 ≥ 3 |
| `"john@example.com"` | 16 | ⚠ Email 必保留 | 含 `@` 且符合 email regex 保留 |
| `"+886-912-345678"` | 15 | ⚠ 電話 | 符合 phone regex 保留 |
| `"https://github.com/x"` | 20 | ⚠ url | 含 `http://` / `https://` 保留 |
| `"PhD"` | 3 | ✅ 純標籤、該過濾 | resume/slides 放寬到 ≥ 3 → 邊界（純標題判定） |
| `"2024"` | 4 | ✅ 純年份、該過濾 | 純數字（`^\d+$`）不論 doc_type 過濾 |
| `"Education"` | 9 | ✅ 純標題、該過濾 | < 10 字元 default 過濾 |

→ `_is_chunk_meaningful` 必須**依 doc_type + 內容類型動態決定**字元下限（§4.2）。

### 3.5 LangChain FAISS score 轉換歧義（baron 補充一）⚠

**baron 補充一原始疑慮**：LangChain 不同版本對 IP score 可能做不同轉換：
- 直接回 raw IP score（FAISS 原始）
- 自動 normalize 到 [0, 1]（公式 `(score+1)/2`）
- 用 distance score（越小越相關）

**已查證**（langchain-community 0.4.1）：
- `similarity_search_with_score` 對 `MAX_INNER_PRODUCT` 回 **raw IP score**（不是 normalize 過的 [0, 1]）
- 既有 `rag_retriever.py:107-110` 註解「相關 0.23-0.27」與此一致

**但提案說「L2 normalize 後 score 拉寬到 0.45-0.75」**——這仍是**假設、不是事實**：
- 我們知道 raw IP score；但 L2 normalize 後具體相關 chunk 的 cosine 區間值（0.4? 0.5? 0.6?）需**實測**才知
- 不同 paper / doc_type / 查詢類型可能差異大

**結論**：
- 本 commit **不無腦升閾值到 0.40**（避免「閾值設太高→相關 chunk 全被擋」回歸）
- **改為閾值 env 化**（§3.6.1 修正 1 + §4.6）：`RAG_SCORE_THRESHOLD` 預設 0.22 + env override、baron 觀察 raw score 後動態調
- **加 raw score logging**（§4.3）：retrieve 結果印 raw IP score、為 RAG-3 收實測數據
- **加 sample 統計 log**（每次 retrieve 都看到 score 分布）

### 3.6 4 個審查補充（v3 新增）

#### 3.6.1 分數閾值漏洞（修正 1）

- **審查者觀點**：L2 normalize 後分數區間可能拉高、繼續用 0.22 會放任垃圾湧入 LLM
- **baron 折衷決策**：**不無腦升 0.40、改為 env 化保留 0.22 預設**
- **理由**：
  - LangChain FAISS score 是否已被內部轉換尚未 100% 證實（§3.5 已查源碼確認 0.4.1 對 MAX_INNER_PRODUCT 是 raw IP、但 L2 後具體相關區間值未實測）
  - 升 0.40 前應先觀察 raw score 分布
  - env override 讓 baron 可在不 commit 情況下動態調整、實測友善
- **落地**：見 §4.6

#### 3.6.2 Markdown 符號漏洞（修正 2）

- **審查者觀點**：原 `_is_chunk_meaningful` 只看 `len(text) >= 10`、漏判 `"## Summary\n---"` 這種純標題 + 分隔線（11 字元、無實質內容）
- **實例對照表**：

  | chunk | 原始 len | 移除 md 符號後 len | 原規則 | 新規則 |
  |---|---|---|---|---|
  | `"## Summary\n---"` | 14 | 7 | 保留（誤殺反向：放任） | **過濾**（< 10） |
  | `"# Education"` | 11 | 9 | 保留（同上） | **過濾**（< 10） |
  | `"---\n***"` | 7 | 0 | 過濾 | **過濾**（< 10） |
  | `"## Working Experience"` | 21 | 18 | 保留 | 保留 |
  | `"Python is a language"` | 21 | 17 | 保留 | 保留 |

- **落地**：合併進修正 4 helper、見 §4.2

#### 3.6.3 `_l2_normalize` 防禦缺陷（修正 3）

- **審查者觀點**：原 helper `if norm < 1e-12: return vec` 有 3 個風險：
  1. **空 list / None**：`np.asarray([])` 不 crash 但 `np.linalg.norm` 回 0、且 `len(vec)` 對 None 拋 TypeError
  2. **float32 精度**：1e-12 在 float32 下不安全（float32 最小正常數 ~1.18e-38、但乘除運算後 1e-12 級可能誤判）；推薦升到 **1e-6** 安全範圍
  3. **零向量回 `vec` 原樣**：caller 可能誤判該向量是「unit vector」、實際 norm=0；明確回 `[0.0] * len(vec)` 更清楚
- **落地**：見 §4.1 新版 helper

#### 3.6.4 履歷結構化資訊保留（修正 4、合併 baron 補充二 + 審查精煉）

- baron 補充二（plan 原版）：resume/slides 放寬 ≥ 3 + email/phone/url 保留 + 純數字過濾
- 審查者補充：用單一 `_CRITICAL_INFO_RE` 合併 3 個 regex 更精煉
- **落地**：見 §4.2 合併 helper

---

## §4 設計方案

### 4.1 `config.py` EmbeddingModel L2 normalize（M-2 核心）

**位置**：`config.py` EmbeddingModel class 內。

**步驟 1**：新增 helper + module-level 常數
```python
# config.py 頂部加 import + 常數
import os
import numpy as np

EMBEDDING_OUTPUT_DIMENSIONS = int(os.environ.get("EMBEDDING_OUTPUT_DIMENSIONS", 768))


class EmbeddingModel(Embeddings):
    ...

    @staticmethod
    def _l2_normalize(vec: list) -> list:
        """L2 正規化單一向量（MODEL-2、修正 3 防禦升級）。

        gemini-embedding-2 在 3072 維時預設已 normalize、但用 MRL 降維到
        768 維時必須手動 normalize；否則 FAISS MAX_INNER_PRODUCT 距離 ≠ cosine、
        score 區間不穩定。

        修正 3 防禦：
        - 空 list / None → 回原樣（避免 TypeError）
        - float32 精度：閾值 1e-6（取代 1e-12、float32 安全範圍）
        - 零向量 → 明確回 `[0.0] * len(vec)`、避免 caller 誤判 unit vector

        Args:
            vec: 原始 embedding 向量

        Returns:
            L2 normalize 後向量；空 / None 回原樣；零向量回 `[0.0] * len`
        """
        if not vec:
            return vec  # 空 list / None / 0-length → 直接回（caller 自處理）

        arr = np.asarray(vec, dtype=np.float32)
        norm = np.linalg.norm(arr)

        # 修正 3：float32 精度 1e-6 安全範圍（取代 1e-12）
        if norm < 1e-6:
            # 修正 3：零向量明確回零、避免 caller 誤判 unit vector
            return [0.0] * len(vec)

        return (arr / norm).tolist()
```

**步驟 2**：4 處 embed call 套 normalize + 抽常數

| 位置 | 原 | 改 |
|---|---|---|
| `config.py:45` `_embed_one` config | `output_dimensionality=768` | `output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS` |
| `config.py:48` `_embed_one` return | `return result.embeddings[0].values` | `return self._l2_normalize(result.embeddings[0].values)` |
| `config.py:77` `embed_documents` batch config | `output_dimensionality=768` | `output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS` |
| `config.py:84` `embed_documents` extend | `embeddings.extend(e.values for e in result.embeddings)` | `embeddings.extend(self._l2_normalize(e.values) for e in result.embeddings)` |
| `config.py:116` `embed_query` config | `output_dimensionality=768` | 用常數 |
| `config.py:118` `embed_query` return | `return result.embeddings[0].values` | 套 `_l2_normalize` |
| `config.py:129` `embed_image` config | `output_dimensionality=768` | 用常數 |
| `config.py:130` `embed_image` return | `return result.embeddings[0].values` | 套 `_l2_normalize` |

### 4.2 `processor/rag_processor.py` 短 chunk 過濾 + baron 補充二防禦放寬

**位置**：`_create_vector_store` 內、`md_splitter.split_text` 後、`FAISS.from_documents` 前。

**新增 module-level 常數 + helper**（含 baron 補充二 + 修正 2 markdown 噪聲過濾 + 修正 4 合併版）：
```python
import os
import re

MIN_CHUNK_CONTENT_CHARS = int(os.environ.get("RAG_MIN_CHUNK_CHARS", 10))
MIN_CHUNK_RESUME_SLIDES = int(os.environ.get("RAG_MIN_CHUNK_RESUME_SLIDES", 3))

# 修正 2：移除非實質字元計算 chunk 字數（純標題 / 分隔線會被過濾）
_MD_NOISE_RE = re.compile(r"[#*_~`\-+>|\[\]\s]")

# 修正 4：純數字（年份等）過濾
_PURE_DIGIT_RE = re.compile(r"^\d+$")

# 修正 4：合併 email / phone / url 為單一精煉 regex（審查者建議）
_CRITICAL_INFO_RE = re.compile(
    r"([\w.+-]+@[\w-]+\.[\w.-]+"     # email
    r"|\+?\d[\d\s\-]{6,}\d"           # phone（國際電話格式）
    r"|https?://\S+)"                 # url
)


def _is_chunk_meaningful(doc, doc_type: str = "") -> bool:
    """判定 LangChain Document chunk 是否值得入向量庫（修正 2 + 修正 4 合併版）。

    過濾規則（依優先序）：
    1. 空字串 → 過濾
    2. 純數字（如年份「2024」）→ 過濾
    3. 含 email / phone / url 結構化資訊 → 保留（不論長度）
    4. doc_type ∈ {'resume', 'slides'} → 放寬到 ≥ 3 **實質字元**（保 Python / Docker 等技能詞）
    5. 其他 doc_type → ≥ 10 **實質字元**

    「實質字元」= 移除 markdown 符號（`# * _ ~ ` `-` `+` `>` `|` `[` `]` 與空白）後字元數。

    範例：
    - `""` → 過濾（空）
    - `"2024"` → 過濾（純數字）
    - `"PhD"` → 過濾（純標籤、3 字元但非 resume/slides）
    - `"Python"` + doc_type='resume' → 保留（技能詞、≥ 3）
    - `"## Summary\n---"` → 過濾（markdown 噪聲、實質 7 字元、< 10）
    - `"john@example.com"` → 保留（含 email）
    - `"+886-912-345678"` → 保留（含 phone）
    - `"https://github.com/x"` → 保留（含 url）
    - `"Education content here"` → 保留（≥ 10）

    Args:
        doc: LangChain Document（含 .page_content + .metadata）
        doc_type: 'academic' / 'resume' / 'slides' / ...

    Returns:
        True 保留 / False 過濾
    """
    text = (doc.page_content or "").strip()

    if not text:
        return False

    # 修正 4：純數字（如「2024」）→ 不論 doc_type 過濾
    if _PURE_DIGIT_RE.match(text):
        return False

    # 修正 4：含結構化資訊（email / phone / url）→ 保留（不論長度）
    if _CRITICAL_INFO_RE.search(text):
        return True

    # 修正 2：計算實質字元數（移除 markdown 噪聲）
    clean_text = _MD_NOISE_RE.sub("", text)

    # 依 doc_type 決定字元下限
    if doc_type in ("resume", "slides"):
        return len(clean_text) >= MIN_CHUNK_RESUME_SLIDES
    return len(clean_text) >= MIN_CHUNK_CONTENT_CHARS
```

**改 `_create_vector_store`（L103-114）**：
```python
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
docs = md_splitter.split_text(content)
self.logger.info(f"分割后得到 {len(docs)} 个文档片段")

# Phase 4.7? MODEL-1+2 short chunk filter（含 baron 補充二防禦放寬）
meaningful_docs = []
filtered_samples = []
for d in docs:
    if _is_chunk_meaningful(d, doc_type=doc_type):
        meaningful_docs.append(d)
    else:
        filtered_samples.append(d)

if filtered_samples:
    # baron 補充二：印前 15 字元便於 baron 調試誤殺
    sample_texts = [
        f'"{(d.page_content or "")[:15]}..."'
        for d in filtered_samples[:5]
    ]
    self.logger.info(
        f"[chunk filter] doc_type={doc_type!r} 過濾 {len(filtered_samples)} "
        f"個短 chunk（resume/slides 放寬 ≥{MIN_CHUNK_RESUME_SLIDES} / 其他 ≥{MIN_CHUNK_CONTENT_CHARS}、純數字過濾）："
        + ", ".join(sample_texts)
        + (f" ... 共 {len(filtered_samples)} 個" if len(filtered_samples) > 5 else "")
    )

vector_store = FAISS.from_documents(
    documents=meaningful_docs,
    embedding=self.embedder,
    distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
)
```

⚠ 需確認 `doc_type` 是 `_create_vector_store` 的可用參數（從 caller 傳入、或從 `paper_data.get('doc_type')` 取）；若不可用、退到無 doc_type 區別、全部用 ≥ 10。**plan 階段建議**：實作時優先讓 doc_type 可傳；無法則退到 `meaningful_docs = [d for d in docs if _is_chunk_meaningful(d)]`（不分 doc_type）。

### 4.3 raw score logging（baron 補充一前置、為 RAG-3 鋪路）

**位置**：`rag_retriever.py:105` 附近、`similarity_search_with_score` 後。

**改動**（**只加 logging、不動 0.22 閾值**）：
```python
docs_with_scores = vector_store.similarity_search_with_score(query=query, k=top_k)

# Phase 4.7? MODEL-1+2: raw score 詳細 logging（為 RAG-3 收實測數據）
# baron 補充一：LangChain FAISS score 對 MAX_INNER_PRODUCT 是 raw IP（已查 0.4.1 源碼確認）
# L2 normalize 後預期 = cosine [-1, 1] 子集、但具體相關區間值需實測
if docs_with_scores:
    _scores = [s for _, s in docs_with_scores]
    # 既有 log（保留、給 15-2 對齊）
    logger.info(
        f"[retrieve] owner={owner_id} paper={paper_id} "
        f"query={query[:40]!r} top_k={top_k} "
        f"scores={[round(s, 3) for s in _scores]} "
        f"above_0.22={sum(1 for s in _scores if s > 0.22)}"
    )
    # 新加：raw score 詳細分布（為 RAG-3 校準用）
    logger.info(
        f"[retrieve raw] owner={owner_id} paper={paper_id} "
        f"min={min(_scores):.4f} max={max(_scores):.4f} "
        f"mean={sum(_scores)/len(_scores):.4f} "
        f"raw_scores={[f'{s:.4f}' for s in _scores]}"
    )

# TODO RAG-3: MODEL-1+2 落地後 score 區間預期變寬（cosine [-1, 1] 子集）；
# 本 0.22 閾值是 pre-normalize 觀察值、需重新校準（屬 RAG-3 範圍）
filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > 0.22]
```

**不動**：0.22 寫死位置——避免「閾值改太高→相關 chunk 全被擋」回歸；留 RAG-3 收 1-2 週數據後校準。

### 4.4 安全 backfill 3 步驟（baron 補充三）

提案原「直接 rm -rf」會撞正在跑的 SSE chat / retrieve 請求；改為：

```bash
cd ~/mad-professor-public

# === Step 1: 停止 Web 服務 ===
pkill -f "web_server.py" && sleep 1
# 確認沒有 web_server 進程在跑
ps aux | grep web_server.py | grep -v grep
# 預期：沒輸出（或只有 grep 自己）

# === Step 2: 安全刪除舊向量庫 ===
rm -rf output/*/*/vector_store/
# 確認為 0
find output -name vector_store -type d | wc -l
# 預期：0

# === Step 3: 背景啟動 Web 服務 ===
> /tmp/webserver_console.log
nohup venv/bin/python web_server.py > /tmp/webserver_console.log 2>&1 &
sleep 3
ps aux | grep web_server.py | grep -v grep
# 預期：1 個 process
head -10 /tmp/webserver_console.log
# 預期：看到 LLMClient / EmbeddingModel 初始化 log（含 MODEL-9 timeout + MODEL-1+2 維度）

# === Step 4: 重新觸發 rag stage ===
# 透過 web 重新上傳 / 或對既有 paper 觸發 rag stage
# 觀察新 log:
tail -50 logs/pipeline.log | grep -E "chunk filter|分割|向量库"
# 預期：
#   分割后得到 N 个文档片段
#   [chunk filter] doc_type='resume' 過濾 M 個短 chunk...
#   向量库创建完成

# === Step 5: 對該 paper 提問、觀察 raw score 分布 ===
grep "\[retrieve raw\]" logs/chat.log | tail -10
# 預期：raw score 區間明顯變寬（cosine 子集、為 RAG-3 收數據）
```

→ 本 commit **執行報告 §7** 必須完整記錄這 5 步驟（baron 補充三：SOP 化、後續 RAG-2 之前都會用）。

### 4.5 settings.py 顯式化常數

```python
# settings.py 既有 L19:
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")

# 本 commit 新增（或在 config.py 內讀 env、與 MODEL-9 風格一致；最終以實作為準）：
# 用 MRL 降維到 768、保留現有 FAISS schema；3072 原生最高品質、768 「near-peak quality」
# storage 省 75%。降維後需手動 L2 normalize（見 config.py::EmbeddingModel._l2_normalize）
EMBEDDING_OUTPUT_DIMENSIONS = int(os.getenv("EMBEDDING_OUTPUT_DIMENSIONS", 768))
```

### 4.6 RAG_SCORE_THRESHOLD 環境變數化（修正 1）

**動機**：審查者擔心 L2 normalize 後 raw IP score 可能拉高、繼續用 0.22 會放任垃圾湧入 LLM。但 baron 決策**不無腦升 0.40**——先 env 化、實測 raw score 後動態調整。

**改動 1：`settings.py` 新增常數**：
```python
# settings.py 新增
import os

# Phase 4.7? MODEL-1+2 修正 1：RAG retrieve 分數閾值（env override）
# 保留現有 0.22 預設、env override 讓 baron 觀察 raw score 後動態調整
# 推測 L2 normalize 後可能需升到 0.35-0.45、待 RAG-3 收實測數據確認
RAG_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", "0.22"))
```

**改動 2：`rag_retriever.py:120` 改用 settings 常數**：
```python
# 原:
# filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > 0.22]

# 改為:
from settings import RAG_SCORE_THRESHOLD

filtered_docs = [(doc, score) for doc, score in docs_with_scores if score > RAG_SCORE_THRESHOLD]
```

**使用方式（baron OrcStack）**：
```bash
# 觀察 raw score 後若需調閾值、不用 commit:
export RAG_SCORE_THRESHOLD=0.40
pkill -f web_server.py
nohup venv/bin/python web_server.py > /tmp/webserver_console.log 2>&1 &

# 或寫進 .env（永久生效）:
echo "RAG_SCORE_THRESHOLD=0.40" >> .env
```

### 4.7 落地策略總覽

| 子項 | 位置 | 行數估計 |
|---|---|---|
| 4.1 L2 normalize helper（修正 3 防禦升級）+ 4 處 embed call 套用 + 4 處 `output_dimensionality` 抽常數 | `config.py` | +40 / -8 |
| 4.2 短 chunk 過濾（修正 2 + 修正 4 合併版）+ `_create_vector_store` 改 | `processor/rag_processor.py` | +50 / -1 |
| 4.3 raw score logging（baron 補充一） | `rag_retriever.py` | +10 |
| 4.5 settings 顯式化常數 | `settings.py` 或 module-level | +3 |
| **4.6 `RAG_SCORE_THRESHOLD` env 化（修正 1）** | `settings.py` + `rag_retriever.py:120` | +5 / -1 |
| 新增 `tests/test_embedding_normalize.py`（含修正 3 三個新 case）| new | +120 (8 tests) |
| 新增 `tests/test_rag_chunk_filter.py`（含修正 2 兩個新 case + 修正 4 完整 8 個）| new | +130 (10 tests) |
| **總計** | 6 檔 | +358 / -10 |

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 緩解 |
|---|---|---|
| 既有 vector store 不相容（混用 raw + normalized 向量導致 retrieve 失準） | 🔴 **必清重建** | §4.4 三步驟 backfill（baron 補充三） |
| 768 維 MRL 降維後語意品質下降 | 🟡 中 | 官方「near-peak quality」+ 實測對比 |
| `_is_chunk_meaningful` 規則誤殺有意義短條目 | 🟡 中 | log 印前 15 字元 + env override（`RAG_MIN_CHUNK_CHARS` / `RAG_MIN_CHUNK_RESUME_SLIDES`） |
| 純數字過濾誤殺「Q4 2024」這種混合 case | 🟢 低 | 規則是「**整段**純數字 `^\d+$` 才過濾」、混合不會撞 |
| **LangChain score 轉換歧義（baron 補充一）** | 🟡 已查證 + 緩解 | 已確認 0.4.1 對 MAX_INNER_PRODUCT 回 raw IP；本 commit **加 raw score logging 不動閾值**、屬 RAG-3 校準 |
| L2 normalize 對既有 retrieve 邏輯影響 | 🟢 低 | `retrieve_with_context` 簽名不變、只是 score 分布變 |
| Gemini Embedding 2 quota / 計費 | 🟢 低 | $0.20/1M tokens × < 10 份 < $0.01 |
| backfill 撞正在跑的 SSE / retrieve（baron 補充三）| 🟡 中 | §4.4 先 pkill 再 rm-rf 再重啟（三步驟 SOP） |
| 0.22 閾值對 normalized score 太低 → retrieve 召回偏多 | 🟡 中（暫時可接受） | 留 RAG-3 校準、本 commit 提供 raw score logging |
| L2 normalize 在 EmbeddingModel 內、其他 LangChain caller 不期望 | 🟢 低 | LangChain Embeddings 抽象不強制 unnormalized；FAISS IP 對 normalized 向量 OK |
| **分數閥值預設 0.22、L2 後可能放任垃圾湧入 LLM**（審查者觀點）| 🟡 中 | **修正 1（§4.6）env override + 第一輪實測**——baron 觀察 raw score 後可 `export RAG_SCORE_THRESHOLD=0.40` 即時調、不用 commit |
| **markdown 噪聲 chunk 可能漏判邊界 case**（如 `"##\n--"` 9 字元）| 🟢 低 | 修正 2 已用 `_MD_NOISE_RE` 清符號計字、log 印前 15 字元便於 baron 調試 |

---

## §6 測試與 E2E 驗證計畫

### 6.1 單元測試（新增）

#### `tests/test_embedding_normalize.py`（5 個 test）

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_l2_normalize_unit_vector_unchanged` | norm=1 向量保持不變（1e-6 容差） |
| 2 | `test_l2_normalize_zero_vector_no_crash` | 零向量返回原樣、不 ZeroDivisionError |
| 3 | `test_l2_normalize_typical_768_dim` | 768 維隨機向量 normalize 後 norm ≈ 1.0 |
| 4 | `test_l2_normalize_preserves_direction` | `_l2_normalize([3, 4])` → `[0.6, 0.8]` |
| 5 | `test_embed_documents_outputs_normalized` | mock SDK、`embed_documents` 結果全部 norm ≈ 1.0 |
| **6** | **`test_l2_normalize_empty_list`** | **修正 3：空 list `[]` 直接回 `[]`、不 crash** |
| **7** | **`test_l2_normalize_none_handling`** | **修正 3：`None` 直接回 `None`（avoid TypeError）** |
| **8** | **`test_l2_normalize_near_zero_float32`** | **修正 3：norm < 1e-6 視為零向量、回 `[0.0] * len`** |

> tests 數量：**5 個 → 8 個**（含修正 3 三個新 case）。原 #2 `test_l2_normalize_zero_vector_no_crash` 應改為 `test_l2_normalize_zero_vector_returns_zeros`（修正 3 行為已變）。

#### `tests/test_rag_chunk_filter.py`（8 個 test、含 baron 補充二全部規則）

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_filter_short_chunk_under_10_chars_default` | `doc_type='academic'`、`page_content='PhD'` 被過濾 |
| 2 | `test_filter_pure_digits_always` | `'2024'` 不論 doc_type 都過濾 |
| 3 | `test_keep_chunk_with_long_content` | ≥ 10 字元保留 |
| 4 | `test_resume_keeps_short_keyword` | `doc_type='resume'`、`'Python'` (6) 保留 |
| 5 | `test_slides_keeps_short_keyword` | `doc_type='slides'`、`'Docker'` (6) 保留 |
| 6 | `test_keep_email_regardless_length` | `'a@b.c'` 保留（雖然 5 字元）|
| 7 | `test_keep_phone_regardless_length` | `'+886-912-345678'` 保留 |
| 8 | `test_keep_url_regardless_length` | `'https://x.com'` 保留 |
| **9** | **`test_filter_markdown_noise_only`** | **修正 2：`'## Summary\n---'`（11 字元、實質 7 字元）被過濾** |
| **10** | **`test_filter_separator_lines`** | **修正 2：純分隔線 `'---\n***\n___'` 過濾（實質 0 字元）** |

> tests 數量：**8 個 → 10 個**（含修正 2 兩個新 case）。

可額外加：`test_env_override_min_chunk_chars`（`RAG_MIN_CHUNK_CHARS=5` 生效）。

### 6.2 整合測試

mock Gemini API 看 `embed_documents`：
- 驗證 `model_name=gemini-embedding-2`（或 env override 值）
- 驗證 `output_dimensionality=EMBEDDING_OUTPUT_DIMENSIONS`（768）
- 驗證輸出全部 normalized

### 6.3 手動 E2E（baron OrcStack、依 §4.4 三步驟）

依 §4.4 完整 5 步驟，重點觀察：

```bash
# Step 4 後：
grep "[chunk filter]" logs/pipeline.log | tail -5
# 預期：doc_type 標籤明確、印前 15 字元 sample

# Step 5 後（baron 補充一驗證）：
grep "[retrieve raw]" logs/chat.log | tail -10
# 預期：raw score 分布（min/max/mean）
# 比對 pre-normalize（0.17-0.27）vs post-normalize（cosine 子集、預期更寬）
```

### 6.4 完整回歸

```bash
venv/bin/pytest tests/ -q
# 預期：164 baseline (MODEL-9 後) + 18 新增（8 embedding + 10 chunk filter）= 182 passed, 3 skipped
```

---

## §7 不可做 / 不可動清單

- ❌ `pipeline_core.py`：未動
- ❌ `web_server.py`：未動
- ❌ `processor/*` 其他模組（`pdf_processor` / `md_cleaner` / `translate_processor` / `md_restore_processor` / `slides_processor` / `resume_processor` 等）：未動
- ❌ `static/*` / DB / 前端：未動
- ❌ 業務邏輯（RAG retrieval 流程、vector store schema、chunk 切 H1 規則、`MAX_INNER_PRODUCT`）：未動
- ❌ **score 閾值 0.22**：本 commit **加 logging 但不動閾值**（屬 RAG-3 範圍、§3.5 + §4.3 已說明）
- ❌ `BATCH_SIZE = 32`：未動（128 batching 在 🚫 不做清單）
- ❌ MinerU SCP（MODEL-10）/ LLMClient timeout（MODEL-9 已完成）：未動
- ❌ `tools/regen_rag.py`（RAG-2 範圍）：未動
- ❌ `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` / `templates/*`：未動
- ❌ 既有 plan / 執行 / hotfix 報告：未動
- ❌ commit / push：未動
- ✅ 可動（本 commit 範圍、v3 已含 4 個審查修正）：
  - **修改** `config.py`（EmbeddingModel + L2 helper **含修正 3 防禦升級** + 4 處 embed call + 抽常數）
  - **修改** `processor/rag_processor.py`（加 `_is_chunk_meaningful` **含修正 2 markdown 噪聲 + 修正 4 合併**）
  - **修改** `rag_retriever.py`（加 raw score logging + **修正 1 把寫死 0.22 改用 `RAG_SCORE_THRESHOLD` 常數**）
  - **修改** `settings.py`（新增 `EMBEDDING_OUTPUT_DIMENSIONS` + **修正 1 `RAG_SCORE_THRESHOLD`**）
  - **新增** `tests/test_embedding_normalize.py`（**8 tests、含修正 3 三個新 case**）
  - **新增** `tests/test_rag_chunk_filter.py`（**10 tests、含修正 2 兩個新 case + 修正 4 完整**）

---

## §8 Open Questions（待 baron 決策）

| # | 問題 | 推薦答案 |
|---|---|---|
| Q1 | 升 `gemini-embedding-2` 還是繼續 `text-embedding-004` / `gemini-embedding-001`？ | ✅ **gemini-embedding-2**（settings.py:19 已預設、本 commit 補做驗證） |
| Q2 | 維度選 768 / 1536 / 3072？ | **768**（FAISS schema 不變、官方「near-peak quality」、storage 省 75%） |
| Q3 | 短 chunk 過濾閾值 default 10 / resume-slides 3 是否合適？ | **先試 10 / 3**（env override `RAG_MIN_CHUNK_CHARS` / `RAG_MIN_CHUNK_RESUME_SLIDES`）；baron 觀察 log 若過多被誤殺再調 |
| Q4 | score 閾值是否在本 commit 一併改？ | **不改、留 RAG-3** — §3.5 LangChain 歧義已查證、本 commit 加 raw logging 收實測；改閾值會撞「相關 chunk 全被擋」回歸 |
| Q5 | 是否要寫 backfill CLI（RAG-2）？ | **不寫** — baron 確認手動清就好、依 §4.4 三步驟 SOP；RAG-2 是長期方案 |
| Q6 | 既有 15-1 chunk 處理（短文合併）保留還是合併？ | **保留** — 15-1 是 markdown 階段「同 section text item 合併」、本 commit 是 chunk 入庫 filter、互補 |
| Q7 | L2 normalize 在 EmbeddingModel 內還是 RagProcessor 內？ | **EmbeddingModel 內** — 所有 embed call 自動 normalize、單一來源、retrieve query 也適用 |
| Q8 | Gemini Embedding 2 BATCH_SIZE 32 是否調整？ | **不改** — 128 batching 在 🚫 不做清單 |
| Q9 | baron 補充二的防禦放寬規則完整嗎？ | 推薦規則：doc_type=resume/slides 放寬到 3 + email/url/phone 保留 + 純數字過濾；可能需要時加更多（如保留 ISBN / DOI 等學術 ID）|
| Q10 | baron 補充三 backfill 流程：要在執行報告寫成 SOP 嗎？ | ✅ **寫成 SOP** — §4.4 五步驟、未來 RAG-2 backfill CLI 之前都會用到 |
| Q11 | 4 處 embed call 全部 L2 normalize？（含 `embed_image`）| ✅ **全部** — 確保 retrieve query / document / image 同空間 |
| Q12 | `_is_chunk_meaningful` 需要從 `_create_vector_store` 傳 `doc_type`？ | ✅ **需要** — 從 caller 傳入或從 `paper_data` 取；無 doc_type 時退到 default ≥ 10 |
| **Q11**（v3 審查補充）| 閾值預設 0.22 還是審查者建議 0.40？ | **0.22 + env override**（修正 1）— 保留現有預設、`RAG_SCORE_THRESHOLD` env var、第一輪實測 raw score 後 baron 自行 `export RAG_SCORE_THRESHOLD=0.40` 即時調、不用 commit |
| **Q13**（v3 審查補充）| 修正 3 零向量行為改成回 `[0.0] * len`、會不會破壞 caller？ | **不破壞** — caller 用 `embed_documents` 結果丟進 FAISS；零向量極罕見、即使發生 FAISS IP 計算 = 0、retrieve 不會選中、行為合理 |
| **Q14**（v3 審查補充）| 修正 2 `_MD_NOISE_RE` 規則 `[#*_~`\-+>|\[\]\s]` 範圍合適？ | **先試此 set** — 涵蓋 commonmark 主要符號；若實測有誤殺（如 `<code>` HTML chunk）再調 |

---

## §9 推薦執行順序

1. **本輪結束**：baron 過目本 plan + Q1-Q14 推薦答案、特別確認：
   - Q3 字元下限 10 / 3
   - Q4 不動 score 閾值 0.22（改 env 化、屬修正 1）
   - Q5 不寫 backfill CLI（依 §4.4 SOP）
   - **Q11 新增**：閾值 env override 預設 0.22（修正 1）
2. **下一輪 MODEL-1+2 commit**（~2 小時、1 個 commit、含 4 個審查修正）：
   - `config.py` L2 normalize（4 處、**修正 3 防禦升級**）+ 抽常數
   - `processor/rag_processor.py` 加 `_is_chunk_meaningful`（**修正 2 markdown 噪聲 + 修正 4 合併**）
   - `rag_retriever.py` 加 raw score logging（baron 補充一）+ **修正 1 改寫死 0.22 為 `RAG_SCORE_THRESHOLD`**
   - `settings.py` 加 `EMBEDDING_OUTPUT_DIMENSIONS` + **`RAG_SCORE_THRESHOLD`**
   - 新增 `tests/test_embedding_normalize.py`（**8 tests、含修正 3 三個新 case**）
   - 新增 `tests/test_rag_chunk_filter.py`（**10 tests、含修正 2 兩個新 case**）
   - pytest → 預期 **182 passed 3 skipped**
3. **baron OrcStack 端**（依 §4.4 五步驟 SOP）：
   - pkill → rm-rf → 重啟
   - 重新上傳 / 觸發 rag stage 1 份 paper
   - 觀察 `[chunk filter]` + `[retrieve raw]` log
   - **觀察 raw score 分布後、若需調閾值**：`export RAG_SCORE_THRESHOLD=0.40` + 重啟 web_server（**不用 commit**、修正 1 env override）
4. **未來 RAG-3 後續**：收 1-2 週實測數據、校準 `RAG_SCORE_THRESHOLD` 預設值（依實測決定、可能升 0.35-0.45 區間）

---

## §10 結尾簡短說明

### SDK probe（`output_dimensionality`）結果

**✅ 已驗證**（§2.5）：
- `venv/bin/python -c "from google.genai import types; print(types.EmbedContentConfig(output_dimensionality=768))"` → `output_dimensionality=768` 為 SDK 原生欄位
- 4 處 `config.py` 既有 code 已用 `output_dimensionality=768` 正常運作
- 結論：本 commit 只是**抽常數**、不需新探索

### 推薦維度選擇

**768**（plan §8 Q2 推薦答案）：
- 維持現有 FAISS schema（既有 retrieve 邏輯零改）
- 官方文件稱「near-peak quality」
- Storage 比 3072 維省 75%
- Cost 與維度無關（按 input tokens 計費）
- **降維後必須手動 L2 normalize**（這是本 commit 主要工作之一）

### 預估工時 + 風險

| 項 | 評估 |
|---|---|
| 工時 | **~2 小時 / 1 commit**（6 個檔改動 + 13 個新 pytest） |
| 改動範圍 | `config.py` 改 5 處 + `processor/rag_processor.py` +40 行 + `rag_retriever.py` +10 行 logging + `settings.py` +3 行 + 2 個新 test 檔 |
| 風險 | 🟡 **中** — 主要 score 區間變化、retrieve 召回暫時偏多（為 RAG-3 收數據用）+ baron 補充二誤殺風險（log 防禦） |
| 不動 | `pipeline_core` / `web_server` / 其他 `processor/*` / RAG retrieval 邏輯 / **score 0.22 閾值** / BATCH_SIZE / vector store schema |
| 回退 | 1 個 commit revert + baron 手動清舊向量庫（§4.4） |

### LangChain FAISS score 轉換歧義處理建議（baron 補充一）

**已查證 + 緩解**：
- langchain-community 0.4.1 對 `MAX_INNER_PRODUCT` 的 `similarity_search_with_score` 回 **raw IP score**（已查源碼確認、非 normalize 後 [0, 1]）
- 既有 `rag_retriever.py:107-110` 註解「相關 0.23-0.27」與此一致
- **但 L2 normalize 後具體相關 chunk 的 cosine 區間值需實測**（提案 0.45-0.75 是假設）
- **策略**：本 commit **加 raw score logging 不動閾值**（§4.3）、留 RAG-3 收 1-2 週實測數據後校準

### baron OrcStack 端 backfill 流程（依 §4.4 五步驟、baron 補充三 SOP）

```bash
# Step 1: 停 web_server（避免 SSE 撞 missing index）
pkill -f "web_server.py" && sleep 1
ps aux | grep web_server.py | grep -v grep  # 預期空

# Step 2: 安全刪舊向量庫
rm -rf output/*/*/vector_store/
find output -name vector_store -type d | wc -l  # 預期 0

# Step 3: 背景啟動 web_server
> /tmp/webserver_console.log
nohup venv/bin/python web_server.py > /tmp/webserver_console.log 2>&1 &
sleep 3
head -10 /tmp/webserver_console.log

# Step 4: 重新觸發 rag stage、觀察 log
tail -50 logs/pipeline.log | grep -E "chunk filter|分割|向量库"

# Step 5: 提問、觀察 raw score 為 RAG-3 收數據
grep "\[retrieve raw\]" logs/chat.log | tail -10
```

### 是否需要先做 probe？

**不需要**：
- §2.5 已確認 `output_dimensionality` SDK 原生支援
- §2.3 已查證 LangChain 0.4.1 `similarity_search_with_score` 對 `MAX_INNER_PRODUCT` 回 raw IP
- 兩個關鍵 SDK / lib API 都已驗證、可直接進實作 commit

---

## §11 不可動清單遵守狀態（plan 階段）

- [x] 業務檔（`config.py` / `processor/*` / `rag_retriever.py` / `settings.py` / `pipeline_core.py` / `web_server.py` / `static/*`）：**未動**（只 view / grep）
- [x] `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` / `templates/*`：**未動**
- [x] 既有 plan / 執行 / hotfix 報告（含 MODEL-9 plan）：**未動**
- [x] DB / 設定 / 前端：**未動**
- [x] commit / push：**未動**
- [x] 本 plan 為新增唯一檔（+ TODO.md 狀態更新、依任務指示步驟 6）
