# 2026-07-09 CONTEXT-1 C4 run 提示詞

- **任務代號**：CONTEXT-1（session 載入鏈瘦身與 context 治理）
- **階段**：C4 Run（階段 4 執行 — TODO Slimming TODO 瘦身歸檔）
- **工作流**：DOC-Refactor
- **歸檔時間**：2026-07-09

---

## 原始提示詞（逐字）

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-09 01:09 |
| **任務代號** | CONTEXT-1 C4 |
| **觸發 Commit** | C4 |
| **相關產出檔案** | .claude-logs/baton/2026-07-08_CONTEXT-1_C4_執行.md |
| **觸發情境** | baron 確認上一個 Commit（C3 生命週期規則同步）後，下達本次執行指令；本 Commit 為 C4 TODO 瘦身歸檔，將已完成清單完整搬移至 archive/TODO_done_archive.md，TODO.md 中改留一行式索引，並回填 a150915 佔位符。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-09_CONTEXT-1_C4_run_提示詞.md`
   格式依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-09_CONTEXT-1_C4_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：CONTEXT-1
- **當前 Commit 代號**：C4 — TODO Slimming（TODO 瘦身歸檔）
- **工作流類別**：DOC-Refactor
- **Tasks 路徑**：.claude-logs/baton/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```

CLAUDE.md                                                                           # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                                                    # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-07_CONTEXT-1_session載入鏈瘦身與context治理_plan_v1.md   # 全局策略 z (StraTA)
.claude-logs/baton/2026-07-08_CONTEXT-1_session載入鏈瘦身與context治理_tasks.md   # 本次執行的依據 tasks

```

### 🏢 工作目錄與授權範圍硬規則（必遵守）

- **唯一合法工作目錄**：`/Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public` (主 repo 目錄就地，依 CLAUDE.md §3 新規定)
- **授權讀寫範圍**：限於 `CLAUDE.md` 及 `.claude-logs/` 下特定的治理與配置檔案，嚴禁讀寫任何後端業務邏輯程式碼或測試目錄。
- **嚴禁改動業務代碼**（`*.py`、`static/`、`tests/`）
- **暫存檔限制**：執行過程中產出的執行報告必須存放在 `baton/` 目錄中，且**嚴禁在 C4 中將其 git add 提交**（不入版控，待 C5 checkout 收官時才一次性歸檔）。

### 🛠️ 執行命令

請依 `tasks.md §8 C4 具體實作細節` 進行代碼與文件修改，並嚴格遵守以下三個防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：逐項確認，不越界。
2. **測試防線**（`tasks.md §6 測試計畫 §6.4 C4 驗收`）：執行對應驗收 grep 條件及測試自檢。
3. **文件防線**（`CLAUDE.md §1.3`）：所有 commit / push 由 baron 手動執行，嚴禁自發。

### 🚨 pre_tool_guard 繞過程序規則

由於本次將對 `TODO.md` 大幅瘦身（縮減約 73.6%），**必然觸發 `pre_tool_guard.sh` 的截斷攔截規則（deny）**。請務必依據 tasks 實作細節規定的 sentinel 減速帶放行程序執行：
1. **重寫 TODO.md 時**：在寫入內容中夾帶 `<!-- BYPASS_TRUNCATION_GUARD: CONTEXT-1 C4 有意瘦身（plan Q6） -->` 註解行，以合法繞過守衛。
2. **重寫完成後**：立即呼叫 Edit 工具，移除該行 sentinel 註解（因為 old_string 包含 sentinel，此編輯不會被 guard 攔截），確保 TODO.md 最終零殘留此 sentinel 註解。

### 💾 備份規則

修改任何既有檔案前，必須先備份：
```bash
cp .claude-logs/TODO.md .claude-logs/archive/2026-07-08_CONTEXT-1_C4_TODO.md.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將本任務當前 Commit C4 標記為 ✅ 已完成（例如：`- ✅ C4 — TODO Slimming（TODO 瘦身歸檔）`）。
   - 將下一個 Commit C5 標記為 🟡 WIP（例如：`- 🟡 WIP: C5 — Checkout（收官歸檔）`）。

2. **歷史已提交 Hash 掃描與自愈回填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 `TODO.md` 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。
   - **特別注意**：在本 Commit 中，已獲得 Q1 baron 授權，自動將 `TODO.md` / `archive/TODO_done_archive.md` 中 RESCUE-1 C5 的 `待 baron 回填` 佔位符直接回填為實際 commit hash `a150915`。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-08_CONTEXT-1_C4_執行.md`（暫存 baton/，**嚴禁 git add**）
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容，將 msg 寫入 `/tmp/CONTEXT-1_C4_msg.txt`，且**嚴禁將 `baton/2026-07-08_CONTEXT-1_C4_執行.md` 放進 git add 列表中**：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（所有本次 Commit 涉及的改動，嚴禁 git add baton/ 下的執行報告與 tasks.md）
git add .claude-logs/TODO.md
git add .claude-logs/archive/TODO_done_archive.md
git add .claude-logs/archive/2026-07-08_CONTEXT-1_C4_TODO.md.bak

# 3. commit message 草稿（已寫入 /tmp/CONTEXT-1_C4_msg.txt）
cat > /tmp/CONTEXT-1_C4_msg.txt << 'EOF'
DOC-Refactor: C4 — TODO Slimming（TODO 瘦身歸檔）

1. 新建 archive/TODO_done_archive.md 歸檔檔，byte 逐字承接 TODO.md L12–L1056 的已完成歷史。
2. 重寫 TODO.md 以進行大幅瘦身，已完成清單改為單行索引指針格式，體積降至 ≤450 行。
3. 依 Q1 授權，將兩檔中的 RESCUE-1 C5 佔位符同步回填為真實 commit hash a150915。
4. 藉由夾帶 sentinel 註解行繞過 pre_tool_guard 的截斷攔截，並於完成後隨即 Edit 清除。
5. 進行 TODO.md 的階段備份並提交。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/CONTEXT-1_C4_msg.txt
```

---

### 🛑 停止指令

**產出 `C4_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C5（必須等 baron 確認後另行下達提示詞）
- ❌ 修改任何未列入本 Commit 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 上下文（承接對話）

1. C3（生命週期規則同步）已執行完畢、baron 確認後下達本 C4 Run。
2. 本提示詞：執行 C4 — TODO Slimming（tasks §8 C4：cp .bak → 新建 `archive/TODO_done_archive.md` byte 逐字承接已完成區 → TODO 重寫為一行式索引〔Q3 格式〕+ 三保留區逐字 + sentinel 夾帶/移除程序〔Q6〕；a150915 已於 C1 提前自癒、兩檔自然承接〔C1 報告 §4.3 既載連鎖〕）；執行報告暫存 baton；TODO C4→✅ / C5→WIP + hash 自癒；產完即停。

## 產出

- 新建 `archive/TODO_done_archive.md` + 重寫 `TODO.md`（≤450 行）+ 1 `.bak`
- `.claude-logs/baton/2026-07-08_CONTEXT-1_C4_執行.md`
- `TODO.md`（C4→✅、C5→🟡 WIP、hash 自癒）
