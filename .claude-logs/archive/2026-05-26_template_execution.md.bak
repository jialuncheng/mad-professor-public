# Phase [Phase名稱] Commit [N] — 執行報告：[主題名稱]

> **基準**：Commit [前一次的落地 Commit Hash] 後的 worktree 狀態
> **狀態**：本地改檔完成，[尚未 commit / 已 commit 未 push / 已落地]

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **[N]** | `[7碼Hash]` | [Git Commit 訊息，如 feat(rag): chunking optimization] |

---

## diff stat

貼上 `git diff --stat`（或 uncommitted/committed 改動統計）的真實輸出：
```
[在這裡貼上真實的 git diff --stat 結果]
```

---

## 真因

簡述本次執行所對應的計畫真因（與 `_plan.md` 的問題與根因呼應）：
- **問題對應 §2 [#1]**：[簡述核心原因]
- **問題對應 §2 [#2]**：[簡述核心原因]

---

## 修法

詳細條列每個檔案的改動內容，必要時附帶關鍵程式碼片段以利未來回溯：

### 1. `[檔案 A]` — [改動名稱]
[詳細描述具體修法與邏輯]
```python
# 關鍵修改代碼片段
```

### 2. `[檔案 B]` — [改動名稱]
[詳細描述具體修法與邏輯]

---

## 不可動清單遵守狀態

驗證已嚴格遵守計畫中制定的「邊界限制」：

- [ ] 已確認 `[檔案名稱 A]` 的 `[特定邏輯]` 未被修改。
- [ ] 已確認 `[檔案名稱 B]` 的 `[特定配置]` 未被修改。
- [ ] 已確認未引發任何超出本 Commit 範疇的額外副作用。

---

## 端到端（E2E）驗證結果

提供真實、不造假的驗證證據：

### 1. 本地改動狀態確認
執行 `git status -s` 的輸出：
```bash
$ git status -s
# [貼上真實輸出]
```

### 2. 靜態語意檢查
執行語意編譯或 Lint 檢查的輸出：
```bash
$ python -m py_compile [修改的檔案.py]
# [無輸出或顯示編譯成功]
```

### 3. 單元測試執行結果
執行 `pytest` 單元測試的完整輸出：
```bash
$ pytest tests/ -v
# [貼上真實測試輸出，確認 N passed, 0 failed]
```

### 4. 手動端到端（E2E）功能測試
[描述您跑手動 E2E 的實際行為，並貼上關鍵的後端日誌輸出或前端表現]
```
[貼上後端 logger 輸出的關鍵日誌或結果數據]
```

---

## 回退方式 (Rollback)

若本改動在 Production 或 Staging 環境發生非預期缺陷，可透過以下步驟快速且無痛回退：

```bash
# 還原到本次改動前的 Commit
git reset --hard [落地前的 Commit Hash]

# 若已推送到遠端且需要強行覆蓋（請謹慎評估）
# git push origin [branch] --force
```
