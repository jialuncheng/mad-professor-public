# PIPE-RESUME C5 — P4 Async RAG 執行報告

---

**任務代號**：PIPE-RESUME C5
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8）
**次級參考**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C5
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C5)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C4（`8971a19`）已落地——`run_phase3`（P3）交付 `BilingualMarkdownSpec`，`run_phase4` 仍為 stub（四 Phase 缺最後一塊）。
- **完成狀態**：實作 `run_phase4`（P4 Async RAG）——唯一輸入 `ctx.bilingual.final_zh_path`，複用 `RagProcessor()._create_vector_store`（doc_type='resume' / paper_db_id）一站式完成 MarkdownHeader 分割 + `_is_chunk_meaningful`(≥3 技能詞保護) 過濾 + FAISS save_local + paper_chunks 批量寫庫 + index_meta.json；讀 `index_meta.json`(chunks_total) 交付 `RagDbSpec`。異常僅 `logger.warning(exc_info=True)` 後拋出由 Orchestrator 標 `rag_status='failed'`、不阻 `reading_ready`。**ResumePipeline 四 Phase 全落地**；複用 RagProcessor **零改動**；全套件 465 passed。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C5 | `run_phase4` P4 Async RAG（RagProcessor._create_vector_store + _is_chunk_meaningful ≥3 + paper_chunks 寫庫 + index_meta）→ RagDbSpec | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C5_resume_pipeline.py.bak` | 實作 run_phase4 + `_load_index_meta` helper；新增 C5 import（RagProcessor） |

> ⚠️ `.bak` 須在 C5 `git add` 清單中（§8）。`baton/` 暫存報告不入 Git。

---

## §4 修法說明

### §4.1 `pipelines/resume_pipeline.py` — run_phase4 P4 Async RAG
`# === [PIPE-RESUME C5 START/END] ===` 包裹（import / run_phase4 / `_load_index_meta`）。核心：
```python
def run_phase4(self, ctx):
    if ctx.bilingual is None:
        raise ValueError("PIPE-RESUME P4：ctx.bilingual 缺失（P3 未交付）")
    final_zh_path = ctx.bilingual.final_zh_path                  # ① 唯一輸入
    vectors_dir = paper_manager.vectors_path(settings.OUTPUT_DIR, ctx.owner_id, ctx.paper_id)
    paper_db_id = paper_manager.get_paper_db_id(ctx.owner_id, ctx.paper_id)  # None → 降級
    try:
        RagProcessor()._create_vector_store(                    # ② 一站式
            str(final_zh_path), str(vectors_dir),
            doc_type="resume", paper_db_id=paper_db_id)
        index_meta = self._load_index_meta(vectors_dir)         # ③ 讀 index_meta.json
        chunk_count = int(index_meta.get("chunks_total", 0))
        return RagDbSpec(vectors_path=str(vectors_dir),
            paper_chunk_count=chunk_count, index_meta=index_meta)
    except Exception as exc:
        logger.warning("...RAG 失敗（不阻主鏈、Orchestrator 標 rag_status='failed'）: %s",
                       ctx.paper_id, exc, exc_info=True)
        raise                                                   # 拋出由 Orchestrator 處理
```

**設計裁決（grep 證據驅動）**：
1. **複用 `_create_vector_store` 一站式**（`rag_processor.py:201`）：內部自動 `_is_chunk_meaningful`(doc_type='resume'→`MIN_CHUNK_RESUME_SLIDES=3`、`rag_processor.py:86`、保 email/phone/url、**不改演算法**) → `FAISS.from_documents`/`save_local` → paper_db_id 非 None 時 `_write_paper_chunks_to_db`（內部 `paper_manager.replace_paper_chunks`、`rag_processor.py:337`）→ **永遠**寫 `index_meta.json`（`chunks_total`）。
2. **DB 交易邊界（SOP）**：Embedding 在 `FAISS.from_documents` 階段（DB 交易外）；`replace_paper_chunks` 批量寫入不含 LLM/Embedding。C5 本體**無直接 commit/session.begin**。
3. **paper_db_id 優雅降級**：`get_paper_db_id` 回 None（測試/影子無 Paper row）→ `_create_vector_store` 內部 log warning、跳過 SQL、僅 FAISS + index_meta（`rag_processor.py:281-286`）；C5 另補一行 warning 明示降級。
4. **錯誤隔離（R4.2）**：P4 異常 `logger.warning(exc_info=True)` 後**拋出**，由 `Orchestrator._default_dispatch_p4`（`orchestrator.py:149-154`）catch → `rag_status='failed'`，不阻 `reading_ready`。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/resume_pipeline.py
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C5_resume_pipeline.py.bak
# （.claude-logs/baton/、prompts/、TODO.md 文件改動另計）
```

### §5.2 驗收輸出
四 Phase 全落地（無 NotImplementedError 殘留）：
```
run_phase1 -> 已實作
run_phase2 -> 已實作
run_phase3 -> 已實作
run_phase4 -> 已實作
```
§6.5 grep 精準命中：`_create_vector_store`(L512) / `RagDbSpec(`(L519) / `vectors_path(`(L499) / `get_paper_db_id`(L503) / `chunks_total`(L518) / `doc_type="resume"`(L514)。

pipelines 既有測試（防 Regression）：`25 passed in 0.60s`。
全套件：
```
1 failed, 465 passed, 3 skipped in 110.45s
# 唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 C5 Regression）
```

> 註：`tests/test_resume_pipeline.py` P4 契約測試屬 **C6**、本 C5 尚未建檔；C5 以 import/四 Phase 落地/grep/SOP/全套件防 Regression 驗收。實打 RAG（FAISS+Embedding）端到端屬 baron 端影子驗證（§6.2 E2E）。

### §5.3 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**：C5 新增 3 處 `logger.warning(..., exc_info=True)`（paper_db_id 降級 / RAG 失敗 / index_meta 失敗）；run_phase4 完成 1 處 `logger.info`；全檔 `logger.error` 仍 0（合規）。逐塊驗證所有 warning 皆含 `exc_info=True`。
- **database 檢測**：C5 本體**無直接 DB 操作**（委派 `RagProcessor`）；`grep .commit()/session.begin()` 於 resume_pipeline.py 僅 C3 docstring 註解文字（合規）。Embedding 於 FAISS 階段交易外、`replace_paper_chunks` 不含 LLM/Embedding。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` 業務代碼 | [x] ✅ 未觸碰（paper_manager 僅呼叫 vectors_path/get_paper_db_id） |
| `processor/rag_processor.py`（`_create_vector_store`/`_is_chunk_meaningful`/`MIN_CHUNK_RESUME_SLIDES`） | [x] ✅ 僅**呼叫**、零改動（不改過濾演算法） |
| `processor/*` 其他既有 processor | [x] ✅ 未觸碰 |
| `pipelines/contracts.py` / `context.py` / `base_strategy.py` / `factory.py` / `orchestrator.py` | [x] ✅ 未變更 |
| 其他 Phase（run_phase1/2/3） | [x] ✅ 未觸碰（C5 僅實作 run_phase4） |
| `models.py` / `db.py` | [x] ✅ 未觸碰（DB 寫入委派 RagProcessor） |
| 既有 `list_papers` / `get_paper` / `delete_paper` API 與前端 | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存 `baton/`、不入版控，待 C7 收官 `mv`+`git add` 歸檔至 `executions/`。
- **下一步**：tasks.md C6 — 單元測試（策略分派與四 Phase 契約）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。
- **附帶（歷史 Hash 自癒）**：C4 已提交 `8971a19` → TODO active 列 C4 佔位符已回填。
- **里程碑**：ResumePipeline **四 Phase（P1-P4）全部落地**；C6 補單元測試、C7 收官。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單（C5 程式碼 + .bak；baton/ 報告嚴禁加入）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C5_resume_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C5_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C5_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C5 — P4 Async RAG（門檻 ≥3 技能詞保護）

實作 ResumePipeline.run_phase4：① 唯一輸入 ctx.bilingual.final_zh_path；② 複用
RagProcessor()._create_vector_store(final_zh_path, vectors_path, doc_type='resume',
paper_db_id) 一站式——MarkdownHeader 分割 + _is_chunk_meaningful(≥3、保 email/phone/url、
不改演算法)過濾 + FAISS save_local + paper_chunks 批量寫庫 + index_meta.json；
③ paper_db_id 由 get_paper_db_id 取得、None 則優雅降級（僅 FAISS）；④ 讀 index_meta.json
(chunks_total) 交付 RagDbSpec。Embedding 於 FAISS 階段（DB 交易外）；異常僅 logger.warning
(exc_info)後拋出由 Orchestrator 標 rag_status='failed'、不阻 reading_ready。四 Phase 全落地、
複用 RagProcessor 零改動、全套件 465 passed。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C5 的代碼變更與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；C7 收官時 Conformance 核對 plan 後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存於 baton/、C7 收官前不入版控；P4 失敗不阻 reading_ready（R4.2） |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C5 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C5 執行完畢——run_phase4 P4 Async RAG（複用 RagProcessor._create_vector_store 一站式：≥3 門檻過濾 + FAISS + paper_chunks 寫庫 + index_meta）→ RagDbSpec；錯誤隔離拋出由 Orchestrator 標 rag_status='failed' 不阻 reading_ready。ResumePipeline 四 Phase 全落地。全套件 465 passed（唯一 failed 為既存環境性 test_settings_log_format_default_auto、非 Regression）。
