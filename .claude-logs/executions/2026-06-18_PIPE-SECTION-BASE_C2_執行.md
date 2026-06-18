# PIPE-SECTION-BASE C2 執行報告 — 翻譯與排版還原機制

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SECTION-BASE C2 |
| 執行日期 | 2026-06-18 |
| 依據規劃 | `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_tasks.md §8 C2` |
| 次級參考 | plan v2 §2 U1、§4.2;RESUME-PERF-1 / HEADING-HOTFIX-1 / PARA-HOTFIX-1 |
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C2)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：C1（`e400789`、摘要簇）已 ship;render/restore 簇仍私有於 resume。
- **完成狀態**：render/restore 簇 8 函式抽入 `section_engine.py`、resume 對應 method 改 delegate（5 保留 + 3 移除）+ 清理 dead `ThreadPoolExecutor` import;業務代碼僅動 plan 指明兩檔。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U1`（共用引擎·翻譯與排版還原簇）+ §4.2;無偏離。**一處架構深化**（見 §自評）：`restore_sections_markdown` 改為**回傳 `(markdown, slots, zh_by_index)`、引擎不做 rag side-effect**;rag 旁路由 resume delegate 自建（C3 簇仍在 resume）→ 引擎對 rag 零認知、C2/C3 邊界乾淨、接縫 key 零位移。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C2 | （待 baron 回填）| BE-Refactor: PIPE-SECTION-BASE C2 — 翻譯與排版還原機制 |

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/section_engine.py` | 修改（追加 C2 簇 8 函式）| **本 commit git add** |
| `pipelines/resume_pipeline.py` | 修改（render/restore 簇 → delegate、清 dead import）| **本 commit git add** |
| `.claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C2_resume_pipeline.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C2_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C2 ✅ / C3 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_C2_執行.md`（本檔）/ C1 報告 / plan / tasks | baton 暫存 | **baton/ 暫存（C5 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-SECTION-BASE C2 ...] ===` 包裹）
- **`section_engine.py` 追加 C2 簇**（8 純函式）：
  - `collect_render_slots`（回傳式、吃任意子樹、key=原文標題 path、level=min(2+depth,6)）
  - `normalize_paragraph_breaks`（pipe-table-safe）/ `translate_unit`（was `_t`）/ `translate_whole`（translator 注入、`TranslateMode.NORMAL`）
  - `flatten_sections` / `own_text_len` / `is_heading_degraded`
  - `restore_sections_markdown(..., *, max_workers) -> (markdown, slots, zh_by_index)`：並行翻譯（`ThreadPoolExecutor(max_workers)` + `{future:index}` 保序 + 單 unit 失敗退原文 `event=resume_translate_unit_fallback`）；**rag side-effect 移除、回傳 slots+zh_by_index 供呼叫端自建**。
  - C2 局部 import：`ThreadPoolExecutor` + `processor.translator.TranslateMode`（翻譯契約耦合、非 doc_type）。
- **`resume_pipeline.py`**（delegate）：
  - `_restore_sections_markdown`：呼 `section_engine.restore_sections_markdown(..., max_workers=LLM_MAX_CONCURRENT)` → 拿回傳 slots/zh_by_index → `rag_sink is not None` 時呼 `_collect_rag_sections`（C3 簇仍在 resume）→ 回 markdown。
  - `_collect_render_slots`（保 out-param、run_phase3 L 呼叫端不變）/ `_translate_whole` / `_normalize_paragraph_breaks`（static、測試 L1094 直呼）/ `_is_heading_degraded`（static、run_phase3 L 呼叫）改 delegate。
  - 移除 `_t` / `_flatten_sections` / `_own_text_len`（僅內部用、無外部/測試引用）+ 清理 dead `from concurrent.futures import ThreadPoolExecutor`。

關鍵片段（restore delegate）：
```python
def _restore_sections_markdown(self, sections, inj, tr, translate, rag_sink=None):
    markdown, slots, zh_by_index = section_engine.restore_sections_markdown(
        sections, inj, tr, translate, max_workers=LLM_MAX_CONCURRENT)
    if rag_sink is not None:
        self._collect_rag_sections(slots, zh_by_index, translate, rag_sink)
    return markdown
```

## §5 測試結果
### §5.1 §6.2 C2 驗收 grep
```
engine C2 函式 8/8 命中;ThreadPoolExecutor 2（並行/限流搬入）;min(2+depth) 1（HEADING-HOTFIX-1 保留）
resume 殘留 C2 私有實作（_t/_flatten_sections/_own_text_len）：0
resume 實際 ThreadPoolExecutor import/呼叫：0（dead import 已清、僅 marker 註解）
```
### §5.2 §6.6 SOP 一致性核查（BE-Refactor 強制）
```
logging（engine logger.error / format_exc）：0 命中（合規;單 unit 失敗為 logger.warning + extra_fields、非 error）
database（engine 裸 commit）：0 命中（合規）
```
### §5.3 行為等價 + 全套件 pytest
```
pytest tests/test_resume_pipeline.py -q → 42 passed
  〔含 test_p3_parallel_order_byte_equal（byte 等拍保序）/ concurrency_capped（patch rp.LLM_MAX_CONCURRENT=2 峰值≤2）/
    unit_error_isolated（單 unit 退原文）/ degraded_single_call（退化整檔）/ normalize_paragraph_breaks 直呼〕
pytest tests/ -q → 1 failed, 640 passed, 3 skipped（640＝基線維持;唯一 fail＝既有 .env LOG_FORMAT env flake）
```
### §5.4 變動範圍（git）
```
git status -s 業務 .py：僅 pipelines/resume_pipeline.py(M) + pipelines/section_engine.py(M)
diff stat：resume −192 / section_engine +201
```
- **並行測試保真關鍵**：測試 `monkeypatch.setattr(rp, "LLM_MAX_CONCURRENT", 2)` patch resume 模組全域 → delegate 讀 `LLM_MAX_CONCURRENT` 傳 `max_workers` → 引擎 cap 生效（故 `max_workers` 參數化、非引擎自讀全域）。

## §6 不可動清單遵守
| 項目 | 狀態 |
|---|---|
| `slide_pipeline.py` 全檔（含其 _normalize_paragraph_breaks/_translate_whole 重複·Q2）| [x] ✅ 未碰 |
| `contracts.py` 四凍結合約 / key 基準 | [x] ✅ 未動（key=原文標題 path 不變）|
| `rag_indexer.py` P4 消費端 | [x] ✅ 未動 |
| resume C3 簇（_collect_rag_sections / _single_container_sections / _render_meta_header）| [x] ✅ 未動（留 C3）|
| resume 攝入層私有 helper | [x] ✅ 未動 |
| A 軌全部 | [x] ✅ 未動 |
| resume final_zh/en 輸出 byte | [x] ✅ 等價（42 測試含 byte 等拍佐證）|
| DocumentStrategy ABC / factory | [x] ✅ 未動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅動 `section_engine.py` + `resume_pipeline.py`（plan 指明兩檔）;slide/contracts/rag_indexer/C3 簇/A 軌零碰（git status 證）。
- **(b) 無關 / 違規?**：否。一處**架構深化非偏離**——`restore_sections_markdown` 回傳 slots+zh_by_index 而非內部填 rag_sink（tasks §8 C2「原值搬移」字面），使引擎對 rag 零耦合、C2/C3 邊界乾淨、行為等價（rag 收集移到 delegate、同 slots/zh_by_index、順序無關）;已 §1/§4 明載。順帶清 dead import（屬本簇移出之收尾）。符 CLAUDE.md（baton 不 add、不自發 commit）。
- **(c) 推進哪個 U-N?**：U1（共用引擎·翻譯與排版還原簇）;無做白工。

## §7 銜接
- baton 狀態：C1/C2 報告 + plan + tasks 留 baton（待 C5 一次性歸檔）。
- 下一步：**C3 — rag 旁路與 meta header 純格式化器**（`_collect_rag_sections`/`_single_container_sections` 抽入 + `_render_meta_header` 重構為純格式化器 U3.1〔收 `(Label,Value)` tuples、引擎零讀 raw_metadata〕）。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3）

# 2. git add（業務兩檔 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/section_engine.py pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-18_PIPE-SECTION-BASE_C2_resume_pipeline.py.bak
git add .claude-logs/prompts/2026-06-18_PIPE-SECTION-BASE_C2_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿
cat > /tmp/PIPE-SECTION-BASE_C2_msg.txt << 'EOF'
BE-Refactor: PIPE-SECTION-BASE C2 — 翻譯與排版還原機制

- section_engine.py 追加 render/restore 簇：collect_render_slots〔key=原文標題 path·
  level=min(2+depth,6)〕/ normalize_paragraph_breaks / translate_unit / translate_whole /
  flatten_sections / own_text_len / is_heading_degraded /
  restore_sections_markdown〔ThreadPoolExecutor 並行+保序+單 unit 退原文、max_workers 注入；
  回傳 (markdown, slots, zh_by_index)、引擎不做 rag side-effect〕。
- resume_pipeline.py 對應 5 method 改 delegate〔restore delegate 以回傳 slots+zh_by_index 呼
  _collect_rag_sections 建旁路〕、移除 _t/_flatten_sections/_own_text_len + 清 dead
  ThreadPoolExecutor import。

驗證：resume 42 passed〔含並行 byte 等拍/concurrency_capped/unit_error_isolated/退化〕；
全套件 640 passed（基線、唯一 fail＝既有 .env LOG_FORMAT flake）；SOP logging/database 無命中；
slide/contracts/rag_indexer/C3 簇/A 軌零碰；接縫 key=原文標題 path 零位移。baton 未 add、待 C5 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SECTION-BASE_C2_msg.txt
```

## §9 回退方式
`git revert <C2 hash>`（或自 `.bak` 還原 resume_pipeline.py + git revert section_engine C2 區塊）。

---
### 結論
🟢 render/restore 簇抽出、resume 改 delegate、引擎對 rag 零耦合（回傳 slots+zh_by_index）、行為等價（42 passed）、SOP 合規、640 基線、接縫 key 零位移。下一步 C3 rag 旁路 + meta header 純格式化器。
