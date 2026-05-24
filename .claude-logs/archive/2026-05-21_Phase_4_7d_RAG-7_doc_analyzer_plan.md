# Phase 4.7d RAG-7 — doc_analyzer 切 section 錯誤診斷 Plan

> 純讀分析、零業務檔案改動。
> 觸發：DeHunt 履歷工作經歷「FOCALTECH-SYSTEM」段被併進「TARGETEK」section、影響 RAG chunk 品質（15-1 短文合併也救不回，因 section 邊界本身就錯）。

---

## TL;DR

- **根因高度懷疑落在 doc_analyzer**（不是 MinerU pdf2md、也不是 md_processor）。最關鍵發現：**resume doc_type 重用 academic 的 `heading_fix` 與 `structure` prompt**（`processor/doc_analyzer.py:22, 34` 寫明 `# Phase 1 reuse academic`）。
- academic prompt 「子章節 = 阿拉伯數字編號或**明顯從屬於上一層的標題**」這條規則對「履歷多個工作經歷」殺傷力大：LLM 容易把後出現的公司（FOCALTECH）判定為前面公司（TARGETEK）的**子章節 H3**，而非平行 H2。
- 但**也可能是 MinerU 沒抽出 FOCALTECH 為 heading**（plain text）—— 此情形 `heading_fix` 無法救（它只改既有 `#` 行的 `#` 數量、不新增 heading）。
- **本輪 plan 不修**——三個假設 A/B/C 需要對 DeHunt 中間檔逐項對照確認。診斷腳本 / 命令在 §2 給出。
- **推薦修法方向**（看診斷結果決定）：B（寫履歷專用 heading_fix prompt）成本最低且擴展性最好；如果是 A（MinerU 沒抽 heading），需考慮後處理補抽——範圍較大、留下次。

---

## 1. 現況盤點

### 1.1 pipeline 內 doc_analyzer 的角色

`pipeline_core._stage_analyze` (`pipeline_core.py:544`)：
```python
def _stage_analyze(self, pdf_path, paper_dir, paper_name, output_paths):
    markdown_path = output_paths.get('pdf2md')  # MinerU 輸出的 .md
    doc_type = output_paths.get('_confirmed_doc_type', 'academic')
    return self.doc_analyzer.analyze(markdown_path, doc_type)
```

`doc_analyzer.analyze` (`processor/doc_analyzer.py:51-65`)：
```python
def analyze(self, markdown_path: Path, doc_type: str) -> Path:
    if doc_type not in HEADING_FIX_PROMPTS:
        doc_type = 'academic'
    self._fix_heading_levels(markdown_path, doc_type)        # 1. LLM 改 # 數量
    self._analyze_document_structure(markdown_path, doc_type)  # 2. LLM 抽 structure 區段
    return markdown_path
```

**Step 1**：`_fix_heading_levels(L67-86)` 用 LLM 看所有 `^#` 行、回 JSON `{行號: # 數量}`、寫回 `.md`。
- caller: `utils/heading_utils.fix_heading_levels()` —— 只改既有 `#` 行的 `#` 數量、**不新增 heading**（line 28-30：`if line_num < len(lines) and lines[line_num].startswith('#')`）。
- 對「MinerU 沒抽出 heading」**完全救不回**。

**Step 2**：`_analyze_document_structure(L88-137)` 用 LLM 看前段 markdown、回 JSON `{"structure": [{"start":N, "end":M, "type":"..."}]}` → 寫到 sidecar `{stem}_doc_structure.json`。
- 「結構」型別有 `title / authors / publication_info / abstract / section_heading / ...`
- **此 sidecar 不改 markdown 本身**；md_processor 之後讀 sidecar 來判斷哪些行是 authors（影響 `authors_info` 抽取、不影響 sections 切割）。

### 1.2 md_processor 的角色

`md_processor.parse` (`processor/md_processor.py:206`) + `build_hierarchy(L189-204)`:

切 sections：
- 每遇到 `^#+\s+(...)` heading 開新 Section（含 `heading_level = # 數量`）
- 最後丟給 `build_hierarchy`：
  ```python
  while stack and stack[-1][0] >= h:   # 找比目前淺的 parent
      stack.pop()
  if stack:
      stack[-1][1]['children'].append(section)  # 變子節
  else:
      hierarchy.append(section)         # 變頂層
  stack.append((h, section))
  ```

**關鍵**：依 `heading_level`（即 markdown 內的 `#` 數量）建巢狀。**若 FOCALTECH 是 H3 而 TARGETEK 是 H2 → FOCALTECH 變 TARGETEK 的 child**。

md_processor 本身**沒有 LLM**、純依 `#` 數量決定。

### 1.3 resume 的 prompt 配置（**關鍵發現**）

`processor/doc_analyzer.py:22`：
```python
'resume': 'prompt/doc/heading_fix_academic.txt',  # Phase 1 reuse academic
```

`processor/doc_analyzer.py:34`：
```python
'resume': 'prompt/doc/structure_academic.txt',  # Phase 1 reuse academic
```

**resume 在 doc_analyzer 兩個 LLM 步驟都重用 academic prompt**。academic prompt（`prompt/doc/heading_fix_academic.txt:9-13`）：
```
- 論文主標題用 #（一個）
- 頂層章節用 ##（兩個）：Abstract、Introduction、Methods、Results、Discussion、Conclusion、References，以及羅馬數字編號（I. II. III.）或無編號的頂層章節
- 子章節用 ###（三個）：阿拉伯數字編號（1. 2. 3.）或明顯從屬於上一層的標題
- 子子章節用 ####（四個）：小數點編號（1.1 1.2）或更深層的標題
```

**對履歷的殺傷力**：
- 履歷頂層章節 = `Working Experience` / `Education` / `Skills` → ##
- 子章節 = 工作經歷的公司 `VIEWTRIX` / `TARGETEK` / `FOCALTECH-SYSTEM`
- prompt 沒指明「同 section 內多個平行子章節都該是 ###」
- LLM 對「明顯從屬於上一層」的判定可能不一致——尤其當公司之間有時序關係（前後排列）時，LLM 可能誤判後出現的為前者的「子章節」

`heading_fix_slides.txt` / `heading_fix_news.txt` 等都有專用 prompt；**唯獨 resume 重用 academic、且 academic prompt 對履歷結構不友好**。

### 1.4 全 doc_type 的 prompt 狀態

| doc_type | heading_fix prompt | structure prompt |
|---|---|---|
| academic | academic | academic |
| book | book | book |
| technical | technical | technical |
| slides | slides | slides |
| news | news | news |
| web | web | web |
| **resume** | **academic（reuse）** | **academic（reuse）** |

resume 是唯一沒專用 prompt 的——標的 `# Phase 1 reuse academic` 註解明示這是「先 ship 後迭代」。

---

## 2. DeHunt 履歷中間檔對照（找切錯的點）

中間檔在 OrcStack `output/1/DeHunt_CTO_Tzung-Yuan_Lee/`。**本 worktree 不在 OrcStack、無法直接看**——以下是 baron 端跑的命令清單：

### 2.1 必看的 3 個檔

```bash
cd output/1/DeHunt_CTO_Tzung-Yuan_Lee/

# A. MinerU 原始輸出（pdf2md 後、analyze 前 → 看 FOCALTECH 原始 # 數量）
grep -nE "^#" DeHunt_CTO_Tzung-Yuan_Lee.md | head -40

# B. heading_fix 跑完的 .md（同檔；analyze 是 in-place 寫回 .md）
# 上面 A 命令就是「fix 後的最終 .md」——MinerU 原始版本沒留存
# 需要看 logs/pipeline.log 才知道 fix 前狀態

# C. doc_analyzer structure sidecar（看 LLM 判定的「結構區段」）
cat DeHunt_CTO_Tzung-Yuan_Lee_doc_structure.json | python -m json.tool

# D. md_processor 切完的 sections（看 FOCALTECH 是否被併進 TARGETEK）
cat DeHunt_CTO_Tzung-Yuan_Lee_structured.json | python -m json.tool | head -200
```

### 2.2 對照表（待 baron 填）

| 檢查項 | 預期 | 實際（待 baron 填） |
|---|---|---|
| `.md` 內 `Working Experience` 的 `#` 數量 | `##` | ? |
| `.md` 內 `VIEWTRIX` 的 `#` 數量 | 期望 `###` 或 `##`（爭議點） | ? |
| `.md` 內 `TARGETEK` 的 `#` 數量 | 同上 | ? |
| `.md` 內 `FOCALTECH-SYSTEM` 的 `#` 數量 | 同上 | ? |
| `.md` 內這 3 個是否都是 heading（有 `#`）？ | 期望都是 | ? |
| `_structured.json` 內 `sections` 第幾項是 `Working Experience` | n | ? |
| `Working Experience` 的 `children` 數量 | 應該 = 公司數（3-4 家） | ? |
| `Working Experience.children` 內各家公司是否平行 | 平行 H3 / 不互為 children | ? |
| `TARGETEK` 的 `children` 數量 | 應為 0 或它的子項目 | **若含 FOCALTECH → 切錯** |
| `FOCALTECH-SYSTEM` 是否出現在頂層 `sections`？ | 不應該（是 Working Experience 子節） | ? |

填完上表即可定位假設 A / B / C 的真兇。

### 2.3 logs 觀察

```bash
# heading_fix LLM 輸入 / 輸出 log
grep "\[analyze\] heading fix" logs/pipeline.log | tail -5
# 預期看到：「heading fix 輸入: N 行 heading」+ 「標題層級修正完成」
# 若有錯能看到 raw LLM JSON response（可能要加 debug log）
```

---

## 3. 三個假設（含證據判定方法）

### 假設 A — MinerU pdf2md 沒抽到 heading

**症狀**：`.md` 內 FOCALTECH 是純文字（無 `#`）、或被併進前一個 heading 段。

**證據判定**：
```bash
grep -n "FOCALTECH" output/1/DeHunt_CTO_Tzung-Yuan_Lee/DeHunt_CTO_Tzung-Yuan_Lee.md
```
- 若回行如 `42:FOCALTECH-SYSTEM` 而非 `42:### FOCALTECH-SYSTEM`、`42:## FOCALTECH-SYSTEM` → **A 成立**

**為何救不回**：
- `_fix_heading_levels` 只改既有 `#` 行的 `#` 數量、不新增 heading
- `md_processor.parse` 只依 `^#+\s+` 切 section
- 若 MinerU 出來就無 `#`、整條鏈都沒人會補

**修法方向**：
- 改 MinerU 設定（可能性低、外部服務）
- 在 `md_cleaner` / 新增 `md_heading_inferrer` stage 用 LLM 看純文字 + 結構特徵補抽 heading
- 範圍大、跨 stage、留 4.7e

### 假設 B — LLM heading_fix prompt 把 FOCALTECH 判定為 TARGETEK 的子章節

**症狀**：`.md` 內 FOCALTECH 是 `###`、TARGETEK 是 `##`（或前者 `####`、後者 `###`）—— `heading_level` 比較深 → `build_hierarchy` 塞進前者 children。

**證據判定**：對照 §2.2 表第 2-5 列。**若 4 個公司的 `#` 數量不一致（有 `##` + `###` 混雜）→ B 成立。**

**為何容易發生**：
- resume 用 academic prompt（§1.3 已盤點）
- academic prompt「明顯從屬於上一層」對連續多家公司殺傷力大
- 沒明示「同 section 內平行子章節都該同一層」

**修法方向**（**推薦**）：寫履歷專用 `prompt/doc/heading_fix_resume.txt`：
```
- 履歷主標題（候選人姓名）用 #
- 頂層章節用 ##：Working Experience、Education、Skills、Projects、Certifications 等
- 工作經歷 / 教育各條目用 ###（**所有同類條目都用 ###、不互為子節**）
- 進一步細分（如職位 / 任期）用 ####

特別注意：
- 多家公司是「**平行**」的工作經歷、**不**要把後面公司判定為前面公司的子章節
- 多個學位是平行的教育經歷、同理
```

工時：30-60 分（寫 prompt + dict 改 path + 測試）；只動 `processor/doc_analyzer.py` 兩 dict + 新增 2 個 prompt 檔（heading_fix_resume.txt + structure_resume.txt）。

### 假設 C — heading fix 邏輯 bug

**症狀**：MinerU 出來原本是 `##` 的 heading 被 fix 降為 `###`。

**證據判定**：
- 看 `logs/pipeline.log` 的 `[analyze] heading fix` 段、若有保留 raw LLM response 即可看 `{"行號": #數量}` 內 FOCALTECH 行的數量
- 若 raw .md 是 `##`、fix 後變 `###` → **C 成立**

**為何發生**：與 B 重疊——LLM 在 prompt 引導下把它降級。

**修法方向**：和 B 同——改 prompt 才能引導 LLM 正確判斷。

### 假設彼此關係

- **A 與 B/C 互斥**：MinerU 沒抽就無 `#` 行給 LLM 看；有 `#` 才有 fix 空間
- **B 與 C 重疊**：兩者都是 prompt + LLM 判斷結果問題；C 強調「降級行為」、B 強調「prompt 沒指引同層」

**最可能**：B（最可能、修法成本最低）；其次 C（同 prompt 修法即解）；A 機率較低但需確認。

---

## 4. 跨 doc_type 影響評估

| doc_type | 是否類似問題 | 為什麼 |
|---|---|---|
| **resume** | 🔴 **嚴重** | 多家工作經歷 / 多個教育 / 多個 project 平行條目、academic prompt 沒指引 |
| **slides** | 🟡 可能 | 簡報內子標題若連續、可能誤判巢狀；但 slides 有專用 prompt（`heading_fix_slides.txt`）、判定規則明確 |
| **news** | 🟢 不太發生 | 通常單一 H1 + 段落；無多層次 H2/H3 |
| **web** | 🟢 不太發生 | 類似新聞 |
| **academic** | 🟢 適用 | prompt 為它寫的；學術論文 H2 文字長、不易誤判 |
| **technical** | 🟡 中性 | 技術文件章節結構清楚；但白皮書 cover-TOC 對 metadata 有問題（已在 4.7c 解）、heading_fix 一般正常 |
| **book** | 🟢 適用 | 章節結構清楚 |

**結論**：本問題主要是 **resume specific** —— 因為「平行條目多」+「academic prompt 借用」雙重因素。其他 doc_type 即使有平行子章節（如 academic 的多個 figures / tables），LLM 多半判定為平行（圖表編號獨立、不互相從屬）。

---

## 5. 各假設修法成本

| 假設 | 動到哪些檔 | 影響範圍 | 工時 | 風險 |
|---|---|---|---|---|
| **A（MinerU 沒抽）** | 新增 `md_heading_inferrer` stage / 改 MinerU 呼叫 / 後處理 | 跨 stage、影響所有 doc_type | 4-8 小時 | 高 |
| **B（prompt）** ⭐ | 新增 `prompt/doc/heading_fix_resume.txt` + `structure_resume.txt`；改 `processor/doc_analyzer.py:22, 34` 兩 dict 指向 | 只動 resume；不影響其他 doc_type | 30-60 分 | 低 |
| **C（heading fix algorithm）** | 改 `utils/heading_utils.fix_heading_levels` | 跨 doc_type、影響大 | 2-4 小時 | 中 |

**推薦優先 B**：成本最低、影響範圍最小、解決真因（履歷 prompt 缺失）。

C 不推薦——algorithm 沒問題、是 prompt 引導 LLM 的方式錯。

A 若真實為主因、再評估範圍——但 §2 對照表填完應該能排除 A（履歷頁面結構清楚、MinerU 多半會抽到 heading）。

---

## 6. 推薦執行順序（依診斷結果）

### Step 1（baron 端）：填 §2.2 對照表

baron 在 OrcStack 跑 §2.1 4 個命令、把 §2.2 表第 2-5 列數值填上。**這一步無編程、純資料蒐集**。

### Step 2：依對照表判定假設

| 觀察結果 | 結論 | 後續動作 |
|---|---|---|
| FOCALTECH 在 .md 沒有 `#` | A 成立 | 留 4.7e 評估 / 與 MinerU 模組化合併處理 |
| FOCALTECH 在 .md 是 `###`、TARGETEK 是 `##` | B/C 成立 | 跑 Step 3（B 修法） |
| FOCALTECH / TARGETEK 都是 `##` 但 _structured.json 仍合併 | md_processor build_hierarchy 邏輯有 bug | 另開 diagnostic、本 plan 範圍外 |

### Step 3（最可能）：B 修法 commit

1. 新建 `prompt/doc/heading_fix_resume.txt`（依 §3 假設 B 修法模板）
2. 新建 `prompt/doc/structure_resume.txt`（仿 `structure_academic.txt`、加履歷特有 type：`contact_info` / `summary` / `experience` / `education` / `skills`；可後做）
3. `processor/doc_analyzer.py:22, 34` 兩 dict 把 resume 指向新檔
4. `tools/check_doc_type_registry.py` 驗證
5. 上傳新 resume 測試 → 看 _structured.json 是否切對

工時 30-60 分。

### Step 4：backfill（依 RAG-2）

既有切錯的 resume（DeHunt 等）需重新跑 `analyze` + `md2json` + `rag` stage 才能套修正。可：
- 等 RAG-2 backfill CLI 落地
- 或 user 重新上傳

---

## 7. open questions（待 baron 決策）

### Q1 — 修法只針對 resume 或全 doc_type？
- 推薦：**只針對 resume**（其他 doc_type prompt 各自為政、無此痛點；履歷是 Phase 1 重用 academic 的技術債）
- 替代：順手檢查 slides 是否類似問題（slides 有專用 prompt、應該沒問題；但可順手 review）

### Q2 — 動 prompt 後是否需要 sample test 不同 paper 確認不回歸？
- 推薦：**需要**。至少 2-3 份不同類型履歷（科技業 / 學界 / 創業）跑一輪、確認 _structured.json 切割正確
- 工時：每份 ~10 分鐘 + 對照表

### Q3 — 既有已切錯的 paper 是否要重生？
- 推薦：**依賴 RAG-2 backfill CLI**。Step 3 修法落地後、baron 可選擇性對「明顯受影響」的 paper 重跑
- 替代：user 重新上傳（簡單但失去既有 chat 歷史）

### Q4 — 如果診斷出是 A（MinerU 沒抽）、要不要繞過、不修上游？
- 推薦：**先確認**——本 plan 完成 §2.2 對照表後再決定
- 若是 A、推薦先以 `md_heading_inferrer` 後處理（不動 MinerU）為主、留 4.7e；不阻擋 B 同時推進
- MinerU 模組化（已完成）使得未來換 PDF 解析工具相對容易，A 的長期解法可能跟換工具一起做

### Q5 — `structure_resume.txt` 是否與 `heading_fix_resume.txt` 同 commit？
- 推薦：**heading_fix 先**（影響 RAG chunk 品質的直接原因）；structure 是 sidecar 用於 authors_info 抽取、對 RAG chunk 切割影響較小
- structure 修法可下次另開 commit

---

## 8. 不可做（已遵守）

- ❌ 業務檔（`processor/*` / `pipeline_core` / `web_server` / `prompt/doc/*`）：未動
- ❌ 新建業務檔：未動
- ❌ commit / push：未動
- ✅ grep / cat / 只讀命令：已執行
- ✅ 本報告 `.md`：唯一新增檔
- ✅ §2 給出 baron 端可跑的命令，不要求 worktree 直接看 OrcStack 中間檔（worktree 無 `output/`）

---

## 狀態

**Plan 完成、等 baron 跑 §2.1 對照命令後再進 Execute 階段**。

執行階段建議：
1. baron 跑 §2.1 命令、填 §2.2 表
2. 依 §6 Step 2 判定假設
3. 假設 B 成立（最可能）→ 寫 `heading_fix_resume.txt` + 改兩 dict + 測試（30-60 分）
4. 假設 A 成立 → 留 4.7e、評估 `md_heading_inferrer` 後處理
5. 假設 C 成立 → 同 B 路徑修
