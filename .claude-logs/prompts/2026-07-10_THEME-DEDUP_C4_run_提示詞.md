# 2026-07-10 — THEME-DEDUP C4 run 提示詞

> **收到時間**：2026-07-10 07:32（UTC+8）
> **任務代號**：THEME-DEDUP C4
> **觸發 commit**：C4
> **相關產出檔案**：`design/docs/theme-template.css`（新·統一骨架模板）+ `.claude-logs/tools/check_css_governance.py`（新·常駐契約腳本·純標準庫）+ `design/docs/{theme-guide,css-architecture}.md` + baton 執行報告 `2026-07-10_THEME-DEDUP_Guard_C4_執行.md`
> **觸發情境**：baron 確認 C3 後下達 C4（Template & Guard）——模板（9 段骨架+26 token 佔位+16 選擇器+兩槽+逐段註解·**嚴禁落 static/themes/**）+ 契約腳本（四類檢查：unlayered 鐵律/token 唯一定義/9 主題+模板骨架合規〔載 Q3 例外表〕/死碼=0；exit 0/1+違規清單+--file 模式；**僅 re/sys/pathlib/json**）+ **首次全綠輸出必貼執行報告** + theme-guide Step-by-step 改指模板+腳本用法登記 + css-architecture 工具交付。

---

## 完整提示詞

````markdown
### 📊 元數據審計塊

| 欄位 | 值 |
|---|---|
| **收到時間** | 2026-07-10 07:32 |
| **任務代號** | THEME-DEDUP C4 |
| **觸發 Commit** | C4 |
| **相關產出檔案** | .claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md |
| **觸發情境** | baron 確認 C3 執行報告後，下達 C4 階段執行指令 |

## 🗄️ 第一步：主動歸檔本提示詞（先完成才准進下一步）
（寫入 `.claude-logs/prompts/2026-07-10_THEME-DEDUP_C4_run_提示詞.md`、更新 INDEX、回覆確認後繼續）

你現在扮演 Claude Code，執行單一 Commit C4。

### 📋 任務資訊
- 任務編碼：THEME-DEDUP / 當前 Commit：C4 / 工作流：FE-Refactor
- Tasks 路徑：.claude-logs/baton/2026-07-10_THEME-DEDUP_主題結構去重_tasks.md

### 🏢 修改邊界與限制（四鐵防線與純標準庫）
1. 僅允許：建 design/docs/theme-template.css + 建 tools/check_css_governance.py + 改 theme-guide/css-architecture；嚴禁業務代碼與 static/**。
2. 模板隔離鐵防線：theme-template.css 嚴禁落 static/themes/（掃描 API 誤入下拉）；必須 design/docs/。
3. 腳本限制：純標準庫（re/sys/pathlib/json）、嚴禁 cssutils 等第三方。
4. 版控：C4 git 追蹤 2 新檔 + 2 docs + 2 .bak；baton 過程檔嚴禁 git add。

### 🛠️ 執行命令
1. 備份 2 檔 → archive/2026-07-10_THEME-DEDUP_C4_*.bak
2. 模板：9 段骨架 + 26 token 佔位 + 16 選擇器（含 .ph::before 空槽 + chrome marker）+ 逐段註解
3. 腳本：四類檢查〔① 主檔系 unlayered=0/themes @layer=0 ② token 唯一定義 globals ③ 9 主題+模板骨架合規〔26 token+16 選擇器+2 槽+內容選擇器白名單·Q3 例外表〕④ demo-bar 死碼=0〕；違規 exit(1)+清單、成功 exit(0)；--file 單檔模式；**首次全綠輸出完整貼執行報告**
4. 文獻：theme-guide Step-by-step 改「複製 theme-template.css」+ 腳本用法登記；css-architecture 工具交付

### 🔄 同步更新 TODO.md + 歷史 Hash 自癒
- C4 → ✅；checkout → 🟡 WIP；git log 掃描回填佔位。

### 📁 產出規格
- 執行報告：`.claude-logs/baton/2026-07-10_THEME-DEDUP_Guard_C4_執行.md`（baton、不入 git）；§1–§8（§5 必含腳本首綠輸出）。
- §8：git add 2 新檔 + 2 docs + 2 .bak；msg /tmp/THEME-DEDUP_C4_msg.txt；baron 手動 commit。

### 🛑 停止指令
產出執行報告後立即停止。嚴禁：續執行 checkout / 改未列入細節的檔 / 自發 git commit/push。
````

---

## 執行結果摘要

- ✅ `design/docs/theme-template.css`：9 段骨架+26 token 佔位+16 選擇器+兩空槽+逐段註解；落點鐵防線遵守（design/docs·非 static/themes）；模板自身過腳本
- ✅ `tools/check_css_governance.py`：純標準庫（re/sys/json/pathlib）；四類檢查〔unlayered brace-walk/token 唯一+散落雙抓/凍結骨架 26 不多不少+16+2 槽+白名單·例外表=§11.3 名鍵控+chrome 規則必在 marker 後/死碼〕；exit 0/1+清單+--file
- ✅ **首跑全量（主檔系 7+主題 9+模板 1）全綠 EXIT 0**（原文入報告 §5）+ **突變負測 5 違規全抓**（@layer/死碼/缺 token/非白名單/例外名鍵控佐證）+ docs 改後迴歸仍綠
- ✅ theme-guide §8 改 copy 模板+步驟 8 機器驗收；css-architecture 工具登記；C3 hash `bf4577c` 自癒
- static/** 零 diff；commit/push：否（baron 手動·6 檔）

## 後續引用

checkout（成果收官歸檔）由 baron 另下獨立提示詞觸發。
