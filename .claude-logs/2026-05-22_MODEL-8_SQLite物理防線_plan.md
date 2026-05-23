# Phase 4.7? MODEL-8 — Plan：SQLite `paper_chunks` 物理防線 + 增強型 backfill CLI

> 本文件為**純分析與設計計畫**，在計畫獲得確認前，**嚴禁修改任何業務代碼與配置**。
> 依據：`.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §1.1 plan-execution 雙軌制、§4.1 plan 結構契約 + `.claude-logs/templates/template_plan.md` 8 章節。
> 來源：`.claude-logs/ref/model_optimization_blueprint.md` §6 + `.claude-logs/ref/db_analysis_and_future_extension.md`（已採納為架構基準）+ TODO MODEL-8（合併原 RAG-2 範圍）。

**Revision 注記（2026-05-23）**：6 個審查問題 + 2 個 Docker 化建議已納入修正：
1. **修正 1**（路徑統一）：grep 證實實體目錄是 `vectors/`（`pipeline_core.py:204 paper_dir / "vectors"`、字典 key 才是 `'vector_store'`）；全 plan 路徑用詞統一為 `vectors/`、舊 SOP 用 `vector_store/` 為錯誤指令、§1.4 已註記。
2. **修正 2**（`paper_db_id` 注入鏈路）：grep 證實 `pipeline_core` 內已有 `self._owner_id` (L233) + `self.paper_info['paper_id']` (= paper_uuid)、`_stage_rag` 自己呼叫 `paper_manager.get_paper_db_id()` 即可，**無需動 web_server**（OUTPUT_DIR import 1 行除外、見修正 7）。詳見新增 §3.3.1。
3. **修正 3**（`tiling_method` 移除）：grep 證實 `MarkdownHeaderTextSplitter` 只加 `{"Header": ...}`、`tiling_method` 寫在 `_tiled.json` 內、與 markdown chunks 上下游分離 → 從 ORM / 寫入 / 對比表全部移除。
4. **修正 4**（`write_index_meta_json` 抽 module-level）：CLI 跟 RagProcessor 共用、改為 `processor/rag_processor.py` 內 module-level helper。
5. **修正 5**（`get_paper_db_id` 確認）：grep 證實 `paper_manager.py:336` **已存在**、本 plan 不需新增、僅在 §3.1 引用。
6. **修正 6**（`cmd_init` pseudo-code 補完）：§3.4 補完 FAISS docstore 反向取邏輯 + §4 風險表加「`init` 場景 `doc_type` 為空」+ §5.1 C3 加 1 個 test。
7. **修正 7**（OUTPUT_DIR env 化、依 db_analysis §5.2）：grep 證實 `web_server.py:77 OUTPUT_DIR = BASE_DIR / "output"` 為寫死、跟 MODEL-1+2/MODEL-3/MODEL-9 等 env 化風格不一致；Docker 部署被阻擋。新增 §3.6 子改動 D、推薦併進 C1（Q17）。
8. **修正 8**（Pg-Ready 安撫註記、依 db_analysis §5.3）：純註記、無 code 改動；§1.0 加 footnote、§4 風險表加 1 條、Q18 收錄。確認既有 `db.py` 已 Pg-Ready、本期不做 Pg 切換驗證。
9. **不納入**：db_analysis §5.1 Volume 掛載（純 DevOps、Docker compose 配置議題）+ §5.4 MinerU SCP→HTTP（MODEL-10 獨立 task、本期不重複）。

---

## TL;DR

- **問題與挑戰**：升級 embedding model（例：`gemini-embedding-2` → 未來新 model）後、既有 `vectors/` 全作廢；當前唯一恢復路徑是「重跑整條 pipeline」（含 MinerU PDF 解析 30-60 分/份），但其實只需要 `raw_text → re-embed`（< 30 秒/份）。**99% 的時間都是浪費**。書籍場景（如《我與你》Martin Buber）更不可接受。
- **核心根因**：raw text 無物理儲存層、只存在於 `output/<owner>/<paper>/<paper_name>_tiled.json` + FAISS docstore（衍生快取）內、無法用 SQL 低成本批次提取；同時 `vectors/` 內無「用哪個 embedding model」的版本標記、無法做自動偵測。
- **設計解法**：4 子項、拆 3 commits 落地。
  - **C1（schema）**：`models.py` 新增 `PaperChunk` ORM、`db.init_db()` 自動建表（無 Alembic、依 db_analysis §1 結論）；`paper_manager.py` 加 `replace_paper_chunks` / `iter_paper_chunks` / `list_papers_with_chunks` 三個 DAL helper（`get_paper_db_id` 已存在、不需新增——**修正 5**）。
  - **C2（pipeline 寫入）**：`processor/rag_processor.py::_create_vector_store` 完成 FAISS 寫入後、新增兩個 helper：`_write_paper_chunks_to_db()` 批次 INSERT 真理源 + module-level `write_index_meta_json()`（**修正 4**） 寫版本標記檔；`pipeline_core.py::_stage_rag` 內 1-3 行注入 `paper_db_id`（**修正 2**）。
  - **C3（CLI）**：新增 `tools/regen_rag.py`、子命令 `--check / --paper / --all / --force / --dry-run / --init`；`--init` 一次性把既有 paper 從 `vectors/` FAISS docstore 反向導入 `paper_chunks`（**修正 6** pseudo-code 完整）。
- **影響範圍**：
  - 新增 1 張表（`paper_chunks`、`ON DELETE CASCADE`）+ 1 個 metadata 檔（`vectors/index_meta.json`）+ 1 個 CLI script
  - **不破壞** 任何既有 schema / API 簽名 / pipeline_core stage 介面
  - 既有 paper 行為向下相容（無 chunks rows 不會崩潰、可由 `--init` 補完）
  - **僅動 web_server.py 1 行**（修正 7：`from settings import OUTPUT_DIR`、其他不動；修正 2 確認 `paper_db_id` 注入由 pipeline_core 內部完成、不涉及 web_server）
- **預估**：3 commits、~10.5 hr 累計（修正 7 OUTPUT_DIR 改動約 ~30 min、併進 C1）；本 task 取代原 RAG-2 候選項。
  - C1：~3 hr（不再需要寫 `get_paper_db_id` helper、實際省 ~10 min）
  - C2：~3 hr（多 1-3 行 `paper_db_id` 注入、可忽略）
  - C3：~4 hr（`cmd_init` pseudo-code 已完整化、實作風險降低）
- **未來價值**：升 embedding model / 改 chunk filter / 改 tiling 後、書籍類 backfill 從 30-60 分 → < 5 分（萬倍提速）。

---

## 1. 現況盤點

### §1.0 既有 DB 架構（依 `db_analysis_and_future_extension.md` 抽取）

> **`db_analysis_and_future_extension.md` §1 結論直接採納**：「這完全不是大改、是極其安全、無縫相容、增量式（Additive）的架構擴充。」
> 既有的 `users` / `folders` / `papers` / `conversations` 四張表 **100% 不動**；只新增 `paper_chunks` 子表。

| 既有表 | 檔案行數 | 主鍵 / 關鍵欄位 | 對 MODEL-8 的相依 |
|---|---|---|---|
| `User` (users) | `models.py` L31-50 | `id` (INT PK) / `username` UNIQUE | 不動 |
| `Folder` (folders) | `models.py` L53-84 | `id` (INT PK) / `owner_id` FK | 不動 |
| `Paper` (papers) | `models.py` L87-149 | `id` (INT PK) / `(owner_id, paper_uuid)` UNIQUE | **新表 FK 對齊 `Paper.id`** |
| `Conversation` (conversations) | `models.py` L152-176 | `id` (INT PK) / `paper_id` FK ON DELETE CASCADE | 不動（樣本：cascade 設計可直接借鏡） |

**DB connection / session 風格**（`db.py` L36-65、`paper_manager.py` L51-65）：
- `engine` 以 `create_engine(DATABASE_URL, pool_pre_ping=True)` 建立、SQLite 加 `check_same_thread=False`
- 每連線自動套用 PRAGMA：`foreign_keys=ON` / `journal_mode=WAL` / `busy_timeout=5000`（`db.py` L36-51）→ **FK ON DELETE CASCADE 物理生效**、MODEL-8 cascade 設計可直接相容
- `SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)`
- 既有 DAL 統一寫法：`with db.SessionLocal() as s: ... s.commit()`（樣本：`paper_manager.py::append_chat_message` L380-393、`save_chat_history` L401-415）
- `init_db()` 用 `Base.metadata.create_all()`、**無 Alembic**（`db.py` L78-83）
- **`paper_manager.get_paper_db_id(owner_id, paper_uuid) -> Optional[int]` 已存在於 L336-343**（**修正 5** grep 確認）；本 plan §3.3.1 / §3.4 / CLI 直接使用、不重新實作。

> **Pg-Ready footnote（修正 8、依 db_analysis §5.3）**：既有 `db.py:36-51` 內所有 SQLite 特有 PRAGMA（`foreign_keys=ON` / `journal_mode=WAL` / `busy_timeout=5000`）已隔離在 `if not _IS_SQLITE: return` 控制項內、是優秀的防禦性設計。MODEL-8 `PaperChunk` ORM 採標準 SQLAlchemy 2.0 Declarative + `ForeignKey(..., ondelete="CASCADE")`、無 SQLite 特有 SQL。未來如要切 PostgreSQL（多 Pod K8s 部署）、只需 `export DATABASE_URL=postgresql://...`、**零 code 修改**。本期不做 Pg 連線測試（Q18）。

**`db_analysis_and_future_extension.md` 內既有的 `paper_chunks` 設計建議（§3.1）vs 本 plan**（已套用**修正 3**：移除 `tiling_method` 行）：

| 維度 | db_analysis 原提案 (§3.1) | 本 plan §3.1 採納方案 | 差異 |
|---|---|---|---|
| `paper_id` FK | `ForeignKey("papers.id", ondelete="CASCADE")` | 同 | ✅ 一致 |
| `chunk_key` | `String(255)` 字串型如 `"sec_0_part_0"` | 同 + 加 `chunk_index INTEGER` 作排序鍵 | 🟡 **本 plan 多 1 欄**（`chunk_index` 用於 stable order、`chunk_key` 用於語意定位） |
| `raw_text` | `Text` 非空 | 同 | ✅ 一致 |
| `translated_text` | `Text` 可空 | 同 | ✅ 一致 |
| `metadata_json` | `Text` JSON 字串 | 同 | ✅ 一致 |
| `embedding_model` / `output_dimensions` | **未提及** | **本 plan 新增**：寫入時記錄 EMBEDDING_MODEL_NAME / OUTPUT_DIMENSIONS | 🔴 **本 plan 額外擴充**（為 CLI `--check` mismatch 偵測必要） |
| `chunk_filter_version` | 未提及 | 本 plan 新增（如 `'B2-2026-05-22'`） | 🔴 本 plan 額外擴充 |
| `Bulk Insert` 效能要求 | `db_analysis §4` 明列：用 SQLAlchemy `insert(PaperChunk)` 批量、千 chunks < 50ms | 完全採納 | ✅ 一致 |
| 級聯刪除 | `passive_deletes=True` 由底層 FK 強制 | 完全採納（既有 `Conversation` 已用此 pattern、樣本可循） | ✅ 一致 |

> **修正 3 註解**：db_analysis §3.1 內原本有 `tiling_method: String(50)` 欄位、本 plan **不採納**。原因：grep `processor/rag_processor.py:172-173` 證實 `MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Header")])` 輸出的 Document.metadata 只含 `{"Header": "..."}`、不會帶 MODEL-3 寫在 `_tiled.json` items 內的 `tiling_method` 標籤（後者寫在 tiling stage、grep `processor/tiling_processor.py:185,297,304`）；硬塞此欄會永遠為 None、無實際資訊。未來如要追溯 tiling 模式、走 `chunk_filter_version` + `tiling_config_signature` snapshot。

**結論**：本 plan **採納 db_analysis §3.1 schema 為基準**、移除 `tiling_method`、加 3 個版本偵測欄位；schema 變動安全、與既有 DB 風格 100% 對齊。

### §1.1 rag_processor 既有 FAISS 寫入流程

**`processor/rag_processor.py::process`（L92-144）**：

```
1. 讀 input_path JSON → paper_data
2. 抽 abstract + 過濾 sections（L117-124）
3. _restructure_tree → 生成 tree_json（L127-131）
4. _generate_markdown → 寫 final_<paper>_rag.md（L134）
5. _create_vector_store(md_path, vector_store_path, doc_type)（L137）
   ├─ MarkdownHeaderTextSplitter.split_text → docs（L172-176）
   ├─ for d in docs: _is_chunk_meaningful(d, doc_type) → filter（L181-186）
   ├─ FAISS.from_documents(meaningful_docs, embedder, distance_strategy=MAX_INNER_PRODUCT)（L200-204）
   └─ vector_store.save_local(vector_store_path)（L207）
```

**Document 結構**（從 `MarkdownHeaderTextSplitter` + `_is_chunk_meaningful` 衍生、L181）：
- `doc.page_content`：MD chunk 內容（含 doc_type Context 前綴、依 B2 已 ship 邏輯）
- `doc.metadata`：**只含 `{"Header": "<section-title>"}`**（`MarkdownHeaderTextSplitter` 加注的 H1 標題、依 L172 `headers_to_split_on = [("#", "Header")]`）；**無 `tiling_method` / `index` / `part` 等 MODEL-3 標籤**（修正 3 grep 證據）

**`_is_chunk_meaningful`（L35-81、B2 已 ship）**：套用 5 條過濾規則（空 / 純數字 / email/phone/url 保留 / resume/slides ≥ 3 / 其他 ≥ 10）；目前無 version constant、本 plan §3.1 將補上 `CHUNK_FILTER_VERSION` 字串標記。

**`pipeline_core.py::_stage_rag`（L677-691）**：呼叫處單一、傳入 `doc_type=output_paths.get('_confirmed_doc_type', 'academic')`；vector_store 物理路徑為 `paper_dir / "vectors"`（**L204、grep #1 確認**）；`output_paths` dict key 為 `'vector_store'`（注意：**字典 key 與實體目錄名不一致**——key 為 `'vector_store'`、實體為 `vectors/`）。

### §1.2 既有 vector store / 物理目錄結構

**修正 1 grep 確認**：

- **實體路徑**：`output/<owner_id>/<paper_uuid>/vectors/`（`pipeline_core.py:204 paper_dir / "vectors"`）
- **`output_paths` 字典 key**：`'vector_store'`（同 L202-204）——key 名與實體目錄名不一致是既有設計、本 plan 沿用、不做重命名
- 內容：FAISS 預設 `index.faiss` + `index.pkl`（langchain `FAISS.save_local`）
- **目前無任何 metadata 檔**——無 model version、無 dimension 紀錄 → MODEL-8 §3.2 新增 `vectors/index_meta.json` 補此空缺

### §1.3 既有 `tools/` 目錄

```bash
$ ls tools/
__pycache__
check_doc_type_registry.py     # doc_type 註冊表檢查
test_resume_vision.py          # resume vision 測試
```

→ **`tools/regen_rag.py` 為新檔**、無既有實作衝突。

### §1.4 既有 backfill SOP（對比 MODEL-8 落地後）

依 MODEL-1+2 plan §4.4 + MODEL-3 B3 執行報告 §7.4 既有 3 步驟 SOP：

```bash
# 既有 SOP（升 embedding 或改 chunk 結構時）
pkill -f web_server.py
# ⚠️ 既有 SOP 內 `rm -rf output/*/*/vector_store/` 路徑名錯誤——實際是 vectors/
rm -rf output/*/*/vectors/                   # 修正後
rm -f output/*/*/*_tiled.json                # MODEL-3 改 chunk 結構時要刪
nohup venv/bin/python web_server.py > log 2>&1 &
# 對每份 paper 重新上傳 / 觸發 pipeline 重跑（pdf2md + translate + tiling + rag 整鏈）
# 書籍類耗時 30-60 分/份
```

> **修正 1 explicit note**：MODEL-1+2 backfill SOP（§4.4）/ MODEL-3 B3 執行報告（§7.4）內的 `rm -rf output/*/*/vector_store/` **路徑名是錯誤指令**、實體目錄是 `vectors/`（grep 證據：`pipeline_core.py:204`）。執行時應改用 `rm -rf output/*/*/vectors/`。**本 plan 不修改既有報告**（規範要求）、只在此處註記；後續執行 backfill 的人請以本 §1.4 為準。

**MODEL-8 落地後 SOP**：

```bash
# 升 embedding（只改 raw_text → vector 對應）
export EMBEDDING_MODEL_NAME="gemini-embedding-3"   # 假設
venv/bin/python tools/regen_rag.py --check         # 自動列出 mismatch
venv/bin/python tools/regen_rag.py --all           # 從 paper_chunks 讀 raw_text、重 embed
# 整鏈耗時 < 5 分（10 份 paper）；書籍類 30-60 秒/份
```

---

## 2. 觀察到的問題與證據

### 問題 #1：重 embedding 必須重 PDF 解析（核心痛點）

- **證據**：`pipeline_core.py::_stage_rag` L677-691 + `processor/rag_processor.py::_create_vector_store` L146-210
  - 整條 pipeline 必經 stages：`pdf2md → analyze → translate → image_caption → tiling → extra_info → rag`
  - 其中 `pdf2md` 依賴 MinerU、CPU/GPU 密集型；500+ 頁書籍實測 30-60 分鐘
  - 但 `_create_vector_store` 真正需要的只是「最終 markdown → FAISS」、< 30 秒（書籍類 < 2 分）
- **影響**：升 embedding model 或改 chunk filter 後、99% 時間浪費在不需重跑的 stages；書籍場景使「升 model」實質不可行（30 份書 = 15+ 小時）

### 問題 #2：raw text 無物理儲存層

- **證據**：
  - `vectors/` 內為 FAISS binary（`index.faiss` + `index.pkl`）、無法用 SQL 提取 raw text
  - `output/<owner>/<paper>/*_tiled.json` 是 tiling stage 中間產物、結構受 MODEL-3 改動影響（B1+B2+B3 已改 chunk 結構 / metadata schema）
  - FAISS `docstore` 內雖然存了 page_content + metadata、但讀法非標準 SQL、需 langchain API + 反序列化
- **影響**：
  - 無法低成本批次提取 raw text 做變換（如：跨 paper 搜尋、chunk 內容審計、檢索診斷）
  - 無法做 hybrid retrieval 擴展（db_analysis §3.3 提到 BM25 + Vector RRF）
  - 翻譯結果 `translated_text` 散落在 `*_tiled.json` 內、無快取機制、未來「重渲對照 PDF / 匯出 MD」會重複叫 LLM 翻譯（db_analysis §3.4）

### 問題 #3：缺乏版本偵測

- **證據**：`find output -name "index_meta.json"` 空、`find output -name "vectors" -type d` 內無 metadata
- **影響**：
  - baron 無法用程式判定「哪些 paper 是用舊 model embed」、只能全砍重做
  - 升 model 後沒有「批次自動偵測 mismatch + 重建」機制、靠人工記憶
  - 無法做 A/B（兩個 model 並存 + 哪個 paper 該用哪個）

### 問題 #4：原 RAG-2 候選範圍過窄

- **證據**：TODO 內原 RAG-2 描述「`tools/regen_rag.py` per-paper 重跑 rag stage」
- **影響**：若沒有 `paper_chunks` 物理表、「重跑 rag stage」仍需從 `_tiled.json` 讀；但 `_tiled.json` 內 zh_text 是 MODEL-3 改 chunk 結構後產出、跟既有 vector_store 內 chunk 可能不對齊 → RAG-2 必須**升級到「從 paper_chunks 讀 raw_text」**才能真正解問題、本 plan 將其合併進 MODEL-8 範圍

---

## 3. 設計方案

### §3.0 整體架構流程圖

```
                     ┌──────────────────────────┐
[PDF Upload] ───────>│ pipeline_core stages:    │
                     │ pdf2md → analyze →       │
                     │ translate → tiling →     │
                     │ extra_info → rag         │
                     └────────────┬─────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ _create_vector_store │ ──(既有 B2 已 ship)──> FAISS 寫 vectors/
                       │  (rag_processor.py)  │
                       └──────────┬───────────┘
                                  │ (本 plan 新增)
                       ┌──────────┴──────────────────┐
                       ▼                             ▼
            _write_paper_chunks_to_db        write_index_meta_json (module-level、修正 4)
            (批次 INSERT into paper_chunks)  (寫 vectors/index_meta.json)
                       │                             │
                       ▼                             ▼
                  ┌─────────┐                ┌──────────────────┐
                  │ SQLite  │                │ vectors/         │
                  │ paper_  │                │  index.faiss     │
                  │ chunks  │                │  index.pkl       │
                  │ (真理源) │                │  index_meta.json │
                  └─────────┘                └──────────────────┘

──────────────────────────────────────────────────────────────────

[未來升 embedding model / 改 chunk filter / 改 tiling]
                  │
                  ▼
       tools/regen_rag.py --check           ──掃所有 paper / 比對──>  mismatch 清單
                  │
                  ▼
       tools/regen_rag.py --all
                  │
                  ▼ (per paper)
              SELECT raw_text, metadata_json FROM paper_chunks WHERE paper_id = ?
                  │
                  ▼
              embed_documents()   ←──(用新 model、< 30 秒/書籍)
                  │
                  ▼
              FAISS.from_documents → save_local()
                  │
                  ▼
              覆寫 index_meta.json （新 model / dimension / timestamp）
                  │
                  ▼
              <DONE、向 baron 報告耗時 + 成功率>
```

### §3.1 子改動 A — SQLite `paper_chunks` 表（C1）

**目標與邏輯**：新增 `PaperChunk` ORM 類別、依 db_analysis §3.1 schema 為基準、加版本偵測欄位、移除 `tiling_method`（修正 3）。

**檔案改動**：
- `models.py` 新增 `PaperChunk` 類別 + `Paper.chunks` back-populates relationship
- `paper_manager.py` 新增 3 個 DAL helper：`replace_paper_chunks` / `iter_paper_chunks` / `list_papers_with_chunks`
  - **不重複新增** `get_paper_db_id`（**修正 5**：已存在於 L336-343）
- `processor/rag_processor.py` 新增 module-level constant：`CHUNK_FILTER_VERSION = 'B2-2026-05-22'`（為 MODEL-1+2 B2 chunk filter 版本錨點；未來改動 `_is_chunk_meaningful` 邏輯時 bump 此字串）

**ORM 設計**（`models.py` 末尾加；**修正 3 已移除 `tiling_method`**）：

```python
class PaperChunk(Base):
    __tablename__ = "paper_chunks"
    __table_args__ = (
        Index("ix_paper_chunks_paper_id", "paper_id"),
        Index("ix_paper_chunks_embedding_model", "embedding_model"),
        UniqueConstraint("paper_id", "chunk_index", name="uq_paper_chunks_paper_chunk"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # 語意鍵：「sec_0_part_0」/「sec_2_text_5」等、來自 doc.metadata['Header']
    chunk_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # 完整 chunk metadata（含 Header / 等）；JSON 字串
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # 版本標記（本 plan 對 db_analysis §3.1 的擴充）
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    output_dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_filter_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    paper: Mapped["Paper"] = relationship(back_populates="chunks")
```

> **修正 3 重點**：移除 `tiling_method` 欄位。grep 證據：`processor/rag_processor.py:172-173` 證實 `MarkdownHeaderTextSplitter` 輸出的 metadata 只含 `{"Header": ...}`、不會有 tiling_method。

**對應 `Paper` 加 back-populates**（`models.py` L142-149 周邊）：

```python
class Paper(Base):
    # ...既有欄位不動...
    chunks: Mapped[list["PaperChunk"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="PaperChunk.chunk_index",
    )
```

**DAL helper**（`paper_manager.py` 末尾加）：

```python
def replace_paper_chunks(paper_db_id: int, chunks: list[dict]) -> int:
    """覆寫式批次 INSERT：清掉舊 chunks、批量寫入新的。

    Args:
        paper_db_id: Paper.id（INT PK）、不是 paper_uuid
        chunks: list of dict 含
            chunk_index, chunk_key, raw_text, translated_text, doc_type,
            metadata_json (JSON 字串),
            embedding_model, output_dimensions, chunk_filter_version
            （修正 3：無 tiling_method）
    Returns:
        寫入筆數
    """
    _ensure_db()
    with db.SessionLocal() as s:
        s.query(PaperChunk).filter_by(paper_id=paper_db_id).delete()
        # SQLAlchemy 2.0 批次 insert（依 db_analysis §4 效能要求、< 50ms/千筆）
        if chunks:
            from sqlalchemy import insert
            s.execute(insert(PaperChunk), [
                {**c, "paper_id": paper_db_id} for c in chunks
            ])
        s.commit()
    return len(chunks)


def iter_paper_chunks(paper_db_id: int):
    """逐 chunk 讀取（regen 用）、yield dict（含 raw_text + metadata_json）。"""
    _ensure_db()
    with db.SessionLocal() as s:
        rows = (
            s.query(PaperChunk)
            .filter_by(paper_id=paper_db_id)
            .order_by(PaperChunk.chunk_index)
            .all()
        )
        for c in rows:
            yield {
                "chunk_index": c.chunk_index,
                "chunk_key": c.chunk_key,
                "raw_text": c.raw_text,
                "translated_text": c.translated_text,
                "doc_type": c.doc_type,
                "metadata_json": c.metadata_json,
                "embedding_model": c.embedding_model,
                "output_dimensions": c.output_dimensions,
                "chunk_filter_version": c.chunk_filter_version,
            }


def list_papers_with_chunks(owner_id: Optional[int] = None) -> list[dict]:
    """掃所有有 paper_chunks 的 paper、回 [(paper_db_id, owner_id, paper_uuid, embedding_model, output_dimensions)...]。

    供 regen_rag --check 用。
    """
    _ensure_db()
    with db.SessionLocal() as s:
        q = (
            s.query(Paper.id, Paper.owner_id, Paper.paper_uuid,
                    PaperChunk.embedding_model, PaperChunk.output_dimensions)
            .join(PaperChunk, PaperChunk.paper_id == Paper.id)
            .distinct()
        )
        if owner_id is not None:
            q = q.filter(Paper.owner_id == owner_id)
        return [
            {"paper_db_id": r[0], "owner_id": r[1], "paper_uuid": r[2],
             "embedding_model": r[3], "output_dimensions": r[4]}
            for r in q.all()
        ]
```

> **修正 5 註解**：`paper_manager.get_paper_db_id(owner_id, paper_uuid) -> Optional[int]` 已存在於 `paper_manager.py:336-343`（grep 確認）、本 plan **不重複新增**；§3.3.1 / §3.4 CLI 直接 import 使用。

### §3.2 子改動 B — `index_meta.json` 寫入（C2、**修正 4** 改 module-level）

**目標與邏輯**：每次 `_create_vector_store` 完成後、立即寫一份版本標記檔到 `vectors/index_meta.json`、供 CLI 比對。**改為 module-level helper**（修正 4），讓 `RagProcessor` 和 `tools/regen_rag.py` CLI 共用、避免重複實作。

**檔案改動**：`processor/rag_processor.py` 新增 module-level 函式 `write_index_meta_json`、`_create_vector_store` 內呼叫。

**`index_meta.json` 格式**：

```json
{
  "embedding_model": "gemini-embedding-2",
  "output_dimensions": 768,
  "chunk_filter_version": "B2-2026-05-22",
  "tiling_config_signature": {
    "TILING_BYPASS_CHAR_LIMIT": 5000,
    "TILING_MAX_LENGTH": 2500,
    "TILING_PARAGRAPH_THRESHOLD": 30000
  },
  "chunks_total": 42,
  "created_at": "2026-05-22T22:35:00Z",
  "rag_processor_version": "MODEL-8-C2"
}
```

**Module-level helper**（`processor/rag_processor.py` 內、class RagProcessor 之前）：

```python
def write_index_meta_json(vector_store_path, chunks_total: int, logger=None) -> None:
    """寫 vectors/index_meta.json、為 regen_rag --check mismatch 偵測用。

    Phase 4.7? MODEL-8 C2（依 plan §3.2、修正 4 改 module-level）。
    Module-level、給 RagProcessor + CLI tools/regen_rag.py 共用、避免重複實作。

    Args:
        vector_store_path: vectors/ 目錄路徑（str 或 Path）
        chunks_total: 寫入的 chunk 數量
        logger: 可選 logger（無則靜默）
    """
    from settings import (
        EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS,
        TILING_BYPASS_CHAR_LIMIT, TILING_MAX_LENGTH, TILING_PARAGRAPH_THRESHOLD,
    )
    from datetime import datetime, timezone
    meta = {
        "embedding_model": EMBEDDING_MODEL_NAME,
        "output_dimensions": EMBEDDING_OUTPUT_DIMENSIONS,
        "chunk_filter_version": CHUNK_FILTER_VERSION,
        "tiling_config_signature": {
            "TILING_BYPASS_CHAR_LIMIT": TILING_BYPASS_CHAR_LIMIT,
            "TILING_MAX_LENGTH": TILING_MAX_LENGTH,
            "TILING_PARAGRAPH_THRESHOLD": TILING_PARAGRAPH_THRESHOLD,
        },
        "chunks_total": chunks_total,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rag_processor_version": "MODEL-8-C2",
    }
    meta_path = Path(vector_store_path) / "index_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    if logger:
        logger.info(
            f"[index_meta] 已寫入 {meta_path}（"
            f"model={EMBEDDING_MODEL_NAME}、dim={EMBEDDING_OUTPUT_DIMENSIONS}）"
        )
```

**`RagProcessor._create_vector_store` 呼叫**（C2）：

```python
write_index_meta_json(vector_store_path_obj, len(meaningful_docs), logger=self.logger)
```

**`tools/regen_rag.py` 呼叫**（C3）：

```python
from processor.rag_processor import write_index_meta_json
# ... after FAISS save_local ...
write_index_meta_json(output_dir, len(docs))
```

### §3.3 子改動 C — rag_processor 寫入 paper_chunks（C2）

**目標與邏輯**：在 `_create_vector_store` 內、`FAISS.from_documents` 之後立即寫 `paper_chunks` 表；確保 raw_text 永久保留、不依賴 `vectors/`。

#### §3.3.1 `paper_db_id` 注入鏈路（**修正 2** 必修點）

**注入源 grep 證據**（依第一步 grep #2 + 補查確認）：

| 來源 | 位置 | 內容 |
|---|---|---|
| `pipeline_core.py:97` | `self.paper_info = {'paper_id': None, 'output_dir': None}` | dict 容器 |
| `pipeline_core.py:233` | `self._owner_id = owner_id` | 從 `process(pdf_path, ..., owner_id=...)` 簽名取 |
| `pipeline_core.py:238` | `self.paper_info['paper_id'] = pid` | 賦值 paper_uuid（變數名 pid、實質為 sanitize 後的 paper_uuid） |
| `pipeline_core.py:658` | `paper_uuid=paper_name` | 後續 upsert_paper 呼叫處、確認 `paper_uuid` 即 paper_name |
| `paper_manager.py:336` | `def get_paper_db_id(owner_id, paper_uuid) -> Optional[int]` | **已存在**、可直接 import |

**結論**：`pipeline_core._stage_rag` 內已有完整資訊（`self._owner_id` + `self.paper_info['paper_id']`）、**無需動 web_server.py**、可在 `_stage_rag` 內部直接呼叫 `paper_manager.get_paper_db_id(...)`。

**注入時機與路徑（C2 採用 fallback 2 = pipeline_core 內部查詢）**：

兩個候選來源：

1. **上游注入**（不採用本期）：web_server.py 內 `/api/papers/{paper_uuid}/process` endpoint 收 request 時、查 SQL 拿 paper_db_id 後、放進 pipeline_core 傳入的 metadata 中
   - 缺點：本期擴張 C2 commit 範圍、跨檔變動
2. **內部查詢**（C2 採用、推薦）：pipeline_core 內知道 `owner_id + paper_uuid`、自己呼叫 `paper_manager.get_paper_db_id(owner_id, paper_uuid)`
   - 優點：C2 動最少、單檔內收斂；不需 touch web_server.py

**C2 commit 範圍明確化**：

- **必動**：`pipeline_core.py::_stage_rag`（L677-691）內加 2-3 行：
  ```python
  def _stage_rag(self, pdf_path, paper_dir, paper_name, output_paths):
      input_path = output_paths.get('extra_info') or output_paths.get('translate')
      if not input_path:
          raise ValueError("未找到 JSON 文件")
      paths = self._get_stage_output_path('rag', paper_dir, paper_name)
      images_info_path = self._get_stage_output_path('image_caption', paper_dir, paper_name)
      doc_type = output_paths.get('_confirmed_doc_type', 'academic')
      # === MODEL-8 C2 新增（修正 2）===
      paper_db_id = None
      if self._owner_id is not None:
          import paper_manager
          paper_db_id = paper_manager.get_paper_db_id(
              self._owner_id, self.paper_info['paper_id']
          )
          if paper_db_id is None:
              self.logger.warning(
                  f"[MODEL-8] get_paper_db_id 回 None "
                  f"(owner={self._owner_id}, uuid={self.paper_info['paper_id']})"
                  "、paper_chunks 寫入將被跳過、CLI --init 可事後補完"
              )
      # === MODEL-8 C2 新增 end ===
      md_path, tree_path, vector_path = self.rag_processor.process(
          str(input_path), str(paths['md']), str(paths['tree_json']), str(paths['vector_store']),
          images_info_path=str(images_info_path) if images_info_path.exists() else None,
          doc_type=doc_type,
          paper_db_id=paper_db_id,   # MODEL-8 新增
      )
      return {...}
  ```
- **必動**：`processor/rag_processor.py::process` + `_create_vector_store` 加 `paper_db_id: Optional[int] = None` 參數
- **不動**：`web_server.py`（修正 2 確認）
- **不動**：`paper_manager.get_paper_db_id`（已存在、修正 5）
- **不動**：其他 paper 入場 hook 流程

**降級策略**：若 `get_paper_db_id` 回 None（極罕見：paper 尚未 commit 進 DB、或舊資料）→ 走 §3.3 paper_db_id=None 優雅降級路徑、log warning、CLI `--init` 可事後補完。

#### §3.3.2 `_create_vector_store` 寫 paper_chunks

```python
def _create_vector_store(self, md_path, vector_store_path, doc_type='', paper_db_id=None):
    # ...既有 split / filter / FAISS 流程不動（L160-210）...
    vector_store.save_local(str(vector_store_path_obj))

    # === MODEL-8 C2 新增 ===
    if paper_db_id is not None:
        try:
            self._write_paper_chunks_to_db(meaningful_docs, paper_db_id, doc_type)
        except Exception as e:
            # 不阻塞主流程（既有 paper / 測試環境無 DB 時優雅降級、依 Q12）
            self.logger.error(f"[paper_chunks] 寫入失敗（不阻塞主流程）: {e}", exc_info=True)
    else:
        self.logger.warning(
            "[paper_chunks] paper_db_id 未提供、跳過寫入 SQLite "
            "(可由 tools/regen_rag.py --init 事後補完)"
        )

    try:
        write_index_meta_json(  # 修正 4：module-level helper
            vector_store_path_obj, len(meaningful_docs), logger=self.logger
        )
    except Exception as e:
        self.logger.error(f"[index_meta] 寫入失敗（不阻塞主流程）: {e}", exc_info=True)
    # === MODEL-8 C2 新增 end ===

    return str(vector_store_path_obj)


def _write_paper_chunks_to_db(self, docs, paper_db_id: int, doc_type: str) -> None:
    """將 meaningful_docs 批次寫入 paper_chunks 表（C2、依 plan §3.3）。

    修正 3：不取 tiling_method（MarkdownHeaderTextSplitter 輸出 metadata 不含此欄位）。
    """
    from settings import EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS
    import paper_manager
    rows = []
    for i, d in enumerate(docs):
        # chunk_key 從 metadata 內抽（MarkdownHeaderTextSplitter 加注的 Header）
        chunk_key = (d.metadata or {}).get('Header', '') or f"chunk_{i}"
        rows.append({
            "chunk_index": i,
            "chunk_key": chunk_key[:255],
            "raw_text": d.page_content or '',
            "translated_text": None,  # 暫時不填、未來 RAG hybrid / translation cache 才補
            "doc_type": doc_type,
            "metadata_json": json.dumps(d.metadata or {}, ensure_ascii=False),
            "embedding_model": EMBEDDING_MODEL_NAME,
            "output_dimensions": EMBEDDING_OUTPUT_DIMENSIONS,
            "chunk_filter_version": CHUNK_FILTER_VERSION,
        })
    n = paper_manager.replace_paper_chunks(paper_db_id, rows)
    self.logger.info(
        f"[paper_chunks] 寫入 {n} 個 chunks (paper_db_id={paper_db_id}, "
        f"model={EMBEDDING_MODEL_NAME}, dim={EMBEDDING_OUTPUT_DIMENSIONS})"
    )
```

### §3.4 子改動 D — `tools/regen_rag.py` CLI（C3、**修正 6** cmd_init 補完）

**完整 spec**：

```python
"""
tools/regen_rag.py — MODEL-8 backfill CLI

用法:
  python tools/regen_rag.py --check                  # 掃所有 paper / 印 mismatch
  python tools/regen_rag.py --check --owner 1        # 限定 owner
  python tools/regen_rag.py --paper <uuid> --owner 1 # 重 embed 單一 paper
  python tools/regen_rag.py --all                    # 全部 paper 重 embed
  python tools/regen_rag.py --all --force            # 不檢查 mismatch、強制重 embed
  python tools/regen_rag.py --all --dry-run          # 不實際執行、印會做什麼
  python tools/regen_rag.py --init                   # 一次性從 vectors/ FAISS docstore 反向導入 paper_chunks
"""

import argparse, json, logging, sys
from pathlib import Path
from typing import Optional

from processor.rag_processor import write_index_meta_json, CHUNK_FILTER_VERSION  # 修正 4


def cmd_check(owner_id: Optional[int] = None) -> int:
    """掃 paper_chunks + 比對 vectors/index_meta.json vs 當前 settings、印 mismatch。

    輸出格式：
      [OK]       owner=1 paper=DeHunt_CTO_Tzung-Yuan_Lee  model=gemini-embedding-2/768
      [MISMATCH] owner=1 paper=hvdc_slides                stored=gemini-embedding-2/768 current=gemini-embedding-3/768
      [MISSING]  owner=1 paper=old_paper_xyz              no_index_meta.json

    Exit code：mismatch_count（給 CI 用）
    """
    from settings import EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS
    import paper_manager
    papers = paper_manager.list_papers_with_chunks(owner_id=owner_id)
    mismatches = 0
    for p in papers:
        if p['embedding_model'] != EMBEDDING_MODEL_NAME or p['output_dimensions'] != EMBEDDING_OUTPUT_DIMENSIONS:
            print(f"[MISMATCH] owner={p['owner_id']} paper={p['paper_uuid']} "
                  f"stored={p['embedding_model']}/{p['output_dimensions']} "
                  f"current={EMBEDDING_MODEL_NAME}/{EMBEDDING_OUTPUT_DIMENSIONS}")
            mismatches += 1
        else:
            print(f"[OK] owner={p['owner_id']} paper={p['paper_uuid']} "
                  f"model={p['embedding_model']}/{p['output_dimensions']}")
    return mismatches


def cmd_regen(paper_db_id, owner_id, paper_uuid, force=False, dry_run=False):
    """重 embed 單一 paper：從 paper_chunks 讀 → 新 model embed → 覆寫 vectors/。

    步驟:
    1. 從 paper_chunks 讀 (raw_text, metadata_json, chunk_index)
    2. 若非 force：比對 stored.embedding_model vs current；一致則 skip
    3. 重建 LangChain Document（page_content=raw_text、metadata=metadata_json 反序列化）
    4. FAISS.from_documents(...) → save_local（覆寫舊 vectors/）
    5. paper_manager.replace_paper_chunks(...) 更新 embedding_model / output_dimensions
    6. 寫新 index_meta.json
    """
    if dry_run:
        print(f"[DRY-RUN] would regen paper {paper_uuid} (owner={owner_id})")
        return
    from langchain.docstore.document import Document
    from langchain_community.vectorstores.faiss import FAISS
    from langchain_community.vectorstores.utils import DistanceStrategy
    from config import EmbeddingModel
    from settings import EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS, _BASE_DIR
    import paper_manager

    docs = []
    rows_for_db = []
    for c in paper_manager.iter_paper_chunks(paper_db_id):
        if not force and c['embedding_model'] == EMBEDDING_MODEL_NAME and c['output_dimensions'] == EMBEDDING_OUTPUT_DIMENSIONS:
            print(f"[SKIP] paper {paper_uuid} model match (use --force to override)")
            return
        meta = json.loads(c['metadata_json']) if c['metadata_json'] else {}
        docs.append(Document(page_content=c['raw_text'], metadata=meta))
        rows_for_db.append({
            **c,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "output_dimensions": EMBEDDING_OUTPUT_DIMENSIONS,
        })

    embedder = EmbeddingModel.get_instance()
    vs = FAISS.from_documents(
        documents=docs, embedding=embedder,
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
    )
    # 注意：實體目錄是 vectors/（修正 1：grep 證實）
    output_dir = Path(_BASE_DIR) / 'output' / str(owner_id) / paper_uuid / 'vectors'
    output_dir.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(output_dir))

    paper_manager.replace_paper_chunks(paper_db_id, rows_for_db)
    write_index_meta_json(output_dir, len(docs))  # 修正 4
    print(f"[OK] paper {paper_uuid} re-embedded ({len(docs)} chunks)")


def cmd_all(force=False, dry_run=False, owner_id: Optional[int] = None):
    """對所有 paper（或 owner 過濾後）執行 cmd_regen。"""
    import paper_manager
    for p in paper_manager.list_papers_with_chunks(owner_id=owner_id):
        cmd_regen(p['paper_db_id'], p['owner_id'], p['paper_uuid'],
                  force=force, dry_run=dry_run)


def cmd_init(owner_id: Optional[int] = None, dry_run: bool = False):
    """一次性把既有 paper 從 vectors/ FAISS docstore 反向導入 paper_chunks。

    步驟（依 plan §3.4 修正 6）:
    1. 掃 output/<owner>/<paper_uuid>/vectors/ 找所有有 index.faiss 的 paper
    2. 為每個 paper 檢查 paper_chunks 表是否已有 rows（避免重複導入）
    3. 用 FAISS.load_local() 讀出 docstore（含原 Document.page_content + metadata）
    4. paper_manager.replace_paper_chunks(...) 寫入
    5. 寫新 index_meta.json（用當前 settings 標記）

    注意：
    - doc_type 在 init 場景已不可考（FAISS docstore 無此資訊）、寫 ''；
      未來如需要、可人工 UPDATE paper_chunks.doc_type 或 cross-join papers 表的 doc_type 欄位
    - owner_id 從目錄結構推得（output/<owner_id>/<paper_uuid>/）
    """
    import logging
    from langchain_community.vectorstores.faiss import FAISS
    from config import EmbeddingModel
    from settings import EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS, _BASE_DIR
    import paper_manager

    logger = logging.getLogger("regen_rag.init")
    output_root = Path(_BASE_DIR) / 'output'
    embedder = EmbeddingModel.get_instance() if not dry_run else None

    for vectors_dir in sorted(output_root.glob('*/*/vectors')):
        if not (vectors_dir / 'index.faiss').exists():
            continue
        owner_dir_name = vectors_dir.parent.parent.name
        paper_uuid = vectors_dir.parent.name
        try:
            owner_id_int = int(owner_dir_name)
        except ValueError:
            logger.warning(f"[init] skip non-int owner dir: {owner_dir_name}")
            continue
        if owner_id is not None and owner_id_int != owner_id:
            continue

        paper_db_id = paper_manager.get_paper_db_id(owner_id_int, paper_uuid)
        if paper_db_id is None:
            logger.warning(f"[init] skip orphan {vectors_dir} (no paper in DB)")
            continue

        # 若已有 paper_chunks、跳過（避免覆寫 C2 ship 後寫入的真實資料）
        existing = list(paper_manager.iter_paper_chunks(paper_db_id))
        if existing:
            logger.info(
                f"[init] skip {paper_uuid} (already has {len(existing)} chunks)"
            )
            continue

        if dry_run:
            print(f"[DRY-RUN] would init {paper_uuid} (owner={owner_id_int})")
            continue

        # 從 FAISS docstore 反向取
        vs = FAISS.load_local(
            str(vectors_dir), embedder, allow_dangerous_deserialization=True
        )
        # docstore 是 InMemoryDocstore、._dict 內含 doc_id → Document 對應
        rows = []
        for i, (_doc_id, doc) in enumerate(vs.docstore._dict.items()):
            chunk_key = (doc.metadata or {}).get('Header', '') or f"chunk_{i}"
            rows.append({
                "chunk_index": i,
                "chunk_key": chunk_key[:255],
                "raw_text": doc.page_content or '',
                "translated_text": None,
                "doc_type": "",   # init 場景 doc_type 已不可考（風險表已收錄、Q16 對應）
                "metadata_json": json.dumps(doc.metadata or {}, ensure_ascii=False),
                "embedding_model": EMBEDDING_MODEL_NAME,
                "output_dimensions": EMBEDDING_OUTPUT_DIMENSIONS,
                "chunk_filter_version": CHUNK_FILTER_VERSION,
            })
        paper_manager.replace_paper_chunks(paper_db_id, rows)
        write_index_meta_json(vectors_dir, len(rows))  # 修正 4
        print(f"[OK] init {paper_uuid} ({len(rows)} chunks reverse-imported)")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--paper', metavar='UUID', help='重 embed 單一 paper')
    parser.add_argument('--all', action='store_true', help='全部重 embed')
    parser.add_argument('--owner', type=int, help='限定 owner_id')
    parser.add_argument('--force', action='store_true', help='略過 mismatch 檢查')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--init', action='store_true',
                        help='從 FAISS docstore 反向導入 paper_chunks（修正 6）')
    args = parser.parse_args()

    if args.check:
        sys.exit(cmd_check(owner_id=args.owner))
    elif args.init:
        cmd_init(owner_id=args.owner, dry_run=args.dry_run)
    elif args.paper:
        # 需要轉 paper_uuid → paper_db_id（用既有 paper_manager.get_paper_db_id、修正 5）
        import paper_manager
        if args.owner is None:
            sys.exit("--paper 需搭配 --owner <id>")
        pid = paper_manager.get_paper_db_id(args.owner, args.paper)
        if pid is None:
            sys.exit(f"paper not found: owner={args.owner} uuid={args.paper}")
        cmd_regen(pid, args.owner, args.paper, force=args.force, dry_run=args.dry_run)
    elif args.all:
        cmd_all(force=args.force, dry_run=args.dry_run, owner_id=args.owner)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    main()
```

### §3.6 子改動 D — `OUTPUT_DIR` env 化（**修正 7**、依 db_analysis §5.2、推薦併進 C1）

**目標與邏輯**：把 `web_server.py:77 OUTPUT_DIR = BASE_DIR / "output"` 寫死改為 env override、Docker / K8s 部署時可用 `OUTPUT_DIR=/app/storage/output -v /host:/app/storage` 集中管理。對齊 MODEL-1+2 / MODEL-3 / MODEL-9 既有 env 化風格（`EMBEDDING_*` / `TILING_*` / `GEMINI_*_TIMEOUT`）。

**grep 證據（修正 7）**：

```bash
$ grep -nE "OUTPUT_DIR|BASE_DIR.*output" web_server.py settings.py | head
web_server.py:76:BASE_DIR = Path(__file__).parent
web_server.py:77:OUTPUT_DIR = BASE_DIR / "output"           # ← 寫死、需 env 化
web_server.py:78:OUTPUT_DIR.mkdir(exist_ok=True)
# ... web_server.py 內 20+ 處 OUTPUT_DIR 引用、全部沿用、不動
```

**檔案改動**（3 處）：

1. **`settings.py`**（在既有 `TILING_*` / `WATERMARK_*` 等 env 區附近、L53 後或 L67 前）：

```python
# Phase 4.7? MODEL-8（依 db_analysis §5.2）：OUTPUT_DIR env override
# Docker / K8s 部署時可用 OUTPUT_DIR=/app/storage/output 集中管理
# 預設值保持 backward compat、現有路徑解析 100% 不變
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(_BASE_DIR / "output")))
```

2. **`web_server.py:77-78`**（只改 2 行、不動其他 20+ 處引用）：

```python
# 既有 L76-78（寫死）：
# BASE_DIR = Path(__file__).parent
# OUTPUT_DIR = BASE_DIR / "output"
# OUTPUT_DIR.mkdir(exist_ok=True)

# 修正後（L76 保留、L77-78 替換）：
BASE_DIR = Path(__file__).parent
from settings import OUTPUT_DIR   # MODEL-8 C1（修正 7、依 db_analysis §5.2）
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

3. **`tools/regen_rag.py`**（C3 內、§3.4 既有寫法 `Path(_BASE_DIR) / 'output' / ...` 改為 import OUTPUT_DIR）：

```python
# 既有 §3.4 cmd_regen / cmd_init 內：
# from settings import _BASE_DIR
# output_dir = Path(_BASE_DIR) / 'output' / str(owner_id) / paper_uuid / 'vectors'

# 修正 7 統一：
from settings import OUTPUT_DIR
output_dir = OUTPUT_DIR / str(owner_id) / paper_uuid / 'vectors'
# cmd_init 內同樣：
output_root = OUTPUT_DIR
for vectors_dir in sorted(output_root.glob('*/*/vectors')):
    ...
```

**為什麼這是低風險**：
- `os.getenv("OUTPUT_DIR", str(_BASE_DIR / "output"))` 預設值不變、現有所有路徑解析 100% backward compat
- web_server.py 既有 20+ 處 `paper_manager.paper_dir(OUTPUT_DIR, ...)` / `OUTPUT_DIR / "papers_index.json"` 等引用**完全不動**
- Docker 化部署只需 `-e OUTPUT_DIR=/app/storage/output -v /host:/app/storage`、零 code 修改

**併進 C1 還是拆 C4？**：見 §8 Q17、推薦**併 C1**（settings.py 改動同一檔、降低 commit 數）。

---

### §3.5 落地策略（拆 commit）

| 子項 | 範圍 | 工時 | 依賴 |
|---|---|---|---|
| **C1** | `models.py` 加 `PaperChunk` ORM + `Paper.chunks` relationship + `paper_manager.py` 加 3 個 DAL helper（`replace_paper_chunks` / `iter_paper_chunks` / `list_papers_with_chunks`、**不重新加** `get_paper_db_id`） + `processor/rag_processor.py` 加 `CHUNK_FILTER_VERSION` 常數 + **`settings.py` 加 `OUTPUT_DIR` env**（修正 7、依 db_analysis §5.2） + **`web_server.py:77-78` 改 `from settings import OUTPUT_DIR`**（其他 20+ 處引用不動） + 5 個 pytest（`tests/test_paper_chunks_schema.py`、含 `test_output_dir_env_override`） | ~3.5 hr | 無 |
| **C2** | `processor/rag_processor.py` 加 module-level `write_index_meta_json` + `RagProcessor._write_paper_chunks_to_db` + `process` / `_create_vector_store` 加 `paper_db_id` 參數 + `pipeline_core.py::_stage_rag` 2-3 行 `paper_db_id` 注入（**修正 2**、不動 `web_server.py`） + 5 個 pytest（`tests/test_rag_processor_chunks_write.py`） | ~3 hr | C1 |
| **C3** | `tools/regen_rag.py` 新檔（`--check / --paper / --all / --force / --dry-run / --init`、**修正 6** cmd_init 完整 pseudo-code） + 7 個 pytest（`tests/test_regen_rag_cli.py`、含 init 反向導入） | ~4 hr | C1 + C2 |

**推薦 3 commits**——跟 MODEL-1+2 / MODEL-3 拆分模式一致、易 revert。

---

## 4. 變動風險與相容性評估

| 風險 | 等級 | 緩解 |
|---|---|---|
| 既有 paper 沒寫到 paper_chunks（C1 / C2 ship 前的舊資料） | 🟡 中 | C3 `--init` 從 FAISS docstore 反向導入；既有 paper 若沒 `paper_chunks` rows、`--check` 不列出（`list_papers_with_chunks` 用 JOIN、無 chunks 直接被過濾）、不會崩潰 |
| metadata_json schema 變動破壞 backward compat | 🔴 高 | `chunk_filter_version` 字串標記版本、舊版本可獨立路徑處理；CLI `--init` 重新落地 |
| SQLite 批次 INSERT 效能 | 🟢 低 | `SQLAlchemy 2.0 insert(PaperChunk)` 批量、單 paper < 100 chunks 預期 < 50ms（依 db_analysis §4 效能基準） |
| paper_chunks 表大小膨脹（書籍場景） | 🟡 中 | 「我與你」估計 ~300-500 chunks、SQLite < 5 MB / 書、長期 > 1M chunks 才考慮分表；本期不做 |
| 跟 paper_manager / 既有 SQL 風格衝突 | 🟢 低 | 完全沿用 `with db.SessionLocal() as s: ... s.commit()` pattern（樣本：`append_chat_message` L380-393） |
| FAISS 重建後 metadata 不一致 | 🟡 中 | regen 從 paper_chunks 反序列化 `metadata_json` 重建 Document.metadata、確保 1:1 對應 |
| `--all` 跑書籍時間過長 | 🟢 低 | `--dry-run` 預估時間、依 embedding API 速率（單 paper < 30 秒 / 書籍 < 2 分） |
| `paper_db_id` 注入鏈路（pipeline_core → rag_processor、修正 2） | 🟢 低 | grep 確認 `pipeline_core._stage_rag` 內已有完整資訊（`self._owner_id` + `self.paper_info['paper_id']`）、無需動 `web_server.py`；`get_paper_db_id` 已存在（修正 5） |
| 寫入 paper_chunks 失敗連帶 FAISS 失敗 | 🟢 低 | C2 內 `try/except` 包住 paper_chunks 寫入、不阻塞 FAISS 主流程；錯誤 log + 後續可 `--init` 修補 |
| Concurrent web_server + regen_rag 寫衝突 | 🟢 低 | 既有 `PRAGMA busy_timeout=5000` + WAL mode、SQLite 已防 `database is locked`；regen_rag 跑時建議 baron 先停 web_server（不強制） |
| `cmd_init` 從 FAISS docstore 反向取 doc_type 為空（修正 6） | 🟢 低 | 可接受、`doc_type` 在 RAG 檢索層不直接使用；未來如需要、可手寫 SQL 從 `papers.doc_type` 跨表 UPDATE 補齊（Q16） |
| `MarkdownHeaderTextSplitter` 未來輸出 metadata 變動 | 🟡 中 | 本期 `chunk_key` 從 `metadata.get('Header')` 取、若 splitter 改版需同步調整；用 `chunk_filter_version` 鎖版本可降低衝擊 |
| `OUTPUT_DIR` env 化破壞既有 path resolve（修正 7） | 🟢 低 | 預設值 `os.getenv("OUTPUT_DIR", str(_BASE_DIR / "output"))` 不變、現有所有路徑解析 100% backward compat；web_server.py 內 20+ 處既有引用全部不動、只改 import 1 行 |
| 未來 K8s 多 Pod 跨網路硬碟（NFS/EFS）造成 SQLite 死鎖（修正 8） | 🟢 低 | 依 db_analysis §5.3、既有 `db.py:36-51` SQLite PRAGMA 已隔離在 `if not _IS_SQLITE` 內、`PaperChunk` ORM 採標準 SQLAlchemy 2.0、`DATABASE_URL=postgresql://...` 一鍵切換；本期不做 Pg 切換驗證（Q18）、設計兼容 |

---

## 5. 測試計畫與端到端（E2E）驗證計畫

### §5.1 自動化單元測試

**既有測試 baseline**：

```bash
$ venv/bin/pytest tests/ -q
208 passed, 3 skipped     # MODEL-3 B3 後現況
```

**C1 新增** — `tests/test_paper_chunks_schema.py`（5 個 test）：

| Test | 驗證 |
|---|---|
| `test_paper_chunks_table_created` | `db.init_db()` 後 `paper_chunks` 表存在、欄位完整（**修正 3**：無 tiling_method 欄位） |
| `test_paper_chunks_foreign_key_cascade` | 刪 Paper → 對應 PaperChunk 全部刪除（FK + WAL pragma 物理生效） |
| `test_paper_chunks_unique_constraint` | 同 paper_id + chunk_index 重複 INSERT 拋 `IntegrityError` |
| `test_replace_paper_chunks_overwrite` | `replace_paper_chunks(pid, [a, b])` → 再呼叫 `replace_paper_chunks(pid, [c])` → 表內只剩 c |
| `test_iter_paper_chunks_order` | `iter_paper_chunks` 依 `chunk_index` 升序回 |

> 注：`get_paper_db_id` 已存在於 paper_manager（修正 5）、且舊有功能已隱含覆蓋（既有 `paper_manager.py::append_chat_message` 等路徑依賴）、本期不重複新增 test。

**C2 新增** — `tests/test_rag_processor_chunks_write.py`（5 個 test、**修正 4** mock 對象改 module-level）：

| Test | 驗證 |
|---|---|
| `test_chunks_written_after_create_vector_store` | mock `paper_db_id` 跑完 `_create_vector_store` → `paper_chunks` 有對應 rows（**修正 3**：rows 無 tiling_method 欄位） |
| `test_chunks_overwrite_on_rerun` | 同 paper 跑兩次 → 第二次 rows 覆寫第一次（不累積） |
| `test_index_meta_json_written` | `vectors/index_meta.json` 存在、含 `embedding_model` / `output_dimensions` / `chunk_filter_version`（**修正 4** mock 對象：`processor.rag_processor.write_index_meta_json`、不是 method） |
| `test_chunk_metadata_preserved` | 從 `paper_chunks.metadata_json` 反序列化 == 原 `doc.metadata`（1:1 對應、含 `Header` 鍵） |
| `test_paper_db_id_none_skips_write_with_warning` | `paper_db_id=None` 時主流程不崩、log warning |

**C3 新增** — `tests/test_regen_rag_cli.py`（7 個 test、**修正 6** 加 init 反向導入）：

| Test | 驗證 |
|---|---|
| `test_check_no_mismatch` | settings 沒改、`--check` exit code = 0 |
| `test_check_mismatch_detected` | monkeypatch EMBEDDING_MODEL_NAME 後、`--check` 印 `[MISMATCH]` |
| `test_regen_single_paper` | `--paper <uuid> --owner 1` → vectors/ 覆寫、paper_chunks rows.embedding_model 更新 |
| `test_regen_all` | `--all` 多 paper 批次成功 |
| `test_regen_force_skips_mismatch_check` | settings 沒變、`--force` 仍重 embed |
| `test_regen_dry_run` | `--dry-run` 印「會做什麼」、不實際寫入 FAISS / DB |
| `test_cmd_init_reverse_import_from_faiss` | **修正 6**：fixture 建好 FAISS vectors/ + 空 paper_chunks → `--init` 後 paper_chunks 有對應 rows、`raw_text` == FAISS docstore 內 page_content |

### §5.2 手動 E2E

```bash
# 1. C2 ship 後、跑完一份 paper、確認 paper_chunks 有 row
venv/bin/python -c "
import paper_manager
pid = paper_manager.get_paper_db_id(1, 'DeHunt_CTO_Tzung-Yuan_Lee')
chunks = list(paper_manager.iter_paper_chunks(pid))
print(f'chunks={len(chunks)}, first_raw={chunks[0][\"raw_text\"][:50]}')
"

# 2. 看 index_meta.json（注意：路徑是 vectors/、修正 1）
cat output/1/DeHunt_CTO_Tzung-Yuan_Lee/vectors/index_meta.json | jq

# 3. 跑 check（應該回 no mismatch）
venv/bin/python tools/regen_rag.py --check
# 預期 exit 0

# 4. 模擬升版：改 env → check
export EMBEDDING_MODEL_NAME="gemini-embedding-3"   # 假設
venv/bin/python tools/regen_rag.py --check
# 預期：所有 paper [MISMATCH]、exit code = paper_count

# 5. dry-run 全部
unset EMBEDDING_MODEL_NAME
venv/bin/python tools/regen_rag.py --all --dry-run

# 6. 真正 regen 一份書籍、計時
time venv/bin/python tools/regen_rag.py --paper "我與你_Martin_Buber" --owner 1 --force
# 預期：< 2 分 / 書（vs 既有重 PDF 30-60 分）

# 7. （C3 ship 後一次性）反向導入既有 paper（修正 6）
venv/bin/python tools/regen_rag.py --init
venv/bin/python tools/regen_rag.py --check   # 預期：所有 [OK]、無 missing
```

### §5.3 完整回歸

```bash
$ venv/bin/pytest tests/ -q
# 預期：208 baseline + 5 (C1) + 5 (C2) + 7 (C3) = 225 passed, 3 skipped
```

---

## 6. 不可做 / 不可動清單

明確劃定修改邊界、防止修改邏輯溢出：

- [ ] `pipeline_core.py` **除 `_stage_rag` 內 2-3 行加 `paper_db_id` 注入外**（修正 2、§3.3.1）、其他 stage / 簽名 / `self.paper_info` / `self._owner_id` 等不動
- [ ] **`web_server.py`：僅改 L77-78 共 2 行**（`OUTPUT_DIR` 改為 `from settings import OUTPUT_DIR`、`OUTPUT_DIR.mkdir(parents=True, exist_ok=True)`；**修正 7** 依 db_analysis §5.2）；**其他 20+ 處 `OUTPUT_DIR` 引用全部不動**；**修正 2 強制不動 `paper_db_id` 注入路徑**：grep 證實 pipeline_core 自己能拿到 `owner_id + paper_uuid`、不需 web_server 層注入 `paper_db_id`
- [ ] **`db.py` 既有 PRAGMA 設計：未動**（已 Pg-Ready、**修正 8** 依 db_analysis §5.3 確認、`if not _IS_SQLITE` 防禦性設計沿用）
- [ ] `processor/*` 除 `rag_processor.py` 外：未動
- [ ] `config.py` / `EmbeddingModel`：未動（MODEL-1+2 已 ship）
- [ ] `llm/*`（MODEL-9）：未動
- [ ] `static/*` / DB schema migration tool：未動（純 `Base.metadata.create_all`、無 Alembic）
- [ ] 既有 `paper_manager.py` 其他 method（`add_paper` / `delete_paper` / `load_chat_history` / **`get_paper_db_id`**（修正 5：已存在、不重做） 等）：未動
- [ ] `tiling_processor` / `md_restore`：未動（MODEL-3 已 ship）
- [ ] 既有 `vectors/` 內 FAISS 二進位檔（`index.faiss` / `index.pkl`）：未動（純新增 `index_meta.json`）
- [ ] `models.py` 既有 4 張表（User / Folder / Paper / Conversation）的欄位與關係：100% 不動（依 db_analysis §1）
- [ ] TODO 內其他條目：未動（本 task 完成後另寫 prompt 把 MODEL-8 從 ⬜ 改 🔵 plan 中）
- [ ] 既有 plan / 執行 / hotfix 報告：未動（**包含 MODEL-1+2 §4.4 / MODEL-3 B3 §7.4 內 `vector_store/` 錯誤路徑、修正 1 只在本 plan §1.4 註記、不去改它們**）
- [ ] commit / push：未動（baron 手動執行）
- [ ] PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / templates/*：未動
- ✅ 可動範圍（本 task 3 commits 內依序落地）:
  - **C1**：`models.py`（加 `PaperChunk` + `Paper.chunks` relationship）/ `paper_manager.py`（加 3 個 helper、**不重做** `get_paper_db_id`）/ `processor/rag_processor.py`（加 `CHUNK_FILTER_VERSION` 常數）/ **`settings.py`**（加 `OUTPUT_DIR` env、修正 7）/ **`web_server.py:77-78`**（2 行 import 改、修正 7）/ `tests/test_paper_chunks_schema.py`（新增、含 OUTPUT_DIR test）
  - **C2**：`processor/rag_processor.py`（加 module-level `write_index_meta_json` + method `_write_paper_chunks_to_db` + `process` / `_create_vector_store` 加 `paper_db_id` 參數）/ `pipeline_core.py::_stage_rag`（加 2-3 行 `paper_db_id` 注入、不動其他 stage）/ `tests/test_rag_processor_chunks_write.py`（新增）
  - **C3**：`tools/regen_rag.py`（新檔、含 cmd_init 修正 6 完整 pseudo-code）/ `tests/test_regen_rag_cli.py`（新增）
  - 新增 plan / 執行報告

---

## 7. 推薦 Commit 拆分與順序

| 序號 | 預期變動內容 | 預估工時 |
|---|---|---|
| **MODEL-8 C1** | schema：`PaperChunk` ORM + 3 個 DAL helper（不重做 `get_paper_db_id`、修正 5） + `CHUNK_FILTER_VERSION` 常數 + **`OUTPUT_DIR` env**（settings + web_server 2 行、修正 7） + 5 個 pytest | ~3.5 hr |
| **MODEL-8 C2** | pipeline 寫入：module-level `write_index_meta_json`（修正 4） + `_write_paper_chunks_to_db` + `_stage_rag` `paper_db_id` 注入（修正 2、不動 web_server）+ 5 個 pytest | ~3 hr |
| **MODEL-8 C3** | CLI：`tools/regen_rag.py` 6 子命令（含 cmd_init 修正 6 完整 pseudo-code） + 7 個 pytest | ~4 hr |

**依賴順序**：C1 → C2（C2 用 C1 的 helper）→ C3（C3 用 C1 + C2 兩者）。

**Backfill 一次性 SOP（C3 ship 後、路徑全用 vectors/、修正 1）**：

```bash
cd ~/mad-professor-public
git pull

# 1. 一次性導入既有 paper（從 FAISS docstore 反向、修正 6）
venv/bin/python tools/regen_rag.py --init

# 2. 驗證
venv/bin/python tools/regen_rag.py --check
# 預期：所有 paper [OK]、無 [MISSING]

# 3. 未來升 embedding 時、直接 --all
# export EMBEDDING_MODEL_NAME="gemini-embedding-3"
# venv/bin/python tools/regen_rag.py --all
```

**Docker / K8s 部署 SOP（修正 7 ship 後、零 code 修改）**：

```bash
# Docker 部署一鍵掛載（依 db_analysis §5.2）
docker run -d \
  -e DATABASE_URL=sqlite:////app/storage/mad-professor.db \
  -e OUTPUT_DIR=/app/storage/output \
  -v /host/persistent:/app/storage \
  mad-professor:latest

# 未來如要 K8s 多 Pod、切 Pg（依 db_analysis §5.3、修正 8、零 code 修改）：
# -e DATABASE_URL=postgresql://user:pass@pg-host:5432/madprof
```

---

## 8. 開放問題 (Open Questions)

> [!WARNING]
> 以下為尚未定案 / 需要與 baron 對齊的決策點：

| # | 問題 | 推薦答案 |
|---|---|---|
| **Q1** | paper_chunks 用獨立 DB 還是合進既有 `mad-professor.db`？ | **合進既有**——對齊 `papers` / `conversations`、用 FK 維護一致性；依 db_analysis §1 採納為「安全增量擴充」。 |
| **Q2** | embedding_model 比對是否含 `output_dimensions`？ | **要**——MRL 降維 768 vs 1536 是不同向量空間、不可混用。 |
| **Q3** | `chunk_filter_version` 用 string 還是 int？ | **string**（如 `'B2-2026-05-22'`）便於 debug、可順帶日期錨點。 |
| **Q4** | C1 / C2 ship 後既有 paper 怎麼處理？ | **C3 加 `--init` 補完**——從 vectors/ FAISS docstore 反向取 page_content + metadata、INSERT 進 paper_chunks（修正 6 pseudo-code 完整）。 |
| **Q5** | `regen_rag --all` 是否要併行多個 paper？ | **單緒**——避免併發寫 SQLite 衝突（雖然 WAL 支援、但 embedding API rate limit 是真瓶頸）；< 10 份 paper 序列也快。 |
| **Q6** | regen_rag 是否要支援 `--diff` 看新舊 embedding 差異？ | **不做**——超出範圍、未來新 task（RAG-3 score 校準累積數據後再評估）。 |
| **Q7** | `metadata_json` 是否要包含 vector？ | **不包含**——vector 在 FAISS、保 paper_chunks 表瘦；只存「重建 Document.metadata 必要欄位」。 |
| **Q8** | 拆 3 commits（C1/C2/C3）還是合併？ | **拆 3**——跟 MODEL-1+2 / MODEL-3 模式對齊、易 revert、CI 失敗影響面小。 |
| **Q9** | db_analysis_and_future_extension.md §3.1 的 `paper_chunks` 設計跟本 plan 一致嗎？ | **一致 + 微調**：db_analysis §3.1 是 schema baseline、本 plan 加 3 欄版本偵測（`chunk_index` / `embedding_model+output_dimensions` / `chunk_filter_version`）+ **移除 `tiling_method`**（修正 3）；無衝突。 |
| **Q10** | 是否要加 `paper_chunks_versions` 表記錄歷次 embed？ | **不做**——只保最新版、舊版直接覆寫（`replace_paper_chunks` 內 DELETE + 批 INSERT）；省空間、簡化。 |
| **Q11** | `tools/regen_rag.py` 是否需要 `--restore` 從 paper_chunks 恢復 vector_store？ | **不需要獨立 flag**——`--paper <uuid> --force` 已等同此語意；如要批次、`--all --force`。 |
| **Q12** | `_write_paper_chunks_to_db` 失敗時是否 rollback FAISS 寫入？ | **不 rollback**——FAISS 寫入是不可逆的本地檔；用 `try/except` 包 SQLite 寫入、失敗 log warning + 後續 `--init` 修補；保證主流程不阻塞。 |
| **Q13** | `paper_db_id=None` 走哪條路徑？（測試環境 / 既有 resume pipeline） | **優雅降級**——log warning 跳過 paper_chunks 寫入、FAISS 正常 save；CLI `--init` 可事後補完。 |
| **Q14** | 是否要把 `translated_text` 一併寫入 paper_chunks？ | **C2 階段先不寫**（值留 NULL）——既有 md chunk 為 zh-only markdown、translated_text 來源在 `*_tiled.json` 內、需另外的 join 邏輯；待未來 translation cache 需求出現時 C4 / C5 再補（db_analysis §3.4 提到的成本防禦）。 |
| **Q15** | `tiling_method` 欄位移除（修正 3）是否影響未來 RAG-X？ | **不影響**——`tiling_method` 在 RAG 檢索層不參與 score 計算、純為 tiling 階段 debug 標籤；未來如要追溯、走 `metadata_json` 內擴欄位或 `chunk_filter_version` snapshot 對應到 tiling config（`tiling_config_signature` 已寫進 `index_meta.json`、可間接還原）。 |
| **Q16** | `cmd_init` 反向導入時 `doc_type` 設為空字串、是否日後補齊？ | **可選擇手補**——`doc_type` 在 `papers` 表已有（`models.py` L105 `Paper.doc_type`）；如需要、可手寫 1 句 SQL `UPDATE paper_chunks SET doc_type = (SELECT doc_type FROM papers WHERE papers.id = paper_chunks.paper_id) WHERE doc_type = ''` 跨表補齊；本期不做。 |
| **Q17** | `OUTPUT_DIR` env 化（修正 7）拆獨立 C4 還是併進 C1？ | **併 C1**——settings.py 同檔擴充、`web_server.py:77-78` 改 2 行、無 schema 依賴、無業務邏輯影響；降低 commit 數、CI 一次驗證；C1 工時從 ~3 hr 微升至 ~3.5 hr 可接受。若 baron 偏好獨立、可拆 C4（純 env 化 + 1 個 test、~30 min）。 |
| **Q18** | 是否要在本期 plan 內做 PostgreSQL 連線測試（驗證 Pg-Ready）？ | **不做**——超出 MODEL-8 範圍、純安撫註記；既有 `db.py:36-51` `if not _IS_SQLITE` 隔離已是足夠防線；未來真要 K8s 多 Pod 時開新 task 處理（含 Pg docker-compose fixture / pytest CI matrix / 跨 DB ORM 行為差異測試）。本期僅在 §1.0 footnote + §4 風險表 + 附錄 A 做設計兼容性宣告。 |

---

## 9. 推薦執行順序

1. baron 過目本 plan + Q1-Q18 推薦答案 + 8 個修正納入結果（含 Docker 化 2 個建議）
2. C1 commit（schema、~3 hr）
3. C2 commit（rag_processor 寫入 + pipeline_core 注入、~3 hr）
4. C3 commit（CLI、~4 hr）
5. baron OrcStack 端 backfill：
   - 跑 `--init` 把既有 paper 導入 paper_chunks（一次性、未來不需重做、依修正 6 SOP）
   - 跑 `--check` 確認所有 paper 都符合當前 settings
6. **未來價值體現**：MODEL-3 / RAG-3 / 升 embedding model 時、直接 `regen_rag --all`、< 5 分鐘搞定 backfill
7. **Docker 化部署（修正 7、依 db_analysis §5.2）**：C1 ship 後即可、`docker run -e OUTPUT_DIR=/app/storage/output -e DATABASE_URL=sqlite:////app/storage/mad-professor.db -v /host:/app/storage`、**零 code 修改**
8. **未來 K8s 多 Pod（修正 8、依 db_analysis §5.3）**：`-e DATABASE_URL=postgresql://...` 即可、本期不做切換驗證（Q18）；MODEL-8 ORM 設計兼容

---

## 附錄 A：與既有 db_analysis_and_future_extension.md §3-4 對齊

| db_analysis 段落 | 本 plan 對應段落 | 採納情況 |
|---|---|---|
| §1 結論「不是大改」 | §1.0 採納為基準 | ✅ 完全採納 |
| §3.1 PaperChunk Schema | §3.1 採納為基準 + 加 3 欄 + 移除 `tiling_method`（修正 3） | ✅ 採納 + 擴充 + 微調 |
| §3.2 0ms 免 PDF 重析（效益 A） | §1.4 / §3.0 引用 | ✅ 本 plan 落地此效益 |
| §3.3 BM25 + Vector RRF（效益 B） | 未實作 | ⏭️ 未來 RAG-X task、本 plan 不做 |
| §3.4 Translation cache（效益 C） | 預留欄位 `translated_text`、Q14 標明 | ⏭️ 未來 C4/C5、本 plan 不做（值留 NULL） |
| §4 步驟 1 Schema 擴充 | C1 | ✅ 完全對齊 |
| §4 步驟 2 Pipeline 寫入 | C2 | ✅ 完全對齊（修正 2：注入鏈路明確化、不動 web_server） |
| §4 步驟 3 regen_rag.py CLI | C3 | ✅ 完全對齊（修正 6：cmd_init pseudo-code 完整化） |
| §4 技術決策 Bulk Insert | §1.0 表格 / §3.1 程式碼採納 `insert(PaperChunk)` 批量 | ✅ 完全採納 |
| §4 技術決策 passive_deletes=True | §3.1 ORM 採納 | ✅ 完全採納 |
| §5.1 Volume 掛載與配置化（DB 持久化） | 未實作 | ⏭️ **不採納**——純 DevOps / Docker Compose 配置議題、不涉及 source code；baron 部署時依 §7 SOP 自行掛載 |
| §5.2 OUTPUT_DIR env 化（修正 7） | §3.6 新增子改動 D + C1 範圍 | ✅ **採納**（併 C1、Q17） |
| §5.3 Pg-Ready 安撫註記（修正 8） | §1.0 footnote / §4 風險表 / Q18 | ✅ **採納為宣告**（無 code 改動、純設計兼容性確認） |
| §5.4 MinerU SCP→HTTP（MODEL-10） | 未實作 | ⏭️ **不採納**——MODEL-10 為獨立 task（TODO 內候選項 🔵 低優先）、本期不重複；範圍涉及 MinerU 端改造、超出 MODEL-8 |

---

## 附錄 B：修正前後對照表（給 baron review 用）

| 修正 # | 項目 | 修正前 | 修正後 |
|---|---|---|---|
| 1 | 實體路徑用詞 | `vector_store/`（部份段落混用） | 全 plan 統一 `vectors/`（grep `pipeline_core.py:204` 證實）；§1.4 explicit note 舊 SOP 路徑錯誤 |
| 2 | `paper_db_id` 注入鏈路 | 不明、寫「上游注入」 | §3.3.1 詳述：`pipeline_core._stage_rag` 內部呼叫 `paper_manager.get_paper_db_id(self._owner_id, self.paper_info['paper_id'])`、**不動 web_server** |
| 3 | `tiling_method` 欄位 | ORM 含此欄位 + 寫入邏輯試圖從 `d.metadata` 取 | **完全移除**（grep 證實 `MarkdownHeaderTextSplitter` metadata 只含 `Header`）；§1.0 對比表移除、§3.1 ORM 移除、§3.3 寫入邏輯移除、§3.4 CLI 移除 |
| 4 | `write_index_meta_json` 抽 module-level | RagProcessor method、CLI 無法 import | 改為 `processor/rag_processor.py` module-level helper；RagProcessor + CLI 共用 |
| 5 | `get_paper_db_id` | plan 寫「需新增」 | grep 證實已存在 `paper_manager.py:336-343`、本 plan **不重新加**、§3.1 / §3.4 / CLI 直接 import 使用 |
| 6 | `cmd_init` pseudo-code | 純 `...` 佔位 | §3.4 補完完整實作（FAISS docstore 反向取、`doc_type` 設空字串、§5.1 加 1 個 test、§4 風險表 + Q16 收錄）|
| 7 | `OUTPUT_DIR` env 化（db_analysis §5.2） | `web_server.py:77` 寫死 `BASE_DIR / "output"` | **採納**：§3.6 新增子改動 D / settings.py 加 `OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(_BASE_DIR / "output")))` / web_server.py:77-78 改 `from settings import OUTPUT_DIR` / `tools/regen_rag.py` 統一用 / 併進 C1（Q17）/ Docker 化部署 SOP 加進 §7 |
| 8 | Pg-Ready 安撫註記（db_analysis §5.3） | 未提及 | **採納為宣告**：§1.0 加 footnote / §4 風險表加 1 條 / Q18 收錄；無 code 改動、確認既有 `db.py:36-51 if not _IS_SQLITE` 防禦性設計足夠 |
