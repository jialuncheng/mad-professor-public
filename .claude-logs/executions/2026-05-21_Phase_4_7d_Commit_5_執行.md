# Phase 4.7d Commit 5 — 執行報告（多檔同時上傳）

> 基準：`2b9aed6`（Phase 4.7d Commit 4-2）
> 完成：1 commit 本地建立完成，**未 push**

---

## Commit Hash

| # | Hash | Subject |
|---|---|---|
| 5 | `b277d87` | feat(frontend): 多檔同時上傳（Phase 4.7d Commit 5） |

---

## diff stat

```
 design/docs/copywriting.md | 14 ++++++++++++
 static/index.html          | 54 ++++++++++++++++++++++++++--------------------
 2 files changed, 45 insertions(+), 23 deletions(-)
```

純前端 + design spec 補。後端 / DB / pipeline / processor / modal 結構 / 既有 schema **全部未動**。

---

## 真因

後端早已支援並行處理多 paper：
- `web_server.run_pipeline` 用 `asyncio.run_in_executor`
- `tasks_lock` 只鎖 dict、不鎖 pipeline
- `PipelineCore` 每次新 instance、無共享 state

唯一限制是前端 `<input type="file">` 沒 `multiple` 屬性 → 使用者一次只能選一份。

---

## 改動

### static/index.html

#### 1. file input 多檔
```js
input.multiple = true;
```

#### 2. change handler 改為 for-loop + await
- `Array.from(e.target.files || [])`
- `for (const file of files)`
- 每份：upload → `await new Promise(resolve => showConfirmModal(..., resolve))`
- 失敗只 alert 該檔名、不中斷整批

#### 3. showConfirmModal 簽名擴充
- 加第 5 參數 `onConfirmed` (optional callback)
- `finally { if (typeof onConfirmed === 'function') onConfirmed() }`
- 既有單檔 caller 不傳此參數、行為等效

#### 4. btn / setBusy 策略
- 進入 for-loop 前 `btn.disabled = true; setBusy(true)`
- **不主動** unlock — 交由各檔 `trackProgress` 完成時自行 unlock（與單檔行為一致；首個完成的 paper 解鎖 btn 即可繼續上傳）

#### 5. Help modal 文案
追加第 6 條：「可同時上傳多份文件」

### design/docs/copywriting.md §6.1.1

新增「文件上傳流程說明」段：6 步驟列表 + 互動契約「confirm modal **逐檔跳出**，不批次選 doc_type，每份 modal 確認後才彈下一份；占位列依序加入左欄頂端」。

---

## 不可動清單（已遵守）

- [x] 後端 `web_server.py`：未動
- [x] `pipeline_core` / processor：未動
- [x] DB schema：未動
- [x] modal 設計 / dropdown：未動（只動 input multiple + handler loop）
- [x] `.paper-item.uploading` 占位列邏輯：保留
- [x] 100 MB 上限檢查：保留
- [x] 既有錯誤處理：保留
- [x] 未引入新 CDN / 套件

---

## 端到端驗證計畫（給 baron）

### 1. 確認 commits

```bash
git log --oneline -3
# 應看到：
# b277d87（Commit 5）/ 2b9aed6（Commit 4-2）/ 9bba1f7（Commit 4-1）
```

### 2. push

```bash
git push origin HEAD:gemini-refactor
```

### 3. OrcStack

```bash
git pull
pkill -f web_server
# 重啟
venv/bin/pytest tests/ -q   # 應 70 passed 3 skipped
```

### 4. Test A — 單檔上傳（回歸）

- 點 upload → 選 1 份 PDF
- 預期：confirm modal 跳一次、確認後占位列加入、SSE 追進度
- 行為與既有單檔流程**等效**

### 5. Test B — 多檔上傳

- 點 upload → 選 3 份 PDF（按 Ctrl/Cmd + 點擊多選）
- 預期：
  1. 第 1 份 confirm modal 跳出、選 doc_type、確認
  2. **modal 自動關閉**，左欄頂端加入第 1 份占位列
  3. 第 2 份 confirm modal 跳出、選 doc_type、確認
  4. 加入第 2 份占位列（在第 1 份下面 / 上面依 insertUploadingRow 邏輯）
  5. 第 3 份 同上
- 後端：3 份 paper 並行跑 pipeline（看 `logs/pipeline.log` 應有 3 個 paper_id 交錯 log）

### 6. Test C — 多檔中某份失敗

- 選 2 份 PDF，其中 1 份故意超過 100 MB（或損壞）
- 預期：失敗那份顯示「上傳「{filename}」失敗：...」alert、**不中斷另一份**繼續處理

### 7. console / logs（不應出現）

- `Cannot read property 'files' of null`
- `TypeError: onConfirmed is not a function`
- modal 重疊（同時開兩個 confirm-modal）

---

## 回退方式

```bash
git revert b277d87 --no-edit
# 或硬退：
git reset --hard 2b9aed6
```

---

## 全 worktree 待 push 總覽

| 群 | commits |
|---|---|
| Stage A chat stateless | 4 |
| MinerU 模組化方案 X | 5 |
| Phase 4.7c metadata 顯示 | 5 |
| Phase 4.7c 修正 1-4 | 4 |
| Phase 4.7d Commit 0 + 1 | 2 |
| Phase 4.7d Commit 2 + 3 | 2 |
| Phase 4.7d Commit 4-1 + 4-2 | 2 |
| **Phase 4.7d Commit 5** | **1** |
| **合計** | **25** |

---

## 狀態

**1 commit 已建立、未 push、等 baron 跑完 Test A/B/C 後一起 push。**
