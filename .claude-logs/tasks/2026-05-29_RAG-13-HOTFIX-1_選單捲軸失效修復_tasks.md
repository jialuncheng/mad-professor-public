# RAG-13-HOTFIX-1 選單捲軸失效修復 — Tasks

> 本文件為 RAG-13-HOTFIX-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_hotfix.md` 計畫產出，含 1 個 Commit + Check 收官。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `tests/test_rag13_hotfix1_scroll_intercept.py`（scroll 捕獲誤傷防禦測試） |
| **修改檔案** | 1 個 | `static/index.html`（L1622 scroll handler 加 ctx-popup 過濾） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 2 個 | C1 → Check |
| **baton 歸檔** | 1 次 | Check 收官：`mv` baton hotfix_plan → `hotfixes/_v1.0.md` + tasks → `tasks/` + C1/Check 執行 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：RAG-13 C2 上線後，自訂主題超過選單高度產生捲軸時，選單內部滾動觸發全域 `scroll` 捕獲監聽，導致選單立即 `closePopups()`（消失）。用滾輪、觸控板滑動、拖拽捲軸滑塊均重現。
- **解法**：單一 Commit（C1）—— 在全域 scroll listener 回調中插入 `e.target.closest('.ctx-popup')` 過濾，事件源自彈出層內部時直接 `return`，不呼叫 `closePopups()`；同步補一個 pytest 確認 guard 字串存在。
- **影響範圍**：`static/index.html` 1 行改 3 行；新增 pytest 1 個；零後端改動。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `static/index.html` L1622 | `window.addEventListener('scroll', closePopups, true)` | scroll 事件在捕獲階段攔截，無法分辨事件源，彈出層內捲動被誤判關閉 |
| `tests/` | 無 scroll intercept 相關測試 | 需補新增測試防 regression |

---

## §3 觀察問題

### 問題 #1：全域 scroll capture listener 無條件呼叫 closePopups

- **證據**：
  ```bash
  grep -n "addEventListener.*scroll" static/index.html
  # static/index.html:1622:window.addEventListener('scroll', closePopups, true);
  ```
  `L1622` — 第三參數為 `true`（**捕獲階段**），選單 `.ctx-popup` 內部的 `overflow-y: auto` 觸發 scroll 事件時，事件沿 DOM 樹向上冒泡至 window 時同樣被捕獲，無條件觸發 `closePopups()`。

- **影響**：自訂主題超過 5–6 個時選單高度觸頂、出現捲軸；任何滾動操作立即令選單消失，捲軸完全無法使用。

---

## §4 設計方案

### §4.1 C1 — scroll handler 加 ctx-popup 過濾

在 `static/index.html` L1622 將裸回調替換為帶過濾的箭頭函式：

```javascript
// Before (L1622)
window.addEventListener('scroll', closePopups, true);

// After
window.addEventListener('scroll', (e) => {
  // 🟢 RAG-13-HOTFIX-1：若滾動源自彈出選單內部，則忽略，防止誤判關閉
  if (e.target.closest && e.target.closest('.ctx-popup')) return;
  closePopups();
}, true);
```

**設計決策**：
- 只改動 L1622 這 1 行，周邊代碼（L1623 `resize` listener、L1621 注解）完全不動
- `e.target.closest && e.target.closest('.ctx-popup')` 雙重防禦：先檢查 `closest` 是否存在（ES5 相容），再確認事件源是否在 `.ctx-popup` 範疇內
- **不影響主頁面滾動**：當 e.target 為 `.ctx-popup` 外的任何元素時，依舊正常觸發 `closePopups()`

同步新增測試 `tests/test_rag13_hotfix1_scroll_intercept.py`（1 個 pytest）：
- 驗證 `static/index.html` 中舊裸回調 `closePopups, true` 已不存在
- 驗證新的 `e.target.closest('.ctx-popup')` guard 字串存在

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| `closest()` 在老舊瀏覽器不存在 | 🟢 低 | 已加 `e.target.closest &&` 前置檢查；MadPro 目標環境為現代瀏覽器，且 closest 自 2017 已全面支援 |
| 改動位置行號偏移 | 🟢 低 | 以 `grep -n "addEventListener.*scroll.*closePopups"` 動態定位，嚴禁使用計畫行號 |
| 修改後 resize listener 未受影響 | 🟢 無風險 | L1623 `resize` 監聽不在修改範圍，完全不動 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# 1. 確認舊裸回調已移除（應無結果）
grep -n "addEventListener.*scroll.*closePopups, true" static/index.html
# 期望：0 matches

# 2. 確認新 guard 字串已存在
grep -n "e.target.closest.*ctx-popup" static/index.html
# 期望：有命中（L1622 附近）

# 3. 確認 resize listener 未動
grep -n "addEventListener.*resize.*closePopups" static/index.html
# 期望：有命中（L1623）

# 4. 全量 pytest
venv/bin/pytest tests/ --tb=short -q
# 期望：383+ passed（+新增 test），1 pre-existing 失敗（test_bug5）
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **`web_server.py`**：所有後端路由與邏輯 100% 不動
- [ ] **`pipeline_core.py` / `paper_manager.py` / `processor/*.py`**：業務後端不動
- [ ] **L1623 `window.addEventListener('resize', closePopups)`**：不在修復範圍，100% 不動
- [ ] **`closePopups` 函式主體**：函式定義本身不動，只修改呼叫方式
- [ ] **其他所有 `window.addEventListener` 呼叫**：只動 L1622 的 scroll，其餘全不動
- [ ] **主 repo 目錄（worktree 父目錄）**：嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C1 — scroll Intercept Hotfix（選單滾動捕獲誤傷修復）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（修改 L1622 scroll handler）、`.claude-logs/archive/2026-05-29_RAG-13-HOTFIX-1_C1_static_index.html.bak`（備份）、`tests/test_rag13_hotfix1_scroll_intercept.py`（新增） |
| **安全性** | 🟢 高 — 最小侵入式修改，只改動 1 行前端 JS 事件回調；零後端影響；`e.target.closest` 雙重防禦相容性佳 |
| **可逆性** | 🟢 高 — `git revert C1` 完整回退；或 `git checkout -- static/index.html` 直接還原 |
| **驗收 grep 條件** | 見 §6.1：舊裸回調 0 matches + 新 guard 字串 1 match + resize 未動 + pytest 全通過 |
| **依賴關係** | 無前置依賴；可獨立執行 |
| **具體實作細節** | 1. **備份**：`cp static/index.html .claude-logs/archive/2026-05-29_RAG-13-HOTFIX-1_C1_static_index.html.bak`<br>2. **定位**：`grep -n "addEventListener.*scroll.*closePopups, true" static/index.html`，確認 L1622 附近，確認周邊是 `// popup 開啟期間捲動...` 注解（L1621）和 `window.addEventListener('resize', closePopups)` (L1623)<br>3. **修改 `static/index.html`**：將 L1622 整行 `window.addEventListener('scroll', closePopups, true);` 替換為三行：<br>&nbsp;&nbsp;&nbsp;&nbsp;`window.addEventListener('scroll', (e) => {`<br>&nbsp;&nbsp;&nbsp;&nbsp;`  // 🟢 RAG-13-HOTFIX-1：若滾動源自彈出選單內部，則忽略，防止誤判關閉`<br>&nbsp;&nbsp;&nbsp;&nbsp;`  if (e.target.closest && e.target.closest('.ctx-popup')) return;`<br>&nbsp;&nbsp;&nbsp;&nbsp;`  closePopups();`<br>&nbsp;&nbsp;&nbsp;&nbsp;`}, true);`<br>4. **新增測試**：建立 `tests/test_rag13_hotfix1_scroll_intercept.py`，含 2 個 def：(a) `test_scroll_intercept_old_bare_callback_removed`：grep STATIC_HTML 確認 `addEventListener('scroll', closePopups, true)` 已不存在；(b) `test_scroll_intercept_ctx_popup_guard_exists`：grep STATIC_HTML 確認 `e.target.closest('.ctx-popup')` 字串存在<br>5. **執行驗收**：`venv/bin/pytest tests/ --tb=short -q`，確認只有 pre-existing test_bug5 失敗，其他全通過<br>6. **產出 C1 執行報告**：寫入 `.claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_C1_執行.md`（baton 暫存） |

---

### Check — Conformance 驗收與 baton/ 全量歸檔（收官驗收與計畫歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `baton/` 全量 mv → `hotfixes/` + `tasks/` + `executions/`；`TODO.md`；`prompts/INDEX.md`；`prompts/2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md` |
| **安全性** | 🟢 高 — 純文件治理操作，零業務代碼改動 |
| **可逆性** | 🟢 高 — 文件移動可還原 |
| **驗收 grep 條件** | `ls .claude-logs/baton/` 確認無 RAG-13-HOTFIX-1 殘留（只剩 README.md 及其他任務暫存）；`ls .claude-logs/hotfixes/` 確認 `_hotfix_v1.0.md` 存在 |
| **依賴關係** | 依賴 C1 已 baron 手動 commit |
| **具體實作細節** | 1. **提示詞歸檔**：寫入 `prompts/2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md`，更新 `prompts/INDEX.md`<br>2. **Conformance 驗收**：(a) §6.1 四項 grep 均有符合結果；(b) pytest 全通過；(c) 不可動清單 §7 全體 ✅；(d) prompts/ 四階段（Tasks/C1/Check）全實體存在；(e) C1 執行報告 §8 含 msg.txt 草稿<br>3. **baton/ 物理歸檔**：`mv .claude-logs/baton/2026-05-29_RAG-13-HOTFIX-1_hotfix.md .claude-logs/hotfixes/2026-05-29_RAG-13-HOTFIX-1_選單捲軸失效修復_hotfix_v1.0.md` / `mv .claude-logs/baton/..._tasks.md .claude-logs/tasks/` / `mv .claude-logs/baton/..._C1_執行.md .claude-logs/executions/` / `mv .claude-logs/baton/..._Check_執行.md .claude-logs/executions/`<br>4. **git add 清單**：上述所有 mv 目的地檔案 + `TODO.md` + `prompts/INDEX.md` + `prompts/2026-05-29_RAG-13-HOTFIX-1_Check_提示詞.md`<br>5. **TODO.md 結案**：RAG-13-HOTFIX-1 移入已完成表格，Hash 回填，從進行中移除，索引標記 ✅ |

---

## §9 Open Questions

無。（hotfix 修法已在 plan 中確認，baron 拍板採用 `e.target.closest` 過濾方案。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RAG-13-HOTFIX-1 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 RAG-13-HOTFIX-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混合不同優先級文件；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | hotfix 計畫規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 hotfix.md 中的診斷脈絡，不重複 CLAUDE.md 中的全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-05-29)：初版拆分完成（hotfix.md 拍板後，1 Commit + Check 架構）
