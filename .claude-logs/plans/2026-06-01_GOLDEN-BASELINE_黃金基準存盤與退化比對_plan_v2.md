# GOLDEN-BASELINE 黃金基準存盤與退化比對 plan

> 在 PIPE 大改版動工的第一微秒，於**舊單體系統（A 軌）**對五路代表性文檔跑完整流程並凍結產物為「黃金基準（Golden Baseline）」；建立 Diff 比對工具與 0% 退化判準，作為新核心（B 軌）每打通一路即比對、Diff 0% 退化才准 Flip the Switch 的唯一驗收基準。本 plan 為純規格定義，不含 commit 拆分。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 大改版以「影子並行縱向五路絞殺」漸進落地（PIPE plan §2 U10），每打通一路必須證明「排版 0% 退化、譯文 0% Regression、RAG 召回不劣化」才准 Flip。但目前**無任何客觀基準**可比對——舊單體產物未凍結存盤、無 Diff 工具、無量化判準，「0% 退化」無從驗收。
- **解法**：建立 GOLDEN-BASELINE 機制——(1) **存盤 Phase**：在改版動工前，於舊單體對五種 `doc_type` 各一份代表性文檔跑完整流程，將三維度產物（排版雙語 Markdown／翻譯 JSON／固定 query set 的 RAG 召回）凍結為不可變黃金快照 + checksum；(2) **比對 Phase**：每路打通後對同一文檔跑新核心 shadow，以 Diff 引擎比對候選產物 vs 黃金快照，輸出三維度量化 Diff 報告；(3) **判準**：定義三維度 0% 退化的可量化通過條件與紅綠燈裁決，紅燈物理阻擋 Flip。
- **影響**：**不改任何業務代碼**（純讀舊系統產物 + 新增工具與資料）。新增 `tools/golden_baseline.py`（存盤 + 比對雙子命令）；新增不可變快照目錄 `tests/golden_baseline/`（測試固定資料集 PDF + 凍結產物 + checksum）；新增 Diff 報告輸出至 `report/golden_baseline/`；新增 `tests/test_golden_baseline.py` 驗證比對引擎邏輯。無 DB Schema 變動、無 API 簽名變動、無 runtime 主鏈影響。

---

## §2 目標規格

> 以下為本機制必須達到的「最終狀態」規格（What it should be），可量化檢驗。實作細節（如何寫）屬 tasks 階段。

### U1. 五路代表性文檔固定資料集
- 對應五條策略管線各挑**一份**代表性文檔，凍結為永久測試集（PDF 原檔入版控於 `tests/golden_baseline/fixtures/`）：

  | 代表文檔 | doc_type | 對應管線 | 三維度驗收重點 |
  |---|---|---|---|
  | 學術論文 | academic | AcademicPipeline | Section 結構／References 不誤翻／公式區塊 |
  | 書籍（節選） | book | BookPipeline | 章節滾動摘要／Sliding Window 連貫性 |
  | 簡報 | slides | SlidePipeline | 圖片 alt 對齊／無雙重 Caption |
  | 履歷 | resume | ResumePipeline | 技能詞保護（Go/C++/AI 不誤殺）／聯絡資訊 |
  | 短文（news/web） | litedoc | LiteDocPipeline | 15k 閥門前後排版／publisher 解碼 |

- 固定資料集**一經凍結即不可變更**（變更須走本 plan §0 改版 + baron 核准 + 重新存盤），確保跨路次比對基準一致。

### U2. 三維度黃金產物存盤規格
- 每份文檔在舊單體跑完後，凍結以下三維度產物為黃金快照（對齊 PIPE-SPEC §1 四份合約的 user-facing 終態）：
  - **D1 排版雙語 Markdown**：`final_{name}_zh.md` + `final_{name}_en.md`（對應 PIPE-SPEC 合約③ `BilingualMarkdownSpec`）。
  - **D2 翻譯結構 JSON**：`final_{name}_rag_tree.json`（保留 Section/Tile 結構與譯文對照，對應合約②衍生）。
  - **D3 RAG 召回結果**：對每份文檔附一組**固定 query set**（3–5 條，入版控），記錄各 query 的 top-k 召回 chunk ID 集合 + raw score（對應 PIPE-SPEC 合約④）。
- 每份黃金快照附 **SHA-256 checksum 清單**（`manifest.json`），存盤時計算、比對時驗證快照未被竄改。

### U3. Diff 引擎三維度比對規格
- 比對引擎對「候選產物（新核心 shadow）vs 黃金快照」逐維度量化：
  - **D1 排版 Diff**：正規化後（去除時間戳／`_shadow` ID／` (測試)` 後綴等已知影子雜訊）比對 Markdown **結構樹**（heading 階層／table 行列數／list 項數／image alt 文字）。退化定義＝結構節點增刪或 alt 文字不符。
  - **D2 譯文 Diff**：逐 Section 比對譯文，計算相似度（建議 token 級 ratio）。退化定義＝相似度 < 門檻（§7 Q2 待定 0.95）或 Section 數量不符。
  - **D3 RAG 召回 Diff**：同一 query 下，比對 top-k 召回 chunk 集合的 **Jaccard 重疊度** + score 排序。退化定義＝重疊度 < 門檻（§7 Q2 待定 0.90）或命中 chunk 集合縮減。
- Diff 結果輸出**雙格式**：機器可讀 `diff_report.json`（供 CI／後續自動化）+ 人類可讀 `diff_report.md`（供 baron 複核）。

### U4. 0% 退化紅綠燈裁決規格
- 單路裁決：該路代表文檔三維度全部 PASS → **綠燈（該路准 Flip 候選）**；任一維度 FAIL → **紅燈（物理阻擋該路 Flip）**。
- 全案 Flip 前置：五路全綠才允許 PIPE-FLIP 啟動（本 plan 只產出裁決訊號，實際 Flip 動作屬 PIPE-FLIP plan）。
- **預期改善豁免通道**：若 Diff 顯示差異源於新核心修復舊 bug（如舊雙 Caption、舊摘要時序錯誤），非退化而是改善 → 標記 `improvement_pending_review`，經 baron 複核核准後**更新黃金快照**為新基準（§7 Q3）。

### U5. 程式流程與判斷（Program Flow & Decision）

#### §2.5.1 存盤 Phase 流程（`golden_baseline.py capture`）
```
START capture(doc_type | --all)
  │
  ├─ 1. 載入固定資料集 PDF（tests/golden_baseline/fixtures/<doc_type>.pdf）
  │     └─[判斷] PDF 不存在？ ──► FAIL FAST「資料集缺檔」、終止
  │
  ├─ 2. 呼叫舊單體 A 軌 PipelineCore（shadow=False）跑完整 11-stage
  │     └─[判斷] pipeline 回傳 FAILED？ ──► FAIL「基準不可用」、記錄 stage、終止
  │
  ├─ 3. 收集三維度產物 D1/D2/D3
  │     ├─ D1 讀 final_*_zh.md / final_*_en.md
  │     ├─ D2 讀 final_*_rag_tree.json
  │     └─ D3 對 fixed query set 逐條呼叫 retrieve_with_context、記 top-k chunk+score
  │     └─[判斷] 任一維度產物缺漏？ ──► FAIL「產物不完整」、列缺項、終止
  │
  ├─ 4. 計算各檔 SHA-256，寫 manifest.json
  │
  └─ 5. [判斷] 該 doc_type 黃金快照已存在？
          ├─ 是 + 無 --force ──► ABORT「快照已存在、防覆寫」（保護不可變性）
          └─ 否 / 有 --force ──► 凍結寫入 tests/golden_baseline/golden/<doc_type>/
        END（綠燈：基準已存盤）
```

#### §2.5.2 比對 Phase 流程（`golden_baseline.py diff`）
```
START diff(doc_type)
  │
  ├─ 1. [判斷] 黃金快照存在？ ──► 否 ──► FAIL FAST「無基準可比、請先 capture」、終止
  │
  ├─ 2. 驗證 manifest checksum
  │     └─[判斷] checksum 不符？ ──► FAIL「基準被竄改、拒絕比對」、終止
  │
  ├─ 3. 呼叫新核心 B 軌 PipelineCore(shadow=True) 跑同一 PDF → 候選產物
  │     └─[判斷] 新核心 FAILED？ ──► FAIL「候選不可用」、記 Phase/Stage、終止
  │
  ├─ 4. 正規化候選與黃金產物（剝離 _shadow / (測試) / 時間戳雜訊）
  │
  ├─ 5. 逐維度 Diff
  │     ├─ D1 排版結構樹比對 ──► degraded? PASS/FAIL
  │     ├─ D2 譯文相似度比對 ──► sim < 門檻? PASS/FAIL
  │     └─ D3 RAG 召回 Jaccard ──► overlap < 門檻? PASS/FAIL
  │
  ├─ 6. [判斷] 三維度彙總
  │     ├─ 全 PASS ──► 綠燈 verdict=PASS
  │     ├─ 任一 FAIL 且屬已知改善 ──► verdict=IMPROVEMENT_PENDING_REVIEW（待 baron）
  │     └─ 任一 FAIL 且為退化 ──► 紅燈 verdict=FAIL（阻擋 Flip）
  │
  └─ 7. 輸出 diff_report.json + diff_report.md → report/golden_baseline/<doc_type>_<ts>/
        END
```

### U6. 資料流程（Data Flow）

```
┌─────────────────────── 存盤 Phase（改版動工前、一次性）────────────────────────┐
│                                                                                  │
│  tests/golden_baseline/fixtures/<doc_type>.pdf  （固定資料集、入版控、不可變）   │
│             │                                                                    │
│             ▼                                                                    │
│   舊單體 A 軌 PipelineCore(shadow=False)  ──11 stage──►  output/<paper>/         │
│             │                                                                    │
│             ├─ D1  final_*_zh.md / final_*_en.md                                 │
│             ├─ D2  final_*_rag_tree.json                                         │
│             └─ D3  fixed query set × retrieve_with_context → {chunk_ids, scores} │
│             │                                                                    │
│             ▼  凍結 + SHA-256                                                     │
│   tests/golden_baseline/golden/<doc_type>/{D1,D2,D3,manifest.json}（不可變黃金）│
└──────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │  （每路打通後觸發）
                                  ▼
┌─────────────────────── 比對 Phase（每路絞殺後）──────────────────────────────┐
│                                                                                │
│   同一 fixtures/<doc_type>.pdf                                                  │
│             │                                                                  │
│             ▼                                                                  │
│   新核心 B 軌 PipelineCore(shadow=True) ──四 Phase──► output/<paper>_shadow/   │
│             │                                                                  │
│             ▼  收集候選 D1/D2/D3 → 正規化（剝 _shadow/(測試)/時間戳）          │
│        candidate {D1',D2',D3'}                                                 │
│             │                                                                  │
│   golden {D1,D2,D3} ──┐                                                        │
│   candidate {D1',D2',D3'} ──► Diff 引擎（D1 結構樹／D2 相似度／D3 Jaccard）    │
│             │                                                                  │
│             ▼                                                                  │
│   report/golden_baseline/<doc_type>_<ts>/{diff_report.json, diff_report.md}   │
│             │                                                                  │
│             ▼                                                                  │
│   verdict ∈ {PASS 綠燈, FAIL 紅燈, IMPROVEMENT_PENDING_REVIEW}                 │
│             └─► PASS×5 → 解鎖 PIPE-FLIP 前置；FAIL → 阻擋該路 Flip            │
└────────────────────────────────────────────────────────────────────────────┘
```

- **資料不可變鐵律**：黃金快照（`golden/`）一旦寫入即唯讀，僅 `--force`（baron 核准）或 IMPROVEMENT 複核通過才可重寫；候選產物（`output/*_shadow/`）由既有 `delete_paper` 清理，不污染基準。
- **零業務耦合**：本機制只**讀取**舊/新核心既有產物與既有 `retrieve_with_context`，不注入任何 hook 至主鏈。

### U7. 產出物明確定義（Deliverables）

> 本計畫落地後**必須且僅產出**以下資產；任何超出此清單的改動均屬越界，須走 §0 改版。三表分列：① 本計畫交付物（自建）、② 消費不交付（讀既有真理源）、③ 明確不產出（零越界保證）。

#### ① 本計畫交付物（self-built）

| 交付物 | 類型 | 內容定義 | 歸屬路徑 |
|---|---|---|---|
| **Golden Baseline 工具** | 可執行 CLI | `capture` 子命令（存盤 Phase：跑舊單體→收 D1/D2/D3→SHA-256→凍結）＋ `diff` 子命令（比對 Phase：跑新核心 shadow→正規化→三維度 Diff→紅綠燈裁決→雙格式報告）；支援 `--all` / `--force` 旗標 | `tools/golden_baseline.py` |
| **不可變黃金快照集** | 凍結測試資產 | 五路固定資料集 PDF（`fixtures/<doc_type>.pdf`）＋ 各 doc_type 三維度凍結產物（`golden/<doc_type>/{D1 雙語 md, D2 rag_tree.json, D3 fixed_queries+召回結果}`）＋ checksum 清單（`manifest.json`） | `tests/golden_baseline/fixtures/`＋`tests/golden_baseline/golden/<doc_type>/` |
| **三維度 Diff 報告** | 工具產出（每次比對） | 機器可讀 `diff_report.json`（D1 結構樹差／D2 相似度／D3 Jaccard＋verdict）＋ 人類可讀 `diff_report.md`（供 baron 複核），時間戳分目錄不覆寫 | `report/golden_baseline/<doc_type>_<ts>/` |
| **比對引擎單元測試** | pytest | 驗證 D1 結構樹比對／D2 相似度／D3 Jaccard／正規化等價／判斷分支（缺基準 fail fast、checksum 拒比、紅綠燈彙總、improvement 豁免） | `tests/test_golden_baseline.py` |

#### ② 消費不交付（讀既有真理源、零改動）

| 消費對象 | 提供方 | 消費方式 |
|---|---|---|
| 舊單體 11-stage 產物（`final_*_zh/en.md`／`final_*_rag_tree.json`／`vectors/`） | `pipeline_core.py L191-209`（既有） | 純讀，存盤 Phase 收 D1/D2 來源 |
| RAG 單篇召回入口 `retrieve_with_context` | `rag_retriever.py L92`（既有） | 純呼叫取結果，D3 召回基準與候選比對 |
| 影子候選清理 `delete_paper` | `web_server.py`（既有 API） | 沿用既有 API 清 `output/*_shadow/`，不另寫清理邏輯 |
| 新核心四 Phase shadow 產物 | B 軌 PipelineCore（PIPE-CORE 交付） | 純讀候選 D1/D2/D3，正規化後進 Diff |

#### ③ 明確不產出（零越界保證）

| 不產出項 | 保證 |
|---|---|
| **零 DB Schema 變動** | 本機制資料全落檔案系統（`tests/golden_baseline/`＋`report/`），不新增任何 `models.py` 表/欄位 |
| **零 API 簽名變動** | 不改 `retrieve_with_context` / `delete_paper` / `list_papers` / `get_paper` 任一既有簽名 |
| **零 runtime 主鏈 hook** | 不在 `pipeline_core.py` 11-stage 或四 Phase 主鏈注入任何 capture/diff 觸發點，純離線工具旁路執行 |
| **零環境變數新增** | 門檻數值（D2 ≥0.95／D3 ≥0.90）經 baron 核准後寫死於工具常數，不引入新 env |
| **零硬編碼路徑外溢** | 所有讀寫限於 `tests/golden_baseline/`＋`report/golden_baseline/`，不觸碰業務 `output/` 既有結構（僅讀） |

---

## §3 現況與證據

詳細盤點與本機制相關的現有產物路徑與調用鏈：

- **`pipeline_core.py`**：
  - `_get_stage_output_path L191-209`：定義既有產物路徑——`final_{name}_en.md` / `final_{name}_zh.md`（L197-198，D1 來源）、`final_{name}_rag_tree.json`（L203，D2 來源）、`vectors/`（L204，D3 FAISS 物理庫）。本機制純讀這些既有產物、零改動。
  - `STAGE_NAMES L40-43`：舊單體 11-stage，存盤 Phase 完整跑完此鏈得黃金產物。
- **`rag_retriever.py`**：
  - `retrieve_with_context L92`：單篇召回入口（owner_id, query, paper_id, top_k），D3 固定 query set 逐條呼叫之、記錄 top-k chunk + score。
  - `retrieve_multi_with_context L184`：多篇召回（本機制單檔基準暫不用，列為 §7 Q4 評估）。
- **`web_server.py`**：
  - `delete_paper`（既有 API）：影子候選產物 `output/*_shadow/` 經此清理，本機制不另寫清理邏輯。

### §3.1 grep 鋼鐵證據

```bash
grep -nE "final_.*_en|final_.*_zh|rag_tree|vectors" pipeline_core.py
# 197:                'en': paper_dir / f"final_{paper_name}_en.md",
# 198:                'zh': paper_dir / f"final_{paper_name}_zh.md"
# 203:                'tree_json': paper_dir / f"final_{paper_name}_rag_tree.json",
# 204:                'vector_store': paper_dir / "vectors"

grep -nE "def retrieve" rag_retriever.py
# 92:    def retrieve_with_context(self, owner_id: int, query: str, paper_id: str, top_k: int = 5) -> str:
# 184:    def retrieve_multi_with_context(

grep -nE "STAGE_NAMES" pipeline_core.py
# 40:STAGE_NAMES = [
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本機制中嚴禁任何改動：**

- [ ] **`pipeline_core.py` 舊單體 11-stage 與 `_get_stage_output_path`**：本機制只**讀取**其產物，嚴禁為了存盤而改動主鏈或產物路徑。
- [ ] **`rag_retriever.py` `retrieve_with_context` 簽名與檢索演算法**：D3 召回只呼叫既有入口取結果，不得改其檢索邏輯。
- [ ] **既有 `delete_paper` / `list_papers` / `get_paper` API**：影子候選清理沿用既有 API，零改動。
- [ ] **`models.py` 既有 Schema**：本機制資料全落於檔案系統（`tests/golden_baseline/` 與 `report/`），不新增任何 DB 表/欄位。
- [ ] **固定資料集 `tests/golden_baseline/fixtures/*.pdf` 與已凍結 `golden/`**：凍結後嚴禁無 baron 核准變更，否則跨路次基準失準。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 影子並行／縱向五路絞殺／Golden Baseline Diff 0% 退化才 Flip | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md §3.5 §1` |
| 大改版目標規格（U10 落地戰略、§8 GOLDEN-BASELINE 路線圖定位） | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v6.md §2 U10 §8.3` |
| 四份凍結接口合約（三維度產物對齊終態） | `PIPE-SPEC §1.1`（合約②③④） |
| plan 結構契約與治理規格 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／文件歸屬 | `.claude-logs/ref/WORKFLOW_SOP.md §2 §3 §6` |
| 專案進度治理框架（雙軌制／不可動清單／E2E 驗證） | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 §4` |
| 現況產物路徑／RAG 召回入口 | `pipeline_core.py L191-209`／`rag_retriever.py L92` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**（防 Regression 底線）：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**（`tests/test_golden_baseline.py`）：
  - **D1 排版結構樹比對**：相同 Markdown → diff=0；heading 增刪／table 行列差／alt 文字差 → 偵測為退化。
  - **D2 譯文相似度**：相同譯文 → sim=1.0；Section 數不符／相似度 < 門檻 → FAIL。
  - **D3 RAG 召回 Jaccard**：相同召回集合 → overlap=1.0；命中 chunk 縮減 → FAIL。
  - **正規化**：含 `_shadow` ID／` (測試)` 後綴／時間戳的候選，正規化後與黃金等價。
  - **判斷分支**：缺基準 fail fast、checksum 不符拒比對、三維度彙總紅綠燈裁決、improvement 豁免標記。

### §6.2 手動端到端（E2E）驗證流程

1. **存盤驗證**：對五份固定資料集執行 `golden_baseline.py capture --all`，確認 `tests/golden_baseline/golden/<doc_type>/` 五組三維度產物 + `manifest.json` checksum 齊全。
2. **自比對歸零驗證**：在「新核心尚未動工」狀態下，對舊系統再跑一次同檔 diff，確認三維度 Diff 0%（證明工具本身無偽陽性）。
3. **退化偵測驗證**：人工竄改一份黃金 Markdown（刪一個 heading），跑 diff，確認 D1 正確報紅燈 FAIL。
4. **改善豁免驗證**：模擬新核心修掉舊雙 Caption（候選比黃金少一個重複 Caption），確認 verdict=IMPROVEMENT_PENDING_REVIEW 而非直接 FAIL。
5. **checksum 防竄改驗證**：篡改 manifest 後跑 diff，確認拒絕比對並報錯。
6. **報告產出驗證**：確認 `report/golden_baseline/<doc_type>_<ts>/` 同時產出 `diff_report.json` 與人類可讀 `diff_report.md`。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **黃金快照與固定資料集存放位置** | **`tests/golden_baseline/`（fixtures + golden 同根）；Diff 報告至 `report/golden_baseline/`** | 固定資料集與凍結產物屬「測試基準資產」、與 pytest 同源最直覺；Diff 報告屬工具產出、依 WORKFLOW_SOP §2 歸 `report/`。惟 PDF + 凍結產物體積可能大，是否入 Git 版控或改 Git LFS／外部存儲待 baron 拍板。 |
| **D2 譯文 / D3 召回的退化門檻數值** | **D2 相似度 ≥ 0.95、D3 Jaccard ≥ 0.90 起始，存盤後實測校準** | LLM 翻譯與 embedding 具非確定性，純字串 100% 相等不切實際；先設保守門檻、跑 §6.2 自比對歸零實測 variance 後回調（門檻數值經 baron 核准寫死）。 |
| **「預期改善」與「退化」的判定誰拍板** | **工具標 `IMPROVEMENT_PENDING_REVIEW`、最終由 baron 人工複核核准更新黃金** | 機器無法自動區分「改善」與「退化」（兩者皆呈現為 Diff≠0）；自動化只負責偵測差異與分類提示，價值判斷保留給人，避免誤把退化當改善放行。 |
| **D3 是否納入多篇召回 `retrieve_multi_with_context`** | **首版只測單篇 `retrieve_with_context`，多篇列後續** | 五路基準皆單檔、單篇召回已覆蓋核心退化風險；多篇跨文獻召回（hashtag RAG）屬 RAG-1 既有功能、非本大改版主鏈退化點，納入徒增複雜度。 |
| **book 代表文檔體積過大是否取節選** | **取代表性節選（含跨章節 Sliding Window 邊界）即可，非全書** | BookPipeline 退化風險集中在章節滾動摘要與 Sliding Window 連貫性，節選含 2-3 章邊界即可覆蓋；全書跑基準耗時且存盤體積過大、CP 值低。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 GOLDEN-BASELINE 黃金基準存盤與退化比對機制的目標規格，作為 PIPE 大改版每路絞殺後 0% 退化驗收的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；每路 PIPE-* plan 落地後引用其 verdict；PIPE-FLIP plan 引用五路全綠前置 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 GOLDEN-BASELINE tasks / 五路 PIPE-* 執行報告 / PIPE-FLIP plan |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段）；嚴禁注入任何 hook 至業務主鏈 |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | PIPE-FLIP 收官且五路全綠後，經 baron 同意歸檔至 archive/ |
| **重複防護** | 僅定義基準存盤與比對技術規格；四份合約唯一源在 PIPE-SPEC；落地戰略唯一源在 PIPE plan §2 U10；工作流規格一律引用 WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v2 (2026-06-01)：依 PIPE master plan v6 對齊更新——新增 **U7 產出物明確定義**（三表：① 本計畫交付物 `tools/golden_baseline.py`／`tests/golden_baseline/{fixtures,golden}`／`report/golden_baseline/`／`tests/test_golden_baseline.py`；② 消費不交付既有真理源；③ 明確不產出零 Schema／零 API／零 hook／零 env／零路徑外溢）；§5 大改版目標規格依據檔名同步 `_plan_v2.md` → `_plan_v6.md`。
- v1 (2026-06-01)：初版建立，依 PIPE-SPEC §3.5 影子並行與 PIPE plan §8.3 路線圖定位，定義五路固定資料集（U1）／三維度黃金產物存盤（U2）／Diff 引擎三維度比對（U3）／0% 退化紅綠燈裁決含改善豁免（U4）／程式流程與判斷雙 Phase 流程圖（U5）／資料流程圖（U6）；§3 附 `pipeline_core.py L197-204`／`rag_retriever.py L92` grep 證據；§7 列 5 項 Open Questions（存放位置／退化門檻數值／改善判定權／多篇召回/book 節選）。
