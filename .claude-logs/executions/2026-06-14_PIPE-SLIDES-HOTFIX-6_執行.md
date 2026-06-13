# PIPE-SLIDES-HOTFIX-6 執行報告 — 殘留母片日期單頁清除 + golden 重捕說明回溯更正

> BE-Hotfix 落地報告（含 Part A 程式 + Part B 文件回溯更正）。依 `.claude-logs/baton/2026-06-14_PIPE-SLIDES-HOTFIX-6_hotfix.md`。

---

## §1 基準與完成狀態
- **基準**：`gemini-refactor`、worktree；HOTFIX-5 剛落地。
- **完成狀態**：Part A 程式 + 4 測試、Part B 8 文件 banner + TODO 14 尾註，皆完成、驗收通過。**尚未 commit**（baron 手動，§8）。

## §2 落地 Commit 表格
| # | Hash | Subject |
|---|---|---|
| HOTFIX-6 | （待 baron 回填）| BE-Hotfix: PIPE-SLIDES-HOTFIX-6 — 殘留母片日期單頁清除 + golden 重捕說明回溯更正 |

## §3 diff stat
```
 pipelines/slide_pipeline.py                 | Part A：_strip_master_date 加單頁純日期清空 pass
 tests/test_slide_pipeline.py                | +4 回歸測試（hf6）
 .claude-logs/hotfixes/*PIPE-SLIDES-HOTFIX-{1,1b,2,3,3c,3d,4,5}_hotfix.md | Part B：各插更正 banner（8 檔）
 .claude-logs/TODO.md                        | HOTFIX-6 完成表 + 14 行 slide-golden 尾註
```
備份：`.claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-6_slide_pipeline.py.bak`。

## §4 真因
- **Part A**：`_strip_master_date` 需 `hit_pages≥2`;本輪 Vision 僅在「都市農業」一頁吐母片頁尾日期成獨立 content 行 → hit_pages=1 早退不洗 → P3 把 `4/28/2026` 譯重排成 `2026/4/28`（全檔唯一日期行 L393、該頁唯一 content）。
- **Part B**：`golden_baseline.py capture slides` 捕 A 軌（`PipelineCore`/`slides_processor`、shadow=False），B 軌 hotfix 改 `slide_pipeline.py` 不影響 A 軌 golden;先前 8 份文件「slides golden 須重捕」為 A/B 軌混淆誤述。

## §5 修法
### Part A（`pipelines/slide_pipeline.py`，`# === [PIPE-SLIDES-HOTFIX-6 ...] ===` 包裹）
`_strip_master_date` 於既有 ≥2 頁邏輯之前加「整頁 content 僅純日期行 → 清空」單頁 pass（無論幾頁、運行 P1 譯前）。真內容頁日期與其他行並存 → `all()` False → 不清。與 HOTFIX-2 正交。
### Part B（8 份歷史 hotfix 文件 + TODO）
- 8 檔（HOTFIX-1/1b/2/3/3c/3d/4/5）golden 誤述段前插「統一更正 banner」（原句保留、加 banner 標作廢，存審計軌跡）。RAG-12-HOTFIX-1（「零 golden 重捕」正確）未動。
- TODO 14 行 slide-golden 附註加尾註「〔更正 HOTFIX-6：capture slides 捕 A 軌、B 軌不需重捕、影子 E2E 驗〕」（含 META-NORM C4 同誤一併）;resume golden 6 行未動（capture resume 屬 A 軌共用 ResumeProcessor、本即正確）。

## §6 不可動清單遵守狀態
- [x] ✅ Part A 僅 `_strip_master_date`;RAG 隔離（`ctx.rag_sections`/`merged` 不碰）、四路/web_server 零碰、保留 ≥2 頁後盾。
- [x] ✅ Part B 僅編輯既有 hotfix 文件附註 + TODO;零業務碼影響。
- [x] ✅ 零非預期 .py（僅 slide_pipeline.py + test）;resume/其他 golden 註記未誤動。
- [x] ✅ 主 repo 目錄未讀寫。

## §7 端到端驗證計畫結果
### §7.1 grep
```
PIPE-SLIDES-HOTFIX-6 包裹：2；hf6 測試：4
Part B banner：8 檔皆有「更正（PIPE-SLIDES-HOTFIX-6 回溯）」
TODO 尾註：14 行（slide+META-NORM C4）；resume golden 6 行 0 誤傷
```
### §7.2 §5 SOP 核查（Part A）
```
[logging] grep logger.error/traceback/exception 於 HOTFIX-6 改動：無命中（合規）
[database] grep .commit( pipelines/slide_pipeline.py：無命中（合規、不涉 DB）
```
### §7.3 pytest
```
tests/test_slide_pipeline.py：71 passed（67 + hf6 新 4）
全套件：1 failed, 640 passed, 3 skipped
```
- **640 passed = 基線（636）+ hf6 新 4**;唯一 failed＝既有 `.env LOG_FORMAT=json` env flake（與本次零關係）。
### §7.4 hf6 4 測試
| 測試 | 情境 | 斷言 |
|---|---|---|
| `test_hf6_sole_date_content_cleared` | content 僅 `4/28/2026`（單頁）| content 清空、單位保留 |
| `test_hf6_date_amid_content_kept` | `1840 年`+真內容（單頁）| 不清（真內容單頁日期未誤殺）|
| `test_hf6_multipage_inline_date_stripped` | ≥2 頁 日期+內容 | HOTFIX-2 剔日期行、保內容（不退化）|
| `test_hf6_normal_content_untouched` | 一般 content | 不變 |
### §7.5 golden / baron E2E（依更正後正確認知）
- **A 軌 golden 不需重捕**（本改 B 軌、A 軌 `slides_processor` 未動）。
- baron **影子重傳 Ch37** → 「都市農業」頁底不再殘留 `2026/4/28`;真內容頁日期（時間軸等）未誤殺。

## §8 baron 執行命令
```bash
# 1. 備份已完成（§3）

# 2. git add（Part A code/test/bak + Part B 8 文件 + 移出 baton 歸檔 + run/doc 提示詞 + INDEX + TODO）
git add pipelines/slide_pipeline.py tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-6_slide_pipeline.py.bak
git add .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1_hotfix.md \
        .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-1b_hotfix.md \
        .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-2_hotfix.md \
        .claude-logs/hotfixes/2026-06-11_PIPE-SLIDES-HOTFIX-3_hotfix.md \
        .claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3c_hotfix.md \
        .claude-logs/hotfixes/2026-06-12_PIPE-SLIDES-HOTFIX-3d_hotfix.md \
        .claude-logs/hotfixes/2026-06-13_PIPE-SLIDES-HOTFIX-4_hotfix.md \
        .claude-logs/hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-5_hotfix.md
git add .claude-logs/hotfixes/2026-06-14_PIPE-SLIDES-HOTFIX-6_hotfix.md
git add .claude-logs/executions/2026-06-14_PIPE-SLIDES-HOTFIX-6_執行.md
git add .claude-logs/prompts/2026-06-14_PIPE-SLIDES-HOTFIX-6_run_提示詞.md .claude-logs/prompts/2026-06-14_PIPE-SLIDES-HOTFIX-6_doc_提示詞.md .claude-logs/prompts/INDEX.md
git add .claude-logs/TODO.md

# 3. commit message 草稿（已寫入 tmp/PIPE-SLIDES-HOTFIX-6_msg.txt；簽名已更正網域）
mkdir -p tmp
cat > tmp/PIPE-SLIDES-HOTFIX-6_msg.txt << 'EOF'
BE-Hotfix: PIPE-SLIDES-HOTFIX-6 — 殘留母片日期單頁清除 + golden 重捕說明回溯更正

Part A（程式）：_strip_master_date 加「整頁 content 僅純日期行 → 清空」單頁 pass（無論幾頁、運行 P1 譯前）。
  真因：HOTFIX-2 ≥2 頁門檻對「Vision 僅單頁吐母片頁尾日期」漏網（Ch37 都市農業頁 4/28/2026 留存、P3 譯成 2026/4/28）。
  真內容頁不受影響（日期與其他行並存 → all() False → 不清）；補 HOTFIX-2 單頁缺口、兩者正交。

Part B（文件回溯更正）：釐清 golden_baseline.py capture slides 捕 A 軌（PipelineCore/slides_processor、shadow=False 正本基準）、
  非 B 軌（slide_pipeline）→ B 軌 hotfix 不需 A 軌 golden 重捕、驗證走影子 E2E。
  8 份 PIPE-SLIDES hotfix 文件（HOTFIX-1/1b/2/3/3c/3d/4/5）「slides golden 須重捕」誤述加更正 banner 作廢
  （RAG-12-HOTFIX-1「零 golden 重捕」本即正確不改）+ TODO slide-golden 附註尾註（含 META-NORM C4 同誤）。

SOP 核查：logging + database 皆無命中（合規）。
驗證：4 新回歸測試（單頁純日期清空/單頁日期夾內容保留/多頁 HOTFIX-2 不退化/一般不動）；slide 71 passed、全套件 640 passed
（基線維持、唯一 fail＝既有 .env LOG_FORMAT flake）。
A 軌 golden 不需重捕（本改 B 軌）；baron 影子重傳 Ch37 → 都市農業頁不再殘留日期。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF

# 4. baron 手動 commit
git commit -F tmp/PIPE-SLIDES-HOTFIX-6_msg.txt
```
> 簽名更正：提示詞原給 `<noreply@anthreply.com>`（網域誤）→ 更正 `<noreply@anthropic.com>`（型號 Opus 4.8 正確）。

## §9 回退方式
`git revert <HOTFIX-6 hash>`（一步還原 Part A 程式 + Part B 文件註記）或 `cp .claude-logs/archive/2026-06-14_PIPE-SLIDES-HOTFIX-6_slide_pipeline.py.bak pipelines/slide_pipeline.py`。

---

### 結論
🟢 Part A 單頁日期清除落地（4 測試）+ Part B 8 文件 banner + TODO 14 尾註;slide 71 / 全套件 640 passed、SOP 合規、HOTFIX-2 不退化。**殘留母片日期治本 + golden A/B 軌誤述全數更正。** A 軌 golden 不需重捕;baron 影子重傳 Ch37 驗都市農業頁無日期。
