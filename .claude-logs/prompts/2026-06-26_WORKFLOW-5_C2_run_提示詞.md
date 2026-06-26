````markdown
# 2026-06-26 — WORKFLOW-5 C2 提示詞

> **收到時間**：2026-06-26 22:31（UTC+8）
> **任務代號**：WORKFLOW-5 C2
> **觸發 commit**：C2
> **相關產出檔案**：.claude-logs/baton/2026-06-26_WORKFLOW-5_C2_執行.md
> **觸發情境**：baron 確認 C1 成功完成後，下達第二個 Commit C2（Baton 3-Phase 形式化）執行指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-06-26 22:31 |
| 任務代號 | WORKFLOW-5 C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | .claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md |
| 觸發情境 | baron 確認 C1 成功完成後，下達第二個 Commit C2 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-06-26_WORKFLOW-5_C2_run_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，請執行指定的單一 Commit C2。

### 任務資訊
- 任務編碼 WORKFLOW-5 / 當前 Commit C2 / 工作流 DOC-Refactor
- Tasks：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / 本次 plan（全局策略 z）/ 本次 tasks（§8）

### 執行命令
依 tasks §8 C2 具體實作細節改文件與檢索，守三防線：
1. 物理防線（§7 不可動：不動 Python 業務碼/前端/API，不改 WORKFLOW_SOP 核心流程定義）
2. 測試防線（§6.2 驗收 grep）
3. 文件防線（§1.3：commit/push 由 baron 手動）

### 備份規則
cp .claude-logs/baton/README.md .claude-logs/archive/2026-06-26_WORKFLOW-5_C2_README.md.bak
cp .claude-logs/TODO.md .claude-logs/archive/2026-06-26_WORKFLOW-5_C2_TODO.md.bak
cp .claude-logs/prompts/INDEX.md .claude-logs/archive/2026-06-26_WORKFLOW-5_C2_INDEX.md.bak

### 同步更新 TODO.md 狀態 + 歷史 Hash 自癒
1. C2 → ✅、C3 → 🟡 WIP
2. git log 掃描，把所有「待 baron 回填」佔位符替換為真實 hash

### 產出規格
- 執行報告：.claude-logs/baton/2026-06-26_WORKFLOW-5_C2_執行.md（暫存 baton/，嚴禁 git add）
- 模板：template_execution.md；含 §1-§8（§4 述 Staging→Validation→Scoped Commit 設計；§5 貼 grep + git status -s；§8 baron 執行命令）

### §8 git add 清單（除 README.md 外嚴禁包含 baton/ 其他暫存檔）
git add .claude-logs/baton/README.md / TODO.md / C2 提示詞 / INDEX.md / 三 .bak

### 停止指令
產出 C2_執行.md 後立即停止。嚴禁：續跑下一 Commit / 改未列入細節的檔 / 自發 git commit|push / 把 baton/ 其他暫存檔加入 git add。
```

---

## 執行結果摘要

- ✅ 完成狀態：baton/README.md §2 改寫為 3-Phase（Staging→Deterministic Validation→Scoped Commit）+ 對齊 WORKFLOW_SOP §3 一次性 mv 鐵律
- pytest baseline → final：N/A（純 DOC-Refactor）
- 改動檔案數：baton/README.md（tracked 例外）/ TODO.md / INDEX.md / C2 提示詞（+ 三 .bak）
- 是否 commit / push：否（依 §1.3，baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
