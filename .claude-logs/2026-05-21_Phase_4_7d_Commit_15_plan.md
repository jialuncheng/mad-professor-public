# Phase 4.7d Commit 15 — Plan：RAG chunk 優化 + 引用源頭強化

> 純分析報告、零檔案改動（除本 .md）。

## TL;DR

- **問題**：短條列文件（履歷 / 簡報 / 新聞）RAG 效果差；AI 答覆沒明確引用源頭。
- **5 個根因**（§2）：空殼 summary chunk、chunk key 路徑稀釋 embedding 信號、結構脈絡（doc_type / section_title）沒進 chunk 內容、同 section 多 text items 各自一 chunk、prompt 沒要求 LLM 引用源頭。
- **解法**：拆 **15-1（chunk 內容優化、純改 rag_processor）**+ **15-2（引用源頭、改 retriever + chat 但不動 chunk 結構）**。15-1 對既有 paper 不重生則不生效；15-2 立即生效。
- **15-1 共 4 個子改動**：跳過空殼 / chunk 內容前綴上下文 / key 路徑簡化 / 同 section 條件式合併（後者僅履歷/簡報/新聞）。
- **15-2 共 2 個子改動**：retrieve_with_context 加 paper_title 標頭 + character prompt 加「請標註引用源頭」instruction。
- **score 閾值 0.22 留意**：chunk 結構大改後分布會變、需重新校準（open question #4）。

---

## 1. 現況盤點

### 1.1 rag_processor.py：chunk 生成鏈

**主流程**（L19-69 `process()`）→ 重構 tree → 生成 markdown → MarkdownHeaderTextSplitter 切 → FAISS 建 vector store。

**`_generate_markdown`（L292-323）**：遍歷 `tree_structure["key_map"]`、對每個 key 取對應 node、呼叫 `_generate_md_content(node, key)`、結果非 None 才寫入 .md。markdown 各區塊以 `# {key}` 為 H1 標頭分隔——這是 splitter 的切點。

**`_generate_md_content(node, key)`（L325-393）**：
```python
md_content = f"# {key}\n"           # 永遠以 key 路徑當 H1
if "summary" in node and "/section" in key:
    md_content += f"{node.get('summary', '')}"  # ⚠ 空 summary 仍返回
    return md_content
if node.get("type") == "text":
    if questions or content:        # 空白雙缺才不返回
        md_content += f"{questions}\n{content}"
        return md_content
# ... 同樣模式 figure / table / formula / section dict
# 全部不匹配 → 隱式 return None
```

**`_generate_key_map`（L219-253）** 為每個 leaf 生成 key 字串，格式：
```
{paper_title}/{section_path}/section                     # section node
{paper_title}/{section_path}/section/{i}/{type}          # content leaf
{paper_title}/{section_path}/{child_section_path}/...    # nested children
```

**範例**（推估，DeHunt 履歷）：
- `DeHunt Resume/Working Experience/section`（section 摘要）
- `DeHunt Resume/Working Experience/section/0/text`（第 0 個 text item）
- `DeHunt Resume/Working Experience/VIEWTRIX/section`（子 section 摘要）
- `DeHunt Resume/Working Experience/VIEWTRIX/section/0/text`

每個 key 都當 `# {key}` 寫入 markdown、各自一個 chunk。

### 1.2 `_create_vector_store`（L70-110）

```python
headers_to_split_on = [("#", "Header")]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
docs = md_splitter.split_text(content)
# FAISS.from_documents（MAX_INNER_PRODUCT）
```

切 H1 → 每個 H1 一個 chunk、`doc.metadata['Header']` = 該 H1 內容（也就是 key 路徑）。

### 1.3 rag_retriever.py：retrieve_with_context

**簽名**：`retrieve_with_context(owner_id, query, paper_id, top_k=5) -> str`——回**純字串**、不是結構化 dict。

**流程**（L91-155）：
1. similarity_search_with_score top_k=5
2. score > 0.22 過濾（comment L106-109：實測 Gemini 768-dim 下相關 0.23-0.27 / 無關 0.17-0.20）
3. 用 `doc.metadata['Header']` 查 `rag_tree['key_map']` 拿 JSON path
4. 依 path 從 rag_tree 拿 node、加相鄰 formula
5. 拼字串：`"以下是論文中與您問題最相關的內容:" + "\n## {section_title}" + 內容`

**section_title 構造（`_build_section_title` L196-216）**：只到 `parent > child` 兩層；更深 children 停在父層級。沒有 paper_title。

### 1.4 AI_professor_chat：RAG 怎麼用

**`_get_rag_context`（L207-220）**：直接拿 `retrieve_with_context` 回的字串、回傳。

**`_prepare_final_messages`（L222-262）**：
```python
final_query = f"用戶問題：{query}\n\n相關文件段落:\n{context_info}"
```
RAG context 整個塞進 user message 結尾。

**system prompt**（character + explain）內**沒有「請標註引用源頭」的 instruction**。`explain_prompt` 只說「當前協助使用者理解的文件為：{title}」——告訴 LLM 是哪份文件、但沒要求引用。

### 1.5 既有測試現況

```bash
$ ls tests/ | grep -i "rag\|retriever"
（無結果）
```

**RAG 相關沒任何單元測試**——本 commit 是好機會補一些。`pytest tests/ -q` 當前 90 passed 3 skipped、無 RAG 覆蓋。

---

## 2. 5 個觀察到的問題（含證據）

### 問題 #1：空殼 summary chunk

**證據**：`_generate_md_content` L332-334：
```python
if "summary" in node and "/section" in key:
    md_content += f"{node.get('summary', '')}"
    return md_content
```
**只檢 key 存在、不檢 value**——`node['summary'] == ''` 也返回。輸出 markdown：
```
# DeHunt Resume/Working Experience/VIEWTRIX/section

```
這變成一個只有 H1 標頭、無實質內容的 chunk。MarkdownHeaderTextSplitter 切完、FAISS embed 後變成「embed 純粹一個 key 路徑」的廢 chunk。
**影響**：履歷 / 簡報 / 短文件大量沒寫 summary 的 section 都會產生這類空殼；占 retrieval candidate 額度。

### 問題 #2：chunk key 路徑稀釋 embedding 信號

**證據**：每個 chunk 的 H1 = 完整 key 路徑（如 `DeHunt Resume/Working Experience/VIEWTRIX/section/0/text`），這串路徑會被 MarkdownHeaderTextSplitter 保留進 `doc.page_content`（splitter 行為：header text + body）。
**影響**：path 字串對 query「他在 VIEWTRIX 做什麼」的 embedding signal 提供有限——`/section/0/text` 是內部結構標籤、跟 query 語意無關、卻佔 chunk 文字的相當比例（履歷 chunk 本來就短，path 反而比 content 還長）。

### 問題 #3：結構脈絡缺失（doc_type / section_title 沒進 chunk 內容）

**證據**：chunk content type 中 text 是：
```python
md_content += f"{questions}\n{content}"
```
只有 raw text。沒帶「這段來自履歷 / 來自工作經歷 / VIEWTRIX 公司」這類脈絡。
**影響**：embedding 看到的是孤立片段，相鄰 chunk 區隔不出語意；retrieval 對「VIEWTRIX 工作」這類問題的精準度差。

### 問題 #4：同 section 內 text items 各自一個 chunk

**證據**：`_generate_key_map` L237-239 為每個 content item 生 key：
```python
for j, item in enumerate(section.get("content", [])):
    content_key = f"{section_key}/{j}/{item.get('type', '')}"
```
履歷工作經歷一個 VIEWTRIX section 可能有 5 個 text item（職位、任期、職責、成就、技能）→ 5 個獨立 chunk、各自 embed。
**影響**：用戶問「VIEWTRIX 主要做什麼」可能只命中其中 1-2 個 chunk、漏掉其他重要 item。短條列尤其嚴重。

### 問題 #5：AI 答覆沒明確引用源頭

**證據**：character prompt + explain prompt grep 後**無**「引用」「source」「來源」「章節」等字。`_prepare_final_messages` 把 RAG context 標題為「相關文件段落」、但沒要求 LLM 答覆時標註。
**影響**：用戶看不到「這句話來自履歷哪個 section」、難驗證 / 難追蹤。

---

## 3. 設計方案

### Commit 15-1：RAG chunk 內容優化（純改 `rag_processor.py`）

#### A. 跳過空 chunk（解問題 #1）

```python
# _generate_md_content 內：summary section 改檢 value 非空
if "summary" in node and "/section" in key:
    summary = (node.get('summary') or '').strip()
    if not summary:
        return None   # 跳過、_generate_markdown L318 已有 if md_content: 護欄
    md_content += summary
    return md_content
```

**風險**：低、純減少無效資料。

#### B. chunk 內容前綴加上下文（解問題 #3）

每個 chunk content 開頭加一行 `Context:` 標籤、讓 embedding 拿到語意脈絡：

```python
def _generate_md_content(self, node: Dict, key: str, doc_type: str = '',
                         section_title: str = '') -> str:
    md_content = f"# {key}\n"
    # Commit 15-1：上下文前綴（解問題 #3）
    ctx_bits = []
    if doc_type:
        ctx_bits.append(doc_type)
    if section_title:
        ctx_bits.append(section_title)
    if ctx_bits:
        md_content += f"Context: {' > '.join(ctx_bits)}\n\n"
    # 既有 type 分支不動
    ...
```

caller `_generate_markdown` 需傳 doc_type（從 tree_structure 取）+ 從 key 路徑算 section_title。

**範例輸出**：
```
# DeHunt Resume/Working Experience/VIEWTRIX/section/0/text
Context: resume > Working Experience > VIEWTRIX

職位：資深 IC 設計工程師
2018-2022
...
```

**風險**：低、不破壞語意；embedding 取 chunk 全文、新增的「Context:」行對 query 是強信號（語意連結）。

#### C. key 路徑簡化（解問題 #2、可選）

key 路徑保留**完整用於 key_map 反查**，但 H1 用簡化形式：

```python
# 既有
md_content = f"# {key}\n"

# Commit 15-1（option C）：
md_content = f"# {section_title or key}\n"
# metadata['Header'] 仍是 section_title；key_map 反查改用 hash / 另一個 anchor
```

**問題**：MarkdownHeaderTextSplitter 切 H1 後、`doc.metadata['Header']` = H1 字串。若多個 chunk 共享同樣 section_title（如「Working Experience」section + 內含的 text items）會撞 key。

**修法**：仍用完整 key 但 H1 後加空行 + Context 行（B）讓 embedding 重點放後者；不簡化 key 本身。

**結論**：**C 不做、由 B 解掉 #2**——Context 行的 embedding 重要性蓋過 path noise。

#### D. 同 section 多 text items 合併（解問題 #4，條件式）

**對 doc_type ∈ {'resume', 'slides', 'news', 'web'}** 套用：合併同 section 內所有 text items 成單一 chunk。

```python
# 加 helper：is_short_doc_type
SHORT_DOC_TYPES = {'resume', 'slides', 'news', 'web'}

def _merge_section_text_chunks(self, section, doc_type) -> Optional[str]:
    if doc_type not in SHORT_DOC_TYPES:
        return None
    text_items = [i for i in section.get('content', []) if i.get('type') == 'text']
    if len(text_items) <= 1:
        return None
    combined = "\n\n".join(
        (item.get('translated_content') or item.get('content') or '').strip()
        for item in text_items if (item.get('content') or item.get('translated_content'))
    )
    return combined if combined.strip() else None
```

整合進 `_generate_markdown`：若該 section 觸發合併、跳過 per-item chunks、寫一個合併 chunk + Context 行。

**風險**：中——chunk 大小變化要驗證。學術 / 技術 / 書籍**不套用**（chunk 太大反而稀釋）。

**doc_type 從哪取**：tree_structure 沒存 doc_type；rag_processor.process() caller 需傳入（`pipeline_core._stage_rag` 取 `output_paths['_confirmed_doc_type']` 並傳給 rag_processor）。

### Commit 15-2：引用源頭強化（改 `rag_retriever` + AI prompt）

#### E. retrieve_with_context 加 paper_title 標頭

```python
# rag_retriever L132：
paper_title = rag_tree.get('translated_title') or rag_tree.get('title') or ''
result_parts = [f"以下是論文《{paper_title}》中與您問題最相關的內容:"]
```

並把 section_title 結構化擴成 `paper_title > section > child`：
```python
def _build_section_title(self, tree, path) -> str:
    # 既有 parent > child 邏輯
    # 加 paper_title 前綴
    paper = tree.get('translated_title') or tree.get('title') or ''
    return f"{paper} > {existing_title}" if paper else existing_title
```

**風險**：低、純擴充字串內容、不改 API 簽名。AI_professor_chat 不需動。

#### F. character prompt 加引用要求

`prompt/ai/ai_character_prompt.txt` 加一條 instruction：

```
3. 引用源頭（新增）
   - 若答覆內容來自文件特定段落，請明確標註來源章節
   - 格式：「根據『{section_path}』段……」
   - 多段引用時逐一標出
```

**風險**：低、純加 instruction；LLM 行為改變但不破壞既有功能。

**E 與 F 必須一起做**：E 提供 section_path 資訊、F 要求 LLM 用它。單獨 E 不引用、單獨 F 沒資訊可標。

#### G. 前端引用顯示（**本 commit 不做**）

footnote / 「參考章節」清單等——留 4.7e。

---

## 4. 風險評估

| 子改 | 風險 | 處理 |
|---|---|---|
| A 空 chunk 跳過 | 🟢 低 | 純減少資料、既有 `if md_content:` 護欄已有 |
| B Context 前綴 | 🟢 低 | embedding 純加正信號；既有 key 路徑保留 |
| C key 簡化 | 🟡 中 | **不做**（與 B 重疊，B 已解 embedding noise） |
| D 同 section 合併 | 🟡 中 | 只對 4 個短文 doc_type 套；其他保留 per-item |
| E retrieve 加 paper_title | 🟢 低 | 純擴 result_parts 字串內容、簽名不變 |
| F prompt 加引用要求 | 🟢 低 | LLM 行為改變但不破壞既有功能 |
| - | - | - |
| 額外：**score 閾值 0.22 重新校準** | 🟡 中 | chunk 結構改後分布會變、實測前不確定 | open Q #4 |
| 額外：**既有 paper 不重生 vector store** | 🟢 預期 | 與 Commit 1-14 一致；新上傳才套新邏輯 |

---

## 5. 測試規劃

### 5.1 既有測試影響

```bash
$ ls tests/ | grep -i "rag\|retriever"
（無）
```
**無 RAG 測試**——本 commit 無回歸風險、可放心加新測試。

### 5.2 新增測試（建議）

**`tests/test_rag_processor.py`**（新檔）：
- `test_generate_md_content_empty_summary_returns_none`：空 summary section → None
- `test_generate_md_content_text_with_context_prefix`：text node + doc_type=resume → 含 `Context: resume > ...`
- `test_merge_section_chunks_resume`：履歷 section 多 text → 合併為單 chunk
- `test_merge_section_chunks_academic_no_merge`：學術不合併
- `test_chunk_count_reduction_dehunt`：DeHunt 樣本 chunk 數應減少（用 fixture）

**`tests/test_rag_retriever.py`**（新檔）：
- `test_retrieve_includes_paper_title`：result 字串應含 `《{paper_title}》`
- `test_build_section_title_with_paper_prefix`：section_title 應有 paper 前綴

**`tests/test_ai_professor_chat.py`**（新增 / 既有？grep 確認）：
- 跑 RAG context、mock LLM 驗證 prompt 內有「請標註引用源頭」字樣

### 5.3 整合（手動 / 半自動）

- 重新生成 DeHunt 履歷 vector store、對比 chunk 數
- 用 fixture set 問同樣 query、觀察 retrieval top_k 變化

---

## 6. 端到端驗證計畫

### 6.1 15-1 落地後

1. 重新上傳 DeHunt 履歷（觸發 rag stage 重生）
2. 觀察 `output/{owner}/{paper}/{paper_uuid}_rag.md`：
   - 空殼 section chunk 數：**應顯著減少**
   - text chunk 開頭有 `Context: resume > ...` 行
   - VIEWTRIX section 應為**單一合併 chunk**（doc_type=resume 觸發 D）
3. 問問題「他在 VIEWTRIX 做什麼」：
   - retrieval 命中 VIEWTRIX 合併 chunk（而非散落 5 個）
   - score 應提升

### 6.2 15-2 落地後

1. 問題「他在 VIEWTRIX 做什麼」
2. 預期答覆：「根據『DeHunt Resume > Working Experience > VIEWTRIX』段，他擔任...」
3. chat history 字串應含引用、可方便人工驗證

### 6.3 跨 doc_type 回歸

每個 doc_type 跑一份代表性 paper：
- academic：retrieval 行為應與 commit 15 前等效（per-item chunks）
- technical：同上
- book：同上
- news / web / slides / resume：套用合併 + Context；觀察 chunk 數降低 / 精準度提升

---

## 7. 推薦執行順序

**建議拆 2 commits**：

### Commit 15-1：rag_processor chunk 優化
- 純改 `processor/rag_processor.py` + `pipeline_core._stage_rag` 傳 doc_type
- 子改 A（空 chunk）+ B（Context 前綴）+ D（短文 doc_type 合併）
- 加 `tests/test_rag_processor.py`
- ~+120 / -10 行
- **既有 paper 不重生 → 不生效；只對新上傳套**

### Commit 15-2：retriever + prompt 引用強化
- 改 `rag_retriever.py` + `prompt/ai/ai_character_prompt.txt`
- 子改 E + F
- 加 `tests/test_rag_retriever.py`
- ~+30 / -5 行
- **既有 paper 立即生效**（retriever 與 prompt 是查詢時行為、不依賴 chunk 結構）

**順序**：15-2 先做（既有 paper 立即受益、低風險）→ 15-1 後做（需要重生 vector store、影響範圍稍大）。

**或同 commit**：兩者邏輯關聯不深、分開更清楚。**推薦分開**。

---

## 8. open questions（待 baron 決策）

### Q1 — 是否做 C（key 路徑簡化）？
- 推薦：**不做**（與 B 重疊、B 已解 embedding noise；C 破壞 key_map 反查）
- 待 baron 同意「不做」、確認方案

### Q2 — D 套用範圍？
- 推薦：`{'resume', 'slides', 'news', 'web'}` 4 個短文 doc_type
- 待 baron 確認：要不要也含 `'book'`？book 章節短時也可能需要合併（但通常 book 章節長、不需）

### Q3 — 前端引用顯示要做多深？
- 推薦：**本 commit 不做**（4.7e 處理 footnote 或側欄列表）
- 若 baron 要本 commit 加 inline footnote 解析，需動前端 markdown 渲染器

### Q4 — score 閾值 0.22 是否需重新校準？
- 推薦：**先觀察**——15-1 落地後實測 score 分布；若大量正確 chunk 落到 < 0.22 → 降閾值
- 不在本 commit 改、留 follow-up
- 可選：開個 logging（retrieve 時 log top score 區間）做數據收集

### Q5 — `rag_tree['key_map']` 反查機制是否受 B 影響？
- B 在 chunk 內容**前綴**加 Context、不改 H1 / key 路徑
- `doc.metadata['Header']` 仍是 key 路徑、`key_map[Header]` 反查邏輯不變
- **不受影響**——已確認

### Q6 — 既有 paper 是否提供「重新生成 vector store」CLI？
- 與 Commit 9（cleanup_orphaned）的 backfill 討論一致：純使用者重上傳就行
- 也可加 `tools/regen_rag.py` per-paper 重跑 rag stage（pipeline_core.process(stages=['rag'])）
- **本 commit 不做**——留 follow-up

### Q7 — 跨文件查詢（baron 需求 3）
- 本 plan 不涵蓋
- 設計擴充點：retrieve_with_context 簽名加 `paper_ids: List[str]`、跨多 vector store 檢索後合併排序
- 留**另開 commit / 4.7e**

---

## 9. 不可做（已遵守）

- ❌ 業務檔（processor/ / retriever / chat / web_server / prompt）：未動
- ❌ 新建業務檔：未動
- ❌ commit / push：未動
- ✅ grep / cat / pytest 只讀命令：已執行
- ✅ 本報告 `.md`：唯一新增檔

---

## 狀態

**Plan 完成、等 baron 確認後再進入 Execute 階段**。

執行階段建議：
- 先 commit **15-2**（低風險、既有 paper 立即受益）
- 再 commit **15-1**（需重生 vector store、改動範圍稍大）
- 跨文件查詢留之後 commit

執行前需 baron 回答 §8 open questions（特別 Q2 / Q4）。
