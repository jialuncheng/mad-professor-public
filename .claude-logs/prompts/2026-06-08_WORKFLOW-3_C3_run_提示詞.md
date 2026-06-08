# WORKFLOW-3 C3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-08 18:06 |
| 任務代號 | WORKFLOW-3 C3 |
| 觸發 Commit | C3 |
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_tasks.md` |
| 觸發情境 | baron 確認 C2 落地，下達 C3 執行指令 |

---

## 正文（原始提示詞全文摘要）

### 任務資訊
- 任務編碼：WORKFLOW-3 / Commit：C3 / 工作流類別：DOC-Refactor
- Tasks 路徑：`.claude-logs/baton/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_tasks.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C3）/ framework（改版對象、讀前先備份）/ template_plan.md（C2 確立的 SSOT、C3 改引用此檔）

### 執行命令（依 tasks §8 C3）
① 改前備份 framework → archive/2026-06-08_WORKFLOW-3_C3_framework.md.bak。
② 改寫 `### 4.1 計畫檔 (_plan.md) 結構契約`（L122-131）：保留前言哲學句「計畫檔是用來向人類/自己證明你已經想透了解法。不寫程式碼，純分析。」；移除原自列 1-8 章節清單；替換為「plan 結構唯一真理源 SSOT = template_plan.md（不再自列、避免 doc-drift）+ 模板含哪些章」+「跨 Phase 接縫契約唯一權威源見 WORKFLOW_SOP §7」。
③ 不刪 `### 4.2 執行報告結構契約` 及其他章節（§1-§3/§4.2/§5-§9 全保留）。
④ §99.2 新增 v4 Revision（§4.1 改引用 template SSOT、消滅 drift、接縫契約引用 §7）。
⑤ 嚴禁 mv/git add baton。

### 不可動
僅改 framework；不碰 WORKFLOW_SOP/template_plan/.py/CLAUDE.md。

### 同步更新 TODO.md
- C3 ✅、C4 🟡 WIP；git log 自癒回填殘留「待 baron 回填」（含 C1/C2 hash）。

### 產出規格
- 執行報告 `baton/2026-06-08_WORKFLOW-3_C3_執行.md`（暫存 baton、嚴禁 mv/git add、C4 才歸檔）；套 template_execution。
- §5.3 SOP 核查填「DOC-Refactor 無 .py 改動、跳過（合規）」。

### §8 baron 執行命令
- git add：framework + .bak + TODO + 2 prompts。
- msg 草稿寫 `/tmp/WORKFLOW-3_C3_msg.txt`，`docs(workflow)` 前綴。
  ⚠️ 署名校正：依 CLAUDE.md 全局規範用 `Claude Opus 4.8 (1M context)`（提示詞模板誤寫 Sonnet 4.6、以全局規範為準）。

### 停止指令
產出執行報告（暫存 baton）後立即停止；不續 C4、不改 WORKFLOW_SOP/template_plan/.py/CLAUDE.md、不 mv/git add baton、不自發 commit/push。
