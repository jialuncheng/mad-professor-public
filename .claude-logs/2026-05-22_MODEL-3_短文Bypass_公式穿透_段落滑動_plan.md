# Phase 4.7? MODEL-3 — Plan：短文 Bypass + 公式穿透 + 段落級滑動（tiling_processor 三合一優化）

> 本文件為**純分析與設計計畫**，獲確認前嚴禁修改業務代碼。
> **依據**：`.claude-logs/ref/model_optimization_blueprint.md` §2.1-§2.4

---

> **審查強化已納入（v2）**：6 個修正
> 1. **公式拼接字元差異化**（修正 1、🔴 production 必須）— `_join_content` helper、`text+formula` 用空格 / `text+text` 用 `\n\n`、防 inline formula 強制斷行災難
> 2. **Bypass 保留原始 `index`**（修正 2、🔴 production 必須）— 絕不重寫、否則 md_restore 對齊（figure/table/text 順序）會錯亂
> 3. **公式長度不觸發 flush**（修正 3）— LaTeX 字元數虛高、`type=='formula'` 無論長度永遠合進 buffer
> 4. **段落 regex split 容錯**（修正 4）— `re.compile(r'\r?\n\s*\r?\n')`、處理 Windows `\r\n` / 多餘空白
> 5. **`TILING_MAX_LENGTH` env 化**（修正 5）— 對齊 `TILING_BYPASS_CHAR_LIMIT` / `TILING_PARAGRAPH_THRESHOLD` 風格
> 6. **MODEL-8 連動標記**（修正 6）— 既有 vector store 不相容、用 MODEL-1+2 backfill SOP；未來 MODEL-8 落地後可自動化
>
> **既有 tiled.json 不相容**：本 commit 改 tiling 邏輯 → 改變下游 chunk 結構 → 既有 vector store 需重建（baron 沿用 MODEL-1+2 backfill SOP）

## §1 TL;DR

- **問題與挑戰**：
  - **(A) 短文 unnecessary tiling**：`tiling_processor.max_length = 2500`、短文（resume / news / web、總字數 < 5000）仍走 TextTiling 邏輯 + embedder API call、零價值純消耗
  - **(B) 公式破碎**：`_merge_small_text_blocks` (L139) 只允許 `type=='text'` 進緩衝區、`type=='formula'`（inline 公式 + 周圍說明文字）會在邊界截斷 → 翻譯語意割裂
  - **(C) 書籍滑動爆炸**：長文書籍時 `_split_into_sentences` (L302) 拆出大量句子、`_texttiling` 滑動窗口（window=3、step=1）次數爆炸 → RTT 序列卡死
- **核心根因**：tiling_processor 設計時針對中等長度 academic paper、未對「短文 / 含公式論文 / 書籍」三類做差異化路徑
- **設計解法**：1 個 tiling_processor + 1 個 settings + 3 個新 pytest 檔，**3 個正交子改動拆 3 commits**（B1/B2/B3 模式對齊 MODEL-1+2）：
  - B1：短文 Bypass（最大價值、最低風險）
  - B2：公式穿透（學術論文受益、改 _merge_small_text_blocks soft-types）
  - B3：段落級滑動（書籍受益、threshold flip 邏輯）
- **影響範圍**：
  - **動**：`processor/tiling_processor.py`（加 bypass / soft-types / paragraph 切換）+ `settings.py`（加 3 個閾值常數）
  - **不動**：`pipeline_core.py` `_stage_tiling` 簽名（後相容）、其他 processor、RAG / Embedding / MODEL-9 / MODEL-1+2 既有架構
- **預估**：~1.5 天 / 3 commits + ~15-16 個 pytest
- **既有 tiled.json 不相容**：本 commit 改 tiling 邏輯 → 改變下游 chunk 結構 → 既有 vector store 需重建（baron 沿用 MODEL-1+2 backfill SOP）

---

## §2 現況盤點

### 2.1 tiling_processor 主流程

**`processor/tiling_processor.py`**（315 行、單一 class `TilingProcessor`）：

| 行 | 函式 | 用途 |
|---|---|---|
| L9 | `class TilingProcessor` | 主類 |
| L17 | `__init__(min_length=500, max_length=2500, window_size=3, step_size=1, embedder=None)` | 既有預設 |
| L34 | `process(input_path, output_path)` | 主入口、**無 doc_type 參數**（caller 也沒傳）|
| L65 | `_process_sections(sections)` | 跳 abstract / references、遞迴處理 |
| L85 | `_process_content(content)` | 對 content list 跑 merge + split |
| L139 | `_merge_small_text_blocks(content)` | **僅 `type=='text'` 進緩衝區**（L156-167）；非 text 強制 flush（L177-181）|
| L191 | `_texttiling(elements, split_mode='sentence')` | 滑動窗口 + depth score 切 boundary |
| L267 | `_find_optimal_boundary(start, elements, ...)` | 在 boundary 候選範圍找最佳切點 |
| L302 | `_split_into_sentences(text)` | 句子切割（推測用正則 / nltk）|

當前 chunk 邏輯：
- 對 `type=='text'` + `len > max_length` (2500) 才切（L107）：
  - 若內含 `\n\n` → `split_mode='delimiter'`
  - 否則 → `split_mode='sentence'`（用 `_split_into_sentences`）
- 對 `type=='text'` + `len < min_length` (500) → 合併進緩衝區
- 非 text item（formula / table / image / heading / ...）：原樣 pass-through、且作為 merge 緩衝區的硬截斷邊界（L177-181）

### 2.2 既有 `max_length` 配置

```
L17 __init__: max_length: int = 2500
L107 if item['type'] == 'text' and len(item['content']) > self.max_length:
L158 if len(item['content']) < self.min_length:
```

- **`max_length = 2500` 寫死 in `__init__`** — caller 不傳會用 2500
- 不是 env 化、無法 ENV override
- 對 Gemini 3.5 Flash 65k 輸出能力來說、2500 過於保守

### 2.3 TextTiling 實作

**自製實作**（不是 nltk TextTilingTokenizer）：

```
L191 def _texttiling(self, elements, split_mode):
L203 if len(elements) < self.window_size + 2: return [...]
L209 for i in range(0, len(elements) - self.window_size + 1, self.step_size):
L210 window = elements[i:i + self.window_size]
```

- 滑動單元：**句子**（split_mode='sentence' via `_split_into_sentences`）或 **delimiter 切片**（split_mode='delimiter'、用 `\n\n`）
- 窗口大小：`window_size=3`、步長：`step_size=1`
- 演算法：滑動窗口 + 計 depth score 找 boundary

### 2.4 node type 處理

**`_process_content` 處理對象（L85-137）**：
- `type=='text'` 是唯一被「切」+「合」的對象（L107 / L139）
- 其他 type 從 L85 內 `for item in content:` 通過 `else: result.append(item)`（L137）原樣 pass-through

**`_merge_small_text_blocks` 跨類型行為（L139-191）**：
- L156：`if item['type'] == 'text':` → 進合併邏輯
- L177：`else: # 遇到非文本块` → **flush 緩衝區 + emit 該 non-text node**

→ **公式（type=='formula'）目前是硬截斷邊界**，導致「text + formula + text」會被切成 3 個獨立 chunk、formula 周圍說明被分離。

### 2.5 doc_type 分支

`grep -nE "doc_type" processor/tiling_processor.py` → **0 處**。

- 當前 tiling_processor 對 doc_type 無感
- 所有 doc_type（academic / resume / slides / news / web / technical / book）走同一條路徑
- pipeline_core `_stage_tiling` (L618-623) 也沒傳 doc_type：
  ```python
  return self.tiling_processor.process(str(input_path), str(output_path))
  ```

### 2.6 上下游

- 上游：`processed.json`（`_stage_json_process` 輸出、JsonProcessor 產出含 `sections[].content[].type` 結構）
- 下游：`tiled.json`（給 `_stage_translate` / `_stage_image_caption` 用）
- pipeline_core stage list 內 tiling 在 `json_process` 後、`translate` 前（L41 STAGE_NAMES）

---

## §3 觀察到的問題與證據

### 3.1 短文 unnecessary TextTiling（子項 A、blueprint §2.1）

**現況**：
- `max_length=2500` 寫死、無 doc_type 區分
- DeHunt 履歷 markdown 約 1.9K 行（依 §2.1 既有 paper sample 推測 < 5000 字實質內容）
- HVDC slides 16 頁 markdown ~7K 行（每頁圖文混合、實質字數可能 < 5000）

**問題**：
- 即使總字數 < 5000、仍跑 `_process_content` 完整流程
- 對 < 500 的 text item 還是會跑 `_merge_small_text_blocks`
- 雖然這條 path 不直接打 embedder（embedder 是 rag_processor 才用）、但走完整流程後 chunk 仍會被切細、增加下游 translate 次數

**影響**：
- 短文跑完 N 個切割 + N 個 translate call、本可 1 個 chunk + 1 個 translate call
- resume / news / web / slides 受益最大

### 3.2 公式破碎（子項 B、blueprint §2.2）

**現況**：
- L156 `if item['type'] == 'text':` 才進 merge 緩衝區
- L177 `else:` → 非 text node 強制 flush + 自己 emit

**範例**：academic paper inline formula
```python
content = [
    {'type': 'text', 'content': 'The energy E is given by'},  # 26 chars < 500
    {'type': 'formula', 'content': 'E = mc^2'},
    {'type': 'text', 'content': 'where m is mass and c is the speed of light.'}  # 45 chars < 500
]
```

**當前行為**：
1. text-1 進緩衝區（短）
2. formula → flush 緩衝區（emit text-1）+ emit formula → **緩衝區清空**
3. text-2 進緩衝區（短）
4. 結束 → emit text-2

→ **3 個獨立 chunk**、「公式說明」被切開、translate 拿不到完整語意上下文。

### 3.3 書籍 RTT 卡死（子項 C、blueprint §2.3）

**現況**：
- `_split_into_sentences` 把長 text 切成句子（L302）
- `_texttiling` 用 `window_size=3` `step_size=1` 滑動（L209）

**書籍範例**（如 `我與你 Martin Buber`）：
- 若整本書某 section text 長 50000 字
- 句子切割後可能 1000+ 句
- 滑動次數約 1000（step=1）
- 每次計 depth score 不打 API、但純 CPU 計算大量、且 _process_content 觸發 _texttiling 嵌套呼叫

**問題**：
- 雖然句子級 depth score 不打 API、但 caller 拿到大量 chunk 後 translate stage 會打大量 LLM call、序列 RTT 累積
- 段落級滑動可大幅降窗口數（80% 減少）

⚠ **未實測**：baron 尚未跑書籍 tiling 實測、§4.3 段落滑動為設計階段、實際提速數字需 B3 落地後驗證

### 3.4 doc_type 無感

`_stage_tiling` 不傳 doc_type、`process()` 無此參數 → 三類短文 / 學術 / 書籍走同條 path、無差異化。

### 3.5 公式拼接字元嚴重 bug（v2 修正 1、🔴 production 必須）

**問題**：本 plan v1 §4.1 / §4.2 內 buffer 合併一律用 `"\n\n"` 連接。對 inline formula 是**毀滅性 bug**：

**範例**：academic paper 內 `"The value of "` + `formula:"x"` + `" is positive."`：
- 應該渲染為單行：`"The value of x is positive."`
- 用 `\n\n` 連接後：
  ```
  The value of

  x

  is positive.
  ```
  → 變 3 個獨立段落、translate 拿到斷裂語意、user 看到崩壞排版

**根因**：v1 helper 對所有 type 一視同仁、無 type-aware 拼接邏輯

**修法**：見 §4.0 新增 `_join_content(prev_type, prev_text, next_type, next_text)` helper、type-aware 差異化拼接

### 3.6 Bypass 重寫 `index` 破壞 md_restore 對齊（v2 修正 2、🔴 production 必須）

**問題**：v1 §4.1 `_bypass_content` 對所有輸出 item 強制 `item_copy['index'] = len(result)`。

**`md_restore_processor.py::_process_section` 對齊機制**：
```python
ordered_items.sort(key=lambda x: (x['index'], x['part']))
```

→ 用原始 `index` 還原 PDF 順序（figure / table / text 該在第幾段）

**重寫後果**：
- 原 PDF 順序：`text[idx=0] | figure[idx=1] | text[idx=2]`
- v1 bypass 後重寫：`text+text[idx=0] | figure[idx=1]`（圖跑到段落後）
- 用戶看到的 final_zh.md：圖片排在文字後、與原 PDF 不一致

**修法**：見 §4.1 修正版——buffer index 取「被合併的第一個 item 原始 index」；non-text item 絕不重寫 index。

### 3.7 公式長度虛高造成截斷（v2 修正 3）

**問題**：LaTeX 源碼字元數 ≠ 視覺密度。

**範例**：`\sum_{i=0}^{n} \alpha_i \cdot \beta_i` = 33 字元 > `min_length=500` 不成立但 ≥ 既有 v1 `_merge_small_text_blocks` 內某些邊界判定的閾值。

**v1 邏輯**：若 text 長度 > min_length（500）→ emit buffer。但 formula 不應走此 size-based 邏輯（即使 LaTeX 字數很長、視覺上仍是 inline 元素、應跟周圍 text 留在同 chunk）

**修法**：見 §4.2 修正版——`type=='formula'` 無條件合進 buffer、不走 size 判定。

### 3.8 段落切割換行符格式差異（v2 修正 4）

**問題**：v1 §4.3 `elements = content_text.split('\n\n')`。

**邊界 case**：
| 輸入 | `\n\n` split | regex `\r?\n\s*\r?\n` split |
|---|---|---|
| `"a\n\nb"`（標準 Unix） | ✅ 切 2 段 | ✅ 切 2 段 |
| `"a\r\n\r\nb"`（Windows）| ❌ 不切 | ✅ 切 2 段 |
| `"a\n \nb"`（多餘空白）| ❌ 不切 | ✅ 切 2 段 |
| `"a\n\t\nb"`（Tab 縮排空行）| ❌ 不切 | ✅ 切 2 段 |

**影響**：MinerU 解析 Windows-encoded PDF 後可能含 `\r\n`、translate 結果偶有 tab 空白行 → v1 切割失敗、長文書籍誤判為「整段一個 chunk」、`_texttiling` 不觸發、書籍提速無效

**修法**：見 §4.3 修正版——`_PARAGRAPH_SPLIT_RE = re.compile(r'\r?\n\s*\r?\n')`

### 3.9 `TILING_MAX_LENGTH` 未 env 化（v2 修正 5）

**問題**：v1 仍沿用 `max_length: int = 2500` 寫死 `__init__` 預設。

**對比既有風格**：
- MODEL-9：`GEMINI_CONNECT_TIMEOUT` / `GEMINI_READ_TIMEOUT` 等 8 個 env override
- MODEL-1+2：`EMBEDDING_OUTPUT_DIMENSIONS` / `RAG_SCORE_THRESHOLD` env override
- MODEL-3 v1：`TILING_BYPASS_CHAR_LIMIT` / `TILING_PARAGRAPH_THRESHOLD` 已 env 化

→ **`max_length` 是 MODEL-3 範圍內**唯一沒 env 化的閾值、不一致

**修法**：見 §4.6 新增——`TILING_MAX_LENGTH = int(os.getenv("TILING_MAX_LENGTH", "2500"))`、`__init__` 從 env 讀預設。

### 3.10 MODEL-8 連動標記（v2 修正 6）

**現況**：MODEL-3 三子項都改 chunk 結構 → 既有 vector store 不相容 → 必須 backfill。

**短期**：用 MODEL-1+2 backfill SOP（pkill → rm-rf vector_store → 重啟）

**長期關聯**：
- MODEL-8（中優先、TODO 內活躍）將提供 `tools/regen_rag.py --all` 自動重 embed
- 書籍場景下、不需重 PDF 解析（30-60 分） / 只重 embed（30 秒-2 分）
- MODEL-3 落地 + MODEL-8 落地 = 書籍可自動化升級 / 不破壞 UX

**plan §9 推薦執行順序**新增：「未來 MODEL-8 落地後、書籍重 tiling 從 30-60 分縮短至 30 秒-2 分」

---

## §4 設計方案

### 4.0 共享 helper `_join_content`（v2 修正 1 核心、所有合併路徑共用）

```python
# tiling_processor.py module-level helper

def _join_content(prev_type: str, prev_text: str,
                  next_type: str, next_text: str) -> str:
    """根據兩個節點的 type 決定拼接字元、防禦 inline formula 排版災難。

    依 plan §3.5 修正 1：
    - text + text → "\\n\\n"（段落分隔）
    - text + formula 或 formula + text → " "（保留 inline、單空格）
    - formula + formula → " "（兩公式相鄰）

    避免「The value of $x$ is positive」被強制斷行成 3 個獨立段落。
    """
    if prev_type == 'text' and next_type == 'text':
        return prev_text + "\n\n" + next_text
    # 含 formula 至少一方、用空格
    return prev_text + " " + next_text
```

**設計重點**：
- module-level helper、`_bypass_content` + `_merge_small_text_blocks` 共用
- type-aware 差異化、防 v1 統一 `\n\n` 災難
- 未來可擴展為「table 用 換行 / image 用 句點」等更細規則、本 commit 先涵蓋 text/formula

### 4.1 短文 Fast-path Bypass（子項 A、B1 commit、含修正 1 + 修正 2）

**目標**：總字數 < `MAX_BYPASS_LENGTH`（預設 5000）時、跳過 TextTiling 切割、每個 section 內 text items 簡單合成單一 chunk。

**改動 1：`settings.py` 新增常數**
```python
# Phase 4.7? MODEL-3 B1: 短文 tiling bypass 上限
# Gemini 3.5 Flash 65k 輸出解鎖、短文整篇進 translate 不用切
TILING_BYPASS_CHAR_LIMIT = int(os.environ.get("TILING_BYPASS_CHAR_LIMIT", "5000"))
```

**改動 2：`tiling_processor.py` 擴 `process()` 簽名 + 加 bypass 邏輯**
```python
def process(self, input_path: str, output_path: str, doc_type: str = '') -> Path:
    self.logger.info(f"开始处理JSON文件: 从 {input_path} 到 {output_path} (doc_type={doc_type!r})")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # B1: 估算總字數、決定是否 bypass
    total_chars = self._estimate_total_chars(data)
    if total_chars < TILING_BYPASS_CHAR_LIMIT:
        self.logger.info(
            f"[tiling bypass] doc_type={doc_type!r} 總字數 {total_chars} < "
            f"{TILING_BYPASS_CHAR_LIMIT}、跳過 TextTiling 切割"
        )
        if 'sections' in data:
            self._bypass_sections(data['sections'])
    else:
        if 'sections' in data:
            self.logger.info(f"开始处理文档sections，共 {len(data['sections'])} 个section")
            self._process_sections(data['sections'])

    ...
```

**新增 helper**：
```python
def _estimate_total_chars(self, data) -> int:
    """估算 sections 內所有 text item 總字數"""
    total = 0
    def walk(sections):
        nonlocal total
        for s in sections:
            if s.get('type') in ('abstract', 'references'):
                continue
            for item in s.get('content', []):
                if item.get('type') == 'text':
                    total += len(item.get('content', ''))
            if s.get('children'):
                walk(s['children'])
    walk(data.get('sections', []))
    return total


def _bypass_sections(self, sections):
    """Bypass 模式：每個 section 內 text/formula 合併為單一 chunk、其他原樣
    pass-through。標記 tiling_method='bypass' 為未來除錯方便。
    """
    for section in sections:
        if section.get('type') in ('abstract', 'references'):
            continue
        if 'content' in section:
            section['content'] = self._bypass_content(section['content'])
        if section.get('children'):
            self._bypass_sections(section['children'])


def _bypass_content(self, content):
    """單 section 內：合併相鄰 text+formula、保留其他 type 與原始 index。

    v2 修正 1：用 _join_content 差異化拼接、防 inline formula 排版災難
    v2 修正 2：保留原始 index、不重寫；確保 md_restore_processor 對齊正確
              （ordered_items.sort(key=lambda x: (x['index'], x['part'])) 依靠原始順序）
    """
    result = []
    buffer = None
    buffer_first_index = None  # 記錄被合併的第一個 item 的原始 index

    for item in content:
        item_type = item.get('type')

        if item_type in ('text', 'formula'):
            if buffer is None:
                buffer = item.copy()
                buffer_first_index = item.get('index', 0)
                buffer['part'] = 0
                buffer['tiling_method'] = 'bypass'
            else:
                # v2 修正 1：用 _join_content 而非寫死 \n\n
                buffer['content'] = _join_content(
                    buffer.get('type', 'text'),
                    buffer.get('content', ''),
                    item_type,
                    item.get('content', '')
                )
        else:
            # non-text/formula：硬截斷 + 保留原始 index
            if buffer is not None:
                buffer['index'] = buffer_first_index  # v2 修正 2
                result.append(buffer)
                buffer = None
                buffer_first_index = None
            item_copy = item.copy()
            item_copy['part'] = 0
            # v2 修正 2：絕不重寫 item_copy['index']、保留原始
            result.append(item_copy)

    if buffer is not None:
        buffer['index'] = buffer_first_index  # v2 修正 2
        result.append(buffer)

    return result
```

**caller 更新（`pipeline_core.py:623`）**：
```python
def _stage_tiling(self, pdf_path, paper_dir, paper_name, output_paths):
    input_path = output_paths.get('json_process')
    if not input_path:
        raise ValueError("未找到 JSON 文件")
    output_path = self._get_stage_output_path('tiling', paper_dir, paper_name)
    doc_type = output_paths.get('_confirmed_doc_type', 'academic')
    return self.tiling_processor.process(str(input_path), str(output_path), doc_type=doc_type)
```

⚠ `process()` 加 `doc_type=''` **預設值**保 caller 後相容；B1 commit 同步更新 `_stage_tiling` 傳入。

### 4.2 公式穿透合併（子項 B、B2 commit）

**目標**：`_merge_small_text_blocks` 把 formula 從 hard-boundary 改為 soft-type、允許 `text + formula + text` 連續合併。

**改動：`_merge_small_text_blocks`（L139-191）改寫**（含 v2 修正 1 / 修正 3）
```python
# 模組頂部新增常數
SOFT_TYPES_FOR_MERGE = frozenset({'text', 'formula'})
HARD_BOUNDARY_TYPES_FOR_MERGE = frozenset({'table', 'heading', 'image_caption'})


def _merge_small_text_blocks(self, content):
    """合并相邻的小文本块（含 formula 穿透合併）；
    遇到 table / heading / image_caption 等硬邊界時截斷、避免破壞語意完整性。

    v2 修正 1：合併用 _join_content 差異化（text+formula 用空格、text+text 用 \\n\\n）
    v2 修正 3：type=='formula' 無論長度都合進 buffer、不觸發 size-based flush
              （LaTeX 字元數虛高、不應因「大文本」邏輯截斷上下文）
    """
    if not content:
        return content

    result = []
    current_buffer = None

    for item in content:
        item_type = item.get('type')

        # v2 修正 3：formula 無條件合併（不走 size 判定）
        if item_type == 'formula':
            text = item.get('content', '')
            if current_buffer is None:
                current_buffer = item.copy()
            else:
                # v2 修正 1：差異化拼接
                current_buffer['content'] = _join_content(
                    current_buffer.get('type', 'text'),
                    current_buffer.get('content', ''),
                    'formula', text
                )
            continue

        if item_type == 'text':
            text = item.get('content', '')
            if len(text) < self.min_length:
                # 小 text、合進 buffer
                if current_buffer is None:
                    current_buffer = item.copy()
                else:
                    # v2 修正 1：差異化拼接
                    current_buffer['content'] = _join_content(
                        current_buffer.get('type', 'text'),
                        current_buffer.get('content', ''),
                        'text', text
                    )
            else:
                # 大 text、合 buffer 後 emit
                if current_buffer is not None:
                    current_buffer['content'] = _join_content(
                        current_buffer.get('type', 'text'),
                        current_buffer.get('content', ''),
                        'text', text
                    )
                    result.append(current_buffer)
                    current_buffer = None
                else:
                    result.append(item)
        else:
            # 硬邊界（table / heading / image_caption / 其他 unknown）
            if current_buffer is not None:
                result.append(current_buffer)
                current_buffer = None
            result.append(item)

    if current_buffer is not None:
        result.append(current_buffer)

    return result
```

**注意**：
- `_process_content` 內 L107 `if item['type'] == 'text'` 也要擴成 `if item['type'] in SOFT_TYPES_FOR_MERGE`、讓 formula > max_length 也能走切割（罕見、但邊界一致）
- 合併後的 buffer `type` 保持原 type（第一個 item 的 type、通常是 'text'）；下游 translate 處理 buffer 仍依 'text' 規則跑

### 4.3 段落級滑動（子項 C、B3 commit）

**目標**：長文（總字數 > `TILING_PARAGRAPH_THRESHOLD`、預設 30000）時、TextTiling 滑動單元從句子改段落、降 80% 滑動次數。

**改動 1：`settings.py` 新增常數 + `tiling_processor.py` 加 regex（v2 修正 4）**
```python
# settings.py
# Phase 4.7? MODEL-3 B3: 段落級滑動觸發閾值（書籍 / 長論文）
TILING_PARAGRAPH_THRESHOLD = int(os.environ.get("TILING_PARAGRAPH_THRESHOLD", "30000"))

# tiling_processor.py module 頂部
import re
# v2 修正 4：容錯 Windows \r\n / 多餘空白
_PARAGRAPH_SPLIT_RE = re.compile(r'\r?\n\s*\r?\n')
```

**改動 2：`_process_content` 內加 doc-level 切換**
```python
def _process_content(self, content, total_chars_hint=0):
    """處理 content 列表 + 合併分割文字塊。
    B3：若 total_chars_hint > TILING_PARAGRAPH_THRESHOLD、長文模式（段落級滑動）。
    """
    # B2: 已含 formula 穿透合併
    content = self._merge_small_text_blocks(content)

    for idx, item in enumerate(content):
        item['index'] = idx
        item['part'] = 0

    long_doc_mode = total_chars_hint > TILING_PARAGRAPH_THRESHOLD

    result = []
    for item in content:
        if item.get('type') in SOFT_TYPES_FOR_MERGE and len(item.get('content', '')) > self.max_length:
            original_index = item.get('index', 0)
            content_text = item['content']

            if long_doc_mode and _PARAGRAPH_SPLIT_RE.search(content_text):
                # B3 段落級：regex 切分、容錯 Windows \r\n / 多餘空白（v2 修正 4）
                elements = _PARAGRAPH_SPLIT_RE.split(content_text)
                elements = [e.strip() for e in elements if e.strip()]
                split_mode = 'paragraph'
            elif '\n\n' in content_text:
                elements = content_text.split('\n\n')
                split_mode = 'delimiter'
            else:
                elements = self._split_into_sentences(content_text)
                split_mode = 'sentence'

            segments = self._texttiling(elements, split_mode)

            # 標記 tiling_method
            for i, segment_text in enumerate(segments):
                new_block = item.copy()
                new_block['content'] = segment_text
                new_block['index'] = original_index
                new_block['part'] = i
                new_block['tiling_method'] = split_mode  # bypass / paragraph / delimiter / sentence
                result.append(new_block)
        else:
            item_with_method = item.copy()
            item_with_method.setdefault('tiling_method', 'passthrough')
            result.append(item_with_method)
    return result
```

**改動 3：`_process_sections` 傳 total_chars_hint**
```python
def _process_sections(self, sections, total_chars_hint=0):
    for section in sections:
        if section.get('type') in ('abstract', 'references'):
            continue
        if 'content' in section:
            section['content'] = self._process_content(section['content'], total_chars_hint=total_chars_hint)
        if section.get('children'):
            self._process_sections(section['children'], total_chars_hint=total_chars_hint)
```

**`process()` 內順傳**：
```python
total_chars = self._estimate_total_chars(data)
if total_chars < TILING_BYPASS_CHAR_LIMIT:
    # B1 bypass
    self._bypass_sections(data['sections'])
else:
    self._process_sections(data['sections'], total_chars_hint=total_chars)
```

### 4.4 slides 按頁合併（blueprint §2.4、整合到 B1）

slides processor 既有按頁產出 `## 第 N 頁` heading + 每頁 markdown block。`_create_vector_store` 在 rag_processor 已用 H1 切（slides 一律 H2 = section heading）；本 commit **不額外動 slides**——確認既有 slides processor + tiling_processor 行為 OK 即可。

⚠ **盤點驗證**：slides 走 tiling_processor 後是否仍按頁分隔？若 slides 因 `_merge_small_text_blocks` 跨頁合併、需在 B1 加 slides 特例不合併。**Plan §8 Q9 列為 open question**。

### 4.6 `TILING_MAX_LENGTH` env 化（v2 修正 5）

對齊 MODEL-9 / MODEL-1+2 / MODEL-3 既有 env override 風格、補上 `max_length` 唯一遺漏項。

**改動 1：`settings.py` 新增常數**
```python
# Phase 4.7? MODEL-3 修正 5: tiling_processor max_length env 化
# 對齊 TILING_BYPASS_CHAR_LIMIT / TILING_PARAGRAPH_THRESHOLD 風格
TILING_MAX_LENGTH = int(os.environ.get("TILING_MAX_LENGTH", "2500"))
```

**改動 2：`tiling_processor.py::__init__`**
```python
from settings import TILING_MAX_LENGTH

class TilingProcessor:
    def __init__(self,
                 min_length: int = 500,
                 max_length: int = None,  # v2 修正 5：None → 從 env 讀預設
                 window_size: int = 3,
                 step_size: int = 1,
                 embedder=None):
        self.min_length = min_length
        self.max_length = max_length if max_length is not None else TILING_MAX_LENGTH
        ...
```

**設計重點**：
- 後相容：caller 顯式傳 `max_length=N` 仍會生效（測試 fixture 友善）
- env override：`export TILING_MAX_LENGTH=5000` 即時調、不用 commit
- 對齊 MODEL-3 系列三常數：`TILING_BYPASS_CHAR_LIMIT` / `TILING_MAX_LENGTH` / `TILING_PARAGRAPH_THRESHOLD` 三段閾值依序成立 `BYPASS < MAX < PARAGRAPH`（5000 < 2500 < 30000？需 baron 確認語意一致）

⚠ 注意：`TILING_MAX_LENGTH` 預設 2500 < `TILING_BYPASS_CHAR_LIMIT` 預設 5000 的「文件總字數 vs 單 chunk 字數」**不同語意**——一個是「整篇 < 5000 字 → bypass」、一個是「單 text item > 2500 字 → 切」。命名上需在 settings.py / 註解標清楚以免混淆。

### 4.7 落地策略總覽（拆 3 commits、對齊 MODEL-1+2 B1/B2 模式）

| Commit | 子項 | 檔案 | 行數 | 風險 |
|---|---|---|---|---|
| **B1 短文 Bypass** | A + slides 確認 | `tiling_processor.py` + `settings.py` + `pipeline_core.py` (`_stage_tiling` +1 行傳 doc_type) | +60 / -5 | 🟢 低（純加 path、既有 path 走原邏輯） |
| **B2 公式穿透** | B | `tiling_processor.py`（改 `_merge_small_text_blocks` + 加 SOFT_TYPES 常數） | +30 / -20 | 🟡 中（改既有合併邏輯、需 pytest 守住既有行為） |
| **B3 段落滑動** | C | `tiling_processor.py`（加 long_doc_mode 切換 + `tiling_method` 標籤）+ `settings.py` | +25 / -3 | 🟡 中（需實測書籍才驗證） |

**推薦 3 commits（baron 補充 B 推薦答案）**：
- B1 立即可 ship（最低風險、價值大、跟 MODEL-1+2 backfill 同批做就好）
- B2 改既有合併邏輯需 pytest 守住既有行為、單獨拆 commit 易 revert
- B3 段落滑動依賴實測、可單獨延後（baron 跑書籍後再決定 BOOK_THRESHOLD）

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 緩解 |
|---|---|---|
| Bypass 短文跳 TextTiling、影響檢索粒度 | 🟢 低 | 短文本來檢索就是「整篇 vs 查詢」、bypass 不會更差；rag_processor 仍按 H1 切 chunk |
| `MAX_BYPASS_LENGTH=5000` 是否合適 | 🟡 中 | env override（`TILING_BYPASS_CHAR_LIMIT`）、baron 可調 |
| 公式穿透後合併 buffer 過大、超過 `max_length` 2500 | 🟢 低 | `_process_content` L107 後續切割仍會把 > max_length 的 buffer 切細 |
| 公式穿透改變既有 academic chunk 結構、vector store 不相容 | 🔴 必清重建 | 與 MODEL-1+2 同：依 backfill SOP（pkill → rm -rf → 重啟）；**未來 MODEL-8 落地後可自動化此 backfill**（v2 修正 6） |
| **Bypass 重寫 `index` 破壞 md_restore 對齊**（v1 隱性 bug） | 🔴 高、production 必須 | **v2 修正 2**：保留原始 index、buffer 取被合併的第一個 item 的 index、non-text 絕不重寫；§4.1 已修 |
| **公式 `\n\n` 連接破壞 inline 排版**（v1 隱性 bug） | 🔴 高、production 必須 | **v2 修正 1**：`_join_content(prev_type, prev_text, next_type, next_text)` helper、type-aware 差異化拼接；§4.0 + §4.1 + §4.2 已修 |
| **公式 LaTeX 字元數虛高造成 buffer flush** | 🟡 中 | **v2 修正 3**：`type=='formula'` 無條件合進 buffer、不走 size 判定；§4.2 已修 |
| **Windows `\r\n` 段落切割失敗** | 🟡 中 | **v2 修正 4**：`_PARAGRAPH_SPLIT_RE = re.compile(r'\r?\n\s*\r?\n')` regex split；§4.3 已修 |
| **`max_length` 寫死 2500 不一致 env 風格** | 🟢 低 | **v2 修正 5**：`TILING_MAX_LENGTH` env 化；§4.6 已修 |
| `BOOK_THRESHOLD=30000` 是否合適 | 🟡 中 | env override（`TILING_PARAGRAPH_THRESHOLD`）+ 實測書籍後調 |
| 段落判定用 `\n\n` 可能不精準（依 processed.json 結構）| 🟡 中 | 看 processed.json 內每個 text node 是否已是「一段」、若是直接用 node-level；若否 fallback `\n\n` split |
| 段落滑動跟既有 TextTiling 演算法整合 | 🟢 低 | 滑動單元改變（元素長度變大）、演算法 `_texttiling` 不變 |
| 三子項互相影響 | 🟢 低（拆 commits） | 每 commit 後 pytest 驗證、有問題單獨 revert |
| `_stage_tiling` 加 doc_type 參數、其他 caller 是否破 | 🟢 低 | `process(input_path, output_path, doc_type='')` 預設值保後相容 |
| slides 跨頁合併破壞按頁結構 | 🟡 中 | §8 Q9 — 實作時看 slides 行為、必要時加 doc_type='slides' 特例 |

---

## §6 測試與 E2E 驗證計畫

### 6.1 單元測試（新增、依拆 commit 分檔）

#### `tests/test_tiling_bypass.py`（B1、5-6 個 test）

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_bypass_under_5000_chars` | data 總字數 4000 → 走 bypass、chunk count = section count |
| 2 | `test_no_bypass_over_5000_chars` | 6000 字 → 走原 `_process_sections` |
| 3 | `test_bypass_resume_doc_type` | doc_type='resume' + 短文 → bypass、metadata 含 tiling_method='bypass' |
| 4 | `test_bypass_passthrough_non_text_types` | section 含 table / image_caption → bypass 模式下保留原 type、不合進 buffer |
| 5 | `test_bypass_merges_text_formula_continuous` | bypass 模式下 `text + formula + text` 合成單一 chunk |
| 6 | `test_env_override_bypass_char_limit` | `TILING_BYPASS_CHAR_LIMIT=3000` 生效 |
| **7** | **`test_inline_formula_preserved_with_space_join`**（v2 修正 1）| `text + formula + text` 合併用空格 + `text + text` 合併用 `\n\n` |
| **8** | **`test_bypass_preserves_image_table_original_index`**（v2 修正 2）| 原 PDF `text[idx=0] / figure[idx=1] / text[idx=2]` bypass 後 figure 仍 `index=1`、不被重寫 |

#### `tests/test_tiling_formula.py`（B2、5 個 test）

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_text_formula_text_merged` | 小 text + small formula + small text → 單一 chunk |
| 2 | `test_table_breaks_buffer` | text + table + text → 3 個獨立 chunks |
| 3 | `test_heading_breaks_buffer` | text + heading + text → 3 個獨立 chunks |
| 4 | `test_formula_only_section_handled` | 整 section 只有 formulas → 合併成 1 個 chunk |
| 5 | `test_image_caption_treated_as_hard_boundary` | text + image_caption + text → 3 個 chunks |
| **6** | **`test_long_formula_does_not_break_buffer`**（v2 修正 3）| 1KB LaTeX formula 不觸發 buffer flush、與周圍 text 留在同 chunk |

#### `tests/test_tiling_paragraph.py`（B3、5 個 test）

| # | 測試 | 驗證 |
|---|---|---|
| 1 | `test_sentence_level_when_under_threshold` | 20000 字 → split_mode='sentence' 或 'delimiter'、不是 'paragraph' |
| 2 | `test_paragraph_level_when_over_threshold` | 35000 字 → split_mode='paragraph' |
| 3 | `test_paragraph_detection_from_newlines` | 長 text 含 `\n\n` 分段 → 段落級正確切 |
| 4 | `test_env_override_paragraph_threshold` | `TILING_PARAGRAPH_THRESHOLD=10000` 生效 |
| 5 | `test_paragraph_count_reduction_vs_sentence` | mock 同一份 50K 字長文、段落級 chunks < 句子級 chunks |
| **6** | **`test_paragraph_split_handles_windows_line_ending`**（v2 修正 4）| `"a\r\n\r\nb"` regex split 切成 2 段 |
| **7** | **`test_paragraph_split_handles_extra_whitespace`**（v2 修正 4）| `"a\n \nb"` / `"a\n\t\nb"` 切成 2 段 |

#### `tests/test_tiling_env_overrides.py`（B1-B3 共用、**1 個 test**、v2 修正 5）

| # | 測試 | 驗證 |
|---|---|---|
| **1** | **`test_env_override_tiling_max_length`**（v2 修正 5）| `TILING_MAX_LENGTH=5000` 生效（`__init__(max_length=None)` → 從 env 讀預設）|

**tests 數量總計**：v1 16 → **v2 22**（B1: 6→8 / B2: 5→6 / B3: 5→7 + env overrides 共用檔 1）

### 6.2 E2E 手動驗證（baron OrcStack）

依 MODEL-1+2 backfill SOP（plan §4.4 三步驟）：

```bash
# 1. 停 web_server
pkill -f "web_server.py" && sleep 1

# 2. 清舊 vector store + tiled.json（B1-B3 改 chunk 結構）
rm -rf output/*/*/vector_store/
rm -f output/*/*/*_tiled.json

# 3. 重啟 + 重新觸發 tiling stage
nohup venv/bin/python web_server.py > /tmp/webserver_console.log 2>&1 &

# 4. 對既有 paper 重跑 pipeline.process(stages=['tiling', 'translate', 'image_caption', 'md_restore', 'extra_info', 'rag'])
# 或重新上傳 1 份各類型 paper（resume + academic + slides + 長文書籍）
# 觀察 logs/pipeline.log:
grep "tiling bypass" logs/pipeline.log     # B1 短文 bypass 觸發
grep "paragraph" logs/pipeline.log         # B3 段落級觸發
grep "tiling_method" output/*/*/*_tiled.json | head  # metadata 標籤
```

### 6.3 完整回歸

```bash
venv/bin/pytest tests/ -q
# 預期：185 baseline + 22 新增（v2、含修正 1/2/3/4/5 新增 6 個 test）= 207 passed, 3 skipped
```

---

## §7 不可做 / 不可動清單

- ❌ `pipeline_core.py`：**僅 1 行**改（`_stage_tiling` 傳 doc_type）；其他完全不動
- ❌ `web_server.py`：未動
- ❌ `processor/*` 除 `tiling_processor.py` 外（md_processor / json_processor / rag_processor / md_restore_processor 等）：未動
- ❌ `config.py` / `llm/*`（含 MODEL-1+2 EmbeddingModel + MODEL-9 共享 client）：未動
- ❌ `static/*` / DB / 前端：未動
- ❌ vector store schema / FAISS distance strategy：未動
- ❌ chunk 既有 metadata keys（index / part / content / type 等）：未動（**只加 `tiling_method` 新 key**）
- ❌ MinerU SCP（MODEL-10）/ MODEL-8 SQLite paper_chunks：未動
- ❌ `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` / `templates/*`：未動
- ❌ 既有 plan / 執行 / hotfix 報告：未動
- ❌ commit / push：未動
- ✅ 可動（本 plan 範圍、v2 含 6 修正）：
  - `processor/tiling_processor.py`：加 Bypass + soft-types + paragraph 切換 + `tiling_method` 標籤 + **`_join_content` module-level helper（v2 修正 1）** + **`_PARAGRAPH_SPLIT_RE` regex（v2 修正 4）** + **`__init__(max_length=None)` 從 env 讀預設（v2 修正 5）**
  - `settings.py`：加 `TILING_BYPASS_CHAR_LIMIT` + `TILING_PARAGRAPH_THRESHOLD` + **`TILING_MAX_LENGTH`（v2 修正 5）**
  - `pipeline_core.py`：`_stage_tiling` 加 1 行傳 doc_type
  - **新增** `tests/test_tiling_bypass.py`（B1、8 tests、含 v2 修正 1/2 新 case）
  - **新增** `tests/test_tiling_formula.py`（B2、6 tests、含 v2 修正 3 新 case）
  - **新增** `tests/test_tiling_paragraph.py`（B3、7 tests、含 v2 修正 4 兩個新 case）
  - **新增** `tests/test_tiling_env_overrides.py`（v2 修正 5、1 test）
  - **新增** 3 個執行報告 + 本 plan

---

## §8 Open Questions（待 baron 決策）

| # | 問題 | 推薦答案 |
|---|---|---|
| Q1 | 拆 1 commit（合併）還是 3 commits（B1/B2/B3）？ | ✅ **3 commits** — 跟 MODEL-1+2 B1/B2 模式對齊、易 revert、B1 最大 ROI 可獨立先 ship |
| Q2 | `TILING_BYPASS_CHAR_LIMIT` 預設 5000？ | ✅ **5000**（依 blueprint §2.1、Gemini 3.5 Flash 65k 輸出能力支撐） |
| Q3 | `TILING_PARAGRAPH_THRESHOLD` 預設 30000？ | **30000**（推測值、待 baron 實測書籍後調整；可先 ship、env override） |
| Q4 | 段落判定用 `\n\n` 還是更精細？ | **看 processed.json 結構決定** — 若每個段落已是獨立 text node、用 node-level；若整段塞同一 text node 用 `\n\n` split；本 plan 假設後者 |
| Q5 | chunk metadata 是否標記 `tiling_method`？ | ✅ **要**：`'bypass'` / `'paragraph'` / `'delimiter'` / `'sentence'` / `'passthrough'`、為未來除錯 + RAG-3 校準分析方便 |
| Q6 | 同一份 paper 改 chunk 結構後既有 vector store 怎辦？ | 短期：手動清重建（MODEL-1+2 backfill SOP）；長期：MODEL-8 SQLite paper_chunks 解 |
| Q7 | 公式穿透實作位置：放 chunk_buffer 邏輯內還是獨立 pre-process？ | ✅ **`_merge_small_text_blocks` 內**（§4.2）— 與 hard boundary 邏輯同處、單一來源、最少改動 |
| Q8 | 段落邊界判定要 LLM 還是規則？ | ✅ **規則** — node-level paragraph（若 processed.json 已切）或 `\n\n` split；不引入 LLM call、零 cost |
| Q9 | slides 按頁合併是否同 commit 內做？ | **B1 內驗證** — 先看既有 tiling_processor 對 slides 是否破壞按頁；若破壞、加 `if doc_type == 'slides': bypass_per_page` 特例；若 OK 不動 |
| Q10 | 段落級實際提速？ | **未實測** — B3 落地後實測 `我與你 Martin Buber` 或同等書籍；plan 估 80% 滑動次數減少 |
| **Q11**（v2）| `TILING_MAX_LENGTH` 預設 2500 還是別的？ | **2500 + env override**（v2 修正 5）— 對齊既有 caller 行為、書籍實測後可 `export TILING_MAX_LENGTH=5000` 動態調 |

---

## §9 推薦執行順序

1. **本輪結束**：baron 過目本 plan + Q1-Q10 推薦答案、特別確認：
   - Q1 拆 3 commits
   - Q2 5000 字上限
   - Q3 30000 字段落閾值（可先 ship 等實測調）
2. **下一輪 MODEL-3 B1 commit**（~3 小時、短文 Bypass）：
   - `tiling_processor.py` 加 `process(doc_type='')` + `_estimate_total_chars` + `_bypass_sections` + `_bypass_content`
   - `settings.py` 加 `TILING_BYPASS_CHAR_LIMIT`
   - `pipeline_core.py` `_stage_tiling` 加 1 行傳 doc_type
   - 新增 `tests/test_tiling_bypass.py`（5-6 tests）
   - pytest → 預期 185 → 190-191 passed
3. **下一輪 MODEL-3 B2 commit**（~3 小時、公式穿透）：
   - `tiling_processor.py` 加 `SOFT_TYPES_FOR_MERGE` / `HARD_BOUNDARY_TYPES_FOR_MERGE` 常數 + 改 `_merge_small_text_blocks`
   - 新增 `tests/test_tiling_formula.py`（5 tests）
   - pytest → 預期 190-191 → 195-196 passed
4. **下一輪 MODEL-3 B3 commit**（~4 小時、段落滑動）：
   - `tiling_processor.py` 加 `_process_content(total_chars_hint=0)` + `long_doc_mode` 切換 + `tiling_method` 標籤
   - `settings.py` 加 `TILING_PARAGRAPH_THRESHOLD`
   - 新增 `tests/test_tiling_paragraph.py`（5 tests）
   - pytest → 預期 195-196 → 200-201 passed
5. **baron OrcStack 端 backfill**（依 MODEL-1+2 SOP）：
   - 清 vector store + tiled.json、重啟 web_server
   - 對 1 份各類型 paper 觸發 pipeline 重跑 tiling 後續 stage
   - 觀察 `[tiling bypass]` / `tiling_method` log
6. **未來**：實測書籍（如 `我與你 Martin Buber`）+ 校準 `TILING_PARAGRAPH_THRESHOLD` / `TILING_MAX_LENGTH`
7. **未來 MODEL-8 落地後**（v2 修正 6 連動）：書籍重 tiling 從重 PDF 30-60 分縮短至**從 paper_chunks 表讀 raw text 重 embed 30 秒-2 分**；本 MODEL-3 改 chunk 結構不再需要全 PDF 重解析

---

## §10 結尾簡短說明

### 三個子項是否互相獨立？

✅ **完全正交、可獨立 ship**：
- **A 短文 Bypass**：純加 `total_chars < 5000` 快速路徑、不影響既有 `_process_sections` / `_process_content` 邏輯
- **B 公式穿透**：改 `_merge_small_text_blocks` 內 type 判定（hard → soft）、`_process_content` 內 type 判定也擴；與 A 無交集（A 走 bypass 不進此 path）
- **C 段落滑動**：改 `_process_content` 內 `split_mode` 選擇邏輯；與 B 無交集（B 改的是 buffer 合併、C 改的是切割模式）

### 推薦拆 commit 策略

**B（3 commits）**——對齊 MODEL-1+2 B1/B2 成功模式：
- B1 最大 ROI + 最低風險 → 先 ship、立即受益
- B2 改既有邏輯、需 pytest 守住 → 單獨 revert 友好
- B3 依賴實測 → 可單獨延後（baron 跑書籍後再決定 threshold）

### 主要風險

| 風險 | 影響 |
|---|---|
| 既有 vector store 不相容 | 🔴 必清重建（同 MODEL-1+2、用 backfill SOP） |
| 段落判定規則 | 🟡 依 processed.json 實際結構決定（Q4） |
| slides 跨頁合併破壞按頁結構 | 🟡 Q9 實作時驗證、必要時加 doc_type='slides' bypass |
| `BOOK_THRESHOLD=30000` 待實測校準 | 🟡 env override、實測後調 |

### 預估工時

**~1.5 天 / 3 commits**：
- B1：3 小時（含 pytest + caller 改）
- B2：3 小時（含 pytest）
- B3：4 小時（含 pytest + 設計 long_doc_mode 切換）
- baron OrcStack backfill + 驗證：每 commit 30 分

### 是否要先做小範圍實測？

**baron 是否要先實測 BOOK_THRESHOLD？**

**推薦：不需要前置實測、直接拆 3 commits ship**：
- B1 對短文（resume / news / web）立即受益、與書籍實測無關
- B2 對 academic 立即受益、與書籍實測無關
- B3 即使 BOOK_THRESHOLD 預設 30000 不精準、env override 可調；先 ship 設計再實測校準效率更高

若 baron 想保守、**可只先做 B1 + B2**（最確定的 7 小時、覆蓋 resume + academic）、B3 等實測書籍後再做。

---

## §11 不可動清單遵守狀態（plan 階段）

- [x] 業務檔（`tiling_processor.py` / `settings.py` / `pipeline_core.py` / 其他 `processor/*`）：**未動**（只 view / grep）
- [x] `.claude-logs/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md` / `templates/*`：**未動**
- [x] 既有 plan / 執行 / hotfix 報告（含 MODEL-1+2 / MODEL-9）：**未動**
- [x] DB / 設定 / 前端：**未動**
- [x] commit / push：**未動**
- [x] `TODO.md`：**未動**（保留 🔵 plan 中狀態）
- [x] 本報告為新增唯一檔
