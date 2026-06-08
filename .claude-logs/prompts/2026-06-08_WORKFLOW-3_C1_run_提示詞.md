# WORKFLOW-3 C1 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-08 17:40 |
| 任務代號 | WORKFLOW-3 C1 |
| 觸發 Commit | C1 |
| 工作流類別 | DOC-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_tasks.md` |
| 觸發情境 | baron 確認 tasks 拆分，下達 C1 執行指令 |

---

## 正文（原始提示詞全文摘要）

### 任務資訊
- 任務編碼：WORKFLOW-3 / Commit：C1 / 工作流類別：DOC-Refactor
- Tasks 路徑：`.claude-logs/baton/2026-06-08_WORKFLOW-3_跨Phase接縫契約與收官前整合測試_tasks.md`

### 強制讀檔
- CLAUDE.md / WORKFLOW_SOP.md（改版對象、讀前先備份）/ tasks.md（§8 C1 具體實作細節）

### 執行命令（依 tasks §8 C1）
- WORKFLOW_SOP.md 新增 §7 跨 Phase 接縫契約（§7.1 接縫契約 + worked example 修正版 #1 + 反例 / §7.2 收官前整合測試 + key-changing transform + Checkout 必驗 + 豁免）+ §3 強制規則一行 + §4.2 A6（6 項）+ §99.1 重複防護 + §99.2 v4。
- 三防線：§7 不可動清單（僅改 WORKFLOW_SOP、不碰 template/framework/.py）/ §6.1 六條 grep 驗收（含 A5 無動態內容）/ 不自發 commit。

### 備份規則
改 WORKFLOW_SOP.md 前備份 `archive/2026-06-08_WORKFLOW-3_C1_WORKFLOW_SOP.md.bak`。

### 同步更新 TODO.md
- C1 ✅、C2 🟡 WIP；git log 自癒回填殘留「待 baron 回填」。

### 產出規格
- 執行報告 `baton/2026-06-08_WORKFLOW-3_C1_執行.md`（暫存 baton、**嚴禁 mv/git add**、C4 才歸檔）；套 template_execution。
- §5.3 SOP 核查填「DOC-Refactor 無 .py 改動、跳過（合規）」。

### §8 baron 執行命令
- git add：WORKFLOW_SOP.md + .bak + TODO + 2 prompts。
- msg 草稿寫 `/tmp/WORKFLOW-3_C1_msg.txt`，`docs(workflow)` 前綴。
  ⚠️ 署名校正：依 CLAUDE.md 全局規範用 `Claude Opus 4.8 (1M context)`（提示詞模板誤寫 Sonnet 4.6、以全局規範為準）。

### 停止指令
產出執行報告（暫存 baton）後立即停止；不續 C2、不改 template/framework/.py、不 mv/git add baton、不自發 commit/push。
