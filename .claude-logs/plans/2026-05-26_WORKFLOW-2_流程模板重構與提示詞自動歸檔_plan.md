# WORKFLOW-2 流程模板重構與提示詞自動歸檔 plan

> 修補工作流文件治理五大漏洞：提示詞漏歸檔、Check 稽核維度缺失、Staging 邊界二義性、§8 格式不一致、歷史幽靈索引自癒。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：工作流模板存在五大系統性漏洞：（1）五大提示詞模板的歸檔指令寫在 AI 看不到的「本體外」，導致 AI 跳過歸檔；（2）Check Conformance 缺少提示詞實體稽核維度；（3）備份檔（`.bak`）與暫存報告（`baton/`）的 Staging 生命週期無明文規範；（4）`§8 baron 執行命令` 在 Check 階段仍含冗餘 `mv`/`git add`，且 commit message 草稿未標準化；（5）`prompts/INDEX.md` 中有 9 份幽靈條目（有索引無實體），WORKFLOW-1 C1~C5 與 TODO-HOTFIX-1 全系列提示詞從未物理建立。
- **解法**：五路並進：R1 在模板本體頂端插入強制自愈歸檔區塊；R2 在 Check 模板新增「維度四」提示詞物理稽核；R3 在 WORKFLOW_SOP.md 與執行/tasks 模板明文化備份/暫存/收官三段生命週期鐵律；R4 極簡化 Check 報告 §8 為單行 commit 並加固 msg.txt 命名與草稿展示規範；R5 對 9 份歷史缺失提示詞全量追溯補建並雙向對齊 INDEX.md。
- **影響**：純 DOC-Refactor。改動範圍：5 個提示詞模板、2 個執行/tasks 模板、1 個 SOP 文件、9 個新建提示詞 `.md`、`prompts/INDEX.md`。零業務代碼改動，零 runtime 影響。

---

## §2 目標規格

### §2.1 R1 — 提示詞模板自愈歸檔防線（重構 5 個提示詞模板）

**目標狀態**：`template_prompt_for_plan.md`、`template_prompt_for_tasks.md`、`template_prompt_for_run.md`、`template_prompt_for_check.md`、`template_prompt_for_sop.md` 的**提示詞本體最頂端**（緊接元數據審計塊之後，所有其他執行指令之前），統一插入以下**強制主動歸檔指令區塊**：

```markdown
---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_<階段>_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`<檔案路徑>`」，然後繼續執行後續步驟。

---
```

- 原末段「`## 提示詞歸檔指令`」（bash `cp /dev/stdin ...` 形式）標記為「備援說明（baron 手動參考用）」，不再作為主要歸檔觸發點。

### §2.2 R2 — Check 階段提示詞物理稽核（新增 Conformance 維度四）

**目標狀態**：`template_prompt_for_check.md` 的 `## ✅ Conformance 驗收流程` 中，在現有三個維度（目標規格 / 驗收條件 / 不可動清單）之後，新增**第四維度**：

```markdown
| **提示詞歸檔** | `.claude-logs/prompts/` 物理目錄 | 執行以下稽核指令，確認本任務各階段提示詞均已實體存在 |
```

稽核指令規格：
```bash
ls .claude-logs/prompts/ | grep "<任務編碼>"
# 期望命中：plan / tasks / run(s) / check 各階段至少一個 .md 文件
```

**例外處理**：
- 若有缺失文件：Claude Code 必須在 Check 報告中明確列出缺失清單，並**立即補建缺失 .md 文件後再繼續**（自癒，不中斷收官流程，但必須在收官前補完）
- 確認全部存在後：標記「✅ 維度四 合規」，繼續收官

### §2.3 R3 — 備份/暫存 Staging 邊界鐵律（SOP + 模板）

**目標狀態**：在以下三份文件中明文確立「生命週期隔離三段式鐵律」：

**文件 A：`ref/WORKFLOW_SOP.md` §3 強制規則**，新增條目：
```
- .bak 備份鐵律：修改既有檔案前產出的 .bak 備份，屬審計存檔，
  **必須在對應 Run 階段的 git add 清單中強制包含**（以利跨環境 pull 與 git show 追溯）。
- baton/ 暫存鐵律：Run 階段產出的執行報告與 plan，
  **嚴禁在 Run 階段 mv 移動或 git add**，必須原封不動留在 baton/ 暫存。
- 收官歸檔鐵律：baton/ 下所有暫存文件，
  **必須且僅能在最後 Check 階段一次性 mv + git add 歸檔至正式目錄**。
```

**文件 B：`templates/template_execution.md` §3 備份路徑欄位說明**，新增：
> 備份檔（`.bak`）已在本 Run 階段 `git add` 納入 commit（必填，不可省略）

**文件 C：`templates/template_tasks.md` §8 六維度表格「git add 清單」說明**，新增備份說明：
> 包含：業務檔案 + `.bak` 備份 + `baton/` **不在此列**（Check 收官一次性歸檔）

### §2.4 R4 — Check §8 極簡化 + Commit Message 一致性加固

**目標狀態 A（Check §8 極簡化）**：

`templates/template_execution.md` 針對 **Check 執行報告**新增專屬 §8 格式規格說明：

> Check 執行報告的 `## §8 baron 執行命令` **只需一行**，所有 mv + git add 均由 AI 在 Check 執行過程中完成（已在本報告 §4 記錄）：

```bash
# 所有 mv + git add 已由 AI 完成（見本報告 §4 變動檔案清單）

# commit message 草稿已寫入（見本報告 §8.2 草稿展示）
git commit -F /tmp/<任務編碼>_Check_msg.txt
```

**目標狀態 B（commit message 草稿一致性）**：

所有執行報告（Run + Check）的 `## §8 baron 執行命令` 必須包含：

```bash
# commit message 草稿（已寫入 /tmp/<任務編碼>_<Commit代號>_msg.txt）
cat > /tmp/<任務編碼>_<Commit代號>_msg.txt << 'EOF'
<工作流類別>: <Commit代號> — <Commit名稱>

<3-5 行改動摘要>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
```

Commit message 檔案命名規範：`/tmp/<任務編碼>_<Commit代號>_msg.txt`（例：`/tmp/WORKFLOW-2_C1_msg.txt`）。

`template_prompt_for_check.md` Conformance 新增「維度五（草稿完整性）」，凡是 §8 缺少 msg.txt 完整草稿展示的執行報告，直接判定驗收不合規。

### §2.5 R5 — 歷史提示詞雙向稽核自癒（9 份缺失物理檔案補建）

**目標狀態（雙向對齊）**：

1. **幽靈條目清理**：刪除 `prompts/INDEX.md` 中所有「文字描述式」（非 `.md` 文件鏈接）的假條目，替換為實體文件鏈接。

2. **9 份缺失 .md 文件補建**：依據對應執行報告 §4 修法說明與對話 context，追溯還原並物理補建以下文件：

| # | 文件名稱 | 依據來源 |
|---|---|---|
| 1 | `2026-05-26_WORKFLOW-1_C1_提示詞.md` | executions/2026-05-26_WORKFLOW-1_C1_執行.md §4 |
| 2 | `2026-05-26_WORKFLOW-1_C1.5_提示詞.md` | executions/2026-05-26_WORKFLOW-1_C1.5_執行.md §4 |
| 3 | `2026-05-26_WORKFLOW-1_C2+C3_提示詞.md` | executions/2026-05-26_WORKFLOW-1_C2+C3_執行.md §4 |
| 4 | `2026-05-26_WORKFLOW-1_C4_提示詞.md` | executions/2026-05-26_WORKFLOW-1_C4_執行.md §4 |
| 5 | `2026-05-26_WORKFLOW-1_C5_提示詞.md` | executions/2026-05-26_WORKFLOW-1_C5_執行.md §4 |
| 6 | `2026-05-26_TODO-HOTFIX-1_Plan_提示詞.md` | hotfixes/2026-05-26_TODO-HOTFIX-1_hotfix.md §4 |
| 7 | `2026-05-26_TODO-HOTFIX-1_Run_提示詞.md` | executions/2026-05-26_TODO-HOTFIX-1_執行.md §4 |
| 8 | `2026-05-26_TODO-HOTFIX-1_Tasks+Run-1b_提示詞.md` | executions/2026-05-26_TODO-HOTFIX-1b_執行.md §4 |
| 9 | `2026-05-26_TODO-HOTFIX-1_Check_提示詞.md` | executions/2026-05-26_TODO-HOTFIX-1_Check_執行.md §4 |

3. **INDEX.md 全量重寫對應段落**：將 L16-26（WORKFLOW-1/TODO-HOTFIX-1 描述塊）替換為實體 .md 文件鏈接；將 L61-65（依時間排序文字描述條目）替換為對應 .md 文件鏈接。

4. **孤兒檔案稽核**：驗證所有物理 .md 文件均在 INDEX.md 有對應條目（目前稽核結論：無孤兒檔案，所有物理文件均已登記）。

---

## §3 現況與證據

### §3.1 漏洞一：提示詞歸檔指令「外置」，AI 可選擇性忽略

五個 `template_prompt_for_*.md` 的歸檔指令均位於提示詞本體**末段之外**（`## 提示詞歸檔指令` 區塊），格式為 baron 執行的 bash 命令，非 AI write_file 呼叫：

```bash
# template_prompt_for_plan.md L85-96（在「提示詞本體」區塊之外）
## 提示詞歸檔指令
cp /dev/stdin .claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_plan_提示詞.md
echo "..." >> .claude-logs/prompts/INDEX.md

# template_prompt_for_tasks.md L137-144（同樣外置）
## 提示詞歸檔指令
cp /dev/stdin .claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_tasks_提示詞.md

# template_prompt_for_run.md L126-135（同樣外置）
# template_prompt_for_check.md L169-178（同樣外置）
# template_prompt_for_sop.md L107-116（同樣外置）
```

**問題根因**：這些 bash 指令是「baron 發出提示詞前手動執行」的說明，AI 收到提示詞時這些指令已脫離 AI 的執行範疇 → AI 不會主動呼叫寫檔工具。

### §3.2 漏洞二：Check Conformance 只有 3 個維度，無提示詞稽核

`template_prompt_for_check.md L53-90`，Conformance 驗收表格僅含三維度：

```markdown
| 驗收維度 | 來源 | 核對方式 |
|---|---|---|
| **目標規格** | plan.md §2 | ... |
| **驗收條件** | tasks.md §6 | ... |
| **不可動清單** | tasks.md §7 | ... |
```

**缺失**：無「提示詞歸檔稽核」維度 → 即使歸檔完全缺失也不會觸發驗收阻斷。

### §3.3 漏洞三：Staging 生命週期無明文規範

**WORKFLOW_SOP.md §3 強制規則**（目前六條）中無任何條目規定：
- `.bak` 備份檔何時 `git add`
- `baton/` 執行報告何時可以 `mv` + `git add`
- Check 階段的 baton 清空義務

**template_execution.md §3** 的備份路徑欄位說明無明文「須在本 Commit git add」要求。

**template_tasks.md §8** 的六維度表格亦無明文區分 `.bak` 備份與 `baton/` 暫存報告的 git add 邊界。

**實際後果（已觀察）**：在 TODO-HOTFIX-1 系列中，`.bak` 備份已正確 git add；但此正確做法未來自模板規範，僅來自執行時的臨場判斷，存在迴歸風險。

### §3.4 漏洞四：§8 格式不一致，msg.txt 草稿缺乏強制規範

`template_execution.md §8 L105-114`：

```bash
# git add 清單
git add [檔案 A]
git add [檔案 B]

# commit message（已寫入 /tmp/[任務編碼]_[Commit代號]_msg.txt）
git commit -F /tmp/[任務編碼]_[Commit代號]_msg.txt
```

**問題**：
1. Check 報告的 §8 在 AI 已完成 mv + git add 後，仍繼承相同格式，出現冗餘的 `mv` 與 `git add` 指令（baron 看到需手動排除）
2. `/tmp/` 路徑使用 `[方括號]` 佔位符而非精確的 `<角括號>` 規格，語義不統一
3. §8 中無「完整草稿展示」要求，AI 只寫入 `/tmp/` 但不在報告中展示完整草稿，baron 無法在 commit 前預覽

### §3.5 漏洞五：幽靈索引詳細清單

**ghost audit 執行結果**（grep 物理目錄 vs INDEX.md 比對）：

**物理目錄檔案數**（`ls .claude-logs/prompts/` 排除 INDEX.md / README.md）：28 個 .md 文件

**INDEX.md 中有條目但物理目錄缺失（幽靈條目）**：9 份

| # | INDEX.md 位置 | 幽靈描述 | 對應缺失物理文件 |
|---|---|---|---|
| 1 | L16-21，WORKFLOW-1 C1 | 文字描述塊，無 .md 鏈接 | `2026-05-26_WORKFLOW-1_C1_提示詞.md` |
| 2 | L16-21，WORKFLOW-1 C1.5 | 文字描述塊，無 .md 鏈接 | `2026-05-26_WORKFLOW-1_C1.5_提示詞.md` |
| 3 | L16-21，WORKFLOW-1 C2+C3 | 文字描述塊，無 .md 鏈接 | `2026-05-26_WORKFLOW-1_C2+C3_提示詞.md` |
| 4 | L16-21，WORKFLOW-1 C4 | 文字描述塊，無 .md 鏈接 | `2026-05-26_WORKFLOW-1_C4_提示詞.md` |
| 5 | L16-21，WORKFLOW-1 C5 | 文字描述塊，無 .md 鏈接 | `2026-05-26_WORKFLOW-1_C5_提示詞.md` |
| 6 | L22-26，TODO-HOTFIX-1 Plan | 文字描述塊，無 .md 鏈接 | `2026-05-26_TODO-HOTFIX-1_Plan_提示詞.md` |
| 7 | L22-26，TODO-HOTFIX-1 Run | 文字描述塊，無 .md 鏈接 | `2026-05-26_TODO-HOTFIX-1_Run_提示詞.md` |
| 8 | L22-26，TODO-HOTFIX-1 Tasks/Run-1b | 文字描述塊，無 .md 鏈接 | `2026-05-26_TODO-HOTFIX-1_Tasks+Run-1b_提示詞.md` |
| 9 | L22-26，TODO-HOTFIX-1 Check | 文字描述塊，無 .md 鏈接 | `2026-05-26_TODO-HOTFIX-1_Check_提示詞.md` |

**L61-65（依時間排序）**：5 行文字描述條目（對應上述 5 個幽靈塊 + TODO-HOTFIX-1 四個），均無 .md 文件鏈接。

**物理目錄有檔但 INDEX 無條目（孤兒文件）**：0 份 ← 目前所有物理文件均已在 INDEX.md 登記 ✅

### §3.6 grep 鋼鐵證據

```bash
# R1 漏洞：歸檔指令外置確認
$ grep -n "cp /dev/stdin\|## 提示詞歸檔指令" templates/template_prompt_for_plan.md
85:## 提示詞歸檔指令
90:cp /dev/stdin .claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_plan_提示詞.md

$ grep -n "cp /dev/stdin\|## 提示詞歸檔指令" templates/template_prompt_for_tasks.md
137:## 提示詞歸檔指令
142:cp /dev/stdin .claude-logs/prompts/<YYYY-MM-DD>_<任務編碼>_tasks_提示詞.md

# R2 漏洞：Check 僅 3 維度
$ grep -n "維度\|稽核\|提示詞" templates/template_prompt_for_check.md
(0 命中「維度四」或「提示詞歸檔稽核」)

# R5 漏洞：物理目錄無 WORKFLOW-1 C1 相關文件
$ ls prompts/ | grep "WORKFLOW-1_C"
(0 命中)

$ ls prompts/ | grep "TODO-HOTFIX"
(0 命中)
```

---

## §4 不可動清單

- [ ] `pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*.py` / `static/*` — 業務代碼完全不動
- [ ] 主 repo 目錄（worktree 父目錄）— 嚴禁讀寫
- [ ] `.claude-logs/prompts/` 中**既有** 28 個 `.md` 文件 — 歷史提示詞歸檔不得改動（僅新增）
- [ ] `CLAUDE.md` §1–§5 既有規範條款 — 不得刪改（§1.2 提示詞歸檔規則已正確；本次只補強模板層）
- [ ] `ref/WORKFLOW_SOP.md` §1–§6 既有條款 — 不得刪改，僅在 §3 強制規則段新增備份/暫存鐵律
- [ ] `template_plan.md` — 不在本次改版範圍（plan 模板規格不變）

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 提示詞歸檔觸發規則 | `CLAUDE.md §1.2` / `prompts/README.md §1` |
| 六階段強制觸發鏈 | `ref/WORKFLOW_SOP.md §3` |
| baton/ 暫存規則 | `CLAUDE.md §3 工作目錄硬規則` |
| 不可動清單 + DOC-Refactor 工作流 | `ref/WORKFLOW_SOP.md §1.3` |
| §0 / §99 拆分式結構 | `ref/WORKFLOW_SOP.md §1.3 驗收要求` |
| 備份規則（現況） | `templates/template_prompt_for_run.md §💾 備份規則` |

---

## §6 驗證計畫

本任務為 DOC-Refactor，無 pytest / BE SOP 要求。

### §6.1 R1 驗收：歸檔指令已進入提示詞本體

```bash
# 每個重構後的模板，以下 grep 必須命中「第一步」區塊
grep -n "第一步：主動歸檔\|🗄️" \
  templates/template_prompt_for_plan.md \
  templates/template_prompt_for_tasks.md \
  templates/template_prompt_for_run.md \
  templates/template_prompt_for_check.md \
  templates/template_prompt_for_sop.md
# 期望：5 個文件各至少 1 命中
```

### §6.2 R2 驗收：Check 模板新增維度四

```bash
grep -n "維度四\|提示詞歸檔稽核" templates/template_prompt_for_check.md
# 期望：≥ 1 命中
```

### §6.3 R3 驗收：WORKFLOW_SOP.md 明文化備份/暫存鐵律

```bash
grep -n "bak 備份鐵律\|baton.*鐵律\|收官歸檔鐵律" \
  .claude-logs/ref/WORKFLOW_SOP.md
# 期望：3 命中（對應三段鐵律）
```

### §6.4 R4 驗收：Check 執行報告 §8 格式

對 Check 執行報告範本執行：
```bash
grep -n "Co-Authored-By\|_msg.txt\|cat > /tmp" templates/template_execution.md
# 期望：≥ 3 命中（草稿寫入 + Co-Author + msg.txt 路徑）
```

### §6.5 R5 驗收：9 份提示詞物理文件存在

```bash
# WORKFLOW-1 系列
ls .claude-logs/prompts/ | grep "WORKFLOW-1_C"
# 期望：5 命中（C1 / C1.5 / C2+C3 / C4 / C5）

# TODO-HOTFIX-1 系列
ls .claude-logs/prompts/ | grep "TODO-HOTFIX-1"
# 期望：4 命中（Plan / Run / Tasks+Run-1b / Check）

# INDEX.md 對齊
grep -c "WORKFLOW-1_C[0-9]" .claude-logs/prompts/INDEX.md
# 期望：≥ 5
grep -c "TODO-HOTFIX-1.*提示詞" .claude-logs/prompts/INDEX.md
# 期望：≥ 4
```

### §6.6 E2E：模板自愈功能驗證

在 baron 下次使用重構後模板發出提示詞時，Claude Code 執行的第一個工具呼叫應為 `Write` 寫入提示詞 `.md`，而非 `Read` 或 `Bash`。可透過觀察工具呼叫順序驗證。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **Q1：9 份歷史提示詞的「完整提示詞正文」如何還原？** | 依對應執行報告 §4 修法說明 + baton/ 規劃書 + 本對話 context 以「摘要重建」方式補建（非一字不漏重建），在「執行結果摘要」欄位標明「歷史補建版本，非原始逐字記錄」 | 原始提示詞文字無法 100% 從執行報告還原，但執行報告 §4 已記錄完整的「改動意圖 + 技術規格」，足以還原語意；完整逐字重建存在幻覺風險，摘要重建更誠實且仍滿足「可追溯」目標 |
| **Q2：WORKFLOW_SOP.md 屬 ref/ 核心文件，修改需要什麼流程？** | 依標準 DOC-Refactor 六階段流程執行，本 plan → tasks → 各 Run Commit → Check | SOP 修改雖是文件，仍需版控稽核；WORKFLOW-1 修改 CLAUDE.md / WORKFLOW_SOP.md 的先例已經確立此路徑正確 |
| **Q3：「維度五：草稿完整性」是否應列為獨立 Conformance 維度，還是整合進維度四？** | 獨立列為維度五 | 提示詞歸檔稽核（維度四）與 commit message 草稿完整性（維度五）是兩個不同的品質控制點；合併會使維度四過於複雜，且維度五 check 對象是執行報告 §8，維度四 check 對象是 prompts/ 目錄 |
| **Q4：Check §8 極簡化後，baton/ 清空驗證是否仍保留？** | 保留「確認 baton/ 只剩 README.md」步驟，但移至 Check 報告 §4 變動檔案清單確認，不放 §8 | §8 極簡化目標是讓 baron 只需看一行。baton/ 清空驗證屬於 AI 自我確認動作，放進 §4 讓 baron 有審計依據但不需手動操作 |
| **Q5：WORKFLOW-2 本身的提示詞（即本 plan 提示詞）如何處理？** | 已在本 session 以 `2026-05-27_WORKFLOW-2_Plan_提示詞.md` 歸檔（R1 修復後的自愈機制的第一次實踐） | 本 plan 提示詞本身即 R5 稽核需涵蓋的對象；歸檔動作已完成，INDEX.md 在 R5 Commit 時統一更新 |

---

## §99 治理規格

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 WORKFLOW-2 流程模板重構與提示詞自動歸檔的五大目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 WORKFLOW-2 tasks / 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 暫存於 baton/；tasks 拆分後 mv → plans/ + git add。嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-05-27)：初版建立（WORKFLOW-2 Plan 首版，五大規格 R1~R5 完整定義）
