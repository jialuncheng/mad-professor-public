# PIPE-RESUME C7-hotfix — 策略註冊缺失與加載鏈修復 執行報告

---

**任務代號**：PIPE-RESUME C7-hotfix
**執行日期**：2026-06-04
**依據規劃**：`.claude-logs/baton/2026-06-04_PIPE-RESUME_C7-hotfix_hotfix.md`（hotfix 規劃）
**次級參考**：`.claude-logs/plans/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（C1 報告 §6 已標註此惰性註冊風險）
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C7-hotfix)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C7（`a644e48`）收官後，開發機影子測試服上傳履歷 PDF（`DeHunt_CTO_Tzung-Yuan_Lee`）→ A 軌正本完成、但 B 軌影子於 `Orchestrator().run(ctx)` Phase 1 拋 `NotImplementedError`：`[factory] doc_type='resume' 未註冊且無 litedoc，回 NullStrategy 哨兵` → `strategy=NullStrategy` → `run_phase1` raise。
- **完成狀態**：BE-Hotfix——於 `pipelines/__init__.py` 末尾補 `from pipelines import resume_pipeline`（觸發 `@PipelineFactory.register('resume')` 惰性註冊），以 `# === [PIPE-RESUME C7-hotfix START/END] ===` 包裹。修復後 `PipelineFactory._registry` 含 `{'resume': ResumePipeline}`、`get_strategy('resume')` 回 `ResumePipeline`；單元測試 15 passed、全套件 480 passed。**最小侵入（單一 import 行）、零業務邏輯改動。**

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C7-hotfix | `pipelines/__init__.py` 補 `from pipelines import resume_pipeline` 觸發策略註冊（修復 NullStrategy 阻斷） | （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/__init__.py` | `.claude-logs/archive/2026-06-04_PIPE-RESUME_C7-hotfix___init__.py.bak` | 末尾補 1 行 `from pipelines import resume_pipeline`（C7-hotfix 標記包裹 + 註解）|

> ⚠️ `.bak` 須在 C7-hotfix `git add` 清單中（§8）。`baton/` 暫存報告於本 hotfix 移出鐵律下移至 `hotfixes/`。

---

## §4 修法說明

### §4.1 `pipelines/__init__.py` — 補策略惰性註冊觸發 import
`# === [PIPE-RESUME C7-hotfix START/END] ===` 包裹，於 `__all__` 之後：
```python
# 惰性註冊觸發：import resume_pipeline 使其 @PipelineFactory.register('resume') 裝飾器執行。
# runtime（web_server `from pipelines import ...`）原本不 import 具體策略 → get_strategy('resume')
# 回 NullStrategy → P1 NotImplementedError 阻斷。於此顯式 import 修復線上策略註冊缺失。
# 後續四路（VISUAL/ACADEMIC/LITEDOC/BOOK）落地時須各補同款 import（見 hotfix 銜接 §1）。
from pipelines import resume_pipeline  # noqa: E402,F401
```

**真因**：`@PipelineFactory.register('resume')` 為**惰性註冊**（裝飾器須在模組被 import 時才執行）。runtime 路徑 `web_server.py:610 from pipelines import Orchestrator, PipelineContext` 執行 `pipelines/__init__.py`，但其原本**未 import 任何具體策略**→ `resume_pipeline` 模組從未載入→裝飾器未執行→註冊表為空→`get_strategy('resume')` 回 `NullStrategy`→`run_phase1` 拋 `NotImplementedError`。

**為何 C6 測試未抓到**：`tests/test_resume_pipeline.py` 顯式 `import pipelines.resume_pipeline`，故測試環境註冊表已填；線上 web_server 不 import，故漏網。此風險**已於 C1 執行報告 §6 標註**（「`__init__.py` 不自動 import 策略——C1 驗收以顯式 import 觸發註冊」），本 hotfix 補上 runtime 接線。

**最小侵入**：僅新增 1 行 import（+ 註解包裹），無 logger、無 DB、無業務邏輯改動。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/__init__.py
?? .claude-logs/archive/2026-06-04_PIPE-RESUME_C7-hotfix___init__.py.bak
# （.claude-logs/baton→hotfixes/ 移出 + prompts/ + TODO.md 改動另計）
```

### §5.2 策略註冊驗證（web_server 同款 import 路徑）
```bash
$ venv/bin/python -c "from pipelines.factory import PipelineFactory; import pipelines; print(PipelineFactory._registry)"
{'resume': <class 'pipelines.resume_pipeline.ResumePipeline'>}
# ✅ 'resume' 已註冊 → get_strategy('resume') 回 ResumePipeline（非 NullStrategy）
```

### §5.3 單元測試 + 全套件防 Regression
```bash
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
15 passed in 0.60s

$ venv/bin/python -m pytest tests/ -q
1 failed, 480 passed, 3 skipped in 49.42s
# 唯一 failed = test_settings_log_format_default_auto（既存環境性 .env LOG_FORMAT=json、非 hotfix Regression）
```

### §5.4 SOP 一致性核查（BE-Hotfix 強制）
- **logging 檢測**（`grep -nE "logger\.error|logger\.exception|traceback.format_exc" pipelines/__init__.py`）：無命中（合規）。
- **database 檢測**（`grep -nE "\.commit\(\)" pipelines/__init__.py`）：無命中（合規）。
- （本 hotfix 僅新增 import 行、無 logger/DB 操作，兩項核查必為空、合規。）

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` 業務代碼 | [x] ✅ 未觸碰 |
| `pipelines/resume_pipeline.py`（C1-C6 業務碼） | [x] ✅ 未變更 |
| `pipelines/factory.py` / `base_strategy.py` / `context.py` / `orchestrator.py` / `contracts.py` | [x] ✅ 未變更 |
| 既有 processors / models / db | [x] ✅ 未觸碰 |
| `pipelines/__init__.py` | [⚠] **本 hotfix 受災點**：僅末尾加 1 行 import（C7-hotfix 標記包裹）；既有 import/`__all__` byte 不動 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態（Hotfix 移出鐵律）**：本執行報告與 hotfix 規劃檔（`C7-hotfix_hotfix.md`）於通過驗證後一次性 `mv` 移出 `baton/` → `hotfixes/` + `git add`（見 §8）。
- **下一步**：待 baron 手動 commit 本 hotfix 並 push 同步至測試機驗證影子 resume pipeline 正常分派至 ResumePipeline 四 Phase；**嚴禁自發續跑後續 Check**。
- **消化歸檔之 baton 檔**：`C7-hotfix_hotfix.md` + `C7-hotfix_執行.md` → `hotfixes/`。
- **架構待辦（見 hotfix 銜接 §1）**：後續四路（PIPE-VISUAL/ACADEMIC/LITEDOC/BOOK）落地時須各補同款 `__init__.py` import，或收斂為集中註冊區（屬後續任務）。
- **回退方式（Rollback）**：`git revert <C7-hotfix hash>`；或 `cp .claude-logs/archive/2026-06-04_PIPE-RESUME_C7-hotfix___init__.py.bak pipelines/__init__.py`。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單
git add pipelines/__init__.py
git add .claude-logs/archive/2026-06-04_PIPE-RESUME_C7-hotfix___init__.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/hotfixes/2026-06-04_PIPE-RESUME_C7-hotfix_hotfix.md
git add .claude-logs/hotfixes/2026-06-04_PIPE-RESUME_C7-hotfix_執行.md
git add .claude-logs/prompts/

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C7-hotfix_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C7-hotfix_msg.txt
```

### §8.2 commit message 草稿

（草稿已寫入 `/tmp/PIPE-RESUME_C7-hotfix_msg.txt`）

```
BE-Hotfix: PIPE-RESUME C7-hotfix — 策略註冊缺失與加載鏈修復

修復因 pipelines/__init__.py 缺少對 resume_pipeline 的顯式導入，導致
PipelineFactory 自動註冊裝飾器未執行、上傳影子測試觸發 NullStrategy 哨兵的阻斷 Bug。
於 pipelines/__init__.py 補上 import resume_pipeline，並以 [C7-hotfix] 註解包裹。
單元測試與 factory._registry 驗證通過。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C7-hotfix 策略註冊缺失修復與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/ → 通過驗證後移出 hotfixes/ 入版控 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | hotfixes/ 歸檔 / Antigravity 驗證 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；BE-Hotfix 最小侵入、嚴禁夾帶無關改動 |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 hotfixes/，不刪除 |
| **重複防護** | 本檔為 C7-hotfix 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-04)：C7-hotfix 執行完畢——`pipelines/__init__.py` 補 `from pipelines import resume_pipeline` 觸發 `@register('resume')`，修復 runtime 策略註冊缺失致影子 resume pipeline P1 NullStrategy NotImplementedError 阻斷。factory._registry 含 'resume' 驗證通過、test_resume_pipeline 15 passed、全套件 480 passed（唯一 failed 為既存環境性、非 Regression）。最小侵入單行 import、零業務邏輯改動。
