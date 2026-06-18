# PIPE-LITEDOC C1 執行報告 — section_engine HTML 扉頁 formatter（純加法·首發隔離驗證）

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-LITEDOC C1 |
| 執行日期 | 2026-06-19 |
| 依據規劃 | `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_litedoc路策略管線_tasks.md §8 C1` |
| 次級參考 | plan v3 §2 U5b;A 軌 `md_restore_processor:435-540`（zh/en 扉頁 byte 基準）|
| 落地 Hash | （留空、待 baron 回填）|
| 狀態 | Completed (Commit C1)、grep + pytest 驗收通過、未 commit |

---

## §1 基準與完成狀態
- **執行前基準**：PIPE-SECTION-BASE 全案結案後;section_engine 有 `render_meta_header`（resume 列表）、無 academic-family HTML 扉頁 formatter。
- **完成狀態**：section_engine **純加法**新增 `render_meta_header_html` + test_section_engine 追加 4 測試;**未碰既有任何函式**。**未 commit**（baron 手動）。
- **與全局策略對齊**：本 commit conditioned on `plan §2 U5b`（section_engine 純加法補 HTML 扉頁 formatter、litedoc 首個 consumer、academic/book/technical 後續共用）;無偏離。U5b 排序為**首發隔離驗證**——本 commit 不接 litedoc route、僅 engine additive + 既有 17+42 測試鎖死。

## §2 Commit 表格
| # | Hash | Subject |
|---|---|---|
| C1 | （待 baron 回填）| BE-Refactor: PIPE-LITEDOC C1 — section_engine HTML 扉頁 formatter（純加法·首發隔離驗證）|

## §3 變動檔案清單（staged vs baton 暫存）
| 檔案 | 類型 | Staging |
|---|---|---|
| `pipelines/section_engine.py` | 修改（純加法 render_meta_header_html）| **本 commit git add** |
| `tests/test_section_engine.py` | 修改（追加 4 測試）| **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C1_section_engine.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/archive/2026-06-19_PIPE-LITEDOC_C1_test_section_engine.py.bak` | 備份 | **本 commit git add** |
| `.claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C1_run_提示詞.md` + `INDEX.md` | 提示詞歸檔 | 本 commit git add |
| `.claude-logs/TODO.md` | 狀態（C1 ✅ / C2 🟡）| 本 commit git add |
| `.claude-logs/baton/2026-06-19_PIPE-LITEDOC_C1_執行.md`（本檔）/ plan / tasks | baton 暫存 | **baton/ 暫存（C8 checkout 歸檔）·嚴禁 git add** |

## §4 修法說明（`# === [PIPE-LITEDOC C1 ...] ===` 包裹）
- **`section_engine.py` 純加法**：新增 `render_meta_header_html(authors, venue, date, doi=None, keywords=None, *, is_zh=False) -> str`——
  - 輸出 `<div class="paper-header-meta">` + `header-authors`〔zh `、`/en `, ` 分隔〕/ `header-venue-date`〔`·` 分隔〕/ `header-doi`〔`DOI: `〕/ `header-keywords`〔zh `關鍵字：`+`、`/en `Keywords: `+`, `〕;**byte 對齊 A 軌 `md_restore:466-477`（en）/ `:523-534`（zh）**。
  - **Zero Schema Coupling**（同 U3.1）：收已抽好值、**零讀 raw_metadata/ctx**（grep 證 raw_metadata 3 命中皆 docstring/註解、無代碼讀取）;不含 `# 標題`（呼叫端 prepend、同 A 軌 title 與 meta block 分離）;空欄略過、全空回 ''、收尾 `\n\n`（同 render_meta_header）。
  - **未碰既有**：`render_meta_header`（resume 列表）+ 摘要簇 + render/restore 簇 + rag 簇全未動。
- **`tests/test_section_engine.py`**：追加 4 測試〔en 全欄 / zh 分隔符+label / 空欄略過 / 全空回 ''〕。

關鍵片段：
```python
def render_meta_header_html(authors=None, venue=None, date=None, doi=None, keywords=None, *, is_zh=False):
    html_bits = []
    if authors:
        sep = "、" if is_zh else ", "
        html_bits.append(f'  <div class="header-authors">{sep.join(str(a) for a in authors)}</div>')
    ...
    if not html_bits:
        return ""
    lines = ['<div class="paper-header-meta">'] + html_bits + ['</div>']
    return "\n".join(lines) + "\n\n"
```

## §5 測試結果
### §5.1 §6.1 C1 驗收 grep
```
render_meta_header_html 定義：1;paper-header-meta/header-* ：8 命中;C1 包裹：3
既有 render_meta_header（resume 列表）仍在：1（未動）
```
### §5.2 行為等價 + 全套件 pytest
```
pytest tests/test_section_engine.py tests/test_resume_pipeline.py -q → 63 passed
  〔既有 section_engine 17 + resume 42 = 59 不退化 + 新 render_meta_header_html 4 = 63〕
pytest tests/ -q → 1 failed, 661 passed, 3 skipped（661＝657 基線 + 4 新;唯一 fail＝既有 .env LOG_FORMAT env flake〕
```
### §5.3 §6.9 SOP 一致性核查（BE-Refactor 強制）
```
logging（engine logger.error / format_exc）：0 命中（合規）
database（engine 裸 commit）：0 命中（合規;純函式無 DB 交易）
raw_metadata：3 命中皆 docstring/註解（L10/446/487）、無代碼讀取（Zero Schema Coupling 守住）
```
### §5.4 變動範圍（git）
```
git status -s 業務/測試 .py：僅 pipelines/section_engine.py(M) + tests/test_section_engine.py(M)
```

## §6 不可動清單遵守
| 項目（tasks §7）| 狀態 |
|---|---|
| `section_engine.py` 既有任何函式（render_meta_header/摘要簇/render-restore 簇/rag 簇）| [x] ✅ 未動（純加法、resume 42 + engine 17 全綠為憑）|
| `rag_indexer.py` / `contracts.py` / `resume_pipeline.py` / `slide_pipeline.py` | [x] ✅ 零碰 |
| 三大共用真理源 / A 軌全部 | [x] ✅ 零碰 |
| `litedoc_pipeline.py`（C2 才建）| [x] ✅ 本 commit 未建（C1 僅 engine additive）|
| 主 repo 目錄 | [x] ✅ 未讀寫 |

## §自評（策略對齊自我審查）
- **(a) 越界?**：否。僅改 `section_engine.py`（純加法）+ `test_section_engine.py`（追加）;litedoc_pipeline 未動（C2 才建）、既有函式零碰。
- **(b) 無關 / 違規?**：否。單一 formatter + 對應測試、byte 對齊 A 軌;Zero Schema Coupling 守住（grep 證）。符 CLAUDE.md（baton 不 add、不自發 commit）。msg 簽名校正為 Opus 4.8（提示詞模板誤植 Sonnet）。
- **(c) 推進哪個 U-N?**：U5b（section_engine 純加法 HTML 扉頁 formatter）;無做白工——litedoc C5 + 未來 academic/book/technical 將共用。

## §7 銜接
- baton 狀態：C1 報告 + plan + tasks 留 baton（待 C8 一次性歸檔）。
- 下一步：**C2 — LiteDoc 骨架與三 key 註冊**（`@register('litedoc'/'news'/'web')` + `__init__` import + 四方法 stub + 分派測試）。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3、.bak 本 commit git add）

# 2. git add（業務 + 測試 + .bak + 提示詞 + TODO;baton 暫存嚴禁 add）
git add pipelines/section_engine.py tests/test_section_engine.py
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C1_section_engine.py.bak
git add .claude-logs/archive/2026-06-19_PIPE-LITEDOC_C1_test_section_engine.py.bak
git add .claude-logs/prompts/2026-06-19_PIPE-LITEDOC_C1_run_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 /tmp/PIPE-LITEDOC_C1_msg.txt）
cat > /tmp/PIPE-LITEDOC_C1_msg.txt << 'EOF'
BE-Refactor: PIPE-LITEDOC C1 — section_engine HTML 扉頁 formatter（純加法·首發隔離驗證）

- section_engine.py 純加法新增 render_meta_header_html（authors/venue-date/doi/keywords →
  <div class="paper-header-meta"> 結構、is_zh 控分隔符與 label）；byte 對齊 A 軌
  md_restore_processor zh/en 扉頁（:466-477 / :523-534）；Zero Schema Coupling（收已抽值、零讀 ctx）。
- 嚴禁碰既有：render_meta_header（resume 列表）+ 摘要/render-restore/rag 簇全未動。
- academic-family 共用（litedoc 首個 consumer、academic/book/technical 後續免重造）。

驗證：test_section_engine 追加 4 測試；既有 section 17 + resume 42 不退化（63 passed）；
全套件 661 passed（657 基線 + 4；唯一 fail＝既有 .env LOG_FORMAT flake）；SOP logging/database
無命中、raw_metadata 僅 docstring。baton（plan/tasks/C1 報告）未 add、待 C8 歸檔。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動執行
git commit -F /tmp/PIPE-LITEDOC_C1_msg.txt
```

## §9 回退方式
`git revert <C1 hash>`（或自 `.bak` 還原 section_engine.py + test）。

---
### 結論
🟢 section_engine 純加法補 `render_meta_header_html`（byte 對齊 A 軌 zh/en 扉頁、Zero Schema Coupling）、既有零碰（63 passed、661 全套件基線+4）、SOP 合規。U5b 首發隔離達標。下一步 C2 LiteDoc 骨架與註冊。
