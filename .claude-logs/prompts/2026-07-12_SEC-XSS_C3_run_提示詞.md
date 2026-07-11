# 2026-07-12 — SEC-XSS C3 run 提示詞

> **收到時間**：2026-07-12 04:51（UTC+8）
> **任務代號**：SEC-XSS C3
> **觸發 commit**：C3
> **相關產出檔案**：`static/index.html`（renderSources 節點化 + meta/清單變數單體消毒）+ `tests/test_sec_xss_guard.py`（追加守衛）+ baton 執行報告 `2026-07-12_SEC-XSS_C3_執行.md`
> **觸發情境**：baron 確認 C2 後下達 C3（Sources & Meta Hardening）——① `renderSources` 重構：createElement('a') + textContent + href scheme 白名單（僅 http/https、其餘不設 href）+ appendChild、廢字串拼接；② `normalizeAcademicHeader`：authorsVal/dateVal/venueVal/doiVal/keywordsVal 各自單體 `DOMPurify.sanitize()` 後填靜態 div；③ `renderPapers`：displayTitle/displaySubtitle 單體消毒後填模板、`data-tip="文件選單"`+`<svg>` 靜態模板嚴禁進 sanitizer；~27 靜態/清空 sink 一字不改；守衛 +2（renderSources 無 `href="${s.uri}"` 拼接+含 createElement/textContent；meta/清單變數呼叫 sanitize）；§6.3+§6.4 全套件綠燈。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-12 04:51 |
| **任務代號** | SEC-XSS C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | .claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md |
| **觸發情境** | baron 確認 C2 成功，下達 C3 階段執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-12_SEC-XSS_C3_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C3。

### 🏢 修改邊界與限制
1. 唯一修改：static/index.html + tests/test_sec_xss_guard.py。
2. 靜態模板不可動防線：item.innerHTML 與 metaEl.innerHTML 之靜態模板（含 data-tip 與 SVG）嚴禁進 sanitizer——變數單體消毒；~27 靜態/清空 sink 一字不改。
3. 版控：2 檔 + 2 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令
1. 備份 2 檔 → archive/2026-07-12_SEC-XSS_C3_*.bak
2. Sources 節點化+scheme 白名單：renderSources 廢字串拼接→createElement('a')+textContent 賦標題+href 僅 http/https（其餘不設）+appendChild
3. Meta 變數單體消毒：normalizeAcademicHeader 五欄各自 DOMPurify.sanitize()（或純文字欄更嚴 escape）後填靜態 div
4. 清單標題單體消毒：renderPapers 對 displayTitle/displaySubtitle 單體 sanitize 後填 innerHTML 模板；data-tip+<svg> 原樣避開
5. 守衛 +：① renderSources 無 href="${s.uri}" 拼接+含 createElement('a')/textContent ② header/papers 變數呼叫 sanitize
6. §6.3+§6.4 + 全套件綠燈；tooltip 手動確認

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C3 → ✅；checkout → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出：baton/2026-07-12_SEC-XSS_C3_執行.md；§8 git add 2 檔+2 .bak；msg /tmp/SEC-XSS_C3_msg.txt

### 🛑 停止：產出後立即停；嚴禁續 checkout / 自發 commit·push
````

---

## 執行結果摘要

- ✅ `renderSources` 節點化（createTextNode/createElement('a')+textContent+**http(s) scheme 白名單**·非白名單 scheme 不設 href）
- ✅ `normalizeAcademicHeader` 五欄 extractField 外包 sanitize（恰 5 呼叫·守衛計數）；`renderPapers` 兩標題單體消毒、`data-tip`+`<svg>` 靜態模板 byte 原樣（守衛斷言）
- ✅ ~27 靜態/清空 sink 一字不改（innerHTML='' ×14 守恆）；守衛 +2（切片錨修正一次：papersInCurrentFolder 定義在前→改 loadPapers·紅→綠）
- ✅ 守衛 7 passed；全套件 713→**715 passed** 零回歸；C2 hash `ecd2e95` 自癒
- commit/push：否（baron 手動·4 檔）

## 後續引用

checkout（成果收官歸檔）由 baron 另下獨立提示詞觸發。
