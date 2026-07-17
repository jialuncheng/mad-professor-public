# 2026-07-18 — SEC-HARDEN C2 提示詞

> **收到時間**：2026-07-18 03:35（UTC+8）
> **任務代號**：SEC-HARDEN C2
> **觸發 commit**：SEC-HARDEN C2（CORS Restriction）
> **相關產出檔案**：`.claude-logs/baton/2026-07-18_SEC-HARDEN_C2_執行.md`
> **觸發情境**：baron 確認 C1（Login Hardening）後，下達 C2（CORS 收斂：#4 `allow_origins` → `settings.CORS_ALLOW_ORIGINS` 顯式白名單、不啟用 credentials）之單一 Commit 執行指令；BE-Refactor 工作流、依 tasks §8 實作、執行報告暫存 baton/。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-18 03:35 |
| **任務代號** | SEC-HARDEN C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-18_SEC-HARDEN_C2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-18_SEC-HARDEN_C2_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`SEC-HARDEN`
- **當前 Commit 代號**：`C2`
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

請依 `tasks.md §8 C2 具體實作細節` 進行代碼修改，並嚴格遵守以下防線：

1. **物理防線**（`tasks.md §7 不可動清單`）：
   - ⚠️ 嚴禁在 CORS 加固中修改任何與 CORS 設定無關的業務邏輯或設定檔。
   - ⚠️ 嚴禁啟用 `allow_credentials`。

2. **測試防線**（`tasks.md §6.2`）：
   - 修改完成後，必須在 `tests/test_sec_harden.py` 中追加針對 CORS `allow_origins` 不為萬用字元 `*` 的測試。
   - 執行 `pytest tests/` 確保全體通過（無 regression），並貼上驗收與 SOP 一致性核查（§6.6）的終端輸出。

3. **文件防線**（`CLAUDE.md §1.3`）：
   - **產出之執行報告與既有的 plan、tasks 等文件均為 baton 暫存文件，嚴禁在此階段執行 `mv` 或 `git add` 歸檔，必須留在 `baton/` 中（暫不入 Git，待最後 checkout 階段統一搬移歸檔）。**
   - 所有實體 `git commit` 與 `push` 動作由 baron 手動執行，你不可擅自 commit。

### 💾 備份規則

修改 `web_server.py` 與 `settings.py` 前，必須先執行備份：

```bash
cp web_server.py .claude-logs/archive/2026-07-18_SEC-HARDEN_C2_web_server.py.bak
cp settings.py .claude-logs/archive/2026-07-18_SEC-HARDEN_C2_settings.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將 `C2` 標記為 ✅ 已完成：`- ✅ C2 — CORS Restriction（CORS 收斂）`。
   - 將 `C3` 標記為 🟡 WIP：`- 🟡 WIP C3 — Error Masking（例外遮蔽）`。

2. **歷史已提交 Hash 掃描與自愈回填（雙源）**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 **`TODO.md` 與 `archive/TODO_done_archive.md`** 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-07-18_SEC-HARDEN_C2_執行.md`（暫存於 baton/ 目錄）
- **套用模板**：`.claude-logs/templates/template_execution.md`

執行報告必須包含：
- 頂部元數據塊（狀態為 `Completed (Commit C2)`，Git hash 留空由 baron 回填）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（需包含備份的兩個 `.bak` 檔案；**特別注意：暫存於 baton/ 的執行報告與 plan/tasks 嚴禁在此列入 git add 清單**）
- §4 修法說明（附關鍵代碼片段）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態 + 下一步指向 C3）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供以下內容：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C2 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add web_server.py
git add settings.py
git add tests/test_sec_harden.py
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C2_web_server.py.bak
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C2_settings.py.bak

# 3. commit message 草稿（已寫入 /tmp/SEC-HARDEN_C2_msg.txt）
cat > /tmp/SEC-HARDEN_C2_msg.txt << 'EOF'
BE-Refactor: SEC-HARDEN C2 — CORS Restriction（CORS 收斂）

1. 新增 settings.CORS_ALLOW_ORIGINS，將 CORS allow_origins 收斂為顯式白名單，廢除萬用字元 "*"。
2. 白名單預設包含同源、本地 localhost 與 127.0.0.1 開發埠，維持不啟用 allow_credentials 以維持原跨源安全性。
3. 於 tests/test_sec_harden.py 追加單元測試，斷言 web_server 的 CORS 中介層設定已收斂，非萬用字元。
EOF

# 4. baron 手動執行
git commit -F /tmp/SEC-HARDEN_C2_msg.txt
```

---

### 🛑 停止指令

**產出 `2026-07-18_SEC-HARDEN_C2_執行.md` 並更新 TODO.md 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit C3（必須等 baron 確認後另行下達 C3 提示詞）
- ❌ 修改任何未列入 C2 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ✅ 完成（C2 落地、未 commit·由 baron 手動）
- pytest baseline 729 passed → final **734 passed / 3 skipped / 0 failed**（+5 CORS 守衛測試）
- 改動檔案：`settings.py` + `web_server.py` + `tests/test_sec_harden.py`（追加）+ 2 `.bak`
- 執行報告：`.claude-logs/baton/2026-07-18_SEC-HARDEN_C2_執行.md`（baton 暫存）；commit msg 草稿 `/tmp/SEC-HARDEN_C2_msg.txt`
- hash 自癒：C1 `52ebae8` 回填 TODO.md + C1 執行報告；GOV-PATH-FIX checkout 仍未 commit、佔位符保留
- commit / push：未執行（依 CLAUDE.md §1.3 待 baron）

## 後續引用

- 無
