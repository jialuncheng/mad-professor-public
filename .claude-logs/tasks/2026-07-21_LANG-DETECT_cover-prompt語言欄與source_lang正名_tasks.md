# LANG-DETECT cover-prompt 語言欄與 source_lang 正名 — Tasks

> 本文件為 LANG-DETECT 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-21_LANG-DETECT_cover-prompt語言欄與source_lang正名_plan.md`（v2、四 OQ 已拍板）產出，含 1 個開發 Commit + 1 個 Checkout。

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
| **修改檔案** | 2 個 | `pipelines/litedoc_pipeline.py`（prompt +language 欄、`_resolve_source_lang` 合成、P1 接點）/ `tests/test_litedoc_pipeline.py`（prompt 契約・合成矩陣・端到端・§7.2 整合） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 2 個 | C1 → C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` plan/tasks/C1 執行報告 → `plans/` + `tasks/` + `executions/` + 逐檔 `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：`classify_source_lang` 拉丁語系全落 catch-all `en` → 義文詞以 `en` 寫入 `GlobalGlossary`、污染英文命名空間（schema 支援多語、破的是偵測層）。
- **解法**：單一原子 commit——`C1 — Language Field & Source-Lang Resolution（語言欄與 source_lang 合成）`：cover-prompt +`language` 欄（搭既有 metadata LLM 便車、零多呼叫）＋`_resolve_source_lang` catch-all 限定合成（白名單 `^[a-z]{2,3}$` 拒 zh 前綴）＋P1 接點；prompt 欄與合成邏輯屬同一語意單元（加欄不接無效果、接合成缺來源）、不拆。末位 `C_CHECKOUT — 收官歸檔（收官歸檔）`。
- **影響範圍**：僅 `pipelines/litedoc_pipeline.py` P1 metadata 段＋測試；`section_engine`／P2／P3 消費端／schema／各路零改；零 flag（Q2 拍板）、零新依賴。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `pipelines/litedoc_pipeline.py` | `_LITEDOC_META_SYSTEM_PROMPT` L67-84 五欄無 language；`run_phase1` L193 `source_lang = classify_source_lang(...)` 唯一 setter | 拉丁語系判 `en`；缺 LLM language 合成層 |
| `pipelines/section_engine.py` | `classify_source_lang` 回 `{zh,hans,ja,ko,en}`、HOTFIX-1 鎖一契約 | 零缺失——本案零改（原職不兼差） |
| `models.py` | `GlobalGlossary.source_lang` 字串欄＋聯合唯一鍵（L300） | 零缺失——schema 已多語、零改 |

---

## §3 觀察問題

### 問題 #1：拉丁語系 catch-all
- **證據**：`pipelines/section_engine.py:576-`（回傳集無 it/de/fr 分支、最終 `en`）；design spec F4 實查義文判 en。
- **影響**：glossary 錯桶寫入、跨文件互污。

### 問題 #2：偵測層與 schema 落差
- **證據**：`models.py:288/300`（source_lang ISO 欄＋聯合鍵）——schema 支援、偵測不供給。
- **影響**：多語 glossary（義文進場）被偵測層卡死；本案為其前置。

---

## §4 設計方案

### §4.1 C1 — Language Field & Source-Lang Resolution（語言欄與 source_lang 合成）
`pipelines/litedoc_pipeline.py` 三點改動（plan v2 §2.1-§2.2、review 逐行確認之實作）：prompt Fields 增列 `language`＋Rule 5 keys 同步；新私有 `_resolve_source_lang(meta, heuristic)`（catch-all 限定＋雙重白名單）；`run_phase1` L193 後接 `source_lang = self._resolve_source_lang(meta, source_lang)`——⚠️ 注意現行順序 meta（L188）先於 source_lang（L193）、直接串接零重排。測試四組（prompt 契約／合成矩陣參數化／P1 端到端 mock `it`／§7.2 整合）。

### §4.2 C_CHECKOUT — 收官歸檔（收官歸檔）
Conformance（plan v2 §2 對照＋§7.2 必驗）→ TODO 雙層結案 → baton 一次性 `mv`＋逐檔 `git add` → `checkout_執行.md`（staged-set 實貼）→ `/tmp` msg。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| LLM 回 zh* token 破繁中 gate | 🟡 中 | 白名單拒 zh 前綴 producer 端硬擋＋`zh`/`zh-tw`/`zho` 參數化測試鎖死 |
| cover-prompt 改動影響既有五欄品質 | 🟢 低 | 僅增列一欄；既有 meta 測試回歸 |
| en/CJK 回歸 | 🟢 低 | 非 catch-all 維持原判；缺欄退啟發式＝100% 等價（矩陣測試鎖） |
| glossary 既有污染 | 🟢 低 | Q4 拍板不追溯、測試期清庫 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
grep -n "language" pipelines/litedoc_pipeline.py                 # 期望：prompt Fields + Rule 5 keys + 合成函式命中
grep -n "_resolve_source_lang" pipelines/litedoc_pipeline.py     # 期望：定義 + run_phase1 接點兩處
grep -n "startswith(\"zh\")" pipelines/litedoc_pipeline.py       # 期望：白名單拒 zh 前綴命中
git diff --stat pipelines/section_engine.py models.py            # 期望：零 diff（偵測器原職/schema 零改）
venv/bin/python -m pytest tests/test_litedoc_pipeline.py tests/ -q   # 期望：新測試全過、全套件 875+ 零回歸
```

### §6.2 SOP 一致性核查（落地前必貼）

```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" pipelines/litedoc_pipeline.py
grep -nE "\.commit\(\)" pipelines/litedoc_pipeline.py tests/test_litedoc_pipeline.py   # 期望：無命中（零 DB）
```

---

## §7 不可動清單

- [ ] `pipelines/section_engine.py` `classify_source_lang`／`detect_zh_tw`（原職、HOTFIX-1 契約、book 共用）
- [ ] P3 `startswith("zh")` gate 與 P2 glossary 消費端簽名（單點正名、消費端零改）
- [ ] `models.py` `GlobalGlossary` schema；`_TARGET_LANG = "zh-tw"`
- [ ] cover-prompt 既有五欄規則語意（title/authors/date/publisher/url 零動）
- [ ] resume／slides／book／academic 各路與 A 軌全檔
- [ ] **嚴禁**第三方語言偵測依賴／獨立偵測器／多一次 LLM 呼叫／新增 env flag（Q2 拍板）
- [ ] **嚴禁** `git commit`／`git push`（baron 手動）

---

## §8 推薦 Commit 拆分

### C1 — Language Field & Source-Lang Resolution（語言欄與 source_lang 合成）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `pipelines/litedoc_pipeline.py`、`tests/test_litedoc_pipeline.py` + 2 個 `.bak`（入 `.claude-logs/archive/`、隨本 commit `git add`） |
| **安全性** | 🟢 高 — 單點合成、缺欄／怪值退啟發式＝與現行 100% 等價；非 catch-all 判定零讓渡；消費端零改 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾（單 commit 單語意單元） |
| **驗收 grep 條件** | §6.1 全項 + §6.2 SOP 雙核查 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `_LITEDOC_META_SYSTEM_PROMPT`：Fields 行增 `language (str: ISO 639-1 two-letter code of the document's main body language, e.g. en/it/de/fr/ja)`；Rules 增一條「judge by the main body language of the text (not the title or URL); use \"\" if unsure」；Rule 5 keys 清單 `title, authors, date, publisher, url` → 加 `language`；既有五欄規則零動。② 新私有 `_resolve_source_lang(self, meta: Dict[str, Any], heuristic: str) -> str`（review 確認版）：`if heuristic != "en": return heuristic`（zh/hans/ja/ko 維持原判、LLM 不得翻案）；`lang = str(meta.get("language") or "").strip().lower()`；`if re.match(r"^[a-z]{2,3}$", lang) and not lang.startswith("zh"): return lang`；否則 `return "en"`（`re` 已 import、零新 import）。③ `run_phase1`：L193 `source_lang = section_engine.classify_source_lang(_lang_sample)` 之後接 `source_lang = self._resolve_source_lang(meta, source_lang)`（meta 於 L188 已先取得、零重排）；既有 L226 P1 log 已含 source_lang、自然帶正名值。④ 測試（`tests/test_litedoc_pipeline.py` 追加）：prompt 契約（含 `language` 字樣與 keys 清單）；合成矩陣參數化——heuristic `zh`/`hans`/`ja`/`ko` × LLM 任意值→維持原判、heuristic `en` × `it`/`de`/`fr`/`ita`→採信、× `IT`→lower 採信、× `zh`/`zh-tw`/`zho`/`Chinese`/`italian`/`en-US`/空/缺欄→退 `en`；P1 端到端（`_setup_p1_mocks` llm_json 帶 `"language":"it"`）→ `spec.source_lang == "it"` 且非 zh 前綴；**§7.2 整合**（key-changing＝語系 token catch-all `en`→`it`）：P1 spec 餵 P2 真步序（沿用既有 `_setup_p2_mocks`＋Glossary stub 捕參）→ 斷言 `_heal_glossary`/`build_termmap` 收到 `source_lang == "it"`＋對照組 en 文件全鏈仍 `en`；繁中回歸（既有 HOTFIX-1 測試零動、另斷言 LLM 回 `it` 時 heuristic `zh` 仍勝出）。⑤ §6.2 SOP 雙核查實貼。 |

### C_CHECKOUT — 收官歸檔（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md` / `archive/TODO_done_archive.md` / `prompts/`（本任務全數提示詞 + INDEX.md）/ baton→`plans/`+`tasks/`+`executions/` 歸檔檔 / `executions/<日期>_LANG-DETECT_checkout_執行.md` |
| **安全性** | 🟢 高 — 純文件歸檔、零業務代碼 |
| **可逆性** | 🟢 高 — `git revert` 回滾歸檔 commit |
| **驗收 grep 條件** | Conformance 對照 plan v2 §2 全項 + §7.2 整合測試存在且通過 + staged-set 自檢（`git diff --cached --name-only` ＝ 宣告清單完全相等） |
| **依賴關係** | 前置 C1 ship |
| **具體實作細節** | 依 WORKFLOW_SOP §3 收官鐵律：Conformance 驗收 → TODO 雙層結案 → baton 一次性 `mv`（標準 mv、禁 git mv）→ 逐檔顯式 `git add`（嚴禁 `git add .`/`-A`/目錄）→ `checkout_執行.md`（staged-set 實貼 + §8 一行 commit）→ `/tmp` msg 草稿；commit 由 baron 手動。 |

---

## §9 Open Questions

無。（plan v2 四 OQ 已於 2026-07-21 review 全數拍板、無遺留。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 LANG-DETECT 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 LANG-DETECT executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（拆分階段）；嚴禁跨 Commit 混合；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；設計規格唯一源＝plan v2；全局硬規則唯一源＝CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-07-21)：初版拆分完成——C1 語言欄與 source_lang 合成（單語意單元不拆、含 §7.2 整合測試）/ C_CHECKOUT；依 plan v2（四 OQ 拍板）
