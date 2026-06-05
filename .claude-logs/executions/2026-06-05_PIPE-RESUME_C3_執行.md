# PIPE-RESUME C3 — P2 步序與讀取對齊 執行報告

---

**任務代號**：PIPE-RESUME C3（v9 整合批次）
**執行日期**：2026-06-05
**依據規劃**：`.claude-logs/baton/2026-06-01_PIPE-RESUME_ResumePipeline策略管線_plan_v1.md`（§99.2 v11）
**次級參考**：`.claude-logs/baton/2026-06-05_PIPE-RESUME_ResumePipeline策略管線_tasks.md` §8 C3
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed (Commit C3)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：C2 後；`run_phase2` 步序為 ①LCC→②摘要、`raw_domain` 讀 `self._raw_meta`（C2 雙寫過渡）。
- **完成狀態**：① **步序互換**——`run_phase2` 改為 **①做摘要（前置）→ ②LCC 分類**（v10 摘要先行、跨路統一；兩者互不依賴、功能等價）；② **改讀 raw_metadata**——`raw_domain` 改 `self._meta_value(ctx.raw_metadata, "domain")`（C2 穿線載體）；③ **廢除 `self._raw_meta`**——移除 `__init__`（無實例狀態）與 `run_phase1` 過渡雙寫、docstring 同步，以 `ctx.raw_metadata` 為唯一載體。全變更 `# === [PIPE-RESUME v9 C3 START/END] ===` 包裹。

> **⚠️ 計畫內測試紅燈（C3→C6 序、待 C6 修復）**：C3 物理防線限定僅改 `resume_pipeline.py`、**不得改 tests**；既有 `tests/test_resume_pipeline.py` 有 5 處引用已廢的 `self._raw_meta`，其中 **2 個測試在 C3 後紅燈**（`test_run_phase1_contract` 斷言 `s._raw_meta`；`test_run_phase2_flag_off` 設 `s._raw_meta` 已失效致 lcc 回 general）。**此為 baron 規劃的 C3（廢 _raw_meta）→ C6（更新測試讀 ctx.raw_metadata）序的預期結果**，C6 落地後即綠。其餘全套件（478 passed、核心 pipelines 25 passed）不受影響。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | `run_phase2` ①摘要→②LCC 互換 + raw_domain 改讀 ctx.raw_metadata + 廢除 self._raw_meta（__init__/run_phase1/docstring）| （留空，由 baron 回填） |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-06-05_PIPE-RESUME_C3_resume_pipeline.py.bak` | run_phase2 步序互換+改讀；移除 __init__/run_phase1 的 _raw_meta；docstring 同步（v9 C3 標記）|

> ⚠️ `.bak` 須在 C3 `git add` 清單（§8）。**執行報告本體不 git add**（依指令）。

---

## §4 修法說明

### §4.1 `run_phase2` 步序互換 + 改讀（v9 C3 標記）
```python
# === [PIPE-RESUME v9 C3 START] ===
raw_domain = (self._meta_value(ctx.raw_metadata, "domain") or "") if ctx.raw_metadata else ""
abstract = self._make_summary(full_text) or full_text[:_ABSTRACT_FALLBACK_CHARS]  # ① 摘要先行（v10）
lcc = normalize_to_lcc(raw_domain, context_text=full_text) or "general"           # ② LCC
# === [PIPE-RESUME v9 C3 END] ===
```
- **步序**：①摘要前置於②LCC（v10 跨路統一）；摘要吃 full_text、LCC 吃 raw_domain+full_text，**互不依賴、輸出不變**（③Glossary/④翻摘要仍需兩者皆備）。
- **讀取**：`raw_domain` 改讀 `ctx.raw_metadata`（C2 寫入的整包 metadata、結構 `{domain:{value,...}}`，故經 `_meta_value` 取 value）。

### §4.2 廢除 `self._raw_meta`（v9 C3 標記）
- `__init__`：移除（唯一作用是初始化 `_raw_meta`、現無實例狀態）→ 以 v9 C3 註解標記。
- `run_phase1`：移除過渡雙寫 `self._raw_meta = {...}` → v9 C3 註解標記。
- docstring（模組頂 + run_phase1）：更新為「整包 metadata 走 `ctx.raw_metadata`、`_raw_meta` 已廢」。
- grep 確認：`self._raw_meta =`/`.get`/`[` 程式碼引用 **0**；`hasattr(s,'_raw_meta')==False`。

---

## §5 測試結果

### §5.1 本地改動狀態確認
```bash
$ git status -s
 M pipelines/resume_pipeline.py
?? .claude-logs/archive/2026-06-05_PIPE-RESUME_C3_resume_pipeline.py.bak
# （baton/ 報告 + prompts/ + TODO.md 另計；無其他越界變動）
```

### §5.2 §6.3 驗收
```
class= ResumePipeline   has _raw_meta attr? False        # 實例屬性已廢
✅ self._raw_meta 程式碼引用 0
摘要先行：L307-308 ①摘要 → L310-311 ②LCC
```

### §5.3 測試（含計畫內紅燈說明）
```bash
$ pytest tests/test_pipe_core.py tests/test_pipe_scaffold.py -q
25 passed in 0.59s                                        # 核心 pipelines 不受影響

$ pytest tests/ -q
3 failed, 478 passed, 3 skipped
# (1) test_settings_log_format_default_auto —— 既存環境性 .env LOG_FORMAT=json、非本批次
# (2) test_run_phase1_contract —— 斷言已廢的 s._raw_meta（AttributeError）→ 【C3→C6 計畫內、C6 改測試讀 ctx.raw_metadata 即綠】
# (3) test_run_phase2_flag_off —— 設 s._raw_meta 已失效、lcc 回 general → 【同上、C6 改測試以 ctx.raw_metadata 設 domain 即綠】
```

> **紅燈裁定**：(2)(3) 屬 baron 規劃的 C3（廢 _raw_meta）→ C6（更新測試）序之**預期暫態**；C3 物理防線禁改 tests，故無法於本 commit 修。C6（本批次）將把測試的 `s._raw_meta=...` 改為 `ctx.raw_metadata=...`、斷言改 ctx，恢復全綠。

### §5.4 SOP 一致性核查（BE-Refactor）
- **logging 檢測**：C3 無新增 `logger.error`/`traceback.format_exc`（合規）。
- **database 檢測**：C3 無 DB 操作（純步序/讀取源/實例屬性移除，無 commit/session.begin）（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` / `processor/*` | [x] ✅ 未觸碰 |
| `pipelines/context.py` / `contracts.py` / `factory.py` / `orchestrator.py` | [x] ✅ 未變更（C3 僅改 resume_pipeline.py）|
| `run_phase1`（除移除 _raw_meta 雙寫）/ `run_phase3` / `run_phase4` | [x] ✅ 核心邏輯未動 |
| `tests/*` | [x] ✅ 未觸碰（C3 物理防線；測試更新屬 C6）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

---

## §7 銜接

- **baton/ 狀態**：C3 執行報告暫存 baton/、不入版控，待 C7 收官歸檔。
- **下一步**：tasks.md C4 — P3 Business Constraints（`run_phase3` 加 `InjectionContext.constraints`）；由 baron 另行下達。**C6 將修復本 C3 的 2 個計畫內測試紅燈。**
- **消化歸檔之 baton 檔**：無。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 .bak）

# 2. git add 清單（代碼 + .bak + TODO/prompts；執行報告本體不 add）
git add pipelines/resume_pipeline.py
git add .claude-logs/archive/2026-06-05_PIPE-RESUME_C3_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-05_PIPE-RESUME_C3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-RESUME_C3_msg.txt）

# 4. baron 手動執行
git commit -F /tmp/PIPE-RESUME_C3_msg.txt
```

### §8.2 commit message 草稿

```
BE-Refactor: PIPE-RESUME C3 — P2 步序與讀取對齊 (摘要先行與 raw_metadata 讀取)

於 run_phase2 將步序互換，改為做摘要前置於 LCC 分類（摘要先行以消除自癒依賴）；
將 raw_domain 的讀取源改為 ctx.raw_metadata，並徹底廢除 self._raw_meta
實例暫存。全變更以大改版註解包裹，完成 C2 過渡期防護的完全收斂。

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 PIPE-RESUME C3 代碼變更與驗收，作為 Traceability 審計依據 |
| **用途** | 暫存 baton/；C7 收官 mv 歸檔 executions/ |
| **權威源** | 本檔 §1–§8 |
| **引用方** | C7 收官 Check |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | C3 限改 resume_pipeline.py；嚴禁改 tests（屬 C6）/自動 commit；執行報告不入 git |
| **改版觸發條件** | 執行報告錯誤修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/ |
| **重複防護** | 本檔為 C3 執行唯一源 |

### §99.2 Revision 歷程

- v1 (2026-06-05)：C3 執行完畢——run_phase2 ①摘要→②LCC 互換（v10 跨路統一、功能等價）+ raw_domain 改讀 ctx.raw_metadata + 徹底廢除 self._raw_meta（__init__/run_phase1/docstring）。核心 pipelines 25 passed；全套件 478 passed / 3 failed（1 既存環境性 + 2 計畫內 _raw_meta 測試紅燈、待 C6 更新測試修復）。
