# 2026-07-10 — THEME-DEDUP C1 run 提示詞

> **收到時間**：2026-07-10 06:23（UTC+8）
> **任務代號**：THEME-DEDUP C1
> **觸發 commit**：C1
> **相關產出檔案**：`static/css/globals.css`（+7 異值結構 token）+ `static/css/content.css`（base 承接）+ `design/docs/css-architecture.md`（§6 +7 + 對照表）+ baton 執行報告 `2026-07-10_THEME-DEDUP_Foundation_C1_執行.md`
> **觸發情境**：baron 確認 C0 後下達 C1（Token & Base Foundation）——globals tokens 層末追加 7 個主題結構覆寫 token（多數派 default）；content.css `@layer components` 內 h2 空槽填承接 + `#paper-content`/`.figure`/`figcaption`/`.ph` 改讀 token + 新增 `.byline` 規則；css-architecture §6 登記 + 「主題結構→base/token 對照表」節；**零視覺變鋪底**（主題 unlayered 蓋 base）；嚴禁 themes/index.html/JS/py。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-10 06:23 |
| **任務代號** | THEME-DEDUP C1 |
| **觸發 Commit** | C1 |
| **相關產出檔案** | .claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md |
| **觸發情境** | baron 確認 C0 執行報告後，下達 C1 階段執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-10_THEME-DEDUP_C1_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C1。

### 📋 任務資訊
- 任務編碼：THEME-DEDUP / 當前 Commit：C1 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md（已載入）/ plan v7 / tasks / 前端 SOP 手冊 /
static/css/{globals,content}.css / design/docs/css-architecture.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：globals.css + content.css + css-architecture.md；嚴禁後端/JS/index.html/themes。
2. 零視覺變更（鋪底保護）：純加法、主題 unlayered 蓋 base 新規則、外觀 100% 無變動。
3. 版控：C1 git 追蹤 2 css + 1 docs + 3 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與代碼修改
1. 備份 3 檔 → archive/2026-07-10_THEME-DEDUP_C1_*.bak
2. 導入異值結構 Tokens：globals tokens 層末（--content-max-w 後）追加 7 token（--pc-pad 等·tasks 名單）+ 多數派 default + 「異值結構 token（THEME-DEDUP·主題覆寫）」標註
3. Base 承接：content.css @layer components 內 h2 空槽填邊框/內距；#paper-content/.figure/figcaption/.ph 改讀 7 token；.figure 前新增 .byline 規則
4. 文獻：css-architecture §6 登記 7 token + 新增「主題結構→base/token 對照表」節（token×規則×各主題覆寫值）
5. 驗收：tasks §6.2；任一主題外觀零視覺變化

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C1 → ✅；C2 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-10_THEME-DEDUP_Foundation_C1_執行.md`（baton、不入 git）；§1–§8。
- §8：git add 2 css + css-architecture + 3 .bak；msg /tmp/THEME-DEDUP_C1_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C2 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ⚠️ **C0 序位 deviation**：執行期查證 C0 baseline 尚未 commit（5 支仍 untracked）——C1 零觸 themes 技術獨立先行（tasks §8 依賴註）；**C2/C3 前 C0 必須先 ship**（TODO 標 ⚠️、報告 §1/§7 記載）
- ✅ 完成：globals T3 +7 異值結構 token〔多數派 default+異值主題註〕+ content.css 承接〔h2 Group B 填槽+#paper-content padding/.figure/figcaption/.ph 讀 token+新增 .byline〕+ css-architecture §6.1+§6.4 對照表
- ✅ **零視覺變結構性證明**：腳本逐支逐屬性驗 9 支主題全自帶 base 承接屬性 → unlayered 全蓋（非僅宣稱）
- ✅ hash 自癒：FE-CSS-GOV C5 `9df0028`/checkout `6fea7dc` 回填 done_archive+TODO 索引（全檔 0 佔位）
- 是否 commit / push：否（baron 手動·6 檔）

## 後續引用

**前置：baron 先 commit C0 baseline** → 再下 C2（Builtin Normalize）提示詞。
