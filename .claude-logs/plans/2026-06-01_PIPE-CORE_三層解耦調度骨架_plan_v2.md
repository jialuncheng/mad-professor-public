# PIPE-CORE 三層解耦調度骨架 plan

> 在新目錄 `pipelines/` 落地 PIPE 大改版的「三層解耦」**空骨架**：Orchestrator（宣告式四 Phase DAG 調度）＋ Pydantic `PipelineContext`（類型安全狀態載體，取代可變 dict 黑盒）＋ `PipelineFactory.get_strategy` ＋ `DocumentStrategy` 抽象基類。本骨架只定義「調度與合約交接的契約」，**不含任何 doc_type 業務細節**（具體五路落地屬 PIPE-RESUME/VISUAL/… 各 plan）。本 plan 為純規格定義，不含 commit 拆分。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：舊 `pipeline_core.py` 為扁平 main loop 驅動的 God Class（`while i < len(self.stages)` L297），三種職責（工作流調度／狀態生命週期／doc_type 業務路由）混雜，狀態靠可變 dict 黑盒（`self._metadata` L251、`output_paths` L293）跨 stage 隱式傳遞，新增 doc_type 須改主幹 inline 分支（如 analyze/detect_domain L301-345、translate/image_caption L356-398 特化）。PIPE 大改版要求三層解耦，但解耦必須先有「空骨架」承接——五路策略無處插入、四份合約無載體承接、影子並行無調度入口。
- **解法**：在新目錄 `pipelines/` 建立三層解耦空骨架——(1) **Orchestrator**：宣告式推進 P1→P2→P3→P4 四 Phase 狀態機，每 Phase 呼叫 `strategy.run_phaseN(ctx)`、在交接點以合約 schema 驗證 Context、`reading_ready`/`rag_status` 解鎖、Early Emit 與 Checkpoint 掛點、`shadow` 旗標貫穿，**零 doc_type 業務細節**；(2) **`PipelineContext`**：Pydantic 類型安全載體，欄位對齊 PIPE-SPEC 四份合約（IngestionMetadataSpec／GlossaryReadySpec／BilingualMarkdownSpec／RAG-DB），跨 Phase 唯一狀態通道，禁可變 dict；(3) **`PipelineFactory` + `DocumentStrategy` ABC**：定義五路統一四 Phase 介面（`run_phase1..run_phase4`）與 `doc_type → strategy` 註冊/查找機制，骨架階段只提供 ABC 與註冊表，**不附任何具體策略實作**。
- **影響**：**不改任何既有業務代碼**（舊 `pipeline_core.py` 全程不動，新目錄物理共存）。新增 `pipelines/` 目錄：`orchestrator.py`／`context.py`／`factory.py`／`base_strategy.py`／`__init__.py`；新增 `tests/test_pipe_core.py` 驗證 DAG 順序、合約驗證、工廠分派、Context 不可變越界防護。無 DB Schema 變動；`DocumentStrategy` ABC 為新增介面、無既有簽名變動；骨架階段 runtime 不接線上流量（`SHADOW_LAUNCH_ENABLED` 預設 false，且尚無具體策略註冊）。

---

## §2 目標規格

> 以下為本骨架必須達到的「最終狀態」規格（What it should be），可量化檢驗。實作細節（如何寫）屬 tasks 階段。

### U1. Orchestrator 指揮層（零業務細節）
- `Orchestrator` 唯一職責＝「保證每 Phase 按四 Phase DAG 順序、依 Context 合約正確交付」。以**宣告式 Phase 序列**（非散落 if/elif）推進 P1→P2→P3→P4。
- **硬約束**：Orchestrator 原始碼**不得出現任何 `doc_type` 字面量分支**（grep `doc_type ==` 於 `orchestrator.py` 須 0 命中）；所有 doc_type 專屬 how 一律下放策略插件。
- 掛點（骨架定義介面、實作可空樁）：Early Emit hook（P1 快軌後）、Checkpoint 讀寫（每 Phase 邊界）、`reading_ready` 解鎖（P3 完成）、P4 非同步派發掛點（不在 Orchestrator 內阻塞）。

### U2. PipelineContext 狀態層（Pydantic 類型安全）
- `PipelineContext` 為 Pydantic 模型，承載四份凍結合約產物，欄位分區對齊 PIPE-SPEC §1.1：
  - `ingestion: IngestionMetadataSpec | None`（合約①；P1 寫入）
  - `glossary_ready: GlossaryReadySpec | None`（合約②；P2 寫入）
  - `bilingual: BilingualMarkdownSpec | None`（合約③；P3 寫入）
  - `rag: RagDbSpec | None`（合約④；P4 寫入）
  - 調度元欄位：`doc_type`、`paper_id`、`shadow: bool`、`phase: PhaseEnum`、`reading_ready: bool`、`rag_status: Literal['pending','ready','failed']`。
- **硬約束**：跨 Phase 狀態傳遞**唯一通道為 `PipelineContext`**，禁止可變全域 dict 黑盒（取代舊 `self._metadata`/`output_paths` 隱式修改）。每份合約子模型本身亦為凍結 Pydantic（對齊 SPEC 凍結語意）。

### U3. PipelineFactory + DocumentStrategy 抽象基類
- `DocumentStrategy`（ABC）定義五路統一介面，至少含四 Phase 方法簽名：
  ```
  run_phase1(ctx) -> IngestionMetadataSpec     # P1 Ingestion
  run_phase2(ctx) -> GlossaryReadySpec         # P2 Glossary & Context Prep
  run_phase3(ctx) -> BilingualMarkdownSpec     # P3 Translation & Restore
  run_phase4(ctx) -> RagDbSpec                 # P4 Async RAG
  rag_char_threshold: int                       # ≥10 或 ≥3（SPEC §3.1）
  ```
- `PipelineFactory.get_strategy(doc_type: str) -> DocumentStrategy`：以註冊表（`@register('academic')` 裝飾器或顯式 mapping）查找；**未命中一律降級 LiteDoc 路**（對齊 SPEC §3.3 最後防線語意）。
- **硬約束（骨架階段）**：本 plan 只交付 ABC + 工廠 + 註冊機制 + 一個 `NullStrategy`（四 Phase 拋 `NotImplementedError`、供骨架測試與防止「無策略時靜默通過」）；**不附任何具體五路實作**，避免與 PIPE-RESUME 等下游 plan 職責重疊。

### U4. 四 Phase 狀態機與合約驗證
- Orchestrator 推進每 Phase 後，於交接點**強制以 Pydantic 驗證**該 Phase 產出合約：
  - 交接點① 驗證：`ingestion` 不含 Abstract/LCC/Glossary（對齊 SPEC R1.1，以 schema 禁欄位斷言）。
  - 交接點②③④ 驗證：對應 Spec 必填欄位齊備。
- 驗證失敗即中止後續 Phase、標記失敗狀態（P1–P3 失敗 → `FAILED`；P4 失敗 → 僅 `rag_status='failed'`、不影響 `reading_ready`，對齊 SPEC R4.2）。

### U5. 程式流程與判斷（Program Flow & Decision）

#### §2.5.1 Orchestrator 主調度流程（`orchestrator.run(ctx)`）
```
START run(ctx: PipelineContext)
  │
  ├─ 1. strategy = PipelineFactory.get_strategy(ctx.doc_type)
  │     └─[判斷] doc_type 未註冊？ ──► 降級 LiteDocStrategy（SPEC §3.3 最後防線）
  │
  ├─ 2. [判斷] Checkpoint 存在（resume 場景）？
  │     ├─ 是 ──► 載入既有 ctx、phase 跳至斷點後續 Phase
  │     └─ 否 ──► phase = P1
  │
  ├─ 3. ── Phase 1 Ingestion ──
  │     ├─ spec1 = strategy.run_phase1(ctx)
  │     ├─[驗證] 交接點① schema：含 Abstract/LCC/Glossary？ ──► FAIL「P1 越界」、status=FAILED、終止
  │     ├─ ctx.ingestion = spec1、寫 Checkpoint
  │     └─[掛點] Early Emit（Title/Author only）─ 快軌已備則早發渲染
  │
  ├─ 4. ── Phase 2 Glossary & Context Prep ──
  │     ├─ spec2 = strategy.run_phase2(ctx)
  │     ├─[驗證] 交接點②：摘要/LCC/凍結 Glossary/translated_abstract 齊？ ──► 缺 → FAILED、終止
  │     └─ ctx.glossary_ready = spec2、寫 Checkpoint
  │
  ├─ 5. ── Phase 3 Translation & Restore ──
  │     ├─ spec3 = strategy.run_phase3(ctx)
  │     ├─[驗證] 交接點③：含 AI Questions/Summary 等非原著？ ──► FAIL、FAILED、終止
  │     ├─ ctx.bilingual = spec3、寫 Checkpoint
  │     └─ ★ ctx.reading_ready = True（閱讀器/Print PDF 解鎖，SPEC R4.1）
  │
  ├─ 6. ── Phase 4 Async RAG（非阻塞派發）──
  │     ├─ 派發背景任務 run_phase4（不在 Orchestrator 內 await）
  │     └─[判斷] 背景結果
  │           ├─ 成功 ──► ctx.rag_status='ready'（解鎖 AI Chat）
  │           └─ 失敗 ──► ctx.rag_status='failed' + warning（SPEC R4.2，主鏈不受影響）
  │
  └─ 7. return ctx（reading_ready 已 True；rag_status 由背景回填）
        END
```

#### §2.5.2 工廠分派流程（`PipelineFactory.get_strategy`）
```
START get_strategy(doc_type)
  │
  ├─ 1. [判斷] doc_type ∈ 註冊表？
  │     ├─ 是 ──► return 註冊策略實例
  │     └─ 否 ──► [判斷] LiteDoc 已註冊？
  │                 ├─ 是 ──► return LiteDocStrategy（fallback）
  │                 └─ 否（骨架階段尚無任何具體策略）──► return NullStrategy
  │                       （四 Phase 拋 NotImplementedError、防靜默通過）
  └─ END
```

### U6. 資料流程（Data Flow）

```
┌──────────────────────────── 輸入 ────────────────────────────┐
│  doc_type + pdf_path + shadow 旗標  ──►  Orchestrator.run()   │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
   PipelineFactory.get_strategy(doc_type) ──► DocumentStrategy 實例
        │
        ▼
   ┌──────────────── PipelineContext（唯一狀態通道，Pydantic）─────────────────┐
   │                                                                            │
   │  P1 run_phase1 ─►① IngestionMetadataSpec ─►[驗證]─► ctx.ingestion         │
   │        │  （🚫 Abstract/LCC/Glossary）          └─► Checkpoint + Early Emit │
   │        ▼                                                                   │
   │  P2 run_phase2 ─►② GlossaryReadySpec ─►[驗證]─► ctx.glossary_ready        │
   │        │  （摘要+LCC+凍結Glossary+translated_abstract）  └─► Checkpoint     │
   │        ▼                                                                   │
   │  P3 run_phase3 ─►③ BilingualMarkdownSpec ─►[驗證]─► ctx.bilingual         │
   │        │  （乾淨雙語 md）          └─► Checkpoint ＋ ★reading_ready=True    │
   │        ▼ （非阻塞派發）                                                     │
   │  P4 run_phase4 ─►④ RagDbSpec ─►[背景] ─► ctx.rag = spec4                  │
   │             （vectors/ + Paper/PaperChunk + index_meta）                   │
   │                              └─► rag_status ∈ {ready, failed}             │
   └────────────────────────────────────────────────────────────────────────┘
        │
        ▼
   輸出：ctx（reading_ready 早於 rag_status；shadow=True 時產物落 *_shadow/）
```

- **狀態流向鐵律**：所有 Phase 間資料只經 `PipelineContext` 顯式欄位傳遞，骨架**禁止**任何 stage 直接讀寫他 Phase 的硬碟產物或全域變數（取代舊 `output_paths` dict 隱式共享）。
- **影子隔離**：`ctx.shadow=True` 時，`paper_id` 尾綴 `_shadow`、產物落 `output/*_shadow/`、Resolved Title 加 ` (測試)`（對齊 SPEC §3.5）；骨架只負責把 `shadow` 旗標貫穿至 Context 與產物路徑命名，不改既有 list/get/delete API。

### U7. 產出物明確定義（Deliverables）

> 本計畫落地後**必須且僅產出**以下資產；任何超出此清單的改動均屬越界，須走 §0 改版。三表分列：① 本計畫交付物（自建空骨架）、② 消費不交付（讀既有真理源規格）、③ 明確不產出（零越界保證）。

#### ① 本計畫交付物（self-built）

| 交付物 | 類型 | 內容定義 | 歸屬路徑 |
|---|---|---|---|
| **Orchestrator 指揮層** | 新模組 | 宣告式四 Phase DAG 調度（P1→P2→P3→P4）、交接點 Pydantic 合約驗證、Early Emit／Checkpoint／`reading_ready`／P4 非阻塞派發掛點、`shadow` 旗標貫穿；**零 doc_type 字面量分支** | `pipelines/orchestrator.py` |
| **PipelineContext 狀態層** | 新模組 | Pydantic 類型安全狀態載體，欄位分區對齊四份合約（`ingestion`／`glossary_ready`／`bilingual`／`rag`）＋調度元欄位（`doc_type`／`paper_id`／`shadow`／`phase`／`reading_ready`／`rag_status`），取代舊可變 dict 黑盒 | `pipelines/context.py` |
| **四份合約 Pydantic schema** | 新模組 | 對齊 PIPE-SPEC §1.1 凍結合約的子模型（`IngestionMetadataSpec`／`GlossaryReadySpec`／`BilingualMarkdownSpec`／`RagDbSpec`），凍結語意、被 Orchestrator 與五路策略共同 import（位置 `pipelines/contracts.py`，§7 Q1 待 baron 拍板是否拆頂層） | `pipelines/contracts.py` |
| **PipelineFactory + DocumentStrategy ABC** | 新模組 | 五路統一四 Phase 介面（`run_phase1..4` + `rag_char_threshold`）抽象基類＋`get_strategy(doc_type)` 註冊/查找機制＋未命中降級 LiteDoc＋`NullStrategy` 哨兵（四 Phase 拋 `NotImplementedError`）；**不附任何具體五路實作** | `pipelines/factory.py`＋`pipelines/base_strategy.py` |
| **套件初始化** | 新模組 | `pipelines/` 套件入口，匯出 Orchestrator／Context／Factory／ABC 公開介面 | `pipelines/__init__.py` |
| **骨架契約測試** | pytest | 驗證 DAG 順序（P1→P2→P3→P4＋P4 非阻塞）／交接點合約驗證 FAIL／工廠分派（命中／降級 LiteDoc／NullStrategy）／Context 不可變越界／P4 容錯（`reading_ready` 仍 True）／shadow 貫穿 | `tests/test_pipe_core.py` |

#### ② 消費不交付（讀既有真理源、零改動）

| 消費對象 | 提供方 | 消費方式 |
|---|---|---|
| 四份凍結接口合約定義 | `PIPE-SPEC §1.1`（規格真理源） | 純對齊，Context 子模型欄位/凍結語意依此宣告 |
| 策略管線插件契約（DocumentStrategy 介面與 factory 語意） | `PIPE-SPEC §1.3` | 純對齊，ABC 四 Phase 方法簽名依此定義 |
| 行為合約硬規則（R1.1–R6.1） | `PIPE-SPEC §2` | 純對齊，交接點驗證斷言與 P4 容錯依此 |
| 影子並行命名鐵律（`_shadow`／` (測試)`） | `PIPE-SPEC §3.5` | 純對齊，`shadow` 旗標路徑命名依此 |
| 舊單體 `pipeline_core.py` | 既有 God Class | **純讀為對照**（grep 現況證據），物理共存、影子期全程不動 |

#### ③ 明確不產出（零越界保證）

| 不產出項 | 保證 |
|---|---|
| **零既有業務代碼變動** | 舊 `pipeline_core.py` 11-stage／`process`／main loop／可變 dict 全程不動、不刪、不改（Flip 屬 PIPE-FLIP plan） |
| **零具體五路策略實作** | 骨架只交付 ABC＋工廠＋註冊機制＋`NullStrategy` 哨兵；五路 how 屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK 各 plan |
| **零 web 層接線** | 不碰 `web_server.py` 上傳/派發入口（雙軌派發 scaffolding 屬 PIPE-SCAFFOLD plan） |
| **零 DB Schema 變動** | Context／合約為記憶體 Pydantic 模型，不新增 `models.py` 表/欄位（RAG/DB 落庫屬 RAG-ASYNC plan） |
| **零 processor 接線** | 只定義 `DocumentStrategy` ABC，不在本 plan 接線任何既有 `processor/*` 解析/翻譯/RAG 模組 |
| **零線上流量** | `SHADOW_LAUNCH_ENABLED` 預設 false 且骨架尚無具體策略註冊，runtime 不接線上流量 |

---

## §3 現況與證據

詳細盤點舊單體調度核心與本骨架的對應關係：

- **`pipeline_core.py`**（舊 God Class，本骨架共存、不動）：
  - `STAGE_NAMES L40-43` + `__init__ L62-95`（`self.stages = stages or default_stages` L95）：扁平 11-stage 靜態陣列驅動。
  - `process L211` → main loop `while i < len(self.stages) L297`（`stage = self.stages[i] L298`）：單一扁平迴圈混雜三職責，新核心改為宣告式四 Phase DAG。
  - 可變 dict 黑盒狀態：`self._metadata = create_empty_metadata() L251`、`output_paths = dict(...) L293`、`output_paths[s] = result L333`——跨 stage 隱式修改，新核心改為 Pydantic `PipelineContext`。
  - doc_type/stage inline 特化：analyze/detect_domain 連動 `L301-345`、translate/image_caption 連動 `L356-398`——主幹硬編碼分支，新核心下放策略插件。
- **PIPE-SPEC**：三層解耦泳道（§0.3）、四份合約（§1.1）、策略插件契約（§1.3）、行為合約 R1.1–R6.1（§2）為本骨架介面真理源。

### §3.1 grep 鋼鐵證據

```bash
grep -nE "STAGE_NAMES|self\.stages|while i < len|def process" pipeline_core.py | head
# 40:STAGE_NAMES = [
# 94:        default_stages = list(STAGE_NAMES)
# 95:        self.stages = stages or default_stages
# 211:    def process(self, pdf_path: str, output_dir: Optional[str] = None,
# 297:        while i < len(self.stages):

grep -nE "self\._metadata|output_paths =|output_paths\[" pipeline_core.py | head
# 251:        self._metadata = create_empty_metadata()
# 293:        output_paths = dict(existing_paths) if existing_paths else {}
# 333:                                output_paths[s] = result

grep -nE "stage == 'analyze'|stage == 'translate'" pipeline_core.py
# 301:            if stage == 'analyze' and 'detect_domain' in self.stages:
# 356:            if stage == 'translate' and 'image_caption' in self.stages:
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本骨架建立中嚴禁任何改動：**

- [ ] **`pipeline_core.py` 整個舊單體（11-stage / `process` / main loop / 可變 dict 狀態）**：新核心於 `pipelines/` 物理共存，舊單體影子期全程不動、不刪、不改（Flip 屬 PIPE-FLIP plan）。
- [ ] **`web_server.py` 上傳/派發入口**：影子雙軌派發 scaffolding 屬 PIPE-SCAFFOLD plan，本骨架不碰 web 層。
- [ ] **`models.py` 既有 Schema**：本骨架的 Context/合約為記憶體 Pydantic 模型，不新增 DB 表/欄位（RAG/DB 落庫實作屬 RAG-ASYNC plan）。
- [ ] **`processor/*` 既有解析/翻譯/RAG 模組**：骨架只定義 `DocumentStrategy` ABC 介面，不在本 plan 內接線任何既有 processor（接線屬各路 PIPE-* plan）。
- [ ] **Orchestrator 原始碼禁混入 doc_type 業務分支**：自我約束邊界，違反即破壞三層解耦本意。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 三層解耦泳道（Orchestrator/Context/Atomic Stages 職責與嚴禁） | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md §0.3` |
| 四份凍結接口合約（Context 欄位對齊源） | `PIPE-SPEC §1.1` |
| 策略管線插件契約（DocumentStrategy 介面與 factory） | `PIPE-SPEC §1.3` |
| 行為合約硬規則（R1.1–R6.1，交接點驗證依據） | `PIPE-SPEC §2` |
| 向下相容過渡／影子並行命名鐵律 | `PIPE-SPEC §3.4 §3.5` |
| 大改版 U1 三層解耦／§8.3 PIPE-CORE 路線圖定位 | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v7.md §2 U1 §8.3` |
| plan 結構契約與治理規格 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／文件歸屬 | `.claude-logs/ref/WORKFLOW_SOP.md §2 §3 §6` |
| 雙軌制／不可動清單／plan 結構 | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 §4` |
| 現況調度核心／可變狀態 | `pipeline_core.py L40-95 L211-398` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**（防 Regression 底線）：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**（`tests/test_pipe_core.py`）：
  - **DAG 順序**：Orchestrator 以固定 NullStrategy 跑，斷言 Phase 推進序為 P1→P2→P3→P4，且 P4 為非阻塞派發。
  - **合約驗證**：餵含 Abstract/LCC/Glossary 的偽 P1 產物，斷言交接點① 驗證 FAIL；缺 `translated_abstract` 的 P2 產物，斷言交接點② FAIL。
  - **工廠分派**：註冊 stub 策略 → `get_strategy('academic')` 命中；未知 doc_type → 降級 LiteDoc；骨架無策略 → 回 NullStrategy 且四 Phase 拋 `NotImplementedError`。
  - **Context 不可變越界**：斷言他 Phase 欄位未寫入前為 `None`、跨 Phase 僅經 Context 傳遞（無全域 dict）。
  - **P4 容錯**：模擬 `run_phase4` 拋例外，斷言 `reading_ready` 仍 True、`rag_status='failed'`、不向上拋（SPEC R4.2）。
  - **shadow 貫穿**：`ctx.shadow=True` 時 `paper_id` 含 `_shadow`、產物路徑落 `*_shadow/`。

### §6.2 手動端到端（E2E）驗證流程

1. **骨架隔離驗證**：`SHADOW_LAUNCH_ENABLED=false`，確認線上 100% 仍走舊 `pipeline_core.py`、新骨架不接流量、既有行為零變化。
2. **NullStrategy 空跑驗證**：以 NullStrategy 手動跑 Orchestrator，確認四 Phase DAG 推進日誌正確、`reading_ready` 在 P3 後置 True、P4 派發後 `rag_status` 由背景回填。
3. **合約驗證攔截**：手動構造越界 P1 產物，確認 Orchestrator 於交接點① 攔截並標 FAILED。
4. **doc_type 無分支核查**：`grep -nE "doc_type ==" pipelines/orchestrator.py` 須 0 命中（三層解耦自證）。
5. **共存無污染**：確認新增 `pipelines/` 目錄不影響既有 `pytest tests/` 全綠、無 import 連鎖破壞。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **四份合約 Pydantic 模型放 `pipelines/` 還是獨立 `contracts/`** | **獨立 `pipelines/contracts.py`（或 `pipelines/contracts/`）** | 四份合約為 PIPE-SPEC 凍結介面、被 Orchestrator 與五路策略共同 import，獨立模組避免循環依賴；與 Orchestrator 同根 `pipelines/` 便於整體 Flip 後管理。是否進一步拆出獨立頂層 `contracts/` 待 baron 評估專案目錄潔癖度。 |
| **Checkpoint 持久化載體（記憶體／JSON 檔／SQLite）** | **骨架先定義 Checkpoint 介面 + JSON 檔實作樁，持久化策略後續可換** | 骨架階段重點是「掛點存在且 Orchestrator 能 resume」，非持久化效能；先用最簡 JSON 檔落 `output/<paper>/_checkpoint.json`，未來如需高併發再換 SQLite，介面不變。 |
| **`run_phase4` 非阻塞派發在骨架階段用何機制** | **骨架定義「派發掛點」介面、預設同步樁，真正 BackgroundTasks 接線屬 RAG-ASYNC plan** | P4 非同步落地（FastAPI BackgroundTasks）牽涉 web 層、屬 RAG-ASYNC 職責；骨架只保證「Orchestrator 不在主鏈 await P4」的介面契約，避免與下游 plan 重疊。 |
| **NullStrategy 是否該存在於正式碼（而非僅測試）** | **存在於正式碼，作為「未註冊任何策略」的顯式失敗哨兵** | 防止骨架階段 / 未來漏註冊時 Orchestrator 靜默跑空通過；NullStrategy 四 Phase 拋 `NotImplementedError` 使問題立即暴露，比回 None 安全。Flip 後五路齊全仍保留作防呆。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-CORE 三層解耦調度骨架的目標規格，作為五路策略插件（PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK）落地的承接基座 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；PIPE-SCAFFOLD 與五路 PIPE-* plan 引用其 Orchestrator/Context/Factory 介面 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 PIPE-CORE tasks / PIPE-SCAFFOLD / 五路 PIPE-* 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史；嚴禁含 commit 拆分（屬 tasks 階段）；Orchestrator 嚴禁混入 doc_type 業務分支；嚴禁附任何具體五路策略實作 |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | PIPE-FLIP 收官且新核心全面接管後，經 baron 同意歸檔至 archive/ |
| **重複防護** | 僅定義調度骨架技術規格；四份合約與行為硬規則唯一源在 PIPE-SPEC；具體五路 how 唯一源在各路 PIPE-* plan；工作流規格一律引用 WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-01)：依 PIPE master plan v7 對齊更新——新增 **U7 產出物明確定義**（三表：① 本計畫交付物 `pipelines/{orchestrator,context,contracts,factory,base_strategy,__init__}.py`＋`tests/test_pipe_core.py`；② 消費不交付 PIPE-SPEC §1.1/§1.3/§2/§3.5 規格真理源＋舊單體純讀對照；③ 明確不產出零業務代碼／零具體五路策略／零 web 接線／零 DB Schema／零 processor 接線／零線上流量）；§5 大改版依據檔名同步 `_plan_v2.md` → `_plan_v7.md`。
- v1 (2026-06-01)：初版建立，依 PIPE-SPEC §0.3 三層解耦泳道與 §1.1/§1.3/§2 介面與行為合約，定義 Orchestrator 零業務指揮層（U1）／PipelineContext Pydantic 狀態層（U2）／PipelineFactory + DocumentStrategy ABC（U3）／四 Phase 狀態機與合約驗證（U4）／程式流程與判斷雙流程圖（U5）／資料流程圖（U6）；§3 附 `pipeline_core.py L40-95 L211-398` 扁平 loop 與可變 dict grep 證據；§7 列 4 項 Open Questions（合約模組位置／Checkpoint 載體／P4 派發機制／NullStrategy 哨兵）。
