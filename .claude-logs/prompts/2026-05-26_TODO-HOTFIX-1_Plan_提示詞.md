# 2026-05-26 — TODO-HOTFIX-1 Plan 提示詞

> **收到時間**：2026-05-26 00:00（估算）
> **任務代號**：TODO-HOTFIX-1 Plan
> **觸發 commit**：無（Plan 階段，無 commit）
> **相關產出檔案**：`.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_hotfix.md`
> **觸發情境**：baron 在 WORKFLOW-1 收官後發現 TODO.md 有多處狀態損毀（RAG-1 Bug Fix 系列殘留 active 區、BUG-B1/B2 hash 缺失、RAG-11/12 未獨立為主條目、MODEL-8 active 殘留），委託 Claude Code 執行緊急診斷並產出熱修復規劃書

---

## 完整提示詞

```
TODO-HOTFIX-1 — 緊急診斷並產出規劃書

任務：DOC-Hotfix / TODO.md 損毀修復
目標檔：.claude-logs/TODO.md

請對 TODO.md 執行以下診斷與規劃：

1. 診斷阻斷現象（4 項）
   - 現象一：RAG-1 Phase 2 條目殘留 active 區（已完成任務未搬移）
   - 現象二：RAG-1 Bug Fix 系列 bullet block 損毀（8 個 BUG-F1~F6+BUG-B1~B2 以 bullet 子列嵌入 active 區、非已完成表格）
   - 現象三：✅ 已完成區缺少 Bug Fix 系列獨立表格
   - 現象四：RAG-11 / RAG-12 以子條目嵌入 Bug Fix block，未獨立為高優先主條目
   
2. Hash 盤點（via git log）
   - 確認 BUG-F1~F6 的真實 hash
   - 補填 BUG-B1（待回填）= `a35a720`
   - 補填 BUG-B2（待回填）= `94ed27d`
   
3. 產出熱修復規劃書（hotfix.md）至 baton/ 暫存
   - 修法 A~D + 修法 E（MODEL-8 殘留）
   - Commit 拆分六維度表格
   - E2E 驗收計畫（V1~V6）

業務代碼零改動。等待 baron 評估確認後方可執行。
```

---

## 執行結果摘要

- ✅ TODO.md 四大損毀現象診斷完成
- ✅ Hash 盤點確認（BUG-F1~F6 + BUG-B1~B2 全部確認）
- ✅ 規劃書產出：`baton/2026-05-26_TODO-HOTFIX-1_hotfix.md`
- ✅ 5 項修法（A/B/C/D/E）規劃 + 2 commit 拆分（TODO-HOTFIX-1 + TODO-HOTFIX-1b）

## 後續引用

- Run 提示詞：`.claude-logs/prompts/2026-05-26_TODO-HOTFIX-1_Run_提示詞.md`

> 本文件為歷史補建版本，非原始逐字記錄。依對應規劃書 §§ 阻斷性問題/修法/Commit 拆分 以摘要方式還原（WORKFLOW-2 R5 補建）。
