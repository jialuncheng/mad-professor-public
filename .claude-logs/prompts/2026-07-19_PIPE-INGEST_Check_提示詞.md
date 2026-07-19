# PIPE-INGEST Check（Conformance 驗收與 Checkout 收官）提示詞

### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-19 20:46 |
| **任務代號** | PIPE-INGEST Check |
| **觸發 Commit** | PIPE-INGEST-Check |
| **相關產出檔案** | 所有執行報告路徑（見下方清單） |
| **觸發情境** | 所有 Commit ship 完畢，baron 下達 Conformance 驗收與 Checkout 收官指令 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

1. 寫入提示詞歸檔檔：`.claude-logs/prompts/2026-07-19_PIPE-INGEST_Check_提示詞.md`（格式依 prompts/README.md §3）。
2. 更新 INDEX.md（對應分類補登 + 依時間排序首行插入、超過 15 筆刪最舊）。
3. 歸檔成功後回覆確認、繼續後續步驟。

---

你現在扮演 **Claude Code**，請對以下任務執行 Conformance 驗收，並在全部合規後執行收官歸檔與 Checkout 動作。

### 📋 任務資訊

- **任務編碼**：`PIPE-INGEST`
- **Plan 路徑**：`.claude-logs/baton/2026-07-18_PIPE-INGEST_litedoc攝入自有化與品質根治_plan.md`
- **Tasks 路徑**：`.claude-logs/baton/2026-07-19_PIPE-INGEST_litedoc攝入自有化與品質根治_tasks.md`
- **執行報告清單**：baton/ 之 C1/C2/C3 執行報告三份

### 📖 強制讀檔清單

CLAUDE.md / WORKFLOW_SOP.md / TODO.md（自動載入）+ plan + tasks + C1/C2/C3 執行報告

### 🏢 工作目錄硬規則

- 唯一合法工作目錄：主 repo 根目錄 `~/mad-professor-public/`（CLAUDE.md §3 唯一權威源）

### ✅ Conformance 驗收流程

第一步：產出 Conformance 驗收報告（目標規格〔純結構化定位項目對照〕/ 測試計畫驗收條件 / 不可動清單 / 提示詞歸檔狀態交叉核對；表格依 template_prompt_for_check.md 第二步格式）。
提示詞歸檔稽核：`ls .claude-logs/prompts/ | grep "PIPE-INGEST"` 確認 tasks、C1-C3 run、Check 共 5 份俱在。

### 🗃️ 收官自動化動作（全部合規後才執行）

第一步：更新 TODO.md 與雙源 Hash 自癒補填（archive 追加完成表格 / git log -n 10 取 C1-C3 真實 hash / 索引行 pointer + 佔位符全替換 / active 條目移除 + 類別索引更新）。
第二步：搬移歸檔 baton/ 暫存文件（plan → plans/、tasks → tasks/、C1-C3 執行報告 → executions/）。
第三步：`ls .claude-logs/baton/` 確認除未落地影子 PDF 外無本案殘留。
第四步：檢查 prompts/ 下本任務 5 份提示詞與 INDEX.md 納入 git add。
第五步：staged 自檢與 checkout 報告產出（executions/2026-07-19_PIPE-INGEST_checkout_執行.md、輕量格式、註明 Conformance 通過 + §7.2 整合測試存在且通過；`git diff --cached --name-only` 自檢暫存集合＝宣告清單、剔除影子 PDF 等無關檔案）。
第六步：產生 `/tmp/PIPE-INGEST_checkout_msg.txt` 並展示於報告 §8。

### 📝 §8 baron 執行命令格式要求

git add 歸檔清單（逐檔顯式列名：plan/tasks/4 執行報告/5 prompts/INDEX.md/4 .bak/TODO.md/archive 歸檔檔）+ commit message 草稿 + baron 手動 `git commit -F /tmp/PIPE-INGEST_checkout_msg.txt`。

### 🛑 停止指令

產出 checkout_執行.md 後立即停止。嚴禁自發 git commit / push、嚴禁修改已歸檔正式歷史文件。
