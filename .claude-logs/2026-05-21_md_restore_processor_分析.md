# md_restore_processor.py 與完整 markdown 鏈路 — 工程影響分析

> 純讀分析、零檔案改動。
> 觸發問題：baron 發現中央正文區開頭品質不一（800-vdc 是「# 目錄」、1763964…
> 是「# 第 1 頁」、DeHunt 正常），質疑 Phase 4.7c 走前端 hero 是否方向錯。

---

## TL;DR

1. **md_restore_processor 不是「restore 圖片」、不是「restore 缺漏內容」**——它是 **JSON → 雙語 Markdown 序列化器**。職責：讀 `translate` 階段產出的 JSON tree（含 `title / authors_info / sections[].title / .content[]`），按章節順序輸出 `final_{paper_name}_en.md` + `final_{paper_name}_zh.md`。
2. **`# 標題` 第一行的真正來源** = **MinerU/SlidesProcessor 輸出的第一個 markdown heading**，一路被 `md_processor.parse()` 抽成 JSON 的 `data['title']`，最後被 RestoreProcessor 在第 244-248 行寫成 `# {title_en}`。
   - 800-vdc：MinerU 對 cover-TOC 文件第一個 `#` 是 `# Contents`
   - 1763964…：SlidesProcessor 從不寫 H1，每頁 `## 第 N 頁`；md_processor 抓第一個 heading（H2）當 title → `# 第 1 頁`
   - DeHunt：heading_fix prompt 把候選人姓名拉到 H1（或原 markdown 結構正常）
3. **方向沒錯，但**：Phase 4.7c 的 5 個 commit 改的是「**paper-item 標題顯示 + metadata hero 區塊**」，跟「**中央 markdown 開頭品質**」是**兩個不同的洞**——baron 提的這個是「中央 markdown 第一行品質」，4.7c 解的是「左欄與中央 hero 顯示」。兩個都該做，4.7c 工作**沒白做、有獨立價值**。
4. **真正該補的是 Phase 4.7d**：讓 `RestoreProcessor.process` 接收外部 `metadata`，**在 markdown 開頭注入正規化的 title + authors + abstract**——取代/覆寫 `data['title']` 來源。工程量小（~30-60 分、1 commit）。
5. **不要動 md_processor 解析邏輯**——它的 `data['title']`「抓第一個 #」是合理的（多數 academic 論文確實如此）；該動的是「md_restore 階段，metadata 比第一個 # heading 更可信時優先用 metadata」。

---

## A. md_restore_processor.py 完整盤點

### A-1 真實職責

檔名 `RestoreProcessor` + 註解「恢复处理器，将提供的json文件还原成中英两篇md文档」——"restore" 是「**從 JSON 還原回 markdown**」（即「翻譯處理是把 markdown→JSON 拆解、md_restore 是 JSON→雙語 markdown 重組」），**不是還原圖片、不是修補內容**。

public 介面只有 1 個：

| 函式 | 簽名 | 職責 |
|---|---|---|
| `process(input_path, output_path_en, output_path_zh, images_info_path=None)` | 讀 input JSON → 寫雙語 .md | 主入口；回 `(en_path, zh_path)` |

内部輔助：
- `_read_file()` — 讀檔
- `_clean_authors_info(authors_info)` — 清作者區塊（移除上標數字、HTML table、Contents 字樣、控制字元）
- `_write_to_md(path, content)` — append 內容 + 兩個換行
- `_process_section(section, out_en, out_zh, level, vision_captions)` — 遞迴章節處理（標題 + 內容 ordered_items：text / formula / figure / table / ref，並按 `(index, part)` 排序合併）

**`# 標題` 第一行寫入點**（`md_restore_processor.py:244-248`）：
```python
title_en = data.get('title', '')
self._write_to_md(output_path_en, f"# {title_en}")
title_zh = data.get('translated_title', title_en)
self._write_to_md(output_path_zh, f"# {title_zh}")
```

**這就是中央正文區看到的「# 第一行」唯一寫入點**。整個 RestoreProcessor 內**不存在 metadata 注入點**——它只認 `data['title']`。

### A-2 在 pipeline 內的位置

pipeline_core stage 列舉（`pipeline_core.py:31-32`）：
```
pdf2md → analyze → detect_domain → md2json → json_process → tiling
→ translate → image_caption → md_restore → extra_info → rag
```

`md_restore` 階段在 `_stage_md_restore`（L587-597）：
- **輸入**：
  - `output_paths['translate']` — 來自 translate 階段的 JSON 檔（含 `title / translated_title / authors_info / sections[]`）
  - `output_paths['image_caption']` — Vision 圖片說明 JSON（可選，補圖檔說明）
- **輸出**：
  - `paper_dir / f"final_{paper_name}_en.md"`
  - `paper_dir / f"final_{paper_name}_zh.md"`

跟其他處理器的關係：

```
[MinerU/SlidesProcessor] → raw markdown ({paper_name}.md)
        ↓ md_cleaner (僅 MinerU 路徑)
[doc_analyzer.analyze] → heading_fix (LLM 修正 #/##/### 層級)
                       → structure sidecar JSON ({stem}_doc_structure.json)
        ↓
[md_processor.parse] → 解析 markdown → JSON:
                       {title, authors_info, sections: [...]}
                       ← data['title'] 在這裡產生：抓第一個 # heading 的文字
        ↓
[json_processor / tiling_processor] → 切塊、加 index/part
        ↓
[translate_processor] → 每個 title / content 加 translated_*
        ↓
[image_caption_processor] (parallel) → Vision 看 images/
        ↓
[md_restore_processor] → 寫 final_*_en.md / final_*_zh.md  ← 前端顯示這個
        ↓
[extra_info / rag] → tags + vector store
```

### A-3 跟 final_*_zh.md / final_*_en.md 的關係

- **final 檔的唯一寫入者**：`md_restore_processor.RestoreProcessor.process`
- **path 定義**：`paper_manager.py:93-98`
  ```python
  article_zh_path = paper_dir / f"final_{paper_uuid}_zh.md"
  article_en_path = paper_dir / f"final_{paper_uuid}_en.md"
  ```
- **前端讀取**：`/api/papers/{paper_id}/content?lang={zh|en}` → 讀 `article_zh / article_en` path → 整檔回傳 → 前端 `marked.parse()` 渲染進 `#paper-content`

**translate_processor 不寫 final**——只動 JSON tree、加 `translated_*` 欄位。final 寫入**僅在** md_restore 階段。

---

## B. markdown pipeline 完整鏈路（從 PDF 到 final）

| 階段 | 處理器 | 輸入 | 輸出 | `title` 軌跡 |
|---|---|---|---|---|
| 1. **pdf2md** | MinerU / SlidesProcessor | PDF | `{paper_name}.md` | MinerU 輸出第一個 `#` 是 PDF 第一頁的視覺主標（cover-TOC 就是 `# Contents`）；SlidesProcessor **從不寫 H1**，全是 `## 第 N 頁` |
| 2. (cleaner) | md_cleaner | raw .md | 同檔（清純數字行等）| 不動 title |
| 3. **analyze** | doc_analyzer | raw .md | （a）改寫 .md heading 層級；（b）`{stem}_doc_structure.json` sidecar | LLM heading_fix prompt 對 slides 規則：「封面頁標題用 #」——但若 SlidesProcessor 沒寫 H1，prompt 無從拉。對 academic 通常 OK |
| 4. detect_domain | domain_detector | PDF | `output_paths['_domain']` | 不動 title |
| 5. **md2json** | md_processor | analyze 後的 .md + sidecar | `{stem}_structured.json` | **`data['title']` 在這裡產生**：`md_processor.py:258` `result['title'] = title_text`，title_text 來自第一個被 `title_pattern` 匹配的 line（pattern = `^(#+)\s*(\S.*?)$`——**`#` `##` `###` 都吃**） |
| 6. json_process | json_processor | structured JSON | 同 + 切塊 | 不動 title |
| 7. tiling | tiling_processor | json | 同 | 不動 title |
| 8. **translate** | translate_processor | structured JSON | `{stem}_translated.json`，加 `translated_title / translated_content` | 只**翻譯** `title`，不換 title 本體 |
| 9. image_caption | image_caption_processor (parallel) | images/ | `{stem}_images_info.json` | 不動 title |
| 10. **md_restore** | md_restore_processor | translated JSON | `final_{paper_name}_en.md` / `_zh.md` | `# {title_en}` / `# {title_zh}` 第一行寫入；**整個 pipeline 內 title 是 read-only**：md_processor 抓什麼，md_restore 就寫什麼 |
| 11. extra_info | extra_info_processor | translated JSON | `{stem}_extra.json` | 不動 final 檔 |
| 12. rag | rag_processor | rag_md / rag_tree | vector store | 不動 final 檔 |

**核心觀察**：
- **stage 5（md2json）是 title 唯一的決定點**。它的策略「抓第一個 # heading」對 academic 合理（論文封面通常 H1 = 標題），對 cover-TOC technical 與無 H1 的 slides 直接壞掉。
- **stage 10（md_restore）是 title 唯一的寫入點**。在這裡注入 `metadata.title` 可以**完全旁路**md2json 的錯誤 title。
- **stage 11+ 不影響 final 檔**——所以「在 md_restore 後再補一道」也沒意義。

---

## C. 三個案例的真實流程追蹤

### C-1 800-vdc-architecture-for-ai-infrastructure（technical）

1. **MinerU 輸出**：cover 是 TOC → 第一個 H1 是 `# Contents`（或 `# 目錄`）
2. **doc_analyzer heading_fix**：LLM 看 heading 列表，但「Contents」確實是 # 等級，沒理由改
3. **md_processor.parse**：第一個 # → `data['title'] = "Contents"`
4. **translate**：`translated_title = "目錄"`
5. **md_restore**：寫 `# Contents` / `# 目錄` 開頭
6. **前端**：看到「# 目錄」

**修正點**：metadata.title（4.7c commit 3 後 technical 走 multi-page LLM 應該能抽到真實 title）若有值，md_restore 應**優先用 metadata.title**。

### C-2 1763964129445952184（slides）

1. **SlidesProcessor 輸出**：完全沒有 H1，每張投影片 `## {slide_title or "第 N 頁"}`
2. **doc_analyzer heading_fix**：slides prompt 寫「封面頁標題用 #」，**但若 LLM 看不到 H1 候選**（SlidesProcessor 沒寫），它只能在 `##` 之間做層級調整——不會自動補出 H1
3. **md_processor.parse**：`title_pattern = ^(#+)\s*` **吃 `##` 也算 title** → 抓到第一個 `## 第 1 頁` → `data['title'] = "第 1 頁"`
4. **md_restore**：寫 `# 第 1 頁` 開頭
5. **前端**：看到「# 第 1 頁」（H2 被 md_restore 提到 H1）

**修正點**：
- 短期：md_restore 接 metadata.title 注入（與 800-vdc 同方案）
- 中期：SlidesProcessor 應寫 H1（用第一張投影片的 title，或從 metadata page1 結果灌入）

### C-3 DeHunt（resume）

1. **MinerU 輸出**：履歷第一行通常是候選人姓名（如 `# XDeHunt`）
2. **heading_fix**：resume 走 academic prompt（4.7c commit 3 後仍如此——commit 3 只動 metadata prompt，不動 heading_fix prompt）；prompt 維持原 # 等級
3. **md_processor.parse**：抓到 `# XDeHunt` → `data['title'] = "XDeHunt"`
4. **md_restore**：寫 `# XDeHunt` + `## 候選人摘要`（後者來自 doc_analyzer structure + extra_info 或 markdown 原段落）
5. **前端**：看到完整結構

**沒有修正需求**——但若 metadata.candidate_name 抽到「DeHunt」（無 X 前綴）會與 markdown 不一致，這需要：md_restore 注入 candidate_name 時取代 markdown 第一行的 `# X...`。

---

## D. Phase 4.7c 5 個 commit 是否還有獨立價值？

**TL;DR：有，全部都有。** 它們解的是「不同的洞」：

| Commit | 解的問題 | 跟「中央 markdown 開頭」的關係 |
|---|---|---|
| 1. `resolve_title` fallback 加 original_filename | **左欄 paper-item / DB.title 顯示**為醜 paper_uuid | **無關**——它是 DB.title 鏡像層，不影響 final markdown |
| 2. schema 加 `candidate_name` | metadata schema 完備 | **下游基建**——下次注入 markdown 開頭時要這欄 |
| 3. resume / technical 專用 prompt | metadata.title / candidate_name 抽得到 | **核心前置**——若沒這 commit，metadata.title 對 technical / resume 都是空的，markdown 注入也注入不出東西 |
| 4. paper-item 顯示優先序 | 左欄顯示 | **無關**——左欄 |
| 5. content-area metadata hero | 中央 hero 顯示 metadata 區塊 | **跟「markdown 開頭」是兩件事**——hero 是 toolbar 下方的獨立 section，並非 markdown 內 |

**整體判斷**：
- 4.7c 解的是 **「顯示層」**問題（左欄 + 中央 toolbar/hero）
- baron 觀察到的是 **「資料層」**問題（final markdown 開頭內容本身）
- **兩個都該做、互不取代**。4.7c 沒走錯方向，只是涵蓋範圍不含 markdown 內文。
- **commit 5（hero）可能被質疑為「重複資訊」**：hero 顯示 title + authors + abstract，markdown 開頭可能也有 # title——但只要 markdown 開頭因 md_restore 注入改成 metadata-derived，兩處顯示**會一致**，hero 仍是「結構化呈現 metadata」的價值，**不重複**。

---

## E. 建議：Phase 4.7d — md_restore 注入 metadata

### E-1 設計

讓 `RestoreProcessor.process` 接收外部 metadata 參數，在寫第一行 `# title` 前優先用 metadata。

**新簽名**：
```python
def process(self, input_path, output_path_en, output_path_zh,
            images_info_path=None,
            metadata: Optional[dict] = None,        # 新增
            doc_type: Optional[str] = None) -> tuple:  # 新增
```

**注入邏輯**（在 `data['title']` 讀取前）：
```python
# Phase 4.7d：metadata.title 比 md2json 抓的 first-# 更可信，優先注入
mt_value = (metadata or {}).get('title', {}).get('value') if metadata else None
mt_tt    = (metadata or {}).get('translated_title', {}).get('value') if metadata else None
mt_cand  = (metadata or {}).get('candidate_name', {}).get('value') if metadata else None

if doc_type == 'resume' and mt_cand:
    final_title_en = mt_cand
    final_title_zh = mt_cand  # 姓名通常不翻譯
elif mt_value:
    final_title_en = mt_value
    final_title_zh = mt_tt or mt_value
else:
    final_title_en = data.get('title', '')
    final_title_zh = data.get('translated_title', final_title_en)

self._write_to_md(output_path_en, f"# {final_title_en}")
self._write_to_md(output_path_zh, f"# {final_title_zh}")
```

**caller 端**（`pipeline_core._stage_md_restore`）：
```python
en_path, zh_path = self.restore_processor.process(
    str(input_path), str(paths['en']), str(paths['zh']),
    images_info_path=...,
    metadata=getattr(self, '_metadata', None),
    doc_type=output_paths.get('_confirmed_doc_type', 'academic'),
)
```

### E-2 涉及檔案

| 檔案 | 動量 | 動什麼 |
|---|---|---|
| `processor/md_restore_processor.py` | +15 / -3 | `process` 加 `metadata` / `doc_type` 參數，title 寫入前優先注入 |
| `pipeline_core.py` | +3 / -0 | `_stage_md_restore` 傳 `metadata + doc_type` |
| **不動** md_processor / translate_processor / doc_analyzer | — | 上游 title 來源邏輯保留為 fallback |

工程量 **30-60 分、1 commit**。

### E-3 風險點

| 風險 | 評估 |
|---|---|
| 既有 paper 重跑 pipeline 會壞？ | **否**。`md_restore` 階段重跑只是覆寫 final_*_en/zh.md，input JSON 不變 |
| metadata 抽錯 → title 比之前更糟？ | 有可能（如 LLM 對 resume 抽到「XCV」之類雜訊）。**緩解**：metadata.title.confidence == 'low' 時 fallback 回 data['title'] |
| markdown 內文與 hero 顯示重複？ | 不重複——hero 是 toolbar 下方的「結構化 metadata block」（含 authors / abstract），markdown 內第一行 `# title` 是文章主體標題；兩者語意上一致是好事，不是冗餘 |
| 既有 final_*_zh.md 不重生 → 顯示不一致？ | 是。若不 backfill，舊 paper 仍顯示醜 title。**緩解**：使用者觸發「重新生成」按鈕（已有？需確認）；或單獨腳本只重跑 md_restore stage（pipeline_core 已有 stage 列表機制，可指定 stages=['md_restore']） |
| slides 沒 H1，md_restore 注入後 markdown 結構變成 H1 + H2 混合？ | 反而是改善——目前 slides 的 final 是 `# 第 1 頁` 接著 `# 第 2 頁`（都被提升）。Phase 4.7d 後第一行是 metadata.title，其餘維持 `## 第 N 頁`，**邏輯反而對了** |

### E-4 拆解：什麼時候做

**建議**：在 Phase 4.7c 5 個 commit **push 並驗證後再做 4.7d**。理由：

1. 4.7c 已先讓 metadata.title 對 resume/technical 抽得到（commit 3）——4.7d 就有 metadata 可用
2. 4.7c 已讓 paper-item / hero 顯示新值——baron 可從 UI 看到 metadata 抽取**有沒有抽好**
3. 若 baron 跑 Test B/C 發現 metadata 抽得不準，先 iterate prompt（commit 3 的 prompt 檔），再做 4.7d——避免把錯誤 metadata 寫進 markdown 內文（讀者看到後印象更深）
4. 4.7d 工程量小，作為「4.7c 證明有效後」的 follow-up 自然

---

## F. 不該動的東西

| | 為何不動 |
|---|---|
| `md_processor.parse()` 的「抓第一個 #」策略 | 對 academic 合理；改它會破壞既有 paper 解析；改 md_restore 是更外層、更乾淨的注入點 |
| `translate_processor` | 它不負責 title 取捨，純翻譯 |
| `doc_analyzer.heading_fix` 邏輯 | LLM 對 heading 層級的判斷沒問題；問題出在 input markdown 第一個 heading 本身就錯（technical=Contents、slides=## 第 1 頁） |
| MinerU 輸出 | 黑盒外部 service，不該指望它改變首頁解析行為 |
| SlidesProcessor 不寫 H1 | 可改但範圍會擴張；4.7d 注入 metadata.title 等於補上 H1 |
| `_clean_authors_info` | 跟 title 無關，現況沒問題 |

---

## G. 跟其他 PENDING 的順序

| 任務 | 優先 | 跟 markdown 鏈路關係 |
|---|---|---|
| **Phase 4.7c push + 端到端驗證** | **P0**（已建好等驗證） | 沒它就沒 metadata 注入素材 |
| **Phase 4.7d md_restore 注入 metadata** | **P1**（4.7c 驗證後做） | 解決 baron 提的「中央 markdown 開頭品質」 |
| GCP 部署 | P1 | 正交 |
| P1 群 rename paper | P2 | 用 metadata 抽完 + 注入後若 user 仍不滿意，rename 是最後一道 user override |
| Stage B chat 抽 package | P3 | 正交 |

---

## H. 一句話結論

**md_restore_processor 是「JSON → 雙語 markdown」的序列化器、不是修補器**；中央正文區開頭的「# 第一行」唯一來源是「md_processor 抓 raw markdown 第一個 # heading」，被 md_restore 原樣寫進 final 檔。**Phase 4.7c 5 commits 沒做錯方向**——它們解的是「顯示層」；**baron 觀察到的是「資料層」**——需要 Phase 4.7d 1 個 commit、~45 分鐘、在 md_restore 階段注入 metadata.title 即可徹底修好。**兩者互補、不衝突**。
