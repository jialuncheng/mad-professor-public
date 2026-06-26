````markdown
# 2026-06-27 — WORKFLOW-5 C3 提示詞

> **收到時間**：2026-06-27 01:37（UTC+8）
> **任務代號**：WORKFLOW-5 C3
> **觸發 commit**：C3
> **相關產出檔案**：.claude-logs/baton/2026-06-27_WORKFLOW-5_C3_執行.md
> **觸發情境**：baron 確認 C2 成功完成後，下達第三個 Commit C3（Template Fidelity Floor）執行指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-06-27 01:37 |
| 任務代號 | WORKFLOW-5 C3 |
| 觸發 Commit | C3 |
| 相關產出檔案 | .claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md |
| 觸發情境 | baron 確認 C2 成功完成後，下達第三個 Commit C3 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-06-27_WORKFLOW-5_C3_run_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，請執行指定的單一 Commit C3。

### 任務資訊
- 任務編碼 WORKFLOW-5 / 當前 Commit C3 / 工作流 DOC-Refactor
- Tasks：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / 本次 plan（全局策略 z）/ 本次 tasks（§8）

### 執行命令
依 tasks §8 C3 具體實作細節改文件，守三防線：
1. 物理防線（§7 不可動：不動 Python 業務碼/前端/API）
2. 測試防線（§6.3 驗收 grep）
3. 文件防線（§1.3：commit/push 由 baron 手動）

### 備份規則
cp .claude-logs/templates/template_file_governance.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C3_template_file_governance.md.bak
cp .claude-logs/TODO.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C3_TODO.md.bak
cp .claude-logs/prompts/INDEX.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C3_INDEX.md.bak

### 同步更新 TODO.md 狀態 + 歷史 Hash 自癒
1. C3 → ✅、C4 → 🟡 WIP
2. git log 掃描，把所有「待 baron 回填」佔位符替換為真實 hash

### 產出規格
- 執行報告：.claude-logs/baton/2026-06-27_WORKFLOW-5_C3_執行.md（暫存 baton/，嚴禁 git add）
- 模板：template_execution.md；含 §1-§8（§4 述三維度 Scope/Provenance/Fidelity Floor 定義 + 機器可讀格式 + Cost-Aware；§5 貼 grep + git status -s；§8 baron 執行命令）

### §8 git add 清單（嚴禁包含 baton/ 暫存檔）
git add template_file_governance.md / TODO.md / C3 提示詞 / INDEX.md / 三 .bak

### 停止指令
產出 C3_執行.md 後立即停止。嚴禁：續跑下一 Commit / 改未列入細節的檔 / 自發 git commit|push / 把 baton/ 暫存檔加入 git add。
```

---

## 執行結果摘要

- ✅ 完成狀態：template_file_governance.md §99.1 新增 Scope / Provenance / Fidelity Floor 三維度 + Cost-Aware 註 + Fidelity Floor 機器可讀格式預留
- pytest baseline → final：N/A（純 DOC-Refactor）
- 改動檔案數：template_file_governance.md / TODO.md / INDEX.md / C3 提示詞（+ 三 .bak）
- 是否 commit / push：否（依 §1.3，baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
