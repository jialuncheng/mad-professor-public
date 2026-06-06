`````markdown
# 2026-06-06 — VISION-HOTFIX-1 Run（Vision 轉錄 temperature 確定化·落地）提示詞

> **收到時間**：2026-06-06 16:05（UTC+8）
> **任務代號**：VISION-HOTFIX-1（BE-Hotfix 落地執行）
> **觸發 commit**：VISION-HOTFIX-1
> **相關產出檔案**：`.claude-logs/baton/2026-06-06_VISION-HOTFIX-1_Vision轉錄temperature確定化_hotfix.md`
> **觸發情境**：baron 確認 hotfix 設計後下達執行指令。

---

## 完整提示詞

````
### 📊 元數據審計塊
| 收到時間 2026-06-06 16:05 | 任務 VISION-HOTFIX-1 | 觸發 Commit VISION-HOTFIX-1 | 依據 hotfix.md |

## 🗄️ 第一步：歸檔本提示詞（先完成才准讀檔/grep/改碼）
寫入 prompts/2026-06-06_VISION-HOTFIX-1_run_提示詞.md + 更新 INDEX（補條目 + 時間排序首行、超 15 刪最舊）。

你扮演 Claude Code，執行單一 Commit VISION-HOTFIX-1（BE-Hotfix）。

### 強制讀檔
CLAUDE.md / WORKFLOW_SOP.md / hotfix.md / logging_SOP / database_SOP

### 具體實作（# === [VISION-HOTFIX-1 START/END] === 包裹）
1. 備份 settings.py + llm/client.py + processor/resume_processor.py + tests/test_resume_processor.py → .bak。
2. settings.py：新增 LLM_VISION_TEMPERATURE = float(getenv("LLM_VISION_TEMPERATURE","0.0"))（緊鄰 LLM_VISION_MODEL）。
3. llm/client.py chat_with_images：簽名加 temperature: float = None；config 改 _cfg_kwargs，temperature 非 None 才注入。
4. processor/resume_processor.py _analyze_resume：chat_with_images 加 temperature=settings.LLM_VISION_TEMPERATURE。
5. tests/test_resume_processor.py：追加 test_vision_passes_temperature_zero（ResumeProcessor 傳 0.0）+ test_chat_with_images_wires_temperature（注入 config + None 向後相容）。
6. 不動：Semaphore/image part/_convert_messages/response.text、chat/chat_stream/chat_with_image/embedding、ResumeProcessor render/prompt/fallback、A軌/B軌編排/母提示詞/DB/合約。

### 三道防線
- 物理：僅 4 檔；測試：pytest test_resume_processor + 全套件 + grep（VISION-HOTFIX-1 包裹 / LLM_VISION_TEMPERATURE / temperature 參數 / 傳值）+ SOP；文件：commit 由 baron。

### 備份
cp settings.py / llm/client.py / processor/resume_processor.py / tests/test_resume_processor.py → archive/*.bak

### TODO 同步 + Hash 自癒
頂部 ✅ BE-Hotfix 段補 VISION-HOTFIX-1（hash 待回填）+ 索引追加；git log 回填殘留佔位符。

### 產出 + 收官歸檔（hotfix 一次性）
baton/2026-06-06_VISION-HOTFIX-1_執行.md（template_execution）→ 收官 mv hotfix.md + 執行.md → hotfixes/；§8 git add 清單 + msg（/tmp/VISION-HOTFIX-1_msg.txt）。

### 🛑 停止
產報告 + 搬移後立即停止；不動未列代碼、不自發 commit/push。
````

---

## 執行結果摘要

- ⏳ 進行中 → 完成
- 改檔：settings.py（LLM_VISION_TEMPERATURE）+ llm/client.py（chat_with_images temperature 參數）+ resume_processor.py（傳值）+ test_resume_processor.py（2 測試）+ 4 .bak
- 驗收：pytest + grep（包裹/常數/參數/傳值）+ SOP
- 收官：hotfix.md + 執行.md mv → hotfixes/
- 是否動其他業務代碼：否；是否 commit：否（待 baron）

## 後續引用

Vision 轉錄 temp=0 greedy 確定化；⚠️ 共用 A軌 pdf2md + B軌 P1、Vision 輸出改變 → 須清 _capture_work 後重捕 resume golden（自此可重現）；msg 署名校正 Opus 4.8。
`````
