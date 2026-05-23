# 2026-05-20 簡報第一頁未翻譯修復（md_processor.parse 對 slides 不收 authors）

只動 `processor/md_processor.py` 一處（`parse()` 內 2 點：取 doc_type +
首個 H1 處依 doc_type 設 collecting_authors）。未動 doc_analyzer / prompts /
translate_processor / pipeline_core / 其他 .py / 前端。

## 真因（既有報告轉述）
`parse()` 對所有 doc_type 一律 `collecting_authors=True`：第一個 H1 之後、
第一個 H2 之前的內容全塞 `authors_info`。學術論文 OK；簡報第一頁標題後
直接是內容（無作者區塊），被整片吞進 `authors_info`，且
`translate_processor` 不翻 `authors_info` → 第一頁中譯缺失。

## 修改 diff
```diff
@@ class MarkdownProcessor:
     def parse(self, content: str, structure: dict = None) -> Dict[str, Any]:
         lines = content.split('\n')
         result = {'title': '', 'authors_info': '', 'sections': []}
+        doc_type = (structure or {}).get('document_type', 'academic')

         # 從 doc_analyzer 的 structure 取得 authors 行號集合
@@ first-H1 branch
                 if not has_started:
                     result['title'] = title_text
-                    collecting_authors = True
+                    # collecting_authors=True 表示「H1 後到 H2 前是 authors 區塊」，
+                    # 適用學術論文與新聞（標題後跟作者/byline）；簡報沒有此區塊，
+                    # 第一頁標題後直接是內容，不啟用收集（否則第一頁會被吞進
+                    # authors_info 且 translate 跳過 → 中譯缺第一頁）。
+                    SLIDES_DOC_TYPES = ('slides',)
+                    collecting_authors = doc_type not in SLIDES_DOC_TYPES
                     has_started = True
                     continue
```
淨變動：+7 行（1 行取 doc_type + 4 行 inline 註解 + 1 行常數 + 1 行條件式
取代原 1 行）。**未動其他邏輯**：`author_lines` 集合（211–217）、abstract /
references / orphan section 分支、後續所有 `collecting_authors` 觸發點皆原封。

## 預期行為（spec 內已述）
- slides：result.authors_info='' / sections[0] = 第一頁孤立內容（走
  line ~282–289 孤立分支：title=''、heading_level=2）/ 之後依原邏輯切段
  → 翻譯後 sections[0] 有 translated_content → final_zh.md 第一頁中文出現。
- 學術論文（800-vdc 等）：`doc_type != 'slides'` → `collecting_authors=True`，
  既有行為不變、無回歸。
- 其他 doc_type（book / technical / news / web）：同 academic，預設仍走
  authors 收集——若日後發現某型不該收，加進 `SLIDES_DOC_TYPES` 即可。

## 驗證
- **py_compile** `processor/md_processor.py`：通過。
- **pytest** `tests/test_metadata_extractor.py -q`：**18 passed, 3 skipped**
  （metadata 測試與 md_processor 無關，符合預期不變）。
- **端到端**（OrcStack 重啟後手動）：
  - ALi 簡報：DB 刪該筆 + disk paper_dir 清乾淨重上傳 → 預期
    `structured.json` `authors_info=""`、sections 從第一頁開始；
    `final_zh.md` 第一頁出現中文翻譯。
  - 800-vdc（學術論文）回歸：上傳後 `authors_info` 仍有作者資料（不受影響）。
  - 若不想重跑整條 pipeline，亦可：手動把該 paper 的後續 stage（md2json
    及之後）視為「需重跑」——但實務上重上傳最簡單。

## 推薦 commit message
```
fix(md_processor): slides 不啟用 collecting_authors，修正第一頁未翻譯

parse() 對所有 doc_type 一律 collecting_authors=True：第一個 H1 之後、
第一個 H2 之前的內容會被塞進 authors_info。學術論文符合（H1 後即作者
名單）；但簡報第一頁標題後直接是內容（無作者區塊），被整片吞進
authors_info，且 translate_processor 不翻 authors_info → final_zh.md
第一頁僅顯示英文，從第一個 H2（## STB…）才有中文。

修法：parse() 從 structure 取 document_type，於首個 H1 處依 doc_type
決定是否啟用 collecting_authors：
  SLIDES_DOC_TYPES = ('slides',)
  collecting_authors = doc_type not in SLIDES_DOC_TYPES

slides → False（不收，第一頁走孤立 section 分支正常翻譯）；
其他 doc_type → True（既有行為不變）。

不動其他邏輯（author_lines 集合、abstract/references/orphan 分支、
所有 collecting_authors 觸發點皆原封）；未改 doc_analyzer / prompts /
translate_processor / pipeline_core / 前端。

py_compile 通過；metadata 測試 18 passed 3 skipped 無回歸。
端到端：簡報需 OrcStack 重啟後重新上傳驗中文第一頁；學術論文回歸
（authors_info 仍有資料）。
```

## 不可動清單（已遵守）
- doc_analyzer.py / prompts：未動
- translate_processor.py：未動
- pipeline_core.py：未動
- 其他 .py：未動
- 前端：未動
- 既有 `author_lines` 集合、abstract / references / orphan section 邏輯、
  後續 `collecting_authors` 觸發點：皆未動
