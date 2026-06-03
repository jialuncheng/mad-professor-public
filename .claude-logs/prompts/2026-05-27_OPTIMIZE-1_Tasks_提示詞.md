# 2026-05-27 — OPTIMIZE-1 Tasks 提示詞（最終版，含三大前端合規防線與真實行號）

> **收到時間**：2026-05-27 11:37
> **任務代號**：OPTIMIZE-1 Tasks
> **觸發 Commit**：OPTIMIZE-1-Tasks
> **相關產出檔案**：`.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md`
> **觸發情境**：baron 同意 plan v2 規格，下達任務拆分指令，並強制鎖定三大前端合規防線與真實行號

---

## 完整提示詞

```
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | `2026-05-27 11:37` |
| **任務代號** | `OPTIMIZE-1 Tasks` |
| **觸發 Commit** | `OPTIMIZE-1-Tasks` |
| **相關產出檔案** | `.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md` |
| **觸發情境** | `baron 同意 plan v2 規格，下達任務拆分指令，並強制鎖定三大前端合規防線與真實行號` |

你現在扮演 Claude Code，請依以下指令將 plan 拆分為可執行的 Commit 清單。

任務編碼：OPTIMIZE-1
工作流類別：BE-Refactor
Plan 路徑：.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md

強制讀檔清單：
- CLAUDE.md
- .claude-logs/ref/WORKFLOW_SOP.md
- .claude-logs/TODO.md
- .claude-logs/sop/2026-05-23_logging_SOP_手冊.md
- .claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_plan.md
- .claude-logs/templates/template_tasks.md
- .claude-logs/templates/template_execution.md

§0.5 baton 歸檔：0 次（tasks 與執行報告均暫存 baton/，收官時才一次性歸檔）

Commit 拆分原則：
- 結構：工作階段 Commit + 含驗收 Commit
- SOP：event: "performance_metric" + stage: "pdf_optimize" + duration_seconds: float
- 寫入安全防線：.tmp.pdf 暫存 + tmp_path.replace() 原子覆寫
- 可逆設計

🚨 前端 UI 復用與控制流翻轉「三大致命漏洞強制修正指令」（不合規防線）：

1. 真實行號鋼鐵定位（嚴禁使用錯誤行號）：
   - #confirm-modal 骨架定義：實際上在 L1287
   - #doc-type-dropdown 下拉選單：實際上在 L1291
   - #upload-btn click 監聽器位置：實際上在 L3193
   - #confirm-ok-btn click 攔截位置（showConfirmModal 內）：實際上在 L3343

2. 既存 Modal HTML 微調（補足取消出口、解鎖 ESC 阻擋，嚴禁新增任何 CSS）：
   (a) 定位 #confirm-modal（真實行號 L1287），將 data-no-esc="true" 與 data-no-mask-close="true" 修改為 false
   (b) 在 .modal-actions 按鈕區（真實行號 L1298）的 #confirm-ok-btn 之前，前插：
       <button id="confirm-cancel-btn" class="modal-btn">取消</button>
       （使用既有 modal-btn CSS class，零新增樣式）

3. 事件控制流翻轉（Phase-Shift）重構指針：
   - 攔截 #upload-btn click（真實行號 L3193），移除舊有直接選檔邏輯，改為顯示 #confirm-modal
   - 綁定 #confirm-cancel-btn click 與 ESC 鍵，僅關閉 Modal，零網路請求
   - 攔截 #confirm-ok-btn click（真實行號 L3343）：讀取選定類型 → 隱藏 Modal → 動態建立 input.click() → FormData POST

4. 不可動清單防線：§7 加入「既有的 waiting_confirm HTML 結構及 showConfirmModal 樣式骨架」

§8 六維度表格（影響範圍/安全性/可逆性/驗收 grep 條件/依賴關係/具體實作細節）
§1 TL;DR 含中文括號命名
TODO.md：OPTIMIZE-1 在 🔴 高優先，C1 WIP / C2 ⬜

產出路徑：.claude-logs/baton/2026-05-23_OPTIMIZE-1_PDF上傳自動無損優化_tasks.md（v3，baton/ 暫存，不移 plan）
嚴禁：_執行.md / 業務代碼 / git commit/push
```

---

## 執行結果摘要

（待執行後填入）

## 後續引用

- 下一步：baron 下達 OPTIMIZE-1 C1 提示詞（Run 階段，套用 template_execution.md）

> 本文件為 OPTIMIZE-1 Tasks 最終版提示詞歸檔，記錄 baron 強制鎖定三大前端合規防線（真實行號鋼鐵定位 + Modal HTML 微調補取消出口/ESC解鎖 + Phase-Shift 事件控制流翻轉）的完整意圖。
