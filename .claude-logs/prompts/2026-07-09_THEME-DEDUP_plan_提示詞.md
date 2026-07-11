# 2026-07-09 — THEME-DEDUP plan 提示詞

> **收到時間**：2026-07-09（UTC+8）
> **任務代號**：THEME-DEDUP
> **階段**：階段 1 — plan（純規劃、不動業務代碼）
> **相關產出檔案**：`.claude-logs/baton/2026-07-09_THEME-DEDUP_主題結構去重_plan_v1.md`
> **觸發情境**：FE-CSS-GOV 收官後，開 C3 外溢之結構去重續集 THEME-DEDUP；baron 指示依 template_plan + 三規範產 plan、落 baton、不含 commit 建議。

---

## 完整提示詞

````markdown
開 THEME-DEDUP
針對上面內容做一個plan
baton/

依據
template/template_plan.md
ref/WORKFLOW_SOP.md
ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md
sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md

不用給commit建議
````

> **「上面內容」語境**：FE-CSS-GOV C3 縮版時，主題**結構去重**整包外溢 THEME-DEDUP（因舊 85 行審計未涵蓋後補裝飾 CSS）。C5 grep 分析已定調處置原則：4 主題非白名單結構屬性——**共用**（4 主題同值）上移 base／**異值**token 化／**裝飾佔位幾何**（`.ph`/`.ph::before`）保留主題（theme-guide §1 Q8 carve-out）。theme-guide §8 已記方向。THEME-DEDUP plan 須對**全部**主題 CSS 完整重審（非舊快照）後細化+凍結。

---

## 執行結果摘要

- ✅ plan 產出於 baton：`2026-07-09_THEME-DEDUP_主題結構去重_plan_v1.md`（內部 v2）
- **v1→v2 擴大**：baron 追加要求「訂死主題規格」→ scope 由「結構去重」升級為「**主題完整規格凍結 + 4 主題全正規化 + doc 權威化**」
- **全 4 主題徹底掃描**（腳本 `{選擇器:屬性鍵}` 跨主題比對）發現三類：① 覆蓋已一致（19 token/15 選擇器）② 非白名單結構屬性需去重（B 共用/C 異值/D 裝飾）③ 白名單內屬性集分歧（font-style/letter-spacing/font-weight/text-align 未登記）
- §2.2 凍結規格草案（19 必備 token/15 必備選擇器/屬性白名單/裝飾例外/禁止清單）；§9 八 OQ（Q1 異值結構 token 化 + Q2 白名單自由度 為主決策）
- 純規劃、零業務碼；待 baron 過目 §9 OQ 拍板後才進 tasks

## 後續引用

baron 過目 plan §Open Questions → 拍板 → 階段 2 tasks（另下提示詞）。
