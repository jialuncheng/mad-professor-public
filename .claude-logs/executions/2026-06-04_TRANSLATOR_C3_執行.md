# TRANSLATOR C3 — Dual-Mode Routing & Thinking（雙模式路由與思考受控擴充）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | TRANSLATOR C3 |
| **執行日期** | 2026-06-04 |
| **依據規劃** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` §8 C3 |
| **次級參考** | plan v10 §2 U3 / model_recommendations.md §1.1 / plan §7 Q3 前向相容 / §4 唯一受控例外 |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`27db830`（BE-Refactor: C2 — Prompt Engine）
- **完成狀態**：C3 於 `settings.py`/`llm/client.py`/`processor/translator.py` 三檔落地雙模式路由 + thinking_config 受控擴充，py_compile + 雙模式功能測試 + 前向相容 gating 測試 + 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C3 | `待 baron 回填` | BE-Refactor: C3 — Dual-Mode Routing & Thinking（雙模式路由與思考受控擴充） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `settings.py` | C3 標記：`LLM_THINKING_BUDGET`（預設 0）+ `TRANSLATE_MODEL` 預設 `gemini-2.0-flash`→`gemini-3.5-flash`（對齊 SOP §1.1）；先 `.bak` | env 仍可覆寫 |
| `llm/client.py` | C3 標記：模組級 `_supports_thinking`（前向相容白名單）+ `chat()` 補 `thinking_budget` 參數與 `thinking_config` 注入分支；先 `.bak` | **§4 唯一受控例外**；`_api_semaphore`/retry/既有路徑不動 |
| `processor/translator.py` | C3 標記：`Translator.translate(text,ctx,mode,text_type)` 雙模式 chat 路由；先 `.bak` | 對齊 PIPE-SPEC §1.2.3 v3 |
| `.claude-logs/archive/2026-06-04_TRANSLATOR_C3_{settings,client,translator}.py.bak` | 改前備份（3 份） | **納入 git add** |
| `.claude-logs/baton/2026-06-04_TRANSLATOR_C3_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C3→✅ / C4→🟡 WIP + C2 Hash 自癒（`待 baron 回填`→`27db830`） | — |
| `.claude-logs/prompts/2026-06-04_TRANSLATOR_C3_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git status -s`：
```
 M llm/client.py
 M processor/translator.py
 M settings.py
```

## §4 修法說明

### §4.1 `settings.py`（C3 標記）
```python
# === [TRANSLATOR C3 START] ===
TRANSLATE_MODEL = os.getenv("LLM_TRANSLATE_MODEL", "gemini-3.5-flash")   # 預設對齊 SOP §1.1
LLM_THINKING_BUDGET = int(os.getenv("LLM_THINKING_BUDGET", "0"))         # 0=關閉
# === [TRANSLATOR C3 END] ===
```
- 預設改 3.5-flash：否則 DEEP_THINK 因 gating（思考世代模型）不成立而靜默退化 NORMAL（plan §2 U3）。

### §4.2 `llm/client.py`（C3 標記、§4 唯一受控例外）
```python
# 模組級前向相容判定（plan §7 Q3、非硬編碼單一 "3.5"）
_THINKING_MODEL_MARKERS = ("2.5", "3.5", "4.0", "4.5", "thinking")
def _supports_thinking(model): return any(mk in (model or "").lower() for mk in _THINKING_MODEL_MARKERS)

def chat(self, messages, temperature=0.5, stream=True, model=None, thinking_budget=0):
    ...
    config_kwargs = dict(temperature=temperature, system_instruction=system_instruction)
    if thinking_budget and thinking_budget > 0 and _supports_thinking(model):
        try:
            config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)
        except Exception:
            logging.getLogger(__name__).warning("[thinking] 注入失敗、降級無思考 model=%s", model)
    config = types.GenerateContentConfig(**config_kwargs)
```
- **範圍嚴格限此一分支**：`_api_semaphore` 並發鎖、`retry` 機制、既有 `temperature`+`system_instruction` 路徑**一律不動**；`thinking_budget=0`（預設）時 `config_kwargs`={temperature, system_instruction} → **byte 等價舊行為**。
- **前向相容**：`_supports_thinking` 正向白名單涵蓋 2.5/3.5/4.0 思考世代（優於 SOP 範例的單 `"3.5"`）；`try/except` 降級防 SDK/模型不支援崩潰。

### §4.3 `processor/translator.py`（C3 標記、translate 雙模式路由）
```python
def translate(self, text, ctx, mode, text_type="content"):
    from llm.client import LLMClient  # 惰性 import 防循環依賴
    llm = self.llm or LLMClient.get_instance()
    messages = [{"role":"system","content":self._build_system_prompt(ctx,text_type)},
                {"role":"user","content":self._build_user_prompt(text,ctx,text_type)}]
    thinking_budget = settings.LLM_THINKING_BUDGET if mode == TranslateMode.DEEP_THINK else 0
    return llm.chat(messages, stream=True, model=settings.TRANSLATE_MODEL, thinking_budget=thinking_budget).strip()
```
- 模式→budget 路由：DEEP_THINK 啟用 `settings.LLM_THINKING_BUDGET`、NORMAL=0；分行容錯屬 C4。

## §5 測試結果

### §5.1 §6.3 grep 驗收（真實輸出節錄）
```
$ grep -nE "LLM_THINKING_BUDGET" settings.py llm/client.py processor/translator.py
settings.py:12:LLM_THINKING_BUDGET = int(os.getenv("LLM_THINKING_BUDGET", "0"))
processor/translator.py:178: ... settings.LLM_THINKING_BUDGET if mode == TranslateMode.DEEP_THINK else 0
$ grep -nE "thinking_config|ThinkingConfig|_supports_thinking|TRANSLATOR C3" llm/client.py  → 命中
```

### §5.2 py_compile + 雙模式路由功能測試（mock chat 攔 thinking_budget）
```
NORMAL budget=0: True | model= gemini-3.5-flash
DEEP_THINK budget=2048: True
strip: '譯文'
settings TRANSLATE_MODEL 預設: gemini-3.5-flash
```

### §5.3 _supports_thinking 前向相容驗證
```
gemini-2.0-flash: False    gemini-3.5-flash: True    gemini-2.5-pro: True
gemini-4.0-flash: True     x-thinking: True
```
→ 涵蓋 2.5/3.5/4.0 思考世代（解 plan §7 Q3「`"3.5"` 排除 2.5/4.0」之慮）。

### §5.4 byte 等價（thinking_budget=0 預設）
```
thinking_budget 預設 0: True
budget=0 不注入 thinking_config（gating budget>0）: True
```
→ 既有 chat caller（不傳 budget）走 `config_kwargs={temperature, system_instruction}`、與舊版識別一致。

### §5.5 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 457 passed, 3 skipped in 43.85s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C3 無關。
- 457 passed 含全部 llm/client 相關測試，證明 chat() 受控擴充對既有 caller 零破壞。

### §5.6 database SOP 核查
- 三檔均無 `.commit()`/session 操作（C3 純路由/config）→ 無命中（合規）。

## §6 不可動清單遵守

- [x] A 軌 `pipeline_core.py` / `translate_processor.py` — **未觸碰**。
- [x] `llm/client.py` `_api_semaphore`/`retry`/既有 config 路徑 — **未動**（僅加 thinking_config 分支，§4 唯一受控例外、明確界定範圍）。
- [x] `models.py` / `Domains` — **未觸碰**。
- [x] `prompt/translate/` — **未觸碰**（C2 已建 caption）。
- [x] PIPE-CORE 四合約 / DOMAIN-NORM / GLOSSARY-CORE — **未觸碰**。
- [x] C1/C2 既有 InjectionContext/TranslateMode/Prompt Engine — **byte 不動**（C3 僅加 translate 方法 + import）。
- [x] 主 repo 目錄 — 未讀寫；baton/ 報告留暫存、未提前 mv/git add。

> 註：`settings.TRANSLATE_MODEL` 預設由 `gemini-2.0-flash`→`gemini-3.5-flash` 為 baron C3 提示詞明列指示（對齊 SOP §1.1）；A 軌 `translate_processor` 經 `config.TRANSLATE_MODEL` 亦受此預設影響，env 可覆寫回舊值。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：本報告 `2026-06-04_TRANSLATOR_C3_執行.md` 暫存 baton/、**不入版控**，待 C5 收官一次性歸檔。
- **下一步**：C4 — Formatting Fallback & Tests（`Translator.translate` 末加 U4 多行 `re.sub` 兜底 + `tests/test_translator.py` 8 測試）。待 baron 確認 C3 後另行下達。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：3 份 .bak（settings/client/translator）

# 2. git add 清單（明確列檔、baton/ 報告不入 git）
git add settings.py
git add llm/client.py
git add processor/translator.py
git add .claude-logs/archive/2026-06-04_TRANSLATOR_C3_settings.py.bak
git add .claude-logs/archive/2026-06-04_TRANSLATOR_C3_client.py.bak
git add .claude-logs/archive/2026-06-04_TRANSLATOR_C3_translator.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-04_TRANSLATOR_C3_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-04_TRANSLATOR_C3_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/TRANSLATOR_C3_msg.txt）
cat /tmp/TRANSLATOR_C3_msg.txt

# 4. baron 手動執行
git commit -F /tmp/TRANSLATOR_C3_msg.txt
```
