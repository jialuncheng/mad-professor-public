`````markdown
# 2026-06-06 — RESUME-P3 PARA-HOTFIX-1 Run（B軌正文段落邊界正規化·落地）提示詞

> **收到時間**：2026-06-06 05:19（UTC+8）
> **任務代號**：RESUME-P3 PARA-HOTFIX-1（BE-Hotfix 落地執行）
> **觸發 commit**：PARA-HOTFIX-1
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-P3_PARA-HOTFIX-1_hotfix.md`
> **觸發情境**：baron 確認 hotfix 計畫後下達執行指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-06 05:19 | 任務 RESUME-P3 PARA-HOTFIX-1 | 觸發 Commit PARA-HOTFIX-1 | 依據 hotfix.md |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-06_RESUME-P3_PARA-HOTFIX-1_run_提示詞.md + 更新 INDEX（補條目 + 時間排序首行、超 15 刪最舊）。

你扮演 Claude Code，執行單一 Commit PARA-HOTFIX-1（BE-Hotfix）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP

### 具體實作（# === [RESUME-P3 PARA-HOTFIX-1 START/END] === 包裹）
1. 備份 resume_pipeline.py + test_resume_pipeline.py → .bak。
2. pipelines/resume_pipeline.py：
   - 新增 @staticmethod _normalize_paragraph_breaks(text)：移植 A軌 _preserve_pipe_table 邏輯（行掃描 pipe table 保護 + re.sub(r"(?<!\|)(?<!\n)\n(?![\n\|])","\n\n")），不 import/不耦合 A軌。
   - _restore_one_section：text item 分支 rendered=_t(...) 後套 _normalize_paragraph_breaks 再 append；純字串 fallback 分支同套。
3. tests/test_resume_pipeline.py：追加 test_p3_text_paragraph_blank_line_normalized（兩段單 \n + pipe table；斷言 (a) 段落升 \n\n (b) table rows 保單 \n）。
4. 不動：標題還原（HEADING-HOTFIX-1）/ formula/figure/table 不套 / A軌不耦合 / 其餘四路 / 母提示詞 / DB。

### 三道防線
- 物理：僅 2 檔；測試：grep（PARA-HOTFIX-1 包裹 / _normalize_paragraph_breaks / md_restore 不耦合=0 / 新測試）+ pytest + SOP；文件：commit 由 baron。

### 備份
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_resume_pipeline.py.bak
cp tests/test_resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_test_resume_pipeline.py.bak

### TODO 同步 + Hash 自癒
頂部 ✅ 完成區追加 PARA-HOTFIX-1（hash 待回填）；git log 回填殘留佔位符（含 HEADING-HOTFIX-1）。

### 產出 + 收官歸檔（hotfix 一次性）
baton/2026-06-06_RESUME-P3_PARA-HOTFIX-1_執行.md（template_execution）→ 收官 mv hotfix.md + 執行.md → hotfixes/；§8 git add 清單 + msg（/tmp/RESUME-P3_PARA-HOTFIX-1_msg.txt）。

### 🛑 停止
產報告 + 搬移後立即停止；不動未列代碼、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（新增 _normalize_paragraph_breaks + _restore_one_section text/fallback 套用）+ test_resume_pipeline.py（追加 1 測試）+ 2 .bak
- 驗收：grep（包裹 / helper / A軌不耦合 0 / 新測試）+ pytest + SOP
- 收官：hotfix.md + 執行.md mv → hotfixes/
- 是否動其他業務代碼：否；是否 commit：否（待 baron）

## 後續引用

段落邊界正規化落地、移植 A軌 pipe-table-safe 邏輯不耦合；改 B軌輸出 → 須 `capture resume --force` 重捕 golden（baron 運維）。
`````
