`````markdown
# 2026-06-06 — RESUME-PERF-1 C1 Run（Collect/Assemble 重構·收集-組裝解耦）提示詞

> **收到時間**：2026-06-06 17:10（UTC+8）
> **任務代號**：RESUME-PERF-1 C1（BE-Refactor 階段 4 執行）
> **觸發 commit**：C1
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_tasks.md`
> **觸發情境**：baron 確認 tasks 拆分後下達 C1 執行指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-06 17:10 | 任務 RESUME-PERF-1 C1 | 觸發 Commit C1 | 依據 tasks.md §8 C1 |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-06_RESUME-PERF-1_C1_run_提示詞.md + 更新 INDEX。

你扮演 Claude Code，執行單一 Commit C1（BE-Refactor）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C1 Collect/Assemble 重構）
1. 備份 resume_pipeline.py → .bak。
2. 新增 _collect_render_slots(sections, depth, out)：遞迴鏡像現行走訪、不翻譯、append slot——title→{kind:title,text,level:min(2+depth,6)}、text→{kind:content,text}、非 text 有 content→{kind:raw,text}、字串 fallback→{kind:content,text}、children depth+1。
3. 重構 _restore_sections_markdown：collect slots → 逐 slot **序列**翻譯（title/content 經 _t）→ 按序組裝（title→`#*level + zh`、content→_normalize_paragraph_breaks(zh)、raw→原文）→ "\n\n".join。仍序列、輸出 byte 等價。
4. _t/_translate_whole/退化偵測不動；HEADING 層級值/PARA 正規化/META header 不改（僅搬位置）。
5. # === [RESUME-PERF-1 C1 START/END] === 包裹。

### 三道防線
- 物理：僅 resume_pipeline.py（tasks §7）；測試：grep（_collect_render_slots / 仍序列 _t）+ pytest test_resume_pipeline 既有全綠（byte 等價）；文件：commit 由 baron。

### 備份
cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-06_RESUME-PERF-1_C1_resume_pipeline.py.bak

### TODO 同步 + Hash 自癒
Tasks + C1 → ✅ done（待回填）；C2 → 🟡 WIP；git log 回填殘留佔位符。

### 產出（baton 暫存紅線）
baton/2026-06-06_RESUME-PERF-1_C1_執行.md（暫存、嚴禁 git add、C4 才歸檔）；§8 git add 清單（不含 baton 報告）+ msg（/tmp/RESUME-PERF-1_C1_msg.txt）。

### 🛑 停止
產報告後立即停止；不續 C2、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：resume_pipeline.py（_collect_render_slots + _restore_sections_markdown 收集-組裝解耦、仍序列）+ .bak
- 驗收：grep + pytest test_resume_pipeline 既有全綠（輸出 byte 等價）
- 報告：baton/..._C1_執行.md（暫存、不 git add）
- 是否動其他業務代碼：否；是否 commit：否（待 baron）

## 後續引用

C1 解耦完成、仍序列、輸出等價；下一步 C2（序列翻譯 → ThreadPool 並行 + 異常隔離）。
`````
