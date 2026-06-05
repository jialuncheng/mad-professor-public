`````markdown
# 2026-06-05 — PIPE-RESUME C2 Run（P1 + Context）提示詞

> **收到時間**：2026-06-05 10:07（UTC+8）
> **任務代號**：PIPE-RESUME C2（v9 整合批次）
> **觸發 commit**：C2（raw_metadata 基建欄 + run_phase1 寫入 + 影子後綴）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C2_執行.md`
> **觸發情境**：baron 確認 C1（三規格同步）後下達 C2——`pipelines/context.py` 加 `raw_metadata` 欄；`resume_pipeline.py run_phase1` 寫 `ctx.raw_metadata`（過渡期保留 `self._raw_meta` 雙寫供 P2）+ `_shadow` 時 title 加綴 `(測試)`；`# === [PIPE-RESUME v9 C2 START/END] ===` 包裹。執行報告不入 Git；產報告 + TODO（C2 ✅ / C3 WIP）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 10:07` |
| **任務代號** | `PIPE-RESUME C2` |
| **觸發 Commit** | `C2` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | `baron 確認 C1 Commit 後，下達 C2 執行指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_C2_run_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，執行單一 Commit C2。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C2 / 工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令
依 tasks §8 C2：
1. 物理防線：僅改 `pipelines/context.py` 與 `pipelines/resume_pipeline.py`(P1 段)；嚴禁越界。
2. context.py：`PipelineContext` 加 `raw_metadata: Dict[str, Any] = {}`。
3. resume_pipeline.py run_phase1：① 結束前將整包 meta（candidate_name/domain/phone/email + confidence/source）寫 `ctx.raw_metadata`；② 過渡期雙寫——保留 `self._raw_meta` 寫入（P2 仍可讀、獨立可逆）；③ 影子後綴——title 解出後若 `ctx.paper_id.endswith('_shadow')` → `f"{title} (測試)"`。
4. `# === [PIPE-RESUME v9 C2 START/END] ===` 包裹。
5. Git 控制：執行報告暫存 baton/、不入 Git（嚴禁 git add 報告/plan/tasks）。

### 💾 備份規則
cp context.py / resume_pipeline.py → `.claude-logs/archive/2026-06-05_PIPE-RESUME_C2_{context.py,resume_pipeline.py}.bak`

### 🔄 同步更新 TODO.md
C2 → ✅（待 baron 回填）；C3 → 🟡 WIP。（不用給 commit 建議、無 Hash 自癒掃描。）

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-05_PIPE-RESUME_C2_執行.md`；套用 template_execution。

### 📝 §8 baron 執行命令與 msg
msg 寫 `/tmp/PIPE-RESUME_C2_msg.txt`；§8 git add 僅 code（context+resume_pipeline）+ .bak + TODO + prompts（執行報告本體不 add）；baron 手動 commit。

### 🛑 停止指令
產 C2_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列檔案 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`context.py` 加 `raw_metadata` 欄；`run_phase1` 寫 ctx.raw_metadata（雙寫 self._raw_meta）+ _shadow title 加綴
- 測試：grep 驗收 + 既有套件防 Regression（含 test_pipe_core/scaffold）
- 報告：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C2_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C1（三規格同步）。本 C2 落地 raw_metadata 基建欄 + P1 寫入 + 影子後綴；下一步 C3 P2 步序與讀取對齊由 baron 另行下達。
`````
