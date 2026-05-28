# 2026-05-29 — FE-AESTHETICS Check 提示詞

> **收到時間**：2026-05-29 06:20
> **任務代號**：FE-AESTHETICS Check
> **觸發 Commit**：FE-AESTHETICS-Check
> **相關產出檔案**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_C1_執行.md`、`.claude-logs/baton/2026-05-29_FE-AESTHETICS_C2_執行.md`
> **觸發情境**：C1 與 C2 Commit 均已執行且手動 commit 完畢，baron 下達 Conformance 驗收與結案收官指令（當前 Checkout Commit 含 C1 與 C2）

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-29 06:20 |
| **任務代號** | FE-AESTHETICS Check |
| **觸發 Commit** | FE-AESTHETICS-Check |
| **相關產出檔案** | .claude-logs/baton/2026-05-29_FE-AESTHETICS_C1_執行.md<br>.claude-logs/baton/2026-05-29_FE-AESTHETICS_C2_執行.md |
| **觸發情境** | C1 與 C2 Commit 均已執行且手動 commit 完畢，baron 下達 Conformance 驗收與結案收官指令 (當前 Checkout Commit 含 C1 與 C2) |

任務編碼：FE-AESTHETICS
Plan 路徑：.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md
Tasks 路徑：.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md
執行報告清單：
  .claude-logs/baton/2026-05-29_FE-AESTHETICS_C1_執行.md
  .claude-logs/baton/2026-05-29_FE-AESTHETICS_C2_執行.md

強制讀檔清單：
CLAUDE.md / .claude-logs/ref/WORKFLOW_SOP.md / .claude-logs/TODO.md（已自動載入）
.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_plan.md
.claude-logs/baton/2026-05-29_FE-AESTHETICS_摘要工具列重構與正文扉頁美化_tasks.md
.claude-logs/baton/2026-05-29_FE-AESTHETICS_C1_執行.md
.claude-logs/baton/2026-05-29_FE-AESTHETICS_C2_執行.md

Conformance 驗收流程（五維度）：
- 維度一：plan §2 目標規格合規性
- 維度二：tasks §6 測試計畫合規性
- 維度三：tasks §7 不可動清單合規性
- 維度四：.claude-logs/prompts/ 物理目錄稽核（ls | grep FE-AESTHETICS）
- 維度五：執行報告 §8 msg.txt 草稿完整性

收官動作（全部合規後）：
1. TODO.md 更新（已完成表格 + 從進行中移除 + 索引 ✅）
2. baton/ 暫存歸檔（tasks → tasks/ + C1/C2 執行報告 → executions/）
3. 全量 Hash 自愈（git log 掃描替換 TODO.md 所有殘留「待 baron 回填」）
4. prompts/INDEX.md 確認 FE-AESTHETICS 系列完整

停止指令：完成 TODO.md 更新與 baton/ 歸檔後立即停止；嚴禁自發 git commit / push。
```

---

## 執行結果摘要

- ✅ 提示詞已歸檔

> 本文件依 `.claude-logs/prompts/README.md §3 檔案格式` 規範建立。
