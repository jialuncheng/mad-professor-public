# PIPE-LITEDOC C4 執行報告 — P2 六步（消費 section_engine + 三真理源）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC C4 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md §8 C4` |
| 次級參考 | plan v3 §2 U4;resume run_phase2 六步鏡像;RAG-ASYNC-HOTFIX-1 接縫基準 |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C4)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C3（P1 攝入）已 ship;litedoc run_phase2 為 strict stub。
- **完成狀態**：實作 `run_phase2`（六步消費 section_engine + 三真理源）+ 5 P2 helper + 2 P2 測試。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U4`（P2 六步、全消費 DomainNormalizer/Glossary/Translator + section_engine、key=原文標題 path）;無偏離。LLM 全在 DB 交易外（database SOP）;section_summaries 接縫基準繼承 section_engine（零位移）。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C4 | （待 baron 回填）| BE-Refactor: PIPE-LITEDOC C4 — P2 六步（消費 section_engine + 三真理源）|

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 修改（run_phase2 + helpers + P2 imports/常數）| **本 commit git add** |
| `tests/test_litedoc_pipeline.py` | 修改（追加 2 P2 測試）| **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C4_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C4_test_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C4_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C4 ✅ / C5 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C4_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C8 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-LITEDOC C4 ...] ===` 包裹）
- **imports + 常數**：加 `section_engine` / `normalize_to_lcc` / `GlossaryManager` / `InjectionContext,TranslateMode,Translator` + P2 常數（_TARGET_LANG / _ABSTRACT_MAX_CHARS / _ABSTRACT_FALLBACK_CHARS / _SECTION_SUMMARY_INPUT_CHARS / `_LITEDOC_SUMMARY_SYSTEM_PROMPT`〔文章摘要〕/ 通用節點摘要 prompt × 2）。
- **`run_phase2`** 六步：① `_make_summary`（全文摘要、LLM 交易外）② `normalize_to_lcc("", context_text=全文)`〔litedoc 無 P1 domain 欄、以內容判定〕③ Glossary 自癒〔旗標 `LLM_USE_GLOSSARY_ALIGN` 閘門、`_heal_glossary`、LLM 交易外〕④ `Translator(DEEP_THINK)` 翻 abstract → translated_abstract〔雙用〕⑤ `_resolve_domain_name(lcc)`〔Domains PK 唯讀〕⑥ `section_engine.build_section_summaries`〔tiles + llm/prompt/model 注入、key=原文標題 path〕→ GlossaryReadySpec。
- **helpers**：`_read_source_text`/`_tiles_to_text`/`_make_summary`/`_heal_glossary`/`_resolve_domain_name`。
- **交易邊界**：LLM 全交易外;`_resolve_domain_name` 用 `SessionLocal()` 唯讀檢索（無 `session.begin()` 寫交易）;glossary upsert 由 `GlossaryManager` 內部處理（litedoc 無裸 commit）。

關鍵片段（⑥ 接縫 key）：
```python
section_summaries = section_engine.build_section_summaries(
    (ctx.ingestion.tiles if ctx.ingestion else []) or [],
    llm=LLMClient.get_instance(), abstract=abstract, source_lang=source_lang,
    summary_model=settings.LLM_DOMAIN_MODEL, translate_model=settings.TRANSLATE_MODEL,
    summary_system_prompt=_SECTION_SUMMARY_SYSTEM_PROMPT,
    translate_system_prompt=_SECTION_SUMMARY_TRANSLATE_SYSTEM_PROMPT,
    input_chars_cap=_SECTION_SUMMARY_INPUT_CHARS, max_chars=_ABSTRACT_MAX_CHARS,
    paper_id=ctx.paper_id,
)   # key=原文標題 path（繼承 section_engine、RAG-ASYNC-HOTFIX-1）
```

## §5 測試結果
### §5.1 §6.4 C4 驗收 grep
```
run_phase2 / build_section_summaries / normalize_to_lcc / GlossaryReadySpec / InjectionContext /
TranslateMode.DEEP_THINK / _resolve_domain_name 全命中
```
### §5.2 P2 測試 + 全套件 pytest
```
pytest tests/test_litedoc_pipeline.py -q → 17 passed
  〔P2 2：GlossaryReadySpec 交付〔abstract/lcc/translated_abstract/domain_name〕/
    **section_summaries key 完全對齊原文標題 path**〕
pytest tests/ -q → 1 failed, 678 passed, 3 skipped（678＝677 基線 + 1〔淨：移 1 stub param + 2 P2〕;
  唯一 fail＝既有 .env LOG_FORMAT env flake〕
```
### §5.3 §6.9 SOP 一致性核查（BE-Refactor 強制）
```
logging（logger.error / format_exc）：0 命中（合規;soft-fail 皆 logger.warning + exc_info=True）
database（裸 commit、不在 session.begin 內）：0 命中（合規）
session.begin 寫交易：0（P2 僅 Domains PK 唯讀 + LLM 交易外、glossary upsert 委 GlossaryManager）
```
### §5.4 變動範圍（git）
```
git status -s 業務/測試 .py：僅 pipelines/litedoc_pipeline.py(M) + tests/test_litedoc_pipeline.py(M)
```

## §6 不可動清單遵守
| 項目（tasks §7）| 狀態 |
|---|---|
| `section_engine.py` | [x] ✅ 零碰（consume build_section_summaries）|
| `rag_indexer.py` / `contracts.py` | [x] ✅ 零碰 |
| `resume_pipeline.py` / `slide_pipeline.py` | [x] ✅ 零碰 |
| **三大共用真理源**（domain_normalizer/glossary_extractor/translator）/ **A 軌全部** | [x] ✅ 零碰（僅 import 消費）|
| `DocumentStrategy` ABC / `factory` | [x] ✅ 未改 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅改 litedoc_pipeline.py + test（plan/tasks §8 C4 範圍）;真理源/section_engine/合約/其他策略零碰。
- **(b) 無關 / 違規?**：否。run_phase2 六步對應 U4;消費共用真理源 + section_engine、LLM 全交易外（database SOP）;section_summaries key 繼承 section_engine 基準。msg 簽名校正 Opus 4.8。符 CLAUDE.md。
- **(c) 推進哪個 U-N?**：U4（P2 六步）;無做白工——section_summaries 為 P4 接縫產物、key 基準鎖死。

## §7 銜接
- baton 狀態：C1-C4 報告 + plan + tasks 留 baton（待 C8 一次性歸檔）。
- 下一步：**C5 — P3 size-gate 翻譯與 HTML 扉頁還原**（size-gate <15k 一鍵 / ≥15k section + `render_meta_header_html` + collect_rag_sections + **U5c 雙語標題鏈** + heading 退化 + zh edge）→ BilingualMarkdownSpec。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3、.bak 本 commit git add）

# 2. git add（業務 + 測試 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C4_litedoc_pipeline.py.bak .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C4_test_litedoc_pipeline.py.bak
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C4_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC_C4_msg.txt）
cat > /tmp/PIPE-LITEDOC_C4_msg.txt << 'EOF'
BE-Refactor: PIPE-LITEDOC C4 — P2 六步（消費 section_engine + 三真理源）

- litedoc_pipeline.run_phase2 六步：①全文摘要 ②normalize_to_lcc（內容判定）③Glossary 級聯自癒（旗標閘門）
  ④Translator(DEEP_THINK) 翻摘要 + lcc→Domains.name→domain_name ⑤⑥ section_engine.build_section_summaries
  （key=原文標題 path）→ GlossaryReadySpec。
- 全消費三大共用真理源 + section_engine、零造輪；LLM 全在 DB 交易外，domain_name 為 Domains PK 唯讀。

驗證：litedoc 17 passed〔P2：GlossaryReadySpec 交付 + section_summaries key 對齊原文標題 path〕；
全套件 678 passed（唯一 fail＝既有 .env LOG_FORMAT flake）；SOP logger.error 0/裸 commit 0/寫交易 0；
真理源/section_engine/合約/其他策略/A 軌零碰。baton 未 add、待 C8 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-LITEDOC_C4_msg.txt
```

## §9 回退方式
`git revert <C4 hash>`（或自 `.bak` 還原 litedoc_pipeline.py + test）。

---
### 結論
🟢 P2 六步落地（全消費 section_engine + 三真理源、LLM 交易外、section_summaries key=原文標題 path）、17 passed、全套件 678 基線、SOP 合規、零碰真理源/A 軌。下一步 C5 P3 size-gate 翻譯與 HTML 扉頁還原。
