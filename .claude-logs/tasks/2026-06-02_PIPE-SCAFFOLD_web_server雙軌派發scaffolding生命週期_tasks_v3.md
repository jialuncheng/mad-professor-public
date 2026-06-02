# PIPE-SCAFFOLD web_server 雙軌派發 Scaffolding — Tasks（v3）

> 本文件為 PIPE-SCAFFOLD 的 **OP-N 執行階段拆分清單**（階段 2 產出）。
> 依 `.claude-logs/baton/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md` 計畫產出，含 3 個 OP 執行階段。
> **本任務不拆分 Git Commit**，改以「OP-N 執行階段」推進；commit / push 由 baron 手動執行（CLAUDE.md §1.3）。
> **範圍界定**：本任務只實作 plan v3 **階段一（建）**——影子期雙軌派發 scaffolding 注入；**階段二（移／Flip）屬 PIPE-FLIP plan**（觸發條件＝五路全通 + Golden Diff 0%，本任務不做）。
> **收官歸檔鐵律**：OP-1/OP-2 執行期 plan／tasks／執行報告一律暫存 baton/、不移動；**唯一在最後 OP-3（Checkout）一次性 `mv` + `git add` 歸檔**（WORKFLOW_SOP §3）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `tests/test_pipe_scaffold.py`（雙軌派發 scaffolding 測試） |
| **修改檔案** | 2 個 | `settings.py`（新增 `SHADOW_LAUNCH_ENABLED` env）/ `web_server.py`（**附加** `run_pipeline_shadow` 單元 + 兩派發點旗標閘門；**A 軌 `run_pipeline` 本體 byte 不動**） |
| **目錄初始化** | 0 個 | —（複用既有 `tests/`） |
| **狀態更新** | 2 個 | `TODO.md` PIPE-SCAFFOLD_v3 條目（🟡 WIP → ✅）/ `prompts/INDEX.md` 登記 |
| **執行階段** | 3 個 | OP-1（旗標 + 影子派發單元 + 派發點一）→ OP-2（派發點二納管 + 雙軌測試）→ OP-3（Checkout / 收官歸檔） |
| **執行報告** | 3 個 | `baton/2026-06-02_PIPE-SCAFFOLD_OP-1/OP-2/OP-3_執行.md`（套用 template_execution.md、暫存 baton/） |
| **.bak 備份** | 2 個 | `settings.py` / `web_server.py` 修改前備份（納入對應 OP git add） |
| **baton 歸檔** | 1 次 | **僅 OP-3 收官**一次性 `mv` plan_v3＋tasks_v3＋三份 OP 執行報告至正式目錄 + `git add` |

> ⚠️ **業務代碼變動提示（baron 須留意）**：本任務為 PIPE 系列首個**實際修改 `web_server.py`／`settings.py`** 的 OP（GOLDEN-BASELINE/PIPE-CORE 皆純新增檔案）。CLAUDE.md §3 將 `web_server.py` 列入嚴禁清單；本任務依 plan v3 U2 採**附加式（additive-only）**——A 軌 `run_pipeline` 本體 byte 不動、影子細節封裝於獨立 `run_pipeline_shadow` 單元、旗標預設 `false` 線上 0 風險。執行前請 baron 確認此業務代碼修改授權（plan v3 已 baron 核准）。

---

## §1 TL;DR（概要）

- **挑戰**：PIPE 影子並行需「A 軌舊單體 / B 軌新核心同時被觸發」的派發機制，但現行 `web_server.py` 派發層為單軌（`upload_paper` L480-482 拋單一 `run_pipeline`）。若直接長存雙軌邏輯，Flip 後遺留技術債；若不先建插入點，第一條 B 軌路（Resume）打通時無處掛載。
- **解法**：原子化拆 3 個 OP——**OP-1** `settings.SHADOW_LAUNCH_ENABLED`（預設 false）+ `web_server.run_pipeline_shadow` 附加派發單元（封裝 `_shadow` 命名／` (測試)` 標題／呼叫新核心 Orchestrator）+ `upload_paper`（派發點一）旗標閘門；**OP-2** retry/confirm（派發點二 L756）旗標閘門納管 + 雙軌測試套件；**OP-3** Checkout 收官。
- **影響範圍**：`settings.py`（+1 env）+ `web_server.py`（附加單元 + 兩閘門，A 軌本體不動）+ 新增測試；旗標 `false` 時 100% 等同現行單軌。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `web_server.py` `processing_tasks L52` | 模組級 dict，鍵 `(owner_id, paper_id)` tuple | 影子須用 `(owner_id, paper_id_shadow)` 獨立鍵不碰撞（U3） |
| `web_server.py` `upload_paper L432-484` | L480-482 拋**單一** `run_pipeline` 背景任務（派發點一） | 須加旗標閘門 + 額外 B 軌派發（U4） |
| `web_server.py` `run_pipeline L487-527` | L503-508 `PipelineCore.process`（A 軌核心調用） | **本體 byte 不動**（U2、§7） |
| `web_server.py` retry/confirm `L756` | `background_tasks.add_task(run_pipeline, ...)`（派發點二） | 須同步納入旗標閘門（U4） |
| `settings.py` | 無 `SHADOW_LAUNCH_ENABLED` | 須新增 env 讀取點（預設 false） |
| `pipelines/`（PIPE-CORE 已落地） | Orchestrator + PipelineFactory 骨架（NullStrategy） | B 軌派發委派對象；無具體策略註冊前 flag 須維持 false（惰性） |

---

## §3 觀察問題

### 問題 #1：派發層單軌，影子並行無掛載點
- **證據**：`web_server.py upload_paper L480-482` 僅 `background_tasks.add_task(run_pipeline, ...)` 一個任務；`run_pipeline L503 pipeline = PipelineCore(...)` 硬綁舊單體。
- **影響**：B 軌新核心無處掛載，第一路（Resume）打通時須臨時動派發層、風險高。

### 問題 #2：影子產物須與正本物理隔離且可既有 API 清除
- **證據**：`processing_tasks L52` 鍵為 `(owner_id, paper_id)` tuple；既有 `delete_paper` 以該鍵清理。
- **影響**：影子須以 `paper_id_shadow` 四重隔離（task_key／output 目錄／Paper row／` (測試)` 標題），且靠既有 `delete_paper` 清除、不新增 API（U3）。

---

## §4 設計方案

> 逐 OP 列出落地設計概要；完整規格見 plan v3 §2（U1–U9）。

### §4.1 OP-1 — 旗標 + 影子派發單元 + 派發點一
`settings.py` 新增 `SHADOW_LAUNCH_ENABLED = os.getenv(...) in ('1','true','True')`（預設 false）。`web_server.py` **附加** `run_pipeline_shadow(owner_id, paper_id, pdf_path, doc_type, ...)`（依 plan v3 §2.7.2：`paper_id_shadow` 衍生鍵 + 寫獨立 `processing_tasks` + 呼叫 B 軌新核心 Orchestrator + ` (測試)` 標題）；`upload_paper`（派發點一）A 軌派發後加旗標閘門 `if SHADOW_LAUNCH_ENABLED: background_tasks.add_task(run_pipeline_shadow, ...)`。**A 軌 `run_pipeline` L487-527 本體 byte 不動**。

### §4.2 OP-2 — 派發點二納管 + 雙軌測試
`web_server.py` retry/confirm（L756）同構加旗標閘門（旗標 true 時額外拋 B 軌）。新建 `tests/test_pipe_scaffold.py`：旗標 false 單軌等價（僅一背景任務、一 row）/ 旗標 true 雙軌（影子 task_key 不碰撞）/ 派發點二納管 / `run_pipeline` A 軌本體未被改寫（grep 斷言）。

### §4.3 OP-3 — Checkout / 收官歸檔
一次性 `mv` baton/ plan_v3+tasks_v3+OP-1~OP-3 報告至 `plans/`/`tasks/`/`executions/`（保留 `_v3`）+ `git add` + TODO ✅。

> **階段二（移／Flip）不在本任務**：plan v3 U6「移除雙軌 = Flip + 收斂單軌」觸發於五路全通 + Golden Diff 0%，屬 PIPE-FLIP plan；本任務只建不移。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 誤改 A 軌 `run_pipeline` 本體（L487-527） | 🔴 高 | 附加式：影子細節全封裝於獨立 `run_pipeline_shadow`；OP-2 測試 grep 斷言 A 軌本體未改（§7） |
| 修改 `web_server.py`/`settings.py`（CLAUDE.md §3 嚴禁清單） | 🟡 中 | plan v3 U2 已 baron 核准附加式修改；旗標預設 false 線上 0 風險；OP-1 執行前 baron 再確認授權 |
| 影子 B 軌呼叫新核心，但無具體策略註冊 → NullStrategy NotImplementedError | 🟡 中 | 旗標**預設 false** 為惰性插入點；待 PIPE-RESUME 註冊策略後才開旗標（plan v3 §7 Q1）；OP-1/OP-2 測試只驗派發行為、不實跑 B 軌 pipeline |
| 影子 task_key 與 A 軌碰撞 | 🔴 高 | `(owner_id, paper_id + "_shadow")` 衍生鍵；OP-2 測試斷言不碰撞（U3） |
| 修改既有檔案未備份 | 🟢 低 | OP-1/OP-2 修改 `settings.py`/`web_server.py` 前 `.bak` 備份並納入 git add（WORKFLOW_SOP §3） |
| logging 未遵守 SOP | 🟢 低 | `run_pipeline_shadow` 異常用 `logger.error(..., exc_info=True)`（logging SOP） |
| baton 暫存報告提早 mv/git add | 🔴 高 | OP-1/OP-2 報告嚴禁移動、僅 OP-3 收官歸檔 |

---

## §6 測試計畫

### §6.1 OP-1 驗收
```bash
# settings 旗標預設 false
python -c "import settings; print(settings.SHADOW_LAUNCH_ENABLED)"   # → False
# A 軌本體未動（run_pipeline L487-527 與 PipelineCore.process 調用保留）
grep -nE "def run_pipeline\b|PipelineCore\(on_progress" web_server.py
# 影子派發單元存在
grep -nE "def run_pipeline_shadow|_shadow|（測試）| \(測試\)" web_server.py | head
```

### §6.2 OP-2 驗收
```bash
pytest tests/test_pipe_scaffold.py -v
# 旗標 false → upload_paper 僅一背景任務、processing_tasks 僅一 row（單軌等價）
# 旗標 true → 額外 B 軌任務、task_key=(owner, paper_id_shadow) 與 A 軌不碰撞
# 派發點二（retry/confirm）旗標 true 同樣觸發 B 軌
pytest tests/ -q       # 既有測試零迴歸
```

### §6.3 OP-3 驗收
```bash
ls .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/ | grep PIPE-SCAFFOLD   # 歸檔齊全
ls .claude-logs/baton/ | grep -c PIPE-SCAFFOLD    # = 0
git status -s .claude-logs/plans/ .claude-logs/tasks/ .claude-logs/executions/
```

---

## §7 不可動清單

明確劃定修改邊界。**以下在本任務全程嚴禁任何改動：**

- [ ] **`web_server.py` `run_pipeline`（L487-527）A 軌同步邏輯本體與 `PipelineCore.process`（L503-508）調用**——影子期須全程可運行、byte 不動，階段二 Flip（PIPE-FLIP）才切換。
- [ ] **`web_server.py` 既有 `list_papers` / `get_paper` / `delete_paper` API**——影子 row 同庫獨立、靠既有 API 自動帶出與清理。
- [ ] **`processing_tasks`（L52）`(owner_id, paper_id)` tuple 鍵結構**——影子僅以 `paper_id_shadow` 衍生新鍵，不改既有鍵語意。
- [ ] **前端 `static/index.html` 讀取與列表渲染路徑**——影子靠 ` (測試)` 標題後綴肉眼區分，前端零改動。
- [ ] **`models.py` `Paper` 表既有主欄位與關係**——影子僅新增同結構 row，不做破壞性 schema 變更。
- [ ] **`pipeline_core.py` 舊單體**——A 軌核心，不動。
- [ ] **主 repo 目錄（worktree 父目錄）**——嚴禁讀寫。
- [ ] **baton/ 暫存文件（OP-1/OP-2 期間）**——嚴禁提早 `mv` / `git add`，僅 OP-3 收官歸檔。

---

## §8 推薦執行階段拆分

### OP-1 — 旗標 + 影子派發單元 + 派發點一（惰性插入點建立）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `settings.py`（+`SHADOW_LAUNCH_ENABLED`，先 `.bak`）；修改 `web_server.py`（**附加** `run_pipeline_shadow` + `upload_paper` 派發點一旗標閘門，先 `.bak`） |
| **安全性** | 🟢 高 — 附加式，A 軌本體 byte 不動；旗標預設 false → 100% 等同現行單軌、線上 0 風險 |
| **可逆性** | 🟢 高 — 還原 `.bak`（或移除 `run_pipeline_shadow` + 閘門 + env）即回到單軌 |
| **驗收 grep/執行 條件** | 見 §6.1（settings 旗標 false / A 軌本體保留 / 影子單元存在） |
| **依賴關係** | PIPE-CORE（已完成、提供 Orchestrator）；無其他前置 |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_OP-1_執行.md`（套用 template_execution.md，暫存 baton/、不移動） |
| **具體實作細節** | 1. **備份**：`cp settings.py .claude-logs/archive/2026-06-02_PIPE-SCAFFOLD_OP-1_settings.py.bak`、`cp web_server.py .claude-logs/archive/2026-06-02_PIPE-SCAFFOLD_OP-1_web_server.py.bak`（納入 git add）。2. `settings.py` 新增 `SHADOW_LAUNCH_ENABLED = os.getenv("SHADOW_LAUNCH_ENABLED", "false").lower() in ("1", "true", "yes")`（預設 False；對齊既有 env 讀取風格）。3. `web_server.py` **附加** `run_pipeline_shadow(owner_id, paper_id, pdf_path, doc_type, original_filename=None)`（依 plan v3 §2.7.2）：① `paper_id_shadow = f"{paper_id}_shadow"`；② 寫 `processing_tasks[(owner_id, paper_id_shadow)]`（獨立鍵）；③ 呼叫 B 軌新核心 `from pipelines import Orchestrator, PipelineContext`；建 `PipelineContext(doc_type=doc_type, paper_id=paper_id_shadow, shadow=True)` → `Orchestrator().run(ctx)`（無註冊策略時為 NullStrategy、僅旗標 true 才會實跑，本階段 flag false 惰性）；④ 異常 `logger.error(..., exc_info=True)` 標 error、不影響 A 軌。4. `upload_paper`（派發點一、A 軌 `add_task(run_pipeline,...)` L480-482 **之後**）加閘門：`if settings.SHADOW_LAUNCH_ENABLED: background_tasks.add_task(run_pipeline_shadow, current_user.id, paper_id, str(pdf_path), doc_type, file.filename)`。5. **A 軌 `run_pipeline` L487-527 本體完全不動**。6. 產 OP-1 報告（暫存 baton/）。 |

### OP-2 — 派發點二納管 + 雙軌測試套件（全覆蓋）

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改 `web_server.py`（retry/confirm L756 派發點二旗標閘門，先 `.bak`）；新建 `tests/test_pipe_scaffold.py` |
| **安全性** | 🟢 高 — 附加閘門、旗標 false 無作用；新增測試零 runtime 影響 |
| **可逆性** | 🟢 高 — 還原 `.bak` + 刪測試檔 |
| **驗收 grep/執行 條件** | 見 §6.2（pytest 雙軌測試全綠 + 既有測試零迴歸） |
| **依賴關係** | OP-1（`run_pipeline_shadow` + 旗標已存在） |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_OP-2_執行.md`（暫存 baton/、不移動） |
| **具體實作細節** | 1. **備份** `web_server.py`（`cp ... .claude-logs/archive/2026-06-02_PIPE-SCAFFOLD_OP-2_web_server.py.bak`，納入 git add）。2. retry/confirm endpoint（L756 `add_task(run_pipeline, ...)` 之後）加同構閘門：`if settings.SHADOW_LAUNCH_ENABLED: background_tasks.add_task(run_pipeline_shadow, ...)`，確保兩派發點影子覆蓋無遺漏（U4）。3. 新建 `tests/test_pipe_scaffold.py`（以 monkeypatch 控旗標 + mock `background_tasks`/`processing_tasks`，不實跑 pipeline）：① 旗標 false → `upload_paper` 僅一次 `add_task(run_pipeline,...)`、`processing_tasks` 僅一 row（單軌等價斷言）；② 旗標 true → 額外 `add_task(run_pipeline_shadow,...)`、影子 task_key=`(owner, f"{paper_id}_shadow")` 與 A 軌鍵不碰撞；③ 派發點二（retry/confirm）旗標 true 同樣觸發 B 軌；④ grep 斷言 `run_pipeline` A 軌本體（`PipelineCore(on_progress` 調用）仍存在未被改寫。4. 跑 `pytest tests/ -q` 確認零迴歸。5. 產 OP-2 報告（暫存 baton/）。 |

### OP-3 — Checkout / 收官歸檔（一次性 Traceability 交接）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` baton/ plan_v3+tasks_v3+OP-1~OP-3 報告 → `plans/`/`tasks/`/`executions/` + `git add`；修改 `.claude-logs/TODO.md` |
| **安全性** | 🟢 高 — 純文件搬移與版控追蹤，零代碼改動 |
| **可逆性** | 🟢 高 — `git rm --cached` + `mv` 回 baton/ |
| **驗收 grep/執行 條件** | 見 §6.3（歸檔齊全 + baton/ 無殘留 + git 已追蹤） |
| **依賴關係** | OP-1 + OP-2（兩 OP 報告皆已產於 baton/） |
| **各階段執行報告** | 必須產出 `.claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_OP-3_執行.md`，於本階段最後一併 `mv` 至 `executions/` |
| **具體實作細節** | 1. 先產 `OP-3_執行.md`（暫存 baton/，含 Conformance + 歸檔清單）。2. **一次性歸檔搬移**（WORKFLOW_SOP §3）：<br>`mv .claude-logs/baton/2026-06-01_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_plan_v3.md .claude-logs/plans/`（**保留 `_v3`**）<br>`mv .claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_web_server雙軌派發scaffolding生命週期_tasks_v3.md .claude-logs/tasks/`（**保留 `_v3`**）<br>`mv .claude-logs/baton/2026-06-02_PIPE-SCAFFOLD_OP-*_執行.md .claude-logs/executions/`。3. `git add` 上述全部正式檔 + `settings.py`/`web_server.py` + `.bak` 備份 + `tests/test_pipe_scaffold.py` + prompts/INDEX + TODO。4. **更新 TODO.md**：PIPE-SCAFFOLD_v3 三項 OP → ✅，移入頂部 ✅ 已完成表格（Hash 待 baron 回填），索引標 ✅。5. 驗收 §6.3。6. **嚴禁** `git commit`/`push`（CLAUDE.md §1.3）。 |

---

## §9 Open Questions

無。（plan v3 §7 之 4 項 Open Questions——改版時機（旗標預設 false 惰性插入）/ B 軌注入方式（獨立 `run_pipeline_shadow` 單元）/ 全量雙跑（baron 已拍板 true 時全量）/ 移除語意（Flip + 收斂、屬 PIPE-FLIP）——皆已標推薦答案/拍板，本 tasks 階段不另增規劃層問題。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 PIPE-SCAFFOLD 階段一（建）雙軌派發 scaffolding 的 OP-N 執行階段拆分與實作細節 |
| **用途** | 供 baron 審查並交由 Claude Code 按 OP 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續該任務的 `baton/` → `executions/` 三份 OP 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改 A 軌 `run_pipeline` 本體；嚴禁實作階段二 Flip（屬 PIPE-FLIP）；嚴禁自動 git commit/push；OP-1/OP-2 報告嚴禁移動、僅 OP-3 收官歸檔；修改既有檔案前 `.bak` 備份 |
| **改版觸發條件** | plan v3 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令；scaffolding 規格唯一源在 plan v3 §2；影子隔離總綱在 PIPE-SPEC §3.5；Flip 屬 PIPE-FLIP plan |

### §99.2 Revision 歷程

- v3 (2026-06-02)：初版拆分（檔名隨 plan 對齊帶 `_v3` 版號），依 plan v3 §2（U1–U9）拆為 3 個 OP——OP-1 旗標 `SHADOW_LAUNCH_ENABLED` + `run_pipeline_shadow` 附加單元 + 派發點一閘門（A 軌本體 byte 不動）/ OP-2 派發點二納管 + `tests/test_pipe_scaffold.py` 雙軌測試 / OP-3 Checkout 收官；明定本任務只做階段一（建）、階段二 Flip 屬 PIPE-FLIP；不拆 Git commit、不給 commit 建議；OP-1/OP-2 修改 `settings.py`/`web_server.py` 前 `.bak` 備份；§0.5 標註業務代碼變動提示（PIPE 系列首個改 web_server.py）。
