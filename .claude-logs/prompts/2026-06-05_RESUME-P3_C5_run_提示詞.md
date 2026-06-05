`````markdown
# 2026-06-05 — RESUME-P3 C5 Run（Unit Tests 逐 heading 契約與退化測試）提示詞

> **收到時間**：2026-06-05 23:59（UTC+8）
> **任務代號**：RESUME-P3 C5（BE-Refactor）
> **觸發 commit**：C5（Unit Tests）
> **相關產出檔案**：`.claude-logs/baton/2026-06-05_RESUME-P3_C5_執行.md`
> **觸發情境**：baron 確認 C4 後下達 C5——僅改 `tests/test_resume_pipeline.py`：①修 C1 carryover `test_run_phase1_contract`（FakeMd JsonProcessor 寫含 section 的 JSON、對齊 C1 opt-out 直讀 processed）②追加 C1 opt-out（不呼叫 TilingProcessor）/ C3 逐 section 標題正文分流翻譯+無整行英文標題殘留 / 無 doubling / C4 退化 fallback（單一巨 section→整檔）/ 契約 BilingualMarkdownSpec 完備。`# === [RESUME-P3 C5 START/END] ===` 包裹 + .bak；全套件除 env flake 全綠。執行報告暫存 baton 不入 Git；TODO C5✅/C6 WIP + hash 自癒；msg 寫 /tmp。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-05 23:59 |
| 任務代號 | RESUME-P3 C5 |
| 觸發 Commit | C5 |
| 相關產出檔案 | .claude-logs/baton/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_tasks.md |
| 觸發情境 | baron 確認上一個 Commit C4 順利完成，下達 C5 執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（必須先完成）
寫入 prompts/2026-06-05_RESUME-P3_C5_run_提示詞.md + 更新 INDEX（RESUME-P3 系列 + 時間排序首行、超 15 刪最舊 PIPE-RESUME_C5）。

你現在扮演 Claude Code，執行單一 Commit C5。

### 任務資訊
- 任務編碼 RESUME-P3 / Commit C5 / BE-Refactor
- Tasks：baton/2026-06-05_RESUME-P3_..._tasks.md（§8 C5）

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / tasks.md / logging_SOP / database_SOP

### 執行命令（依 tasks §8 C5）
1. 僅改 tests/test_resume_pipeline.py。
2. 修 C1 carryover：_mock_p1_processors 的 FakeMd 輸出含 section 的 JSON（{"sections":[{"type":"text","level":1,"title":"王小明","content":[]}]}）對齊 C1 opt-out 直讀 processed → test_run_phase1_contract 轉綠。
3. 追加 ①C1 opt-out（不呼叫 TilingProcessor embedding）②C3 逐 section 標題/正文分流翻譯 + 無整行英文標題殘留 ③無 doubling ④C4 fallback（單一巨 section→整檔降級+交付契約）⑤契約 BilingualMarkdownSpec 完備（translated_abstract 沿用 P2）。
4. `# === [RESUME-P3 C5 START/END] ===` 包裹。
5. 備份：cp test_resume_pipeline.py → archive/2026-06-05_RESUME-P3_C5_test_resume_pipeline.py.bak
6. 測試：grep RESUME-P3 C5 + pytest test_resume_pipeline + 全套件（除 env flake 全綠）。
7. baton 暫存鐵律：執行報告留 baton、嚴禁 git add/搬移。

### TODO 同步 + hash 自癒
C5 → ✅；C6 → 🟡 WIP；掃 git log 回填「待 baron 回填」。

### 產出規格
執行報告 baton/2026-06-05_RESUME-P3_C5_執行.md；套用 template_execution。

### §8 baron 命令
git add test_resume_pipeline.py + .bak + TODO + prompts；msg 寫 /tmp/RESUME-P3_C5_msg.txt；baron 手動 commit。

### 🛑 停止指令
產 C5_執行.md + 更新 TODO 後立即停止；不續跑 C6、不改未列檔、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 產出：test_resume_pipeline.py 修 C1 carryover + 追加 C1 opt-out/C3 逐 section/無 doubling/C4 fallback/契約 測試
- 測試：test_resume_pipeline 全綠 + 全套件除 env flake 全綠
- 報告：baton/2026-06-05_RESUME-P3_C5_執行.md（暫存、不入版控）
- 是否 commit：否（msg 寫 /tmp、baron 手動）

## 後續引用

承 C1-C4（P1 opt-out / U4 停用 / 逐 section 翻譯 / 退化 fallback）；C5 統一恢復測試全綠並覆蓋新契約；下一步 C6 Checkout 收官歸檔由 baron 另行下達。
`````
