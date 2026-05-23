# Google Gemini 2026 最新旗艦模型與 API 開發指南

> 本文件彙整了 **Google 於 2026 年 I/O 大會及春季正式 GA 的最新一代 Gemini 模型系列技術規格**。
> 重點聚焦於 2026 年 5 月 19 日甫發布的 **Gemini 3.5 Flash**，以及 2026 年 4 月 22 日 GA 的**多模態嵌入旗艦 Gemini Embedding 2**。
> 本指南亦提供 2026 年全新一代統一 Python SDK `google-genai` 的標準開發範例、呼叫限制與開發實務建議。

---

## 1. 核心模型矩陣與規格 (Core Model Matrix & Specs)

截至 **2026 年 5 月 22 日**，Google Gemini 官方推薦的最新主力模型如下：

### 1.1 大語言模型 (LLM)
| 模型名稱 (Model Name) | API 識別碼 (Model ID) | Context Window (輸入) | Max Output Tokens (輸出) | 發布狀態 / 核心定位 |
| :--- | :--- | :--- | :--- | :--- |
| **Gemini 3.5 Flash** | `gemini-3.5-flash` | **1,048,576 (1M)** | **65,536 (65k)** | **GA (2026/05/19)**<br>最新旗艦 Flash。吞吐量提升 4 倍，編譯與 Agentic 評測超越 3.1 Pro，支援動態 Thinking。 |
| **Gemini 3.5 Pro** | *未公開* | *未公開* | *未公開* | **內部測試中**<br>預計 2026 年 6 月正式發布，定位為極致推理與複雜架構設計模型。 |
| **Gemini 2.0 Flash** | `gemini-2.0-flash` | 1,048,576 (1M) | 8,192 | **Legacy 降級**<br>Google 建議 2026 年新專案全面移轉至 3.5/2.5 世代，舊版將逐步限流。 |

> [!IMPORTANT]
> **Gemini 3.5 Flash 的輸出突破**：
> 傳統 LLM 的最大輸出通常限制在 8k 左右。Gemini 3.5 Flash 首次將單次最大輸出拓寬至 **65,536 Tokens**，這使其在「長程式碼生成」、「大型論文全還原翻譯」與「深度多文檔交叉摘要」等場景中，徹底擺脫了輸出中斷的痛點。

### 1.2 向量嵌入模型 (Embedding)
| 模型名稱 (Model Name) | API 識別碼 (Model ID) | Context Window | 原生維度 (Dimensions) | 特色與支援模態 |
| :--- | :--- | :--- | :--- | :--- |
| **Gemini Embedding 2** | `gemini-embedding-2` | **8,192 tokens** | **3072 維**<br>(支援 MRL 降維) | **GA (2026/04/22)**<br>Google 旗艦多模態嵌入模型。**原生支援 Text, Image, Video, Audio, PDF** 混合向量化。 |
| **Text-embedding-004**| `text-embedding-004` | 2,048 tokens | 768 維 | **Legacy 降級**<br>傳統純文字向量模型。2026 年新專案建議升級至 Gemini Embedding 2。 |

> [!TIP]
> **Matryoshka 降維技術 (MRL)**：
> `gemini-embedding-2` 採用了 Matryoshka Representation Learning。雖然預設輸出 3072 維以提供極致的語意對齊，但開發者可以在 API 呼叫時**直接指定輸出為 1536 或 768 維**，向量特徵品質幾乎無損，但能為資料庫（如 FAISS、Pgvector）節省高達 **50% ~ 75%** 的儲存與檢索計算開銷！

---

## 2. 全新 `google-genai` SDK 範例程式碼

> [!WARNING]
> **SDK 換代**：
> 舊版的 `google-generativeai` (Python) 與 `@google-cloud/vertexai` 於 2026 年已全面進入維護模式。
> Google 全新推出 **`google-genai`** 統一 SDK，不論是使用 AI Studio (API Key) 還是 Google Cloud Vertex AI，都使用同一套 Client 語法。

### 2.1 基礎安裝
```bash
pip install -U google-genai
```

### 2.2 範例 A：基礎內容生成與動態 Thinking (Gemini 3.5 Flash)
```python
import os
from google import genai
from google.genai import types

# 1. 初始化 Client (自動讀取環境變數 GEMINI_API_KEY)
client = genai.Client()

# 2. 呼叫 Gemini 3.5 Flash 並設定 Dynamic Thinking
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="請為 Mad Professor 專案規劃一套連線自癒的重試偽代碼，需使用指數退避。",
    config=types.GenerateContentConfig(
        # 2026 新增功能：允許設定 Thinking 深度，平衡延遲與推理品質
        thinking_config=types.ThinkingConfig(thinking_budget=1024),
        temperature=0.3,
        max_output_tokens=8192
    )
)

print(response.text)
```

### 2.3 範例 B：多模態 PDF 還原與解析 (Gemini 3.5 Flash)
```python
from google import genai
from google.genai import types

client = genai.Client()

# 1. 上傳 PDF 檔案至 Google File API (支持大檔案與 Token 優化)
pdf_file = client.files.upload(file="docs/academic_paper.pdf")
print(f"檔案上傳成功，URI: {pdf_file.uri}")

# 2. 進行多模態還原分析
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        pdf_file,
        "請將此學術論文還原為乾淨的 Markdown 格式，將行內公式以 Latex 表示，保留圖表說明。"
    ],
    config=types.GenerateContentConfig(
        temperature=0.1,
        # Gemini 3.5 Flash 最大支援 65,536 tokens 輸出！
        max_output_tokens=40000 
    )
)

print(response.text)

# 3. 清理雲端暫存檔案
client.files.delete(name=pdf_file.name)
```

### 2.4 範例 C：多模態與文字向量化及 MRL 降維 (Gemini Embedding 2)
```python
from google import genai
from google.genai import types

client = genai.Client()

# 文字與圖片混合多模態向量化 (Gemini Embedding 2)
image_part = client.files.upload(file="output/extracted_chart.png")

response = client.models.embed_content(
    model="gemini-embedding-2",
    contents=[
        "這是 Mad Professor 專案萃取出的圖表，描述 RAG 相似度隨閥值變化的關係：",
        image_part
    ],
    config=types.EmbedContentConfig(
        # 利用 MRL 技術將 3072 原生維度安全降至 768 維，優化 FAISS 儲存
        output_dimensionality=768
    )
)

# 獲取 768 維的 L2 正規化特徵向量
embedding_vector = response.embeddings[0].values
print(f"向量維度: {len(embedding_vector)}")
print(f"前 5 個特徵值: {embedding_vector[:5]}")
```

---

## 3. API 使用限制與開發者守則 (Usage Limits & Guardrails)

在將 `gemini-3.5-flash` 與 `gemini-embedding-2` 引入生產環境或 Mad Professor 專案時，開發者必須遵循以下硬性限制：

### 3.1 速率限制 (Rate Limits - 以 AI Studio Free/Pay-as-you-go 為例)
1. **付費模式 (Pay-as-you-go)**：
   * **RPM (每分鐘請求數)**：預設 1,000 RPM (可申請提升至 5,000 RPM)。
   * **TPM (每分鐘 Tokens 數)**：4,000,000 TPM。
   * **RPD (每日請求數)**：無限制。
2. **免費測試模式 (Free Tier)**：
   * **RPM**: 15 RPM。
   * **TPM**: 1,000,000 TPM。
   * **RPD**: 1,500 RPD。

> [!CAUTION]
> **429 錯誤預防**：
> 在長文分塊（Tiling）或大文件向量化時，若同時並發發送 128 批次請求，極易在免費額度或併發陡增時觸發 `429 Rate Limit`。開發者**必須**引入隨機抖動指數退避重試（如 `MODEL-9` 所實作的自癒機制），絕不能進行硬編碼等待。

### 3.2 知識切分時間 (Knowledge Cut-off)
* **Gemini 3.5 Flash**：**2025 年 1 月**。
* 任何涉及 2025 年 1 月之後的外部事實（如 2025/2026 的最新政策、開源庫升級），必須透過 **Google Search Grounding (自動聯網)** 或 RAG 本地文件注入進行事實修正。

---

## 4. 開發者關鍵參考與建議資料 (Developer Resources)

### 4.1 引用與官方網頁 (References)
1.  **Google AI Studio 官方開發平台**: [https://aistudio.google.com/](https://aistudio.google.com/)
2.  **新一代 Python SDK GitHub 倉庫**: [https://github.com/googleapis/python-genai](https://github.com/googleapis/python-genai)
3.  **`google-genai` Python API 參考手冊**: [https://googleapis.github.io/python-genai/](https://googleapis.github.io/python-genai/)
4.  **Google I/O 2026 模型發布說明 (DeepMind)**: [https://deepmind.google/technologies/gemini/](https://deepmind.google/technologies/gemini/)

### 4.2 Mad Professor 專案升級建議
基於 2026 最新模型的發布，對我們目前正在規劃的**「Docker 化前置工作」與「模型優化藍圖」**有以下直接推動效益：
*   **優化點 A (針對翻譯長文)**：
    使用 `gemini-3.5-flash` 的 **65,536 輸出 Tokens** 特性，在進行 Bypass 快速通道時，即使是 5,000 字至 10,000 字的長履歷或學術論文 Section，亦能**一次性送入翻譯並一次性完整輸出**，免去切碎翻譯後再拼接造成的「斷句語法破碎」與「排版錯亂」。
*   **優化點 B (針對多模態 RAG)**：
    升級向量庫至 `gemini-embedding-2`，我們可以直接在 Markdown 提取出圖片（例如論文中的折線圖、履歷中的照片）時，**連同周圍的 Context 文字一起送入 Embedding**。這使得用戶在進行 QA 對話時，連同「圖表意圖」也能被 FAISS 召回，大幅提升 AI 問答的智慧邊際。
*   **優化點 C (MRL 降維減資)**：
    使用 `gemini-embedding-2` 呼叫並指定 `output_dimensionality=768`。如此一來，我們既能獲得二代強大模型跨語言對齊的最新優勢，又**完全不需要修改現有 FAISS 向量庫的維度配置（維持 768 維）**，完美做到無痛升級！
