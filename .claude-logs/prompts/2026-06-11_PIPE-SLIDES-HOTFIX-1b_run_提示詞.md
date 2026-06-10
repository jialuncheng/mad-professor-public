# PIPE-SLIDES-HOTFIX-1b Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 06:54 |
| 任務代號 | PIPE-SLIDES-HOTFIX-1b HOTFIX-1b |
| 觸發 Commit | HOTFIX-1b |
| 工作流類別 | BE-Hotfix |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_PIPE-SLIDES-HOTFIX-1b_hotfix.md` |
| 觸發情境 | 影子寫庫端因譯題旁路格式不符拋 AttributeError，下達緊急修補執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- PIPE-SLIDES-HOTFIX-1b / HOTFIX-1b / BE-Hotfix；依據 baton hotfix.md「熱修復修法」

### 執行命令
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② 依 hotfix.md 落地（`# === [PIPE-SLIDES-HOTFIX-1b START/END] ===` 包裹）：
   寫入端 `raw_metadata['translated_title']` 改三欄 dict {value,source,confidence}；
   `run_phase4` 讀取端 dict 取 value（str 向後相容）
③ test_hf2 追加格式契約斷言 + 新增 upsert 同式消費測試（共 29 測綠）
- 物理防線：僅兩檔；嚴禁改共用元件/A 軌；SOP §5.2 無裸 commit

### 收官自動化（全綠後）
- mv hotfix.md → hotfixes/ + 執行報告 → executions/ + git add；兩份 `2026-06-01_PIPE*` 規格書長駐 baton 嚴禁動
- TODO：完成表 + active 移除 + 索引 ✅ + git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_PIPE-SLIDES-HOTFIX-1b_HOTFIX-1b_執行.md（暫存→隨收官移出）

### §8 baron 命令
- git add：兩檔 + 2 .bak + run 提示詞 + INDEX + TODO；msg → /tmp/PIPE-SLIDES-HOTFIX-1b_msg.txt

### 停止
- 產出執行報告 + TODO 更新後立即停止；不自發 commit/push
