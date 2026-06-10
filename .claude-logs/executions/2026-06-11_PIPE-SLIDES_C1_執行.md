# PIPE-SLIDES C1 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES C1 — Skeleton & Register（骨架與註冊）|
| 執行日期 | 2026-06-11 |
| 依據規劃 | `baton/2026-06-11_PIPE-SLIDES_..._tasks.md §8 C1`（plan v1〔v1.1〕）|
| 次級參考 | PIPE-RESUME C1/C7-hotfix 範式 |
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ §6.1 驗收全綠（4 pytest + 2 grep）；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：PIPE-SYNC-2 C4 收官後 HEAD（`43ad9c6`）。
- **本次**：SlidePipeline 骨架 + Factory 註冊 + 分派測試；**僅三檔**（工作範圍硬限）；影子旗標外零行為；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C1 | `待 baron 回填` | BE-Refactor: PIPE-SLIDES C1 — Skeleton & Register |

## §3 變動檔案清單

```
新建：pipelines/slide_pipeline.py        （61 行：register + 四方法 stub + threshold=3 + 四 Phase 規格 docstring）
新建：tests/test_slide_pipeline.py       （4 測試：註冊/分派/門檻/stub 合約）
修改：pipelines/__init__.py              （+6 行 import 包裹、C1 標記 1 對）
```
備份（入版控、審計）：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES_C1_pipelines___init__.py.bak
```

## §4 修法說明

### `pipelines/slide_pipeline.py`（新建、免中段包裹）
```python
@PipelineFactory.register('slides')
class SlidePipeline(DocumentStrategy):
    rag_char_threshold: int = 3   # U11：保 'SiC'/'THD' 級短技術詞
    def run_phase1(...): raise NotImplementedError("...C2 落地")
    # phase2/3/4 同式（C3/C4/C5）
```
- docstring 完整載四 Phase 規格藍圖（P1 存圖+Vision temp=0+封面+去重 / P2 六步 key=`p{N}_{標題}` / P3 逐頁+alt 對齊+旁路 / P4 rag_indexer）——後續 commit 對照落地。
- stub 拋 NotImplementedError＝strict 合約：影子 B 軌觸發時被 Orchestrator 攔截、線上 0 風險。

### `pipelines/__init__.py`（`# === [PIPE-SLIDES C1 START/END] ===` 包裹）
```python
from pipelines import slide_pipeline  # noqa: E402,F401
```
- C7-hotfix 教訓：runtime 不 import 具體策略 → `get_strategy('slides')` 回 NullStrategy 阻斷；顯式 import 觸發裝飾器註冊。

### `tests/test_slide_pipeline.py`（新建、4 測試）
註冊（`_registry` 含 'slides'、經套件入口 import 路）/ 分派（回 SlidePipeline 非 NullStrategy）/ 門檻=3 / stub 四 Phase 拋 NotImplementedError。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -v
test_slides_registered_in_factory PASSED
test_get_strategy_returns_slide_pipeline PASSED
test_slide_rag_char_threshold_is_3 PASSED
test_stub_phases_raise_not_implemented PASSED
========================= 4 passed in 0.67s =========================

$ grep -n "register('slides')" pipelines/slide_pipeline.py → L36 命中 ✅
$ grep -n 'slide_pipeline' pipelines/__init__.py → L42/L44 命中 ✅

$ venv/bin/python -m pytest tests/ -q
1 failed, 560 passed, 3 skipped
  唯一 failed = 既知 env flake test_settings_log_format_default_auto（與 C1 無關）；560 passed（556+4 新）
```

### §5.3 SOP 核查
```
grep -nE 'logger.error|format_exc|\.commit\(\)' slide_pipeline.py test_slide_pipeline.py → 無命中（合規；stub 無 log/DB）
```

## §6 不可動清單遵守

- [x] **僅三檔**：git status 證（M `__init__.py` + ?? 兩新檔、零其他 .py）。
- [x] A 軌全部 / resume_pipeline / 三真理源 / rag_indexer / contracts / orchestrator / factory / web_server——零改動。
- [x] C1 標記平衡（1 START / 1 END）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本報告暫存（嚴禁 mv/git add）；plan + tasks 續留。
- **下一步＝C2**（P1 Vision Ingestion：每頁存圖 + Vision temp=0 + 條件滾動 + 封面判定 + 統計去重、U1-U4），待 baron 下達 C2 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/2026-06-11_PIPE-SLIDES_C1_pipelines___init__.py.bak）

# 2. git add 清單（實體代碼 + .bak + 提示詞 + TODO；嚴禁 baton/ 執行報告）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add pipelines/__init__.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES_C1_pipelines___init__.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES_C1_msg.txt
git commit -F /tmp/PIPE-SLIDES_C1_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <C1 hash>   # 或刪兩新檔 + 還原 __init__ .bak；stub 零行為、回退無副作用
```
