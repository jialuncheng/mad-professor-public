# TRANSLATOR C4 — Formatting Fallback & Tests（分行容錯與單元測試）執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | TRANSLATOR C4 |
| **執行日期** | 2026-06-04 |
| **依據規劃** | `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` §8 C4 + plan v10 §2 U4/§6.1 |
| **次級參考** | 既有 `translate_processor.py` re.sub 範式 / mock LLM |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 已備好改動，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`11ea52a`（BE-Refactor: C3 — Dual-Mode Routing & Thinking）
- **完成狀態**：C4 於 `processor/translator.py` 補 U4 分行兜底 + 新建 `tests/test_translator.py`（8 pytest 全綠），全套件 465 passed（除既有環境性失敗 1 項），**未 commit / 未 push**。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C4 | `待 baron 回填` | BE-Refactor: C4 — Formatting Fallback & Tests（分行容錯與單元測試） |

## §3 變動檔案清單

| 檔案 | 變動 | 備註 |
|---|---|---|
| `processor/translator.py` | C4 兩塊（`# === [TRANSLATOR C4 START/END] ===`）：① `import re`；② `translate()` 末 U4 多行分行兜底 | C1/C2/C3 既有區塊 byte 不動 |
| `tests/test_translator.py` | **新建**（8 測試、mock LLM） | 純測試新增 |
| `.claude-logs/archive/2026-06-04_TRANSLATOR_C4_translator.py.bak` | 改前備份 | **納入 git add** |
| `.claude-logs/baton/2026-06-04_TRANSLATOR_C4_執行.md` | 本報告 | **暫存 baton/，嚴禁 git add**（唯 C5 收官歸檔） |
| `.claude-logs/TODO.md` | C4→✅ / C5→🟡 WIP + C3 Hash 自癒（`待 baron 回填`→`11ea52a`） | — |
| `.claude-logs/prompts/2026-06-04_TRANSLATOR_C4_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | — |

`git status -s`：
```
 M processor/translator.py
?? tests/test_translator.py
```

## §4 修法說明

### §4.1 U4 多行分行容錯（C4 標記、translate() 末）
```python
        translated = llm.chat(...).strip()
        # === [TRANSLATOR C4 START] ===
        original_lines = text.strip().split("\n")
        if len(original_lines) > 1:
            translated_lines = translated.split("\n")
            if len(translated_lines) < len(original_lines):
                translated = re.sub(r"([。！？])\s*", r"\1\n", translated).strip()
        # === [TRANSLATOR C4 END] ===
        return translated
```
- 原文多行但譯文行數較少時，按句末標點（。！？）重分行——逐字對齊既有 `translate_processor.translate_text` L290-295 行為。`import re`（C4 標記）。

### §4.2 `tests/test_translator.py`（新建、8 測試、mock LLM）
| # | 測試 | 驗證點 |
|---|---|---|
| 1 | `normal_mode` | NORMAL → model=TRANSLATE_MODEL + thinking_budget=0 |
| 2 | `deep_think_mode` | DEEP_THINK → thinking_budget=LLM_THINKING_BUDGET(2048)（顯式設 budget + 3.5 模型） |
| 3 | `style_hints` | doc_type=book/resume/預設 academic 風格提示正確 |
| 4 | `prompt_file_routing` | title/caption/content 底層提示詞檔相異；caption 含 Figure/編號規則 |
| 5 | `lcc_domain_injection` | domain_name 注入；None→fallback lcc；旗標 off 不注入 |
| 6 | `glossary_injection` | 術語強約束 + 大小寫不敏感 + riesling→雷司令；旗標 off 不注入 |
| 7 | `formatting_fallback` | 原文三行、譯文單行（含三句號）→ 重分行 ≥2 換行 |
| 8 | `user_prompt_references` | zh_summary/preceding 生成參考區塊；plain 無 |

## §5 測試結果

### §5.1 C4 八測試全綠（真實輸出）
```
$ venv/bin/python -m pytest tests/test_translator.py -v
tests/test_translator.py::test_translator_normal_mode PASSED             [ 12%]
tests/test_translator.py::test_translator_deep_think_mode PASSED         [ 25%]
tests/test_translator.py::test_translator_style_hints PASSED             [ 37%]
tests/test_translator.py::test_translator_prompt_file_routing PASSED     [ 50%]
tests/test_translator.py::test_translator_lcc_domain_injection PASSED    [ 62%]
tests/test_translator.py::test_translator_glossary_injection PASSED      [ 75%]
tests/test_translator.py::test_translator_formatting_fallback PASSED     [ 87%]
tests/test_translator.py::test_translator_user_prompt_references PASSED  [100%]
============================== 8 passed in 0.29s ===============================
```

### §5.2 全套件零迴歸（+8 新測試）
```
$ venv/bin/python -m pytest tests/ -q
1 failed, 465 passed, 3 skipped in 38.93s
```
- 465 passed = C4 前 457 + 本次新增 8，**淨增 8、零既有迴歸**。
- 唯一失敗 `test_settings_log_format_default_auto`：**既有環境性失敗**（`.env:54 LOG_FORMAT=json`），與 C4 無關。

### §5.3 §6.4 grep + C4 標記
```
$ grep -nE "re.sub|TranslateMode|InjectionContext" tests/test_translator.py   → 命中
$ grep -c "TRANSLATOR C4 START|TRANSLATOR C4 END" processor/translator.py     → 4（兩塊成對）
```

### §5.4 database SOP 核查
- C4 無 `.commit()`/session 操作 → 無命中（合規）。

## §6 不可動清單遵守

- [x] A 軌 `pipeline_core.py` / `translate_processor.py` — **未觸碰**。
- [x] `llm/client.py` / `settings.py` — **未觸碰**（C3 已定）。
- [x] `models.py` / `Domains` / PIPE-CORE 四合約 / DOMAIN-NORM / GLOSSARY-CORE — **未觸碰**。
- [x] `prompt/translate/` — **未觸碰**。
- [x] C1/C2/C3 既有區塊 — **byte 不動**（C4 僅加 import re + translate() 末兜底）。
- [x] 主 repo 目錄 — 未讀寫；baton/ 報告留暫存、未提前 mv/git add。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：本報告 `2026-06-04_TRANSLATOR_C4_執行.md` 暫存 baton/、**不入版控**，待 C5 收官一次性歸檔。
- **下一步**：C5 — Checkout & Clean（Conformance 三維度驗收 + 一次性 mv plan_v10/tasks/C1-C5 報告至正式目錄 + TODO 結案 + 歷史 Hash 自癒）。待 baron 下達 C5 收官提示詞。

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3）：
#    .claude-logs/archive/2026-06-04_TRANSLATOR_C4_translator.py.bak

# 2. git add 清單（明確列檔、baton/ 報告不入 git）
git add processor/translator.py
git add tests/test_translator.py
git add .claude-logs/archive/2026-06-04_TRANSLATOR_C4_translator.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-04_TRANSLATOR_C4_run_提示詞.md
git add .claude-logs/prompts/INDEX.md
# （注意：.claude-logs/baton/2026-06-04_TRANSLATOR_C4_執行.md 暫留 baton/，不 add）

# 3. commit message 草稿（已寫入 /tmp/TRANSLATOR_C4_msg.txt）
cat /tmp/TRANSLATOR_C4_msg.txt

# 4. baron 手動執行
git commit -F /tmp/TRANSLATOR_C4_msg.txt
```
