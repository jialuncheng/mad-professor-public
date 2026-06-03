# DOMAIN-NORM C2 — Normalizer Core（對齊器核心邏輯）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | DOMAIN-NORM C2 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` §8 C2 |
| **次級參考** | plan v2 §2 U1/U2 / database_SOP 原則 1+2 / logging_SOP / PIPE-SPEC §1.2.1 |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`8d4f75f`（BE-Refactor: DOMAIN-NORM C1 — Database Schema）
- **完成狀態**：C2 新建 `processor/domain_normalizer.py` 落地 worktree，import + 功能 smoke test + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C2 | `待 baron 回填` | BE-Refactor: DOMAIN-NORM C2 — Normalizer Core (對齊器核心邏輯) |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `processor/domain_normalizer.py` | **新建**（約 195 行） | C2 核心類；**未對外接線**（公開入口屬 C3） |
| `.claude-logs/baton/2026-06-03_DOMAIN-NORM_C2_執行.md` | 本報告 | **暫存 baton/，不入 git**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C2→✅ / C3→🟡 WIP + C1 Hash 自癒（`待 baron 回填`→`8d4f75f`） | — |
| `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_C2_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

- **備份**：本 Commit 為純新建檔案、**無修改任何既有檔案**，故無 `.bak` 備份。
- **包裝標記**：本 Commit 無修改既有原始碼，故無 `=== [DOMAIN-NORM C2 START/END] ===` 標記（防線 1 僅在改既有檔時觸發）。

`git diff --stat`（未追蹤新檔，以 `git status -s` 呈現）：
```
?? processor/domain_normalizer.py
```

## §4 修法說明

依 tasks §8 C2，新建 `processor/domain_normalizer.py`，定義 `DomainNormalizer` 類，內部四階段對齊流程：

### §4.1 型別與哨兵
```python
LCCCode = str                 # LCC 主類代碼型別別名（C3 公開入口共用）
DEFAULT_LCC: LCCCode = "general"   # 降級哨兵（plan §7 Q1）
_LCC_RE = re.compile(r"^[A-Za-z]{1,3}$")   # LCC 1-3 字母硬限（plan §7 Q2）
```

### §4.2 ① 快取查（read-only、極短 session）
```python
def _cache_lookup(self, raw_key):
    with self._session_factory() as session:
        row = session.get(DomainMapping, raw_key)
        return row.lcc_code if row is not None else None
```

### §4.3 ② LLM 內容判定（**交易外**、不持有 session）
- System Instruction 定義 LCC 收斂規則：履歷按**實質專業技能**（行銷→HF、AI→QA）而非文件類型；冷門領域給最近 LCC（古生物→QE）；格式 `CODE|Name`；無法判斷回 `general|General`。
- `temperature=0.0` + `stream=False` + `model=settings.LLM_DOMAIN_MODEL`（複用既有 cheap domain 模型）。
- 解析 `_parse_llm_result`：取首行 `CODE|Name`、`code.upper()` 後過 `_LCC_RE` 驗證，格式不符回 `None`。

### §4.4 ③+④ 動態註冊 + 寫回（取得代碼後才開極短交易、冪等 upsert）
```python
def _register_and_cache(self, raw_key, lcc, name):
    with self._session_factory() as session:
        with session.begin():        # 成功自動 commit / 失敗自動 rollback
            session.execute(
                sqlite_insert(Domains).values(lcc_code=lcc, name=name)
                .on_conflict_do_nothing(index_elements=["lcc_code"]))   # 不塞單字
            session.execute(
                sqlite_insert(DomainMapping).values(raw_key=raw_key, lcc_code=lcc)
                .on_conflict_do_nothing(index_elements=["raw_key"]))    # 併發冪等
```

### §4.5 主流程 `normalize`（C2 內部入口；C3 公開 `normalize_to_lcc` 包旗標後委派此處）
- 順序嚴格：正規化鍵 → ① 快取命中即回 → ② **LLM（交易外）** → ③+④ 極短交易寫表 → 回 lcc。
- 全程 `try/except`，任何異常 `logger.error(..., exc_info=True)` 後降級 `DEFAULT_LCC`，不阻斷。

### §4.6 交易邊界鐵律（防線 2）落實
`_llm_classify`（外部 API）在 `normalize` 中於**任何 `session.begin()` 之外**完成；唯有取得 `(lcc, name)` 後才進入 `_register_and_cache` 的極短交易 → SQLite 寫鎖持有時間僅兩條 INSERT，杜絕 `database is locked`。

## §5 測試結果

### §5.1 §6.2 grep 驗收（真實輸出節錄）
```
$ grep -nE "class DomainNormalizer|on_conflict_do_nothing|temperature|session.begin" processor/domain_normalizer.py
64:class DomainNormalizer:
120:            temperature=0.0,
136:            with session.begin():
141:                    .on_conflict_do_nothing(index_elements=["lcc_code"])
147:                    .on_conflict_do_nothing(index_elements=["raw_key"])
```

### §5.2 import 檢測（C2 公開符號齊全；normalize_to_lcc 應缺席 = C3）
```
$ venv/bin/python -c "from processor.domain_normalizer import DomainNormalizer, LCCCode, DEFAULT_LCC; print('C2 import OK', DEFAULT_LCC)"
C2 import OK general
$ venv/bin/python -c "from processor.domain_normalizer import normalize_to_lcc"
ImportError: cannot import name 'normalize_to_lcc' ...   # 預期（屬 C3）
```

### §5.3 功能 smoke test（mock LLM + in-memory SQLite，含 FK ON、create_all 建表）
```
r1: QA | llm calls: 1                     # 首查：未命中→LLM→註冊+快取
r2: QA | llm calls (應仍為1): 1            # 再查：快取命中、0 API
Domains: [('QA', 'Mathematics')]          # 動態註冊（僅領域空間、無單字）
DomainMapping: [('應用數學 - 拓樸學', 'QA')]  # raw→lcc 快取寫回
empty: general                            # 空 raw → 降級
bad-format: general                       # LLM 格式錯 → 降級
```
- 驗證 `temperature == 0.0` 由 mock 內 assert 強制；通過。
- 確認 `_register_and_cache` 透過 `session.begin()` 寫入兩表成功（FK domains→ok）。

### §5.4 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 448 passed, 3 skipped in 37.53s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json` override 預設 `auto`），與 C2（純新增未接線模組）**無關**。

### §5.5 SOP 一致性核查（WORKFLOW_SOP §5）
- **database §5.2**：無裸 commit（僅 `with session.begin():` 上下文、無顯式 `.commit()`）→ **無命中（合規）**。
- **logging §5.1**：`logger.error("[domain-norm] 對齊失敗...", exc_info=True)`（L186-188）→ 含 `exc_info=True`，**合規**。

## §6 不可動清單遵守

- [x] `models.py` `Paper` 表 — **未觸碰**（C2 僅 import `Domains`/`DomainMapping`）。
- [x] `processor/domain_detector.py` `detect` — **未觸碰**（C2 僅讀其輸出概念，無 import 改動）。
- [x] `rag_retriever.py` — **未觸碰**。
- [x] `processor/translate_processor.py` — **未觸碰**（接線屬後續路次 plan）。
- [x] 僅**新增** `processor/domain_normalizer.py`，無改任何既有檔（防線 4 ✅）。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_DOMAIN-NORM_C2_執行.md` 暫存 baton/，連同 C1 報告 + plan_v2 + tasks 待 C5 收官一次性歸檔。
- **下一步**：C3 — Entry & Feature Flag：在 `domain_normalizer.py` 補模組級公開入口 `normalize_to_lcc(raw_domain, context_text=None) -> LCCCode`（旗標 False 走舊 raw 直注、不查 DB/不呼 LLM；True 委派 `DomainNormalizer.normalize`）+ `settings.LLM_USE_GLOSSARY_ALIGN`（預設 False、先 `.bak`）。待 baron 確認 C2 後另行下達。

## §8 baron 執行命令

```bash
# 1. 本 Commit 無修改既有檔，故無備份
# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add processor/domain_normalizer.py
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_DOMAIN-NORM_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_DOMAIN-NORM_C2_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/DOMAIN-NORM_C2_msg.txt）
cat /tmp/DOMAIN-NORM_C2_msg.txt

# 4. baron 手動執行
git commit -F /tmp/DOMAIN-NORM_C2_msg.txt
```
