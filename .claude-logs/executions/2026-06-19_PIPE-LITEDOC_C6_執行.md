# PIPE-LITEDOC C6 執行報告 — P4 Async RAG（rag_indexer ≥10 + 雙語標題）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC C6 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md §8 C6` |
| 次級參考 | plan v3 §2 U6/U7;resume run_phase4 鏡像;rag_indexer（RAG-ASYNC 共用引擎）|
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C6)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C5（P3 size-gate）已 ship;litedoc run_phase4 為 strict stub（litedoc 四 Phase 至此全實作）。
- **完成狀態**：實作 `run_phase4`（消費共用 rag_indexer、≥10 門檻、雙語標題）+ 3 P4 測試 + 移除已實作 phase 的 strict-stub 測試。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U6`（P4 消費 rag_indexer、零改引擎、門檻 ≥10）+ U7（接縫 key=原文標題 path、section_summaries 同基準）;無偏離。translated_title 讀 P3 旁路（U5c/U6）、非 resume 捷徑同取。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C6 | （待 baron 回填）| BE-Refactor: PIPE-LITEDOC C6 — P4 Async RAG（rag_indexer ≥10 + 雙語標題）|

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | 修改（run_phase4）| **本 commit git add** |
| `tests/test_litedoc_pipeline.py` | 修改（追加 3 P4 測試、移除已實作 stub 測試）| **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C6_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C6_test_litedoc_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C6_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C6 ✅ / C7 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C6_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C8 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-LITEDOC C6 ...] ===` 包裹）
- **`run_phase4`**：① 惰性 `from processor import rag_indexer`（B 軌自有、零 rag_processor）② 輸入＝`ctx.rag_sections`（P3 旁路）+ `ctx.glossary_ready.section_summaries`（P2）③ `vectors_dir`/`rag_tree_path` 取自 paper_manager ④ **雙語標題**：`title=ctx.ingestion.title`、`translated_title` 讀 `ctx.raw_metadata["translated_title"]["value"]`（P3 旁路、容錯 fallback title）⑤ `paper_db_id`（None → rag_indexer 內部降級）⑥ `rag_indexer.index(rag_sections, section_summaries, "litedoc", vectors_dir, paper_db_id, rag_tree_path, title, translated_title)` **門檻走 is_chunk_meaningful 預設 ≥10**（litedoc 不在 resume/slides ≥3 tuple、**rag_indexer 零改**）⑦ 異常 logger.warning(exc_info) 後**拋出**（交 Orchestrator 標 rag_status='failed'、不阻 reading_ready）→ RagDbSpec。

關鍵片段：
```python
title = (ctx.ingestion.title if ctx.ingestion else None) or ctx.paper_id
_tt = (ctx.raw_metadata or {}).get("translated_title")
translated_title = (_tt.get("value") if isinstance(_tt, dict) else _tt) or title
spec = rag_indexer.index(
    rag_sections, section_summaries, "litedoc", vectors_dir,
    paper_db_id=paper_db_id, rag_tree_path=str(rag_tree_path),
    title=title, translated_title=translated_title,
)   # 門檻 ≥10（litedoc 走 else 預設、rag_indexer 零改）
```

## §5 測試結果
### §5.1 §6.6 C6 驗收 grep
```
run_phase4 / rag_indexer.index / "litedoc" / translated_title= 全命中
rag_indexer.py 含 litedoc：0（引擎未被改）;rag_indexer.py 在本次 diff：0
```
### §5.2 P4 測試 + 全套件 pytest
```
pytest tests/test_litedoc_pipeline.py -q → 24 passed
  〔P4 3：呼 rag_indexer.index 傳 'litedoc'+雙語標題+消費 P2 section_summaries / 門檻 else 預設 ≥10〔inspect
    rag_indexer.is_chunk_meaningful 證 litedoc 未入 ≥3 tuple、引擎零改〕/ 失敗拋出不靜默吞〕
pytest tests/ -q → 1 failed, 685 passed, 3 skipped（685＝683 基線 + 2;唯一 fail＝既有 .env LOG_FORMAT env flake〕
```
### §5.3 §6.9 SOP 一致性核查（BE-Refactor 強制）
```
logging（logger.error / format_exc）：0 命中（合規;失敗為 logger.warning + exc_info=True 後拋出）
database（裸 commit）：0 命中（合規;paper_chunks 寫庫委 rag_indexer 內部極短交易）
```
### §5.4 變動範圍（git）
```
git status -s 業務/測試 .py：僅 pipelines/litedoc_pipeline.py(M) + tests/test_litedoc_pipeline.py(M)
```

## §6 不可動清單遵守
| 項目（tasks §7）| 狀態 |
|---|---|
| **`processor/rag_indexer.py`** | [x] ✅ **零改**（litedoc 走 else 預設 ≥10、不動 :69 tuple;grep litedoc=0、不在 diff）|
| `section_engine.py` / `contracts.py` / `context.py` | [x] ✅ 零碰 |
| `resume_pipeline.py` / `slide_pipeline.py` | [x] ✅ 零碰 |
| 三大共用真理源 / A 軌全部 | [x] ✅ 零碰（rag_indexer 為 consume）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅改 litedoc_pipeline.py + test;**rag_indexer 零改**（grep + diff 雙證）;section_engine/合約/其他策略零碰。
- **(b) 無關 / 違規?**：否。run_phase4 消費共用 rag_indexer、傳 'litedoc' + 雙語標題（translated_title 讀 P3 旁路、非捷徑）;異常拋出交 Orchestrator（不靜默吞、合 plan U6）。msg 簽名校正 Opus 4.8。
- **(c) 推進哪個 U-N?**：U6（P4 Async RAG ≥10）+ U7（接縫 section_summaries 同基準）;無做白工。litedoc 四 Phase 全鏈至此貫通。

## §7 銜接
- baton 狀態：C1-C6 報告 + plan + tasks 留 baton（待 C8 一次性歸檔）。
- 下一步：**C7 — 單元與接縫整合測試（雙鎖）**：補全 test_litedoc_pipeline.py——分派四路 + P1-P4 契約整合 + **§7.2 P2→P3→P4 key-changing 整合測試**（真翻譯改 title、斷言 section_summaries key 與 rag_sections summary_key 同基準＝原文標題 path）。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3、.bak 本 commit git add）

# 2. git add（業務 + 測試 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C6_litedoc_pipeline.py.bak .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C6_test_litedoc_pipeline.py.bak
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C6_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC_C6_msg.txt）
cat > /tmp/PIPE-LITEDOC_C6_msg.txt << 'EOF'
BE-Refactor: PIPE-LITEDOC C6 — P4 Async RAG（rag_indexer ≥10 + 雙語標題）

- litedoc_pipeline.run_phase4：消費共用 rag_indexer.index（ctx.rag_sections + P2 section_summaries、
  doc_type='litedoc'、vectors_dir/rag_tree_path、paper_db_id 降級），門檻走 is_chunk_meaningful 預設 ≥10
  （litedoc 不在 resume/slides ≥3 tuple、rag_indexer 零改）；四產物；異常拋出交 Orchestrator 標
  rag_status='failed'、不阻 reading_ready。
- 雙語標題：title=ingestion.title、translated_title 讀 P3 旁路 ctx.raw_metadata["translated_title"]
  （非 resume 捷徑同取）。

驗證：litedoc 24 passed〔P4：傳 'litedoc'+雙語標題、門檻 else ≥10〔inspect 證引擎未改〕、失敗拋出〕；
全套件 685 passed（唯一 fail＝既有 .env LOG_FORMAT flake）；rag_indexer 零改（grep litedoc=0、不在 diff）；
SOP logger.error 0/裸 commit 0；section_engine/合約/其他策略/A 軌零碰。baton 未 add、待 C8 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-LITEDOC_C6_msg.txt
```

## §9 回退方式
`git revert <C6 hash>`（或自 `.bak` 還原 litedoc_pipeline.py + test）。

---
### 結論
🟢 P4 落地（消費共用 rag_indexer、門檻 ≥10、rag_indexer 零改、雙語標題讀 P3 旁路、異常拋出不阻主鏈）、24 passed、全套件 685 基線、SOP 合規。**litedoc 四 Phase 全鏈貫通**。下一步 C7 單元與接縫整合測試（雙鎖·§7.2）。
