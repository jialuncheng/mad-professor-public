# WORKFLOW-4 C3 Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-18 01:58 |
| 任務代號 | WORKFLOW-4 C3 |
| 觸發 Commit | C3 |
| 相關產出檔案 | `.claude-logs/baton/2026-06-18_WORKFLOW-4_C3_執行.md` |
| 觸發情境 | baron 審 C2 報告並手動 commit 後下達 C3（Check 側減負前移）|
| 工作流類別 | DOC-Refactor |

## 正文（原文摘要）
執行單一 Commit C3（Check 側減負前移·信用分配）。
- 強制讀檔：CLAUDE.md / WORKFLOW_SOP.md / tasks.md（§8 C3）/ template_execution / template_prompt_for_check
- staging：只動模板、嚴禁業務代碼;baton 暫存（plan/tasks/C1-C3 報告）嚴禁 git add、C4 才歸檔（.bak 與模板除外）
- 實作：① 備份 template_prompt_for_check .bak（.claude-logs/templates/、入 C3 git add）② U5 在 Conformance 交叉比對段加輕量註記「不可動（維度三）+ msg（維度五）已由各 Run §自評（U3）前移分攤;Check 減負非省略、仍為最後總閘門、聚焦跨 commit U-coverage（總驗收）+ §7.2 跨 Phase 整合、確保所有 commit 疊加 100% 實現全 U-N」;`<!-- [WORKFLOW-4 C3 U5] -->` 包裹;**嚴禁重寫 WORKFLOW_SOP §4 五維度定義**
- 驗收：§6.3 grep + 零業務代碼 + pytest 基線
- C3 報告套用**重構後** template_execution（含 §1 對齊欄 + §自評、dogfood）
- 產出：C3 報告 baton（嚴禁 git add）;TODO C3 ✅ / C4 🟡 WIP + hash 自癒
- 停止：報告 + TODO 後立即停;嚴禁 C4/自發 commit/baton git add

## 偏差註記
- cp 路徑 `templates/`→實際 `.claude-logs/templates/`;INDEX 補「### WORKFLOW 系列」（非 DOC-Refactor 系列）
