`````markdown
# 2026-06-06 — RESUME-PERF-1 Check（C4 Checkout·Conformance 驗收與一次性歸檔）提示詞

> **收到時間**：2026-06-07 01:55（UTC+8）
> **任務代號**：RESUME-PERF-1 Check（C4 收官）
> **觸發 commit**：RESUME-PERF-1-Check
> **相關產出檔案**：plan_v1 / tasks / C1-C3 執行報告（baton）
> **觸發情境**：C1-C3 全 ship，baron 下達 Conformance 驗收指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-07 01:55 | 任務 RESUME-PERF-1 Check | 觸發 Commit RESUME-PERF-1-Check | 依據 plan/tasks/C1-C3 報告 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep）
寫入 prompts/2026-06-06_RESUME-PERF-1_Check_提示詞.md + 更新 INDEX。

你扮演 Claude Code，對 RESUME-PERF-1 執行 Conformance 驗收 + 收官歸檔。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / tasks / C1-C3 執行報告 / template_execution

### Conformance 三維度
- 目標規格（plan §2 U1-U7：並行化/限流統一/行為等價/保序/異常隔離/退化不變/範圍限 resume）
- 驗收條件（tasks §6 grep+pytest，含 C3 4 並行專屬測試）
- 不可動清單（tasks §7 git 證據）
+ 提示詞稽核（ls prompts | grep RESUME-PERF-1）+ msg 完整性

### 收官
1. TODO 結案：移入 ✅ 完成表（C1-C4 + hash 待回填、git log 自癒）+ 索引 ✅。
2. 產 baton/2026-06-06_RESUME-PERF-1_C4_執行.md（Conformance 報告）。
3. §8 baron 命令：一次性 mv baton（plan→plans//tasks→tasks//C1-C4 報告→executions/）+ git add + msg（/tmp/RESUME-PERF-1_C4_msg.txt）。

### 🛑 停止
產報告 + 更新 TODO 後立即停止；不自發 commit/push（mv 由 Claude、commit 由 baron）。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- Conformance 三維度全綠（U1-U7、tasks §6、不可動清單）+ SOP + 提示詞稽核 + msg 完整
- 收官：TODO 結案（C1-C4 完成表 + hash 自癒）+ baton 一次性歸檔（plan/tasks/C1-C4 → plans//tasks//executions/）
- 是否動業務代碼：否；是否 commit：否（待 baron）

## 後續引用

RESUME-PERF-1 全案結案——run_phase3 逐 section 翻譯序列→ThreadPool 受限並行（保序/限流/異常隔離/退化不並行）；效能 wall-clock 下降屬 baron E2E 觀測；plan Q5「Flip 前」由 baron 拍板提前現在做。
`````
