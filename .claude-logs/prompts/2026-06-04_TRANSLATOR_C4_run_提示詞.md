`````markdown
# 2026-06-04 — TRANSLATOR C4 Run 提示詞

> **收到時間**：2026-06-04 14:19（UTC+8）
> **任務代號**：TRANSLATOR C4
> **觸發 commit**：C4
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_TRANSLATOR_C4_執行.md`
> **觸發情境**：baron 確認 C3 後，下達 C4 執行指令——`processor/translator.py` `translate()` 末加 U4 多行 `re.sub` 分行兜底（原文行數 > 譯文行數時按句號重分行）；新建 `tests/test_translator.py` 8 測試（normal/deep_think/style_hints/prompt_file_routing/lcc_domain_injection/glossary_injection/formatting_fallback/user_prompt_references）；C4 標記包裹、改前 .bak。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-06-04 14:19 |
| **任務代號** | TRANSLATOR C4 |
| **觸發 Commit** | C4 |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` |
| **觸發情境** | baron 確認上一個 Commit 後，下達本次執行指令 |
---
## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
1. 寫入 `.claude-logs/prompts/2026-06-04_TRANSLATOR_C4_run_提示詞.md`（README §3）。
2. 更新 INDEX.md（分類 + 時間排序首行，超 15 筆刪最舊）。
3. 回覆「✅ 提示詞已歸檔：<路徑>」後繼續。
---
你現在扮演 **Claude Code**，執行單一 Commit C4。
### 📋 任務資訊
- 任務編碼 TRANSLATOR｜當前 Commit C4｜工作流 BE-Refactor
- Tasks `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md`
### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP / framework / TRANSLATOR tasks §8 C4 / database_SOP
### 🛠️ 執行命令與標記規則（四防線）
1. 物理防線：§7 不可動逐項確認、不越界。
2. 測試防線：`pytest tests/test_translator.py -v` 8 綠 + 全套件零迴歸。
3. 註記包裝：改既有檔處 `# === [TRANSLATOR C4 START/END] ===` 包裹。
4. 文件防線：commit/push 由 baron 手動。
### 💾 備份規則
`cp processor/translator.py .claude-logs/archive/2026-06-04_TRANSLATOR_C4_translator.py.bak`
### 🔄 同步更新 TODO.md（必做、即時）
1. C4 → ✅；C5 → 🟡 WIP。
2. git log 掃描 + 自癒回填「待 baron 回填」佔位符。
### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-04_TRANSLATOR_C4_執行.md`（套 template_execution，§1-§8、baton 不入 git）。
### 📝 §8 baron 執行命令格式
git add translator.py + tests/test_translator.py + .bak + TODO + 提示詞 + INDEX（明確列檔、baton 報告不 add）；msg /tmp/TRANSLATOR_C4_msg.txt。
### 🛑 停止指令
產出 C4_執行.md 後立即停止；嚴禁續執行下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 改動檔案數：`processor/translator.py`（+U4 分行兜底）+ 新建 `tests/test_translator.py`（8 測試）+ .bak；修改 TODO.md；新增 C4_執行.md（baton/）
- 是否 commit / push：否（依 CLAUDE.md §1.3，baron 手動執行）

## 後續引用

依據 TRANSLATOR tasks §8 C4。C5（Checkout & Clean 收官）由 baron 後續獨立提示詞觸發。
`````
