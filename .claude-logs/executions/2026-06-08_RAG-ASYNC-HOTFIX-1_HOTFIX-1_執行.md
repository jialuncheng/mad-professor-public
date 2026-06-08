# RAG-ASYNC-HOTFIX-1 HOTFIX-1 執行報告

> BE-Hotfix · section_summaries 跨譯 key 對位失效（#1 嚴重·靜默）+ dead code（#3）
> 依據：`.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md`

---

## 1. 基準與完成狀態

- **基準 Commit**：RAG-ASYNC C6 `13abdfa`（B 軌 run_phase4 改呼 rag_indexer 後）。
- **本次狀態**：代碼 + 測試已落地、全套件驗證通過；**未 commit / 未 push**（待 baron 手動）。
- **工作流類別**：BE-Hotfix（單一 Commit、無獨立 Check 階段、執行時一次性歸檔）。

## 2. 落地 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-1 | `待 baron 回填` | fix(rag): RAG-ASYNC-HOTFIX-1 — section_summaries 跨譯 key 穿線 + 移除 dead code |

## 3. diff stat（真實）

```
 pipelines/resume_pipeline.py  | 48 +++++++++++++++++++++-------------
 processor/rag_indexer.py      |  7 ++++-
 tests/test_rag_indexer.py     | 32 +++++++++++++++++++++++
 tests/test_resume_pipeline.py | 60 +++++++++++++++++++++++++++++++++++++++++++
 4 files changed, 128 insertions(+), 19 deletions(-)
```

備份（改前 .bak，archive/，git add 強制含）：
```
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_resume_pipeline.py.bak
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_rag_indexer.py.bak
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_test_rag_indexer.py.bak
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_test_resume_pipeline.py.bak
```

## 4. 真因

RAG-ASYNC 七 commit 全綠結案，但 **C5 批次產+翻的 `section_summaries` 在真實 en→zh 履歷流程 100% 取不到**——三處 key 基準不一致：
- **P2** `_collect_summary_targets` 走原文樹 → `section_summaries` key＝**原文標題 path**（`"Working Experience"`）。
- **P3** `_collect_rag_sections` 用譯文當 section title（`"工作經歷"`）。
- **P4** `rag_indexer._walk` 以譯後 title 算 node_key 查 summaries → MISS → `Chapter Summary:` 行永不出現 → Strategy B 靜默退化成 A。

非崩潰（chunks 數正常），故影子 E2E 看 `chunks≥20` 誤判成功。**#3**：`_load_index_meta`（C6 後 run_phase4 改呼 rag_indexer，已無 caller）為 dead code。

**為何全綠仍漏**：plan v2 §U3/D1 只寫「key 對位巢狀樹」、**未凍結跨 Phase 接縫 key 契約**；C5/C6 各自孤立實作（原文 key／譯文 title）單元測試皆自洽；**全程無一條 P2→P3→P4 串接 + 真翻譯器整合測試**能照出接縫斷裂。

## 5. 修法

**核心：穿一個穩定 key（原文標題 path）貫穿 P2／P3／P4。** 四處改動，全 `# === [RAG-ASYNC-HOTFIX-1 HOTFIX-1 START/END] ===` 包裹：

1. **`pipelines/resume_pipeline.py::_collect_render_slots`**：簽名加 `path_prefix=""`；計算 `node_key = f"{path_prefix}/{title}" if (path_prefix and title) else (title or path_prefix)`；title slot 附加 `"key": node_key`（slot 在翻譯前收集、text 即原文 → 與 P2 同式同基準）；children 遞迴傳 `node_key`。`key` 為附加欄、不影響 RESUME-PERF-1 rendering（用 text/level）。
2. **`pipelines/resume_pipeline.py::_collect_rag_sections`**：title section 新增 `"summary_key": slot.get("key","")`（原文 path；譯後 title 仍存於 `"title"` 供顯示）。
3. **`processor/rag_indexer.py::_walk`**：`skey = sec.get("summary_key") or ""`；`summary = (summaries.get(skey) or summaries.get(node_key) or summaries.get(title) or "").strip()`——summary_key 首選，無則退回 node_key/title（**向後相容** C3/C4 既有單元呼叫）。
4. **`pipelines/resume_pipeline.py`**：移除 dead `_load_index_meta`（#3、grep 證 0 caller），保留 C5/C1 收尾標記。

## 6. 不可動清單遵守狀態

- [x] `rag_processor.py` — 未動（git diff 空）。
- [x] `rag_retriever.py` — 未動（git diff 空）。
- [x] `pipeline_core.py` — 未動（git diff 空）。
- [x] `config.py`（EmbeddingModel）— 未動（git diff 空）。
- [x] `_collect_render_slots` rendering 輸出（RESUME-PERF-1 byte 等價）/ run_phase3 final_zh/en 輸出 — 不變（既有 P3 測試全綠）。
- [x] 主 repo 目錄 — 未讀寫。

## 7. 端到端驗證計畫結果

### 7.1 受影響模組 + 3 新測試
```
$ venv/bin/python -m pytest tests/test_rag_indexer.py tests/test_resume_pipeline.py -q
53 passed

逐一點名：
tests/test_rag_indexer.py::test_summary_key_lookup_crosslang PASSED
tests/test_rag_indexer.py::test_summary_key_absent_falls_back PASSED
tests/test_resume_pipeline.py::test_seam_p3_to_p4_section_summary_attaches PASSED
```
- `test_summary_key_lookup_crosslang`：譯後 title（工作經歷）+ summary_key=原文 path（Working Experience）+ 原文 key summaries → Chapter Summary 貼上（#1 核心修復鐵證）。
- `test_summary_key_absent_falls_back`：無 summary_key → 退回 title 查找（向後相容 C3/C4）。
- **`test_seam_p3_to_p4_section_summary_attaches`（先前缺的接縫整合測試）**：`run_phase3`（FakeTr `ZH::` 真翻譯使譯文≠原文 key）→ `ctx.rag_sections` 帶 summary_key（含巢狀 `Working Experience/Company A`）→ 以 P2 原文 key summaries 餵 P4 → Chapter Summary（頂層 + 巢狀）真的貼上。

### 7.2 全套件
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 528 passed, 3 skipped
```
- **528 passed**（HOTFIX 前 525 + 3 新測試）。
- 唯一 failed＝既知環境 flake `test_logging_config.py::test_settings_log_format_default_auto`（隔離跑 0.02s 亦失敗、非本 hotfix 引入、TODO 既載「僅 env flake」）。

### 7.3 SOP 一致性核查（BE-Hotfix 強制）
```
database：grep -E '\.commit\(\)' resume_pipeline.py rag_indexer.py | grep -v 'with .*session.*begin'
        → 無命中（合規·本 hotfix 無 DB 操作）

logging：grep 'logger.error' → rag_indexer.py:264 / :332 兩處皆既存、皆含 exc_info=True ✅
        本次 git diff 未新增/未碰 logger.error（grep 證）；新增碼無錯誤日誌 → 合規
```

### 7.4 git status -s（業務/測試碼）
```
 M pipelines/resume_pipeline.py
 M processor/rag_indexer.py
 M tests/test_rag_indexer.py
 M tests/test_resume_pipeline.py
?? .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_*.bak（4 份）
```

## 8. baron 執行命令

```bash
# 1. 備份已完成（報告 §3，archive/ 4 份 .bak）

# 2. git add 清單（4 業務/測試碼 + 4 備份 + 歸檔計畫 + 執行報告 + TODO + 2 prompts）
git add pipelines/resume_pipeline.py
git add processor/rag_indexer.py
git add tests/test_rag_indexer.py
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_rag_indexer.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_test_rag_indexer.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-1_test_resume_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-1_hotfix.md
git add .claude-logs/executions/2026-06-08_RAG-ASYNC-HOTFIX-1_HOTFIX-1_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-08_RAG-ASYNC-HOTFIX-1_HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/RAG-ASYNC-HOTFIX-1_msg.txt
git commit -F /tmp/RAG-ASYNC-HOTFIX-1_msg.txt
```

## 9. 回退方式（Rollback）

```bash
git revert <HOTFIX-1 hash>          # 或還原 4 支 archive/*.bak 至原路徑
```
`summary_key` 為附加欄、無 summary_key 時自動 fallback、無資料遷移 → 回退無副作用。

## 10. ⚠️ baron 運維（非 commit）

B 軌履歷召回行為改變（Chapter Summary 進入 chunk）→ 衝擊 golden D2/D3；**Flip/結案前須重捕 resume 單路** `venv/bin/python tools/golden_baseline.py capture resume --force`（與 TILING/SHADOW/RESUME-P3/VISION 同屬 B 軌輸出變更類）。
