# 2026-07-10 — THEME-DEDUP C2 run 提示詞

> **收到時間**：2026-07-10 06:51（UTC+8）
> **任務代號**：THEME-DEDUP C2
> **觸發 commit**：C2
> **相關產出檔案**：`static/themes/{kahn,kandinsky,mies,nara}.css`（統一骨架重排+26 token+去結構+兩槽）+ `design/docs/theme-guide.md`（升格目錄級凍結規格源）+ baton 執行報告 `2026-07-10_THEME-DEDUP_Builtin_C2_執行.md`
> **觸發情境**：baron 確認 C1 後下達 C2（Builtin Normalize）——4 內建主題按 plan §2.2-B 標準 9 段骨架重排、`:root` 顯式寫滿 26 token（7 結構 token 各自原值）、剝除 15 內容選擇器白名單外結構屬性、白名單色補償（kandinsky byline border-color 等）、補裝飾層槽（kahn 入 geometry、3 支空規則）+ chrome 覆寫層 marker（4 支空）；theme-guide 重寫為凍結規格源（26 token 表/16 選擇器骨架/屬性白名單含 text-align/禁止清單/收斂 §8）；Q3 裝飾排版例外嚴守；multiset 對帳；themes 嚴禁 @layer。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-10 06:51 |
| **任務代號** | THEME-DEDUP C2 |
| **觸發 Commit** | C2 |
| **相關產出檔案** | .claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md |
| **觸發情境** | baron 確認 C1 執行報告後，下達 C2 階段執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-10_THEME-DEDUP_C2_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C2。

### 📋 任務資訊
- 任務編碼：THEME-DEDUP / 當前 Commit：C2 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md（已載入）/ plan v7 / tasks / 前端 SOP 手冊 /
static/themes/{kahn,kandinsky,mies,nara}.css / design/docs/theme-guide.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：4 內建主題 + theme-guide.md；嚴禁後端/JS/index.html/static/css/上傳 5 支。
2. Q3 裝飾排版例外嚴守（kahn figcaption max-width+margin-inline、kahn .ph position:relative、mies max-width:none 等）。
3. 無 cascade 翻轉：骨架重排前後規則內容 multiset 對帳相等；themes 嚴禁 @layer。
4. 版控：C2 git 追蹤 4 主題 + theme-guide + 5 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與代碼修改
1. 備份 5 檔 → archive/2026-07-10_THEME-DEDUP_C2_*.bak
2. 內建主題重組與去結構：統一骨架重排（plan §2.2-B 九段）/ :root 顯式寫滿 26 token〔7 結構 token 各自原值·kahn --pc-pad: var(--space-8) 等〕/ 剝除 15 內容選擇器白名單外結構屬性〔h2 底線/pc padding 等〕/ 白名單色補償〔kandinsky .byline border-color 等〕/ 補槽〔.ph::before：kahn 入 geometry、3 支空規則；chrome marker 4 支空〕
3. 文獻：theme-guide 重寫升格目錄級凍結規格源（26 token 必備表/16 選擇器統一骨架/每選擇器屬性白名單含補登 text-align/可選裝飾/禁止清單/收斂原 §8 方向章）
4. 驗收：tasks §6.3；multiset 核對；瀏覽器 E2E 4 主題視圖+slide 底線間距

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C2 → ✅；C3 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-10_THEME-DEDUP_Builtin_C2_執行.md`（baton、不入 git）；§1–§8。
- §8：git add 4 主題 + theme-guide + 5 .bak；msg /tmp/THEME-DEDUP_C2_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C3 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ C0 `2380420`/C1 `f64d15b` 已 ship 確認（序位鐵則滿足）→ TODO hash 自癒
- ✅ 4 內建全檔重寫至統一 9 段骨架：26 token 顯式寫滿〔7 結構 token 各自原值〕+ 剝 9 結構屬性 + 色補償〔kandinsky byline divider·kahn ph border-strong〕+ 兩槽〔kahn ::before 入槽、3 支空；chrome marker ×4〕
- ✅ **雙重機器驗證**：宣告級 delta 對帳（刪==計畫/加==token+補償/其餘 multiset 零改寫）+ 7 token×4 覆寫值==原結構值（視覺等價）
- ✅ theme-guide 重寫升格目錄級凍結規格源（§1-§10：模型/26 token/骨架 16 選擇器/白名單含 text-align/兩槽/禁止/unlayered/步驟 checklist/上傳）
- 上傳 5 支/static/css/index.html 全零 diff；是否 commit/push：否（baron 手動·10 檔）

## 後續引用

C3（Uploads Normalize）由 baron 另下獨立提示詞觸發。
