`````markdown
# 2026-06-04 — PIPE-RESUME C2 Run 提示詞

> **收到時間**：2026-06-04 18:29（UTC+8）
> **任務代號**：PIPE-RESUME C2
> **觸發 commit**：C2（P1 Ingestion — Vision 整份解析與元數據）
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C2_執行.md`
> **觸發情境**：baron 確認 C1 已手動提交（Checkout 含 C1），下達 C2 執行指令——實作 `run_phase1`：呼叫 `ResumeProcessor` Vision 核心整份解析+去浮水印、抽 `candidate_name→title` 建 `IngestionMetadataSpec`、`phone/email/domain` 暫存 `self._raw_meta` interim 穿線；產報告暫存 baton/、同步 TODO.md（C2 ✅ / C3 WIP + Hash 自癒）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 18:29 |
| **任務代號** | `PIPE-RESUME C2` |
| **觸發 Commit** | `C2` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | baron 確認 C1 已手動提交，下達 C2 執行指令（當前 Checkout Commit 含 C1）。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-06-04_PIPE-RESUME_C2_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-06-04_PIPE-RESUME_C2_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit。

### 📋 任務資訊

- **任務編碼**：`PIPE-RESUME`
- **當前 Commit 代號**：`C2`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單

請在開始執行前，必須完整閱讀以下文件：

```

CLAUDE.md                                                                           # 核心規範與契約（已自動載入）
.claude-logs/ref/WORKFLOW_SOP.md                                                    # 工作流規範（已自動載入）
.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md           # 本次執行的依據 tasks（§8 實作細節）
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md                                      # logging SOP 手冊
.claude-logs/sop/2026-05-23_database_SOP_手冊.md                                     # database SOP 手冊

```

### 🛠️ 執行命令與代碼修改規則

請依 `tasks.md §8 C2 具體實作細節` 進行代碼修改，並嚴格遵守以下規則：

1. **物理防線**（`tasks.md §7 不可動清單`）：阻斷級別，不可觸碰 `pipeline_core.py`、既有 processors 的內部核心或凍結合約。
2. **測試防線**（`tasks.md §6 測試計畫`）：執行對應驗收 grep 條件及 `pytest`（§6.2 驗收測試），確保 P1 契約與無 Abstract/LCC/Glossary 斷言通過。
3. **文件防線**（`CLAUDE.md §1.3`）：所有 commit / push 由 baron 手動執行，嚴禁自發。
4. **原始碼修改註解包裝**：
   *   請在修改既有原始碼的地方，統一使用對應語言的註解格式，將修改區塊以 `=== [<任務編碼> <Commit/OP代號> START] ===` 與 `=== [<任務編碼> <Commit/OP代號> END] ===` 包裝起來（例如 Python 為 `# === [PIPE-RESUME C2 START] ===` 與 `# === [PIPE-RESUME C2 END] ===`），以利後續人工審計與未來的代碼 Flip/重構移除。

### 💾 備份規則

修改任何既有檔案前，必須先備份（由於本次修改 C1 已建的 `pipelines/resume_pipeline.py`，請先執行備份）：
```bash
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_resume_pipeline.py.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填（必做、即時）

**在產出本階段的執行報告後，你必須立即修改根目錄下的 `TODO.md`，進行以下狀態更新與歷史 Hash 自愈填入：**

1. **WIP 狀態更新**：
   - 將本任務當前 Commit 標記為 ✅ 已完成：`- ✅ C2 — P1 Ingestion（Vision 整份解析與元數據）`。
   - 將下一個 Commit 標記為 🟡 WIP：`- 🟡 WIP: C3 — P2 Glossary & Context Prep（四步循序自癒）`。

2. **歷史已提交 Hash 掃描與自愈回填**：
   - 執行 `git log` 讀取 Git 歷史紀錄，查出所有先前已完成任務但仍為 `待 baron 回填` 佔位符的真實 Commit Hash。
   - 自動將 `TODO.md` 中所有 `待 baron 回填` 佔位符替換為讀取出的真實 Git Commit Hash，保持 Single Source of Truth 的物理對齊與歷史自癒。

### 📁 產出規格

- **執行報告路徑**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C2_執行.md`（暫存於 `baton/`，**不併入 Git 版本控管**）
- **套用模板**：`.claude-logs/templates/template_execution.md`
- **命名格式**：依 `.claude-logs/ref/WORKFLOW_SOP.md §6 命名規則`

執行報告必須包含：
- 頂部元數據塊（任務代號 / 執行日期 / 依據規劃 / 次級參考 / hash 留空 / 狀態）
- §1 基準與完成狀態
- §2 Commit 表格
- §3 變動檔案清單（含備份路徑，注意 `baton/` 暫存報告與備份檔嚴禁寫入 Git）
- §4 修法說明（附關鍵代碼片段與註解包裝範圍）
- §5 測試結果（貼上真實終端輸出）
- §6 不可動清單遵守
- §7 銜接（baton 狀態為暫存於 baton/ 不入版控 + 下一步指向 C3）
- **§8 baron 執行命令**（見下方格式要求）

### 📝 §8 baron 執行命令格式要求

在執行報告的 `## §8 baron 執行命令` 中，必須提供：

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C2 新增與修改的程式碼與測試檔，暫存的執行報告與備份檔嚴禁加入）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C2_resume_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C2_msg.txt）
cat > /tmp/PIPE-RESUME_C2_msg.txt << 'EOF'
BE-Refactor: PIPE-RESUME C2 — P1 Ingestion（Vision 整份解析與元數據）

實作 run_phase1：呼叫 ResumeProcessor Vision 核心進行整份渲染解析與去浮水印，抽取 candidate_name 映射為 title，構建 IngestionMetadataSpec 交付，並暫存 phone/email/domain 於策略實例以供 interim 穿線。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C2_msg.txt
```

---

### 🛑 停止指令

**產出 `C2_執行.md` 後必須立即停止所有工具呼叫與代碼修改。**

嚴禁：
- ❌ 繼續執行下一個 Commit/OP（必須等 baron 確認後另行下達提示詞）
- ❌ 修改任何未列入本 Commit §8 實作細節的代碼或文件
- ❌ 自發執行 `git commit` 或 `git push`
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`pipelines/resume_pipeline.py` `run_phase1` 實作（複用 ResumeProcessor Vision 核心 + 建 IngestionMetadataSpec + `_raw_meta` 暫存 phone/email/domain）
- 測試：§6.2 grep 驗收 + P1 契約測試（title=candidate_name、無 Abstract/LCC/Glossary）+ 既有套件全綠
- 報告：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C2_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 `/tmp/PIPE-RESUME_C2_msg.txt`、baron 手動）

## 後續引用

承 C1（骨架註冊）。本階段 C2 實作 P1；下一步 C3 P2 Glossary & Context Prep 由 baron 另行下達。
`````
