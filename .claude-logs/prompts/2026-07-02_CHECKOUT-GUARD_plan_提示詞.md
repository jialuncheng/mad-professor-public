# 2026-07-02 — CHECKOUT-GUARD plan 提示詞

> **收到時間**：2026-07-02（UTC+8）
> **任務代號**：CHECKOUT-GUARD
> **觸發 commit**：plan
> **相關產出檔案**：`.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_plan_v1.md`
> **觸發情境**：FE-PERF-1 收官期間，WORKFLOW-5 之未追蹤歸檔檔被廣義 `git add` 掃進 FE-PERF-1 C1 commit（跨任務混檔）；事後以歷史重寫淨化。baron 要求從流程層面根治——立「收官 git-add 白名單鐵律 + staged 自檢」防再犯。依 template_plan/WORKFLOW_SOP/framework，**不含 commit 建議**。

---

## 完整提示詞

````markdown
開 CHECKOUT-GUARD
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

不用給commit建議
````

## 上下文（承接對話）
1. FE-PERF-1 checkout 時，WORKFLOW-5 C7 因先前漏 commit，其歸檔檔以未追蹤狀態躺在工作區，被 commit 的廣義 `git add` 掃入 FE-PERF-1 C1（`60cd126`）→ 跨任務混檔。
2. 因未 push，走安全歷史重寫（`fe_rebuild.py`：守衛 + 逐顆 `git add --` + **每顆 commit 前斷言 staged 集合 == 預期集合** + 備份 tag）淨化為乾淨邊界（WF5 C7 `12564be` / FE-PERF-1 C1 `3ec7b3f` 只含 SOP / C2 `4fb2248`）。
3. baron 拍板：把「checkout 逐檔 `git add`、禁 `git add .`／`-A`／`<目錄>` + commit 前 staged 自檢」寫進流程根治。

## 產出
- `.claude-logs/baton/2026-07-02_CHECKOUT-GUARD_收官git-add白名單鐵律_plan_v1.md`
