# 2026-05-19 Claude Code 環境 venv 建立 + runtime 套件稽核（純環境設定，無程式碼變更）

## ★ 給未來分析任務的事實（重要）
本 worktree 已建立可用 venv，未來任務可直接 **runtime 驗證**，不必只靠 grep：
- 路徑：`/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/venv`
- 用法：`./venv/bin/python <script>`、`./venv/bin/pip ...`、`./venv/bin/pipdeptree ...`
- 已裝：requirements.txt 全部 + pipdeptree
- 大小 ~350M；`venv/` 已被 .gitignore（不會提交）
- Python 3.12.3（aarch64）
- 注意：settings.py 會 load_dotenv()，但無 .env 時 os.getenv 取預設值；
  db.py/models.py 不依賴 GEMINI_API_KEY，可直接 runtime 測 DB。
  測 DB 建議帶 `DATABASE_URL='sqlite:////tmp/xxx.db'` 避免動到專案 ./data。

## ① 安裝結果（requirements 套件 installed 版本，與 pin 規格一致）
fastapi 0.136.1 / starlette 1.0.0 / pydantic 2.13.4 / pydantic-settings 2.14.1 /
google-genai 2.3.0 / langchain 1.3.1 / langchain-core 1.4.0 / langchain-community 0.4.1 /
langchain-text-splitters 1.1.2 / faiss-cpu 1.13.2 / PyMuPDF 1.27.2.3 / SQLAlchemy 2.0.43
（核心 == 全部精確命中）
uvicorn 0.47.0 / python-multipart 0.0.29 / numpy 2.4.6 / python-dotenv 1.2.2 /
requests 2.34.2 / bcrypt 5.0.0 / itsdangerous 2.2.0（輔助 >= 皆滿足）

requirements 未列但被 langchain 生態帶入的 transitive：
langchain-classic 1.0.7 / langchain-protocol 0.0.15 / langgraph 1.2.0 /
langgraph-checkpoint 4.1.0 / langgraph-prebuilt 1.1.0 / langgraph-sdk 0.3.14 / langsmith 0.8.5

## ② import 驗證（⑤⑥）— 全成功
sqlalchemy 2.0.43 / dotenv OK / google.genai OK / langchain_core 1.4.0 /
langchain_community 0.4.1 / langchain_text_splitters 1.1.2（模組無 __version__ 屬性，
僅 cosmetic；importlib.metadata 版本 1.1.2）/ faiss OK / PyMuPDF 1.27.2.3 /
fastapi 0.136.1 / bcrypt 5.0.0 / langchain 1.3.1（meta 可被 import，但程式從不 import 它）
無任何 ImportError。

## ⑦⑩ pipdeptree runtime 依賴稽核（取代先前 grep 推論）

### langchain（meta）→ 確定可移除（runtime 證實）
- `pipdeptree -r -p langchain` → 僅 `langchain==1.3.1`，**無任何反向依賴者**。
- 程式碼 active code 從不 `import langchain`（只用 -core/-community/-text-splitters 拆分包）。
- 正向依賴：langchain-core、langgraph、pydantic。
- langchain-community 依賴樹中**不含 langchain meta**（只含 langchain-classic、langchain-core 等）。
- 結論：**langchain meta 真正可移除**；移除後 langgraph（其唯一反向依賴是 langchain meta）
  及 langgraph-checkpoint/-prebuilt/-sdk 會一併變孤兒（程式皆未用）。

### pydantic-settings → 修正：必須保留（先前 grep-only 誤判）
- 先前 grep-only 稽核結論「❌ 移除候選（settings.py 未用）」**錯誤**。
- `pipdeptree -r -p pydantic-settings` → `langchain-community==0.4.1 requires pydantic-settings>=2.10.1`。
- 即 pydantic-settings 是 **langchain-community 的必要 transitive 依賴**（langchain-community 有被使用）。
- 結論：🟡 間接必要，**不可從 requirements 移除**（移除會破壞 langchain-community 安裝解析）。
- ★ 這正是「runtime 勝過 grep」的關鍵案例：grep 只看 import，看不到打包依賴。

### 其他 transitive（runtime 確認，皆必要、正確未列於 requirements）
- langchain-classic ← langchain-community 要求 >=1.0.0
- langchain-protocol ← langchain-core 要求 >=0.0.14
- langsmith ← langchain-core 要求 >=0.3.45
- langgraph ← 僅 langchain meta 要求（若移除 langchain meta 則 langgraph 變孤兒）

## ⑧ DB schema 建立測試（in-memory/臨時檔，未動專案資料）
`DATABASE_URL=sqlite:////tmp/_phase0_test.db ./venv/bin/python -c "import db,models; db.init_db(); ..."`
→ tables: ['conversations','folders','papers','users']；User 查詢 OK（count=0）；測後刪臨時檔。
db.py / models.py 在真實 SQLAlchemy 下完整載入、建表成功（Phase 0 設計 runtime 驗證通過）。

## ⑨ py_compile 全專案（venv 內）
所有 active .py（排除 _deprecated/.git/.claude/venv）→ 全數編譯通過。

## 跟 requirements.txt 的差異（runtime 權威）
- 列了且必要：19 個全部正確安裝、版本符合 pin。
- 「列了但程式未直接 import」：langchain（meta，可移除）、pydantic-settings（**修正：必要 transitive，保留**）、itsdangerous（starlette 用）、python-multipart（fastapi Form 用）、faiss-cpu（langchain_community FAISS 用）。
- 「未列但安裝」：langchain 生態 transitive（classic/protocol/langgraph*/langsmith）—— 正常，pip 依賴解析帶入，不需手列。

## 最終建議：langchain 是否可移除
**可移除（runtime 確證）**：無反向依賴、程式不 import。若要精簡，
從 requirements.txt 移除 `langchain==1.3.1` 一行即可，並會連帶不再安裝
langgraph / langgraph-checkpoint/-prebuilt/-sdk（程式皆未使用，可省 ~數十 MB）。
保留 langchain-core / langchain-community / langchain-text-splitters（RAG 核心，必要）。
**pydantic-settings 必須保留**（langchain-community 依賴）—— 撤回先前可移除的結論。
本任務僅環境設定與稽核，**未修改 requirements.txt / 任何程式碼**；上述為建議，待後續任務執行。

## 驗證/限制
- 全部結論基於本次 venv 內 runtime（pip list / pipdeptree / 實際 import / init_db / py_compile）。
- 未跑完整 web_server 啟動（需 .env / GEMINI 金鑰 / MinerU 服務），非本任務範圍；
  但 DB 層、所有模組 import、編譯均已 runtime 驗證。
- 無任何程式碼或設定檔變更（git 僅新增未追蹤的 venv/，已被 gitignore）。
