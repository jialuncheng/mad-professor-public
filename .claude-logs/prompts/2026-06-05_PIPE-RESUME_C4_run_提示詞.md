`````markdown
# 2026-06-05 — PIPE-RESUME C4 Run（P3 Business Constraints）提示詞

> **收到時間**：2026-06-05 10:22（UTC+8）
> **任務代號**：PIPE-RESUME C4（v9 整合批次）
> **觸發 commit**：C4（P3 業務規則 constraints 注入）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C4_執行.md`
> **觸發情境**：baron 確認 C3 後下達 C4——`resume_pipeline.py` 新增模組常數 `_RESUME_CONSTRAINTS`（公司/產品名保留、Email/電話/URL 原樣、技能詞英文、專利/期刊原文+對照）；`run_phase3` 的 `InjectionContext` 加 `constraints=_RESUME_CONSTRAINTS`（共用 Translator 自動貼「【額外譯文約束】」）；`# === [PIPE-RESUME v9 C4 START/END] ===` 包裹。執行報告不入 Git；產報告 + TODO（C4 ✅ / C5 WIP）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 10:22` |
| **任務代號** | `PIPE-RESUME C4` |
| **觸發 Commit** | `C4` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | `baron 確認 C3 Commit 後，下達 C4 執行指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_C4_run_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，執行單一 Commit C4。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C4 / 工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令
依 tasks §8 C4：
1. 物理防線：僅改 `pipelines/resume_pipeline.py`（P3 段 + 常數宣告）；嚴禁越界。
2. 新增模組常數 `_RESUME_CONSTRAINTS = ["公司名稱、產品名稱保留原文不翻","Email／電話／URL 原樣保留","專業技能詞（Python/Docker 等）保留英文","專有名詞（如專利、期刊等名稱）保留原文並在中譯中附加對照"]`。
3. run_phase3 的 InjectionContext 加 `constraints=_RESUME_CONSTRAINTS`。
4. `# === [PIPE-RESUME v9 C4 START/END] ===` 包裹。
5. Git 控制：執行報告暫存 baton/、不入 Git。

### 💾 備份規則
cp resume_pipeline.py → `.claude-logs/archive/2026-06-05_PIPE-RESUME_C4_resume_pipeline.py.bak`

### 🔄 同步更新 TODO.md
C4 → ✅（待 baron 回填）；C5 → 🟡 WIP。（不用給 commit 建議、無 Hash 自癒掃描。）

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-05_PIPE-RESUME_C4_執行.md`；套用 template_execution。

### 📝 §8 baron 執行命令與 msg
msg 寫 `/tmp/PIPE-RESUME_C4_msg.txt`；§8 git add 僅 code + .bak + TODO + prompts（執行報告本體不 add）；baron 手動 commit。

### 🛑 停止指令
產 C4_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列檔案 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`_RESUME_CONSTRAINTS` 常數 + run_phase3 InjectionContext 加 constraints
- 測試：grep 驗收 + 既有套件防 Regression（C3 的 2 計畫內紅燈仍在、待 C6 修）
- 報告：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C4_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C3（P2 步序與讀取）。本 C4 落地 P3 業務規則 constraints；下一步 C5 影子寫庫保真由 baron 另行下達。
`````
