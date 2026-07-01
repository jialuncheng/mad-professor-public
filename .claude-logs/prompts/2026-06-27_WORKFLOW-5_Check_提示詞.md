````markdown
# 2026-06-27 — WORKFLOW-5 Check 提示詞

> **收到時間**：2026-06-27 02:11（UTC+8）
> **任務代號**：WORKFLOW-5 Check
> **觸發 commit**：WORKFLOW-5-Check（C7 Checkout）
> **相關產出檔案**：.claude-logs/baton/2026-06-27_WORKFLOW-5_C7_執行.md + baton 一次性歸檔
> **觸發情境**：C1–C6 全部完成，baron 下達 Conformance 驗收與 C7 收官歸檔指令。

---

## 完整提示詞

```
### 📊 元數據審計塊
| 收到時間 | 2026-06-27 02:11 |
| 任務代號 | WORKFLOW-5 Check |
| 觸發 Commit | WORKFLOW-5-Check |
| 相關產出檔案 | C1–C6 執行報告 + 即將產出 C7 |
| 觸發情境 | C1–C6 已完成，baron 下達 Conformance 驗收與 C7 收官歸檔指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 .claude-logs/prompts/2026-06-27_WORKFLOW-5_Check_提示詞.md（格式依 README §3）
2. 更新 INDEX.md（分類 + 依時間排序首行，超 15 刪最舊）
3. 回覆「✅ 提示詞已歸檔：...」後繼續

你現在扮演 Claude Code，對 WORKFLOW-5 執行 Conformance 驗收，全部合規後收官歸檔。

### 任務資訊
- 任務編碼 WORKFLOW-5；plan / tasks / C1–C6 執行報告（baton）。

### Conformance 五維度（產 C7 執行報告比對）
1. 目標規格 plan §2（C1–C6 100% 實現）
2. 測試計畫 tasks §6（§6.1–§6.6 全綠）
3. 不可動清單 tasks §7（全 ✅ 未觸碰、無業務碼）
4. 提示詞歸檔入 Git 稽核（ls + git ls-files prompts/，漏則 git add）
5. msg.txt 草稿完整性（C1–C6 §8）
6. §7.2 跨 Phase 整合測試——純治理 + hook、無 handoff → 顯式豁免

### 收官動作（全綠後）
1. TODO：移出 active、寫入 ✅ 完成表（C1–C7 待 baron 回填）、索引改 ✅、全量 hash 自癒
2. baton 一次性 mv + git add：plan→plans/、tasks→tasks/、C1–C7 報告→executions/
3. ls baton 確認僅剩 README.md

### 停止指令
完成 TODO 更新與 baton 歸檔後停止。嚴禁自發 git commit|push、嚴禁改已歸檔報告。

### §8 baron 執行命令
git add TODO.md / Check 提示詞 / INDEX.md；commit msg 草稿 /tmp/WORKFLOW-5_C7_msg.txt；baron 手動 git commit。
```

---

## 執行結果摘要

- ✅ 完成狀態：C7 Conformance 五維度全綠 + §7.2 純治理豁免 + baton 一次性歸檔（plan/tasks/C1–C7 報告）+ TODO 結案 + hash 自癒
- pytest baseline → final：N/A（DOC-Refactor + hook script-level；test_hook_guards all = truncation 8 + dirty_reset 4 全綠）
- 改動檔案數：TODO.md / INDEX.md / Check 提示詞 + baton 11 檔歸檔（plan/tasks/C1–C7 報告）
- 是否 commit / push：否（依 §1.3，baron 手動）

## 後續引用

WORKFLOW-5 全案結案。
````
