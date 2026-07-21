# PIPE-SYNC-5 C1 Run 階段提示詞

- **歸檔日期**：2026-07-21
- **任務**：PIPE-SYNC-5（PIPE-INGEST＋GLOSSARY-TERMMAP 回灌母 plan/PIPE-SPEC + F7 門檻更正）
- **階段**：階段 4（執行 C1 — Spec & Plan Backfill）
- **來源**：baron 結構化提示詞
- **⚠️ 拆分覆寫**：本 C1 提示詞將 tasks.md 之 C1（PIPE-SPEC）/ C2（母 plan + design spec）**合併為單一 C1**（三份文件一次回灌）、C1→checkout 直達（無 C2）；baron 為 authority、依本提示詞執行。

---

## 提示詞原文

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-21 10:18 |
| **任務代號** | PIPE-SYNC-5 C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md` |
| **觸發情境** | baron 確認上一個 任務/Tasks 後，下達本次執行指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：呼叫寫檔工具，將本次對話的完整提示詞（含元數據塊與全部正文）寫入：
   `.claude-logs/prompts/2026-07-21_PIPE-SYNC-5_C1_run_提示詞.md`
   格式嚴格依 `.claude-logs/prompts/README.md §3 檔案格式`。

2. **更新 INDEX.md**：在 `.claude-logs/prompts/INDEX.md` 的對應分類下補登新條目，並在 `## 依時間排序` 首行插入新條目，超過 15 筆則刪除最舊一筆。

3. **確認完成後繼續**：歸檔成功後，在此回覆「✅ 提示詞已歸檔：`.claude-logs/prompts/2026-07-21_PIPE-SYNC-5_C1_run_提示詞.md`」，然後繼續執行後續步驟。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit/OP。

### 📋 任務資訊

- **任務編碼**：`PIPE-SYNC-5`
- **當前 Commit 代號**：`C1`
- **工作流類別**：`DOC-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-21_PIPE-SYNC-5_PIPE-INGEST與GLOSSARY-TERMMAP回灌母plan與SPEC_tasks.md`

### 📖 強制讀檔清單

```
CLAUDE.md
.claude-logs/ref/WORKFLOW_SOP.md
.claude-logs/baton/2026-07-21_PIPE-SYNC-5_..._plan.md
.claude-logs/baton/2026-07-21_PIPE-SYNC-5_..._tasks.md
.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md
.claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md
.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md
.claude-logs/sop/2026-05-23_logging_SOP_手冊.md
.claude-logs/sop/2026-05-23_database_SOP_手冊.md
```

### 🏢 工作目錄硬規則

- **唯一合法工作目錄**：主 repo 根目錄 `~/mad-professor-public/`。

### 🛠️ 執行命令（防線）

1. **物理防線**：嚴禁動 `pipelines/`/`processor/` 業務代碼與測試；嚴禁改 PIPE-SPEC §1.1 四凍結合約與 §1.2.1/§1.2.3/§1.2.4/§1.2.5 本體（僅增 §1.2.6 + roster）；design spec 僅更正規則①作廢門檻、脈絡不動；全部增修 `<!-- [PIPE-SYNC-5 Dn] -->` ~ `<!-- [PIPE-SYNC-5 Dn END] -->` 包裹。
2. **測試防線**：`pytest tests/` 920 passed 防呆；grep 驗收（ingestion_engine/build_termmap 已寫入 SPEC；design spec MIN_LONG_SIDE/200k 已除、100k 已補）；貼 §6.2 SOP 核查。
3. **文件防線**：執行報告與 plan/tasks 為 baton 暫存、嚴禁 mv/git add；commit 由 baron 手動。

### 💾 備份規則（修改前先備份）

```bash
cp .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_specification.md.bak
cp .claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_plan_v10.md.bak
cp .claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_design_spec.md.bak
```

### 🔄 同步更新 TODO.md 狀態與歷史 Hash 自癒回填

1. C1 → ✅、checkout → 🟡 WIP。
2. `git log` 掃描、雙源（TODO.md + archive/TODO_done_archive.md）`待 baron 回填` 佔位符替換為真實 hash。

### 📁 產出規格

- **執行報告**：`.claude-logs/baton/2026-07-21_PIPE-SYNC-5_C1_執行.md`（暫存 baton）；套用 template_execution.md。
- 含元數據塊（Completed (Commit C1)、hash 留空）/ §1 基準 / §2 Commit 表 / §3 變動檔案（3 文件 + 3 .bak；baton 報告不列 git add）/ §4 說明（ingestion_engine 契約/build_termmap 規格/F7 門檻）/ §5 測試與 Grep / §6 不可動 / §7 銜接（→ checkout）/ §8 baron 執行命令。

### 📝 §8 baron 執行命令格式

```bash
# 2. git add 清單（逐檔顯式列名，嚴禁 git add . / -A / <目錄>）
git add .claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md
git add .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_specification.md.bak
git add .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_plan_v10.md.bak
git add .claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_design_spec.md.bak

# 3. commit message draft（已寫入 /tmp/PIPE-SYNC-5_C1_msg.txt）
cat > /tmp/PIPE-SYNC-5_C1_msg.txt << 'EOF'
DOC-Refactor: PIPE-SYNC-5 C1 — Spec & Plan Backfill（規格書與母計畫回灌）

1. 回灌 PIPE-INGEST 與 GLOSSARY-TERMMAP 落地規格：於 PIPE-SPEC 補登 §1.2.6 ingestion_engine 契約（家族第 6 員）、於 §1.2.2 補 build_termmap 事前定案 builder 演算法與術語 align 預設開關、 roster 增列。
2. 同步回灌母 plan v10：更新 U8 家族成員 Roster 與 U7 LiteDoc 管線描述，於 §8.5 進度表將 PIPE-INGEST/GLOSSARY-TERMMAP/IMG-FILTER 三案標記為 ✅。
3. 修正 design_spec F7 門檻值：廢除長邊軸判定，將規則 ① 尺寸門檻更新為實測校正後之面積比對（area < 100000），並加註 size-filter 演進說明。
4. 全量增修使用 HTML 註解 `<!-- [PIPE-SYNC-5 Dn] -->` 進行可追溯性標記。
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-SYNC-5_C1_msg.txt
```

---

### 🛑 停止指令

產出 `2026-07-21_PIPE-SYNC-5_C1_執行.md` 並更新 TODO.md 後必須立即停止。嚴禁繼續 checkout、改未列入文件、自發 commit/push。
