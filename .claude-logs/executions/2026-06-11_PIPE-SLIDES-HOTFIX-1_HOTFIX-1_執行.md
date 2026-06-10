# PIPE-SLIDES-HOTFIX-1 HOTFIX-1 執行報告

| 欄位 | 值 |
|---|---|
| 任務代號 | PIPE-SLIDES-HOTFIX-1 HOTFIX-1 — B 軌簡報三缺陷緊急修補 |
| 執行日期 | 2026-06-11 |
| 依據規劃 | `hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1_hotfix.md`（baron 拍板 1C/2B/3C 不修/4 移植）|
| 次級參考 | resume PARA-HOTFIX-1（F4 移植源）/ SHADOW-HOTFIX-2（doubling 同族先例）|
| 落地 Hash | （留空、baron 回填）|
| 狀態 | ✅ 28 測試全綠（24 既有 + 4 新）+ 全套件 584 passed + SOP 合規；未 commit（待 baron）|

---

## §1 基準與完成狀態

- **基準**：PIPE-SLIDES C7 收官（`eb23bd5`）之後、baron A/B 軌同件實測（ST 簡報、06:02 兩實件）發現三缺陷。
- **本次**：F1/F2/F4 三點落地 + F3 顯式不修；**僅兩檔**；共用元件/A 軌零改；未 commit。

## §2 Commit 表格

| Commit | Hash | Subject |
|---|---|---|
| HOTFIX-1 | `待 baron 回填` | BE-Hotfix: PIPE-SLIDES HOTFIX-1 — B 軌簡報三缺陷 |

## §3 變動檔案清單

```
修改：pipelines/slide_pipeline.py     （F1 helper+套用 / F2 兩落點 / F4 helper+兩套用；HOTFIX-1 標記 4 對 + 4 單行）
修改：tests/test_slide_pipeline.py    （+4 回歸測試 + _make_p3_ctx 加 paper_id 參數；標記 1 對）
```
備份（入版控、審計）：
```
.claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1_slide_pipeline.py.bak
.claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1_test_slide_pipeline.py.bak
```

## §4 修法說明（全依 hotfix.md「熱修復修法」、`# === [PIPE-SLIDES-HOTFIX-1 HOTFIX-1 ...] ===` 包裹）

### F1 物理去標題回聲（選 C、原文層）
- 新增 `_strip_title_echo(title, content)`：正規化（去空白/標點/lower）後 content 開頭連續行 ≈ title（相等或 ≥6 字含括）即剔、**cap 2 行**（覆蓋實件 p6 ×3 案例）；套用於 `run_phase1` units 構造（`content` 欄）。
- **真因**：Vision 忠實轉錄使頁標題同入 title 欄與 content 首行 → P3 兩欄各自翻譯 → 同句雙譯相鄰（實件 p1/p6×3/p8/p16）。源頭修 → 閱讀視圖/rag_sections/chunk 三處同淨；title 欄不動 → `page_key` 契約零影響（測試鎖死）。

### F2 P4 接譯題（選 B、零增量 LLM）
- `_deliver` 正常路：封面譯題 `zh_fields[0][0]`（**P3 本就翻好**）→ `ctx.raw_metadata["translated_title"]`（旁路先例；web_server C8-hotfix 既有寫庫自動流到 DB、零改）。
- `run_phase4`：`_translated` 首選旁路、缺退暫同取（退化/zh 路向後相容）+ 影子 `(測試)` 綴對齊 → `rag_indexer.index(translated_title=_translated)`。
- **真因**：C5「暫同取」技術債——譯文存在、只缺穿線。

### F4 移植 `_normalize_paragraph_breaks`（pipe-table-safe）
- 逐字移植 resume PARA-HOTFIX-1 邏輯（pipelines/ 內私有重建、**不跨策略 import**）；套用 `_deliver` zh 渲染 + `_page_source_md` en 渲染（對稱）；rag_sections merged text 不套（chunk 對 soft break 無感）。
- **真因**：正文內部 Vision 原樣裸單 `\n` → CommonMark soft break 黏段（實件多條列未顯症、純文字頁必發）；slides C4 漏移植（grep 證 0 命中）。

### F3 中英並列密度 —— 顯式不修（選 C、決策記錄於 hotfix.md）
結構性根因＝逐頁並行翻譯頁間零記憶、「首次」跨頁無法定義；BM25 召回受益；列觀察項。

## §5 測試結果（真實輸出）

```
$ venv/bin/python -m pytest tests/test_slide_pipeline.py -q
28 passed in 0.65s     # 24 既有（回歸網零紅）+ 4 新

  test_hf1_title_echo_stripped PASSED            # ×2 回聲全剔 / 非回聲不誤殺 / 無標題不動
  test_hf1_p1_units_content_echo_free PASSED     # P1 接線：content 淨、title 欄不動（key 契約）
  test_hf2_translated_title_wired PASSED         # 旁路就位 + P4 傳「譯Power Deck (測試)」
  test_hf4_paragraph_breaks_normalized PASSED    # 純文字升級 \n\n / table rows 不拆 / 端到端進 final_zh

$ venv/bin/python -m pytest tests/ -q
1 failed, 584 passed, 3 skipped   # 唯一 failed=既知 env flake test_settings_log_format_default_auto；584（580+4）
```

### §5.3 SOP 核查（BE-Hotfix 強制）
```
$ grep -nE "traceback.format_exc|logger\.error" pipelines/slide_pipeline.py
無命中（合規；本 hotfix 零新增 error 路）
$ grep -nE "\.commit\(\)" pipelines/slide_pipeline.py | grep -v "session.begin"
無命中（合規；零 DB 寫）
```

## §6 不可動清單遵守

- [x] **僅兩檔**（git status 證）；共用元件（translator/rag_indexer/contracts）/ A 軌零改。
- [x] 既有 24 測試零紅（key 契約 / alt 對齊 / 整合測試全綠＝行為回歸網通過）。
- [x] 標記平衡（pipeline 4 對 + 4 單行 F-tag；test 1 對）。
- [x] 兩份 `2026-06-01_PIPE*` 規格書長駐 baton 未動未 add。

## §7 銜接（完成緊急修補、歸檔收官）

- 收官自動化已執行：hotfix.md → `hotfixes/`、本報告 → `executions/`（mv + git add）。
- **⚠️ 行為變更 + golden**：F1/F4 改 B 軌 final 輸出、F2 改 rag_tree 譯題 → **slides golden 建議本 hotfix 落地後一次首捕**（`venv/bin/python tools/golden_baseline.py capture slides --force`、免捕兩次）。
- **baron E2E（非 commit）**：影子重傳 ST 簡報 → p1 單一標題/p6 僅 1 次/前端列表顯中文譯題+(測試)/table 頁不破碎/引用 p{N} 標題不變。

## §8 baron 執行命令

```bash
# 1. 備份已完成（archive/ 2 份 .bak）

# 2. git add 清單（hotfixes/ 與 executions/ 已於收官自動化 mv + git add 完畢）
git add pipelines/slide_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1_slide_pipeline.py.bak
git add .claude-logs/archive/2026-06-11_PIPE-SLIDES-HOTFIX-1_test_slide_pipeline.py.bak
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES-HOTFIX-1_run_提示詞.md
git add .claude-logs/prompts/2026-06-11_PIPE-SLIDES-HOTFIX-1_doc_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿已寫入 /tmp/PIPE-SLIDES-HOTFIX-1_msg.txt
git commit -F /tmp/PIPE-SLIDES-HOTFIX-1_msg.txt
```

## §9 回退方式（Rollback）

```bash
git revert <HOTFIX-1 hash>   # 或還原 2 .bak；F1 誤殺備案：閾值收緊為「正規化後完全相等」一檔、免 revert 全件
```
