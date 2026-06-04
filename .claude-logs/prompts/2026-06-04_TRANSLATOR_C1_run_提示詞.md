`````markdown
# 2026-06-04 — TRANSLATOR C1 Run 提示詞

> **收到時間**：2026-06-04 13:37（UTC+8）
> **任務代號**：TRANSLATOR C1
> **觸發 commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_TRANSLATOR_C1_執行.md`
> **觸發情境**：baron 確認 tasks 拆分後，下達 C1 執行指令——新建 `processor/translator.py` 定義 `InjectionContext`（7 欄 frozen+forbid）+ `TranslateMode`（NORMAL/DEEP_THINK）；`pipelines/contracts.py::GlossaryReadySpec` 補 `domain_name`（C1 標記包裹、改前 .bak）。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 13:37 |
| **任務代號** | TRANSLATOR C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_TRANSLATOR_C1_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C1。
### 📋 任務資訊
- 任務編碼 TRANSLATOR｜當前 Commit C1｜工作流 BE-Refactor
- Tasks `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / framework / TRANSLATOR tasks §8 C1 / database_SOP
### 🛠️ 執行命令與標記規則（四防線）
1. 物理防線：§7 不可動清單逐項確認、不越界。
2. 測試防線：執行 §6.1 C1 驗收 grep + import 檢測。
3. 註記包裝：改既有檔處 `# === [TRANSLATOR C1 START/END] ===` 包裹。
4. 文件防線：commit/push 由 baron 手動。
### 💾 備份規則
`cp pipelines/contracts.py .claude-logs/archive/2026-06-04_TRANSLATOR_C1_contracts.py.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C1 → ✅；C2 → 🟡 WIP。
2. git log 掃描 + 自癒回填所有「待 baron 回填」佔位符為真實 Hash。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-04_TRANSLATOR_C1_執行.md`（套 template_execution，§1-§8、baton 不入 git）。
### 📝 §8 baron 執行命令格式
git add pipelines/contracts.py + .bak（明確列檔、baton 報告不 add）；msg 草稿 /tmp/TRANSLATOR_C1_msg.txt。
### 🛑 停止指令
產出 C1_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：新增 `processor/translator.py`（InjectionContext+TranslateMode）；修改 `pipelines/contracts.py`（GlossaryReadySpec +domain_name）+ .bak；新增 C1_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 TRANSLATOR tasks §8 C1。C2（Prompt Engine）由 baron 後續獨立提示詞觸發。
`````
