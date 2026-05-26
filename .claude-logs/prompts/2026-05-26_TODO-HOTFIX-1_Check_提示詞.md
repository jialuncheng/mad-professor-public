# 2026-05-26 — TODO-HOTFIX-1 Check 提示詞

> **收到時間**：2026-05-26 00:00（估算）
> **任務代號**：TODO-HOTFIX-1 Check
> **觸發 commit**：TODO-HOTFIX-1 Check（`5f3ef01`）
> **相關產出檔案**：`.claude-logs/executions/2026-05-26_TODO-HOTFIX-1_Check_執行.md`
> **觸發情境**：baron 確認 TODO-HOTFIX-1 與 TODO-HOTFIX-1b 兩個 commits 均已手動執行，下達 TODO-HOTFIX-1 Check 指令：執行全案 Conformance 驗收 + baton 全歸檔收官

---

## 完整提示詞

```
TODO-HOTFIX-1 Check — Conformance 驗收與歸檔收官

任務：TODO-HOTFIX-1 Check / DOC-Hotfix
依據規劃：.claude-logs/hotfixes/2026-05-26_TODO-HOTFIX-1_hotfix.md
執行報告清單：
  .claude-logs/baton/2026-05-26_TODO-HOTFIX-1_執行.md
  .claude-logs/baton/2026-05-26_TODO-HOTFIX-1b_執行.md

Conformance 驗收（8 項）：
V1：BUG-F1/BUG-B1 在 ✅ 已完成區命中
V2：BUG-B1 a35a720 / BUG-B2 94ed27d hash 存在
V3：Active 區無 ~~**RAG-1 殘留（0 命中）
V4：孤兒 heading 已移除（Phase 4.X? RAG-1 Bug Fix 僅 ✅ 區 1 命中）
V5：RAG-11/RAG-12 出現為獨立主條目
V6：業務代碼零改動
V1b：MODEL-8 active 區 0 命中
V2b：業務代碼零改動

全部合規後執行收官：
1. TODO.md 更新
   - ✅ 已完成頂部新增 TODO-HOTFIX-1 三列表格（TODO-HOTFIX-1/1b/Check，hash 待 baron 回填）
   - 移除 active 區 TODO-HOTFIX-1 WIP 條目

2. baton/ 歸檔（全部使用系統 mv，嚴禁 git mv）
   - hotfix.md → hotfixes/
   - TODO-HOTFIX-1 執行.md → executions/
   - TODO-HOTFIX-1b 執行.md → executions/
   - TODO-HOTFIX-1 Check 執行.md → executions/

3. prompts/INDEX.md 補登 TODO-HOTFIX-1 提示詞索引

停止指令：嚴禁 git commit/push，baron 手動執行。
```

---

## 執行結果摘要

- ✅ Conformance 驗收：8 項全部通過
- ✅ TODO.md：TODO-HOTFIX-1 三列表格新增（頂部）+ active WIP 條目清除
- ✅ baton/ 4 份文件歸檔完成（hotfixes/ + executions/）
- ✅ prompts/INDEX.md 補登
- 觸發 Commit：`5f3ef01`

## 後續引用

- （本 TODO-HOTFIX-1 全案完工，無後續引用）

> 本文件為歷史補建版本，非原始逐字記錄。依對應執行報告 §3 Conformance 驗收 + §4 變動檔案清單以摘要方式還原（WORKFLOW-2 R5 補建）。
