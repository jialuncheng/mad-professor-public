# 2026-07-08 CONTEXT-1 C1 run 提示詞

- **任務代號**：CONTEXT-1（session 載入鏈瘦身與 context 治理）
- **階段**：C1 Run（階段 4 執行 — Loading Chain Convergence 載入鏈收斂）
- **工作流**：DOC-Refactor
- **歸檔時間**：2026-07-08

---

## 原始提示詞（逐字）

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-08 23:54 |
| **任務代號** | CONTEXT-1 C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-07-08_CONTEXT-1_C1_執行.md |
| **觸發情境** | baron 確認上一個階段（Tasks 拆分與 TODO 🟡 WIP 新增）後，下達本次執行指令；本 Commit 為 C1 載入鏈收斂，改動 CLAUDE.md 及 baton/README.md。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-08_CONTEXT-1_C1_run_提示詞.md`
   格式依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-08_CONTEXT-1_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：CONTEXT-1
- **當前 Commit 代號**：C1 — Loading Chain Convergence（載入鏈收斂）
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
- **暫存檔限制**：執行過程中產出的執行報告必須存放在 `baton/` 目錄中，且**嚴禁在 C1 中將其 git add 提交**（不入版控，待 C5 checkout 收官時才一次性歸檔）。

### 🛠️ 執行命令

請依 `tasks.md §8 C1 具體實作細節` 進行代碼與文件修改，並嚴格遵守以下三個防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：逐項確認，不越界。
2. **測試防線**（`tasks.md §6 測試計畫 §6.1 C1 驗收`）：執行對應驗收 grep 條件及測試自檢。
3. **文件防線**（`CLAUDE.md §1.3`）：所有 commit / push 由 baron 手動執行，嚴禁自發。

### 💾 備份規則

修改任何既有檔案前，必須先備份：
```bash
cp CLAUDE.md .claude-logs/archive/2026-07-08_CONTEXT-1_C1_CLAUDE.md.bak
cp .claude-logs/baton/README.md .claude-logs/archive/2026-07-08_CONTEXT-1_C1_baton_README.md.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將本任務當前 Commit C1 標記為 ✅ 已完成（例如：`- ✅ C1 — Loading Chain Convergence（載入鏈收斂）`）。
   - 將下一個 Commit C2 標記為 🟡 WIP（例如：`- 🟡 WIP: C2 — Workdir Stale Fix（工作目錄修正）`）。

2. **歷史已提交 Hash 掃描與自愈回填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 `TODO.md` 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-08_CONTEXT-1_C1_執行.md`（暫存 baton/，**嚴禁 git add**）
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

---

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容，將 msg 寫入 `/tmp/CONTEXT-1_C1_msg.txt`，且**嚴禁將 `baton/2026-07-08_CONTEXT-1_C1_執行.md` 放進 git add 列表中**：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（所有本次 Commit 涉及的改動，嚴禁 git add baton/ 下的執行報告與 tasks.md）
git add CLAUDE.md
git add .claude-logs/baton/README.md
git add .claude-logs/archive/2026-07-08_CONTEXT-1_C1_CLAUDE.md.bak
git add .claude-logs/archive/2026-07-08_CONTEXT-1_C1_baton_README.md.bak

# 3. commit message 草稿（已寫入 /tmp/CONTEXT-1_C1_msg.txt）
cat > /tmp/CONTEXT-1_C1_msg.txt << 'EOF'
DOC-Refactor: C1 — Loading Chain Convergence（載入鏈收斂）

1. 收斂 CLAUDE.md 載入鏈中的 baton wildcard 引用，僅保留 README.md。
2. 補全 CLAUDE.md 治理規格排序原則，明定靜態規範優先、動態狀態靠後。
3. 更新 baton/README.md 說明頁面，新增按需取用機制指南。
4. 完成 CLAUDE.md 與 baton/README.md 之階段基準備份。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/CONTEXT-1_C1_msg.txt
```

---

### 🛑 停止指令

**產出 `C1_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C2（必須等 baron 確認後另行下達提示詞）
- ❌ 修改任何未列入本 Commit 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 上下文（承接對話）

1. Tasks（5 commits、C1 設 🟡 WIP）已於前一輪產出；baron 確認後下達本 C1 Run。
2. 本提示詞：執行 C1 — Loading Chain Convergence（tasks §8 C1：CLAUDE.md §0 wildcard→僅 README〔U3/Q4〕+ §99.1 排序原則〔U5/Q5〕+ §99.2 v4 + baton/README 按需取用節；2 `.bak`）；產執行報告暫存 baton（嚴禁 git add）；TODO C1→✅ / C2→WIP + hash 自癒；產完即停。

## 產出

- `CLAUDE.md`（§0 L12 / §99.1 / §99.2 v4）+ `baton/README.md`（按需取用節）+ 2 `.bak`
- `.claude-logs/baton/2026-07-08_CONTEXT-1_C1_執行.md`
- `TODO.md`（C1→✅、C2→🟡 WIP、hash 自癒）
