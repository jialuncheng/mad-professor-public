# PIPE-CORE 三層解耦調度骨架 — Tasks（v2）

> 本文件為 PIPE-CORE 的 **OP-N 執行階段拆分清單**（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md` 計畫產出，含 4 個 OP 執行階段。
> **本任務不拆分 Git Commit**，改以「OP-N 執行階段」推進；commit / push 由 baron 手動執行（CLAUDE.md §1.3）。
> **收官歸檔鐵律**：OP-1~OP-3 執行期所有 plan／tasks／執行報告一律暫存 baton/、不移動、不入版控；**唯一在最後 OP-4（Checkout）一次性 `mv` + `git add` 歸檔**（WORKFLOW_SOP §3）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 7 個 | `pipelines/__init__.py` / `pipelines/contracts.py` / `pipelines/context.py` / `pipelines/factory.py` / `pipelines/base_strategy.py` / `pipelines/orchestrator.py` / `tests/test_pipe_core.py` |
| **修改檔案** | 2 個 | `.claude-logs/TODO.md`（新增任務 + 收官結案）/ `.claude-logs/prompts/INDEX.md`（提示詞登記） |
| **目錄初始化** | 1 個 | `pipelines/`（PIPE 新核心三層解耦套件，與舊 `pipeline_core.py` 物理共存） |
| **狀態更新** | 2 個 | `TODO.md` PIPE-CORE_v2 條目（🟡 WIP → ✅）/ `prompts/INDEX.md` 登記 |
| **執行階段** | 4 個 | OP-1（合約與狀態層）→ OP-2（工廠與策略基類）→ OP-3（Orchestrator 四 Phase DAG）→ OP-4（Checkout / 收官歸檔） |
| **執行報告** | 4 個 | `baton/2026-06-02_PIPE-CORE_OP-1/OP-2/OP-3/OP-4_執行.md`（套用 template_execution.md、暫存 baton/） |
| **baton 歸檔** | 1 次 | **僅 OP-4 收官**一次性 `mv` plan_v2＋tasks_v2＋四份 OP 執行報告至正式目錄 + `git add` |

> **不附任何具體五路策略實作**（plan v2 U3 硬約束）：本任務只交付空骨架 + ABC + 工廠 + `NullStrategy`；五路 how 屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK 各 plan。

---

## §1 TL;DR（概要）

- **挑戰**：舊 `pipeline_core.py` 為扁平 main loop God Class（`while i < len(self.stages)` L297），調度/狀態/doc_type 路由三職責混雜、狀態靠可變 dict 黑盒隱式傳遞；PIPE 大改版要求三層解耦，但需先有「空骨架」承接五路策略、四份合約與影子並行調度入口。
- **解法**：原子化拆 4 個 OP——**OP-1** 合約與狀態層（`contracts.py` 四份凍結 Pydantic + `context.py` PipelineContext）；**OP-2** 工廠與策略基類（`factory.py` + `base_strategy.py`：DocumentStrategy ABC + NullStrategy + 註冊/降級）；**OP-3** Orchestrator 四 Phase DAG 調度（`orchestrator.py` + `__init__.py`：宣告式 P1→P4 + 交接點合約驗證 + reading_ready/rag_status + Early Emit/Checkpoint/P4 派發掛點）；**OP-4** Checkout 收官歸檔。
- **影響範圍**：100% 新增 `pipelines/` 套件與測試；**零既有業務代碼改動**（舊 `pipeline_core.py` / `web_server.py` / `models.py` / `processor/*` 全程不動，新目錄物理共存，runtime 不接線上流量）。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/`（目錄） | 不存在 | 須新建套件（6 模組） |
| `pipeline_core.py` | 舊 God Class（`STAGE_NAMES L40-43`、main loop `while i < len(self.stages) L297`、可變 dict `self._metadata L251`/`output_paths L293`、doc_type inline 特化 L301-345/L356-398） | **只讀對照、不動**；新核心 `pipelines/` 物理共存，Flip 屬 PIPE-FLIP |
| `tests/test_pipe_core.py` | 不存在 | 須新建契約測試（DAG/合約驗證/工廠/Context/P4 容錯/shadow） |
| PIPE-SPEC §1.1 | 四份凍結接口合約規格 | `contracts.py` 欄位對齊源（唯讀引用） |

---

## §3 觀察問題

### 問題 #1：扁平 main loop 混雜三職責、無解耦承接點
- **證據**：`pipeline_core.py L297 while i < len(self.stages)` + doc_type inline 特化 `L301-345`（analyze/detect_domain）、`L356-398`（translate/image_caption）。
- **影響**：新增 doc_type 須改主幹分支；五路策略無處插入、四份合約無載體承接、影子並行無調度入口。

### 問題 #2：可變 dict 黑盒狀態跨 stage 隱式傳遞
- **證據**：`self._metadata = create_empty_metadata() L251`、`output_paths = dict(...) L293`、`output_paths[s] = result L333`。
- **影響**：狀態流向不可追、型別不安全；新核心須以 Pydantic `PipelineContext` 為唯一狀態通道取代。

---

## §4 設計方案

> 逐 OP 列出落地設計概要；完整規格見 plan v2 §2（U1–U7）。

### §4.1 OP-1 — 合約與狀態層
`pipelines/contracts.py`：四份凍結 Pydantic 子模型（`IngestionMetadataSpec` / `GlossaryReadySpec` / `BilingualMarkdownSpec` / `RagDbSpec`）對齊 PIPE-SPEC §1.1，含 R1.1 禁欄位斷言（ingestion 不得含 Abstract/LCC/Glossary）。`pipelines/context.py`：`PipelineContext`（承載四合約 + 調度元欄位 `doc_type`/`paper_id`/`shadow`/`phase`/`reading_ready`/`rag_status` + `PhaseEnum`）。

### §4.2 OP-2 — 工廠與策略基類
`pipelines/base_strategy.py`：`DocumentStrategy` ABC（`run_phase1..4` + `rag_char_threshold`）+ `NullStrategy`（四 Phase 拋 `NotImplementedError`）。`pipelines/factory.py`：`PipelineFactory.get_strategy(doc_type)` 註冊表 + 未命中降級 LiteDoc（無 LiteDoc 時回 NullStrategy）。

### §4.3 OP-3 — Orchestrator 四 Phase DAG 調度
`pipelines/orchestrator.py`：宣告式 P1→P2→P3→P4 推進（**零 doc_type 字面量分支**）+ 交接點 Pydantic 驗證 + `reading_ready`（P3 後）/`rag_status`（P4 背景）+ Early Emit/Checkpoint/P4 非阻塞派發掛點 + shadow 旗標貫穿。`pipelines/__init__.py`：套件公開介面匯出。

### §4.4 OP-4 — Checkout / 收官歸檔
一次性 `mv` baton/ plan_v2+tasks_v2+四份 OP 報告至 `plans/`/`tasks/`/`executions/` + `git add` + TODO ✅。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 誤動舊 `pipeline_core.py` God Class | 🔴 高 | 新核心全在 `pipelines/` 新目錄、物理共存，舊單體只讀對照、零改（§7） |
| Orchestrator 混入 doc_type 業務分支（破壞三層解耦） | 🔴 高 | OP-3 驗收強制 `grep -nE "doc_type ==" pipelines/orchestrator.py` 須 0 命中 |
| 新增 `pipelines/` import 連鎖破壞既有測試 | 🟡 中 | 骨架不 import 任何既有 processor；OP 驗收跑 `pytest tests/` 確認零迴歸 |
| 修改既有 `tests/test_pipe_core.py`（OP-2/OP-3 追加）未備份 | 🟢 低 | OP-2/OP-3 修改該檔前先 `.bak` 備份並納入 git add（WORKFLOW_SOP §3 .bak 鐵律） |
| baton 暫存報告提早 mv/git add | 🔴 高 | OP-1~OP-3 報告嚴禁移動、僅 OP-4 收官一次性歸檔 |
| Pydantic 版本 API 差異（v1 vs v2） | 🟡 中 | OP-1 先 `grep pydantic` 確認專案版本，對齊既有 `models.py` / SPEC 用法 |

---

## §6 測試計畫

> 每個 OP 在 `tests/test_pipe_core.py` 追加對應測試、保持當階段獨立可測（OP-1 建檔，OP-2/OP-3 追加）。

### §6.1 OP-1 驗收
```bash
python -c "import sys; sys.path.insert(0,'.'); from pipelines.contracts import IngestionMetadataSpec, GlossaryReadySpec, BilingualMarkdownSpec, RagDbSpec; from pipelines.context import PipelineContext; print('import OK')"
pytest tests/test_pipe_core.py -v -k "contract or context"
# 含 Abstract/LCC/Glossary 的偽 P1 產物 → 交接點① 驗證 FAIL；缺必填欄位 → FAIL
```

### §6.2 OP-2 驗收
```bash
pytest tests/test_pipe_core.py -v -k "factory or strategy"
# get_strategy('academic') 命中 stub；未知 doc_type → 降級 LiteDoc；無策略 → NullStrategy 且四 Phase 拋 NotImplementedError
```

### §6.3 OP-3 驗收
```bash
pytest tests/test_pipe_core.py -v
grep -nE "doc_type ==" pipelines/orchestrator.py    # 須 0 命中（三層解耦自證）
# DAG 推進序 P1→P2→P3→P4、P4 非阻塞；交接點① 攔截；P4 拋例外 → reading_ready 仍 True、rag_status='failed'；shadow=True → paper_id 含 _shadow
```

### §6.4 全 OP 共通（零迴歸）
```bash
pytest tests/ -q     # 既有測試全綠（新增 pipelines/ 不破壞既有 import）
```

---

## §7 不可動清單

明確劃定修改邊界。**以下檔案與邏輯在本任務全程嚴禁任何改動：**

- [ ] **`pipeline_core.py` 整個舊單體**（11-stage / `process` / main loop / 可變 dict 狀態）：新核心 `pipelines/` 物理共存，舊單體影子期全程不動、不刪、不改（Flip 屬 PIPE-FLIP plan）。
- [ ] **`web_server.py` 上傳/派發入口**：影子雙軌派發屬 PIPE-SCAFFOLD plan，本骨架不碰 web 層。
- [ ] **`models.py` 既有 Schema**：Context/合約為記憶體 Pydantic 模型，不新增 DB 表/欄位（RAG/DB 落庫屬 RAG-ASYNC plan）。
- [ ] **`processor/*` 既有解析/翻譯/RAG 模組**：骨架只定義 ABC 介面，不接線任何既有 processor。
- [ ] **Orchestrator 原始碼禁混入 doc_type 業務分支**：自我約束邊界，違反即破壞三層解耦本意。
- [ ] **主 repo 目錄（worktree 父目錄）**：嚴禁讀寫。
- [ ] **baton/ 暫存文件（OP-1~OP-3 期間）**：嚴禁提早 `mv` / `git add`，僅 OP-4 收官一次性歸檔。

---

## §8 推薦執行階段拆分

### OP-1 — 合約與狀態層（contracts 四合約 + Context 狀態載體）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `pipelines/__init__.py`（佔位）、`pipelines/contracts.py`、`pipelines/context.py`、`tests/test_pipe_core.py`（建檔） |
| **安全性** | 🟢 高 — 純新增 Pydantic 模型，零既有代碼改動、零 runtime 接線 |
| **可逆性** | 🟢 高 — 刪除 `pipelines/` 與 `tests/test_pipe_core.py` 即還原 |
| **驗收 grep/執行 條件** | 見 §6.1（import OK + `pytest -k "contract or context"` 全綠：交接點① 禁欄位斷言 FAIL、必填欄位 FAIL） |
| **依賴關係** | 無前置 |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-CORE_OP-1_執行.md`（套用 template_execution.md，暫存 baton/、不移動） |
| **具體實作細節** | 1. 先 `grep -rnE "pydantic|BaseModel" models.py requirements*.txt` 確認 Pydantic 版本（v1/v2 API 對齊）。2. `pipelines/contracts.py`：依 PIPE-SPEC §1.1 定義四份**凍結** Pydantic 子模型——① `IngestionMetadataSpec`（P1：title/authors 等；**禁含** abstract/lcc/glossary 欄位，以 schema 層保證 R1.1，可用 model_config `extra='forbid'` + 不宣告禁欄位）；② `GlossaryReadySpec`（P2：摘要/lcc/凍結 glossary/translated_abstract 必填）；③ `BilingualMarkdownSpec`（P3：乾淨雙語 md 路徑/內容；**禁含** AI Questions/Summary）；④ `RagDbSpec`（P4：vectors 路徑/PaperChunk 統計/index_meta）。全部 `frozen=True`（凍結語意）。3. `pipelines/context.py`：`PhaseEnum`（P1/P2/P3/P4）+ `PipelineContext`（Pydantic：`ingestion/glossary_ready/bilingual/rag` 四欄預設 None + 調度元欄位 `doc_type:str`/`paper_id:str`/`shadow:bool=False`/`phase:PhaseEnum`/`reading_ready:bool=False`/`rag_status:Literal['pending','ready','failed']='pending'`）。4. `pipelines/__init__.py`：暫匯出 contracts + context。5. `tests/test_pipe_core.py` 建檔：測 ① 偽 P1 含 abstract → 驗證 FAIL；② 缺 translated_abstract 的 P2 → FAIL；③ PipelineContext 預設 None / phase 推進；④ 合約 frozen 不可變。6. logging 依 logging SOP（模組級 logger；如需）。 |

### OP-2 — 工廠與策略基類（DocumentStrategy ABC + NullStrategy + 工廠降級）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `pipelines/base_strategy.py`、`pipelines/factory.py`；修改 `pipelines/__init__.py`（匯出）、`tests/test_pipe_core.py`（追加，**先 .bak 備份**） |
| **安全性** | 🟢 高 — 純新增介面與工廠，零既有代碼改動 |
| **可逆性** | 🟢 高 — 刪除二新檔 + 還原 `__init__`/測試即可 |
| **驗收 grep/執行 條件** | 見 §6.2（`pytest -k "factory or strategy"` 全綠：命中/降級 LiteDoc/NullStrategy NotImplementedError） |
| **依賴關係** | OP-1（contracts + context） |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-CORE_OP-2_執行.md`（暫存 baton/、不移動） |
| **具體實作細節** | 1. **修改 `tests/test_pipe_core.py` 前先備份**：`cp tests/test_pipe_core.py .claude-logs/archive/2026-06-02_PIPE-CORE_OP-2_test_pipe_core.py.bak`（納入 git add）。2. `pipelines/base_strategy.py`：`DocumentStrategy`（`abc.ABC`）宣告抽象方法 `run_phase1(ctx)->IngestionMetadataSpec` / `run_phase2(ctx)->GlossaryReadySpec` / `run_phase3(ctx)->BilingualMarkdownSpec` / `run_phase4(ctx)->RagDbSpec` + 類屬性 `rag_char_threshold:int`；`NullStrategy(DocumentStrategy)` 四 Phase 一律 `raise NotImplementedError("骨架階段無具體策略")`（防靜默通過哨兵）。3. `pipelines/factory.py`：`PipelineFactory` 含註冊表（`_registry: dict[str, type[DocumentStrategy]]` + `register(doc_type)` 裝飾器或 `register_strategy()`）+ `get_strategy(doc_type)->DocumentStrategy`：命中回實例；未命中且 `'litedoc'` 已註冊 → 降級 LiteDoc（SPEC §3.3 最後防線）；未命中且無 LiteDoc（骨架階段）→ 回 `NullStrategy()`。4. `__init__.py` 匯出 factory/base_strategy。5. 追加測試：stub 策略註冊 → `get_strategy('academic')` 命中；未知 doc_type → 降級/NullStrategy；NullStrategy 四 Phase 拋 NotImplementedError。 |

### OP-3 — Orchestrator 四 Phase DAG 調度（宣告式狀態機 + 交接點驗證）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新建 `pipelines/orchestrator.py`；修改 `pipelines/__init__.py`（匯出 Orchestrator）、`tests/test_pipe_core.py`（追加，**先 .bak 備份**） |
| **安全性** | 🟢 高 — 純新增調度層，零既有代碼改動、runtime 不接流量（`SHADOW_LAUNCH_ENABLED` 預設 false 且無具體策略註冊） |
| **可逆性** | 🟢 高 — 刪除 `orchestrator.py` + 還原 `__init__`/測試 |
| **驗收 grep/執行 條件** | 見 §6.3（`pytest tests/test_pipe_core.py -v` 全綠 + `grep -nE "doc_type ==" pipelines/orchestrator.py` **0 命中**） |
| **依賴關係** | OP-1 + OP-2 |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-CORE_OP-3_執行.md`（暫存 baton/、不移動） |
| **具體實作細節** | 1. **修改 `tests/test_pipe_core.py` 前先備份** `.bak`（納入 git add）。2. `pipelines/orchestrator.py`：`Orchestrator.run(ctx)` 依 plan v2 §2.5.1 **宣告式 Phase 序列**（如 `_PHASES=[(P1,run_phase1,'ingestion',_validate_p1), ...]` 迴圈推進，**禁 doc_type if/elif**）：① `strategy=PipelineFactory.get_strategy(ctx.doc_type)`；② Checkpoint 存在則 resume（骨架先 JSON 樁/介面，§7 Q2）；③ 逐 Phase：呼叫 `strategy.run_phaseN(ctx)` → 交接點 Pydantic 驗證（交接點① 禁欄位 / ②③④ 必填）→ 寫 `ctx.<欄位>` + Checkpoint 掛點；P1 後 Early Emit 掛點（空樁介面）；P3 後 `ctx.reading_ready=True`；P4 非阻塞派發掛點（不在 run 內 await，骨架預設同步樁，真正 BackgroundTasks 屬 RAG-ASYNC，§7 Q3），成功 `rag_status='ready'`、失敗 `rag_status='failed'`+warning（不拋、不影響 reading_ready，SPEC R4.2）；P1–P3 驗證失敗 → `phase`/狀態標 FAILED 並中止。3. `__init__.py` 匯出 Orchestrator。4. 追加測試：DAG 序 P1→P4 + P4 非阻塞；交接點① 攔截越界 P1；P4 模擬拋例外 → reading_ready 仍 True/rag_status='failed'/不上拋；shadow=True → paper_id 含 `_shadow`、產物路徑落 `*_shadow/`（命名貫穿）。5. `grep doc_type ==` 自證 0 命中。 |

### OP-4 — Checkout / 收官歸檔（一次性 Traceability 交接）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` baton/ plan_v2+tasks_v2+OP-1~OP-4 報告 → `plans/`/`tasks/`/`executions/` + `git add`；修改 `.claude-logs/TODO.md` |
| **安全性** | 🟢 高 — 純文件搬移與版控追蹤，零代碼改動 |
| **可逆性** | 🟢 高 — `git rm --cached` + `mv` 回 baton/ 即還原 |
| **驗收 grep/執行 條件** | `ls .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/ \| grep PIPE-CORE`（歸檔齊全）；`ls .claude-logs/baton/ \| grep -c PIPE-CORE` = 0；`git status -s` 已追蹤 |
| **依賴關係** | OP-1 + OP-2 + OP-3（三 OP 報告皆已產於 baton/） |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-CORE_OP-4_執行.md`，於本階段最後一併 `mv` 至 `executions/` |
| **具體實作細節** | 1. 先產 `OP-4_執行.md`（暫存 baton/，記錄 Conformance + 歸檔清單 + diff stat）。2. **一次性歸檔搬移**（WORKFLOW_SOP §3 收官歸檔鐵律）：<br>`mv .claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md .claude-logs/plans/`（**保留 `_v2`**）<br>`mv .claude-logs/baton/2026-06-02_PIPE-CORE_三層解耦調度骨架_tasks_v2.md .claude-logs/tasks/`（**保留 `_v2`**）<br>`mv .claude-logs/baton/2026-06-02_PIPE-CORE_OP-*_執行.md .claude-logs/executions/`。3. `git add` 上述全部正式檔（plans/tasks/executions）+ `pipelines/`（6 模組）+ `tests/test_pipe_core.py` + `.bak` 備份 + prompts/INDEX + TODO。4. **更新 TODO.md**：PIPE-CORE_v2 四項 OP `🟡/⬜` → `✅`，依框架 §2.5 移入頂部 ✅ 已完成表格（落地 Hash 待 baron 回填），索引標 ✅。5. 驗收：`baton/` 無 PIPE-CORE 殘留 + 正式目錄齊全。6. **嚴禁** `git commit`/`push`（CLAUDE.md §1.3，baron 手動）。 |

---

## §9 Open Questions

無。（plan v2 §7 之 4 項 Open Questions——合約模組位置（已採 `pipelines/contracts.py`）/Checkpoint 載體（骨架 JSON 樁介面）/P4 派發機制（骨架同步樁、BackgroundTasks 屬 RAG-ASYNC）/NullStrategy 哨兵——皆已標推薦答案，由 baron 於各 OP 執行前最終拍板；本 tasks 階段不另增規劃層問題。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-CORE 三層解耦空骨架的 OP-N 執行階段拆分與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 OP 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 `baton/` → `executions/` 四份 OP 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動既有業務代碼；嚴禁附具體五路策略實作；Orchestrator 禁 doc_type 分支；嚴禁自動 git commit/push；OP-1~OP-3 報告嚴禁移動、僅 OP-4 收官歸檔 |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；三層解耦/四合約規格唯一源在 plan v2 §2 與 PIPE-SPEC §1.1；工作流規格一律引用 WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-02)：初版拆分（檔名隨 plan 對齊帶 `_v2` 版號），依 plan v2 §2（U1–U7）/ §6 拆為 4 個 OP——OP-1 合約與狀態層（contracts 四合約 + context）/ OP-2 工廠與策略基類（DocumentStrategy ABC + NullStrategy + 工廠降級）/ OP-3 Orchestrator 四 Phase DAG（宣告式 + 交接點驗證 + 掛點 + shadow 貫穿、grep doc_type== 0 命中）/ OP-4 Checkout 收官；不拆 Git commit、不給 commit 建議；OP-2/OP-3 修改 `tests/test_pipe_core.py` 前 `.bak` 備份；同步 §0.5 成果盤點與 §7 不可動清單。
