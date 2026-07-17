# 2026-07-18 — SOP-COMPLY C3 提示詞

> **收到時間**：2026-07-18 06:51（UTC+8）
> **任務代號**：SOP-COMPLY C3
> **觸發 commit**：SOP-COMPLY C3（Borrow-Session Transaction Coordination）
> **相關產出檔案**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_C3_執行.md`
> **觸發情境**：baron 確認 C2（自持交易守護）後，下達 C3（借用交易呼叫端協調·**原子**：`paper_manager.py` 6 借用 helper 移除 `session.commit()` + `web_server.py` 5 端點包 `with s.begin():` + 3 直呼測試檔包 `with s.begin():` 三者同 commit）之單一 Commit 執行指令；BE-Refactor 工作流、依 tasks §8 實作、執行報告暫存 baton/。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-18 06:51 |
| **任務代號** | SOP-COMPLY C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-18_SOP-COMPLY_C3_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-18_SOP-COMPLY_C3_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`SOP-COMPLY`
- **當前 Commit 代號**：`C3`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```
CLAUDE.md                                                      # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                               # 工作流規範（已自動載入）
.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_plan_v1.md  # 全局策略 plan
.claude-logs/baton/2026-07-18_SOP-COMPLY_logging與DB_SOP合規清帳_tasks.md  # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                # 日誌配置 SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md               # 資料庫操作 SOP 手冊
```

### 🛠️ 執行命令

請依 `tasks.md §8 C3 具體實作細節` 進行代碼修改，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 僅限修改 5 個變更檔案的 Session 呼叫包裹與 commit 移除，嚴禁改動寫入的業務邏輯。
   - ⚠️ 嚴禁更動測試檔中的斷言期望值本體，僅修改 Session 生命週期宣告。
   - ⚠️ 必須將 **helper commit 移除 + web_server 呼叫端包裹 + 3 個測試檔包裹** 作為單一原子改動落於本 Commit（防範測試紅燈）。

2. **測試防線**（`tasks.md §6.3`）：
   - 修改完成後，執行 `pytest tests/` 確保全體通過（無 regression，尤其是自動標籤與手動標籤測試）。
   - 執行 `grep -nE "\.commit\(\)" paper_manager.py | grep -v "with .*session.*begin()"`，預期命中為 0。
   - 貼上驗收與 SOP 一致性核查（§6.5）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改 5 檔既有檔案前，必須先執行備份：

```bash
cp paper_manager.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_paper_manager.py.bak
cp web_server.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_web_server.py.bak
cp tests/test_paper_tags.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_paper_tags.py.bak
cp tests/test_normalize_tag.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_normalize_tag.py.bak
cp tests/test_folder_auto_tags.py .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_folder_auto_tags.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C3` 標記為 ✅ 已完成：`- ✅ C3 — Borrow-Session Transaction Coordination（借用交易呼叫端協調）`。
   - 將 `checkout` 標記為 🟡 WIP：`- 🟡 WIP checkout — 成果收官歸檔（成果歸檔與移出暫存）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-18_SOP-COMPLY_C3_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C3)`，Git hash 留空由 baron 回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（需包含備份的 5 個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 修法說明（附關鍵代碼片段）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 checkout 收官）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C3 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add paper_manager.py
git add web_server.py
git add tests/test_paper_tags.py
git add tests/test_normalize_tag.py
git add tests/test_folder_auto_tags.py
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_paper_manager.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_web_server.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_paper_tags.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_normalize_tag.py.bak
git add .claude-logs/archive/2026-07-18_SOP-COMPLY_C3_test_folder_auto_tags.py.bak

# 3. commit message 草稿（已寫入 /tmp/SOP-COMPLY_C3_msg.txt）
cat > /tmp/SOP-COMPLY_C3_msg.txt << 'EOF'
BE-Refactor: SOP-COMPLY C3 — Borrow-Session Transaction Coordination（借用交易呼叫端協調）

1. 移除 paper_manager.py 中 6 個借用 Session 的 helper 函數內的 session.commit()，將交易邊界控制權回歸呼叫端。
2. 修改 web_server.py 中的 5 處資料夾/標籤 API 路由，以 with s.begin(): 包裹事務呼叫。
3. 修改 test_paper_tags.py、test_normalize_tag.py 與 test_folder_auto_tags.py 三檔單元測試中對 pm.set_paper_* 函數的直呼，包裹 with s.begin(): 防止因 helper 內移除 commit 而在 Session 關閉時自動 rollback。
EOF

# 4. baron 手動執行
git commit -F /tmp/SOP-COMPLY_C3_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-18_SOP-COMPLY_C3_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行 checkout 收官（必須等 baron 確認後另行下達 checkout 提示詞）
- ❌ 修改 any 未列入 C3 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ✅ 完成（C3 原子落地、未 commit·由 baron 手動）；**paper_manager 裸 commit 歸零＝database SOP §5.2 全清**
- pytest baseline 748 passed → final **748 passed / 3 skipped / 0 failed**（零退化·標籤 18 測試全綠＝持久化實證）
- 改動：6 helper 移除 commit〔create_folder 補 flush 保 f.id〕+ web_server 4 session 區塊（5 呼叫點）包 begin〔ValueError→400 保留〕+ 3 測試檔 15 寫入區塊包 begin〔斷言零動·腳本防誤包〕+ 5 `.bak`
- 執行報告：`.claude-logs/baton/2026-07-18_SOP-COMPLY_C3_執行.md`；msg 草稿 `/tmp/SOP-COMPLY_C3_msg.txt`
- hash 自癒：無新 commit、雙源佔位符 0
- commit / push：未執行（依 CLAUDE.md §1.3 待 baron）

## 後續引用

- 無
