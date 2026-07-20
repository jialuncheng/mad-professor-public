# IMG-FILTER C3 — Litedoc Pre-pass Wiring（litedoc 報頭預掃接線）執行報告

---

**任務代號**：IMG-FILTER C3
**執行日期**：2026-07-21
**依據規劃**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_plan.md`（v2）
**次級參考**：`.claude-logs/baton/2026-07-20_IMG-FILTER_垃圾圖三規則確定性過濾_tasks.md`（§8 C3）
**Git commit hash**：[留空，由 baron 回填]
**狀態**：Completed (Commit C3)

---

## §0 改版規則

- 改版觸發：§1–§8 任一執行條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄

---

## §1 基準與完成狀態

- **執行前基準**：工作區位於 `f39f8cb`（IMG-FILTER C2、engine 注入點就緒未接線）。litedoc P1 無報頭預掃、無過濾注入——垃圾圖仍全數入 tiles。
- **完成狀態**：litedoc P1 接線完成——`_collect_header_srcs`（判型行界收窄預掃、soft 降級 ∅）＋`make_figure_filter(md 同目錄 images/, header_srcs)` 注入 `assemble`；**三規則過濾自本 commit 起於 litedoc 生效**（`IMG_FILTER_ENABLED=false` 即回全保留）。§7.2 跨 Phase 整合測試落地（實體圖檔全鏈、**481×369 KEEP 守門**）。全套件 **831 passed**（C2 後基線 827＋4、0 failed）。
- **與全局策略對齊**：本 commit conditioned on plan v2 §2.3（P1 接線與 header_srcs 界定）＋§2.6（規則③收窄）＋§8.1 §7.2 整合測試；無偏離——resume／slides／A 軌／contracts 零碰、Vision 零參與。

---

## §2 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C3 | litedoc `_collect_header_srcs` 預掃＋filter 注入 assemble＋litedoc 測試 ×3＋§7.2 整合測試 ×1 | [留空，由 baron 回填] |

---

## §3 變動檔案清單

| 狀態 | 檔案 | 備份路徑 | 說明 |
|---|---|---|---|
| 修改 | `pipelines/litedoc_pipeline.py` | `.claude-logs/archive/2026-07-21_IMG-FILTER_C3_litedoc_pipeline.py.bak` | `image_filter` import＋`_build_tiles` 注入兩行＋`_collect_header_srcs` 新私有輔助 |
| 修改 | `tests/test_litedoc_pipeline.py` | `.claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_litedoc_pipeline.py.bak` | 新增 C3 測試 ×3（行界界定／soft 降級／ENABLED=False None 回歸） |
| 修改 | `tests/test_ingestion_engine.py` | `.claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_ingestion_engine.py.bak` | 新增 `TestImageFilterIntegration` §7.2 整合測試 |

> ⚠️ 三 `.bak` 必須列入本 commit `git add` 清單（§8）。baton/ 暫存檔不在清單。

---

## §4 修法說明

### §4.1 `_collect_header_srcs` — 報頭行界預掃（規則③ producer）

```python
@staticmethod
def _collect_header_srcs(markdown_text, structure) -> set:
    try:
        blocks = structure.get("structure") if isinstance(structure, dict) else None
        if not isinstance(blocks, list) or not blocks:
            return set()
        hdr_end = max(int(b["end"]) for b in blocks)      # 報頭行界＝判型 max(end)
    except Exception as exc:
        logger.warning("[img-filter] 報頭行界解析失敗（規則③停用、①②照跑）: %s",
                       exc, exc_info=True)
        return set()
    srcs = set()
    for line in markdown_text.split("\n")[: hdr_end + 1]:  # 行界（含）以內
        m = re.match(r"^!\[.*?\]\((.*?)\)", line.strip())
        if m and m.group(1):
            srcs.add(m.group(1))
    return srcs
```

**行號邊界細節**：行界＝判型 blocks `max(end)`（**收窄界定**——非整個孤兒容器，防誤殺首 heading 前正文 hero 圖、plan §2.6）；掃描切片 `[: hdr_end + 1]`（行界含）；src 抽取 regex 與 engine `_FIGURE_RE` 同語意、**零轉換**（§4 接縫契約——engine 呼 filter 時傳的正是同一 src 字串）。三態降級：structure None／空／缺 `end` 欄 → ∅（規則③停用、①②照跑、soft）。

### §4.2 `_build_tiles` 注入（兩行）

```python
header_srcs = self._collect_header_srcs(markdown_text, structure)
fig_filter = image_filter.make_figure_filter(md_path.parent / "images", header_srcs)
result = ingestion_engine.assemble(..., figure_filter=fig_filter)
```

`images_root`＝`md_path.parent / "images"`（MinerU 落檔同目錄基準）；`IMG_FILTER_ENABLED=false` 時工廠回 None → `assemble` 走預設路（零過濾、spy 測試釘死）。`_build_tiles` 其餘流程（processed.json／tiling／`_load_tiles`）零動。

### §4.3 測試 ×4

- **litedoc ×3**：`test_collect_header_srcs_line_boundary`（行界 max end=5 內兩圖入、**行界外 hero 不入**）；`test_collect_header_srcs_soft_fallbacks`（None／空 dict／缺 end 三態 ∅）；`test_build_tiles_filter_disabled_none_regression`（開關關 → assemble 收 `figure_filter=None` spy 斷言＋3 圖全保留）。過程校正一處：初版預期 2 圖保留、實跑 3——行 2/5 判型 "other" 不在 litedoc `_META_TYPES`、報頭圖留 body（正確行為——報頭圖濾除本就靠規則③非 meta 剔行）；依實況修正斷言。
- **§7.2 整合**（`TestImageFilterIntegration`）：tmp_path 建**實體 header-only PNG ×3**（150×88 報頭小圖／**481×369 內文 chart**／1575×852 大圖＋Figure-1 caption）＋擬真 md＋判型 dict → **真 `_build_tiles` 端到端**（真 TilingProcessor bypass、真 image_filter 讀檔）→ 斷言：報頭小圖 DROP（③＋① 雙保險）、**chart KEEP（門檻校正守門——spec F7 原門檻在此測試會 fail）**、大圖 KEEP 且 `content`＋caption 穿透 tiling、正文零損。

---

## §5 測試結果

### §5.1 `git status -s`（實貼、baton/ 與 prompts/ 未列）

```
 M pipelines/litedoc_pipeline.py
 M tests/test_ingestion_engine.py
 M tests/test_litedoc_pipeline.py
?? .claude-logs/archive/2026-07-21_IMG-FILTER_C3_litedoc_pipeline.py.bak
?? .claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_ingestion_engine.py.bak
?? .claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_litedoc_pipeline.py.bak
```

### §5.2 目標測試（實貼）

```
tests/test_ingestion_engine.py + tests/test_litedoc_pipeline.py + tests/test_image_filter.py
.....................                                                    [100%]
93 passed in 0.68s
```

### §5.3 全套件（實貼）

```
831 passed, 3 skipped, 3 warnings in 54.66s
```

C2 後基線 827 passed → **831 passed（+4、0 failed、零回歸）**。

### §5.4 §6.3 驗收 grep（實貼）

```
pipelines/litedoc_pipeline.py:245:        header_srcs = self._collect_header_srcs(markdown_text, structure)
pipelines/litedoc_pipeline.py:246:        fig_filter = image_filter.make_figure_filter(
pipelines/litedoc_pipeline.py:268:    def _collect_header_srcs(
tests/test_ingestion_engine.py:423:class TestImageFilterIntegration:（§7.2 整合測試存在）
```

### §5.5 §5 SOP 一致性核查（實貼）

```
--- logging：grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <三修改檔>
無命中（合規）——新增 warning 於行界解析 soft 路（含 exc_info=True）
--- database：grep -nE "\.commit\(\)" <三修改檔> | grep -v "with .*session.*begin()"
無命中（合規）——零 DB 操作
```

---

## §6 不可動清單遵守狀態

- [x] `pipelines/resume_pipeline.py`、`pipelines/slide_pipeline.py` — 零改（無圖片路）
- [x] A 軌鏈本體／`pipelines/contracts.py` 凍結合約 — 零改
- [x] Vision LLM — 零參與 Drop 決策（全鏈純幾何）
- [x] `ingestion_engine`（C2 產物）／`image_filter`（C1 產物）／`section_engine` — 零改
- [x] `_build_tiles` 既有流程（processed.json／tiling／_load_tiles）— 零動（僅插入兩行注入）
- [x] 門檻＝plan v2 校正值（filter 讀 settings、C1 已鎖）
- [x] 既有 tests 斷言本體 — 零改（僅新增 4 測試）

---

## §7 銜接

- **baton 狀態**：C1-C3 報告＋plan v2＋tasks＋design spec 均暫存 `baton/`、未 mv 未 git add（C_CHECKOUT 一次性歸檔）。
- **hash 自癒**：C2 已 ship＝`f39f8cb`；「待 baron 回填」佔位符雙源掃描＝0。
- **自評（正向）**：plan v2 §2 全部實作條款（§2.1-§2.6）落地——三規則過濾全鏈自此於 litedoc 生效、§7.2 整合以實體圖檔驗畢兩個最險邊界。**（負向防錯）**：SpaceX 真樣本 3 垃圾／20 內容之硬判與第二樣本泛化屬 baron 影子 E2E（plan §8.2、Checkout 後）；log 三筆 DROP 審計亦於 E2E 核對。
- **下一步**：C_CHECKOUT — Checkout（收官歸檔）；等 baron 確認本 commit 後另行下達 checkout 提示詞。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（報告 §3 中已列出）

# 2. git add 清單（僅包含本次 C3 實質改動代碼與對應的備份檔；baton/ 目錄下的報告等文件不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add pipelines/litedoc_pipeline.py
git add tests/test_litedoc_pipeline.py
git add tests/test_ingestion_engine.py
git add .claude-logs/archive/2026-07-21_IMG-FILTER_C3_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_litedoc_pipeline.py.bak
git add .claude-logs/archive/2026-07-21_IMG-FILTER_C3_test_ingestion_engine.py.bak

# 3. commit message 草稿（已寫入 /tmp/IMG-FILTER_C3_msg.txt）
cat > /tmp/IMG-FILTER_C3_msg.txt << 'EOF'
BE-Refactor: IMG-FILTER C3 — Litedoc Pre-pass Wiring（litedoc 報頭預掃接線）

1. 修改 pipelines/litedoc_pipeline.py，新增私有方法 _collect_header_srcs，依前段結構判型 doc_structure max end 界定報頭行界，預掃該行界內 ![](src) 行收集 header_srcs。
2. 於 _build_tiles 內建立 image_filter.make_figure_filter 閉包工廠實例，將與 paper_name 對齊之 images_root 與 header_srcs 傳入，並注入 assemble 頂層入口。
3. 擴充 tests/test_litedoc_pipeline.py，驗證報頭區行界 pre-pass 準確度與 sidecar 缺失時的降級行為。
4. 於 tests/test_ingestion_engine.py 中新增 §7.2 跨 Phase 整合測試，使用實體 header-only 暫存檔與擬真 md 執行真實 tiled 組裝，驗證報頭垃圾圖 DROP 且 481 級內文 Chart 圖 KEEP（守門測試）。
EOF

# 4. baron 手動執行
git commit -F /tmp/IMG-FILTER_C3_msg.txt
```

---

## §99 治理規格與 Revision

### §99.2 Revision 歷程

- v1 (2026-07-21)：C3 執行完成——報頭預掃＋注入接線、三規則於 litedoc 生效、§7.2 實體圖檔整合（481 守門）、831 passed 零回歸、SOP 雙核查合規
