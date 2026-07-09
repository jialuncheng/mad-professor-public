# 2026-07-09 — DOC-SYNC-1 C1 run 提示詞

> **收到時間**：2026-07-09 07:53（UTC+8）
> **任務代號**：DOC-SYNC-1 C1
> **觸發 commit**：C1
> **相關產出檔案**：design/docs 5 檔（components 標註/dom-reference 補 48 ID+戳/token 三檔零差戳）+ baton 執行報告 `2026-07-09_DOC-SYNC-1_Sync_C1_執行.md`
> **觸發情境**：baron 確認 tasks（plan v3 勘誤後）下達 C1（Docs Truth Sync）：兩款凍結措辭標註（2 真幽靈+3 半實作）、`.dropdown-popup` 零碰、48 ID 依分區表補齊（輕量欄位）、同步戳×2、token 戳×3；5 .bak；index.html 唯讀零 byte 變更。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 07:53 |
| **任務代號** | DOC-SYNC-1 C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_tasks.md |
| **觸發情境** | baron 確認 tasks 規格，下達第一個 Commit 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-09_DOC-SYNC-1_C1_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C1。

### 📋 任務資訊
- 任務編碼：DOC-SYNC-1 / 當前 Commit：C1 / 工作流：DOC-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / plan_v1（v3）/ tasks / index.html（唯讀）/ design/docs 5 修改目標

### 🏢 修改邊界與限制
1. 僅允許修改 design/docs 五檔；嚴禁改任何代碼/靜態資源（index.html 唯讀零 byte 變更）。
2. `.dropdown-popup` 零碰（tasks 勘誤判定有效）。
3. 版控限制：C1 git 追蹤僅 5 檔 + 5 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與備份
1. 備份 5 檔 → archive/2026-07-09_DOC-SYNC-1_C1_<檔名>.md.bak
2. components 標註（title-meta×2 處未實作 / L357-359 半實作凍結措辭）+ dom-reference 依 tasks §4.1(b) 補 48 ID（id｜用途一句｜JS 綁定行號）+ 兩檔頂部同步戳 + token 三檔 H1 下零差戳（§4.1(c) 逐字）
3. 驗收：tasks §6.1（差集 0、⚠️ 標記、戳×5、增量 ≤160、零代碼）

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C1 → ✅；checkout → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-09_DOC-SYNC-1_Sync_C1_執行.md`（baton、不入 git）；§1–§8。
- §8：git add 5 檔+5 .bak；msg /tmp/DOC-SYNC-1_C1_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 checkout / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 完成狀態：components 兩款標註（dropdown-popup 零碰）+ dom-reference 補 48 ID（分區歸組+Modal 家族新節）+ 同步戳×2 + token 零差戳×3
- §6.1 驗收：差集 0、每幽靈處帶 ⚠️、戳×5、增量 ≤160、diff 僅 design/docs
- 是否 commit / push：否（baron 手動）

## 後續引用

checkout 由 baron 另下獨立提示詞觸發。
