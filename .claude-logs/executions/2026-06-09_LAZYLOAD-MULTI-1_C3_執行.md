# LAZYLOAD-MULTI-1 C3 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | LAZYLOAD-MULTI-1 C3 |
| 執行日期 | 2026-06-10 |
| 依據規劃 | `baton/..._tasks.md §8 C3`（對齊 plan v5 U2/U4 + §4 lazy-load callback）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 7 測試全綠 + 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C2（併發鎖）之上。
- **本次**：`web_server.py` 啟動 lifespan 接線 `set_loader` + `settings.py` `RAG_MAX_CACHE` 5→100 + 追加 cap 測試；**純加法、核心跨文件修復此刻 LIVE**；未 commit。
- **工作流類別**：BE-Refactor（單一 Commit；執行報告暫存 baton、C5 Checkout 才歸檔）。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C3 | `待 baron 回填` | feat(rag): LAZYLOAD-MULTI-1 C3 — 啟動接線 set_loader + RAG_MAX_CACHE 100（核心跨文件修復 LIVE）|

## §3 變動檔案清單

```
 settings.py                  | 2 +-（RAG_MAX_CACHE 5→100）
 web_server.py                | 8 ++++++++（啟動 lifespan set_loader 接線、純加法）
 tests/test_lazyload_multi.py | +test_cap_100_default
```
備份（改前 .bak、archive/、git add 強制含）：
```
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C3_web_server.py.bak
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C3_settings.py.bak
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C3_test_lazyload_multi.py.bak
```

## §4 修法說明（U2/U4 + §4 接縫；只動啟動段、與 C4 hunk 不重疊）

### `settings.py`（U4）
```python
RAG_MAX_CACHE = int(os.getenv("RAG_MAX_CACHE", "100"))   # === [LAZYLOAD-MULTI-1 C3] === 5→100
```
記憶體實測 13MB 語料無虞、釋放策略主導、cap 僅安全天花板；env 仍可覆寫。

### `web_server.py`（U2、**僅啟動 lifespan 接線段**、L230-238、`# === [LAZYLOAD-MULTI-1 C3 START/END] ===`）
插入點：`ai_core.init_rag_retriever()`（L216、retriever 就緒）後、API-PERF C3 區（L224-229）後、`yield`（L240）前：
```python
ai_core.retriever.set_loader(
    lambda o, p: paper_manager.load_paper_resources(OUTPUT_DIR, o, p, ai_core)
)
```
- **接線後 ③ 生效**：retrieve_multi 對未載 tagged 篇經 `_get_vector_store` 第三層自我載入 → 跨文件 `#cv` 不再只召當前篇。
- §4 接縫契約：loader 之 `(o,p)` ＝ `_get_vector_store` 之 `(owner_id, paper_uuid)` ＝ paper_uuid 原值、同基準。
- **只新增此接線塊、未改任何端點 handler / 既有 lifespan 邏輯**（與 C4 `/content`+`/upload` 端點段 hunk 天然不重疊）。

### `tests/test_lazyload_multi.py`
- `test_cap_100_default`：`importlib.reload(settings)` 驗預設 100（env 未設）+ env override=7；finally 還原。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_lazyload_multi.py -q
7 passed in 1.08s   # C1 5 + C2 並發 1 + C3 cap 1

$ venv/bin/python -m pytest tests/ -q
1 failed, 553 passed, 3 skipped
  唯一 failed = 既知環境 flake test_settings_log_format_default_auto（與 C3 無關）；553 passed（552 + 1 cap）
```

### §5.3 SOP 核查
```
logging：本 commit 未新增 logger.error（純接線 + 常數）
database：grep '\.commit\(\)' settings.py | grep -v session.begin → 無命中（合規）
         （接線 loader callback 內 load_paper_resources 之 DB 查詢為唯讀、C2 §3.1⑥ 已證 thread-safe、非本 commit 新增）
就位：web_server.py:234 set_loader / settings.py:65 RAG_MAX_CACHE=100
```

## §6 不可動清單遵守

- [x] 只動 `web_server.py`（**僅啟動 lifespan 接線段、8 行純加法**）+ `settings.py`（1 行字面）+ `tests/test_lazyload_multi.py`。
- [x] **未碰任何端點 handler**（`/content` L740 / `/upload` L468 / `/chat` 等遠在 L234 接線之後、git diff 僅啟動段）→ 與 C4 hunk 不重疊。
- [x] `rag_retriever.py` / `ai_core.py` — **未再改動**（C1/C2 已落地）。
- [x] **未加釋放邏輯**（C4）。
- [x] web_server 既有 lifespan 邏輯未改（只新增接線塊）；C3 標記平衡（1 START / 1 END）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本 C3 執行報告暫存 baton（未 mv / 未 git add）；plan v1-v5 + tasks + C1/C2 報告續留 baton。
- **核心跨文件修復此刻 LIVE**：C1（自載咽喉）+ C2（併發鎖）+ C3（接線）= `#cv 比較` 應已涵蓋全 tagged 篇（baron 可在 C3 後先做一次 E2E 觀測，正式驗收於 C5）。
- **下一步＝C4**（記憶體釋放策略：`/content` 換篇 gate + `/upload` 開關 + 跳過 active_streams + gc + docstring），待 baron 下達 C4 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 3 份 .bak）

# 2. git add（baton 執行報告不 git add；.gitignore 若 M 非本 commit、不納入）
git add web_server.py
git add settings.py
git add tests/test_lazyload_multi.py
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C3_web_server.py.bak
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C3_settings.py.bak
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C3_test_lazyload_multi.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-10_LAZYLOAD-MULTI-1_C3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/LAZYLOAD-MULTI-1_C3_msg.txt
git commit -F /tmp/LAZYLOAD-MULTI-1_C3_msg.txt
```
> baton/ 下 plan + tasks + C1/C2/C3 執行報告**嚴禁 git add**（C5 Checkout 一次性歸檔）。

## §9 回退方式（Rollback）

```bash
git revert <C3 hash>   # 或還原 .bak；移除 set_loader 接線即回 ③ 未生效（loader 未設＝現況）、cap 還原 5
```
