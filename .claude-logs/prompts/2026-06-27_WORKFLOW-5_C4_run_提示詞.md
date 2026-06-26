````markdown
# 2026-06-27 — WORKFLOW-5 C4 提示詞

> **收到時間**：2026-06-27 01:44（UTC+8）
> **任務代號**：WORKFLOW-5 C4
> **觸發 commit**：C4
> **相關產出檔案**：.claude-logs/baton/2026-06-27_WORKFLOW-5_C4_執行.md
> **觸發情境**：baron 確認 C3 成功完成後，下達第四個 Commit C4（截斷守衛腳本）執行指令；並把 C1 實測兩修正（exit 0+JSON deny／python3 非 jq）寫進提示詞強制遵循。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-06-27 01:44 |
| 任務代號 | WORKFLOW-5 C4 |
| 觸發 Commit | C4 |
| 相關產出檔案 | .claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md |
| 觸發情境 | baron 確認 C3 成功完成後，下達第四個 Commit C4 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-06-27_WORKFLOW-5_C4_run_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，請執行指定的單一 Commit C4。

### 任務資訊
- 任務編碼 WORKFLOW-5 / 當前 Commit C4 / 工作流 DOC-Refactor
- Tasks：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md

### 🔴 C1 實測結果修正（C4 必讀且強制遵循）
1. 攔截機制：禁用 exit 2；改 exit 0 + stdout JSON
   {"hookSpecificOutput":{"permissionDecision":"deny","reason":"<拒絕理由，提示 bypass sentinel>"}}
   不 deny 則 exit 0 不輸出 JSON；所有異常/錯誤 fail-open（exit 0 無 JSON）。
2. 解析：禁用 jq（環境無），改用 python3 (3.12.3) 解析 stdin PreToolUse JSON，取 tool_name（Write/Edit）與 tool_input.file_path。

### 執行命令
依 tasks §8 C4 + 上述 C1 修正編寫腳本與測試，守三防線（§7 不可動 / §6.4 驗收 / §1.3 commit 由 baron）。

### 備份規則（新增檔不需備份）
cp .claude-logs/TODO.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C4_TODO.md.bak
cp .claude-logs/prompts/INDEX.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C4_INDEX.md.bak

### 同步更新 TODO.md 狀態 + 歷史 Hash 自癒
1. C4 → ✅、C5 → 🟡 WIP
2. git log 掃描替換「待 baron 回填」

### 產出規格
- 執行報告：.claude-logs/baton/2026-06-27_WORKFLOW-5_C4_執行.md（暫存 baton/，嚴禁 git add）
- 模板：template_execution.md；§4 述 python3 解析 stdin + >50% 且 >50 行截斷 + bypass sentinel 減速帶 + fail-open；§5 貼 bash test_hook_guards.sh truncation 真實通過 + git status -s；§8 baron 執行命令（git add -f 兩腳本）

### 停止指令
產出 C4_執行.md 後立即停止。嚴禁：續跑下一 Commit / 改未列入細節的檔 / 自發 git commit|push / 把 baton/ 暫存檔加入 git add。
```

---

## 執行結果摘要

- ✅ 完成狀態：新建 `.claude-logs/tools/pre_tool_guard.sh`（PreToolUse 截斷守衛·python3·exit 0+JSON deny·sentinel bypass·fail-open）+ `test_hook_guards.sh`（truncation 子命令 7 案例全綠）
- pytest baseline → final：N/A（hook 腳本 script-level 測試）
- 改動檔案數：新增兩腳本 + TODO.md / INDEX.md / C4 提示詞（+ 兩 .bak）
- 是否 commit / push：否（依 §1.3，baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
