# GLOSSARY-TERMMAP C4 — Sliding Summary Window（litedoc 摘要型滑窗注入）執行報告

---

**任務代號**：GLOSSARY-TERMMAP C4
**執行日期**：2026-07-20
**依據規劃**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-19_GLOSSARY-TERMMAP_事前定案術語表與glossary旗標開啟_tasks.md`（§8 C4）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C4)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `83f0503`（GLOSSARY-TERMMAP C3、三路收斂完成）。litedoc P3 section 模式全 slot 共用單一 `InjectionContext`、P2 已算好的 `section_summaries` 只餵 P4 RAG、跨段語篇連貫零支援。
- **完成狀態**：`section_engine` **純加法**擴充（`restore_sections_markdown` 增可選 `slot_context_fn`、`collect_render_slots` content/raw slot 補 `key`＝所屬 section 原文標題 path）；litedoc P3 上下文工廠落地——後段翻譯單元注入**前一鄰近 section 繁中摘要**（`model_copy(update=...)` 產新 frozen 實例、parallel-safe、容缺）。全套件 **805 passed**（C3 後基線 799＋6、0 failed）；**resume 呼叫端零改、預設路徑等價經測試實證**。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.7（連貫附論、Q4 併案＋純加法護欄）；一處實作層對齊（非偏離、§4.2 詳述）：translator 既有 `zh_summary` 優先序 → 滑窗經 zh_summary 合併注入確保浮出、preceding 同步攜帶。**未觸發「結構性受阻」停止條款**——純加法路徑走通。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C4 | section_engine 純加法（slot_context_fn＋content/raw slot key）＋litedoc P3 滑窗工廠（前鄰摘要注入、容缺）＋測試 ×6 | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/section_engine.py` | `.claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_section_engine.py.bak` | `restore_sections_markdown` 增 `slot_context_fn=None` 可選參數；content/raw slot 補 `key` 欄；Callable import |
| 修改 | `pipelines/litedoc_pipeline.py` | `.claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_litedoc_pipeline.py.bak` | P3 section 分支接 `slot_context_fn`；新增 `_make_slot_context_fn` 上下文工廠 |
| 修改 | `tests/test_section_engine.py` | `.claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_section_engine.py.bak` | 新增 ×3：缺省等價／slot key 補欄／逐 slot 配發 |
| 修改 | `tests/test_litedoc_pipeline.py` | `.claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_litedoc_pipeline.py.bak` | 新增 ×3：前鄰摘要注入／容缺與空 fallback／whole・is_zh 分支零滑窗回歸 |

> ⚠️ 四 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存檔不在清單。

---

## §4 修法說明

### §4.1 `pipelines/section_engine.py` — 純加法擴充

- **`collect_render_slots`**：content／raw slot 補 `"key": node_key`（所屬 section 原文標題 path、與 P2 `section_summaries`／P4 `summary_key` **同基準**）；title slot 既有 `key` 行為零變。純加法欄位——既有消費者（`collect_rag_sections` 等）零讀取 content slot 之 key。
- **`restore_sections_markdown`**：簽名增 `slot_context_fn: Optional[Callable[[int, Dict], Any]] = None`；提交翻譯單元時：

```python
ex.submit(
    translate_unit, slot["text"],
    slot_context_fn(i, slot) if slot_context_fn else inj,
    tr, ttype,
)
```

None（預設）＝全 slot 共用 `inj`、現行為等價（測試以 identity 斷言實證：`all(c is inj)`）；docstring 標註 factory 須純讀 parallel-safe。

### §4.2 `pipelines/litedoc_pipeline.py` — 滑窗上下文工廠（`model_copy` 安全複製）

`_make_slot_context_fn(inj, section_summaries)`：預建 `prev_of` 前鄰對照（summaries keys 之 DFS 序）、factory 純讀零狀態；命中前鄰摘要時以 **Pydantic `model_copy(update=...)`** 自 frozen `InjectionContext` 產新實例（共用 inj 不受污染、執行緒安全）：

```python
combined = ((inj.zh_summary or "") + f"\n\n鄰近前段摘要參考：{prev_sum}").strip()
return inj.model_copy(update={"preceding": prev_sum, "zh_summary": combined})
```

**注入路徑之實作層對齊（誠實記錄）**：translator `_build_user_prompt` 既有優先序為 `zh_summary` **先於** `preceding`（`translator.py:153-156`）——litedoc inj 恆帶 `zh_summary=譯摘要`、若僅設 `preceding` 將永不浮出。故鄰近摘要**合併入 zh_summary**（「全文摘要＋鄰近段摘要」＝design spec BOOK 三層滑窗語意本體）確保實際進入 user prompt、`preceding` 同步攜帶原始鄰近摘要（語意欄位、供未來消費）。translator 本體零動。
**容缺三態**：summaries 空 → factory 回 `None`（引擎預設路、行為零變）；首段無前鄰／前鄰摘要缺 → 沿用共用 inj。**嚴禁譯文型 preceding** 遵守——注入物僅 P2 摘要、無任何 slot 譯文（測試斷言 `not preceding.startswith("ZH::")`）。whole／is_zh 分支零接（size-gate 三分支結構零動）。

### §4.3 測試 ×6

- `test_section_engine.py`：**缺省等價**（未傳／None／傳三跑輸出相同＋全單元收同一 inj identity）；**slot key 補欄**（root/child/raw 巢狀 path 基準、title 既有零變）；**逐 slot 配發**（factory 按 key 回不同 ctx、翻譯器逐單元收到對應者）。
- `test_litedoc_pipeline.py`：**前鄰注入**（Sec1 零滑窗共用 inj；Sec2 `preceding=="摘一"`＋zh_summary 合併含「譯摘要」與「鄰近前段摘要參考：摘一」；非譯文型斷言）；**容缺**（前鄰摘要缺→共用 inj；summaries 空→全段零 preceding）；**分支回歸**（whole 模式零滑窗）。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M pipelines/litedoc_pipeline.py
 M pipelines/section_engine.py
 M tests/test_litedoc_pipeline.py
 M tests/test_section_engine.py
?? .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_litedoc_pipeline.py.bak
?? .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_section_engine.py.bak
?? .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_litedoc_pipeline.py.bak
?? .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_section_engine.py.bak
```

### §5.2 目標測試（實貼）

```
tests/test_litedoc_pipeline.py + tests/test_section_engine.py + tests/test_resume_pipeline.py
........................................................................ [ 60%]
................................................                         [100%]
120 passed in 1.16s
```

（resume 全綠＝呼叫端零改之回歸實證）

### §5.3 全套件（實貼）

```
805 passed, 3 skipped, 3 warnings in 53.41s
```

C3 後基線 799 passed → **805 passed（+6、0 failed、零回歸）**。

### §5.4 §6.4 驗收 grep（實貼）

```
pipelines/section_engine.py:349:    slot_context_fn: Optional[Callable[[int, Dict[str, Any]], Any]] = None,
pipelines/section_engine.py:376:                        slot_context_fn(i, slot) if slot_context_fn else inj,
pipelines/litedoc_pipeline.py:523:                    slot_context_fn=self._make_slot_context_fn(
pipelines/litedoc_pipeline.py:576:    def _make_slot_context_fn(
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <四修改檔>
無命中（合規）——本 commit 未新增日誌呼叫、無異常吞沒路徑（factory 純讀零 except）
--- database：grep -nE "\.commit\(\)" <四修改檔> | grep -v "with .*session.*begin()"
無命中（合規）——本 commit 零 DB 操作
```

---

## §6 不可動清單遵守狀態

- [x] `models.py` 表定義與 `pipelines/contracts.py` 凍結合約 — 零改（`InjectionContext` 僅以 `model_copy` 消費、欄位零增刪）
- [x] `section_engine` 僅純加法（slot_context_fn 參數＋slot key 欄）；預設路徑等價經測試 identity 斷言實證；**resume 呼叫端零改動**（resume 測試全綠）；結構性受阻停止條款**未觸發**
- [x] 譯文型 preceding — 未引入（注入物僅 P2 摘要、測試斷言把關）
- [x] litedoc P3 size-gate 三分支結構／whole・is_zh 分支 — 零動
- [x] `glossary_extractor`／`translator`／`ingestion_engine`／A 軌鏈／母 prompt — 零改
- [x] `settings.py` 旗標預設 — 維持 false（C5 點火）
- [x] 既有 tests 斷言本體 — 零改（僅新增 6 測試）

---

## §7 銜接

- **baton 狀態**：C1-C4 報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add。
- **hash 自癒**：C3 已 ship＝`83f0503`；「待 baron 回填」佔位符雙源掃描＝0。
- **自評（正向）**：plan v2 §2.7 連貫附論落地——C1-C4 全鏈（builder／三路收斂／免括號／滑窗）就緒、只餘 C5 點火。**（負向防錯）**：滑窗實效（跨段代名詞／指涉連貫）依賴旗標開啟後才可觀察（旗標關時 glossary 段休眠但滑窗**不受旗標 gate**——滑窗掛在 section 模式本身、C4 起即生效於 zh_summary 合併；此為 plan §2.7 規格內行為、非旗標範圍）；量化驗收屬 C5 後 baron 影子 E2E（plan §8.2 第 6 步）。
- **下一步**：C5 — Glossary Flag-On（旗標預設開啟；含 tasks §4.5 點火後 slides census 觀察項）；等 baron 確認本 commit 後另行下達 C5 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C4 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/section_engine.py
git add pipelines/litedoc_pipeline.py
git add tests/test_section_engine.py
git add tests/test_litedoc_pipeline.py
git add .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_section_engine.py.bak
git add .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_section_engine.py.bak
git add .claude-logs/archive/2026-07-20_GLOSSARY-TERMMAP_C4_test_litedoc_pipeline.py.bak

# 3. commit message 草稿（已寫入 /tmp/GLOSSARY-TERMMAP_C4_msg.txt）
cat > /tmp/GLOSSARY-TERMMAP_C4_msg.txt << 'EOF'
BE-Refactor: GLOSSARY-TERMMAP C4 — Sliding Summary Window（litedoc 摘要型滑窗注入）

1. 修改 pipelines/section_engine.py，為 restore_sections_markdown 增加 slot_context_fn 可選關鍵字參數，並在 collect_render_slots 中為 content slots 補齊 "key" 屬性，達成執行緒安全的多段翻譯上下文動態配發。
2. 於 pipelines/litedoc_pipeline.py 中實作上下文工廠，逐段掃描 content 並從 gspec.section_summaries 取得前一鄰近章節之繁中摘要，經由 preceding 注入單個 InjectionContext 後，直發 P3 並行翻譯。
3. 於 tests/test_section_engine.py 中驗證可選參數缺省時的等價行為。
4. 於 tests/test_litedoc_pipeline.py 中加入單元測試，驗證鄰近段落摘要滑窗 preceding 注入、容缺及 fallback 規格。
EOF

# 4. baron 手動執行
git commit -F /tmp/GLOSSARY-TERMMAP_C4_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-20)：C4 執行完成——section_engine 純加法（缺省等價 identity 實證）＋litedoc 滑窗工廠（model_copy 安全複製、zh_summary 合併浮出對齊、容缺三態）、805 passed 零回歸、SOP 雙核查合規、受阻停止條款未觸發
