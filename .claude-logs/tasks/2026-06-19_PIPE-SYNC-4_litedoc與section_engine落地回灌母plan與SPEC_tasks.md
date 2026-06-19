# PIPE-SYNC-4 litedoc 與 section_engine 落地回灌母 plan 與 SPEC — Tasks

> 本文件為 PIPE-SYNC-4 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-19_PIPE-SYNC-4_..._plan_v1.md`（v3、§9 五 OQ 全 🟢）產出，含 4 個 Commit。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | 無（純回灌既有真理源）|
| **修改檔案** | 3 個 | `plans/...PIPE_..._plan_v10.md`（D1-D4·版控）/ `baton/...PIPE-SPEC_..._specification.md`（D5/D5b/D6/D7/D8·baton 就地不版控）/ `docs/HOW_TO_ADD_DOC_TYPE.md`（D9·版控）|
| **目錄初始化** | 0 個 | 無 |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 4 個 | C1（master plan）→ C2（SPEC）→ C3（HOW_TO_ADD）→ C4（Checkout）|
| **baton 歸檔** | 1 次 | C4 收官：`mv` plan→plans/ + tasks→tasks/ + C1-C4 報告→executions/ + `git add`;SPEC `.bak`→archive 各 commit git add |

---

## §1 TL;DR（概要）

- **挑戰**：PIPE-SECTION-BASE（section_engine 共用真理源）+ PIPE-LITEDOC（第 3 路）落地後，master plan v10 / PIPE-SPEC drift——三大共用真理源漏 META-NORM+section_engine、master plan technical 分歧、section_engine/MetaNormalizer 契約缺、litedoc 旁路未登記;HOW_TO_ADD 為 A 軌時代 doc。
- **解法**：DOC-Refactor 一次性回灌（純文件、就地補註）——master plan v10（D1-D4）/ PIPE-SPEC（D5 section_engine §1.2.5 + D5b MetaNormalizer §1.2.4 + D6 litedoc 旁路 + D7 家族措辭 + D8 bump v8）/ HOW_TO_ADD（D9 B 軌範式 + A/B 對比 + U2.1 映射）。
- **影響範圍**：**100% DOC-Refactor、零業務代碼、零測試、四凍結合約型別欄位零變動**;686 passed 基線應零影響。
- **Commit 序**：
  - C1 — master plan v10 回灌（technical 矯正 + LiteDoc ✅ + 三大→家族 + 順序）
  - C2 — PIPE-SPEC 回灌（section_engine + MetaNormalizer 兩契約章 + litedoc 旁路 + 家族 + v8）
  - C3 — HOW_TO_ADD B 軌範式（裝飾器機制 + A/B 對比 + U2.1 映射）
  - C4 — Checkout 收官
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `plans/...PIPE_..._plan_v10.md`（版控）| L72 LiteDoc 含 technical / L260 ⬜ / 三大共用真理源 / 順序 Resume→…→Academic→LiteDoc | technical 分歧 / LiteDoc 未標 ✅ / 漏 META-NORM+section_engine / 順序實況 |
| `baton/...PIPE-SPEC_..._specification.md`（baton 不版控）| v7、三大共用真理源、§1.1.1 登 phone/email/domain | 缺 section_engine + MetaNormalizer 契約章 / litedoc 旁路未登 / 三大措辭 / §1.3 L140 **已正確** |
| `docs/HOW_TO_ADD_DOC_TYPE.md`（版控）| A 軌時代、0 提及 litedoc/section_engine | 缺 B 軌裝飾器範式 / 無 A/B 對比 / 無 U2.1 映射規範 |

---

## §3 觀察問題

### 問題 #1：真理源漏登兩共用成員 + technical 分歧
- **證據**：master plan `L72`（technical）/ `L18/L74`（三大）;SPEC grep META-NORM=0、section_engine=0。
- **影響**：PIPE-ACADEMIC/BOOK/INFRA-4 等下游被誤導（同 PIPE-SYNC-2/3 動因）。

### 問題 #2：HOW_TO_ADD 誤導下游寫 A 軌分支
- **證據**：`docs/HOW_TO_ADD_DOC_TYPE.md` grep litedoc/section_engine=0、舊指南全 pipeline_core.py 硬分支。
- **影響**：academic/book 開發者可能走回 A 軌老路。

---

## §4 設計方案

> 全程純文件就地補註（不重寫整檔、不刪既有審計）。master plan/HOW_TO_ADD 版控直接 git add;**SPEC 長駐 baton 不版控、本體就地編輯、`.bak`→archive git add 作審計**（PIPE-SYNC-2 195e12b / PIPE-SYNC-3 先例、grep 證 SPEC gitignored）。

### §4.1 C1 — master plan v10 回灌（D1-D4）
`plans/...PIPE_..._plan_v10.md` 就地補註：D1 L72 technical 排除矯正、D2 L260 LiteDoc ✅+hash+順序、D3 L18/L74/§8.4 三大→共用真理源家族〔含 META-NORM/section_engine〕、D4 絞殺順序實況註;§99.2 加 Revision。

### §4.2 C2 — PIPE-SPEC 回灌（D5/D5b/D6/D7/D8）
`baton/...PIPE-SPEC_..._specification.md` 就地：D5 §1.2.5 section_engine 契約章、D5b §1.2.4 MetaNormalizer 契約章、D6 §1.1.1 litedoc 旁路登記、D7 三大→家族措辭、D8 §99.2 bump v8;**D8.1 不改項**〔§1.3 L140 / §3.3 15k / §2 ≥10 / 四凍結合約結構〕。

### §4.3 C3 — HOW_TO_ADD B 軌範式（D9）
`docs/HOW_TO_ADD_DOC_TYPE.md` 補 B 軌加 doc_type 一節：裝飾器機制（@register + __init__ import + 四 Phase 消費真理源 + raw_metadata 旁路 + §7.2 整合）+ **A/B 機制對比**（防寫 A 軌分支）+ **U2.1 DocAnalyzer 映射規範**;A 軌既有章不動。

### §4.4 C4 — Checkout 收官
Conformance 五維度 + §7.2 豁免 + baton 一次性歸檔 + TODO 結案 + hash 自癒。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 誤改已正確內容（SPEC §1.3 L140）| 🟡 中 | C2 §6.2 grep 驗 L140 未動;D8.1 不改項明列 |
| 四凍結合約被誤動 | 🟢 低 | 純文字、零 contracts.py、§6 grep 驗合約結構不在 diff |
| SPEC 誤入版控 | 🟢 低 | SPEC gitignored、僅 .bak→archive git add（grep check-ignore 證）|
| 業務代碼/測試誤動 | 🟢 低 | 100% .md、§6 全套件 686 passed 旁證零代碼 diff |

---

## §6 測試計畫

> 純 DOC-Refactor、無 SOP §5（logging/database 無代碼）;驗收＝grep + wc + pytest 基線旁證。

### §6.1 C1 驗收（master plan）
```bash
grep -nE "news/web/未知|technical 歸深結構家族" .claude-logs/plans/2026-06-01_PIPE_*_plan_v10.md   # D1 矯正
grep -c "PIPE-LITEDOC.*✅\|b1012bc" .claude-logs/plans/2026-06-01_PIPE_*_plan_v10.md                  # D2
grep -c "共用真理源家族\|META-NORM\|section_engine" .claude-logs/plans/2026-06-01_PIPE_*_plan_v10.md  # D3
```

### §6.2 C2 驗收（SPEC）
```bash
grep -nE "§1.2.5|§1.2.4|section_engine|MetaNormalizer|render_meta_header_html" .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md  # D5/D5b
grep -c "translated_title\|publisher\|date" .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md   # D6 litedoc 旁路
grep -c "v8 (2026-06-19)" .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md                      # D8 bump
grep -c "news/web/未知 fallback" .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md               # D8.1 §1.3 L140 未動（仍在）
git check-ignore .claude-logs/baton/2026-06-01_PIPE-SPEC_*.md && echo "SPEC gitignored✓（僅 .bak→archive）"
ls .claude-logs/archive/2026-06-19_PIPE-SYNC-4_C2_PIPE-SPEC.md.bak                          # .bak 存在
```

### §6.3 C3 驗收（HOW_TO_ADD）
```bash
grep -cE "PipelineFactory.register|section_engine|B 軌|A 軌" docs/HOW_TO_ADD_DOC_TYPE.md     # D9 B 軌範式 + A/B 對比（由 0→≥1）
grep -c "DocAnalyzer|安全映射|U2.1" docs/HOW_TO_ADD_DOC_TYPE.md                              # U2.1 映射規範
```

### §6.4 C4（Checkout）驗收
```bash
pytest tests/ -q                                       # 686 passed 基線（純 .md 應零影響）
ls .claude-logs/baton/ | grep -i PIPE-SYNC-4 && echo "❌殘留" || echo "✅ baton 清空"
git status -s | grep -E '\.py$' | wc -l                # 期望 0（零業務/測試代碼）
```

---

## §7 不可動清單

- [ ] **所有業務代碼**（`pipelines/*` / `processor/*` / `web_server.py` / `pipeline_core.py` / A 軌 / `static/*`）— 100% 不動。
- [ ] **任何測試檔**（`tests/*`）— 不動。
- [ ] **`contracts.py` 四凍結合約型別/欄位** — 零變動（D5/D6 僅 SPEC 文字描述）。
- [ ] **SPEC §1.3 表 L140 litedoc 格**（news/web/未知）— 已正確、嚴禁改（D8.1）。
- [ ] **SPEC §3.3 15k / §2 ≥10 / 四凍結合約結構** — 已對齊、不動。
- [ ] master plan / SPEC 既有 Revision 史與 D1-D7 補註 — 只增不刪。
- [ ] **主 repo 目錄** — 嚴禁讀寫。

---

## §8 推薦 Commit 拆分

### C1 — master plan v10 回灌（technical 矯正 + LiteDoc ✅ + 三大→家族 + 順序）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `plans/2026-06-01_PIPE_..._plan_v10.md`（D1-D4 就地補註）+ `.bak`→archive |
| **安全性** | 🟢 高 — 純文件就地補註、零代碼 |
| **可逆性** | 🟢 高 — `git revert C1` / 自 .bak 還原 |
| **驗收 grep 條件** | §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① 備份 `cp plans/...plan_v10.md archive/2026-06-19_PIPE-SYNC-4_C1_PIPE_plan_v10.md.bak`。② **D1** L72「news/web/**technical**/未知」→「news/web/未知 fallback」+ 一句「technical 歸深結構家族（academic/book）、A 軌證非 FLAT/非 SHORT/有 abstract」。③ **D2** L260 §8.5 表 PIPE-LITEDOC「⬜ 待建立/依賴 academic/含 technical」→「✅ 已落地（C1-C8、b1012bc…ff16271）/實際先於 academic/news/web/未知」。④ **D3** L18/L74/§8.4「三大共用真理源」→「共用真理源**家族**」+ roster 補 META-NORM（第 4）+ section_engine（第 5）、標明三大為原始核心。⑤ **D4** L86/L222/L253 順序句後加實況補註（LiteDoc 先於 Academic 落地、不改原規劃序）。⑥ §99.2 加 Revision。⑦ 用 `<!-- === [PIPE-SYNC-4 C1] === -->` 包裹補註處。⑧ git add plan_v10.md + .bak。⑨ 產 `baton/..._C1_執行.md`（baton 暫存、嚴禁 git add）。 |

### C2 — PIPE-SPEC 回灌（section_engine + MetaNormalizer 兩契約章 + litedoc 旁路 + v8）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `baton/2026-06-01_PIPE-SPEC_..._specification.md`（**baton 就地、不版控**）+ `.bak`→archive（git add）|
| **安全性** | 🟡 中 — 最大回灌（2 契約章）、須避誤改 §1.3 L140 等已正確處 |
| **可逆性** | 🟢 高 — 自 .bak 還原（SPEC 本體不版控、靠 .bak 審計）|
| **驗收 grep 條件** | §6.2 |
| **依賴關係** | 依賴 C1（家族口徑一致）|
| **具體實作細節** | ① 備份 `cp baton/...PIPE-SPEC...md archive/2026-06-19_PIPE-SYNC-4_C2_PIPE-SPEC.md.bak`。② **D5** §1.2「三大共用真理源模組契約」後新增 **§1.2.5 section_engine 契約章**：9 公開介面〔collect_summary_targets/build_section_summaries/collect_render_slots/restore_sections_markdown/translate_whole/is_heading_degraded/collect_rag_sections/single_container_sections/render_meta_header〔resume 列表〕+ render_meta_header_html〔academic-family HTML 扉頁〕〕+ 鐵律〔零 doc_type 字面量·注入·Zero Schema Coupling·接縫 key=原文標題 path〕+ consumer〔resume/litedoc 已消費〕。③ **D5b** 新增 **§1.2.4 MetaNormalizer 契約章**：normalize_fields〔旗標閘門〕+ 三路分流〔reserved BS1/黑名單 Q9/canonical 註冊 BS4〕+ schema〔MetaField/MetaFieldAlias〕+ 交易邊界〔LLM 交易外·temp=0〕+ consumer〔slides/litedoc〕+ 動因〔為 INFRA-4 鋪規格〕。④ **D6** §1.1.1 raw_metadata 登記補 litedoc date/url/publisher/translated_title〔三欄 dict 範式〕。⑤ **D7** L4/L15/L52/L75「三大共用真理源」措辭→「共用真理源家族」。⑥ **D8** §99.2 加 v8 Revision。⑦ **D8.1 嚴禁改**：§1.3 L140〔news/web/未知〕/ §3.3 15k / §2 ≥10 / 四凍結合約結構。⑧ `<!-- === [PIPE-SYNC-4 C2] === -->` 包裹。⑨ **git add 僅 .bak**（SPEC 本體 gitignored、不 git add）。⑩ 產 `baton/..._C2_執行.md`（baton 暫存）。 |

### C3 — HOW_TO_ADD B 軌範式（裝飾器機制 + A/B 對比 + U2.1 映射）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `docs/HOW_TO_ADD_DOC_TYPE.md`（D9·版控）+ `.bak`→archive |
| **安全性** | 🟢 高 — 補一節、A 軌既有章不動 |
| **可逆性** | 🟢 高 — `git revert C3` / 自 .bak |
| **驗收 grep 條件** | §6.3 |
| **依賴關係** | 依賴 C1/C2（B 軌範式引用 section_engine/真理源契約）|
| **具體實作細節** | ① 備份 `.bak`。② 補一節「B 軌（PIPE 五路）加 doc_type」：**裝飾器機制**〔`@PipelineFactory.register('xxx')` + `pipelines/__init__` import 觸發 + 四 Phase 消費共用真理源〔section_engine + DomainNormalizer/Glossary/Translator + rag_indexer〕+ raw_metadata 旁路 + §7.2 key-changing 整合測試〕。③ **A/B 機制對比**：明示「B 軌裝飾器插件 vs A 軌 pipeline_core.py 硬分支〔即將絞殺〕、下游嚴禁寫 A 軌分支」。④ **U2.1 DocAnalyzer 映射規範**：扁平短文〔litedoc/unknown〕呼叫端安全映射避免 fallback academic、指引深結構文體對齊既有 structure/heading_fix prompts。⑤ A 軌既有章不動。⑥ `<!-- === [PIPE-SYNC-4 C3] === -->` 包裹新增節。⑦ git add HOW_TO_ADD + .bak。⑧ 產 `baton/..._C3_執行.md`（baton 暫存）。 |

### C4 — Checkout 收官

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` / `prompts/INDEX.md` + baton 歸檔（plan→plans/、tasks→tasks/、C1-C4 報告→executions/）|
| **安全性** | 🟢 高 — 純歸檔/狀態 |
| **可逆性** | 🟢 高 |
| **驗收 grep 條件** | §6.4 |
| **依賴關係** | 依賴 C1-C3 全 ship |
| **具體實作細節** | ① Conformance 五維度（目標規格 D1-D9+D5b / tasks §6 grep + pytest 686 / 不可動〔零業務碼·凍結合約·§1.3 L140〕/ 提示詞稽核 / msg §8）+ **§7.2 純 DOC 顯式豁免**〔無 code handoff〕。② baton 一次性 `mv` + `git add`：plan→plans/、tasks→tasks/、C1-C4 報告→executions/。③ TODO 結案（移 WIP、頂端完成表、索引 ✅）+ 全量 hash 自癒。④ 產 `baton/..._C4_執行.md` 後隨歸檔。⑤ 嚴禁自發 commit/push。 |

---

## §9 Open Questions

無。（plan v3 §9 五 OQ 已於 baron review 全 🟢 定案。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SYNC-4 原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序執行;Antigravity 階段 5 驗證引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 PIPE-SYNC-4 executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼/測試/四凍結合約型別;SPEC 本體 gitignored 不入版控〔僅 .bak→archive〕;嚴禁自動 commit/push |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔、經 baron 同意移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令、不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-06-19)：初版拆分（4 Commit：C1 master plan v10 回灌〔D1-D4〕/ C2 PIPE-SPEC 回灌〔D5 section_engine §1.2.5 + D5b MetaNormalizer §1.2.4 + D6 litedoc 旁路 + D7 家族 + D8 v8、D8.1 不改項〕/ C3 HOW_TO_ADD〔D9 B 軌範式 + A/B 對比 + U2.1 映射〕/ C4 Checkout;純 DOC-Refactor 零業務碼;SPEC baton 就地不版控、.bak→archive 審計〔PIPE-SYNC-2/3 先例〕;§7.2 豁免）
