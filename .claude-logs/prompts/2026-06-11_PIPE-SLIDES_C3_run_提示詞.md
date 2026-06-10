# PIPE-SLIDES C3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 04:15 |
| 任務代號 | PIPE-SLIDES C3 |
| 觸發 Commit | C3 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES_..._tasks.md` |
| 觸發情境 | baron 確認 C2 後，下達 C3 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES / C3 — P2 Six-Step / BE-Refactor；tasks §8 C3（plan U5/U6、Q 定案）

### 執行命令（tasks §8 C3）
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② slide_pipeline.py 實作 run_phase2（`# === [PIPE-SLIDES C3 START/END] ===` 包裹）統一六步：
   ① 全文摘要（prompt 同呼叫順產 raw_domain 一行、缺→None 降級）
   ② 批次每頁摘要（同呼叫對無標題頁順產標題、缺→p{N} 裸序兜底）；key=p{頁序}_{原文頁標題}
   ③ normalize_to_lcc(raw_domain, context=摘要) ④ Glossary 級聯（query_cascade→extract_terms〔全文+摘要+LCC〕→upsert 冪等、LLM 交易外）
   ⑤ 翻全文摘要（DEEP_THINK） ⑥ 批次翻頁摘要 → GlossaryReadySpec.section_summaries + domain_name
   三安全鎖（批次有界/非致命/可量測 performance_metric phase=P2）
③ tests 追加 C3 mock 測試（六步序/key 不撞/無標題順產/raw_domain 順產+降級/section_summaries 對位）
- 物理防線：僅兩檔；嚴禁改共用元件/A 軌；SOP §5.2 無裸 commit

### 驗收（§6.3）
- pytest + grep '\.commit\(\)' 無裸 commit

### TODO 同步
- C3 ✅、C4 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES_C3_執行.md（暫存、不入版控）

### §8 baron 命令
- git add：兩檔 + 2 .bak + 2 prompts + TODO；msg → /tmp/PIPE-SLIDES_C3_msg.txt

### 停止
- 產出 C3_執行.md 後立即停止；不續 C4、不自發 commit/push
