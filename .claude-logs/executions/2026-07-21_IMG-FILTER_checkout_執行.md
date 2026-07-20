# IMG-FILTER C_CHECKOUT — 收官歸檔（Checkout）執行報告

---

**任務代號**：IMG-FILTER C_CHECKOUT
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/plans/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_plan.md`（v2、已歸檔）
**次級參考**：`.claude-logs/tasks/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`（已歸檔）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C_CHECKOUT)

---

## §1 Conformance 驗收結果（摘要）

**判定：🟢 全數合規**（完整表格見本次 Check 回覆、依 template_prompt_for_check 第二步格式）。

- **目標規格（plan v2 §2 八項）**：過濾器三規則本體（C1）／engine 純加法注入＋**DROP caption `used[cap_idx]=True` 防孤兒圖說**（C2）／litedoc 報頭預掃接線＋行界收窄（C3）／三常數 env 可調／**門檻校正禁令全程遵守**（100k／4.0／廢長邊軸、spec F7 原始數字零使用）——全數 ✅。
- **測試計畫（tasks §6）**：各 commit 驗收 grep 全實貼；805→822→827→831 passed、逐 commit 0 failed；checkout 階段 fresh 重跑 **831 passed, 3 skipped** 再確認。
- **§7.2 跨 Phase 整合測試（Checkout 必驗）**：`tests/test_ingestion_engine.py::TestImageFilterIntegration` **存在且通過**——實體 header-only PNG＋擬真 md＋判型 dict → 真 `_build_tiles` 端到端（真 TilingProcessor bypass、真 image_filter 讀檔）：報頭小圖 DROP（③＋①雙保險）、**481×369 內文 chart KEEP（門檻校正守門）**、大圖 content＋caption 穿透 tiling、DROP 圖 caption 未殘留。**正面達標、無需豁免**。
- **不可動清單**：C1-C3 §6 全項打勾（resume／slides／A 軌／contracts 零碰；engine 純加法預設等價；Vision 零參與 Drop）。
- **SOP 一致性核查**：三 commit 雙 grep 全數「無命中（合規）」（本案全程零 DB、審計 log 依規範）。
- **提示詞歸檔稽核**：tasks／C1-C3 run／Check **5 份俱在** ✅（另 plan／review 2 份依 PIPE-INGEST 收官前例併入版控）。

---

## §2 Commit 表格（本任務全程）

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Image Filter Module（圖片過濾器模組） | `de3a475` |
| C2 | Engine Figure-Filter Hook（引擎純加法注入點） | `f39f8cb` |
| C3 | Litedoc Pre-pass Wiring（litedoc 報頭預掃接線） | `8cfaf5b` |
| C_CHECKOUT | 收官歸檔（本 commit） | [留空，由 baron 回填] |

---

## §3 baton 歸檔確認

一次性 `mv`（標準 mv、非 git mv）＋逐檔 `git add`：plan → `plans/`、tasks → `tasks/`、C1-C3 執行報告 → `executions/` ×3。

`ls .claude-logs/baton/` 實查：本案任務檔**零殘留**；餘留皆合規長駐（PIPE-SPEC／QUEUE-1 v2／PIPE-INGEST-REVIEW design spec〔後續 FITZ／LANG-DETECT 種子〕／litedoc_shadow_artifacts 與樣本 PDF／README／audit）。

---

## §4 staged-set 自檢（git diff --cached --name-only 實貼）

宣告清單＝**16 檔**（15 檔先行 staged＋本報告）；`.bak` ×7（C1×2/C2×2/C3×3）已隨各 commit（`de3a475`／`f39f8cb`／`8cfaf5b`）入版控、本次 no-op 不入 staged（與宣告一致）；plan／review 2 份 plan 階段提示詞依前例併入：

```
.claude-logs/TODO.md
.claude-logs/archive/TODO_done_archive.md
.claude-logs/executions/2026-07-20_IMG-FILTER_C1_執行.md
.claude-logs/executions/2026-07-20_IMG-FILTER_C2_執行.md
.claude-logs/executions/2026-07-21_IMG-FILTER_C3_執行.md
.claude-logs/executions/2026-07-21_IMG-FILTER_checkout_執行.md
.claude-logs/plans/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_plan.md
.claude-logs/prompts/2026-07-20_IMG-FILTER_C1_run_提示詞.md
.claude-logs/prompts/2026-07-20_IMG-FILTER_C2_run_提示詞.md
.claude-logs/prompts/2026-07-20_IMG-FILTER_plan_提示詞.md
.claude-logs/prompts/2026-07-20_IMG-FILTER_review_提示詞.md
.claude-logs/prompts/2026-07-20_IMG-FILTER_tasks_提示詞.md
.claude-logs/prompts/2026-07-21_IMG-FILTER_C3_run_提示詞.md
.claude-logs/prompts/2026-07-21_IMG-FILTER_Check_提示詞.md
.claude-logs/prompts/INDEX.md
.claude-logs/tasks/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md
```

已剔除（維持未追蹤／未 staged、跨任務混檔禁令）：影子 PDF ×4、`litedoc_shadow_artifacts/`、`2026-07-10_PROJECT-REVIEW_審査_提示詞.md`（他任務）、SEC-HARDEN／SOP-COMPLY Check 提示詞之外部修改（他任務）。

---

## §5 TODO 雙層結案

- `TODO.md`：active 條目移除；✅ 索引頂部 pointer（`de3a475`…`8cfaf5b`、3 commits、checkout 待回填→隨下次 hash 自癒補）；類別索引新增 `### IMG-FILTER (✅ 已完成·垃圾圖確定性過濾)`。
- `archive/TODO_done_archive.md`：頂部追加完成表格（C1-C3 hash 已填）＋修法依據＋影子 E2E 詳步驟註記。

---

## §7 銜接

- **baron 影子 E2E**（plan §8.2 硬判）：重傳 `SpaceX & the Sentient Sun.pdf`——3 垃圾圖（Share 鈕／頭像裝飾／互動列橫條）消失、20 內容全在（**特驗** `9896a383` 481×369 chart 與 `366e4094` hero 無人船照）、後端 log 三筆 DROP 審計（src＋尺寸＋規則）；重傳第二樣本（`The_hidden_risks_in_Taiwan_s_boom`）驗門檻泛化零誤殺；RAG 一輪迴歸。誤殺應急：`IMG_FILTER_ENABLED=false` env 單點關回。
- **後續銜接**：**PIPE-INGEST-FITZ**（F6、born-digital 文字層＋連字修復）→ **LANG-DETECT**（F4、義文樣本前必做）→ **PIPE-SYNC-5 回灌案**（母 plan v10→v11、PIPE-SPEC v8→v9：含 ingestion_engine／build_termmap 契約章＋**spec F7 門檻更正**〔廢長邊軸、面積 100k、規則③收窄——本案實測校正回灌〕）；glossary 清詞工具 GLOSSARY-UI 生產後期非前提。

---

## §8 baron 執行命令

```bash
git commit -F /tmp/IMG-FILTER_checkout_msg.txt
```

（git add 已於 Checkout 階段逐檔完成、staged set 見 §4；msg 草稿已寫入 `/tmp/IMG-FILTER_checkout_msg.txt`。）
