# 2026-05-27 — OPTIMIZE-1 Tasks v2 提示詞

> **收到時間**：2026-05-27 10:18
> **任務代號**：OPTIMIZE-1 Tasks v2
> **觸發 Commit**：OPTIMIZE-1-Tasks-v2
> **相關產出檔案**：`.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md`
> **觸發情境**：baron 同意 OPTIMIZE-1 v2 plan 規格，下達任務拆分更新指令

---

## 完整提示詞

```
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | `2026-05-27 10:18`                                           |
| **任務代號**     | `OPTIMIZE-1 Tasks v2`                                        |
| **觸發 Commit**  | `OPTIMIZE-1-Tasks-v2`                                        |
| **相關產出檔案** | `.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md` |
| **觸發情境**     | `baron 同意 OPTIMIZE-1 v2 plan 規格，下達任務拆分更新指令`   |

你現在扮演 Claude Code，請依以下指令將 v2 plan 重新拆分為可執行的 Commit 清單，並覆寫更新現有的 tasks 檔案。

任務編碼：OPTIMIZE-1
工作流類別：BE-Refactor
Plan 路徑：.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md

強制讀檔清單：
- CLAUDE.md（核心規範與契約）
- .claude-logs/ref/WORKFLOW_SOP.md（工作流規範）
- .claude-logs/TODO.md（任務狀態真理源）
- .claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md（本次拆分的依據 v2 plan）
- .claude-logs/templates/template_tasks.md（tasks 模板）
- .claude-logs/sop/2026-05-23_logging_SOP_手冊.md（規章：日誌編寫標準作業手冊）

Commit 拆分（2 個）：
- C1 — Implement Core Optimization Module with Atomic Overwrite（實作無損優化核心與單元測試）
- C2 — Integrate 1-Step Upload in Web Server & Frontend（整合一字步上傳端點與前台 UI）

§0.5 成果盤點必置文件開頭。
§1 TL;DR 中文括號命名。
§8 六維度 Commit 拆分表格（每個 Commit 必填，具體實作細節必須嚴格遵守 logging/database SOP）。

TODO.md：OPTIMIZE-1 → 🟡 WIP v2，含 C1/C2 子任務。
§99.2 加 v2 Revision 記錄。

產出路徑（不要改檔名）：.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md
嚴禁：繼續產出 _執行.md / 動任何業務代碼 / 自發 git commit/push
```

---

## 執行結果摘要

（待執行後填入）

## 後續引用

- 下一步：baron 下達 OPTIMIZE-1 C1 提示詞（Run 階段）

> 本文件為 OPTIMIZE-1 Tasks v2 提示詞歸檔，記錄 baron 下達 v2 任務拆分更新指令的完整意圖。
