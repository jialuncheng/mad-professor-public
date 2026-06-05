`````markdown
# 2026-06-05 — PIPE-RESUME C5 Run（Shadow DB Fidelity）提示詞

> **收到時間**：2026-06-05 10:31（UTC+8）
> **任務代號**：PIPE-RESUME C5（v9 整合批次）
> **觸發 commit**：C5（影子寫庫讀 raw_metadata 保真）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C5_執行.md`
> **觸發情境**：baron 確認 C4 後下達 C5——`web_server.py` `run_pipeline_shadow` C8-hotfix 影子寫庫改由 `ctx.raw_metadata` 組整包 `metadata_json`（對齊 A 軌保真）；title 沿用 P1 已加綴 (測試) 的 `ctx.ingestion.title`；`ctx.raw_metadata` 空則防禦性 fallback 最小 meta_dict；僅呼叫既有 `upsert_paper`（無裸 commit）；`# === [PIPE-RESUME v9 C5 START/END] ===` 包裹（疊於 C8-hotfix 內）。執行報告不入 Git；產報告 + TODO（C5 ✅ / C6 WIP）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 10:31` |
| **任務代號** | `PIPE-RESUME C5` |
| **觸發 Commit** | `C5` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | `baron 確認 C4 Commit 後，下達 C5 執行指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_C5_run_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，執行單一 Commit C5。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C5 / 工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令
依 tasks §8 C5：
1. 物理防線：僅改 `web_server.py` `run_pipeline_shadow` 的 C8-hotfix 影子寫庫區塊；嚴禁動 A 軌。
2. 影子寫庫保真：① meta_dict 改優先讀 `ctx.raw_metadata` 整包組 metadata_json；② title 沿用 `ctx.ingestion.title`（已自帶 (測試)）；③ ctx.raw_metadata 空 → 防禦性 fallback 原最小 meta_dict 補 title。
3. `# === [PIPE-RESUME v9 C5 START/END] ===` 包裹（疊於 C8-hotfix 內）。
4. database SOP：僅呼叫既有 `upsert_paper`（內部自管交易）；嚴禁裸 commit/SessionLocal().begin()。
5. Git 控制：執行報告暫存 baton/、不入 Git。

### 💾 備份規則
cp web_server.py → `.claude-logs/archive/2026-06-05_PIPE-RESUME_C5_web_server.py.bak`

### 🔄 同步更新 TODO.md
C5 → ✅（待 baron 回填）；C6 → 🟡 WIP。（不用給 commit 建議、無 Hash 自癒掃描。）

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-05_PIPE-RESUME_C5_執行.md`；套用 template_execution。

### 📝 §8 baron 執行命令與 msg
msg 寫 `/tmp/PIPE-RESUME_C5_msg.txt`；§8 git add 僅 code + .bak + TODO + prompts（執行報告本體不 add）；baron 手動 commit。

### 🛑 停止指令
產 C5_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列檔案 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`run_pipeline_shadow` C8-hotfix 區塊改讀 ctx.raw_metadata 組 metadata_json + title 沿用 + fallback
- 測試：grep 驗收 + SOP（無裸 commit）+ test_pipe_scaffold + 既有套件（C3 的 2 紅燈仍在、待 C6）
- 報告：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C5_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C4（P3 constraints）。本 C5 落地影子寫庫保真（消費 C2 的 ctx.raw_metadata）；下一步 C6 單元測試（修 C3 的 2 紅燈）由 baron 另行下達。
`````
