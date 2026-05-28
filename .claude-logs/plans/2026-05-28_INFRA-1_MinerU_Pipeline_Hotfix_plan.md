# INFRA-1 MinerU Pipeline Hotfix & SOP Update plan

> **本文件為 INFRA-1 任務的改版規劃書（階段 1 產出）。**
> 針對 CPU 環境下 MinerU 推理後端 `hybrid_auto` 卡死在 Predict 0% 的阻斷性問題，確立業務程式碼中的 backend 參數錨定、單元測試補強、以及 `.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` 的運維更新規格。

---

## §0 改版規則

- 改版觸發：§1–§7 任一規格條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：在 CPU 環境下，MinerU 預設的 `hybrid_auto` 後端 VLM 推理模式會永久卡死在 `Predict: 0%`，且在 GCP 容器中設定 `MINERU_VIRTUAL_VRAM_SIZE` 會導致記憶體超配而 OOM 崩溃，即使設為較小值也會拖慢 CPU 運算（耗時增加 33 秒）。
- **解法**：修改並錨定本機 `pdf_processor.py` 在呼叫 `/file_parse` API 時，強制在 `data` 中傳入 `"backend": "pipeline"` 參數；同時，必須大幅更新已建立之 `sop/2026-05-27_mineru_SOP_手冊.md`，增補 CPU 部署環境變數禁用紅線與 backend 硬規格；並在單元測試中新增對 `backend` 參數的 Mock 斷言以防未來被 Regression 退化。
- **影響**：BE-Refactor 工作流（包含 python 業務程式碼、單元測試、.env.example、SOP 文件更新）；無資料庫 Schema 與 API 路由影響；無 runtime 迴歸影響。

---

## §2 目標規格

### 2.1 業務程式碼與配置規格
* **請求後端錨定**：`processor/pdf_processor.py` 呼叫 MinerU 服務時，`requests.post` 的 `data` 載荷必須**強制且恆常攜帶 `"backend": "pipeline"`**（以多模型 PaddleOCR + RapidTable 在 CPU 上穩定跑完推理，預期 18 頁文件實測耗時約 1 分 6 秒）。
* **環境變數禁用提示**：`.env.example` 新增說明，警告在 CPU 部署模式下必須將 `MINERU_VIRTUAL_VRAM_SIZE` 等 GPU 參數移除或留空，防止 OOM 卡死。

### 2.2 SOP 運維手冊更新規格
對 `.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` 進行以下實體更新：
* **§1 變數配置表更新**：加入 `MINERU_VIRTUAL_VRAM_SIZE` 變數條目，標記為 **「CPU 部署禁用」**，並詳加說明其在 CPU 下強設 8 導致 OOM、強設 4 拖慢 33 秒的實測數據。
* **§2.2 超時與後端對策擴充**：增設 **§2.3 CPU 環境後端紅線規格**，明文規定「CPU 部署下嚴禁使用預設的 `hybrid_auto` 推理，必須且唯一指定 `backend=pipeline` 推理後端，否則會在 Predict 0% 永久卡死」。
* **§6.2 容器重啟與排障擴充**：在應急重啟排障中，補強 CPU 環境下排障時的「VRAM 超配 OOM 卡死自愈步驟」（即先確認 docker-compose.yml 已剔除 GPU/VRAM 變數，再 docker down/up 重啟）。
* **SOP 文件限制**：更新後的 SOP 手冊行數必須嚴格控制在 **250 行** 以內（原為 193 行，預計更新後在 220 行內）。

### 2.3 單元測試規格
* **單元測試斷言補強**：在 `tests/test_pdf_processor_timeout.py` 的 Test Cases 中，必須追加對 `requests.post` 接收之 `data` 參數進行斷言，確保 `backend` 鍵值必定為 `"pipeline"`。

---

## §3 現況與證據

### 3.1 程式碼現況
- **`processor/pdf_processor.py`**：
  - `process() L66-77`：目前已包含 `backend: "pipeline"` 配置：
    ```python
    response = requests.post(
        self.MINERU_API_URL,
        files={"files": (mineru_upload_name, f, "application/pdf")},
        data={
            "return_md": "true",
            "response_format_zip": "true",
            "backend": "pipeline",
            "return_images": "true",
        },
        timeout=self.MINERU_TIMEOUT
    )
    ```
- **`tests/test_pdf_processor_timeout.py`**：
  - 目前的單元測試僅斷言 `timeout` 參數與防禦性 fallback，未對 `data` 中的 `backend` 進行任何 Mock 斷言。

### 3.2 grep 鋼鐵證據

```bash
# 1. 核查當前 pdf_processor.py 中的 backend 配置
grep -n "backend" processor/pdf_processor.py
# 輸出：72:                         "backend": "pipeline",

# 2. 核查當前測試對 backend 斷言之缺失
grep "backend" tests/test_pdf_processor_timeout.py
# 輸出：（無命中，證明目前測試完全沒有對 backend="pipeline" 進行斷言覆蓋）
```

---

## §4 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `processor/pdf_processor.py` 的 `_copy_images` ZIP 圖拷貝優先級 1 核心邏輯 — 不動，確保穩定。
- [ ] GCP 容器部署中關於 `cpus: "3.0"` 和 `memory: 10G` 的硬體限制配置 — 嚴禁變更。
- [ ] 既有 API 的 HTTP 回傳 ZIP 解壓行為 — 不動。

---

## §5 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 任務原始 Hotfix 診斷書 | `.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix.md` |
| 文件治理與暫存鐵律 | `ref/WORKFLOW_SOP.md §2 & §3` |
| SOP 結構與 grep 規格 | `templates/template_prompt_for_sop.md` |

---

## §6 驗證計畫

### 6.1 自動化單元測試
* **新增測試案例**：
  在 `tests/test_pdf_processor_timeout.py` 內追加：
  - `test_backend_parameter_is_pipeline`：執行 `PDFProcessor().process()` 時，斷言 `requests.post` 收到的 payload `data` 中包含 `"backend": "pipeline"`，防範日後重構遭意外篡改。
* **測試命令**：
  ```bash
  # 跑新增測試
  venv/bin/python -m pytest tests/test_pdf_processor_timeout.py -v
  # 跑全套單元測試，預期 383 passed (新增 1)
  venv/bin/python -m pytest tests/ -v
  ```

### 6.2 手動驗證流程（文件核查）
1. **SOP 檔案行數核查**：
   ```bash
   wc -l .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
   # 預期：總行數 ≤ 250
   ```
2. **SOP 檔案結構與 IP 核查**：
   ```bash
   # 確保 §0 / §99 結構完整
   grep "^## §0\|^## §99" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
   # 確保無硬編碼 IP 洩漏（應為 0 行命中）
   grep -n "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
   ```

---

## §7 Open Questions

無。（CPU 環境下的 PaddleOCR backend 連線與 VRAM 禁用限制是目前唯一的效能最佳解答。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 INFRA-1 任務的目標技術規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§7 |
| **引用方** | 後續 INFRA-1 tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段）；暫存於 baton/ 不入版控 |
| **改版觸發條件** | §1–§7 任一規格條款變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-05-28)：初版建立（INFRA-1）
