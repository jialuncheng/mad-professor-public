# WORKFLOW-2 流程模板重構與提示詞自動歸檔 — Tasks

> 本文件為 WORKFLOW-2 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md` 計畫產出，含 5 個 Commit。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 9 個 | 歷史提示詞補建：`prompts/2026-05-26_WORKFLOW-1_C1_提示詞.md`（+C1.5/C2+C3/C4/C5，共 5）+ `prompts/2026-05-26_TODO-HOTFIX-1_Plan/Run/Tasks+Run-1b/Check_提示詞.md`（共 4） |
| **修改檔案** | 9 個 | `templates/template_prompt_for_plan/tasks/run/check/sop.md`（5）+ `ref/WORKFLOW_SOP.md` + `templates/template_execution.md` + `templates/template_tasks.md` + `prompts/INDEX.md` |
| **baton 歸檔** | 2 次 | C5 收官：`baton/plan.md` → `plans/` + `baton/tasks.md` → `tasks/` |
| **狀態更新** | 1 個 | `TODO.md`（已於 Tasks 階段更新 WIP 條目） |
| **Commits** | 5 個 | C1 → C2 → C3 → C4 → C5 |

---

## §1 TL;DR（概要）

- **挑戰**：工作流模板存在五大系統性漏洞，導致 AI 可選擇性跳過提示詞歸檔（R1）、Check 無提示詞物理稽核維度（R2）、備份與暫存 Staging 邊界無明文規範（R3）、§8 格式不一致（R4）、9 份歷史提示詞形成幽靈索引（R5）。
- **解法**：5 個原子 Commit：C1 在模板本體插入強制歸檔區塊；C2 擴充 Check Conformance 維度四+五；C3 明文化備份/暫存鐵律並重構 §8；C4 補建 9 份歷史提示詞；C5 雙向對齊 INDEX.md 並收官歸檔。
- **影響範圍**：100% DOC-Refactor。零業務代碼影響，零 runtime 影響。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `templates/template_prompt_for_plan.md` | 歸檔指令外置（L85-96 bash cp）| 需在提示詞本體最頂端插入「第一步」強制歸檔區塊 |
| `templates/template_prompt_for_tasks.md` | 歸檔指令外置（L137-144 bash cp）| 同上 |
| `templates/template_prompt_for_run.md` | 歸檔指令外置（L126-135）；已有元數據塊 | 同上 |
| `templates/template_prompt_for_check.md` | 歸檔指令外置（L169-178）；Conformance 僅 3 維度 | 插入「第一步」區塊 + 新增維度四+五 |
| `templates/template_prompt_for_sop.md` | 歸檔指令外置（L107-116）| 插入「第一步」區塊 |
| `ref/WORKFLOW_SOP.md` | §3 強制規則 6 條，無備份/暫存鐵律 | 新增三段鐵律條目 |
| `templates/template_execution.md` | §8 含冗餘 mv/git add；msg.txt 用[方括號] | 新增 Check §8 極簡格式說明；規範 msg.txt 命名與草稿展示 |
| `templates/template_tasks.md` | §8 git add 清單無備份說明 | 新增 .bak 必含、baton/ 不含說明 |
| `prompts/INDEX.md` | 9 份幽靈條目（有索引無物理文件）| C5：幽靈清理 + 9 份實體鏈接 + WORKFLOW-2 條目 |
| `prompts/` 目錄 | 缺失 9 份歷史提示詞物理文件 | C4：依執行報告 §4 以摘要重建方式補建 |

---

## §3 觀察問題

### 問題 #1：提示詞歸檔指令外置，AI 不觸發
- **證據**：`grep -n "cp /dev/stdin" templates/template_prompt_for_plan.md` → 命中 L90（外置 bash cp）
- **影響**：AI 收到提示詞時這些 bash 指令已脫離 AI 執行範疇，歸檔率趨近於零

### 問題 #2：Conformance 缺提示詞物理稽核
- **證據**：`grep -n "維度四\|提示詞歸檔稽核" templates/template_prompt_for_check.md` → 0 命中
- **影響**：Check 通過不代表歸檔完整，漏歸檔永遠不會被發現

### 問題 #3：INDEX.md 幽靈條目 9 份
- **證據**：`ls prompts/ | grep "WORKFLOW-1_C"` → 0 命中；`ls prompts/ | grep "TODO-HOTFIX-1"` → 0 命中
- **影響**：INDEX.md 失去作為可信目錄的功能；歷史提示詞無法被追溯

---

## §4 設計方案

### §4.1 C1 — R1 五大提示詞模板自愈歸檔防線
在五個 `template_prompt_for_*.md` 提示詞本體最頂端（緊接元數據審計塊之後，所有其他執行指令之前），插入 plan §2.1 定義的標準「第一步：主動歸檔」強制指令區塊。原末段 `## 提示詞歸檔指令` 標題改為「備援提示詞歸檔指令（baron 手動參考）」並加說明注。

### §4.2 C2 — R2 Check Conformance 維度四+五
在 `template_prompt_for_check.md` 的 Conformance 表格中新增兩個驗收維度：
- 維度四：提示詞歸檔物理稽核（`ls prompts/ | grep 任務編碼`；缺則自癒補建）
- 維度五：commit message 草稿完整性（§8 必含 msg.txt 完整草稿展示）

### §4.3 C3 — R3+R4 SOP 備份暫存鐵律 + §8 重構
- `ref/WORKFLOW_SOP.md §3`：新增三段鐵律（.bak 必含 Run git add / baton 嚴禁 Run mv / Check 一次性收官）
- `templates/template_execution.md`：§3 備份欄位說明補充「須在本 Run git add」；§8 新增 Check 專屬格式說明 + msg.txt 草稿展示規格；佔位符 `[方括號]` → `<角括號>`
- `templates/template_tasks.md`：§8 git add 說明補「含 .bak、不含 baton/」

### §4.4 C4 — R5a 歷史 9 份提示詞物理補建
依對應執行報告 §4 修法說明，以「摘要重建」方式補建 9 份歷史提示詞 .md，統一標註「歷史補建版本，非原始逐字記錄」。

### §4.5 C5 — R5b INDEX.md 雙向對齊收官
- 刪除 INDEX.md 9 份幽靈描述塊，替換為 9 份實體 .md 文件鏈接
- 補登 WORKFLOW-2 C1~C5 執行報告鏈接（收官後補填 hash）
- `mv baton/plan.md → plans/` + `mv baton/tasks.md → tasks/`（`git add` 兩者）

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 插入第一步區塊位置錯誤（插在本體外）| 🟡 中 | C1 執行後立即 grep 驗證：`grep -n "第一步：主動歸檔" templates/template_prompt_for_*.md` 確認 5 個命中 |
| 歷史提示詞摘要重建有幻覺風險 | 🟡 中 | 嚴格依對應執行報告 §4 還原，不臆測；每份文件標明「歷史補建版本」 |
| INDEX.md 幽靈清理後殘留 | 🟢 低 | C5 完成後執行驗收 grep 確認（見 §6.5）|
| 改動 WORKFLOW_SOP.md 引入格式破壞 | 🟢 低 | 純新增條目於 §3 強制規則，不刪改既有內容 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
grep -n "第一步：主動歸檔\|🗄️" \
  .claude-logs/templates/template_prompt_for_plan.md \
  .claude-logs/templates/template_prompt_for_tasks.md \
  .claude-logs/templates/template_prompt_for_run.md \
  .claude-logs/templates/template_prompt_for_check.md \
  .claude-logs/templates/template_prompt_for_sop.md
# 期望：5 個文件各至少 1 命中
```

### §6.2 C2 驗收

```bash
grep -n "維度四\|維度五\|提示詞歸檔稽核\|草稿完整性" \
  .claude-logs/templates/template_prompt_for_check.md
# 期望：≥ 4 命中
```

### §6.3 C3 驗收

```bash
grep -n "bak 備份鐵律\|baton.*暫存鐵律\|收官歸檔鐵律" \
  .claude-logs/ref/WORKFLOW_SOP.md
# 期望：3 命中

grep -n "Co-Authored-By\|_msg.txt\|cat > /tmp" \
  .claude-logs/templates/template_execution.md
# 期望：≥ 3 命中
```

### §6.4 C4 驗收

```bash
ls .claude-logs/prompts/ | grep "WORKFLOW-1_C"
# 期望：5 命中（C1 / C1.5 / C2+C3 / C4 / C5）

ls .claude-logs/prompts/ | grep "TODO-HOTFIX-1"
# 期望：4 命中（Plan / Run / Tasks+Run-1b / Check）
```

### §6.5 C5 驗收

```bash
grep -c "WORKFLOW-1_C[0-9]" .claude-logs/prompts/INDEX.md
# 期望：≥ 5

grep -c "TODO-HOTFIX-1.*提示詞" .claude-logs/prompts/INDEX.md
# 期望：≥ 4

ls .claude-logs/plans/ | grep "WORKFLOW-2"
# 期望：1 命中（plan.md）

ls .claude-logs/tasks/ | grep "WORKFLOW-2"
# 期望：1 命中（tasks.md）
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **業務代碼**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*` — 100% 不動
- [ ] **主 repo 目錄**（worktree 父目錄）— 嚴禁讀寫
- [ ] **`CLAUDE.md`** §1–§5 既有規範條款 — 不得刪改（本次只補強模板層）
- [ ] **`ref/WORKFLOW_SOP.md`** §1–§6 既有條款 — 僅在 §3 強制規則段**新增**三條鐵律，不得刪改既有條目
- [ ] **`templates/template_plan.md`** — 不在本次改版範圍
- [ ] **`.claude-logs/prompts/` 既有 28 個 .md 文件** — 歷史提示詞只新增，不改動既有文件

---

## §8 推薦 Commit 拆分

### C1 — R1 五大提示詞模板自愈歸檔防線

| 維度 | 內容 |
|---|---|
| **影響範圍** | `templates/template_prompt_for_plan.md`、`templates/template_prompt_for_tasks.md`、`templates/template_prompt_for_run.md`、`templates/template_prompt_for_check.md`、`templates/template_prompt_for_sop.md`（5 個模板）+ 5 份 .bak 備份到 `archive/` |
| **安全性** | 🟢 高 — 純文件改動，零 runtime 影響；範本模板不影響既有 session |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；archive/ .bak 備份亦可手動還原 |
| **驗收 grep 條件** | 見 §6.1：5 個文件各命中「第一步：主動歸檔」≥ 1 次 |
| **依賴關係** | 無（可獨立執行） |
| **具體實作細節** | 1. 備份 5 個文件：`cp templates/template_prompt_for_plan.md archive/2026-05-27_template_prompt_for_plan.md.bak`（其餘 4 個同樣備份）。2. 對每個模板，讀檔後找到提示詞本體區塊中的元數據審計塊（`\| 欄位 \| 值 \|` 表格）末行之後、第一個正文執行指令之前的位置，插入以下標準「第一步」區塊（exact 格式見 plan §2.1 verbatim 引用）：`---\n\n## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）\n\n**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**\n\n1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：\n   `.claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_<階段>_提示詞.md`\n   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。\n\n2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。\n\n3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`<檔案路徑>`」，然後繼續執行後續步驟。\n\n---`. 3. 找到末段 `## 提示詞歸檔指令` 標題行，改為 `## 備援提示詞歸檔指令（baron 手動參考）`，並在表格或說明前插入一行說明：`> ℹ️ AI 主動歸檔已由上方「第一步」區塊處理。以下 bash 指令僅供 baron 手動備援用。`. 4. `git add` 5 個模板 + 5 份 .bak 備份（共 10 個文件）。 |

---

### C2 — R2 Check 模板 Conformance 維度四+五

| 維度 | 內容 |
|---|---|
| **影響範圍** | `templates/template_prompt_for_check.md`（1 個模板）+ 1 份 .bak 備份到 `archive/` |
| **安全性** | 🟢 高 — 純文件改動；只新增維度，不改動現有三維度內容 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾 |
| **驗收 grep 條件** | 見 §6.2：命中「維度四」「維度五」「提示詞歸檔稽核」「草稿完整性」各 ≥ 1 次 |
| **依賴關係** | 無（可與 C1 並行；建議 C1 完成後順序執行） |
| **具體實作細節** | 1. 備份：`cp templates/template_prompt_for_check.md archive/2026-05-27_template_prompt_for_check.md.bak`. 2. 在 Conformance 驗收表格（現有三維度）末行之後，追加兩個新維度行：第一行（維度四）：`\| **提示詞歸檔** \| \`.claude-logs/prompts/\` 物理目錄 \| 執行 \`ls .claude-logs/prompts/ \| grep "<任務編碼>"\`，確認 plan / tasks / run(s) / check 各階段 .md 實體存在；若缺失則立即補建自癒後繼續 \|`；第二行（維度五）：`\| **msg.txt 草稿完整性** \| 本任務各執行報告 §8 \| 確認每份執行報告 §8 含完整 msg.txt 草稿展示（含 \`cat > /tmp/...\` 寫入指令 + 草稿全文）；缺失則列出清單要求補完 \|`. 3. 在 `## ✅ Conformance 驗收流程` 說明段落（表格之後）追加例外處理說明：「**若維度四缺失**：Claude Code 必須立即補建缺失提示詞 .md，補完後繼續收官；**若維度五不合規**：列出缺失 §8 msg.txt 展示的執行報告，要求 baron 確認後收官。」4. `git add` 1 個模板 + 1 份 .bak。 |

---

### C3 — R3+R4 SOP 備份暫存鐵律 + §8 重構

| 維度 | 內容 |
|---|---|
| **影響範圍** | `ref/WORKFLOW_SOP.md`、`templates/template_execution.md`、`templates/template_tasks.md`（3 個文件）+ 3 份 .bak 備份 |
| **安全性** | 🟢 高 — 純文件改動；WORKFLOW_SOP.md 只在 §3 強制規則段新增，不刪改既有 6 條 |
| **可逆性** | 🟢 高 — `git revert C3` 完全回滾 |
| **驗收 grep 條件** | 見 §6.3：SOP 命中 3 條鐵律；execution 模板命中 msg.txt + Co-Authored-By |
| **依賴關係** | 無（可獨立執行） |
| **具體實作細節** | 1. 備份 3 個文件各自到 `archive/`。2. **WORKFLOW_SOP.md §3 強制規則**：在現有最後一條強制規則（`- 階段 2 同步更新 TODO.md…`）之後，追加三條新鐵律：`- .bak 備份鐵律：修改既有檔案前產出的 .bak 備份，**必須在對應 Run 階段的 \`git add\` 清單中強制包含**（審計存檔，便於 git show 追溯）`；`- baton/ 暫存鐵律：Run 階段產出的執行報告與 plan，**嚴禁在 Run 階段 \`mv\` 移動或 \`git add\`**，必須原封不動留在 baton/ 暫存`；`- 收官歸檔鐵律：baton/ 下所有暫存文件，**必須且僅能在最後 Check 階段一次性 \`mv\` + \`git add\` 歸檔至正式目錄**`. 同步在 §99.2 加 Revision：`- v3 (2026-05-27)：WORKFLOW-2 C3——§3 強制規則新增三段備份/暫存/收官鐵律（R3）`. 3. **template_execution.md §3 備份路徑欄位**：在備份路徑欄位說明行末追加備注：`（此備份檔**必須**在本 Run Commit 的 \`git add\` 清單中包含，勿省略）`. **template_execution.md §8**：(a) 將所有 `[任務編碼]` 佔位符改為 `<任務編碼>`，`[Commit代號]` 改為 `<Commit代號>`（全文替換）；(b) 在 `## §8 baron 執行命令` 標題下，現有內容之前插入 Check 專屬格式說明框：`> ℹ️ **Check 執行報告的 §8 僅保留以下一行 commit 指令**；所有 mv + git add 已在本報告 §4 完成（見變動檔案清單）。`；(c) 在末段追加 §8.2 子節：`### §8.2 commit message 草稿\n（草稿已寫入 /tmp/<任務編碼>_<Commit代號>_msg.txt，以下為完整展示）\n```\n<工作流類別>: <任務編碼> <Commit代號> — <Commit名稱>\n\n<3-5 行改動摘要>\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>\n````. 4. **template_tasks.md §8** `影響範圍` 維度說明末追加：`（包含：業務/文件檔案 + 對應 \`.bak\` 備份；\`baton/\` 暫存報告**嚴禁**在此列入，待 Check 收官一次性歸檔）`. 5. `git add` 3 個文件 + 3 份 .bak 備份（共 6 個文件）。 |

---

### C4 — R5a 歷史 9 份提示詞物理補建

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 9 個 .md 文件至 `.claude-logs/prompts/`（全部為新增，零既有文件改動） |
| **安全性** | 🟢 高 — 純新建文件；不影響任何既有文件 |
| **可逆性** | 🟢 高 — `git revert C4` 刪除 9 個新建文件；無副作用 |
| **驗收 grep 條件** | 見 §6.4：`ls prompts/ \| grep "WORKFLOW-1_C"` ≥ 5 命中；`grep "TODO-HOTFIX-1"` ≥ 4 命中 |
| **依賴關係** | C5 依賴 C4 完成（9 份文件必須先存在才能在 INDEX 建實體鏈接） |
| **具體實作細節** | 依序補建 9 份文件（格式：標準 metadata 塊 + 完整提示詞正文（依對應執行報告 §4 摘要重建）+ 執行結果摘要 + 歷史補建聲明）。每份文件末尾標準聲明：`> 本文件為歷史補建版本，非原始逐字記錄。依對應執行報告 §4 修法說明以摘要方式還原（WORKFLOW-2 R5 補建）。` 補建清單及依據來源：(1) `prompts/2026-05-26_WORKFLOW-1_C1_提示詞.md` ← `executions/2026-05-26_WORKFLOW-1_C1_執行.md §4`；(2) `prompts/2026-05-26_WORKFLOW-1_C1.5_提示詞.md` ← `executions/2026-05-26_WORKFLOW-1_C1.5_執行.md §4`；(3) `prompts/2026-05-26_WORKFLOW-1_C2+C3_提示詞.md` ← `executions/2026-05-26_WORKFLOW-1_C2+C3_執行.md §4`；(4) `prompts/2026-05-26_WORKFLOW-1_C4_提示詞.md` ← `executions/2026-05-26_WORKFLOW-1_C4_執行.md §4`；(5) `prompts/2026-05-26_WORKFLOW-1_C5_提示詞.md` ← `executions/2026-05-26_WORKFLOW-1_C5_執行.md §4`；(6) `prompts/2026-05-26_TODO-HOTFIX-1_Plan_提示詞.md` ← `hotfixes/2026-05-26_TODO-HOTFIX-1_hotfix.md §4`；(7) `prompts/2026-05-26_TODO-HOTFIX-1_Run_提示詞.md` ← `executions/2026-05-26_TODO-HOTFIX-1_執行.md §4`；(8) `prompts/2026-05-26_TODO-HOTFIX-1_Tasks+Run-1b_提示詞.md` ← `executions/2026-05-26_TODO-HOTFIX-1b_執行.md §4`；(9) `prompts/2026-05-26_TODO-HOTFIX-1_Check_提示詞.md` ← `executions/2026-05-26_TODO-HOTFIX-1_Check_執行.md §4`。`git add` 9 個新文件。 |

---

### C5 — R5b INDEX.md 雙向對齊 + 收官歸檔

| 維度 | 內容 |
|---|---|
| **影響範圍** | `prompts/INDEX.md`（1 個文件，1 份 .bak 備份）+ `baton/plan.md` → `plans/` mv；`baton/tasks.md` → `tasks/` mv（2 個 baton 暫存歸檔） |
| **安全性** | 🟢 高 — INDEX.md 僅做幽靈清理 + 補登；baton mv 為標準收官操作 |
| **可逆性** | 🟢 高 — `git revert C5` 完全回滾 INDEX.md 改動；mv 文件可用 git show 追溯 |
| **驗收 grep 條件** | 見 §6.5：INDEX.md 命中 WORKFLOW-1_C[0-9] ≥ 5 次；TODO-HOTFIX-1 提示詞 ≥ 4 次；plans/ + tasks/ 各 1 個 WORKFLOW-2 文件 |
| **依賴關係** | 依賴 C4 完成（9 份物理文件必須先存在才能建實體鏈接） |
| **具體實作細節** | 1. 備份：`cp prompts/INDEX.md archive/2026-05-27_prompts_INDEX.md.bak`. 2. **幽靈清理**：刪除 INDEX.md WORKFLOW 系列中 WORKFLOW-1 C1~C5 文字描述塊（`✅ **WORKFLOW-1 C1~C5 落地全鏈路…` + C1/C1.5/C2+C3/C4/C5 五行子 bullet），替換為 5 個 .md 文件鏈接：`- \`2026-05-26_WORKFLOW-1_C1_提示詞.md\` — WORKFLOW-1 C1 Bootstrap Core…`（依此類推 C1.5/C2+C3/C4/C5）；刪除 TODO-HOTFIX-1 文字描述塊（Plan/Run/Tasks+Run-1b/Check 四行），替換為 4 個 .md 文件鏈接。3. **依時間排序更新**：L61-65 的文字描述條目替換為對應 9 個 .md 文件鏈接條目（每行格式 `- 2026-05-26 — \`2026-05-26_WORKFLOW-1_C1_提示詞.md\``）；新增後超過 15 筆者依規則刪除最舊條目至保持 15 筆。4. **WORKFLOW-2 完整登記**：在 WORKFLOW 系列補登 WORKFLOW-2 C1~C5 執行報告條目（hash 在 baron commit 後回填）。5. 更新 INDEX.md 頂部「最後更新」行為 `最後更新：2026-05-27（WORKFLOW-2 全案收官）`. 6. **baton 歸檔**：`mv .claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_plan.md .claude-logs/plans/`；`mv .claude-logs/baton/2026-05-26_WORKFLOW-2_流程模板重構與提示詞自動歸檔_tasks.md .claude-logs/tasks/`（兩個 mv 命令均用 system mv，不用 git mv）. 7. `git add` INDEX.md + INDEX.md.bak + plans/plan.md + tasks/tasks.md（共 4 個文件）。 |

---

## §9 Open Questions

無。（R1~R5 所有規劃層面 Open Questions 已在 plan §7 結案：Q1 採摘要重建、Q3 採獨立維度五。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-2 任務的 5 個原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 WORKFLOW-2 executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 暫存於 baton/；C5 收官時 mv → tasks/。嚴禁改動業務代碼；嚴禁 git commit / git push |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複計畫書中的設計脈絡 |

### §99.2 Revision 歷程

- v1 (2026-05-27)：初版（WORKFLOW-2 Tasks，5 Commit C1~C5 六維度完整拆分）
