# Mad Professor

學術論文、新聞、書籍、簡報的 AI 閱讀助手。上傳 PDF 後自動解析、翻譯成繁體中文，並提供基於 RAG 的問答功能。

本專案 Fork 自 [LYiHub/mad-professor-public](https://github.com/LYiHub/mad-professor-public)，在原作者基礎上大規模重構，從桌面應用改為 Web 架構。

## 功能

- **多文件類型支援**：學術論文、新聞、書籍、技術文件、簡報、網頁存檔
- **自動翻譯**：全文翻譯成繁體中文，支援中英切換
- **圖表理解**：Vision 自動生成圖片說明，整合進 RAG
- **簡報解析**：每頁投影片獨立渲染，Vision 辨識內容
- **RAG 問答**：基於 Gemini Embedding 2 的多模態向量檢索
- **AI 導師**：蘇格拉底式啟發、第一性原理、事後驗屍三種引導模式
- **對話紀錄**：問答歷史自動儲存，重啟不遺失

## 技術架構

- **後端**：FastAPI，REST API + SSE 串流
- **前端**：純 HTML/JS，無框架依賴
- **LLM**：Gemini（翻譯、問答、Vision）
- **Embedding**：Gemini Embedding 2（文字 + 圖片多模態）
- **PDF 解析**：MinerU API（本地部署）
- **簡報解析**：PyMuPDF + Gemini Vision
- **向量庫**：FAISS

## 系統架構

```text
web_server.py          ← HTTP 路由、SSE、背景任務
pipeline_core.py       ← 處理階段編排、進度回報
paper_manager.py       ← 論文索引管理、資源載入

processor/
  pdf_processor.py         ← PDF → Markdown（MinerU API）
  slides_processor.py      ← 簡報 PDF → PyMuPDF 渲染 + Vision 解析
  md_cleaner.py            ← 清除控制字元、過濾雜訊行
  doc_analyzer.py          ← 標題修正、文件結構分析
  md_processor.py          ← Markdown → JSON
  json_processor.py        ← JSON 清理
  tiling_processor.py      ← 切片
  translate_processor.py   ← 翻譯（含 doc_type 風格提示）
  md_restore_processor.py  ← 還原 Markdown（整合 Vision caption）
  extra_info_processor.py  ← 章節摘要
  rag_processor.py         ← RAG 向量庫建立
  image_caption_processor.py ← 圖片 Vision 說明生成

AI_professor_chat.py   ← 問答流程、RAG 檢索、決策路由
ai_core.py             ← AI 介面
rag_retriever.py       ← 向量庫檢索
config.py              ← LLMClient、EmbeddingModel

prompt/
  ai/                  ← 問答 prompt
  translate/           ← 翻譯 prompt
  doc/                 ← 文件分析 prompt
```

## 安裝

### 環境需求

- Python 3.12+
- MinerU API 服務（本地部署，參考 [MinerU](https://github.com/opendatalab/MinerU)）
- Gemini API Key

### 安裝步驟

```bash
git clone https://github.com/jialuncheng/mad-professor-public.git
cd mad-professor-public
git checkout gemini-refactor

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 設定

複製 `.env.example` 並填入設定：

```bash
cp .env.example .env
```

`.env` 內容：

```
GEMINI_API_KEY=your_api_key
LLM_TRANSLATE_MODEL=gemini-3.1-flash-lite
LLM_CHAT_MODEL=gemini-3.1-flash-lite
EMBEDDING_MODEL=gemini-embedding-2
MINERU_API_URL=http://your_mineru_host:8000/file_parse
MINERU_HOST=user@your_mineru_host
MINERU_OUTPUT_DIR=/path/to/mineru/output
```

## 啟動

```bash
source venv/bin/activate
python web_server.py
```

Web 介面：http://localhost:8080

## 使用流程

1. 點擊左側「＋ 上傳文件」，選擇 PDF
2. 上傳完成後選擇文件類型（學術論文／書籍／技術文件／簡報／新聞／網頁存檔）
3. 點擊「確認，開始處理」
4. 等待處理完成後，點擊左側文件進入閱讀
5. 右上角切換中英文；右側輸入框進行 AI 問答

## 已知限制

- MinerU 對複雜子圖排版（如 Fig. 1a/1b/1c）的切割可能不準確
- 圖片被 MinerU 歸到錯誤 section 屬 MinerU 解析限制，無法從程式端完全解決

## 授權

Apache License — 詳見 LICENSE 文件

## 致謝

感謝原專案作者 [LYiHub](https://github.com/LYiHub) 的創意與基礎實作。

感謝以下開源專案：
- [MinerU](https://github.com/opendatalab/MinerU) — PDF 解析引擎
- [LangChain](https://github.com/langchain-ai/langchain) — RAG 向量檢索框架
- [FAISS](https://github.com/facebookresearch/faiss) — 向量相似度搜尋
- [FastAPI](https://github.com/tiangolo/fastapi) — Web 框架