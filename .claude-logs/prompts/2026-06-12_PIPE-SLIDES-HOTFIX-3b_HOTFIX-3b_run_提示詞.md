# PIPE-SLIDES-HOTFIX-3b HOTFIX-3b Run 提示詞

## 元數據審計塊
| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-12 05:25 |
| 任務代號 | PIPE-SLIDES-HOTFIX-3b HOTFIX-3b |
| 觸發 Commit | HOTFIX-3b |
| 相關產出檔案 | .claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3b_hotfix.md |
| 觸發情境 | baron 審查並通過 HOTFIX-3b 前端排版補完規劃，下達緊急修補執行指令 |
| 工作流類別 | FE-Hotfix |

## 正文（原文，敏感資訊已去識別化——本提示詞無敏感資訊）

你現在扮演 Claude Code，執行單一 Commit HOTFIX-3b（FE-Hotfix）。

### 強制讀檔
- CLAUDE.md
- .claude-logs/ref/WORKFLOW_SOP.md
- .claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3b_hotfix.md

### 執行命令
依 hotfix.md 進行樣式修改，修改區塊統一包裹在 HOTFIX-3 既有 START/END 註解內。

1. 備份（最先）：
   `cp static/index.html .claude-logs/archive/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_index.html.bak`

2. 樣式修改 static/index.html：
   在 HOTFIX-3 「二：清單縮排」CSS 區塊，selector 前置 `#paper-content ul, #paper-content ol,`，
   padding-left: 1.5em 不變，解決全域 reset 致第一層 bullet 凸排。
   結構：
   ```css
   /* 二：清單縮排（結構性 fallback、主題無關、含自訂主題受益）
      L79 全域 reset 把 ul/ol padding 歸零 → list-style:outside 下 bullet 凸排；
      此處補回 top-level + 巢狀縮排（HOTFIX-3b：補 top-level、原僅巢狀） */
   #paper-content ul, #paper-content ol,
   #paper-content ul ul, #paper-content ol ol,
   #paper-content ul ol, #paper-content ol ul {
     padding-left: 1.5em;
   }
   ```

### 物理防線與驗收
1. 僅改 static/index.html 單檔，不動 .py。
2. grep 驗收：
   - `grep -n "#paper-content ul, #paper-content ol," static/index.html`（預期 1）
   - `grep -n "#paper-content ul ul, #paper-content ol ol," static/index.html`（預期 1）
   - `for f in static/themes/*.css; do grep -c "paper-content ul\|paper-content ol\|paper-content li" "$f"; done`（皆 0）
3. 回歸：`venv/bin/python -m pytest tests/ -q`（全綠、與 HOTFIX-3 一致）。

### TODO.md 同步 + Hash 自癒
- FE-Hotfix PIPE-SLIDES-HOTFIX-3b 標 ✅。
- git log 自癒回填所有「待 baron 回填」佔位符。

### 產出與歸檔
1. 執行報告 → .claude-logs/baton/2026-06-12_PIPE-SLIDES-HOTFIX-3b_HOTFIX-3b_執行.md（template_execution.md）
2. baton 移出：
   - hotfix.md → .claude-logs/hotfixes/
   - 執行.md → .claude-logs/executions/
   - 註：PIPE-SPEC specification.md 嚴禁移動。

### §8 baron 執行命令
git add 清單（index.html / .bak / run 提示詞 / INDEX / TODO / hotfix.md / 執行.md）+ msg 草稿 /tmp/PIPE-SLIDES-HOTFIX-3b_msg.txt + baron 手動 commit。

### 停止指令
完成 TODO 更新與 baton 歸檔後立即停止，嚴禁自發 git commit / push。
