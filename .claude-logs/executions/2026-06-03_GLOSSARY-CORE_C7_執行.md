# GLOSSARY-CORE C7 — Conformance 驗收與收官歸檔執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | GLOSSARY-CORE C7（Checkout） |
| **執行日期** | 2026-06-04 |
| **依據規劃** | plan v2 §2（U1-U5）/ tasks §6（§6.1-§6.6）/ §7 不可動清單 |
| **次級參考** | C1~C6 執行報告 / WORKFLOW_SOP §3 baton 鐵律 / §5 SOP 核查 |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 三維度合規，已執行收官歸檔，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`ae705d5`（BE-Refactor: C6 — Unit Tests）
- **完成狀態**：三維度 Conformance 全綠 → 執行收官（TODO 結案 + baton 一次性歸檔）。**未 commit / 未 push**。
- **commit hash 對照**：C1=`03d85c8` / C2=`9af971f` / C3=`fd0e84f` / C4=`06bf3df` / C6=`ae705d5` / **C5=未提交（見下）** / C7=`待 baron 回填`。

> ⚠️ **C5 未提交揭露**：`tools/manage_glossary.py`（C5 交付物）目前仍 **untracked**（baron 提交 C6 `ae705d5` 時未含此檔；本 Check 提示詞 §8 git add 清單亦未列）。為杜絕「已交付未入版控」缺口，本 C7 §8 git add 清單**已補入** `git add tools/manage_glossary.py`，使其隨 C7 收官 commit 一併落地。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C7 | `待 baron 回填` | BE-Refactor: C7 — Checkout（收官與成果審計） |

---

## Conformance 驗收結果

### 目標規格合規性（plan §2 U1-U5）
| # | plan §2 規格項 | 對應執行報告 | 狀態 |
|---|---|---|---|
| 1 | U1 Global Glossary DB Schema（聯合唯一索引） | C1 §4/§5 | ✅ 合規 |
| 2 | U2 Cascading Priority Retrieval（專屬覆寫 general） | C2 §4/§5 | ✅ 合規 |
| 3 | U3 Book Translation Integration | C3 §4/§5 | ✅ 合規（單文 translate 注入+回填完成；書籍 `ParallelChapterTranslator` 雙層融合按 tasks §9 延後至 TRANSLATE-BOOK 落地） |
| 4 | U4 Chat Integration（System constraint 注入） | C4 §4/§5 | ✅ 合規 |
| 5 | U5 Hot-Pluggable CLI（三子命令） | C5 §4/§5 | ✅ 合規 |

### 測試計畫合規性（tasks §6.1-§6.6）
| # | tasks §6 驗收條件 | 本次複驗 | 狀態 |
|---|---|---|---|
| 1 | §6.1 C1（兩表/唯一約束） | `grep class GlobalGlossary\|uq_glossary` → 2 | ✅ 合規 |
| 2 | §6.2 C2（核心/交易外/級聯） | `grep query_cascade\|on_conflict\|session.begin\|extract_terms` → 8 | ✅ 合規 |
| 3 | §6.3 C3（translate 旗標閘門+回填） | `grep LLM_USE_GLOSSARY_ALIGN\|GLOSSARY-CORE C3`（兩檔）→ 12 | ✅ 合規 |
| 4 | §6.4 C4（Chat 注入） | `grep LLM_USE_GLOSSARY_ALIGN\|GLOSSARY-CORE C4` → 6 | ✅ 合規 |
| 5 | §6.5 C5（CLI 子命令） | 檔存在 + `grep init\|test-pipeline\|backfill` → 12 | ✅ 合規 |
| 6 | §6.6 C6（5 pytest） | `pytest tests/test_glossary_core.py -q` → **5 passed** | ✅ 合規 |

> 全套件回歸：457 passed（唯一失敗 `test_settings_log_format_default_auto` 為既有 `.env:54 LOG_FORMAT=json` 環境性失敗，與本任務無關，各報告已標註）。

### SOP 一致性核查（WORKFLOW_SOP §5）
| 核查 | 結果 |
|---|---|
| database §5.2 裸 commit（glossary_extractor / manage_glossary） | 無命中（僅 `session.begin()`）→ 合規 |
| logging §5.1 exc_info / setup_logging | glossary_extractor 3 處 exc_info / manage_glossary 用 setup_logging 無 basicConfig → 合規 |

### 不可動清單合規性（tasks §7）
| 項目 | git 全量證據 | 狀態 |
|---|---|---|
| `models.py` Paper 等既有表 | C1 僅 +39（新增 GlobalGlossary）、既有 byte 不動 | ✅ 未觸碰 |
| `translate_processor.py` / `pipeline_core.py` / `AI_professor_chat.py` 旗標閘門以外 | 全旗標閘門 + 標記包裹 + 旗標 OFF byte 等價（C3/C4 §5 證實） | ✅ 未越界 |
| `normalize_to_lcc` / `Domains` / `DomainMapping`（DOMAIN-NORM） | 僅呼叫消費、未改 | ✅ 未觸碰 |
| `rag_retriever.py` / `tiling_processor.py` | 零命中 | ✅ 未觸碰 |
| RAG-14 既存改動（C4 隔離） | C4 只 stage C4 hunks、RAG-14 由 baron 獨立 commit `595e3d8` | ✅ 隔離 |

### 提示詞歸檔稽核（`ls prompts/ | grep GLOSSARY-CORE`）
| 階段 | 檔案 | 狀態 |
|---|---|---|
| Tasks / C1 / C2 / C3 / C4 / C5 / C6 / Check | 8 份齊全 | ✅ |

### msg.txt 草稿完整性
| 報告 | §8 草稿（`cat > tmp/...`）| 狀態 |
|---|---|---|
| C1-C6 | `tmp/GLOSSARY-CORE_C1~C6_commit_msg.txt` | ✅ 完整 |

### 總結
- 🟢 **全部合規** → 執行收官動作（TODO 結案 + baton 一次性歸檔 + 歷史 Hash 自癒）。
- ⚠️ 附帶提醒：C5 `manage_glossary.py` 未提交，已納入 C7 §8 git add 清單補正。

---

## §3 變動檔案清單（收官動作）

| 動作 | 檔案 |
|---|---|
| `mv`+`git add` | `baton/...plan_v2.md` → `plans/` |
| `mv`+`git add` | `baton/...tasks.md` → `tasks/` |
| `mv`+`git add` | `baton/...C1~C7_執行.md` → `executions/`（7 份） |
| `git add`（補正） | `tools/manage_glossary.py`（C5 未提交交付物） |
| 修改 | `.claude-logs/TODO.md`（GLOSSARY-CORE 移入 ✅ 已完成表 + 移除 active + 索引標 ✅ + C1-C6 Hash 回填 + 歷史全量自癒） |
| 修改 | `.claude-logs/prompts/INDEX.md`（Check 條目） |

## §4 修法說明

C7 為驗收與文件歸檔、**零業務代碼改動**。收官三動作：① TODO.md 結案（建 ✅ BE-Refactor GLOSSARY-CORE 表、填 C1-C6 真實 Hash、移除 active、索引標 ✅）；② baton/ 八份暫存（plan_v2 + tasks + C1-C7 報告）一次性 `mv` 至正式目錄 + `git add`；③ 驗 baton/ 無 GLOSSARY-CORE 殘留。另補正 C5 `manage_glossary.py` 入 git add。

## §5 測試結果

- §6.1-§6.6 複驗全綠（見上 Conformance 測試計畫表）；`tests/test_glossary_core.py` 5 passed；全套件 457 passed。

## §6 不可動清單遵守

- [x] 業務代碼禁區（rag_retriever / tiling_processor / DOMAIN-NORM 結構）— git 全量證據零命中。
- [x] 已歸檔 executions//plans//tasks/ 文件 — C7 不回改。
- [x] 主 repo 目錄 — 未讀寫。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：收官後 baton/ 無 GLOSSARY-CORE 殘留（八份暫存全數歸檔）。
- **任務狀態**：GLOSSARY-CORE 全案 7 commit 收官（C1-C7）；**PIPE 大改版三大共用真理源之二「中央領域術語庫」就緒**（消費 DomainNormalizer LCC、translate/chat 一致性注入、自癒 CLI）。
- **延後項**：書籍並行 `ParallelChapterTranslator` 雙層融合待 TRANSLATE-BOOK 落地後整合（tasks §9）。

## §8 baron 執行命令

```bash
# C7 為文件歸檔 + C5 交付物補正、無業務代碼邏輯改動、無備份
# git add 清單（明確列檔，嚴禁 git add -A/.）
git add tools/manage_glossary.py                                                   # C5 交付物補正（先前未提交）
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-04_GLOSSARY-CORE_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/plans/2026-06-01_GLOSSARY-CORE_中央領域術語庫_plan_v2.md
git add .claude-logs/tasks/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md
git add .claude-logs/executions/2026-06-03_GLOSSARY-CORE_C1_執行.md
git add .claude-logs/executions/2026-06-03_GLOSSARY-CORE_C2_執行.md
git add .claude-logs/executions/2026-06-03_GLOSSARY-CORE_C3_執行.md
git add .claude-logs/executions/2026-06-03_GLOSSARY-CORE_C4_執行.md
git add .claude-logs/executions/2026-06-03_GLOSSARY-CORE_C5_執行.md
git add .claude-logs/executions/2026-06-03_GLOSSARY-CORE_C6_執行.md
git add .claude-logs/executions/2026-06-03_GLOSSARY-CORE_C7_執行.md

# commit message 草稿（已寫入 tmp/GLOSSARY-CORE_C7_commit_msg.txt）
cat tmp/GLOSSARY-CORE_C7_commit_msg.txt

# baron 手動執行
git commit -F tmp/GLOSSARY-CORE_C7_commit_msg.txt
```
