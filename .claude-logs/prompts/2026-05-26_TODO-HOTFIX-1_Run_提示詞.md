# 2026-05-26 — TODO-HOTFIX-1 Run 提示詞

> **收到時間**：2026-05-26 00:00（估算）
> **任務代號**：TODO-HOTFIX-1 Run
> **觸發 commit**：TODO-HOTFIX-1（`a0d1951`）
> **相關產出檔案**：`.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_執行.md`
> **觸發情境**：baron 評估 TODO-HOTFIX-1 規劃書確認無誤後，授權執行 TODO-HOTFIX-1：RAG 狀態整理、Bug Fix 表格補建、RAG-11/12 抽離為獨立主條目

---

## 完整提示詞

```
TODO-HOTFIX-1 — 執行 RAG 狀態修復

任務：TODO-HOTFIX-1 / DOC-Hotfix
依據規劃：.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_hotfix.md

修改前備份：cp .claude-logs/TODO.md .claude-logs/archive/2026-05-26_TODO-HOTFIX-1.md.bak

執行修法 A~D（單一 commit TODO-HOTFIX-1）：

修法 A：在 ## ✅ 已完成 建立 Bug Fix 系列標準表格
- 位置：Phase 4.X? RAG-1 Phase 2 表格之後
- 內容：8 commits（BUG-F1~F6 + BUG-B1~B2）完整表格
- 補填 BUG-B1 hash = a35a720
- 補填 BUG-B2 hash = 94ed27d

修法 B：從 ## 🟡 進行中 徹底移除損毀 block（第 198–213 行）
- 刪除：RAG-1 Phase 2 殘留條目
- 刪除：RAG-1 Bug Fix 系列 parent + 8 子條目 + RAG-11/12 子條目 + 孤兒 heading

修法 C：在 🔴 高優先 新增 RAG-11 / RAG-12 獨立主條目
- ⬜ RAG-11 reload SSE 還原（Bug 6、需獨立 plan）
- ⬜ RAG-12 LaTeX KaTeX 渲染支援（Bug 9、需獨立 plan）

修法 D：更新索引 ## 索引 → ### RAG 段
- 計數 7 → 9 項 active
- 新增 BUG-F1~F6+BUG-B1~B2 ✅ 條目 + RAG-11/12 ⬜ 條目

E2E 驗收（V1~V6）後產出執行報告至 baton/。
停止指令：嚴禁繼續 TODO-HOTFIX-1b，嚴禁 git commit/push。
```

---

## 執行結果摘要

- ✅ 修法 A：✅ 已完成區 Bug Fix 表格建立（8 commits，BUG-B1/B2 hash 補填）
- ✅ 修法 B：active 區損毀 block（198~213 行）徹底清除
- ✅ 修法 C：RAG-11/RAG-12 獨立為 🔴 高優先 ⬜ 主條目
- ✅ 修法 D：索引 RAG 計數 7→9 + 3 新條目
- ✅ V1~V6 全通過
- 觸發 Commit：`a0d1951`

## 後續引用

- Tasks+Run-1b 提示詞：`.claude-logs/prompts/2026-05-26_TODO-HOTFIX-1_Tasks+Run-1b_提示詞.md`

> 本文件為歷史補建版本，非原始逐字記錄。依對應執行報告 §4 修法說明以摘要方式還原（WORKFLOW-2 R5 補建）。
