````markdown
# 2026-06-27 — WORKFLOW-5 C6 提示詞

> **收到時間**：2026-06-27 02:09（UTC+8）
> **任務代號**：WORKFLOW-5 C6
> **觸發 commit**：C6
> **相關產出檔案**：.claude-logs/baton/2026-06-27_WORKFLOW-5_C6_執行.md
> **觸發情境**：baron 確認 C5 成功完成後，下達第六個 Commit C6（Settings 掛載與部署 SOP）執行指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-06-27 02:09 |
| 任務代號 | WORKFLOW-5 C6 |
| 觸發 Commit | C6 |
| 相關產出檔案 | .claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md |
| 觸發情境 | baron 確認 C5 成功完成後，下達第六個 Commit C6 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-06-27_WORKFLOW-5_C6_run_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，請執行指定的單一 Commit C6。

### 任務資訊
- 任務編碼 WORKFLOW-5 / 當前 Commit C6 / 工作流 DOC-Refactor
- Tasks：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / 本次 plan（全局策略 z）/ 本次 tasks（§8）

### 執行命令
依 tasks §8 C6 具體實作細節新建/改檔，守三防線（§7 不可動 / §6.6 驗收 / §1.3 commit 由 baron）。

### 備份規則（新增檔不需備份）
cp .claude-logs/baton/README.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C6_README.md.bak
cp .claude-logs/TODO.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C6_TODO.md.bak
cp .claude-logs/prompts/INDEX.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C6_INDEX.md.bak

### 同步更新 TODO.md 狀態 + 歷史 Hash 自癒
1. C6 → ✅、C7 → 🟡 WIP
2. git log 掃描替換「待 baron 回填」

### 產出規格
- 執行報告：.claude-logs/baton/2026-06-27_WORKFLOW-5_C6_執行.md（暫存 baton/，嚴禁 git add）
- 模板：template_execution.md；§4 述 settings.hooks.sample.json 掛載點 + README 專案級 settings.json 指針跨環境部署 SOP；§5 貼 grep + git status -s；§8 baron 執行命令（git add -f sample）

### 停止指令
產出 C6_執行.md 後立即停止。嚴禁：續跑下一 Commit / 改未列入細節的檔 / 自發 git commit|push / 把 baton/ 其他暫存檔加入 git add。
```

---

## 執行結果摘要

- ✅ 完成狀態：新建 `.claude-logs/tools/settings.hooks.sample.json`（PreToolUse→pre_tool_guard / SessionEnd→dirty_reset 掛載樣本）+ baton/README 追加「跨環境部署 SOP」（專案級 .claude/settings.json 指向 tools/ 版控腳本·作用域隔離·Q1 採 (a)）
- pytest baseline → final：N/A（純 DOC-Refactor + 設定樣本）
- 改動檔案數：新增 sample.json + 改 baton/README.md / TODO.md / INDEX.md / C6 提示詞（+ 三 .bak）
- 是否 commit / push：否（依 §1.3，baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
