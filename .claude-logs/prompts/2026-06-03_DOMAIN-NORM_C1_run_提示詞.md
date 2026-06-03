`````markdown
# 2026-06-03 — DOMAIN-NORM C1 Run 提示詞

> **收到時間**：2026-06-03 18:11（UTC+8）
> **任務代號**：DOMAIN-NORM C1
> **觸發 commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-06-03_DOMAIN-NORM_C1_執行.md`
> **觸發情境**：baron 確認 tasks 拆分後，下達 C1 執行指令——`models.py` 新增 `Domains`（lcc_code PK + name 動態註冊）+ `DomainMapping`（raw→lcc 快取）兩表；`Paper` 等既有表不動；`=== [DOMAIN-NORM C1 START/END] ===` 包裹；改前 `.bak`。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-03 18:11 |
| **任務代號** | DOMAIN-NORM C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` |
| **觸發情境** | baron 確認 tasks 拆分後，下達 C1 執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）
1. 寫入 `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_C1_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C1。
### 📋 任務資訊
- 任務編碼 `DOMAIN-NORM`｜當前 Commit `C1`｜工作流 `BE-Refactor`
- Tasks 路徑 `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / DOMAIN-NORM tasks / database_SOP / logging_SOP
### 🛠️ 執行命令（四防線）
1. 代碼包裝標籤：`# === [DOMAIN-NORM C1 START] ===` / `# === [DOMAIN-NORM C1 END] ===`。
2. 物理防線：`models.py` 既有 `Paper` 表/關係嚴禁改，僅可新增 `Domains` / `DomainMapping`。
3. 測試防線：執行 §6.1 驗收 grep + python-import 檢測。
4. 文件防線：commit/push 由 baron 手動。
### 💾 備份規則
`cp models.py .claude-logs/archive/2026-06-03_DOMAIN-NORM_C1_models.py.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C1 → ✅；C2 → 🟡 WIP。
2. git log 掃描 + 自癒回填所有「待 baron 回填」佔位符為真實 Hash。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-03_DOMAIN-NORM_C1_執行.md`（套 template_execution，§1-§8）。
### 📝 §8 baron 執行命令格式
git add models.py + .bak（明確列檔、報告留 baton 不 add）；msg 草稿 /tmp/DOMAIN-NORM_C1_msg.txt。
### 🛑 停止指令
產出 C1_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- pytest baseline → final：新表 import + create_all 驗證（見 C1_執行.md §5）
- 改動檔案數：`models.py`（+2 表）+ `.bak` 備份；新增 C1_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 DOMAIN-NORM tasks §8 C1。C2（Normalizer Core）由 baron 後續獨立提示詞觸發。
`````
