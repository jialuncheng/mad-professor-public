# META-NORM C4 Run 提示詞

## 元數據

| 欄位 | 值 |
|---|---|
| 收到時間 | 2026-06-11 21:50 |
| 任務代號 | META-NORM C4 — Subtitle（小標題結構化）|
| 觸發 Commit | C4 |
| 工作流類別 | BE-Refactor |
| 相關產出檔案 | `.claude-logs/baton/2026-06-11_META-NORM_..._tasks.md` |
| 觸發情境 | baron 審查通過 C3，下達 C4 執行指令 |

---

## 正文（原始提示詞摘要）

### 任務資訊
- META-NORM / C4 / BE-Refactor；tasks §8 C4（plan U8/D）

### 執行命令（`# === [META-NORM C4 START/END] ===` 包裹）
① 改前備份 slide_pipeline.py + test_slide_pipeline.py（2 .bak）
② slide_pipeline.py：
   - `_VISION_PROMPT` schema 追加 `subtitle` 欄（大標題 title、次級小標題 subtitle）
   - run_phase1 units.append 收 `subtitle`
   - page_key/section_summaries fallback：title 空但 subtitle 存在 → 用 subtitle 當標題生 key/對齊（防分隔頁 key 漂移）
   - `_translate_pages_parallel` 翻譯 tuple 加 `("subtitle","title")`、回傳結構帶 subtitle 譯文
   - `_page_source_md`(en)/`_deliver`(zh)：subtitle 存在 → `## {title}` 後、圖前渲染 `### {subtitle}`
③ tests 追加（subtitle 提取+翻譯+雙語 ### 渲染 + 無大標題 fallback key）
- 物理防線：僅兩檔；SOP §5.2 無裸 commit

### 驗收
- pytest tests/test_slide_pipeline.py + 全套件不退化;grep format_exc/logger.error(0)/裸 commit(0)

### TODO 同步
- C4 ✅、C5 🟡 WIP；git log hash 自癒

### 產出
- 執行報告 baton/2026-06-11_META-NORM_C4_執行.md（暫存、嚴禁 mv/git add baton）

### §8 baron 命令
- git add：slide_pipeline + test + 2 .bak + 提示詞 + INDEX + TODO；msg → /tmp/META-NORM_C4_msg.txt

### 停止
- 產出 C4_執行.md + TODO 更新後立即停止；不續 C5、不自發 commit/push
