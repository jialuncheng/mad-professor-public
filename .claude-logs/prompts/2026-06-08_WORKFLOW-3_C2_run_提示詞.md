# WORKFLOW-3 C2 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-08 17:53 |
| 任務代號 | WORKFLOW-3 C2 |
| 觸發 Commit | C2 |
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_tasks.md` |
| 觸發情境 | baron 確認 C1 落地，下達 C2 執行指令 |

---

## 正文（原始提示詞全文摘要）

### 任務資訊
- 任務編碼：WORKFLOW-3 / Commit：C2 / 工作流類別：DOC-Refactor
- Tasks 路徑：`.claude-logs/baton/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_tasks.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md（C1 已落地 §7、C2 交叉引用）/ tasks.md（§8 C2）/ template_plan.md（改版對象、讀前先備份）

### 執行命令（依 tasks §8 C2）
① 改前備份 template_plan.md → archive/2026-06-08_WORKFLOW-3_C2_template_plan.md.bak。
② 於 §3 現況與證據 後、原 §4 不可動 前插入兩新章：
   - `## §4 跨 Phase 接縫契約（跨 Phase 任務必填、否則「無」）`：三欄式空範本（| handoff | producer | consumer | key 精確身份 + 同基準保證 |）+ 交叉引用 WORKFLOW_SOP §7（唯一權威源）。
   - `## §5 變動風險與相容性評估`：三欄式空範本（| 風險 | 等級 | 評估/緩解 |）+ 對齊 framework §4.1 #5。
③ 重編號：原 §4 不可動→§6 / §5 規格依據→§7 / §6 驗證（§6.1/§6.2）→§8（§8.1/§8.2）/ §7 OQ→§9。
④ §0 改版觸發 §1–§7→§1–§9。
⑤ §99 權威源/改版觸發 §1–§7→§1–§9 + §99.2 新增 Revision（升 SSOT、新增 §4/§5 + 重編號）。
⑥ grep -c '^## §' 確認章節數 = 原數 +2。
⑦ 嚴禁 mv/git add baton。

### 不可動
僅改 template_plan.md；不碰 WORKFLOW_SOP/framework/.py/CLAUDE.md；保留 §2 目標規格「不寫實作」精煉哲學。

### 同步更新 TODO.md
- C2 ✅、C3 🟡 WIP；git log 自癒回填殘留「待 baron 回填」（含 C1 hash）。

### 產出規格
- 執行報告 `baton/2026-06-08_WORKFLOW-3_C2_執行.md`（暫存 baton、嚴禁 mv/git add、C4 才歸檔）；套 template_execution。
- §5.3 SOP 核查填「DOC-Refactor 無 .py 改動、跳過（合規）」。

### §8 baron 執行命令
- git add：template_plan.md + .bak + TODO + 2 prompts。
- msg 草稿寫 `/tmp/WORKFLOW-3_C2_msg.txt`，`docs(workflow)` 前綴。
  ⚠️ 署名校正：依 CLAUDE.md 全局規範用 `Claude Opus 4.8 (1M context)`（提示詞模板誤寫 Sonnet 4.6、以全局規範為準）。

### 停止指令
產出執行報告（暫存 baton）後立即停止；不續 C3、不改 WORKFLOW_SOP/framework/.py/CLAUDE.md、不 mv/git add baton、不自發 commit/push。
