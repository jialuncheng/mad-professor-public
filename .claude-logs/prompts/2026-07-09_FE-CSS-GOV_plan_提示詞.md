# 2026-07-09 — FE-CSS-GOV plan 提示詞

> **收到時間**：2026-07-09（UTC+8；本檔為**重發修訂版**、取代同日初版，差異見文末註）
> **任務代號**：FE-CSS-GOV（CSS 治理與作用域收斂）
> **觸發 commit**：plan
> **相關產出檔案**：`.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_plan_v1.md`
> **觸發情境**：DOC-SYNC-1 收官（`c8d6bcb`、地圖對齊現況、deep-doc 前置達成）後，baron 依 `baton/frontend_css_governance_audit.md`（治理高度定案：tokens→命名作用域+主題去重+拆檔+@layer、底線 **Safari 18+**、不跨 Tailwind/CSS Modules）下令開 FE-CSS-GOV plan——**FE-Refactor、每個 commit 含 docs 同步配套**；依據含 **FE 必讀 SOP**。

---

## 完整提示詞（重發修訂版、權威）

````markdown
FE-CSS-GOV（FE-Refactor、每個 commit 含 docs 同步配套）
frontend_css_governance_audit.md
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md

不用給commit建議
````

## 上下文（承接對話）

1. `baton/frontend_css_governance_audit.md`（7 節 + Priority Matrix、baron 兩輪定案）＝本案規格源：治理高度 `tokens（已達標）→ 命名作用域 + 主題去重 + 檔案拆分 → @layer（GO）`；**相容底線 Safari 18+**（取代 15.4）；❌ 不跨入 Tailwind/CSS Modules/SPA。
2. DOC-SYNC-1 已收官：design/docs 對齊現況（幽靈去毒+75/75 覆蓋）——deep-doc（ownership map / @layer 原則 / theme-guide 契約改寫 / principles margin-flow〔DOC-SYNC Q4 顯式移交〕）**唯一歸屬本案、隨各 commit 配套**（baron 拍板凍結於本提示詞標題）。
3. FE-PERF-2 已收官（`337764e`…`bc2bcc4`）：index.html 行號較 css audit 稽核時位移、plan 需重錨；C4 已於 `.msg-*` 加 content-visibility（拆檔時隨遷）。
4. 本案 FE-Refactor：**必讀 FE SOP**（§2 紅線/§3 渲染陷阱/§4 檢查表逐 commit）、驗收 E2E + console 0；純前端零 golden。

## 產出
- `.claude-logs/baton/2026-07-09_FE-CSS-GOV_CSS治理與作用域收斂_plan_v1.md`

---

> **版本註**：同日初版提示詞之第四依據為 `baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（絞殺者漸進範式）；重發版改列 **FE 必讀 SOP** 為第四依據（PIPE v10 未再列、其漸進精神仍為本案遷移策略之一般參照）。以重發版為權威。
