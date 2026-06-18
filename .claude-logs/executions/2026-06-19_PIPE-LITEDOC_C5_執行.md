# PIPE-LITEDOC C5 執行報告 — P3 size-gate 翻譯與 HTML 扉頁還原（含雙語標題鏈）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC C5 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md §8 C5` |
| 次級參考 | plan v3 §2 U5/U5b/U5c;resume run_phase3 鏡像;section_engine（C1-C2 已落地）|
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C5)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C4（P2 六步）已 ship;litedoc run_phase3 為 strict stub。
- **完成狀態**：實作 `run_phase3`（size-gate + HTML 扉頁 + U5c 雙語標題鏈 + rag 旁路 + zh edge）+ 2 P3 helper + 6 P3 測試。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U5/U5b/U5c`（size-gate 分流 / render_meta_header_html HTML 扉頁 / translated_title 三路）;無偏離。全消費 section_engine（C1 formatter + C2 翻譯還原簇）;translated_title 經既有 raw_metadata 旁路傳 P4（不動凍結合約/context.py）。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C5 | （待 baron 回填）| BE-Refactor: PIPE-LITEDOC C5 — P3 size-gate 翻譯與 HTML 扉頁還原（含雙語標題鏈）|

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 修改（run_phase3 + 2 helper）| **本 commit git add** |
| `tests/test_litedoc_pipeline.py` | 修改（追加 6 P3 測試）| **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C5_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C5_test_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C5_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C5 ✅ / C6 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C5_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C8 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-LITEDOC C5 ...] ===` 包裹）
- **`run_phase3`**：① `InjectionContext(lcc/glossary/zh_summary/domain_name/doc_type=ctx.doc_type)`〔news/web → 對應 STYLE_HINTS〕② **size-gate**（`getattr(settings,"LITEDOC_WHOLE_TRANSLATE_THRESHOLD",15000)`、免動 settings.py）：`is_zh`→不重譯;`len(full_text)<門檻 or 無 section or is_heading_degraded`→`translate_whole`（一鍵）;否則 `restore_sections_markdown`（逐 section 並行、max_workers=LLM_MAX_CONCURRENT）③ **U5c translated_title 三路**：zh→title / 分段→`_extract_translated_title`（頂層 title slot zh）/ 一鍵→`translate_unit(title,…,"title")` ④ rag 旁路：`collect_rag_sections`（分段/zh、summary_key=原文標題 path）或 `single_container_sections`（一鍵/兜底）→ `ctx.rag_sections` ⑤ **HTML 扉頁**：`_render_meta_headers` 組 `# 標題`（zh 譯題/en 原題）+ `section_engine.render_meta_header_html`（authors/venue〔publisher〕/date、Zero Schema Coupling）prepend ⑥ translated_title 存 `ctx.raw_metadata["translated_title"]={value,source,confidence}`（PIPE-SLIDES-HOTFIX-1b 旁路範式）→ BilingualMarkdownSpec（rag_tree_json=None）。
- **helpers**：`_extract_translated_title`（取頂層 title slot 譯後）/ `_render_meta_headers`（呼叫端抽欄 + lang）。

關鍵片段（size-gate + U5c）：
```python
degraded = bool(sections) and section_engine.is_heading_degraded(sections)
whole_mode = (len(full_text) < threshold) or (not sections) or degraded
if whole_mode:
    zh_text = section_engine.translate_whole(full_text, inj, tr, True)
    translated_title = section_engine.translate_unit(title, inj, tr, "title") if title else title
else:
    zh_text, slots, zh_by_index = section_engine.restore_sections_markdown(sections, inj, tr, True, max_workers=settings.LLM_MAX_CONCURRENT)
    section_engine.collect_rag_sections(slots, zh_by_index, True, rag_sections)
    translated_title = self._extract_translated_title(slots, zh_by_index) or title
```

## §5 測試結果
### §5.1 §6.5 C5 驗收 grep
```
run_phase3 / WHOLE_TRANSLATE_THRESHOLD / translate_whole / restore_sections_markdown /
render_meta_header_html / collect_rag_sections / translated_title / is_heading_degraded 全命中
```
### §5.2 P3 測試 + 全套件 pytest
```
pytest tests/test_litedoc_pipeline.py -q → 22 passed
  〔P3 6：size-gate whole / size-gate section〔summary_key=原文標題 path〕/ translated_title whole〔ZH::title〕/
    translated_title section〔頂層 slot〕/ HTML 扉頁〔zh 譯題 en 原題 + paper-header-meta〕/ zh edge 不重譯〕
pytest tests/ -q → 1 failed, 683 passed, 3 skipped（683＝678 基線 + 5;唯一 fail＝既有 .env LOG_FORMAT env flake〕
```
### §5.3 §6.9 SOP 一致性核查（BE-Refactor 強制）
```
logging（logger.error / format_exc）：0 命中（合規;退化 fallback 為 logger.warning）
database（裸 commit）：0 命中（合規;P3 無 DB 交易）
```
### §5.4 變動範圍（git）
```
git status -s 業務/測試 .py：僅 pipelines/litedoc_pipeline.py(M) + tests/test_litedoc_pipeline.py(M)
```

## §6 不可動清單遵守
| 項目（tasks §7）| 狀態 |
|---|---|
| `section_engine.py` | [x] ✅ 零碰（consume translate_whole/restore/collect_rag_sections/render_meta_header_html）|
| `rag_indexer.py` / **`contracts.py` 凍結合約 / `context.py`** | [x] ✅ 零碰（translated_title 走既有 raw_metadata 旁路、未加欄位）|
| `resume_pipeline.py` / `slide_pipeline.py` | [x] ✅ 零碰 |
| 三大共用真理源 / A 軌全部 | [x] ✅ 零碰（僅 import 消費）|
| `settings.py` | [x] ✅ 未動（門檻用 getattr 預設 15000）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅改 litedoc_pipeline.py + test;section_engine/contracts/context/settings/其他策略零碰（translated_title 走既有旁路、未動凍結合約）。
- **(b) 無關 / 違規?**：否。run_phase3 全鏈對應 U5/U5b/U5c;size-gate 門檻 getattr 免動 settings;translated_title handoff 沿用 PIPE-SLIDES-HOTFIX-1b 旁路範式（避開 context.py 改動、守 C5 scope）。msg 簽名校正 Opus 4.8。
- **(c) 推進哪個 U-N?**：U5（size-gate + 還原）+ U5b（HTML 扉頁消費）+ U5c（雙語標題三路）;無做白工。

## §7 銜接
- baton 狀態：C1-C5 報告 + plan + tasks 留 baton（待 C8 一次性歸檔）。
- 下一步：**C6 — P4 Async RAG**（`rag_indexer.index(ctx.rag_sections, section_summaries, 'litedoc', …, title, translated_title)`、門檻 ≥10、四產物;translated_title 讀 `ctx.raw_metadata["translated_title"]`）→ RagDbSpec。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3、.bak 本 commit git add）

# 2. git add（業務 + 測試 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C5_litedoc_pipeline.py.bak .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C5_test_litedoc_pipeline.py.bak
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C5_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC_C5_msg.txt）
cat > /tmp/PIPE-LITEDOC_C5_msg.txt << 'EOF'
BE-Refactor: PIPE-LITEDOC C5 — P3 size-gate 翻譯與 HTML 扉頁還原（含雙語標題鏈）

- litedoc_pipeline.run_phase3：size-gate〔<15k 或無 section 或 heading 退化→translate_whole 一鍵；
  ≥15k→restore_sections_markdown 逐 section 並行〕+ U5c translated_title 三路〔zh→title／分段→頂層 title
  slot 譯後／一鍵→translate_unit〕+ render_meta_header_html HTML 扉頁〔# 標題：zh 譯題 en 原題〕+
  collect_rag_sections→ctx.rag_sections + zh edge 不重譯。
- translated_title 經既有 ctx.raw_metadata 旁路傳 P4（PIPE-SLIDES-HOTFIX-1b 三欄 dict 範式、不動凍結合約/context）。
- size-gate 門檻 getattr(settings,"LITEDOC_WHOLE_TRANSLATE_THRESHOLD",15000)、免動 settings.py。

驗證：litedoc 22 passed〔size-gate×2／translated_title×2／HTML 扉頁／zh edge〕；
全套件 683 passed（唯一 fail＝既有 .env LOG_FORMAT flake）；SOP logger.error 0／裸 commit 0；
section_engine/contracts/context/settings/其他策略/A 軌零碰。baton 未 add、待 C8 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-LITEDOC_C5_msg.txt
```

## §9 回退方式
`git revert <C5 hash>`（或自 `.bak` 還原 litedoc_pipeline.py + test）。

---
### 結論
🟢 P3 落地（size-gate 一鍵/逐 section 分流 + heading 退化 fallback + U5c 雙語標題三路 + HTML 扉頁〔zh 譯題/en 原題〕+ rag 旁路 + zh edge + translated_title 旁路傳 P4）、22 passed、全套件 683 基線、SOP 合規、零碰共用真理源/合約/A 軌。下一步 C6 P4 Async RAG。
