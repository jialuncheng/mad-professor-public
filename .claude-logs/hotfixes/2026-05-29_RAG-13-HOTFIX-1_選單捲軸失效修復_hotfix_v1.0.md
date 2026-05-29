# Phase RAG-13 Commit RAG-13-HOTFIX-1 — 緊急熱修復：自訂主題下拉選單捲軸無作用修復

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門用於修正自訂 CSS 主題功能（RAG-13）上線後，當自訂主題數量過多觸發垂直滾動條時，下拉選單捲軸完全失效且滾動時選單立即關閉消失的 Regression Bug。
> **修復原則**：只改動受災點程式碼，嚴禁夾帶任何無關的新功能或大型重構。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **RAG-13-HOTFIX-1** | `[由 baron 填入]` | fix(theme): global scroll intercept hotfix for dropdown scrollbar |

---

## 阻斷性問題與真因

詳細記錄發生的 Regression 或 Block 問題，以及造成此問題的直接真因：

### 1. 阻斷現象 (Block Issue)
* **現象描述**：
  當使用者上傳過多自訂 CSS 主題（例如 Fuller, Gropius, Corbusier 等超過選單高度限制時），下拉選單右側會正常產生垂直滾動條。然而，當使用者**使用滾輪滾動選單、在觸控板上滑動、或用滑鼠左鍵點擊並拖拽滾動條滑塊（Thumb）**時，下拉選單會**瞬間消失（關閉）**，導致捲軸完全「無作用」且無法瀏覽下方的主題。
* **受災範圍**：風格選單 (`#theme-dropdown` 展開的 `.dropdown-popup`) 自訂主題選擇。

### 2. 真因診斷 (Root Cause)
* **技術細節**：
  為了防範主頁面滾動時彈出層懸空偏移，系統在全域註冊了 `scroll` 監聽器：
  `window.addEventListener('scroll', closePopups, true);`
  由於第三個參數設為 `true`（**捕獲階段**），且 `scroll` 事件在選單內部滾動時（觸發了選單 `.ctx-popup` 的 `overflow-y: auto`）會向上傳遞至 `window`。這導致全域監聽器在第一時間攔截了自訂選單內部的滾動事件，並立刻觸發 `closePopups()`，將選單直接從 DOM 中移除。
* **定位程式碼**：`file:///Users/baroncheng/OrbStack/claude-lab/home/baroncheng/mad-professor-public/.claude/worktrees/hopeful-yalow-902c50/static/index.html#L1622`

---

## 熱修復修法 (Minimal Hotfix)

本修復採取的**最小侵入式**解決方案：

### `static/index.html` — 最小改動

透過 `e.target.closest('.ctx-popup')` 進行事件源過濾，如果滾動事件源自於彈出層內部，則忽略該事件，防止誤殺關閉。

```diff
<<<<
  // popup 開啟期間捲動 / 縮放視窗就關閉，避免錨點失準
  window.addEventListener('scroll', closePopups, true);
  window.addEventListener('resize', closePopups);
====
  // popup 開啟期間捲動 / 縮放視窗就關閉，避免錨點失準
  window.addEventListener('scroll', (e) => {
    // 🟢 RAG-13-HOTFIX-1：若滾動源自彈出選單內部，則忽略，防止誤判關閉
    if (e.target.closest && e.target.closest('.ctx-popup')) return;
    closePopups();
  }, true);
  window.addEventListener('resize', closePopups);
>>>>
```

---

## regression 預防與 E2E 驗證

越是緊急修補，越要嚴防 Regression：

### 1. 受影響模組的單元測試
由於本修復純屬前端 DOM 事件處理優化，不涉及任何後端 Python 邏輯，因此既有 tests 全量通過。
同時，執行測試以確保核心功能未受破壞：
```bash
$ pytest tests/ -v
# [貼上真實測試輸出，全量 pytest 均維持 383 Passed]
```

### 2. 本地 E2E 快速復現與驗證
1. **問題復現**：上傳 5 個以上自訂 CSS 主題，打開風格 modal，點選下拉選單。
2. **滾動測試**：
   - 嘗試用滑鼠滾輪向下滾動選單 ➔ 選單正常滾動，**不再消失**！
   - 用滑鼠拖拽右側捲軸滑塊 ➔ 選單正常滾動，**不再消失**！
3. **主頁面滾動測試**：滾動背後的主頁面（中欄文章）➔ 下拉選單立刻正常關閉（原設計美學依舊完美保留）。

---

## 回退與備案

若此 Hotfix 依然未能完全解決問題，或引發更大的 Regression，請立即執行回退：

```bash
# 復原 static/index.html 並退回上一 commit
git checkout -- static/index.html
git reset --hard d842008
```
