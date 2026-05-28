# INFRA-1 MinerU Pipeline Hotfix & SOP Update — Tasks

> 本文件為 INFRA-1 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md` 計畫產出，含 3 個 Commit。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 0 個 | （無新增業務檔；.bak 備份僅臨時暫存） |
| **修改檔案** | 4 個 | `processor/pdf_processor.py` / `tests/test_pdf_processor_timeout.py` / `.env.example` / `.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 3 個 | C1 → C2 → Check |
| **baton 歸檔** | 1 次 | Check 收官：`mv` baton/ 4 份暫存 → `plans/` `tasks/` `executions/` + Check 執行報告直接寫入 `executions/` |

---

## §1 TL;DR（概要）

- **挑戰**：CPU 環境下 MinerU `hybrid_auto` 後端永久卡死 Predict 0%，且 `MINERU_VIRTUAL_VRAM_SIZE` 設定導致 OOM 或拖慢 33 秒；現有測試對 `backend` 參數無覆蓋，存在 regression 風險。
- **解法**：C1 — pdf_processor backend 鎖定與單元測試（請求參數錨定與斷言測試）；C2 — SOP 手冊 CPU 推理與環境規格更新（SOP 文件運維規格補強）；Check — TODO.md 結案與全量 baton 歸檔（收官結案與物理歸檔）。
- **影響範圍**：BE-Refactor 工作流；修改 `pdf_processor.py`（comment lock）、`test_pdf_processor_timeout.py`（新增斷言）、`.env.example`（VRAM 警告）、SOP 手冊（3 章節補強）；零 API 路由與資料庫影響。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 待處理問題 |
|---|---|---|
| `processor/pdf_processor.py` L70-72 | `data` 中已包含 `"backend": "pipeline"` | 無 inline comment 說明 CPU 鎖定原因，有被誤刪 regression 風險 |
| `tests/test_pdf_processor_timeout.py` | 含 3 個測試（timeout A/B/C）| 完全無對 `backend="pipeline"` 的斷言覆蓋（plan §3.2 grep 0 命中） |
| `.env.example` L30-42 | 有 MINERU 段落，含 MINERU_TIMEOUT 說明 | 無 `MINERU_VIRTUAL_VRAM_SIZE` CPU 禁用警告 |
| `sop/2026-05-27_mineru_SOP_手冊.md` | 193 行，§1-§6 + §99 | §1 缺 VRAM 禁用條目；§2 無 CPU 後端紅線；§6 無 VRAM OOM 自愈步驟 |

---

## §3 觀察問題

### 問題 #1：backend 參數無測試覆蓋
- **證據**：`grep "backend" tests/test_pdf_processor_timeout.py` → 0 命中
- **影響**：未來重構時 `"backend": "pipeline"` 被意外移除或改為 `hybrid_auto`，無任何自動化防線攔截，CPU 環境直接卡死

### 問題 #2：SOP 缺 CPU 後端紅線規格
- **證據**：`grep -n "pipeline\|backend\|CPU\|VRAM" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` → 0 命中
- **影響**：維運人員在 CPU 環境排障時無法從 SOP 得知 `hybrid_auto` 卡死根因與 `pipeline` 強制規格

### 問題 #3：VRAM 環境變數無禁用說明
- **證據**：`grep "VRAM" .env.example` → 0 命中
- **影響**：新進人員可能在 CPU 部署時配置 `MINERU_VIRTUAL_VRAM_SIZE`，觸發 OOM 或拖慢 33 秒

---

## §4 設計方案

### §4.1 C1 — pdf_processor backend 鎖定與單元測試

1. `processor/pdf_processor.py` L70-72：在 `"backend": "pipeline"` 上方插入 2 行 inline comment，說明 CPU 鎖定原因。
2. `tests/test_pdf_processor_timeout.py`：在 `TestMineruTimeout` class 末尾追加新測試方法 `test_backend_parameter_is_pipeline`，Mock `requests.post`，斷言 `data.get("backend") == "pipeline"`。
3. `.env.example`：在 `MINERU_TIMEOUT=1800` 後插入 VRAM 警告段落（4-5 行）。

### §4.2 C2 — SOP 手冊 CPU 推理與環境規格更新

1. `sop/2026-05-27_mineru_SOP_手冊.md §1` 配置表：追加一列 `MINERU_VIRTUAL_VRAM_SIZE` 條目（標記「CPU 部署禁用」，含 OOM/拖慢數據）。
2. `sop/...§2` 超時對策：在 §2.2 後插入 `§2.3 CPU 環境後端紅線規格`（7-10 行）。
3. `sop/...§6` 容器卡死釋放：在現有 docker restart 步驟後，插入「VRAM 超配 OOM 自愈」補充步驟（8-10 行）。
4. `sop/...§99.2` Revision 歷程：追加 v2 紀錄。
5. 全程嚴守 `wc -l ≤ 250` 上限。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| 測試 Mock 對象錯誤（patch 路徑不符） | 🟡 中 | 對齊既有 3 個測試的 `patch("requests.post")` 路徑；pytest -v 若 0 collected 立即中止 |
| SOP 行數超過 250 | 🟢 低 | 每段新增前 `wc -l` 計算，控制在 220-230 行內 |
| pdf_processor.py comment 誤觸既有邏輯 | 🟢 低 | 僅插入 `#` 注釋行，不改任何業務邏輯 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# 確認 backend comment 存在
grep -n "CPU.*pipeline\|pipeline.*CPU" processor/pdf_processor.py

# 新增測試通過
venv/bin/pytest tests/test_pdf_processor_timeout.py -v
# 預期：4 passed（原 3 個 + 新增 test_backend_parameter_is_pipeline）

# 整體 pytest
venv/bin/pytest tests/ -q
# 預期：383 passed, 3 skipped
```

### §6.2 C2 驗收

```bash
# SOP 行數 ≤ 250
wc -l .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md

# §0 / §99 結構完整
grep "^## §0\|^## §99" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md

# 無硬編碼 IP（應為 0 命中）
grep -n "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md

# §2.3 CPU 後端紅線存在
grep "§2.3\|pipeline\|backend" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md | head -5

# §1 VRAM 條目存在
grep "VRAM\|CPU.*禁\|禁.*CPU" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md | head -3
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `processor/pdf_processor.py` 的 `_copy_images` ZIP 圖拷貝優先級 1 核心邏輯 — 不動
- [ ] `processor/pdf_processor.py` 的 `requests.post` data 鍵值業務邏輯（除追加 comment 外）— 不動
- [ ] `web_server.py` / `pipeline_core.py` / `paper_manager.py` — 100% 不動
- [ ] `static/*` 前端資源 — 100% 不動
- [ ] 主 repo 目錄（worktree 父目錄）— 嚴禁讀寫
- [ ] GCP 容器的 `cpus`/`memory` 硬體限制配置 — 嚴禁變更

---

## §8 推薦 Commit 拆分

### C1 — pdf_processor backend 鎖定與單元測試（請求參數錨定與斷言測試）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `processor/pdf_processor.py`（+2 行 comment）/ `tests/test_pdf_processor_timeout.py`（+1 測試方法）/ `.env.example`（+5 行 VRAM 警告）/ `.claude-logs/archive/2026-05-28_INFRA-1_C1_pdf_processor.py.bak` / `.claude-logs/archive/2026-05-28_INFRA-1_C1_test_pdf_processor_timeout.py.bak` / `.claude-logs/archive/2026-05-28_INFRA-1_C1_env.example.bak` |
| **安全性** | 🟢 高 — pdf_processor 僅加 comment，無邏輯改動；測試為純 append；.env.example 純文件 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；.bak 備份可手動還原 |
| **驗收 grep 條件** | 見 §6.1（4 passed pytest + backend comment 存在） |
| **依賴關係** | 無前置 |
| **具體實作細節** | 見下方 §8.1 |

#### §8.1 C1 詳細實作步驟

**步驟 0：備份（.bak）**
```bash
cp processor/pdf_processor.py .claude-logs/archive/2026-05-28_INFRA-1_C1_pdf_processor.py.bak
cp tests/test_pdf_processor_timeout.py .claude-logs/archive/2026-05-28_INFRA-1_C1_test_pdf_processor_timeout.py.bak
cp .env.example .claude-logs/archive/2026-05-28_INFRA-1_C1_env.example.bak
```

**步驟 1：修改 `processor/pdf_processor.py`**

在 `"backend": "pipeline"` 所在行（L72 附近，現況 grep 行為：`grep -n '"backend"' processor/pdf_processor.py` 應命中 1 行）的**上方**插入 2 行 comment：

修改前（保持其他行不動）：
```python
                data={
                    "return_md": "true",
                    "response_format_zip": "true",
                    "backend": "pipeline",
```

修改後：
```python
                data={
                    "return_md": "true",
                    "response_format_zip": "true",
                    # CPU 環境必須鎖定 pipeline backend（PaddleOCR + RapidTable）
                    # hybrid_auto（MinerU 預設）在無 GPU 時永久卡死 Predict: 0%
                    "backend": "pipeline",
```

**步驟 2：修改 `tests/test_pdf_processor_timeout.py`**

在 `TestMineruTimeout` class 最後一個方法（`test_invalid_env_fallback_to_default`）末尾之後，追加新方法：

```python
    def test_backend_parameter_is_pipeline(self, tmp_path):
        """
        Case D: requests.post data must always contain backend='pipeline'.
        CPU 環境下 hybrid_auto 永久卡死 Predict: 0%，此測試防止 regression。
        """
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        zip_bytes = _make_minimal_zip("original")

        with patch("requests.post") as mock_post:
            mock_post.return_value = _mock_response(zip_bytes)
            proc = PDFProcessor()
            try:
                proc.process(str(pdf_file), str(tmp_path / "out"))
            except Exception:
                pass  # 只關心 requests.post 收到的 data 參數

            assert mock_post.called, "requests.post should have been called"
            _, call_kwargs = mock_post.call_args
            data = call_kwargs.get("data", {})
            assert data.get("backend") == "pipeline", (
                f"Expected backend='pipeline', got {data.get('backend')!r}. "
                "CPU 環境下 hybrid_auto 會永久卡死，嚴禁移除此鎖定。"
            )
```

**步驟 3：修改 `.env.example`**

在 `MINERU_TIMEOUT=1800` 行後方插入 5 行（空行 + 4 行 VRAM 警告）：

```bash

# ⚠️  CPU 部署模式下，嚴禁設定 MINERU_VIRTUAL_VRAM_SIZE：
#     設為 8 → 程式嘗試分配 8GB 虛擬 VRAM，導致容器 OOM 崩潰
#     設為 4 → 拖慢 MinerU 推理約 33 秒（CPU 排程頻繁喚起 GPU 路徑）
#     GPU 容器中才設定此變數；CPU 部署一律保持此行被完整移除（不留空值也不留 key）。
```

**步驟 4：驗收（§6.1 指令）**

```bash
grep -n "CPU.*pipeline\|pipeline.*CPU" processor/pdf_processor.py
venv/bin/pytest tests/test_pdf_processor_timeout.py -v
venv/bin/pytest tests/ -q
```

**步驟 5：產出執行報告**（暫存 baton/，嚴禁在此 mv）
- 寫入 `.claude-logs/baton/2026-05-28_INFRA-1_C1_執行.md`

**步驟 6：baron 執行命令草稿**（寫入 `/tmp/INFRA-1_C1_msg.txt`）：
```
BE-Refactor: INFRA-1 C1 — backend=pipeline 鎖定 comment + 回歸斷言測試 + VRAM 警告

- processor/pdf_processor.py：在 "backend": "pipeline" 上方插入 2 行 CPU 鎖定原因 comment
- tests/test_pdf_processor_timeout.py：追加 test_backend_parameter_is_pipeline（Case D）
  mock requests.post，斷言 data.get("backend") == "pipeline"
- .env.example：MINERU_TIMEOUT 後補充 VRAM CPU 禁用警告（5 行）

驗收：4 passed（test_pdf_processor_timeout.py）/ 383 passed 整體
```

**git add 清單**：
```bash
git add processor/pdf_processor.py
git add tests/test_pdf_processor_timeout.py
git add .env.example
git add .claude-logs/archive/2026-05-28_INFRA-1_C1_pdf_processor.py.bak
git add .claude-logs/archive/2026-05-28_INFRA-1_C1_test_pdf_processor_timeout.py.bak
git add .claude-logs/archive/2026-05-28_INFRA-1_C1_env.example.bak
```

---

### C2 — SOP 手冊 CPU 推理與環境規格更新（SOP 文件運維規格補強）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md`（§1 +1 列 / §2 +§2.3 / §6 +VRAM 自愈 / §99.2 v2）/ `.claude-logs/archive/2026-05-28_INFRA-1_C2_mineru_SOP_手冊.md.bak` |
| **安全性** | 🟢 高 — 純文件，零業務代碼影響 |
| **可逆性** | 🟢 高 — `git revert C2`；.bak 可手動還原 |
| **驗收 grep 條件** | 見 §6.2（wc -l ≤ 250 + §2.3 存在 + VRAM 存在 + §0/§99 完整 + 0 硬編碼 IP） |
| **依賴關係** | 無前置（可獨立執行，但建議在 C1 之後） |
| **具體實作細節** | 見下方 §8.2 |

#### §8.2 C2 詳細實作步驟

**步驟 0：備份（.bak）**
```bash
cp .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md .claude-logs/archive/2026-05-28_INFRA-1_C2_mineru_SOP_手冊.md.bak
```

**步驟 1：§1 環境變數配置表 — 追加 VRAM 列**

在 `| \`MINERU_TIMEOUT\`` 條目所在的表格之後（即 `**核查指令**：` 行之前），插入新表格列：

```markdown
| `MINERU_VIRTUAL_VRAM_SIZE` | `""` (不設) | **CPU 部署禁用**。設 8 → OOM 崩潰；設 4 → 增加推理耗時 ~33 秒。僅 GPU 容器環境才設定，CPU 部署務必完整移除此變數（連 key 都不留）。 |
```

**步驟 2：§2 超時對策 — 插入 §2.3**

在 `### §2.2 防禦性容錯機制` 區塊末尾（`**核查指令**：` 之後）插入新小節：

```markdown
### §2.3 CPU 環境後端紅線規格

**🚫 嚴禁使用預設推理後端**：CPU 部署環境下，MinerU 預設的 `hybrid_auto` 推理模式會在 `Predict: 0%` 永久卡死，無法自行恢復。

**強制指定**：`processor/pdf_processor.py` 的 `requests.post` `data` 載荷必須恆常攜帶 `"backend": "pipeline"`，以 PaddleOCR + RapidTable 組合在 CPU 上穩定完成推理（18 頁文件實測約 66 秒）。

**鎖定位置**：`processor/pdf_processor.py` L70-74 的 `data` dict 中已鎖定；回歸防護由 `tests/test_pdf_processor_timeout.py::TestMineruTimeout::test_backend_parameter_is_pipeline` 斷言保護。
```

**步驟 3：§6 容器卡死釋放 — 插入 VRAM OOM 自愈**

在 §6 現有 `docker restart` + `docker logs` + `curl health check` + `等候 30–60 秒` 段落末尾，插入以下補充（以空行分隔）：

```markdown
### §6.2 VRAM 超配 OOM 自愈（CPU 部署專用）

若日誌出現 `MemoryError` / `Killed` / `OOM` 且確認為 CPU 部署環境：

```bash
# 確認 docker-compose.yml 未設定 MINERU_VIRTUAL_VRAM_SIZE
grep "VIRTUAL_VRAM" /path/to/docker-compose.yml || echo "（未設定，合規）"
# 若有設定 → 移除該行，再重新部署
docker-compose down && docker-compose up -d
```

> 不論設為 8 或 4，CPU 部署皆必須完整移除此變數（詳見 §1 表格說明）。
```

**步驟 4：§99.2 Revision 歷程追加 v2**

在 `- v1 (2026-05-27)：...` 下方追加：
```markdown
- v2 (2026-05-28)：INFRA-1 C2——§1 補 MINERU_VIRTUAL_VRAM_SIZE CPU 禁用條目 + §2.3 CPU 後端紅線規格 + §6.2 VRAM OOM 自愈步驟
```

**步驟 5：驗收（§6.2 指令）**

```bash
wc -l .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
grep "^## §0\|^## §99" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
grep -n "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
grep "§2.3\|pipeline\|backend" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md | head -5
grep "VRAM\|CPU.*禁" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md | head -3
```

**步驟 6：產出執行報告**（暫存 baton/，嚴禁在此 mv）
- 寫入 `.claude-logs/baton/2026-05-28_INFRA-1_C2_執行.md`

**步驟 7：baron 執行命令草稿**（寫入 `/tmp/INFRA-1_C2_msg.txt`）：
```
DOC-Refactor: INFRA-1 C2 — SOP 手冊 CPU 推理後端紅線 + VRAM 禁用規格補強

- sop/2026-05-27_mineru_SOP_手冊.md §1：追加 MINERU_VIRTUAL_VRAM_SIZE CPU 禁用條目
  （設 8 OOM 崩潰 / 設 4 拖慢 ~33 秒 / CPU 部署必須完整移除）
- §2.3 新增 CPU 環境後端紅線規格：hybrid_auto 卡死原因 + pipeline 強制指定
- §6.2 新增 VRAM 超配 OOM 自愈步驟：docker-compose VRAM 確認 + down/up
- §99.2 v2 Revision 歷程
- 行數 ≤ 250 合規
```

**git add 清單**：
```bash
git add .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
git add .claude-logs/archive/2026-05-28_INFRA-1_C2_mineru_SOP_手冊.md.bak
```

---

### Check — TODO.md 結案與全量 baton 歸檔（收官結案與物理歸檔）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `TODO.md`（INFRA-1 ✅ 表格寫入 + WIP 移除 + 索引更新）/ `prompts/INDEX.md`（Check 提示詞條目）/ `executions/2026-05-28_INFRA-1_Check_執行.md`（直接落地）/ baton/ 4 份 mv 歸檔 |
| **安全性** | 🟢 高 — 純文件與歸檔，零業務代碼影響 |
| **可逆性** | 🟢 高 — `git revert Check` |
| **驗收 grep 條件** | baton/ 無 INFRA-1 殘留；TODO.md INFRA-1 ✅；pytest 整體仍全綠 |
| **依賴關係** | C1 + C2 全部 baron commit 後才執行 |
| **具體實作細節** | 見下方 §8.3 |

#### §8.3 Check 詳細實作步驟

**步驟 1：提示詞歸檔 + INDEX.md 更新**
- 寫入 `.claude-logs/prompts/2026-05-28_INFRA-1_Check_提示詞.md`
- 更新 `prompts/INDEX.md`（INFRA 系列 Check 條目 + 時間排序維持 15 筆）

**步驟 2：5 維度 Conformance 驗收**
- 維度一：檔案落地（pdf_processor.py comment / 測試 4 passed / .env.example VRAM / SOP ≤250行）
- 維度二：測試通過（4 passed + 383 passed 整體）
- 維度三：TODO.md 狀態（INFRA-1 ✅ 表格 + WIP 移除 + 索引更新）
- 維度四：提示詞歸檔（Tasks + C1 + C2 + Check 四份）
- 維度五：baton/ 全量歸檔（4 份 mv + Check exec 直接落地）

**步驟 3：git log 掃描 Hash 自愈**
- 掃描 C1 / C2 Hash 填入 TODO.md 表格

**步驟 4：TODO.md 更新**
- 在 `## ✅ 已完成` 頂部新增 `### INFRA-1 MinerU Pipeline Hotfix & SOP Update` 表格（C1/C2/Check 三欄）
- 移除 `### 🔴 高優先` 中的 `🟡 INFRA-1` WIP 條目
- 更新索引區 INFRA-1 → `✅`

**步驟 5：baton/ 全量 mv 歸檔（4 份）**
```bash
mv .claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md .claude-logs/plans/
mv .claude-logs/baton/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_tasks_v1.md .claude-logs/tasks/
mv .claude-logs/baton/2026-05-28_INFRA-1_C1_執行.md .claude-logs/executions/
mv .claude-logs/baton/2026-05-28_INFRA-1_C2_執行.md .claude-logs/executions/
```

**步驟 6：Check 執行報告直接寫入 executions/**
- 寫入 `.claude-logs/executions/2026-05-28_INFRA-1_Check_執行.md`（不過 baton/）

**步驟 7：baron 執行命令草稿**（寫入 `/tmp/INFRA-1_Check_msg.txt`）：
```
DOC-Refactor: INFRA-1 Check — Conformance 驗收 + baton/ 全量歸檔 + 結案

Conformance 5 維度全通過
baton/ 4 份全量 mv 歸檔（plan/tasks/C1-exec/C2-exec）
TODO.md INFRA-1 ✅ 結案
```

**git add 清單**：
```bash
git add .claude-logs/TODO.md
git add .claude-logs/prompts/INDEX.md
git add .claude-logs/prompts/2026-05-28_INFRA-1_Tasks_v1_提示詞.md
git add .claude-logs/prompts/2026-05-28_INFRA-1_Check_提示詞.md
git add .claude-logs/executions/2026-05-28_INFRA-1_Check_執行.md
git add .claude-logs/plans/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_plan.md
git add .claude-logs/tasks/2026-05-28_INFRA-1_MinerU_Pipeline_Hotfix_tasks_v1.md
git add .claude-logs/executions/2026-05-28_INFRA-1_C1_執行.md
git add .claude-logs/executions/2026-05-28_INFRA-1_C2_執行.md
```

---

## §9 Open Questions

無。（CPU 環境下的 pipeline backend 鎖定與 VRAM 禁用規格已在 plan §7 確認無歧義。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 INFRA-1 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 INFRA-1 executions/ 執行報告 |
| **被引用方** | `<由 Antigravity 自動掃描注入>` |
| **約束事項** | 嚴禁改動業務代碼；嚴禁跨 Commit 混合；嚴禁自動 git commit/push |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | INFRA-1 全案收官後 baron 同意歸檔 |
| **重複防護** | 僅定義拆分細節與驗收指令；不重複計畫書設計脈絡；不重複 CLAUDE.md 全局規則 |

### §99.2 Revision 歷程

- v1 (2026-05-28)：初版拆分完成（INFRA-1 Tasks）
