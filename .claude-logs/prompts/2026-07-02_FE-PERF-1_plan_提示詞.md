# 2026-07-02 FE-PERF-1 plan 提示詞

- **任務代號**：FE-PERF-1（前端效能與渲染 SOP 建立）
- **階段**：plan（階段 1 規劃）
- **工作流**：DOC-Refactor
- **歸檔時間**：2026-07-02

---

## 原始提示詞（逐字）

> 產出一份 sop
> 針對上面內容做一個plan
> baton/
>
> 依據
> template/template_plan.md
> ref/WORKFLOW_SOP.md
> ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
>
> 不用給commit建議

---

## 上下文（承接對話）

1. baron 給《How modern browsers work》(Addy Osmani) PDF，要求以其為標準檢驗前端 → Claude 產出 8 條效能/渲染稽核。
2. baron 要求比對既有 `.claude-logs/baton/frontend_browser_standards_audit.md` → Claude 補入遺漏之最高槓桿項（串流 O(n²) 重排）等並重排 Priority Matrix。
3. baron 問是否值得做成 `ref/` 前端開發準則 → Claude 評估：值得，但建議放 `sop/`（workflow-gated、不污染 @path auto-load）、範圍限效能+渲染正確性、回填 WORKFLOW_SOP FE 兩列。
4. 本提示詞：baron 拍板產 plan，落 baton/，依三份權威源，**不含 commit 建議**（tasks 階段才拆）。

## 產出

- `.claude-logs/baton/2026-07-02_FE-PERF-1_前端效能與渲染SOP建立_plan_v1.md`
