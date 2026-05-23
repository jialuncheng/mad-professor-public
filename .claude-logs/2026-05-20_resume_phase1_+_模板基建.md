# 2026-05-20 resume doc_type Phase 1 + 模板基建（A+B+C+D）

四件事一次完成。**未 commit**，等 baron 確認。

| 件 | 內容 | 檔數 |
|---|---|---|
| A | 七層 resume 註冊 | 5 既有 .py/.html 修改（7 處 edit）|
| B | 七層 marker 註解 | 與 A 合併同次 edit |
| C | 模板文件 `docs/HOW_TO_ADD_DOC_TYPE.md` | 新檔（~250 行）|
| D | 驗證腳本 `tools/check_doc_type_registry.py` | 新檔（~170 行）|

---

## A + B：七層 resume 註冊 + marker（diff）

### A-1 + B-1：`web_server.py:481` valid_types
```diff
-    valid_types = ['academic', 'book', 'technical', 'slides', 'web', 'news']
+    # === doc_type-registry ===
+    # 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
+    valid_types = ['academic', 'book', 'technical', 'slides', 'web', 'news', 'resume']
```

### A-2 + B-2：`static/index.html` DOC_TYPES（line 1573）
```diff
   (function setupDropdown() {
+    // === doc_type-registry ===
+    // 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
     const DOC_TYPES = [
       ['academic', '學術論文'], ['book', '書籍'], ['technical', '技術文件'],
       ['slides', '簡報'], ['web', '網頁存檔'], ['news', '新聞文章'],
+      ['resume', '履歷'],
     ];
```

### A-3 + B-3：`static/index.html` DOC_TYPE_LABELS（line 2322）
```diff
 // 文件類型確認
+// === doc_type-registry ===
+// 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
 const DOC_TYPE_LABELS = {
   academic: '學術論文', book: '書籍', technical: '技術文件',
   slides: '簡報', web: '網頁存檔',
-  news: '新聞文章'
+  news: '新聞文章',
+  resume: '履歷'
 };
```

### A-4 + B-4：`processor/doc_analyzer.py` HEADING_FIX_PROMPTS
```diff
+# === doc_type-registry ===
+# 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
 HEADING_FIX_PROMPTS = {
     'academic':  'prompt/doc/heading_fix_academic.txt',
     ...（既有 6 項）
+    'resume':    'prompt/doc/heading_fix_academic.txt',  # Phase 1 reuse academic
 }
```

### A-5 + B-5：`processor/doc_analyzer.py` STRUCTURE_PROMPTS
```diff
+# === doc_type-registry ===
+# 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
 STRUCTURE_PROMPTS = {
     'academic':  'prompt/doc/structure_academic.txt',
     ...（既有 6 項）
+    'resume':    'prompt/doc/structure_academic.txt',  # Phase 1 reuse academic
 }
```

### A-6 + B-6：`processor/translate_processor.py` style_hints
```diff
         doc_type = getattr(self, 'doc_type', 'academic')
+        # === doc_type-registry ===
+        # 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
         style_hints = {
             ...（既有 6 項）
+            'resume': '文件為個人履歷（CV），請使用正式商務中文，職稱、公司名、技術名詞保留原文',
         }
```

### A-7 + B-7：`pipeline_core.py:598` extra_info skip
```diff
         doc_type = output_paths.get('_confirmed_doc_type', 'academic')
         domain = output_paths.get('_domain', '')
-        if doc_type in ('news', 'web', 'slides'):
+        # === doc_type-registry ===
+        # 新增 doc_type 須同步更新此處。詳見 docs/HOW_TO_ADD_DOC_TYPE.md
+        if doc_type in ('news', 'web', 'slides', 'resume'):
             return self.extra_info_processor.generate_document_summary(
```

### diff stat
```
 pipeline_core.py                 |  4 +++-
 processor/doc_analyzer.py        |  6 ++++++
 processor/translate_processor.py |  3 +++
 static/index.html                |  8 +++++++-
 web_server.py                    |  4 +++-
 5 files changed, 22 insertions(+), 3 deletions(-)
```

---

## C：`docs/HOW_TO_ADD_DOC_TYPE.md` 完整內容

新建 ~250 行模板文件，含七章節：

§1. 概念說明（doc_type vs domain、6+1 doc_type 處理特點對照表）
§2. 註冊點清單（7 處詳列：位置、形式、作用、改動範例、注意事項）
§3. 新增 doc_type 必填問題清單（9 項）
§4. prompt 設計指南（heading_fix / structure 兩類骨架 + 既有 6 prompt 對比）
§5. 驗證流程（6 步驟，含跑 check_doc_type_registry.py）
§6. 反例：不該做的（5 條）
§7. marker / 工具引用

關鍵摘錄：

**§1.2 doc_type vs domain**
> doc_type = pipeline **處理路由**（使用者選；決定 SlidesProcessor/MinerU、
> 是否跑 extra_info、哪個 prompt、哪個 style hint）。
> domain = AI **prompt 描述用**（LLM 看第一頁產生；附加到 character /
> explain / summary / translate prompt 結尾，提供具體文件主題描述）。
> 互補不衝突。

**§2 七註冊點 grep 入口**
> `grep -n "=== doc_type-registry ===" <file>` 即可定位所有註冊點。

**§6 反例**
> 不要為新 doc_type 改 ai_router / ai_character prompt 措辭（已通用化、
> 靠 domain 注入補名詞）；不要在 `_stage_extra_info` 加新分支（只能加入或
> 不加入 skip tuple）；不要隨意擴充 `md_processor.SLIDES_DOC_TYPES`。

完整內容請見 `docs/HOW_TO_ADD_DOC_TYPE.md`。

---

## D：`tools/check_doc_type_registry.py` 完整 source + 範例輸出

### 主要邏輯
1. 從 7 個註冊點抽 doc_type 集合（regex 解析）
2. 5 個註冊點必須 = `web_server.valid_types`（truth set）
3. `pipeline_core.extra_info_skip` 必須是 truth 的子集
4. 每個註冊點上方 5 行內必須有 marker `=== doc_type-registry ===`
5. `doc_analyzer` 兩 dict 指向的所有 prompt 檔必須存在
6. exit 0 / 1

### 自我驗證輸出
```
✓ All doc_types aligned across 6 registry points (+1 subset):
  academic, book, news, resume, slides, technical, web
  pipeline_core.extra_info_skip (subset): news, resume, slides, web
✓ All 7 markers present
✓ All required prompts exist
exit code: 0
```

### 用法
```
python tools/check_doc_type_registry.py   # 從專案根目錄跑
```
exit code 可接 pre-commit hook（成功 0、失敗 1）。

### 失敗範例（模擬：移除 doc_analyzer 的 resume）
```
✗ DOC_TYPE MISALIGNMENT:
  web_server.valid_types: ['academic','book','news','resume','slides','technical','web']
  doc_analyzer.HEADING_FIX_PROMPTS: missing: ['resume']
✓ All 7 markers present
✓ All required prompts exist
exit code: 1
```

### 開發 catch（誠實標註）
首次自我驗證**自抓 1 個 bug**：原 `_extract_dict_keys` regex 只認 quoted
key（`'academic':`），但 `DOC_TYPE_LABELS` 用 JS shorthand 無引號
（`academic: '...'`）→ 誤報 5 個 missing。已修：regex 支援 quoted /
unquoted JS shorthand 兩種寫法。

完整 source 請見 `tools/check_doc_type_registry.py`（~170 行，含註解）。

---

## 驗證

| 項 | 結果 |
|---|---|
| `py_compile` 5 個 .py（含新 tool） | ✓ |
| `node --check` 抽出主 `<script>` | ✓ |
| `pytest tests/test_metadata_extractor.py -q` | **18 passed, 3 skipped**（無回歸）|
| `python tools/check_doc_type_registry.py` 自我驗證 | **exit 0**（全 ✓）|
| 7 個 marker grep（每 file 至少 1）| ✓（web_server / pipeline_core / doc_analyzer×2 / translate_processor / static/index.html×2）|
| `doc_analyzer.py` HEADING_FIX/STRUCTURE 兩 dict 指向 prompt 存在 | ✓（resume reuse academic.txt 存在）|

端到端（待 OrcStack 重啟 + Ctrl+Shift+R）：
- 前端 dropdown「履歷」排尾出現
- 上傳履歷 → 選「履歷」→ confirm → pipeline 跑完（DB `Paper.doc_type='resume'`、
  extra_info 走 `generate_document_summary` 不走 process）
- AI 對話可正常引用履歷內容（domain 注入 + character prompt 通用化已就位）

---

## 推薦 commit 拆分

**推薦 3 commit**（可閱讀性與 revert 粒度最佳）：

### Commit 1：`feat(doc_type): 加 resume，並對齊 7 註冊點 marker`
**檔**：`web_server.py` / `pipeline_core.py` / `processor/doc_analyzer.py` /
`processor/translate_processor.py` / `static/index.html`
**A + B 合一**：因 marker 與 resume entry 在同一處 edit、邏輯上同源
（marker 為「此處屬 doc_type registry」的 metadata，與「resume 入列」一起
正向變動），合一 commit 較自然。

```
feat(doc_type): 新增 resume 文件類型（Phase 1 reuse academic prompt）

Phase 1：七層註冊 + doc_type-registry marker。reuse academic prompt 讓
功能能跑；Phase 2 才寫專用 prompt。

七層改動：
- web_server.py:481  valid_types +'resume'
- static/index.html  DOC_TYPES +['resume','履歷']（dropdown，排尾）
- static/index.html  DOC_TYPE_LABELS +resume:'履歷'
- processor/doc_analyzer.py  HEADING_FIX_PROMPTS +'resume': academic.txt
- processor/doc_analyzer.py  STRUCTURE_PROMPTS +'resume': academic.txt
- processor/translate_processor.py  style_hints +'resume': 商務中文提示
- pipeline_core.py  extra_info skip tuple +'resume'

每處註冊點上方加 `=== doc_type-registry ===` marker 註解，指向
docs/HOW_TO_ADD_DOC_TYPE.md。

baron 決策對齊：title 由 LLM 自訂 / 走翻譯 / 跳 extra_info / 排尾 /
SLIDES_DOC_TYPES 不擴充 / 不做 is_resume_pdf。

py_compile + node --check + pytest 通過；驗證腳本見後續 commit。
```

### Commit 2：`docs: 新增 HOW_TO_ADD_DOC_TYPE 模板文件`
**檔**：`docs/HOW_TO_ADD_DOC_TYPE.md`（新）
```
docs: 新增 docs/HOW_TO_ADD_DOC_TYPE.md（doc_type 工程手冊）

涵蓋：
- doc_type vs domain 概念辨明
- 6+1 doc_type 處理特點對照表
- 7 個註冊點詳列（路徑、形式、改動範例、注意事項）
- 新增 doc_type 必填問題清單（9 項）
- prompt 設計指南（heading_fix / structure 骨架 + 既有 prompt 對比）
- 驗證流程（含驗證腳本）
- 反例（不要做的事）

對應上輪「加 doc_type-registry marker」commit；marker 文字
（'# === doc_type-registry ===' / '// === doc_type-registry ==='）
精確一致，供下輪驗證腳本 grep。
```

### Commit 3：`tools: 新增 check_doc_type_registry.py 對齊驗證腳本`
**檔**：`tools/check_doc_type_registry.py`（新）
```
tools: 新增 check_doc_type_registry.py 驗證 doc_type 七層對齊

從 7 個註冊點 regex 抽 doc_type 集合，比對：
1. 5 個註冊點必須 = web_server.valid_types（truth set）
2. pipeline_core.extra_info_skip 必須是 truth 的子集
3. 每個註冊點上方 5 行內須有 '=== doc_type-registry ===' marker
4. doc_analyzer 兩 dict 指向的 prompt 檔須存在

exit 0 = 全對齊；exit 1 = 任一不對齊。可接 pre-commit hook。

用法：python tools/check_doc_type_registry.py（從專案根目錄）

開發注意：JS DOC_TYPE_LABELS 用 unquoted shorthand 鍵（academic: '...'），
_extract_dict_keys 需同時支援 quoted（Python）與 unquoted（JS shorthand）。
首次自我驗證即抓到此差異並修正。
```

> 也可合成單一 commit（feat+docs+tools 一起），但拆 3 commit revert 粒度
> 較佳——尤其 commit 1 若日後要 revert resume 但保留 marker/工具基建，
> 拆分可直接 `git revert HEAD~2`。

---

## 不可動清單（已遵守）
- `prompt/doc/heading_fix_academic.txt` / `structure_academic.txt`：未動
  （Phase 1 reuse 但不複製，doc_analyzer dict 指向 academic 檔即可）
- 未新增 `prompt/doc/heading_fix_resume.txt` 或 `structure_resume.txt`
  （Phase 2 才做）
- `md_processor.py` `SLIDES_DOC_TYPES`：未動（D-3 決策保持 `('slides',)`）
- `AI_professor_chat.py` / `ai_core.py` / `paper_manager.py`：未動
- 其他既有 prompt：未動
- 未引入新 CDN
- **未 git add / 未 commit**

## 開放問題（暫無）
本輪 4 件事完整完成、自我驗證通過、無 baron 拍板需求；端到端 UX 驗證
待 OrcStack 重啟後手動跑。
