# Mad Professor（Web 版）

一個以 Web 為基礎的學術文件閱讀與問答系統。上傳 PDF 後自動處理、翻譯，並透過 AI 導師引導深度思考。

本專案 Fork 自 [LYiHub/mad-professor-public](https://github.com/LYiHub/mad-professor-public)，在原作者的基礎上進行大規模重構，從桌面應用改為 Web 架構。

## 主要特性

- **多種文件類型**：學術論文、書籍、技術文件、簡報、新聞、網頁存檔
- **自動文件類型偵測**：上傳後由 LLM 判斷文件類型，使用者確認後開始處理
- **雙語閱讀**：中英文切換顯示
- **AI 學術導師**：結合論文內容回答問題，以蘇格拉底式啟發、第一性原理、事後驗屍三種模式引導思考
- **RAG 精準檢索**：基於向量庫的論文段落檢索
- **對話紀錄**：問答歷史自動儲存，重啟不遺失

## 技術架構

- **後端**：FastAPI，提供 REST API 和 SSE 串流
- **前端**：純 HTML/JS，無框架依賴
- **AI 問答**：LLM（Gemini）+ RAG 向量檢索 + Vision
- **PDF 解析**：MinerU API（本地部署）
- **Embedding**：BAAI/bge-m3（本地）

## 系統架構

    web_server.py          <- HTTP 路由、SSE、背景任務
    pipeline_core.py       <- 處理階段編排、進度回報
    paper_manager.py       <- 論文索引管理、資源載入

    processor/
      pdf_processor.py     <- PDF -> Markdown（MinerU API）
      md_cleaner.py        <- 清除控制字元
      doc_analyzer.py      <- 文件類型偵測、標題修正、結構分析
      md_processor.py      <- Markdown -> JSON
      json_processor.py    <- JSON 清理
      tiling_processor.py  <- 切片
      translate_processor.py   <- 翻譯
      md_restore_processor.py  <- 還原 Markdown
      extra_info_processor.py  <- 章節摘要
      rag_processor.py     <- RAG 向量庫建立

    AI_professor_chat.py   <- 問答流程、RAG 檢索、決策路由
    ai_core.py             <- AI 介面（供 web_server 呼叫）
    rag_retriever.py       <- 向量庫檢索
    config.py              <- LLMClient、EmbeddingModel
    paper_manager.py       <- 論文資料管理

    prompt/
      ai/                  <- AI 問答相關 prompt
      translate/           <- 翻譯相關 prompt
      doc/                 <- 文件分析相關 prompt

## 安裝指南

### 環境需求

- Python 3.10 以上
- MinerU API 服務（本地部署，參考 [MinerU](https://github.com/opendatalab/MinerU)）
- Gemini API Key

### 安裝步驟

1. 建立虛擬環境

        python -m venv venv
        source venv/bin/activate

2. 安裝依賴

        bash install.sh

    `install.sh` 會按照正確順序安裝所有套件，並在結尾自動驗證。

3. 設定環境變數，建立 `.env` 檔案：

        GEMINI_API_KEY=your_api_key
        LLM_TRANSLATE_MODEL=gemini-2.0-flash
        LLM_CHAT_MODEL=gemini-2.0-flash

4. 確認 MinerU API 服務已啟動，並在 `processor/pdf_processor.py` 設定正確的 API 位址：

        MINERU_API_URL = "http://your_mineru_host:8000/file_parse"

## 使用說明

### 啟動應用

    python web_server.py

開啟瀏覽器：http://localhost:8080

### 上傳文件

1. 點擊左側「＋ 上傳論文」按鈕，選擇 PDF
2. 系統完成解析後，顯示偵測到的文件類型
3. 確認或修改文件類型後，點擊「確認，開始處理」
4. 等待處理完成，論文會出現在左側列表

### 閱讀論文

1. 在左側列表選擇論文
2. 右上角切換中英文
3. 滑鼠移到論文標題上，點擊 ✕ 可刪除論文

### AI 問答

在右側輸入框輸入問題，按 Enter 或點擊「送出」。AI 導師會結合論文內容回答，並在結尾引導下一個問題。

## 已知問題

1. MinerU 對簡報的圖片解析效果較差，部分圖片可能遺漏或截斷
2. 文件名稱含有特殊字元會自動清理為底線
3. 複雜的子圖排版標籤對應可能不準確

## 授權

本專案採用 Apache License - 詳見 LICENSE 文件

## 致謝

特別感謝原專案作者 [LYiHub](https://github.com/LYiHub) 的創意與基礎實作，本專案在其基礎上進行重構。

感謝以下開源專案：

- [MinerU](https://github.com/opendatalab/MinerU) — PDF 解析引擎
- [LangChain](https://github.com/langchain-ai/langchain) — RAG 向量檢索框架
- [FAISS](https://github.com/facebookresearch/faiss) — 向量相似度搜尋
- [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) — 多語言 Embedding 模型
- [FastAPI](https://github.com/tiangolo/fastapi) — Web 框架
