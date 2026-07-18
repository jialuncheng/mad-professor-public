# Brainstorming 視覺伴讀（Visual Companion）操作指引

> 本文件 vendored 自 superpowers（`obra/superpowers@HEAD` `skills/brainstorming/visual-companion.md`），**改寫貼合本專案**：所有 `scripts/xxx` 相對引用改指 `.claude-logs/tools/xxx`、mockup / session 目錄改導 `.claude-logs/baton/.brainstorm/<session>/`。
> 上位規範見 `.claude-logs/sop/2026-07-18_brainstorming_設計發想作業_SOP_手冊.md §5`。
> **前置**：Node ≥ 12（`server.cjs` 零 npm 相依）；腳本位於 `.claude-logs/tools/`（BRAINSTORM-1 C2 導入）。

---

## §1 目的

瀏覽器式視覺發散工具：當「用看的比用讀的更好懂」時，向 baron 展示 mockup、diagram、設計選項。

---

## §2 判斷框架

核心測試：**baron 用「看」會不會比用「讀」更好懂？**

**適合開瀏覽器（視覺型問題）**：
- UI 線框與版面
- 呈現系統關係的架構圖
- 並排設計比較
- 空間關係與流程圖

**留在終端（文字型問題）**：
- 需求釐清
- 概念方向選型
- 取捨分析
- 技術決策

> 「主題與 UI 有關」不自動等於「問題是視覺型」。區分「你要哪種 wizard?」（概念）與「哪種 wizard 版面感覺對?」（視覺）。

---

## §3 操作流程

### §3.1 啟動

代理執行：

```bash
.claude-logs/tools/start-server.sh --project-dir <專案根> --open
```

回傳連線資訊，含**帶 session key 查詢參數**的安全 URL、`screen_dir`、`state_dir`。落點經 `start-server.sh` 導向 `.claude-logs/baton/.brainstorm/<session>/`（已 gitignored）。

### §3.2 每一輪

1. 經 `$STATE_DIR/server-info` 確認 server 存活
2. 將 **HTML 內容片段**寫入 `screen_dir`（server 自動套用 frame 模板包裝）
3. 把含 session key 的完整 URL 給 baron
4. 描述 baron 將看到什麼
5. 請求回饋

### §3.3 回饋迴路

讀 `$STATE_DIR/events`（JSON 格式的瀏覽器互動：點選 + timestamp），與終端文字合併理解 baron 的選擇與理由。

### §3.4 迭代

回饋建議修改時，推送帶版本後綴的新 HTML（如 `layout-v2.html`）；經確認後才前進。

### §3.5 收尾

```bash
.claude-logs/tools/stop-server.sh <session_dir>
```

`--project-dir` 之 session 保留 mockup 於 `.claude-logs/baton/.brainstorm/`（gitignored）；`/tmp` session 自動刪除。**session 結束 / Checkout 前清空 mockup、守 baton 平時為空**。

---

## §4 內容撰寫指引

預設寫**內容片段**（僅內層 markup）；frame 模板自動處理 HTML 結構、CSS 主題、連線狀態、互動基建。

可用 CSS class：
- `.options` / `.option`：A/B/C 選項
- `.cards`：視覺設計
- `.mockup`：預覽
- `.split`：並排版面
- Mock 元素（`.mock-nav` / `.mock-sidebar` / `.mock-button`）：線框

瀏覽器事件以 JSON lines 記錄至 `state_dir/events`（點選 + timestamp），呈現 baron 在各選項間的探索路徑。

---

## §5 檔案依賴（vendored 位置）

| 用途 | 本專案位置 |
|---|---|
| 啟動 server | `.claude-logs/tools/start-server.sh` |
| 停止 server | `.claude-logs/tools/stop-server.sh` |
| server 主體（零 npm 相依） | `.claude-logs/tools/server.cjs` |
| frame 模板（CSS 參考） | `.claude-logs/tools/frame-template.html` |
| client 端互動 helper | `.claude-logs/tools/helper.js` |
| smoke 健康驗證 | `.claude-logs/tools/test_brainstorm_server_smoke.sh` |

> 落點改導僅發生於 `start-server.sh` 之 `SESSION_DIR`/`BRAINSTORM_DIR` 組裝（`.claude-logs/baton/.brainstorm/<session>/`）；`server.cjs` 零編輯、僅消費 `BRAINSTORM_DIR` env（BRAINSTORM-1 plan §3 源碼證據）。
