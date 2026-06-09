# LAZYLOAD-MULTI-1 C1 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | LAZYLOAD-MULTI-1 C1 |
| 執行日期 | 2026-06-10 |
| 依據規劃 | `baton/..._tasks.md §8 C1`（對齊 plan v5 §4.1 / U1 / U7 / §4 接縫）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 5 測試全綠 + 全套件不退化；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：RAG-MULTI-1 收官後 HEAD（`e88c304` 或其後）。
- **本次**：`rag_retriever.py` 加 loader 接縫（set_loader + `_get_vector_store` 完全 miss 自載 + is_ready loader-aware）+ 新建 `tests/test_lazyload_multi.py` 5 測試；未 commit。
- **工作流類別**：BE-Refactor（單一 Commit；執行報告暫存 baton、不入 git、C5 Checkout 才歸檔）。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| C1 | `待 baron 回填` | feat(rag): LAZYLOAD-MULTI-1 C1 — retriever loader 接縫（_get_vector_store 完全 miss 自載）|

## §3 變動檔案清單

```
 rag_retriever.py        | 42 insertions(+), 2 deletions(-)
 tests/test_lazyload_multi.py | （新建、5 測試）
```
備份（改前 .bak、archive/、git add 強制含）：
```
.claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C1_rag_retriever.py.bak
```
> ⚠️ `git status` 另見 `.gitignore` M —— **C1 未碰 .gitignore**（worktree 既有未提交變動、不納入本 commit git add）。

## §4 修法說明（對齊 U1/U7/§4 接縫）

`rag_retriever.py`（`# === [LAZYLOAD-MULTI-1 C1 START/END] ===` 包裹，3 對標記 + is_ready 內聯標記）：

### ① `__init__` + `set_loader`（U1、§4 lazy-load callback）
```python
self._loader = None           # ③ lazy-load hook，web_server 啟動 set_loader 注入
def set_loader(self, fn) -> None:
    self._loader = fn          # 存不透明 callable、retriever 不 import paper_manager/web_server
```

### ② `_get_vector_store` 第三層「完全 miss 自載」（U1、§4）
既有兩層（vector_stores 命中 / paper_vector_paths 命中重載 FAISS）之後、`return None` 之前：
```python
if self._loader is not None:
    try:
        self._loader(owner_id, paper_id)
    except Exception as e:
        logger.error(f"lazy-load 自載失敗: ...", exc_info=True)   # logging SOP：exc_info=True
        return None
    if key in self.vector_stores: ... return store
    if key in self.paper_vector_paths: ... return store
return None
```
- 根治 API-PERF C3 lazy-load 只載當前 paper、跨文件 retrieve_multi 漏召其餘 tagged 篇。
- **loader 未設時略過此段、行為與現況完全一致（回 None）→ 向後相容。**
- §4 接縫：傳 loader 的 `paper_id` ＝ retrieve_multi.paper_ids 元素 ＝ 自載寫回 key，同 **paper_uuid 原值**。

### ③ `is_ready()` loader-aware（U7）
```python
return bool(self.paper_vector_paths) or self._loader is not None
```
- 防全清（C4 切換/上傳釋放）後 paper_vector_paths 空 → 原回 False 致 retrieve_* 繞過 ③。

### ④ 新建 `tests/test_lazyload_multi.py`（5 測試、檔頭 `# === [LAZYLOAD-MULTI-1 C1] ===`）
mock vector store + loader 模擬 load_paper_resources（一併補 vector + rag_tree）；不 mock retrieve_multi 本體。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_lazyload_multi.py -v
test_get_vector_store_self_loads_on_miss PASSED
test_get_vector_store_loader_unset_returns_none PASSED   # 向後相容（loader 未設回 None）
test_retrieve_multi_loads_all_tagged PASSED              # 整合：6 篇只註冊 1、其餘自載、全召
test_evict_then_reload_preserves_title PASSED            # 全清→重載 title 非空
test_is_ready_after_full_evict PASSED                    # U7 loader-aware
========================= 5 passed =========================

$ venv/bin/python -m pytest tests/ -q
1 failed, 551 passed, 3 skipped
  唯一 failed = 既知環境 flake test_settings_log_format_default_auto（與 C1 無關）；551 passed（546+5 新）
```

### §5.3 SOP 核查
```
logging：grep -nE 'logger.error|format_exc|exception' rag_retriever.py
  → L125 為本 commit 新增（lazy-load 自載失敗）、已含 exc_info=True（合規）；
    L79/86/98/252 為既存、非本 commit 引入。
database：grep -nE '\.commit\(\)' rag_retriever.py | grep -v 'with session.begin' → 無命中（合規、retriever 純記憶體）
```

## §6 不可動清單遵守

- [x] 只動 `rag_retriever.py` + 新建 `tests/test_lazyload_multi.py`（git status 證）。
- [x] `ai_core.py` / `web_server.py` / `settings.py` — 零改動（屬 C2/C3/C4）。
- [x] **未加 RLock**（C2 才加）/ **未加釋放邏輯**（C4 才加）。
- [x] `retrieve_multi` 保底演算法 / `retrieve_with_context` 檢索 / context 格式 / 向量資料 — 未動（既有兩層邏輯保留、僅在其後追加第三層）。
- [x] 標記平衡（3 START / 3 END + is_ready 內聯）。
- [x] `.gitignore` — 未碰（worktree 既有變動、不納入）。

## §7 銜接（baton 狀態 + 下一步）

- baton：本 C1 執行報告暫存 baton（未 mv / 未 git add）；plan v1-v5 + tasks 續留 baton。
- **下一步＝C2**（Cache 併發鎖純硬化：RLock 包 rag_retriever 三 dict + ai_core._paper_cache 全 mutation；行為不變、既有全套件即回歸網），待 baron 下達 C2 Run 提示詞。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/2026-06-10_LAZYLOAD-MULTI-1_C1_rag_retriever.py.bak）

# 2. git add（baton 執行報告不 git add；.gitignore 不納入——非本 commit 改動）
git add rag_retriever.py
git add tests/test_lazyload_multi.py
git add .claude-logs/archive/2026-06-10_LAZYLOAD-MULTI-1_C1_rag_retriever.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-10_LAZYLOAD-MULTI-1_C1_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿已寫入 /tmp/LAZYLOAD-MULTI-1_C1_msg.txt
git commit -F /tmp/LAZYLOAD-MULTI-1_C1_msg.txt
```
> baton/ 下 plan + tasks + C1 執行報告**嚴禁 git add**（C5 Checkout 一次性歸檔）。

## §9 回退方式（Rollback）

```bash
git revert <C1 hash>   # 或還原 .bak；loader 未設時行為與現況等價、回退無副作用
```
