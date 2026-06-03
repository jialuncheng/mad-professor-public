# DOMAIN-NORM C3 — Entry & Feature Flag（單一入口與熱插拔旗標）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | DOMAIN-NORM C3 |
| **執行日期** | 2026-06-03 |
| **依據規劃** | `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` §8 C3 |
| **次級參考** | plan v2 §2 U3/U4 / PIPE-SPEC §1.2.1 / PIPE master v10 L69 / logging_SOP |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`125af97`（BE-Refactor: DOMAIN-NORM C2 — Normalizer Core）
- **完成狀態**：C3 擴充公開入口 + 旗標落地 worktree，旗標 ON/OFF 雙路徑功能測試 + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C3 | `待 baron 回填` | BE-Refactor: DOMAIN-NORM C3 — Entry & Feature Flag (單一入口與熱插拔旗標) |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `settings.py` | +8 行（`LLM_USE_GLOSSARY_ALIGN` 旗標，`=== [DOMAIN-NORM C3 START/END] ===` 包裹） | 改前 `.bak`；既有 env byte 不動 |
| `processor/domain_normalizer.py` | +模組級 `normalize_to_lcc` 公開入口 + `_get_normalizer` 惰性單例（C3 標記包裹） | C2 新建未版控檔，無需 `.bak`；C2 既有 class byte 不動 |
| `.claude-logs/archive/2026-06-03_DOMAIN-NORM_C3_settings.py.bak` | 新增（改前備份） | 納入 git add（審計存檔） |
| `.claude-logs/baton/2026-06-03_DOMAIN-NORM_C3_執行.md` | 本報告 | **暫存 baton/，不入 git**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C3→✅ / C4→🟡 WIP + C2 Hash 自癒（`待 baron 回填`→`125af97`） | — |
| `.claude-logs/prompts/2026-06-03_DOMAIN-NORM_C3_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git diff --stat settings.py`：
```
 settings.py | 8 ++++++++
 1 file changed, 8 insertions(+)
```

## §4 修法說明

### §4.1 `settings.py` 新增熱插拔旗標（防線 3、C3 標記包裹）
```python
# === [DOMAIN-NORM C3 START] ===
# DOMAIN-NORM：領域標準化對齊器（DomainNormalizer）熱插拔旗標。
# False（預設）→ normalize_to_lcc 走舊行為：直接回傳 raw_domain，不查 DB、不呼 LLM、零風險。
# True → 啟用 LLM 內容判定 + Domains/DomainMapping 動態註冊與快取（plan v2 U1/U4）。
LLM_USE_GLOSSARY_ALIGN = os.getenv("LLM_USE_GLOSSARY_ALIGN", "false").lower() in ("1", "true", "yes")
# === [DOMAIN-NORM C3 END] ===
```
- 對齊既有 env 風格（`os.getenv` + 預設字串解析）；置於 `LLM_MAX_CONCURRENT` 之後（LLM 設定區）。

### §4.2 `processor/domain_normalizer.py` 暴露單一公開入口（防線 2、C3 標記包裹）
```python
# === [DOMAIN-NORM C3 START] ===
_normalizer_singleton: Optional[DomainNormalizer] = None

def _get_normalizer() -> DomainNormalizer:
    global _normalizer_singleton
    if _normalizer_singleton is None:
        _normalizer_singleton = DomainNormalizer()
    return _normalizer_singleton

def normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode:
    if not settings.LLM_USE_GLOSSARY_ALIGN:
        return raw_domain                                   # 舊行為：原樣回傳、不查 DB/不呼 LLM
    return _get_normalizer().normalize(raw_domain, context_text)
# === [DOMAIN-NORM C3 END] ===
```
- **簽名逐字對齊**：`normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode` 與 PIPE-SPEC §1.2.1（L74）、PIPE master v10（L69）完全一致（grep 雙向比對見 §5.2）。
- **惰性單例**：`_get_normalizer` 僅在旗標 True 首次呼叫時才實例化 `DomainNormalizer`（連帶 `LLMClient` / DB），避免旗標 OFF 時的 import/呼叫期副作用 → 預設零風險（plan U4）。

## §5 測試結果

### §5.1 §6.3 grep 驗收（真實輸出節錄）
```
$ grep -nE "def normalize_to_lcc|LLM_USE_GLOSSARY_ALIGN" processor/domain_normalizer.py settings.py
processor/domain_normalizer.py:205:def normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode:
processor/domain_normalizer.py:212:    if not settings.LLM_USE_GLOSSARY_ALIGN:
settings.py:74:LLM_USE_GLOSSARY_ALIGN = os.getenv("LLM_USE_GLOSSARY_ALIGN", "false").lower() in ("1", "true", "yes")
```

### §5.2 簽名逐字對齊驗證（雙向 grep）
```
$ grep -n "normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode" processor/domain_normalizer.py
205:def normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode:
$ grep -rn "normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode" baton/...PIPE-SPEC...
74:DomainNormalizer.normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode
$ grep -rn "normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode" baton/...plan_v10.md
69:- **DomainNormalizer**：單一入口 normalize_to_lcc(raw_domain: str, context_text: str | None = None) -> LCCCode；...
```
→ 三處逐字一致。

### §5.3 旗標 OFF 路徑（原樣回傳、不查 DB/不呼 LLM、單例不建）
```
$ venv/bin/python -c "<settings.LLM_USE_GLOSSARY_ALIGN=False; normalize_to_lcc('應用數學 - 拓樸學', 'Python LLM')>"
flag OFF → '應用數學 - 拓樸學'
singleton 未實例化（旗標 off 不建）: True
```

### §5.4 旗標 ON 路徑（委派 DomainNormalizer.normalize）
```
$ venv/bin/python -c "<settings.LLM_USE_GLOSSARY_ALIGN=True; _normalizer_singleton=FakeNorm(); normalize_to_lcc('應用數學','topology')>"
flag ON → 'QA'
```

### §5.5 settings 預設值驗證
```
$ venv/bin/python -c "import importlib, settings; importlib.reload(settings); print(settings.LLM_USE_GLOSSARY_ALIGN)"
LLM_USE_GLOSSARY_ALIGN = False
```

### §5.6 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 448 passed, 3 skipped in 41.70s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json` override 預設 `auto`），與 C3 無關。

### §5.7 SOP 一致性核查（WORKFLOW_SOP §5）
- **database §5.2**：C3 無新增任何 `.commit()` / session 操作（交易語意全在 C2）→ 無命中（合規）。
- **logging §5.1**：C3 無新增 logger 呼叫（公開入口為純分派邏輯）→ 無命中（合規）。

## §6 不可動清單遵守

- [x] `models.py` `Paper` 表 — **未觸碰**。
- [x] `processor/domain_detector.py` `detect` — **未觸碰**。
- [x] `rag_retriever.py` — **未觸碰**。
- [x] `processor/translate_processor.py` — **未觸碰**（接線屬後續路次 plan）。
- [x] `settings.py` 既有 env — **byte 不動**（`git diff` 僅末段新增 8 行）。
- [x] C2 既有 `DomainNormalizer` class — **byte 不動**（C3 僅在檔末追加模組級函式）。
- [x] 主 repo 目錄 — **未讀寫**。
- [x] baton/ 暫存 — 本報告留 baton/，**未提前 mv/git add**。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：`2026-06-03_DOMAIN-NORM_C3_執行.md` 暫存 baton/，連同 C1/C2 報告 + plan_v2 + tasks 待 C5 收官一次性歸檔。
- **下一步**：C4 — Unit Tests：`tests/test_domain_normalizer.py` 4 測試（內容分類 HF/QA / 冷門動態註冊不塞單字 / 快取命中 0 API / 旗標 off 保舊行為），mock LLM + in-memory SQLite 隔離。待 baron 確認 C3 後另行下達。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-03_DOMAIN-NORM_C3_settings.py.bak

# 2. git add 清單（明確列檔，嚴禁 git add -A/.；baton/ 報告不入 git）
git add settings.py
git add processor/domain_normalizer.py
git add .claude-logs/archive/2026-06-03_DOMAIN-NORM_C3_settings.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_DOMAIN-NORM_C3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-03_DOMAIN-NORM_C3_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/DOMAIN-NORM_C3_msg.txt）
cat /tmp/DOMAIN-NORM_C3_msg.txt

# 4. baron 手動執行
git commit -F /tmp/DOMAIN-NORM_C3_msg.txt
```
