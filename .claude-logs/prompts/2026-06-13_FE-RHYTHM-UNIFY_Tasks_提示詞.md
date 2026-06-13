# FE-RHYTHM-UNIFY Tasks 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-13 22:30 |
| 任務代號 | FE-RHYTHM-UNIFY Tasks |
| 觸發 Commit | FE-RHYTHM-UNIFY-Tasks |
| 相關產出檔案 | `.claude-logs/baton/2026-06-13_FE-RHYTHM-UNIFY_閱讀視圖垂直節奏統一_tasks.md` |
| 觸發情境 | baron 同意 plan 規格（v2 九 OQ 全定案、模型凍結），下達任務拆分指令 |
| 工作流類別 | FE-Refactor |

## 正文（原文摘要）
扮演 Claude Code，依 plan v2 拆分為可執行 Commit 清單。
- 任務編碼 FE-RHYTHM-UNIFY / FE-Refactor / plan：baton/2026-06-13_FE-RHYTHM-UNIFY_..._plan_v1.md
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / TODO.md / plan / template_tasks.md
- 工作目錄硬規則：唯一合法 worktree；tasks 階段只 view/grep/文件編輯、不改代碼；產出留 baton/
- tasks.md §0.5 成果盤點 + §1 TL;DR（中文括號命名）+ §8 六維度 Commit 拆分表格
- 最後 Commit 必為 Checkout（收官歸檔）；每 Commit 語意完整可逆
- 同步更新 TODO.md（高優先區最前、🟡 WIP）
- Plan 歸檔時機警告：baton/ 一律 Checkout 才一次性 mv + git add
- 產出 tasks.md + 更新 TODO.md 後立即停止；嚴禁產執行.md/改代碼/提前 mv/commit/push

## 決策軌跡
- plan v2 九 OQ 全 🟢 定案、§9.1 凍結候選模型（4 條 CSS：基準流 space-4 / 非標題→標題 space-6 / 標題→* space-2 / p→清單 space-1）
- Q2 主題讓位：清理 4 主題 margin 拆獨立 commit（降 regression）
- spike 三驗點：① 塊級=#paper-content 直接子代 ② 巢狀清單不誤撐 ③ Dia 渲染
- Q5 不收編 3c/3d/promote（markdown 層正交）；Q7 supersede FE-RHYTHM-1（同 commit 移除）；Q9 不含 chat
