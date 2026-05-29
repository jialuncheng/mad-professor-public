# 2026-05-29 — FE-AESTHETICS-HOTFIX-1 Check 提示詞

> **收到時間**：2026-05-29 18:03
> **任務代號**：FE-AESTHETICS-HOTFIX-1 Check
> **觸發 commit**：FE-AESTHETICS-HOTFIX-1-Check
> **相關產出檔案**：.claude-logs/baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_執行.md
> **觸發情境**：C2-hotfix Commit 已由 baron 手動 commit，下達 Conformance 驗收與收官歸檔指令

---

## 完整提示詞

```
### 📊 元數據審計塊
| 欄位             | 值                                                           |
| ---------------- | ------------------------------------------------------------ |
| **收到時間**     | 2026-05-29 18:03                                             |
| **任務代號**     | FE-AESTHETICS-HOTFIX-1 Check                                 |
| **觸發 Commit**  | FE-AESTHETICS-HOTFIX-1-Check                                 |
| **相關產出檔案** | .claude-logs/baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_執行.md |
| **觸發情境**     | C2-hotfix Commit已由baron手動commit，下達Conformance驗收與收官歸檔指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

你現在扮演 Claude Code，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔動作。

### 📋 任務資訊

- **任務編碼**：`FE-AESTHETICS-HOTFIX-1`
- **Plan 路徑**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md`
- **執行報告清單**：
  ```
  .claude-logs/baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_執行.md
  ```

### 📖 強制讀檔清單

CLAUDE.md / .claude-logs/ref/WORKFLOW_SOP.md / .claude-logs/TODO.md /
.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix.md /
.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md /
.claude-logs/baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_執行.md

### ✅ Conformance 驗收流程

五維度驗收：目標規格 / 驗收條件 / 不可動清單 / 提示詞歸檔稽核 / msg.txt 草稿完整性

### 🗃️ 收官自動化動作（全部合規後才執行）

1. 更新 TODO.md（新增完成表格 + 移除進行中條目 + 索引更新 + 全量 Hash 自愈）
2. 歸檔 baton/ 暫存文件至 hotfixes/ tasks/ executions/
3. 確認 baton/ 只剩 README.md
4. 更新 prompts/INDEX.md

### 🛑 停止指令

完成 TODO.md 更新與 baton/ 歸檔後必須立即停止。嚴禁自發 git commit / push。
```

---

## 執行結果摘要

- ✅ 提示詞歸檔完成
- ✅ INDEX.md 更新完成
- ✅ Conformance 五維度全通過
- ✅ Check 執行報告產出至 baton/
- ✅ baton/ 全量 mv 歸檔完成
- ✅ TODO.md 更新完成（FE-AESTHETICS HOTFIX-1 → ✅ done，歷史 hash 自愈）
- 等待 baron 手動 commit Check
