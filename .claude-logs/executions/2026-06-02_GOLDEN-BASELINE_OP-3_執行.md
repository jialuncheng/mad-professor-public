# GOLDEN-BASELINE OP-3 — Checkout / 收官歸檔 執行報告

---

**任務代號**：GOLDEN-BASELINE OP-3（Checkout）
**執行日期**：2026-06-02
**依據規劃**：`.claude-logs/baton/2026-06-01_GOLDEN-BASELINE_黃金基準存盤與退化比對_plan_v2.md`
**次級參考**：`.claude-logs/baton/2026-06-02_GOLDEN-BASELINE_黃金基準存盤與退化比對_tasks.md` §8 OP-3
**Git commit hash**：留空，由 baron 回填
**狀態**：✅ Completed (OP-3 收官)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動 ｜ 改版規則：直接修改對應章節 + §99.2 加 Revision ｜ 完整治理規格 → §99

---

## §1 基準與完成狀態

- **執行前基準**：OP-1（`3be0b0d`）+ OP-2（`74d34e8`）已 ship；五路 golden 快照與 diff 引擎齊備、自比對歸零 PASS。plan/tasks/OP-1/OP-2 報告仍暫存 baton/。
- **完成狀態**：✅ Conformance 三維度全合規（見 §5 Conformance 表）；一次性歸檔 plan→`plans/`（保留 `_v2`）、tasks→`tasks/`、OP-1/OP-2/OP-3 報告→`executions/` + `git add`；TODO.md 結案（GOLDEN-BASELINE 移入 ✅ 已完成表 + 索引標 ✅ + 歷史 Hash 自癒）。業務代碼零改動。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| OP-1 | 黃金基準 capture 工具 + 固定 query set + 五路物理存盤 | `3be0b0d` |
| OP-2 | 自動化 Regression Diff 比對引擎 + 18 pytest + 五路自比對歸零 | `74d34e8` |
| OP-3 | Checkout 收官歸檔（mv plan/tasks/三報告 + TODO 結案） | 留空，由 baron 回填 |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 說明 |
|---|---|---|
| 移動+追蹤 | `plans/2026-06-01_GOLDEN-BASELINE_..._plan_v2.md` | 自 baton/ 歸檔（保留 `_v2`） |
| 移動+追蹤 | `tasks/2026-06-02_GOLDEN-BASELINE_..._tasks.md` | 自 baton/ 歸檔 |
| 移動+追蹤 | `executions/2026-06-02_GOLDEN-BASELINE_OP-1_執行.md` | 自 baton/ 歸檔 |
| 移動+追蹤 | `executions/2026-06-02_GOLDEN-BASELINE_OP-2_執行.md` | 自 baton/ 歸檔 |
| 移動+追蹤 | `executions/2026-06-02_GOLDEN-BASELINE_OP-3_執行.md` | 本報告，自 baton/ 歸檔 |
| 新建+追蹤 | `prompts/2026-06-02_GOLDEN-BASELINE_Check_提示詞.md` | Check 提示詞歸檔 |
| 修改 | `prompts/INDEX.md` | 登記 Check 提示詞 |
| 修改 | `.claude-logs/TODO.md` | GOLDEN-BASELINE 結案 + 歷史 Hash 自癒 |

---

## §4 修法說明

純文件治理（DOC 收官），無代碼改動：
1. Conformance 三維度逐項驗收（§5）。
2. 一次性 `mv` baton/ 5 份暫存 → `plans/` / `tasks/` / `executions/` + `git add`（WORKFLOW_SOP §3 收官歸檔鐵律）。
3. TODO.md：✅ 已完成新增 GOLDEN-BASELINE 表（OP-1 `3be0b0d` / OP-2 `74d34e8` / OP-3 待回填）+ 刪 active 條目 + 索引標 ✅。

---

## §5 測試結果（Conformance 驗收）

### §5.1 本地改動狀態確認
```bash
$ git status -s   # baton/ 5 份 mv 至 plans/tasks/executions、prompts/TODO/INDEX 已追蹤
```

### §5.2 Conformance 驗收結果

#### 目標規格合規性
| # | plan §2 規格項 | 對應執行報告 | 狀態 |
|---|---|---|---|
| 1 | U1. 五路代表性 PDF 凍結 | OP-1 §1 & §3（fixtures 五路置入並存盤） | 🟢 合規 |
| 2 | U2. 三維度黃金產物與 manifest | OP-1 §4 + 實測 golden/ 五路 D1/D2/D3+manifest 齊全 | 🟢 合規 |
| 3 | U3. Diff 引擎比對與雙格式報告 | OP-2 §4.1（D1 結構樹/D2 相似度/D3 Jaccard + json+md） | 🟢 合規 |
| 4 | U4. 紅綠燈裁決與已知改善豁免 | OP-2 §4.1（PASS/FAIL/IMPROVEMENT_PENDING_REVIEW + `--improvement`） | 🟢 合規 |
| 5 | U7. CLI 工具、測試檔、快照齊備 | OP-1/OP-2 §3（golden_baseline.py + test_golden_baseline.py + golden/） | 🟢 合規 |

#### 測試計畫合規性
| # | tasks §6 驗收條件 | 執行報告驗證 | 狀態 |
|---|---|---|---|
| 1 | OP-1: 五路快照與 manifest 齊全 | OP-1 §5（baron 端實跑存盤）+ 實測 ls 五路齊全 | 🟢 合規 |
| 2 | OP-1: capture 防覆寫閘生效 | OP-1 §5.2（ABORT + JSON logging） | 🟢 合規 |
| 3 | OP-2: 18 項比對引擎測試全綠 | OP-2 §5.2（18 passed） | 🟢 合規 |
| 4 | OP-2: 五路自比對歸零 PASS | OP-2 §5.2（五路 verdict=PASS + 負向竄改 FAIL） | 🟢 合規 |

#### 不可動清單合規性
| 項目 | 核對狀態 | 狀態 |
|---|---|---|
| 核心業務代碼（pipeline_core/web_server/rag_retriever/models/paper_manager/processor） | OP-1/OP-2 §6 標「✅ 未觸碰」+ git show e24f48e/3be0b0d/74d34e8 變動檔案無命中業務代碼 | 🟢 合規 |
| 主 repo 目錄 | 全部執行報告 §6 標「✅ 未讀寫」 | 🟢 合規 |

#### 提示詞歸檔稽核
```bash
$ ls .claude-logs/prompts/ | grep "GOLDEN-BASELINE"
2026-06-02_GOLDEN-BASELINE_Tasks_提示詞.md
2026-06-02_GOLDEN-BASELINE_Tasks_修正提示詞.md
2026-06-02_GOLDEN-BASELINE_OP-1_run_提示詞.md
2026-06-02_GOLDEN-BASELINE_OP-2_run_提示詞.md
2026-06-02_GOLDEN-BASELINE_Check_提示詞.md
# plan(Tasks/修正) / OP-1 run / OP-2 run / Check 各階段實體齊全 🟢
```

#### msg.txt 草稿完整性
| 報告 | §8 commit 草稿 | 狀態 |
|---|---|---|
| OP-1 §8 | `/tmp/GOLDEN-BASELINE_OP-1_msg.txt`（誠實改寫、揭露物理存盤待 MinerU） | 🟢 完整 |
| OP-2 §8 | `/tmp/GOLDEN-BASELINE_OP-2_msg.txt`（diff 引擎 + 18 pytest + 自比對歸零） | 🟢 完整 |

#### 總結
- 🟢 **全部合規** → 執行收官歸檔動作（見 §3 / §4）。

### §5.3 SOP 一致性核查
DOC 收官工作流、無 `.py` 改動，跳過 logging/database SOP 核查（合規）。

---

## §6 不可動清單遵守

| 項目 | 狀態 |
|---|---|
| 業務代碼（pipeline_core/web_server/rag_retriever/models/paper_manager/processor） | [x] ✅ 未觸碰 |
| 主 repo 目錄 | [x] ✅ 未讀寫 |
| 已移入 plans//tasks//executions/ 的正式檔 | [x] ✅ 移動後未再改動 |

---

## §7 銜接

- **baton/ 狀態**：本階段一次性 `mv` plan/tasks/OP-1/OP-2/OP-3 報告至正式目錄後，baton/ 僅剩 `README.md`（純淨）。
- **消化歸檔之 baton 檔 → Git hash 映射（Traceability）**：
  - `plan_v2.md` → `plans/`（隨 Check commit）
  - `tasks.md` → `tasks/`（隨 Check commit）
  - `OP-1_執行.md` → `executions/`（對應落地 commit `3be0b0d`）
  - `OP-2_執行.md` → `executions/`（對應落地 commit `74d34e8`）
  - `OP-3_執行.md` → `executions/`（隨 Check commit、hash 待 baron 回填）
- **下一步**：GOLDEN-BASELINE 全案收官。新核心（PIPE-CORE）落地後，shadow 候選接入 `diff` 即可每路絞殺後自動退化比對。
- **後續任務**：依 PIPE master plan v9 §8 路線圖，GOLDEN-BASELINE（階段 1）已完成，可推進階段 2 三大真理源 / 階段 3 五路絞殺。

---

## §8 baron 執行命令

> ℹ️ **Check 收官 §8 僅保留一行 commit 指令**；所有 `mv` + `git add` 已於本報告 §3/§4 完成。

```bash
# git add 清單（mv + add 已執行；此處為 baron 複核用，hash 由 baron 回填 TODO 後 commit）
# 已 add：plans/ tasks/ executions/（5 份）+ prompts/Check + prompts/INDEX.md + TODO.md
git commit -F /tmp/GOLDEN-BASELINE_Check_msg.txt
```

### §8.2 commit message 草稿

```
DOC-Refactor: GOLDEN-BASELINE Check — Conformance 驗收 + baton/ 全量歸檔 + 結案

1. Conformance 三維度全合規（目標規格 U1-U7 / 測試計畫 OP-1+OP-2 / 不可動清單）。
2. 一次性歸檔 baton/：plan_v2→plans/、tasks→tasks/、OP-1/OP-2/OP-3 報告→executions/。
3. TODO.md GOLDEN-BASELINE 結案（OP-1 3be0b0d / OP-2 74d34e8）+ 索引標 ✅ + 歷史 Hash 自癒。
4. baton/ 回歸純淨（僅 README.md）。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 記錄 GOLDEN-BASELINE OP-3 收官的 Conformance 驗收與歸檔軌跡，作為 Traceability 審計依據 |
| **用途** | 隨 Check commit 歸檔至 executions/；全案結案憑證 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | TODO.md ✅ 已完成 GOLDEN-BASELINE 表 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁自動 git commit；hash 待 baron 人工回填 |
| **改版觸發條件** | 收官修正 / baron 重新驗收 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 永久保留歸檔於 executions/，不刪除 |
| **重複防護** | 本檔為 OP-3 收官唯一源，不重複 OP-1/OP-2 實作細節 |

### §99.2 Revision 歷程

- v1 (2026-06-02)：OP-3 Checkout 收官——Conformance 三維度全合規（目標規格 U1-U7 / 測試計畫 OP-1+OP-2 / 不可動清單 git 驗證）；一次性 `mv` baton/ plan_v2+tasks+OP-1+OP-2+OP-3 報告至 plans//tasks//executions/ + `git add`；TODO.md 結案（OP-1 `3be0b0d` / OP-2 `74d34e8` / OP-3 待回填）+ 索引標 ✅ + 歷史 Hash 自癒；baton/ 回歸純淨。
