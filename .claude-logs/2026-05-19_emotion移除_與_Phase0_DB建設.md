# 2026-05-19 任務A emotion 移除 + 任務B Phase 0 SQLite/SQLAlchemy 建設

NEVER 修改任何業務邏輯。Phase 0 = 只建設、不接線。

## 任務 A：移除 emotion（Live2D 語音殘留）
grep 全專案（.py/.js/.html/.json/.txt，排除 .git/.claude-logs/_deprecated）：
emotion 僅出現在 ai_core.py 4 處；前端 index.html / AI_professor_chat.py / prompt/ai/* / 任何 json 皆無；
_deprecated/* 有但屬封存死碼、不在範圍。

移除清單（ai_core.py，僅刪 emotion 鍵，保留 grounding_sources/其他）：
- docstring: `{'sentence': str, 'emotion': str, 'done': bool}` → `{'sentence': str, 'done': bool}`
- busy-return chunk：移除 `'emotion': 'neutral'`
- done chunk：移除 `'emotion': 'neutral'`（保留 grounding_sources）
- except done chunk：移除 `'emotion': 'neutral'`（保留 grounding_sources=[]）

驗證：殘留 grep（active code）為空；py_compile ai_core.py OK；node --check index.html JS OK
（前端從不讀 chunk.emotion，SSE 結構移除後相容）。

## 任務 B：Phase 0 DB 建設（不接線）

新增檔案：
- db.py：SQLAlchemy 2.0 同步 engine（check_same_thread=False, pool_pre_ping）；
  @event connect 設 PRAGMA foreign_keys=ON / journal_mode=WAL / busy_timeout=5000（僅 sqlite，非 sqlite 跳過）；
  SessionLocal(expire_on_commit=False)；get_db() generator；init_db() = _ensure_sqlite_dir()+Base.metadata.create_all；
  models 延遲 import 避免循環；__main__ 可直接 init_db。
- models.py：DeclarativeBase；User/Folder/Paper/Conversation。
  conversations 保留 grounding_sources(JSON)、**無 emotion 欄**。
  關聯/cascade：Paper.conversations cascade all,delete-orphan + passive_deletes；
  Folder.children cascade + passive_deletes；FK ondelete：
  papers.owner_id→users RESTRICT；papers.folder_id→folders SET NULL；
  folders.parent_id→folders CASCADE；conversations.paper_id→papers CASCADE；conversations.user_id→users RESTRICT。
  約束/索引見下方 DDL 預覽。
- scripts/migrate_to_db.py：--dry-run / --rollback / 預設遷移；idempotent（get-or-create by 唯一鍵、已存在略過）；
  admin 取自 AUTH_USERNAME/AUTH_PASSWORD_HASH(role=admin)；papers_index→papers(status=done)；
  chat_history.json→conversations(grounding_sources=NULL)；output/{id}→output/{admin_id}/{id}；
  rollback：目錄搬回 + 刪 .db(-wal/-shm)。Phase 0 不自動執行。

修改檔案：
- settings.py：+`from pathlib import Path`；+DATABASE_URL（預設 sqlite:///<root>/data/mad-professor.db）。
- .env.example：加註解化的 DATABASE_URL（Phase 0 未接線說明）。
- requirements.txt：加「# 資料庫」群組 `SQLAlchemy==2.0.43`（核心精確鎖定；安裝後依實際版本確認）；alembic 暫不加。
- .gitignore：加 `data/*.db` `data/*.db-wal` `data/*.db-shm` `*.db` `*.db-wal` `*.db-shm`
  （**注意**：原規格 ⑥ 寫 `data/`，但 `data/` 會使 `!data/.gitkeep` 因 Git「父目錄被排除無法重納」限制失效；
  改為只忽略 data/ 內 db 檔、保留目錄，同時滿足 ⑥ 意圖與 ⑦ 之 .gitkeep 可追蹤。已驗證 git check-ignore。）
- 新增 data/.gitkeep（目錄存在、db 不入庫）。

### 4 表 DDL 預覽（SQLite 方言；create_all 產生）
users(id PK, username UNIQUE NOT NULL, password_hash NOT NULL, display_name, role NOT NULL def 'user',
  email, is_active NOT NULL def 1, created_at NOT NULL def now)
folders(id PK, owner_id→users RESTRICT NOT NULL, parent_id→folders CASCADE NULL, name NOT NULL,
  sort_order NOT NULL def 0, created_at NOT NULL def now;
  UNIQUE(owner_id,parent_id,name); INDEX(owner_id,parent_id))
papers(id PK, owner_id→users RESTRICT NOT NULL, paper_uuid NOT NULL, title, translated_title, domain,
  doc_type, folder_id→folders SET NULL NULL, status NOT NULL def 'processing', progress_index,
  progress_stage, error_message, file_size, page_count, created_at, updated_at(onupdate now),
  ready_for_reading_at, ready_for_chat_at, last_opened_at;
  UNIQUE(owner_id,paper_uuid); INDEX(owner_id,status)/(owner_id,folder_id)/(paper_uuid)/(owner_id,last_opened_at))
conversations(id PK, paper_id→papers CASCADE NOT NULL, user_id→users RESTRICT NOT NULL, session_id,
  role NOT NULL, content NOT NULL, grounding_sources JSON NULL, tokens_used, created_at NOT NULL def now;
  INDEX(paper_id,id))  ← 無 emotion 欄

### migration script 使用方式
- 預演：`python scripts/migrate_to_db.py --dry-run`（只報告 users/papers/conversations 數與搬移計畫）
- 正式：`python scripts/migrate_to_db.py`（idempotent，可重跑）
- 還原：`python scripts/migrate_to_db.py --rollback`（目錄搬回 + 刪 .db）

## 驗證結果
- py_compile：ai_core.py / settings.py / db.py / models.py / scripts/migrate_to_db.py 全通過。
- node --check：index.html inline JS 通過。
- 非接線確認：grep `import db|from db import|import models|from models import` 於
  web_server/paper_manager/pipeline_core/ai_core → 皆無（Phase 0 未接線）。
- git：data/.gitkeep 可追蹤、data/*.db 被忽略（git check-ignore 已驗）。
- ⚠ runtime 驗證（init_db 建表 / import models / web_server 啟動 / migrate --dry-run）
  **此環境缺 sqlalchemy 與 dotenv，無法執行**，僅靜態 py_compile 保證語法。
  使用者須於正式 venv 跑：
    pip install -r requirements.txt
    python -c "import db; db.init_db(); print('tables created')"
    python -c "import models"
    python scripts/migrate_to_db.py --dry-run
    python web_server.py   # 應與現在完全相同（未接 DB）

## Phase 0 結束時系統行為
與現在 100% 相同：核心模組未 import db/models，執行期續走 papers_index.json + chat_history.json；
即使無 .db 或刪除 .db 亦不影響運作。DB 僅「就緒未使用」，翻開關（migrate + 接線）為 Phase 1。

## 疑慮 / 待確認
1. SQLAlchemy 精確版本 2.0.43 為建議值，安裝後請依實際版本微調（符合 requirements 精確鎖定政策）。
2. .gitignore 對規格 ⑥「data/」做了必要偏離（見上），以同時滿足 .gitkeep 可追蹤。
3. runtime 驗證未能在此環境執行（缺 sqlalchemy/dotenv），已列使用者驗證指令；py_compile 僅保證語法非執行期。
4. migrate 對舊資料 created_at 用目錄 mtime 近似；doc_type/domain 設 NULL（papers_index 無此資訊）。
5. conversations.grounding_sources 對舊 chat_history 一律 NULL；未來新對話要寫入需 Phase 1 同步前端 saveChatHistory 格式（與前次設計分析一致）。
