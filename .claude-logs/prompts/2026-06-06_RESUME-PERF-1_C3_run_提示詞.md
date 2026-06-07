`````markdown
# 2026-06-06 — RESUME-PERF-1 C3 Run（Unit Tests·並行專屬測試）提示詞

> **收到時間**：2026-06-07 01:44（UTC+8）
> **任務代號**：RESUME-PERF-1 C3（BE-Refactor 階段 4 執行）
> **觸發 commit**：C3
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_tasks.md`
> **觸發情境**：baron 確認 C2 落地後下達 C3 執行指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-07 01:44 | 任務 RESUME-PERF-1 C3 | 觸發 Commit C3 | 依據 tasks.md §8 C3 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-06_RESUME-PERF-1_C3_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C3（BE-Refactor）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C3 Unit Tests）
1. 備份 tests/test_resume_pipeline.py → .bak。
2. 追加 4 並行專屬測試（mock Translator 回確定化 f"ZH::{text}"、不打真 API、# === [RESUME-PERF-1 C3 START/END] === 包裹）：
   - test_p3_parallel_order_byte_equal：多層多 section〔title/text/raw/children〕→ run_phase3 輸出 == 預期序列組裝〔保序 + 層級 ##/###/#### + PARA 空行〕。
   - test_p3_parallel_concurrency_capped：patch resume_pipeline.LLM_MAX_CONCURRENT=2 + fake translate 計數 lock 製造重疊、斷言峰值 ≤ 2。
   - test_p3_parallel_unit_error_isolated：某 text 翻譯拋例外 → 該段退原文、其餘正常、BilingualMarkdownSpec 仍交付。
   - test_p3_parallel_degraded_single_call：heading 退化 → _translate_whole 單呼叫、未走並行〔calls==1〕。
3. 不動 resume_pipeline.py 業務碼（C3 僅改 tests）。

### 三道防線
- 物理：僅 tests/test_resume_pipeline.py（tasks §7）；測試：grep 4 新測試 + pytest test_resume_pipeline 全綠 + 全套件不退化；文件：commit 由 baron。

### 備份
cp tests/test_resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-PERF-1_C3_test_resume_pipeline.py.bak

### TODO 同步 + Hash 自癒
C3 → ✅ done（待回填）；C4 → 🟡 WIP；git log 回填殘留佔位符（含 C2）。

### 產出（baton 暫存紅線）
baton/2026-06-06_RESUME-PERF-1_C3_執行.md（暫存、嚴禁 git add、C4 才歸檔）；§8 git add 清單（不含 baton 報告）+ msg（/tmp/RESUME-PERF-1_C3_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C4、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：tests/test_resume_pipeline.py（追加 4 並行專屬測試）+ .bak
- 驗收：grep 4 新測試 + pytest test_resume_pipeline 全綠 + 全套件不退化
- 報告：baton/..._C3_執行.md（暫存、不 git add）
- 是否動業務代碼：否（純測試）；是否 commit：否（待 baron）

## 後續引用

C3 並行專屬測試落地（保序 byte 等拍/併發峰值≤上限/異常隔離/退化單呼叫）；下一步 C4（Checkout 三維度驗收 + baton 一次性歸檔收官）。
`````
