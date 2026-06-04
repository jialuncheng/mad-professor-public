# PIPE-RESUME C3 — P2 Glossary & Context Prep 執行報告

---

**任務代號**：PIPE-RESUME C3
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 內部 v8）
**次級參考**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C3
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C3)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C2（`d7edcd9`）已落地——`run_phase1`（P1 Ingestion）交付 `IngestionMetadataSpec`，`run_phase2` 仍為 stub。
- **完成狀態**：實作 `run_phase2`（P2 Glossary & Context Prep）四步循序自癒——① `normalize_to_lcc` 收斂 LCC；② 直接 LLM 生成履歷原文摘要；翻摘要 `Translator(DEEP_THINK)`→`translated_abstract`；③ `GlossaryManager` 自癒（旗標閘門、LLM 交易外、冪等回寫）；④ `lcc→Domains.name` PK 唯讀→`domain_name`；交付 `GlossaryReadySpec`。消費三大共用真理源（DomainNormalizer / GlossaryManager / Translator）**零改動**；全套件 465 passed。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | `run_phase2` 四步循序自癒（normalize_to_lcc + 摘要 + Translator DEEP_THINK + GlossaryManager 自癒 + Domains.name）→ GlossaryReadySpec | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C3_resume_pipeline.py.bak` | 實作 run_phase2 + 5 個 P2 私有輔助；新增 C3 imports + 常數 |

> ⚠️ `.bak` 須在 C3 `git add` 清單中（§8）。`baton/` 暫存報告不入 Git。

---

## §4 修法說明

### §4.1 `pipelines/resume_pipeline.py` — run_phase2 四步循序自癒
`# === [PIPE-RESUME C3 START/END] ===` 包裹（imports / 常數 / run_phase2 / 5 輔助）。核心：
```python
def run_phase2(self, ctx):
    source_lang = (ctx.ingestion.source_lang if ctx.ingestion else None) or "en"
    full_text = self._read_source_text(ctx)               # 讀 P1 原文 md（fallback tiles 重組）
    raw_domain = self._raw_meta.get("domain") or ""
    lcc = normalize_to_lcc(raw_domain, context_text=full_text) or "general"   # ①
    abstract = self._make_summary(full_text) or full_text[:600]              # ②
    translated_abstract = Translator().translate(                           # 翻摘要（DEEP_THINK）
        abstract, InjectionContext(lcc=lcc, glossary={}, doc_type="resume"),
        TranslateMode.DEEP_THINK, "abstract")
    glossary = {}
    if settings.LLM_USE_GLOSSARY_ALIGN:                                      # ③ 旗標閘門
        glossary = self._heal_glossary(source_lang, "zh-tw", lcc, abstract, translated_abstract)
    domain_name = self._resolve_domain_name(lcc)                            # ④ PK 唯讀
    return GlossaryReadySpec(abstract=abstract, lcc=lcc, glossary=glossary,
        translated_abstract=translated_abstract, chapter_summaries=None, domain_name=domain_name)
```

**設計裁決（grep 證據驅動、據實記錄）**：
1. **實作必然序（extract_terms 簽名所迫，保留 baron 意圖）**：落地 `GlossaryManager.extract_terms(source_text, translated_text, source_lang, target_lang, domain)`（`glossary_extractor.py:122`）**需 translated_text**。P2 唯一可用譯文為 `translated_abstract`，故 DEEP_THINK 翻摘要須先於 ③ glossary 抽詞，且 **一次翻譯雙用**（交付 + 抽詞樣本），不重複翻譯。完全保留 baron 重排意圖（摘要先生成、作 glossary 基礎），僅為簽名所迫的依賴序。
2. **Glossary 旗標閘門**：`settings.LLM_USE_GLOSSARY_ALIGN`（預設 False、`settings.py:80`）→ False 時 glossary={}、跳過自癒（線上零風險、對齊 GLOSSARY-CORE 設計）。
3. **摘要生成**：codebase 無「生成式履歷摘要」函式（`extract_abstract_from_markdown` 對 resume 回 None；`extra_info_processor.generate_document_summary` 會注入 AI Questions 違反 R3.1 且 plan 廢除 extra_info）→ C3 以 `LLMClient.chat`（stream=False、temp=0.2、`LLM_DOMAIN_MODEL`）直接摘要、原文語言；失敗兜底原文截斷。
4. **source_lang**：取 `ctx.ingestion.source_lang`（P1 交付）；`target_lang` 固定 `"zh-tw"`。
5. **abstract 翻譯不帶 glossary**：glossary 尚未建（雞生蛋）→ 空 glossary 翻摘要；P3 正文翻譯才注入凍結 glossary。

**database SOP（§6.7）**：所有 LLM 呼叫（normalize/summary/translate/extract_terms）皆在 DB 交易外；`_resolve_domain_name` 以 `session.get(Domains, lcc)` PK **唯讀檢索**（`with SessionLocal() as session`、**無 `session.begin()` 寫交易**）。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/resume_pipeline.py
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C3_resume_pipeline.py.bak
# （.claude-logs/baton/、prompts/、TODO.md 文件改動另計）
```

### §5.2 驗收輸出
import + 註冊（C3 imports 不破壞載入）：
```
strategy= ResumePipeline
```
§6.3 四步真理源呼叫齊全（grep）：`normalize_to_lcc`(L286) / `query_cascade`(L377) / `extract_terms`(L381) / `upsert_terms`(L385) / `TranslateMode.DEEP_THINK`(L295) / `Domains`(session.get L397) 全命中。

pipelines 既有測試（防 Regression）：
```
25 passed in 0.60s
```
全套件：
```
1 failed, 465 passed, 3 skipped in 132.27s
# 唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 C3 Regression）
```

> 註：`tests/test_resume_pipeline.py` P2 契約測試屬 **C6**、本 C3 尚未建檔；§6.3 的 pytest 斷言於 C6 落地。C3 以 import/grep/SOP/全套件防 Regression 驗收。

### §5.3 SOP 一致性核查（BE-Refactor 強制）
- **logging 檢測**：6 處 `logger.warning(..., exc_info=True)`（P1 3 + P2 3、逐塊程式驗證**全含 exc_info=True**）；無裸 `logger.error`、無 `traceback.format_exc`（合規）。
- **database 檢測**（`grep -nE "\.commit\(\)" pipelines/resume_pipeline.py`）：無命中（合規）。`session.begin` 命中僅 docstring/註解文字（無實際寫交易；`domain_name` 走 `session.get` PK 唯讀）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` 業務代碼 | [x] ✅ 未觸碰（paper_manager 僅呼叫 paper_dir） |
| `processor/domain_normalizer.py` / `glossary_extractor.py` / `translator.py` 三大真理源 | [x] ✅ 僅**消費落地簽名**、零改動 |
| `processor/resume_processor.py` / `rag_processor.py` 等既有 processor | [x] ✅ 未觸碰 |
| `pipelines/contracts.py` / `context.py` / `base_strategy.py` / `factory.py` / `orchestrator.py` | [x] ✅ 未變更（C3 僅實作 run_phase2 本體） |
| `models.py` / `db.py` | [x] ✅ 僅讀取（Domains PK 唯讀、SessionLocal 唯讀） |
| 其他 Phase（run_phase1/3/4）與合約 | [x] ✅ 未觸碰（run_phase1 C2 已落地、3/4 仍 stub） |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：本執行報告暫存 `baton/`、不入版控，待 C7 收官 `mv`+`git add` 歸檔至 `executions/`。
- **下一步**：tasks.md C4 — P3 Translation & Restore（100% Bypass 翻譯還原）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。
- **附帶（歷史 Hash 自癒）**：C2 已提交 `d7edcd9` → TODO active 列 C2 佔位符已回填。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單（C3 程式碼 + .bak；baton/ 報告嚴禁加入）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C3_resume_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C3_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C3_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C3 — P2 Glossary & Context Prep（四步循序自癒）

實作 ResumePipeline.run_phase2 四步：① normalize_to_lcc(raw_domain, context_text=履歷全文)
收斂 LCC；② 直接 LLM 生成履歷原文摘要 abstract；翻摘要 Translator(DEEP_THINK)→
translated_abstract（一次翻譯雙用：交付 + glossary 抽詞樣本，extract_terms 簽名所迫）；
③ Glossary 自癒（旗標 LLM_USE_GLOSSARY_ALIGN 閘門、預設 False 空 glossary；query_cascade→
缺詞 extract_terms→upsert 冪等回寫、LLM 全在 DB 交易外）；④ lcc→Domains.name PK 唯讀免交易→
domain_name。交付 GlossaryReadySpec。消費三大真理源零改動、全套件 465 passed。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C3 的代碼變更與驗收結果，作為 Traceability 審計依據 |
| **用途** | 暫存於 baton/；C7 收官時 Conformance 核對 plan 後 mv 歸檔至 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；暫存於 baton/、C7 收官前不入版控；LLM 呼叫嚴守 DB 交易外 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 C3 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C3 執行完畢——run_phase2 四步循序自癒（LCC / 摘要 / 翻摘要 DEEP_THINK / Glossary 旗標閘門自癒 / Domains.name PK 唯讀）→ GlossaryReadySpec；消費三大真理源零改動。設計裁決：extract_terms 需 translated_text → 翻摘要先於 glossary 抽詞且一次翻譯雙用（保留 baron 意圖）；摘要以 LLMClient 直接生成。全套件 465 passed（唯一 failed 為既存環境性 test_settings_log_format_default_auto、非 Regression）。
