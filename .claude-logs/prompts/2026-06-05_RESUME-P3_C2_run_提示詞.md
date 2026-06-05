`````markdown
# 2026-06-05 — RESUME-P3 C2 Run（Translator U4 resume 停用）提示詞

> **收到時間**：2026-06-05 23:25（UTC+8）
> **任務代號**：RESUME-P3 C2（BE-Refactor）
> **觸發 commit**：C2（Translator U4 resume 停用 / 行結構對齊容錯停用）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_RESUME-P3_C2_執行.md`
> **觸發情境**：baron 確認 C1 後下達 C2——`translator.py::translate` U4 區塊加閘門 `if (ctx.doc_type or '') != 'resume':`，使 resume 不執行 `。！？` 重切（保全條列/日期/地點原行結構），其他文體不變。僅改 translator.py U4；`# === [RESUME-P3 C2 START/END] ===` 包裹 + .bak；執行報告暫存 baton 不入 Git；TODO C2✅/C3 WIP + hash 自癒；msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 23:25 |
| 任務代號 | RESUME-P3 C2 |
| 觸發 Commit | C2 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_tasks.md |
| 觸發情境 | baron 確認上一個 Commit C1 順利完成，下達 C2 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_RESUME-P3_C2_run_提示詞.md + 更新 INDEX（RESUME-P3 系列 + 時間排序首行、超 15 刪最舊 PIPE-RESUME_C2）。

你現在扮演 Claude Code，執行單一 Commit C2。

### 任務資訊
- 任務編碼 RESUME-P3 / Commit C2 / BE-Refactor
- Tasks：baton/2026-06-05_RESUME-P3_..._tasks.md（§8 C2）

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C2）
1. 編輯 translator.py translate U4 區塊：`re.sub(r"([。！？])\s*", r"\1\n", translated)` 限非 resume 執行；加閘門 `if (ctx.doc_type or '') != 'resume':`，resume 不重切（保全條列/日期/地點行結構）。
2. `# === [RESUME-P3 C2 START/END] ===` 包裹。
3. 物理防線：僅改 translator.py U4；不動 A 軌/合約/雙模式引擎核心。
4. 備份：cp translator.py → archive/2026-06-05_RESUME-P3_C2_translator.py.bak
5. 測試：grep RESUME-P3 C2 + doc_type 'resume' 閘門；pytest test_translator（其他文體不退化）。
6. SOP：translator.py logger.error/.commit() 靜態檢測。
7. baton 暫存鐵律：執行報告留 baton、嚴禁 git add/搬移。

### TODO 同步 + hash 自癒
C2 → ✅；C3 → 🟡 WIP；掃 git log 回填「待 baron 回填」。

### 產出規格
執行報告 baton/2026-06-05_RESUME-P3_C2_執行.md；套用 template_execution。

### §8 baron 命令
git add translator.py + .bak + TODO + prompts；msg 寫 /tmp/RESUME-P3_C2_msg.txt；baron 手動 commit。

### 🛑 停止指令
產 C2_執行.md + 更新 TODO 後立即停止；不續跑 C3、不改未列檔、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：translator.py U4 加 `doc_type=='resume'` 停用閘門（resume 不 `。！？` 重切）
- 測試：grep 驗收 + test_translator 不退化 + SOP
- 報告：baton/2026-06-05_RESUME-P3_C2_執行.md（暫存、不入版控）
- 是否 commit：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C1（P1 履歷 tiling opt-out）；C2 停用 U4 為 C3 逐 heading section 翻譯保留條列/日期/地點行結構；下一步 C3（P3 逐 heading 翻譯與還原、廢 100% Bypass）由 baron 另行下達。
`````
