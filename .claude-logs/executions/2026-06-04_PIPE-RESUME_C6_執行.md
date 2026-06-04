# PIPE-RESUME C6 — 單元測試 執行報告

---

**任務代號**：PIPE-RESUME C6
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8）
**次級參考**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C6
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C6)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C5（`e8a7429`）已落地——ResumePipeline 四 Phase（P1-P4）全部落地、`run_phase1..4` 皆已實作；尚無對應單元測試。
- **完成狀態**：新建 `tests/test_resume_pipeline.py`（**15 測試**、全程 mock LLM/Embedding 不實打 API），涵蓋策略分派 + P1-P4 四 Phase 契約。新測試 **15 passed**；全套件 **480 passed**（465+15）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C6 | 新建 `tests/test_resume_pipeline.py` 15 測試（策略分派 + P1-P4 契約、mock 隔離） | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 新建 | `tests/test_resume_pipeline.py` | — | 15 單元測試；`# === [PIPE-RESUME C6 START/END] ===` 包裹（純新增、無須備份） |

> `baton/` 暫存報告不入 Git。

---

## §4 修法說明

### §4.1 `tests/test_resume_pipeline.py` — 15 測試（檔頭尾 C6 標記包裹）

| # | 測試 | 驗證點 |
|---|---|---|
| ① | `test_factory_dispatch_resume` | `get_strategy('resume')`→ResumePipeline 實例、`rag_char_threshold==3` |
| ② | `test_no_doctype_branch_in_strategy` | 策略源碼無 `doc_type ==` 硬編碼分支 |
| ③ | `test_detect_source_lang` | CJK→'zh'、ASCII→'en' |
| ④ | `test_extract_contact` | email/phone regex 抽取 |
| ⑤ | `test_resolve_title_priority` | candidate_name→# 行→paper_name |
| ⑥ | `test_load_tiles` | dict→sections / list→直接 |
| ⑦ | `test_run_phase1_contract` | IngestionMetadataSpec title=candidate_name、**不含** abstract/lcc/glossary/translated_abstract/domain_name、_raw_meta 穿線 |
| ⑧ | `test_run_phase2_flag_off` | 旗標 OFF：glossary={}、lcc=raw、abstract/translated/domain_name 交付 |
| ⑨ | `test_run_phase2_lcc_fallback_general` | raw 空 → lcc fallback 'general' |
| ⑩ | `test_run_phase2_glossary_selfheal_injects_summary_and_lcc` | 缺詞自癒：extract_terms 注入原文摘要(src)+LCC(domain)、upsert 冪等、glossary 回填 |
| ⑪ | `test_run_phase2_cache_hit_zero_extract` | query_cascade 命中 → 不呼 extract_terms/upsert（0 抽詞 LLM）|
| ⑫ | `test_run_phase3_bypass_doctype_and_carryforward` | 100% Bypass（整份 1 次 content）、InjectionContext.doc_type=='resume'、zh_summary←translated_abstract、translated_abstract 沿用 P2、final_zh/en 寫檔 |
| ⑬ | `test_is_chunk_meaningful_resume_threshold` | resume ≥3 保 Python/Docker/email/phone/url、純數字/空過濾、academic ≥10 |
| ⑭ | `test_run_phase4_failure_isolation` | RAG 失敗拋出（交 Orchestrator 標 failed）、`reading_ready` 不受影響 |
| ⑮ | `test_run_phase4_success` | 讀 index_meta.json(chunks_total) 交付 RagDbSpec |

**mock 策略**：monkeypatch 模組級 `rp.ResumeProcessor`/`DocAnalyzer`/`Markdown/Json/TilingProcessor`/`normalize_to_lcc`/`Translator`/`GlossaryManager`/`RagProcessor` 與實例方法 `_extract_metadata`/`_read_source_text`/`_make_summary`/`_resolve_domain_name`；`settings.OUTPUT_DIR`→`tmp_path`、`settings.LLM_USE_GLOSSARY_ALIGN` 切換旗標；`_is_chunk_meaningful` 用真實函式 + `SimpleNamespace(page_content=...)` 替身 doc。**全程零實打線上 API**。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
?? tests/test_resume_pipeline.py
# （.claude-logs/baton/、prompts/、TODO.md 文件改動另計）
```

### §5.2 新測試全通過
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -v
... 15 items
test_factory_dispatch_resume PASSED
test_no_doctype_branch_in_strategy PASSED
test_detect_source_lang PASSED
test_extract_contact PASSED
test_resolve_title_priority PASSED
test_load_tiles PASSED
test_run_phase1_contract PASSED
test_run_phase2_flag_off PASSED
test_run_phase2_lcc_fallback_general PASSED
test_run_phase2_glossary_selfheal_injects_summary_and_lcc PASSED
test_run_phase2_cache_hit_zero_extract PASSED
test_run_phase3_bypass_doctype_and_carryforward PASSED
test_is_chunk_meaningful_resume_threshold PASSED
test_run_phase4_failure_isolation PASSED
test_run_phase4_success PASSED
============================== 15 passed in 0.61s ==============================
```

### §5.3 全套件（防 Regression）
```bash
$ venv/bin/python -m pytest tests/ -q
1 failed, 480 passed, 3 skipped in 39.41s
# 480 = 既有 465 + C6 新增 15；唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 C6 Regression）
```

### §5.4 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**：C6 為純測試檔、無 `logger.error`/`traceback.format_exc`（合規）。
- **database 檢測**：C6 無 DB 操作（mock 隔離、無 `.commit()`/`session.begin()`）（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / 既有 processors 核心 | [x] ✅ 未觸碰 |
| `pipelines/resume_pipeline.py`（C1-C5 業務碼） | [x] ✅ 未變更（C6 僅新增測試檔） |
| `pipelines/contracts.py` / `context.py` / `factory.py` 等合約/骨架 | [x] ✅ 未變更 |
| 既有測試檔 | [x] ✅ 未觸碰（純新增 test_resume_pipeline.py） |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存 `baton/`、不入版控，待 C7 收官 `mv`+`git add` 歸檔至 `executions/`。
- **下一步**：tasks.md C7 — Checkout / 收官歸檔（Conformance 三維度驗收 + 一次性 mv plan_v1/tasks/C1-C7 報告 + TODO 結案）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。
- **附帶（歷史 Hash 自癒）**：C5 已提交 `e8a7429` → TODO active 列 C5 佔位符已回填。
- **里程碑**：ResumePipeline 四 Phase 落地 + 15 單元測試覆蓋；剩 C7 收官。

---

## §8 baron 執行命令

```bash
# 1. 純新增測試檔、無須備份

# 2. git add 清單（C6 測試檔；baton/ 報告嚴禁加入）
git add tests/test_resume_pipeline.py

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C6_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C6_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C6 — 單元測試（策略分派與四 Phase 契約）

新建 tests/test_resume_pipeline.py（15 測試、mock LLM/Embedding 不實打 API）驗證
ResumePipeline 完整合約：1) 策略分派 get_strategy('resume')→ResumePipeline 無 doc_type 分支；
2) P1 IngestionMetadataSpec title=candidate_name、不含 Abstract/LCC/Glossary、_raw_meta 穿線；
3) P2 normalize_to_lcc cache 命中 0 抽詞 / raw 空 fallback 'general' / GlossaryReadySpec
abstract+translated_abstract+domain_name / 缺詞自癒注入原文摘要+LCC / 旗標 off 空 glossary；
4) P3 100% Bypass 整份 1 次 content 翻譯 + InjectionContext.doc_type='resume' + translated_abstract
沿用 P2；5) P4 _is_chunk_meaningful ≥3 保 Python/Docker/email/phone/url、純數字過濾、RAG 失敗
拋出隔離不阻 reading_ready。新測試 15 passed、全套件 480 passed。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C6 的測試新增與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；C7 收官時 Conformance 核對 plan 後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存於 baton/、C7 收官前不入版控；測試嚴禁實打線上 API |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C6 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C6 執行完畢——新建 tests/test_resume_pipeline.py 15 測試（策略分派 + P1-P4 四 Phase 契約、mock LLM/Embedding 隔離）；新測試 15 passed、全套件 480 passed（唯一 failed 為既存環境性 test_settings_log_format_default_auto、非 Regression）。ResumePipeline 四 Phase 落地 + 單元測試覆蓋完成，剩 C7 收官。
