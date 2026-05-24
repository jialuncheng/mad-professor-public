# Phase 4.7d RAG-7 (a + b) — Plan：浮水印黑名單清理 + resume 專用 heading_fix prompt

> 純讀分析、零業務檔案改動。
> 觸發：DeHunt 履歷 PDF 含 XDeHunt / HDeHunt 公司浮水印、被 MinerU OCR 抽成 markdown heading；加上 resume 借用 academic prompt、LLM 把 TARGETEK / ITRI 誤判為 H2——兩個獨立問題、需拆兩個 commit。

---

## TL;DR

- **既有黑名單機制**：`processor/md_cleaner.py` 已是 pdf2md 後、analyze 前的「行級清理 stage」、目前只清「圖表純數字行」；`md_restore_processor` 內另有大量 BLACKLIST 常數（title / authors / date 等）但屬 final stage 用、不是本問題場景。**md_cleaner 是浮水印清理的天然延伸點**。
- **7a 推薦設計**：自動偵測「整篇出現 ≥ 3 次的 heading 行」→ 視為浮水印 → 移除所有出現。閾值可從 settings env 調整。**只刪重複的 heading 行、不刪正文重複的字**。
- **7b 推薦設計**：新建 `prompt/doc/heading_fix_resume.txt`、改 `doc_analyzer.HEADING_FIX_PROMPTS['resume']` 指向新檔。明示「履歷多家公司 / 多個學位都是平行 H3」。**structure_resume.txt 留下次**（structure sidecar 對 RAG chunk 切割影響小、authors_info 抽取對履歷意義也低）。
- **拆 2 commits、7a 先 7b 後**——浮水印清掉後 prompt 看到的 markdown 才乾淨、LLM 判定才準。
- **5 個 open questions**（核心：偵測閾值預設值 / 是否允許 user override / structure_resume 何時做 / 既有 paper backfill 依賴 RAG-2）。

---

## 1. 既有黑名單機制盤點

### 1.1 grep 結果

```
processor/md_restore_processor.py:14-32, 217-241
  - TITLE_BLACKLIST_EXACT / TITLE_BLACKLIST_PATTERN
  - AUTHORS_BLACKLIST_NORM / DATE_BLACKLIST
  - META_LABEL_BLACKLIST / CANDIDATE_LABEL_BLACKLIST
  → final stage（md_restore 寫 header 時用、過濾不可信值）
```

**唯一既有「行級 / 文字級」清理**：`processor/md_cleaner.py`。

### 1.2 md_cleaner 結構與時機

`processor/md_cleaner.py:13-36` `MarkdownCleaner.clean(markdown_path)`：
```python
text = markdown_path.read_text(encoding='utf-8')
lines = text.split('\n')
cleaned_lines = []
for line in lines:
    stripped = line.strip()
    if stripped and re.match(r'^[-\d\s.%]+$', stripped):
        if not re.search(r'[a-zA-Z一-鿿]', stripped):
            self.logger.debug(f"移除圖表數字行: {repr(stripped)}")
            continue
    cleaned_lines.append(line)
text = '\n'.join(cleaned_lines)
markdown_path.write_text(text, encoding='utf-8')
```

特點：
- **In-place 重寫**（讀 → 過濾 → 寫回同檔）
- 行級過濾（每行 strip 後判斷）
- 用 `re.match` 字串 pattern；目前只一條規則（純數字行）
- soft fail：`try/except` 警告但不中止 pipeline

### 1.3 pipeline 內 md_cleaner 觸發時機

`pipeline_core.py:534-542` `_stage_pdf_to_md`：
```python
markdown_path = parser.parse(str(pdf_path), str(paper_dir))  # MinerU 或 SlidesProcessor
if doc_type != 'slides':
    self.md_cleaner.clean(markdown_path)   # pdf2md 後、analyze 前
return markdown_path
```

- **pdf2md 之後**（MinerU 輸出已落地 .md）
- **analyze 之前**（doc_analyzer 還沒看 .md）
- **slides 跳過**（SlidesProcessor 自己控制 markdown 結構）
- 對其他 doc_type 都跑

**天然是浮水印清理的延伸點**——既有架構、既有時機、既有檔。

### 1.4 結論

**選 md_cleaner 作為 7a 落地點**。無需新增 stage 或新檔；只擴 `clean()` 加一段「重複 heading 偵測 + 移除」邏輯。

---

## 2. B-1 浮水印黑名單設計

### 2.1 偵測策略選項

| 選項 | 描述 | 優 | 缺 |
|---|---|---|---|
| **A 純自動偵測** | 整篇出現 ≥ N 次的 heading line → 視為浮水印 | 零維護、適用所有 paper | 閾值校準難、可能誤殺正常重複（如「References」在書中可能多章節結尾出現） |
| **B 純手動 list** | global / per-doc_type 維護黑名單字串 | 精確、可控 | 維護成本高、新 paper 浮水印要新增 |
| **C 自動 + manual override** | 自動為主、user 可加 per-paper override list | 兼具 | 設計複雜、本 commit 範圍會擴大 |

**推薦 A**（純自動偵測），理由：
- 浮水印特性：**整篇反覆出現**（每幾頁出現一次）；正常 heading 通常**只出現一次**
- 履歷 / 簡報 / 學術 paper / 白皮書中重複 ≥ 3 次的 heading 幾乎都是浮水印
- 例外（如書本「References」章節結尾重複）：書本通常只章末出現 1 次、不會 ≥ 3
- 閾值改變只需 1 行 env override
- 留 C（自動 + override）給 RAG-7c 之後

### 2.2 偵測規則（A 方案具體化）

```
規則：
1. 統計整篇 .md 內每個 heading line（^#+\s+.+）出現的「次數」
2. 次數 ≥ N（預設 3）的 heading line → 視為浮水印
3. 移除所有這些 heading 行（保留其他行）
4. 不動正文（plain text 內重複字串不算 heading、不刪）

settings 加入 env：
WATERMARK_HEADING_THRESHOLD = int(os.getenv("WATERMARK_HEADING_THRESHOLD", "3"))
```

### 2.3 邊界處理

- **大小寫**：規則用 `heading_line_stripped.casefold()` 比對（避免大小寫變體被當不同 heading）。
- **# 數量**：同 heading 內容、不同 `#` 數量算同一筆嗎？建議**算同一筆**——浮水印 OCR 出來常 `#` 數量不一（XDeHunt 出現 `# XDeHunt` / `### XDeHunt` 等變體）。比對時 strip `#` 後再 casefold。
- **保留標題**：若 paper title 是「DeHunt CTO Tzung-Yuan Lee」、整份文件 user query 已知就是它——這種「整篇就 1-2 次」的 heading 不會觸發閾值、不會誤殺。
- **日誌**：移除時 `logger.info` 記錄被移除的 heading 字串 + 次數，便於 baron 觀察 / 調整閾值。

### 2.4 偽碼

```python
# md_cleaner.py 加 helper（或 inline 進 clean()）
def _detect_watermark_headings(lines, threshold=3):
    """偵測重複 heading 行（≥ threshold 次）= 浮水印候選。
    回傳 set of normalized heading text。"""
    from collections import Counter
    counter = Counter()
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('#'):
            continue
        # strip # 與空白、casefold
        norm = stripped.lstrip('#').strip().casefold()
        if norm:
            counter[norm] += 1
    return {h for h, n in counter.items() if n >= threshold}

# clean() 內加：
def clean(self, markdown_path):
    text = markdown_path.read_text(...)
    lines = text.split('\n')

    # 既有圖表數字行清理（不動）
    # ...

    # 新增：浮水印 heading 清理
    from settings import WATERMARK_HEADING_THRESHOLD
    watermarks = _detect_watermark_headings(lines, threshold=WATERMARK_HEADING_THRESHOLD)
    if watermarks:
        cleaned = []
        for line in cleaned_lines_from_step1:
            stripped = line.strip()
            if stripped.startswith('#'):
                norm = stripped.lstrip('#').strip().casefold()
                if norm in watermarks:
                    self.logger.info(f"移除浮水印 heading: {repr(stripped)}")
                    continue
            cleaned.append(line)
        cleaned_lines_from_step1 = cleaned
    # ... write back ...
```

### 2.5 settings 加常數

```python
# settings.py
# Phase 4.7d RAG-7a：浮水印偵測閾值（整篇出現 ≥ N 次的 heading 視為浮水印）
WATERMARK_HEADING_THRESHOLD = int(os.getenv("WATERMARK_HEADING_THRESHOLD", "3"))
```

---

## 3. B-2 resume 專用 prompt 設計

### 3.1 新建 `prompt/doc/heading_fix_resume.txt`

草案：
```
以下是一份履歷（resume / CV）Markdown 的所有標題行（格式：行號: 標題內容）：

{headings}

請根據履歷的結構邏輯，判斷每個標題應該使用幾個 # 符號。

層級規則：
- 履歷主標題（候選人姓名 / Resume / CV）用 #（一個）
- 頂層章節用 ##：Working Experience、Education、Skills、Projects、
  Certifications、Honors、Publications、Patents、Languages、Summary 等
- 每段工作經歷的公司 / 每個學位 / 每個 project 用 ###（**平行條目都同層**）
- 工作經歷 / project 內的細項標題（如「Job Responsibilities」/「Key Achievements」）用 ####

**關鍵注意**：
- 多家公司是「平行」的工作經歷、**不**要把後出現的公司判為前面公司的子節
- 多個學位 / 多個 project 同理
- 即使前後條目有時序關係（2020-2023 / 2018-2020）、仍是平行 ###
- 不要因為內容長度差異把短的判定為「子節」

只輸出 JSON，key 為行號（數字），value 為 # 數量（1-4）：
{"行號": 數量, ...}
```

### 3.2 改 `processor/doc_analyzer.py`

```python
# === doc_type-registry ===
HEADING_FIX_PROMPTS = {
    'academic':  'prompt/doc/heading_fix_academic.txt',
    'book':      'prompt/doc/heading_fix_book.txt',
    'technical': 'prompt/doc/heading_fix_technical.txt',
    'slides':    'prompt/doc/heading_fix_slides.txt',
    'web':       'prompt/doc/heading_fix_web.txt',
    'news':      'prompt/doc/heading_fix_news.txt',
    'resume':    'prompt/doc/heading_fix_resume.txt',  # 7b：專用 prompt
}
```

`STRUCTURE_PROMPTS['resume']` **暫不動**（留下次或 7b'），保留 `'prompt/doc/structure_academic.txt'` reuse 標記：
```python
'resume': 'prompt/doc/structure_academic.txt',  # Phase 1 reuse academic; structure 對 RAG chunk 影響小、留下次
```

理由：
- `structure` sidecar 給 md_processor 抽 `authors_info` 用（每行 line range）—— 履歷的 `authors_info` 概念跟學術 paper 不同（履歷頭部是聯絡資訊、不是論文作者）；但這條 sidecar 對 RAG chunk 切割影響小（md_processor.parse 在 build_hierarchy 階段只看 `heading_level`、不看 sidecar）
- 同 commit 兩個 prompt 一起改、改動範圍變大、回歸風險也變大
- 等 7b 落地後驗證、若 baron 認為 structure 也要改、再做 7b'

### 3.3 verify

```bash
venv/bin/python tools/check_doc_type_registry.py   # exit 0
# 確認新 prompt 檔存在、HEADING_FIX_PROMPTS dict 各 key 對齊 valid_types
```

---

## 4. commit 拆分

### Commit 7a：浮水印黑名單清理（純自動偵測）

**範圍**：
- 改 `processor/md_cleaner.py`：加 `_detect_watermark_headings` helper + `clean()` 內串接
- 改 `settings.py`：加 `WATERMARK_HEADING_THRESHOLD`
- 新增 `tests/test_md_cleaner.py`（新檔；既有無 md_cleaner 測試）

**工時**：30-60 分（含 fixture 寫法 + 測試）

**測試**：
- fixture 1：3 處 `# XDeHunt` + 正常 heading「Working Experience」（1 次）→ 應移除 XDeHunt、保留 Working Experience
- fixture 2：閾值 2 / 4 邊界（恰好 = N、N-1、N+1）
- fixture 3：大小寫變體 `# XDeHunt` / `### XDeHunt` / `#  xDeHunt` → 都算同一個浮水印
- fixture 4：正常 heading 純文字行非 `#` 開頭 → 不受影響

### Commit 7b：resume 專用 heading_fix prompt

**範圍**：
- 新增 `prompt/doc/heading_fix_resume.txt`（§3.1 草案）
- 改 `processor/doc_analyzer.py:22`：`HEADING_FIX_PROMPTS['resume']` 指向新 prompt（移除 `# Phase 1 reuse academic` 註解）
- `STRUCTURE_PROMPTS['resume']` **不動**

**工時**：30-60 分（含 prompt 寫法 + tools/check_doc_type_registry.py 驗證 + sample test）

**測試**：
- `tools/check_doc_type_registry.py` exit 0
- 既有 7 個 doc_type prompt 檔存在性檢查 pass
- 整合測試（手動）：上傳新履歷、看 logs/pipeline.log 內 heading_fix 結果

### 順序

**7a 先 7b 後**。理由：
- 浮水印清掉後、prompt 看到的 markdown 才乾淨、LLM 判定才準
- 若 prompt 先、浮水印 heading 仍會被 LLM 看到、結果仍不對
- 兩個 commit 都對「新上傳 resume」生效；既有 paper 需 RAG-2 backfill 才能套

---

## 5. 風險評估

| Commit | 風險 | 緩解 |
|---|---|---|
| **7a** | 🟡 中：閾值設太低（N=2）可能誤殺正常重複 heading（如書本章末「References」） | 預設 N=3、env override 可隨時放寬；首版實測 DeHunt + 2-3 份正常履歷 / paper、觀察 log 不誤殺 |
| **7a** | 🟢 低：md_cleaner soft fail 已有 try/except；新邏輯失敗也不中斷 pipeline | 既有架構 |
| **7a** | 🟢 低：對 slides 不跑（pipeline_core L539 已 `if doc_type != 'slides'`） | 既有架構 |
| **7b** | 🟢 低：只動 resume dict 一條 entry；其他 doc_type 不受影響 | grep `HEADING_FIX_PROMPTS` 確認 |
| **7b** | 🟡 中：新 prompt 對 LLM 引導效果需實測；可能對「非標準履歷」（如混合 portfolio）仍誤判 | sample test 2-3 份不同類型履歷；首版以「平行 H3」為核心、後續迭代 |
| **跨 commit** | 🟢 低：兩個 commit 都對既有 paper **不**自動重生 vector store；新上傳生效 | 與 15-1 / 15-2 一致 |
| **跨 commit** | 🟢 低：7a 7b 都不改 schema、不動 DB、不動前端 | — |

---

## 6. 測試規劃

### 6.1 既有測試影響

```bash
$ ls tests/ | grep -i "cleaner\|doc_analyzer\|md_cleaner"
（無相關測試）
```

- `pytest tests/ -q` 當前 **123 passed 3 skipped**
- 7a + 7b 都不動既有測試對象、預期無回歸

### 6.2 新增測試

**7a：`tests/test_md_cleaner.py`**（新檔）
- `test_existing_numeric_line_removed`（既有邏輯回歸驗證）
- `test_watermark_heading_removed_threshold_3`：3 次 `# X` → 移除；2 次保留
- `test_watermark_case_insensitive`：`# XDeHunt` / `### xDeHunt` 算同一個
- `test_watermark_different_hash_count_same`：`# X` / `### X` 算同一個（normalize 後）
- `test_normal_heading_not_removed`：「Working Experience」(1 次) 不受影響
- `test_threshold_env_override`：env `WATERMARK_HEADING_THRESHOLD=2` 生效

**7b：純整合測試**（單元測試難度高、LLM 行為非確定）
- `tools/check_doc_type_registry.py` exit 0
- 手動上傳 DeHunt 履歷 + 觀察 logs/pipeline.log heading_fix 結果

### 6.3 端到端驗證（給 baron）

**7a 落地後**：
1. 上傳新履歷（含浮水印的測試 PDF）→ 看 logs 內 `[md_cleaner] 移除浮水印 heading:` 出現次數
2. 看 `output/{owner}/{paper}/{paper_uuid}.md` 確認浮水印 heading 已清

**7b 落地後**：
1. 上傳新履歷 → analyze stage 跑完
2. 看 `output/{owner}/{paper}/{paper_uuid}_structured.json`：
   - `Working Experience` 是 `level=2`（H2）
   - `children` 內各家公司都是 `level=3`（H3）
   - **無**「TARGETEK / ITRI 變 H2 與 Working Experience 平行」
   - **無**「FOCALTECH 被塞進 TARGETEK 的 children」

**7a + 7b 串聯**：
1. 對 DeHunt 履歷重新跑 pipeline（依賴 RAG-2 backfill CLI 或 user 重新上傳）
2. 看 `_structured.json` 結構正確 + chunks `_rag.md` 切割正確
3. AI chat 對 VIEWTRIX / FOCALTECH 等公司問題能精準引用

---

## 7. open questions（待 baron 決策）

### Q1 — 偵測閾值預設值
- 推薦：**N=3**（整篇出現 3 次以上 → 浮水印）
- 替代：N=4（更保守）/ N=2（更激進但風險高）
- baron 確認預設值；env 隨時可調

### Q2 — 是否本 commit 加 manual override（per-paper / global blacklist list）？
- 推薦：**不加**（純自動偵測）
- 替代：保留設計位置（如 `prompt/watermark_blacklist.txt`）但本 commit 不啟用
- 若 baron 認為某些浮水印自動偵測不到（如只出現 2 次但確實是浮水印）→ 後續 RAG-7c 加 manual override

### Q3 — `structure_resume.txt` 是否本次同 commit？
- 推薦：**不**（留下次或 7b'）
- 替代：同 commit 一起改、影響範圍變大
- 理由：structure sidecar 對 RAG chunk 切割影響小、authors_info 對履歷意義也低

### Q4 — B-1 / B-2 是否同 commit（拆 7a + 7b 還是合 1 個）？
- 推薦：**拆 7a + 7b**（功能正交、測試獨立、回退方便）
- 替代：合 1 個（commit 較少、但 review / 回退單位變大）

### Q5 — DeHunt 履歷既有資料是否要重生？
- 推薦：依 **RAG-2 backfill CLI** 落地後再處理；user 也可重新上傳
- 替代：手動跑 `pipeline_core.process(stages=['pdf2md', 'analyze', 'md2json', 'tiling', 'translate', 'image_caption', 'md_restore', 'extra_info', 'rag'])` per-paper（既有支援 stage 列表）

### Q6 — 浮水印偵測時機：pdf2md 後 vs analyze 前
- **已決**（§1.3）：在 md_cleaner 內、pdf2md 之後 analyze 之前。slides 跳過（既有架構）。
- baron 確認此時機 OK 即可

### Q7 — `# 數量 normalize`：要不要保留浮水印 heading 但降為 plain text？
- 推薦：**整行移除**（簡單、明確）
- 替代：把 `# XDeHunt` 改成 `XDeHunt`（保留文字、移 `#`）—— LLM 看到的 heading 列表會乾淨、但正文多了無意義字串
- 整行移除更乾淨

---

## 8. 不可做（已遵守）

- ❌ 業務檔（`processor/*` / `pipeline_core` / `prompt/doc/*` / `settings.py`）：未動
- ❌ 新建業務檔（prompt 檔 / fixture 等）：未動
- ❌ commit / push：未動
- ✅ grep / cat / 只讀命令：已執行
- ✅ 本報告 `.md`：唯一新增檔

---

## 狀態

**Plan 完成、等 baron 確認 §7 open questions（特別 Q1 閾值 / Q2 是否 manual override / Q3 structure_resume 何時做）後再進 Execute 階段**。

執行階段建議：
1. baron 回答 open questions
2. **Commit 7a**（30-60 分、低-中風險、自動偵測閾值 = 預設 3）
3. **Commit 7b**（30-60 分、低風險、新 prompt）
4. baron 端整合測試（DeHunt 履歷重新上傳 or RAG-2 backfill）
5. 若實測仍有 case 不對（如 FOCALTECH 因 plain text 被併入 TARGETEK content）→ RAG-7c 評估 `md_heading_inferrer` 後處理（允許新增 heading）
