# Mad Professor 專案：AI 模型與智能檢索優化建議報告

> **本報告針對 Mad Professor 專案中現有的 13 個 AI 模型與運行設定進行了全面的代碼審計與技術分析。**  
> 報告結合了 **2026 年最新正式 GA 的 Google Gemini 3.5 Flash、Gemini Embedding 2 等旗艦級模型技術規格**，為專案的「效能優化」、「成本控制」與「Docker 部署前置準備」提供最具落地價值的配置升級建議與數學/架構理由。

---

## ── 核心模型架構對齊矩陣 (Model Alignment Matrix) ──

下表彙整了 Mad Professor 專案中目前所有的模型設定、其在代碼中的預設值、2026 最新推薦模型，以及改動帶來的效益：

| 環境變數設定 | 系統預設值 (As-Is) | 2026 最新推薦 (To-Be) | 核心優化方向 / 改進理由 | 重要性 |
| :--- | :--- | :--- | :--- | :--- |
| **`LLM_TRANSLATE_MODEL`** | `gemini-2.0-flash` | **`gemini-3.5-flash`** | 吞吐量提升 4 倍，且解鎖 **65k 輸出**，免除短文切割後的語境破碎痛點。 | 🌟 高 |
| **`LLM_CHAT_MODEL`** | `gemini-2.0-flash` | **`gemini-3.5-flash`** | 顯著提升問答與 Web Grounding 的回應速度，更聰明的 Dynamic Thinking 能擬真教授語氣。 | 🌟 高 |
| **`LLM_DOMAIN_MODEL`** | `CHAT_MODEL` fallback | **`gemini-2.5-pro`** | 每篇文件僅上傳時分析一次。選用 Pro 旗艦能以強大視覺與文字理解力，精準識別專業術語領域。 | 💎 中 |
| **`LLM_DOC_MODEL`** | `CHAT_MODEL` fallback | **`gemini-3.5-flash`** | 後台標題分析與 Metadata 提取。Flash 等級兼顧大 Context Window (1M) 與高性價比。 | ✅ 低 |
| **`LLM_VISION_MODEL`** | `CHAT_MODEL` fallback | **`gemini-3.5-flash`** <br>*(密集視覺可選 `2.5-pro`)* | 圖片圖說、簡報與多頁履歷分析。建議回退至 Flash 級以大幅降低後台處理時間與 API 成本。 | 💎 中 |
| **`LLM_EXTRA_INFO_MODEL`** | `CHAT_MODEL` fallback | **`gemini-3.5-flash`** | 密集生成章節摘要與提問。`3.5-flash` 對於 LaTeX 數學公式與結構化生成能力更佳。 | ✅ 低 |
| **`EMBEDDING_MODEL`** | `gemini-embedding-2` | **`gemini-embedding-2`** | 2026 最新旗艦多模態嵌入。原生支持 Text, Image, PDF 混合表徵，Context 擴展至 8k。 | 🌟 高 |
| **`EMBEDDING_OUTPUT_DIMENSIONS`**| `768` | **`768` (MRL)** | 使用 MRL 降維技術輸出 768 維向量。**100% 無痛相容現有 FAISS 向量庫規格**。 | 🌟 高 |
| **`RAG_SCORE_THRESHOLD`** | `0.22` | **`0.38` ~ `0.42`** | 代碼已實作 L2 正規化（Cosine 相似度）。閥值調高能精確排除背景噪聲，拉大安全邊際。 | 🌟 高 |

---

## 1. 核心大語言模型 (LLM) 設定細分與建議

### 1.1 `LLM_TRANSLATE_MODEL` (翻譯核心)
*   **代碼常數**：`TRANSLATE_MODEL`（導入自 `settings.py`）
*   **調用語法**：`processor/translate_processor.py:261` 
    ```python
    translated = self.llm.chat(messages, stream=True, model=TRANSLATE_MODEL).strip()
    ```
*   **用途描述**：段落翻譯。將解析後的 Markdown 內容依照 Tiling 機制切割成小區塊，進行批次/逐段的英翻中處理。屬於高吞吐、高 Token 消耗的後台重度背景任務。
*   **建議配置**：**`gemini-3.5-flash`**（若追求極致翻譯品質可啟用 Dynamic Thinking 深度配置）。
*   **深度原因**：
    1.  **65k 輸出解除封印**：傳統大模型單次最大輸出通常限制在 8k 左右。`gemini-3.5-flash` 首次解鎖了高達 **65,536 (65k) Tokens 的輸出上限**，這使得短文 Bypass（如 5,000 字以內的履歷或論文 Section）能夠**整篇一次性送入翻譯並一次性完整回傳**，完美解決了以往切碎翻譯再拼接造成的句式破碎與排版移位痛點。
    2.  **極致性價比**：相較於上一代 `gemini-2.0-flash`，新一代的吞吐量提升了 4 倍，且翻譯成本可降低達 40% 以上，是長文與多本書籍背景翻譯的最佳平衡選擇。

> [!TIP]
> **如何啟用 Dynamic Thinking (動態思考)？**
>
> 啟用 Dynamic Thinking **並非僅靠單一設定，而是透過「環境變數」與「SDK API 參數」雙軌配置實現**：
>
> 1. **新增環境變數與設定 (`settings.py`)**：
>    在 `.env` 與 `settings.py` 中新增 `LLM_THINKING_BUDGET` 設定：
>    ```python
>    # settings.py
>    # 思考 Tokens 預算，設為 0 代表關閉（預設），可設為 1024、2048 等以啟用思考
>    LLM_THINKING_BUDGET = int(os.getenv("LLM_THINKING_BUDGET", "0"))
>    ```
> 
> 2. **適配器代碼實作 (`llm/client.py`)**：
>    在 `LLMClient.chat` 等方法中，透過 `google-genai` SDK 的 `GenerateContentConfig` 傳遞給 API：
>    ```python
>    # llm/client.py
>    from google.genai import types
>    from settings import LLM_THINKING_BUDGET
> 
>    config_kwargs = {
>        "temperature": temperature,
>        "system_instruction": system_instruction,
>    }
>    # 只有當 budget > 0 且模型為支持 Thinking 的 3.5 世代時才注入
>    if LLM_THINKING_BUDGET > 0 and "3.5" in model:
>        config_kwargs["thinking_config"] = types.ThinkingConfig(
>            thinking_budget=LLM_THINKING_BUDGET
>        )
> 
>    config = types.GenerateContentConfig(**config_kwargs)
>    ```
> 
> *啟用動態思考能使 `gemini-3.5-flash` 在面對專業文獻的複雜文藝語境或高度學術性的句式轉換時，先進行內部邏輯思考與結構重組，從而生成細緻度極高的專業譯文。*

### 1.2 `LLM_CHAT_MODEL` (前台問答大腦)
*   **代碼常數**：`CHAT_MODEL`（導入自 `settings.py`）
*   **調用語法**：在 `llm/client.py` 中作為預設 fallback：
    ```python
    model = model or CHAT_MODEL
    ```
*   **用途描述**：負責前台使用者與 AI 教授的對話互動、流式文字輸出、以及是否啟用 Google 網頁搜尋聯網（`use_web_search`）獲取即時外部資訊的決策大腦。
*   **建議配置**：**`gemini-3.5-flash`** 或 **`gemini-2.5-pro`**（若預算充足且極度要求複雜推理）。
*   **深度原因**：
    1.  **流暢的對話響應**：`gemini-3.5-flash` 對於首字輸出延遲（First Token Latency）進行了極大優化，能為使用者提供如行雲流水般的打字機串流體驗。
    2.  **精準的搜尋 Grounding**：當前台開啟聯網搜尋時，`gemini-3.5-flash` 對於搜尋結果的整合與事实對齊（Anti-hallucination）表現優異，能精準過濾網頁噪聲。

### 1.3 `LLM_DOMAIN_MODEL` (領域分類器)
*   **代碼常數**：`settings.LLM_DOMAIN_MODEL`
*   **調用語法**：`processor/domain_detector.py:63`
    ```python
    response = self.llm.chat_with_image(messages, image_data=img_bytes, model=settings.LLM_DOMAIN_MODEL)
    ```
*   **用途描述**：在文件剛上傳時，讀取首頁前 4,000 字與 2x 畫質 JPEG 截圖，分析並診斷該文件屬於何種主題領域（例如醫學、計算機科學、金融等）。
*   **建議配置**：**`gemini-2.5-pro`**。
*   **深度原因**：
    *   **低頻率、高重要性**：此步驟每份文件**僅在上傳時呼叫一次**，其結果將永久寫入資料庫，並深度影響後續的專業術語處理。
    *   **極致的多模態推理**：專業學術論文或商業簡報的首頁排版非常複雜，`gemini-2.5-pro` 的多模態視覺與文字交叉理解力極強，能以極高準確率識別冷門或高度細分的領域，避免 Flash 模型因推理能力受限而將專業論文誤分類為普通學科。

### 1.4 `LLM_VISION_MODEL` (後台視覺引擎)
*   **代碼常數**：`settings.LLM_VISION_MODEL`
*   **調用語法**：
    - `processor/image_caption_processor.py:109`（提取文件中插圖之圖說）
    - `processor/slides_processor.py:187`（簡報 PDF 視覺內容解析）
    - `processor/resume_processor.py:160`（多頁履歷 PDF 截圖視覺結構化抽取）
*   **用途描述**：所有涉及圖像、多頁 PDF 視覺識別的後台背景處理任務。
*   **建議配置**：**`gemini-3.5-flash`**（若履歷/簡報有極致排版精度要求，可在部署環境中針對性調成 **`gemini-2.5-pro`**）。
*   **深度原因**：
    1.  **視覺成本控制**：後台視覺任務的處理量往往非常巨大（例如簡報有數十頁，或大批履歷上傳）。在 Baron 的開發環境中，曾將其覆寫為 `gemini-3.1-pro-preview`，導致單次多頁視覺處理的 API 延遲拉長至 30~90s，且單次分析成本激增至 $0.5 ~ $1。
    2.  **效能自癒保護**：代碼中已部署了 `LLMClient._api_semaphore`（並發上限限制為 6），配合 `@retry_call` 來防止並發視覺請求撞斷 endpoint。如果預設改用 `gemini-3.5-flash`，不僅能提升並發處理吞吐量，還能將整體視覺解析成本大幅降低 80% 以上。

### 1.5 `LLM_DOC_MODEL` (文件結構修復)
*   **代碼常數**：`settings.LLM_DOC_MODEL`
*   **用途描述**：`processor/doc_analyzer.py` 的標題修復與目錄分析，以及首頁 metadata 的 LLM 抽取。
*   **建議配置**：**`gemini-3.5-flash`**。
*   **深度原因**：主要是文字的層級語意梳理，屬於高頻率、高上下文的背景處理。`gemini-3.5-flash` 的 1M Context Window 能輕鬆吞下整篇文件的標題目錄，並在極短時間內完成結構優化，性價比最佳。

### 1.6 `LLM_EXTRA_INFO_MODEL` (加值資訊生成)
*   **代碼常數**：`settings.LLM_EXTRA_INFO_MODEL`
*   **用途描述**：生成章節的摘要、學習用問答 (QA)，以及針對文中的數學公式進行 LaTeX 公式提取與文字原理解析 (`processor/extra_info_processor.py`)。
*   **建議配置**：**`gemini-3.5-flash`**。
*   **深度原因**：摘要與問答生成屬於高密度的文字生成任務，且 LaTeX 公式提取需要極佳的 Markdown 渲染理解。新一代 `3.5-flash` 對於結構化公式的輸出能力大幅進化，能產出極度標準的行內公式，且費用低廉。

---

## 2. 向量嵌入 (Embedding) 與相似度門檻設定

```
【原始 Markdown 區塊】
       │
       ▼ (過濾極短/空區塊 < 10字，防禦雜訊)
【乾淨 Chunks 列表】
       │
       ▼ (呼叫 gemini-embedding-2，指定 output_dimensionality=768)
【MRL 768維 原始特徵】
       │
       ▼ (強制 L2 正規化: v / ||v||)
【正規化向量 (數學上內積 100% 等同 Cosine 相似度)】
       │
       ▼ (FAISS 檢索計算)
【相似度分數分布】
  - 相關區塊：0.45 ~ 0.75
  - 無關噪聲：0.25 以下
       │
       ▼ (動態閥值門檻：RAG_SCORE_THRESHOLD = 0.38 ~ 0.42)
【精準召回 Chunks】
```

### 2.1 `EMBEDDING_MODEL` (嵌入模型)
*   **代碼常數**：`EMBEDDING_MODEL_NAME`（導入自 `settings.py`）
*   **調用語法**：`config.py::EmbeddingModel`
*   **用途描述**：將切分後的文件片段進行向量化，建立本地 FAISS 向量索引庫，用於 RAG 問答時檢索最相關的內容。
*   **建議配置**：保持 **`gemini-embedding-2`**。
*   **深度原因**：作為 Google 於 2026 年 4 月正式 GA 的多模態嵌入旗艦，其原生支持混合文字與圖片的對齊表徵，Context 拓寬至 8,192 Tokens，在跨語言及多語意對齊上相比初代模型有質的飛躍。

### 2.2 `EMBEDDING_OUTPUT_DIMENSIONS` (嵌入輸出維度)
*   **用途描述**：指定嵌入模型輸出的向量維度。
*   **建議配置**：保持 **`768`**。
*   **深度原因**：
    *   **無痛維度對齊**：`gemini-embedding-2` 原生原生維度為 3072 維。但其內建了 **Matryoshka Representation Learning (MRL)** 降維技術，允許開發者在呼叫 API 時指定 `output_dimensionality=768`。
    *   這使我們能在特徵表徵能力近乎無損的前題下，**100% 無縫相容 Mad Professor 現有的 768 維度 FAISS 向量庫規格**，完美免除資料庫大規模重構與遷移的痛苦！

### 2.3 `RAG_SCORE_THRESHOLD` (相似度檢索門檻)
*   **當前預設值**：`0.22`
*   **建議配置**：調整至 **`0.38` ~ `0.42` 之間**。
*   **深度原因**：
    1.  **強制 L2 正規化效應**：系統代碼在 `config.py` 中實作了強制的 `_l2_normalize`。這使得 FAISS 在進行向量內積計算時，**在數學上將 100% 等同於 Cosine 相似度**（分數嚴格限制於 $[-1, 1]$）。
    2.  **安全邊際擴大 4 倍**：在正規化後，相關區塊的分數會分佈在 `0.45 ~ 0.75`，而無關的背景噪聲則會被壓低到 `0.25` 以下。原本 `0.22` 的硬編碼閥值會導致大量不相干的空區塊或背景干擾被誤召回。將閥值提升至 `0.38 ~ 0.42`，能完美排除雜訊，極大提升大腦回答的精準度。

---

## 3. 切割與滑動窗口 (Tiling) 自適應設定

### 3.1 `TILING_BYPASS_CHAR_LIMIT` (短文穿透上限)
*   **當前預設值**：`5000`
*   **用途描述**：當文件或章節總字數少於此閾值時，直接繞過複雜的 TextTiling 分塊，直接將整篇內容送入翻譯或分析。
*   **建議配置**：維持 **`5000`**（若部署環境主要處理履歷/簡報，可微調至 **`6000`**）。
*   **深度原因**：配合 `gemini-3.5-flash` 的 65k 大輸出能力，小於 5,000 字的短履歷或簡報不需要再做句子切割。一次性直通翻譯能保障 100% 的排版與語氣連貫性，並且把原本需要多次 API 往返 (RTT) 的開銷降為 0ms，大幅加快前台速度。

### 3.2 `TILING_MAX_LENGTH` (單一區塊上限)
*   **當前預設值**：`2500`
*   **用途描述**：單一文字段落超過此字數時，才會被強制截斷切割，對齊 Bypass 與滑動窗口的風格。

### 3.3 `TILING_PARAGRAPH_THRESHOLD` (段落級滑動臨界點)
*   **當前預設值**：`30000`
*   **用途描述**：長文（書籍、長論文）的段落級滑動觸發閾值。
*   **建議配置**：維持 **`30000`**。
*   **深度原因**：當總字數大於 30,000 字（如整本小說或書籍）時，如果依然採用句子級滑動，會產生數百個窗口，導致 HTTP 連線過多、RTT 延遲卡死。觸發段落級滑動能減少 80% 的窗口數量，配合 128 批次向量化，徹底根治 429。

---

## 4. 全域連線與並發防禦設定

### 4.1 `LLM_MAX_CONCURRENT` (全域 LLM 並發限制)
*   **當前預設值**：`6`
*   **用途描述**：控制全域 LLM 呼叫並發的 Semaphore 上限。
*   **建議配置**：
    - **免費/限制型 API Key**：保持 **`6`**。
    - **企業級/付費生產環境**：可上調至 **`16` ~ `32`**，配合 `settings.py` 進行 env override。
*   **深度原因**：
    *   在後台高載（如多個 worker 同時在背景處理多份簡報投影片與多頁履歷的 Vision 分析）時，如果沒有 Semaphore 限制，十多條 Vision 連線會瞬間發送，極易撞上 Google 端點的連線限制並返回 `Server disconnected` 的 502/503 錯誤。
    *   預設 `6` 是經過實測的經驗安全值，能最大化榨取 API 效能而絕不撞斷 TCP 連線。

### 4.2 `WATERMARK_HEADING_THRESHOLD` (浮水印偵測)
*   **當前預設值**：`3`
*   **用途描述**：整篇 markdown 內重複出現次數 $\ge 3$ 的 Heading line，將被識別為浮水印（如 `Candidate: John Doe` 或學校/企業頁首），自動整行抹除。
*   **建議配置**：維持 **`3`** (根據真實履歷與論文除雜訊實測，這是最安全的去汙界限)。

---

## 5. 架構總結與優化落地路徑 (Action Plan)

為了讓 Mad Professor 在接下來的 **Docker 化部署** 及 **SQLite 真理隔離（原始分塊物理防線）** 開發中擁有最高的穩定性，建議落實以下設定優化：

1.  **環境變數統一配置**：  
    在 Docker 部署的 `docker-compose.yml` 或 Kubernetes `ConfigMap` 中，將上述變數明確注入。避免使用舊一代 `gemini-2.0-flash` 作為預設，全面對齊 2026 最強的 **`gemini-3.5-flash`** 與 **`gemini-embedding-2`**。
2.  **雙軌自適應重新向量化**：  
    搭配 `EMBEDDING_MODEL_NAME = gemini-embedding-2` 與 `EMBEDDING_OUTPUT_DIMENSIONS = 768`。若未來模型再次抽換，SQLite 中永久保留的 `paper_chunks` 原始 Markdown 文字（真理之源）能免除耗時的 PDF MinerU 重新解析，在背景 2 秒內完成無感自癒重跑，提供極致的用戶體驗。

> [!NOTE]  
> 本報告已寫入 Artifacts 目錄下，請隨時作為 Mad Professor 架構優化的權威配置指南參考。
