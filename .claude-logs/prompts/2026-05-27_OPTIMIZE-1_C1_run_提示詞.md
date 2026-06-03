# 2026-05-27 — OPTIMIZE-1 C1 Run 提示詞

> **收到時間**：2026-05-27 11:59
> **任務代號**：OPTIMIZE-1 C1
> **觸發 Commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-05-23_OPTIMIZE-1_C1_執行.md`
> **觸發情境**：baron 同意 tasks.md 規格，下達 C1 執行指令

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-05-27 11:59` |
| **任務代號** | `OPTIMIZE-1 C1` |
| **觸發 Commit** | `C1` |
| **相關產出檔案** | `.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md` |
| **觸發情境** | `baron 同意 tasks.md 規格，下達 C1 執行指令` |

你現在扮演 Claude Code，請執行以下指定的單一 Commit/OP。

任務編碼：OPTIMIZE-1
當前 Commit 代號：C1
工作流類別：BE-Refactor
Tasks 路徑：.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md

強制讀檔清單：
- CLAUDE.md
- .claude-logs/ref/WORKFLOW_SOP.md
- .claude-logs/sop/2026-05-23_logging_SOP_手冊.md
- .claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md（§8 C1 實作細節）

執行範圍：tasks.md §8 C1 — Implement Core Optimization Module with Atomic Overwrite（實作無損優化核心與單元測試）

三大防線：
1. 物理防線：本 Commit 僅允許新建 utils/pdf_optimizer.py 與 tests/test_pdf_optimize.py
2. 測試防線：必須執行 §6.1 grep 合規自檢與 pytest tests/test_pdf_optimize.py -v
3. 文件防線：嚴禁自發 commit/push

備份規則：無修改既有業務檔案，免除 .bak 備份（合規）。

TODO.md 更新：
- C1 改為 ✅ 已完成
- C2 改為 🟡 WIP
- 執行 git log 掃描歷史 hash，自愈 TODO.md 中的「待 baron 回填」佔位符

產出：
- .claude-logs/baton/2026-05-23_OPTIMIZE-1_C1_執行.md（暫存 baton/）
- 套用 template_execution.md
- §8 baron 執行命令（git add 清單 + commit message 草稿至 /tmp/OPTIMIZE-1_C1_msg.txt）

嚴禁：C2 執行 / 修改未列入 C1 的代碼 / git commit/push
```

---

## 執行結果摘要

（待執行後填入）

## 後續引用

- 下一步：baron 驗收 C1 後，下達 OPTIMIZE-1 C2 提示詞

> 本文件為 OPTIMIZE-1 C1 Run 提示詞歸檔，記錄 baron 下達 C1 執行指令（新建無損優化核心模組 + 配套測試）的完整意圖。
