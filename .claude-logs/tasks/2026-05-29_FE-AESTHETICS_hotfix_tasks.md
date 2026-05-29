# FE-AESTHETICS HOTFIX-1 前端學術扉頁自癒與排版靠左優化 — Tasks

> 本文件為 FE-AESTHETICS HOTFIX-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix.md`（v1.2）計畫產出，含 1 個 Commit + Check 收官。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `tests/test_fe_aesthetics_c2_hotfix.py`（新建靜態 JS 測試）/ `.claude-logs/archive/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_static_index.html.bak`（備份）/ `.claude-logs/archive/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_test_bug_f1.bak`（備份） |
| **修改檔案** | 2 個 | `static/index.html`（CSS 對齊靠左 + normalizeAcademicHeader JS）/ `tests/test_bug_f1_frontend_micro_fix.py`（test_bug5 斷言 #current-title → #abstract-toolbar）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 2 個 | C2-hotfix → Check |
| **baton 歸檔** | 1 次 | Check 收官：`mv` baton hotfix.md → `hotfixes/` + tasks.md → `tasks/` + 執行報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：FE-AESTHETICS C2 解鎖 `.paper-header-meta` 螢幕顯示後，歷史論文（舊單行格式 / 舊 dash-list 格式）的 Markdown 已固化於後端儲存，前端無自癒機制，與新 CSS 碰撞後排版爆版。同時 test_bug5 的斷言仍指向舊容器 `#current-title`（應為 `#abstract-toolbar`），導致 pre-existing 失敗。
- **解法**：單一 Commit（C2-hotfix）—— ① CSS `.paper-header-meta` 對齊改靠左斷行；② 新增 `normalizeAcademicHeader()` 前端自癒函數（含 Guard clause 防誤傷新格式）並在 `fetchContent` 中調用；③ 修正 `test_bug_f1` 舊斷言自癒 pre-existing 失敗；④ 新建 `test_fe_aesthetics_c2_hotfix.py` 靜態防線。
- **影響範圍**：`static/index.html`（CSS 2 行 + JS 新增約 55 行）/ `tests/test_bug_f1_frontend_micro_fix.py`（2 行斷言更新）/ 新增 1 測試檔；零後端改動。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `static/index.html` L814 | `align-items: center;` | 需改為 `flex-start` |
| `static/index.html` L815 | `text-align: center;` | 需改為 `left` |
| `static/index.html` L2696 | `marked.parse(content)` 後直接渲染，無自癒 | 需在渲染後呼叫 `normalizeAcademicHeader()` |
| `static/index.html` L2697–L2698 | `fetchContent` 閉合括號後 | 需插入 `normalizeAcademicHeader()` 函式定義 |
| `tests/test_bug_f1_frontend_micro_fix.py` L129, L135 | `#current-title` 斷言 | FE-AESTHETICS C2 後容器已改為 `#abstract-toolbar`，造成 pre-existing 失敗 |
| `tests/test_fe_aesthetics_c2_hotfix.py` | 不存在 | 需新建靜態防線測試 |

---

## §3 觀察問題

### 問題 #1：歷史論文 .paper-header-meta 格式與新 CSS 衝突

- **證據**：
  ```bash
  grep -n "align-items: center\|text-align: center" static/index.html | awk -F: '$1>=811 && $1<=820'
  # 814:  align-items: center;
  # 815:  text-align: center;
  ```
  舊單行論文（所有 meta 連成一行）與舊 dash-list 論文（`<ul>/<li>` 帶圓點），在 `display:flex; align-items:center` 下排版爆版。

- **影響**：所有 FE-AESTHETICS C2 前已上傳的學術論文扉頁，前端顯示破碎。

### 問題 #2：test_bug5 pre-existing 失敗（#current-title 斷言未隨 C2 更新）

- **證據**：
  ```bash
  grep -n "current-title.*details" tests/test_bug_f1_frontend_micro_fix.py
  # 129:    r'#current-title\s+details\.title-abstract\s*\{[^}]*width:\s*100%',
  # 135:    r'#current-title\s+details\.title-abstract\s*\{[^}]*box-sizing:\s*border-box',
  ```
  FE-AESTHETICS C2 將 `#current-title details.title-abstract` 移至 `#abstract-toolbar details.title-abstract`，但測試未同步更新。

---

## §4 設計方案

### §4.1 C2-hotfix — 學術扉頁自癒與排版靠左優化

**修改 1：`static/index.html` L814–815 CSS 對齊靠左**

```diff
-   align-items: center;
-   text-align: center;
+   align-items: flex-start;
+   text-align: left;
```

**修改 2：`fetchContent` 內（L2696 後）加 `normalizeAcademicHeader()` 呼叫**

```diff
  document.getElementById('paper-content').innerHTML = marked.parse(content);
+ normalizeAcademicHeader(); // FE-AESTHETICS HOTFIX-1：學術扉頁自癒
}
```

**修改 3：`fetchContent` 下方新增函式定義**

```javascript
function normalizeAcademicHeader() {
  const metaEl = document.querySelector('#paper-content .paper-header-meta');
  if (!metaEl) return;

  // 🟢 Guard：若已含新格式 class divs（C1 後端正確渲染），直接跳過，防止誤傷
  if (metaEl.querySelector('.header-authors, .header-venue-date, .header-doi, .header-keywords')) return;

  const rawText = metaEl.textContent.trim();

  function extractField(text, labels) {
    for (const label of labels) {
      const pattern = new RegExp(
        label + '\\s*[:：]\\s*([\\s\\S]*?)(?=\\s*(?:作者|Authors|日期|Date|出處|Venue|DOI|關鍵字|Keywords|$))',
        'i'
      );
      const match = text.match(pattern);
      if (match) return match[1].trim().replace(/^[:：]\s*/, '').trim();
    }
    return '';
  }

  const authorsVal = extractField(rawText, ['作者', 'Authors']);
  const dateVal    = extractField(rawText, ['日期', 'Date']);
  const venueVal   = extractField(rawText, ['出處', 'Venue']);
  const doiVal     = extractField(rawText, ['DOI']);
  const keywordsVal = extractField(rawText, ['關鍵字', 'Keywords']);

  if (!authorsVal && !dateVal && !venueVal && !doiVal && !keywordsVal) return;

  const htmlBits = [];
  if (authorsVal) htmlBits.push(`  <div class="header-authors">${authorsVal}</div>`);
  const venueDateBits = [];
  if (venueVal) venueDateBits.push(venueVal);
  if (dateVal)  venueDateBits.push(dateVal);
  if (venueDateBits.length) htmlBits.push(`  <div class="header-venue-date">${venueDateBits.join(' · ')}</div>`);
  if (doiVal)      htmlBits.push(`  <div class="header-doi">DOI: ${doiVal}</div>`);
  if (keywordsVal) {
    const isZh = rawText.includes('關鍵字') || keywordsVal.includes('、');
    htmlBits.push(`  <div class="header-keywords">${isZh ? '關鍵字：' : 'Keywords: '}${keywordsVal}</div>`);
  }
  metaEl.innerHTML = htmlBits.join('\n');
}
```

**修改 4：`tests/test_bug_f1_frontend_micro_fix.py` L129 + L135 斷言自癒**

```diff
-   r'#current-title\s+details\.title-abstract\s*\{[^}]*width:\s*100%',
+   r'#abstract-toolbar\s+details\.title-abstract\s*\{[^}]*width:\s*100%',
...
-   r'#current-title\s+details\.title-abstract\s*\{[^}]*box-sizing:\s*border-box',
+   r'#abstract-toolbar\s+details\.title-abstract\s*\{[^}]*box-sizing:\s*border-box',
```

**新增 5：`tests/test_fe_aesthetics_c2_hotfix.py`**

```python
"""FE-AESTHETICS HOTFIX-1 專屬靜態測試"""
from pathlib import Path

STATIC_HTML = (Path(__file__).parent.parent / 'static' / 'index.html').read_text(encoding='utf-8')


def test_hotfix_normalize_academic_header_function_exists():
    """HOTFIX-1：index.html 應定義 normalizeAcademicHeader 自癒函數"""
    assert 'function normalizeAcademicHeader' in STATIC_HTML, \
        '應在 index.html 內定義 normalizeAcademicHeader 自癒相容函數'
    assert 'normalizeAcademicHeader()' in STATIC_HTML, \
        '應在 fetchContent 中調用 normalizeAcademicHeader()'
```

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| Guard clause 漏判新格式 | 🟢 低 | `querySelector('.header-authors, .header-venue-date, .header-doi, .header-keywords')` 覆蓋全部 C1 輸出 class |
| 歷史舊格式提取 regex 漏欄位 | 🟢 低 | 每個欄位獨立提取；全欄皆空則 early return，保持原樣 |
| CSS 靠左影響簡歷 / Slides 扉頁 | 🟢 低 | 非學術論文無 `.paper-header-meta`，不受影響 |
| test_bug_f1 斷言改錯容器 | 🟢 低 | `#abstract-toolbar` 已由 FE-AESTHETICS C2 確認存在 |

---

## §6 測試計畫

### §6.1 C2-hotfix 驗收

```bash
# 1. CSS 已靠左（0 matches = 已改）
grep -n "align-items: center\|text-align: center" static/index.html | awk -F: '$1>=811 && $1<=820'
# 期望：0 matches

# 2. normalizeAcademicHeader Guard clause 存在
grep -n "querySelector.*header-authors.*header-venue-date" static/index.html
# 期望：有命中

# 3. fetchContent 內呼叫存在
grep -n "normalizeAcademicHeader()" static/index.html
# 期望：有命中（fetchContent 體內 + 函式定義合計 ≥2 matches）

# 4. test_bug_f1 舊斷言已移除
grep -n "current-title.*details" tests/test_bug_f1_frontend_micro_fix.py
# 期望：0 matches

# 5. 全量 pytest（目標：387 passed, 0 failed, 3 skipped）
venv/bin/pytest tests/ --tb=short -q
```

---

## §7 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] **`web_server.py`**：所有後端路由 100% 不動
- [ ] **`pipeline_core.py` / `paper_manager.py` / `processor/*.py`**：業務後端不動
- [ ] **`static/index.html` 中 `fetchContent` 以外的所有函式**：只在 `fetchContent` 內插入一行呼叫，新增函式定義緊接在 `fetchContent` 閉合 `}` 後
- [ ] **`.paper-header-meta` 以外的 CSS 規則**：只改 `align-items` + `text-align` 兩行
- [ ] **`tests/test_bug_f1_frontend_micro_fix.py` 的其他斷言**：只改 L129 / L135 兩行 regex
- [ ] **主 repo 目錄（worktree 父目錄）**：嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C2-hotfix — Frontend Academic Header Self-Healing（前端學術扉頁自癒與靠左重塑）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `static/index.html`（L814–815 CSS + L2696 呼叫插入 + L2698 後新增函式）/ `tests/test_bug_f1_frontend_micro_fix.py`（L129, L135 斷言）/ `tests/test_fe_aesthetics_c2_hotfix.py`（新建）/ `.claude-logs/archive/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_static_index.html.bak` / `.claude-logs/archive/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_test_bug_f1.bak` |
| **安全性** | 🟢 高 — 純前端 JS / CSS / 靜態測試；Guard clause 防新格式誤傷；零後端影響 |
| **可逆性** | 🟢 高 — `git revert C2-hotfix` 完整回滾；或 `git checkout -- static/index.html tests/test_bug_f1_frontend_micro_fix.py && git rm -f tests/test_fe_aesthetics_c2_hotfix.py` |
| **驗收 grep 條件** | 見 §6.1 五項指令全通過；pytest 387 passed, 0 failed, 3 skipped |
| **依賴關係** | FE-AESTHETICS C2（`b735a94`）已落地；無其他前置 |
| **具體實作細節** | **Step 1 備份**：`cp static/index.html .claude-logs/archive/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_static_index.html.bak` / `cp tests/test_bug_f1_frontend_micro_fix.py .claude-logs/archive/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_test_bug_f1.bak`<br>**Step 2 定位 CSS**：`grep -n "align-items: center\|text-align: center" static/index.html` 確認 L814–815；將 `align-items: center` → `align-items: flex-start`，`text-align: center` → `text-align: left`<br>**Step 3 定位 fetchContent**：`grep -n "async function fetchContent\|marked.parse" static/index.html` 確認 `marked.parse(content)` 行；在該行下方插入 `  normalizeAcademicHeader(); // FE-AESTHETICS HOTFIX-1：學術扉頁自癒`<br>**Step 4 插入函式**：在 `fetchContent` 閉合 `}` 之後、`// 列印` 區塊之前，插入完整 `normalizeAcademicHeader()` 函式（含 Guard clause，見 §4.1）<br>**Step 5 修正 test_bug_f1**：`grep -n "current-title.*details" tests/test_bug_f1_frontend_micro_fix.py` 確認 L129, L135；將兩處 `#current-title` → `#abstract-toolbar`<br>**Step 6 新建測試**：建立 `tests/test_fe_aesthetics_c2_hotfix.py`（內容見 §4.1 修改 5）<br>**Step 7 執行驗收**：`venv/bin/pytest tests/ --tb=short -q`；期望 387 passed, 0 failed, 3 skipped<br>**Step 8 產出執行報告**：寫入 `.claude-logs/baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_執行.md`（baton 暫存） |

---

### Check — Conformance 驗收與 baton/ 全量歸檔（收官驗收與計畫歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `baton/` 全量 mv → `hotfixes/` + `tasks/` + `executions/`；`TODO.md`；`prompts/INDEX.md`；`prompts/2026-05-29_FE-AESTHETICS-HOTFIX-1_Check_提示詞.md` |
| **安全性** | 🟢 高 — 純文件治理，零業務代碼改動 |
| **可逆性** | 🟢 高 — 文件移動可還原 |
| **驗收 grep 條件** | `ls .claude-logs/baton/` 確認無 FE-AESTHETICS-HOTFIX-1 殘留；`ls .claude-logs/hotfixes/` 確認 `_hotfix_v1.2.md` 存在 |
| **依賴關係** | 依賴 C2-hotfix baron 手動 commit |
| **具體實作細節** | 1. 歸檔提示詞 `prompts/2026-05-29_FE-AESTHETICS-HOTFIX-1_Check_提示詞.md` + 更新 `INDEX.md`<br>2. Conformance 驗收：§6.1 五項 grep + pytest 387 passed + 不可動清單 §7 全 ✅ + prompts 三階段實體確認<br>3. baton/ 物理歸檔：`mv .claude-logs/baton/2026-05-29_FE-AESTHETICS_hotfix.md .claude-logs/hotfixes/2026-05-29_FE-AESTHETICS-HOTFIX-1_學術扉頁自癒與靠左排版_hotfix_v1.2.md` / `mv baton/..._tasks.md tasks/` / `mv baton/..._C2-hotfix_執行.md executions/` / `mv baton/..._Check_執行.md executions/`<br>4. git add 全量歸檔檔案 + TODO.md + prompts/<br>5. TODO.md 結案：FE-AESTHETICS HOTFIX-1 移入已完成表格，Hash 回填，從進行中移除，索引標記 ✅ |

---

## §9 Open Questions

無。（hotfix v1.2 三輪評審後所有問題均已拍板。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FE-AESTHETICS HOTFIX-1 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Check 收官時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 FE-AESTHETICS HOTFIX-1 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務後端代碼；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | hotfix 計畫規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部收官歸檔，經 baron 同意 |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 hotfix.md 中的診斷脈絡 |

### §99.2 Revision 歷程

- v1 (2026-05-29)：初版拆分完成（hotfix v1.2 拍板後，1 Commit C2-hotfix + Check 架構）
