# PIPE-RESUME C6 — Unit Tests 執行報告

---

**任務代號**：PIPE-RESUME C6（v9 整合批次）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11）
**次級參考**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C6 / §4.6 / §6.6
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C6)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C5 後；`tests/test_resume_pipeline.py` 19 測試中 **2 紅燈**（C3 廢除 `self._raw_meta` 後遺留）：`test_run_phase1_contract`（斷言 `s._raw_meta` → AttributeError）、`test_run_phase2_flag_off`（設 `s._raw_meta` 已失效 → lcc='general' 而非 '程式設計'）。
- **完成狀態**：C6 **僅改 `tests/test_resume_pipeline.py`**：
  1. **修復 2 紅燈**——將 `self._raw_meta` 斷言/設定全面改對齊 `ctx.raw_metadata`（C2 穿線載體、三軸 `{value,source,confidence}` 結構，經 `s._meta_value()` 取值）；`_ctx_with_ingestion` 擴 `raw_metadata` 參數。
  2. **追加 4 個 v9 契約測試**——① P1 影子後綴（`_shadow`→title `(測試)`、非 shadow 乾淨）② P2 摘要先行步序（`_make_summary` 早於 `normalize_to_lcc`）③ P3 `InjectionContext.constraints` 注入 `_RESUME_CONSTRAINTS` + 內容無 `(測試)` ④ C5 影子寫庫保真（mock `run_pipeline_shadow`／`upsert_paper`，斷言 meta_dict 含整包 raw_metadata + title 繼承 `(測試)` + domain_name 傳入）。
  3. 全變更 `# === [PIPE-RESUME v9 C6 START/END] ===` 包裹（8 對標記）。
- **測試結果**：`test_resume_pipeline.py` **19 passed**（13 原綠 + 2 紅燈修復 + 4 v9 新增）；核心 `pipelines` 套件（test_pipe_core + test_pipe_scaffold）**25 passed** 不退化。

> **全套件確定性狀態**：C6 後確定性失敗 **僅 1 個**（`test_settings_log_format_default_auto`，`.env` LOG_FORMAT=json 環境性、跨所有 commit 一致）。**C5 遺留的 2 個 C3 carryover 紅燈已由 C6 全數修復**。`test_tiling_paragraph.py`（MODEL-3）全套件負載下偶發 flaky（本次失 3 子測試、隔離整檔 **7 passed**）——與 C6（純測試檔、僅改 test_resume_pipeline）零關係，屬既存環境性（詳 §5.3）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C6 | `tests/test_resume_pipeline.py` 修 2 個 _raw_meta 紅燈（改 ctx.raw_metadata）+ 追加 4 v9 契約測試 | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `tests/test_resume_pipeline.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C6_test_resume_pipeline.py.bak` | 修 2 紅燈 + 追加 4 v9 契約測試（v9 C6 標記） |

> ⚠️ `.bak` 須在 C6 `git add` 清單（§8）。**執行報告本體不 git add**（依指令）。

---

## §4 修法說明

### §4.1 修復 C3 遺留紅燈（self._raw_meta → ctx.raw_metadata）
| 測試 | 原（紅） | 新（綠） |
|---|---|---|
| `test_run_phase1_contract` | 捕 `s.run_phase1(_ctx(...))` 不留 ctx；斷言 `s._raw_meta["domain"]/["email"]` | 先建 `ctx=_ctx(...)` 再 `run_phase1(ctx)`；斷言 `s._meta_value(ctx.raw_metadata,"domain")=="程式設計"` / `ctx.raw_metadata["email"]["value"]` / `"phone" in ctx.raw_metadata` |
| `test_run_phase2_flag_off` 等 4 個 P2 | `s._raw_meta = {"domain": ...}` | `_ctx_with_ingestion(raw_metadata={"domain": {"value": ...}})`（三軸結構、經 `_meta_value` 取值） |
| `_ctx_with_ingestion` helper | 無 raw_metadata | 擴 `raw_metadata=None` 參數 → 設 `ctx.raw_metadata`（v9 P2 唯一 domain 載體） |

### §4.2 追加 v9 契約測試（4 個）
- `test_p1_shadow_title_suffix`：`run_phase1` 以 `p1_shadow` paper_id → `spec.title == "王小明 (測試)"`；`p1` → 乾淨 `"王小明"`。
- `test_run_phase2_summary_before_lcc`：mock `_make_summary`/`normalize_to_lcc` 各 append 至 `order` → 斷言 `order == ["summary","lcc"]`（v10 摘要先行步序）。
- `test_run_phase3_injects_resume_constraints`：capture `Translator.translate` 收到的 `InjectionContext` → 斷言 `inj.constraints == rp._RESUME_CONSTRAINTS`（非空、含 "Email" 規則）；且 `final_zh` 內容無 `(測試)`（影子後綴不污染內容）。
- `test_c5_shadow_write_uses_raw_metadata`：mock `pipelines.Orchestrator`（原地填 raw_metadata/ingestion/glossary_ready/bilingual）+ `web_server.paper_manager.upsert_paper`（捕 metadata/domain）→ `asyncio.run(web_server.run_pipeline_shadow(...))` → 斷言傳入 meta_dict 含 `candidate_name/domain/email` 整包 + `title["value"]=="王小明 (測試)"` + `domain=="CS"`。複用 `test_pipe_scaffold` 既證 harness（local `from pipelines import Orchestrator` → patch `pipelines.Orchestrator`）。

### §4.3 物理防線遵守
- **僅改 `tests/test_resume_pipeline.py`**；零觸碰 `pipelines/`、`web_server.py`、`processor/*` 業務代碼。
- C5 影子寫庫測試以 **mock** 隔離（不實打 LLM/Embedding/DB；fake `upsert_paper`）。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M tests/test_resume_pipeline.py
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C6_test_resume_pipeline.py.bak
# （另 C5 .bak 未 commit、baton 報告 + prompts/ + TODO.md 另計；唯一 .py 變動＝tests/test_resume_pipeline.py）
```

### §5.2 §6.6 目標測試 + 核心套件
```
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
  19 passed in 0.64s          # 13 原綠 + 2 紅燈修復 + 4 v9 新增
$ venv/bin/python -m pytest tests/test_pipe_core.py tests/test_pipe_scaffold.py -q
  25 passed in 0.62s          # 核心 pipelines 不退化
grep "PIPE-RESUME v9 C6 START" tests/test_resume_pipeline.py → 8 命中（包裹標記）
```

### §5.3 全套件（含 flaky 釐清）
```bash
$ venv/bin/python -m pytest tests/ -q
  4 failed, 481 passed, 3 skipped in 34.83s
  # failed = 1 env（test_settings_log_format_default_auto）
  #        + 3 test_tiling_paragraph（負載 flaky）
$ venv/bin/python -m pytest tests/test_tiling_paragraph.py -q
  7 passed in 38.44s          # 隔離整檔通過 → 確認 flaky
$ grep -n LOG_FORMAT .env
  54:LOG_FORMAT=json          # 環境性、非 C6 引入
```
**flaky 裁定**：`test_tiling_paragraph.py`（MODEL-3，每測試 ~14s）全套件負載下偶發失敗、隔離整檔 7 passed → **負載/時序型 flaky、與 C6（純測試檔、僅改 test_resume_pipeline）零關係**、屬既存環境性。
**C6 確定性結算**：確定性失敗由 C5 的 **3 個（1 env + 2 C3 carryover）降至 1 個（僅 env）**——**2 個 C3 carryover 紅燈已由 C6 全數修復**；C6 零新增失敗。

### §5.4 SOP 一致性核查（BE-Refactor、§6.7）
```bash
$ grep -nE "logger\.error|logger\.exception|traceback.format_exc" tests/test_resume_pipeline.py
  → 無命中（合規）
$ grep -nE "\.commit\(\)" tests/test_resume_pipeline.py
  → 無命中（合規）
```
- **logging**：純測試檔、無新增 `logger.error`（合規）。
- **database**：純測試檔、無裸 `.commit()`；C5 寫庫測試以 fake `upsert_paper` 隔離、不觸真實 session（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipelines/*`（resume_pipeline/context/contracts 等）| [x] ✅ 未觸碰 |
| `web_server.py`（A 軌 + 影子區塊）| [x] ✅ 未觸碰（C5 寫庫測試以 mock 隔離） |
| `pipeline_core.py` / `paper_manager.py` / `processor/*` | [x] ✅ 未觸碰 |
| `models.py` / `db.py` | [x] ✅ 未觸碰 |
| 其他既有測試檔 | [x] ✅ 未觸碰（僅改 test_resume_pipeline.py） |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：C6 執行報告暫存 baton/、不入版控，待 C7 收官歸檔。
- **下一步**：tasks.md C7 — Checkout / 收官歸檔（Conformance 三維度驗收 + SOP 核查 + 一次性 `mv` plan_v1〔保留 `_v1`〕/tasks/C1-C7 報告 → plans//tasks//executions/ + TODO 結案 + 歷史 Hash 自癒；母 plan/PIPE-SPEC 為其本身既有 baton 位、不隨本批次 mv）；由 baron 另行下達。
- **消化歸檔之 baton 檔**：無。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單（測試代碼 + .bak + TODO/prompts；執行報告本體不 add）
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C6_test_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_C6_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C6_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C6_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C6 — Unit Tests (v9 契約單元測試與紅燈修復)

於 tests/test_resume_pipeline.py 修復 C3 遺留的 _raw_meta 測試斷言紅燈，
改為對齊 ctx.raw_metadata；並追加 v9 契約測試，包含 P1 影子後綴判定、
P2 摘要先行步序、P3 constraints 注入及影子寫庫保真度。
全變更以大改版註解包裹，恢復核心 pipelines 測試全綠。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C6 測試變更與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/；C7 收官 mv 歸檔 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | C6 限改 tests/test_resume_pipeline.py；嚴禁動 pipelines/業務代碼/自動 commit；執行報告不入 git |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/ |
| **重複防護** | 本檔為 C6 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：C6 執行完畢——`tests/test_resume_pipeline.py` 修復 C3 遺留 2 個 `_raw_meta` 紅燈（改 `ctx.raw_metadata`）+ 追加 4 個 v9 契約測試（P1 影子後綴 / P2 摘要先行步序 / P3 constraints 注入 / C5 影子寫庫保真）；test_resume_pipeline 19 passed、核心 pipelines 25 passed。確定性失敗由 3 降至 1（僅 env）；test_tiling_paragraph 全套件偶發 flaky 經查與 C6 零關係（隔離 7 passed）。
