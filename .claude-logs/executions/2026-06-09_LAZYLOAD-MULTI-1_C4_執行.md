# LAZYLOAD-MULTI-1 C4 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | LAZYLOAD-MULTI-1 C4 |
| 執行日期 | 2026-06-10 |
| 依據規劃 | `baton/..._tasks.md §8 C4`（對齊 plan v5 U5/U9/P4 + §4 跳過活躍串流/當前篇 + §3.5 F1 + §3.6 M1）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 10 測試全綠（含 3 釋放）+ 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C3（接線 LIVE）之上。
- **本次**：`web_server.py` 釋放策略（helper + `/content` 換篇 gate + `/upload` 開關 hook）+ `settings.py` `RELEASE_ON_UPLOAD` + `ai_core.py` docstring 修；未 commit。
- **工作流類別**：BE-Refactor（單一 Commit；執行報告暫存 baton、C5 Checkout 才歸檔）。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C4 | `待 baron 回填` | feat(rag): LAZYLOAD-MULTI-1 C4 — 記憶體釋放策略（換篇/上傳全清跳過活躍串流 + gc）|

## §3 變動檔案清單

```
 web_server.py                | 42 +（import gc + _owner_current_paper + helper + /content gate + /upload hook + None 防呆）
 ai_core.py                   | 6 +1-（remove_paper docstring 修·P4）
 settings.py                  | 3 +（RELEASE_ON_UPLOAD）
 tests/test_lazyload_multi.py | +3 釋放測試
```
備份（改前 .bak、archive/、git add 強制含）：
```
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_web_server.py.bak
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_ai_core.py.bak
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_settings.py.bak
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_test_lazyload_multi.py.bak
```

## §4 修法說明（U5/U9/P4 + §4；只動端點段+helper、不碰 C3 啟動段）

### `settings.py`（`# === [LAZYLOAD-MULTI-1 C4] ===`）
```python
RELEASE_ON_UPLOAD = os.getenv("RELEASE_ON_UPLOAD", "true").lower() == "true"   # 預設 on
```

### `web_server.py`（**僅模組級 helper/狀態 + `/content` + `/upload` 端點段**）
- `import gc`（補）。
- 模組級 `_owner_current_paper: dict = {}`（owner→當前 paper_uuid、F1 gate 用）。
- helper `_release_caches_except_active(owner_id)`（U9/M1）：
  - **`if ai_core is None: return`**（lifespan 未初始化/測試防呆——修 upload 測試 None.attr）；
  - `active = {s.paper_uuid for s in active_streams.values() if not s.done and s.owner_id==owner_id}`（U9 豁免活躍串流）；
  - 快照該 owner cached uuid（`_paper_cache` + `paper_vector_paths`）後逐篇 `ai_core.remove_paper`（skip active）；
  - 末 `gc.collect()` + `logger.info`（M1 騰 FAISS C++ 給 MinerU）。
- `/content`（`paper_content` 回傳前、`# === C4 START/END ===`）：`if _owner_current_paper.get(uid) != paper_id: release; update`（**F1：語言切換同篇不放**）。
- `/upload`（`upload_paper` 驗證後、流式寫入前、`# === C4 START/END ===`）：`if settings.RELEASE_ON_UPLOAD: release`（騰 RAM 給 MinerU）。
- **未碰 C3 啟動 lifespan set_loader 接線段；未改 `/content` 讀檔回傳 / `/upload` 上傳派發既有邏輯（只加 hook）。**

### `ai_core.py`（P4）
`remove_paper` docstring 移除「當前對話上下文」誤述（body 本就未清對話、僅修文字）。

### `tests/test_lazyload_multi.py` 追加 3
- `test_release_skips_active_stream`（U9）：mock ai_core/active_streams → done==False 篇豁免、其餘清（含 done==True）。
- `test_release_only_on_actual_switch`（F1）：TestClient `/content` 三次（A→A語言切換→B）→ 釋放只在 A 首次 + 換 B（`calls==[1,1]`）。
- `test_release_on_upload_toggle`：env 控 RELEASE_ON_UPLOAD True/False、預設 on。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_lazyload_multi.py -v
... 10 passed in 1.49s   # C1 5 + C2 1 + C3 1 + C4 3

$ venv/bin/python -m pytest tests/ -q
1 failed, 556 passed, 3 skipped
  唯一 failed = test_settings_log_format_default_auto（既知環境 flake、單獨跑亦 fail 0.02s、LOG_FORMAT env 性質、C1-C4 一路既存、與本 commit 無關）；556 passed（553 + 3 釋放）
```
> ⚠️ **過程修正**：初版 upload hook 在 `ai_core=None`（upload 測試）時 `ai_core._paper_cache` 拋 AttributeError → 3 個 upload 測試紅。**修法＝helper 加 `if ai_core is None: return` 防呆**（正確：未初始化時無可釋放）→ 三測試恢復綠、且更健壯。

### §5.3 SOP 核查
```
logging：本 commit 未新增 logger.error（釋放僅 logger.info）；既有不變
database：grep '\.commit\(\)' web_server.py ai_core.py settings.py | grep -v session.begin → 無命中（合規；釋放純記憶體、loader DB 查詢唯讀為既有）
釋放就位：web_server 9 命中（helper/gate/hook/gc）/ settings 1（RELEASE_ON_UPLOAD）
docstring：grep '當前對話上下文' ai_core.py → 0（已修）
```

## §6 不可動清單遵守

- [x] 只動 `web_server.py`（端點段+helper+模組級）+ `ai_core.py`（docstring）+ `settings.py` + 測試。
- [x] **C3 啟動 lifespan set_loader 接線段未碰**（grep C3 標記 2 仍在、git diff 僅端點段+模組級 helper）→ C3/C4 hunk 不重疊。
- [x] `rag_retriever.py` — **零改動**。
- [x] `/content` 讀檔回傳 / `/upload` 上傳派發既有邏輯 — 未改（只加釋放 hook）。
- [x] `retrieve_multi` / `retrieve_with_context` 演算法 — 未動。
- [x] C4 標記平衡（3 START / 3 END）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本 C4 執行報告暫存 baton（未 mv / 未 git add）；plan v1-v5 + tasks + C1/C2/C3 報告續留 baton。
- **LAZYLOAD-MULTI-1 五修法全落地**（C1 自載咽喉 + C2 併發鎖 + C3 接線 LIVE + C4 釋放策略）；待 C5 Checkout 收官。
- **下一步＝C5 Checkout**（Conformance 驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒），待 baron 下達 C5 Run 提示詞。
- ⚠️ **baron E2E（plan v5 §8.2）**：#cv 涵蓋全 6 位 / 並發 / 串流中切篇不斷 / 語言切換不放 / 上傳釋放 RAM 降 / shadow pid 入 chosen。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 4 份 .bak）

# 2. git add（baton 執行報告不 git add；.gitignore 若 M 非本 commit、不納入）
git add web_server.py
git add ai_core.py
git add settings.py
git add tests/test_lazyload_multi.py
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_web_server.py.bak
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_ai_core.py.bak
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_settings.py.bak
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C4_test_lazyload_multi.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-10_LAZYLOAD-MULTI-1_C4_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/LAZYLOAD-MULTI-1_C4_msg.txt
git commit -F /tmp/LAZYLOAD-MULTI-1_C4_msg.txt
```
> baton/ 下 plan + tasks + C1-C4 執行報告**嚴禁 git add**（C5 Checkout 一次性歸檔）。

## §9 回退方式（Rollback）

```bash
git revert <C4 hash>   # 或還原 4 .bak；移除釋放 hook 回 C3 狀態（cap=100 仍在、③ 仍 LIVE）、無副作用
```
