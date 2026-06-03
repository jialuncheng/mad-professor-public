# 2026-05-28 — INFRA-1 Tasks v1 提示詞

> **收到時間**：2026-05-28 04:35
> **任務代號**：INFRA-1 Tasks
> **觸發 Commit**：INFRA-1-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_tasks_v1.md`
> **觸發情境**：baron 同意 plan 規格，下達任務拆分與 TODO.md WIP 更新指令

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-05-28 04:35` |
| **任務代號** | `INFRA-1 Tasks` |
| **觸發 Commit** | `INFRA-1-Tasks` |
| **相關產出檔案** | `.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_tasks_v1.md` |
| **觸發情境** | `baron 同意 plan 規格，下達任務拆分與 TODO.md WIP 更新指令` |

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

任務編碼：INFRA-1
工作流類別：BE-Refactor
Plan 路徑：.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md

強制讀檔清單：
- CLAUDE.md（已自動載入）
- .claude-logs/ref/WORKFLOW_SOP.md（已自動載入）
- .claude-logs/TODO.md（已自動載入）
- .claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md
- .claude-logs/templates/template_tasks.md

Commit 拆分：3 段（C1 BE-Refactor + C2 DOC-Refactor + Check）
- C1：pdf_processor backend 鎖定與單元測試（請求參數錨定與斷言測試）
- C2：SOP 手冊 CPU 推理與環境規格更新（SOP 文件運維規格補強）
- Check：TODO.md 結案與全量 baton 歸檔（收官結案與物理歸檔）

產出：.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_tasks_v1.md
同步更新 TODO.md（🟡 WIP 條目寫入 🔴 高優先最前方）

嚴禁：執行代碼 / 搬移 plan.md / git commit/push
```

---

## 執行結果摘要

（tasks_v1.md 產出後填入）

## 後續引用

- 下一步：baron 確認 tasks 後，下達 INFRA-1 C1 執行提示詞

> 本文件為 INFRA-1 Tasks v1 提示詞歸檔，記錄 baron 下達任務拆分指令（3 commits：C1 backend 鎖定 + C2 SOP 更新 + Check 收官）的完整意圖。
