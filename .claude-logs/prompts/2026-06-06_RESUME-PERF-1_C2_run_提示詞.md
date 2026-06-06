`````markdown
# 2026-06-06 — RESUME-PERF-1 C2 Run（ThreadPool 並行翻譯·序列→受限並行）提示詞

> **收到時間**：2026-06-07 01:38（UTC+8）
> **任務代號**：RESUME-PERF-1 C2（BE-Refactor 階段 4 執行）
> **觸發 commit**：C2
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_tasks.md`
> **觸發情境**：baron 確認 C1 落地後下達 C2 執行指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-07 01:38 | 任務 RESUME-PERF-1 C2 | 觸發 Commit C2 | 依據 tasks.md §8 C2 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-06_RESUME-PERF-1_C2_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C2（BE-Refactor）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C2 ThreadPool 並行翻譯）
1. 備份 resume_pipeline.py → .bak。
2. 檔頭 import（C2 包裹）：from concurrent.futures import ThreadPoolExecutor、from settings import LLM_MAX_CONCURRENT。
3. _restore_sections_markdown「逐 slot 序列翻譯」段改並行：對 title/content slot submit(self._t, text, inj, tr, text_type)、{index:future} 保序回填；raw 不提交；max_workers=max(1,LLM_MAX_CONCURRENT)；實際 API 併發受既有 LLMClient._api_semaphore 限。
4. 異常隔離：取 future.result() try/except → 退回原文 slot["text"] + logger.warning(event=resume_translate_unit_fallback,reason)；不中斷其餘、保交付。
5. 組裝段（title 前綴/PARA 正規化/raw）不動、按 slot 原序；退化 _translate_whole/zh* 不並行不動。
6. # === [RESUME-PERF-1 C2 START/END] === 包裹。

### 三道防線
- 物理：僅 resume_pipeline.py（tasks §7）；測試：grep（ThreadPoolExecutor/LLM_MAX_CONCURRENT/異常隔離 warning event）+ SOP（logger.error exc_info / 無裸 commit）+ pytest test_resume_pipeline 既有 29 全綠（行為等價）；文件：commit 由 baron。

### 備份
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-PERF-1_C2_resume_pipeline.py.bak

### TODO 同步 + Hash 自癒
C2 → ✅ done（待回填）；C3 → 🟡 WIP；git log 回填殘留佔位符。

### 產出（baton 暫存紅線）
baton/2026-06-06_RESUME-PERF-1_C2_執行.md（暫存、嚴禁 git add、C4 才歸檔）；§8 git add 清單（不含 baton 報告）+ msg（/tmp/RESUME-PERF-1_C2_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C3、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（import ThreadPoolExecutor/LLM_MAX_CONCURRENT + 翻譯段序列→並行 + 單 unit 異常隔離退原文+warning）+ .bak
- 驗收：grep（ThreadPool/LLM_MAX_CONCURRENT/異常隔離）+ SOP + pytest 既有 29 全綠（行為等價）
- 報告：baton/..._C2_執行.md（暫存、不 git add）
- 是否動其他業務代碼：否；是否 commit：否（待 baron）

## 後續引用

C2 並行落地、保序靠 slot index、限流靠既有 semaphore、單 unit 失敗退原文；下一步 C3（並行專屬測試：byte 等拍保序/併發峰值≤上限/異常隔離/退化單呼叫）。
`````
