# 專案進度管控框架 · Mad Professor

> 本文件為 **Mad Professor 專案進度管控框架 (Project Progress Control Framework)** 的權威規範。
> 供開發工程師、專案協作者與 AI 助理（如 Claude Code、Gemini Agent）在進行任何功能開發、重構、Bug 修正時，嚴格遵循的進度與品質防護網。

---

## 1. 核心理念（心法）

### 1.1 Plan-Execution 雙軌制（Double-Track Assurance）
- **無計畫，不改動**：除了極少數緊急且無副作用的 Hotfix 外，任何功能的加入與架構改動，皆必須遵循「先 Plan，後執行，再驗證」的嚴密雙軌循環。
- **證據驅動（Evidence-Driven）**：所有的問題診斷必須附帶具體代碼行數、錯誤日誌或實測證據；所有的修復必須伴隨明確的端到端（E2E）驗證步驟與真實執行結果。

### 1.2 最小干擾與不可動清單（Regress-Free Commits）
- **畫地自限，嚴防外溢**：在每次修改前，必須界定「不可動清單」，明確限制修改的邊界。
- **小步快跑，獨立可逆**：每一次的 Commit 應是語意完整的最小功能單元，且具備隨時回退（Rollback）的可逆性。

---

## 2. 進度管理工具：TODO 與已完成清單

項目進度集中管理於 `file:///.claude-logs/TODO.md`，其寫入與維護規則如下：

### 2.1 單一檔案整合原則 (Single Source of Truth)
- **不另外分檔**：待辦清單與已完成清單統一整合維護於 `TODO.md` 中。這能讓 AI 與人類開發者在單一上下文中快速交叉對照歷史變更與未來待辦。

### 2.2 狀態標記與優先序
每項任務必須清楚標註：
- **狀態 Emoji**：
  - `⬜ 未開始`：尚未進入分析規劃階段。
  - `🔵 plan 中`：正在撰寫 `_plan.md`。
  - `🟡 WIP` (Work In Progress)：正在執行修改或驗證中。
  - `✅ done`：已完成驗證並落地 Git Commit。
- **優先級**：高 / 中 / 低。
- **估計工時**：明確估算 Commit 數量或預估時間（如「1 個 commit」、「2-3 個 commits」）。
- **落地 Commit Hash**：任務完成時，必須回填該任務落地之 Git Commit 縮寫（前 7 碼）。

### 2.3 TODO 清單寫入規則
```markdown
- [狀態] **[編碼] [任務名稱]**（[關聯計畫/來源]）
  - [子任務細節 1]
  - [子任務細節 2]
  - 工時：[預估工時]
  - 依賴：[相依任務或等待條件]
```
*範例：*
```markdown
- ⬜ **RAG-1 跨文件查詢**（baron 需求 3 / Commit 15 plan Q7）
  - `retrieve_with_context` 簽名擴 `paper_ids: List[str]`
  - 跨多 vector store 檢索後合併排序
  - 工時：2-3 個 commits
  - 依賴：無
```

### 2.4 已完成清單寫入規則
已完成項目應依據 **Phase** 與 **主題** 以表格形式歸檔，並精確關聯 Git Hash 與 Commit 代號：
```markdown
### [Phase 名稱] [主題]

| Commit | 內容 | Hash |
|---|---|---|
| [編號] | [具體變動內容] | `[Commit Hash]` |
```
*範例：*
```markdown
### Phase 4.7d RAG 改造（15 系列）

| Commit | 內容 | Hash |
|---|---|---|
| 15-2 | retriever 加 paper_title 引用 + score logging | `b6622a1` |
| 15-1 | chunk 優化（空 chunk / Context 前綴 / 短文合併） | `d6cb3df` |
```

### 2.5 任務生命週期流向與歸檔規則 (Task Lifecycle & Archiving)
為確保待辦清單保持精簡、不被歷史資訊淹沒，任務的狀態流轉必須遵循以下「動態搬移歸檔規則」：

1. **Active 階段**：當任務處於 `⬜ 未開始`、`🔵 plan 中` 或 `🟡 WIP` 時，統一放置於下方的 `## 🟡 進行中 / ⬜ 未開始` 的優先級分組中。
2. **歸檔搬移**：當任務 100% 完成驗證並落地 Git，狀態轉為 `✅ done` 時，開發者或 AI **必須將該任務從下方的列表中移除**。
3. **表格寫入**：將該任務的成果改以表格列點形式，**追加寫入至頂部的 `## ✅ 已完成` 對應主題表格中**，確實填寫 Commit 編號、內容簡述與落地 Hash（前 7 碼）。
4. **類別索引更新**：同步更新 `TODO.md` 最底部的 `## 索引（依類別）`，將索引區的狀態標記與主列表同步（例如將 `- RAG-1 跨文件查詢（高）` 更新為 `- ✅ RAG-1 跨文件查詢（高）`）。

---

## 3. 編碼機制與命名規則

為了讓 TODO、計畫、執行報告與 Git 歷史無縫追蹤，本專案採用三位一體編碼機制：

### 3.1 任務編碼（Task ID）
任務編碼採用 `[模組前綴]-[序號]` 格式：
- **模組前綴**：
  - `RAG-`：向量檢索、Chunk 分割、Embedding 等 RAG 鏈改動。
  - `CHAT-`：AI 問答、SSE 串流、Broker 管理、對話歷史等對話鏈改動。
  - `DB-`：資料庫 Schema、資料遷移（Migration）等儲存層改動。
  - `INFRA-`：系統底層重構、環境套件稽核、Docker 容器化等基礎建設。
  - `BUG-`：跨越單一模組的系統級 Bug 修正。
- **子代號**：同一個任務若有前後端分離或後續清理，可附加小寫英文字母，如 `CHAT-3b`。

### 3.2 紀錄檔命名規則（Log Filename）
所有的紀錄檔皆儲存於 `file:///.claude-logs/` 中，命名必須嚴格遵循：
`[YYYY-MM-DD]_[Phase]_[Commit/Task]_[類別].md`

| 類別 | 命名範例 | 說明 |
|---|---|---|
| **計畫檔** | `2026-05-22_Phase_4_7d_Commit_15_plan.md` | 進行改檔前的詳細分析與設計方案。 |
| **執行檔** | `2026-05-22_Phase_4_7d_Commit_15-1_執行.md` | 具體改檔後的真因、修法、與 E2E 驗證結果。 |
| **熱修復檔** | `2026-05-22_Phase_4_7d_Commit_15-1b_hotfix.md` | 用於緊急修補前次 Commit 的小缺陷。 |

---

## 4. 進度管制與系統運行日誌（Logs）撰寫規格

為了區分「開發進度管制紀錄 (Session Progress Logs)」與「系統程式運行日誌 (System Runtime Logs)」，特訂定雙重日誌規格契約。任何開發修改均須同時嚴格遵守這兩類規格。

### 4.1 計畫檔 (`_plan.md`) 結構契約（開發進度管制）
計畫檔是用來**向人類/自己證明你已經想透了解法**。不寫程式碼，純分析。
1. **TL;DR**：簡述問題、根因、解法、受影響範圍與相依性。
2. **現況盤點**：梳理目前程式碼邏輯、關鍵 Class/Method 與調用路徑（務必指出確切行數）。
3. **觀察到的問題與證據**：條列具體問題，並列出日誌或程式碼行數做為證據。
4. **設計方案**：具體的修改邏輯，包含預期效果與可能的破壞性變更（Breaking Changes）。
5. **變動風險與相容性評估**：評估對舊資料或既有 API 的衝擊。
6. **測試與端到端（E2E）驗證計畫**：明確規範要跑的 pytest 單元測試與手動驗證的預期行為。
7. **不可做 / 不可動清單**：宣告邊界，限制修改範圍以防止 Regression。
8. **開放問題 (Open Questions)**：需要與專案負責人（人類）討論的設計決策。

### 4.2 執行報告 (`_執行.md`) 結構契約（開發進度管制）
執行報告是**程式碼落地的承諾與證明**。
1. **基準與完成狀態**：描述是在哪個 Commit 上進行改動，以及目前是否已 commit/push。
2. **落地 Commit 表格**：條列本次執行的 Commit 編號、落地 Hash 與 Subject。
3. **diff stat**：貼上 `git diff --stat` 的真實結果。
4. **真因**：對應計畫檔，簡述造成 Bug 或需要開發的底層原因。
5. **修法**：條列修改的檔案、修改內容與邏輯（附帶關鍵代碼片段）。
6. **不可動清單遵守狀態**：逐項檢查並打勾標記 `[x]`，證明沒有越界修改。
7. **端到端驗證計畫結果**：
   - 貼上 `git status -s` 的真實結果。
   - 貼上靜態語意檢查、單元測試（如 `pytest`）的真實執行通過輸出。
   - 記錄手動端到端測試的實際輸出或日誌截圖。
8. **回退方式 (Rollback)**：寫明若在 Production 出現問題，該如何用 git 還原。

### 4.3 系統運行日誌（System Runtime Logs）撰寫規範（程式碼級）
未來任何修改或新增程式碼時，日誌（`logging`）編寫必須嚴格遵循權威規格 [2026-05-23_logging_SOP_手冊.md](file:///.claude-logs/ref/2026-05-23_logging_SOP_%E6%89%8B%E5%86%8A.md)，重點要求如下：

1. **嚴禁調用 `basicConfig` 與 `dictConfig`**：全域僅在 `web_server.py` 與 CLI 工具 `__main__` 最早期載入 `utils/logging_config.py::setup_logging()`。新入口直接導入調用即可，利用其內置的冪等性（Idempotency）防護。
2. **異常堆疊（Exception）標準化**：嚴禁手動 `traceback.format_exc()` 拼接多行字串。**強制使用 `logger.error("...", exc_info=True)`**，以便 Formatter 自動轉換為 Loki 友善的結構化單行 JSON 子字典。
3. **結構化指標（`extra_fields`）規格**：效能指標事件必須在 `extra` 中指定 `extra_fields` 字典，並附帶 `event: "performance_metric"` 標記（數值時間使用 float，不要加 "秒" 字樣），以供本機分析器及雲端大屏解讀。
4. **ContextVar 雙保險讀取**：定義時指定 `default=None`，且 Formatter 格式化時必須使用 `trace_context.get(None)`，防範 CLI 腳本或 pytest 測試等無 middleware 場景拋出 `LookupError`。
5. **降級與噪聲防禦**：`json.dumps` 統一傳入 `default=str` 降級防 TypeError。且第三方 logger（如 SQLAlchemy）必須實施噪聲分流（DEBUG mode 才開 SQL，其餘 WARNING），防範日誌暴漲。

### 4.4 資料庫操作與 Schema 設計規範（程式碼級）

未來任何涉及到資料庫的 Schema 變更、CRUD 寫入、Docker 化部署或數據遷移時，必須嚴格遵循權威規格 [2026-05-23_database_SOP_手冊.md](file:///.claude-logs/ref/2026-05-23_database_SOP_%E6%89%8B%E5%86%8A.md)，重點要求如下：

1. **標準交易語意管理**：禁止使用手動無 rollback 守護的 commit 範式。強制使用 SQLAlchemy 2.0 `session.begin()` 上下文管理器，確保「成功時自動 Commit、失敗時自動 Rollback」。
2. **極短交易原則**：嚴禁在交易（Transaction 鎖定區間）內進行任何第三方 API 請求（如 Gemini API 呼叫）或 CPU 密集型計算，防止併發鎖庫。
3. **高速批量寫入 (Bulk Insert)**：寫入大量數據（如 `PaperChunk`）時，嚴禁使用 `session.add()` 迴圈，必須強制使用 SQLAlchemy 2.0 批量 `session.execute(insert(Model), [...])` 語意。
4. **🚫 網路檔案系統紅線**：絕對禁止將 SQLite 檔案部署於 NFS 或 AWS EFS 等共享網絡儲存，WAL 共享記憶體 `*.shm` 機制不支援此結構，會導致資料庫瞬間損毀。Docker 部署必須掛載於本地 SSD/EBS 區塊儲存，或一鍵切換至 PostgreSQL。

---

## 5. SPEC 技術規格與指南撰寫規則

當專案需要新增大型領域知識、新介面規範或系統手冊時（如 `file:///.claude-logs/doc_type_新增手冊_三軸融合.md`），必須遵循以下 SPEC 撰寫規格：

### 5.1 SPEC 必備核心結構
```markdown
# [技術/功能名稱] 指南與規格

> [!NOTE]
> 本文件為 [系統名] 的權威技術規格。
> 當程式碼實作與本文件不符時，應以【核心程式碼定義】為準，並及時同步更新本文件。

## 1. 概念模型（Mental Model）
- 描述該技術的底層哲學與設計出發點（如三軸融合理念）。
- 繪製 ASCII 架構圖或 Mermaid 流程圖，讓讀者迅速掌握核心資料流。

## 2. 核心規範與硬規則（Hard Rules）
- **不可違反的硬規則**（如必須在哪些 config 註冊、哪些 interface 必須實作）。
- 嚴格界定邊界與相容性限制。

## 3. 實作步驟指南（Step-by-Step Blueprint）
- 提供詳盡的落地指引：
  - Step 1: 修改配置或註冊層。
  - Step 2: 實作特定的處理器 (Processor)。
  - Step 3: 更新儲存層/API 端點。
- 附帶極簡且標準的 Mock Code/Template。

## 4. 驗證與測試清單（Verification Checklist）
- 設計防呆機制，條列開發完成後必須手動跑完的 Regression Test 套路。
```

---

## 6. 提示詞歸檔規範（強制）

### 6.1 觸發時機

每次收到 baron 的「任務命令式提示詞」、Claude / Claude Code 必須：

1. **先**把提示詞歸檔到 `.claude-logs/prompts/`
2. **再**執行提示詞內容
3. **同步**更新 `.claude-logs/prompts/INDEX.md`

順序固定、不可顛倒。

### 6.2 判定標準

歸檔 ✅：
- 含「請執行 / 撰寫 / 修正 / 建立」等命令動詞
- 長度 > 500 字
- 結構化區塊（含 `═══` 分隔或 `## 第X步`）
- 跟 commit / plan / 執行報告對應

不歸檔 ❌：
- 純查詢（「跑 git status」「結果對嗎」）
- 短回應（< 200 字非命令）

模糊時：**優先歸檔**（寧多勿少、未來可刪、不可重建）。

### 6.3 規範詳細

完整規則見 `.claude-logs/prompts/README.md`、含命名規則 / 檔案格式 / INDEX 結構 / 敏感資訊去識別化（API key / 密碼 / email / phone / DB connection string 等寫入前必須打碼）。

### 6.4 入版控

`.claude-logs/prompts/` 已透過 `.gitignore` 設定入版控（其他 `.claude-logs/` 子目錄仍排除）、可跨環境（Claude Code Server / Macbook OrbStack / Docker / GCP 正式機）同步、GitHub 網頁端可檢索 markdown。

`.gitignore` 規則：

```gitignore
.claude-logs/*
!.claude-logs/ref/
!.claude-logs/templates/
!.claude-logs/prompts/
```

---

## 7. 衝突仲裁優先級

當進度管控、編碼規則與實際開發發生衝突時，決策優先級如下：

1. **不可動清單之絕對遵守**：寧可延遲交付，也絕不破壞不可動清單。
2. **端到端驗證之 100% 通過**：任何未通過單元測試或手動 E2E 驗證的程式碼，嚴禁 commit。
3. **進度紀錄之完備性**：必須先寫完計畫並取得同意，才可動手修改程式碼；執行完畢必須立即補齊執行報告。

---

## 8. 附錄：防 Regression 黃金三角

```
             ┌──────────────────────┐
             │    1. 計畫與不可動   │
             │   (Boundaried Plan)  │
             └──────────┬───────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│  2. 嚴格邊界修法 │         │   3. E2E 驗證防線│
│(Isolated Coding) │ ──────> │ (Verifiable E2E) │
└──────────────────┘         └──────────────────┘
```

1. **計畫限制邊界**：開工前就在 `_plan.md` 寫好「不可動清單」，並獲得確認。
2. **隔離修法**：只在限定範圍內動刀，不動無關的代碼、全域變數或配置。
3. **驗證防線**：透過自動化測試與嚴密的日誌比對，確保原有功能絲毫無損。
