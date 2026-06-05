# PIPE-RESUME v9 影子整合與規格同步 — Tasks

> 本文件為 PIPE-RESUME **v9 後續整合批次**的 Commit 拆分清單（階段 2 產出、03:35 精修版）。
> 依 `.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 至 **v11**）產出，含 7 個 Commit（C1 三文件規格同步 + C2-C5 實作 + C6 測試 + C7 Checkout）。
> **批次區別**：本批次 commit 代號 C1-C7 為 v9 整合內部序，**與原 PIPE-RESUME C1-C7（已收官、四 Phase 落地）區別**——本批次處理 plan v9 項3（P1 影子後綴）/ 項4（ctx.raw_metadata 穿線）/ 項5（P3 constraints）/ 項6（治理）+ v10（P2 步序 ①②互換）+ v11（表格保留明文）。
> 工作流類別：**BE-Refactor**（強制 logging SOP + database SOP 一致性核查）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （測試追加於既有 `tests/test_resume_pipeline.py`）|
| **修改檔案** | 7 個 | C1：`PIPE-RESUME plan_v1`／`PIPE_…plan_v10.md`（母 plan）／`PIPE-SPEC_…specification.md`；C2：`pipelines/context.py`＋`pipelines/resume_pipeline.py`(P1)；C3：`pipelines/resume_pipeline.py`(P2)；C4：`pipelines/resume_pipeline.py`(P3)；C5：`web_server.py`(影子區塊)；C6：`tests/test_resume_pipeline.py` |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 7 個 | C1 → C2 → C3 → C4 → C5 → C6 → C7（Checkout）|
| **baton 歸檔** | 1 次 | C7 收官：`mv` plan_v1（保留 `_v1`）→ `plans/` + tasks/C1-C7 報告 → `tasks/`/`executions/` + `git add`（母 plan/PIPE-SPEC 為其本身既有 baton 歸檔位、C1 就地改、不隨本批次 mv）|

---

## §1 TL;DR（概要）

- **挑戰**：plan §99.2 v9-v11 拍板的設計（項3 P1 影子標題 (測試) 後綴 / 項4 `ctx.raw_metadata` 整包 metadata 穿線取代 `_raw_meta` 死路與 custom_metadata-in-Spec / 項5 P3 業務 `constraints` 逐路注入 / v10 P2 步序 ①做摘要→②LCC 互換 / v11 表格保留明文）為待落地；且須先同步上游凍結合約規格書方可動共用基建 `PipelineContext`。
- **解法**：7 原子 Commit——`C1 — Sync System Specs（同步三份核心規格文件）` → `C2 — P1 + Context（raw_metadata 基建欄 + run_phase1 寫入 + 影子後綴）` → `C3 — P2 步序與讀取對齊（①②互換 + 改讀 raw_metadata）` → `C4 — P3 Business Constraints（履歷業務規則注入）` → `C5 — Shadow DB Fidelity（影子寫庫讀 raw_metadata 保真）` → `C6 — Unit Tests（v9 契約單元測試）` → `C7 — Checkout（收官歸檔）`。
- **影響範圍**：C1 三份規格文件（純文件）+ 新核心 `pipelines/`（context/resume_pipeline）+ 影子 scaffold `web_server.py` 之 C8-hotfix 區塊；A 軌 `run_pipeline` 本體、舊 `pipeline_core.py`、既有 processors、凍結合約 `contracts.py` 零改動。
- **不可動清單**：見 §7

> **註：P4 無 v9 變更**——原 `run_phase4`（C5 `e8a7429`）已落地、本批次不改 P4；故無「實作 P4」commit；項4 的 DB 寫入消費端在影子 scaffold（C5），非 Phase。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `PIPE-RESUME plan_v1` | §99.2 已至 **v11**（設計定稿）| 為來源真理；C1 確認 §5 引用一致、登記與母檔互引 |
| `PIPE_…plan_v10.md`（母 plan）| §8.5 五路 + 共用基建總綱 | 未含 v9 整合（raw_metadata 穿線 / P3 翻譯隔離 / Phase2 摘要先行 / C7-C8 史 / Flip Cleanup）|
| `PIPE-SPEC_…specification.md` | §1.1 四凍結合約、§0.3 PipelineContext 狀態層 | 同上：未含 `raw_metadata` 規格與 P3 翻譯隔離原則 |
| `pipelines/context.py:34` | `PipelineContext`（…pdf_path/owner_id + 4 specs）| **無 `raw_metadata` 欄**（項4 死路根因）|
| `pipelines/resume_pipeline.py:165` | P1 `self._raw_meta = {...}`（實例暫存）| `Orchestrator.run` 後撈不到；無影子標題後綴 |
| `pipelines/resume_pipeline.py:290-293` | P2 步序 ①LCC→②摘要、讀 `self._raw_meta` | v10 應 ①摘要→②LCC；改讀 `ctx.raw_metadata` |
| `pipelines/resume_pipeline.py:433` | P3 `InjectionContext(…doc_type)`（無 constraints）| 項5 業務規則缺入口 |
| `web_server.py:648`（C8-hotfix 區塊）| 影子寫庫 `meta_dict`＝最小 | 未讀 `ctx.raw_metadata` → metadata_json 保真不足 |

---

## §3 觀察問題

### 問題 #1：P1 metadata 穿線斷鏈（項4）
- **證據**：`resume_pipeline.py:165` 寫 `self._raw_meta`（實例）；`Orchestrator.run`（`orchestrator.py:134`）只回 ctx → 影子寫庫拿不到 phone/email/domain 與完整 metadata。
- **影響**：DB `metadata_json` 保真度低於 A 軌 `upsert_paper(self._metadata)`。

### 問題 #2：影子論文前端無法肉眼區分（項3）
- **證據**：C8-hotfix 寫 `original_filename="…(測試)"` 但 `title=candidate_name`（無後綴）；前端列表顯示 `p.title`（`paper_manager._to_dict`）→ 影子不帶 (測試)。

### 問題 #3：履歷翻譯業務風格無客製入口（項5）；P2 步序未跨路統一（v10）
- **證據**：`run_phase3:433` 無 `constraints`；`run_phase2:290` LCC-first（v10 應摘要-first、跨路統一）。

---

## §4 設計方案

### §4.1 C1 — Sync System Specs（三份規格文件同步、純文件）
同步 plan_v1（確認定稿）+ 母 plan v10 + PIPE-SPEC：寫入 C7/C8-hotfix 歷史、P1 影子後綴 + Flip Cleanup、`ctx.raw_metadata` 穿線設計（定義 PipelineContext 基建欄、承載完整履歷及論文元數據、對齊 A 軌保真）、P3 constraints 翻譯自主隔離原則、Phase 2 流程異動（摘要先行）、Revision + §7.1 Cleanup。為 C2 動共用基建鋪路。

### §4.2 C2 — P1 + Context
`context.py` 加 `raw_metadata: Dict[str,Any]={}`；`run_phase1` 寫整包 metadata 至 `ctx.raw_metadata`（過渡期保留 `self._raw_meta` 供 P2 不破），`_shadow` 時 title 加綴 `(測試)`。

### §4.3 C3 — P2 步序與讀取對齊
`run_phase2` 步序 ①摘要→②LCC（v10 互換、功能等價）；改讀 `ctx.raw_metadata.get("domain")`、廢 `self._raw_meta`。

### §4.4 C4 — P3 Business Constraints
`run_phase3` 建 `InjectionContext(..., constraints=_RESUME_CONSTRAINTS)`（公司/產品名保留、Email/電話/URL 原樣、技能詞英文、中英對照）。

### §4.5 C5 — Shadow DB Fidelity
`web_server.py` C8-hotfix 影子寫庫改讀 `ctx.raw_metadata` 組 `metadata_json`（對齊 A 軌保真）；title 沿用 P1 已加綴值。

### §4.6 C6 — Unit Tests
`tests/test_resume_pipeline.py` 追加 v9 契約測試（raw_metadata 穿線 / 影子標題 / P2 步序 / P3 constraints）。

### §4.7 C7 — Checkout / 收官歸檔
Conformance 驗收 + baton plan_v1（保留 `_v1`）/tasks/C1-C7 報告一次性歸檔。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C2 改 `PipelineContext`（共用基建）破壞既有測試 | 🟡 中 | `raw_metadata` 預設 `{}`、前向相容；跑 test_pipe_core/scaffold 防 Regression |
| C2/C3 拆分致 P2 讀 self._raw_meta 中斷 | 🟡 中 | C2 過渡期 P1 雙寫（ctx.raw_metadata + self._raw_meta）；C3 才切換讀取並廢實例暫存 → 每 commit 獨立可運作 |
| P2 步序互換改變輸出 | 🟢 低 | LCC/摘要互不依賴（grep 證）、功能等價；測試斷言 lcc/abstract 不變 |
| 影子標題後綴污染內容/Golden Diff | 🟢 低 | title 不入內容（P3 讀 .md full_text）；測試斷言 final_zh 無 (測試) |
| C5 動 web_server（業務代碼） | 🟡 中 | 僅改 C8-hotfix 影子區塊（shadow scaffold 授權例外、A 軌 byte 不動）；改前 .bak |
| database SOP：影子寫庫含 LLM/交易 | 🟢 低 | 僅呼叫既有 `upsert_paper`（內部自管交易）、無新裸 commit |

---

## §6 測試計畫

### §6.0 既有測試底線（每 Commit 後跑）
```bash
venv/bin/python -m pytest tests/ -q   # 防 Regression（既存 test_settings_log_format_default_auto 為環境性、非本批次）
```

### §6.1 C1 驗收（三文件同步）
```bash
grep -nE "raw_metadata|翻譯策略隔離|constraints|C7-hotfix|C8-hotfix|摘要先行|Flip Cleanup" .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md  # 期望：命中
grep -nE "raw_metadata|C7-hotfix|C8-hotfix|Cleanup|摘要先行" .claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md  # 期望：命中
```

### §6.2 C2 驗收（context.raw_metadata + P1 影子後綴）
```bash
grep -nE "raw_metadata" pipelines/context.py  # 期望：欄位命中
grep -nE "ctx.raw_metadata|endswith\('_shadow'\)|\(測試\)" pipelines/resume_pipeline.py  # 期望：P1 寫入 + 後綴
pytest tests/test_resume_pipeline.py tests/test_pipe_core.py -q
```

### §6.3 C3 驗收（P2 步序 + 讀取）
```bash
grep -nE "ctx.raw_metadata.get|_make_summary.*\n.*normalize_to_lcc|步驟①.*摘要" pipelines/resume_pipeline.py  # 期望：摘要先行 + 讀 ctx
grep -nE "self\._raw_meta" pipelines/resume_pipeline.py  # 期望：0（或僅 __init__ 相容）
pytest tests/test_resume_pipeline.py -k "phase2" -q
```

### §6.4 C4 驗收（P3 constraints）
```bash
grep -nE "constraints=" pipelines/resume_pipeline.py  # 期望：run_phase3 命中
pytest tests/test_resume_pipeline.py -k "phase3 or constraint" -q
```

### §6.5 C5 驗收（影子寫庫保真）
```bash
grep -nE "ctx.raw_metadata" web_server.py  # 期望：C8-hotfix 區塊讀取命中
grep -nE "\.commit\(\)" web_server.py | grep -v "with .*session.*begin\(\)"  # 期望：本次新增區塊無裸 commit
```

### §6.6 C6 驗收（測試套件）
```bash
pytest tests/test_resume_pipeline.py -v  # 期望：含 v9 新測試全綠
```

### §6.7 SOP 一致性核查（C2-C5 落地前強制、貼執行報告）
```bash
grep -nE "logger\.error|logger\.exception|traceback.format_exc" pipelines/resume_pipeline.py pipelines/context.py web_server.py  # error 須 exc_info=True
grep -nE "\.commit\(\)" pipelines/resume_pipeline.py pipelines/context.py | grep -v "with .*session.*begin\(\)"  # 無裸 commit
```

---

## §7 不可動清單

- [ ] **舊單體 `pipeline_core.py`**（A 軌 resume branch）— 100% 不動
- [ ] **A 軌 `run_pipeline`（web_server.py）本體** — byte 不動（C5 僅改 C8-hotfix 影子區塊）
- [ ] `paper_manager.py` / `processor/*.py`（resume_processor/rag_processor/translator/glossary_extractor/domain_normalizer/metadata_extractor）— 僅**呼叫**、零改動
- [ ] `pipelines/contracts.py` 四凍結合約 — **不改**（項4 走 `ctx.raw_metadata` 非合約欄）
- [ ] `pipelines/base_strategy.py` / `factory.py` / `orchestrator.py` — 不動（C2 僅加 context 欄）
- [ ] `models.py` / `db.py` — 不動（DB 寫入委派既有 `upsert_paper`）
- [ ] `run_phase4`（P4）— **本批次不改**（無 v9 變更）
- [ ] 既有 `list_papers` / `get_paper` / `delete_paper` API 與前端 — 零改動
- [ ] 主 repo 目錄 — 嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C1 — Sync System Specs（同步三份核心規格文件）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md` / `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（母 plan）/ `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（純文件、就地改）|
| **安全性** | 🟢 高 — 純規格文件、零 runtime |
| **可逆性** | 🟢 高 — `git revert C1` |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置（為 C2 動共用基建鋪路）|
| **具體實作細節** | 1) **plan_v1**：已至 §99.2 v11（六項 + v10 P2 步序 + v11 表格保留），為來源真理——本 commit 確認 §5 規格依據引用一致、與母檔互引登記（內容已定稿、僅微調/no-op）。2) **PIPE-SPEC §1.1 / §0.3**：登記 `PipelineContext.raw_metadata: Dict[str,Any]={}`「DB 持久化用整包原始 metadata 旁路欄」（與四凍結結構化合約分離、承載完整履歷及論文元數據、對齊 A 軌 `upsert_paper(self._metadata)` 保真）；P3 章節明訂「**翻譯策略隔離原則**」（各路 `run_phase3` 自建 `InjectionContext.constraints` 逐路注入共用 `Translator`、業務規則由策略擁有、不另維護完整 prompt、不污染核心）。3) **母 plan v10 §8.5 / Revision**：登記 C7-hotfix（`from pipelines import resume_pipeline`）、C8-hotfix（影子 `upsert_paper`）歷史；**Phase 2 流程異動（摘要先行 → LCC 雙參分類 → 術語自癒 → DEEP_THINK 翻摘要）**；**P1 影子標題後綴規格 + Flip Cleanup 待辦「移除 P1 影子後綴」**；標 `raw_metadata`/翻譯隔離為 successor pipelines 共用參照。4) 三檔以章節 Revision 或 `<!-- === [PIPE-RESUME v9 …] === -->` 標記變更區。**嚴禁改 Python 業務代碼。** |

### C2 — P1 + Context（raw_metadata 基建欄 + run_phase1 寫入 + 影子後綴）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/context.py`（加 `raw_metadata` 欄）+ `pipelines/resume_pipeline.py`（run_phase1）+ 改前各 `.bak` |
| **安全性** | 🟡 中 — 改共用 `PipelineContext`（前向相容預設 `{}`）|
| **可逆性** | 🟢 高 — `git revert C2` |
| **驗收 grep 條件** | §6.2 + §6.7 |
| **依賴關係** | C1（規格已同步）|
| **具體實作細節** | 1) `context.py`：`PipelineContext` 加 `raw_metadata: Dict[str, Any] = {}`（`# === [PIPE-RESUME v9 C2 START/END] ===` 包裹、緊接 pdf_path/owner_id）。2) `run_phase1`：將 Stage A 整包 `meta`（含 candidate_name/domain/phone/email + confidence/source）寫 `ctx.raw_metadata`；**過渡期保留 `self._raw_meta = {...}` 雙寫**（讓 C2 後 P2 仍可運作、獨立可逆）；`title = self._resolve_title(...)` 後 **`if ctx.paper_id.endswith('_shadow')` → `title = f"{title} (測試)"`**。3) `# === [PIPE-RESUME v9 C2 START/END] ===` 包裹。4) logging SOP：無新 logger.error、無 DB。|

### C3 — P2 步序與讀取對齊（①②互換 + 改讀 raw_metadata）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（run_phase2）+ 改前 `.bak` |
| **安全性** | 🟢 高 — 步序互換功能等價、改讀來源 |
| **可逆性** | 🟢 高 — `git revert C3` |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | C2（`ctx.raw_metadata` 已填）|
| **具體實作細節** | 1) `run_phase2` 步序：**①`_make_summary(full_text)`→abstract 前置 → ②`normalize_to_lcc(...)`→lcc**（v10 互換；兩者互不依賴、輸出不變）。2) `raw_domain` 改讀 `ctx.raw_metadata.get("domain")`（取代 `self._raw_meta`）。3) 廢 `self._raw_meta`（C2 雙寫的實例副本可移除、以 ctx 為準）。4) `# === [PIPE-RESUME v9 C3 START/END] ===` 包裹。|

### C4 — P3 Business Constraints（履歷業務規則注入）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（run_phase3）+ 改前 `.bak` |
| **安全性** | 🟢 高 — 純加翻譯規則、共用 Translator 不動 |
| **可逆性** | 🟢 高 — `git revert C4` |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | C2（run_phase3 既有）|
| **具體實作細節** | 1) 新增模組常數 `_RESUME_CONSTRAINTS = ["公司名稱、產品名稱保留原文不翻","Email／電話／URL 原樣保留","專業技能詞（Python/Docker 等）保留英文",（中英對照/期刊專利例外等）]`。2) `run_phase3` 建 `InjectionContext(..., constraints=_RESUME_CONSTRAINTS)`；`Translator._build_system_prompt ⑤`（`translator.py:134-137`）自動貼「【額外譯文約束】」、共用 Translator 零改。3) `# === [PIPE-RESUME v9 C4 START/END] ===` 包裹。|

### C5 — Shadow DB Fidelity（影子寫庫讀 raw_metadata 保真）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（`run_pipeline_shadow` C8-hotfix 區塊）+ 改前 `.bak` |
| **安全性** | 🟡 中 — 動 web_server（限影子 scaffold 區塊、A 軌不動）|
| **可逆性** | 🟢 高 — `git revert C5`；`.bak` 還原 |
| **驗收 grep 條件** | §6.5 + §6.7 |
| **依賴關係** | C2（`ctx.raw_metadata` 已填）|
| **具體實作細節** | 1) C8-hotfix 影子寫庫區塊：`meta_dict` 改由 `ctx.raw_metadata` 組裝（整包寫 DB `metadata_json`、對齊 A 軌保真）；`title` 沿用 P1 已加綴 `ctx.ingestion.title`（已含 (測試)）。2) `ctx.raw_metadata` 為空時 fallback 既有最小 meta_dict（守衛）。3) `# === [PIPE-RESUME v9 C5 START/END] ===`（疊於 C8-hotfix 區塊內）。4) database SOP：僅呼叫既有 `upsert_paper`、無新裸 commit/session.begin。|

### C6 — Unit Tests（v9 契約單元測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_resume_pipeline.py`（追加 v9 測試）|
| **安全性** | 🟢 高 — 純測試、mock 隔離 |
| **可逆性** | 🟢 高 — `git revert C6` |
| **驗收 grep 條件** | §6.6 |
| **依賴關係** | C2-C5 |
| **具體實作細節** | 追加（`# === [PIPE-RESUME v9 C6 START/END] ===`）：① P1 寫 `ctx.raw_metadata`（含 phone/email/domain）；② `_shadow` paper_id → title 帶 (測試)、非 shadow 不帶、且 final_zh 內容無 (測試)；③ P2 步序摘要先行 + 改讀 `ctx.raw_metadata` 後 lcc/domain 仍正確；④ P3 `InjectionContext.constraints` 非空含履歷規則（capture translate ctx）；⑤ C5 影子寫庫以 `ctx.raw_metadata` 組 meta（mock upsert_paper 斷言傳入）。全程 mock LLM/Embedding。|

### C7 — Checkout / 收官歸檔

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`；`mv` baton plan_v1（保留 `_v1`）→ `plans/`、tasks/C1-C7 報告 → `tasks/`/`executions/`；無業務代碼 |
| **安全性** | 🟢 高 — 純歸檔 |
| **可逆性** | 🟢 高 — mv 可逆 |
| **驗收 grep 條件** | Conformance：plan v9-v11 / §6 grep+pytest / 不可動清單 git 證據 + §6.7 SOP 核查 |
| **依賴關係** | C1-C6 全 ship |
| **具體實作細節** | 1) Conformance 三維度驗收 + SOP 核查貼 grep。2) TODO.md：✅ 完成新增「PIPE-RESUME v9 影子整合」C1-C7 表（Hash 待回填）+ 移除 active + 索引 + 歷史 Hash 自癒。3) 一次性 `mv` baton（plan_v1〔保留 `_v1`〕/tasks/C1-C7 報告）→ plans//tasks//executions/ + git add（**母 plan/PIPE-SPEC 為其本身既有 baton 歸檔位、C1 就地改、不隨本批次 mv**）。4) 確認 baton/ 無本批次殘留。5) 嚴禁自發 commit/push（msg 寫 /tmp）。|

---

## §9 Open Questions

| 項 | 狀態 |
|---|---|
| commit 代號 C1-C7 與原 PIPE-RESUME C1-C7 重號 | **已知、可接受**：task 名「PIPE-RESUME v9 影子整合」+ 日期 2026-06-05 區隔；TODO 完成表分列；hash 回填以 task 標題辨識。若 baron 偏好獨立代號（如 v9-C1）執行前可調。 |
| C1 改 PIPE-SPEC / 母 plan / plan_v1 | **baron 授權**：本批次 C1 明確指定改此 3 檔（plan→Task 第一個 commit 同步上游、見 plan v9 §7.1）。 |
| P4 無 v9 變更 | **本批次不含「實作 P4」commit**（原 `run_phase4` 已落地、無修改項）。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-RESUME v9 整合的原子 Commit 拆分與實作細節，作為執行期唯一指針 |
| **用途** | 供 baron 審查、Claude Code 按序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 v9 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | C1 限改 3 份規格文件；C2-C5 限改 pipelines/ + web_server 影子區塊 + tests；嚴禁改舊單體/A 軌本體/凍結合約/P4；嚴禁自動 commit/push；BE-Refactor 落地前強制 §6.7 SOP 核查 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務收官歸檔，經 baron 同意移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收；不重複 plan 設計脈絡、不重複 CLAUDE.md 全域硬規則 |

### §99.2 Revision 歷程

- v2 (2026-06-05)：03:35 精修——C1 由「同步 2 檔」擴為「同步 **3 檔**（含 PIPE-RESUME plan_v1）」並明列 Phase 2 流程異動（摘要先行）；commit 重編為 7 個（C2 P1+Context / C3 P2 步序與讀取 / C4 P3 / C5 影子寫庫保真 / C6 測試 / C7 Checkout，Phase 對齊 baron 例示、P4 無變更不立 commit）；對齊 plan §99.2 v11。
- v1 (2026-06-05)：初版拆分（6 Commit、C1 同步 2 檔）。
