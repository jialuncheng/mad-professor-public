# 2026-07-10 — THEME-DEDUP C3 run 提示詞

> **收到時間**：2026-07-10 07:12（UTC+8）
> **任務代號**：THEME-DEDUP C3
> **觸發 commit**：C3
> **相關產出檔案**：`static/themes/{apple,corbusier,fuller,google,gropius}.css`（死碼清理+26 token+骨架重排+chrome 槽）+ `design/docs/{theme-guide,css-architecture}.md` + baton 執行報告 `2026-07-10_THEME-DEDUP_Uploads_C3_執行.md`
> **觸發情境**：baron 確認 C2 後下達 C3（Uploads Normalize）——5 支上傳：C2 同法清 `#demo-bar` 死碼、補 `--content-max-w` 與 7 結構 token（值依 C0 baseline grep 核定、不缺不漏 26）、標準 9 段骨架重排（**apple/google chrome 覆寫段原樣入第 9 槽、嚴禁改一字**、其餘 3 支僅 marker）、剝 15 內容選擇器白名單外結構屬性；theme-guide 補「自訂/上傳主題」章 + css-architecture 現狀更新；嚴禁內建 4 支/static/css/index.html。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-10 07:12 |
| **任務代號** | THEME-DEDUP C3 |
| **觸發 Commit** | C3 |
| **相關產出檔案** | .claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md |
| **觸發情境** | baron 確認 C2 執行報告後，下達 C3 階段執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-10_THEME-DEDUP_C3_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C3。

### 📋 任務資訊
- 任務編碼：THEME-DEDUP / 當前 Commit：C3 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md

### 📖 強制讀檔清單
CLAUDE.md / WORKFLOW_SOP.md（已載入）/ plan v7 / tasks / 前端 SOP 手冊 /
static/themes/{apple,corbusier,fuller,google,gropius}.css / design/docs/{theme-guide,css-architecture}.md

### 🏢 修改邊界與限制（四鐵防線）
1. 僅允許：5 支上傳主題 + theme-guide + css-architecture；嚴禁後端/JS/index.html/static/css/內建 4 支。
2. chrome 覆寫內容原樣保留：apple/google 之 `.btn-*`/`.modal-*`/`.msg-*`/`.paper-item` 等覆寫塊＝設計本體、**嚴禁改一字**；僅整塊原序移入骨架第 9 槽。
3. 版控：C3 git 追蹤 5 主題 + 2 docs + 7 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令與代碼修改
1. 備份 7 檔 → archive/2026-07-10_THEME-DEDUP_C3_*.bak
2. 死碼清理（C2 同法）+ Token 補齊（--content-max-w: 760px + 7 結構 token 值依 C0 baseline grep 核定·不缺不漏 26）+ 統一骨架重排（apple/google chrome 段原樣入槽 9、其餘 3 支 marker）+ 剝 15 內容選擇器白名單外結構屬性
3. 文獻：theme-guide 補「自訂/上傳主題」章〔unlayered 機制/chrome 槽規範/建議 var token〕+ css-architecture 現狀更新
4. 驗收：tasks §6.4——demo-bar=0、token 合規、E2E apple/google chrome 覆寫選單對話框完好

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C3 → ✅；C4 → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-10_THEME-DEDUP_Uploads_C3_執行.md`（baton、不入 git）；§1–§8。
- §8：git add 5 主題 + 2 docs + 7 .bak；msg /tmp/THEME-DEDUP_C3_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 C4 / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ 執行期簡化：5 支段序已天然符骨架 → 免重排、手術式操作（腳本+逐項斷言）
- ⚠️ **scope 精修（視覺等價鐵律優先·framework §7 #1 自裁）**：上傳帶 base 不可重現之結構〔全 5 支 pre-FE-RHYTHM 節奏 margin／fuller dashed×2+tnum／apple/google ph border-radius〕→ **保留 + theme-guide §11.3 登記**（C4 腳本例外依據）
- ✅ 5 支：demo-bar 清除（22-26 宣告/支）+ 26 token〔8 新·值==C0 baseline〕+ 剝可剝結構（10/10/10/8/10）+ 補償色 + 兩槽〔**apple/google chrome 段逐宣告零改寫**·機器證〕
- ✅ 獨立 delta 對帳 5 支全過；theme-guide §11 上傳章 + css-architecture §6.4 現狀
- 內建 4 支/static/css/index.html 零 diff；C2 hash `0fd4ca6` 自癒；commit/push：否（baron 手動·14 檔）

## 後續引用

C4（Template & Guard）由 baron 另下獨立提示詞觸發。
