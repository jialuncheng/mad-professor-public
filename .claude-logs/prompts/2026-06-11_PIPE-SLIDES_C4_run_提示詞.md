# PIPE-SLIDES C4 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 04:37 |
| 任務代號 | PIPE-SLIDES C4 |
| 觸發 Commit | C4 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES_..._tasks.md` |
| 觸發情境 | baron 確認 C3 後，下達 C4 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES / C4 — P3 Per-Page Translate & Restore / BE-Refactor；tasks §8 C4（plan U7-U10、Q3/Q4/Q5 定案）

### 執行命令（tasks §8 C4）
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② slide_pipeline.py 實作 run_phase3（`# === [PIPE-SLIDES C4 START/END] ===` 包裹）：
   - 逐頁 InjectionContext(lcc/glossary/zh_summary=P2 譯摘要/domain_name/constraints=_SLIDE_CONSTRAINTS/doc_type='slides') → Translator NORMAL
   - 並行照抄 RESUME-PERF-1（ThreadPool+slot index 保序+既有 _api_semaphore+單頁失敗退原文）
   - 還原 `![alt](images/page-N.jpg)`+譯文、alt=Vision description 譯文（en 版原文）、嚴禁 *圖表：* 段、不渲染 meta header
   - _SLIDE_CONSTRAINTS（Q4）：品牌/產品原文、術語中英並列、cell 禁 ###、數字/單位原樣
   - ctx.rag_sections 旁路（summary_key=page_key 同基準）+ 同頁短 items 合併（Q3 策略側）
   - zh 來源跳譯仍建 per-section（SPEC U4）；fallback（Q5：頁數=1 或 >50% 頁空→整檔單發）
③ tests 追加 C4 mock 測試（無圖表段/alt/並行保序/合併/zh/fallback/無 header）
- 物理防線：僅兩檔；不污染 rag_indexer

### 驗收（§6.4）
- pytest + grep（_SLIDE_CONSTRAINTS / 渲染路徑無「圖表：」）

### TODO 同步
- C4 ✅、C5 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES_C4_執行.md（暫存、不入版控）

### §8 baron 命令
- git add：兩檔 + 2 .bak + 2 prompts + TODO；msg → /tmp/PIPE-SLIDES_C4_msg.txt

### 停止
- 產出 C4_執行.md 後立即停止；不續 C5、不自發 commit/push
