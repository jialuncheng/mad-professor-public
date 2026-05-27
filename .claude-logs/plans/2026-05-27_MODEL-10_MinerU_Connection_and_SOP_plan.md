# MODEL-10 MinerU 連線優化與運作維護 SOP plan

> 本計畫屬 **BE-Refactor** 工作流性質（涉及 `.py` 業務邏輯修改），旨在完成後端 PDF 處理器與 MinerU 連線機制的優化與規格定義。包含修改 `pdf_processor.py` 與 `.env.example`，將原先寫死的 300 秒超時限制改為可透過環境變數 `MINERU_TIMEOUT` 自訂的防禦性動態超時（預設為 1800 秒）。為防止設定為非數字字串導致崩潰，程式加載時將使用防禦性 `try...except` 結構，若無效則安全退回預設 1800 秒。在 SSH/SCP 複製圖片退回機制（Priority 2）上，採取**保留代碼但標記為 Deprecated（過期）＋輸出警告日誌**的策略，並將**其配置規範完整編載於 SOP 手冊中**以兼顧相容性與運維便利性。本計畫同時將建立 `tests/test_pdf_processor_timeout.py` 單元測試驗證超時邏輯，並產出標準的 `sop/2026-05-27_mineru_SOP_手冊.md`（包含本機端 SSH Keep-Alive 與遠端宿主機自動清理 cron 腳本），最後將 `TODO.md` 中的 `MODEL-10` 項目結案。後續 tasks 拆分與執行時，必須強制套用 `logging SOP` 與 `database SOP` 核查。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：
  1. **客戶端超時中斷**：處理大型書籍 PDF 時，由於 MinerU 排版分析與 OCR 耗時極長（通常需 10-30 分鐘以上），本地 Python `requests` 端寫死的 `timeout=300` 會主動拋出 `ReadTimeout` 中斷連線。
  2. **SSH 連線閒置斷開**：SSH Tunnel 在 MinerU 運算期間無數據流量，容易被防火牆或 GCE/AWS 網關因 Idle 超時自動關閉。
  3. **缺少長期運維規範**：MinerU 無自動清檔機制，遠端目錄隨時有硬碟爆滿風險，且缺乏整合性 SOP 指南。
  4. **測試覆蓋空缺與配置脆弱**：目前 `pdf_processor.py` 缺乏單元測試，且直接將環境變數轉型為 `int` 若遇到非法格式（如 `"abc"`）會直接崩潰。
  5. **MODEL-10 進度稽核**：需確認既有的 `return_images=true` 管道是否已滿足 `plans/model_optimization_blueprint.md` 4.5 節的解耦要求，並優雅處置舊版 SCP 備用方案。
- **解法**：
  1. **防禦性超時載入 (Option 1)**：在 `__init__` 中載入環境變數時，包裹在 `try...except (ValueError, TypeError)` 結構中。若環境變數設為非數字，程式不會崩潰，而是輸出警告日誌並安全退回預設 1800 秒。並將 `requests.post` 的 `timeout` 修改為此變數，防範處理書籍超時。
  2. **保留舊機制並寫入 SOP (Option A)**：保留 `pdf_processor.py` 中的 Priority 2（SCP/SSH 複製圖片）相容代碼，但於連線處加註 Deprecated 警告日誌。將這套舊有機制的完整 SSH/SCP 配置規範寫入 `sop/2026-05-27_mineru_SOP_手冊.md`，供未來隨時快速遵循與抽換，不需死磕代碼。
  3. **新建專屬單元測試**：新建 `tests/test_pdf_processor_timeout.py`，使用 `unittest.mock` 模擬 `requests.post`，驗證預設值、環境變數覆寫與非法設定的防禦性自癒 fallback (1800s)。
  4. **建立 MinerU SOP 手冊**：於 `sop/` 目錄建立 `2026-05-27_mineru_SOP_手冊.md`，整合 `.env`、`timeout`、**本機端 (Client) SSH Keep-Alive 連線維護指南**（指明於本機 `~/.ssh/config` 進行配置）、遠端舊版 SSH/SCP 圖片複製的完整規格手冊、遠端宿主機自動清理（cron）與 `docker restart` 應急排障指令。所有主機 IP 使用 `<MINERU_HOST_IP>` 動態說明以防硬編碼。考慮到內容豐富度，**行數上限由 150 放寬至 250 行**以防 Conformance Check 阻擋。
  5. **MODEL-10 審計結案與歸檔**：審計代碼，確認 Priority 1 (ZIP 自帶圖) 已讓程式完全不經過 SSH/SCP 即可透過 HTTP API 完成完整解析。確認無誤後，將 `TODO.md` 中 `MODEL-10` 結案（移入已完成表格並清理 active 列表），本案暫存於 `baton/` 的檔案於最後 Check 階段一次性 mv 與 git add 歸檔。
  6. **雙 SOP 合規核查 (BE-Refactor)**：本案屬 **BE-Refactor**，執行時必須強制執行 `logging SOP` 與 `database SOP` 審計核查。其中，針對 `_copy_images` 中加載的 `logger.warning`，**經研判其屬於正常降級/退回處理路徑（Normal Degradation Path），並非例外錯誤（Non-Exception），故無 `exc_info=True` 需求，直接輸出 `warning` 即可合規。**
- **影響**：修改 `processor/pdf_processor.py` 與 `.env.example`。新增 `tests/test_pdf_processor_timeout.py` 與 `sop/2026-05-27_mineru_SOP_手冊.md`。更新 `TODO.md` 與 `.claude-logs/prompts/INDEX.md`。無資料庫 Schema 變動，對 runtime pipeline 零迴歸影響。

---

## §2 目標規格

### 1. 程式端超時配置與防禦規格
- **超時變數化**：`processor/pdf_processor.py` 在 `__init__` 時必須載入環境變數 `MINERU_TIMEOUT`。
- **防禦性加載 (Try/Except)**：轉換環境變數至整數時，必須使用 `try...except (ValueError, TypeError)` 保護。若環境變數未設定、設定為空、或為非法字串（如 `"abc"`），必須安全退回預設的 `1800` 秒，並記錄 `logger.warning("MINERU_TIMEOUT 設定值無效，退回預設 1800 秒")`。
- **動態超時調用**：在 `requests.post(...)` 中，`timeout` 參數必須設定為 `self.MINERU_TIMEOUT`。
- **環境變數範例**：`.env.example` 中必須新增 `MINERU_TIMEOUT=1800` 與相關繁體中文註解。
- **Fallback 警告日誌 (SOP 合規規格)**：若程式因 ZIP 中無圖而不得不退回 Priority 2 執行 SCP 複製時，必須輸出 `logger.warning("[copy_images] ZIP 無圖，退回已過期 (Deprecated) 的 SCP 遠端取圖機制，請確認 MinerU 服務是否支援 return_images")`。**依據 logging SOP 判定：此退回為正常降級機制、非拋出 Exception 錯誤，故嚴禁附加 `exc_info=True`，直接進行 warning 日誌輸出即為 100% 合規。**

### 2. 新增單元測試規格
- **測試路徑**：`tests/test_pdf_processor_timeout.py`。
- **測試案例 A (預設超時)**：在不設定 `MINERU_TIMEOUT` 的情況下，mock `requests.post` 並斷言傳入的 `timeout` 等於 `1800`。
- **測試案例 B (自訂超時)**：在設定 `MINERU_TIMEOUT="600"` 的情況下，驗證 mock 傳入的 `timeout` 等於 `600`。
- **測試案例 C (防禦性容錯)**：若 `MINERU_TIMEOUT` 被設定為非數字字串時，驗證程式不崩潰且能正確自癒並安全退回預設的 `1800` 秒。

### 3. MinerU 運作與維護 SOP 規格
- **手冊路徑**：`.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md`。
- **結構要求**：必須嚴格遵守 `template_prompt_for_sop.md` 的拆分式 `§0` / `§99` 結構與元數據審計塊。
- **行數約束**：內容必須精練且結構清晰，**行數限制在 250 行以內**。
- **手冊必含主題**：
  - **環境變數配置**：`.env` 中對 `MINERU_API_URL`、`MINERU_HOST`、`MINERU_OUTPUT_DIR` 及 `MINERU_TIMEOUT` 的標準配置說明。
  - **超時對策**：針對書籍大文件調整 `MINERU_TIMEOUT` 的邏輯。
  - **SSH Tunnel Keep-Alive**：提供本機端 (Client) 連線維護指令，並詳細說明如何在 `~/.ssh/config` 中配置 `ServerAliveInterval 30` 達到免指令自動保活。
  - **(相容性備用) 遠端 SSH/SCP 圖片獲取配置規格**：完整記錄舊版 Priority 2 的 SSH 憑證信任與 SCP 連線配置要求，確保隨時可切換遵循。
  - **定期刪檔維護 (宿主機 Cron)**：提供在遠端宿主機 `/etc/cron.d/mineru-cleanup` 每日清理的指令與驗證命令，並設置標準權限 `644`。
  - **容器卡死釋放**：提供使用 `docker restart mineru` 回復記憶體與 CPU 佔用的應急排障指令。
- **動態去寫死**：IP 一律使用 `<MINERU_HOST_IP>` 或以 `MINERU_HOST` 環境變數動態代稱表示。

### 4. MODEL-10 審計與 TODO.md 結案規格
- **架構審計**：確認當 API 回傳 ZIP 且 `return_images=true` 開啟時，`shutil.copytree`（Priority 1）在本地直接解壓並複製圖片，完全不調用外部 Shell 的 `scp` 或 `ssh` 連線。
- **結案定義**：若上述 Priority 1 邏輯已被驗證能獨立穩定運行，則判定 `MODEL-10` 核心解耦目標已 100% 達成。
- **TODO 清理**：
  - 將 `TODO.md` 中的 `MODEL-10` 從「進行中/未開始」與「### MODEL」中完全移除。
  - 將其移入頂端 `## ✅ 已完成` 表格中，記錄對應 Commit 與結案說明。

### 5. 文件歸檔規格
- **SOP 驗證與治理**：全新產出的 `sop/` 檔案必須通過 `ref/WORKFLOW_SOP.md §4` 核心驗證（C1存在、C2行數、C3命名）與 A2（§0/§99結構）進階驗證。
- **歸檔流程**：將本案產出的所有提示詞檔案、執行報告等，依 `ref/WORKFLOW_SOP.md §3` 收官歸檔鐵律，一次性 `mv` 與 `git add` 歸檔至對應資料夾。

---

## §3 現況與證據

詳細盤點與本功能相關的現有程式碼邏輯與關鍵調用鏈（必須指出確切的檔案與行數，並附帶 `grep` 核查證據）：

- **`processor/pdf_processor.py`**：
  - `__init__ L24-34`：目前已載入 API_URL, HOST, OUTPUT_DIR, PAPER_NAME，但**無 `MINERU_TIMEOUT`** 變數。
  - `process L61-72`：向 MinerU 發送 POST 請求時，寫死了超時參數：
    ```python
    response = requests.post(
        self.MINERU_API_URL,
        files={"files": (mineru_upload_name, f, "application/pdf")},
        data={...},
        timeout=300  # 寫死 300 秒
    )
    ```
- **`.claude-logs/TODO.md`**：
  - `MODEL-10 L393` 與 `L469` 仍標記為 ⬜ 未開始 / 🔵 進行中。
- **`plans/model_optimization_blueprint.md`**：
  - `4.5 節 L134-138`：定義了外部服務（MinerU）連線解耦與 HTTP 傳輸的具體重構建議（用 HTTP API 代替 SCP/SSH 自帶金鑰）。

### §3.1 grep 鋼鐵證據

```bash
# 檢索 pdf_processor.py 寫死的 timeout 參數
grep -n -C 3 "timeout=" processor/pdf_processor.py
# 輸出：
# 69:                         # MinerU 3.1.6 預設 return_images=False，不設則 ZIP 無圖
# 70:                         "return_images": "true",
# 71:                     },
# 72:                     timeout=300
# 73:                 )

# 檢索 TODO.md 中的 MODEL-10 項目
grep -n "MODEL-10" .claude-logs/TODO.md
# 輸出：
# 393:- ⬜ **MODEL-10 MinerU SSH/SCP → HTTP API**（容器化前置 / 安全強化、依 model_optimization_blueprint.md §4.5）
# 469:- 🔵 MODEL-10 MinerU SSH/SCP → HTTP（容器化前置、最低優先）
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `models.py` 的資料庫 Schema 與 `Paper` 表結構（維持 100% 穩定）。
- [ ] `processor/pdf_parser.py` 的 `PDFParser` 抽象類別簽名（維持 `parse(self, pdf_path: str, output_dir: str) -> Path` 語意契約 100% 不變）。
- [ ] 既有的 `pipeline_core.py` 中 `_stage_pdf_to_md` 階段控制流與 doc-type 分流路由邏輯。
- [ ] 既有 RAG, translate, extra_info 等後續處理器的具體業務邏輯。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 專案工作流程規範 | `.claude-logs/ref/WORKFLOW_SOP.md` |
| 提示詞與計畫模板 | `.claude-logs/templates/template_plan.md` |
| SOP 撰寫規格 | `.claude-logs/templates/template_prompt_for_sop.md` |
| AI 模型改版藍圖 | `.claude-logs/plans/model_optimization_blueprint.md §4.5` |
| 日誌審查規範 | `.claude-logs/sop/2026-05-23_logging_SOP_手冊.md` |

---

## §6 驗證計畫

### §6.1 自動化單元測試

- **預計新增的測試**：
  在 `tests/test_pdf_processor_timeout.py` 中新增 3 個單元測試，模擬超時加載與防禦性錯誤處理：
  ```bash
  python3 -m pytest tests/test_pdf_processor_timeout.py -v
  ```

### §6.2 手動驗證與 Conformance 核查流程

1. **SOP 檔案稽核**：
   - 驗證 `sop/2026-05-27_mineru_SOP_手冊.md` 正確生成。
   - 執行 `wc -l` 確保內容精煉（確認小於 250 行以內）。
   - 檢查是否包含 `## §0 改版規則` 與 `## §99 治理規格` 拆分式架構。
2. **SOP 一致性核查 (Grep 驗證，對齊 §1-6)**：
   - 執行 `logging SOP` 核查（驗證 warning 無 `exc_info` 的合法性與其餘日誌規範）。
   - 執行 `database SOP` 核查（本案無 db 改動，預期 0 命中符合規範）。
3. **TODO 狀態稽核**：
   - 查看 `.claude-logs/TODO.md`，驗證 `MODEL-10` 已從未完成區塊中移除，且移入已完成表格中。
4. **檔案歸檔核查**：
   - 確保本案暫存檔案已依據收官鐵律從 `baton/` 歸檔完畢。

---

## §7 Open Questions

| 開放問題 | 推薦方案 | 推薦理由 |
|---|---|---|
| 是否要在 `pdf_processor.py` 中徹底刪除 Priority 2 的 SCP/SSH Fallback 舊代碼？ | **A (已由 baron 拍板核准)**：保留 Priority 2 兼容代碼，但於連線處加註 Deprecated 警告，並**將其配置規範完整編載於 SOP 手冊中** | 這是非常棒的運維決策。保留舊有 SCP 機制作為備用方案以應對舊版 MinerU，並將配置指南完整寫入 SOP。這能確保日後若要重新切換時可以快速遵循，無需死磕程式碼，最大程度保障系統相容性與運維便利性。 |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 MODEL-10 MinerU 連線優化與運作維護 SOP 的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 MODEL-10 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程 / 為何要做的理由；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§7 任一規格規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v4 (2026-05-27)：**雙 SOP 核查對齊**。根據人類負責人（baron）三次評估回饋修正：
  1. **工作流屬性標註**：明確標記本案計畫屬於 **BE-Refactor** 工作流性質，在 tasks 拆分與執行時必須強制執行 `logging SOP` 與 `database SOP` 審計核查。
  2. **`_copy_images` 警告日誌合規判定**：明確註記退回 Priority 2 備用路徑為「正常降級/退回處理路徑」，非程式拋出之 Exception，故依日誌規範不需附加 `exc_info=True`，直接使用 `warning` 即可 100% 合規。
- v3 (2026-05-27)：根據 baron 二次評估回饋修正：防禦性超時載入處理與 SOP 行數放寬至 250 行。
- v2 (2026-05-27)：更正為 `tests/test_pdf_processor_timeout.py` 單元測試覆蓋。
- v1 (2026-05-27)：初版建立。
