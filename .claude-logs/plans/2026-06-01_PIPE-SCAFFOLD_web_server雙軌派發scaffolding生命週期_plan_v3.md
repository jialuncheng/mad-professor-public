# PIPE-SCAFFOLD web_server 雙軌派發 Scaffolding 生命週期 plan

> 定義 PIPE 大改版影子並行期間，`web_server.py` 上傳派發層「雙軌 scaffolding」的注入與移除兩階段規格：影子期先建可選 B 軌派發，Flip the Switch 後移除 dual-dispatch 並收斂至單軌新核心。本 plan 為純規格定義，落地戰略總綱見 §5 所列 PIPE plan §2 U10。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 大改版採影子並行落地（A 軌舊 11-stage 單體 / B 軌新核心同庫共存），需要一個讓兩軌「同時被觸發」的派發機制。現行 `web_server.py` 派發層為單軌——`upload_paper`（L432）僅拋一個 `run_pipeline` 背景任務（L480-482），`run_pipeline`（L487）內硬綁 `PipelineCore`（L503）。若直接在派發層長存雙軌邏輯，Flip 後將遺留技術債；若不先建插入點，第一條 B 軌路（Resume）打通時無處掛載。
- **解法**：將雙軌派發定義為**有明確生死週期的臨時 scaffolding**，分兩階段：**階段一（建）**——在派發層加一個**旗標閘門（`SHADOW_LAUNCH_ENABLED`，預設 `false`）** 控制的**可選 B 軌派發**，A 軌 `run_pipeline` 既有路徑 byte-for-byte 不動，B 軌以 `_shadow` ID 後綴物理隔離；旗標 `false` 時 100% 等同現行單軌、為惰性插入點。**階段二（移）**——五路全通且 Golden Baseline Diff 0% 退化後 Flip，移除 dual-dispatch 與旗標，將主派發收斂至 B 軌新核心、下線 A 軌。
- **影響**：階段一臨時改動 `web_server.py` 派發層（`upload_paper` 與 retry/confirm 兩個 `run_pipeline` 派發點，加 `settings.py` 一個 env）；階段二回收同一批改動並將 `PipelineCore` 引用切至新核心。對既有 list/get/delete API、`processing_tasks` 鍵結構、前端讀取路徑零改動。屬 PIPE §2 U10「影子並行 + Flip the Switch」的 `web_server` 切片實作規格，不重定義重構本體。

---

## §2 目標規格

> 以下為本 scaffolding 必須達到的「最終狀態」規格（What it should be），可量化檢驗。實作細節（如何寫）屬 tasks 階段。

### U1. 雙軌派發為旗標閘門惰性插入點
- 派發層新增環境變數 `SHADOW_LAUNCH_ENABLED`（`settings.py` 定義，預設 `false`）。
- 旗標 `false` 時，上傳→派發→處理行為 **100% 等同現行單軌（僅 A 軌）**，dual-dispatch 路徑為零作用插入點，線上 0 風險。
- 旗標 `true` 時，**每篇上傳**皆**額外**觸發一條 B 軌背景任務（全量雙跑、無逐篇篩選），A 軌任務照常觸發。

### U2. A 軌路徑零侵入（Additive-Only）
- B 軌派發以**附加方式**接入，**不得改寫 A 軌既有 `run_pipeline`（L487-527）同步邏輯本體**；A 軌 `PipelineCore.process` 調用（L503-508）保持原樣可運行至 Flip 前一刻。
- 影子業務細節（`_shadow` 命名、` (測試)` 標題、新核心調用）封裝於 B 軌專屬派發單元，不滲入 A 軌函式。

### U3. 影子隔離契約（與 PIPE U10 對齊）
- B 軌任務以 `paper_id + "_shadow"` 後綴達成四重物理隔離：① `processing_tasks` 獨立 `task_key`（tuple key `(owner_id, paper_id_shadow)`，與 A 軌不碰撞）；② 獨立 `output/*_shadow/` 目錄；③ 獨立 SQLite `Paper` row；④ 前端 ` (測試)` 標題後綴肉眼可辨。
- 影子 row 必須能被**既有** `delete_paper` 一鍵清除（同庫獨立 row），不新增刪除 API。

### U4. 兩個派發點全納管
- `upload_paper`（首次上傳，L480-482）與 retry/confirm endpoint（L756 第二派發點）**兩處** `run_pipeline` 派發**皆**納入旗標閘門，避免任一入口遺漏導致影子覆蓋不全。

### U5. 階段一交付定義（建）
- 影子並行期開始時落地，旗標預設 `false`；待 PIPE 縱向第一路（Resume）B 軌可運行後才以 `SHADOW_LAUNCH_ENABLED=true` 開啟實際雙跑。開啟後**每篇上傳全量雙跑**（baron 拍板，見 §7 Q3）。
- 交付完成判據：旗標 `false` 時既有 pytest 全綠且 E2E 行為與舊版逐位元一致；旗標 `true` 時前端列表同時出現「原著」與「原著 (測試)」兩列。

### U6. 階段二交付定義（移）
- 觸發條件：PIPE 五路全通 + Golden Baseline Diff 0% 退化（由 PIPE plan 認定）。
- 「移除雙軌」語意 = **Flip + 收斂單軌**：① 主派發 `run_pipeline` 的 `PipelineCore` 引用切至 B 軌新核心；② 移除 B 軌附加派發單元、`SHADOW_LAUNCH_ENABLED` 旗標、`_shadow`／` (測試)` 影子標記；③ 下線 A 軌舊單體調用。
- 完成判據：`grep -rnE "SHADOW_LAUNCH_ENABLED|_shadow|（測試）| \(測試\)" web_server.py settings.py` **0 殘留**；`run_pipeline` 單一路徑指向新核心；既有 pytest 全綠。

### U7. 程式流程與判斷（Program Flow & Decision）

#### §2.7.1 `upload_paper` 雙軌派發流程（階段一·建、派發點一）
```
START upload_paper(file, doc_type)
  │
  ├─ 1. 存檔 + 無損優化（既有，byte 不動）
  ├─ 2. 寫 processing_tasks[(owner, paper_id)]（A 軌，既有）
  ├─ 3. background_tasks.add_task(run_pipeline, ...)  ── A 軌派發（既有本體不動）
  │
  └─ 4. [判斷] SHADOW_LAUNCH_ENABLED？
          ├─ false（預設）──► END（100% 單軌、惰性插入點、線上 0 風險）
          └─ true ──► 額外 background_tasks.add_task(run_pipeline_shadow, ...)
                        └─► END（A+B 全量雙跑，§7 Q3 baron 拍板）
```

#### §2.7.2 影子 B 軌派發單元（`run_pipeline_shadow`，A 軌 byte 不動的獨立單元）
```
START run_pipeline_shadow(owner, paper_id, pdf_path, doc_type)
  │
  ├─ 1. paper_id_shadow = paper_id + "_shadow"
  ├─ 2. 寫 processing_tasks[(owner, paper_id_shadow)]（獨立 task_key、不碰 A 軌鍵）
  ├─ 3. 呼叫 B 軌新核心 Orchestrator.run(ctx, shadow=True)（PIPE-CORE 交付）
  │       └─ ctx.shadow=True ⇒ 產物落 output/<id>_shadow/、Resolved Title 加 ` (測試)`
  ├─ 4. [判斷] 新核心回傳？
  │       ├─ 成功 ──► processing_tasks[shadow_key].status='done'
  │       └─ 例外 ──► status='error'（影子失敗不影響 A 軌正本，logger.error exc_info=True）
  └─ END
```

#### §2.7.3 retry/confirm 派發點納管（派發點二，L756）
> 與 §2.7.1 同構：A 軌 `run_pipeline` 既有派發不動；旗標 `true` 時同步額外拋 `run_pipeline_shadow`，確保兩個入口影子覆蓋無遺漏（U4）。

#### §2.7.4 階段二 Flip 移除流程（移）
```
START Flip
  │
  ├─ 1. [判斷] PIPE plan 認定五路全通 + Golden Baseline Diff 0%？
  │        └─ 否 ──► ABORT（紅燈物理阻擋、禁止 Flip）
  ├─ 2. run_pipeline 內 PipelineCore 引用 ──► 切換至 B 軌新核心 Orchestrator
  ├─ 3. 移除 run_pipeline_shadow 單元 + SHADOW_LAUNCH_ENABLED 旗標 + _shadow/` (測試)` 標記
  ├─ 4. 下線 A 軌舊單體 PipelineCore 調用
  └─ 5. [驗證] grep 0 殘留 + run_pipeline 單一核心引用 + pytest 全綠
        END（收斂單軌）
```

### U8. 資料流程（Data Flow）

```
                          upload PDF（同一檔，旗標 true）
                                   │
        ┌──────────────────────────┴──────────────────────────┐
        ▼ A 軌（既有、不動）                                     ▼ B 軌（影子附加單元）
 processing_tasks[(owner, paper_id)]              processing_tasks[(owner, paper_id_shadow)]
        │                                                       │
 run_pipeline ─► PipelineCore（舊 11-stage）         run_pipeline_shadow ─► Orchestrator（新核心, shadow=True）
        │                                                       │
 output/<id>/                                          output/<id>_shadow/
        │                                                       │
 SQLite Paper row（正本）                              SQLite Paper row（id_shadow、標題 + ` (測試)`）
        └──────────────────────────┬──────────────────────────┘
                                   ▼
           list_papers（既有 API、零改動）──► 前端同時帶出「原著」+「原著 (測試)」兩列
           delete_paper（既有 API）──► 各自獨立 row + 獨立目錄分別清除、互不影響
```

- **影子四重隔離鐵律**（呼應 U3）：① `(owner, paper_id_shadow)` 獨立 task_key；② 獨立 `output/*_shadow/`；③ 獨立 `Paper` row；④ ` (測試)` 標題後綴肉眼可辨。四者皆衍生自 `_shadow` 後綴，零碰撞。
- **零侵入鐵律**：A 軌資料流（左半）byte-for-byte 等同現行單軌；B 軌（右半）為純附加旁路，Flip 時整塊回收，A 軌零改名零連鎖。
- **單向依賴**：B 軌派發單元**消費** PIPE-CORE 交付的 Orchestrator 介面，scaffolding 本身不定義任何調度/合約邏輯。

### U9. 產出物明確定義（Deliverables）

> 本計畫落地後**必須且僅產出**以下資產；任何超出此清單的改動均屬越界，須走 §0 改版。三表分列：① 本計畫交付物（臨時 scaffolding，有明確生死週期）、② 消費不交付（讀既有/上游真理源）、③ 明確不產出（零越界保證）。

#### ① 本計畫交付物（self-built、Flip 後回收）

| 交付物 | 類型 | 內容定義 | 歸屬路徑 |
|---|---|---|---|
| **影子 B 軌派發單元** | 臨時 scaffolding | `run_pipeline_shadow`（封裝 `_shadow` 命名／` (測試)` 標題／呼叫新核心 Orchestrator）＋ `upload_paper`（派發點一）與 retry/confirm（派發點二）兩處旗標閘門下的額外派發掛點；A 軌 `run_pipeline` 本體 byte 不動 | `web_server.py`（階段二整塊移除） |
| **旗標環境變數** | 臨時 env | `SHADOW_LAUNCH_ENABLED`（預設 `false`），控制 B 軌是否實際雙跑；`false` 時為零作用惰性插入點 | `settings.py`（階段二移除） |
| **scaffolding 生命週期測試** | pytest | 旗標 `false` 單軌等價（僅一背景任務、一 row）／旗標 `true` 雙軌（影子 task_key 不碰撞）／派發點二納管／階段二移除態 grep 0 殘留 | `tests/`（新增測試） |
| **階段二收斂** | 移除動作 | Flip 後 `run_pipeline` 的 `PipelineCore` 引用切至新核心 + 回收上述全部 scaffolding/旗標/影子標記 + 下線 A 軌調用 | `web_server.py`／`settings.py` |

#### ② 消費不交付（讀既有/上游真理源、零改動）

| 消費對象 | 提供方 | 消費方式 |
|---|---|---|
| B 軌新核心 `Orchestrator.run(ctx, shadow=True)` | PIPE-CORE 交付（`pipelines/`） | 純呼叫，影子派發單元委派調度給新核心 |
| 影子並行命名鐵律（`_shadow`／` (測試)`／四重隔離） | `PIPE-SPEC §3.5` | 純對齊，命名與隔離語意依此 |
| A 軌 `run_pipeline` + `PipelineCore`（舊 11-stage） | 既有 God Class | 純沿用，影子期全程可運行至 Flip 前一刻 |
| `list_papers` / `get_paper` / `delete_paper` API | 既有 web 層 | 純沿用，影子 row 同庫獨立、靠既有 API 自動帶出與清理 |
| `processing_tasks` dict / `models.py` Paper 表 | 既有 | 純沿用鍵語意/schema，影子僅衍生新鍵/新 row |

#### ③ 明確不產出（零越界保證）

| 不產出項 | 保證 |
|---|---|
| **零 A 軌本體改寫** | `run_pipeline`（L487-527）同步邏輯與 `PipelineCore.process`（L503-508）影子期 byte 不動 |
| **零新刪除/查詢 API** | 影子 row 為同庫獨立 row，清理/列出靠既有 `delete_paper`/`list_papers`，不新增端點 |
| **零 `processing_tasks` 鍵語意變更** | 僅以 `paper_id_shadow` 衍生新鍵，既有 `(owner, paper_id)` tuple 語意不動 |
| **零前端改動** | 影子產物靠 ` (測試)` 標題後綴肉眼區分，`static/index.html` 讀取/渲染路徑零改動 |
| **零 DB Schema 變動** | 影子僅新增同結構 `Paper` row，不做破壞性 schema 變更 |
| **零逐篇 opt-in 篩選邏輯** | 旗標 `true` 全量雙跑、配額吃緊時整段關旗標（§7 Q3），派發層不做逐篇篩選、保持 scaffolding 最小化 |
| **零調度/合約定義** | 三層解耦調度與四份合約唯一源在 PIPE-CORE/PIPE-SPEC，scaffolding 只消費不重定義 |

---

## §3 現況與證據

詳細盤點與本 scaffolding 相關的現有派發鏈與關鍵調用點：

- **`web_server.py`**：
  - `processing_tasks L52`：模組級 dict，鍵為 `(owner_id, paper_id)` tuple，值含 `status` / `progress` / `_pdf_path` / `_original_filename`。影子 row 須用 `(owner_id, paper_id_shadow)` 獨立鍵不碰撞（U3）。
  - `upload_paper L432-484`：存檔 + 無損優化後，於 L473-479 寫入 `processing_tasks`、L480-482 `background_tasks.add_task(run_pipeline, ...)` 拋**單一**背景任務（派發點一）。
  - `run_pipeline L487-527`：L503 `pipeline = PipelineCore(on_progress=...)` → L504-508 `pipeline.process(...)`（A 軌核心調用）→ L516 `load_paper_resources` → L519 `status='done'`；異常 L522-527 標 `error`。階段一嚴禁改其本體（U2）。
  - retry/confirm 派發點 L756：`background_tasks.add_task(run_pipeline, ...)`（派發點二），須同步納管（U4）。
- **`settings.py`**：
  - 新增 `SHADOW_LAUNCH_ENABLED` env 讀取點（現無，屬本 scaffolding 新增）。

### §3.1 grep 鋼鐵證據

```bash
grep -nE "def upload_paper|BackgroundTasks|add_task|run_pipeline|processing_tasks" web_server.py | head -40
# 52:processing_tasks: dict = {}  # (owner_id, paper_id) -> {...}
# 432:async def upload_paper(
# 433:    background_tasks: BackgroundTasks,
# 474:        processing_tasks[(current_user.id, paper_id)] = {
# 480:    background_tasks.add_task(
# 481:        run_pipeline, current_user.id, paper_id, str(pdf_path), doc_type, file.filename
# 487:async def run_pipeline(owner_id: int, paper_id: str, pdf_path: str, doc_type: str,
# 756:    background_tasks.add_task(
# 757:        run_pipeline, current_user.id, paper_id, pdf_path, request.doc_type,

# run_pipeline 內 A 軌核心調用（L503-508，階段一不可動本體）
# 503:        pipeline = PipelineCore(on_progress=on_progress)
# 504:        output_paths2 = await loop.run_in_executor(
# 505:            None, lambda: pipeline.process(pdf_path, str(OUTPUT_DIR),
# 519:            processing_tasks[task_key]['status'] = 'done'
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在階段一（建）嚴禁任何改動：**

- [ ] `web_server.py` `run_pipeline`（L487-527）A 軌既有同步邏輯本體與 `PipelineCore.process` 調用（L503-508）——影子期須全程可運行，階段二 Flip 才切換。
- [ ] `web_server.py` 既有 `list_papers` / `get_paper` / `delete_paper` API——影子 row 為同庫獨立 row，必須靠既有 API 零改動自動帶出與清理。
- [ ] `processing_tasks`（L52）的 `(owner_id, paper_id)` tuple 鍵結構——影子僅以 `paper_id_shadow` 衍生新鍵，不改既有鍵語意。
- [ ] 前端 `static/index.html` 讀取與列表渲染路徑——影子產物靠 ` (測試)` 標題後綴肉眼區分，前端零改動。
- [ ] `models.py` `Paper` 表既有主欄位與關係——影子僅新增同結構 row，不做破壞性 schema 變更。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 影子並行 + Flip the Switch 落地戰略總綱（U10） | `.claude-logs/baton/2026-06-01_PIPE_PipelineCore流程重構大改版_plan_v8.md §2 U10 / §7 Q3` |
| 影子並行命名鐵律（`_shadow`／` (測試)`／四重隔離） | `.claude-logs/baton/2026-06-01_PIPE-SPEC_PipelineCore流程重構架構_specification.md §3.5` |
| B 軌新核心調度入口（`Orchestrator.run(ctx, shadow=True)`，影子派發委派對象） | `.claude-logs/baton/2026-06-01_PIPE-CORE_三層解耦調度骨架_plan_v2.md §2 U1 §2 U7` |
| plan 結構契約與治理規格 | `.claude-logs/templates/template_plan.md` |
| 六階段觸發鏈／命名規則／SOP 核查 | `.claude-logs/ref/WORKFLOW_SOP.md §3 §5 §6` |
| 專案進度治理框架（雙軌制／不可動清單／plan 結構） | `.claude-logs/ref/PROJECT_PROGRESS_CONTROL_FRAMEWORK.md §1 §4` |
| logging 程式碼級 SOP（BE-Refactor 執行時強制） | `.claude-logs/sop/2026-05-23_logging_SOP_手冊.md` |
| 現況派發鏈 | `web_server.py L52 / L432-484 / L487-527 / L756` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **既有測試執行**（防 Regression 底線）：
  ```bash
  pytest tests/ -v
  ```
- **預計新增的測試**：
  - 階段一—旗標 `false`：`SHADOW_LAUNCH_ENABLED=false` 時 `upload_paper` 僅拋一個背景任務、`processing_tasks` 僅一 row（單軌等價斷言）。
  - 階段一—旗標 `true`：開啟時 `upload_paper` 額外拋 B 軌任務、影子 `task_key` 為 `paper_id_shadow`、與 A 軌鍵不碰撞。
  - 派發點二納管：retry/confirm（L756）路徑在旗標 `true` 時同樣觸發 B 軌。
  - 階段二—移除完成態：`grep` 斷言 `SHADOW_LAUNCH_ENABLED` / `_shadow` / ` (測試)` 0 殘留、`run_pipeline` 單一核心引用。

### §6.2 手動端到端（E2E）驗證流程

1. **惰性插入點驗證**：`SHADOW_LAUNCH_ENABLED=false` 上傳 PDF，前端僅一列、`output/` 無 `_shadow` 目錄，行為與舊版逐位元一致。
2. **雙軌啟用驗證**：`SHADOW_LAUNCH_ENABLED=true` 上傳，前端列表同時出現「原著」與「原著 (測試)」兩列，物理產物分別落 `output/<id>/` 與 `output/<id>_shadow/`。
3. **零殘留清理**：對「原著 (測試)」列按既有前端 `delete_paper`，SQLite 影子 row 與 `output/<id>_shadow/` 100% 清空，A 軌正本不受影響。
4. **Flip 後單軌驗證**（階段二）：移除 scaffolding 後 `SHADOW_LAUNCH_ENABLED` 不再被引用，上傳流量 100% 走新核心，前端無 ` (測試)` 殘列。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| **「改版開始前先建 scaffolding」是否正確時機** | **正確、但旗標須預設 `false`**——插入點於影子期起點建好，實際雙跑延後至 Resume 路 B 軌可運行才開旗標 | 兩階段大方向與 PIPE §2 U10 / §7 Q3 完全一致。唯一須校正的是：B 軌核心尚未存在時就建 dual-dispatch，會形成「派發到空殼」風險。以 `false` 預設使其成惰性插入點，可同時滿足「先建好掛載點」與「線上 0 風險」，避免第一路打通時才臨時動派發層。 |
| **B 軌注入方式：改 `run_pipeline` 內分支 vs 新增獨立影子派發單元** | **新增獨立 B 軌派發單元**（A 軌 `run_pipeline` byte 不動） | PIPE §4 不可動清單要求 A 軌全程可運行至 Flip。在 `run_pipeline` 內塞 `if shadow` 分支會污染 A 軌熱路徑、增加 Regression 面；獨立單元封裝影子細節，Flip 時整塊刪除、A 軌零改名零連鎖。 |
| **影子期是否每篇上傳都雙跑（A+B 全鏈各跑一次、算力翻倍）** | **✅ baron 拍板：旗標 `true` 時全量雙跑**——每篇上傳 A+B 各跑一次，不設逐篇 opt-in 篩選 | baron 已拍板採全量雙跑，以最大化 Golden Baseline Diff 覆蓋面（每篇都有 A/B 對照樣本）。代價是旗標開啟期間 Embedding/翻譯算力與 API 配額翻倍，屬影子期可接受成本；若配額吃緊，靠 `SHADOW_LAUNCH_ENABLED` 旗標整段關閉、不在派發層做逐篇篩選邏輯（保持 scaffolding 最小化）。 |
| **階段二「移除雙軌」的精確語意** | **定義為「Flip + 收斂單軌」三步**（切引用→刪 scaffolding/旗標/影子標記→下線 A 軌），非獨立 delete | 若僅刪 B 軌 scaffolding 會退回舊單體；正確的 Flip 是把主派發引用切到新核心後，才一併移除 A 軌與影子腳手架。U6 已據此定義完成判據（grep 0 殘留 + 單一核心引用）。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE 影子並行期 `web_server.py` 雙軌派發 scaffolding 的注入（階段一）與移除（階段二）目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用；為 PIPE U10 落地戰略的 `web_server` 切片實作依據 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 PIPE-SCAFFOLD tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段）；落地戰略總綱不重寫（唯一源在 PIPE plan §2 U10） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 階段二 Flip 完成、scaffolding 全數移除、經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義 `web_server` 派發層 scaffolding 規格；影子隔離總綱與五路絞殺戰略唯一源在 PIPE plan；工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v3 (2026-06-01)：依 PIPE master plan v8／PIPE-CORE v2 對齊更新——新增 **U7 程式流程與判斷**（upload_paper 雙軌派發旗標閘門／run_pipeline_shadow 影子單元／retry-confirm 派發點二納管／階段二 Flip 移除四流程圖）＋ **U8 資料流程**（A 軌正本 vs B 軌影子雙軌資料流＋四重隔離＋零侵入鐵律）＋ **U9 產出物明確定義**（三表：① 影子派發單元/旗標/測試/階段二收斂；② 消費 PIPE-CORE Orchestrator/PIPE-SPEC 命名鐵律/既有 A 軌與 API；③ 零 A 軌本體改寫/零新 API/零鍵語意變更/零前端/零 Schema/零逐篇篩選/零調度合約定義）；§5 PIPE 依據檔名同步 `_plan_v1.md` → `_plan_v8.md`，新增 PIPE-SPEC §3.5 與 PIPE-CORE v2 兩列依據。
- v2 (2026-06-01)：baron 拍板 §7 Q3——影子期旗標 `true` 時**全量雙跑**（每篇上傳 A+B 各跑一次、不設逐篇 opt-in）；同步調整 §2 U1／U5 表述，明定算力／配額翻倍為影子期可接受成本、配額吃緊時整段關旗標而非派發層篩選。
- v1 (2026-06-01)：初版建立，定義 `web_server.py` 雙軌派發 scaffolding 兩階段生命週期（旗標閘門惰性插入點／A 軌零侵入附加派發／影子四重隔離／兩派發點納管／Flip 收斂單軌移除），對齊 PIPE plan §2 U10 與 §7 Q3。
