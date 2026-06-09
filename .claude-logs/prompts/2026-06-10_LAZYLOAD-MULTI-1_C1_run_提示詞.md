# LAZYLOAD-MULTI-1 C1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-10 |
| 任務代號 | LAZYLOAD-MULTI-1 C1 |
| 觸發 Commit | C1 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_LAZYLOAD-MULTI-1_..._tasks.md` |
| 觸發情境 | baron 確認 tasks，下達 C1 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- LAZYLOAD-MULTI-1 / C1 / BE-Refactor；tasks §8 C1、plan v5 §4.1/U1/U7/§4 接縫

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP / framework / tasks / plan v5 / database SOP / logging SOP / template_execution

### 執行命令（tasks §8 C1）
① 改前備份 rag_retriever.py → archive/2026-06-10_LAZYLOAD-MULTI-1_C1_rag_retriever.py.bak
② 改 rag_retriever.py（`# === [LAZYLOAD-MULTI-1 C1] ===` 包裹）：
   - __init__ 加 self._loader=None
   - 新增 set_loader(fn)（存不透明 callable、不 import paper_manager/web_server）
   - _get_vector_store 兩層後加第三層「完全 miss 自載」：_loader 非 None → 呼 loader(owner,pid) 後重試取庫
   - is_ready() → bool(paper_vector_paths) or _loader is not None（U7 防全清繞過）
   - 保留既有兩層；loader 未設＝現況回 None
③ 新建 tests/test_lazyload_multi.py 5 測試：self_loads_on_miss / loader_unset_returns_none / retrieve_multi_loads_all_tagged（整合 6 篇只註冊 1）/ evict_then_reload_preserves_title / is_ready_after_full_evict
- 物理防線：只動 rag_retriever.py + 新測試檔；不動 ai_core/web_server/settings；不加 RLock（C2）/釋放（C4）/retrieve_multi 演算法/context 格式

### SOP 核查
- logging grep logger.error rag_retriever.py（新增者須 exc_info）；database grep .commit()（無裸 commit）

### 同步 TODO
- C1 ✅、C2 🟡 WIP；git log 自癒

### 產出
- 執行報告 baton/2026-06-09_LAZYLOAD-MULTI-1_C1_執行.md（暫存 baton、嚴禁 mv/git add）；套 template_execution

### §8 baron 命令
- git add rag_retriever.py + tests/test_lazyload_multi.py + .bak + TODO + 2 prompts
- msg → /tmp/LAZYLOAD-MULTI-1_C1_msg.txt（feat(rag) 前綴、署名 Claude Opus 4.8 (1M context)）

### 停止
- 產出執行報告（暫存 baton）後立即停止；不續 C2、不動 ai_core/web_server/settings、不加鎖/釋放、不 mv/git add baton、不自發 commit
