# 2026-05-20 三改動：domain 注入 / prompt 措辭 / upload 取消 bug

**未 commit**。三改動互相獨立、互不依賴；建議拆 2–3 個 commit（見末尾）。

動到的檔（共 6 個）：
- `paper_manager.py`（domain 注入 ×2 site）
- `AI_professor_chat.py`（character/explain prompt 後條件附加 domain）
- `prompt/ai/ai_character_prompt.txt`（措辭）
- `prompt/ai/ai_explain_prompt.txt`（措辭）
- `prompt/translate/summary_generation_prompt.txt`（措辭 + IMRaD 放鬆）
- `static/index.html`（upload onchange guard 顯式化）

未動：ai_core / web_server / pipeline_core / processor/* / prompt/doc/* / 其他 translate prompt / router prompt。

---

## 改動 1：domain 注入 AI 對話端

### 1.1 paper_manager.py（兩個 site：preload + load_paper_resources）
```diff
 def preload_vector_stores(output_dir, ai_core) -> None:
     ...
     with db.SessionLocal() as s:
         items = [
-            (p.owner_id, p.paper_uuid)
+            (p.owner_id, p.paper_uuid, p.domain)
             for p in s.query(Paper).filter_by(status='done').all()
         ]
-    for owner_id, paper_uuid in items:
+    for owner_id, paper_uuid, domain in items:
         ...
         if rtree.exists():
             ai_core.load_paper_cache(paper_uuid, str(rtree))
+            # 注入 domain 到 ai_core 的 paper_cache（沿用 translate_processor:233-235 範式）
+            cache = ai_core._paper_cache.get(paper_uuid)
+            if cache is not None and domain:
+                cache['_domain'] = domain

 def load_paper_resources(output_dir, owner_id, paper_uuid, ai_core) -> None:
     ...
     if rtree.exists():
         ai_core.load_paper_cache(paper_uuid, str(rtree))
+        # 注入 domain 到 ai_core 的 paper_cache（沿用 translate_processor:233-235 範式）
+        with db.SessionLocal() as s:
+            row = s.query(Paper.domain).filter_by(
+                owner_id=owner_id, paper_uuid=paper_uuid
+            ).one_or_none()
+            domain = row[0] if row else None
+        cache = ai_core._paper_cache.get(paper_uuid)
+        if cache is not None and domain:
+            cache['_domain'] = domain
     logger.info(...)
```
- preload：SELECT 加 `p.domain` 同包出來、unpack tuple +1、注入 cache 5 行。
- load_paper_resources：函式無 Paper row 在 scope，做一次 `SELECT Paper.domain WHERE owner_id=? AND paper_uuid=?`（毫秒級單行查詢），注入 cache。
- 兩處皆 `if domain:` 守門，空字串/None 不打擾 AI。
- 鍵名 `_domain`（底線前綴避免與 rag_tree 既有欄位衝突）。
- **未動 ai_core.load_paper_cache 簽名**。

### 1.2 AI_professor_chat.py（_prepare_final_messages 內）
```diff
         character_prompt = self._read_file(AI_CHARACTER_PROMPT_PATH)
         explain_prompt = self._read_file(AI_EXPLAIN_PROMPT_PATH)
         ...
         explain_prompt = explain_prompt.format(title=title)
+
+        # 注入 domain（沿用 translate_processor.py:233-235 範式：caller 端條件附加）
+        if paper_data:
+            domain = paper_data.get('_domain', '')
+            if domain:
+                character_prompt = character_prompt + f"\n\n當前文件主題：{domain}"
+                explain_prompt = explain_prompt + f"\n\n當前文件主題：{domain}"
+
         system_message = f"{character_prompt}\n{explain_prompt}"
```
- 條件性附加；不改 prompt 檔本體變數、不改 paper_data 結構。
- 兩 prompt 皆附加（character 一般對話用、explain 用於「請解釋這段」）。

---

## 改動 2：prompt 措辭去學術化

### 2.1 `prompt/ai/ai_character_prompt.txt`（L11–L15 整段重寫）
```diff
 2. 回答策略
-   - 充分利用論文內容回答問題，保持學術嚴謹性
-   - 對於不確定的文獻、作者、期刊、機構，直接說「我不確定」或「這篇論文沒有提到」
-   - NEVER 推測或補全不確定的學術資訊，不要編造文獻、作者、機構或期刊名稱
-   - 當資訊不足時，誠實說明並引導回到論文本身
-   - 結合自身知識補充論文未涵蓋但相關的背景脈絡
+   - 充分利用文件內容回答問題，保持嚴謹性
+   - 對於不確定的內容、出處、機構，直接說「我不確定」或「這份文件沒有提到」
+   - NEVER 推測或補全不確定的內容，不要編造出處、作者或機構名稱
+   - 當資訊不足時，誠實說明並引導回到文件本身
+   - 結合自身知識補充文件未涵蓋但相關的背景脈絡
```
**驗證**：`grep '論文' prompt/ai/ai_character_prompt.txt` = **0**。

> L13 在 baron 明確列表外，但因 baron 指示「請完整 grep 此檔內所有
> 『論文/學術/文獻/期刊』並依語境替換」+「保留 L11 的『嚴謹性』（去掉
> 『學術』二字即可）」，L13 含「學術資訊/文獻/期刊」皆屬該 grep 命中，
> 已一併替換（學術→去除、文獻/期刊→「內容/出處」）。如不符 baron 預期請告知。

### 2.2 `prompt/ai/ai_explain_prompt.txt`（L1 整行重寫）
```diff
-你是一位專業的學術導師，當前協助學習者理解的論文或書籍為：{title}
+你是一位專業的文件閱讀助手，當前協助使用者理解的文件為：{title}
```
`{title}` 變數保留；`grep '論文\|學術導師' prompt/ai/ai_explain_prompt.txt` = **0**。

### 2.3 `prompt/translate/summary_generation_prompt.txt`（通篇）
- 「學術論文分析專家/論文章節/論文摘要背景/論文整體框架/論文整體主題/論文整體結構/論文框架/論文整體邏輯結構」→「文件…」
- 「以論文語言風格呈現」→「以文件原有的語言風格呈現」
- 「使用學術論文的自然語言風格…論文的一部分」→「使用文件原有的自然語言風格…原文的一部分」
- L26–31 IMRaD 例舉 → 改 4 條 doc 類型分支（依 baron 建議）：
  ```
  【關係分析要求（依文件類型自適應）】
  - 若為論證型文件（如學術論文）：可採引言/方法/結果/討論的章節敘事
  - 若為敘事型文件（如新聞、報導）：以時序與事件因果鋪陳
  - 若為條列型文件（如簡報、履歷）：以主題/段落為單位精煉
  - 其他類型：依文件實際結構自適應
  - 如有子章節：體現子章節之間的邏輯關係和層次結構
  ```
- 順手修正：「邏輯關**系**」→「邏輯關**係**」（4 處，繁中正確字）；
  「採用台灣**學術**語境」→「採用台灣語境」（去學術化一致）。
**驗證**：`grep '論文' prompt/translate/summary_generation_prompt.txt`
**剩 1 處**：line 27「論證型文件（如學術論文）」← 預期且合理（baron 驗證
條：「IMRaD 例舉的學術論文分支仍會引導」即此）。

---

## 改動 3：upload 取消 bug（onchange guard 顯式化）

```diff
   input.onchange = async (e) => {
-    const file = e.target.files[0];
-    if (!file) return;
+    const files = e.target.files;
+    if (!files || files.length === 0) return;  // 使用者取消選檔
+    const file = files[0];
```
與 baron 提供的範例一致。既有上傳/進度/錯誤處理邏輯**完全保留**。

> ⚠ **誠實標註**：原有 `if (!file) return;` 對「使用者取消選檔」**語意上
> 已等價守住**（`e.target.files[0]` undefined → `!file` true → return）。
> 此修法主要是改為 baron 偏好的顯式 `length === 0` 表述。
>
> 若 baron 觀察到的「點上傳 → 取消選檔 → 仍跳 confirm modal」**實際上仍會
> 發生**，則真正肇因是 **prototype demo handler**：`static/index.html:1489`
> `document.getElementById('upload-btn').addEventListener('click', () =>
> openModal('confirm-modal'));`——此 handler 於 upload-btn 點擊時**立即**
> 開啟 confirm-modal，與 file picker 結果無關。Phase 4.7c 決策 3.2 已記
> 「prototype 先註冊 → 業務後註冊 → stopImmediatePropagation 擋不掉已執
> 行的 prototype handler」。處置選項：
>   1. 刪除 line 1489 該行（破例改 prototype JS）；或
>   2. 點上傳時改用 capture-phase listener 在 prototype handler 前攔截；
>   3. 維持現狀，視覺上接受多開一個空 modal。
> **本輪未動 line 1489**，遵守 baron 明確 scope。

---

## 驗證
| 項 | 結果 |
|---|---|
| `py_compile paper_manager.py AI_professor_chat.py` | ✓ 通過 |
| `pytest tests/test_metadata_extractor.py -q` | **18 passed, 3 skipped**（與改前一致，無回歸）|
| `node --check` 抽出主 `<script>` body | ✓ 通過 |
| `grep '論文' ai_character_prompt.txt` | 0 |
| `grep '論文\|學術導師' ai_explain_prompt.txt` | 0 |
| `grep '論文' summary_generation_prompt.txt` | 1（line 27「學術論文」分支，預期）|

端到端（待 OrcStack 重啟，**paper_manager 改動需重啟**）：
1. DeHunt 履歷問「請分析這位候選人職涯主要的領域變化」
   → character prompt 末尾被附加「當前文件主題：{domain}」
   → AI 不再說「論文」、依 domain 自然用「文件/履歷/報導」名詞稱呼
   → 應引用 Novatek/Focaltech/iPhone DDIC 等具體內容
2. 800-vdc 學術論文回歸：summary 章節精煉的「學術論文 IMRaD 分支」仍會
   引導 AI 採引言/方法/結果/討論章節敘事
3. 點 `#upload-btn` → 取消選檔 → 若仍跳 confirm-modal，請依「⚠ 標註」處置
   line 1489 prototype demo handler

---

## 疑慮列表（baron 確認）
1. **`AI_professor_chat.py:221` `title = "無論文"` 字面常數未動**——是 Python
   字面字串、不在改動 1 scope（domain 注入）、不在改動 2 scope（prompt 檔）。
   若需去學術化建議改「無文件」，但本輪未動。
2. **`summary_generation_prompt.txt` 順手改動**：
   - 「採用台灣學術語境」→「採用台灣語境」（去除「學術」二字，與整體
     去學術化一致；不影響繁中規則）
   - 「邏輯關**系**」→「邏輯關**係**」（4 處繁中正字修正）
   兩者皆非 baron 明確列入修法清單，但與整體方向一致；如不符請告知。
3. **`ai_character_prompt.txt` L13** 替換已於 2.1 流程內標註；同樣可回退。
4. **改動 3 的 onchange guard** 與原邏輯**語意等價**；真正使 confirm-modal
   彈出的肇因（line 1489 prototype demo handler）未動——若驗 UI 仍跳
   modal，請就「⚠ 標註」三選項拍板（本輪不自行處置）。

---

## 推薦 commit 拆分（**未 commit**）

### Commit A — domain 注入
**檔**：`paper_manager.py`, `AI_professor_chat.py`
```
feat(ai): inject paper.domain into AI character/explain prompts

paper_manager.preload_vector_stores 與 load_paper_resources 載入 paper_data
時把 Paper.domain 注入 ai_core._paper_cache[paper_uuid]['_domain']。
AI_professor_chat._prepare_final_messages 載入 character/explain prompt 後，
若 paper_data 含 _domain 則條件附加「當前文件主題：{domain}」到兩 prompt
尾部。沿用 translate_processor.py:233-235 同範式（caller 端條件附加，
prompt 本體不加變數、空值不打擾）。

未動 ai_core.load_paper_cache 簽名；未動 web_server / pipeline_core / 任何
prompt 檔。實際效果：AI 一般對話與「請解釋這段」皆能依 domain（如
「半導體電源轉換器 - 800V 直流配電架構」/「體育新聞 - 環義自由車賽
報導」）自然用合適名詞稱呼當前文件。

py_compile 通過；metadata 測試 18 passed 3 skipped 無回歸。
端到端待 OrcStack 重啟（paper_manager 改動需重啟生效）。
```

### Commit B — prompt 措辭去學術化
**檔**：`prompt/ai/ai_character_prompt.txt`, `prompt/ai/ai_explain_prompt.txt`, `prompt/translate/summary_generation_prompt.txt`
```
fix(prompt): 措辭去學術化（D-1），讓 prompt 對所有 doc_type 通用

原 prompt 全用「論文/學術導師/文獻/期刊」字眼，AI 對履歷/簡報/新聞
回答時會稱「這份論文沒有提到」，與 baron 觀察的 DeHunt 履歷狀況一致。

ai_character_prompt.txt L11-15：「論文/學術/文獻/期刊」→「文件/內容/
出處/機構」，保留「嚴謹性」（去除「學術」二字）。
ai_explain_prompt.txt L1：「學術導師/論文或書籍」→「文件閱讀助手/文件」，
{title} 變數保留。
summary_generation_prompt.txt 通篇「論文」→「文件」（保留 line 27
「論證型文件（如學術論文）」作為 IMRaD 引導分支，academic 仍享深度）；
L26-31 IMRaD 例舉放鬆為 4 條 doc-type-自適應分支（學術論文/新聞報導/
簡報履歷/其他）；順手修正「邏輯關系」→「邏輯關係」（繁中正字）、
「台灣學術語境」→「台灣語境」（去學術化一致）。

未動 router prompt（上輪已修）/ prompt/doc/* / translate 其他 prompt /
任何 .py。Prompt 為純文字檔即時讀，**不需重啟**。

驗證：grep 確認 ai_character/ai_explain「論文」=0；summary 剩 1 處於
line 27「學術論文」IMRaD 分支（預期）。端到端 router→character→
summary 對履歷/簡報/新聞應自然用通用名詞，與 domain 注入互補。
```

### Commit C — upload onchange guard 顯式化
**檔**：`static/index.html`
```
fix(ui/upload): onchange guard 顯式化為 length === 0 檢查

upload-btn 的 input.onchange 將「未選檔」守門從 `const file =
e.target.files[0]; if (!file) return;` 顯式化為 `const files =
e.target.files; if (!files || files.length === 0) return;`，與
baron 風格一致。語意等價（兩者皆於使用者取消選檔時 early return）。

附帶觀察（未自行處置）：若 baron 觀察「點上傳 → 取消選檔 → 仍跳
confirm-modal」實際仍發生，肇因可能是 prototype demo handler（line
1489 `openModal('confirm-modal')` 於 click 時立即觸發、與 file picker
結果無關）。Phase 4.7c 決策 3.2 已記為「stopImmediatePropagation 擋不
掉早註冊的 prototype handler」。處置選項與此 commit 無關，待 baron
另議。

node --check 通過；後端 0 改動。
```

---

## 不可動清單（已遵守）
- ai_core.py：未動（domain 透過 `_paper_cache[paper_uuid]['_domain']` 注入，
  簽名未變）
- web_server.py / pipeline_core.py / processor/* / doc_analyzer.py /
  translate_processor.py / extra_info_processor.py：未動
- `prompt/doc/*`：未動
- `prompt/translate/{content,title,question,formula,graph_question}_*.txt`：未動
- `prompt/ai/ai_router_prompt.txt`：未動（上輪已修）
- prototype JS（含 line 1489 demo upload handler）：未動
- 未新增 resume doc_type / 未動 domain_detector / 未引入新檔案 / 未新增 CDN
- **未 git add / 未 git commit**
