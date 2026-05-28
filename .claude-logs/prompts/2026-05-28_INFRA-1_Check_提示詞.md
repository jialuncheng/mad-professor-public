# 2026-05-28 — INFRA-1 Check 提示詞

> **收到時間**：2026-05-28 10:25
> **任務代號**：INFRA-1 Check
> **觸發 Commit**：INFRA-1-Check
> **相關產出檔案**：`.claude-logs/executions/2026-05-28_INFRA-1_Check_執行.md`
> **觸發情境**：C1 與 C2 Commit 皆已由 baron 手動提交，下達最終 Conformance 驗收與收官歸檔指令

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-05-28 10:25` |
| **任務代號** | `INFRA-1 Check` |
| **觸發 Commit** | `INFRA-1-Check` |
| **相關產出檔案** | `.claude-logs/baton/2026-05-28_INFRA-1_C1_執行.md` + `.claude-logs/baton/2026-05-28_INFRA-1_C2_執行.md` |
| **觸發情境** | `C1 與 C2 Commit 皆已由 baron 手動提交，下達最終 Conformance 驗收與收官歸檔指令` |

你現在扮演 Claude Code，請對 INFRA-1 任務執行 Conformance 驗收，並在全部合規後執行收官歸檔動作。

任務編碼：INFRA-1
Plan 路徑：.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md
Tasks 路徑：.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_tasks_v1.md
執行報告清單：
  .claude-logs/baton/2026-05-28_INFRA-1_C1_執行.md
  .claude-logs/baton/2026-05-28_INFRA-1_C2_執行.md

五維度 Conformance 驗收：
1. 目標規格：backend=pipeline 鎖定、Case D test、.env.example VRAM 警告、SOP §1/§2.3/§6.2/§99.2
2. 測試計畫：4 passed + 383 passed + SOP 216 行 ≤ 250 + §0/§99 + 0 IP + §2.3 + VRAM
3. 不可動清單：pipeline_core.py / web_server.py / paper_manager.py 均未碰觸
4. 提示詞歸檔：Tasks + C1 + C2 + Check 皆歸檔 + INDEX.md 已登錄
5. msg.txt 草稿：C1/C2 §8 均含完整 git add 清單，baton/ 暫存檔剃除

全部合規後：
- TODO.md 結案（INFRA-1 ✅ 完成表格 + WIP 移除 + 索引 ✅）
- 歷史 Hash 自愈補填
- baton/ 4 份 mv 歸檔（plan → plans/ / tasks → tasks/ / C1執行 + C2執行 → executions/）
- Check 執行報告直寫 executions/
- 寫入 /tmp/INFRA-1_Check_msg.txt

嚴禁：自發 git commit/push
```

---

## 執行結果摘要

（執行完成後填入）

## 後續引用

- 本文件為 INFRA-1 Check 提示詞歸檔，記錄 baron 下達最終 Conformance 驗收與收官歸檔指令的完整意圖。

> 本文件依 `.claude-logs/prompts/README.md §3 檔案格式` 規範建立。
