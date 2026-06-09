# LAZYLOAD-MULTI-1 C3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-10 |
| 任務代號 | LAZYLOAD-MULTI-1 C3 |
| 觸發 Commit | C3 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_LAZYLOAD-MULTI-1_..._tasks.md` |
| 觸發情境 | baron 確認 C2 落地，下達 C3 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- LAZYLOAD-MULTI-1 / C3 / BE-Refactor；tasks §8 C3、plan v5 U2/U4/§4 lazy-load callback

### 執行命令
① 改前備份 web_server.py + settings.py + tests/test_lazyload_multi.py（3 .bak）
② settings.py（U4）：RAG_MAX_CACHE 預設 "5"→"100"（env 可覆寫）
③ web_server.py（U2、僅啟動 lifespan 接線段、`# === [LAZYLOAD-MULTI-1 C3] ===`）：
   ai_core.retriever.set_loader(lambda o,p: paper_manager.load_paper_resources(OUTPUT_DIR,o,p,ai_core))
   定位 API-PERF C3 廢 preload 區附近、ai_core/retriever 就緒後、yield 前；先 grep 確認作用域
   嚴禁碰端點 handler / 既有 lifespan 邏輯（只新增接線一行）
④ tests 追加 test_cap_100_default（預設 100 + env override）
- 物理防線：只動 web_server 啟動段 + settings + 測試；不碰端點（C4）/rag_retriever/ai_core（C1/C2）/釋放（C4）
- 純加法 2-3 行→核心跨文件修復 LIVE

### SOP 核查
- logging grep（本 commit 不應新增 logger.error）；database grep（無裸 commit）；接線+常數就位

### 同步 TODO
- C3 ✅、C4 🟡 WIP；git log 自癒 C1/C2

### 產出
- 執行報告 baton/2026-06-09_LAZYLOAD-MULTI-1_C3_執行.md（暫存 baton、嚴禁 mv/git add）；§4 強調只動啟動段、與 C4 hunk 不重疊

### §8 baron 命令
- git add web_server+settings+test+3 .bak+TODO+2 prompts；msg → /tmp/LAZYLOAD-MULTI-1_C3_msg.txt（feat(rag)、署名 Claude Opus 4.8 (1M context)）

### 停止
- 產出執行報告後立即停止；不續 C4、不碰端點/釋放、不動 rag_retriever/ai_core、不改既有 lifespan、不 mv/git add baton、不自發 commit
