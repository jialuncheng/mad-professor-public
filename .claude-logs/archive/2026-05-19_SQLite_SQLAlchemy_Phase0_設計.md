# 2026-05-19 Phase 0：SQLite + SQLAlchemy 化設計（純設計，未改任何程式碼）

## 背景
承接 .claude-logs/2026-05-19_多使用者隔離與資料夾結構_設計分析.md，決定走 DB 化。
圖片/PDF/MD/vector_store 續留 output/ 檔案系統；DB 只存 metadata/users/papers/conversations/folders。

## A. 套件與架構
- SQLAlchemy 2.0.x（2.0 declarative；安裝後精確鎖定，requirements「核心」群組）。
- Alembic：Phase 0 不需要（首版用 create_all）；建議建立 0001_initial 基線+stamp，Phase 1 才實際 upgrade。alembic 列「輔助」。
- async：建議「同步 SQLAlchemy」。端點 Depends 取同步 Session（FastAPI 丟 threadpool），pipeline 執行緒自建 session。不引入 aiosqlite。
- sqlite3 vs SQLAlchemy → SQLAlchemy（PG 平移零痛、Alembic、relationship/cascade）。
- ORM vs Core → ORM declarative；migration script 可用 Core/bulk insert 加速。

## B. Schema（4 表，SQLite/PG 相容；PK INTEGER autoincrement；paper_uuid 為對外字串）
- users: id PK / username UNIQUE NOT NULL / password_hash / display_name(建議) / role default 'user'(建議) / email(可選) / is_active default 1 / created_at
- papers: id PK / owner_id FK users / paper_uuid / title / translated_title / domain / doc_type / folder_id FK folders NULL / status(processing|readable|done|error) / progress_index / progress_stage / error_message(建議) / file_size(建議) / page_count(可選) / created_at / updated_at / ready_for_reading_at / ready_for_chat_at / last_opened_at(建議)。路徑不入庫，由 (owner_id,paper_uuid) 推導。
- folders: id PK / owner_id FK users / parent_id FK folders NULL(巢狀) / name / sort_order default 0(建議) / created_at。不存 path（由 parent_id 推導，避免雙來源不一致）。
- conversations: id PK / paper_id FK papers / user_id FK users / session_id(建議,預留NULL) / role / content / grounding_sources JSON(建議,需Phase1前端配合) / emotion(可選) / tokens_used(可選) / created_at。
- 疑慮：現 chat_history.json 僅 {role,content}；grounding_sources/emotion 目前未持久化，schema 預留但真正寫入需 Phase 1 同步改前端 saveChatHistory 與端點（跨層相依，已標記）。

## C. 索引/約束/FK
- UNIQUE: users.username; papers(owner_id,paper_uuid); folders(owner_id,parent_id,name)（頂層重名 NULL parent 需應用層再擋）。
- INDEX: papers(owner_id,status); papers(owner_id,folder_id); papers(paper_uuid); papers(owner_id,last_opened_at); conversations(paper_id,id); folders(owner_id,parent_id)。
- ON DELETE: papers.owner_id→users RESTRICT（user 刪除走服務層流程/軟刪 is_active）；papers.folder_id→folders SET NULL（刪資料夾論文回根）；folders.parent_id→folders CASCADE（刪子資料夾，論文因 SET NULL 回根不丟）；conversations.paper_id→papers CASCADE；conversations.user_id→users RESTRICT。
- SQLite 坑：FK 預設不強制，需每連線 PRAGMA foreign_keys=ON（event.listens_for connect）。

## D. 檔案系統對應
- paper_dir(owner_id,paper_uuid)=OUTPUT_DIR/str(owner_id)/paper_uuid（用不可變 owner_id，非 username）。檔名規則不變。
- 不存絕對 path 在 DB（避免漂移）。刪 paper：先 DB 刪 row(cascade conv) commit→rmtree；失敗記 orphan，擴充 /api/cleanup 掃孤兒。
- 重命名 paper：只改 title；paper_uuid/目錄永不變。

## E. Migration
- scripts/migrate_to_db.py：init_db→建 admin(從 AUTH_USERNAME/HASH)→讀 papers_index.json 寫 papers(owner=admin,paper_uuid=舊id,status=done)→讀各 chat_history.json 寫 conversations→搬 output/{id}/→output/{admin_id}/{id}/。idempotent + --dry-run。
- 首版 schema 用 create_all（或 Alembic 0001 後 stamp）；Phase 0 不跑 migration 工具。
- Rollback：執行前 tar/cp -a output 備份；dry-run 先驗證；--rollback 刪 .db＋目錄移回。Phase 0 不接線→刪 .db 即完全還原。

## F. DB 位置/備份
- DATABASE_URL 預設 sqlite:///{BASE_DIR}/data/mad-professor.db。.gitignore 加 data/ *.db *.db-wal *.db-shm。
- 備份：WAL 下用 sqlite3 .backup 或 VACUUM INTO（一致性快照）＋ output/ tar。

## G. 連線管理
- 單例 engine（check_same_thread=False, pool_pre_ping）；event 設 PRAGMA foreign_keys=ON / journal_mode=WAL / busy_timeout=5000。
- sessionmaker(expire_on_commit=False)；get_db() yield+close；資料端點建議走同步(def→threadpool)，SSE/async 端點 DB 操作包 run_in_threadpool；pipeline 執行緒自建 session。
- 寫入節流（重要）：progress 不逐 SSE tick 寫 DB；即時進度續留記憶體 processing_tasks，DB 只寫狀態里程碑（processing→readable→done/error）。

## H. 既有程式碼影響（Phase 1 接線時）
- 新增 db.py/models.py/init_db ~150-220、migrate script ~150-250。
- paper_manager.py 幾乎全改（repository）~250-350。
- web_server.py 加 get_db+current_user、~15 端點查 DB+owner 授權、upload paper_uuid 唯一化 ~150-250。
- pipeline_core.py _update_global_index→寫 row + run_pipeline 里程碑 ~30-60。
- ai_core/rag_retriever 改動小（rag_tree/FAISS 仍 FS，只 preload 來源改查 DB）~30-60。
- 總計 ~700-1200 行 + 2 模組 + 1 script。良訊：rag_tree/FAISS 不入庫，衝擊集中在 paper_manager 與端點授權層。

## I. Phase 0 邊界（建議）
- Phase 0 = DB 層建好但「不接線」，系統行為與現在 100% 相同（續用 papers_index.json/chat_history.json）。
- 交付：db.py、models.py、init_db、(可選 Alembic 基線)、scripts/migrate_to_db.py（可 dry-run、預設不執行）、requirements/.gitignore/.env.example、設計文件。
- 不做：任何核心模組 import/呼叫 DB。
- import 時機：Phase 1 第一步正式跑 migrate→接線。Phase 0 僅以 dry-run 對 output 副本驗證資料可完整對應。
- 界線一句話：Phase 0 結束時 schema＋遷移腳本就緒且可演練，系統一行不依賴它；翻開關是 Phase 1。

## 驗證
純設計，無程式碼變更。靜態核對 paper_manager.py / web_server.py / pipeline_core.py / ai_core.py / rag_retriever.py / settings.py / requirements.txt。

## 待確認疑慮
1. conversations 的 grounding_sources/emotion：現持久化資料無此欄，Phase 1 需同步改前端 saveChatHistory 與 /chat/history 端點格式。
2. folders 頂層同名（parent_id NULL）SQLite UNIQUE 對多 NULL 不擋，需應用層檢查或 parent 用 0 哨兵。
3. user 刪除採 RESTRICT/軟刪：需產品決定「停用」vs「硬刪含 FS 目錄」流程（Phase 1）。
4. paper created_at/conversation 時間在舊資料無精確來源，遷移用檔案 mtime 近似。
