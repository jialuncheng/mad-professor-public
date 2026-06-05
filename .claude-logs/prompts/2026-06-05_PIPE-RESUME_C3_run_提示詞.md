`````markdown
# 2026-06-05 — PIPE-RESUME C3 Run（P2 步序與讀取對齊）提示詞

> **收到時間**：2026-06-05 10:14（UTC+8）
> **任務代號**：PIPE-RESUME C3（v9 整合批次）
> **觸發 commit**：C3（①②互換 + 改讀 raw_metadata + 廢 self._raw_meta）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C3_執行.md`
> **觸發情境**：baron 確認 C2 後下達 C3——`run_phase2` 步序改①做摘要→②LCC（摘要先行）；`raw_domain` 改讀 `ctx.raw_metadata.get("domain")`；廢除 `self._raw_meta`（__init__ + run_phase1 雙寫一併移除、以 ctx.raw_metadata 為唯一載體）；`# === [PIPE-RESUME v9 C3 START/END] ===` 包裹。執行報告不入 Git；產報告 + TODO（C3 ✅ / C4 WIP）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 10:14` |
| **任務代號** | `PIPE-RESUME C3` |
| **觸發 Commit** | `C3` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | `baron 確認 C2 Commit 後，下達 C3 執行指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_C3_run_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，執行單一 Commit C3。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C3 / 工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令
依 tasks §8 C3：
1. 物理防線：僅改 `pipelines/resume_pipeline.py`（P2 段 + 初始化）；嚴禁越界。
2. run_phase2 步序互換：①做摘要（前置於 normalize_to_lcc）→ ②LCC 分類。
3. 改讀 raw_metadata：`raw_domain` 改 `ctx.raw_metadata.get("domain")`。
4. 廢除 self._raw_meta：移除 __init__ 與 run_phase1 的實例暫存雙寫（以 ctx.raw_metadata 為唯一載體）。
5. `# === [PIPE-RESUME v9 C3 START/END] ===` 包裹。
6. Git 控制：執行報告暫存 baton/、不入 Git。

### 💾 備份規則
cp resume_pipeline.py → `.claude-logs/archive/2026-06-05_PIPE-RESUME_C3_resume_pipeline.py.bak`

### 🔄 同步更新 TODO.md
C3 → ✅（待 baron 回填）；C4 → 🟡 WIP。（不用給 commit 建議、無 Hash 自癒掃描。）

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-05_PIPE-RESUME_C3_執行.md`；套用 template_execution。

### 📝 §8 baron 執行命令與 msg
msg 寫 `/tmp/PIPE-RESUME_C3_msg.txt`；§8 git add 僅 code + .bak + TODO + prompts（執行報告本體不 add）；baron 手動 commit。

### 🛑 停止指令
產 C3_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列檔案 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`run_phase2` ①摘要→②LCC 互換 + raw_domain 改讀 ctx.raw_metadata + 廢 self._raw_meta（__init__ + run_phase1）
- 測試：grep 驗收 + 既有套件防 Regression
- 報告：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C3_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C2（raw_metadata 基建 + 雙寫）。本 C3 完成 P2 步序統一 + 讀取切換 + 雙寫收斂；下一步 C4 P3 constraints 由 baron 另行下達。
`````
