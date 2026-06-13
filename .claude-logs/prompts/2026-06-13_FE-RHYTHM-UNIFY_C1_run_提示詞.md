# FE-RHYTHM-UNIFY C1 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 23:03 |
| 任務代號 | FE-RHYTHM-UNIFY C1 |
| 觸發 Commit | C1 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-13_FE-RHYTHM-UNIFY_閱讀視圖垂直節奏統一_tasks.md` |
| 觸發情境 | baron 確認上一步後下達 C1 執行指令 |
| 工作流類別 | FE-Refactor |

## 正文（原文摘要）
執行單一 Commit C1（Spike & 模型凍結）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C1）
- 三防線：① 物理——嚴禁改任何 production / themes ② 測試——本地最小 HTML harness 測三軌（履歷/論文/簡報）+ Dia/Safari 肉眼 + 審視真實 reading-view DOM 確認直接子代假設 ③ 文件——凍結 token(4/6/2/1) + 特殊塊 margin-top 明列(.slide-head/.katex-display/.paper-header-meta…) + 選擇器最終形(含互斥性) + :has() 完全消滅結論，寫入 C1 執行報告；完成刪 harness、git status 無 production 變更
- 備份：純 spike 無 production 變動、無備份
- TODO：C1 標 ✅、C2 標 🟡 WIP + git log hash 自癒回填
- 產出：執行報告 → baton/2026-06-13_FE-RHYTHM-UNIFY_C1_執行.md（暫存、不入 Git）
- §8 baron 命令：本階段無 production 變動 → git add 空、msg 草稿寫 tmp/、`git commit --allow-empty`
- 停止：產報告 + TODO 後立即停；嚴禁執行 C2 / 改代碼 / 自發 commit/push

## 偏差註記（Claude Code）
- 提示詞 §8 commit msg 草稿簽名為 `Claude Sonnet 4.6 <noreply@anthreply.com>`（錯）→ 執行報告更正為當前模型 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- 瀏覽器肉眼（Dia/Safari）渲染為 baron E2E；Claude Code 於 headless worktree 以「DOM 生成碼審查 + headless 計算 getComputedStyle margin（如可用）+ 選擇器特異度/互斥推理」做可驗證之 spike，視覺終驗交 baron
