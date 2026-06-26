````markdown
# 2026-06-27 — WORKFLOW-5 C5 提示詞

> **收到時間**：2026-06-27 01:57（UTC+8）
> **任務代號**：WORKFLOW-5 C5
> **觸發 commit**：C5
> **相關產出檔案**：.claude-logs/baton/2026-06-27_WORKFLOW-5_C5_執行.md
> **觸發情境**：baron 確認 C4 成功完成後，下達第五個 Commit C5（DIRTY-RESET 守衛腳本）執行指令；附 C1 修正（Observable Fault／exit 0+JSON／python3 非 jq）。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-06-27 01:57 |
| 任務代號 | WORKFLOW-5 C5 |
| 觸發 Commit | C5 |
| 相關產出檔案 | .claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md |
| 觸發情境 | baron 確認 C4 成功完成後，下達第五個 Commit C5 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-06-27_WORKFLOW-5_C5_run_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，請執行指定的單一 Commit C5。

### 任務資訊
- 任務編碼 WORKFLOW-5 / 當前 Commit C5 / 工作流 DOC-Refactor
- Tasks：.claude-logs/baton/2026-06-26_WORKFLOW-5_ClawVM混合治理Hook落地_tasks.md

### 🔴 C1 實測與環境修正（C5 必讀且強制遵循）
1. 阻擋/攔截機制：
   - 路徑 A（Stop 攔截）：exit 0 + stdout {"decision":"block","reason":"..."}
   - 路徑 B（Observable Fault·首版，依 C1+baron 建議）：偵測違規僅 stdout/日誌警告 + exit 0，不輸出 block JSON。
2. 解析：禁用 jq（環境無），改用 python3 解析 stdin JSON 或 TODO.md/baton 對帳。

### 執行命令
依 tasks §8 C5 + 上述 C1 修正編寫腳本與測試，守三防線（§7 不可動 / §6.5 驗收 / §1.3 commit 由 baron）。

### 備份規則
cp .claude-logs/tools/test_hook_guards.sh .claude-logs/archive/2026-06-27_WORKFLOW-5_C5_test_hook_guards.sh.bak
cp .claude-logs/TODO.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C5_TODO.md.bak
cp .claude-logs/prompts/INDEX.md .claude-logs/archive/2026-06-27_WORKFLOW-5_C5_INDEX.md.bak

### 同步更新 TODO.md 狀態 + 歷史 Hash 自癒
1. C5 → ✅、C6 → 🟡 WIP
2. git log 掃描替換「待 baron 回填」

### 產出規格
- 執行報告：.claude-logs/baton/2026-06-27_WORKFLOW-5_C5_執行.md（暫存 baton/，嚴禁 git add）
- 模板：template_execution.md；§4 述 dirty_reset_guard.sh 解析 TODO「Checkout ✅ 且未歸檔」觸發條件 + Observable Fault 警告邏輯；§5 貼 bash test_hook_guards.sh dirty_reset 真實通過 + git status -s；§8 baron 執行命令（git add -f）

### 停止指令
產出 C5_執行.md 後立即停止。嚴禁：續跑下一 Commit / 改未列入細節的檔 / 自發 git commit|push / 把 baton/ 暫存檔加入 git add。
```

---

## 執行結果摘要

- ✅ 完成狀態：新建 `.claude-logs/tools/dirty_reset_guard.sh`（SessionEnd·Observable Fault Only·python3·觸發＝TODO Checkout ✅ 但 baton 未歸檔）+ test_hook_guards.sh 補 dirty_reset 案例
- pytest baseline → final：N/A（hook 腳本 script-level 測試）
- 改動檔案數：新增 dirty_reset_guard.sh + 改 test_hook_guards.sh / TODO.md / INDEX.md / C5 提示詞（+ 三 .bak）
- 是否 commit / push：否（依 §1.3，baron 手動）

## 後續引用

如本提示詞被其他 session 改寫 / 引用、在此處記錄連結。
````
