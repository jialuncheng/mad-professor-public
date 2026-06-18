# PIPE-SECTION-BASE 共用 section 機制抽取 — Tasks

> 本文件為 PIPE-SECTION-BASE 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-18_PIPE-SECTION-BASE_共用section機制抽取_plan_v1.md`（v2、§9 六 OQ 全 🟢）產出，含 5 個 Commit。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `pipelines/section_engine.py`（共用 section 引擎、pure-function）/ `tests/test_section_engine.py`（引擎單元 + base 層 key-changing 整合測試）|
| **修改檔案** | 1 個 | `pipelines/resume_pipeline.py`（私有 section helper → 呼叫共用引擎、行為等價；含 `.bak`）|
| **目錄初始化** | 0 個 | 無 |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 5 個 | C1（摘要機制）→ C2（翻譯與排版還原）→ C3（rag 旁路 + meta header 純格式化器）→ C4（測試）→ C5（Checkout 收官）|
| **baton 歸檔** | 1 次 | C5 收官：`mv` baton plan → `plans/` + tasks → `tasks/` + C1-C5 報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：resume_pipeline 的「遞迴標題樹走訪 → 逐節點摘要 / 並行翻譯 / 排版還原 / rag section 旁路」為私有，litedoc/academic/technical/book 將重複 copy（`_normalize_paragraph_breaks`/`_translate_whole` 已在 slides 重複一份）。
- **解法**：抽成 `pipelines/section_engine.py` 純函式共用引擎（translator/llm/doc_type 注入），resume 改消費；行為等價、既有 resume 測試鎖死（RESUME-PERF-1 C1 範式）。
- **影響範圍**：B 軌 `resume_pipeline.py` + 新增 `section_engine.py` / 測試；零 Schema / 零 final byte / 零 A 軌 / 零 contracts.py / 零 slide_pipeline 變動。
- **Commit 序**：
  - C1 — section_engine 骨架與摘要機制（標題樹走訪 + 批次摘要）
  - C2 — 翻譯與排版還原機制（render slots + 並行翻譯 + level 還原 + 退化 fallback）
  - C3 — rag 旁路與 meta header 純格式化器（Zero Schema Coupling）
  - C4 — 引擎單元測試與接縫整合測試（雙鎖）
  - C5 — Checkout 收官（Conformance + 歸檔）
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/resume_pipeline.py` | section 機制（摘要 L448-591 / render+還原 L746-1038 / rag 旁路 L811-848 / meta header L922）全私有 | 多路將重複 copy；機制與 resume 攝入層耦合在同一檔 |
| `pipelines/slide_pipeline.py` | `_normalize_paragraph_breaks` L431 / `_translate_whole` L937 | 與 resume 重複（已兩份）；本案不收編（§7、plan Q2）|
| `pipelines/section_engine.py` | 不存在 | 待新建為共用引擎 |

---

## §3 觀察問題

### 問題 #1：section 機制私有、多路重複
- **證據**：`file:///pipelines/resume_pipeline.py#L448`（_build_section_summaries）/ `file:///pipelines/slide_pipeline.py#L431`（_normalize_paragraph_breaks 重複）
- **影響**：litedoc 將成第三份；修補需多處同步、易 drift。

### 問題 #2：meta header 與 metadata 結構耦合
- **證據**：`file:///pipelines/resume_pipeline.py#L922`（_render_meta_header 讀 ctx.raw_metadata）
- **影響**：各文體欄位/語系差異大，直接讀 dict 使共用層綁死特定 schema（plan U3.1 須解耦為純格式化器）。

---

## §4 設計方案

> 全程**行為等價**抽取：每個 Run Commit 完成後，`pytest tests/test_resume_pipeline.py` 必須全綠（含 RAG-ASYNC-HOTFIX-1 key-changing 整合測試）= 鐵證。section_engine 全為 pure function、translator/llm/inj 由參數注入、引擎內零 doc_type 字面量。

### §4.1 C1 — section_engine 骨架與摘要機制
新建 `pipelines/section_engine.py`，抽出摘要 cluster 為純函式：`collect_summary_targets`（DFS 走標題樹、可吃任意子樹·U3.2）、`node_content_text`、`build_section_summaries`（llm 注入）、`generate_section_summaries`、`translate_section_summaries`、`parse_indexed`。resume 對應私有 helper 改 delegate 呼叫，原邏輯不改值。

### §4.2 C2 — 翻譯與排版還原機制
抽出 render/restore cluster：`collect_render_slots`（key=原文標題 path、level=遞迴深度）、`restore_sections_markdown`（ThreadPoolExecutor 並行 + 保序回填 + 單 unit 失敗退原文）、`translate_whole`、`t`、`normalize_paragraph_breaks`、`is_heading_degraded`+`flatten_sections`+`own_text_len`。並行/限流/異常隔離邏輯原樣搬移（RESUME-PERF-1）。

### §4.3 C3 — rag 旁路與 meta header 純格式化器
抽出 `collect_rag_sections`（summary_key=原文標題 path）、`single_container_sections`；`render_meta_header` **重構為純格式化器**（U3.1）：簽名 `render_meta_header(title, items: List[Tuple[str,str]], sep="：")`、引擎零讀 raw_metadata；resume 呼叫端負責從 `ctx.raw_metadata` 抽欄 + zh/en label 對照後傳 tuples。

### §4.4 C4 — 引擎單元測試與接縫整合測試
新建 `tests/test_section_engine.py`：DFS 走訪 / 批次摘要保序 / 並行翻譯 byte 等拍保序 + 限流 + 單 unit 失敗退原文 / heading 退化 fallback / meta header 純格式化 / **base 層 P2→P3→P4 key-changing 整合測試**（Mock Translator 改 key、斷言 summary_key 與 rag_sections 同基準、堵 RAG-ASYNC-HOTFIX-1 類退化）。

### §4.5 C5 — Checkout 收官
Conformance 五維度 + §7.2 整合測試驗收 + baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 抽取改到 final 輸出 / 召回 | 🟡 中 | 每 Run Commit 後 `pytest tests/test_resume_pipeline.py` 全綠（行為等價鐵證）|
| 接縫 key 位移 | 🟡 中 | §4 凍結 key=原文標題 path；C4 base 層 key-changing 測試 + resume 既有整合測試雙鎖 |
| 抽錯抽象（resume 形狀）| 🟡 中 | 介面參數化、引擎零 doc_type 字面量；依據對齊三類 consumer（plan §7）|
| scope creep 滲 slides | 🟢 低 | §7 不可動：slide_pipeline 全檔不碰 |
| SOP 違規 | 🟢 低 | 待抽區段 grep logger.error / 裸 commit 皆無命中（合規、§6.6）|

---

## §6 測試計畫

> 每個 Run Commit（C1-C3）完成後皆須跑 `pytest tests/test_resume_pipeline.py -q`（行為等價）+ 全套件基線（640 passed）。

### §6.1 C1 驗收
```bash
ls -la pipelines/section_engine.py                                   # 期望：存在
grep -nE "def collect_summary_targets|def build_section_summaries|def parse_indexed" pipelines/section_engine.py   # 期望：命中
grep -cE "_build_section_summaries|_collect_summary_targets|_parse_indexed" pipelines/resume_pipeline.py            # 期望：剩 delegate 呼叫、私有實作已移
grep -cE "section_engine" pipelines/resume_pipeline.py               # 期望：≥1（import + 呼叫）
pytest tests/test_resume_pipeline.py -q                              # 期望：全綠（行為等價）
```

### §6.2 C2 驗收
```bash
grep -nE "def collect_render_slots|def restore_sections_markdown|def normalize_paragraph_breaks|def is_heading_degraded|def translate_whole" pipelines/section_engine.py   # 期望：命中
grep -n "ThreadPoolExecutor\|LLM_MAX_CONCURRENT" pipelines/section_engine.py   # 期望：並行/限流邏輯已搬入
grep -n "min(2 + \|min(2+" pipelines/section_engine.py               # 期望：level=遞迴深度（HEADING-HOTFIX-1）保留
pytest tests/test_resume_pipeline.py -q                              # 期望：全綠
```

### §6.3 C3 驗收
```bash
grep -nE "def collect_rag_sections|def render_meta_header|def single_container_sections" pipelines/section_engine.py   # 期望：命中
grep -nE "def render_meta_header\(.*items: *List\[Tuple" pipelines/section_engine.py   # 期望：純格式化器簽名（收 tuples、U3.1）
grep -c "raw_metadata" pipelines/section_engine.py                   # 期望：0（引擎零讀 raw_metadata、Zero Schema Coupling）
grep -n "summary_key" pipelines/section_engine.py                    # 期望：summary_key=原文標題 path（接縫基準）
pytest tests/test_resume_pipeline.py -q                              # 期望：全綠
```

### §6.4 C4 驗收
```bash
ls -la tests/test_section_engine.py                                  # 期望：存在
grep -ciE "key.?chang|不位移|same.?baseline|summary_key" tests/test_section_engine.py   # 期望：≥1（接縫不變式測試）
pytest tests/test_section_engine.py -v                               # 期望：全綠
pytest tests/ -q                                                     # 期望：全套件基線（≥640 passed + 新增）
```

### §6.5 C5（Checkout）驗收
```bash
pytest tests/ -q                                                     # 期望：基線維持
ls .claude-logs/baton/ | grep -i PIPE-SECTION-BASE && echo "❌殘留" || echo "✅ baton 已清空"
git status -s | grep -E "executions/|plans/|tasks/"                  # 期望：歸檔檔已 staged
```

### §6.6 §5 SOP 一致性核查（BE-Refactor 強制）
```bash
# logging（§5.1）：section_engine 用 logger.error 須含 exc_info=True
grep -nE "logger\.error|logger\.exception|traceback\.format_exc" pipelines/section_engine.py   # 期望：無命中（合規）或含 exc_info=True
# database（§5.2）：section_engine 無 DB 交易（純函式）
grep -nE "\.commit\(\)" pipelines/section_engine.py                  # 期望：無命中（合規）
```
> 執行報告 §5 必貼以上 grep 結果（空輸出貼「無命中（合規）」）。

---

## §7 不可動清單

- [ ] `pipelines/slide_pipeline.py` 全檔 — 不收編其重複副本（避免動已 ship + golden 路、plan Q2）。
- [ ] `pipelines/contracts.py` 四凍結合約 — key 基準（原文標題 path）零變動、不新增/改欄位。
- [ ] `processor/rag_indexer.py` — P4 消費端不動（本案只改 producer 端實作歸屬）。
- [ ] `resume_pipeline` 攝入層私有 helper（`_extract_contact` / `_resolve_title` / `_detect_source_lang` / `_heal_glossary` / `_extract_metadata` / `_build_tiles` / `_make_summary` / `_resolve_domain_name`）— resume 專屬、不抽。
- [ ] **A 軌全部**：`pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*`（非本案新增者）/ `static/*` — 100% 不動。
- [ ] resume `final_zh` / `final_en` 輸出 byte — 抽取後須逐 byte 等價。
- [ ] `DocumentStrategy` ABC / `PipelineFactory` 註冊範式 — 方案 A 不動繼承鏈。
- [ ] **主 repo 目錄** — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — section_engine 骨架與摘要機制（共用引擎建立·摘要簇）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `pipelines/section_engine.py`；改 `pipelines/resume_pipeline.py`（+ `.bak`）|
| **安全性** | 🟢 高 — 純函式抽取、邏輯原值搬移、無新行為 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾 |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① 新建 `pipelines/section_engine.py`，頂部 `# === [PIPE-SECTION-BASE] ===` marker + module docstring（共用 section 引擎、pure-function、zero doc_type 耦合）。② 將 resume 之 `_collect_summary_targets`(L480)/`_node_content_text`(L496)/`_build_section_summaries`(L448)/`_generate_section_summaries`(L507)/`_translate_section_summaries`(L533)/`_parse_indexed`(L579) **邏輯原值搬入** section_engine 為 module-level 純函式；凡用到 `self.llm`/`self._translator` 之處改為**函式參數注入**（如 `build_section_summaries(targets, llm, ...)`）；`collect_summary_targets` 簽名保持可吃任意子樹（U3.2、現已是 sections 參數遞迴、天然支援）。③ resume 對應私有 method 改為 **delegate**（呼叫 `section_engine.xxx(...)` 並傳入 `self.llm` 等），不改回傳值/型別。④ resume 頂部 `import pipelines.section_engine as section_engine`（或具名 import）。⑤ key 基準（node_key=原文標題 path）原樣保留。⑥ 跑 §6.1 驗收：resume 既有測試全綠。⑦ 產 `baton/..._C1_執行.md`（套 template_execution、含 §1 對齊欄〔U2〕+ §自評〔U3〕），**baton 暫存、嚴禁 git add**。 |

### C2 — 翻譯與排版還原機制（render slots + 並行翻譯 + level 還原）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 改 `pipelines/section_engine.py`（追加）+ `pipelines/resume_pipeline.py`（+ `.bak`）|
| **安全性** | 🟡 中 — 含並行翻譯與 fallback、邏輯較密；原值搬移、測試鎖死 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾 |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | 依賴 C1（section_engine 模組已建）|
| **具體實作細節** | ① 將 resume `_collect_render_slots`(L849)/`_restore_sections_markdown`(L746)/`_translate_whole`(L904)/`_t`(L913)/`_normalize_paragraph_breaks`(L968)/`_is_heading_degraded`(L1008)/`_flatten_sections`(L1030)/`_own_text_len`(L1038) **原值搬入** section_engine；`Translator`/`InjectionContext`/`ThreadPoolExecutor`/`settings.LLM_MAX_CONCURRENT`/既有 `_api_semaphore` 限流與「單 unit 失敗退原文」異常隔離**原樣搬移**（RESUME-PERF-1）；`level=min(2+depth,6)`（HEADING-HOTFIX-1）保留；translator/inj 由參數注入。② resume 對應 method 改 delegate。③ 跑 §6.2：resume 測試全綠、final byte 等價。④ 產 `baton/..._C2_執行.md`（baton 暫存、嚴禁 git add）。 |

### C3 — rag 旁路與 meta header 純格式化器（Zero Schema Coupling）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 改 `pipelines/section_engine.py`（追加）+ `pipelines/resume_pipeline.py`（+ `.bak`）|
| **安全性** | 🟡 中 — meta header 由「讀 dict」重構為「收 tuples」、呼叫端須補抽欄+label；resume final byte 須等價 |
| **可逆性** | 🟢 高 — `git revert C3` 完全回滾 |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | 依賴 C2 |
| **具體實作細節** | ① 將 `_collect_rag_sections`(L811)/`_single_container_sections`(L840) 原值搬入 section_engine（`summary_key`=原文標題 path 基準保留）。② `_render_meta_header`(L922) **重構為純格式化器**（U3.1）：section_engine 新增 `render_meta_header(title: str, items: List[Tuple[str,str]], sep: str = "：") -> str`，**僅產 `# 標題` + 無序列表、零讀 raw_metadata/ctx**；resume 呼叫端（原 `_render_meta_header` 處）改為：先從 `ctx.raw_metadata` 抽 phone/email/domain/organization + 依 lang 做 zh/en label 對照 → 組 `(Label, Value)` 清單 → 呼 `section_engine.render_meta_header(...)`；輸出 markdown 須與重構前**逐 byte 等價**（label 文字、欄位順序、缺項省略規則照舊）。③ 跑 §6.3：`grep raw_metadata section_engine.py`=0、resume 測試全綠。④ 產 `baton/..._C3_執行.md`（baton 暫存、嚴禁 git add）。 |

### C4 — 引擎單元測試與接縫整合測試（雙鎖·U5/Q6）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增 `tests/test_section_engine.py` |
| **安全性** | 🟢 高 — 純測試新增、零業務代碼改動 |
| **可逆性** | 🟢 高 — `git revert C4` |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | 依賴 C1-C3（引擎完整）|
| **具體實作細節** | 新建 `tests/test_section_engine.py` 覆蓋：① DFS `collect_summary_targets` 走任意子樹 / ② 批次摘要 `parse_indexed` 保序 / ③ `restore_sections_markdown` 並行 byte 等拍保序 + patch `LLM_MAX_CONCURRENT` 限流計數 + 單 unit 拋例外退原文 / ④ `is_heading_degraded` 退化 fallback / ⑤ `render_meta_header` 純格式化（給 tuples → 預期 markdown、不碰任何 dict）/ ⑥ **base 層 P2→P3→P4 key-changing 整合測試**：Mock Translator 真改 key（原文→譯文）、斷言 `collect_summary_targets` 產之 key 與 `collect_rag_sections` 之 `summary_key` 同基準（原文標題 path）、下游可正確 match（堵 RAG-ASYNC-HOTFIX-1）。跑 §6.4 全綠。產 `baton/..._C4_執行.md`（baton 暫存）。 |

### C5 — Checkout 收官（Conformance + 歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` / `prompts/INDEX.md` + baton 歸檔（plan→plans/、tasks→tasks/、C1-C5 報告→executions/）|
| **安全性** | 🟢 高 — 純歸檔/狀態 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.5 |
| **依賴關係** | 依賴 C1-C4 全 ship |
| **具體實作細節** | ① Conformance 五維度（目標規格 U1-U6 / tasks §6 grep + pytest / 不可動 §7 / 提示詞稽核 / msg §8）+ §7.2 整合測試存在且通過（C4 base 層 key-changing + resume 既有整合，**免豁免**）。② baton 一次性 `mv` + `git add`：plan→`plans/`、tasks→`tasks/`、C1-C5 報告→`executions/`。③ TODO 結案（移 WIP、頂端完成表、索引 ✅）+ 全量 hash 自癒。④ 產 `baton/..._C5_執行.md` 後隨歸檔。⑤ 嚴禁自發 commit/push。 |

---

## §9 Open Questions

無。（plan v2 §9 六 OQ 已於 baron review 全 🟢 定案。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SECTION-BASE 原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 PIPE-SECTION-BASE executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（除 plan 指明之 section_engine.py + resume_pipeline.py）；Run 階段 baton 暫存嚴禁 git add；嚴禁自動 commit/push |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔、經 baron 同意移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令、不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-18)：初版拆分（5 Commit：C1 摘要機制 / C2 翻譯與排版還原 / C3 rag 旁路 + meta header 純格式化器〔U3.1 Zero Schema Coupling〕/ C4 引擎單元 + base 層 key-changing 整合測試〔雙鎖·Q6〕/ C5 Checkout 收官；行為等價 RESUME-PERF-1 C1 範式、每 Run Commit resume 測試鎖死；SOP §5 待抽區段 grep 合規；slide_pipeline 不收編〔Q2〕）
