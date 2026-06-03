# DOMAIN-NORM 領域標準化對齊器 plan

> 本計畫定義「自適應領域標準化對齊器（DomainNormalizer）」：將 `DomainDetector` 或文檔核心內容產出的 raw 領域短句，動態收斂為標準的 LCC 1–3 字母代碼，並在資料庫中動態註冊新領域與寫入本地快取防重。其產物 `LCCCode` 為 GLOSSARY-CORE 術語庫與 Translator 雙模式翻譯共同的上游真理源。本計畫為規格定義。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：
  1. `DomainDetector.detect` 產出的是高自由度自然語言短句（如 `"哲學與存在主義"`），無法作為穩定的查詢主鍵。
  2. 傳統採用靜態白名單（寫死在代碼中）與 general 安全回退的設計，在開放式多人使用情境下無法擴展——系統無法為未知冷門領域（如 `"侏羅紀/古生物"`）自動對齊並建立獨立領域空間。
  3. 履歷等複合類型文檔，重點在於其文字展現的實質專業（如 "行銷"、"AI"），而非 "履歷" 這種類型。
- **解法**：
  1. **基於內容的 LCC 代碼判定（U1）**：讀取文檔關鍵字/核心文本，調用 LLM（cheap model, Temp=0.0）自動生成標準的 LCC 1–3 字母代碼與領域名稱。
  2. **動態領域註冊與快取（U2）**：SQLite 中建立 `Domains`（註冊領域代碼）與 `DomainMapping`（快取映射）表。判定領域時，若 LCC 代碼在資料庫中不存在，系統自動在 `Domains` 表中插入記錄進行「動態註冊」（此時無單字）；映射結果寫入快取防重。
  3. **單一入口與熱插拔開關（U3 + U4）**：暴露 `normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode`。新增 `LLM_USE_GLOSSARY_ALIGN` 預設為 `False` 的熱插拔開關。
- **影響**：修改 `models.py`（新增 `Domains` 表與 `DomainMapping` 表）、新增 `processor/domain_normalizer.py`、`settings.py` 新增環境變數；既有檢測器本體零改動。

---

## §2 目標規格

### U1. 實質內容領域判定與標準化（Taxonomy and Normalization）
*   **規格**：
    *   `DomainNormalizer` 必須基於文檔中提取的核心關鍵字、摘要或特徵文本（而非單純文檔類型名稱），利用 LLM 依美國國會圖書館分類法（LCC）自動分派一個標準的 1–3 字母 LCCCode 以及領域名稱。
    *   對於履歷（Resume）等複合類型文件，必須根據履歷內容的技能關鍵字，自動判定並分派其對應的科學/技術 LCC 代碼（如：「投放/社群」對齊至 `"HF" Commerce/Marketing`；「Python/LLM」對齊至 `"QA" Computer Science/AI`），嚴禁粗暴歸類為 `"resume"` 類型。

### U2. 領域動態註冊與本地快取自癒（Dynamic Registration and Cache）
*   **規格**：
    *   SQLite 中必須建立兩張表：
      1. `Domains`：記錄已註冊的所有領域真理源，含 `lcc_code` (PK) 與 `name`。
      2. `DomainMapping`：記錄 raw 領域短句與標準 `lcc_code` 的快取映射。
    *   **動態註冊機制**：當 AI 產出對齊的 `lcc_code` 後，系統必須先查詢資料庫 `Domains` 表：若該 `lcc_code` 不存在，則自動在 `Domains` 中插入該代碼與領域名稱（例如自動註冊並插入 `lcc_code='QE', name='Geology/Paleontology'`），完成新領域註冊。此階段**不塞入任何單字或術語**（符合「單字是後續 GLOSSARY-CORE 的工作」邊界）。
    *   **交易邊界約束 (Transaction Boundary)**：任何 LLM 外部呼叫必須完全在 SQLite `session.begin()` 交易區塊之外執行（遵守 database SOP 禁交易內外部 API 呼叫規則，防範 SQLite `database is locked`），待 LLM 取得標準代碼後才開啟極短交易進行 `Domains` 與 `DomainMapping` 表的寫入。
    *   **併發寫入防護 (Concurrency Safety)**：為防範多個併發請求同時寫入同一個新註冊領域（如 `'QE'`），向 `Domains` 表插入記錄時必須採用 `INSERT OR IGNORE` 或 upsert 機制，保證 lcc_code PK 寫入的冪等性與安全，避免觸發 `IntegrityError` 衝突。
    *   **快取防重機制**：對齊領域時必須優先檢索 `DomainMapping` 本地快取，命中則 **0ms 立即回傳**、零 API 呼叫。未命中才呼叫 LLM 進行對齊與動態註冊，並將映射結果寫入快取。

### U3. 單一入口契約（Single-Entry Source）
*   **規格**：
    *   對外只暴露單一入口：
      ```python
      DomainNormalizer.normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode
      ```
    *   此入口為 GLOSSARY-CORE 級聯查詢與自癒演算法的 `domain=LCC` 參數，以及 Translator 雙模式 `InjectionContext.lcc` 必填欄位的**唯一來源**。
    *   五路策略管線（Academic／Book／Slides／Resume／LiteDoc）共用本入口，差異僅在 `raw_domain` 來源與文字特徵。

### U4. 熱插拔開關（Feature Flag）
*   **規格**：
    *   新增環境變數 `LLM_USE_GLOSSARY_ALIGN` 控制標準化對齊與動態註冊的全系統開關，預設為 `False`。
    *   為 `False` 時，系統行為 100% 維持舊狀（沿用既有 raw domain 直接注入路徑），零風險；為 `True` 時全面啟用本對齊與動態註冊。

---

## §3 現況與證據

詳細盤點與本功能相關的現有程式碼邏輯與關鍵調用鏈：

- **`processor/domain_detector.py`**：
  - `detect L39-76`：主題領域偵測，回傳 10-30 字高自由度詳細短句，是 `DomainNormalizer` 標準化對齊的原始輸入源之一。
- **`processor/translate_processor.py`**：
  - `translate_text L205-271`：單次 LLM 翻譯呼叫；L237-239 目前將 `domain` 詳細短句直接拼入 system_prompt 尾端。
- **`models.py`**：
  - `Paper L87-157`：`domain: Mapped[Optional[str]]` 欄位已為文獻領域預留位置，標準化後寫回此欄位。
- **`settings.py`**：
  - 目前無 `LLM_USE_GLOSSARY_ALIGN` 環境變數。

### §3.1 grep 鋼鐵證據

```bash
# 1. DomainDetector.detect 回傳 raw 短句
grep -n "def detect" processor/domain_detector.py
# 輸出：39:    def detect(self, ...):

# 2. 現有 translate 提示詞中 domain 注入方式
grep -n "domain" processor/translate_processor.py
# 輸出：
# 41:            self.domain = domain  # 主題領域（空字串時不影響任何輸出）
# 237:        domain = getattr(self, 'domain', '')
# 238:        if domain:
# 239:            system_prompt = system_prompt + f"\n\n本文件主題領域：{domain}，請以該領域標準術語翻譯。"

# 3. Paper ORM 表 domain 欄位
grep -n "domain:" models.py
# 輸出：104:    domain: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `processor/domain_detector.py` 的 `detect` 既有多模態（Vision）與文字提取核心邏輯嚴禁改動。
- [ ] `models.py` `Paper` 表除 `domain` 欄位複用之外，其他主欄位與關係屬性嚴禁任何改動；僅可新增 `Domains` 表與 `DomainMapping` 表。
- [ ] 既有問答與 RAG 核心檢索邏輯 `rag_retriever.py` 嚴禁任何改動。
- [ ] `LLM_USE_GLOSSARY_ALIGN=False` 時的舊行為路徑嚴禁破壞，確保預設零風險。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 專案進度治理框架 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` |
| plan 結構契約與治理規格 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／SOP 核查 | `.claude-logs/ref/WORKFLOW_SOP.md §3 §5 §6` |
| PipelineCore 大改版（三大共用真理源 U8，本器為其一） | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md §2 U8` |
| GLOSSARY-CORE 術語庫（本器之下游消費方） | `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md` |
| 領域診斷模組介面 | `processor/domain_detector.py L32-86` |
| ORM 數據結構規格 | `models.py L87-157` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**：
  在 `tests/` 下建立專屬測試檔 `tests/test_domain_normalizer.py`：
  *   `test_domain_normalization_content_based`：驗證輸入履歷「投放/社群」對齊為 `"HF"`，輸入「Python/LLM」對齊為 `"QA"`。
  *   `test_domain_dynamic_registration`：驗證輸入冷門領域「侏羅紀/化石/恐龍」，若資料庫無 `"QE"` 則自動在 `Domains` 表中註冊 `lcc_code='QE', name='Geology/Paleontology'`（確認無單字寫入）。
  *   `test_domain_mapping_cache_hit`：驗證快取命中，第二次查詢實現 0ms 且零 API 呼叫。
  *   `test_feature_flag_off_preserves_raw`：驗證 `LLM_USE_GLOSSARY_ALIGN=False` 時走舊 raw domain 直注路徑。

### §6.2 手動端到端（E2E）驗證流程

1.  **步驟一**：設定 `LLM_USE_GLOSSARY_ALIGN=True`，準備一份包含「侏羅紀/恐龍」文字的冷門學科 PDF。
2.  **步驟二**：啟動 Pipeline，觀察日誌與資料庫，確認 `Domains` 表中自動新增了 `"QE"` 記錄，且 `Paper.domain` 寫入 `"QE"`。
3.  **步驟三**：上傳第二份同為「侏羅紀/恐龍」的 PDF，確認直接命中 `DomainMapping` 本地快取（顯示 0ms cache hit）。
4.  **步驟四**：檢查 `Paper.domain` 對應之 `"QE"` 術語記錄，確認此時無任何自動寫入的單字/術語（單字為後續 Glossary 任務負責）。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **LCC 動態產生失敗的降級方案** | **寫檔與 LLM 均設 try/except，失敗時退回 `"general"` 不阻斷 Pipeline** | 動態註冊因 LLM 異常或 SQLite 鎖定可能失敗。退回 `"general"` 可確保系統的高可用性。 |
| **動態生成的 LCC 代碼範圍是否作限制** | **在 LLM System Instruction 中定義 LCC 1–3 字母基本規則，且長度嚴格限為 1 至 3 字元** | 避免 LLM 產出過長或非標準 LCC 碼，保證資料庫 `lcc_code` 主鍵的簡潔性與檢索效能。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 DOMAIN-NORM 領域標準化對齊器的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 DOMAIN-NORM tasks / 執行報告；GLOSSARY-CORE plan；PIPE plan §2 U8 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義領域標準化與動態註冊規格；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-03)：依據 baron 17:00 需求進行重構——徹底廢除寫死的靜態白名單，改為 **「基於文檔實質內容的 LCC 代碼動態生成與自癒註冊」** 架構；設計 `Domains` 領域註冊表與 `DomainMapping` 快取對應；明確定義履歷等文檔按實質技能（如 QA/HF）判定領域；落實動態註冊 LCC（不塞入單字）之規格。
- v1 (2026-06-01)：初版建立，由 GLOSSARY-CORE v1 拆分而出，為靜態白名單設計。
