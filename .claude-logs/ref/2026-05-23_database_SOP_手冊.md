# Mad Professor 資料庫操作與未來擴充標準作業程序（Database Operations SOP）

> [!NOTE]
> 本文件為 **Mad Professor 專案資料庫操作的權威標準作業程序 (Database Operations SOP)**。
> 所有後續開發工程師及 AI 助理在進行任何涉及到資料庫（SQLite/PostgreSQL）的 Schema 修改、交易寫入、讀取查詢、Docker 化部署或數據遷移時，必須嚴格遵循本手冊之原則。

---

## 1. 核心開發原則（Core Principles）

任何資料庫的操作與開發，皆必須遵循以下四大黃金原則，以確保在多用戶、高併發下的系統穩定性。

### 原則 1：數據唯一真實來源（Single Source of Truth）
* 所有實體物件的狀態（使用者、資料夾樹、論文元數據、對話歷史、文件切片文本）一律以資料庫（`models.py`）中的資料記錄為唯一真理之源（SSoT）。
* 本地磁碟目錄（`OUTPUT_DIR`）僅作為「衍生快取與靜態檔案」存放區。不得在業務層直接依賴磁碟檔案進行論文存在性判定，一律優先查詢 DB。

### 原則 2：極短交易與防斷線自癒（Short Transactions & Auto-Heal）
* **禁止交易內含外部 API 調用**：嚴禁在資料庫交易（Transaction / Session 鎖定區間）內，進行任何網路請求、LLM/Gemini API 呼叫或 CPU 密集型計算。這會導致連線被長時間佔用，在 SQLite 下會引發 `database is locked` 災難，在 Postgres 下會迅速榨乾連線池。
* **自癒防禦**：所有 DB 引擎配置必須強制啟用 `pool_pre_ping=True`。在每一次獲取連線時進行 PING 測試，確保因雲端防火牆或超時切斷的 TCP 連線能自動重建自癒。

### 原則 3：標準交易語意管理（Safe Transaction Context）
* 為防止交易洩漏或殘留髒鎖，寫入/更新函數必須使用 SQLAlchemy 2.0 推薦的 `session.begin()` 上下文管理器，以確保**成功時自動 Commit、失敗時自動 Rollback**：
```python
# 🔴 錯誤寫法（未處理 rollback，易鎖庫）
with db.SessionLocal() as s:
    s.add(model_instance)
    s.commit()

# ✅ 正確寫法（語意安全，自動 Rollback/Commit）
with db.SessionLocal() as s:
    with s.begin():
        s.add(model_instance)
```

### 原則 4：高效能批次寫入（Bulk Insert Optimization）
* 當寫入大量數據（如 RAG 切片 `PaperChunk`，一次可能高達數千筆）時，**嚴禁使用 `for` 迴圈調用 `session.add()`**。這會產生高頻的 I/O 往返。
* 必須強制使用 SQLAlchemy 2.0 的 `session.execute(insert(Model), [...])` 進行批量寫入，將寫入耗時控制在 **50ms/千筆** 以內。
```python
from sqlalchemy import insert
from models import PaperChunk

# ✅ 標準 Bulk Insert 範式
with db.SessionLocal() as s:
    with s.begin():
        s.execute(insert(PaperChunk), [
            {"paper_id": pid, "chunk_index": idx, "raw_text": txt, ...}
            for idx, txt in enumerate(chunks)
        ])
```

---

## 2. 數據庫防禦性 Schema 設計規範（Defensive Schema Design）

### 2.1 物理級聯刪除與外鍵約束（Physical Cascades）
* SQLite 預設關閉外鍵。本專案在 `db.py` 中透過 SQLAlchemy Event 強制開啟外鍵約束：
  ```python
  cursor.execute("PRAGMA foreign_keys=ON")
  ```
* 後續開發在定義主子表關係（如 `Paper` 對 `PaperChunk`）時，必須同時設定 ORM 與資料庫物理外鍵的級聯刪除：
  ```python
  # models.py 聲明規範
  class PaperChunk(Base):
      paper_id: Mapped[int] = mapped_column(
          ForeignKey("papers.id", ondelete="CASCADE"), nullable=False # 物理級外鍵
      )

  class Paper(Base):
      chunks: Mapped[list["PaperChunk"]] = relationship(
          back_populates="paper",
          cascade="all, delete-orphan", # ORM 級外鍵
          passive_deletes=True,         # 允許 SQLite 底層物理 CASCADE，提高刪除效能
      )
  ```

### 2.2 多用戶與租戶隔離（Tenant Isolation）
* 所有涉及使用者數據的表，必須建立 `owner_id` 欄位並與 `users.id` 綁定。
* 執行查詢時，呼叫端（如 `web_server.py`）必須從會話（Session / JWT）中解析出 `owner_id`，並**顯式**作為過濾條件傳入 DAL，嚴禁寫出未隔離的 `s.query(Paper).all()`，以防止重大越權安全性漏洞。

---

## 3. Docker 容器化部署 SOP（Dockerization SOP）

當專案進行 Docker 鏡像打包與雲原生環境（K8s/ECS）部署時，必須嚴格執行以下儲存原則。

### 3.1 🚫 網路檔案系統（NFS/EFS）紅線防禦
> [!CAUTION]
> **絕對禁止在 NFS、AWS EFS 等網路檔案系統上運行 SQLite 資料庫！**
> SQLite 的 WAL 模式需要透過 `mmap()` 建立 `*.shm`（共享記憶體）檔案。網路檔案系統不支援多節點併發 `mmap`，在此類硬碟上運行 SQLite WAL 會 **100% 導致資料庫瞬間損毀（Database Corruption）**。

* **SOP 執行規則**：
  * **單機/單 Pod 容器化**：SQLite 檔案（`mad-professor.db`）必須掛載在**宿主機本地區塊儲存（本地 SSD / EBS）**。
  * **多 Pod 水平擴展容器化**：必須停止使用 SQLite，一鍵將 `DATABASE_URL` 切換至 PostgreSQL 雲端服務。

### 3.2 容器持久化 Volume 規劃
* Docker 部署時，必須採用統一的數據掛載卷（統一持久化路徑 `/app/storage`），利用 `settings.py` 中已支援的 `OUTPUT_DIR` 環境變數，實現單一掛載點掛載：
  ```bash
  # Docker 啟動指令規範範例
  docker run -d \
    -e DATABASE_URL=sqlite:////app/storage/data/mad-professor.db \
    -e OUTPUT_DIR=/app/storage/output \
    -e LOG_DIR=/app/storage/logs \
    -v /my/host/persistent_data:/app/storage \
    mad-professor:latest
  ```

---

## 4. 未來遷移與彈性防線（Future Migration & Scaling）

為了保障 Mad Professor 從目前的單機架構平滑過渡到大規模商用分散式架構，後續開發需遵循以下 Pg-Ready 與分散式 RAG 設計規範。

### 4.1 pgvector 中央向量化遷移
* **現狀限制**：目前向量庫採用本地 FAISS 扁平檔案儲存，無法在多個伺服器 Pod 間同步。
* **演進原則**：未來遷移至 PostgreSQL 時，應引入 `pgvector` 插件。
* 將 `vectors/` 目錄的扁平檔案徹底消滅，在資料庫中新建 `paper_embeddings` 資料表，使用 `HNSW` 索引實作向量檢索：
  ```sql
  -- pgvector 遷移 Schema 參考
  CREATE TABLE paper_embeddings (
      id SERIAL PRIMARY KEY,
      paper_id INT REFERENCES papers(id) ON DELETE CASCADE,
      chunk_index INT,
      embedding vector(768), -- 對齊 gemini-embedding-2 768 維度
      raw_text TEXT
  );
  CREATE INDEX ON paper_embeddings USING hnsw (embedding vector_cosine_ops);
  ```
  這可以讓 Web Server 變為完全無狀態，且向量檢索可利用 SQL 直接與 Metadata 混合查詢。

### 4.2 儲存層與 S3/GCS 雲端存取解耦
* 本地 PDF 與圖片目錄未來必須與宿主機檔案系統解耦。
* **演進原則**：寫入與讀取檔案時，必須透過標準的 `StorageProvider` 介面，在本地開發時使用 `LocalStorageProvider`，在雲端一鍵透過環境變數切換至 `S3StorageProvider`（對接 AWS S3 或 Google Cloud Storage）。

### 4.3 PostgreSQL 進階調優原則
當切換至 PostgreSQL 時，環境變數必須提供以下調優設定，以應對高併發與防火牆靜默中斷 TCP 連線：
* `DB_POOL_SIZE`（預設 10）：控制連線池大小。
* `DB_MAX_OVERFLOW`（預設 20）：應對突發高載。
* `DB_POOL_RECYCLE`（預設 1800 秒）：定時回收 TCP 連線，防範 NLB 超時斷開。

---

## 5. 未來需要強化的地方（Future Strengthening Checklist）

以下為資料庫架構未來升級的待辦任務清單，後續開發者應依此規劃：

- [ ] **1. 整合 Alembic 資料庫版控機制**
  * **目的**：取代 `Base.metadata.create_all()` 的定時炸彈，實現 Schema 熱升級。
  * **關鍵原則**：在 Alembic 配置中強制開啟 `render_as_batch=True`，確保相容 SQLite 的 `ALTER TABLE` 限制。
- [ ] **2. 實作線上安全備份機制（Online SQLite Backup API）**
  * **目的**：避免 WAL 併發寫入時直接 `cp` 導致備份檔案損毀。
  * **關鍵原則**：在 Python 端調用 `sqlite3.Connection.backup()` 進行線上熱備份。
- [ ] **3. 防禦 SQL IN 999 變數上限（RAG-1 跨文件查詢）**
  * **目的**：防範 SQLite `SQLITE_LIMIT_VARIABLE_NUMBER` 硬限制崩潰。
  * **關鍵原則**：在 RAG-1 跨文件查詢時，當 `paper_ids` 超過 500 個，必須將 SQL 查詢進行分批（Chunked Query）或改用 Subquery。
- [ ] **4. 資料夾遞迴深度與環偵測設計（Anti-Recursion Loop）**
  * **目的**：防止資料夾搬移時產生循環引用（A parent B, B parent A）造成資料庫死鎖。
  * **關鍵原則**：除應用層 seen 偵測外，在資料庫層加入防環約束或寫入前完整檢索。
- [ ] **5. 軟刪除與垃圾桶機制（Soft Delete）**
  * **目的**：提供資料誤刪復原防線（Trash Bin）。
  * **關鍵原則**：在 `Paper` 中引入 `deleted_at: DateTime` 欄位，預設過濾 `deleted_at IS NULL`，並由定時背景 task 物理清除 30 天前的過期資料。
