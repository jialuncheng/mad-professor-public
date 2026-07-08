# 2026-07-09 — FE-PERF-2 plan 提示詞

> **收到時間**：2026-07-09（UTC+8）
> **任務代號**：FE-PERF-2（前端效能紅線四項實修）
> **觸發 commit**：plan
> **相關產出檔案**：`.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_plan_v1.md`
> **觸發情境**：`baton/frontend_browser_standards_audit.md` 經落實性複核（每節 ✅/⚠️/❌ 裁決 + 建議打包）後，baron 下令針對其「FE-Refactor 一包」（#1 串流 O(n²) 重排 / #3 marked 自託管+defer / #4 KaTeX 字型 preload / #7 scroll passive）開正式 plan、落 baton/、依 template_plan/WORKFLOW_SOP/framework，**不含 commit 建議**。

---

## 完整提示詞

````markdown
frontend_browser_standards_audit.md
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

不用給commit建議
````

## 上下文（承接對話）

1. Osmani《How modern browsers work》稽核 → `baton/frontend_browser_standards_audit.md`（8 findings + Priority Matrix + 落實性裁決）。
2. FE-PERF-1 已立 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md` 並回填 WORKFLOW_SOP §1.1/§1.4——**本案為該 FE 必讀 SOP 首次 dogfood 之 FE-Refactor（實碼）**。
3. audit 落實性複核定案打包：**FE 包 = #1+#3+#4+#7**；#2 Gzip 屬 BE-Refactor 另開；#6/#8/§1-2 不做；#5/§1-3 緩議。
4. 前端相容底線已拍板 **Safari 15.4+**（css governance audit 定案；本案四項不依賴 15.4 特性、僅記背景）。
5. 產 plan 時效性重驗：`static/index.html` 自稽核以來零改動（中間 FE-PERF-1/CHECKOUT-GUARD/CONTEXT-1 皆純 DOC），所有反例行號仍有效；並補「body markup L1367-1598 零 inline handler」證據（DOMContentLoaded 包裹可行性）。

## 產出
- `.claude-logs/baton/2026-07-09_FE-PERF-2_前端效能紅線四項實修_plan_v1.md`
