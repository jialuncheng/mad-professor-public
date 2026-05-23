# Phase [Phase名稱] Commit [N]-hotfix — 緊急熱修復：[修復主題]

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門用於修正前一次 Commit 落地後立即發現的嚴重阻斷性 Bug 或 Regression。
> **修復原則**：只改動受災點程式碼，嚴禁夾帶任何無關的新功能或大型重構。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **[N]-hotfix** | `[7碼Hash]` | [Git Commit 訊息，如 fix(rag): hotfix for null pointer exception] |

---

## 阻斷性問題與真因

詳細記錄發生的 Regression 或 Block 問題，以及造成此問題的直接真因：

### 1. 阻斷現象 (Block Issue)
- **現象描述**：[描述使用者或系統遇到的具體崩潰或異常表現]
- **受災範圍**：[哪些 API、頁面或功能直接停擺]
- **首發日誌/錯誤堆疊**：
  ```
  [在此貼上第一時間捕捉到的 traceback 或 error log]
  ```

### 2. 真因診斷 (Root Cause)
- **技術細節**：[簡述為何前一個 Commit 會漏掉此邊界條件或產生此衝突]
- **定位程式碼**：`file:///path/to/buggy_file.py#L123`

---

## 熱修復修法 (Minimal Hotfix)

本修復採取的**最小侵入式**解決方案：

### `[受災檔案]` — 最小改動
```diff
- [貼上 - 刪除的 buggy 代碼]
+ [貼上 + 修復後的 safe 代碼]
```

---

## regression 預防與 E2E 驗證

越是緊急修補，越要嚴防 Regression：

### 1. 受影響模組的單元測試
```bash
$ pytest tests/ -v
# [貼上真實測試輸出，特別是針對本次受災點的單元測試]
```

### 2. 本地 E2E 快速復現與驗證
[記錄如何快速手動重跑一次原先出 Bug 的流程，並證明當前已 100% 正常]
```
[貼上修復後，成功執行的正常日誌輸出]
```

---

## 回退與備案

若此 Hotfix 依然未能完全解決問題，或引發更大的 Regression，請立即執行回退：

```bash
# 退回到最初安全穩定版本的 Commit (前前個 Commit)
git reset --hard [安全版本的 Commit Hash]
```
