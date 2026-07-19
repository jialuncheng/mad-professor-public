# GLOSSARY-TERMMAP C2 — Litedoc Termmap Switch（litedoc 收斂與括號約束）執行報告

---

**任務代號**：GLOSSARY-TERMMAP C2
**執行日期**：2026-07-19
**依據規劃**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`（§8 C2）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C2)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `16a5f09`（GLOSSARY-TERMMAP C1、builder 已落地零接線）。litedoc P2 `_heal_glossary` 仍帶飛輪早退、抽詞僅餵摘要對；translator 強約束區塊無免括號防呆。
- **完成狀態**：litedoc P2 收斂共用 `build_termmap`（傳 **full_text**＋摘要對、早退鏈廢除——`grep "if existing"` → 0 命中）；translator gated 區塊補免括號句（母 prompt 檔零動）；§7.2 跨 Phase 整合測試落地（key-changing、多單元注入一致、免括號句存在、旗標關零注入回歸）。旗標預設仍關 → 生產 runtime 零變化。全套件 **797 passed**（C1 後基線 793＋4、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.2（litedoc 收斂）＋§2.4（括號收斂）＋§2.3（注入鏈零新機制——僅靠既有 `glossary` 欄生效）＋§8.1 §7.2 整合測試；無偏離。resume／slides 依 Q6 界線零碰（C3 進行）。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | litedoc P2 收斂 build_termmap（廢早退）＋translator 免括號句＋§7.2 整合測試 ×2＋litedoc 測試 ×2 | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/litedoc_pipeline.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_litedoc_pipeline.py.bak` | `_heal_glossary` 收斂為委派 `build_termmap`（簽名擴 `full_text`、呼叫點同步）；P2 其餘步序零動 |
| 修改 | `processor/translator.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_translator.py.bak` | 術語強約束 gated 區塊（L127 分支）補免括號句一行 |
| 修改 | `tests/test_litedoc_pipeline.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_test_litedoc_pipeline.py.bak` | 新增旗標開路 build_termmap 呼叫斷言＋模組層早退靜態掃描（既有斷言零改） |
| 修改 | `tests/test_glossary_termmap.py` | —（C1 新檔延續編修、依 tasks 無需 bak） | 新增 `TestCrossPhaseIntegration` §7.2 整合測試 ×2 |

> ⚠️ 三 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存檔不在清單。

---

## §4 修法說明

### §4.1 `pipelines/litedoc_pipeline.py` — P2 glossary 段收斂

呼叫點（`run_phase2` ③）傳入現場既有 `full_text`（census 吃全文、根治「抽詞綁摘要漏 body 長尾」）：

```python
if settings.LLM_USE_GLOSSARY_ALIGN:
    glossary = self._heal_glossary(
        full_text, source_lang, _TARGET_LANG, lcc, abstract, translated_abstract
    )
```

`_heal_glossary` 本體由 13 行早退鏈（`query_cascade → if existing: return → extract_terms → upsert`）收斂為委派單一實作源：

```python
def _heal_glossary(self, full_text, source_lang, target_lang, lcc,
                   abstract, translated_abstract) -> Dict[str, str]:
    return GlossaryManager().build_termmap(
        full_text, abstract, translated_abstract,
        source_lang, target_lang, lcc,
    )
```

### §4.2 `processor/translator.py` — 免括號約束（缺陷④根治點）

術語強約束區塊（`if settings.LLM_USE_GLOSSARY_ALIGN and ctx.glossary` gated、母 prompt txt 檔零動）尾補一行：

```python
f"{term_lines}"
# === [GLOSSARY-TERMMAP C2] 免括號約束（缺陷④根治；gated 區塊、母 prompt 檔零動）===
"\n術語譯法與原文相同者，直接沿用原文、不得另加括號注解原文。"
```

機制閉環：C1 之 N4 prompt 已定「慣例不譯者譯法＝原文」→ 定案表含 `spacex → SpaceX` 同字行 → 本句指示遇同字定案直接沿用、不加括號 → `SpaceX (SpaceX)` ×74 型噪音自譯文生成器本體根治。

### §4.3 `tests/test_glossary_termmap.py` — §7.2 跨 Phase 整合測試（Checkout 必驗）

`TestCrossPhaseIntegration`：真 builder（mock LLM census 三專名、**key-changing**——`Sentient Sun → [譯]Sentient Sun` 譯文≠原文、`SpaceX → SpaceX` 同字定案）→ 定案表入 `InjectionContext.glossary` → 旗標 patch 開 → **模擬 P3 三個並行翻譯單元各自組 system prompt**。斷言：每單元皆含定案行與免括號句、三單元 prompt **完全一致**（`len(set(prompts)) == 1`＝全篇譯法唯一之結構性保證）；另 `test_flag_off_zero_injection_regression`（旗標關 gated 區塊整段缺席）。

### §4.4 `tests/test_litedoc_pipeline.py` — 收斂斷言（+2、既有零改）

- `test_p2_glossary_flag_on_calls_build_termmap`：旗標開 → stub `GlossaryManager.build_termmap` 被呼、**`full_text == "EN FULL TEXT"`**（吃全文非僅摘要）、定案表入 `GlossaryReadySpec.glossary` 交付合約。
- `test_p2_heal_glossary_no_early_return_source`：模組源碼靜態掃描 `if existing` 歸零＋`build_termmap` 已接。
- 既有測試僅 `_setup_p2_mocks` 註解補「（預設路）」三字、斷言本體零改。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M pipelines/litedoc_pipeline.py
 M processor/translator.py
 M tests/test_glossary_termmap.py
 M tests/test_litedoc_pipeline.py
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_litedoc_pipeline.py.bak
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_test_litedoc_pipeline.py.bak
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_translator.py.bak
```

### §5.2 目標測試（實貼）

```
tests/test_glossary_termmap.py + tests/test_litedoc_pipeline.py
.....................................................                    [100%]
53 passed in 0.73s
```

### §5.3 全套件（實貼）

```
797 passed, 3 skipped, 3 warnings in 53.12s
```

C1 後基線 793 passed → **797 passed（+4、0 failed、零回歸）**。

### §5.4 §6.2 驗收 grep（實貼）

```
--- 早退廢除（期望 0 命中）
grep -n "if existing" pipelines/litedoc_pipeline.py → 0 matches（exit=1）
--- litedoc 收斂
pipelines/litedoc_pipeline.py:423:# === [GLOSSARY-TERMMAP C2 START] P2 術語自癒收斂共用 build_termmap ===
--- 免括號句
processor/translator.py:137:"\n術語譯法與原文相同者，直接沿用原文、不得另加括號注解原文。"
--- §7.2 整合測試
tests/test_glossary_termmap.py: class TestCrossPhaseIntegration（key-changing 斷言俱在）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <四修改檔>
無命中（合規）——本 commit 未新增任何日誌呼叫、收斂後日誌責任在 build_termmap（C1 已核）
--- database：grep -nE "\.commit\(\)" <四修改檔> | grep -v "with .*session.*begin()"
無命中（合規）——本 commit 零 DB 寫入（寫入走 C1 upsert_terms 既有極短交易）
```

---

## §6 不可動清單遵守狀態

- [x] `models.py` 表定義與 `pipelines/contracts.py` 凍結合約 — 零改（定案表走既有 `GlossaryReadySpec.glossary` 欄）
- [x] `prompt/translate/*.txt` 母翻譯提示詞檔 — 零改（免括號句在 translator.py gated 區塊）
- [x] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py` — 零改（C3 界線）
- [x] litedoc P2 glossary 段以外步序（摘要／LCC／節點摘要）＋P3 全部 — 零改
- [x] `InjectionContext.constraints` — 未注入任何括號約束（一律由定案表注入）
- [x] `glossary_extractor` 三既有函式／`section_engine`／`ingestion_engine`／A 軌鏈 — 零改
- [x] `settings.py` 旗標預設 — 維持 false（C5 點火）
- [x] 既有 tests 斷言本體 — 零改（僅新增 4 測試＋mock 註解三字）

---

## §7 銜接

- **baton 狀態**：C1／C2 報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add。
- **hash 自癒**：C1 已 ship＝`16a5f09`；「待 baron 回填」佔位符雙源掃描＝0。
- **自評（正向）**：推進 plan v2 §2.2／§2.3／§2.4＋§7.2 整合測試——litedoc 全鏈（census 吃全文 → 定案 → 注入 → 免括號）已就緒、只待 C5 點火。**（負向防錯）**：免括號效果依賴 LLM 遵從 system 指令、非結構性攔截——實效以 C5 後 SpaceX 樣本重跑量化驗收（plan §8.2 硬驗收「同字括號 ≤1」）；若遵從度不足、後續可於 termmap 注入層過濾同字行改為顯式禁注清單（屬觀察後追加、不預做）。
- **下一步**：C3 — Resume & Slides Convergence（resume 與 slides 等價收斂）；等 baron 確認本 commit 後另行下達 C3 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C2 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add processor/translator.py
git add tests/test_litedoc_pipeline.py
git add tests/test_glossary_termmap.py
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_translator.py.bak
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C2_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/GLOSSARY-TERMMAP_C2_msg.txt）
cat > /tmp/GLOSSARY-TERMMAP_C2_msg.txt << 'EOF'
BE-Refactor: GLOSSARY-TERMMAP C2 — Litedoc Termmap Switch（litedoc 收斂與括號約束）

1. 將 pipelines/litedoc_pipeline.py 的 P2 術語自癒 _heal_glossary 改呼叫共用 build_termmap 產生器，傳入 markdown 全文（run_phase2 現場讀取）、摘要及譯文摘要對，並廢除與清理舊的 query_cascade 早退阻斷邏輯。
2. 於 processor/translator.py 的術語強約束 gated 注入區塊新增「術語譯法與原文相同者，直接沿用原文、不得另加括號注解原文」之指示，自譯文生成器本體根治重複括號噪音。
3. 於 tests/test_glossary_termmap.py 新增 §7.2 跨 Phase 整合測試，驗證多段專名一致與免括號指令生效。
4. 更新 tests/test_litedoc_pipeline.py Glossary 測試以對位 build_termmap mock 呼叫。
EOF

# 4. baron 手動執行
git commit -F /tmp/GLOSSARY-TERMMAP_C2_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-19)：C2 執行完成——litedoc 收斂廢早退（grep 0）＋免括號句＋§7.2 整合測試、797 passed 零回歸、SOP 雙核查合規
