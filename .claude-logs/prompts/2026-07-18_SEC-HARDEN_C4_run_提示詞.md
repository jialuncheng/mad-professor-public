# 2026-07-18 — SEC-HARDEN C4 提示詞

> **收到時間**：2026-07-18 03:51（UTC+8）
> **任務代號**：SEC-HARDEN C4
> **觸發 commit**：SEC-HARDEN C4（Theme Overwrite Guard）
> **相關產出檔案**：`.claude-logs/baton/2026-07-18_SEC-HARDEN_C4_執行.md`
> **觸發情境**：baron 確認 C3（Error Masking）後，下達 C4（主題覆寫守衛：#6 模組級 `BUILTIN_THEMES` frozenset + sanitize 後 `lower()` 命中內建 4 名即 400 拒絕、`write_bytes` 前攔截）之單一 Commit 執行指令；BE-Refactor 工作流、依 tasks §8 實作、執行報告暫存 baton/。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-18 03:51 |
| **任務代號** | SEC-HARDEN C4 |
| **觸發 Commit** | C4 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-18_SEC-HARDEN_C4_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-18_SEC-HARDEN_C4_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`SEC-HARDEN`
- **當前 Commit 代號**：`C4`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_plan_v1.md  # 全局策略 plan
.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🛠️ 執行命令

請依 `tasks.md §8 C4 具體實作細節` 進行代碼修改，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁修改或弱化既有的檔名 sanitize、路徑 traversal 檢查與大小限制（L1251-1268 邏輯本體）。
   - ⚠️ 僅限在 `write_bytes` 前新增內建同名檢查。

2. **測試防線**（`tasks.md §6.4`）：
   - 修改完成後，在 `tests/test_sec_harden.py` 中追加針對主題上傳檔名經過處理後為 `mies` 或大小寫變體 `Mies` 等內建主題名時，回傳 400 且不寫檔的測試。
   - 執行 `pytest tests/` 確保全體通過（無 regression），並貼上驗收與 SOP 一致性核查（§6.6）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改 `web_server.py` 前，必須先執行備份（C4 僅修改此業務檔案）：

```bash
cp web_server.py .claude-logs/archive/2026-07-18_SEC-HARDEN_C4_web_server.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C4` 標記為 ✅ 已完成：`- ✅ C4 — Theme Overwrite Guard（主題覆寫守衛）`。
   - 將 `checkout` 標記為 🟡 WIP：`- 🟡 WIP checkout — 成果收官歸檔（成果歸檔與移出暫存）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-18_SEC-HARDEN_C4_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C4)`，Git hash 留空由 baron 回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（需包含備份的 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 修法說明（附關鍵代碼片段）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 checkout 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C4 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add web_server.py
git add tests/test_sec_harden.py
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C4_web_server.py.bak

# 3. commit message 草稿（已寫入 /tmp/SEC-HARDEN_C4_msg.txt）
cat > /tmp/SEC-HARDEN_C4_msg.txt << 'EOF'
BE-Refactor: SEC-HARDEN C4 — Theme Overwrite Guard（主題覆寫守衛）

1. 新增模組級 BUILTIN_THEMES 唯讀集，收錄 mies, kahn, kandinsky, nara 四個內建主題名。
2. 於主題上傳處理器之寫檔（write_bytes）前新增檔名大小寫不敏感比對守衛，命中時以 400 狀態拒絕上傳。
3. 防範大小寫變體（例如 Mies）在不區分大小寫之檔案系統中覆寫內建主題 CSS 資產。
4. 於 tests/test_sec_harden.py 追加單元測試，驗證內建主題覆寫攔截機制。
EOF

# 4. baron 手動執行
git commit -F /tmp/SEC-HARDEN_C4_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-18_SEC-HARDEN_C4_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達 checkout 提示詞）
- ❌ 修改任何未列入 C4 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ✅ 完成（C4 落地、未 commit·由 baron 手動）；C1–C4 四項實作全數完成、僅餘 checkout
- pytest baseline 739 passed → final **745 passed / 3 skipped / 0 failed**（+6 主題守衛測試·含行為測試 tmp_path 隔離）
- 改動檔案：`web_server.py`（BUILTIN_THEMES + sanitize 後守衛）+ `tests/test_sec_harden.py`（追加）+ 1 `.bak`
- 執行報告：`.claude-logs/baton/2026-07-18_SEC-HARDEN_C4_執行.md`（baton 暫存）；commit msg 草稿 `/tmp/SEC-HARDEN_C4_msg.txt`
- hash 自癒：C3 `bc5d5f4` 回填 TODO.md + C3 執行報告；GOV-PATH-FIX checkout 仍未 commit、佔位符保留
- commit / push：未執行（依 CLAUDE.md §1.3 待 baron）

## 後續引用

- 無
