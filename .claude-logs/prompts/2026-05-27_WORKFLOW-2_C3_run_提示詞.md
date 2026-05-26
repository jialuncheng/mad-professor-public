# 2026-05-27 — WORKFLOW-2 C3 提示詞

> **收到時間**：2026-05-27 04:20
> **任務代號**：WORKFLOW-2 C3
> **觸發 commit**：C3
> **相關產出檔案**：`.claude-logs/baton/2026-05-27_WORKFLOW-2_C3_執行.md`
> **觸發情境**：baron 審查 C2 執行報告無誤並已手動 Commit（TODO 中歷史 Hash 已完美回填），下達 C3 SOP 鐵律、重構模板 §8 暨物理自癒防線落地指令

---

## 完整提示詞

```
### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-27 04:20 |
| **任務代號** | WORKFLOW-2 C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | .claude-logs/baton/2026-05-27_WORKFLOW-2_C3_執行.md |
| **觸發情境** | baron 審查 C2 執行報告無誤並已手動 Commit（TODO 中歷史 Hash 已完美回填），下達 C3 SOP 鐵律、重構模板 §8 暨物理自癒防線落地指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

[歸檔指令 — 已執行]

---

你現在扮演 Claude Code，請執行 C3 — R3+R4 SOP 備份暫存鐵律 + §8 重構。

任務編碼：WORKFLOW-2 / Commit C3 / DOC-Refactor
Tasks 路徑：.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md

C3 實作細節：

0. 備份 5 個檔案至 archive/：
   - ref/WORKFLOW_SOP.md → archive/2026-05-27_WORKFLOW-2_C3_WORKFLOW_SOP.md.bak
   - templates/template_execution.md → archive/2026-05-27_WORKFLOW-2_C3_template_execution.md.bak
   - templates/template_tasks.md → archive/2026-05-27_WORKFLOW-2_C3_template_tasks.md.bak
   - templates/template_prompt_for_run.md → archive/2026-05-27_WORKFLOW-2_C3_template_prompt_for_run.md.bak
   - templates/template_prompt_for_check.md → archive/2026-05-27_WORKFLOW-2_C3_template_prompt_for_check.md.bak

1. ref/WORKFLOW_SOP.md §3 強制規則新增三段鐵律：
   - .bak 備份鐵律：修改既有檔案前的 .bak 備份必須在對應 Run 階段的 git add 清單中強制包含
   - baton/ 暫存鐵律：Run 階段產出的執行報告與 plan 嚴禁在 Run 階段 mv 移動或 git add
   - 收官歸檔鐵律：baton/ 下所有暫存文件必須且僅能在最後 Check 階段一次性 mv + git add 歸檔
   - §99.2 新增 v3 Revision 紀錄

2. templates/template_execution.md §3 + §8 重構：
   - §3 備份欄位末追加：（此備份檔必須在本 Run Commit 的 git add 清單中包含，勿省略）
   - §8 將 [任務編碼]/[Commit代號] 方括號佔位符改為 <尖括號> 格式
   - §8 Check 專屬格式說明（ℹ️ 提示）
   - §8.2 commit message 草稿子節追加

3. templates/template_tasks.md §8 影響範圍欄位末追加：
   （包含：業務/文件檔案 + 對應 .bak 備份；baton/ 暫存報告嚴禁在此列入，待 Check 收官一次性歸檔）

4. templates/template_prompt_for_run.md 在 💾 備份規則 後插入：
   🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）區塊

5. templates/template_prompt_for_check.md 在收官自動化動作第一步下追加：
   歷史全量 Hash 審計與自愈補填說明；確認並保留第二步歸檔流程

停止指令：C3_執行.md + TODO.md 更新後即停，嚴禁繼續 C4，嚴禁 git commit/push。
```

---

## 執行結果摘要

- ✅ 第一步歸檔完成：本檔案
- ✅ 5 個檔案備份至 archive/（.bak）
- ✅ WORKFLOW_SOP.md §3 三段鐵律追加 + §99.2 v3 Revision
- ✅ template_execution.md §3 備份備注 + §8 佔位符改尖括號 + Check ℹ️ + §8.2 草稿子節
- ✅ template_tasks.md §8 影響範圍備注追加
- ✅ template_prompt_for_run.md 🔄 TODO 自癒防線區塊插入
- ✅ template_prompt_for_check.md Hash 審計說明 + 歸檔流程確認
- ✅ TODO.md：C3 ✅ / C4 🟡 WIP
- ✅ C3 執行報告：`baton/2026-05-27_WORKFLOW-2_C3_執行.md`

## 後續引用

- C4 Run 提示詞（待建）：`.claude-logs/prompts/2026-05-27_WORKFLOW-2_C4_run_提示詞.md`
