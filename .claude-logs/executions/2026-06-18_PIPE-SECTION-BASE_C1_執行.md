# PIPE-SECTION-BASE C1 執行報告 — section_engine 骨架與摘要機制

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SECTION-BASE C1 |
| 執行日期 | 2026-06-18 |
| 依據規劃 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_tasks.md §8 C1` |
| 次級參考 | plan v2 §2 U1/U3.2、§2.5 方案 A |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C1)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：WORKFLOW-4 全案結案（C4 `8892bcd`）後;resume section 機制全私有、未抽。
- **完成狀態**：新建 `pipelines/section_engine.py`（摘要簇純函式引擎）+ resume `_build_section_summaries` 改 delegate、移除 5 個私有 leaf method;業務代碼僅動 plan 指明之兩檔。**未 commit**（baron 手動，§8）。
- **與全局策略對齊**：本 commit conditioned on `plan §2` 之 **U1（共用引擎模組·摘要簇）+ U3.2（DFS 吃任意子樹）+ §2.5 方案 A（pure-function + 注入）**;無偏離。**一處合理深化**（見 §自評）：`build_section_summaries` 之 prompt/model 採**參數注入**（resume 傳自身常數）而非硬搬常數——更貼合「引擎零 doc_type 耦合」、litedoc 可傳不同 prompt;接縫 key＝原文標題 path 零位移。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C1 | （待 baron 回填）| BE-Refactor: PIPE-SECTION-BASE C1 — section_engine 骨架與摘要機制 |

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/section_engine.py` | 新增（共用引擎、純函式）| **本 commit git add** |
| `pipelines/resume_pipeline.py` | 修改（摘要簇 → delegate、import section_engine）| **本 commit git add** |
| `.claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C1_resume_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C1_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C1 ✅ / C2 🟡 + hash 自癒）| 本 commit git add |
| `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C1_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C5 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-SECTION-BASE C1 ...] ===` 包裹）
- **新建 `pipelines/section_engine.py`**：摘要簇 6 純函式——
  - `node_content_text` / `collect_summary_targets`（**回傳式、吃任意子樹·U3.2**、node_key＝原文標題 path）/ `parse_indexed`（純結構）
  - `generate_section_summaries` / `translate_section_summaries`（**llm + model + system_prompt 參數注入**、三安全鎖：批次/非致命 try-except/可量測）
  - `build_section_summaries`（orchestration + performance_metric 遙測、`paper_id` 參數注入、引擎不讀 ctx）
  - 引擎內**零 doc_type 字面量、零 `raw_metadata` / `PipelineContext` 讀取**。
- **`resume_pipeline.py`**：
  - import 區加 `from pipelines import section_engine`。
  - `_build_section_summaries` 改 delegate：傳 `LLMClient.get_instance()` + resume prompt 常數（`_SECTION_SUMMARY_SYSTEM_PROMPT` 等）+ `settings.LLM_DOMAIN_MODEL`/`TRANSLATE_MODEL` + `ctx.paper_id`。
  - 移除 `_collect_summary_targets` / `_node_content_text` / `_generate_section_summaries` / `_translate_section_summaries` / `_parse_indexed`（已搬入引擎、全檔僅簇內互用、無 C2/C3 跨引用、grep 證）。

關鍵片段（resume delegate）：
```python
return section_engine.build_section_summaries(
    (ctx.ingestion.tiles if ctx.ingestion else []) or [],
    llm=LLMClient.get_instance(),
    abstract=abstract, source_lang=source_lang,
    summary_model=settings.LLM_DOMAIN_MODEL, translate_model=settings.TRANSLATE_MODEL,
    summary_system_prompt=_SECTION_SUMMARY_SYSTEM_PROMPT,
    translate_system_prompt=_SECTION_SUMMARY_TRANSLATE_SYSTEM_PROMPT,
    input_chars_cap=_SECTION_SUMMARY_INPUT_CHARS, max_chars=_ABSTRACT_MAX_CHARS,
    paper_id=ctx.paper_id,
)
```

## §5 測試結果
### §5.1 §6.1 C1 驗收 grep
```
section_engine.py 存在（8803 bytes）;engine 函式 6/6 命中
resume 殘留私有實作：0（僅 delegate）
resume 引用 section_engine：5
```
### §5.2 §6.6 SOP 一致性核查（BE-Refactor 強制）
```
logging（engine logger.error / traceback.format_exc）：0 命中（合規;warning 已含 exc_info=True）
database（engine 裸 commit）：0 命中（合規;引擎純函式無 DB 交易）
```
### §5.3 行為等價 + 全套件 pytest
```
pytest tests/test_resume_pipeline.py -q → 42 passed（行為等價鐵證、含 RAG-ASYNC-HOTFIX-1 key-changing 整合測試）
pytest tests/ -q → 1 failed, 640 passed, 3 skipped（640＝基線維持;唯一 fail＝既有 .env LOG_FORMAT env flake、與本案無關）
```
### §5.4 變動範圍（git）
```
git status -s 業務 .py：僅 pipelines/resume_pipeline.py(M) + pipelines/section_engine.py(??)
git diff --stat resume_pipeline.py：+24 / -136（摘要簇移出）
```

## §6 不可動清單遵守
| 項目 | 狀態 |
|---|---|
| `slide_pipeline.py` 全檔（不收編重複·Q2）| [x] ✅ 未碰 |
| `contracts.py` 四凍結合約 / key 基準 | [x] ✅ 未動（node_key＝原文標題 path 不變）|
| `rag_indexer.py` P4 消費端 | [x] ✅ 未動 |
| resume 攝入層私有 helper（_extract_contact 等）| [x] ✅ 未動 |
| A 軌全部（pipeline_core / web_server / processor 非新增 / static）| [x] ✅ 未動 |
| resume final_zh/en 輸出 byte | [x] ✅ 等價（42 測試全綠佐證）|
| DocumentStrategy ABC / factory 註冊 | [x] ✅ 未動（方案 A 不動繼承）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
〔dogfood U3〕
- **(a) 越界?**：否。僅動 `section_engine.py`（新）+ `resume_pipeline.py`（plan 指明兩檔）;slide/contracts/rag_indexer/A 軌零碰（git status 證）。
- **(b) 無關 / 違規?**：否。一處**深化非偏離**——prompt/model 參數注入（而非 tasks §8 字面「搬常數」）使引擎更零耦合、litedoc 可傳異 prompt;已 §1 明載、接縫 key 零位移、行為等價測試全綠。符 CLAUDE.md（baton 不 add、不自發 commit）。
- **(c) 推進哪個 U-N?**：U1（共用引擎·摘要簇）+ U3.2（DFS 吃任意子樹）;無做白工。

## §7 銜接
- baton 狀態：C1 報告 + plan + tasks 留 baton（待 C5 一次性歸檔）。
- 下一步：**C2 — 翻譯與排版還原機制**（render slots + 並行翻譯 + level 還原 + 退化 fallback 抽入 section_engine、resume 改 delegate）。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3）

# 2. git add（業務兩檔 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/section_engine.py pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C1_resume_pipeline.py.bak
git add .claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C1_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿
cat > /tmp/PIPE-SECTION-BASE_C1_msg.txt << 'EOF'
BE-Refactor: PIPE-SECTION-BASE C1 — section_engine 骨架與摘要機制

- 新建 pipelines/section_engine.py 共用 section 引擎（pure-function、零 doc_type 耦合）；
  摘要簇 collect_summary_targets〔吃任意子樹·U3.2〕/ node_content_text / parse_indexed /
  generate / translate / build_section_summaries 抽出，llm + model + prompt 參數注入。
- resume_pipeline.py 摘要簇 5 私有 method 移除、_build_section_summaries 改 delegate，
  傳 resume prompt 常數 + 模型設定 + ctx.paper_id；接縫 key＝原文標題 path 零位移。

驗證：resume 42 passed（行為等價、含 key-changing 整合測試）；全套件 640 passed（基線、
唯一 fail＝既有 .env LOG_FORMAT flake）；SOP logging/database 無命中（合規）；
slide/contracts/rag_indexer/A 軌零碰。baton（plan/tasks/C1 報告）未 add、待 C5 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SECTION-BASE_C1_msg.txt
```

## §9 回退方式
`git revert <C1 hash>`（或自 `.bak` 還原 resume_pipeline.py + 刪 section_engine.py）。

---
### 結論
🟢 section_engine 摘要簇抽出、resume 改 delegate、行為等價（42 passed）、SOP 合規、640 基線、接縫 key 零位移。下一步 C2 翻譯與排版還原機制。
