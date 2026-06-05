# RESUME-P3 PARA-HOTFIX-1 — B軌正文段落邊界正規化 執行報告

---

**任務代號**：RESUME-P3 PARA-HOTFIX-1（BE-Hotfix）
**執行日期**：2026-06-06
**依據計畫**：`.claude-logs/baton/2026-06-06_RESUME-P3_PARA-HOTFIX-1_hotfix.md`
**次級參考**：`sop/2026-05-23_logging_SOP_手冊.md` / `sop/2026-05-23_database_SOP_手冊.md`
**Git commit hash**：（留空，由 baron 回填）
**狀態**：Completed（程式碼落地 + 驗收全綠 + 收官歸檔；待 baron commit）

---

## §1 基準與完成狀態
- **基準**：HEADING-HOTFIX-1（`7c8a0da`）head；同屬 RESUME-P3 C3 還原邏輯的排版 Regression hotfix。
- **完成狀態**：`pipelines/resume_pipeline.py` 新增 pipelines/ 私有 `_normalize_paragraph_breaks`（移植 A軌 pipe-table-safe 單 `\n`→`\n\n`、不耦合 A軌）+ `_restore_one_section` text/字串 fallback 套用；`tests/test_resume_pipeline.py` 追加 1 測試；`# === [RESUME-P3 PARA-HOTFIX-1 START/END] ===` 包裹；改前 2 `.bak`。**未 commit**（待 baron）。

---

## §2 落地 Commit 表格
| # | Hash | Subject |
|---|---|---|
| PARA-HOTFIX-1 | （待回填）| `fix(resume): RESUME-P3 PARA-HOTFIX-1 — B軌正文段落邊界正規化 (修兩段黏一起)` |

---

## §3 變動檔案清單
| 檔案 | 變動 | 備份 |
|---|---|---|
| `pipelines/resume_pipeline.py` | 新增 `_normalize_paragraph_breaks` static helper + `_restore_one_section` text item/字串 fallback 套用 | `archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_resume_pipeline.py.bak` |
| `tests/test_resume_pipeline.py` | 追加 `test_p3_text_paragraph_blank_line_normalized` | `archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_test_resume_pipeline.py.bak` |

`git diff --stat`：
```
 pipelines/resume_pipeline.py  | 49 +++++++++++++++++++++++++++++++++++++++++--
 tests/test_resume_pipeline.py | 19 +++++++++++++++++
 2 files changed, 66 insertions(+), 2 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因
CommonMark 規範：段落間須 `\n\n`（空行）才分段；單一 `\n`=soft break=同段。
- **A軌有留白**：① `_write_to_md`（L587）每塊補 `content + "\n\n"`；② `_preserve_pipe_table`（L629）`re.sub(r"(?<!\|)(?<!\n)\n(?![\n\|])","\n\n")` 把段內單 `\n`→`\n\n`（pipe table 以 `|` 開頭、lookbehind/ahead 保護）。
- **B軌黏連**：`_restore_one_section` 只 `parts.append(譯文)`、`_restore_sections_markdown` 只在不同 part 間 `"\n\n".join`、段內單 `\n` 不處理 → soft break → 黏一起；且 RESUME-P3 C2 為 resume 停用 Translator U4 → 全鏈無換行升級。

### §4.2 修法（`pipelines/resume_pipeline.py`）
**新增 pipelines/ 私有 helper（移植 A軌邏輯、不 import/不耦合 A軌）**：
```python
@staticmethod
def _normalize_paragraph_breaks(text: str) -> str:
    import re
    if not text:
        return text
    lines = text.split("\n")
    out_lines = []
    in_table = False
    for line in lines:
        is_table_row = bool(re.match(r"^\s*\|", line))
        if is_table_row:
            if not in_table and out_lines and out_lines[-1].strip():
                out_lines.append("")
            in_table = True
            out_lines.append(line)
        elif in_table:
            in_table = False
            if line.strip():
                out_lines.append("")
            out_lines.append(line)
        else:
            out_lines.append(line)
    text = "\n".join(out_lines)
    text = re.sub(r"(?<!\|)(?<!\n)\n(?![\n\|])", "\n\n", text)   # 一般段落單 \n → \n\n
    return text
```
**`_restore_one_section` text item（含字串 fallback）套用**：
```python
if itype == "text":
    rendered = self._t(content, inj, tr, "content") if translate else content
    parts.append(self._normalize_paragraph_breaks(rendered))    # 段落邊界正規化
# 純字串 fallback 同套；formula/figure/table 不套（保結構）
```
- **不動**：標題還原（HEADING-HOTFIX-1 `level=min(2+depth,6)`）/ formula/figure/table 分支 / `_translate_whole` / `_t` / `run_phase3` 主流程 / `BilingualMarkdownSpec` / A軌（不 import）/ 其餘四路 / 母提示詞 / DB。
- 為使驗收 grep `_preserve_pipe_table|md_restore_processor|RestoreProcessor` 真 0-hit（不耦合自證），helper docstring 改述「移植自 A軌既有 pipe-table-safe 邏輯」、不留 A軌符號字面。

### §4.3 測試
`test_p3_text_paragraph_blank_line_normalized`：直接驗 helper——輸入「兩段單 `\n` + pipe table 兩 rows 單 `\n`」→ 斷言 (a) 段落升 `\n\n`、單 `\n` 不殘留；(b) pipe table rows 仍單 `\n` 相連不拆散。

---

## §5 測試結果與 SOP 核查

### §5.1 驗收 grep（hotfix.md §測試計畫）
```
$ grep -nc 'RESUME-P3 PARA-HOTFIX-1' pipelines/resume_pipeline.py
6     ✅ START/END 包裹

$ grep -nc 'def _normalize_paragraph_breaks' pipelines/resume_pipeline.py
1     ✅ helper 存在

$ grep -nc '_preserve_pipe_table\|md_restore_processor\|RestoreProcessor' pipelines/resume_pipeline.py
0     ✅ 不耦合 A軌（不 import、docstring 已去 A軌符號字面）

$ grep -nc 'def test_p3_text_paragraph_blank_line_normalized' tests/test_resume_pipeline.py
1     ✅ 新測試
```

### §5.2 SOP 一致性核查（BE-Hotfix 強制）
```
# logging：logger.error 須 exc_info
$ grep -n 'logger\.error\|logger\.exception\|traceback\.format_exc' pipelines/resume_pipeline.py
無命中（合規）

# database：裸 commit
$ grep -nE '\.commit\(\)' pipelines/resume_pipeline.py | grep -v 'with .*session.*begin'
無命中（合規）
```

### §5.3 pytest
```
$ venv/bin/python -m pytest tests/test_resume_pipeline.py -q
28 passed in 0.82s     ✅（27 既有 + 1 新）

$ venv/bin/python -m pytest tests/ -q
1 failed, 501 passed, 3 skipped in 27.31s
FAILED tests/test_logging_config.py::test_settings_log_format_default_auto   ← 既知 LOG_FORMAT env flake、與本任務無關
```
- **501 passed**（HEADING-HOTFIX-1 後 500 + 本次 1 新）；唯一 failed 為既知環境 flake。✅ 不退化。
- 語法 `ast.parse` → OK。

---

## §6 不可動清單遵守狀態（hotfix.md）
| 不可動項 | 判定 |
|---|---|
| 標題還原（HEADING-HOTFIX-1 `level=min(2+depth,6)`）| [x] ✅ 未動 |
| `content` formula / figure / table 分支 | [x] ✅ 不套正規化、保結構 |
| `_translate_whole` / `_t` / C4 退化偵測 | [x] ✅ 未動 |
| `run_phase3` 主流程 / `BilingualMarkdownSpec` 合約 | [x] ✅ 未動 |
| A軌 `md_restore_processor`（不 import、不耦合）/ 其餘四路 / 母提示詞 / DB Schema | [x] ✅ 未動（grep 0 命中）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

`git diff --stat` 證：本次僅 `pipelines/resume_pipeline.py` + `tests/test_resume_pipeline.py`。

---

## §7 銜接與下一步
- **⚠️ Golden 重捕（baron 運維、非 commit）**：本 hotfix 改變 B軌 `final_zh` 段落空行結構 → 衝擊 golden D1/D2。Flip/結案前須重捕 resume 單路：
  ```bash
  venv/bin/python tools/golden_baseline.py capture resume --force
  ```
  （與 TILING-HOTFIX-1 / SHADOW-HOTFIX-2 / RESUME-P3 / HEADING-HOTFIX-1 同屬 B軌輸出變更類；其餘四路免捕。）
- **E2E 肉眼驗證**：影子上傳履歷 → B軌 `final_zh`：正文相鄰段落間有空行留白、不再黏連；含表格段落 table 結構不破。
- **收官歸檔**：本報告 + hotfix.md 一次性 mv → `hotfixes/`（§8）。

---

## §8 baron 執行命令
```bash
# 1. 備份檔案已完成（§3）
#    .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_resume_pipeline.py.bak
#    .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_test_resume_pipeline.py.bak

# 2. 收官搬移已由 Claude Code 完成（mv hotfix.md + 執行.md → hotfixes/）；git add 清單：
git add pipelines/resume_pipeline.py
git add tests/test_resume_pipeline.py
git add .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_resume_pipeline.py.bak
git add .claude-logs/archive/2026-06-06_RESUME-P3_PARA-HOTFIX-1_test_resume_pipeline.py.bak
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_PARA-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/2026-06-06_RESUME-P3_PARA-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_PARA-HOTFIX-1_hotfix.md
git add .claude-logs/hotfixes/2026-06-06_RESUME-P3_PARA-HOTFIX-1_執行.md

# 3. commit message 草稿（已寫入 /tmp/RESUME-P3_PARA-HOTFIX-1_msg.txt）
# 4. baron 手動執行
git commit -F /tmp/RESUME-P3_PARA-HOTFIX-1_msg.txt
```

### §8.2 commit message 草稿
```
fix(resume): RESUME-P3 PARA-HOTFIX-1 — B軌正文段落邊界正規化 (修兩段黏一起)

修改 pipelines/resume_pipeline.py：
1. 新增 pipelines/ 私有 helper _normalize_paragraph_breaks（移植 A軌 _preserve_pipe_table 的 pipe-table-safe 單 \n→\n\n 邏輯、不耦合 A軌 class）。
2. _restore_one_section 處理 text item（含純字串 fallback）時套用段落邊界正規化，使段內單 \n 升級為 \n\n（空行）；formula/figure/table 不套用、pipe table rows 保留原 \n。
修改 tests/test_resume_pipeline.py：
1. 追加 test_p3_text_paragraph_blank_line_normalized 驗證段落單 \n 升級 \n\n、且 pipe table rows 不被拆散。
變更與新增區塊已使用 # === [RESUME-P3 PARA-HOTFIX-1 START/END] === 註解物理包裹。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §9 回退方式（Rollback）
```bash
git revert <PARA-HOTFIX-1-hash>     # 單獨回退本 hotfix（保留 C1-C6 + HEADING-HOTFIX-1）
git reset --hard 7c8a0da            # 或退回 HEADING-HOTFIX-1 落地點
```

---

## §99 Revision
- v1 (2026-06-06)：PARA-HOTFIX-1 落地——新增 pipelines/ 私有 `_normalize_paragraph_breaks`（移植 A軌 pipe-table-safe 單 `\n`→`\n\n` 段落正規化、不 import/不耦合 A軌 restore 處理器）+ `_restore_one_section` text item/字串 fallback 套用（formula/figure/table 不套、pipe table rows 保留）；追加 `test_p3_text_paragraph_blank_line_normalized`（兩段升 `\n\n` + pipe table rows 不拆散）；PARA-HOTFIX-1 包裹 + 2 .bak；grep 全綠（包裹 6 / helper 1 / A軌不耦合 0 / 新測試 1）、SOP logging+database 合規、resume 28 passed、全套件 501 passed（唯一 failed 既知 LOG_FORMAT env flake）；改 B軌段落空行 → resume golden 須重捕（baron 運維）。
