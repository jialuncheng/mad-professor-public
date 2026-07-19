# GLOSSARY-TERMMAP C3 — Resume & Slides Convergence（resume 與 slides 等價收斂）執行報告

---

**任務代號**：GLOSSARY-TERMMAP C3
**執行日期**：2026-07-19
**依據規劃**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`（§8 C3）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C3)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `30684e5`（GLOSSARY-TERMMAP C2、litedoc 已收斂）。resume／slides 兩路 P2 `_heal_glossary` 仍帶飛輪早退、抽詞僅餵摘要對。
- **完成狀態**：兩路 P2 術語自癒段等價收斂共用 `build_termmap`（各自現地傳全文——resume＝既讀 markdown 全文、slides＝tiles 合併頁文本；早退鏈雙廢——`grep "if existing"` 兩檔 0 命中）；兩路 P2 其餘步序零動。全套件 **799 passed**（C2 後基線 797＋2、0 failed）。旗標預設仍關 → 生產 runtime 零變化。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.2（三路收斂之其餘兩路、Q6 分開落地序）；無偏離——三份重複 `_heal_glossary` 至此全數收斂為單一實作源。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | resume／slides P2 `_heal_glossary` 等價收斂 build_termmap（雙廢早退）＋兩測試檔對位（更新 2＋新增 3） | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/resume_pipeline.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_resume_pipeline.py.bak` | `_heal_glossary` 委派 build_termmap（簽名擴 `full_text`）；呼叫點傳 P2 既有 `full_text` |
| 修改 | `pipelines/slide_pipeline.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_slide_pipeline.py.bak` | 同式收斂（staticmethod 保留；傳 tiles 合併頁文本 `full_text`） |
| 修改 | `tests/test_resume_pipeline.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_resume_pipeline.py.bak` | 原⑩⑪兩測試依規格改寫（詳 §4.3） |
| 修改 | `tests/test_slide_pipeline.py` | `.claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_slide_pipeline.py.bak` | 新增收斂測試 ×2（旗標開走 builder＋早退靜態掃描） |

> ⚠️ 四 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存檔不在清單。

---

## §4 修法說明

### §4.1 `pipelines/resume_pipeline.py` — P2 收斂（full_text＝既讀 markdown 全文）

P2 現場既有 `full_text = self._read_source_text(ctx)`（L349、零新增讀取），呼叫點直接傳入：

```python
if settings.LLM_USE_GLOSSARY_ALIGN:
    glossary = self._heal_glossary(
        full_text, source_lang, _TARGET_LANG, lcc, abstract, translated_abstract
    )
```

`_heal_glossary` 13 行早退鏈收斂為委派（同 C2 litedoc 式）：

```python
def _heal_glossary(self, full_text, source_lang, target_lang, lcc,
                   abstract, translated_abstract) -> Dict[str, str]:
    return GlossaryManager().build_termmap(
        full_text, abstract, translated_abstract, source_lang, target_lang, lcc)
```

### §4.2 `pipelines/slide_pipeline.py` — P2 收斂（full_text＝tiles 合併頁文本）

P2 現場既有 `full_text = "\n\n".join(title/content/figure_description per tile)`（①全文摘要之同一來源、零新增組裝），呼叫點傳入；`_heal_glossary` 保留 `@staticmethod` 與模組內惰性 import 慣例、本體同式委派。兩路 P2 其餘步序（摘要／頁摘要／LCC／storyboard／section_summaries）**零動**。

### §4.3 測試對位（更新 2＋新增 3、逐條記錄）

- **`test_resume_pipeline.py` 原⑩ `test_run_phase2_glossary_selfheal_injects_summary_and_lcc` 依規格改寫**為 `test_run_phase2_glossary_builds_termmap`：原斷言綁 `query_cascade→缺詞 extract_terms→upsert` 早退鏈（Q1 拍板廢除之行為）→ 新斷言：`build_termmap` 收到 **`full_text=="履歷全文 Python"`**（census 吃全文）＋摘要對＋LCC domain、定案表入 `spec.glossary`。
- **原⑪ `test_run_phase2_cache_hit_zero_extract` 依規格改寫**為 `test_run_phase2_no_early_return_cache_contract`：原斷言「cache hit 不呼 extract_terms」＝**早退契約本身**（Q1 判定缺陷）→ 新斷言：路級不直呼 `query_cascade`（raise 守衛）、一律走 build_termmap；分流語意由 `test_glossary_termmap` Q1 回歸把關。
- **`test_slide_pipeline.py` 新增 ×2**：`test_p2_glossary_flag_on_builds_termmap`（旗標開 → builder 收到合併頁文本〔`alpha 內容`/`beta 內容` 俱在〕＋LCC=TK、定案表入交付）＋`test_p2_heal_glossary_no_early_return_source`（模組靜態掃描 `if existing` 歸零）。
- 兩檔其餘既有斷言本體**零改**。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M pipelines/resume_pipeline.py
 M pipelines/slide_pipeline.py
 M tests/test_resume_pipeline.py
 M tests/test_slide_pipeline.py
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_resume_pipeline.py.bak
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_slide_pipeline.py.bak
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_resume_pipeline.py.bak
?? .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_slide_pipeline.py.bak
```

### §5.2 兩路測試（實貼）

```
tests/test_resume_pipeline.py + tests/test_slide_pipeline.py
........................................................................ [ 62%]
...........................................                              [100%]
115 passed in 1.01s
```

### §5.3 全套件（實貼）

```
799 passed, 3 skipped, 3 warnings in 55.08s
```

C2 後基線 797 passed → **799 passed（+2、0 failed、零回歸）**。

### §5.4 §6.3 驗收 grep（實貼）

```
--- 早退廢除（期望 0 命中）
grep -n "if existing" pipelines/resume_pipeline.py pipelines/slide_pipeline.py → 0 matches（exit=1）
--- 兩路收斂
pipelines/resume_pipeline.py:489:return GlossaryManager().build_termmap(
pipelines/slide_pipeline.py:（同式委派、GLOSSARY-TERMMAP C3 marker 區塊）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <四修改檔>
無命中（合規）——本 commit 未新增日誌呼叫、日誌責任在 build_termmap（C1 已核）
--- database：grep -nE "\.commit\(\)" <四修改檔> | grep -v "with .*session.*begin()"
無命中（合規）——本 commit 零 DB 寫入
```

---

## §6 不可動清單遵守狀態

- [x] `models.py` 表定義與 `pipelines/contracts.py` 凍結合約 — 零改
- [x] 兩路 P2 中 `_heal_glossary` 以外任何步序（摘要／頁摘要／LCC／節點摘要／storyboard）— 零改
- [x] `pipelines/litedoc_pipeline.py`（C2 已收斂、本 commit 零碰）／`section_engine`／`ingestion_engine`／A 軌鏈 — 零改
- [x] `prompt/translate/*.txt` 母提示詞／`glossary_extractor` 三既有函式 — 零改
- [x] `settings.py` 旗標預設 — 維持 false（C5 點火）
- [x] 既有 tests 斷言本體 — 僅原⑩⑪兩條依 plan §2.2 規格改寫（§4.3 逐條記錄）、其餘零改

---

## §7 銜接

- **baton 狀態**：C1-C3 報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add。
- **hash 自癒**：C2 已 ship＝`30684e5`；「待 baron 回填」佔位符雙源掃描＝0。
- **自評（正向）**：plan v2 §2.2 三路收斂**全數完成**——三份重複 `_heal_glossary` 收斂為 build_termmap 單一實作源、早退鏈全庫歸零；全鏈只餘 C4 滑窗附論與 C5 點火。**（負向防錯）**：slides 之 census 源為 tiles 合併文本（含 figure_description）——Vision 描述文字可能引入非正文專名入 census；屬可接受面（census prompt 已限專名界定、且 slides 正文即投影片要點）、C5 後影子 E2E 觀察。**（可行動版本已移入 tasks §4.5 C5、含濾點座標；C5 只讀 tasks、勿在本報告動手。）**
- **下一步**：C4 — Sliding Summary Window（litedoc 摘要型滑窗注入）；等 baron 確認本 commit 後另行下達 C4 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C3 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/resume_pipeline.py
git add pipelines/slide_pipeline.py
git add tests/test_resume_pipeline.py
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_resume_pipeline.py.bak
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_slide_pipeline.py.bak
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_resume_pipeline.py.bak
git add .claude-logs/archive/2026-07-19_GLOSSARY-TERMMAP_C3_test_slide_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/GLOSSARY-TERMMAP_C3_msg.txt）
cat > /tmp/GLOSSARY-TERMMAP_C3_msg.txt << 'EOF'
BE-Refactor: GLOSSARY-TERMMAP C3 — Resume & Slides Convergence（resume 與 slides 等價收斂）

1. 修改 pipelines/resume_pipeline.py 的 _heal_glossary 術語自癒方法，改呼叫共用 build_termmap 產生器，並由 run_phase2 現地傳入既有已讀取的 markdown 全文。
2. 修改 pipelines/slide_pipeline.py 的 _heal_glossary 術語自癒方法，改呼叫共用 build_termmap 產生器，並由 run_phase2 現地傳入合併後的 slide 頁面文本。
3. 兩路均刪除舊有 query_cascade 的 if existing 早退阻斷邏輯，改為「已知與新詞」增量自癒學習。
4. 更新對位 tests/test_resume_pipeline.py 與 tests/test_slide_pipeline.py 內的 Glossary stub。
EOF

# 4. baron 手動執行
git commit -F /tmp/GLOSSARY-TERMMAP_C3_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-19)：C3 執行完成——兩路等價收斂（早退雙廢 grep 0）、三路單一實作源達成、799 passed 零回歸、SOP 雙核查合規
