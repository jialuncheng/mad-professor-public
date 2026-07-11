# 2026-07-12 — SEC-XSS C1 run 提示詞

> **收到時間**：2026-07-12 04:30（UTC+8）
> **任務代號**：SEC-XSS C1
> **觸發 commit**：C1
> **相關產出檔案**：`static/vendor/dompurify/purify.min.js`（新·自託管）+ `tools/fetch_frontend_vendor.sh` + `static/vendor/README.md` + `static/index.html`（defer 載入）+ `tests/test_sec_xss_guard.py`（新·靜態守衛）+ baton 執行報告 `2026-07-12_SEC-XSS_C1_執行.md`
> **觸發情境**：baron 確認 tasks 後下達 C1（Vendor & Load）——`npm pack dompurify@3.1.6` 提取 `dist/purify.min.js` 自託管；fetch_frontend_vendor.sh 追加下載+SHA-256 段；vendor README 補 dompurify 章（版本/來源/載入/指紋）；index.html head 於 marked script 後插 `<script src="/static/vendor/dompurify/purify.min.js" defer>`；新測試 4 斷言（實體在/index 載入含 defer/腳本含 dompurify 段/README 含說明指紋）；§6.1 + 全套件綠燈。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-12 04:30 |
| **任務代號** | SEC-XSS C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md |
| **觸發情境** | baron 確認 tasks 規格，下達 C1 階段執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-12_SEC-XSS_C1_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C1。

### 📋 任務資訊
- 任務編碼：SEC-XSS / 當前 Commit：C1 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-12_SEC-XSS_DOMPurify輸出消毒_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md（已載入）/ plan_v1 / tasks / 前端 SOP 手冊 /
tools/fetch_frontend_vendor.sh / static/vendor/README.md / static/index.html

### 🏢 修改邊界與限制
1. 唯一異動與新建：index.html（載入標籤）/ fetch_frontend_vendor.sh / vendor README / static/vendor/dompurify/purify.min.js / tests/test_sec_xss_guard.py。
2. 鐵防線：嚴禁後端業務代碼（.py 僅限 tests/）。
3. 版控：上述檔 + 3 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令
1. 備份 3 檔 → archive/2026-07-12_SEC-XSS_C1_*.bak
2. 自託管：npm pack dompurify@3.1.6（或最新穩定 3.x）→ 提取 dist/purify.min.js → static/vendor/dompurify/
3. fetch_frontend_vendor.sh 追加 npm pack+下載+SHA-256 校驗段；vendor README 補 dompurify 章（3.1.6/來源/載入/實測 SHA-256）
4. index.html head 於 marked script（L9）後插 `<script src="/static/vendor/dompurify/purify.min.js" defer></script>`
5. tests/test_sec_xss_guard.py 四斷言（① purify.min.js 實體 ② index 載入 script 含 defer ③ 腳本含 dompurify 段 ④ README 含說明+指紋）
6. §6.1 驗收 + 全套件綠燈

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C1 → ✅；C2 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-12_SEC-XSS_C1_執行.md`（baton、不入 git）；§1–§8（§5 含 pytest 輸出）。
- §8：git add 5 檔 + 3 .bak；msg /tmp/SEC-XSS_C1_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C2/C3 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ dompurify@3.1.6 npm pack 自託管（21.5KB·SHA-256 `c0845096…dbe3a1` 登記 README·版本戳實測 3.1.6）
- ✅ index.html head L10-11 於 marked 後 defer 載入；fetch_frontend_vendor.sh 追加 DOMPURIFY_VERSION 釘版下載/校驗段（bash -n OK）；vendor README dompurify 分節
- ✅ tests/test_sec_xss_guard.py 四守衛（實體/defer+載入序/腳本段/README 指紋==實測 hash）4 passed；**全套件 708→712 passed 零回歸**
- 純載入零行為變更（接線屬 C2/C3）；⚠️ INDEX 時間排序區 38 筆逾上限＝歷史欠帳、另案清理
- commit/push：否（baron 手動·8 檔）

## 後續引用

C2（Markdown Sanitize）由 baron 另下獨立提示詞觸發。
