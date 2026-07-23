# FITZ-ANCHOR LLM錨定前移與fitz幾何整形 — Tasks

> 本文件為 FITZ-ANCHOR 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-23_FITZ-ANCHOR_LLM錨定前移與fitz幾何整形_plan.md`（v2、六 OQ 全拍板）產出，含 3 個 Commit（C1 / C2 / C_CHECKOUT）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | — |
| **修改檔案** | 7 個 | `processor/fitz_processor.py`（U4 ε 容差去重、U5 比例重複門檻、U3 sidecar 寫端移除）／`pipelines/litedoc_pipeline.py`（U1 錨定前移、U2 標題回注、U3 hints 讀端與參數清理）／`pipelines/section_engine.py`（U6 echo 長度比守衛）／`settings.py`（`LITEDOC_ANCHOR_MAX_PAGES`＋`FITZ_DEDUP_EPSILON` 兩常數）／`.env.example`（兩常數註記）／`tests/test_fitz_processor.py`（U4/U5/U3 移除測試＋§3.1 模擬轉 fixture）／`tests/test_litedoc_pipeline.py`（U1/U2/U3 移除/U6 測試＋§7.2 整合） |
| **目錄初始化** | 0 個 | — |
| **狀態更新** | 2 個 | `TODO.md`／`prompts/INDEX.md` |
| **Commits** | 3 個 | C1 → C2 → C_CHECKOUT |
| **baton 歸檔** | 1 次 | C_CHECKOUT 收官：`mv` plan → `plans/`、本 tasks → `tasks/`、C1/C2 執行報告 → `executions/` + 逐檔 `git add` |

> 註（對提示詞 §0.5 草稿之更正）：草稿列 5 檔、漏 `settings.py`／`.env.example`——plan §2 U1（`LITEDOC_ANCHOR_MAX_PAGES`）與 U4（ε settings 常數可調）明文要求、據實補列。

---

## §1 TL;DR（概要）

- **挑戰**：fitz 快速道三輪 hotfix 失手全屬「幾何啟發式猜錯重要性」類（標題被當浮水印/頁首、lede 被當回聲）；NHK E2E 四症狀（標題全滅／QA Q×4 攪爛／「史上初」段被跨頁規則誤殺／lede 被 echo 子字串誤吃）。
- **解法**：兩個開發 commit——**C1 — Fitz Geometry Refinement（fitz 幾何整形與容差去重）**：U4 ε 容差同位去重＋U5 跨頁重複比例門檻、§3.1 模擬表全項轉 fixture；**C2 — Meta Anchor & Title Reinjection（LLM 錨定前移、標題回注與 sidecar 退場）**：U1 錨定前移（既有 cover-prompt 換吃前 1-2 頁裸文字、零新增呼叫）＋U2 標題回注 promote-else-inject＋U3 HOTFIX-3 K2 sidecar 生產/消費端同刀退場＋U6 echo 長度比守衛；**C_CHECKOUT（收官歸檔）**。
- **影響範圍**：BE-Refactor、僅 litedoc 路供給端（`fitz_processor`／`litedoc_pipeline`／`section_engine` 一行）＋兩常數；A 軌／resume／slides／engine／image_filter／md_cleaner 零改。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `processor/fitz_processor.py` | L248 `dedup_key = (text, round(y0,1), round(x0,1), round(size,1))` 精確 key；L397 `len(hit) >= 2` 跨頁門檻；L35 `_URL_RE`＋L181 sidecar 寫端＋L362 URL 捕捉（HOTFIX-3 K2） | 精確 key 被描邊 ±0.84pt 擊穿（NHK 標題 4→3、log `(3 次)`；section 標題 `(4 次)` 全 miss）；≥2 頁門檻誤殺 2/10 頁重複之內容段；sidecar 管線待退場 |
| `pipelines/litedoc_pipeline.py` | L274 `hints=self._load_source_hints(...)`＋L480 `_load_source_hints`（K2 讀端）；L503 `_extract_litedoc_metadata(markdown_text, hints="")` 吃 knives 絞完的 md 文首（L64 `_META_INPUT_CHARS=4000`） | meta 錨定輸入受損（垃圾進垃圾出）；無標題回注保底；K2 讀端待退場 |
| `pipelines/section_engine.py` | L622 `if sa == sb or sa in sb or sb in sa:`（`_title_echo_match` 子字串分支） | 「大谷翔平」(4字) ⊂ lede (88字) 誤判回聲整行剝除 |
| `settings.py` | L138-144 LITEDOC_FITZ 區塊 | 缺 `LITEDOC_ANCHOR_MAX_PAGES`／`FITZ_DEDUP_EPSILON` 兩常數 |
| `tests/` | fitz/litedoc 測試基線（993 passed 起算、以現碼實跑為準） | 缺 ε 去重/比例門檻/錨定/回注/退場/守衛測試與 §3.1 模擬 fixture |

---

## §3 觀察問題

### 問題 #1：精確 key 同位去重被描邊偏移擊穿
- **證據**：`processor/fitz_processor.py:248`；NHK 源 PDF 實測標題 4 副本 x0＝`45.2417/46.0770×2/46.9122`（±0.84pt）→ round 後三 key → 收 4→3 → `WATERMARK_HEADING_THRESHOLD=3` 照殺（log `(3 次)` 鐵證）；6 個 section 標題 `(4 次)`＝一份未收。
- **影響**：標題與全部 section 標題滅失 → 1 section → whole mode → P2/滑窗/RAG 粒度全塌；QA 區 Q 行（×4）殘骸攪爛 Q/A 流。

### 問題 #2：跨頁重複門檻 ≥2 頁誤殺內容段
- **證據**：`processor/fitz_processor.py:397`；NHK「史上初」段 p2/p5 重複（2/10 頁）、前兩行 y0=40.6/63.1 落頂 band（<67）→ 被當 chrome 殺頭、留孤兒 `めてです。`×2；chrome 實際分布 SpaceX 23/23、NHK 10/10。
- **影響**：真內容段落殘缺、whole-mode 譯文出現無頭句。

### 問題 #3：meta 錨定輸入受損 + 無標題保底
- **證據**：`pipelines/litedoc_pipeline.py:503` 輸入＝knives 絞完 md 文首；NHK 實跑 P1 log `title='大谷翔平' publisher='' authors=0`（cover-prompt 只能撈 date 行尾 tag）。
- **影響**：標題/譯題/檔名/PDF Title 全鏈錯；每個新版式＝一輪新 hotfix（打地鼠結構性根源）。

### 問題 #4：echo 子字串分支誤吃 lede
- **證據**：`pipelines/section_engine.py:622` `sb in sa`；「大谷翔平」⊂ lede 88 字行 → 整行剝除（K3 先移 date 行後 echo 首匹配滑至 lede 之連鎖）。
- **影響**：文首導語滅失。

### 問題 #5：HOTFIX-3 K2 sidecar 管線冗餘
- **證據**：`fitz_processor.py:35/181/362`＋`litedoc_pipeline.py:274/480`；U1 錨定改吃裸文字後、chrome URL 天然在輸入內（NHK 頁尾 `https://news.web.nhk/...` 實證）。
- **影響**：兩套 publisher 來源共存＝判讀歧義＋外部檔案依賴（plan §9 Q3 拍板同案移除）。

---

## §4 設計方案

### §4.1 C1 — Fitz Geometry Refinement（fitz 幾何整形與容差去重）

U4：`_collect_page` 去重由精確 key 改 ε 容差聚類（同頁同 `(text, round(size,1))` 群、`|Δx0|≤ε 且 |Δy0|≤ε` 判重繪副本；`FITZ_DEDUP_EPSILON=3.0` settings 常數）；U5：`_repeated_band_keys` 門檻 `len(hit) >= 2` 改 `>= max(2, ceil(len(pages) * 0.5))`。每頁獨立、跨頁職責不變。測試含 §3.1 模擬表全項轉 fixture（plan §9 Q6）。

### §4.2 C2 — Meta Anchor & Title Reinjection（LLM 錨定前移、標題回注與 sidecar 退場）

U1：新增 `_read_anchor_text(pdf_path, max_pages)`（fitz 裸抽前 `LITEDOC_ANCHOR_MAX_PAGES=2` 頁、異常回 ""）、`_extract_litedoc_metadata` 輸入改「錨定文字非空 ? 錨定文字 : 現行 md 文首」（fail-open 等價）；U2：P1 ②'（cleaner/連字/R7 後、③ analyze 前）標題回注三分支（heading 已在→不動／正文行→就地升級 `# `／缺席→頂部注入）＋ warning 告警；U3：sidecar 生產端（fitz L35/L181/L362）與消費端（litedoc L274/L480、`hints` 參數）同刀移除；U6：`_title_echo_match` 子字串分支加 `min(len)/max(len) >= 0.5` 守衛。§7.2 整合測試隨本 commit。

### §4.3 C_CHECKOUT — Checkout（收官歸檔）

Conformance＋§7.2 整合測試確認＋baton 一次性 mv（plan→plans/、tasks→tasks/、C1/C2 報告→executions/）＋逐檔 git add 白名單＋checkout 執行報告＋TODO 雙層結案。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 錨定 LLM 誤判 title → 回注錯 heading | 🟡 中 | temp=0＋裸文字含完整版面線索；promote-else-inject 不產生重複標題；回注即告警可觀測；E2E 雙樣本把關 |
| U4 誤合 3pt 內合法重複文字 | 🟢 低 | 同頁同文同級且距 ≤3pt＝視覺重疊、無正當版式如此排；ε settings 可調 |
| U5 比例門檻改變既有剝除行為 | 🟢 低 | `max(2,…)` 下限保 2 頁件等價；SpaceX 23/23、NHK 10/10 chrome 遠超 50% |
| U3 移除後 publisher 回歸 | 🟢 低 | 裸文字含同一 URL、同 rule 1 解碼（NHK 輸入面更完整；SpaceX body 自帶 URL 零差異）；C2 測試含 publisher 斷言 |
| C1/C2 同檔（fitz_processor）分次改動 staging 混雜 | 🟢 低 | 各 commit 各自 `.bak`、commit 前 `git diff --cached --name-only` 白名單自檢（CHECKOUT-GUARD 鐵律） |
| MinerU 路／A 軌回歸 | 🟢 低 | 錨定屬輸入改善＋fallback 等價；`pdf_processor`／`pipeline_core` byte 不動；全套件回歸 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
grep -n "FITZ_DEDUP_EPSILON" settings.py processor/fitz_processor.py        # 期望：settings 定義 + fitz 消費
grep -n "dedup_key = (text, round" processor/fitz_processor.py              # 期望：零命中（精確 key 已廢）
grep -n "max(2, " processor/fitz_processor.py                               # 期望：_repeated_band_keys 比例門檻命中
env PYTHONPATH=. venv/bin/pytest tests/test_fitz_processor.py -q            # 期望：全綠（含 ±0.84pt ×4→1 / 3pt 外保留 / 2/10 頁內容段存活 / 10/10 chrome 照殺 / §3.1 fixture）
env PYTHONPATH=. venv/bin/pytest -q                                         # 期望：基線不退、0 failed
```

### §6.2 C2 驗收

```bash
grep -n "_read_anchor_text\|LITEDOC_ANCHOR_MAX_PAGES" pipelines/litedoc_pipeline.py settings.py   # 期望：雙命中
grep -rn "_load_source_hints\|source_hints" pipelines/ processor/ --include="*.py"                # 期望：零命中（U3 兩端退場）
grep -n "hints" pipelines/litedoc_pipeline.py | grep _extract_litedoc_metadata                    # 期望：零命中（單參數恢復）
grep -n "標題回注\|_reinject_title\|promote" pipelines/litedoc_pipeline.py                         # 期望：U2 回注器命中
grep -n "0.5" pipelines/section_engine.py | grep -n "echo\|ratio\|len"                            # 期望：U6 守衛命中
env PYTHONPATH=. venv/bin/pytest tests/test_litedoc_pipeline.py tests/test_section_engine.py -q   # 期望：全綠
env PYTHONPATH=. venv/bin/pytest -q                                                               # 期望：全綠、§7.2 整合含在內
```

### §6.3 SOP 一致性核查（BE-Refactor 落地前強制、兩 commit 各自實貼）

```bash
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" <各修改 .py>   # 規則：logger.error 必含 exc_info=True
grep -nE "\.commit\(\)" <各修改 .py> | grep -v "with .*session.*begin\(\)"      # 規則：裸 commit 零命中（本案零 DB、應「無命中（合規）」）
```

---

## §7 不可動清單

**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] cover-prompt `_LITEDOC_META_SYSTEM_PROMPT` 六欄 schema 與 Rules（U1 只換輸入來源）
- [ ] `processor/md_cleaner.py` 浮水印規則本體／`WATERMARK_HEADING_THRESHOLD`
- [ ] HOTFIX-3 **K3**（`_strip_meta_source_lines` 行級歸零、含其 echo-strip/R8 前時序）
- [ ] `pipelines/image_filter.py`／`pipelines/ingestion_engine.py`／`processor/rag_indexer.py`／`contracts.py`
- [ ] `pipelines/section_engine.py` 除 U6 一行守衛外全部（`strip_title_echo` 主體/`classify_source_lang` 等零改）
- [ ] `PDFParser` ABC 簽名／`processor/pdf_processor.py`（MinerU impl）／`pipeline_core.py`／A 軌全鏈／resume／slides／book
- [ ] `LITEDOC_FITZ_ENABLED` 等既有旗標語意（新常數純加法）
- [ ] 母提示詞／DB schema／API 簽名

---

## §8 推薦 Commit 拆分

### C1 — Fitz Geometry Refinement（fitz 幾何整形與容差去重）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `processor/fitz_processor.py`／`settings.py`／`.env.example`／`tests/test_fitz_processor.py`＋各自 `.bak`（`archive/2026-07-23_FITZ-ANCHOR_C1_*.bak`） |
| **安全性** | 🟢 高 — 純幾何整形、確定性零 LLM；U4 收斂面經 §3.1 離線模擬全量驗證（標題+section 樹+14 組 QA 復活、零誤殺）；U5 有 `max(2,…)` 下限保短件等價 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；`LITEDOC_FITZ_ENABLED=false` 另有整路 env 降級 |
| **驗收 grep 條件** | 本檔 §6.1 全項＋§6.3 SOP 雙 grep 實貼 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `settings.py`：LITEDOC_FITZ 區塊（L138-144 附近）純加法新增 `FITZ_DEDUP_EPSILON = float(os.getenv("FITZ_DEDUP_EPSILON", "3.0"))`＋行註（同位重繪容差、pt）；`.env.example` fitz 區塊補註解行 `# FITZ_DEDUP_EPSILON=3.0`。② `fitz_processor.py` `_collect_page`（L244-255 K1 區塊改造）：廢精確 `dedup_key`；改群組容差——`groups: Dict[Tuple[str, float], List[Tuple[float, float]]]`、group key＝`(text, round(size,1))`、對群內已保留 `(x0,y0)` 逐一比 `abs(dx)<=eps and abs(dy)<=eps`（`eps=settings.FITZ_DEDUP_EPSILON`、模組頂 import settings 已有則沿用；若 fitz_processor 現無 import settings 則函式內讀避免模組級耦合——以現碼為準）命中即 `continue`（debug log 沿用 K1 訊息格式）、未命中 append 群組並收行；**每頁獨立初始化**（K1 既有語意、docstring 更新為 FITZ-ANCHOR U4 並保留「不越權跨頁 R2」句）。③ `_repeated_band_keys`（L383-397）：`import math`（檔頂已有 statistics、加 math）、回傳行改 `need = max(2, math.ceil(len(pages) * 0.5))` ＋ `len(hit) >= need`；docstring 補比例門檻依據（chrome 全頁 vs 內容少數頁、NHK 2/10 反例錨）。④ `tests/test_fitz_processor.py`：新增 `TestOverlapDedupEpsilon`（±0.84pt ×4 fixture→恰 1 份／3pt 外同文保留／每頁獨立）＋`TestBandRatioThreshold`（10 頁 chrome 10/10 殺、內容 2/10 留、2 頁件行為等價）＋`TestSimulationFixture`（§3.1 模擬轉正式：fitz 現造描邊 ×4 標題與 Q 行 PDF → 經真 `MarkdownCleaner` 後標題 heading 存活 ×1、QA 成對、`(N 次)` 浮水印剝除零觸發）；既有 K1 精確 key 測試依新語意改寫（留 FITZ-ANCHOR 註記）。⑤ 修改前先產 `.bak` ×2（fitz_processor/test）入 archive/。 |

### C2 — Meta Anchor & Title Reinjection（LLM 錨定前移、標題回注與 sidecar 退場）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `pipelines/litedoc_pipeline.py`／`processor/fitz_processor.py`（U3 寫端移除）／`pipelines/section_engine.py`（U6 一行＋守衛註）／`settings.py`／`.env.example`／`tests/test_litedoc_pipeline.py`／`tests/test_section_engine.py`／`tests/test_fitz_processor.py`（U3 寫端測試移除）＋各自 `.bak` |
| **安全性** | 🟡 中 — 涉 LLM 輸入切換與回注，但三重保險：fail-open 全鏈（錨定空→現行輸入 byte 等價、回注跳過）、promote-else-inject 防重複標題、回注告警可觀測；U3 退場經 C2 publisher 斷言把關 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾（U3 移除之 sidecar 代碼隨 revert 復活、無資料遷移） |
| **驗收 grep 條件** | 本檔 §6.2 全項＋§6.3 SOP 雙 grep 實貼 |
| **依賴關係** | C1（U2 回注測試建立在幾何整形後的穩定 md 上；U4 fixture 為 §7.2 整合前段） |
| **具體實作細節** | ① `settings.py`：新增 `LITEDOC_ANCHOR_MAX_PAGES = int(os.getenv("LITEDOC_ANCHOR_MAX_PAGES", "2"))`＋行註（meta 錨定裸抽頁數、baron 拍板 1-2 頁）；`.env.example` 補 `# LITEDOC_ANCHOR_MAX_PAGES=2`。② litedoc **U1**：新增 `_read_anchor_text(pdf_path) -> str`（`fitz.open` 逐頁 `get_text("text")` 取前 `settings.LITEDOC_ANCHOR_MAX_PAGES` 頁 `"\n".join`；任何異常 `logger.warning(exc_info=True)` 回 `""`）；P1 呼叫點（現 L272 附近 `meta = self._extract_litedoc_metadata(markdown_text, hints=...)`）改 `anchor = self._read_anchor_text(ctx.pdf_path)`＋`meta = self._extract_litedoc_metadata(anchor if anchor.strip() else markdown_text)`；`_extract_litedoc_metadata`（L503）**恢復單參數**、內部 `[:_META_INPUT_CHARS]` 截斷語意不變、docstring 更新（輸入＝錨定裸文字優先/md 文首 fallback、FITZ-ANCHOR U1）。③ litedoc **U2**：新增 `_reinject_title(md_path, title) -> None`——正規化（`re.sub(r"\s+","",…).casefold()`）比對：掃 md 行、(a) 存在 `#` 開頭且正規化相等 → return；(b) 存在正文行正規化相等 → 該行就地改寫為 `f"# {原行文字}"`（promote）＋`logger.warning("[FITZ-ANCHOR] 標題回注 case=promote …")`；(c) 全文缺席 → `md.write_text(f"# {title}\n\n" + 原文)`（inject）＋ warning `case=inject`；title 空白 → 直接 return；接線於 P1 ②'（R7 之後、③ `DocAnalyzer().analyze` 之前、`markdown_text` 重讀之前——回注後重讀 markdown_text 保下游同基準）。④ **U3 退場**（生產/消費端同刀）：fitz_processor 刪 L35 `_URL_RE`、L181 sidecar 寫檔塊、L362 URL 捕捉塊與 `chrome_urls` 收集；litedoc 刪 L480 `_load_source_hints` 全函式與 L274 `hints=` 接線（②已含）；同步刪兩測試檔對應測試（sidecar 產出/加載/截斷窗注入——以 FITZ-ANCHOR 註記標記刪因）。⑤ **U6**：`section_engine.py` L622 子字串分支改 `if sa == sb or ((sa in sb or sb in sa) and min(len(sa),len(sb)) / max(len(sa),len(sb)) >= 0.5):`＋行註（FITZ-ANCHOR U6、4字⊂88字反例錨）；`SequenceMatcher` 分支不動。⑥ 測試：U1（錨定非空→捕 messages 斷言含裸文字/chrome URL 行；空→fallback 現行輸入 byte 等價；頁數截斷）／U2（三分支＋告警＋title 空跳過＋回注後 sidecar 行號基準：analyze 在回注後跑）／U3（§6.2 歸零 grep 之測試化＋publisher 經錨定輸入仍可解斷言）／U6（0.045 比不判回聲、整行≈標題照剝）／**§7.2 跨 Phase 整合**（fitz 現造「描邊 ×4 標題＋2/N 頁重複段＋全頁 chrome＋頁尾 URL」PDF → 真 FitzProcessor（C1 幾何）→ 真 cleaner → mock 錨定 LLM 回 meta → U2 回注 → 真 `_build_tiles` → 真 `run_phase3` 素材鏈——斷言標題 heading 存活、QA 成對、內容段完整、meta 零重播、key-changing PDF→md→tiles）。⑦ 修改前 `.bak`（litedoc/section_engine/fitz/三測試檔）入 archive/。 |

### C_CHECKOUT — Checkout（收官歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv`：baton plan → `plans/`、本 tasks → `tasks/`、C1/C2 執行報告 → `executions/`；新增 `executions/2026-07-XX_FITZ-ANCHOR_checkout_執行.md`；`TODO.md`／`archive/TODO_done_archive.md` 雙層結案；`prompts/` 本案提示詞入版控 |
| **安全性** | 🟢 高 — 純歸檔零代碼 |
| **可逆性** | 🟢 高 — 檔案搬移可逆 |
| **驗收 grep 條件** | `ls .claude-logs/baton/ | grep FITZ-ANCHOR` 期望零殘留；`git diff --cached --name-only` ＝宣告白名單全等（多一檔/少一檔即停） |
| **依賴關係** | C1、C2 均已 ship（hash 可回填） |
| **具體實作細節** | 依 WORKFLOW_SOP §3 收官三鐵律：Conformance 驗收（plan v2 §2 U1-U6 對照 C1/C2 報告＋§7.2 整合測試存在且通過、缺則不得判 🟢）→ baton 3-Phase 自檢（Provenance/Schema/Non-destructive/Scope）→ 一次性 `mv`＋逐檔 `git add`（嚴禁 `git add .`／`-A`／目錄）→ staged-set 自檢實貼 → checkout 執行報告（§8 一行 commit 指令＋msg 草稿 `/tmp/FITZ-ANCHOR_checkout_msg.txt`）→ TODO 雙層結案＋hash 自癒佔位。 |

---

## §9 Open Questions

無。（plan v2 六 OQ 已全數拍板：Q1 `LITEDOC_ANCHOR_MAX_PAGES=2` 常數／Q2 fail-open 全鏈／Q3 U3 同案同 commit 移除／Q4 U6 帶守衛／Q5 MinerU 路同享（A 軌零碰之精度勘誤已註）／Q6 模擬 harness 入 tests。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 FITZ-ANCHOR 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 FITZ-ANCHOR executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動業務代碼（本階段）；嚴禁跨 Commit 混檔；嚴禁自動 `git commit` / `git push`；各 commit `.bak` 強制入 `git add` 清單 |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；設計脈絡唯一源＝plan v2；全局硬規則唯一源＝CLAUDE.md |

### §99.2 Revision 歷程

- v1 (2026-07-23)：初版拆分完成——C1 幾何整形（U4/U5）／C2 錨定前移+回注+sidecar 退場（U1/U2/U3/U6）／C_CHECKOUT；§0.5 對提示詞草稿補列 settings/.env.example 兩檔（plan U1/U4 常數要求）
