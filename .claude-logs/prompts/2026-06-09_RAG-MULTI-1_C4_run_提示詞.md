# RAG-MULTI-1 C4 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-09 |
| 任務代號 | RAG-MULTI-1 C4 |
| 觸發 Commit | C4 |
| 工作流類別 | BE-Refactor（純新增測試檔、無業務碼）|
| 相關產出檔案 | `.claude-logs/baton/2026-06-09_RAG-MULTI-1_跨文件多篇檢索覆蓋與引用修正_tasks.md` |
| 觸發情境 | baron 確認 C3 落地，下達 C4 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- 任務編碼：RAG-MULTI-1 / Commit：C4 / 工作流類別：BE-Refactor（純測試）
- Tasks 路徑：`.claude-logs/baton/2026-06-09_RAG-MULTI-1_..._tasks.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md / framework / tasks.md（§8 C4）/ logging SOP / database SOP / template_execution
- 參考既有 `tests/test_phase2_p2_2_hashtag_routing.py` 的 `_make_retriever_with_mock_papers` mock 範式

### 執行命令（依 tasks §8 C4、對齊 plan v3 §8.1）
新建 `tests/test_rag_multi.py`（檔頭 `# === [RAG-MULTI-1 C4] ===`），mock vector store 確定化分數、**不 mock retrieve_multi 本體**，11 測試：
1 per_paper_floor / 2 floor_underfilled_takes_all / 3 small_n_no_floor_balloon（N=3 floor=2 非 5）/
4 cap_not_exceeded / 5 n_gt_cap_truncate_by_best / 6 global_fill_excludes_floored /
7 zero_candidate_paper_skipped / 8 cap_override_param / 9 mixed_doctype_small_not_starved（book 100 chunk 不壓 resume）/
10 single_path_unchanged / 11 prompt_forbids_bracket_citation（grep ai_character_prompt 禁 [N]）。
- 物理防線：只新建測試檔；**嚴禁改業務碼**（rag_retriever/settings/ai_character_prompt）；測試對不上 → 停下回報、不弱化斷言/不改實作。
- 純新建檔、無 .bak。

### SOP 核查（BE-Refactor）
- logging：grep logger.error test_rag_multi.py → 無命中（合規）。
- database：grep `.commit()` test_rag_multi.py → 無命中（合規）。

### 同步更新 TODO
- C4 ✅、C5 🟡 WIP；git log 自癒回填殘留「待 baron 回填」。

### 產出規格
- 執行報告 `baton/2026-06-09_RAG-MULTI-1_C4_執行.md`（暫存 baton、嚴禁 mv/git add、baton 不入 git、C5 才歸檔）；套 template_execution；§5 貼 11 測試逐一 PASSED + 全套件。

### §8 baron 執行命令
- git add：tests/test_rag_multi.py + TODO + 2 prompts（baton 執行報告不 git add）。
- msg 草稿寫 `/tmp/RAG-MULTI-1_C4_msg.txt`，`test(rag)` 前綴、署名 Claude Opus 4.8 (1M context)。

### 停止指令
產出執行報告（暫存 baton）後立即停止；不續 C5、不改業務碼、不 mv/git add baton、不自發 commit/push。
