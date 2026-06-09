# LAZYLOAD-MULTI-1 C4 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-10 |
| 任務代號 | LAZYLOAD-MULTI-1 C4 |
| 觸發 Commit | C4 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_LAZYLOAD-MULTI-1_..._tasks.md` |
| 觸發情境 | baron 確認 C3 落地，下達 C4 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- LAZYLOAD-MULTI-1 / C4 / BE-Refactor；tasks §8 C4、plan v5 U5/U9/P4 + §4 跳過活躍串流/當前篇 + §3.5 F1 + §3.6 M1

### 執行命令
① 改前備份 web_server.py + ai_core.py + settings.py + tests/test_lazyload_multi.py（4 .bak）
② settings.py：RELEASE_ON_UPLOAD = os.getenv("RELEASE_ON_UPLOAD","true").lower()=="true"（預設 on）
③ web_server.py（`# === [LAZYLOAD-MULTI-1 C4] ===`、只動端點段+模組級）：
   - 模組級 _owner_current_paper={}（owner→當前 paper_uuid）
   - helper _release_caches_except_active(owner)：active={s.paper_uuid for active_streams if not done and owner match}；快照 cached uuid（_paper_cache+paper_vector_paths）再清；逐篇 skip active、ai_core.remove_paper；gc.collect()+logger.info
   - /content（paper_content 回傳前）gate：paper_id != _owner_current_paper.get(uid) 才釋放+更新（F1 語言切換同篇不放）
   - /upload（upload_paper）：if settings.RELEASE_ON_UPLOAD: 釋放（騰 RAM 給 MinerU）
   - 🔴 不碰 C3 啟動接線段、不改 /content 讀檔回傳/  /upload 上傳派發邏輯（只加 hook）；import gc/settings 視需補
④ ai_core.py：remove_paper docstring 移「當前對話上下文」（P4）
⑤ tests 追加 3：release_skips_active_stream / release_only_on_actual_switch / release_on_upload_toggle（純 unit、mock）
- 物理防線：只動 web_server 端點段+helper + ai_core docstring + settings + 測試；不動 rag_retriever；不改 retrieve_* 演算法

### SOP 核查
- logging grep（新增 logger.error 須 exc_info；本 commit 釋放僅 logger.info）；database grep（無裸 commit）；釋放就位 grep；docstring grep（當前對話上下文=0）

### 同步 TODO
- C4 ✅、C5 🟡 WIP；git log 自癒 C1/C2/C3

### 產出
- 執行報告 baton/2026-06-09_LAZYLOAD-MULTI-1_C4_執行.md（暫存 baton、嚴禁 mv/git add）；§4 強調只動端點段+helper、不碰 C3 啟動段

### §8 baron 命令
- git add web_server+ai_core+settings+test+4 .bak+TODO+2 prompts；msg → /tmp/LAZYLOAD-MULTI-1_C4_msg.txt（feat(rag)、署名 Claude Opus 4.8 (1M context)）

### 停止
- 產出執行報告後立即停止；不續 C5、不動 C3 啟動段/rag_retriever、不改端點既有邏輯、不改 retrieve_* 演算法、不 mv/git add baton、不自發 commit
