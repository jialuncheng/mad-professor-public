# 2026-05-20 新增 resume doc_type 工程影響盤點 + prompt 內容提案

純讀分析 + prompt 內容設計，**未動任何檔案、未 commit**。

依 baron 5 項決策（resume 進 doc_type / title 由 LLM 決定 / 走翻譯 /
跳 extra_info / RAG 仍走）對 7+2 層動點完整盤點，並設計 2 個新 prompt
草稿（heading_fix_resume.txt / structure_resume.txt）。

---

## 任務 A：完整工程影響盤點

### 層 1：`web_server.py:481` valid_types
```python
valid_types = ['academic', 'book', 'technical', 'slides', 'web', 'news']
```
→ 加 `'resume'`：
```python
valid_types = ['academic', 'book', 'technical', 'slides', 'web', 'news', 'resume']
```

### 層 2：前端 `static/index.html:1574` `DOC_TYPES`（prototype dropdown）
原 6 條（academic/book/technical/slides/web/news），加：
```js
['resume', '履歷']
```
排序建議（見 D-1，待 baron 拍板）：
- A. 排尾（最簡單，與後端 valid_types 同序）
- B. 排「academic」後（學術類聚集）
- C. 排「news」前（人物相關文件聚集）
- **推薦 A**（排尾）—與後端 valid_types 同序、認知最低成本。

### 層 3：前端 `static/index.html:2319` `DOC_TYPE_LABELS`
```js
const DOC_TYPE_LABELS = {
  academic: '學術論文', book: '書籍', technical: '技術文件',
  slides: '簡報', web: '網頁存檔', news: '新聞文章',
};
```
→ 加 `resume: '履歷'`。

### 層 4：`processor/doc_analyzer.py:14–19` `HEADING_FIX_PROMPTS`
加 1 行：
```python
'resume': 'prompt/doc/heading_fix_resume.txt',
```

### 層 5：`processor/doc_analyzer.py:23–28` `STRUCTURE_PROMPTS`
加 1 行：
```python
'resume': 'prompt/doc/structure_resume.txt',
```

### 層 6：`processor/translate_processor.py:222–230` `style_hints`
加 1 行（草稿，見 D-2）：
```python
'resume': '文件為個人履歷（CV），請使用正式商務中文，職稱、公司名、技術名詞保留原文。',
```

### 層 7：`pipeline_core.py:598` extra_info 分流
```python
if doc_type in ('news', 'web', 'slides'):
```
→ 加 `'resume'`：
```python
if doc_type in ('news', 'web', 'slides', 'resume'):
```
與 baron 決策 4 一致：履歷走 `generate_document_summary` 而非
`extra_info_processor.process`（不做 question/formula/graph 等學術衍生）。

### 層 8：新增 `prompt/doc/heading_fix_resume.txt`（草稿見 B-1）

### 層 9：新增 `prompt/doc/structure_resume.txt`（草稿見 B-2）

### 工程量總計（不含 prompt 設計）
| 層 | 改動 | 行數 |
|---|---|---|
| 1 valid_types | +1 token | 1 行內 |
| 2 DOC_TYPES | +1 entry | 1 行 |
| 3 DOC_TYPE_LABELS | +1 entry | 1 行 |
| 4 HEADING_FIX_PROMPTS | +1 entry | 1 行 |
| 5 STRUCTURE_PROMPTS | +1 entry | 1 行 |
| 6 style_hints | +1 entry | 1 行 |
| 7 extra_info skip | +1 token | 1 行內 |
| 8 heading_fix_resume.txt | 新檔 | ~15 行 |
| 9 structure_resume.txt | 新檔 | ~25 行 |
| 7 layer code 總計 | | **7 行 .py / .html 改動**（+2 新 prompt 檔）|

---

## 任務 B：新 prompt 內容草稿

### B-1：`prompt/doc/heading_fix_resume.txt`（完整草稿）

```
以下是一份履歷 Markdown 的所有標題行（格式：行號: 標題內容）：

{headings}

請根據履歷的結構邏輯，判斷每個標題應該使用幾個 # 符號。

規則：
- 候選人姓名用 #（一個）：作為履歷主標題；通常只有一個
- 主要區段用 ##（兩個）：Summary、Objective、Work Experience、Working Experience、Professional Experience、Education、Skills、Technical Skills、Certifications、Projects、Publications、Languages、Awards、References、Volunteer、Interests，以及對應中文「自我介紹／工作經歷／學歷／技能／證照／專案／著作／語言／獎項／推薦人／志工經歷／興趣」等
- 工作經歷項目用 ###（三個）：公司名 + 職稱（如「Novatek - Senior Director」、「Acme Corp – Software Engineer (2020–2024)」），或學歷項目（學校 + 學位）、專案名稱、證照名稱
- 細項用 ####（四個）：職責／成就／參與專案的子分項；多層巢狀的細節

注意：履歷結構通常扁平，候選人姓名 + 主要區段 + 經歷條目三層為主，不要過度深化。允許單一 H1（候選人姓名）；若同層出現多個並列大標題，依語義保持同階。

只輸出 JSON，key 為行號（數字），value 為 # 數量（1-4）：
{"行號": 數量, ...}
```

設計重點：
- 中英雙語區段名舉例（履歷常見英文 + 中文標籤）
- 強調「結構扁平」「不要過度深化」（同 news/slides 提示）
- 允許「單一 H1」（履歷只有候選人姓名一個主標題）
- 工作經歷項目（公司+職稱）= H3、細項（職責/成就）= H4

### B-2：`prompt/doc/structure_resume.txt`（完整草稿）

```
以下是一份履歷的前段內容（格式：原始行號: 內容，空行已省略但行號保留）：

{content}

請分析這份履歷的前段結構，回傳 JSON：

{
  "structure": [
    {"start": 起始行號, "end": 結束行號, "type": "類型"}
  ]
}

type 選項：
- name：候選人姓名（履歷主標題；通常為文件最頂端的 H1）
- contact：聯絡方式（email、電話、地址、LinkedIn、GitHub、個人網站等）
- summary：候選人摘要、自我介紹、Professional Summary、Objective、Profile
- section_heading：各主要區段標題行（## 開頭，如 Work Experience、Education、Skills 等）
- experience：工作經歷條目（公司 + 職稱 + 期間 + 內容）
- education：學歷條目（學校 + 學位 + 期間）
- skills：技能列表（技術技能、語言、軟技能等）
- other：其他無法分類的內容（如 Hobbies、Personal、引言佳句、版面裝飾文字）

注意：履歷沒有 abstract、references、equations、figures。第一頁通常依序為「候選人姓名 → 聯絡方式 → 摘要 → 工作經歷區段標題 → 第一個經歷條目」。

只輸出 JSON，不要任何解釋。
```

設計重點：
- type 列表涵蓋履歷專屬概念（name / contact / summary / experience / education / skills）
- **沒有 abstract / references / publication_info**（與 academic 不同）
- 「注意」段點明履歷的第一頁排版常規（給 LLM 結構參考）
- 不加「title」type（按 B-3 提案：title 從 name 抽出）

### B-3：title 由 LLM 自己決定 — 提案

選項對比：
| 方案 | 來源 | 優點 | 缺點 |
|---|---|---|---|
| **A.（推薦）title = name** | structure_resume.txt 的 `name` type | 直觀、姓名即文件最直接識別、與 academic「title=論文主標題」對稱 | 看到「David Hunt」不知是履歷還是其他文件；可用 doc_type 標籤輔助 |
| B. structure 加 `title` type，讓 LLM 自由命名 | 新增 type | 可組合「姓名 + 目標職位」更具識別性 | LLM 自由度增加可能不穩；違反 baron「不寫死候選人姓名/職位/檔名」（自由型 LLM 仍可能寫死 → 不違反原則但有規範問題） |
| C. title = name + 第一個 section_heading 拼接 | structure 後處理 | 自動具識別性 | code 端後處理增加複雜度，違反「LLM 自己決定」精神 |

**推薦 A**：`title` 直接 = `name` type 的內容。
- 對齊 academic（title = `title` type）的處理模式
- 不增加 type 數量、不增加後處理
- 識別性靠 doc_type 標籤（`履歷`）+ 姓名一起呈現
- 若 baron 後續希望「姓名 + 職位」，將 structure 的 `name` 範圍擴大到含
  目標職位即可（LLM 已會把姓名下面的「Director, IC Design」一起圈入 name
  的 end），仍由 LLM 決定。

baron 決策 2「title 由 LLM 自己決定」對應實作 = LLM 在 structure 中決定
`name` 涵蓋的行號範圍 → md_processor 依此抽 title。**B-1/B-2 草稿即此設計。**

---

## 任務 C：與既有架構的相容性檢查

### C-1：`md_processor.parse()` 的 `collecting_authors` 邏輯
**現況**：`processor/md_processor.py:263` 定義
```python
SLIDES_DOC_TYPES = ('slides',)
collecting_authors = doc_type not in SLIDES_DOC_TYPES
```
academic 走 `collecting_authors=True`（H1 後 → 第一 H2 前的內容當 authors_info）；
slides 走 `False`（前一輪修正：簡報第一頁全進 sections）。

**履歷結構觀察**（baron 提供 DeHunt 範例 + 一般履歷常規）：
- 結構為 `# 候選人姓名` 後緊接 `## Candidate Summary` 或 `## Summary`，
  **中間可能有 contact info（email/phone/LinkedIn）**
- 若 collecting_authors=True：H1（姓名）後到 H2（Summary）前的 contact
  info 會被吞進 `authors_info`（**正是 authors_info 的學術定義延伸**——
  作者 vs 候選人，concept 對偶）
- 若 collecting_authors=False（同 slides）：contact info 會被視為第一個
  「孤立 section」（無標題），雖然能保留並翻譯，但語意上不對。

**提案**：履歷**保留 `collecting_authors=True`**（與 academic 同），讓
contact info 自然進 `authors_info` 欄位。**不擴充 SLIDES_DOC_TYPES**。
- 等同於把履歷的「候選人姓名 + 聯絡方式」對應到學術論文的「論文標題 +
  作者群」結構，semantic 對偶、實作零改。
- DeHunt 風險：若 contact 段是「（一行 email）（一行 LinkedIn）→ 立即
  `## Candidate Summary`」，contact 進 authors_info；若 contact 段缺、
  H1 後直接接 `## Candidate Summary`，authors_info 為空（不影響）。
- 真正風險場景：H1 姓名後**不是 H2 而是內文**（如 `# John Doe\nIC 設計
  資深經理\n（很長一段自介文字）\n## Skills`）——此時整個自介會被吞
  進 authors_info、翻譯被跳過。

**結論建議**：暫不擴充 SLIDES_DOC_TYPES；觀察實測。若 baron 後續發現
履歷自介被吞進 authors_info 不翻譯，**再**擴充為
`SLIDES_DOC_TYPES = ('slides', 'resume')`（同 slides 處理）。詳見 D-3。

### C-2：extra_info_processor 對「無 abstract」的處理
履歷無 abstract，與 news/web/slides 同。pipeline_core.py:598 分流：
- news/web/slides/**resume** → `generate_document_summary`（單純做整篇 summary）
- 其他 → `process`（含 question/formula/graph_question 等學術衍生）

加入 resume 到 skip 名單後，extra_info 不會對履歷產生：
- 章節級 questions（履歷的 Skills/Experience 不適合生成「為什麼這樣設計」這類學術問題）
- formula analysis（履歷無公式）
- graph questions（履歷無圖表）

**只跑** `generate_document_summary`：單純把整份履歷文字 + domain
（如「半導體 IC 設計資深經理人履歷」）給 LLM 生成 1 段 summary，存進
paper_data，供 RAG / macro_retrieval 使用。**架構無破壞、零特殊處理**。

### C-3：rag_processor 履歷的 chunks 切分
**關鍵發現**（`processor/rag_processor.py:93–94`）：
```python
headers_to_split_on = [("#", "Header")]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
```
**只依 H1 切 chunks**。對履歷：
- 履歷的 H1 = 候選人姓名（**通常只有 1 個**）→ **整份履歷 = 1 個 chunk**
- 全文 embedding 一次、retrieve 永遠回整份內容
- baron 決策 5「簡短履歷全 chunks 被 retrieve 沒差，不破壞架構」← 對應此

**風險評估**：
- 履歷通常 1–3 頁，全文裝進 1 chunk 後 token 數 < 2000，embedding/retrieve
  完全 OK
- 若履歷很長（> 5 頁、含多個 project 細節），1 chunk 會超 embedding model
  輸入上限（gemini-embedding 768 dim 上限 2048 tokens）→ 內容截斷風險
- 但 `_filter_sections`（line 128–134）只濾 abstract/references，履歷
  兩者皆無 → 不會誤濾任何 section
- 既有 8 篇學術論文採同切法，運作正常 → 履歷 ≤ 學術論文長度，安全餘裕大

**結論**：完全沿用既有切法、零改動。若實際發現 > 5 頁長履歷有 token
超限，再考慮 fallback 切分（如 H2-split for resume），**目前不必動**。

---

## 任務 D：暴露的決策點（待 baron 拍板）

### D-1：前端 dropdown 排序位置
| 選項 | 排序 | 認知/工程成本 |
|---|---|---|
| **A.（推薦）** | …news, **resume**（排尾，與後端 valid_types 同序）| 最低 |
| B. | …academic, **resume**, book…（學術類聚集）| 低 |
| C. | …web, news, **resume**（人物相關文件聚集）| 中 |

### D-2：translate `style_hints` 描述
| 選項 | 文案 | 風險 |
|---|---|---|
| A. | 「文件為履歷」 | 太短，LLM 可能風格偏隨意 |
| **B.（推薦）** | 「文件為個人履歷（CV），請使用正式商務中文，職稱、公司名、技術名詞保留原文。」 | 與其他 hint 風格一致，明確指引保留專有名詞 |
| C. | 「文件為個人履歷，請使用客觀、簡潔的職場敘事，避免過度修辭。」 | 偏 narrative 風格，可能弱化技能列表簡潔性 |

### D-3：履歷是否擴充 `SLIDES_DOC_TYPES` 至 `(slides, resume)`？
| 選項 | 結果 | 適用場景 |
|---|---|---|
| **A.（推薦）保持 `('slides',)`** | 履歷走 `collecting_authors=True`，H1 後到 H2 前進 authors_info | 履歷有 contact info 段（標準格式） |
| B. 擴充 | 履歷走 False，第一段內容進 orphan section | 履歷 H1 後直接接內文（非標準格式） |

→ 推薦 A（先觀察）；實測若發現自介被吞 authors_info 不翻譯，再切 B。

### D-4：structure_resume.txt 是否加 `title` type 讓 LLM 決定？
**推薦不加**（沿用 B-3 推薦 A）：title 直接從 `name` 抽。
若 baron 改要 B（加 title type），structure 需 +1 type、md_processor 需
判讀新 type、且 title 與 name 範圍重疊處理會複雜。

### D-5：heading_fix_resume.txt 層級規則嚴格度
| 選項 | 規則 | 影響 |
|---|---|---|
| 嚴格 | 強制 H1 唯一 | 多名候選人共享履歷（罕見）會失敗 |
| **寬鬆（推薦）** | 「通常只有一個 H1」+ 「不要過度深化」軟性指引 | 與 news/slides 風格一致；LLM 自適應 |

B-1 草稿採寬鬆。

### D-6：是否新增 `is_resume_pdf()` 偵測讓 `suggested_doc_type` 自動建議
**非必要**。`is_slides_pdf` 用 PyMuPDF 圖文比例啟發；履歷沒有同樣可靠的
圖形特徵。可能信號：
- 第一頁有 email/phone regex 命中
- 第一頁有「Experience/Education/Skills」關鍵字命中
- 第一頁 H1 為「人名」格式（兩個英文 word capitalized）

但這些都不夠可靠（學術論文也有 email、技術文件也有 Experience 章節）。
**推薦：暫不做**。使用者開啟 dropdown 即可選；前端可加排序讓「履歷」
易找。後續若履歷量大可再評估 `is_resume_pdf()`。

---

## 任務 E：執行順序推薦

### Phase 1（最小可用，**強烈推薦先做**）
**7 行 code 改動，reuse academic prompt 為 resume**：
1. 動 web_server.py / static/index.html(×2) / doc_analyzer.py(×2) /
   translate_processor.py / pipeline_core.py — 共 7 處
2. **暫時** `HEADING_FIX_PROMPTS['resume'] = 'prompt/doc/heading_fix_academic.txt'`、
   `STRUCTURE_PROMPTS['resume'] = 'prompt/doc/structure_academic.txt'`
   （reuse 不新建 prompt 檔；academic prompt 的「論文」措辭對履歷不貼，
   但**結構**——title/authors/section_heading 等 type——對履歷的「name/
   contact/section_heading」可勉強映射，至少跑得起來）
3. **驗證**：上傳 DeHunt 履歷選「履歷」→ pipeline 跑完、AI 對話可引用內容
4. 工程量：**小（30–60 分）**

### Phase 2（履歷專用 prompt，**Phase 1 驗證 OK 後做**）
**新增 2 個 prompt 檔**（B-1 / B-2 草稿）：
1. `prompt/doc/heading_fix_resume.txt`（B-1，~15 行）
2. `prompt/doc/structure_resume.txt`（B-2，~25 行）
3. 改 doc_analyzer.py 兩個 dict 的 'resume' 值指向新檔
4. **驗證**：對 DeHunt + 其他履歷 A/B 比對 academic vs resume prompt
   生成的 structure.json、final_zh.md
5. 工程量：**中（60–120 分）**——主要是寫 prompt、實測調 prompt 措辭

### 合做 vs 分做？
**推薦分做（Phase 1 → 驗證 → Phase 2）**：
- Phase 1 後即可端到端使用，baron 可實測決定 Phase 2 prompt 寫法
- Phase 2 的 prompt 設計依賴實測樣本（看 academic prompt 套在履歷上的
  失敗模式）才能精準下手；無實測直接寫 prompt 容易過度設計
- 兩 Phase 不互相阻塞、任一單獨 commit 都安全

如果 baron 想一次到位：合做也可（Phase 1 + Phase 2 同一 commit），但
建議**最少把 Phase 1 與 Phase 2 拆兩 commit**便於 revert/比對。

---

## 任務 A 完整改動清單摘要（給 commit message 用）

```
feat(doc_type): 新增 resume 文件類型（Phase 1）

七層改動：
- web_server.py:481  valid_types 加 'resume'
- static/index.html  DOC_TYPES 加 ['resume', '履歷']（line 1574）
- static/index.html  DOC_TYPE_LABELS 加 resume: '履歷'（line 2319）
- processor/doc_analyzer.py:14-19  HEADING_FIX_PROMPTS 加 resume
- processor/doc_analyzer.py:23-28  STRUCTURE_PROMPTS 加 resume
- processor/translate_processor.py:223-230  style_hints 加 resume
- pipeline_core.py:598  extra_info skip 加 'resume'

doc_analyzer 兩 dict 暫指向 academic prompt（Phase 1 reuse），
Phase 2 再換成專用 prompt。

md_processor.SLIDES_DOC_TYPES 保持 ('slides',)，履歷走 academic 同
collecting_authors=True 路徑（H1 後 → 第一 H2 前內容進 authors_info，
對應履歷的 contact info 區段）。

rag_processor MarkdownHeaderTextSplitter 沿用既有 H1 切法：履歷通常
單一 H1 → 全文 = 1 chunk，retrieve 永遠回全內容（baron 決策 5）。

extra_info_processor 對 resume 走 generate_document_summary（與
news/web/slides 同），不做 questions/formula/graph 學術衍生。

translate 仍跑（baron 決策 3：重複翻譯可接受）。
```

---

## 任務 F：未動清單 / 限制

- 純讀分析 + prompt 草稿；**未動任何檔案**
- 未 git add / commit
- 未 stub / mock
- prompt 草稿（B-1/B-2）僅文字提案，**未寫入 prompt/doc/**
- 7 層 code 改動皆**未實作**（連 Phase 1 也未動），等 baron 確認本提案再執行
