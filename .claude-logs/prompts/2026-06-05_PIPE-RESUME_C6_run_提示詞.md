`````markdown
# 2026-06-05 — PIPE-RESUME C6 Run（Unit Tests）提示詞

> **收到時間**：2026-06-05 10:51（UTC+8）
> **任務代號**：PIPE-RESUME C6（v9 整合批次）
> **觸發 commit**：C6（v9 契約單元測試與紅燈修復）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C6_執行.md`
> **觸發情境**：baron 確認 C5 後下達 C6——僅改 `tests/test_resume_pipeline.py`：①修復 C3 遺留 `_raw_meta` 紅燈（改對 `ctx.raw_metadata`）②追加 v9 契約測試（P1 raw_metadata 寫入+影子後綴 / P2 摘要先行步序+LCC 讀 raw_metadata fallback general / P3 constraints 注入 / C5 影子寫庫保真）。`# === [PIPE-RESUME v9 C6 START/END] ===` 包裹。執行報告不入 Git；產報告 + TODO（C6 ✅ / C7 WIP）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 10:51` |
| **任務代號** | `PIPE-RESUME C6` |
| **觸發 Commit** | `C6` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | `baron 確認 C5 Commit 後，下達 C6 執行指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_C6_run_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，執行單一 Commit C6。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C6 / 工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令
依 tasks §8 C6：
1. 物理防線：僅改 `tests/test_resume_pipeline.py`；嚴禁動 pipelines/ 或業務代碼。
2. 修復 C3 遺留紅燈：原對廢除 `self._raw_meta` 的斷言/設定（test_run_phase1_contract、test_run_phase2_flag_off）→ 改對 `ctx.raw_metadata`，恢復核心 pipelines/resume 測試全綠。
3. 追加 v9 契約新測試：① P1 raw_metadata 寫入 + 影子後綴 (測試)；② P2 摘要先行步序 + LCC raw_domain 讀 raw_metadata 且空值 fallback general；③ P3 constraints 注入履歷專屬約束；④ C5 影子寫庫 meta_dict 含完整 raw_metadata + 繼承 (測試)。
4. `# === [PIPE-RESUME v9 C6 START/END] ===` 包裹。
5. Git 控制：執行報告暫存 baton/、不入 Git。

### 💾 備份規則
cp tests/test_resume_pipeline.py → `.claude-logs/archive/2026-06-05_PIPE-RESUME_C6_test_resume_pipeline.py.bak`

### 🔄 同步更新 TODO.md
C6 → ✅（待 baron 回填）；C7 → 🟡 WIP（Checkout）。（不用給 commit 建議、無 Hash 自癒掃描。）

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-05_PIPE-RESUME_C6_執行.md`；套用 template_execution。

### 📝 §8 baron 執行命令與 msg
msg 寫 `/tmp/PIPE-RESUME_C6_msg.txt`；§8 git add 僅 code + .bak + TODO + prompts（執行報告本體不 add）；baron 手動 commit。

### 🛑 停止指令
產 C6_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列檔案 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：tests/test_resume_pipeline.py 修復 2 個 _raw_meta 紅燈（改 ctx.raw_metadata）+ 追加 v9 契約測試（P1 影子後綴 / P2 摘要先行 / P3 constraints / C5 影子寫庫保真）
- 測試：核心 pipelines/resume 套件恢復全綠
- 報告：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C6_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C5（影子寫庫保真）。本 C6 落地 v9 契約測試與紅燈修復；下一步 C7 Checkout 收官歸檔由 baron 另行下達。
`````
