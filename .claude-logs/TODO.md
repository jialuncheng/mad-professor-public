# Mad Professor — TODO（最後更新 2026-05-27，OPTIMIZE-1 全案收官）

> 本文件為 **Single Source of Truth**（依 `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` §2.1）。
> **任何規劃 / 執行 / hotfix 前必先 view 框架文件**：`.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md`
> 對應 template 位於 `.claude-logs/templates/template_plan.md` / `template_execution.md` / `template_hotfix.md`
>
> **狀態 Emoji**（依框架 §2.2）：⬜ 未開始 / 🔵 plan 中 / 🟡 WIP / ✅ done
> **任務生命週期**（依框架 §2.5）：done 後**必須**從下方 active 列表移除、改寫入頂部 ✅ 已完成表格 + 同步索引。

---

## ✅ 已完成

### OPTIMIZE-1 PDF上傳自動無損優化

| Commit | 內容 | Hash |
|---|---|---|
| C1 | 新建 `utils/pdf_optimizer.py`（Atomic Overwrite + Logging SOP）+ `tests/test_pdf_optimize.py`（2 tests） | `b8892be` |
| C2 | 後端 is_slides_pdf 刪除 + optimize_pdf_lossless 整合 + doc_type Form 直通 + 前端 Phase-Shift 翻轉 + 3 tests | `28f098e` |
| C3 | Final Archiving and TODO Sync（baton/ 全量 mv 歸檔 + TODO.md 結案） | `93ab716` |

> **修法依據**：`.claude-logs/plans/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md`（v2）

### WORKFLOW-2 流程模板重構與提示詞自動歸檔

| Commit | 內容 | Hash |
|---|---|---|
| WORKFLOW-2-Tasks | Tasks 拆分（baton 暫存，C5 歸檔） | `7a3332f` |
| C1 | R1 五大提示詞模板自愈歸檔防線 | `b3e22c7` |
| C2 | R2 Check Conformance 維度四+五 | `5d7bdda` |
| C3 | R3+R4 SOP 備份暫存鐵律 + §8 重構 | `5a55939` |
| C4 | R5a 歷史 9 份提示詞物理補建 | `10f9561` |
| C5 | R5b INDEX 幽靈自癒 + 全案收官歸檔 | `7a3332f` |

> **修法依據**：`.claude-logs/plans/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`

### TODO-HOTFIX-1 TODO.md 緊急狀態與殘留修復

| Commit | 內容 | Hash |
|---|---|---|
| TODO-HOTFIX-1 | RAG 狀態整理與 RAG-11/12 抽離（RAG 狀態修復） | `a0d1951` |
| TODO-HOTFIX-1b | MODEL-8 進行中殘留清理（MODEL-8 狀態清理） | `2c78f9e` |
| TODO-HOTFIX-1 Check | Conformance 驗收與歸檔收官（第三階段驗收） | `5f3ef01` |

> **修法依據**：`.claude-logs/hotfixes/2026-05-26_TODO-HOTFIX-1_hotfix.md`

### WORKFLOW-1 流程簡化與文件治理

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Bootstrap Core（自動載入核心文件治理基礎） | `1a0394c` |
| C1.5 | Core Spec Align & TODO Bootstrap（核心規格與 TODO 自舉） | `e0c7a17` |
| C2 & C3 | Templates & Overview + Prompt Templates（模板與引導 / 提示詞模板） | `365aa5d` |
| C4 | SOP & Diagnostics（領域 SOP 與診斷目錄） | `ad0be4e` |
| C5 | 收官 (Closure) | `8965725` |

> **修法依據**：`.claude-logs/plans/2026-05-25_WORKFLOW-1_流程簡化與文件治理_plan_v4-final-r4-v6.md`（v11）

### Phase 4.7d Chat 改造（17 系列）

| Commit | 內容 | Hash |
|---|---|---|
| 17-1 | 後端寫 DB + 廢前端 saveChatHistory POST | `8a1a0ec` |
| 17-1b | 切 paper 立即清 chat + SSE 改 asyncio.to_thread | `7452067` |
| 17-2 | stream broker + /chat/attach + /chat/history 加 in_progress | `5394365` |
| 17-3 | 前端 loadChatHistory + EventSource attach | `aed989c` |
| 17-4 | 移除 POST /chat/history endpoint | `a1adfbc` |

### Phase 4.7d RAG 改造（15 系列）

| Commit | 內容 | Hash |
|---|---|---|
| 15-1 | chunk 優化（空 chunk / Context 前綴 / 短文合併） | `d6cb3df` |
| 15-2 | retriever 加 paper_title 引用 + score logging | `b6622a1` |

### Phase 4.7d RAG-7 doc_analyzer / md_cleaner 切 section 修正（2 commits）

| Commit | 內容 | Hash |
|---|---|---|
| RAG-7a | md_cleaner 偵測 + 移除重複 heading 行（浮水印自動偵測） | `e2ed0e4` |
| RAG-7b | heading_fix_resume.txt prompt + HEADING_FIX_PROMPTS['resume'] 改指 | `5c182cf` |

### Phase 4.7? MODEL-9 連線彈性防禦（1 commit）

| Commit | 內容 | Hash |
|---|---|---|
| MODEL-9 | 新增 `llm/_http_client.py` 共享 httpx.Client 工廠（timeout 5/60/30/60 + Keep-Alive pool）+ LLMClient / EmbeddingModel 注入 + `llm/retry.py` 升級為 Full Jitter (`random(0, min(MAX, base*2^attempt))`) + 7 個 factory pytest + 2 個 retry pytest；R1 graceful shutdown + R2 環境變數 override（`GEMINI_*_TIMEOUT` / `LLM_RETRY_MAX_BACKOFF`） | `dd18922` |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-9_連線彈性防禦_plan.md` §4 + baron R1/R2 補充
> **環境變數**：`GEMINI_CONNECT_TIMEOUT=5` / `GEMINI_READ_TIMEOUT=60` / `GEMINI_WRITE_TIMEOUT=30` / `GEMINI_POOL_TIMEOUT=60` / `GEMINI_MAX_KEEPALIVE=20` / `GEMINI_MAX_CONNECTIONS=100` / `GEMINI_KEEPALIVE_EXPIRY=30` / `LLM_RETRY_MAX_BACKOFF=60`

### Phase 4.7? MODEL-3 tiling 三合一優化（3 commits、B1 + B2 + B3）

| Commit | 內容 | Hash |
|---|---|---|
| B1 | 短文 Fast-path Bypass + `_join_content` helper（修正 1 防排版災難）+ `_bypass_content` 保留 index（修正 2 防 md_restore 對齊破裂）+ `TILING_MAX_LENGTH` env（修正 5）+ pipeline_core 傳 doc_type；新增 10 個 pytest | e97ddd2 |
| B2 | `_merge_small_text_blocks` 改寫：`SOFT_TYPES`/`HARD_BOUNDARY` 常數 + 公式穿透合併 + formula 永不 flush（修正 3）；新增 6 個 pytest | abed78d |
| B3 | `_process_content` long_doc_mode + `_PARAGRAPH_SPLIT_RE` regex（修正 4 容錯 `\r\n` / 多餘空白）+ `TILING_PARAGRAPH_THRESHOLD` env + `tiling_method` 標籤完整化（bypass / paragraph / delimiter / sentence / passthrough）；新增 7 個 pytest | 9177930 |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-3_短文Bypass_公式穿透_段落滑動_plan.md`（§4.0 + §4.1 + §4.2 + §4.3 + §4.6 + §3.5/3.6/3.7/3.8/3.9 修正 1-5）
> **環境變數**：`TILING_BYPASS_CHAR_LIMIT=5000` / `TILING_MAX_LENGTH=2500` / `TILING_PARAGRAPH_THRESHOLD=30000`（皆預設）
> **Backfill**：baron OrcStack 端按 plan §4.4 SOP（pkill → `rm -rf output/*/*/{vector_store,*_tiled.json}` → 重啟）執行；觀察 `[tiling bypass]` + `tiling_method` 標籤為書籍場景 / RAG-3 校準鋪路。

### Phase 4.7? MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI（3 commits、C1 + C2 + C3）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | `models.py` 加 `PaperChunk` ORM + `Paper.chunks` relationship + `paper_manager.py` 加 3 個 DAL helper（不重做 `get_paper_db_id`、修正 5）+ `processor/rag_processor.py` 加 `CHUNK_FILTER_VERSION` 常數 + `settings.py` 加 `OUTPUT_DIR` env（修正 7、依 db_analysis §5.2）+ `web_server.py:77-78` 改 `from settings import OUTPUT_DIR`（2 行、其他 20+ 處引用不動）；新增 7 個 pytest | aeb42cb |
| C2 | `processor/rag_processor.py` 加 module-level `write_index_meta_json`（修正 4、CLI 共用）+ `RagProcessor._write_paper_chunks_to_db` method + `process` / `_create_vector_store` 加 `paper_db_id` 參數 + `pipeline_core.py::_stage_rag` 加 2-3 行 `paper_db_id` 注入（修正 2、不動 web_server）；新增 5 個 pytest | ab40fdc |
| C3 | `tools/regen_rag.py` 新檔（6 子命令：`--check / --paper / --all / --force / --dry-run / --init`、含 cmd_init 修正 6 完整 pseudo-code 反向導入既有 paper）；新增 7 個 pytest | 16f62d4 |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-8_SQLite物理防線_plan.md` v3（§3.1 + §3.2 + §3.3 + §3.3.1 + §3.4 + §3.6 + §5.1 + §6 + §7 + Q1-Q18 + 附錄 A/B）+ `.claude-logs/ref/db_analysis_and_future_extension.md`（§1 + §3.1 + §4 + §5.2 + §5.3）
> **8 個修正**：路徑統一 `vectors/` / paper_db_id 內部注入 / 移除 tiling_method / write_index_meta_json 抽 module-level / 不重做 get_paper_db_id / cmd_init pseudo-code 完整 / OUTPUT_DIR env 化 / Pg-Ready 安撫
> **環境變數**：`OUTPUT_DIR=/app/storage/output`（預設 `_BASE_DIR / "output"`、Docker / K8s 部署用）
> **Backfill 一次性 SOP**：baron OrcStack 端 `git pull && venv/bin/python tools/regen_rag.py --init` 從 `vectors/` FAISS docstore 反向導入既有 paper、未來升 embedding 直接 `--all`、< 5 分/書籍。

### Phase 4.X? RAG-1 Phase 2 Hashtag RAG 路由 + 雙語摘要 + Chat Token UI（3 commits、P2-1 + P2-2 + P2-3）

| Commit | 內容 | Hash |
|---|---|---|
| P2-1 | 雙語摘要管道：`processor/metadata_extractor._ALL_FIELDS` 加 `translated_abstract` + `pipeline_core._stage_translate` 完成後同步寫入 `self._metadata["translated_abstract"]`（source=translate_pipeline / confidence=high、try/except 防禦 / 空值不覆寫）；3 個 pytest | 26a4439 |
| P2-2 | 後端 hashtag RAG 路由：`settings.RAG_MULTI_TOP_K=7` env + `paper_manager.list_paper_uuids_by_tag`（owner-scoped、共用 R2 `_normalize_tag`）+ `paper_manager.parse_query_hashtag`（長標籤優先排序防 `#complex` 攔 `#complex_system`）+ `rag_retriever.retrieve_multi_with_context`（跨 paper 全域 Merge-Sort top-k、L2 normalize 後 cosine 可比）+ `AI_professor_chat.process_query_stream` 入口分流（0/1/多/無 4 路徑、繞 router、單篇路徑 100% 不動）；14 個 pytest | 9ee44f3 |
| P2-3 | 前端 chat hashtag token UI：`static/index.html` chat-input `<textarea>` → `<div contenteditable>` + placeholder hint（Q11 完整版）+ `:empty::before` data-placeholder CSS（§3.3.5-#1）+ `contenteditable="false"` 禁用契約（§3.3.5-#2）+ 全域 grep 替換 `.value` / `.disabled` / textarea autosize（§3.3.5-#3）+ autocomplete dropdown 綁 `#chat-input-area` 容器（§3.3.5-#4）+ Claude `/skill` 風格 hashtag-token + 6 個 JS handler（input / keydown / compositionstart-end / blur / mousedown / × remove）+ design/docs/components.md §11.2 Hashtag Token + dom-reference.md / interaction.md 同步註記；9 個 pytest（含 §3.3.5-#1 / #3 兩個 v2 grep test） | f85b830 |

> **修法依據**：`.claude-logs/2026-05-23_RAG-1_Phase2_執行計劃.md` v2（8 章節 + §3.3.5 四點防護補強 + 15 Open Questions Q1-Q15）+ `.claude-logs/ref/2026-05-23_RAG-1_Hashtag_Backend_Implementation_Plan.md`（後端全部 Proposed Changes）+ baron 新需求（chat hint + Claude `/skill` 風格 token UI）+ `design/docs/components.md §11.2`（新增）
> **計畫累積**：plan v1 → v2（補 §3.3.5 4 點防護：CSS placeholder / disabled 樣式 / 全域 grep / dropdown 錨點）→ 落地 P2-1/P2-2/P2-3、共 **26 個 pytest**（3 P2-1 + 14 P2-2 + 9 P2-3、含 §3.3.5-#1 / #3 兩個 v2 grep test）
> **核心設計亮點**：
> - **零 schema 變動**：讀 Phase 1 `metadata_json.user_tags` 陣列、共用 `_normalize_tag` 真理源
> - **單篇 / 多篇 分流**：多篇 hashtag 走新 `retrieve_multi_with_context` + 繞 router；單篇 / 無 hashtag 走既有 `_get_rag_context` 路徑、零變動
> - **全域 Merge-Sort**：L2 normalize 後 cosine score 跨 paper 可比、防 prompt 爆炸（top_k=7 env override）
> - **長標籤優先排序**：`sorted(tags, key=len, reverse=True)` 防 `#complex` 攔 `#complex_system`
> - **contenteditable 四點防護**（§3.3.5）：CSS `:empty::before` placeholder / `contenteditable="false"` 禁用契約 / 全域 grep 替換 `.value` / dropdown 容器錨點
> - **中文 IME 防護**（Q12）：`compositionstart/end` + `e.isComposing` 雙重防護、組字中不觸發 autocomplete
> - **跟 Phase 1 解耦**：Phase 1 寫入路徑 100% 不動、Phase 2 純讀 user_tags 陣列、可獨立 ship
> **手動驗證 SOP**（baron OrcStack）：
> 1. **P2-1**：上傳英文 paper → 跑完 pipeline → 切中文、toolbar abstract 顯示中文（不再 fallback 英文）
> 2. **P2-2**：建 3 篇 HR 履歷加 `#hr` tag → 輸入 `#hr 比較這幾篇` → AI 回答含 3 個 paper title 引用、後端 log「matched_papers=3」
> 3. **P2-3**：chat-input 顯示「輸入 # 可加入 hashtag 跨文獻搜尋」placeholder → 輸入 `#` autocomplete dropdown 跳出 → `↓` `Enter` 確認、`#hr` 變藍色 token → `×` / `Backspace` 一次刪掉
> 4. **跨文件問答收官**（baron 需求 3）：`#hr 我的學歷區應該怎麼寫？` → AI 跨 3 份履歷比較 + 統一建議
> **影響範圍**：純 user-facing 功能擴充、無 schema 變動、無 backfill 需求；舊 paper 缺 `translated_abstract` 走前端 R1 子項 F fallback

### Phase 4.X? RAG-1 Bug Fix 系列（8 commits、BUG-F1~F6 + BUG-B1~B2）

| Commit | 內容 | Hash |
|---|---|---|
| BUG-F1 | 前端 micro fix 包 — tag fallback / placeholder 斷行 / export-btn / --content-max-w（Bug 1/3/4/5、5 pytest） | `9877e54` |
| BUG-F2 | theme dropdown + ESC + P2-3 latent fix — dropdownAPI IIFE + TDZ-aware 3 段拆分（Bug 2 + Bug 11、6 pytest） | `ae20559` |
| BUG-F3 | .modal-input CSS — ui-fixes-batch B5 廣義 selector + color-mix 跨主題 focus ring（Bug 7、2 pytest） | `57c71c8` |
| BUG-F4 | P1 critical 4 項 — A1 trackProgress / A2 empty-state / A3 customPrompt / A4 closeBizPopups（9 pytest） | `646afe4` |
| BUG-F5 | P2 inconsistencies — B1 廢 token 替換主 scale + B3 demo-bar dead code + B4 no-op（8 pytest） | `e799687` |
| BUG-F6 | P3 polish — C4 ~43 ticket 註解清理 / C5 marked 改寫 / C7 ⋯→SVG；C3+C6 no-op（7 pytest） | `12428aa` |
| BUG-B1 | 後端 abstract fallback — A 側路 translate_text + B regex 擴中日文「摘要/概要/內容提要/要旨」（Bug 8、28 pytest） | `a35a720` |
| BUG-B2 | 後端 blockquote→list + 前端 paper-header-meta CSS — `>` → `-` list + `<div>` wrap + @media screen（Bug 10、7 pytest、全鏈路收官） | `94ed27d` |

> **修法依據**：`.claude-logs/2026-05-24_RAG-1_前端_Bug_Fix_可行性評估.md` v2/v3 + `.claude-logs/2026-05-24_RAG-1_Bug_Fix_可行性評估.md` v4  
> **收官摘要**：6 前端 + 2 後端 = 8 commits、修 9 / 11 bugs、共 72 pytest 全綠、零迴歸；Bug 6 / Bug 9 延後為 RAG-11 / RAG-12

### Phase 4.X? RAG-1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫（3 commits、R1 + R2 + R3）

| Commit | 內容 | Hash |
|---|---|---|
| R1 | UI Fixes 子項 A/C/F/G 部分：`paper_manager.set_paper_tags` 新增 + `web_server.PaperUpdate.tags` Pydantic 擴充 + PATCH `/api/papers/{paper_uuid}` 整合 tags 處理 + `static/index.html` Modal CSS 補 `--radius-md` / `--font-display`（子項 C）+ `renderTitleHeader` 雙語 abstract fallback（子項 F）+ `#lang-toggle` 切語言後重繪 toolbar（子項 F）+ `#current-title padding-right` + `details.title-abstract max-height: 12rem` 防遮擋 / 防破版（子項 G 部分）；3 個 pytest | 9977428 |
| R2 | UI Fixes 子項 B/D/E/G 剩餘/H + v3 強化全域 lowercase：`paper_manager._normalize_tag()` module-level helper（單一真理源、lowercase + strip）+ `set_paper_tags` 整合 `_normalize_tag` + dedup + `web_server.upload_theme` endpoint（5 道安全過濾）+ `static/index.html` 加 `#` 標籤按鈕 + tag-modal + theme upload UI + tag-pill 半透明磨砂玻璃 + 風格選項英文化（Kahn · Kimbell Art Museum / Yoshitomo Nara）+ 移除「⚠ 後端未實作」警語 + `design/docs/theme-guide.md §7` 寫入 + `design/docs/components.md §11 Tag Pill` 新增 + `api_audit #23` 補完；13 個 pytest | f44a7e6 |
| R3 | 資料夾路徑自動標籤：`paper_manager._folder_ancestor_path_names`（遞迴向 root 取 folder name path、防環 + max_depth=32）+ `_apply_folder_path_tags`（共用 R2 ship 的 `_normalize_tag`、append + de-dup 策略、Q6/Q7 不清舊 tag）+ `set_paper_folder` commit 後 hook（try/except 包覆、不阻塞 core move）；7 個 pytest（HR/CV 基本 / 4 層巢狀 / lowercase / dedup / 未分類保留 / corrupt metadata / 中文 folder） | 49fe66a |

> **修法依據**：`.claude-logs/2026-05-23_RAG-1_前端執行計劃_含資料夾自動標籤.md`（§4.1 + §4.2 + §4.3 + §5 + §6 + §7 + §8 Q1-Q18 + §10）+ `.claude-logs/ref/2026-05-23_RAG-1_UI_Fixes_Implementation_Plan.md` v3（8 大子項 A-H + v3 強化段 + 附錄 C 4 點深度評估認證）+ `.claude-logs/ref/api_audit_and_performance_report.md` #22 + #23 + `design/docs/components.md §2 §6 §11` + `design/docs/theme-guide.md §7`
> **4 輪 review 累積**：v0 原始 UI Plan → v2 整合資料夾自動標籤 + Q1-Q10 決策 → v3 全域 lowercase 強化 + 4 點深度評估認證 → 落地 R1/R2/R3 3 個 commit、共 **23 個 pytest**（3 R1 + 13 R2 + 7 R3）
> **核心設計亮點**：
> - **零 schema 變動**：所有 tag 寫進既有 `metadata_json.user_tags` 陣列
> - **後端 Hook 注入**：所有 client（前端拖拽 / 對話框 / 首次上傳 / CLI）統一觸發、前端零負擔
> - **單一真理源**：`_normalize_tag()` 為所有 tag 寫入路徑唯一 normalize 入口
> - **中文友善**：`.lower()` 對中文無效、`#人資` `#工程` 保留原樣
> - **防禦性容錯**：`_apply_folder_path_tags` `try/except` 包覆、不阻塞 core `set_paper_folder` 移動
> - **Backward compat**：既有大寫 tag 不 retroactively 改寫；既有 R1 `set_paper_tags` 3 個 pytest 重構後仍 passed
> - **跟 Phase 2 解耦**：本 RAG-1 ship `metadata_json.user_tags` 寫入路徑、`.claude-logs/ref/2026-05-23_RAG-1_Hashtag_Backend_Implementation_Plan.md` Phase 2（hashtag RAG 路由 + parse_query_hashtag + retrieve_multi_with_context）讀此陣列、可獨立 ship
> **手動驗證 SOP**（baron OrcStack）：
> 1. 移動 paper 到資料夾 HR/CV → 重整、tag-pill 顯示 `#hr #cv`
> 2. 在 `#` Modal 輸入 `#HR #plant 工程` → 儲存後顯示 `#hr #plant #工程`（v3 lowercase + 中文保留 + dedup）
> 3. 從 HR/CV 移回未分類 → 自動 tag `#hr #cv` 保留（Q6/Q7）
> 4. 上傳 .css 主題 → 立即套用 + 重整不失效
> **影響範圍**：純 user-facing UI + 後端 helper、無 schema 變動、無 backfill 需求

### Phase 4.X? LOGGING refactor 統一日誌基建（3 commits、LOGGING-1 + 2 + 3）

| Commit | 內容 | Hash |
|---|---|---|
| LOGGING-1 | `utils/logging_config.py` 新檔（`JSONFormatter` + `ConsoleFormatter` + `setup_logging` + `reset_logging`）+ 補強 1 冪等性 + 補強 2 第三方劫持（`uvicorn` / `uvicorn.access` / `uvicorn.error` / `sqlalchemy.engine`）+ 補強 4 + v3 建議 1 exception 結構化 + v4 建議 1 噪聲分流（SQLAlchemy DEBUG-only / Uvicorn 動態）+ v4 建議 2 ContextVar `default=None` 雙保險 + v4 建議 3 `json.dumps default=str` 降級 + 🔴 v3 陷阱 1 `ConsoleFormatter.asctime` 顯式綁定 + 🔴 v3 陷阱 2 `uvicorn.run(log_config=None)`；`settings.py` 加 5 env（`LOG_LEVEL` / `LOG_DIR` / `LOG_FORMAT` / `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT`）；`web_server.py` 替換 `_setup_logging`；16 個 pytest | 011cc8c |
| LOGGING-2 | `web_server.py` 加 `@app.middleware("http") trace_id_middleware`（在 `auth_guard` decorator 與 `SessionMiddleware add_middleware` 之間、確保 `request.session` 可讀 owner）+ `X-Trace-ID` request/response header + `ContextVar set/reset` 跨 request 隔離（try/finally）+ SSE chat 路徑（`web_server.py:151 asyncio.to_thread`）自動繼承 ContextVar（Python 3.12.3、補強 3 / §4.11）；9 個 pytest | 3e406a1 |
| LOGGING-3 | `tools/regen_rag.py::main` 改用 `from utils.logging_config import setup_logging` 取代 `logging.basicConfig`；CLI 場景對齊 web_server 共用 settings env + Formatter + 噪聲分流 + ContextVar 雙保險；補 1 個 pytest | 6e764ea |

> **修法依據**：`.claude-logs/2026-05-23_logging_refactor_可行性評估.md` v4（§4.3 + §4.4 + §4.8-4.19 + §6 + Q1-Q22 + 附錄 v2/v3/v4 對照表）+ `.claude-logs/ref/logging_refactor_proposal.md`
> **4 輪 review 累積**：v0 原始 → v2 補強 4 點 → v3 致命陷阱 2 + 架構優化 2 → v4 生產健壯性 3 點、確保「不缺漏任何已知陷阱」
> **環境變數**：`LOG_LEVEL`（預設 INFO）/ `LOG_DIR`（預設 `_BASE_DIR/logs`）/ `LOG_FORMAT`（預設 `auto`、auto/json/console）/ `LOG_MAX_BYTES`（預設 10MB）/ `LOG_BACKUP_COUNT`（預設 5）/ `ENVIRONMENT`（development / production、控制 auto 切換）
> **Docker 部署**：`docker run -e ENVIRONMENT=production -e LOG_FORMAT=json -e LOG_LEVEL=INFO ...`、web_server + CLI 都自動 JSON output、Loki/ELK 可解析
> **不採納**：第三方 lib `structlog` / `loguru`（Q2）/ background pipeline ContextVar 跨 thread 注入（Q8、用既有 `[MODEL-8] owner=X paper=Y` 串連 90% 場景）

### Phase 4.7? MODEL-1+2 Embedding 升級（2 commits、B1 + B2）

| Commit | 內容 | Hash |
|---|---|---|
| B1 | EmbeddingModel 升級 `gemini-embedding-2` + MRL 768 維 + `_l2_normalize` helper（防禦升級：空值 / 1e-6 / 零向量 → `[0.0]*len`）+ 4 處 embed call 套用 + `EMBEDDING_OUTPUT_DIMENSIONS` env override；新增 10 個 pytest（`tests/test_embedding_normalize.py`）| `f415218` |
| B2 | `rag_processor._is_chunk_meaningful` helper（修正 2 markdown 噪聲 + 修正 4 履歷防誤殺 `resume/slides ≥ 3` + email/phone/url 保留）+ `rag_retriever` raw score logging + `RAG_SCORE_THRESHOLD` env 化（修正 1、預設 0.22）；新增 11 個 pytest（`tests/test_rag_chunk_filter.py`）| `de649cc` |

> **修法依據**：`.claude-logs/2026-05-22_MODEL-1+2_Embedding升級_plan.md`（§4.1 + §4.2 + §4.3 + §4.6 + §3.6 修正 1/2/3/4）
> **環境變數**：`EMBEDDING_MODEL_NAME=gemini-embedding-2` / `EMBEDDING_OUTPUT_DIMENSIONS=768` / `RAG_SCORE_THRESHOLD=0.22`（預設）/ `RAG_*_TIMEOUT`（MODEL-9）
> **Backfill**：baron OrcStack 端按 plan §4.4 SOP（pkill → `rm -rf output/*/*/vector_store/` → 重啟）執行；觀察 `[chunk filter]` + `[retrieve raw]` log 為 RAG-3 score 校準鋪路。

### Phase 4.7? RAG-8/9 翻譯保留排版下游 bug（2 commits）

| Commit | 內容 | Hash |
|---|---|---|
| RAG-9 | `static/index.html` marked.js GFM strikethrough 關閉、避免單 `~` 配對成 `<del>`（履歷 `100~500 人` / `2003/8~ 仍在職` 等 tilde 範圍語法） | `3a0c523` |
| RAG-8 | `processor/md_restore_processor.py` 加 `_preserve_pipe_table()` helper、L683-684 改用 helper 保留 pipe table 結構；+ 6 個 pytest（`tests/test_md_restore_table_preservation.py`） | `230ca13` |

> **修法依據**：`.claude-logs/2026-05-22_RAG-8_RAG-9_合併診斷_plan.md`（§4.1 + §4.2 修法 1）
> **Backfill**：baron OrcStack 端對 < 10 份既有 paper 重跑 md_restore stage、user-facing 驗證可接受（江元杰 `~` 不再撞線 ✅、DeHunt 學歷 table 自然文字流呈現 ✅、HVDC slides table 欄位對齊正確 ✅）。

### Phase 4.7e Resume 獨立 Pipeline（含 1 次 revert+v2 重做）

| Commit | 內容 | Hash |
|---|---|---|
| 7e-1（舊、已 revert） | ResumeProcessor + Vision prompt + chat_with_images（方向走偏：重組摘要） | `ffb3000` |
| 7e-2（舊、已 revert） | resume 走獨立 ResumeProcessor + doc_analyzer 短路 | `fdc2838` |
| Revert 7e-2 | revert 上述 7e-2 | `32563b5` |
| Revert 7e-1 | revert 上述 7e-1 | `ce91665` |
| 7e-1 v2 | ResumeProcessor 重寫、忠實轉錄 + 主標題黑名單對齊手冊 v2 | `1fb2d7b` |
| 7e-1 v2 hotfix | prompt 加投遞元資訊排除 + 主標題抽取優先順序（解黃忠偉 case） | `eb2164c` |
| 7e-2 v2 | pipeline_core 整合 ResumeProcessor + md_cleaner 跳過（保留 doc_analyzer 雙保險 = baron Q6） | `70889aa` |

> **7e-3 v2** 為 baron OrcStack 端到端 backfill 驗證（重新上傳 DeHunt / 黃忠偉 / 江元杰）、無 commit、純驗證活動；驗證滿意後本系列收尾。

---

## 🟡 進行中 / ⬜ 未開始（依優先序）

### 🔴 高優先

- 🟡 **MODEL-10 MinerU 連線優化與運作維護 SOP**（`baton/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md`）
  - ✅ C1：`pdf_processor.py` MINERU_TIMEOUT 防禦性載入 + L71 timeout 動態化 + Priority 2 廢棄 warning + `.env.example` + 3 pytest
  - ✅ C2：`sop/2026-05-27_mineru_SOP_手冊.md` 新建（≤250 行、SSH Keep-Alive / cron / Priority 2 規格）
  - 🟡 WIP Check：TODO.md 結案 + baton/ 全量歸檔收官
  - 工時：3 個 commits（C1 BE-Refactor + C2 DOC-Refactor + Check DOC-Refactor）
  - 依賴：無

- 🔵 **QUEUE-1 文件優先權協同避讓調度器**（`2026-05-23_QUEUE-1_文件佇列與優先權管控_plan.md`）
  - PipelineCore 實作 class-level 執行緒安全任務註冊表
  - 依 doc_type 與檔案大小自動計算優先權（1/2/3）
  - 階段迭代頂端實作 should_yield 協同避讓與 sleep(2) 迴圈
  - 確保 try...finally 結構保證註冊解除，無死鎖
  - 新增 tests/test_priority_scheduler.py 驗證協同暫停與恢復
  - 工時：1-2 個 commits
  - 依賴：無

- ⬜ **RAG-11 reload SSE 還原**（Bug 6、需獨立 plan 評估）
  - 問題：切換 paper / 重新整理後，SSE chat history reload 功能缺失（API 合約需調整）
  - 工時：待 plan 評估（預估 1-2 commits）
  - 依賴：無

- ⬜ **RAG-12 LaTeX KaTeX 渲染支援**（Bug 9、需獨立 plan 評估）
  - 問題：論文 / 履歷中的 LaTeX 數學公式無法在前端正確渲染（需引入 KaTeX CDN）
  - 工時：待 plan 評估（預估 1 commit）
  - 依賴：無

### 🟡 中優先

- ⬜ **RAG-4 前端引用顯示**（Commit 15 plan Q3）
  - footnote / 「參考章節」清單 / 連結回原文段落
  - 工時：2-3 個 commits（前端 markdown 渲染 + 點擊跳轉）
  - 依賴：15-2 已提供 section_path

- ⬜ **RAG-3 score 閾值 0.22 校準**（Commit 15 plan Q4）
  - 跑 1-2 週實際 query、收 B2 `[retrieve raw]` logging 數據
  - 用 `grep '\[retrieve raw\]' logs/*.log` 抽 raw score 分布
  - 依 p10/p50/p90 調整閾值
  - **L2 normalize 後預期區間**：raw score 會顯著拉寬、相關 chunks 落 0.45-0.75、無關 < 0.25
  - **推測閾值升到 0.35-0.45 區間**（B2 預設保留 0.22、待實測決定）
  - 透過 env override 動態調整：`export RAG_SCORE_THRESHOLD=0.40`（不需 commit）
  - 工時：1 個 commit（純調常數預設 + 加註解、本機 env 已可先調）
  - 依賴：等資料累積（不能立刻做）

- ⬜ **CHAT-3b 前端清理 POST /chat/history 殘留**（Commit 17-4 報告新加）
  - 17-1 已刪 saveChatHistory 函式定義、留 marker 註解（`static/index.html` L2422 + L2487 兩個 Phase 4.7d Commit 17-1 marker）
  - 17-4 已移後端 endpoint
  - 前端可清掉 marker 註解 / dead reference
  - 工時：5-10 分鐘、純清理
  - 依賴：無（與 CHAT-5 可一起做）

### 🟢 低優先

- ⬜ **RAG-5 短文合併上限 cap**（Commit 15-1 已知限制 #3）
  - 實測若 chunk 過大（> 20 text items）需加上限
  - 工時：觀察驅動、實際撞到才做
  - 依賴：實測撞到

- ⬜ **RAG-6 `_SHORT_DOC_TYPES` 寫進 HOW_TO_ADD_DOC_TYPE.md**
  - 補說明短文型決策標準
  - 工時：1 個小 commit、純 docs
  - 依賴：無

- ⬜ **CHAT-4 取消進行中對話功能**（Commit 17 plan Q7）
  - 用戶按 Esc / cancel button 中止 stream
  - broker 支援 cancel：`session.cancelled = True` → `_run_stream_background` 檢查
  - 工時：1-2 個 commits
  - 依賴：留 4.7e 之後

- ⬜ **CHAT-5 `paper_manager.save_chat_history` 移除（dead code）**（Commit 17-4 報告盤點發現）
  - 17-4 後 0 業務 caller、變 dead code candidate
  - 工時：5 分鐘、純清理
  - 依賴：無(與 CHAT-3b 可一起做)

### 🔵 候選（待 baron 評估、依 `.claude-logs/model_optimization_blueprint.md`）

- 🔵 **RAG-10 中文 Header Meta Block 軟換行渲染 bug**（user-facing 排版、修法 ~5 行、低風險）

  **問題**：論文 Header 區的「作者 / 日期 / 出處 / DOI / 關鍵字」blockquote 在前端渲染時全擠成一行、無斷行。

  **症狀範例**（Jian Xu et al. 2026-01-26 Wuhan University paper）：
  ```
  > 作者：Jian Xu、Xinxiong Jiang... 日期：2026-01-26 出處：Wuhan University 關鍵字：AI data center...
  ```
  預期：每個欄位獨立一行。

  **根因**：CommonMark / GFM 規範下、blockquote 內連續多行**無空行**時、會被解析為**軟換行（soft break）**、在 HTML `<p>` 內被瀏覽器渲染為**單一空格**。`marked.js` 預設行為符合此規範（已 grep `static/` 確認無 `marked.setOptions({ breaks: true })`）。

  **代碼證據**（grep `processor/md_restore_processor.py` 實測）：
  - `_render_header_en`（L435 簽名、meta_bits L460-L470）：
    ```python
    meta_bits = []
    if authors_list:
        meta_bits.append(f"> **Authors**: {', '.join(...)}")  # ← 行尾無斷行標記
    if date:
        meta_bits.append(f"> **Date**: {date}")
    if venue:
        meta_bits.append(f"> **Venue**: {venue}")
    if doi:
        meta_bits.append(f"> **DOI**: {doi}")
    if keywords:
        meta_bits.append(f"> **Keywords**: {', '.join(keywords)}")
    ```
  - `_render_header_zh`（L484 簽名、meta_bits L511-L519）：相同 pattern、中文欄位。

  **Markdown 標準斷行語法（三選一）**：
  1. 行尾雙空格 `"  "`（推薦、最低侵入）
  2. 行尾反斜線 `\`
  3. 行之間插入僅有 `>` 的空行

  **修法（推薦從後端產生器修正、不改前端）**：

  在 `_render_header_zh` + `_render_header_en` 兩處 `meta_bits.append(...)` 結尾、每行**字串末尾補兩個半形空格**：

  ```python
  # _render_header_en L460-L470
  meta_bits.append(f"> **Authors**: {', '.join(...)}  ")   # ← 末尾補 "  "
  meta_bits.append(f"> **Date**: {date}  ")
  meta_bits.append(f"> **Venue**: {venue}  ")
  meta_bits.append(f"> **DOI**: {doi}  ")
  meta_bits.append(f"> **Keywords**: {', '.join(keywords)}  ")

  # _render_header_zh L511-L519 同樣處理
  ```

  **為何不用前端 `marked.setOptions({ breaks: true })`**：
  - 全域開啟會把所有 paragraph 內的單換行都變 `<br>`、可能破壞原本應該軟換行的 chunk content 排版（如 PDF 內單句跨行的情況）
  - 從後端修正才是定點打擊、零副作用

  **預估工時**：~30 分鐘（含 pytest）

  **拆 commit**：單一 commit（FIX-1）即可、無依賴

  **新增 pytest**（推薦 2-3 個）：
  - `test_render_header_zh_appends_double_space_for_soft_break`
  - `test_render_header_en_appends_double_space_for_soft_break`
  - `test_rendered_meta_block_has_br_in_html`（mock 過一遍 marked.js 風格的解析、驗證 `<br>` 存在）

  **影響範圍**：
  - 僅影響 `_tiled.json` → 最終 markdown 的 Header 區渲染
  - **不需 backfill**（純前端 markdown 字串差異、既有 paper 重開即生效）
  - 既有 paper 重新前端 load 即修正、無需 vector store 重建

  **依據**：
  - CommonMark §6.7 Blockquote + §6.5 Hard line breaks
  - 修正後 HTML 預期含 `<br>` 而非 inline space

- ⬜ **MODEL-5 Structured Outputs router**（依 model_optimization_blueprint.md §3.2）
  - 升級對話路由器、利用 Gemini SDK Structured Outputs (JSON Schema)
  - Pydantic 聲明 `RouterDecision` 模型、消滅 regex + `json.loads`
  - 改 ai_chat / ai_router 相關檔案
  - 工時：1 commit
  - 依賴：無
  - 解 router 對格式變動的脆弱性

- 🔵 **MODEL-7c Metadata 語意前綴增強**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.3、新增）
  - 在生成 Chunk 文本時、最前端注入全域 Metadata 前綴
    - 範例：`"Candidate: John Doe | DocType: Resume | Section: Employment | [內文]"`
  - 將全域背景與局部細節強制綁定、強化語意特徵、embedding 也吃到 doc-level 語意
  - 工時：0.5 commit
  - 依賴：等 RAG-3 score 校準後評估必要性（可能 MODEL-1+2 已夠用、是否真的需要再評估）
  - **優先度低、純候選**

- ⬜ **MODEL-10 MinerU SSH/SCP → HTTP API**（容器化前置 / 安全強化、依 model_optimization_blueprint.md §4.5）
  - 現狀：`processor/pdf_processor.py` 用 shell `scp -r` + OS 級 SSH key 從 MinerU host 拉圖片
  - 風險：跨平台不可移植、容器化阻塞、SSH key 是安全漏洞、shell command injection 風險
  - 改法：MinerU `/file_parse` endpoint 改回 JSON 含 base64 圖片 / 簽名 URL、Mad Professor 端用標準 httpx 下載
  - 工時：2-3 commits（含 MinerU 端改造）
  - 依賴：先確認 MinerU 是否可改 endpoint
  - 優先度視「是否要 Docker 化部署」決定
  - **本項視為 MODEL 系列中優先度最低、純候選**

### 🚫 評估後不做（依 `.claude-logs/model_optimization_blueprint.md` / `.claude-logs/pipeline_decoupling_plan.md`）

以下提案經評估為過早優化 / 失控感 / 場景不符、暫不加入 TODO：

- **Parent-Child Indexing**（雙層檢索）
  - 提案：履歷子經歷小區塊向量化、父區塊回 LLM
  - 不做理由：履歷已切到 ### 公司層級、單份 7-8 chunks、痛點不大；實作複雜（chunk 結構 + retriever 邏輯 + schema 改動）、3-4 commits regression 風險高

- **128 Batching 自適應**（Embedding API 並行）
  - 提案：BATCH_SIZE 32 → 128、聲稱「30-50x 提速」
  - 不做理由：測試機 + < 10 份文件、batch size 增益無感（可能省 10-20 秒）；撞 429 風險上升、效益數字行銷話術不可信（實際提速 2-3x）

- **企業 Proxy（HTTP_PROXY/HTTPS_PROXY）**
  - 提案：受限網絡 / GFW 部署支援
  - 不做理由：個人測試機 + 台灣環境、無 firewall / 翻牆需求；未來若要賣企業客戶再做

- **AUTO Grounding（Gemini 自動聯網）**
  - 提案：Gemini 模型自己判斷何時聯網查 Google
  - 不做理由：論文 / 履歷分析場景需明確控制資料來源；AUTO 模式下 user 不知道答案來自文件還是 Google、UX 失控；應 user 明確 opt-in、不該預設啟用
  - **note**：手動 opt-in 聯網已存在於既有 `#web-search-toggle` 前端 toggle（`static/index.html` + `web_server.py:375 use_web_search` + `llm/client.py:118` Gemini Grounding）、整鏈路已通；不需新增 task 重做

- **Pipeline 解耦重構（pipeline_decoupling_plan.md 全套）**
  - 提案：17+ 檔重寫、`BaseStage` / `Context` / `Observer` / `Strategy` 完整體系
  - 不做理由：過早抽象、Mad Professor 是 2 人 / < 10 文件規模；7e-2 v2 `KNOWN_DOC_TYPES` + `check_doc_type_registry.py` 已解 80% 痛點；重構期 regression 風險巨大、機會成本超過所有收益；候選漸進式小手術（dict lookup parser / 並行 helper / module-level constants）可考慮、但全套重構不做

- **MODEL-6 聯網搜尋自動 Fallback 降級路由**（依 `.claude-logs/ref/model_optimization_blueprint.md` §3.2）
  - 提案：RAG max score < 0.35 時、自動切換 Web Search + Google Grounding
  - 不做理由：跟既有「AUTO Grounding 不做」決策**直接衝突**、本質是 trigger condition 不同的 AUTO Grounding；user 不知道答案來自文件還是 Google、UX 失控；mad-professor 定位是「論文/履歷分析助手」、用戶問問題期望基於文件
  - **未來若要做、改為「手動 opt-in 聯網按鈕」**、用戶按下才聯網 + 回答時明確標 [Google Search]

- **MODEL-7b 中英雙語對齊嵌入**（依 `.claude-logs/ref/model_optimization_blueprint.md` §5.2）
  - 提案：中英混雜文件、chunking 前拼接「原文 + 譯文」一起 embed、提高跨語召回
  - 不做理由：**gemini-embedding-2 是多語旗艦模型、跨語對齊本身就比舊 model 強得多**（MODEL-1+2 已內建解決 80%）；拼接後每個 chunk 大小翻倍、API tokens / storage 翻倍、是針對舊 model 的 workaround
  - **未來若 B2 backfill 後跑 1-2 週仍有跨語檢索品質問題、再重新評估**

---

## 索引（依類別）

### RAG（9 項 active）
- ✅ ~~RAG-1 Phase 2 hashtag RAG 路由 + 雙語摘要 + chat token UI~~（已落地、P2-1 + P2-2 + P2-3 三 commit、見 ✅ 完成區）
- ✅ ~~RAG-1 Phase 1 前端 UI Fixes + 資料夾自動標籤 + 標籤強制小寫~~（已落地、R1 + R2 + R3 三個 commit、hash 待 push 後回填、見上方 ✅ 完成區）
- ✅ ~~RAG-1 Bug Fix 系列 (BUG-F1~F6 + BUG-B1~B2)~~（已落地、全鏈路收官、8 commits、見 ✅ 完成區）
- RAG-3 score 校準（中、等數據）
- RAG-4 前端引用顯示（中）
- RAG-5 合併 cap（低）
- RAG-6 docs（低）
- 🔵 RAG-10 中文 Header meta block 軟換行渲染 bug（候選、修法 ~5 行、user-facing 排版）
- ⬜ RAG-11 reload SSE 還原（高、需獨立 plan）
- ⬜ RAG-12 LaTeX KaTeX 渲染支援（高、需獨立 plan）
- ⚙️ ~~RAG-2 backfill CLI~~（合併到 MODEL-8、見 MODEL 區）
- ✅ ~~RAG-7 doc_analyzer 切 section~~（已落地、拆 RAG-7a `e2ed0e4` + RAG-7b `5c182cf`）
- ✅ ~~RAG-8 md_restore / translate table 渲染 bug~~ `230ca13`
- ✅ ~~RAG-9 markdown `~` 誤判刪除線~~ `3a0c523`

### Chat（3 項 active）
- CHAT-3b 前端清理（中）
- CHAT-4 取消對話（低、留 4.7e 之後）
- CHAT-5 dead code 清理（低）

### MODEL（0 項中優先 / 3 項候選 / 4 項已落地）
- ✅ ~~MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI~~（已落地、C1 + C2 + C3 三個 commit、hash 待 push 後回填、合併原 RAG-2）
- ✅ ~~MODEL-1+2 Embedding 2 升級 + L2 正規化 + 短 chunk 過濾~~（已落地、B1 `f415218` + B2 `de649cc`）
- ✅ ~~MODEL-3 短文 Bypass + 公式穿透 + 段落滑動~~（已落地、B1 + B2 + B3 三個 commit、hash 待 push 後回填）
- 🔵 MODEL-5 Structured Outputs router
- 🔵 MODEL-7c Metadata 語意前綴（候選、低優先、等 RAG-3 結果再評估）
- ✅ ~~MODEL-9 連線彈性防禦~~（已落地、`dd18922`）
- 🔵 MODEL-10 MinerU SSH/SCP → HTTP（容器化前置、最低優先）

### Phase 4.7e Resume Independent Pipeline（全完工）
- ✅ ~~7e-1 v2~~ `1fb2d7b`
- ✅ ~~7e-1 v2 hotfix~~ `eb2164c`
- ✅ ~~7e-2 v2~~ `70889aa`
- 7e-3 v2 端到端驗證（無 commit、純驗證、baron OrcStack 重新上傳 3 份 backfill 後收尾）

### WORKFLOW（✅ 已完成）
- ✅ ~~WORKFLOW-1 流程簡化與文件治理~~（已落地、C1~C5 六 commits、見 ✅ 完成區）
- ✅ ~~WORKFLOW-2 流程模板重構與提示詞自動歸檔~~（已落地、C1~C5 六 commits、見 ✅ 完成區）

### QUEUE (1 項 active)
- 🔵 QUEUE-1 文件優先權協同避讓調度器（高、`2026-05-23_QUEUE-1_文件佇列與優先權管控_plan.md`）

### OPTIMIZE (1 項 active)
- ✅ ~~OPTIMIZE-1 PDF 上傳自動無損優化~~（已落地、C1 `b8892be` + C2 `28f098e` + C3 收官）

