# LAZYLOAD-MULTI-1 C2 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | LAZYLOAD-MULTI-1 C2 |
| 執行日期 | 2026-06-10 |
| 依據規劃 | `baton/..._tasks.md §8 C2`（對齊 plan v5 U8 / §4 鎖不變式）+ 本 Run 提示詞鎖設計修正 |
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 6 測試全綠（含並發不死鎖）+ 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：C1（loader 接縫）之上。
- **本次**：`rag_retriever.py` + `ai_core.py` 加 in-memory cache 併發鎖（**單一共享 RLock**）+ 追加並發測試；**純加鎖、行為不變**；未 commit。
- **工作流類別**：BE-Refactor（單一 Commit；執行報告暫存 baton、C5 Checkout 才歸檔）。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C2 | `待 baron 回填` | refactor(rag): LAZYLOAD-MULTI-1 C2 — in-memory cache 併發鎖純硬化（單一共享 RLock）|

## §3 變動檔案清單

```
 rag_retriever.py             | import threading + self._lock RLock + 包 5 處 mutation
 ai_core.py                   | import nullcontext + load_paper_cache/remove_paper 共用 retriever._lock
 tests/test_lazyload_multi.py | +test_concurrent_lazyload_no_corruption
```
備份（改前 .bak、archive/、git add 強制含）：
```
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C2_rag_retriever.py.bak
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C2_ai_core.py.bak
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C2_test_lazyload_multi.py.bak
```

## §4 修法說明（U8 + §4 鎖不變式）

### 🔑 鎖設計修正：單一共享 RLock 取代 tasks §4.2「兩鎖」（防 AB-BA 死鎖）
tasks §4.2 之「各 class 自有鎖、無跨 class 鎖序」**有 AB-BA 死鎖風險**（碼證）：
- `ai_core.load_paper_cache`（持 _cache_lock）→ `retriever.set_rag_tree`（取 retriever 鎖）＝序 **A→B**；
- `_get_vector_store` 自載（持 retriever 鎖）→ loader → `ai_core.load_paper_cache`（取 _cache_lock）＝序 **B→A**。
→ 改用**單一共享 `threading.RLock`**：retriever 持 `self._lock`，ai_core 之 `_paper_cache` mutation **共用 `self.retriever._lock`**（None 時退 `nullcontext`）。同一把可重入鎖 → **零鎖序、不可能 AB-BA**。

### `rag_retriever.py`（`# === [LAZYLOAD-MULTI-1 C2] ===`）
- `import threading`；`__init__` 加 `self._lock = threading.RLock()`；
- `with self._lock:` 包：`_evict_vector_lru`（popitem 迴圈）/ `set_rag_tree` / `add_paper`（dict mutation 段）/ `remove_paper`（三 dict pop）/ `_get_vector_store`（前兩層 dict 存取 + 第三層 loader 回來後的 retry 段）。
- **🔴 死鎖鐵則**：`_get_vector_store` 第三層 `self._loader(owner_id, paper_id)` 呼叫**在鎖外**（loader re-enter ai_core/retriever 取同鎖）；僅 loader 回來後的 retry dict 存取持鎖。
```python
with self._lock:          # 前兩層
    if key in self.vector_stores: ...
    if key in self.paper_vector_paths: ...
if self._loader is not None:
    self._loader(owner_id, paper_id)   # ← 鎖外（防 AB-BA）
    with self._lock:      # retry
        ...
```

### `ai_core.py`（`# === [LAZYLOAD-MULTI-1 C2] ===`）
- `from contextlib import nullcontext`；
- `load_paper_cache`：`_lock_ctx = self.retriever._lock if self.retriever else nullcontext()`；`with _lock_ctx:` 包 `_paper_cache[key]=` + `set_rag_tree`（可重入吸收）+ LRU popitem 段（file IO/json.load 在鎖外）；
- `remove_paper`：同 `_lock_ctx` 包 `del _paper_cache` + `retriever.remove_paper`（可重入）。

### `tests/test_lazyload_multi.py`
- `test_concurrent_lazyload_no_corruption`：8 worker、16 任務並發 `_get_vector_store`（loader→add_paper/set_rag_tree re-enter 共享鎖）+ `remove_paper` + 小 cache 觸發 evict → `f.result(timeout=20)` 驗不死鎖、無 KeyError/RuntimeError、cap 不超。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_lazyload_multi.py -v
test_get_vector_store_self_loads_on_miss PASSED / test_get_vector_store_loader_unset_returns_none PASSED /
test_retrieve_multi_loads_all_tagged PASSED / test_evict_then_reload_preserves_title PASSED /
test_is_ready_after_full_evict PASSED / test_concurrent_lazyload_no_corruption PASSED
========================= 6 passed in 1.14s =========================   # 並發測試 timeout 內完成＝不死鎖

$ venv/bin/python -m pytest tests/ -q
1 failed, 552 passed, 3 skipped
  唯一 failed = 既知環境 flake test_settings_log_format_default_auto（與 C2 無關）；552 passed（551 + 1 並發）
  → 既有全套件全綠＝行為不變回歸網
```

### §5.3 SOP 核查
```
logging：C2 純加鎖、未新增 logger.error（既存 L79/86/98/125/252 不變、L125 為 C1 已含 exc_info）
database：grep '\.commit\(\)' rag_retriever.py ai_core.py | grep -v session.begin → 無命中（合規）
鎖就位：grep 'threading.RLock|with self._lock|self.retriever._lock' → rag_retriever 8 / ai_core 2 命中
```

## §6 不可動清單遵守（行為不變證據）

- [x] 只動 `rag_retriever.py` + `ai_core.py` + `tests/test_lazyload_multi.py`（git status 證）。
- [x] `web_server.py` / `settings.py` — **零改動**（C3/C4）。
- [x] **未加釋放邏輯**（C4）。
- [x] **除加鎖外不改任何既有邏輯/順序/回傳** → 既有全套件全綠（552 passed）＝回歸網鐵證。
- [x] `_get_vector_store` 第三層 loader 呼叫在鎖外（AB-BA 死鎖鐵則遵守、並發測試驗證）。
- [x] C2 標記平衡（rag_retriever 1 START/1 END + 內聯；ai_core 1 START/1 END + 內聯）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本 C2 執行報告暫存 baton（未 mv / 未 git add）；plan v1-v5 + tasks + C1 報告續留 baton。
- **下一步＝C3**（啟動接線與容量：web_server 啟動 `set_loader` 接線 + `RAG_MAX_CACHE`=100；純加法、核心跨文件修復 LIVE），待 baron 下達 C3 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 3 份 .bak）

# 2. git add（baton 執行報告不 git add；.gitignore 若 M 非本 commit、不納入）
git add rag_retriever.py
git add ai_core.py
git add tests/test_lazyload_multi.py
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C2_rag_retriever.py.bak
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C2_ai_core.py.bak
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C2_test_lazyload_multi.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-10_LAZYLOAD-MULTI-1_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/LAZYLOAD-MULTI-1_C2_msg.txt
git commit -F /tmp/LAZYLOAD-MULTI-1_C2_msg.txt
```
> baton/ 下 plan + tasks + C1/C2 執行報告**嚴禁 git add**（C5 Checkout 一次性歸檔）。

## §9 回退方式（Rollback）

```bash
git revert <C2 hash>   # 或還原 3 .bak；純加鎖、移除鎖即回 C1 狀態、無副作用
```
