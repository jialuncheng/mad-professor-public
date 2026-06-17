# WORKFLOW-4 plan 產出提示詞

## 元數據
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-14 |
| 任務代號 | WORKFLOW-4（StraTA 任務成功率原理移植進文件治理模板）|
| 工作流 | DOC-Refactor |
| 觸發情境 | 讀 StraTA 論文（2605.06642v1、Strategic Trajectory Abstraction）後，評估其「提高任務成功率」機制可透過文件管理移植；經兩輪分析整合 |

## 正文（原文）
開 DOC-Refactor 的 plan、針對上面內容做一個 plan、baton/
依據 template/template_plan.md / ref/WORKFLOW_SOP.md / ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
不用給 commit 建議

## 移植規格（整合兩輪分析）
- StraTA 四機制：① 顯式固定策略 + 每步 conditioned ② 分層 ③ 多樣策略 rollout（farthest-point 取語意分散候選）④ 批判性自我評判（逐步:follow 策略? 推進任務?）
- 我們已有：plan=策略 z（凍結）/ 六階段分層 / 真因+hash+審計鏈=長程信用分配
- 移植進 4 模板：
  - template_prompt_for_plan §4：高風險才列 ≥2 語意分散候選 + trade-offs + baron 擇優（條件化、非每 plan 硬性）
  - template_plan（可選）：§候選方案留痕（被否決案作 §1.9 軌跡）
  - template_prompt_for_run：強制讀檔同列 plan（策略 z）+ tasks（動作）re-inject
  - template_execution：§1 加「與全局策略對齊說明」+ 新增 §自評（三問:越界? 無關? **推進哪個 U-N?**〔正向軸防做白工〕）
- 三校正：① 多案條件化非 blanket ② 自評補正向軸（推進哪個 U-N）③ Check 減負非省略（per-commit 自評前移分攤不可動/msg、Check 仍驗跨 commit U-coverage + §7.2）
- 誠實前提：StraTA 是 RL 訓練法、我們不訓練;移植的是「執行紀律原理」非演算法
