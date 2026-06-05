# PIPE-RESUME C4 — P3 Business Constraints 執行報告

---

**任務代號**：PIPE-RESUME C4（v9 整合批次）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11）
**次級參考**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C4
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C4)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C3 後；`run_phase3` 的 `InjectionContext` 無 `constraints`、履歷業務翻譯規則無入口。
- **完成狀態**：① 新增模組常數 `_RESUME_CONSTRAINTS`（4 條履歷業務規則：公司/產品名保留原文、Email/電話/URL 原樣、技能詞保留英文、專利/期刊原文+對照）；② `run_phase3` 的 `InjectionContext` 加 `constraints=_RESUME_CONSTRAINTS`，由共用 `Translator._build_system_prompt ⑤` 自動貼為「【額外譯文約束】」（PIPE-SPEC §1.2.3.1 翻譯策略隔離原則）。全變更 `# === [PIPE-RESUME v9 C4 START/END] ===` 包裹。**共用 Translator 引擎零改**；端到端驗證 constraints 確實注入系統提示詞。全套件 478 passed（C4 零新增紅燈）。

> **既有 2 紅燈為 C3 carryover**（`test_run_phase1_contract`/`test_run_phase2_flag_off` 引用已廢 `_raw_meta`）——**C4 未新增任何失敗**，待 C6 更新測試修復。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C4 | `_RESUME_CONSTRAINTS` 常數 + run_phase3 InjectionContext 加 constraints（共用 Translator 注入） | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C4_resume_pipeline.py.bak` | 新增 `_RESUME_CONSTRAINTS` 常數 + run_phase3 InjectionContext constraints（v9 C4 標記）|

> ⚠️ `.bak` 須在 C4 `git add` 清單（§8）。**執行報告本體不 git add**（依指令）。

---

## §4 修法說明

### §4.1 `_RESUME_CONSTRAINTS` 常數（v9 C4 標記）
```python
# === [PIPE-RESUME v9 C4 START] P3 履歷業務翻譯約束 ===
_RESUME_CONSTRAINTS = [
    "公司名稱、產品名稱保留原文不翻",
    "Email／電話／URL 原樣保留",
    "專業技能詞（Python/Docker 等）保留英文",
    "專有名詞（如專利、期刊等名稱）保留原文並在中譯中附加對照",
]
# === [PIPE-RESUME v9 C4 END] ===
```

### §4.2 `run_phase3` 注入 constraints（v9 C4 標記）
```python
inj = InjectionContext(
    lcc=gspec.lcc, glossary=gspec.glossary, zh_summary=gspec.translated_abstract,
    domain_name=gspec.domain_name, doc_type="resume",
    # === [PIPE-RESUME v9 C4 START] ===
    constraints=_RESUME_CONSTRAINTS,   # 履歷業務規則逐路注入共用 Translator（PIPE-SPEC §1.2.3.1）
    # === [PIPE-RESUME v9 C4 END] ===
)
```
**設計（翻譯策略隔離、PIPE-SPEC §1.2.3.1）**：規則由策略（ResumePipeline）擁有、經 `InjectionContext.constraints` 逐路注入；共用 `Translator._build_system_prompt ⑤`（`translator.py:134-137`）自動貼「【額外譯文約束】」條列入系統提示詞。**不為各路 fork prompt、不污染 Translator 核心**。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/resume_pipeline.py
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C4_resume_pipeline.py.bak
# （baton/ 報告 + prompts/ + TODO.md 另計；無其他越界變動）
```

### §5.2 §6.4 驗收 + 端到端注入驗證
```
_RESUME_CONSTRAINTS= 4 條
grep：resume_pipeline.py:108 常數宣告、:471 constraints=_RESUME_CONSTRAINTS
# 端到端（mock Translator._build_system_prompt）：
含【額外譯文約束】? True | 含規則? True   # constraints 確實貼入系統提示詞
```

### §5.3 測試（C4 零新增紅燈）
```bash
$ pytest tests/test_resume_pipeline.py tests/test_pipe_core.py tests/test_pipe_scaffold.py -q
2 failed, 38 passed   # 2 failed = C3 carryover（_raw_meta、待 C6）；C4 未新增

$ pytest tests/ -q
3 failed, 478 passed, 3 skipped
# 與 C3 完全相同：(1) test_settings_log_format_default_auto 環境性；(2)(3) C3 carryover _raw_meta 測試（待 C6）
# C4 新增失敗數 = 0
```

### §5.4 SOP 一致性核查（BE-Refactor）
- **logging 檢測**：C4 無新增 `logger.error`/`traceback.format_exc`（合規）。
- **database 檢測**：C4 無 DB 操作（純常數 + InjectionContext 欄位、無 commit/session.begin）（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*`（含 `translator.py`）| [x] ✅ 未觸碰（共用 Translator 零改、僅消費 constraints 欄）|
| `pipelines/context.py` / `contracts.py` / `factory.py` / `orchestrator.py` | [x] ✅ 未變更 |
| `run_phase1` / `run_phase2` / `run_phase4` | [x] ✅ 未觸碰（C4 僅改 run_phase3 + 常數）|
| `tests/*` | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：C4 執行報告暫存 baton/、不入版控，待 C7 收官歸檔。
- **下一步**：tasks.md C5 — Shadow DB Fidelity（`web_server.py` `run_pipeline_shadow` 改讀 `ctx.raw_metadata` 組 `metadata_json`）；由 baron 另行下達。**C6 將修復 C3 的 2 個 _raw_meta 測試紅燈。**
- **消化歸檔之 baton 檔**：無。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單（代碼 + .bak + TODO/prompts；執行報告本體不 add）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C4_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_C4_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C4_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C4_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C4 — P3 Business Constraints (履歷業務規則注入)

於 pipelines/resume_pipeline.py 宣告履歷專屬翻譯約束常數，
並在 run_phase3 建立 InjectionContext 時，將其作為 constraints 傳入，
以此將公司/產品名、技能詞、電話/Email 等翻譯規則動態注入共用 Translator。
全變更以大改版註解包裹，遵循翻譯策略自主隔離規範。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C4 代碼變更與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/；C7 收官 mv 歸檔 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | C4 限改 resume_pipeline.py（P3+常數）；嚴禁自動 commit；執行報告不入 git |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/ |
| **重複防護** | 本檔為 C4 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：C4 執行完畢——`_RESUME_CONSTRAINTS`（4 條業務規則）+ run_phase3 InjectionContext 加 constraints；端到端驗證 constraints 注入共用 Translator 系統提示詞（PIPE-SPEC §1.2.3.1、引擎零改）。全套件 478 passed / 3 failed（1 環境性 + 2 C3 carryover _raw_meta、C4 零新增、待 C6）。
