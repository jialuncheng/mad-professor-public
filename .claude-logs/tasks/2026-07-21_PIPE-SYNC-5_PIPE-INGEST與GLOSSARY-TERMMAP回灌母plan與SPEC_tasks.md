# PIPE-SYNC-5 PIPE-INGEST 與 GLOSSARY-TERMMAP 回灌母 plan 與 SPEC — Tasks

> 本文件為 PIPE-SYNC-5 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-21_PIPE-SYNC-5_..._plan.md`（v2、五 OQ 已拍板）產出，含 **1 個開發 Commit + 1 個 Checkout**（⚠️ 原拆 C1/C2 兩開發 commit，baron C1 提示詞合併為單一 C1，Checkout 階段依實況更正、見 §8 更正註）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | — |
| **修改檔案** | 3 個 | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md`（更至 v9） / `.claude-logs/plans/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v10.md`（就地補註） / `.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md`（F7 門檻更正） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 2 個 | C1（合併版·三文件一次回灌、`cc53452`）→ C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` plan/tasks/C1 執行報告 → `plans/` + `tasks/` + `executions/` + 逐檔 `git add` |

> ⚠️ `.bak` 說明：PIPE-SPEC 與 design spec 為長駐 baton 檔（gitignored）、母 plan 為 tracked——三檔之 `.bak` 一律置 `.claude-logs/archive/`（tracked、審計存檔·對齊 RESCUE-1「archive `.bak` 防再遺失閘門」慣例），並於對應 commit 之 git add 清單強制包含。

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-INGEST（`ingestion_engine` 攝入引擎、借用鏈退場、譯題單一源）與 GLOSSARY-TERMMAP（`build_termmap` 事前定案）兩案已 ship，但兩真理源（PIPE-SPEC v8、母 plan v10）未回灌、design spec F7 仍載作廢門檻。
- **解法**：`C1 — Spec & Plan Backfill（規格書與母計畫回灌）`〔**合併版·三文件一次回灌**〕（① PIPE-SPEC v8→v9：§1.2.6 ingestion_engine 契約章 + §1.2.6.1 litedoc 借用鏈退場/譯題單一源 + §1.2.2.1 build_termmap 事前定案 + 家族 roster 第 6 員 + 旗標 true 註 + Revision v9；② 母 plan U7/U8/§8.5 就地補註 + Revision；③ design spec F7 門檻更正）→ `C_CHECKOUT — 收官歸檔（收官歸檔）`。
- **影響範圍**：100% DOC-Refactor；3 份治理文件；零業務代碼、零 schema、零測試新增。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| PIPE-SPEC v8（baton 長駐） | §1.2 家族 5 員（三大+MetaNormalizer+section_engine）；§1.2.2 GLOSSARY-CORE 無 build_termmap；§99.2 至 v8 | 無 ingestion_engine 契約章；build_termmap 未登記；litedoc 借用鏈退場/譯題單一源未反映 |
| 母 plan v10（tracked） | U8 三大+第 4/5 家族；§8.5 PIPE-LITEDOC ✅ | 無第 6 ingestion_engine；PIPE-INGEST/GLOSSARY-TERMMAP/IMG-FILTER 未登記；U7 LiteDoc 未補現況 |
| design spec F7（baton） | L123 規則① `MIN_LONG_SIDE 600`/`MIN_AREA 200k` | 與 IMG-FILTER 實測校正（100k/廢長邊軸）矛盾、恐誤導後續 |

---

## §3 觀察問題

### 問題 #1：ingestion_engine 無契約章（家族缺員）
- **證據**：PIPE-SPEC §1.2 roster 止於第 5 section_engine；`pipelines/ingestion_engine.py` 已落地（`assemble` 純函式、零 doc_type）。
- **影響**：後續管線（academic/book）規劃時無攝入引擎介面真理源可依、doc-drift 風險。

### 問題 #2：build_termmap 未登記於 GLOSSARY-CORE
- **證據**：PIPE-SPEC §1.2.2 僅載舊自癒演算法；`glossary_extractor.py:331 build_termmap` 已為五路共用 builder。
- **影響**：事前定案（取代收割）之演進未入真理源、術語一致硬驗收依據缺席。

### 問題 #3：design spec F7 作廢門檻
- **證據**：design spec L123 `MIN_LONG_SIDE 600`/`MIN_AREA 200k`；`settings.py` L130 `IMG_FILTER_MIN_AREA=100000`（廢長邊軸）。
- **影響**：未來讀 F7 恐重踩「481×369 內容 chart 誤殺」坑。

---

## §4 設計方案

### §4.1 C1 — Spec & Plan Backfill（規格書與母計畫回灌）〔合併版〕
就地 `<!-- [PIPE-SYNC-5 Dn] -->` 補註三份治理文件（plan §2.1–§2.3 一次到位）：**① PIPE-SPEC v8→v9**——D1 新增 §1.2.6 ingestion_engine 契約章（家族第 6 員、`assemble` 簽名/四鐵律/figure_filter hook）+ §1.2.6.1 litedoc 借用鏈退場/譯題單一源（原 D4 併入）；D2 §1.2.2 內補 §1.2.2.1 build_termmap 事前定案 builder 五步；D3 §0.3 家族 roster 增第 6 員；D5 `LLM_USE_GLOSSARY_ALIGN` 預設 true 註；D6 §4 Change Log + §99.2 Revision v9。**② 母 plan**——D_U7 LiteDoc 現況、D_U8 roster 第 6 員 + build_termmap 演進註、D_85 §8.5 補三案 ✅（hash + 產出檔）、Revision 加列。**③ design spec F7**——D_F7 規則① 廢長邊軸改 `area < 100000`、規則③ 收窄、補實測校正註。四凍結合約結構零變動（§2.1 不改鐵律）。

### §4.2 C_CHECKOUT — 收官歸檔（收官歸檔）
Conformance（plan §2 對照 + §8.2 DOC 驗收 6 項 + 純 DOC §7.2 豁免）→ TODO 雙層結案 → baton 一次性 `mv` + 逐檔 `git add` → `checkout_執行.md`（staged-set 實貼）→ `/tmp` msg。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 誤動四凍結合約結構 | 🟢 低 | C1 §2.1 不改鐵律；HTML 註解包裹增修、§6.1 grep 驗四合約區塊零改 |
| 契約章與現役代碼 doc-drift | 🟢 低 | §6 驗收 assemble/build_termmap 簽名對照落地 grep（實貼零落差） |
| 母 plan 引用 SPEC 未落地章號 | 🟢 低 | ~~依賴關係鎖 C1→C2~~ → **合併版 C1 三文件同 commit**、章號於同 commit 內建立、無跨 commit 懸掛；驗收含 §1.2.6/§1.2.2.1 章號存在檢查 |
| 誤觸業務代碼/測試 | 🟢 低 | DOC-Refactor 零碰；§6 pytest 920 passed 防呆 + `git status` 僅 3 文件 |
| .bak 混檔 | 🟢 低 | 三檔 .bak 逐檔顯式列名於對應 commit git add；收官白名單自檢 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
grep -n "§1.2.6\|ingestion_engine" .../PIPE-SPEC_...specification.md   # 期望：§1.2.6 契約章命中
grep -n "build_termmap\|事前定案" .../PIPE-SPEC_...specification.md    # 期望：§1.2.2 內命中
grep -c "第 6\|ingestion_engine" .../PIPE-SPEC_...specification.md      # 期望：家族 roster 含第 6 員
grep -n "v9 (2026-07-21)\|PIPE-SYNC-5" .../PIPE-SPEC_...specification.md # 期望：Revision v9 + 就地註解
grep -c "PIPE-SYNC-5" .../PIPE-SPEC_...specification.md                 # 期望：與 D1-D6 補註數一致
# 四凍結合約守恆（§1.1 區塊零改）——與 .bak diff 僅 D1-D6 增修
```

### §6.2 母 plan 與 design spec 驗收（合併版 C1 之②③組）

```bash
grep -n "第 6\|ingestion_engine" .../PIPE_...plan_v10.md                # 期望：U8 roster 補第 6
grep -n "PIPE-INGEST\|GLOSSARY-TERMMAP\|IMG-FILTER" .../PIPE_...plan_v10.md  # 期望：§8.5 三案登記
grep -n "PIPE-SYNC-5" .../PIPE_...plan_v10.md                           # 期望：就地補註 + Revision
grep -n "MIN_LONG_SIDE\|200k" .../2026-07-19_PIPE-INGEST-REVIEW_design_spec.md  # 期望：零命中（作廢已除）
grep -n "100000\|100k\|廢長邊" .../2026-07-19_PIPE-INGEST-REVIEW_design_spec.md  # 期望：命中
```

### §6.3 全域防呆（每 commit）

```bash
git status -s | grep -vE "\.claude-logs/(baton|plans|archive)/"  # 期望：無業務代碼/測試改動
venv/bin/python -m pytest tests/ -q                              # 期望：920 passed 零回歸（DOC 未誤觸代碼）
```

---

## §7 不可動清單

- [ ] **業務代碼**：`pipelines/`（含 ingestion_engine/image_filter/litedoc_pipeline/section_engine）／`processor/`（含 glossary_extractor）／`settings.py`／`models.py` — 100% 不動
- [ ] **測試代碼**：`tests/` 全數 — 不動
- [ ] PIPE-SPEC §1.1 四份凍結 Phase 交接合約結構；§1.2.1/§1.2.3/§1.2.4/§1.2.5 既有章本體；§1.3 L140/§3.3 15k/§2/§3.1 ≥10 逐字守
- [ ] 母 plan §1/§2 U1-U6/U9-U11、§8.1-§8.4 既有規劃本體（僅 U7/U8/§8.5 就地補註）
- [ ] design spec F7 探索脈絡（實測鴻溝、Vision 反直覺、規則②③）— 僅更正規則①作廢門檻
- [ ] 既有 Revision 歷程既有列 — 只增不刪、不溯及既往修既有編號

---

## §8 推薦 Commit 拆分

<!-- === [PIPE-SYNC-5 Check 更正] === §8 原拆 C1（PIPE-SPEC）/ C2（母 plan + design spec）兩個開發 commit；baron C1 run 提示詞（2026-07-21 10:18）將兩者**合併為單一 C1**（備份規則列三檔、§8 git add 列母 plan + 3 `.bak`、commit message 涵蓋三文件、TODO 更新指示 C1→checkout 直達）。實際落地即為合併版單一 commit `cc53452`。本節於 Checkout 階段依實況更正為「C1 合併版」、移除已失效之獨立 C2，防日後對照困惑；§0.5／§1／§4 相應同步。原兩段拆分內容全數保留於下方合併 C1 之實作細節（①PIPE-SPEC ②母 plan ③design spec 三組），無資訊遺失。 === -->

### C1 — Spec & Plan Backfill（規格書與母計畫回灌）〔合併版：三文件一次回灌〕

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `.claude-logs/baton/2026-06-01_PIPE-SPEC_..._specification.md`（baton gitignored）、`.claude-logs/plans/2026-06-01_PIPE_..._plan_v10.md`（tracked）、`.claude-logs/baton/2026-07-19_PIPE-INGEST-REVIEW_design_spec.md`（baton gitignored） + 3 個 `.bak`（`.claude-logs/archive/2026-07-21_PIPE-SYNC-5_C1_specification.md.bak`／`..._C1_plan_v10.md.bak`／`..._C1_design_spec.md.bak`、皆 tracked） |
| **安全性** | 🟢 高 — 純文件就地補註、HTML 註解包裹、四凍結合約零觸、零業務代碼 |
| **可逆性** | 🟢 高 — `git revert C1`（母 plan + 3 .bak）或對照 `.bak` 還原 baton 兩檔 |
| **驗收 grep 條件** | §6.1 + §6.2 全項 + §6.3 全域防呆 |
| **依賴關係** | 無前置（三文件一次到位；母 plan roster 引用之 SPEC §1.2.6/§1.2.2.1 章號於同 commit 內建立、無跨 commit 懸掛） |
| **具體實作細節** | 依 plan §2.1–§2.3 三組就地補註（全部 `<!-- [PIPE-SYNC-5 Dn] -->` 包裹）：<br>**① PIPE-SPEC v8→v9（六項）**：**D1** §1.2.5 後新增 §1.2.6 `ingestion_engine` 契約章——模組 `pipelines/ingestion_engine.py`、純函式零文體字面量/不 import A 軌 processor/不讀 PipelineContext、公開介面 `assemble(markdown_text, structure, *, meta_types=("title","authors","publication_info"), figure_filter=None) -> {"title","meta","sections"}`（含 extract_title/mark_meta_lines/split_blocks/build_sections）、四鐵律〔title 抽取不丟/meta 行非連續分離/figure 帶 content+caption/可選 figure_filter hook 預設 None byte 等價·DROP 連帶 caption used 防孤兒〕、consumer litedoc；**D4**（併入 D1）§1.2.6.1 litedoc 攝入自有化接點〔A 軌 md2json/行級分塊借用鏈退場·`_structured.json` 不再產·P3 譯題單一源＝P1 title 根治扉頁/分頁名/PDF Title 三受害者〕。**D2** §1.2.2 內補 §1.2.2.1「事前定案 builder」——`glossary_extractor.py::GlossaryManager.build_termmap(full_text, abstract, translated_abstract, source_lang, target_lang, domain, ...)` 五步〔N1 段落邊界切塊 `GLOSSARY_CENSUS_CHUNK_CHARS`→N2 並行 census 只認詞不翻→N3 `_normalize_key` 去重+query_cascade 分流廢飛輪早退→N4 只翻未知→N5 定案 upsert `source="termmap_decided"`〕+ 三路 `_heal_glossary` 收斂委派單一實作源 + 全文單一譯法可硬驗收。**D3** §0.3 家族 roster 增列第 6 `ingestion_engine`（契約見 §1.2.6）。**D5** §1.2.2 補 `LLM_USE_GLOSSARY_ALIGN` 預設 true 註（GLOSSARY-TERMMAP C5 末位點火·env 關回）。**D6** §4 Change Log v9 列 + §99.2 Revision v9（含不改項守恆宣告）。<br>**② 母 plan v10（就地補註、沿 PIPE-SYNC-4 不 bump 主版本）**：**D_U7** L72 LiteDoc 行補攝入自有化現況（原規劃句保留作軌跡）；**D_U8** §U8 家族 roster 補第 6 `ingestion_engine`（契約見 SPEC §1.2.6）+ GLOSSARY-CORE `build_termmap` 事前定案演進註（契約見 SPEC §1.2.2.1、旗標 true）；**D_85** §8.5 橫跨共用模組表補三案 ✅ 已落地〔PIPE-INGEST `e7b9e6c`…`ab65208`／GLOSSARY-TERMMAP `16a5f09`…`6b5c975`／IMG-FILTER `de3a475`…`8cfaf5b`、hash 以 archive/TODO_done_archive.md 核對、post-roadmap 落地〕；**Revision** §99.2 加「PIPE-SYNC-5 C1 回灌」一行。<br>**③ design spec F7 門檻更正**：**D_F7** 規則① 廢長邊軸、更正為 `area < IMG_FILTER_MIN_AREA(預設 100000)`；規則③ 收窄報頭判型行界；補實測校正註〔誤殺 481×369 內容 chart 理由·指向 IMG-FILTER plan v2/settings〕；規則②④ 及探索脈絡零動（**更正註以「600px／20 萬」白話表述，避免作廢 token 字面殘留、確保 §6.2 clean grep**）。 |

### C_CHECKOUT — 收官歸檔（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` / `archive/TODO_done_archive.md` / `prompts/`（本任務全數提示詞 + INDEX.md）/ baton→`plans/`+`tasks/`+`executions/` 歸檔檔 / `executions/<日期>_PIPE-SYNC-5_checkout_執行.md` |
| **安全性** | 🟢 高 — 純文件歸檔 |
| **可逆性** | 🟢 高 — `git revert` 回滾歸檔 commit |
| **驗收 grep 條件** | Conformance 對照 plan §2 全項 + §7.2 純 DOC 豁免聲明 + staged-set 自檢（`git diff --cached --name-only` ＝ 宣告清單完全相等） |
| **依賴關係** | 前置 C1（合併版）ship |
| **具體實作細節** | 依 WORKFLOW_SOP §3 收官鐵律：Conformance 驗收 → **§8 更正為「C1 合併版」**（防日後對照困惑）→ TODO 雙層結案（active 移除 + archive 表格 + pointer + 類別索引）→ baton 一次性 `mv`（標準 mv、禁 git mv；plan/tasks/C1 執行報告）→ 逐檔顯式 `git add`（嚴禁 `git add .`/`-A`/目錄；含 C1 之 3 個 `.bak`）→ `checkout_執行.md`（staged-set 實貼 + §8 一行 commit）→ `/tmp` msg 草稿；commit 由 baron 手動。 |

---

## §9 Open Questions

無。（plan v2 五 OQ 已於 2026-07-21 review 全數拍板、無遺留。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SYNC-5 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 PIPE-SYNC-5 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務與測試代碼（DOC-Refactor）；嚴禁改動四凍結合約結構；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；回灌規格唯一源＝plan v2；被回灌契約唯一源＝現役代碼 |

### §99.2 Revision 歷程

- v2 (2026-07-21)：**Checkout 階段依實況更正為「C1 合併版」**——baron C1 run 提示詞（10:18）將原 C1（PIPE-SPEC）/ C2（母 plan + design spec）合併為單一 C1（三文件一次回灌、C1→checkout 直達），實際落地即合併版 `cc53452`；本版同步 §0.5 Commits 3→2、§1 解法、§4.1 合併（原 §4.2 C2 併入、§4.3→§4.2）、§8 合併 C1 + 更正註（原兩段內容全數保留於合併 C1 之①②③三組、無資訊遺失）
- v1 (2026-07-21)：初版拆分完成——C1 PIPE-SPEC v9回灌（D1-D6）/ C2 母 plan 就地補註 + design spec F7 更正 / C_CHECKOUT；依 plan v2（五 OQ 拍板）；三檔 .bak 置 archive/ tracked
