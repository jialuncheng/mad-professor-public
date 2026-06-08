# RAG-ASYNC-HOTFIX-3 HOTFIX-3 執行報告

> BE-Hotfix · zh 來源履歷 P3 改建 per-section rag_sections（#4·選 B）
> 依據：`.claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md`

---

## 1. 基準與完成狀態

- **基準 Commit**：RAG-ASYNC-HOTFIX-1（#1 slot `key`/`summary_key` 已落地）+ HOTFIX-2 之上。
- **本次狀態**：代碼 + 測試已落地、全套件驗證通過；**未 commit / 未 push**（待 baron 手動）。
- **工作流類別**：BE-Hotfix（單一 Commit、無獨立 Check、執行時一次性歸檔）。

## 2. 落地 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-3 | `待 baron 回填` | fix(rag): RAG-ASYNC-HOTFIX-3 — zh 來源履歷 P3 改建 per-section rag_sections（修 #4 單一容器） |

## 3. 變動檔案清單（含備份）

```
 pipelines/resume_pipeline.py  | 16 ++++++++--
 tests/test_resume_pipeline.py | 73 +++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 86 insertions(+), 3 deletions(-)
```
備份（改前 .bak，archive/，git add 強制含）：
```
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_resume_pipeline.py.bak
.claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_test_resume_pipeline.py.bak
```

## 4. 真因與修法

### 真因
`run_phase3` 的 `is_zh` 分支只做 `zh_text = full_text`（原文已中文、**正確跳過翻譯**），但**順帶也跳過了結構化**——en 路的 per-section 結構是 `_restore_sections_markdown` 內 `_collect_render_slots`+`_collect_rag_sections` 的副產物；is_zh 不走這條，只剩 `_single_container_sections` 兜底 → zh 來源履歷 P4 chunk 不依 section 切、size-cap 切任意 token 窗、召回粒度低於 en（**en/zh 品質不對稱**、非崩潰故易忽略）。

**為何漏**：RAG-ASYNC plan v2 只設計 en→zh 主路的 per-section chunking、**未規範 is_zh 路結構化**；C6 給 is_zh「單一容器 fallback」（合理但粗、當時聚焦 chunks=1 主修）。

### 修法（`pipelines/resume_pipeline.py::run_phase3` is_zh 分支，`# === [RAG-ASYNC-HOTFIX-3 HOTFIX-3 START/END] ===` 包裹）
```python
if is_zh:
    zh_text = full_text
    # #4-B：zh 走 tiles 不翻譯、建 per-section rag_sections（複用 en 路收集器）
    if sections:
        _slots: List[Dict[str, Any]] = []
        self._collect_render_slots(sections, 0, _slots)
        self._collect_rag_sections(_slots, {}, False, rag_sections)
    else:
        rag_sections = self._single_container_sections(full_text, ctx)
```
- `_collect_render_slots(sections, 0, _slots)`：收原文 slots（含 #1 的 `key`=原文標題 path）。
- `_collect_rag_sections(_slots, {}, False, rag_sections)`：`translate=False` → `text=原文 zh`、`summary_key=原文 path`。
- zh「原文＝譯文」→ `summary_key` 與 P2 `section_summaries` key、#1 chunk node_key **天然完全對齊**（無跨譯落差）。
- **不改** `zh_text = full_text`（final_zh 閱讀視圖 byte 不變）；無 section 退單一容器兜底。

## 5. 測試結果（真實輸出）

### 5.1 3 新測試
```
tests/test_resume_pipeline.py::test_p3_zh_source_builds_per_section PASSED
tests/test_resume_pipeline.py::test_p3_zh_no_section_falls_back_single PASSED
tests/test_resume_pipeline.py::test_p3_zh_summary_attaches PASSED
```
- `test_p3_zh_source_builds_per_section`：source_lang="zh-TW" + 2 section → `ctx.rag_sections` 為 per-section（title=技能/工作經歷、非單一「履歷全文」容器）、`summary_key`=原文 path、內容無 `ZH::` 前綴（**證 FakeTr 未被呼叫、未重譯**）。
- `test_p3_zh_no_section_falls_back_single`：zh + tiles=[] → 退單一容器兜底（len==1）。
- `test_p3_zh_summary_attaches`（接 #1）：zh `section_summaries`（原文 key）→ `build_chunk_markdown(ctx.rag_sections)` Chapter Summary 貼上（zh summary_key==P2 key、必中）。

### 5.2 不退化 + 全套件
```
$ pytest tests/test_resume_pipeline.py -q
42 passed
（en 主路抽驗 -k "phase3 or seam or parallel" → 8 passed）

$ pytest tests/ -q
1 failed, 535 passed, 3 skipped
```
- **535 passed**（HOTFIX-3 前 532 + 3 新測試）。
- 唯一 failed＝既知環境 flake `test_settings_log_format_default_auto`（非本 hotfix 引入）。

### 5.3 SOP 一致性核查（BE-Hotfix 強制）
```
database：grep -nE '\.commit\(\)' pipelines/resume_pipeline.py | grep -v 'with .*session.begin'
        → 無命中（合規·is_zh 分支無 DB 操作）

logging：本次 git diff 未新增 logger.error（grep 證）；既有 logger.error 不變、皆含 exc_info=True
```

## 6. 不可動清單遵守狀態

- [x] en 主路（`elif sections and not degraded`）/ degraded fallback — 未動（en 主路 8 測試不退化）。
- [x] `zh_text = full_text`（final_zh/en 閱讀視圖輸出）— byte 不變（既有 is_zh 測試全綠）。
- [x] `_collect_render_slots` / `_collect_rag_sections` — 僅**複用**、邏輯未改（git diff 無其定義改動、僅 is_zh 多呼叫一次）。
- [x] `rag_processor.py` / `rag_retriever.py` / `rag_indexer.py` / `config.py` / `pipeline_core.py` — 零改動（git diff 空）。
- [x] 唯一刪除行＝舊 is_zh 之 `_single_container_sections` 呼叫（已移入新分支 `else` 兜底、非邏輯刪除）。
- [x] 主 repo 目錄 — 未讀寫。

## 7. 銜接（baton 狀態 + 下一步）

- baton：HOTFIX-3 hotfix.md 已一次性 `mv` 至 `hotfixes/`、baton 無殘留。
- 執行報告直寫 `executions/`、未留 baton。
- 下一步：#5 聯絡資訊（CHAT-STRUCT-1 plan、待拍板）；WORKFLOW-3 治本（plan v3 待拍板）。RAG-ASYNC 第一性原理體檢 5 項：#1/#2/#4 已落地、#3 併入 #1、#5 另立。

## 8. baron 執行命令

```bash
# 1. 備份已完成（報告 §3，archive/ 2 份 .bak）

# 2. git add 清單（業務碼 + 測試碼 + 2 備份 + 歸檔計畫 + 執行報告 + TODO + 2 prompts）
git add pipelines/resume_pipeline.py
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_test_resume_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-08_RAG-ASYNC-HOTFIX-3_hotfix.md
git add .claude-logs/executions/2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-08_RAG-ASYNC-HOTFIX-3_HOTFIX-3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/RAG-ASYNC-HOTFIX-3_msg.txt
git commit -F /tmp/RAG-ASYNC-HOTFIX-3_msg.txt
```

## 9. 回退方式（Rollback）

```bash
git revert <HOTFIX-3 hash>          # 或還原 2 支 .bak
```
僅改 is_zh 分支之 rag_sections 建構、不動翻譯輸出與其他路；回退即恢復單一容器、無資料遷移、無副作用。

## 10. ⚠️ baron 運維（非 commit）

本 hotfix 改變 **zh 來源履歷** 的 chunk 邊界（單一容器 → per-section）→ 衝擊該類文件 golden D2/D3；**en 履歷 byte 不變**。**zh 來源履歷 golden 須重捕**（`venv/bin/python tools/golden_baseline.py capture resume --force`、en 來源不需）。
影子 E2E 觀察：zh 來源履歷 P4 log chunks 數 ≈ section 數量級（非 1 個巨容器被任意切）、retrieve 分數分布與 en 對等。
