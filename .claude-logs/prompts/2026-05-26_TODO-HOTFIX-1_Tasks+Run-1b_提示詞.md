# 2026-05-26 — TODO-HOTFIX-1 Tasks+Run-1b 提示詞

> **收到時間**：2026-05-26 00:00（估算）
> **任務代號**：TODO-HOTFIX-1b（Tasks 確認 + Run-1b 執行）
> **觸發 commit**：TODO-HOTFIX-1b（`2c78f9e`）
> **相關產出檔案**：`.claude-logs/baton/2026-05-26_TODO-HOTFIX-1b_執行.md`
> **觸發情境**：baron 確認 TODO-HOTFIX-1 執行完成並手動 commit 後，授權執行 TODO-HOTFIX-1b：MODEL-8 active 區殘留清理（修法 E）

---

## 完整提示詞

```
TODO-HOTFIX-1b — 執行 MODEL-8 Active 殘留清理

任務：TODO-HOTFIX-1b / DOC-Hotfix
依據規劃：.claude-logs/baton/2026-05-26_TODO-HOTFIX-1_hotfix.md（修法 E + 六維度表格 TODO-HOTFIX-1b）

前置確認：TODO-HOTFIX-1（a0d1951）已 commit 完成。

修改前備份：cp .claude-logs/TODO.md .claude-logs/archive/2026-05-26_TODO-HOTFIX-1b.md.bak

執行修法 E（單一 commit TODO-HOTFIX-1b）：

1. 確認 ✅ 已完成區 MODEL-8 表格完整性（只讀，不修改）
   - C1 = aeb42cb ✅
   - C2 = ab40fdc ✅
   - C3 = 16f62d4 ✅

2. 移除 active 區 MODEL-8 殘留行
   - 位置：### 🟡 中優先 區段
   - 刪除：「- ✅ ~~**MODEL-8 SQLite paper_chunks 物理防線 + 增強型 backfill CLI**~~...」一行及後方多餘空行

3. 更新 TODO-HOTFIX-1 任務兩個子項進度 → ✅ done

驗收：active 區 MODEL-8 0 命中（✅ 區第 71 行 + 索引區除外）
業務代碼零改動。停止指令：嚴禁 git commit/push。
```

---

## 執行結果摘要

- ✅ MODEL-8 active 區殘留行（+ 多餘空行）徹底移除
- ✅ ✅ 已完成區 MODEL-8 表格確認完整（不修改）
- ✅ TODO-HOTFIX-1 兩子項更新為 ✅ done
- ✅ V1b/V2b 驗收通過
- 觸發 Commit：`2c78f9e`

## 後續引用

- Check 提示詞：`.claude-logs/prompts/2026-05-26_TODO-HOTFIX-1_Check_提示詞.md`

> 本文件為歷史補建版本，非原始逐字記錄。依對應執行報告 §4 修法說明以摘要方式還原（WORKFLOW-2 R5 補建）。
