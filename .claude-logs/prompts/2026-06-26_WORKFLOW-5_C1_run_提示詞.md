````markdown
# 2026-06-26 — WORKFLOW-5 C1 提示詞

> **收到時間**：2026-06-26 21:34（UTC+8）
> **任務代號**：WORKFLOW-5 C1
> **觸發 commit**：C1
> **相關產出檔案**：.claude-logs/baton/2026-06-26_WORKFLOW-5_C1_執行.md
> **觸發情境**：baron 開始執行 WORKFLOW-5，下達首個 Commit C1（SessionEnd Dry-Run·gate）執行指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-06-26 21:34 |
| 任務代號 | WORKFLOW-5 C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | .claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md |
| 觸發情境 | baron 開始執行 WORKFLOW-5，下達首個 Commit C1 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-06-26_WORKFLOW-5_C1_run_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，請執行指定的單一 Commit C1。

### 任務資訊
- 任務編碼 WORKFLOW-5 / 當前 Commit C1 / 工作流 DOC-Refactor
- Tasks：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / 本次 plan（全局策略 z·StraTA re-inject）/ 本次 tasks（§8）

### 執行命令
依 tasks §8 C1 具體實作細節進行測試與文件撰寫，守三防線：
1. 物理防線（§7 不可動：不動 Python 業務碼/前端/API）
2. 測試防線（§6.1 驗收 grep）
3. 文件防線（§1.3：commit/push 由 baron 手動，嚴禁自發）

### 備份規則
cp .claude/settings.json .claude-logs/archive/2026-06-26_WORKFLOW-5_C1_settings.json.bak
cp .claude-logs/TODO.md .claude-logs/archive/2026-06-26_WORKFLOW-5_C1_TODO.md.bak
cp .claude-logs/prompts/INDEX.md .claude-logs/archive/2026-06-26_WORKFLOW-5_C1_INDEX.md.bak

### 同步更新 TODO.md 狀態 + 歷史 Hash 自癒
1. C1 → ✅、C2 → 🟡 WIP
2. git log 掃描，把所有「待 baron 回填」佔位符替換為真實 hash

### 產出規格
- 執行報告：.claude-logs/baton/2026-06-26_WORKFLOW-5_C1_執行.md（暫存 baton/，嚴禁 git add）
- 模板：template_execution.md；含 §1-§8（§5 貼實測 SessionEnd/Stop 輸出 + git status -s；§8 baron 執行命令）

### 停止指令
產出 C1_執行.md 後立即停止。嚴禁：續跑下一 Commit / 改未列入細節的檔 / 自發 git commit|push / 把 baton/ 加入 git add。
```

---

## 執行結果摘要

- ✅/⚠️ 完成狀態：C1 執行報告產出（SessionEnd 能否 block 之裁決 + script-level 真實測試 + harness live test 移交 baron）
- pytest baseline → final：N/A（DOC-Refactor + hook script-level 測試）
- 改動檔案數：TODO.md / INDEX.md / 本歸檔檔（+ archive .bak）
- 是否 commit / push：否（依 §1.3，baron 手動）
- 關鍵裁決：SessionEnd hook **不能 block** session 終止（權威來源）→ plan §9 Q2 定案路徑 B（C5 走 Observable Fault Only）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
