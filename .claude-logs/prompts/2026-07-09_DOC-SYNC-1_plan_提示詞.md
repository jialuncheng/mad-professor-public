# 2026-07-09 — DOC-SYNC-1 plan 提示詞

> **收到時間**：2026-07-09（UTC+8）
> **任務代號**：DOC-SYNC-1（設計文件現況對齊）
> **觸發 commit**：plan
> **相關產出檔案**：`.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_plan_v1.md`
> **觸發情境**：design/docs 一致性實測（doc ID 27 vs 實際 75、components 6 幽靈 class、docs 停更 2026-05-24~06-13）→ baron 拍板順序「先輕量 DOC-SYNC 清帳、後 FE-CSS-GOV（docs 同 commit 配套）、兩 plan 分開」→ 下令開 DOC-SYNC plan（1–2 commits、小）、落 baton/、依三權威源、不含 commit 建議。

---

## 完整提示詞

````markdown
DOC-SYNC（DOC-Refactor、1–2 commits、小）
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md

不用給commit建議
````

## 上下文（承接對話）

1. CSS 治理稽核（`baton/frontend_css_governance_audit.md`）→ baron 問 design/docs 是否需配合改版修改 → 複核：分三層（必改/條件改/新增）。
2. baron 再問「docs 約定 vs 現況一致嗎」→ 實測：**token 契約層零差全準**（color-tokens/spacing/typography/theme-guide 19 必供）；**元件/DOM 記載層顯著過時**（dom-reference 覆蓋率 36%〔27/75 ID〕、components 6 幽靈 class〔msg-copy 等規劃寫成現況〕）；docs 停更於 2026-05-24~06-13、index.html 改到 07-09（≈5 個任務世代欠帳）。
3. baron 問先後 → 定案：**先輕量 DOC-SYNC（只清幽靈+補漏記、不深耕）→ 後 FE-CSS-GOV（ownership map/@layer 原則/theme-guide 改寫隨各 commit 配套）**、兩 plan 分開。
4. 本提示詞：開 DOC-SYNC plan。

## 產出
- `.claude-logs/baton/2026-07-09_DOC-SYNC-1_設計文件現況對齊_plan_v1.md`
