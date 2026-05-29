# FE-AESTHETICS HOTFIX-1 C2-hotfix 執行報告

> **任務編碼**：FE-AESTHETICS HOTFIX-1
> **Commit 代號**：C2-hotfix（Frontend Academic Header Self-Healing）
> **工作流類別**：FE-Hotfix
> **執行時間**：2026-05-29
> **狀態**：✅ 執行完成，等待 baron 手動 commit

---

## §1 基準與完成狀態

| 項目 | 值 |
|---|---|
| **基準 Commit** | `75ab18a` — RAG-13-HOTFIX-1 Check |
| **工作目錄** | `.claude/worktrees/hopeful-yalow-902c50/` |
| **修改是否已 commit** | ❌ 等待 baron 手動 commit |
| **pytest 結果** | ✅ 387 passed, 0 failed, 3 skipped |
| **物理防線遵守** | ✅ 後端業務邏輯 100% 不動；僅修改 static/index.html + 測試檔 |

---

## §2 Commit 表格

| Commit 代號 | 落地 Hash | Subject |
|---|---|---|
| C2-hotfix | 待 baron 手動 commit | FE-Hotfix: HOTFIX-1 — Frontend Header Self-Healing & Left-Aligned |

---

## §3 變動檔案清單

| 檔案 | 類型 | 說明 |
|---|---|---|
| `static/index.html` | 修改 | CSS 靠左 + normalizeAcademicHeader JS 函數 + fetchContent 呼叫 |
| `tests/test_bug_f1_frontend_micro_fix.py` | 修改 | L129/L135 斷言自癒（#current-title → #abstract-toolbar） |
| `tests/test_fe_aesthetics_c2_hotfix.py` | 新增 | HOTFIX-1 專屬測試（normalizeAcademicHeader 函數存在性驗證） |
| `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_static_index.html.bak` | 新增 | static/index.html 備份 |
| `.claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_test_bug_f1_frontend_micro_fix.py.bak` | 新增 | test_bug_f1 備份 |
| `/tmp/FE-AESTHETICS_HOTFIX-1_msg.txt` | 新增 | commit message 草稿 |

---

## §4 修法說明

### 4.1 CSS 靠左對齊（static/index.html L814–815）

**修改前：**
```css
.paper-header-meta {
  display: flex;
  flex-direction: column;
  align-items: center;    /* 置中 */
  text-align: center;
  ...
}
```

**修改後：**
```css
.paper-header-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;  /* 靠左 */
  text-align: left;
  ...
}
```

**效果**：所有 paper（歷史格式 + 新格式）的扉頁元數據區一律靠左斷行，消除置中造成的排版混亂。

### 4.2 normalizeAcademicHeader() JS 自癒函數（static/index.html）

在 `fetchContent` 末尾插入呼叫：
```javascript
document.getElementById('paper-content').innerHTML = marked.parse(content);
normalizeAcademicHeader(); // FE-AESTHETICS HOTFIX-1：學術扉頁自癒
```

**函數核心邏輯：**

1. **Guard Clause（關鍵防線）**：若 `.paper-header-meta` 已含 `.header-authors / .header-venue-date / .header-doi / .header-keywords` class divs（即 C1 後端正確渲染的新格式），**直接 return，不做任何修改**。防止誤傷新格式論文。

2. **歷史格式處理**：對不含上述 class divs 的元素（歷史 dash-list / 單行格式），從 `textContent` 提取作者/日期/出處/DOI/關鍵字，重建為換行靠左的 HTML divs。

3. **空值防護**：若所有欄位均為空（非學術扉頁），直接 return，不修改 innerHTML。

### 4.3 test_bug_f1 斷言自癒（tests/test_bug_f1_frontend_micro_fix.py）

FE-AESTHETICS C2 將 `#current-title details.title-abstract` 改為 `#abstract-toolbar details.title-abstract`，但 test_bug_f1 的 L129/L135 兩個 regex 仍匹配舊選擇器：

**修改前：**
- L129: `r'#current-title\s+details\.title-abstract\s*\{[^}]*width:\s*100%'`
- L135: `r'#current-title\s+details\.title-abstract\s*\{[^}]*box-sizing:\s*border-box'`

**修改後：**
- L129: `r'#abstract-toolbar\s+details\.title-abstract\s*\{[^}]*width:\s*100%'`
- L135: `r'#abstract-toolbar\s+details\.title-abstract\s*\{[^}]*box-sizing:\s*border-box'`

### 4.4 新增 test_fe_aesthetics_c2_hotfix.py

```python
def test_hotfix_normalize_academic_header_function_exists():
    assert 'function normalizeAcademicHeader' in STATIC_HTML
    assert 'normalizeAcademicHeader()' in STATIC_HTML
```

---

## §5 測試結果

```
venv/bin/pytest tests/ --tb=short -q

387 passed, 3 skipped in 45.63s
```

| 類型 | 數量 |
|---|---|
| passed | **387** |
| failed | **0** |
| skipped | 3 |

✅ 全量 pytest 通過，達到目標基準 387 passed, 0 failed, 3 skipped。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| 後端業務邏輯（pipeline_core.py / web_server.py / paper_manager.py / processor/*.py）100% 不動 | ✅ |
| fetchContent 以外的 JS 不動 | ✅（僅在 fetchContent 末尾加呼叫 + 新增獨立函數） |
| .paper-header-meta 以外的 CSS 不動 | ✅（僅修改 .paper-header-meta 的 align-items / text-align） |
| 不自發 git commit / push | ✅ |
| baton/ 執行報告不入 git add | ✅（§8 git add 清單不含 baton/ 路徑） |

---

## §7 銜接

本 Commit 完成後，需進入 Check 階段：
- Conformance 驗收（4 維度：目標規格 / 物理防線 / 測試防線 / 文件防線）
- baton/ 全量歸檔：
  - `baton/2026-05-29_FE-AESTHETICS_hotfix.md` → `hotfixes/`
  - `baton/2026-05-29_FE-AESTHETICS_hotfix_tasks.md` → `tasks/`
  - `baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_C2-hotfix_執行.md` → `executions/`
  - `baton/2026-05-29_FE-AESTHETICS-HOTFIX-1_Check_執行.md` → `executions/`（Check 產出）
- TODO.md 更新 FE-AESTHETICS HOTFIX-1 → ✅ done + 回填 hash

---

## §8 baron 執行命令

```bash
git add static/index.html
git add tests/test_bug_f1_frontend_micro_fix.py
git add tests/test_fe_aesthetics_c2_hotfix.py
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_static_index.html.bak
git add .claude-logs/archive/2026-05-29_FE-AESTHETICS_C2-hotfix_test_bug_f1_frontend_micro_fix.py.bak
git add .claude-logs/prompts/2026-05-29_FE-AESTHETICS_C2-hotfix_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md
git commit -F /tmp/FE-AESTHETICS_HOTFIX-1_msg.txt
```
