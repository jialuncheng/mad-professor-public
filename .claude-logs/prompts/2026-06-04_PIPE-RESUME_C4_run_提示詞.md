`````markdown
# 2026-06-04 — PIPE-RESUME C4 Run 提示詞

> **收到時間**：2026-06-04 19:37（UTC+8）
> **任務代號**：PIPE-RESUME C4
> **觸發 commit**：C4（P3 Translation & Restore — 100% Bypass 翻譯還原）
> **相關產出檔案**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C4_執行.md`
> **觸發情境**：baron 確認 C3 已手動提交（Checkout 含 C1-C3），下達 C4 執行指令——實作 `run_phase3`：建 `InjectionContext`（lcc/glossary/zh_summary←translated_abstract/domain_name/**doc_type='resume'**）→ 正文 100% Bypass `Translator.translate(NORMAL,content)` → md_restore 純樣板渲染 → 產 `final_zh_path`/`final_en_path` → 交付 `BilingualMarkdownSpec`（translated_abstract 沿用 P2、必填）。產報告暫存 baton/、同步 TODO.md（C4 ✅ / C5 WIP + Hash 自癒）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-04 19:37` |
| **任務代號** | `PIPE-RESUME C4` |
| **觸發 Commit** | `C4` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | baron 確認 C3 已手動提交，下達 C4 執行指令（當前 Checkout Commit 含 C1 至 C3）。 |

---

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成，才准進入下一步）

**你現在必須立即執行以下歸檔動作，完成前嚴禁進行任何讀檔、grep 或代碼操作：**

1. **寫入提示詞歸檔檔**：`.claude-logs/prompts/2026-06-04_PIPE-RESUME_C4_run_提示詞.md`（依 README §3）。
2. **更新 INDEX.md**：分類補登 + 時間排序首行插入，超 15 筆刪最舊。
3. **確認完成後繼續**：回覆「✅ 提示詞已歸檔：...」後續執行。

---

你現在扮演 **Claude Code**，請執行以下指定的單一 Commit。

### 📋 任務資訊
- **任務編碼**：`PIPE-RESUME`
- **當前 Commit 代號**：`C4`
- **工作流類別**：`BE-Refactor`
- **Tasks 路徑**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 🛠️ 執行命令與代碼修改規則
依 tasks §8 C4。物理防線（§7 不可動）/ 測試防線（§6.4 + §6.7 SOP）/ 文件防線（§1.3 不自發 commit）/ C4 START/END 註解包裝。
**P3 實作約束**：InjectionContext（lcc / glossary / zh_summary←P2 translated_abstract / domain_name / **doc_type='resume'**）；正文 100% Bypass 整份 `Translator.translate(text, ctx, NORMAL, "content")`；md_restore 純樣板渲染（無 extra_info）產 final_zh.md/final_en.md → BilingualMarkdownSpec（translated_abstract 沿用 P2、必填）；嚴禁 AI Questions / Summary 非原著文字。

### 💾 備份規則
`cp pipelines/resume_pipeline.py .claude-logs/archive/2026-06-04_PIPE-RESUME_C4_resume_pipeline.py.bak`

### 🔄 同步更新 TODO.md（必做、即時）
C4 → ✅（待 baron 回填）；C5 → 🟡 WIP；歷史 Hash 自癒（含 C3 hash 回填）。

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-04_PIPE-RESUME_C4_執行.md`（暫存 baton/、不入版控）；套用 template_execution。

### 📝 §8 baron 執行命令
git add resume_pipeline.py + .bak；msg 寫 /tmp/PIPE-RESUME_C4_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出 C4_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列代碼 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：`pipelines/resume_pipeline.py` `run_phase3` 實作（InjectionContext doc_type='resume' + 100% Bypass NORMAL 翻譯 + md_restore 樣板 + BilingualMarkdownSpec）
- 測試：§6.4 grep + §6.7 SOP + 既有全套件防 Regression
- 報告：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C4_執行.md`（暫存 baton/、不入版控）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C3（P2）。本階段 C4 實作 P3；下一步 C5 P4 Async RAG 由 baron 另行下達。
`````
