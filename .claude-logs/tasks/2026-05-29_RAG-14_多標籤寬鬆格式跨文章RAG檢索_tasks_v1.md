# RAG-14 多標籤寬鬆格式跨文章 RAG 檢索與對話體驗升級 — Tasks v1

> 本文件為 RAG-14 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-29_RAG-14_多標籤寬鬆格式跨文章RAG檢索_plan_v3.md` 計畫產出，含 3 個 Commit（C1 + C2 + Check）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `tests/test_rag14_c1_css_and_filter.py` / `tests/test_rag14_c2_dom_structure.py` |
| **修改檔案** | 1 個 | `static/index.html`（CSS 氣泡滿寬 + Sticky + QA-group + sendMessage × 過濾 + loadChatHistory DOM 重構） |
| **備份檔案** | 2 個 | `.claude-logs/archive/2026-05-30_RAG-14_C1_static_index.html.bak` / `.claude-logs/archive/2026-05-30_RAG-14_C2_static_index.html.bak` |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 1 個 | `TODO.md`（RAG-14 WIP 條目 + 結案歸檔） |
| **Commits** | 3 個 | C1 → C2 → Check |
| **baton 歸檔** | 1 次 | Check 收官：`mv` baton plan_v3 → `plans/` + tasks_v1 → `tasks/` + C1/C2/Check _執行.md → `executions/` + `git add` |

> **已落地（Tasks 開始前已完成）**：
> - `paper_manager.py` L956：`def parse_query_hashtags` 已新增
> - `AI_professor_chat.py` L76–L137：P2-2 多標籤路由已完整替換，含 `exc_info=True`
> - `tests/test_phase2_p2_2_hashtag_routing.py`：L302 / L329 / L371 三處 mock 已更新為 `parse_query_hashtags`；`test_parse_query_hashtags_combinations`（L391, 6 scenarios）已新增

---

## §1 TL;DR（概要）

- **挑戰**：後端多標籤解析（plan §7 後端修改處 1/2）與測試升級（plan §7 測試修改處 1）已於 Tasks 開始前全數落地。剩餘工作為**前端三項改動**：① `sendMessage` × 字元過濾、② CSS 氣泡滿寬 + `.qa-group` + Sticky 置頂、③ `loadChatHistory` QA-group DOM 重構（含 `in_progress` currentGroup 沿用）
- **解法**：
  - **C1** — FE CSS 氣泡滿寬 + sendMessage × 過濾（視覺對齊與輸入淨化）：CSS 4 項變更 + `sendMessage` query 提取改 clone 去 × 按鈕模式；新增靜態 pytest 4 個
  - **C2** — FE loadChatHistory + sendMessage QA-group DOM 重構（Sticky 容器架構）：`loadChatHistory` history.forEach → qa-group；in_progress → `currentGroup.appendChild`；`sendMessage` → qa-group 包裝；新增靜態 pytest 3 個
  - **Check** — Conformance 驗收 + baton 全量歸檔 + TODO.md 結案
- **影響範圍**：FE-Refactor + 單元測試新增，零後端業務邏輯改動、零 schema 變動
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 待處理 |
|---|---|---|
| `static/index.html` L3224 | `const query = (input.textContent \|\| '').trim();` | 改為 clone + remove `.hashtag-token-remove` |
| `static/index.html` L916-926 `.msg-user` | `align-self: flex-end; max-width: 75%;` | 改 stretch + 100% + sticky |
| `static/index.html` L938-948 `.msg-ai` | `align-self: flex-start; max-width: 90%;` | 改 stretch + 100% |
| `static/index.html` L914 `#chat-messages` | `gap: var(--space-4);` | 改 `var(--space-6)`；新增 `.qa-group` CSS block |
| `static/index.html` L2872-2887 `loadChatHistory` forEach | 平鋪 `messages.appendChild(div)` | 包裝成 `currentGroup` qa-group 結構 |
| `static/index.html` L2893-2903 `in_progress` | `messages.appendChild(aiMsg)` | 改 `if (currentGroup) currentGroup.appendChild(aiMsg); else messages.appendChild(aiMsg)` |
| `static/index.html` L3231-3243 `sendMessage` | `messages.appendChild(userMsg)` + `messages.appendChild(aiMsg)` | 改 qaGroup 包裝再 append |
| `paper_manager.py` L956 | `def parse_query_hashtags` **已存在** | ✅ 無需改動 |
| `AI_professor_chat.py` L76-137 | P2-2 多標籤路由 **已落地** | ✅ 無需改動 |
| `tests/test_phase2_p2_2_hashtag_routing.py` L302/329/371/391 | mock 已更新；combinations test 已新增 | ✅ 無需改動 |

---

## §3 觀察問題

### 問題 #1：`×` 字元混入送出內容
- **證據**：`static/index.html:3224: const query = (input.textContent || '').trim();`
- **影響**：hashtag token 的刪除按鈕 `×` 被包含在 textContent 中，形成 `#sstx` 送至後端

### 問題 #2：氣泡寬度不對稱
- **證據**：`static/index.html:924: max-width: 75%;` / `static/index.html:947: max-width: 90%;`
- **影響**：問與答泡泡左右邊界不齊，視覺不整齊

### 問題 #3：提問泡泡在長回答時滑出視窗
- **證據**：`static/index.html:2872-2887`：history.forEach 無 qa-group 包裝
- **影響**：無法實現 `position: sticky` 提問置頂效果

### 問題 #4：`in_progress` DOM 結構不一致
- **證據**：`static/index.html:2903: messages.appendChild(aiMsg);`（直接附加到 messages，不在 qa-group）
- **影響**：F5 reload 時 in_progress AI 回覆未與 user message 同組，破壞 sticky 效果

---

## §4 設計方案

### §4.1 C1 — FE CSS 氣泡滿寬 + sendMessage × 過濾

修改 `static/index.html`（4 項 CSS + 1 項 JS）：

1. **`#chat-messages`（L914）**：`gap: var(--space-4)` → `gap: var(--space-6)`（外層群組間距）
2. **`.msg-user`（L916）**：移除 `align-self: flex-end; max-width: 75%;`；補入 `align-self: stretch; max-width: 100%; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);`
3. **`.msg-ai`（L938）**：移除 `align-self: flex-start; max-width: 90%;`；補入 `align-self: stretch; max-width: 100%;`
4. **新增 `.qa-group` CSS block**（插入在 `.msg-user` 區塊後）：
   ```css
   .qa-group {
     position: relative;
     display: flex;
     flex-direction: column;
     gap: var(--space-4);
     margin-bottom: var(--space-3);
   }
   ```
5. **`sendMessage`（L3224）**：`const query = (input.textContent || '').trim();` → clone node 去 × 後取 textContent

### §4.2 C2 — FE loadChatHistory + sendMessage QA-group DOM 重構

修改 `static/index.html`（3 項 JS）：

1. **`loadChatHistory` history.forEach（L2872-2887）**：在迴圈前加 `let currentGroup = null;`；user message 時先建 `.qa-group` div 並 `messages.appendChild(currentGroup)`；所有 div 改 append 到 `currentGroup`
2. **`loadChatHistory` in_progress（L2893-2903）**：移除 `messages.appendChild(aiMsg)`；改為 `if (currentGroup) currentGroup.appendChild(aiMsg); else messages.appendChild(aiMsg);`
3. **`sendMessage` append block（L3231-3243）**：在 `messages.appendChild(userMsg)` 前建立 `qaGroup` div；`messages.appendChild(qaGroup)`；`qaGroup.appendChild(userMsg)`；`qaGroup.appendChild(aiMsg)`；移除原 `messages.appendChild(userMsg)` 和 `messages.appendChild(aiMsg)`

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| `position: sticky` 在 flex 容器內不生效 | 🟡中 | 確認 `#chat-messages` 有 `overflow-y: auto`（L910 已確認）；`.qa-group` 無 overflow 設定，sticky 可向上穿透到 messages 滾動容器 |
| `sendMessage` clone 邏輯改動後 `query` 為空 | 🟢低 | clone+removeChildren 後 `textContent.trim()` 仍依賴 token span 的 textContent；hashtag token span 的 textContent 為 `#tag`（不含 ×）；× 僅在 `.hashtag-token-remove` 按鈕中，移除後剩餘文字正確 |
| `loadChatHistory` qa-group 包裝破壞 grounding sources render | 🟢低 | `renderSources(div, ...)` 仍操作 div（msg-ai），只是 div 的 parent 從 messages 改為 currentGroup；函式不依賴 parent，無影響 |
| 現有 pytest grep tests 對 `msg-user` 樣式有硬斷言 | 🟡中 | 執行 C1 前先確認（`grep -n "align-self: flex-end\|max-width: 75%" tests/`）；如有則在 C1 同步更新 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# 1. CSS sticky 與 stretch 存在
grep -n "position: sticky" static/index.html
# 期望：有命中（.msg-user block 內）

grep -n "align-self: stretch" static/index.html
# 期望：≥ 2 命中（.msg-user + .msg-ai）

grep -n "\.qa-group" static/index.html
# 期望：有命中（CSS block）

# 2. sendMessage × 過濾邏輯
grep -n "cloneNode" static/index.html
# 期望：sendMessage 內有 cloneNode(true) 命中

grep -n "hashtag-token-remove.*remove\|querySelectorAll.*hashtag-token-remove" static/index.html
# 期望：sendMessage 內有命中

# 3. 舊樣式已移除
grep -n "align-self: flex-end" static/index.html
# 期望：0 命中（確認已刪）

# 4. pytest
venv/bin/pytest tests/test_rag14_c1_css_and_filter.py -v
```

### §6.2 C2 驗收

```bash
# 1. currentGroup 與 qa-group JS 存在
grep -n "currentGroup" static/index.html
# 期望：loadChatHistory + sendMessage 內有多處命中

grep -n "qa-group" static/index.html
# 期望：CSS block + loadChatHistory + sendMessage 內有命中

# 2. in_progress 沿用 currentGroup
grep -n "currentGroup\.appendChild" static/index.html
# 期望：in_progress block 內有命中

# 3. messages.appendChild 不在 forEach / in_progress 中（已移到 qa-group）
# 手動確認 loadChatHistory 中 messages.appendChild 僅用於 qaGroup 或 fallback

# 4. pytest
venv/bin/pytest tests/test_rag14_c2_dom_structure.py -v
venv/bin/pytest tests/ -x --tb=short -q  # 全量回歸
```

---

## §7 不可動清單

明確劃定修改邊界。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `paper_manager.py` 中的 `parse_query_hashtag`（單數，deprecated 保留）與 `_normalize_tag`
- [ ] `AI_professor_chat.py` 中的 `_prepare_final_messages` 核心 Prompt 封裝邏輯
- [ ] `rag_retriever.py` 中的 `retrieve_multi_with_context`
- [ ] 既有的 `/api/papers/{paper_id}/chat` 請求 Schema（`ChatRequest`）
- [ ] `tests/test_phase2_p2_2_hashtag_routing.py`（已更新完畢，本次不再改動）
- [ ] 主 repo 目錄（嚴禁讀寫 worktree 父目錄）

---

## §8 推薦 Commit 拆分

### C1 — FE CSS 氣泡滿寬 + sendMessage × 過濾（前端視覺對齊與輸入淨化）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（CSS 4 項 + sendMessage JS 1 項） / `tests/test_rag14_c1_css_and_filter.py`（新增）/ `.claude-logs/archive/2026-05-30_RAG-14_C1_static_index.html.bak`（備份） |
| **安全性** | 🟢 高 — 僅改 CSS 樣式屬性與 JS query 提取邏輯；不改任何 API 呼叫或資料流 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；.bak 備份可輔助手動還原 |
| **驗收 grep 條件** | 見 §6.1 |
| **依賴關係** | 無前置；C2 依賴本 Commit |
| **具體實作細節** | **Step 1**：備份 `cp static/index.html .claude-logs/archive/2026-05-30_RAG-14_C1_static_index.html.bak`<br><br>**Step 2**：確認現有 pytest 是否有 `align-self: flex-end` 或 `max-width: 75%` 的斷言：`grep -rn "flex-end\|75%" tests/`；若有則同步更新<br><br>**Step 3**：修改 `static/index.html` CSS — `#chat-messages`（L908 block）：`gap: var(--space-4)` → `gap: var(--space-6)`<br><br>**Step 4**：修改 `static/index.html` CSS — `.msg-user`（L916 block）：<br>- 移除 `align-self: flex-end;`<br>- 移除 `max-width: 75%;`<br>- 補入（在現有屬性後）：`align-self: stretch;` / `max-width: 100%;` / `position: sticky;` / `top: 0;` / `z-index: 10;` / `box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);`<br><br>**Step 5**：修改 `static/index.html` CSS — `.msg-ai`（L938 block）：<br>- 移除 `align-self: flex-start;`<br>- 移除 `max-width: 90%;`<br>- 補入：`align-self: stretch;` / `max-width: 100%;`<br><br>**Step 6**：在 `static/index.html` CSS 中，在 `.msg-user` block 結束後（`}` 之後）插入新 `.qa-group` CSS block：<br>```css<br>  .qa-group {<br>    position: relative;<br>    display: flex;<br>    flex-direction: column;<br>    /* 內層 gap：問與答泡泡之間的垂直間距 */<br>    gap: var(--space-4);<br>    margin-bottom: var(--space-3);<br>  }<br>```<br><br>**Step 7**：修改 `static/index.html` JS — `sendMessage`（L3224 附近）：<br>將 `const query = (input.textContent \|\| '').trim();`<br>替換為：<br>```javascript<br>const tempDiv = input.cloneNode(true);<br>tempDiv.querySelectorAll('.hashtag-token-remove').forEach(btn => btn.remove());<br>const query = (tempDiv.textContent \|\| '').trim();<br>```<br><br>**Step 8**：建立 `tests/test_rag14_c1_css_and_filter.py`，內含 4 個靜態 grep 測試：<br>- `test_msg_user_has_sticky_positioning`：assert `'position: sticky'` in STATIC_HTML<br>- `test_msg_user_msg_ai_have_stretch_width`：assert `'align-self: stretch'` in STATIC_HTML（count ≥ 2）<br>- `test_qa_group_css_block_exists`：assert `'.qa-group'` in STATIC_HTML<br>- `test_sendmessage_filters_hashtag_token_remove`：assert `'cloneNode(true)'` in STATIC_HTML and `"querySelectorAll('.hashtag-token-remove')"` in STATIC_HTML<br><br>**Step 9**：`git add` 清單（baton 執行報告嚴禁在此列入）：<br>`static/index.html` / `tests/test_rag14_c1_css_and_filter.py` / `.claude-logs/archive/2026-05-30_RAG-14_C1_static_index.html.bak` |

---

### C2 — FE loadChatHistory + sendMessage QA-group DOM 重構（前端 Sticky 容器架構）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（loadChatHistory JS + sendMessage JS）/ `tests/test_rag14_c2_dom_structure.py`（新增）/ `.claude-logs/archive/2026-05-30_RAG-14_C2_static_index.html.bak`（備份） |
| **安全性** | 🟡 中 — DOM 結構調整影響對話歷史渲染方式；需確認 grounding sources、copy 按鈕等依賴 DOM 結構的功能不受影響 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾；.bak 備份可輔助手動還原 |
| **驗收 grep 條件** | 見 §6.2 |
| **依賴關係** | 必須在 C1 之後執行（依賴 `.qa-group` CSS 已存在） |
| **具體實作細節** | **Step 1**：備份 `cp static/index.html .claude-logs/archive/2026-05-30_RAG-14_C2_static_index.html.bak`<br><br>**Step 2**：修改 `static/index.html` JS — `loadChatHistory` 的 `history.forEach` 區塊（L2872 附近）：<br>在 `history.forEach(msg => {` 前加：<br>```javascript<br>let currentGroup = null;<br>```<br>在 forEach 函式體內，在 `const div = document.createElement('div');` 前插入：<br>```javascript<br>if (msg.role === 'user') {<br>  currentGroup = document.createElement('div');<br>  currentGroup.className = 'qa-group';<br>  messages.appendChild(currentGroup);<br>}<br>```<br>將 forEach 結尾的 `messages.appendChild(div);` 改為：<br>```javascript<br>if (currentGroup) currentGroup.appendChild(div);<br>else messages.appendChild(div);<br>```<br><br>**Step 3**：修改 `static/index.html` JS — `loadChatHistory` 的 `in_progress` 區塊（L2903 附近）：<br>將 `messages.appendChild(aiMsg);`<br>替換為：<br>```javascript<br>if (currentGroup) {<br>  currentGroup.appendChild(aiMsg);<br>} else {<br>  messages.appendChild(aiMsg);<br>}<br>```<br><br>**Step 4**：修改 `static/index.html` JS — `sendMessage` 的 append 區塊（L3231-3243 附近）：<br>在 `const messages = document.getElementById('chat-messages');` 之後、`const userMsg = document.createElement('div');` 之前插入：<br>```javascript<br>const qaGroup = document.createElement('div');<br>qaGroup.className = 'qa-group';<br>messages.appendChild(qaGroup);<br>```<br>將 `messages.appendChild(userMsg);` 改為 `qaGroup.appendChild(userMsg);`<br>將 `messages.appendChild(aiMsg);`（建立 aiMsg 後的那行）改為 `qaGroup.appendChild(aiMsg);`<br><br>**Step 5**：建立 `tests/test_rag14_c2_dom_structure.py`，內含 3 個靜態 grep 測試：<br>- `test_loadchathistory_uses_currentgroup_for_qa_group`：assert `'currentGroup = document.createElement' ` in STATIC_HTML and `"currentGroup.className = 'qa-group'"` in STATIC_HTML<br>- `test_inprogress_reuses_currentgroup`：assert `'currentGroup.appendChild(aiMsg)'` in STATIC_HTML（確認 in_progress block 改用 currentGroup）<br>- `test_sendmessage_wraps_in_qa_group`：assert `"qaGroup.className = 'qa-group'"` in STATIC_HTML and `'qaGroup.appendChild(userMsg)'` in STATIC_HTML<br><br>**Step 6**：全量 pytest 確認 0 regression：`venv/bin/pytest tests/ -x --tb=short -q`<br><br>**Step 7**：`git add` 清單：<br>`static/index.html` / `tests/test_rag14_c2_dom_structure.py` / `.claude-logs/archive/2026-05-30_RAG-14_C2_static_index.html.bak` |

---

### Check — Conformance 驗收與 baton 全量歸檔（收官）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `.claude-logs/plans/`（plan_v3 歸檔）/ `.claude-logs/tasks/`（tasks_v1 歸檔）/ `.claude-logs/executions/`（C1 + C2 + Check 執行報告歸檔）/ `TODO.md`（RAG-14 結案） |
| **安全性** | 🟢 高 — 純文件搬移與狀態更新，零業務代碼改動 |
| **可逆性** | 🟢 高 — `git revert Check` 還原文件搬移 |
| **驗收 grep 條件** | `ls .claude-logs/plans/2026-05-29_RAG-14*` / `ls .claude-logs/tasks/2026-05-29_RAG-14*` / `grep "✅.*RAG-14" TODO.md` |
| **依賴關係** | 必須在 C1 + C2 全部 ship 後執行 |
| **具體實作細節** | **Step 1**：5 維度 Conformance 驗收（目標規格 / 驗收條件 / 不可動清單 / 提示詞歸檔 / commit msg 草稿）<br><br>**Step 2**：將 baton 暫存文件搬移至正式目錄：<br>```bash<br>mv .claude-logs/baton/2026-05-29_RAG-14_多標籤寬鬆格式跨文章RAG檢索_plan_v3.md \<br>   .claude-logs/plans/2026-05-29_RAG-14_多標籤寬鬆格式跨文章RAG檢索_plan_v3.md<br>mv .claude-logs/baton/2026-05-29_RAG-14_多標籤寬鬆格式跨文章RAG檢索_tasks_v1.md \<br>   .claude-logs/tasks/2026-05-29_RAG-14_多標籤寬鬆格式跨文章RAG檢索_tasks_v1.md<br>mv .claude-logs/baton/2026-05-30_RAG-14_C1_執行.md \<br>   .claude-logs/executions/2026-05-30_RAG-14_C1_執行.md<br>mv .claude-logs/baton/2026-05-30_RAG-14_C2_執行.md \<br>   .claude-logs/executions/2026-05-30_RAG-14_C2_執行.md<br>mv .claude-logs/baton/2026-05-30_RAG-14_Check_執行.md \<br>   .claude-logs/executions/2026-05-30_RAG-14_Check_執行.md<br>```<br><br>**Step 3**：`git add` 以上所有已 mv 的檔案<br><br>**Step 4**：更新 `TODO.md`：<br>- 將 RAG-14 active 條目移除（含 WIP: C1 / ⬜ C2 / ⬜ Check）<br>- 在 `## ✅ 已完成` 新增 RAG-14 表格（含 C1 hash / C2 hash / Check hash）<br>- 更新 `## 索引（依類別）` 中 RAG-14 狀態為 ✅<br>- baron 手動回填 Check commit hash<br><br>**Step 5**：寫 commit message 草稿至 `/tmp/RAG-14_Check_msg.txt` |

---

## §9 Open Questions

無。（plan_v3 已通過三輪評估，所有規格已拍板）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RAG-14 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混合不同優先級文件；嚴禁自動 `git commit` / `git push`；baton/ 執行報告嚴禁在 Run 階段 git add，只能在 Check 一次性歸檔 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複計畫書中的設計脈絡，不重複 CLAUDE.md 中的全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-05-30)：初版拆分完成；現況盤點確認後端（paper_manager.py / AI_professor_chat.py / tests 三處）已全部落地；tasks 範圍收斂為 static/index.html 前端 3 項改動（CSS + sendMessage × 過濾 + loadChatHistory QA-group DOM）拆成 C1 + C2 + Check
