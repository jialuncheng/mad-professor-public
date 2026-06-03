# DOMAIN-NORM C5 — Conformance 驗收與收官歸檔執行報告

| 欄位 | 值 |
|---|---|
| **任務代號** | DOMAIN-NORM C5（Check / Checkout） |
| **執行日期** | 2026-06-03 |
| **依據規劃** | plan v2 §2（U1-U4）/ tasks §6（§6.1-§6.4）/ §7 不可動清單 |
| **次級參考** | C1~C4 執行報告 / WORKFLOW_SOP §3 baton 鐵律 / §5 SOP 核查 |
| **落地 Hash** | `待 baron 回填` |
| **狀態** | 全維度合規，已執行收官歸檔，待 baron 手動 commit（CLAUDE.md §1.3） |

---

## §1 基準與完成狀態

- **基準 Commit**：`aeb4fc2`（test: DOMAIN-NORM C4 — DomainNormalizer 單元測試）
- **完成狀態**：三維度 Conformance 全綠 → 執行收官（TODO 結案 + baton 一次性歸檔）。**未 commit / 未 push**。
- **commit hash 對照**：C1=`8d4f75f` / C2=`125af97` / C3=`7e7f2a1` / C4=`aeb4fc2` / C5=`待 baron 回填`。

## §2 Commit 表格

| Commit | 落地 Hash | Subject |
|---|---|---|
| C5 | `待 baron 回填` | DOC-Refactor: DOMAIN-NORM C5 — Conformance 驗收與收官歸檔 |

---

## Conformance 驗收結果

### 目標規格合規性（plan §2 U1-U4）
| # | plan §2 規格項 | 對應執行報告 | 狀態 |
|---|---|---|---|
| 1 | U1 實質內容領域判定與標準化（LLM 內容判定、履歷按技能 HF/QA、Temp=0.0） | C2 §4.3/§5.3 + C4 §5.1（test 1） | ✅ 合規 |
| 2 | U2 領域動態註冊與快取自癒（Domains 動態註冊不塞單字 + DomainMapping 快取防重） | C1 §4 + C2 §4.4/§5.3 + C4 §5.1（test 2/3） | ✅ 合規 |
| 3 | U3 單一入口契約（`normalize_to_lcc(raw_domain, context_text=None)->LCCCode` 逐字對齊 PIPE-SPEC/master v10） | C3 §4.2/§5.1/§5.2 | ✅ 合規 |
| 4 | U4 熱插拔開關（`LLM_USE_GLOSSARY_ALIGN` 預設 False、舊行為零風險） | C3 §4.1/§5.3/§5.5 + C4 §5.1（test 4） | ✅ 合規 |

### 測試計畫合規性（tasks §6.1-§6.4）
| # | tasks §6 驗收條件 | 執行報告驗證 | 本次複驗 | 狀態 |
|---|---|---|---|---|
| 1 | §6.1 C1（兩表新增） | C1 §5.1-§5.3 | `grep -cE "class Domains\|class DomainMapping" models.py` → 2 | ✅ 合規 |
| 2 | §6.2 C2（核心、交易外、冪等） | C2 §5.1-§5.3 | `grep` DomainNormalizer/on_conflict/session.begin/temperature=0.0 → 10 命中 | ✅ 合規 |
| 3 | §6.3 C3（入口與旗標） | C3 §5.1-§5.5 | `grep` normalize_to_lcc/LLM_USE_GLOSSARY_ALIGN → 4+1 命中 | ✅ 合規 |
| 4 | §6.4 C4（單元測試 4 pytest） | C4 §5.1-§5.3 | `pytest tests/test_domain_normalizer.py -q` → **4 passed** | ✅ 合規 |

> 全套件回歸：452 passed（唯一失敗 `test_settings_log_format_default_auto` 為既有 `.env:54 LOG_FORMAT=json` 環境性失敗，與本任務無關，C1-C4 報告均已標註）。

### SOP 一致性核查（WORKFLOW_SOP §5）
| 核查 | 指令 | 結果 |
|---|---|---|
| database §5.2 裸 commit | 掃 `processor/domain_normalizer.py` `.commit()` | 無命中（僅 `with session.begin():`）→ 合規 |
| logging §5.1 exc_info | C2 `logger.error(..., exc_info=True)` | 命中（C2 §5.5）→ 合規 |

### 不可動清單合規性（tasks §7）
| 項目 | git 全量證據 | 狀態 |
|---|---|---|
| `models.py` Paper 表 | C1 僅 +52 行（新增兩表）、既有行 byte 不動 | ✅ 未觸碰 |
| `domain_detector.py` / `rag_retriever.py` / `translate_processor.py` | `git show --stat 8d4f75f 125af97 7e7f2a1 aeb4fc2` 全量過濾後**無任何禁區 .py 命中** | ✅ 未觸碰 |
| `pipeline_core.py` / `web_server.py` / `paper_manager.py` / `static/` | 同上、零命中 | ✅ 未觸碰 |
| 主 repo 目錄 / baton 提前歸檔 | 各報告 §6 全標 ✅ | ✅ 遵守 |

### 提示詞歸檔稽核（`ls prompts/ | grep DOMAIN-NORM`）
| 階段 | 檔案 | 狀態 |
|---|---|---|
| Tasks | `2026-06-03_DOMAIN-NORM_Tasks_提示詞.md` | ✅ 存在 |
| C1 Run | `2026-06-03_DOMAIN-NORM_C1_run_提示詞.md` | ✅ 存在 |
| C2 Run | `2026-06-03_DOMAIN-NORM_C2_run_提示詞.md` | ✅ 存在 |
| C3 Run | `2026-06-03_DOMAIN-NORM_C3_run_提示詞.md` | ✅ 存在 |
| Check | `2026-06-03_DOMAIN-NORM_Check_提示詞.md` | ✅ 存在（含 18:46→18:59 重導紀錄；C4 Unit Tests 由此 Check 重導落地，無獨立 C4 run 提示詞） |

### msg.txt 草稿完整性
| 報告 | §8 msg 草稿 | 狀態 |
|---|---|---|
| C1 | `/tmp/DOMAIN-NORM_C1_msg.txt` | ✅ 完整 |
| C2 | `/tmp/DOMAIN-NORM_C2_msg.txt` | ✅ 完整 |
| C3 | `/tmp/DOMAIN-NORM_C3_msg.txt` | ✅ 完整 |
| C4 | `/tmp/DOMAIN-NORM_C4_msg.txt` | ✅ 完整 |

### 總結
- 🟢 **全部合規** → 執行收官動作（TODO 結案 + baton 一次性歸檔 + 歷史 Hash 自癒）。

---

## §3 變動檔案清單（收官動作）

| 動作 | 檔案 |
|---|---|
| `mv`+`git add` | `baton/...plan_v2.md` → `plans/` |
| `mv`+`git add` | `baton/...tasks.md` → `tasks/` |
| `mv`+`git add` | `baton/...C1~C5_執行.md` → `executions/`（5 份） |
| 修改 | `.claude-logs/TODO.md`（DOMAIN-NORM 移入 ✅ 已完成表 + 移除 active + 索引標 ✅ + C1-C4 Hash 回填 + 歷史全量自癒） |
| 修改 | `.claude-logs/prompts/INDEX.md`（Check 條目 C5 化） |

> 本 C5 報告於收官時一併 `mv` baton→executions/、`git add`。

## §4 修法說明

C5 為驗收與文件歸檔、**零業務代碼改動**。收官三動作：① TODO.md 結案（建 ✅ BE-Refactor DOMAIN-NORM 表、填 C1-C4 真實 Hash、移除 active 條目、索引標 ✅）；② baton/ 七份暫存（plan_v2 + tasks + C1-C5 報告）一次性 `mv` 至正式目錄 + `git add`；③ 驗 baton/ 僅剩 README.md。

## §5 測試結果

- §6.1-§6.4 複驗全綠（見上 Conformance 測試計畫表）；`tests/test_domain_normalizer.py` 4 passed；全套件 452 passed。

## §6 不可動清單遵守

- [x] 業務代碼禁區（detector/retriever/translate/pipeline_core/web_server/paper_manager/static）— git 全量證據零命中。
- [x] `models.py` Paper 表 byte 不動。
- [x] 已歸檔 executions//plans//tasks/ 文件 — C5 不回改。
- [x] 主 repo 目錄 — 未讀寫。

## §7 銜接（baton 狀態 + 下一步）

- **baton 狀態**：收官後 baton/ 僅剩 README.md（DOMAIN-NORM 七份暫存全數歸檔）。
- **任務狀態**：DOMAIN-NORM 全案 5 commit 收官（C1-C5）；**PIPE 大改版三大共用真理源之一 DomainNormalizer 就緒**（GLOSSARY-CORE / Translator 之共同上游）。
- **下一步**：依 PIPE master v10 §8.4，後續路次（PIPE-RESUME / VISUAL / ACADEMIC / LITEDOC / BOOK 策略 + TRANSLATOR / GLOSSARY-CORE）由 baron 後續提示詞觸發。

## §8 baron 執行命令

```bash
# C5 為文件歸檔、無業務代碼改動、無備份
# git add 清單（明確列檔，嚴禁 git add -A/.）
git add .claude-logs/plans/2026-06-01_DOMAIN-NORM_領域標準化對齊器_plan_v2.md
git add .claude-logs/tasks/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md
git add .claude-logs/executions/2026-06-03_DOMAIN-NORM_C1_執行.md
git add .claude-logs/executions/2026-06-03_DOMAIN-NORM_C2_執行.md
git add .claude-logs/executions/2026-06-03_DOMAIN-NORM_C3_執行.md
git add .claude-logs/executions/2026-06-03_DOMAIN-NORM_C4_執行.md
git add .claude-logs/executions/2026-06-03_DOMAIN-NORM_C5_執行.md
git add .claude-logs/TODO.md
git add .claude-logs/prompts/2026-06-03_DOMAIN-NORM_Check_提示詞.md
git add .claude-logs/prompts/INDEX.md

# commit message 草稿（已寫入 /tmp/DOMAIN-NORM_C5_msg.txt）
cat /tmp/DOMAIN-NORM_C5_msg.txt

# baron 手動執行
git commit -F /tmp/DOMAIN-NORM_C5_msg.txt
```
