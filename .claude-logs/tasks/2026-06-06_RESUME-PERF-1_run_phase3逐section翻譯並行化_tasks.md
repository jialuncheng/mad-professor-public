# RESUME-PERF-1 run_phase3 逐 section 翻譯並行化 — Tasks

> 本文件為 RESUME-PERF-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-06_RESUME-PERF-1_run_phase3逐section翻譯並行化_plan_v1.md`（§99.2 v2、§7 OQ Q1-Q7 核准）產出，含 4 個 Commit（C1 → C2 → C3 → C4 Checkout）。
> 工作流類別：**BE-Refactor**（改 `.py` 業務邏輯）→ 落地前強制 logging + database SOP 核查（§5）。
> baron 拍板「**不必等五路、現在做**」（plan Q5 原寫「Flip 前」屬優先序判斷、非技術依賴；RESUME-PERF-1 自包於 resume_pipeline.py、不依賴其餘四路與 A 軌）。

---

## §0 改版規則
- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （C3 沿用既有 `tests/test_resume_pipeline.py` 追加測試）|
| **修改檔案** | 2 個 | `pipelines/resume_pipeline.py`（C1 收集-組裝解耦 + C2 ThreadPool 並行翻譯）/ `tests/test_resume_pipeline.py`（C3 並行專屬測試）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`（高優先新增 → Checkout 結案）/ `prompts/INDEX.md`（Tasks + 各階段提示詞登錄）|
| **Commits** | 4 個 | C1 → C2 → C3 → C4（Checkout）|
| **baton 歸檔** | 1 次 | C4 Checkout 一次性 `mv` plan_v1 → `plans/` + tasks → `tasks/` + C1-C4 報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：B 軌 `run_phase3` 逐 heading section 翻譯為**完全序列**——`_restore_one_section` 對每個標題/正文同步呼叫 `_t`（阻塞式 LLM）、遞迴序列走 children；A 軌等價結構實測 translate **~315-330s（佔單份 76%）**，B 軌 resume 影子上傳承此瓶頸。
- **解法**：原子化拆 4 commit——
  - **C1 — Collect/Assemble 重構（收集-組裝解耦）**：把 `_restore_one_section` 的「邊走邊翻邊組」拆成「**先序列收集有序 render slot**（標題/正文/passthrough，記錄層級與正規化旗標）→ **序列翻譯** → **按序組裝**」；**仍序列、輸出 byte 等價**（既有 29 resume 測試保持全綠）。
  - **C2 — ThreadPool 並行翻譯（序列→受限並行）**：把 C1 的「序列翻譯 slot」換成 `ThreadPoolExecutor`（`max_workers=LLM_MAX_CONCURRENT`），結果**依 slot index 保序**回填；實際 API 併發**受既有 `LLMClient._api_semaphore` 限流**；單 slot 翻譯失敗**退回原文 + warning**（不污染其他、保交付）。輸出與序列版**邏輯等價**。
  - **C3 — Unit Tests（單元測試）**：`tests/test_resume_pipeline.py` 追加並行專屬測試（mock 確定化譯文 byte 等拍保序 / 併發峰值 ≤ `LLM_MAX_CONCURRENT` / 單 unit 異常隔離 / 退化路徑單呼叫不並行）。
  - **C4 — Checkout（收官驗收歸檔）**：Conformance 三維度 + SOP 核查 + baton 一次性歸檔。
- **影響範圍**：2 檔；**只改翻譯「執行方式」（序列→並行）、不改輸出內容/順序/層級/段落/header**；不改 Translator/LLMClient/凍結合約/DB。行為等價、僅 wall-clock 下降（預估 ~5x）。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/resume_pipeline.py` `_restore_sections_markdown` L549-560 | 序列 `for sec: _restore_one_section(...)` → 組單一字串 | 內部翻譯全序列 |
| `_restore_one_section` L562-607 | 對 title（L578）/ text（L587）/ 字串 fallback（L599）**同步 `_t`**、`for child`（L606）**遞迴序列**；formula/figure/table 不翻直 append；title 套 HEADING 層級、text 套 PARA 正規化 | **逐單元序列翻譯**、~40 個 LLM call 串行 = 瓶頸 |
| `_t` L617+ | `tr.translate(...)` 阻塞式單元翻譯 | 被序列逐一呼叫 |
| `llm/client.py` `_api_semaphore` L49 | `threading.Semaphore(LLM_MAX_CONCURRENT=6)`、每次 `chat` 套用 | ✅ 限流基建現成、thread-safe（C2 沿用）|

---

## §3 觀察問題

### 問題 #1：逐 section 翻譯完全序列（效能瓶頸）
- **證據**：`pipelines/resume_pipeline.py:578/587/599`（同步 `_t`）+ `:606`（遞迴序列）；無 `await/asyncio/gather/ThreadPool`（grep 零命中）。
- **影響**：整份履歷 ~40 個翻譯單元串行、A 軌等價結構實測 translate ~315-330s（76%）；B 軌 resume 影子上傳同量級。

---

## §4 設計方案

### §4.1 C1 — Collect/Assemble 重構（收集-組裝解耦、仍序列、行為等價）
新增私有 `_collect_render_slots(sections, depth, out)`：遞迴走訪（鏡像現行 `_restore_one_section` 順序），**不翻譯**、只 append 有序 slot：
- 標題 → `{"kind":"title","text":title,"level":min(2+depth,6)}`（沿用 HEADING-HOTFIX 層級邏輯、值不變）
- text item → `{"kind":"content","text":content}`（待翻 + 待 PARA 正規化）
- formula/figure/table（非 text、有 content）→ `{"kind":"raw","text":content}`（不翻、passthrough）
- 字串 fallback → `{"kind":"content","text":txt}`
- children → 遞迴 `depth+1`
`_restore_sections_markdown` 改為：collect slots → **逐 slot 序列翻譯**（title/content 走 `_t`）→ **按序組裝**（title→`f"{'#'*level} {zh}"`；content→`_normalize_paragraph_breaks(zh)`；raw→原文）→ join。**輸出與現行 byte 等價**。

### §4.2 C2 — ThreadPool 並行翻譯（序列→受限並行）
把 C1 的「逐 slot 序列翻譯」換成 `concurrent.futures.ThreadPoolExecutor(max_workers=LLM_MAX_CONCURRENT)`：對所有 `kind in (title,content)` 的 slot 提交 `_t`、**用 slot index 保序**回填譯文；`kind=raw` 不提交。實際 API 併發受既有 `LLMClient._api_semaphore` 限流（C2 不新增鎖）。**異常隔離**：單 slot future 拋例外 → 該 slot 退回**原文** + `logger.warning`，不中斷其餘、整份仍交付。組裝邏輯不變（沿用 C1）。

### §4.3 C3 — Unit Tests（單元測試）
`tests/test_resume_pipeline.py` 追加（mock Translator 確定化）：保序 byte 等拍 / 併發峰值 ≤ `LLM_MAX_CONCURRENT` / 單 unit 異常隔離退原文 / 退化路徑單呼叫不並行。

### §4.4 C4 — Checkout
Conformance 三維度（plan §2 U1-U7 / tasks §6 / 不可動清單 git 證據）+ SOP 核查 + 提示詞稽核 + baton 一次性歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 並行導致章節/正文錯位（失序）| 🔴 高 | C1 先做收集-組裝解耦（slot index 為唯一順序源）、C2 僅換執行緒、結果按 index 回填；C3 mock 確定化 byte 等拍強驗保序 |
| C1 重構改變輸出（破壞 HEADING/PARA/header）| 🟡 中 | C1 為行為等價重構、既有 29 resume 測試保持全綠為基本盤；層級/正規化邏輯原值搬移不改 |
| 並行加劇 429 / 配額超賣 | 🟢 低 | 沿用 `LLMClient._api_semaphore`（6）、不新增鎖；既有 `retry_call` 吸收 transient |
| Translator/LLMClient 非 thread-safe | 🟢 低 | `Translator.translate` 用 locals 無 per-call 狀態、LLMClient 共享 httpx.Client + Semaphore 皆 thread-safe（plan §3 grep 證）|
| 單 unit 失敗拖垮整份 | 🟢 低 | C2 異常隔離：退原文 + warning、保 `BilingualMarkdownSpec` 交付 |

---

## §6 測試計畫

### §6.1 C1 驗收
```bash
grep -n 'RESUME-PERF-1 C1\|_collect_render_slots' pipelines/resume_pipeline.py   # 期望：包裹 + 新 helper 命中
grep -nc 'self._t(' pipelines/resume_pipeline.py                                 # 期望：仍序列呼叫（C1 不並行）
venv/bin/python -m pytest tests/test_resume_pipeline.py -q                       # 期望：既有 resume 測試全綠（byte 等價、輸出不變）
```

### §6.2 C2 驗收
```bash
grep -n 'RESUME-PERF-1 C2\|ThreadPoolExecutor\|LLM_MAX_CONCURRENT' pipelines/resume_pipeline.py   # 期望：並行 + 限流命中
grep -n "event': 'resume_translate_unit_fallback'\|退回原文\|logger.warning" pipelines/resume_pipeline.py  # 期望：異常隔離 warning
# SOP — logging：logger.error 須 exc_info / database：無裸 commit
grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' pipelines/resume_pipeline.py
grep -nE '\.commit\(\)' pipelines/resume_pipeline.py | grep -v 'with .*session.*begin'
venv/bin/python -m pytest tests/test_resume_pipeline.py -q                       # 期望：既有 resume 測試仍全綠（行為等價）
```

### §6.3 C3 驗收
```bash
grep -n 'def test_p3_parallel_order_byte_equal\|def test_p3_parallel_concurrency_capped\|def test_p3_parallel_unit_error_isolated\|def test_p3_parallel_degraded_single_call' tests/test_resume_pipeline.py  # 期望：4 新測試
venv/bin/python -m pytest tests/test_resume_pipeline.py -q   # 期望：全綠（含 4 新測試）
venv/bin/python -m pytest tests/ -q                         # 期望：全套件不退化（僅既知 LOG_FORMAT env flake）
```

### §6.4 C4 Checkout 驗收
- 三維度全綠（U1-U7：U2 限流/U3 等價/U4 保序 由 C3 測試自證；效能 wall-clock 下降屬 baron E2E 觀測）。
- baton 一次性歸檔；`ls baton/` 僅餘 `README.md`（及其他 parked plan）。

---

## §7 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `Translator.translate` / `Translator` 提示詞拼接與翻譯 API — 不改（並行只改呼叫方式）
- [ ] `LLMClient.chat` / `chat_stream_by_sentence` / `_api_semaphore` 限流機制 — 不改（沿用）
- [ ] HEADING-HOTFIX-1 標題層級遞迴深度（`level=min(2+depth,6)`）邏輯 — 值不變（僅搬至 collect slot）
- [ ] PARA-HOTFIX-1 `_normalize_paragraph_breaks` 段落正規化邏輯 — 不改（僅於 assemble 套用）
- [ ] META-HOTFIX-1 `_render_meta_header` 文件 header — 不動
- [ ] `run_phase3` 輸出內容/順序/層級/段落/header 與 `BilingualMarkdownSpec` 合約 — 必須等價不變
- [ ] heading 退化 fallback（`_translate_whole`）與 `source_lang='zh*'` 不重譯 — 維持單呼叫、不並行
- [ ] A 軌 `translate_processor` / 其餘四路 / 母提示詞 / DB Schema / 凍結合約 — 不改
- [ ] 主 repo 目錄 — 嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C1 — Collect/Assemble 重構（收集-組裝解耦、仍序列、行為等價）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（新增 `_collect_render_slots`、重構 `_restore_sections_markdown`/`_restore_one_section`）+ `.bak` 備份 `archive/2026-06-06_RESUME-PERF-1_C1_resume_pipeline.py.bak` |
| **安全性** | 🟢 高 — 純結構重構、仍序列、輸出 byte 等價（既有測試保證）|
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；`# === [RESUME-PERF-1 C1 START/END] ===` 包裹便於定位 |
| **驗收 grep 條件** | §6.1（包裹 + `_collect_render_slots` + 仍序列 `_t` + 既有 resume 測試全綠）|
| **依賴關係** | 無前置（首 commit）|
| **具體實作細節** | 1. 先備份 `.bak`（git add）。2. 新增 `@staticmethod`/instance helper `_collect_render_slots(sections, depth, out)`：遞迴鏡像現行走訪順序，append slot dict——title→`{"kind":"title","text":title,"level":min(2+depth,6)}`〔沿用 HEADING 邏輯〕、text item→`{"kind":"content","text":content}`、非 text 有 content→`{"kind":"raw","text":content}`、字串 fallback→`{"kind":"content","text":txt}`、children 遞迴 `depth+1`。3. 重構 `_restore_sections_markdown`：`slots=[]; _collect_render_slots(sections,0,slots)`；**逐 slot 序列**處理——`title`/`content` 經 `_t(text, inj, tr, "title"/"content")` 取譯文〔`translate=False` 時用原文〕；組裝：`title`→`f"{'#'*level} {zh}"`、`content`→`self._normalize_paragraph_breaks(zh)`〔沿用 PARA〕、`raw`→原文；`"\n\n".join(非空).strip()+"\n"`。4. `_restore_one_section` 若不再被引用可保留為 thin wrapper 或移除〔擇一、不影響輸出〕；`_t`/`_translate_whole`/退化偵測不動。5. `# === [RESUME-PERF-1 C1 START/END] ===` 包裹改動。6. 產 `baton/..._C1_執行.md`。**驗證**：既有 `tests/test_resume_pipeline.py` 全綠＝輸出 byte 等價。|

### C2 — ThreadPool 並行翻譯（序列→受限並行）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（`_restore_sections_markdown` 序列翻譯 → ThreadPool 並行 + 異常隔離）+ `.bak` |
| **安全性** | 🟡 中 — 改執行模型為並行；保序靠 slot index、限流靠既有 semaphore；行為等價但需 C3 強驗保序 |
| **可逆性** | 🟢 高 — `git revert C2`（回 C1 序列版）；包裹便於定位 |
| **驗收 grep 條件** | §6.2（ThreadPoolExecutor / LLM_MAX_CONCURRENT / 異常隔離 warning / SOP / 既有測試全綠）|
| **依賴關係** | 前置 C1（收集-組裝已解耦）|
| **具體實作細節** | 1. 先備份 `.bak`。2. 檔頭 import（`# === [RESUME-PERF-1 C2 START] ===` 包裹）：`from concurrent.futures import ThreadPoolExecutor`、`from settings import LLM_MAX_CONCURRENT`。3. `_restore_sections_markdown` 的「逐 slot 序列翻譯」段改並行：收集需翻的 slot index 清單；`with ThreadPoolExecutor(max_workers=max(1, LLM_MAX_CONCURRENT)) as ex:` 對每個 title/content slot `submit(self._t, text, inj, tr, text_type)`；以 `{index: future}` 保存；逐 index 取 `future.result()` 回填譯文。4. **異常隔離**：取 result 包 `try/except Exception as e:` → 該 slot 譯文退回**原文** `slot["text"]` + `self.logger.warning("[RESUME-PERF-1] 單元翻譯失敗、退回原文", extra={'extra_fields':{'event':'resume_translate_unit_fallback','reason':str(e)[:200]}})`〔logger.warning、非 error、符 SOP〕。5. 組裝段（title 前綴/PARA 正規化/raw）**完全不動**、仍按 slot 原序。6. 退化 fallback（`_translate_whole`）與 zh* 路徑不並行、不動。7. `# === [RESUME-PERF-1 C2 START/END] ===` 包裹。8. 產 `baton/..._C2_執行.md`（**必貼 §5 SOP grep**）。**驗證**：既有 resume 測試仍全綠（行為等價）。|

### C3 — Unit Tests（單元測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_resume_pipeline.py`（追加 4 並行專屬測試）|
| **安全性** | 🟢 高 — 純測試、mock 隔離不打真 API |
| **可逆性** | 🟢 高 — `git revert C3` 完全回滾 |
| **驗收 grep 條件** | §6.3（4 新測試命中 + 檔級全綠 + 全套件不退化）|
| **依賴關係** | 前置 C1 + C2 |
| **具體實作細節** | 1. 追加 4 測試（mock Translator 回確定化 `f"ZH::{text}"`、不打真 API）：① `test_p3_parallel_order_byte_equal`——多層多 section 結構〔含 title/text/raw/children〕→ `run_phase3` 輸出與「預期序列組裝」**逐字相同**〔保序 + 層級 ##/###/#### + PARA 空行〕；② `test_p3_parallel_concurrency_capped`——以 lock 計數 fake translate 同時進入峰值、斷言 ≤ `LLM_MAX_CONCURRENT`〔patch `resume_pipeline.LLM_MAX_CONCURRENT` 小值如 2 加 sleep 製造重疊〕；③ `test_p3_parallel_unit_error_isolated`——令某 text 翻譯拋例外 → 該段退回原文、其餘正常、`BilingualMarkdownSpec` 仍交付；④ `test_p3_parallel_degraded_single_call`——heading 退化 → `_translate_whole` 單呼叫、未走並行〔calls==1〕。2. `# === [RESUME-PERF-1 C3 START/END] ===` 包裹。3. 產 `baton/..._C3_執行.md`。|

### C4 — Checkout（收官驗收與一次性歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` 結案 + `prompts/INDEX.md` + baton 一次性 `mv` 歸檔（plan_v1→`plans/` + tasks→`tasks/` + C1-C4 報告→`executions/`）+ `git add`；無業務代碼 |
| **安全性** | 🟢 高 — 純驗收 + 文件搬移 |
| **可逆性** | 🟢 高 — 文件層級、git 可回滾 |
| **驗收 grep 條件** | §6.4（三維度全綠 + baton 僅餘 README/其他 parked）|
| **依賴關係** | 前置 C1 + C2 + C3 全 ship |
| **具體實作細節** | 1. **維度一目標規格**（plan §2 U1-U7）：U1 並行化〔grep ThreadPoolExecutor〕/ U2 限流統一〔LLM_MAX_CONCURRENT〕/ U3 行為等價〔C3 byte 等拍 + 既有測試〕/ U4 保序〔C3〕/ U5 異常隔離〔C3〕/ U6 退化不變〔C3〕/ U7 範圍限 resume〔grep 僅 resume_pipeline〕→ 逐項判定〔效能 wall-clock 屬 baron E2E〕。2. **維度二測試**：貼 C1-C3 grep + `pytest tests/ -q` 真實輸出。3. **維度三不可動清單**：`git show --stat` 證 C1-C3 僅動 `resume_pipeline.py` + `test_resume_pipeline.py`、Translator/LLMClient/合約/A軌/其餘四路零命中。4. **SOP 核查**：貼 logging（無 logger.error 缺 exc_info）+ database（無裸 commit）grep。5. **提示詞稽核**：`ls prompts | grep RESUME-PERF-1` ≥ Tasks + C1-C3 run + Check。6. **msg 完整性**：C1-C4 報告 §8.2 均含 msg 草稿。7. **baton 一次性歸檔**：`mv` plan_v1 → `plans/`、tasks → `tasks/`、C1-C4 `_執行.md` → `executions/` + `git add`。8. **TODO 結案**：RESUME-PERF-1 從 active 移除 → ✅ 完成表（C1-C4 + hash 待回填）+ 同步索引。9. 產 `baton/..._C4_執行.md`。|

---

## §9 Open Questions

無。（plan v2 §7 Q1-Q7 已於階段 3 由 baron 全數核准結案；時機由「Flip 前」改「即時可做」屬 baron 拍板、非規格變動。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RESUME-PERF-1 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 RESUME-PERF-1 executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改不可動清單（§7）；嚴禁跨 Commit 混合；嚴禁自動 git commit/push；行為等價、只改翻譯執行方式；BE-Refactor 落地前強制 SOP 核查 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡與 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-06)：初版拆分——依 plan v2（§7 OQ Q1-Q7 核准）拆 4 commit：C1 Collect/Assemble 重構（收集-組裝解耦、仍序列、輸出 byte 等價、既有測試保證）/ C2 ThreadPool 並行翻譯（`max_workers=LLM_MAX_CONCURRENT`、slot index 保序、受既有 `_api_semaphore` 限流、單 unit 失敗退原文+warning）/ C3 Unit Tests（保序 byte 等拍 / 併發峰值 ≤ 上限 / 異常隔離 / 退化單呼叫）/ C4 Checkout（三維度驗收 + baton 一次性歸檔）。baron 拍板「不必等五路、現在做」（plan Q5「Flip 前」屬優先序、非依賴）。
