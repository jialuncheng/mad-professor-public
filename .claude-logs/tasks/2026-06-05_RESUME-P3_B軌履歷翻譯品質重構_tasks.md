# RESUME-P3 B軌履歷翻譯品質重構 — Tasks

> 本文件為 RESUME-P3 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-05_RESUME-P3_B軌履歷翻譯品質重構_plan_v1.md`（§99.2 v3、OQ 已核准）產出，含 6 個 Commit（C1 P1 opt-out + C2 U4 停用 + C3 P3 核心 + C4 fallback + C5 測試 + C6 Checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | 逐單元翻譯/還原以 `resume_pipeline.py` 私有方法實作（不新增模組、不耦合 A 軌；如過大可選拆 `pipelines/_resume_restore.py`，預設不拆）|
| **修改檔案** | 3 個 | `pipelines/resume_pipeline.py`（C1 `_build_tiles` opt-out / C3 `run_phase3` 重寫 + 私有還原輔助 / C4 fallback）/ `processor/translator.py`（C2 U4 resume 停用閘門）/ `tests/test_resume_pipeline.py`（C5 測試）|
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 6 個 | C1 → C2 → C3 → C4 → C5 → C6（Checkout）|
| **baton 歸檔** | 1 次 | C6 收官：`mv` baton plan → `plans/`、tasks → `tasks/`、C1-C6 報告 → `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：B軌 `run_phase3` 對履歷 100% Bypass（整份 .md 單次翻譯、直寫、不還原），致結構標題漏翻、原文/譯文重複、地點行錯亂、技術詞不一致；且 P1 對無消費者 tiles 跑 TextTiling embedding（做白工 + 429 源）。
- **解法**（原子化拆 6 commit、對齊 plan v3 核准 OQ）：
  - `C1 — P1 履歷 Tiling Opt-out（P1 切塊旁路）`：`_build_tiles` 對 resume 強制 opt-out TextTiling、tiles 改為乾淨 heading section（Q3 + 滅 429）。
  - `C2 — Translator U4 resume 停用（行結構對齊容錯停用）`：`translator.py` U4 `。！？` 重切對 `ctx.doc_type=='resume'` 停用（Q4、保留條列/日期/地點行）。
  - `C3 — P3 逐 heading section 翻譯與還原（廢 100% Bypass）`：`run_phase3` 改逐 heading section 翻譯 + 結構還原重組（Q1/Q2、pipelines/ 內重建、不耦合 A 軌）。
  - `C4 — heading 退化 Fallback（單一巨 section 降級防護）`：偵測 heading 退化（section 數異常少 / 單一巨 section）→ 降級整檔翻譯（Q9）。
  - `C5 — Unit Tests（逐 heading 契約與退化測試）`：結構標題翻譯 / 無 doubling / opt-out / fallback / 契約不變。
  - `C6 — Checkout（收官與 baton 檔案歸檔）`。
- **影響範圍**：B軌 `resume_pipeline.py`（P1/_P3/fallback）+ `translator.py`（U4 resume 閘門）+ 測試；**不動** A軌 / `contracts.py` / `translator.py` 雙模式引擎核心 / `TilingProcessor` 演算法本體 / P4 RAG 切 chunk / DB Schema。**改 B軌輸出 → 須與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 合併一次重捕 Golden**。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `resume_pipeline.py` `_build_tiles` L233-242 | 無條件 `TilingProcessor().process(..., doc_type="resume")` | 履歷對無消費者 tiles 跑 TextTiling embedding（做白工 + 429）|
| `resume_pipeline.py` `run_phase3` L447-513 | 100% Bypass：`_read_source_text` 讀 .md → 單次 `Translator.translate(full_text)` → 直寫 | 結構標題漏翻 / doubling / 地點錯亂 / 技術詞不一致 |
| `resume_pipeline.py` `_read_source_text` L361-372 / `_tiles_to_text` L374-384 | 讀 .md；tiles 僅 fallback | P3 未用 heading 結構 |
| `translator.py` `translate` U4 L188-193 | `。！？` 重切（譯文行數<原文行數時）| 對英文/條列履歷切不動、壓縮行結構 → 地點錯亂 |

---

## §3 觀察問題

### 問題 #1：100% Bypass 整檔單發 → 結構性翻譯品質差
- **證據**：`file:///pipelines/resume_pipeline.py#L484`（單次整檔 translate）+ `#L496`（直寫無還原）。
- **影響**：標題漏翻 / 原文+譯文 doubling / 多行結構壓縮。

### 問題 #2：履歷 P1 跑無消費者的 TextTiling
- **證據**：`file:///pipelines/resume_pipeline.py#L241`（無條件 tiling）；tiles 僅 `#L375` fallback。
- **影響**：做白工 + 自找 429（TILING-HOTFIX-1 根源）。

---

## §4 設計方案

### §4.1 C1 — P1 履歷 Tiling Opt-out
`_build_tiles`：resume 路徑 **不跑 TextTiling embedding**，tiles 改為 `JsonProcessor` 輸出的 heading section（或 `TilingProcessor` 強制 bypass 路徑），保全 `###` 結構。`# === [RESUME-P3 C1 START/END] ===` 包裹 + 改前 .bak。

### §4.2 C2 — Translator U4 resume 停用
`translator.py::translate` U4 區塊：`if ctx.doc_type == 'resume': 跳過 。！？ 重切`（僅 resume 範疇、不動其他文體）。`# === [RESUME-P3 C2 START/END] ===` 包裹 + 改前 .bak。

### §4.3 C3 — P3 逐 heading section 翻譯與還原（核心、廢 100% Bypass）
`run_phase3` 重寫：讀 heading sections（C1 後的 `ctx.ingestion.tiles`）→ 逐 section **標題/正文分流**呼叫 `Translator.translate`（沿用 InjectionContext：lcc/glossary/zh_summary/domain_name/doc_type='resume'/constraints）→ 按 section 結構**重組** final_zh（en=原著）→ 寫檔 → 交付 `BilingualMarkdownSpec`（欄位不變）。逐單元拼接/還原以**私有方法**實作、**不 import `translate_processor`**。source_lang='zh*' 不重譯。`# === [RESUME-P3 C3 START/END] ===` 包裹 + 改前 .bak。

### §4.4 C4 — heading 退化 Fallback
偵測 heading 退化（section 數 ≤ 門檻 / 單一巨 section 佔比過高 = heading 未抓到）→ 降級為整檔翻譯（沿用舊 Bypass 路徑作 fallback），確保極限情況仍可完整翻譯。`# === [RESUME-P3 C4 START/END] ===` 包裹。

### §4.5 C5 — Unit Tests
`tests/test_resume_pipeline.py` 追加（`# === [RESUME-P3 C5 START/END] ===`）：opt-out（無 TextTiling 呼叫）/ 逐 section 標題翻譯 / 無 doubling（單元→單譯文）/ fallback（單一巨 section→整檔）/ 契約 `BilingualMarkdownSpec` 不變。mock LLM。

### §4.6 C6 — Checkout
Conformance 驗收 + 一次性 mv 歸檔（plan/tasks/C1-C6 報告）+ TODO 結案。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| C3 重寫 run_phase3 破壞契約/下游 P4 | 🟡 中 | `BilingualMarkdownSpec` 欄位不變、final_zh_path 仍交付；跑 test_resume_pipeline + test_pipe_scaffold |
| 逐 section 失去跨段上下文、術語不一致 | 🟡 中 | 沿用 P2 zh_summary + glossary 注入 InjectionContext；E2E 比對 A軌 |
| heading 未抓到 → 逐單元退化為整檔（doubling 回歸）| 🟡 中 | C4 退化偵測 + 整檔 fallback；依賴 P1 DocAnalyzer heading fix |
| C2 動 U4 波及其他文體 | 🟢 低 | 僅 `ctx.doc_type=='resume'` 閘門、其他路 byte 等價；跑既有 translator 測試 |
| C1 opt-out 後 tiles fallback 來源改變 | 🟢 低 | `_tiles_to_text` fallback 改吃 heading section；確認無其他 tiles 消費者（grep 證 §3）|
| 改 B軌輸出污染既有 Golden | 🟡 中 | 與 TILING/SHADOW-HOTFIX-2 合併一次重捕（baron MinerU `capture --all`）|

---

## §6 測試計畫

### §6.1 C1 驗收（P1 opt-out）
```bash
grep -nE "RESUME-P3 C1" pipelines/resume_pipeline.py            # 標記包裹
grep -nE "doc_type=.resume.|bypass|TilingProcessor" pipelines/resume_pipeline.py  # opt-out 邏輯
venv/bin/python -m pytest tests/test_resume_pipeline.py -q       # 不退化
```

### §6.2 C2 驗收（U4 resume 停用）
```bash
grep -nE "RESUME-P3 C2|doc_type == .resume.|doc_type==.resume." processor/translator.py  # resume 閘門
venv/bin/python -m pytest tests/test_translator.py -q            # 其他文體不退化
```

### §6.3 C3 驗收（P3 逐 heading 重寫）
```bash
grep -nE "RESUME-P3 C3" pipelines/resume_pipeline.py
grep -nE "translate_processor" pipelines/resume_pipeline.py || echo "未耦合 A 軌 translate_processor ✓"
grep -nE "BilingualMarkdownSpec" pipelines/resume_pipeline.py   # 契約不變
venv/bin/python -m pytest tests/test_resume_pipeline.py tests/test_pipe_core.py -q
```

### §6.4 C4 驗收（fallback）
```bash
grep -nE "RESUME-P3 C4|退化|fallback|單一" pipelines/resume_pipeline.py
venv/bin/python -m pytest tests/test_resume_pipeline.py -k "fallback or degrade" -q
```

### §6.5 C5 驗收（測試套件）
```bash
venv/bin/python -m pytest tests/test_resume_pipeline.py -q       # 含新測試全綠
venv/bin/python -m pytest tests/ -q                              # 全套件僅既存 env flake
```

### §6.6 SOP 一致性核查（C1-C4 落地前強制、貼執行報告）
```bash
grep -nE "logger\.error|logger\.exception|traceback.format_exc" pipelines/resume_pipeline.py processor/translator.py | grep -v "exc_info=True"
grep -nE "\.commit\(\)" pipelines/resume_pipeline.py processor/translator.py
```

### §6.7 E2E（baron 手動）
1. 上傳 `DeHunt_CTO_Tzung-Yuan_Lee.pdf` + 啟用影子 → B軌（測試）中文 md：學歷單一譯文行 / 無原文重複 / 地點不錯亂 / 公司「中文(原文)」/ 技能標題已翻、技術詞保英文。
2. 確認 P1 未跑 TextTiling embedding（無 429）。
3. `golden_baseline.py diff` 對重捕 golden 裁決 D2≥0.95。

---

## §7 不可動清單

- [ ] **A軌全鏈**（`pipeline_core.py` / `processor/translate_processor.py`）— byte 不動（棄修、嚴禁 import 耦合）。
- [ ] **`processor/translator.py` 雙模式引擎核心**（`translate()` 路由 / `_build_system_prompt` 五步）— 不動（C2 僅加 resume U4 閘門）。
- [ ] **`processor/tiling_processor.py` TextTiling 演算法本體** — 不改（C1 僅 opt-out 不呼叫）。
- [ ] **`pipelines/contracts.py` 凍結合約**（`BilingualMarkdownSpec` 欄位）— 不改。
- [ ] **`processor/rag_processor.py` P4 RAG 切 chunk** + embedding 參數 — 不動。
- [ ] **`prompt/translate/content_translate_prompt.txt`** — 不動（A/B 共用）。
- [ ] **P2/P4**（`run_phase2/4`）+ `ctx.raw_metadata` 穿線 — 不動；**P1 僅限 `_build_tiles` 履歷 opt-out 閘門**。
- [ ] **`models.py` / `db.py` / 既有 API 與前端** — 不動。
- [ ] 主 repo 目錄 — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — P1 履歷 Tiling Opt-out（P1 切塊旁路）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（`_build_tiles`）+ `.claude-logs/archive/2026-06-05_RESUME-P3_C1_resume_pipeline.py.bak` |
| **安全性** | 🟡 中 — 改 P1 tiles 來源；以「tiles 現僅 fallback 用」+ heading 結構保全緩解 |
| **可逆性** | 🟢 高 — `git revert C1`（.bak 可還原）|
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | 1) `cp resume_pipeline.py .bak`。2) `_build_tiles`：resume 路徑**不執行 TextTiling embedding**——優先做法「跳過 `TilingProcessor`、直接回 `JsonProcessor` 輸出（`processed.json`）的 heading sections」；或「`TilingProcessor` 走強制 bypass 路徑」（**不得改 TextTiling 演算法本體**）。3) 確認回傳結構仍為 `_load_tiles` 可解析的 sections list（title/content/children）。4) `# === [RESUME-P3 C1 START/END] ===` 包裹。5) 產 `baton/..._C1_執行.md`。 |

### C2 — Translator U4 resume 停用（行結構對齊容錯停用）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `processor/translator.py`（`translate()` U4 區塊）+ `.bak` |
| **安全性** | 🟢 高 — 僅 `ctx.doc_type=='resume'` 閘門、其他文體 byte 等價 |
| **可逆性** | 🟢 高 — `git revert C2` |
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | 無前置（與 C1 獨立）|
| **具體實作細節** | 1) `cp translator.py .bak`。2) `translate()` 的 U4 區塊（L188-193）加閘門：`if (ctx.doc_type or '') == 'resume': 不執行 re.sub 。！？ 重切`（保留條列/日期/地點原行結構）；其餘文體維持原 U4。3) `# === [RESUME-P3 C2 START/END] ===` 包裹。4) 產 `baton/..._C2_執行.md`（貼 §6.2 + 其他文體不退化證據）。 |

### C3 — P3 逐 heading section 翻譯與還原（廢 100% Bypass·核心）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（`run_phase3` 重寫 + 私有逐單元翻譯/還原輔助）+ `.bak` |
| **安全性** | 🟡 中 — 核心重寫；以「契約欄不變 + 不耦合 A 軌 + C4 fallback 兜底」緩解 |
| **可逆性** | 🟢 高 — `git revert C3`（.bak 可還原）|
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | C1（tiles=heading sections）+ C2（U4 已停）|
| **具體實作細節** | 1) `cp resume_pipeline.py .bak`。2) `run_phase3`：改讀 `ctx.ingestion.tiles`（C1 後=heading sections）；**逐 section** 將標題與正文 item 分流呼叫 `Translator().translate(unit, inj, NORMAL, text_type)`（沿用既有 `InjectionContext`：lcc/glossary/zh_summary/domain_name/`doc_type='resume'`/constraints）。3) 以**私有方法**（如 `_translate_sections` / `_restore_zh_markdown`）按 section 結構（title/level/content/children）**重組** final_zh；**嚴禁 import `translate_processor`**（不耦合 A 軌）。4) `source_lang.startswith('zh')` → 不重譯（zh=原文）。5) en=原著、寫 `article_en_path`；final_zh 寫 `article_zh_path`。6) 交付 `BilingualMarkdownSpec`（`final_zh_path`/`final_en_path`/`translated_abstract`←P2/`rag_tree_json=None`、欄位不變）。7) `# === [RESUME-P3 C3 START/END] ===` 包裹。8) 產 `baton/..._C3_執行.md`。 |

### C4 — heading 退化 Fallback（單一巨 section 降級防護）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/resume_pipeline.py`（`run_phase3` 內退化偵測 + 整檔 fallback 分支）+ 沿用 C3 .bak |
| **安全性** | 🟢 高 — 純防護分支、正常路徑不受影響 |
| **可逆性** | 🟢 高 — `git revert C4` |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | C3 |
| **具體實作細節** | 1) `run_phase3` 進逐 section 前偵測 heading 退化：section 數 `<` 門檻（如 2）或單一 section 文字佔全文比例過高（= heading 未抓到）。2) 退化 → 走**整檔翻譯 fallback**（沿用舊 Bypass：`Translator.translate(full_text, inj, NORMAL, 'content')`）+ logger.warning（exc_info 視情況）。3) 仍交付相同 `BilingualMarkdownSpec`。4) `# === [RESUME-P3 C4 START/END] ===` 包裹。5) 產 `baton/..._C4_執行.md`。 |

### C5 — Unit Tests（逐 heading 契約與退化測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `tests/test_resume_pipeline.py`（追加）|
| **安全性** | 🟢 高 — 純測試、mock 隔離 |
| **可逆性** | 🟢 高 — `git revert C5` |
| **驗收 grep 條件** | §6.5 |
| **依賴關係** | C1-C4 |
| **具體實作細節** | 追加（`# === [RESUME-P3 C5 START/END] ===`、mock LLM）：① C1 opt-out（run_phase1/_build_tiles 下 resume 不觸發 TextTiling embedding 呼叫）；② C3 逐 section 標題翻譯（多 section fixture → 各標題經翻譯、無整行英文標題殘留）；③ 無 doubling（單一來源單元 → 單一譯文單元、final_zh 無原文行回顯）；④ C4 fallback（單一巨 section fixture → 走整檔翻譯且交付契約）；⑤ 契約不變（run_phase3 回 `BilingualMarkdownSpec` 欄位齊備）。產 `baton/..._C5_執行.md`。 |

### C6 — Checkout（收官與 baton 檔案歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`；`mv` baton plan→`plans/`、tasks→`tasks/`、C1-C6 報告→`executions/`；無業務代碼 |
| **安全性** | 🟢 高 — 純驗收 + 歸檔 |
| **可逆性** | 🟢 高 — mv 可逆 |
| **驗收 grep 條件** | §6.5 + Conformance（目標規格 plan §2 U1-U8 / §6 pytest+grep / 不可動清單 git 證據）+ §6.6 SOP |
| **依賴關係** | C1-C5 全 ship |
| **具體實作細節** | 1) Conformance 三維度驗收 + SOP 核查貼 grep。2) `TODO.md`：RESUME-P3 移入 ✅ 完成表（Hash 待回填）+ 移除 active + 索引 + 歷史 Hash 自癒。3) 一次性 `mv` baton（plan_v1〔保留 `_v1`〕/tasks/C1-C6 報告）→ plans//tasks//executions/ + `git add`。4) 確認 baton/ 無本任務殘留。5) **提醒 baron：改 B軌輸出 → 與 TILING-HOTFIX-1/SHADOW-HOTFIX-2 合併一次重捕 Golden Baseline**。6) msg 寫 /tmp、嚴禁自發 commit/push。 |

---

## §9 Open Questions

無。（plan §7 Q1-Q10 已於 plan v3 由 baron 拍板核准：Q1 逐 heading / Q2 pipelines 內重建不耦合 A 軌 / Q3 P1 履歷 tiling bypass / Q4 resume 停用 U4 / Q9 退化 fallback / Q10 通用化歸 INFRA-3；Q5/Q7/Q8 採推薦、Q6 已落地。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 RESUME-P3 的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按序執行；Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 RESUME-P3 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改 A 軌/凍結合約/translator 引擎核心/tiling 演算法本體；嚴禁 import translate_processor；嚴禁自動 commit/push |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務收官歸檔、經 baron 同意移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡與 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：初版拆分——依 plan v3（OQ 核准）拆 6 commit（C1 P1 履歷 tiling opt-out / C2 translator U4 resume 停用 / C3 P3 逐 heading section 翻譯與還原〔廢 100% Bypass、pipelines 內重建不耦合 A 軌〕/ C4 heading 退化 fallback / C5 單元測試 / C6 Checkout）；§0.5 成果盤點 + §8 六維度；明載改 B軌輸出須與 TILING/SHADOW 合併重捕 Golden、通用化 chunking 歸 INFRA-3。
