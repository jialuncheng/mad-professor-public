# LANG-DETECT C_CHECKOUT — 收官歸檔（Checkout）執行報告

---

**任務代號**：LANG-DETECT C_CHECKOUT
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/plans/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_plan.md`（v2、已歸檔）
**次級參考**：`.claude-logs/tasks/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_tasks.md`（已歸檔）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C_CHECKOUT)

---

## §1 Conformance 驗收結果（摘要）

**判定：🟢 全數合規**（完整表格見本次 Check 回覆）。

- **目標規格（plan v2 §2 六項）**：cover-prompt +`language` ISO 欄＋Rule 主體語言判定＋Rule 6 keys 同步（搭既有 metadata LLM 便車、零多呼叫）／`_resolve_source_lang` catch-all 限定雙重白名單（`^[a-z]{2,3}$` 且拒 zh 前綴）／繁中 bypass gate 謂詞同源封鎖／P1 單點正名、下游消費端零改／`classify_source_lang` 原職不兼差／零新依賴——全數 ✅。
- **測試計畫（tasks §6）**：C1 驗收 grep 全實貼；875→920 passed；checkout 階段 fresh 重跑 **920 passed, 3 skipped** 再確認。
- **§7.2 跨 Phase 整合測試（Checkout 必驗）**：`tests/test_litedoc_pipeline.py::test_seam_lang_p1_to_p2_glossary_bucket_integration` **存在且通過**——key-changing＝語系 token 由 catch-all `en`→`it`：P1 真 `run_phase1` 正名 → spec 值直通 P2 真 `run_phase2`（旗標開）→ 捕參斷言 `build_termmap` 收到 `source_lang=="it"`＋`target_lang=="zh-tw"`＋P3 gate 謂詞不 bypass；對照組英文文件全鏈仍 `en`、跨文件不互污。**正面達標、無需豁免**。
- **不可動清單**：`pipelines/section_engine.py`（`classify_source_lang`／`detect_zh_tw` 原職）／`models.py`（`GlobalGlossary` schema）git diff 零；cover-prompt 既有五欄規則零動；P3 gate／P2 消費端簽名零改；零第三方偵測套件、零 env flag（Q2 拍板）。
- **SOP 一致性核查**：C1 雙 grep 全數合規（本 commit 零新增日誌點、零 DB）。
- **提示詞歸檔稽核**：tasks／C1 run／Check **3 份俱在** ✅（另 plan／review 2 份依收官前例併入版控、共 5 份）。

### ⚠️ CHECKOUT-GUARD 攔截紀錄（誠實留痕）

Check 首輪 Conformance 通過但**當場攔下收官**——`git log` 偵測 LANG-DETECT C1 從未 commit（`litedoc_pipeline.py`／`tests` 仍為工作區 `M`、HEAD 無 C1 標記）。若當時執行收官 mv＋`git add`，C1 未提交代碼將與 checkout 歸檔文件混入同一 staged set、破壞 commit 邊界。回報 baron → baron 補 `git commit`（C1＝`c17e183`）→ 重下 Check 提示詞 → 本輪收官（git log 已有 C1 hash 可回填、staged set 純歸檔文件）。對齊 CHECKOUT-GUARD 鐵律 dogfood 前例。

---

## §2 Commit 表格（本任務全程）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Language Field & Source-Lang Resolution（語言欄與 source_lang 合成） | `c17e183` |
| C_CHECKOUT | 收官歸檔（本 commit） | [留空，由 baron 回填] |

---

## §3 baton 歸檔確認

一次性 `mv`（標準 mv、非 git mv）＋逐檔 `git add`：plan → `plans/`、tasks → `tasks/`、C1 執行報告 → `executions/`。

`ls .claude-logs/baton/` 實查：本案任務檔**零殘留**；餘留皆合規長駐（PIPE-SPEC／QUEUE-1 v2／PIPE-INGEST-REVIEW design spec〔後續 PIPE-SYNC-5 種子〕／litedoc_shadow_artifacts 與樣本 PDF／README／audit）。

---

## §4 staged-set 自檢（git diff --cached --name-only 實貼）

宣告清單＝**12 檔**（11 檔先行 staged＋本報告）；`.bak` ×2 已隨 C1（`c17e183`）入版控、本次 no-op 不入 staged（與宣告一致）；plan／review 2 份 plan 階段提示詞依前例併入：

```
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/executions/2026-07-21_LANG-DETECT_C1_執行.md
.claude-logs/executions/2026-07-21_LANG-DETECT_checkout_執行.md
.claude-logs/plans/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_plan.md
.claude-logs/prompts/2026-07-21_LANG-DETECT_C1_run_提示詞.md
.claude-logs/prompts/2026-07-21_LANG-DETECT_Check_提示詞.md
.claude-logs/prompts/2026-07-21_LANG-DETECT_plan_提示詞.md
.claude-logs/prompts/2026-07-21_LANG-DETECT_review_提示詞.md
.claude-logs/prompts/2026-07-21_LANG-DETECT_tasks_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/tasks/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_tasks.md
```

已剔除（維持未 staged、跨任務混檔禁令）：SEC-HARDEN／SOP-COMPLY Check 提示詞之外部修改（他任務）、`2026-07-10_PROJECT-REVIEW_審查_提示詞.md`（他任務）、影子 PDF 與長駐 baton 檔。

---

## §5 TODO 雙層結案

- `TODO.md`：active 條目移除；✅ 索引頂部 pointer（`c17e183`、1 commit、checkout 待回填→隨下次 hash 自癒補）；類別索引新增 `### LANG-DETECT (✅ 已完成·cover-prompt 語言欄與 source_lang 正名)`。
- `archive/TODO_done_archive.md`：頂部追加完成表格（C1 hash 已填 `c17e183`）＋修法依據＋影子 E2E 詳步驟註記＋CHECKOUT-GUARD 攔截誠實留痕。

---

## §7 銜接

- **baron 影子 E2E**（plan §8.2）：① 上傳**義大利文樣本**——後端 log `source_lang=it`；`SELECT DISTINCT source_lang FROM global_glossary` 出現 `it` 桶且英文桶無義文新詞（桶隔離 SQL 抽查）；譯文正常繁中。② 英文樣本（SpaceX）回歸 `en`。③ 繁中樣本 `zh` bypass 不翻譯（HOTFIX-1 回歸）、簡體 `hans` 轉繁照舊。
- **後續銜接**（design spec §3.1）：義文樣本進場前置至此完成 → **PIPE-SYNC-5 回灌案**（母 plan v10→v11、PIPE-SPEC v8→v9：ingestion_engine／build_termmap 契約章＋spec F7 門檻更正＋FitzProcessor／閘門契約新章＋**LANG-DETECT language 欄合成契約**）；清詞工具 GLOSSARY-UI 生產後期非前提。

---

## §8 baron 執行命令

```bash
git commit -F /tmp/LANG-DETECT_checkout_msg.txt
```

（git add 已於 Checkout 階段逐檔完成、staged set 見 §4；msg 草稿已寫入 `/tmp/LANG-DETECT_checkout_msg.txt`。）
