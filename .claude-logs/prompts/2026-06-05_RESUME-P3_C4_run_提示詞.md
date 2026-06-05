`````markdown
# 2026-06-05 — RESUME-P3 C4 Run（heading 退化 Fallback）提示詞

> **收到時間**：2026-06-05 23:50（UTC+8）
> **任務代號**：RESUME-P3 C4（BE-Refactor）
> **觸發 commit**：C4（heading 退化 Fallback / 單一巨 section 降級防護）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_RESUME-P3_C4_執行.md`
> **觸發情境**：baron 確認 C3 後下達 C4——`run_phase3` 逐 section 前加退化偵測（section 數 < 2 或單一 section 文字佔比 > 85% = heading 抓取失敗）→ warning + 降級走 C3 的 `_translate_whole` 整檔翻譯 fallback，保證極限情況仍交付 BilingualMarkdownSpec。僅改 resume_pipeline.py；`# === [RESUME-P3 C4 START/END] ===` 包裹 + .bak；退化單元測試歸 C5。執行報告暫存 baton 不入 Git；TODO C4✅/C5 WIP + hash 自癒；msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 23:50 |
| 任務代號 | RESUME-P3 C4 |
| 觸發 Commit | C4 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_tasks.md |
| 觸發情境 | baron 確認上一個 Commit C3 順利完成，下達 C4 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_RESUME-P3_C4_run_提示詞.md + 更新 INDEX（RESUME-P3 系列 + 時間排序首行、超 15 刪最舊 PIPE-RESUME_C4）。

你現在扮演 Claude Code，執行單一 Commit C4。

### 任務資訊
- 任務編碼 RESUME-P3 / Commit C4 / BE-Refactor
- Tasks：baton/2026-06-05_RESUME-P3_..._tasks.md（§8 C4）

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C4）
1. run_phase3 逐 section 前加退化偵測：①section 數 < 2 ②單一 section 文字佔總字數 > 85%（走訪累加 text item 長度算最大佔比）→ logger.warning + 路由至 _translate_whole(full_text, inj, tr, True) 整檔 fallback；保證交付 BilingualMarkdownSpec。
2. `# === [RESUME-P3 C4 START/END] ===` 包裹。
3. 物理防線：僅改 resume_pipeline.py；不動 A 軌/contracts/tiling/translator。
4. 備份：cp resume_pipeline.py → archive/2026-06-05_RESUME-P3_C4_resume_pipeline.py.bak
5. 測試：grep RESUME-P3 C4/退化/fallback；pytest test_resume_pipeline + test_pipe_core（維持 C3 綠燈、僅 C1 carryover 紅）。退化單元測試歸 C5。
6. SOP：logger.error/.commit() 靜態檢測。
7. baton 暫存鐵律：執行報告留 baton、嚴禁 git add/搬移。

### TODO 同步 + hash 自癒
C4 → ✅；C5 → 🟡 WIP；掃 git log 回填「待 baron 回填」。

### 產出規格
執行報告 baton/2026-06-05_RESUME-P3_C4_執行.md；套用 template_execution。

### §8 baron 命令
git add resume_pipeline.py + .bak + TODO + prompts；msg 寫 /tmp/RESUME-P3_C4_msg.txt；baron 手動 commit。

### 🛑 停止指令
產 C4_執行.md + 更新 TODO 後立即停止；不續跑 C5、不改未列檔、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：run_phase3 加 heading 退化偵測（section<2 或單一佔比>85%）→ warning + _translate_whole 整檔 fallback
- 測試：grep + test_resume_pipeline/test_pipe_core（維持 C3 綠燈、僅 C1 carryover 紅）
- 報告：baton/2026-06-05_RESUME-P3_C4_執行.md（暫存、不入版控）
- 是否 commit：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C3（逐 heading 翻譯 + _translate_whole helper）；C4 加退化偵測啟發式守住單一巨 section；下一步 C5（單元測試：C1 tiles carryover + 逐 section / 退化 fallback 契約）由 baron 另行下達。
`````
