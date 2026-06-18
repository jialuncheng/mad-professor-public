# PIPE-LITEDOC C3 執行報告 — P1 MinerU 攝入與 metadata 旁路（DocAnalyzer 映射 + URL publisher 解碼）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC C3 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md §8 C3` |
| 次級參考 | plan v3 §2 U2/U2.1/U3、§2.5 方案 A;resume run_phase1 鏡像 |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C3)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C2（骨架 + 三 key 註冊）已 ship;litedoc run_phase1 為 strict stub。
- **完成狀態**：實作 `litedoc_pipeline.py::run_phase1`（MinerU 攝入 + DocAnalyzer U2.1 映射 + tiles + B 軌原生 metadata + 旁路）+ 5 P1 helper + `test_litedoc_pipeline.py` 追加 7 P1 測試。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U2/U3 + U2.1`（P1 MinerU 文字攝入·非 Vision / DocAnalyzer 映射防 academic 偏位 / metadata 旁路 + URL publisher 解碼·方案 A B 軌原生）;無偏離。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C3 | （待 baron 回填）| BE-Refactor: PIPE-LITEDOC C3 — P1 MinerU 攝入與 metadata 旁路（DocAnalyzer 映射 + URL publisher 解碼）|

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 修改（run_phase1 + helpers）| **本 commit git add** |
| `tests/test_litedoc_pipeline.py` | 修改（追加 7 P1 測試）| **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C3_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C3_test_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C3_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C3 ✅ / C4 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C3_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C8 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-LITEDOC C3 ...] ===` 包裹）
- **imports + 常數**：加攝入 processor import（PDFProcessor/MarkdownCleaner/DocAnalyzer/MarkdownProcessor/JsonProcessor/TilingProcessor/meta_normalizer）+ 啟發式常數（_CJK_MIN/_CJK_RATIO/_META_INPUT_CHARS）+ `_LITEDOC_META_SYSTEM_PROMPT`（B 軌原生 cover-prompt、含 URL→組織解碼指引）+ `_strip_json_fence`。
- **`run_phase1`**：① `PDFProcessor().parse`（MinerU）② **強制 `MarkdownCleaner().clean`**（非 resume/slides 跳過）③ `DocAnalyzer().analyze(md, analyzer_doc_type)` **U2.1 映射** `analyzer_doc_type = ctx.doc_type if ctx.doc_type in ("news","web") else "web"`（soft-fail try/except + exc_info）④⑤⑥ `_build_tiles`（md2json→json_process→TilingProcessor、litedoc 不 opt-out）⑦ `_extract_litedoc_metadata`（LLM cover-prompt、temp=0、soft-fail）→ title/authors/date/publisher/url;`venue` 承接 publisher 回填 spec、`date`/`url`/`organization` 經 `meta_normalizer.normalize_fields`（旗標閘門）寫 `ctx.raw_metadata` 旁路（{value,source,confidence}）;`_shadow` title 綴 (測試) → IngestionMetadataSpec。
- **helpers**：`_build_tiles`/`_load_tiles`/`_extract_litedoc_metadata`/`_resolve_title`/`_detect_source_lang`。

關鍵片段（U2.1 + 旁路）：
```python
analyzer_doc_type = ctx.doc_type if ctx.doc_type in ("news", "web") else "web"  # 防 fallback academic
...
normalized = meta_normalizer.normalize_fields(raw_fields, context=title) if raw_fields else {}
ctx.raw_metadata = {k: {"value": v, "source": "litedoc_p1", "confidence": "medium"} for k, v in normalized.items()}
spec = IngestionMetadataSpec(title=title, authors=[...], venue=publisher or None, doi=None, source_lang=source_lang, tiles=tiles)
```

## §5 測試結果
### §5.1 §6.3 C3 驗收 grep
```
run_phase1 / PDFProcessor / MarkdownCleaner / DocAnalyzer / analyzer_doc_type〔in ("news","web") else "web"〕命中
URL publisher 解碼 prompt：1（"decode the publisher from the ... URL domain"）
raw_metadata 旁路寫入命中
```
### §5.2 P1 測試 + 全套件 pytest
```
pytest tests/test_litedoc_pipeline.py -q → 16 passed
  〔分派 9〔C2〕+ P1 7：spec 交付 / raw_metadata 旁路 / URL→publisher 解碼 / DocAnalyzer 映射 ×4〔news/web/litedoc/unknown→web〕/ shadow title 綴〕
pytest tests/ -q → 1 failed, 677 passed, 3 skipped（677＝670 基線 + 7;唯一 fail＝既有 .env LOG_FORMAT env flake〕
```
### §5.3 §6.9 SOP 一致性核查（BE-Refactor 強制）
```
logging（logger.error / format_exc）：0 命中（合規;3 處 soft-fail 皆 logger.warning + exc_info=True）
database（裸 commit）：0 命中（合規;P1 無 DB 交易、寫庫屬 web_server 影子端）
```
### §5.4 變動範圍（git）
```
git status -s 業務/測試 .py：僅 pipelines/litedoc_pipeline.py(M) + tests/test_litedoc_pipeline.py(M)
```

## §6 不可動清單遵守
| 項目（tasks §7）| 狀態 |
|---|---|
| `section_engine.py`（C1 formatter）/ `rag_indexer.py` / `contracts.py` | [x] ✅ 零碰 |
| `resume_pipeline.py` / `slide_pipeline.py` | [x] ✅ 零碰 |
| 三大共用真理源 / **A 軌全部**（processor 為 consume、未改其碼）| [x] ✅ 零碰（僅 import 消費既有 processor）|
| `DocumentStrategy` ABC / `factory` 機制 | [x] ✅ 未改 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅改 litedoc_pipeline.py + test（plan/tasks §8 C3 範圍）;processor 為 import 消費、未改其碼;section_engine/合約/其他策略零碰。
- **(b) 無關 / 違規?**：否。run_phase1 全鏈對應 U2/U2.1/U3;metadata 採方案 A B 軌原生 cover-prompt（不耦合 A 軌 metadata_extractor、§2.5 決策）;SOP soft-fail 皆 warning+exc_info。msg 簽名校正 Opus 4.8。符 CLAUDE.md。
- **(c) 推進哪個 U-N?**：U2（P1 攝入）+ U2.1（DocAnalyzer 映射）+ U3（metadata 旁路 + URL 解碼）;無做白工。

## §7 銜接
- baton 狀態：C1-C3 報告 + plan + tasks 留 baton（待 C8 一次性歸檔）。
- 下一步：**C4 — P2 六步**（消費 `section_engine.build_section_summaries` + DomainNormalizer/Glossary/Translator）→ GlossaryReadySpec。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3、.bak 本 commit git add）

# 2. git add（業務 + 測試 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C3_litedoc_pipeline.py.bak .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C3_test_litedoc_pipeline.py.bak
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C3_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC_C3_msg.txt）
cat > /tmp/PIPE-LITEDOC_C3_msg.txt << 'EOF'
BE-Refactor: PIPE-LITEDOC C3 — P1 MinerU 攝入與 metadata 旁路（DocAnalyzer 映射 + URL publisher 解碼）

- litedoc_pipeline.run_phase1：PDFProcessor(MinerU) parse + 強制 md_cleaner + DocAnalyzer
  〔U2.1 映射：news/web 原樣、litedoc/unknown→'web' 扁平 prompt、防 doc_analyzer fallback academic〕
  + md2json/json_process/TilingProcessor 產 tiles。
- metadata 方案 A（B 軌原生 cover-prompt、不耦合 A 軌）：抽 title/authors/date/publisher/url，
  含 URL→組織名解碼；venue 承接 publisher、date/url/organization 經 meta_normalizer 寫 ctx.raw_metadata 旁路。

驗證：litedoc 16 passed〔分派 9 + P1 7：spec/旁路/URL 解碼/DocAnalyzer 映射×4/shadow〕；
全套件 677 passed（670 基線 + 7；唯一 fail＝既有 .env LOG_FORMAT flake）；SOP soft-fail 皆 warning+exc_info、
無裸 commit；section_engine/合約/其他策略/A 軌零碰（processor 為 consume）。baton 未 add、待 C8 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-LITEDOC_C3_msg.txt
```

## §9 回退方式
`git revert <C3 hash>`（或自 `.bak` 還原 litedoc_pipeline.py + test）。

---
### 結論
🟢 P1 run_phase1 落地（MinerU 文字攝入 + U2.1 DocAnalyzer 映射防偏位 + B 軌原生 metadata + URL publisher 解碼 + raw_metadata 旁路）、16 passed、全套件 677 基線、SOP 合規、零碰共用真理源/A 軌。下一步 C4 P2 六步。
