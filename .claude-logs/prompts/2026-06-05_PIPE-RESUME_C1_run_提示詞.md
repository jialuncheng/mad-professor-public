`````markdown
# 2026-06-05 — PIPE-RESUME C1 Run（Sync System Specs）提示詞

> **收到時間**：2026-06-05 09:50（UTC+8）
> **任務代號**：PIPE-RESUME C1（v9 整合批次）
> **觸發 commit**：C1（同步三份核心規格文件）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C1_執行.md`
> **觸發情境**：baron 下達 C1 執行——就地同步 baton/ 三份 Markdown（plan_v1 / 母 plan v10 / PIPE-SPEC），寫入 C7/C8-hotfix 史、raw_metadata 穿線、P3 翻譯隔離、P2 摘要先行、Revision + §7.1 Cleanup。純文件、baton/ 主文件不入 Git（僅 .bak + 報告 + TODO + prompts git add）；產報告 + TODO（C1 ✅ / C2 WIP）後即停。

---

## 完整提示詞

````
### 📊 元數據審計塊（baron 填入）

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-06-05 09:50` |
| **任務代號** | `PIPE-RESUME C1` |
| **觸發 Commit** | `C1` |
| **相關產出檔案** | `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` |
| **觸發情境** | `baron 下達 C1 同步核心規格之執行指令` |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 `.claude-logs/prompts/2026-06-05_PIPE-RESUME_C1_run_提示詞.md`（README §3）+ 更新 INDEX（分類 + 時間排序首行、超 15 刪最舊）+ 回覆已歸檔後續執行。

你現在扮演 Claude Code，執行單一 Commit C1。

### 📋 任務資訊
- 任務編碼 PIPE-RESUME / 當前 Commit C1 / 工作流 BE-Refactor
- Tasks 路徑 `.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md`

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / plan_v1 / 母 plan v10 / PIPE-SPEC / database_SOP

### 🛠️ 執行命令
依 tasks §8 C1 修改三份核心文件：
1. 物理防線：僅就地改 baton/ 三份 Markdown（plan_v1/plan_v10/specification）；嚴禁改 Python/前端/其他目錄。
2. Git 控制防線：baton/ 三份主文件此階段**不入 Git**（嚴禁 git add）；僅 git add 產生的 .bak（archive/）。
3. SOP：純文件異動、不涉 DB/logger。

### 💾 備份規則
cp 三份 → `.claude-logs/archive/2026-06-05_PIPE-RESUME_C1_{plan_v1,plan_v10,specification}.md.bak`

### 🔄 同步更新 TODO.md
C1 → ✅（待 baron 回填）；C2 → 🟡 WIP。（不用給 commit 建議、無須 Hash 自癒掃描。）

### 📁 產出規格
執行報告 `.claude-logs/baton/2026-06-05_PIPE-RESUME_C1_執行.md`；套用 template_execution。

### 📝 §8 baron 執行命令與 Commit msg
msg 寫 `/tmp/PIPE-RESUME_C1_msg.txt`；§8 git add 僅 .bak + 執行報告 + TODO + prompts（baton/ 三主文件不入 git）；baron 手動 commit。

### 🛑 停止指令
產 C1_執行.md 後立即停止。嚴禁續跑下一 Commit / 改未列檔案 / 自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中
- 產出：母 plan v10 + PIPE-SPEC 同步寫入（raw_metadata 穿線 / P3 翻譯隔離 / Phase2 摘要先行 / C7-C8 史 / Flip Cleanup）；plan_v1 已 v11、確認對齊
- 備份：三份 .bak → archive/
- 報告：`.claude-logs/baton/2026-06-05_PIPE-RESUME_C1_執行.md`（暫存 baton/）
- 是否 commit / push：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 Tasks（03:35 精修 7 Commit）。本 C1 純三文件同步、為 C2 動共用基建（PipelineContext.raw_metadata）鋪路；下一步 C2 由 baron 另行下達。
`````
