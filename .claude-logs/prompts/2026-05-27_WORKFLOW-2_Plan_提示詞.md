# 2026-05-27 — WORKFLOW-2 Plan 提示詞

> **收到時間**：2026-05-27 00:10
> **任務代號**：WORKFLOW-2 Plan
> **觸發 commit**：WORKFLOW-2-Plan
> **相關產出檔案**：`.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`
> **觸發情境**：baron 發現 prompts/INDEX.md 存在有索引無實體之幽靈漏洞，且前面 WORKFLOW-1 與 TODO-HOTFIX-1 系列提示詞皆未歸檔，下達 WORKFLOW-2 規劃、重構流程與歷史提示詞大一統自癒指令

---

## 完整提示詞

```
### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-05-27 00:10 |
| **任務代號** | WORKFLOW-2 Plan |
| **觸發 Commit** | WORKFLOW-2-Plan |
| **相關產出檔案** | `.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md` |
| **觸發情境** | baron 發現 prompts/INDEX.md 存在有索引無實體之幽靈漏洞，且前面 WORKFLOW-1 與 TODO-HOTFIX-1 系列提示詞皆未歸檔，下達 WORKFLOW-2 規劃、重構流程與歷史提示詞大一統自癒指令 |

---

你現在扮演 **規劃顧問**，請依以下指令，針對我們工作流流程與模板的文件治理缺陷，產出新任務的規格計畫書（WORKFLOW-2 Plan）。

### 📋 任務資訊

- **任務編碼**：WORKFLOW-2
- **任務簡述**：重構全套工作流流程模板與提示詞模板，加裝「AI 主動自愈式提示詞歸檔防線」，修補備份檔與暫存檔案的 Staging 歸檔二義性，徹底極簡化 baron 的交接命令與強制 commit message 一致性，並一舉雙向稽核、治癒與補齊前面 WORKFLOW-1 與 TODO-HOTFIX-1 流程中所有缺失的 9 份物理提示詞存檔。
- **工作流類別**：DOC-Refactor
- **套用模板**：`.claude-logs/templates/template_plan.md`
- **目標產出**：`.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`（注意：依據 SOP §3 工作目錄硬規則，階段 1 規劃書必須暫存於 baton/ 目錄下，嚴禁直接寫入 plans/）

### 📖 強制讀檔清單

CLAUDE.md、WORKFLOW_SOP.md、PROJECT_PROGRESS_CONTROL_FRAMEWORK.md（已自動載入）
.claude-logs/TODO.md
.claude-logs/prompts/README.md
.claude-logs/prompts/INDEX.md
.claude-logs/templates/template_prompt_for_plan.md
.claude-logs/templates/template_prompt_for_tasks.md
.claude-logs/templates/template_prompt_for_run.md
.claude-logs/templates/template_prompt_for_check.md
.claude-logs/templates/template_prompt_for_sop.md
.claude-logs/templates/template_execution.md
.claude-logs/templates/template_tasks.md

### 📐 規劃與撰寫規格

#### 1. 核心規格一：提示詞漏歸檔（重構五大類提示詞模板）
漏洞真因：舊模板將歸檔指令寫在提示詞本體「之外」，AI 缺乏「呼叫 write_to_file 寫檔」的當下指令，導致 AI 選擇性裝死忽略。
目標：在五大提示詞模板的對話本體最頂端（緊接元數據塊後），插入「第一步：自愈式提示詞主動歸檔與 INDEX 同步更新」標準指令區塊。AI 必須先歸檔才准進入下一步。

#### 2. 核心規格二：Check 階段的歸檔強制物理稽核
重構 template_prompt_for_check.md，Conformance 驗收新增「維度四：提示詞歸檔稽核」。
若有缺失則強制拋出例外中斷、拒絕收官，直至自癒補齊。

#### 3. 核心規格三：備份與暫存 Staging 邊界二義性
明文確立三條鐵律：
1. .bak 備份檔：Run 階段 git add 納入 commit
2. baton/ 執行報告：嚴禁 Run 階段 mv 或 git add
3. Check 階段：一次性 mv + git add 全量歸檔

#### 4. 核心規格四：Check §8 極簡化 + Commit Message 一致性
Check 報告 §8 僅保留一行：git commit -F /tmp/..._msg.txt
強制 AI 寫入 /tmp/<任務編碼>_<Commit代號>_msg.txt 並在 §8 完整展示草稿本體。

#### 5. 核心規格五：歷史提示詞雙向稽核與物理補救重建
補建 9 份缺失物理提示詞：
- WORKFLOW-1 系列（5 份）：C1/C1.5/C2+C3/C4/C5
- TODO-HOTFIX-1 系列（4 份）：Plan/Run/Tasks+Run-1b/Check
雙向對齊稽核，消除所有幽靈條目與孤兒檔案。

### 📄 產出檔案規格
路徑：`.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`
模板：template_plan.md

### 🛑 停止指令
產出 plan.md 後立即停止。嚴禁繼續拆分 commit、修改模板/SOP/INDEX.md/代碼、自發 git commit/push。
```

---

## 執行結果摘要

- ✅ 完成：產出 `baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md`
- 改動檔案：1 個（新建 plan.md）+ 1 個（本提示詞歸檔）
- 業務代碼：零改動
- commit / push：由 baron 手動執行

## 後續引用

本提示詞為 WORKFLOW-2 Plan 階段依據，後續 tasks 拆分與執行報告均引用此次規劃內容。
