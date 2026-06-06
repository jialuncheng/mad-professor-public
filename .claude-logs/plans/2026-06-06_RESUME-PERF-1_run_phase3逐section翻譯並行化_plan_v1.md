# RESUME-PERF-1 run_phase3 逐 section 翻譯並行化 plan

> 定義 B 軌 `ResumePipeline.run_phase3` 將「逐 heading section 序列翻譯」改為「受限並行翻譯」的效能優化目標規格：在不改變輸出內容/順序/層級/段落結構的前提下，把整份履歷翻譯的 wall-clock 由序列（實測 A 軌等價結構 ~330s）壓到受 `LLMClient._api_semaphore` 併發上限約束的並行時間。純規格、不含實作細節與 commit 拆分。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：B 軌 `run_phase3` 逐 heading section 翻譯為**完全序列**——`_restore_one_section` 對每個標題與每個正文 text item 同步呼叫 `_t`（→ `Translator.translate` → 阻塞式 LLM streaming），並遞迴序列走訪 children。整份履歷 ~40 個翻譯單元串行，A 軌等價結構實測 translate 階段達 **331.85s（佔單份總時長 77%）**，B 軌 resume 上線後將繼承同等瓶頸。
- **解法**：在 `run_phase3` 的還原路徑改為**兩段式受限並行**——① 序列「收集」階段走訪 section 樹、建立**有序的翻譯單元清單**（標題/正文/passthrough）；② 並行「翻譯」階段以執行緒池提交所有翻譯單元、由**既有 `LLMClient._api_semaphore`（`LLM_MAX_CONCURRENT`）統一限流**；③ 序列「組裝」階段依原始順序重建 Markdown（沿用 HEADING-HOTFIX 層級推算 / PARA-HOTFIX 段落正規化 / META-HOTFIX header）。
- **影響**：僅改 `pipelines/resume_pipeline.py` 的 `_restore_*` 翻譯**執行方式**（序列→受限並行）；**不改輸出內容/順序/層級/段落/header**、不改 `Translator` / `LLMClient` / 凍結合約 / DB Schema。無新增獨立併發鎖（沿用 LLM semaphore）。**行為等價、僅 wall-clock 下降**。

---

## §2 目標規格

本次改動必須達到的「最終狀態」（可量化、可檢驗）：

- **U1 翻譯並行化**：`run_phase3` 的逐 section 翻譯由序列改為並行；整份履歷翻譯 wall-clock 顯著下降，理論下界 ≈ `max(最慢單一翻譯單元, 總翻譯時間 / 有效併發數)`。
- **U2 限流統一**：並行翻譯的實際 API 併發**完全受既有 `LLMClient._api_semaphore`（`LLM_MAX_CONCURRENT`）約束**；不新增獨立併發鎖、不繞過 semaphore、不超賣 LLM 配額。
- **U3 行為等價（邏輯）**：輸出的翻譯單元集合、文件順序、標題層級（HEADING-HOTFIX）、段落空行（PARA-HOTFIX）、文件 header（META-HOTFIX）、`BilingualMarkdownSpec` 欄位與序列版**完全等價**；唯一差異為翻譯 API 的執行先後順序（不影響組裝結果）。
- **U4 保序**：並行翻譯結果依**原始文件順序**重組；嚴禁因並行導致章節/正文錯位。
- **U5 異常隔離**：單一翻譯單元失敗不污染其他單元、不中斷整份交付；有明確降級策略（§7 Q3）。
- **U6 退化路徑不變**：heading 退化 fallback（`_translate_whole` 整檔單呼叫）與 `source_lang='zh*'` 原文不重譯路徑維持**單呼叫/不並行**、行為不變。
- **U7 範圍邊界**：本任務僅優化 **resume 軌 `run_phase3`**；其餘四路（visual/academic/book/litedoc）各自 P3 的並行化屬另一任務（通用化另議）。

---

## §3 現況與證據

- **`pipelines/resume_pipeline.py`**：
  - `_restore_sections_markdown L549-560`：序列 `for sec in sections: _restore_one_section(...)`，組成單一字串。
  - `_restore_one_section L562-605`：對 `title`（L578）與每個 `content` text item（L587 / 純字串 fallback L599）**同步呼叫 `_t`**；`for child in sec.get("children")`（L603）**遞迴序列**。全程無 `await` / `asyncio` / `gather` / `ThreadPool`。
  - `_t L617 附近`：`return tr.translate(t, inj, TranslateMode.NORMAL, text_type)`——阻塞式單元翻譯。
- **`llm/client.py`**：
  - `LLMClient._api_semaphore = threading.Semaphore(LLM_MAX_CONCURRENT)`（L49，class-level、預設 6）；`chat` / `chat_stream_by_sentence` 每次 API 呼叫 `with LLMClient._api_semaphore:`（L95 / L148）→ **併發限流基建現成、thread-safe**。
- **`processor/translator.py`**：
  - `Translator.translate L161+`：`system_prompt` / `user_prompt` 為 method locals（L177-178）、`llm` 取共享單例（L176）；`__init__` 後 `self.llm` / `self.logger` 唯讀 → **無 per-call 可變狀態、可安全跨執行緒呼叫**。

### §3.1 grep 鋼鐵證據

```bash
# B 軌逐 section 翻譯為序列（無並行原語）
$ grep -n 'self._t(\|for child in\|await\|asyncio\|gather\|ThreadPool' pipelines/resume_pipeline.py
578:            zh_title = self._t(title, inj, tr, "title") if translate else title
587:                    rendered = self._t(content, inj, tr, "content") if translate else content
599:                    rendered = self._t(txt, inj, tr, "content") if translate else txt
603:        for child in sec.get("children", []) or []:
#（await / asyncio / gather / ThreadPool → 零命中）

# LLM 併發鎖基建現成（class-level Semaphore + 每次 chat 套用）
$ grep -n '_api_semaphore\|LLM_MAX_CONCURRENT' llm/client.py
49:    _api_semaphore = threading.Semaphore(LLM_MAX_CONCURRENT)
95:        with LLMClient._api_semaphore:
148:        with LLMClient._api_semaphore:

$ grep -n 'LLM_MAX_CONCURRENT' settings.py
87:LLM_MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "6"))

# Translator 無 per-call 可變狀態（translate 用 locals、可跨執行緒）
$ grep -n 'def translate\|system_prompt =\|user_prompt =\|llm = self.llm' processor/translator.py
161:    def translate(
176:        llm = self.llm if self.llm is not None else LLMClient.get_instance()
177:        system_prompt = self._build_system_prompt(ctx, text_type)
178:        user_prompt = self._build_user_prompt(text, ctx, text_type)
```

> **效能量化依據**：A 軌 golden capture（doc_type=resume、同一份 fixture）translate 階段實測 **331.85s / 總 429.00s（77%）**，~40 個序列 `streamGenerateContent`；B 軌 `_restore_*` 為同等序列結構 → 上線後同量級瓶頸。`LLM_MAX_CONCURRENT=6` 下，理論並行下界 ≈ max(最慢單元 ~30s, 331/6 ≈ 55s) → 預估 ~5x 改善（屬目標、非保證、待實測）。

---

## §4 不可動清單

明確劃定修改邊界，防止 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `Translator.translate` / `Translator` 提示詞拼接與翻譯 API — 不改（並行只改「呼叫方式」、不改翻譯本身）。
- [ ] `LLMClient.chat` / `chat_stream_by_sentence` / `_api_semaphore` 限流機制 — 不改（沿用既有 semaphore 限流）。
- [ ] HEADING-HOTFIX-1 標題層級遞迴深度推算（`level=min(2+depth,6)`）— 不改邏輯。
- [ ] PARA-HOTFIX-1 `_normalize_paragraph_breaks` 段落正規化 — 不改邏輯。
- [ ] META-HOTFIX-1 `_render_meta_header` 文件 header 組裝 — 不改邏輯。
- [ ] `run_phase3` 的**輸出內容/順序/層級/段落/header** 與 `BilingualMarkdownSpec` 合約 — 必須等價不變。
- [ ] heading 退化 fallback（`_translate_whole`）與 `source_lang='zh*'` 不重譯路徑 — 維持單呼叫、不並行。
- [ ] A 軌 `translate_processor` / 其餘四路 / 母提示詞 / DB Schema / 凍結合約 — 不改。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流 / 六階段 / SOP 核查 | `ref/WORKFLOW_SOP.md §1 / §3 / §5` |
| 進度框架（雙軌制 / 防 Regression 黃金三角 / 不過早優化心法） | `ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 / §8` |
| LLM 連線彈性與併發限流（Semaphore + retry_call） | `llm/client.py L49 / L95` + `MODEL-9 連線彈性防禦`（已落地）|
| B 軌履歷 P3 逐 section 翻譯還原 | `plans/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_plan_v1.md` + HEADING/PARA/META hotfix（hotfixes/）|
| 效能瓶頸量化來源 | A 軌 golden capture log（translate 331.85s / 429.00s、2026-06-06）|

---

## §6 驗證計畫

### §6.1 自動化單元測試

- 既有：`venv/bin/python -m pytest tests/ -q`（防 Regression、特別是 `tests/test_resume_pipeline.py` 既有 P3 測試全綠）。
- 新增：
  - **保序**：mock `Translator.translate` 回「可辨識且確定化」的譯文（如 `f"ZH::{text}"`），驗證並行版輸出與序列版**逐字相同**（順序/層級/段落/header 一致）。
  - **限流**：以可探測的 fake LLM 記錄「同時進入翻譯的執行緒峰值」≤ `LLM_MAX_CONCURRENT`（驗證受 semaphore 約束、未超賣）。
  - **異常隔離**：令某一翻譯單元拋例外，驗證其餘單元仍完成、整份仍交付 `BilingualMarkdownSpec`、降級策略生效（§7 Q3）。
  - **退化路徑**：heading 退化 → `_translate_whole` 仍單呼叫、不並行。
  - **等價對拍**：同一 mock 確定化譯文下，序列版 vs 並行版輸出字串完全相同（structural + byte 等價）。

### §6.2 手動端到端（E2E）驗證流程

1. 影子上傳一份履歷（resume），觀察 `run_phase3` 翻譯 wall-clock（performance_metric / 計時 log）較序列版顯著下降。
2. 開 B 軌 `final_zh`：標題層級（##/###/####）、段落空行、文件開頭 meta header、章節順序**與優化前肉眼一致**。
3. 觀察 LLM 併發 log（429 命中率）未因並行而惡化；如撞 429，由既有 `retry_call` 吸收、最終仍完整交付。

---

## §7 Open Questions

> **✅ baron 拍板核准（2026-06-06）**：Q1-Q7 全數採推薦方案、無異動。**全數結案 → 本 plan 可進階段 2 拆 tasks（時機＝B 軌 resume 正式 Flip 上線前）。**
> - **Q1**：✅ `ThreadPoolExecutor`——避免 async viral effect 全域改動、與現行 `threading.Semaphore` 完美契合。
> - **Q2**：✅ 綁定 `LLM_MAX_CONCURRENT`（直接用 `settings.LLM_MAX_CONCURRENT`）——最大化配額利用、避免多餘執行緒空等的上下文切換開銷。
> - **Q3**：✅ 退回原文 + `logger.warning`（保交付）——局部 block 失敗仍完成其餘重組、確保 `BilingualMarkdownSpec` 成功交付。
> - **Q4**：✅ Mock 確定化譯文做 byte 等拍 + 真跑只驗 Markdown 結構——強驗並行/序列組裝順序/層級/段落 100% 吻合。
> - **Q5**：✅ B 軌 resume 正式 Flip 上線前實施、A 軌完全不動（Strangler 被替換階段、不耗精力優化）。
> - **Q6**：✅ 否、限 `resume` 策略內——其餘四路 P3 結構不同（如 Book 採 ParallelChapter 級聯）；穩定後再提取為共用並行元件。
> - **Q7**：✅ 不需 deterministic、沿用現行 `temperature`——非確定性早被 Golden D2（0.95）吸收、不為並行犧牲翻譯流暢度。

| 開放問題 | 推薦方案（✅ 已核准） | 推薦理由 |
|---|---|---|
| Q1 並行機制：ThreadPool vs asyncio？ | ✅ **`concurrent.futures.ThreadPoolExecutor`** | 現行 `run_phase3` / Orchestrator 為同步阻塞模型；ThreadPool 避免 async viral effect 全域改動；與 thread-safe 的 `threading.Semaphore` 完美契合；GIL 對 I/O-bound 無礙。 |
| Q2 執行緒池大小 `max_workers`？ | ✅ **綁定 `LLM_MAX_CONCURRENT`**（直接用 `settings.LLM_MAX_CONCURRENT`） | 實際並行瓶頸受 `LLMClient._api_semaphore`（預設 6）限；池 = 6 最大化配額、避免多餘執行緒空等的上下文切換開銷。 |
| Q3 單一翻譯單元失敗策略？ | ✅ **退回原文 + `logger.warning`（保交付）** | 局部 block（429/逾時）失敗時保留原文並完成其餘重組，遠優於整份失敗；warning 便追蹤、確保 `BilingualMarkdownSpec` 仍交付。 |
| Q4 等價性如何驗證（LLM 非確定性）？ | ✅ **mock 確定化譯文 byte 等拍** + 真跑只驗 Markdown 結構 | mock `Translator.translate` 為 `f"ZH::{text}"` 強驗並行/序列組裝順序/層級/段落 100% byte 吻合；真 LLM run-to-run 非確定、只驗結構。 |
| Q5 實施時機？ | ✅ **B 軌 resume 正式 Flip 上線前**；A 軌完全不動 | A 軌已進入 Strangler 被替換階段、不耗精力優化；B 軌影子期優化、正式接管流量前驗效能、上線無痛。 |
| Q6 是否同步套用其餘四路？ | ✅ **否（本 plan 限 resume run_phase3）** | 其餘四路 P3 還原策略複雜度不同（如 Book 採 ParallelChapter 級聯）；先在 resume 內封裝、穩定後再提取為共用並行元件。 |
| Q7 是否需保證翻譯結果 deterministic？ | ✅ **不需**（沿用現行 `temperature`） | 非確定性早被 Golden D2（0.95）吸收；不為並行強制限制 LLM 隨機性而降低翻譯流暢度。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RESUME-PERF-1（run_phase3 逐 section 翻譯並行化）的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 RESUME-PERF-1 tasks / 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段）；行為等價、只改翻譯執行方式不改輸出；不改 Translator/LLMClient/HEADING/PARA/META/合約 |
| **改版觸發條件** | §1–§7 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義並行化技術規格；LLM 限流唯一源在 `llm/client.py`；翻譯邏輯唯一源在 `Translator`；工作目錄/流程一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-06)：**baron 拍板核准 §7 Open Questions Q1-Q7（階段 3 驗證）**——Q1 ThreadPoolExecutor〔避 async viral effect〕/ Q2 綁定 LLM_MAX_CONCURRENT〔避空等上下文切換〕/ Q3 退原文+warning 保交付 / Q4 mock 確定化譯文 byte 等拍+真跑驗結構 / Q5 B 軌 resume Flip 上線前實施 A 軌不動 / Q6 限 resume〔Book ParallelChapter 級聯結構不同、穩定後再抽共用〕/ Q7 不需 deterministic〔Golden D2 0.95 吸收〕。全數採推薦方案、無異動 → 結案，可進階段 2 拆 tasks（時機：resume 正式 Flip 前）。
- v1 (2026-06-06)：初版建立——B 軌 `run_phase3` 逐 section 序列翻譯（A 軌等價結構實測 331.85s/77%）改受限並行（兩段式：序列收集→ThreadPool 並行翻譯〔受既有 LLMClient._api_semaphore/LLM_MAX_CONCURRENT 限流〕→保序組裝）；目標 U1-U7（並行化/限流統一/行為等價/保序/異常隔離/退化路徑不變/範圍限 resume）；現況 grep 證 `_restore_one_section` 序列 `_t`、LLM semaphore 基建現成、Translator thread-safe；OQ Q1-Q7（ThreadPool/池大小綁 LLM_MAX_CONCURRENT/失敗退原文/mock 確定化對拍/上線前實施/限 resume/不需 deterministic）；不含 commit 建議。
