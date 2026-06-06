# VISION-HOTFIX-1 — 緊急熱修復：Vision 履歷轉錄非確定性（每次輸出抖動）

> **警示**：本文件為**熱修復 (Hotfix)** 紀錄，修正履歷 Vision 解析（`chat_with_images`）因未設 temperature、吃 Gemini 預設高溫（~1.0）導致「忠實轉錄」任務每次輸出不同的問題。
> **修復原則**：只在 `chat_with_images` 加可選 `temperature` 參數並由 `ResumeProcessor` 傳 0，嚴禁夾帶其他 LLM 行為調整或無關功能。
> **工作流類別**：BE-Hotfix（改 `.py` 業務邏輯）→ 落地前強制 logging + database SOP 核查（WORKFLOW_SOP §5）。
> **狀態**：📝 文件階段（plan）。本文件僅產出於 `baton/`，**不動業務代碼**；Run（落地）由 baron 後續獨立提示詞觸發。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **VISION-HOTFIX-1** | `（待 baron Run 後回填）` | `fix(vision): VISION-HOTFIX-1 — chat_with_images 加 temperature、履歷轉錄 temp=0 確定化` |

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：同一份履歷 PDF、同一套程式碼，Vision pdf2md 每次解析輸出**字數都不同**——三次重捕分別 `13126 / 13233 / 13281 chars`（~1.2% 抖動）。導致 golden baseline 不是固定靶：每次 `capture` 都生出不同的參考，D2/D3 容差被迫吸收本可消除的雜訊。
- **受災範圍**：`ResumeProcessor.parse`（Vision 履歷轉錄）——**A 軌 pdf2md 階段 + B 軌 `run_phase1` 共用**。間接衝擊 golden 穩定性與「兩次 capture 不可重現」。
- **首發來源**：baron 比對三次 golden capture log 的 `resume.md` 字數——**非確定性問題、非例外崩潰**。

### 2. 真因診斷 (Root Cause)

- **定位程式碼**：[`llm/client.py:308`](llm/client.py:308)（`chat_with_images` 組 config）
  ```python
  config = types.GenerateContentConfig(
      system_instruction=system_instruction
  )   # ← 完全沒給 temperature → 吃 Gemini 預設 ~1.0（高溫採樣）
  ```
- **技術細節**：`chat_with_images` 建 `GenerateContentConfig` 時**未設 temperature** → Gemini SDK 採用模型預設值（約 1.0），屬**高溫採樣（creative sampling）**。但 Vision 履歷解析是**忠實轉錄（faithful transcription）**任務——應走 greedy（temp=0）以求可重現，卻被當創意生成在隨機採樣 → 每次輸出不同。
- **唯一呼叫者**：[`processor/resume_processor.py:157`](processor/resume_processor.py:157) `_analyze_resume` 呼叫 `chat_with_images` 時也沒傳 temperature（grep 證全專案僅此一處呼叫）。
- **為何切單頁救不了**：切頁改的是輸入分塊、不改採樣隨機性——每個單頁 call 仍 temp≈1.0、仍會抖；且會砸掉履歷跨頁 section 結構（`chat_with_images` docstring 明示整份送是為「判斷跨頁結構」）。**真正槓桿是 temperature，不是切頁。**

---

## 熱修復修法 (Minimal Hotfix)

**設計決策（baron 拍板）**：`chat_with_images` 加**可選 `temperature` 參數**（預設 `None` → 向後相容、維持既有行為）；`ResumeProcessor` 傳入 `temperature=0`（經 settings `LLM_VISION_TEMPERATURE`、預設 `0.0`、env 可調）。temp=0 後同一份 PDF → 輸出近乎一致。

> ⚠️ **誠實補充**：temp=0 **不保證 byte 完全相同**（Google 後端 batching/浮點/MoE 路由仍有殘餘非確定性），但會把 ~150 chars 抖動壓到「幾乎一致」。

### 改動 1：`settings.py` 新增 Vision temperature 常數（緊鄰 `LLM_VISION_MODEL`）

```diff
 LLM_VISION_MODEL = os.getenv("LLM_VISION_MODEL", CHAT_MODEL)
+# === [VISION-HOTFIX-1 START] ===
+# 履歷 Vision「忠實轉錄」temperature：預設 0.0（greedy、最大可重現）。
+# 根因：chat_with_images 原未設 temperature → 吃 Gemini 預設 ~1.0（高溫採樣）
+# 致同一份 PDF 每次輸出抖動（golden 非固定靶）。轉錄任務應 greedy。
+LLM_VISION_TEMPERATURE = float(os.getenv("LLM_VISION_TEMPERATURE", "0.0"))
+# === [VISION-HOTFIX-1 END] ===
```

### 改動 2：`llm/client.py` `chat_with_images` 加可選 `temperature` 參數

```diff
     def chat_with_images(self, messages: List[Dict[str, Any]],
                          images: List[tuple], model: str = None,
-                         timeout: float = None) -> str:
+                         timeout: float = None, temperature: float = None) -> str:
```
```diff
-            config = types.GenerateContentConfig(
-                system_instruction=system_instruction
-            )
+            # === [VISION-HOTFIX-1 START] ===
+            # temperature 為 None 時不設（維持既有行為、向後相容）；
+            # 傳入時注入 config（履歷轉錄傳 0 → greedy 確定化）。
+            _cfg_kwargs = {"system_instruction": system_instruction}
+            if temperature is not None:
+                _cfg_kwargs["temperature"] = temperature
+            config = types.GenerateContentConfig(**_cfg_kwargs)
+            # === [VISION-HOTFIX-1 END] ===
```

### 改動 3：`processor/resume_processor.py` `_analyze_resume` 傳 `temperature`

```diff
+            # === [VISION-HOTFIX-1 START] 忠實轉錄走 greedy（temp=0、可重現）===
             text = self.llm.chat_with_images(
                 messages=[{"role": "user", "content": prompt}],
                 images=[(img, "image/jpeg") for img in page_images],
                 model=settings.LLM_VISION_MODEL,
+                temperature=settings.LLM_VISION_TEMPERATURE,
             )
+            # === [VISION-HOTFIX-1 END] ===
```

**不動清單（嚴守最小侵入）**：
- `chat_with_images` 的 Semaphore acquire/release、image part 組裝、`_convert_messages`、回傳 `response.text` — 不動。
- 既有 `chat` / `chat_stream_by_sentence` / `chat_with_image`（單張）/ embedding — 不動。
- `chat_with_images` 既有呼叫的向後相容：`temperature` 預設 `None` → 不設 config、行為與改動前**完全一致**（且全專案僅 ResumeProcessor 一個呼叫者）。
- `ResumeProcessor` 的 render / prompt / fallback / 主標題抽取 — 不動。
- A 軌 pipeline_core / B 軌 run_phase1 編排 / 母提示詞 / DB Schema / 凍結合約 — 不動。

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（Run 階段執行）
`tests/test_resume_processor.py`（既有已 mock `chat_with_images` 並檢查 `call_args`）追加 / 擴充：
- `test_vision_passes_temperature_zero`：跑 `ResumeProcessor.parse`（mock LLM）→ 斷言 `mock_llm.chat_with_images.call_args.kwargs["temperature"] == 0.0`（= `LLM_VISION_TEMPERATURE` 預設）。
- （client 接線）`test_chat_with_images_wires_temperature`：以 mock `genai` client（`__new__` 繞單例）呼叫 `chat_with_images(..., temperature=0)` → 攔截 `generate_content` 的 `config`、斷言 `config.temperature == 0`；另測 `temperature=None` → config 無 temperature（向後相容）。
```bash
$ venv/bin/python -m pytest tests/test_resume_processor.py -q   # 期望：全綠（含新測試）
$ venv/bin/python -m pytest tests/ -q                          # 期望：全套件不退化（僅既知 LOG_FORMAT env flake）
```

### 2. 驗收 grep
```bash
grep -n 'VISION-HOTFIX-1' settings.py llm/client.py processor/resume_processor.py   # 期望：三檔 START/END 包裹
grep -n 'LLM_VISION_TEMPERATURE' settings.py processor/resume_processor.py          # 期望：定義 + 傳值命中
grep -n 'temperature: float = None' llm/client.py                                   # 期望：chat_with_images 簽名加參數
grep -n 'temperature=settings.LLM_VISION_TEMPERATURE' processor/resume_processor.py # 期望：ResumeProcessor 傳值
# SOP — logging / database
grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' llm/client.py processor/resume_processor.py
grep -nE '\.commit\(\)' llm/client.py processor/resume_processor.py | grep -v 'with .*session.*begin'
```

### 3. 本地 E2E 快速復現與驗證（baron）
重跑 Vision 解析 **兩次**（清 `_capture_work` 後各跑一次）→ 比對 `resume.md` 字數：temp=0 後兩次應**幾乎一致**（不再 ±150 chars 抖動）。
```bash
rm -rf tests/golden_baseline/_capture_work/900001/golden_resume
venv/bin/python tools/golden_baseline.py capture resume --force   # 跑兩次比對字數穩定性
```

### 4. ⚠️ 行為變更 + Golden 重捕（重要）
本 hotfix **改變 Vision 轉錄輸出**（temp ~1.0 → 0）→ **A 軌 golden + B 軌 P1/final 都會變**（這是**共用 Vision 解析**、非單軌）。落地後須**重捕 resume golden**（且自此可重現、不再抖）：
```bash
rm -rf tests/golden_baseline/_capture_work/900001/golden_resume   # 先清中間快取（--force 不清、見前次分析）
venv/bin/python tools/golden_baseline.py capture resume --force
```

---

## 回退與備案

```bash
# 單獨回退本 hotfix（恢復預設高溫行為）
git revert <VISION-HOTFIX-1-hash>

# 或不回退代碼、即時調回高溫：.env 設 LLM_VISION_TEMPERATURE=1.0
```

---

## 附錄：受影響檔案與包裹標記

| 檔案 | 改動 | 標記 |
|---|---|---|
| `settings.py` | 新增 `LLM_VISION_TEMPERATURE`（預設 0.0）| `# === [VISION-HOTFIX-1 START/END] ===` |
| `llm/client.py` | `chat_with_images` 加 `temperature` 參數 + 注入 config | 同上 |
| `processor/resume_processor.py` | `_analyze_resume` 傳 `temperature=settings.LLM_VISION_TEMPERATURE` | 同上 |
| `tests/test_resume_processor.py` | 追加 temperature 傳遞 / 接線測試 | 同上 |
| `.bak` 備份 | 三業務檔 + 測試檔改前 `.bak` → `archive/` | 改前備份鐵律 |

## §commit baron 執行命令（Run 階段交付參考）
```bash
# 備份
cp settings.py .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_settings.py.bak
cp llm/client.py .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_client.py.bak
cp processor/resume_processor.py .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_resume_processor.py.bak
cp tests/test_resume_processor.py .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_test_resume_processor.py.bak

# git add（收官 mv hotfix.md + 執行.md → hotfixes/ 後）
git add settings.py llm/client.py processor/resume_processor.py tests/test_resume_processor.py
git add .claude-logs/archive/2026-06-06_VISION-HOTFIX-1_*.bak
git add .claude-logs/TODO.md .claude-logs/prompts/INDEX.md
git add .claude-logs/prompts/2026-06-06_VISION-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/2026-06-06_VISION-HOTFIX-1_run_提示詞.md
git add .claude-logs/hotfixes/2026-06-06_VISION-HOTFIX-1_Vision轉錄temperature確定化_hotfix.md
git add .claude-logs/hotfixes/2026-06-06_VISION-HOTFIX-1_執行.md

# commit（msg 草稿 /tmp/VISION-HOTFIX-1_msg.txt）
git commit -F /tmp/VISION-HOTFIX-1_msg.txt
```

### commit message 草稿
```
fix(vision): VISION-HOTFIX-1 — chat_with_images 加 temperature、履歷轉錄 temp=0 確定化

修改 settings.py：
1. 新增 LLM_VISION_TEMPERATURE（預設 0.0、env 可調），供履歷 Vision 忠實轉錄走 greedy。
修改 llm/client.py：
1. chat_with_images 加可選 temperature 參數（預設 None 向後相容）；傳入時注入 GenerateContentConfig。
修改 processor/resume_processor.py：
1. _analyze_resume 呼叫 chat_with_images 時傳 temperature=settings.LLM_VISION_TEMPERATURE（=0），消除 Vision 轉錄每次輸出抖動。
修改 tests/test_resume_processor.py：
1. 追加 temperature 傳遞與 client 接線測試。
真因：chat_with_images 原未設 temperature → 吃 Gemini 預設 ~1.0（高溫採樣），忠實轉錄任務卻在隨機採樣致同一份 PDF 每次輸出不同。
變更與新增區塊已使用 # === [VISION-HOTFIX-1 START/END] === 註解物理包裹。
注：Vision 轉錄輸出改變（共用 A 軌 pdf2md + B 軌 P1）→ 須重捕 resume golden（自此可重現）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```
