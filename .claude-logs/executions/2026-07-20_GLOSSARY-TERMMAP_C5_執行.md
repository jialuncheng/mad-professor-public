# GLOSSARY-TERMMAP C5 — Glossary Flag-On（旗標預設開啟）執行報告

---

**任務代號**：GLOSSARY-TERMMAP C5
**執行日期**：2026-07-20
**依據規劃**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`（§8 C5、§4.5 觀察項）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C5)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `c571c5b`（GLOSSARY-TERMMAP C4）。C1-C4 全鏈就緒（builder／三路收斂／免括號／滑窗）、旗標預設 false＝全鏈休眠。
- **完成狀態**：**末位點火**——`settings.py` `LLM_USE_GLOSSARY_ALIGN` 預設 `"false"` → `"true"`（env 單點關回註記）；`.env.example` 新增 Glossary 段（旗標＋census 常數＋關回方式＋清庫重跑說明）；全測試旗標掃描＝22 處引用盤點、**僅 1 檔需防禦性隔離**（`test_slide_pipeline.py`、詳 §4.2）。全套件於**新預設下 805 passed**（0 failed、與 C4 基線持平——隔離後零回歸）。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.6（GLOSSARY-ON、Q2 settings 翻轉拍板）；無偏離——僅 settings／.env.example／測試隔離三類改動、零其餘業務代碼。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C5 | 旗標預設翻轉 true（點火）＋.env.example Glossary 段＋test_slide_pipeline 旗標防禦性隔離 | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `settings.py` | `.claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_settings.py.bak` | L114 預設 `"false"`→`"true"`＋點火註記與關回方式（其餘零動） |
| 修改 | `.env.example` | `.claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_env.example.bak` | 檔尾新增 Glossary 段（旗標關回範例＋`GLOSSARY_CENSUS_CHUNK_CHARS` 說明） |
| 修改 | `tests/test_slide_pipeline.py` | `.claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_test_slide_pipeline.py.bak` | `_run_p2` harness＋§7.2 整合測試補旗標隔離（斷言 100% 零動、詳 §4.2） |

> ⚠️ 三 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存檔不在清單。

---

## §4 修法說明

### §4.1 `settings.py`＋`.env.example` — 點火與關回

```python
# === [GLOSSARY-TERMMAP C5] 預設點火（Q2 拍板）：false → true ===
LLM_USE_GLOSSARY_ALIGN = os.getenv("LLM_USE_GLOSSARY_ALIGN", "true").lower() in ("1", "true", "yes")
```

`.env.example` 檔尾新增「Glossary 術語一致性」段：全鏈說明（DOMAIN-NORM＋GLOSSARY-CORE＋GLOSSARY-TERMMAP）、**關回方式**（`# LLM_USE_GLOSSARY_ALIGN=false` 取消註解即單點回退）、測試期清庫重跑說明（GlobalGlossary 表可丟）、census 常數（`# GLOSSARY_CENSUS_CHUNK_CHARS=6000`）。

### §4.2 測試旗標掃描與防禦性隔離（受影響檔逐條）

**盤點**（`grep -rn "LLM_USE_GLOSSARY_ALIGN" tests/` → 22 處／8 檔）：`test_glossary_core`／`test_domain_normalizer`／`test_glossary_termmap`／`test_translator`／`test_litedoc_pipeline`／`test_resume_pipeline` 六檔**均已顯式 patch**（True/False 各按測試意圖）→ 零改動。

**新預設下實跑暴露 2 失敗、均在 `test_slide_pipeline.py`**（未引用旗標、依賴舊預設 false 之 P2 行為——旗標開後 glossary 分支吃掉 mock chat 佇列）：

1. `_run_p2` 共用 harness：增 `glossary_align=False` 參數並顯式 `monkeypatch.setattr(_st, "LLM_USE_GLOSSARY_ALIGN", glossary_align)`——既有測試全數回到旗標關行為；C3 之旗標開測試 `test_p2_glossary_flag_on_builds_termmap` 改傳 `glossary_align=True`（呼叫引數、斷言零動）。
2. `test_integration_p2_p3_p4_key_changing`（§7.2 整合、自建 harness）：測試體頂補 `monkeypatch.setattr(_st, "LLM_USE_GLOSSARY_ALIGN", False)`（chat 佇列依旗標關設計）。

**既有斷言 100% 零動**；無任何測試在新預設下打真 LLM（失敗模式為 mock 佇列錯位、非外呼——隔離後歸零）。

### §4.3 點火生效面（記錄）

自本 commit 起：B 軌五路 P2 `build_termmap`（census→分流→定案）＋P3 術語強約束注入（含免括號句）＋DomainNormalizer LLM 判定全鏈啟用；**tasks §4.5 點火後觀察項**（slides census 源含 `figure_description`、濾點座標已載明）移交 baron 影子 E2E。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M .env.example
 M settings.py
 M tests/test_slide_pipeline.py
?? .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_env.example.bak
?? .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_settings.py.bak
?? .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_test_slide_pipeline.py.bak
```

### §5.2 新預設暴露與隔離後（實貼）

```
（翻轉後首跑）FAILED tests/test_slide_pipeline.py::test_p2_six_step_spec_and_key_uniqueness
             FAILED tests/test_slide_pipeline.py::test_integration_p2_p3_p4_key_changing
             2 failed, 803 passed
（隔離後）    tests/test_slide_pipeline.py → 73 passed in 0.58s
```

### §5.3 全套件（新預設、實貼）

```
805 passed, 3 skipped, 3 warnings in 52.95s
```

C4 後基線 805 passed → **805 passed（0 failed、隔離後零回歸）**。

### §5.4 §6.5 驗收 grep（實貼）

```
settings.py:114:LLM_USE_GLOSSARY_ALIGN = os.getenv("LLM_USE_GLOSSARY_ALIGN", "true")...
.env.example:76:# LLM_USE_GLOSSARY_ALIGN=false      （關回範例）
.env.example:79:# GLOSSARY_CENSUS_CHUNK_CHARS=6000  （census 常數說明）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" settings.py tests/test_slide_pipeline.py
無命中（合規）
--- database：grep -nE "\.commit\(\)" settings.py tests/test_slide_pipeline.py | grep -v "with .*session.*begin()"
無命中（合規）——本 commit 零 DB 操作
```

---

## §6 不可動清單遵守狀態

- [x] `models.py` 表定義與 `pipelines/contracts.py` 凍結合約 — 零改
- [x] 改動僅限 settings 旗標翻轉／.env.example 說明／測試 monkeypatch 隔離（提示詞界線）——**零其餘業務代碼**
- [x] 既有 tests 斷言本體 — **100% 零動**（僅 harness 參數化＋2 處隔離 patch＋1 呼叫引數）
- [x] `glossary_extractor`／`translator`／三路 pipeline／`section_engine`／`ingestion_engine`／A 軌鏈 — 零改
- [x] `GLOSSARY_CENSUS_CHUNK_CHARS` 常數值 — 零動（僅 .env.example 補說明）

---

## §7 銜接

- **baton 狀態**：C1-C5 報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add（C_CHECKOUT 一次性歸檔）。
- **hash 自癒**：C4 已 ship＝`c571c5b`；「待 baron 回填」佔位符雙源掃描＝0。
- **自評（正向）**：plan v2 §2 全部規格項（§2.1-§2.8）至此落地——GLOSSARY-TERMMAP 全鏈點火、缺陷④⑤根治機制上線。**（負向防錯）**：點火實效（全文單一譯法硬驗收／同字括號 ≤1／跨文件累積／slides census 觀察項）屬 baron 影子 E2E（plan §8.2、Checkout 後）——建議先清 GlobalGlossary 表歸零基線再重傳 SpaceX 樣本。
- **下一步**：C_CHECKOUT — Checkout（收官歸檔）；等 baron 確認本 commit 後另行下達 checkout 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C5 實質改動代碼、受影響測試與備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add settings.py
git add .env.example
git add tests/test_slide_pipeline.py
git add .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_settings.py.bak
git add .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_env.example.bak
git add .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C5_test_slide_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/GLOSSARY-TERMMAP_C5_msg.txt）
cat > /tmp/GLOSSARY-TERMMAP_C5_msg.txt << 'EOF'
BE-Refactor: GLOSSARY-TERMMAP C5 — Glossary Flag-On（旗標預設開啟）

1. 將 settings.py 中的 LLM_USE_GLOSSARY_ALIGN 預設值由 false 翻轉為 true，正式啟用 B 軌策略管線全線之領域術語自癒與一致性注入。
2. 於 .env.example 中同步更新該旗標預設值及 GLOSSARY_CENSUS_CHUNK_CHARS 配置說明，並註記環境變數關回方式。
3. 掃描全測試套件，為未自行進行旗標隔離之既有測試補齊 monkeypatch.setattr 設置，避免其在新預設下打 LLM 或發生斷言 Regress，確保 780+ 測試在新設定下全綠通過。
EOF

# 4. baron 手動執行
git commit -F /tmp/GLOSSARY-TERMMAP_C5_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-20)：C5 執行完成——旗標點火（新預設下 805 passed 零回歸）、.env.example 同步、僅 1 檔測試需隔離（斷言零動）、SOP 雙核查合規
