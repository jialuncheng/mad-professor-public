`````markdown
# 2026-06-06 — RESUME-PERF-1 plan 撰寫提示詞（run_phase3 逐 section 翻譯並行化）

> **收到時間**：2026-06-06（UTC+8）
> **任務代號**：RESUME-PERF-1（perf 候選 plan·plan 階段）
> **觸發情境**：分析 A軌 golden capture log 發現 translate 序列 331.85s = 全程 77%；grep 確認 B軌 `run_phase3` `_restore_one_section` 同樣序列呼叫 `_t`（無 async/gather/ThreadPool）→ B軌 resume 上線後同樣 ~300s 序列瓶頸。baron 拍板「B軌 resume 接近上線時開一張 perf plan（run_phase3 並行化 _restore）」、存 baton/、依 template_plan、不用給 commit 建議。

---

## 完整提示詞

````
在 B軌 resume 接近上線時開一張 perf plan（run_phase3 並行化 _restore）
針對以上內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

不用給commit建議
````

---

## 上文脈絡（grep 鋼證）

- A軌 golden capture log：translate 331.85s（77%）、~40 個序列 `streamGenerateContent`、長專利 block 單個 13~30s。
- B軌同病：`resume_pipeline.py:578/587/599` `_t(...)` 同步序列、`:603` 遞迴序列、無 `await/asyncio/gather/ThreadPool`。
- 基建現成：`LLMClient._api_semaphore = threading.Semaphore(LLM_MAX_CONCURRENT=6)`（client.py:49）；`Translator.translate` 用 locals、無 per-call 可變狀態 → thread-safe。
- 方向：`run_phase3` 逐 section 翻譯改 ThreadPool 並行（受既有 LLM semaphore 限流）、保序、不動 HEADING/PARA/META 組裝。

## 執行結果摘要

- 產出：`baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_plan_v1.md`（依 template_plan、含 §2 目標規格 / §3 grep 證據 / §4 不可動 / §6 驗證 / §7 OQ；不含 commit 建議）
- 性質：plan 階段文件（不動業務代碼）；tasks 由 baron 後續觸發
- 是否動 .py：否；是否 commit：否

## 後續引用

並行化 `_restore`（兩段式：收集→並行翻譯→保序組裝）、受 `LLMClient._api_semaphore` 限流、行為等價（同 unit/同序/同 prompt）、HEADING/PARA/META 不變；實施時機＝resume 上線前、A軌不動。
`````
