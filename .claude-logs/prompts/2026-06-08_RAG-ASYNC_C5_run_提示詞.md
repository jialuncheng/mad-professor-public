`````markdown
# 2026-06-08 — RAG-ASYNC C5 Run（P2 Six-Step·統一六步 section_summaries）提示詞

> **收到時間**：2026-06-08 06:14（UTC+8）
> **任務代號**：RAG-ASYNC C5（BE-Refactor·階段 4 執行）
> **觸發 commit**：C5
> **相關產出檔案**：`.claude-logs/baton/2026-06-08_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_tasks.md`
> **觸發情境**：baron 確認 C4 向量落庫報告後，下達 C5 P2 統一六步流程開發指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-08 06:14 | 任務 RAG-ASYNC C5 | 觸發 Commit C5 | 依據 tasks §8 C5 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-08_RAG-ASYNC_C5_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C5（BE-Refactor·P2 統一六步）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / PROJECT_PROGRESS_CONTROL_FRAMEWORK.md / tasks.md / logging SOP / database SOP / resume_pipeline.py / test_resume_pipeline.py

### 執行命令（依 tasks §8 C5 具體實作細節）
1. 物理防線（§7 不可動）；2. 測試防線（§6.5 grep + pytest test_resume_pipeline）；3. 文件防線（不自發 commit）；
4. 既有檔修改區塊 # === [RAG-ASYNC C5 START/END] === 包裹。

### 備份
cp resume_pipeline.py / test_resume_pipeline.py → archive/…_C5_….bak

### 改動
- run_phase2 四步→六步：② 產章節摘要（原文、非 book 1 次批次、可併①）+ ⑥ 以全文摘要引導一次性批次翻全部章節摘要 → 繁中 section_summaries（超 token 拆批）。
- 三安全鎖：批次（非 N 次）/ 非致命（②⑥ 失敗該節點留空、不阻 reading_ready、不拋、logger.warning exc_info + extra_fields）/ 可量測（performance_metric phase=P2 埋點）。
- 交付 GlossaryReadySpec(section_summaries=…)。
- SOP：LLM 交易外、logger.error/warning 非致命 fallback 須 exc_info、extra_fields 規範。
- test_resume_pipeline.py：產 section_summaries（key 對位 section）/ ②⑥ 批次（mock 計呼叫數驗非 N）/ 某 section 摘要拋例外 → 留空 + spec 交付 + 不拋。

### Git 可入庫
archive/ 2 .bak + resume_pipeline.py + test_resume_pipeline.py；baton（含 _執行.md）C7 前不 git add。

### TODO 同步 + Hash 自癒
C5 → ✅；C6 → 🟡 WIP；git log 回填佔位符。

### 產出（baton 暫存）
baton/2026-06-08_RAG-ASYNC_C5_執行.md（暫存、不 git add）；§5 貼 pytest + SOP（LLM 交易外 / exc_info+extra_fields）；§8 git add 清單 + msg（/tmp/RAG-ASYNC_C5_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C6、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（run_phase2 六步 + section_summaries 批次產+翻 + 三安全鎖）+ test_resume_pipeline.py；各 .bak
- 驗收：grep（section_summaries / performance_metric / 批次）+ pytest + SOP（交易外 / exc_info+extra_fields）
- 報告：baton/…_C5_執行.md（暫存、不 git add）
- 是否動業務代碼：是（run_phase2）；是否 commit：否（待 baron）

## 後續引用

C5 P2 統一六步 section_summaries 落地（批次產+翻、三安全鎖）；下一步 C6（P3 旁路封存譯後 section 結構 + run_phase4 改呼 rag_indexer、砍 rag_processor import）。
`````
