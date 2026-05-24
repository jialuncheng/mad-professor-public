# 2026-05-19 套件使用徹底稽核（重點 langchain 系列）— 純檢查，無程式碼變更

稽核方法：對 active code（排除 _deprecated/.git/.claude）grep 所有 import 並逐一驗證識別字實際被使用。
⚠ 本分析環境未安裝這些套件，無法跑專案 venv 的權威 pip list / 依賴圖；以「import grep」為使用權威依據，依賴關係以套件打包慣例推論並標示需 venv 複驗處。

## A/B/C 使用點與實際使用驗證

| 套件 | 直接 import 位置 | 實際使用證據 | 結論 |
|---|---|---|---|
| **langchain (meta 1.3.1)** | **無** | active code 完全未 `import langchain` / `from langchain.` | ❌ 移除候選（見 F） |
| langchain-core | config.py:6 `from langchain_core.embeddings import Embeddings` | config.py:196 `class EmbeddingModel(Embeddings)` 繼承實作 | ✅ 必要 |
| langchain-community | rag_processor.py:6-7 FAISS+DistanceStrategy；rag_retriever.py:4 FAISS | rag_processor:100 `FAISS.from_documents`、:103 `DistanceStrategy.MAX_INNER_PRODUCT`；rag_retriever:48 `FAISS.load_local`、:14/59 型別 | ✅ 必要 |
| langchain-text-splitters | rag_processor.py:5 MarkdownHeaderTextSplitter | rag_processor:94 `MarkdownHeaderTextSplitter(headers_to_split_on=...)` | ✅ 必要 |
| faiss-cpu | 無直接 `import faiss` | langchain_community FAISS 之執行期相依（提供 `faiss`） | 🟡 間接必要 |
| google-genai | config.py:4-5、llm/message_utils.py:2 | config.py:28 `genai.Client`、:42/82 `types.*`；message_utils 用 types | ✅ 必要 |
| PyMuPDF | domain_detector.py:3、slides_processor.py:5 `import fitz` | domain_detector:34 `fitz.open`、:42 `fitz.Matrix`；slides:61 `fitz.open` | ✅ 必要 |
| numpy | tiling_processor.py:4 `import numpy as np` | tiling:221/233/234 `np.dot/linalg.norm/mean/std` | ✅ 必要 |
| requests | pdf_processor.py:2 | pdf_processor:43 `requests.post`、:92 `requests.exceptions.ConnectionError` | ✅ 必要 |
| fastapi | web_server.py:16-19 | FastAPI/Depends/UploadFile/Form/HTTPException/各 Response/StreamingResponse 全程使用 | ✅ 必要 |
| starlette | web_server.py:20 SessionMiddleware | :app.add_middleware(SessionMiddleware,...)（亦為 fastapi 相依，且直接 import） | ✅ 必要 |
| pydantic | web_server.py:21 BaseModel | ChatRequest/ChatHistory/ConfirmTypeRequest 繼承 BaseModel | ✅ 必要 |
| uvicorn | web_server.py:567（__main__ 內 import） | :568 `uvicorn.run(app,...)` | ✅ 必要 |
| bcrypt | web_server.py:12、scripts/generate_password_hash.py:12 | web_server:176 `bcrypt.checkpw`；script `bcrypt.hashpw/gensalt` | ✅ 必要 |
| python-dotenv | settings.py:1、web_server.py:22 | `load_dotenv()` 兩處呼叫 | ✅ 必要 |
| SQLAlchemy | db.py:16-18、models.py:12/23-24 | create_engine/event/sessionmaker/Session；DeclarativeBase/Mapped/mapped_column/relationship/JSON 全用 | ✅ 必要（Phase 0+ 新增） |
| itsdangerous | 無直接 import | starlette SessionMiddleware 之 cookie 簽章執行期相依 | 🟡 間接必要 |
| python-multipart | 無直接 import | fastapi 解析 `Form(...)`（/login POST）執行期必需 | 🟡 間接必要 |
| **pydantic-settings** | **無** | settings.py 全用 `os.getenv`，未用 BaseSettings；專案零處 import | ❌ 移除候選 |

附帶發現（非套件問題，僅記錄，未改）：web_server.py:19 `from fastapi.staticfiles import StaticFiles` 已 import 但無 `app.mount`/`StaticFiles(...)` 使用 → 死 import；fastapi 本就必要，不影響套件結論。

## B⑤ langchain-classic / langchain-protocol
requirements.txt 未列；active code 亦未 import。屬 langchain 1.x 生態子套件，若實際安裝係 `langchain` meta 自帶相依，與本專案程式碼無關（程式只用 -core/-community/-text-splitters 三個拆分包）。

## D 結論（每套件建議）
- ✅ 必要（直接 import 且使用）：langchain-core、langchain-community、langchain-text-splitters、google-genai、PyMuPDF、numpy、requests、fastapi、starlette、pydantic、uvicorn、bcrypt、python-dotenv、SQLAlchemy
- 🟡 間接必要（未直接 import，但必要套件之執行期相依）：faiss-cpu（langchain_community FAISS）、itsdangerous（starlette session）、python-multipart（fastapi Form）
- ❌ 移除候選：
  - **pydantic-settings**：零使用、零依賴關係（settings.py 純 os.getenv）。可安全自 requirements 移除（本次不改）。
  - **langchain（meta 1.3.1）**：active code 完全未直接 import。依 langchain 1.x 打包慣例，langchain-community 相依的是 langchain-core，不需 `langchain` meta 包。**很可能可移除**，但須於正式 venv 以 `pipdeptree` / `pip show langchain-community langchain-text-splitters` 確認無一相依 `langchain` meta 後再動（本次僅報告、不改）。

## E 安裝 vs requirements 差異
- 本分析環境未安裝任何上述套件（與先前 sqlalchemy/dotenv 缺失一致），**無法在此跑專案 venv 的權威 pip list**。
- 「實際裝了但 requirements 沒列」類：itsdangerous/python-multipart 屬此性質（執行期相依，requirements 已明列，正確）；langchain-classic/-protocol 可能因 langchain meta 帶入但與程式無關。
- 「requirements 列了但程式沒用」：pydantic-settings（確定未用）、langchain meta（未直接 import）。
- 須於正式 venv 執行 `pip list` 與 `pipdeptree` 才能給出權威差異表；本報告以 import grep 為使用權威。

## E② langchain 1.x vs 0.x
程式僅用跨版本穩定 API：`FAISS.from_documents` / `FAISS.load_local` / `similarity_search_with_score`、
`MarkdownHeaderTextSplitter`、`Embeddings` 基底、`DistanceStrategy.MAX_INNER_PRODUCT`。
未偵測任何 1.x 專屬功能 → 版本 1.3.1 屬「被動跟版」，非功能驅動。無程式碼依賴 1.x 新特性。

## F 風險評估（若移除）
- pydantic-settings：**零風險**（無 import、無依賴關係）。移除僅清 requirements 一行。
- langchain（meta）：低風險，前提是 -core/-community/-text-splitters 不相依它（依打包慣例應不相依）。即使移除，若有任何套件實際相依，pip 仍會自動帶入；顯式列出僅屬冗餘。**務必 venv 內 pipdeptree 複驗再移除**。
- langchain-core/-community/-text-splitters：**不可移除**。移除 → rag_processor（建向量庫）、rag_retriever（檢索）、config.EmbeddingModel（Embeddings 基底）全部 ImportError，RAG 與問答整條斷。
- 「langchain-community FAISS → 換 faiss 原生 API」：技術可行（faiss index + 自管 docstore/metadata + 自寫 save/load 與 similarity_search_with_score 等價邏輯），但屬非平凡重寫且影響既有向量庫格式相容；**不建議**，保留 langchain-community。
- faiss-cpu / itsdangerous / python-multipart：移除即破壞（FAISS 後端 / session 簽章 / 表單登入），保留。

## 建議（不在本次執行）
1. requirements.txt 可移除 `pydantic-settings`（確定無用）。
2. `langchain`（meta）建議於正式 venv 跑 `pipdeptree -p langchain-community,langchain-core,langchain-text-splitters` 確認無反向相依後移除；無法確認前維持現狀（冗餘但無害）。
3. 其餘套件全部保留（✅/🟡）。
4. 附帶：web_server.py 未使用的 `StaticFiles` import 可於日後清理（非套件、非本次範圍）。

## 驗證
- 純稽核，無任何程式碼/設定變更（git 無 .py/requirements 變動）。
- 結論基於 active code import grep（權威）+ 識別字使用驗證（已逐一列證據）。
- 限制：本環境無法跑專案 venv 的 pip/pipdeptree；依賴關係結論已明確標示「需 venv 複驗」處（langchain meta、pip 差異表）。
