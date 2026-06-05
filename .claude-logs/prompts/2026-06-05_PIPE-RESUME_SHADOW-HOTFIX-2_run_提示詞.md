`````markdown
# 2026-06-05 — PIPE-RESUME SHADOW-HOTFIX-2 Run 提示詞

> **收到時間**：2026-06-05 16:40（UTC+8）
> **任務代號**：PIPE-RESUME SHADOW-HOTFIX-2（BE-Hotfix）
> **觸發 commit**：SHADOW-HOTFIX-2（影子標題 (測試) + 履歷公司名翻譯）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_執行.md`
> **⚠️ 執行狀態：HALTED（未落地）**——本 Run 提示詞與**現行已核准的 hotfix.md（3 處「移除矛盾」版）相矛盾**：提示詞 §2 要求改 `processor/translate_processor.py`（A 軌、對 B 軌無效）並採「加翻譯規則」舊法（v1），而 hotfix.md 已定為改 `translator.py:40` + `resume_pipeline.py:109`（B 軌）採「移除矛盾、交回母提示詞」（v2）。已停下、向 baron 呈報待裁示，未動任何業務代碼。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 16:40 |
| 任務代號 | PIPE-RESUME SHADOW-HOTFIX-2 |
| 觸發 Commit | SHADOW-HOTFIX-2 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_hotfix.md |
| 觸發情境 | baron 確認上一個 Commit 與熱修復規劃後，下達本次執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_run_提示詞.md + 更新 INDEX。

你現在扮演 Claude Code，執行單一 BE-Hotfix SHADOW-HOTFIX-2。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / SHADOW-HOTFIX-2_hotfix.md / logging_SOP / database_SOP

### 執行命令
1. web_server.py 影子寫庫區塊：translated_title 尾端加 (測試)（`# === [PIPE-RESUME SHADOW-HOTFIX-2 START/END] ===` 包裹）。
2. processor/translate_processor.py：style_hints['resume'] 改為「公司名與機構名翻譯後附英文原文（例：視彩光電 (VIEWTRIX TECHNOLOGY)）」（同標記包裹）。
3. 物理防線：僅改 web_server.py 與 processor/translate_processor.py。
4. 測試：orb venv/bin/pytest tests/test_resume_pipeline.py tests/test_resume_processor.py -v（33 passed）；logging/database grep 核查。

### 備份
cp web_server.py / processor/translate_processor.py → archive/*.bak

### TODO 同步
SHADOW-HOTFIX-2 → ✅；掃描回填所有「待 baron 回填」hash。

### 產出與歸檔
執行報告 baton/2026-06-05_PIPE-RESUME_SHADOW-HOTFIX-2_執行.md；完成後 mv hotfix.md + 執行.md → hotfixes/ + git add。

### §8 baron 命令
msg 寫 /tmp/PIPE-RESUME_SHADOW-HOTFIX-2_msg.txt；git add code+bak+hotfixes+prompts+TODO；baron 手動 commit。

### 🛑 停止指令
產執行報告 + 歸檔後立即停止；嚴禁自發 commit/push。
````

---

## 執行結果摘要

- 🛑 **HALTED（未執行代碼）**——與現行 hotfix.md 矛盾（見下）：
  - 提示詞 §2 改 `translate_processor.py`（A 軌）；hotfix.md 為改 `translator.py:40` + `resume_pipeline.py:109`（B 軌）。
  - 提示詞採「加翻譯規則」（v1 舊法）；hotfix.md 採「移除矛盾、交回母提示詞」（v2）。
  - baron 先前明示「只修 B 軌、A 軌棄修」、並已核准 3 處 v2 版 hotfix.md。
- 已向 baron 呈報三項矛盾、待裁示；未動業務代碼、未備份、未歸檔。

## 後續引用

待 baron 裁示「依現行 hotfix.md（3 處 v2）執行」或「重發對齊的 Run 提示詞」後再落地。
`````
