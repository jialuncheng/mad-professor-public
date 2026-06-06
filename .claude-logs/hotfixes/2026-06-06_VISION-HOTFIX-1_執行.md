# VISION-HOTFIX-1 — Vision 履歷轉錄 temperature 確定化 執行報告

---

**任務代號**：VISION-HOTFIX-1（BE-Hotfix）
**執行日期**：2026-06-06
**依據計畫**：`.claude-logs/baton/2026-06-06_VISION-HOTFIX-1_Vision轉錄temperature確定化_hotfix.md`
**次級參考**：`sop/2026-05-23_logging_SOP_手冊.md` / `sop/2026-05-23_database_SOP_手冊.md`
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed（程式碼落地 + 驗收全綠 + 收官歸檔；待 baron commit）

---

## §1 基準與完成狀態
- **基準**：RESUME-P3 META-HOTFIX-1（`2ba97fc`）head。
- **完成狀態**：`settings.py` 加 `LLM_VISION_TEMPERATURE`(0.0) + `llm/client.py` `chat_with_images` 加可選 `temperature` 參數（注入 config）+ `processor/resume_processor.py` `_analyze_resume` 傳 0 + `tests/test_resume_processor.py` 追加 2 測試；`# === [VISION-HOTFIX-1 START/END] ===` 包裹；改前 4 `.bak`。**未 commit**（待 baron）。

---

## §2 落地 Commit 表格
| # | Hash | Subject |
|---|---|---|
| VISION-HOTFIX-1 | （待回填）| `fix(vision): VISION-HOTFIX-1 — chat_with_images 加 temperature、履歷轉錄 temp=0 確定化` |

---

## §3 變動檔案清單
| 檔案 | 變動 | 備份 |
|---|---|---|
| `settings.py` | 新增 `LLM_VISION_TEMPERATURE`（預設 0.0）| `archive/2026-06-06_VISION-HOTFIX-1_settings.py.bak` |
| `llm/client.py` | `chat_with_images` 加 `temperature` 參數 + 注入 `GenerateContentConfig` | `archive/2026-06-06_VISION-HOTFIX-1_client.py.bak` |
| `processor/resume_processor.py` | `_analyze_resume` 傳 `temperature=settings.LLM_VISION_TEMPERATURE` | `archive/2026-06-06_VISION-HOTFIX-1_resume_processor.py.bak` |
| `tests/test_resume_processor.py` | 追加 `test_vision_passes_temperature_zero` + `test_chat_with_images_wires_temperature` | `archive/2026-06-06_VISION-HOTFIX-1_test_resume_processor.py.bak` |

`git diff --stat`：
```
 llm/client.py                  | 16 ++++++++++++----
 processor/resume_processor.py  |  3 +++
 settings.py                    |  6 ++++++
 tests/test_resume_processor.py | 43 +++++++++++++++++++++++++++++++++++++++++
 4 files changed, 64 insertions(+), 4 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因
`llm/client.py:308` `chat_with_images` 組 `GenerateContentConfig(system_instruction=...)` **未設 temperature** → 吃 Gemini 預設 ~1.0（高溫採樣）；`resume_processor.py:157` 呼叫也沒傳。**忠實轉錄任務在隨機採樣** → 同份 PDF 每次輸出不同（13126/13233/13281 chars）、golden 非固定靶。切頁救不了（temp 才是槓桿、且切頁砸跨頁結構）。

### §4.2 修法
1. **`settings.py`**：`LLM_VISION_TEMPERATURE = float(os.getenv("LLM_VISION_TEMPERATURE", "0.0"))`（緊鄰 `LLM_VISION_MODEL`）。
2. **`llm/client.py` `chat_with_images`**：簽名加 `temperature: float = None`（預設 None 向後相容）；config 改：
   ```python
   _cfg_kwargs = {"system_instruction": system_instruction}
   if temperature is not None:
       _cfg_kwargs["temperature"] = temperature
   config = types.GenerateContentConfig(**_cfg_kwargs)
   ```
3. **`processor/resume_processor.py` `_analyze_resume`**：`chat_with_images(..., temperature=settings.LLM_VISION_TEMPERATURE)`。
- **向後相容**：`temperature=None` → 不設 config、行為與改前完全一致（全專案僅 ResumeProcessor 一個呼叫者）。
- **不動**：Semaphore/image part/_convert_messages/response.text、chat/chat_stream/chat_with_image/embedding、ResumeProcessor render/prompt/fallback、A軌/B軌編排/母提示詞/DB/合約。

### §4.3 測試
- `test_vision_passes_temperature_zero`：`ResumeProcessor.parse`（mock LLM）→ `chat_with_images.call_args.kwargs["temperature"] == 0.0`（= `LLM_VISION_TEMPERATURE`）。
- `test_chat_with_images_wires_temperature`：mock genai client（`__new__` 繞單例）→ `chat_with_images(temperature=0)` 攔 `generate_content` config、斷言 `config.temperature == 0`；`temperature=None` → `config.temperature is None`（向後相容）。

---

## §5 測試結果與 SOP 核查

### §5.1 驗收 grep
```
$ grep -c 'VISION-HOTFIX-1' settings.py llm/client.py processor/resume_processor.py
settings.py:2 / llm/client.py:4 / resume_processor.py:2     ✅ 三檔包裹
$ grep -n 'LLM_VISION_TEMPERATURE' settings.py processor/resume_processor.py
settings.py:26 定義 / resume_processor.py:162 傳值          ✅
$ grep -n 'temperature: float = None' llm/client.py
L276（chat_with_images 簽名）                              ✅
$ venv/bin/python -c "import settings; print(settings.LLM_VISION_TEMPERATURE)"
0.0                                                       ✅
$ grep -nc 'def test_vision_passes_temperature_zero\|def test_chat_with_images_wires_temperature' tests/test_resume_processor.py
2                                                         ✅
```

### §5.2 SOP 一致性核查（BE-Hotfix 強制）
```
# logging：logger.error 須 exc_info
$ grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' llm/client.py processor/resume_processor.py
processor/resume_processor.py:166: self.logger.error(f"Vision 履歷解析失敗 {paper_name}: {e}")
```
- ⚠️ **判定：本 hotfix 新增代碼合規**——`resume_processor.py:166` 的 `logger.error`（無 `exc_info=True`）為**前置既存**（在既有 except 區塊、`raise ... from e` 前）、**非本 hotfix 引入**（本 hotfix 只在 `chat_with_images` call 加 `temperature` 參數、未碰錯誤處理）。本 hotfix START/END 區塊內**無任何 logger.error**。該前置行屬獨立 SOP cleanup 候選、不在本 hotfix 範圍（hotfix 不動清單明訂 ResumeProcessor fallback 不動）。
```
# database：裸 commit
$ grep -nE '\.commit\(\)' llm/client.py processor/resume_processor.py | grep -v 'with .*session.*begin'
無命中（合規）
```

### §5.3 pytest
```
$ venv/bin/python -m pytest tests/test_resume_processor.py -q
16 passed in 5.91s     ✅（14 既有 + 2 新）

$ venv/bin/python -m pytest tests/ -q
1 failed, 504 passed, 3 skipped in 26.36s
FAILED tests/test_logging_config.py::test_settings_log_format_default_auto   ← 既知 LOG_FORMAT env flake、與本任務無關
```
- **504 passed**（META 後 502 + 本次 2 新）；唯一 failed 為既知環境 flake。✅ 不退化。
- 語法 `ast.parse`（4 檔）→ OK。

---

## §6 不可動清單遵守狀態（hotfix.md）
| 不可動項 | 判定 |
|---|---|
| `chat_with_images` Semaphore/image part/_convert_messages/response.text | [x] ✅ 未動 |
| `chat` / `chat_stream_by_sentence` / `chat_with_image`（單張）/ embedding | [x] ✅ 未動 |
| `chat_with_images` 既有呼叫向後相容（temperature 預設 None）| [x] ✅ 既有行為不變、全專案僅 1 呼叫者 |
| `ResumeProcessor` render / prompt / fallback / 主標題抽取 | [x] ✅ 未動（僅加 temperature kwarg）|
| A軌 pipeline_core / B軌 run_phase1 / 母提示詞 / DB Schema / 凍結合約 | [x] ✅ 未動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

`git diff --stat` 證：本次僅 `settings.py` + `llm/client.py` + `processor/resume_processor.py` + `tests/test_resume_processor.py`。

---

## §7 銜接與下一步
- **⚠️ Golden 重捕（baron 運維、非 commit）**：本 hotfix 改變 Vision 轉錄輸出（temp ~1.0→0）→ **A軌 pdf2md golden + B軌 P1/final 都會變**（共用 `ResumeProcessor.parse`）。落地後須**先清中間快取再重捕**（`--force` 不清 `_capture_work`、見前次分析）：
  ```bash
  rm -rf tests/golden_baseline/_capture_work/900001/golden_resume
  venv/bin/python tools/golden_baseline.py capture resume --force
  ```
- **驗穩定性**：清快取後連跑兩次 capture，比對 `resume.md` 字數應**幾乎一致**（不再 ±150 抖動）。
- **⚠️ 誠實限制**：temp=0 不保證 byte 完全相同（Google 後端殘餘非確定）、僅大幅壓抖動。
- **獨立 cleanup 候選**：`resume_processor.py:166` 前置 `logger.error` 缺 `exc_info=True`（非本 hotfix 引入）。

---

## §8 baron 執行命令
```bash
# 1. 備份檔案已完成（§3）

# 2. 收官搬移已由 Claude Code 完成（mv hotfix.md + 執行.md → hotfixes/）；git add 清單：
git add settings.py
git add llm/client.py
git add processor/resume_processor.py
git add tests/test_resume_processor.py
git add .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_settings.py.bak
git add .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_client.py.bak
git add .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_resume_processor.py.bak
git add .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_test_resume_processor.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-06_VISION-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/2026-06-06_VISION-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/hotfixes/2026-06-06_VISION-HOTFIX-1_Vision轉錄temperature確定化_hotfix.md
git add .claude-logs/hotfixes/2026-06-06_VISION-HOTFIX-1_執行.md

# 3. commit message 草稿（已寫入 /tmp/VISION-HOTFIX-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/VISION-HOTFIX-1_msg.txt
```

### §8.2 commit message 草稿
```
fix(vision): VISION-HOTFIX-1 — chat_with_images 加 temperature、履歷轉錄 temp=0 確定化

修改 settings.py：
1. 新增 LLM_VISION_TEMPERATURE（預設 0.0、env 可調），供履歷 Vision 忠實轉錄走 greedy。
修改 llm/client.py：
1. chat_with_images 加可選 temperature 參數（預設 None 向後相容）；傳入時注入 GenerateContentConfig。
修改 processor/resume_processor.py：
1. _analyze_resume 呼叫 chat_with_images 時傳 temperature=settings.LLM_VISION_TEMPERATURE（=0），消除 Vision 轉錄每次輸出抖動。
修改 tests/test_resume_processor.py：
1. 追加 test_vision_passes_temperature_zero + test_chat_with_images_wires_temperature。
真因：chat_with_images 原未設 temperature → 吃 Gemini 預設 ~1.0（高溫採樣），忠實轉錄任務卻在隨機採樣致同一份 PDF 每次輸出不同。
變更與新增區塊已使用 # === [VISION-HOTFIX-1 START/END] === 註解物理包裹。
注：Vision 轉錄輸出改變（共用 A 軌 pdf2md + B 軌 P1）→ 須清 _capture_work 後重捕 resume golden（自此可重現）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

> ⚠️ 提示詞範本 msg 署名為 `Claude Sonnet 4.6`；本 session 實際模型 Opus 4.8，已校正署名。

---

## §9 回退方式（Rollback）
```bash
git revert <VISION-HOTFIX-1-hash>          # 回滾代碼
# 或不回滾、即時調回高溫：.env 設 LLM_VISION_TEMPERATURE=1.0
```

---

## §99 Revision
- v1 (2026-06-06)：VISION-HOTFIX-1 落地——`settings.py` 加 `LLM_VISION_TEMPERATURE`(0.0) + `llm/client.py` `chat_with_images` 加可選 `temperature` 參數〔None 向後相容、非 None 注入 config〕+ `resume_processor.py` 傳 0、Vision 忠實轉錄走 greedy 消除每次輸出抖動；VISION-HOTFIX-1 包裹 + 4 .bak；追加 test_vision_passes_temperature_zero + test_chat_with_images_wires_temperature；grep 全綠（三檔包裹/常數定義+傳值/簽名參數/2 測試）、SOP database 合規、logging 僅前置既存 logger.error〔非本 hotfix 引入〕、test_resume_processor 16 passed、全套件 504 passed（唯一 failed 既知 LOG_FORMAT env flake）；⚠️ 共用 A軌 pdf2md+B軌 P1、Vision 輸出變→清 _capture_work 後重捕 resume golden；temp=0 不保證 byte 相同〔僅壓抖動〕。
