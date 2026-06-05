`````markdown
# 2026-06-05 — RESUME-P3 C3 Run（P3 逐 heading section 翻譯與還原·核心）提示詞

> **收到時間**：2026-06-05 23:40（UTC+8）
> **任務代號**：RESUME-P3 C3（BE-Refactor）
> **觸發 commit**：C3（P3 逐 heading section 翻譯與還原、廢 100% Bypass）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_RESUME-P3_C3_執行.md`
> **觸發情境**：baron 確認 C2 後下達 C3（核心）——重寫 `resume_pipeline.py::run_phase3`：讀 `ctx.ingestion.tiles`（C1 後=heading sections）逐 section 遞迴分流翻譯標題/正文 + pipelines/ 內私有方法重組 zh/en md（不耦合 A 軌 translate_processor）+ 沿用 InjectionContext + source_lang zh* 不重譯 + 交付 BilingualMarkdownSpec 不變。`# === [RESUME-P3 C3 START/END] ===` 包裹 + .bak。預期 `test_run_phase3_bypass_doctype_and_carryforward` carryover 紅燈、歸 C5。執行報告暫存 baton 不入 Git；TODO C3✅/C4 WIP + hash 自癒；msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 23:40 |
| 任務代號 | RESUME-P3 C3 |
| 觸發 Commit | C3 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_tasks.md |
| 觸發情境 | baron 確認上一個 Commit C2 順利完成，下達 C3 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_RESUME-P3_C3_run_提示詞.md + 更新 INDEX（RESUME-P3 系列 + 時間排序首行、超 15 刪最舊 PIPE-RESUME_C3）。

你現在扮演 Claude Code，執行單一 Commit C3。

### 任務資訊
- 任務編碼 RESUME-P3 / Commit C3 / BE-Refactor
- Tasks：baton/2026-06-05_RESUME-P3_..._tasks.md（§8 C3）

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C3）
1. 重寫 run_phase3：讀 ctx.ingestion.tiles（heading sections：level/title/content/children）逐 section 遞迴；標題與正文分流呼叫 Translator().translate（title→text_type="title"、text→"content"）；沿用 InjectionContext（lcc/glossary/zh_summary/domain_name/doc_type='resume'/constraints=_RESUME_CONSTRAINTS）；formula/figure/table 等保留原文結構；私有遞迴 _translate_sections/_restore_markdown_block 重組 zh/en；嚴禁 import translate_processor；source_lang.startswith('zh') 不重譯；寫 article_zh_path/article_en_path；交付 BilingualMarkdownSpec 欄位不變。
2. `# === [RESUME-P3 C3 START/END] ===` 包裹。
3. 物理防線：僅改 resume_pipeline.py；不動 A 軌/contracts/tiling/translator。
4. 備份：cp resume_pipeline.py → archive/2026-06-05_RESUME-P3_C3_resume_pipeline.py.bak
5. 測試：grep RESUME-P3 C3 + translate_processor 0 命中 + BilingualMarkdownSpec；pytest test_resume_pipeline + test_pipe_core。test_run_phase3_bypass_doctype_and_carryforward 預期紅燈（歸 C5）。
6. SOP：logger.error/.commit() 靜態檢測。
7. baton 暫存鐵律：執行報告留 baton、嚴禁 git add/搬移。

### TODO 同步 + hash 自癒
C3 → ✅；C4 → 🟡 WIP；刪重複 ⬜ C3 行；掃 git log 回填「待 baron 回填」。

### 產出規格
執行報告 baton/2026-06-05_RESUME-P3_C3_執行.md；套用 template_execution。

### §8 baron 命令
git add resume_pipeline.py + .bak + TODO + prompts；msg 寫 /tmp/RESUME-P3_C3_msg.txt；baron 手動 commit。

### 🛑 停止指令
產 C3_執行.md + 更新 TODO 後立即停止；不續跑 C4、不改未列檔、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：run_phase3 重寫逐 heading section 翻譯+還原（pipelines/ 內私有重組、不耦合 A 軌）；廢 100% Bypass
- 測試：grep（translate_processor 0 命中）+ test_resume_pipeline/test_pipe_core；test_run_phase3_bypass_* 預期 carryover 紅燈歸 C5
- 報告：baton/2026-06-05_RESUME-P3_C3_執行.md（暫存、不入版控）
- 是否 commit：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C1（tiles=heading sections）+ C2（resume 停用 U4）；C3 為核心逐 section 翻譯重組；下一步 C4（heading 退化 fallback）由 baron 另行下達。C5 統一修 carryover 測試（C1 tiles + C3 bypass）。
`````
