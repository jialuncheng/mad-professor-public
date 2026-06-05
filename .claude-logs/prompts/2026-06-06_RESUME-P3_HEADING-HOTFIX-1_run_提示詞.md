`````markdown
# 2026-06-06 — RESUME-P3 HEADING-HOTFIX-1 Run（B軌標題層級遞迴深度修復·落地）提示詞

> **收到時間**：2026-06-06 03:40（UTC+8）
> **任務代號**：RESUME-P3 HEADING-HOTFIX-1（BE-Hotfix 落地執行）
> **觸發 commit**：HEADING-HOTFIX-1
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_hotfix.md`
> **觸發情境**：baron 確認 hotfix 計畫後下達執行指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-06 03:40 | 任務 RESUME-P3 HEADING-HOTFIX-1 | 觸發 Commit HEADING-HOTFIX-1 | 依據 hotfix.md |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_run_提示詞.md + 更新 INDEX（補條目 + 時間排序首行、超 15 刪最舊）。

你扮演 Claude Code，執行單一 Commit HEADING-HOTFIX-1（BE-Hotfix）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP

### 具體實作（# === [RESUME-P3 HEADING-HOTFIX-1 START/END] === 包裹）
1. 備份 resume_pipeline.py + test_resume_pipeline.py → .bak。
2. pipelines/resume_pipeline.py：
   - _restore_sections_markdown 呼叫加 depth=0。
   - _restore_one_section 簽名加 depth:int=0；移除 sec.get("level") 短路、改 level=min(2+depth,6)；`parts.append(f"{'#'*level} {zh_title}")`；children 遞迴傳 depth=depth+1。
3. tests/test_resume_pipeline.py：追加 test_p3_heading_level_by_recursion_depth（3 層巢狀、所有節點 level=1、斷言 ##/###/#### 來自遞迴深度、≥2 層級防塌陷）。
4. 不動：content 分流 / _translate_whole / _t / C4 退化偵測 / run_phase3 主流程 / BilingualMarkdownSpec / A軌 / 其餘四路 / 母提示詞 / DB。

### 三道防線
- 物理：僅 2 檔；測試：grep（HEADING-HOTFIX-1 包裹 / sec.get("level") 期望 0 / 遞迴深度命中）+ pytest + SOP；文件：commit 由 baron。

### 備份
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_resume_pipeline.py.bak
cp tests/test_resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_test_resume_pipeline.py.bak

### TODO 同步 + Hash 自癒
頂部 ✅ 完成區 RESUME-P3 追加 HEADING-HOTFIX-1（hash 待回填）；git log 回填殘留佔位符。

### 產出 + 收官歸檔（hotfix 一次性）
baton/2026-06-06_RESUME-P3_HEADING-HOTFIX-1_執行.md（template_execution）→ 收官 mv hotfix.md + 執行.md → hotfixes/；§8 git add 清單 + msg（/tmp/RESUME-P3_HEADING-HOTFIX-1_msg.txt）。

### 🛑 停止
產報告 + 搬移後立即停止；不動未列代碼、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（_restore_one_section depth 推算）+ test_resume_pipeline.py（追加 1 測試）+ 2 .bak
- 驗收：grep（包裹 / sec.get("level")=0 / 遞迴深度）+ pytest + SOP
- 收官：hotfix.md + 執行.md mv → hotfixes/
- 是否動其他業務代碼：否；是否 commit：否（待 baron）

## 後續引用

修法落地遞迴深度 level=min(2+depth,6)；改 B軌輸出 → 須 `capture resume --force` 重捕 golden（baron 運維）。
`````
