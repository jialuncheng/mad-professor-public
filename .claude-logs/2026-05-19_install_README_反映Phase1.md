# 2026-05-19 更新 install.sh 與 README.md 反映 Phase 1（純文件，無業務邏輯變更）

變更檔：install.sh、README.md（git status 僅此兩檔）。

## install.sh 改動摘要
- 新增「── 5. 建立 data/ 目錄並初始化 DB schema ──」（在安裝套件後、提示前）：
  - `mkdir -p data`（idempotent）
  - `python -c "from db import init_db; init_db()"`，失敗則 WARN 提示手動執行（不中止，set -e 下用 if 包住）
  - 不自動跑 migration（避免 .env 未設好就執行）—— 改列在後續手動步驟
- 原「5 & 6 提示」改編號為「6 & 7」
- 後續手動步驟由 4 步 → 5 步：新增「4. 建立 admin user：python scripts/migrate_to_db.py（可先 --dry-run）」，
  啟動服務改為第 5 步；必填項補上 AUTH_USERNAME
- 維持 [INFO]/[WARN]/[ERROR] 前綴與 idempotent；bash -n 通過

## README.md 改動摘要（維持原章節編號與風格）
- 三、快速開始：.env 必填補 `AUTH_USERNAME`；新增「### 3. 初始化資料庫」子節
  （init_db + migrate_to_db.py，含 --dry-run 提示）；原「3. 啟動」→「4. 啟動」
- 四、設定詳細說明：變數表新增 `DATABASE_URL` 列（SQLite 預設、可換 PG）。
  （LLM_DOC/VISION/EXTRA_INFO_MODEL 與模型選擇建議於前階段已存在，內容已符合 Pro/Flash 設計，無需重寫）
- 七、Pipeline 階段：`detect_domain` 已在列表（前階段已加），確認正確，未改
- 八、開發者：專案結構更新——paper_manager 描述改為「論文/對話 DB 存取層（DB-backed）」、
  新增 db.py / models.py / scripts/migrate_to_db.py / data/；新增「資料持久化」小節
  （DB vs 檔案系統分工；明示廢除 papers_index.json / chat_history.json）
- 九、部署：新增「備份策略」（sqlite3 .backup + tar output/）
- 十一、本次重構主要改動：新增 DB 化 / 文件閱讀提前 / Web Search / LLM model 細分 /
  字元清理（NFKC + 移除 emotion）/ 套件精簡（移除 langchain meta）；主題領域偵測原已有，未重複
- 致謝：新增 SQLAlchemy

## 與既有功能矛盾的內容是否清除
- §8 paper_manager 舊描述「論文索引管理」（暗示 papers_index）已改為 DB 存取層；
  「資料持久化」小節明確聲明 papers_index.json / chat_history.json 已廢除 → 矛盾清除。
- §3 章節重編號一致（3 初始化 DB / 4 啟動）。
- 未寫入任何尚未實作功能（多帳號登入、folder UI 皆未提及）。

## D 驗證
- `bash -n install.sh` 通過
- README 指令實際可執行（venv 內）：`from db import init_db; init_db()` → OK；
  `scripts/migrate_to_db.py --dry-run` → exit 0
- .env.example 與 README 變數一致：DATABASE_URL / LLM_DOC_MODEL / LLM_VISION_MODEL /
  LLM_EXTRA_INFO_MODEL / AUTH_USERNAME 皆存在於 .env.example ✓
- git：僅 README.md、install.sh 變更，無 .py / 業務邏輯改動

## 備註
- install.sh 於 venv 啟用後才呼叫 init_db，`from db import init_db` 在 SCRIPT_DIR 下可解析；
  db.py 僅需 settings（load_dotenv 有預設值），不需 GEMINI 金鑰即可建表，故安裝期執行安全。
- migration 仍由使用者手動跑（需先設 .env 的 AUTH_*），install.sh 不自動執行，符合需求。
