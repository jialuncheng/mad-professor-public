# LAZYLOAD-MULTI-1 C2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-10 |
| 任務代號 | LAZYLOAD-MULTI-1 C2 |
| 觸發 Commit | C2 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_LAZYLOAD-MULTI-1_..._tasks.md` |
| 觸發情境 | baron 確認 C1 落地，下達 C2 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- LAZYLOAD-MULTI-1 / C2 / BE-Refactor；tasks §8 C2、plan v5 U8/§4 鎖不變式

### 鎖設計修正（覆寫 tasks §4.2 兩鎖）
- tasks §4.2「各 class 自有鎖、無跨 class 鎖序」有 AB-BA 死鎖：load_paper_cache(持_cache_lock)→set_rag_tree(取 retriever 鎖)=A→B；_get_vector_store(持 retriever 鎖)→loader→load_paper_cache(取_cache_lock)=B→A。
- 改用單一共享 threading.RLock：retriever 持鎖、ai_core 共用 self.retriever._lock，可重入、零鎖序、不可能死鎖。

### 執行命令
① 改前備份 rag_retriever.py + ai_core.py + tests/test_lazyload_multi.py（3 .bak）
② rag_retriever.py（`# === [LAZYLOAD-MULTI-1 C2] ===`）：import threading；__init__ 加 self._lock=RLock()；with self._lock 包 add_paper/_evict_vector_lru/remove_paper/set_rag_tree/_get_vector_store dict mutation 區段。🔴 鐵則：_get_vector_store 第三層 self._loader(...) 呼叫必須在鎖外（loader re-enter）。
③ ai_core.py：不另建鎖、用 self.retriever._lock 包 load_paper_cache（_paper_cache 寫+LRU）+remove_paper；retriever None 防呆退不加鎖+warning。
④ tests 追加 test_concurrent_lazyload_no_corruption（≥8 thread 並發自載+evict、無 KeyError/RuntimeError、timeout 內完成驗不死鎖）。
- 物理防線：只動 rag_retriever+ai_core+測試；不動 web_server/settings；純加鎖行為不變；不加釋放（C4）。

### SOP 核查
- logging grep（新增 logger.error 須 exc_info）；database grep（無裸 commit）；鎖就位 grep。

### 同步 TODO
- C2 ✅、C3 🟡 WIP；git log 自癒

### 產出
- 執行報告 baton/2026-06-09_LAZYLOAD-MULTI-1_C2_執行.md（暫存 baton、嚴禁 mv/git add）；§4 含共享 RLock 取代兩鎖防 AB-BA + loader 鎖外鐵則。

### §8 baron 命令
- git add rag_retriever+ai_core+test+3 .bak+TODO+2 prompts；msg → /tmp/LAZYLOAD-MULTI-1_C2_msg.txt（refactor(rag)、署名 Claude Opus 4.8 (1M context)）

### 停止
- 產出執行報告（暫存 baton）後立即停止；不續 C3、不動 web_server/settings、不改既有邏輯、不持鎖跨 loader、不 mv/git add baton、不自發 commit
