# PIPE-SLIDES-HOTFIX-3 HOTFIX-3 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-12 04:10 |
| 任務代號 | PIPE-SLIDES-HOTFIX-3 HOTFIX-3 |
| 觸發 Commit | HOTFIX-3 |
| 工作流類別 | BE-Hotfix |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES-HOTFIX-3_hotfix.md` |
| 觸發情境 | baron 審查通過 HOTFIX-3 規劃，下達緊急修補執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES-HOTFIX-3 / HOTFIX-3 / BE-Hotfix；依據 baton hotfix.md

### 執行命令（`# === [PIPE-SLIDES-HOTFIX-3 HOTFIX-3 START/END] ===` 包裹）
① 改前備份 slide_pipeline.py + static/index.html + test_slide_pipeline.py（3 .bak）
② slide_pipeline.py：
   - 新增 `_slide_head_html(title,subtitle)`（`<div class="slide-head"><h2>+<p class="slide-sub">`、html.escape）
   - 新增 `_promote_subheadings(text)`（整行 `**X**`→`### X`、regex `\r?$` 相容 CRLF、前一行非空才補空行）
   - `_page_source_md`(en)/`_deliver`(zh) parts 重排：圖 → 標題塊 → 正文(promote+normalize)；**sections.append/merged/ctx.rag_sections 原封不動**
③ static/index.html base CSS（接 #paper-content h2 後）：`.slide-head`（border-bottom var(--divider-w)/var(--color-divider) + padding-bottom）/ `.slide-head h2`（border none/margin 0）/ `.slide-sub`（15px 次級）/ `ul ul/ol ol/ul ol/ol ul { padding-left:1.5em }`
④ tests：更新既有 `##`/`###` 斷言→`<h2>`/`.slide-sub`；新增 4（圖序+標題塊 / h3 升級+\r+不產連續空行 / escape / rag 不變）
- 物理防線：僅三檔；SOP §5.2 無裸 commit

### 驗收
- pytest test_slide_pipeline 全綠 + 全套件不退化;grep format_exc/logger.error(0)/裸 commit(0)

### TODO 同步
- BE-Hotfix PIPE-SLIDES-HOTFIX-3 標 ✅；git log hash 自癒

### 收官自動化（全綠後）
- mv hotfix.md → hotfixes/ + 執行報告 → executions/；PIPE-SPEC 長駐嚴禁動

### 產出
- 執行報告 baton/2026-06-12_PIPE-SLIDES-HOTFIX-3_HOTFIX-3_執行.md（暫存→隨收官移出）

### §8 baron 命令
- git add：三檔 + 3 .bak + run 提示詞 + INDEX + TODO + hotfixes/ + executions/；msg → /tmp/PIPE-SLIDES-HOTFIX-3_msg.txt

### 停止
- 移出歸檔 + 產執行報告 + TODO 更新後立即停止；不自發 commit/push
