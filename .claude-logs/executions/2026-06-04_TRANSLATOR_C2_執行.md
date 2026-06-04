# TRANSLATOR C2 — Prompt Engine（提示詞與約束動態注入）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | TRANSLATOR C2 |
| **執行日期** | 2026-06-04 |
| **依據規劃** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` §8 C2 |
| **次級參考** | plan v10 §2 U2 / 既有 `translate_processor.py`（style_hints/用戶提示詞範式）/ §4 不可動 |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`1558f79`（BE-Refactor: C1 — Contract & Context）
- **完成狀態**：C2 於 `processor/translator.py` 補 `Translator` 類 + Prompt Engine + 新建 `prompt/translate/caption_translate_prompt.txt`，落地 worktree，py_compile + 功能測試（五步系統提示詞/路由/旗標閘門/用戶提示詞）+ 全套件 pytest 通過（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C2 | `待 baron 回填` | BE-Refactor: C2 — Prompt Engine（提示詞與約束動態注入） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `processor/translator.py` | C2 兩塊（`# === [TRANSLATOR C2 START/END] ===`）：① import logging/settings + 提示詞路徑常數 + `_STYLE_HINTS`；② `Translator` 類（`_read_file`/`_build_system_prompt`/`_build_user_prompt`） | C1 既有 InjectionContext/TranslateMode byte 不動 |
| `prompt/translate/caption_translate_prompt.txt` | **新建**（圖說專屬提示詞、保留 Figure/Table 編號與標點） | §4 准新增（非改既有 title/content 檔） |
| `.claude-logs/archive/2026-06-04_TRANSLATOR_C2_translator.py.bak` | 新建（改前備份） | **納入 git add** |
| `.claude-logs/baton/2026-06-04_TRANSLATOR_C2_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C2→✅ / C3→🟡 WIP + C1 Hash 自癒（`待 baron 回填`→`1558f79`） | — |
| `.claude-logs/prompts/2026-06-04_TRANSLATOR_C2_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git status -s`：
```
 M processor/translator.py
?? prompt/translate/caption_translate_prompt.txt
```

## §4 修法說明

### §4.1 提示詞路徑常數 + Style Hints（C2 標記、檔頭）
```python
# === [TRANSLATOR C2 START] ===
import settings
TITLE_TRANSLATE_PROMPT_PATH = "prompt/translate/title_translate_prompt.txt"
CONTENT_TRANSLATE_PROMPT_PATH = "prompt/translate/content_translate_prompt.txt"
CAPTION_TRANSLATE_PROMPT_PATH = "prompt/translate/caption_translate_prompt.txt"   # C2 新增
_STYLE_HINTS = { "academic":..., "book":..., ... }   # 七文體、逐字對齊既有 translate_processor
# === [TRANSLATOR C2 END] ===
```

### §4.2 `Translator` 類 Prompt Engine（C2 標記、檔末）
- **`_build_system_prompt(ctx, text_type)` 五步**（plan U2）：
  - ① 底層提示詞載入：`title`→title 檔、`caption`→**caption 新檔**、其餘→content 檔。
  - ② Style Hints：依 `ctx.doc_type`（預設 academic）附 7 文體提示。
  - ③ LCC 領域注入：`if settings.LLM_USE_GLOSSARY_ALIGN:` 讀 `ctx.domain_name`（空 fallback `ctx.lcc`）附「本文件主題領域：{}」，**零 DB**。
  - ④ Glossary 強約束塊：`if 旗標 and ctx.glossary:` 附「術語強約束 System constraint（**大小寫不敏感套用**）」+ 逐項 `- {term_key} → {translation}`。
  - ⑤ constraints 注入：`if ctx.constraints:` 附「【額外譯文約束】」逐項（文字級約束、不 gate 旗標）。
- **`_build_user_prompt(text, ctx, text_type)`**：title/abstract/zh_summary/preceding/else 五分支（對齊既有 translate_text）。
- **`translate()` 公開方法的 chat 雙模式路由屬 C3**；C2 僅交付提示詞拼接（純函式、零 DB、零外部呼叫）。

### §4.3 caption 提示詞（新建、遵 §4）
`prompt/translate/caption_translate_prompt.txt`：最高優先硬規則「保留 Figure/Table 編號與標點原文、嚴禁翻譯/刪除/改動編號」+ 僅翻描述文字 + 去引用。**新增檔、非改既有 title/content**（§4 合規）。

## §5 測試結果

### §5.1 §6.2 grep 驗收（真實輸出節錄）
```
$ grep -nE "caption_translate_prompt|大小寫不敏感|本文件主題領域|術語強約束|額外譯文約束|_STYLE_HINTS" processor/translator.py
27:CAPTION_TRANSLATE_PROMPT_PATH = "prompt/translate/caption_translate_prompt.txt"
30:_STYLE_HINTS = {
（111-128 行含 本文件主題領域 / 術語強約束 / 大小寫不敏感 / 額外譯文約束）
$ ls prompt/translate/caption_translate_prompt.txt   → 存在
```

### §5.2 py_compile + 功能測試（mock、零 DB）
```
② style(book): True
③ LCC 注入: True
④ 術語強約束+大小寫不敏感: True（含 riesling → 雷司令）
⑤ constraints: True（- 人名不翻）
① caption 提示詞載入(Figure/Table 規則): True
① title 提示詞≠content: True
旗標OFF 無LCC/術語注入: True | 仍有 style + constraints: True
用戶提示詞 zh_summary: True | preceding: True
ALL OK
```
- 旗標 OFF 時 ③④ 不注入（gated 正確）、② Style + ⑤ constraints 仍套用（獨立於旗標）。

### §5.3 既有測試套件零迴歸
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 457 passed, 3 skipped in 41.00s
```
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C2 無關。

### §5.4 database SOP 核查
- `processor/translator.py` 無 `.commit()`/session 操作（Prompt Engine 純函式、零 DB）→ 無命中（合規）。

## §6 不可動清單遵守

- [x] A 軌 `pipeline_core.py` / `translate_processor.py` — **未觸碰**（既有 style_hints/路徑常數僅**複製對齊**至 translator.py、未改原檔）。
- [x] `llm/client.py` / retry — **未觸碰**（雙模式 chat 屬 C3）。
- [x] `models.py` / `Domains` — **未觸碰**（Prompt Engine 零 DB）。
- [x] `prompt/translate/` 既有 title/content 檔 — **byte 不動**（僅**新增** caption 檔）。
- [x] PIPE-CORE 四合約 — **未觸碰**（C1 已補 domain_name、C2 不動 contracts）。
- [x] C1 既有 InjectionContext/TranslateMode — **byte 不動**（C2 僅追加 import/常數/Translator 類）。
- [x] 主 repo 目錄 — 未讀寫；baton/ 報告留暫存、未提前 mv/git add。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：本報告 `2026-06-04_TRANSLATOR_C2_執行.md` 暫存 baton/、**不入版控**，待 C5 收官一次性歸檔。
- **下一步**：C3 — Dual-Mode Routing & Thinking（`settings.LLM_THINKING_BUDGET` + `llm/client.py::chat()` 補 `thinking_config` 受控例外〔§4 唯一例外〕+ `Translator.translate(text,ctx,mode,text_type)` 雙模式 chat 路由）。待 baron 確認 C2 後另行下達。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-04_TRANSLATOR_C2_translator.py.bak

# 2. git add 清單（明確列檔、baton/ 報告不入 git）
git add processor/translator.py
git add prompt/translate/caption_translate_prompt.txt
git add .claude-logs/archive/2026-06-04_TRANSLATOR_C2_translator.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-04_TRANSLATOR_C2_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-04_TRANSLATOR_C2_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/TRANSLATOR_C2_msg.txt）
cat /tmp/TRANSLATOR_C2_msg.txt

# 4. baron 手動執行
git commit -F /tmp/TRANSLATOR_C2_msg.txt
```
