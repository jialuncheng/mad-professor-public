# RAG-ASYNC P4 RAG 索引共用真理源與全 P2 Section Summary — Tasks

> 本文件為 RAG-ASYNC 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-07_RAG-ASYNC_P4_RAG索引共用真理源與全P2摘要_plan_v2.md` 計畫產出，含 **7 個 Commit**（C1 規格同步 → C2–C6 代碼 → C7 Checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動 → 直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `processor/rag_indexer.py`（B 軌自有 RAG 索引引擎、全重寫零 import rag_processor）/ `tests/test_rag_indexer.py`（新模組單元 + ④ conformance 測試） |
| **修改檔案** | 5 個 | `pipelines/contracts.py`（GlossaryReadySpec：section_summaries 取代 chapter_summaries）/ `pipelines/resume_pipeline.py`（run_phase2 統一六步 + run_phase3 旁路封存 section 結構 + run_phase4 改呼新模組、砍 rag_processor import）/ `tests/test_resume_pipeline.py`（對齊新合約 + P2/P4 新測試）/ `baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（§U2/§U6 同步）/ `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（§1.1②/§1.4/§1.3 同步、含修 P3 doc-drift）；各既有檔修改前產 `.bak` 入 `archive/` |
| **目錄初始化** | 0 個 | 無（`processor/` / `tests/` 既存） |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 7 個 | C1（規格文件同步）→ C2（合約欄位）→ C3（分塊與 size-cap）→ C4（向量落庫與 ④ 合約）→ C5（P2 統一六步）→ C6（P3 旁路與 P4 接線）→ C7（Checkout 收官） |
| **baton 歸檔** | 1 次 | C7 Checkout 一次性 `mv` baton/（plan_v1+v2 / tasks / C1–C7 報告）至 `plans/` `tasks/` `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：B 軌 P4 對 13358 字元履歷只切 1 chunk（`est_tokens=11997`、RAG 召回崩潰）；根因＝切塊器只切 `#`、B 軌 P4 餵 reading-view `final_zh.md`（section 皆 `##`、唯一 `#` 為 META header）。並偏離 PIPE-SPEC §1.4 / 母 plan R4.3、A 軌切塊無 size-cap（書籍大章潛在弱點）。
- **解法**：拆 7 個原子 commit——**C1 — Spec Sync（規格文件同步）** 先對齊母 plan v10 + PIPE-SPEC；**C2 — Contract（合約欄位 section_summaries）**；**C3 — Chunk Build（Strategy B 分塊與 size-cap 子切）** 與 **C4 — Vector Persist（向量落庫與 ④ 合約 conformance）** 建 B 軌自有 `rag_indexer.py`（零 import rag_processor）；**C5 — P2 Six-Step（P2 統一六步 section_summaries 產出）**；**C6 — Wire P4（P3 旁路封存與 P4 改呼新模組）**；**C7 — Checkout（收官·Conformance 驗收與一次性歸檔）**。
- **影響範圍**：1 規格同步 commit（DOC、零 Python）+ 5 代碼 commit（新增 1 模組 + 1 測試檔、修 contracts/resume_pipeline/test）+ 1 Checkout；A 軌 `rag_processor.py`/`pipeline_core.py`/`rag_retriever.py` 零改動。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/resume_pipeline.py` | `L72-73` import RagProcessor；`run_phase4 L799-` 餵 `ctx.bilingual.final_zh_path` 給 `_create_vector_store` | B 軌咬 A 軌 + 餵閱讀 md → chunks=1；run_phase2 為四步（無 section_summaries 產出） |
| `processor/rag_processor.py` | `L231-233` `MarkdownHeaderTextSplitter([("#","Header")])` header-only、無 size-cap | A 軌專屬；B 軌須全重寫等價物、不沿用；書籍大章無 cap 弱點 |
| `pipelines/contracts.py` | `GlossaryReadySpec L51` `chapter_summaries:Optional[List[str]]=None`（Book 專用） | 無五路通用節點摘要欄；List 不對位巢狀樹 |
| `processor/rag_indexer.py` | 不存在 | 待新建 B 軌自有索引引擎（Strategy B + size-cap + filter + embed + FAISS + paper_chunks + index_meta） |
| `baton/…PIPE-SPEC…specification.md` | §1.3 L133 resume P3「100% Bypass 一鍵」；§1.4 物理分塊 header-only | doc-drift（P3 早改逐 section）；chunk 來源/格式未對齊 plan v2 |
| `baton/…PIPE…plan_v10.md` | §U2 衍生語境內聚 P2；§U6 P1-P3 零 Embedding | 未載明 section summary 歸 P2 統一六步、size-cap |

---

## §3 觀察問題

### 問題 #1：B 軌 P4 chunks=1 退化
- **證據**：`file:///pipelines/resume_pipeline.py#L833`（餵 `final_zh_path` 閱讀 md）+ `file:///processor/rag_processor.py#L231`（只切 `#`）
- **影響**：整份履歷塌成 1 個 11997-token chunk，RAG 召回粒度崩潰、問答品質掛掉。

### 問題 #2：B 軌 P4 咬 A 軌 rag_processor
- **證據**：`file:///pipelines/resume_pipeline.py#L73`（`from processor.rag_processor import RagProcessor`）
- **影響**：B 軌未與即將棄用之 A 軌切割；Flip 時拆耦合困難；違 P1-P4 獨立原則。

### 問題 #3：A 軌切塊無 size-cap（書籍潛在弱點）
- **證據**：`file:///processor/rag_processor.py#L231-233`（無 `RecursiveCharacterTextSplitter` / `chunk_size`）
- **影響**：書籍一章一個 `#` → 超大 chunk 爆 embedding token 上限、召回粒度差（per-chapter 版 chunks=1）。

### 問題 #4：PIPE-SPEC §1.3 P3 doc-drift
- **證據**：`PIPE-SPEC §1.3 L133`「100% Bypass 一鍵」vs RESUME-P3 落地逐 section 翻譯
- **影響**：規格與實作不符，未來路次讀 SPEC 被誤導。

---

## §4 設計方案

### §4.1 C1 — Spec Sync（規格文件同步）
依 plan v2 §2 U6，於 baton/ 就地修 母 plan v10（§U2 載明 section summary 歸 P2 統一六步；§U6 措辭修正「零 Embedding 呼叫；P2 summary 為 LLM 文字、批次有界、非致命、不阻 reading_ready」）+ PIPE-SPEC（§1.1② section_summaries 取代 chapter_summaries；§1.4 chunk Chapter Summary 來源＝P2、物理分塊＝P4 自生 + size-cap；§1.3 resume P3「100% Bypass」→「逐 heading section 翻譯 + 退化 fallback」）。各檔 §99.2 加 Revision。**零 Python。**

### §4.2 C2 — Contract（合約欄位 section_summaries）
`contracts.py` `GlossaryReadySpec`：移除 `chapter_summaries`、新增 `section_summaries: Optional[Dict[str, str]] = None`（key＝section_key/path、五路通用節點摘要、向後相容預設 None、`frozen/extra=forbid` 不破）。對齊既有測試（如有引用 chapter_summaries）。

### §4.3 C3 — Chunk Build（Strategy B 分塊與 size-cap 子切）
新建 `processor/rag_indexer.py`：依 section 結構 + section_summaries 生成 Strategy B chunk-md（`# {chunk_key}` + `Context:` + `Chapter Summary:`〔缺則略〕+ 內文）+ **Stage 2 size-cap 遞迴子切**（超 `EMBEDDING_MAX_TOKENS_PER_ITEM` 子切、每子塊重貼前綴）+ 自實作 `_is_chunk_meaningful` 等價門檻（≥3 + email/phone/url 保護）。**零 import rag_processor。** 本 commit 僅至「產出 chunk 文件清單」、不嵌入。

### §4.4 C4 — Vector Persist（向量落庫與 ④ 合約 conformance）
`rag_indexer.py` 補：chunk → `MarkdownHeaderTextSplitter`（切 #）→ filter → `EmbeddingModel` 批量 1 次 → `FAISS.save_local` → `paper_chunks` 批量（交易外、paper_db_id None 降級）→ `index_meta.json` → 交付 `RagDbSpec`。對齊凍結 ④ 格式；**conformance 測試**（B 軌 vector store ↔ `rag_retriever.load_vector_store` 讀取 + 召回）。

### §4.5 C5 — P2 Six-Step（P2 統一六步 section_summaries 產出）
`run_phase2` 由四步擴為六步：② 產章節摘要（原文、非 book 1 次批次、可併① ）+ ⑥ 以全文摘要引導一次性批次翻章節摘要 → 繁中 `section_summaries`（超 token 拆批）。三安全鎖：批次（非 N）/ 非致命（失敗留空、不阻 reading_ready、不拋）/ 可量測（`performance_metric` phase=P2 埋點）。交付擴充後 `GlossaryReadySpec`。

### §4.6 C6 — Wire P4（P3 旁路封存與 P4 改呼新模組）
`run_phase3`：於 ctx 旁路封存「譯後 section 結構」（title/level/content/children，供 P4 結構化輸入；不改 P3 既有翻譯輸出）。`run_phase4`：改呼 `rag_indexer`（消費 ctx 旁路結構 + section_summaries）、**移除 `from processor.rag_processor import RagProcessor`（L73）**、不再餵 final_zh.md；交付 RagDbSpec 不變。

### §4.7 C7 — Checkout（收官）
Conformance 三維度驗收（plan v2 §2 U1-U6 / §6 測試 / §7 不可動清單 git 證據）+ SOP 核查 + 提示詞稽核 + msg 完整性 → 全綠後 TODO 結案 + baton 一次性歸檔（plan_v1+v2 / tasks / C1-C7 報告 → plans//tasks//executions/）+ hash 全量自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| B 軌全重寫輸出與 `rag_retriever` 格式不相容 → 檢索壞 | 🔴 高 | C4 conformance 測試（B 軌 vector store 實餵 `load_vector_store` 驗讀取 + 召回）+ index_meta/paper_chunks 欄位斷言 |
| `chapter_summaries` 移除破壞既有測試/book 設計 | 🟡 中 | book pipeline 未落地、無 runtime 消費；C2 grep 全庫引用、同 commit 對齊測試 |
| size-cap 子切後 chunk 過碎或斷句 → 召回變差 | 🟡 中 | 子切走 token 預算 + 小 overlap（§7.2 待調）；E2E retrieve 分數分布核對 golden D3 |
| P2 六步使 reading_ready 延後過多 | 🟡 中 | ②⑥ 批次（~2 call、非 N）+ 安全鎖 3 埋點量測；超標再調批次門檻 |
| P3 旁路封存改動牽連 P3 翻譯輸出 | 🟡 中 | 旁路為附加式（不改既有翻譯/組裝路徑）；既有 resume 測試全綠為退化鐵證 |
| 改 A 軌共用基建誤觸 A 軌行為 | 🟢 低 | 只用 `config.EmbeddingModel`/ORM/FAISS（不改）；`rag_processor.py` 整檔零改動（§7） |

---

## §6 測試計畫

> 每個代碼 commit 完成後執行對應 grep + `venv/bin/python -m pytest tests/ -q` 不退化。

### §6.1 C1 驗收（規格同步）
```bash
# 母 plan v10：section summary 歸 P2 / size-cap 措辭
grep -n "section_summaries\|size-cap\|批次有界\|不阻 reading_ready" .claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md
# PIPE-SPEC：§1.1② section_summaries / §1.3 P3 doc-drift 已修
grep -n "section_summaries" .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md
grep -n "100% Bypass 一鍵" .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md   # 期望：resume 列已不再命中
# Revision 條目
grep -n "RAG-ASYNC" .claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md
```

### §6.2 C2 驗收（合約）
```bash
grep -n "section_summaries" pipelines/contracts.py          # 期望：有命中（Dict 型別）
grep -n "chapter_summaries" pipelines/contracts.py          # 期望：0 命中
venv/bin/python -m pytest tests/ -q
```

### §6.3 C3 驗收（分塊 + size-cap）
```bash
grep -n "rag_processor" processor/rag_indexer.py            # 期望：0 命中（零耦合）
grep -n "Chapter Summary\|Context:\|def .*chunk\|size" processor/rag_indexer.py   # 期望：Strategy B + size-cap 有命中
venv/bin/python -m pytest tests/test_rag_indexer.py -q      # 多塊 / 格式 / size-cap / 門檻
```

### §6.4 C4 驗收（落庫 + conformance）
```bash
grep -n "FAISS\|save_local\|index_meta\|paper_chunks\|RagDbSpec\|EmbeddingModel" processor/rag_indexer.py
grep -n "rag_processor" processor/rag_indexer.py            # 期望：仍 0 命中
venv/bin/python -m pytest tests/test_rag_indexer.py -q      # 含 conformance：vector store ↔ rag_retriever 讀取
```

### §6.5 C5 驗收（P2 六步）
```bash
grep -n "section_summaries\|performance_metric\|phase.*P2\|batch\|批次" pipelines/resume_pipeline.py
# SOP：logger.error 須 exc_info / 無裸 commit
grep -n "logger.error\|logger.exception\|traceback.format_exc" pipelines/resume_pipeline.py
grep -nE "\.commit\(\)" pipelines/resume_pipeline.py | grep -v "with .*session.*begin"   # 期望：無命中（合規）
venv/bin/python -m pytest tests/test_resume_pipeline.py -q
```

### §6.6 C6 驗收（P4 接線）
```bash
grep -n "rag_processor\|RagProcessor" pipelines/resume_pipeline.py   # 期望：0 命中（import 已砍）
grep -n "rag_indexer\|final_zh_path" pipelines/resume_pipeline.py    # 期望：run_phase4 改呼 rag_indexer、不餵 final_zh_path
venv/bin/python -m pytest tests/ -q                                  # 全套件不退化
```

---

## §7 不可動清單

- [ ] **`processor/rag_processor.py`** — 整檔零改動（A 軌 frozen-until-Flip、golden 參考實作）。
- [ ] **`rag_retriever.py`** — 檢索演算法 / `load_vector_store` / 距離策略零改動。
- [ ] **`vectors/` FAISS 格式 + `index_meta.json` schema + `models.PaperChunk` 表結構** — 凍結 ④ 輸出合約（C4 須 byte 相容）。
- [ ] **`config.EmbeddingModel`** — embedding 機制 / `EMBEDDING_MAX_TOKENS_PER_ITEM` 沿用不改。
- [ ] **`RagDbSpec` 既有欄位** + `frozen=True, extra="forbid"` — 不變。
- [ ] **A 軌 `pipeline_core.py`** 對 RAG 的調用 — 不動。
- [ ] **resume `run_phase1` / `run_phase3` 既有翻譯品質/結構/層級輸出** — 僅可附加旁路封存，不改既有翻譯/組裝。
- [ ] **`processor/translator.py` / `domain_normalizer.py` / `glossary_extractor.py`** — 既有簽名不變。
- [ ] **主 repo 目錄**（worktree 父目錄）— 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — Spec Sync（規格文件同步）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（+ `.bak`）/ `baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（+ `.bak`）；**零 Python**；`baton/` 暫存報告不列入 |
| **安全性** | 🟢 高 — 純文件、零 runtime |
| **可逆性** | 🟢 高 — `git revert C1` 或還原 `.bak` |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① 修改前 `cp` 兩檔至 `.claude-logs/archive/2026-06-08_RAG-ASYNC_C1_<檔名>.bak`。② 母 plan v10 §U2 補「RAG 所需 section summary 歸 P2 同步產（統一六步流程、衍生語境內聚）」；§U6 措辭改「零 Embedding 呼叫；P2 section summary 屬 LLM 文字生成（非 embedding）、批次有界、非致命、不阻 `reading_ready`」。③ PIPE-SPEC §1.1② 將 `chapter_summaries` 改 `section_summaries`（五路通用節點摘要、產出位置 P2）；§1.4 chunk 格式 `Chapter Summary` 來源註明 P2、「物理分塊」改「P4 依 P3 結構自生 RAG md + size-cap 二段子切」；§1.3 resume 列 P3「100% Bypass 一鍵」改「逐 heading section 翻譯 + 退化 fallback」。④ 兩檔 §99.2 各加一條 `RAG-ASYNC C1` Revision。⑤ 不得 `git add`/`mv`/`git commit`。產 `baton/2026-06-08_RAG-ASYNC_C1_執行.md`（template_execution、暫存）。 |

### C2 — Contract（合約欄位 section_summaries）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/contracts.py`（+ `.bak`）/ 如有引用則 `tests/test_pipe_core.py` 或 `tests/test_resume_pipeline.py`（+ `.bak`） |
| **安全性** | 🟢 高 — 欄位替換、向後相容預設 None |
| **可逆性** | 🟢 高 — `git revert C2` |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | C1（規格已定 section_summaries 語意） |
| **具體實作細節** | ① 修改前 `.bak`。② `GlossaryReadySpec` 移除 `chapter_summaries: Optional[List[str]] = None`、新增 `section_summaries: Optional[Dict[str, str]] = None`（docstring 註：五路通用節點摘要、key=section_key/path、P2 產出；Book 滾動章節摘要亦填此欄）。③ 全庫 `grep -rn chapter_summaries` 確認無其他消費（book 未落地）；若測試/型別有引用一併改 `section_summaries`。④ `frozen=True, extra="forbid"` 保持。⑤ `pytest tests/ -q` 綠。⑥ 不 commit；產 `baton/…_C2_執行.md`（暫存）。 |

### C3 — Chunk Build（Strategy B 分塊與 size-cap 子切）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `processor/rag_indexer.py` / 新增 `tests/test_rag_indexer.py` |
| **安全性** | 🟢 高 — 純新增檔、無既有調用 |
| **可逆性** | 🟢 高 — 刪新增檔即回滾 |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | C2（消費 section_summaries 結構） |
| **具體實作細節** | ① 新建 `processor/rag_indexer.py`，模組級 `# === [RAG-ASYNC] ===` 標記、**禁 import rag_processor**。② 函式 `build_chunk_markdown(sections, section_summaries, doc_type) -> list[str]`：DFS 走訪 section 樹，每節點 Stage 1 組 `# {chunk_key}\nContext: {doc_type} > {section_title}\nChapter Summary: {summary}\n\n{內文}`（summary 缺則省 Chapter Summary 行）；chunk_key 取 section 標題/path。③ Stage 2 size-cap：估內文 token（沿 MODEL-11 `len`-based 上界估），超 `EMBEDDING_MAX_TOKENS_PER_ITEM`（settings 引入、§7.2 可留 margin）→ 遞迴子切（保段落邊界 + 小 overlap）、每子塊重貼同一前綴。④ 自實作 `_is_chunk_meaningful` 等價（≥3 + email/phone/url regex 保留、純數字/markdown 噪聲過濾；不 import rag_processor 版）。⑤ 新建 `tests/test_rag_indexer.py`：多塊（N section→≈N chunk）/ Strategy B 格式 + summary 缺降級 / size-cap（大節點子切、子塊重貼前綴、小節點不觸發）/ 門檻 ≥3 + email 保留。⑥ 不 commit；產 `baton/…_C3_執行.md`（暫存）。 |

### C4 — Vector Persist（向量落庫與 ④ 合約 conformance）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `processor/rag_indexer.py`（補落庫段）/ `tests/test_rag_indexer.py`（補 conformance） |
| **安全性** | 🟡 中 — 觸及 FAISS/DB 寫；但走既有 EmbeddingModel/ORM、輸出對齊凍結格式 |
| **可逆性** | 🟢 高 — `git revert C4`（產物在沙箱輸出目錄） |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | C3（chunk 文件清單） |
| **具體實作細節** | ① `rag_indexer.py` 加 `index(...) -> RagDbSpec`：chunk-md → `MarkdownHeaderTextSplitter([("#","Header")])` 切 → 自實作 filter → `config.EmbeddingModel` 批量 1 次（task_type document）→ `FAISS.from_documents(distance_strategy=MAX_INNER_PRODUCT)` → `save_local(vectors_dir)` → `paper_chunks` 批量 `session.execute(insert(...))`（交易外 embedding、極短交易寫庫、`paper_db_id None` 優雅降級僅 FAISS+meta）→ 自寫 `index_meta.json`（model/dim/chunks_total）→ 回 `RagDbSpec`。② 嚴禁 import rag_processor（含 `write_index_meta_json`，自實作等價）。③ SOP：embedding/LLM 在 `session.begin()` 外；無裸 commit。④ `tests/test_rag_indexer.py` 補 **conformance**：以本模組產 vector store → `rag_retriever.load_vector_store` 讀回 + 一條 query 召回非空 + `index_meta.json` 鍵（model/dim/chunks_total）齊全 + `paper_db_id=None` 降級僅 FAISS。⑤ 不 commit；產 `baton/…_C4_執行.md`（暫存）。 |

### C5 — P2 Six-Step（P2 統一六步 section_summaries 產出）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（`run_phase2`，+ `.bak`）/ `tests/test_resume_pipeline.py`（+ `.bak`） |
| **安全性** | 🟡 中 — 主鏈 P2 加 LLM 步；批次有界 + 非致命降級 |
| **可逆性** | 🟢 高 — `git revert C5` |
| **驗收 grep 條件** | §6.5 |
| **依賴關係** | C2（section_summaries 欄位） |
| **具體實作細節** | ① `.bak`。② `run_phase2` 由四步擴六步、`# === [RAG-ASYNC C5] ===` 包裹新增段：步驟 ② 產章節摘要（原文；resume 為非 book → 對 section 樹**1 次批次** LLM、可與 ① 全文摘要併呼，回 `{section_key: 原文摘要}`、超 token 拆批）；步驟 ⑥ 以 ① 全文摘要 + ④ 凍結 Glossary 引導，**1 次批次**翻全部章節摘要為繁中 → `section_summaries`（超 token 拆批）。③ 三安全鎖：批次（非 N 次）；非致命（②/⑥ 任一失敗 → 該節點摘要留空、`logger.warning(exc_info=True, event=section_summary_fallback)`、不拋、不阻）；可量測（`logger.info(..., extra={'extra_fields':{'event':'performance_metric','phase':'P2','stage':'section_summary',...}})`）。④ 交付 `GlossaryReadySpec(section_summaries=…)`。⑤ SOP：LLM 在交易外、logger.error 須 exc_info。⑥ `tests/test_resume_pipeline.py` 加：run_phase2 產 section_summaries（key 對位 section）/ ②⑥ 批次（mock 計呼叫數驗非 N）/ 某 section 摘要拋例外 → 留空 + spec 仍交付 + 不拋。⑦ 不 commit；產 `baton/…_C5_執行.md`（暫存）。 |

### C6 — Wire P4（P3 旁路封存與 P4 改呼新模組）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（`run_phase3` 旁路封存 + `run_phase4` 改呼 + 砍 L73 import，+ `.bak`）/ `tests/test_resume_pipeline.py`（+ `.bak`） |
| **安全性** | 🟡 中 — 換 P4 核心；P3 旁路為附加式 |
| **可逆性** | 🟢 高 — `git revert C6` |
| **驗收 grep 條件** | §6.6 |
| **依賴關係** | C3 + C4（rag_indexer 完整）+ C5（section_summaries 已產） |
| **具體實作細節** | ① `.bak`。② `run_phase3`：於既有逐 section 翻譯流程**附加**封存「譯後 section 結構」（title/level/譯後 content/children）至 ctx 旁路屬性（如 `ctx.rag_sections` 或沿 `ctx.bilingual` 旁路欄；不改既有 final_zh/final_en 組裝與輸出），`# === [RAG-ASYNC C6] ===` 包裹。③ `run_phase4`：**移除 `from processor.rag_processor import RagProcessor`（L73）**；改呼 `processor.rag_indexer`：輸入＝ctx 旁路譯後 section 結構 + `ctx.glossary_ready.section_summaries` + doc_type；輸出 `RagDbSpec`（欄位不變）；不再讀 `ctx.bilingual.final_zh_path` 當切塊輸入。④ 保 `paper_db_id None` 降級語意。⑤ `tests/test_resume_pipeline.py` 改：run_phase4 路徑 grep 0 命中 rag_processor / mock 驗 chunks ≥ 20（多 section）/ P4 零 LLM（spy）/ RagDbSpec 交付。⑥ 全套件 `pytest tests/ -q` 不退化。⑦ 不 commit；產 `baton/…_C6_執行.md`（暫存）。 |

### C7 — Checkout（收官·Conformance 驗收與一次性歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（結案）/ `prompts/INDEX.md`（如需）/ baton→正式目錄一次性 `mv` + `git add`；**零業務代碼** |
| **安全性** | 🟢 高 — 驗收 + 文件歸檔 |
| **可逆性** | 🟢 高 — 文件搬移可逆 |
| **驗收 grep 條件** | 彙總 §6.1–§6.6 全綠 + 全套件 `pytest tests/ -q` |
| **依賴關係** | C1–C6 全數 ship |
| **具體實作細節** | ① Conformance 三維度：目標規格（plan v2 §2 U1-U6 對 C1-C6 報告逐項核）/ 測試（§6 grep + pytest 全綠、含 conformance）/ 不可動清單（§7 git 證據：rag_processor/rag_retriever/pipeline_core 零改）。② SOP 一致性核查（logging/database，貼 grep）。③ 提示詞稽核 `ls prompts | grep RAG-ASYNC`（plan/Tasks/C1-C6 run/Check 齊全）。④ msg 完整性。⑤ 全綠後：TODO 移入 ✅ 完成表（C1-C7 + hash 待回填、git log 自癒）+ 索引 ✅。⑥ baton 一次性 `mv`：plan_v1+v2 → `plans/`、tasks → `tasks/`、C1-C7 報告 → `executions/` + `git add`（清單寫入 C7 報告 §8）。⑦ 產 `baton/…_C7_執行.md`（先暫存、隨即隨 baton 同批歸檔）。⑧ **不自發 commit**；msg 草稿寫 `/tmp/RAG-ASYNC_C7_msg.txt`。 |

---

## §9 Open Questions

無。（plan v2 §7 七項設計議題 D1–D7 已全數定案；殘留僅 §7.2 待調實作參數〔size-cap token 門檻/overlap、批次拆批門檻〕，屬執行期微調、非設計分岔。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RAG-ASYNC 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 RAG-ASYNC executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（本 Tasks 階段）；C1 純規格同步零 Python；嚴禁自動 `git commit`/`git push`；baton 暫存、唯 C7 一次性歸檔 |
| **改版觸發條件** | plan v2 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡與 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-08)：依 plan v2（七定案 D1-D7）初版拆分。7 Commit：C1 規格同步（母 plan v10 + PIPE-SPEC、含修 §1.3 P3 doc-drift、零 Python）→ C2 合約 section_summaries 取代 chapter_summaries → C3 rag_indexer Strategy B 分塊 + size-cap 子切（零 import rag_processor）→ C4 向量落庫 + ④ conformance 測試 → C5 P2 統一六步 section_summaries（三安全鎖）→ C6 P3 旁路封存 + P4 改呼新模組（砍 rag_processor import）→ C7 Checkout 一次性 baton 歸檔。
