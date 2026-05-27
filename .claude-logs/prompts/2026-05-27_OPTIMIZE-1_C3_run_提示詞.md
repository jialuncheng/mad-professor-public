# 2026-05-27 — OPTIMIZE-1 C3 Run 提示詞

> **收到時間**：2026-05-27 16:06
> **任務代號**：OPTIMIZE-1 C3
> **觸發 Commit**：C3
> **相關產出檔案**：`.claude-logs/baton/2026-05-27_OPTIMIZE-1_C3_執行.md`
> **觸發情境**：baron 確認 C2 成功落地後，下達 C3 歸檔收官指令

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-05-27 16:06` |
| **任務代號** | `OPTIMIZE-1 C3` |
| **觸發 Commit** | `C3` |
| **相關產出檔案** | `.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md` |
| **觸發情境** | `baron 確認 C2 成功落地後，下達 C3 歸檔收官指令` |

你現在扮演 Claude Code，請執行 C3 — Final Archiving and TODO Sync（收官歸檔與 TODO 結案同步）。

任務編碼：OPTIMIZE-1
當前 Commit 代號：C3
工作流類別：DOC-Refactor
Tasks 路徑：.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md

強制讀檔清單：
- CLAUDE.md
- .claude-logs/ref/WORKFLOW_SOP.md
- .claude-logs/TODO.md
- .claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md（§8 C3 實作細節）

三大防線：
1. 物理防線：除 TODO.md 外，嚴禁修改任何業務代碼。本 Commit 只允許對 baton/ 暫存文件進行 mv 搬移與 INDEX.md 變更。
2. 測試防線：必須在 Mac 宿主機調用穿透指令 orb pytest tests/ -v 以在虛擬機內部執行全套單元測試，確保搬移後測試依然 100% 通過（無 regression）。並物理核查 baton/ 移出狀態。
3. 文件防線：所有 commit / push 由 baron 手動執行，嚴禁自發執行 commit 或 push。

備份規則：
cp .claude-logs/TODO.md .claude-logs/archive/2026-05-27_OPTIMIZE-1_C3_TODO.md.bak
（備份必須在 §8 git add 清單中強制包含）

TODO.md 更新：
1. 結案（WIP 移出 → ✅ 已完成表格追加）
2. 歷史 Hash 自愈（git log 掃描、填入所有「待 baron 回填」）

產出：
- .claude-logs/baton/2026-05-27_OPTIMIZE-1_C3_執行.md（暫存 baton/）
- 套用 template_execution.md
- §8 baron 執行命令（git add 清單 + commit message 至 /tmp/OPTIMIZE-1_C3_msg.txt）

全量 mv 歸檔：
- baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md → plans/
- baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md → tasks/
- baton/2026-05-23_OPTIMIZE-1_C1_執行.md → executions/
- baton/2026-05-27_OPTIMIZE-1_C2_執行.md → executions/
- baton/2026-05-27_OPTIMIZE-1_C3_執行.md → executions/（C3 執行報告直接寫入 executions/）

嚴禁：業務代碼修改 / git commit/push
```

---

## 執行結果摘要

（待執行後填入）

## 後續引用

- 本任務全部 3 個 Commit 收官，OPTIMIZE-1 完工。

> 本文件為 OPTIMIZE-1 C3 Run 提示詞歸檔，記錄 baron 下達 C3 收官指令（baton/ 全量 mv 歸檔 + TODO.md 結案）的完整意圖。
