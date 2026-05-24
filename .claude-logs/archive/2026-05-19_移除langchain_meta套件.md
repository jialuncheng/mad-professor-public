# 2026-05-19 從 requirements.txt 移除 langchain meta 套件（僅設定變更，無程式碼變更）

依據 .claude-logs/2026-05-19_venv建立與runtime套件稽核.md 的 runtime 確證執行。

## 變更
- requirements.txt：刪除 `langchain==1.3.1` 一行；RAG 區段加註解說明為何不需 meta，
  並補強 langchain-core/-community/-text-splitters/faiss-cpu 的用途註解。
- 保留：langchain-core==1.4.0、langchain-community==0.4.1、langchain-text-splitters==1.1.2、faiss-cpu==1.13.2。
- git diff：requirements.txt 1 檔，+7/-4。無任何 .py / 業務邏輯變更。

## 移除前後 pip list（langchain 生態）
移除前：
  langchain 1.3.1 / langchain-classic 1.0.7 / langchain-community 0.4.1 / langchain-core 1.4.0 /
  langchain-protocol 0.0.15 / langchain-text-splitters 1.1.2 / langgraph 1.2.0 /
  langgraph-checkpoint 4.1.0 / langgraph-prebuilt 1.1.0 / langgraph-sdk 0.3.14 / langsmith 0.8.5
移除後：
  langchain-classic 1.0.7 / langchain-community 0.4.1 / langchain-core 1.4.0 /
  langchain-protocol 0.0.15 / langchain-text-splitters 1.1.2 / langsmith 0.8.5

## 卸載清單（langchain meta 帶走的 langgraph 全家）
Successfully uninstalled：langchain-1.3.1、langgraph-1.2.0、langgraph-checkpoint-4.1.0、
langgraph-prebuilt-1.1.0、langgraph-sdk-0.3.14（共 5 個；皆程式未用，langgraph 根反向依賴僅 langchain meta）。
保留 langchain-classic / langchain-protocol / langsmith（langchain-community/-core 必要 transitive）。

## requirements 完整性驗證
卸載後重跑 `pip install -r requirements.txt` → 正常完成，**未重新抓回 langchain / langgraph**
（requirements 已無 meta，且無其他套件依賴 langgraph）。確認新 requirements 完整可解析。

## 節省磁碟空間
venv 350M → 345M（約省 5MB；langgraph 全家為純 Python 套件，體積有限；
主要效益是依賴面收斂、安裝更快、移除未用程式碼路徑）。

## 驗證結果
- submodule import：`import langchain_core, langchain_community, langchain_text_splitters` → All OK
- langchain meta import：`import langchain` → ModuleNotFoundError（如預期，已移除）
- ④ py_compile：*.py processor/*.py utils/*.py llm/*.py → 全通過
- ⑤ db.init_db()（臨時 DB）→ DB OK
- ⑥ pipdeptree 頂層：langchain-community 為頂層，**無 langchain meta**，無漏依賴/衝突警告
- RAG 關鍵類別所屬套件（langchain-core Embeddings、langchain-community FAISS/DistanceStrategy、
  langchain-text-splitters MarkdownHeaderTextSplitter）全部仍可用，未受影響。

## 結論
langchain meta 已乾淨移除，RAG 功能依賴（-core/-community/-text-splitters/faiss-cpu）完整保留並 runtime 驗證可用。
pydantic-settings 仍由 langchain-community 依賴鏈帶入（未列於 requirements 亦會被安裝），無需手動加回。
本次純 requirements.txt 設定收斂，零業務邏輯變更。

## 限制
- 未跑完整 web_server 啟動（需 .env/GEMINI 金鑰/MinerU），非本任務範圍；
  但所有模組 import、py_compile、DB 層均已在 venv runtime 驗證。
