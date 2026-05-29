# FE-AESTHETICS Commit C2-hotfix — 緊急熱修復：前端學術扉頁動態自癒相容與靠左斷行排版優化

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，專門用於修正前一次 Commit 落地後預覽歷史數據時發現的扉頁排版不一致性 Bug。
> **修復原則**：只改動受災點前端程式碼，嚴禁夾帶任何無關的新功能或大型後端重構。

---

## §0 改版與 Revision 歷程

- **改版觸發**：配合 baron 最新設計升級意志與 Conformance 靜態審計反饋。
- **改版規則**：直接修改對應章節 + §0.2 Revision 紀錄。

### §0.2 Revision 歷程
- **v1.0 (2026-05-29)**：初版建立，針對點表與單行歷史數據提供動態自癒與靠左斷行 CSS 規劃。
- **v1.1 (2026-05-29)**：依 baron 技術審計反饋進行全方位修正自癒（修補 test_bug_f1 舊斷言，預防全量 regression 錯誤）。
- **v1.2 (2026-05-29)**：配合技術稽核的新發現進行緊急修正：
  1. **防止誤傷新格式（Critical Guard）**：在自癒函數開頭增加 1 行 Guard clause，檢測若已包含 `.header-authors` 等新 class divs 則直接 early return，徹底防止自癒程序覆蓋新格式導致作者與出處消失的災難性 Regression。
  2. **行號動態定位更新**：將 `fetchContent` 的位置描述修正為最新的 `L2680` 附近，以動態定位方式指導執行。
  3. **測試檔案獨立解耦**：不再把 Hotfix 單元測試強塞入無關的 BUG-F5 中，而是遵循 SOP 新建專屬的 `tests/test_fe_aesthetics_c2_hotfix.py` 測試檔案，確保結構清晰、語意高自洽。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **C2-hotfix** | `[待 baron 回填]` | fix(frontend): hotfix for academic header dynamic self-healing and left-aligned stack |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)
- **現象描述**：解鎖 `.paper-header-meta` 螢幕顯示後，由於歷史數據在後端已完成 Markdown 儲存（後端不會自動對既有論文重新渲染），導致既有論文在前端顯示時，其元數據格式與新 CSS 產生嚴重排版衝突，資料完全沒有一致性：
  1. 早期單行無換行論文：所有屬性連成一整段雜亂文字擠在同一行，視覺破碎。
  2. 前一版本帶 dot 清單點表論文：無序清單 `<ul>`/`<li>` 居中且圓點錯位。
- **受災範圍**：所有系統中歷史已導入的學術論文扉頁預覽頁面。
- **首發現象截圖**：與 baron 反饋之 3 張排版破碎截圖一致。

### 2. 真因診斷 (Root Cause)
- **技術細節**：前端解鎖 `.paper-header-meta` 顯示且應用樣式時，僅對 C1 修改後產生的 HTML div 階梯結構運作優良。對於歷史數據中殘存的舊 `dash-list` 格式與舊 `單行 metadata` 格式，前端缺乏防禦性與動態相容性清洗，導致 CSS 直接把舊 DOM 結構撐爆或錯置。
- **定位程式碼**：`file:///static/index.html#L2680-L2695` (在 `fetchContent` 內，`marked.parse` 後直接渲染，無任何 dynamic sanitization 與 fallback 機制)。

---

## 熱修復修法 (Minimal Hotfix)

本修復採取的**最小侵入式**解決方案：
1. **排版優化（對齊與斷行）**：
   - 標題（`h1:first-child`）保持 `text-align: center`（置中對稱）。
   - 其他元數據資訊（`.paper-header-meta` 內）調整為 **靠左對齊，並且斷行**。
2. **動態自癒與 Normalization**：
   - 在前端 `static/index.html` 內加入 `normalizeAcademicHeader()` 函數。
   - **關鍵防禦**：首行加入 Guard，若檢測到已含 `.header-authors` 等新樣式類，代表為新格式論文，直接提前退出，徹底防範誤傷。
   - 當 `fetchContent` 解析完 Markdown 後，動態精準匹配歷史元數據（Authors/Date/Venue/DOI/Keywords），消除點表 `li` 圓點及單段擠壓干擾，將其 100% 統一自癒為無 dots、換行靠左的最新階梯式 HTML 結構，實現全案極致的視覺一致性。

### 1. `static/index.html` — CSS 與 JS 修改

```diff
-   align-items: center;
-   text-align: center;
+   align-items: flex-start;
+   text-align: left;
```

```diff
  async function fetchContent(paperId, lang) {
    const res = await fetch(`${API}/api/papers/${paperId}/content?lang=${lang}`);
    const data = await res.json();
  
    // 把圖片路徑換成 API 取代
    const content = data.content.replace(
      /!\[([^\]]*)\]\(images\/([^)]+)\)/g,
      `![$1](/api/papers/${paperId}/images/$2)`
    );
  
    document.getElementById('paper-content').innerHTML = marked.parse(content);
+   normalizeAcademicHeader(); // 執行前端學術扉頁動態自癒與對齊格式化
  }
```

```html
// 新增在 fetchContent 下方的自癒相容函數
function normalizeAcademicHeader() {
  const metaEl = document.querySelector('#paper-content .paper-header-meta');
  if (!metaEl) return;

  // 🟢 關鍵 Guard 防禦：若已含新格式 class divs（代表為 C1 後端正確渲染新論文），直接跳過自癒，防範誤傷
  if (metaEl.querySelector('.header-authors, .header-venue-date, .header-doi, .header-keywords')) return;

  const rawText = metaEl.textContent.trim();
  
  // 多語系邊界預判提取演算法
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

  const authorsVal = extractField(rawText, ["作者", "Authors"]);
  const dateVal = extractField(rawText, ["日期", "Date"]);
  const venueVal = extractField(rawText, ["出處", "Venue"]);
  const doiVal = extractField(rawText, ["DOI"]);
  const keywordsVal = extractField(rawText, ["關鍵字", "Keywords"]);

  // 若提取不到任何核心元數據，代表非學術論文或格式不符，保持原樣
  if (!authorsVal && !dateVal && !venueVal && !doiVal && !keywordsVal) return;

  let htmlBits = [];
  if (authorsVal) {
    htmlBits.push(`  <div class="header-authors">${authorsVal}</div>`);
  }
  let venueDateBits = [];
  if (venueVal) venueDateBits.push(venueVal);
  if (dateVal) venueDateBits.push(dateVal);
  if (venueDateBits.length > 0) {
    htmlBits.push(`  <div class="header-venue-date">${venueDateBits.join(' · ')}</div>`);
  }
  if (doiVal) {
    htmlBits.push(`  <div class="header-doi">DOI: ${doiVal}</div>`);
  }
  if (keywordsVal) {
    const isZh = rawText.includes('關鍵字') || keywordsVal.includes('、');
    const label = isZh ? '關鍵字：' : 'Keywords: ';
    htmlBits.push(`  <div class="header-keywords">${label}${keywordsVal}</div>`);
  }

  metaEl.innerHTML = htmlBits.join('\n');
}
```

### 2. `tests/test_bug_f1_frontend_micro_fix.py` — 歷史斷言自癒更新
將 L127-139 舊斷言修改為新容器：
```diff
-   r'#current-title\s+details\.title-abstract\s*\{[^}]*width:\s*100%',
+   r'#abstract-toolbar\s+details\.title-abstract\s*\{[^}]*width:\s*100%',
...
-   r'#current-title\s+details\.title-abstract\s*\{[^}]*box-sizing:\s*border-box',
+   r'#abstract-toolbar\s+details\.title-abstract\s*\{[^}]*box-sizing:\s*border-box',
```

### 3. [NEW] `tests/test_fe_aesthetics_c2_hotfix.py` — 新建專屬測試檔案
```python
"""FE-AESTHETICS Commit C2-hotfix 專屬測試檔

驗證前端 index.html 內新 JS 自癒函數的存在性與調用。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')


def test_hotfix_normalize_academic_header_js_healing_exists():
    """HOTFIX-1: 驗證前端 index.html 內 normalizeAcademicHeader 函數定義與 fetchContent 調用存在"""
    assert 'function normalizeAcademicHeader' in STATIC_HTML, '應在 index.html 內定義 normalizeAcademicHeader 自癒相容函數'
    assert 'normalizeAcademicHeader()' in STATIC_HTML, '應在 fetchContent 中調用 normalizeAcademicHeader()'
```

---

## regression 預防與 E2E 驗證

### 1. 單元測試驗證
本修復自癒了歷史 Regression 測試，且新建專屬測試檔防範 Regress：
```bash
$ orb -m claude-lab ./venv/bin/pytest tests/ -v
# 期望：387 passed, 0 failed, 3 skipped 🟢 (1 pre-existing fail 完美自癒，新建 1 測試 2 assertions 全綠)
```

### 2. 本地 E2E 快速復現與驗證
1. 開啟系統預覽新上傳的論文，其標題居中，元數據（作者、出處日期等）靠左對齊，且以獨立 div 垂直斷行。驗證其因為 Guard clause 而完全沒有被誤傷。
2. 預覽歷史數據中「無換行單段文字」格式的舊論文（如圖一、二），確認其元數據被前端 JS 完美解析，重新排列為靠左、斷行、無 label 雜音的整潔扉頁。
3. 預覽歷史數據中「居中無序點表」格式的舊論文（如圖三），確認無序列表點 `•` 被完全剔除，且同樣呈現靠左、斷行的階梯式結構。
4. 控制台 100% 零錯誤。

---

## 回退與備案

若此 Hotfix 產生 unexpected regression，請執行 Git 還原以恢復 C2 Commit 落地狀態：

```bash
git checkout -- static/index.html tests/test_bug_f1_frontend_micro_fix.py
git rm -f tests/test_fe_aesthetics_c2_hotfix.py
```
