# GLOSSARY-CORE 中央領域術語庫與跨語系一致性 plan

> 本計畫設計並建立「中央領域術語資料庫（Global Glossary DB）」：以 SQLite 為基礎的中央術語存儲，配合動態級聯優先權查詢、與並行書籍翻譯管線的雙層字典融合、增量自動回填（Backfill）自癒學習，以及前台對話（Chat）的術語強約束注入，解決文檔翻譯與問答在跨語系、跨時間、跨文獻時的語意一致性問題。領域標準化代碼（LCC）由上游 DOMAIN-NORM 計畫提供，本計畫純消費其產物。本計畫為純規格定義。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：Mad Professor 的文獻閱讀版圖極其廣泛（橫跨海德格哲學、環義自行車賽、雷思玲白酒釀造、Tuscany 橄欖油等）。現有翻譯管道缺乏跨文獻術語的一致性防線，且 LLM 在 Dynamic Thinking 過程中容易因「無狀態思考」而產生語意與譯名漂移；同一專有名詞在不同文獻、不同時間、前台問答與譯本之間譯法不一。
- **解法**：建立一個「多語系、自動增量學習」的中央術語存儲與一致性注入體系：
  1.  **中央資料庫（Global Glossary DB）**：在 SQLite 建立 `GlobalGlossary` 表，以 `(source_lang, target_lang, term_key, domain)` 為聯合唯一索引，物理鎖死同語系同領域單詞唯一譯法。
  2.  **級聯優先權查詢與融合（Cascading & Fusion）**：翻譯/問答時動態查詢「文獻專屬 LCC + 通用 general」並以優先權覆寫去重；與 `TRANSLATE-BOOK` 並行管線無縫融合，新書術語自動回填學習；並將術語注入問答大腦 System Prompt，實現全鏈路一致性。
  3.  **熱插拔自癒 CLI**：提供獨立 `tools/manage_glossary.py` 離線閉環測試與一鍵歷史回填。
- **上游依賴（硬前置）**：本計畫所有 `domain` 欄位的標準化 LCC 代碼，均來自 **DOMAIN-NORM 計畫**的 `normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode` 單一入口（對齊 PIPE plan §2 U8 三大共用真理源）。本計畫不自行定義領域白名單與收斂邏輯，純消費其凍結產物。
- **影響**：新增 `models.py` 的 `GlobalGlossary` 表、新增處理模組 `processor/glossary_extractor.py`、新增獨立測試腳本 `tools/manage_glossary.py`，並在 `translate_processor.py`、`pipeline_core.py` 進行熱插拔開關判斷接入。既有資料庫數據與 API 路由保持 100% 穩定，零 Regression 風險。

---

## §2 目標規格

### U1. 中央術語資料庫與 ISO 多語系支援（Global Glossary DB Schema）
*   **規格**：
    *   系統必須在 SQLite 建立 `GlobalGlossary` 表，欄位包含：`source_lang`（如 `en`, `de`, `ja`）、`target_lang`（如 `zh-tw`）、`term_key`（強制小寫與 strip 去空白）、`original_term`（保留大小寫）、`translation`（繁中譯詞）、`domain`（標準化 LCC/自定義代碼，由 DOMAIN-NORM 提供）、`source`（來源，分 `auto_extract` 與 `manual_edit`）。
    *   建立 `(source_lang, target_lang, term_key, domain)` 的**聯合唯一約束索引**，從物理層面鎖死同語系、同領域下同一單詞的唯一譯法。

### U2. 級聯優先權查詢與去重（Cascading Priority Retrieval）
*   **規格**：
    *   文獻翻譯或 Chat 問答拉取術語時，系統必須支援**「級聯優先權查詢」**：
        `SELECT * FROM global_glossaries WHERE domain IN ('[文獻標準 LCC]', 'general')`。
    *   在 Python 記憶體中，文獻專屬領域術語（如 `BF`）優先權必須大於通用領域（`general`）；同詞衝突時專屬領域譯法必須自動「覆寫」通用譯法。

### U3. 與 `TRANSLATE-BOOK` 並行書籍翻譯管線的完美融合（Book Translation Integration）
*   **規格**：
    *   `TRANSLATE-BOOK` 第二階段（`GlobalTranslator`）提取的領域代碼必須對齊 DOMAIN-NORM 的標準 LCC。
    *   第三階段（`ParallelChapterTranslator`）並行 Worker 啟動前，系統必須在記憶體進行**雙層字典融合**：將本書實時提取術語（`book_glossary`）與中央資料庫歷史累積術語（`sqlite_glossary`）合併，本地歷史真理術語擁有最高優先權。
    *   書籍翻譯完成時必須啟動背景增量回填（Backfill），將本書新術語**自動寫回** SQLite，實現知識飛輪。

### U4. Chat 前台問答大腦的術語強約束注入（Chat Integration）
*   **規格**：
    *   用戶開啟某篇文獻對話時，後端必須讀取該文獻 `paper.domain`（標準 LCC，如 `"B"`）。
    *   從 `GlobalGlossary` 拉取對應術語表，作為**「不可違背的 System constraint 契約」**注入對話大腦。
    *   確保問答時 AI 使用的中文專有名詞與論文譯本 100% 絕對一致。

### U5. 獨立、熱插拔與自癒補丁 CLI（Hot-Pluggable CLI）
*   **規格**：
    *   術語對齊的全系統開關沿用 DOMAIN-NORM 的 `LLM_USE_GLOSSARY_ALIGN` 環境變數（預設 `False` 時行為 100% 維持舊狀，零風險），本計畫不重複定義。
    *   必須提供獨立測試腳本 `tools/manage_glossary.py`，具備以下子命令：
        *   `--init`：建立空表。
        *   `--test-pipeline --pdf [path]`：完整跑「真實領域偵測 ──► 標準化對齊（呼叫 DOMAIN-NORM）──► 快取比對 ──► 增量提取 ──► 寫入回填 ──► 輸出 `{stem}_glossary.json`」的離線閉環測試。
        *   `--backfill-existing-papers`：一鍵掃描更新歷史舊文獻，將其 `domain` 欄位透過 DOMAIN-NORM 全自動標準化升級為 LCC 代碼。

---

## §3 現況與證據

詳細盤點與本功能相關的現有程式碼邏輯與關鍵調用鏈（必須指出確切的檔案與行數，並附帶 `grep` 核查證據）：

- **`models.py`**：
  - `Paper L87-157`：包含 `domain: Mapped[Optional[str]]`（L104）與 `metadata_json: Mapped[Optional[str]]`（L134），已為文獻領域預留位置；標準化後的 LCC 即寫入此 `domain` 欄位。
- **`processor/translate_processor.py`**：
  - `translate_text L205-271`：單次 LLM 翻譯呼叫。L237-239 將 `domain` 拼入 system_prompt 尾端，為術語表注入的快速通道入口。
- **`AI_professor_chat.py`**：
  - Chat 問答大腦組裝 System Prompt 之處，為 U4 術語強約束注入點。
- **`settings.py`**：
  - `LLM_USE_GLOSSARY_ALIGN` 開關由 DOMAIN-NORM 計畫建立，本計畫複用。

### §3.1 grep 鋼鐵證據

```bash
# 1. 驗證 Paper ORM 表 domain 欄位（術語級聯查詢主鍵來源）
grep -n "domain:" models.py
# 輸出：104:    domain: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

# 2. 現有 translate 提示詞中 domain 注入方式（術語表注入入口）
grep -n "domain" processor/translate_processor.py
# 輸出：
# 41:            self.domain = domain  # 主題領域（空字串時不影響任何輸出）
# 237:        domain = getattr(self, 'domain', '')
# 238:        if domain:
# 239:            system_prompt = system_prompt + f"\n\n本文件主題領域：{domain}，請以該領域標準術語翻譯。"
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `Paper` 表除 `domain` 欄位複用之外，其他主欄位與既有關係屬性嚴禁任何改動，防範資料庫不相容（僅可新增 `GlobalGlossary` 表）。
- [ ] DOMAIN-NORM 計畫的 `normalize_to_lcc` 入口與 `DomainMapping` 表結構嚴禁在本計畫內改動，僅可呼叫消費。
- [ ] 既有問答與 RAG 核心檢索邏輯 `rag_retriever.py` 嚴禁任何改動。
- [ ] `tiling_processor.py` 中的 `tiling_method` 及 Bypass 判斷邏輯嚴禁改動。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 專案進度治理框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| plan 結構契約與治理規格 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／SOP 核查 | `.claude-logs/ref/WORKFLOW_SOP.md §3 §5 §6` |
| 領域標準化對齊器（上游硬前置，提供 `LCCCode`） | `.claude-logs/plans/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md` |
| PipelineCore 大改版（三大共用真理源 U8、本庫為其一） | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md §2 U8` |
| 書籍並行翻譯規劃 | `.claude-logs/baton/2026-06-01_TRANSLATE-BOOK_書籍並行翻譯與雙語故事板引導_plan_v4.md` |
| ORM 數據結構規格 | `models.py L87-157` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**：
  在 `tests/` 下建立專屬測試檔 `tests/test_glossary_core.py`：
  *   `test_global_glossary_unique_constraint`：驗證 SQLite 唯一性索引約束，確保同一語言、同一領域下同一單詞無法寫入不同中文譯法。
  *   `test_cascading_priority_match`：驗證級聯優先權查詢與去重，當 `BF` 存在專屬譯法而 `general` 存在通用譯法時，查詢 `BF` 必須自動返回 `BF` 專屬譯文。
  *   `test_book_glossary_fusion_priority`：驗證書籍翻譯雙層融合時，中央資料庫歷史真理術語優先權高於本書實時提取術語。
  *   `test_chat_glossary_injection`：驗證 Chat 開啟文獻時，對應 `domain` 術語表被注入 System Prompt 契約。
  *   `test_glossary_cli_backfill_existing`：驗證 `tools/manage_glossary.py --backfill-existing-papers` 自癒指令，確保所有舊文獻 domain 欄位一鍵批量升級正確。

### §6.2 手動端到端（E2E）驗證流程

1.  **步驟一**：準備一本德文白酒釀造 PDF（`doc_type='book'`），確保 `LLM_USE_GLOSSARY_ALIGN=True`、DOMAIN-NORM 已先行落地。
2.  **步驟二**：啟動 Pipeline 翻譯。觀察日誌確認：DOMAIN-NORM 將 raw 領域對齊為 `"wine"` 後，`GlobalTranslator` 提取的術語自動回填寫入 SQLite。
3.  **步驟三**：上傳第二本德文白酒 PDF，確認相同專有名詞（如 `Riesling`）直接從 SQLite 命中並注入 Prompt，無需 LLM 重複思考。
4.  **步驟四**：打開前台對話界面與該論文問答，確認 AI 教授回答使用的專有名詞與譯本 100% 完全一致。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **手動校正字典（Human-in-the-loop）的實作** | **提供 CLI 修改，未來前台做 UI 抽屜** | Phase 1-3 階段允許用戶在 CLI 或直接 SQLite 編輯 `GlobalGlossary` 作手動修正（`source='manual_edit'`）；未來前端建「術語審核抽屜」讓用戶翻譯前手動確認，實現最高人機協同品質。 |
| **同義詞庫是否需要模糊匹配（Fuzzy Match）** | **強限制 exact match，利用 model 內部對齊** | 術語表 SQL 比對應強制完全精準（Lowercase Exact Match），模糊匹配大幅增加檢索複雜度與錯誤率；語意微調交給 model 內部消化即可。 |
| **DomainNormalizer 拆出後的落地順序綁定** | **GLOSSARY-CORE 以 DOMAIN-NORM 為硬前置，後落地** | `domain` LCC 主鍵唯一來源為 DOMAIN-NORM；級聯查詢與書籍融合皆依賴穩定 LCC。tasks 排程時 DOMAIN-NORM 必須先綠，本計畫方可整合驗證。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 GLOSSARY-CORE 中央領域術語庫與跨語系一致性的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 GLOSSARY-CORE tasks / 執行報告；PIPE plan §2 U8 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 領域標準化白名單與收斂邏輯唯一源在 DOMAIN-NORM plan，本計畫純消費；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-01)：拆分改版——將原 U1 混合領域標準化分類、U2 領域映射本地快取抽離為獨立的 DOMAIN-NORM 計畫；本計畫保留中央術語庫存儲（原 U3→U1）、級聯優先權查詢（原 U4→U2）、書籍翻譯融合（原 U5→U3）、Chat 注入（原 U6→U4）、自癒 CLI（原 U7→U5），並全面改為消費 DOMAIN-NORM 提供的 `LCCCode`、標明硬前置依賴。檔名由 `2026-05-28_GLOSSARY-CORE_中央領域術語庫與多語系自適應對齊_plan.md` 更名而來。（2026-06-03 同步修正：更新 `normalize_to_lcc` 上游依賴簽名為 v2 雙參數版；同步修正 §5 參考計畫至新版檔名以消除懸掛引用。）
- v1 (2026-05-28)：初版建立，融合 LCC 標準、自定義生活標籤、級聯優先權、增量自癒學習、開關熱插拔以及與並行書籍翻譯和 Chat 大腦的雙重融合規格。
