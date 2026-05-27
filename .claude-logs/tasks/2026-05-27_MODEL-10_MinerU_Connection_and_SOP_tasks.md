# MODEL-10 MinerU 連線優化與運作維護 SOP — Tasks

> 本文件為 MODEL-10 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md` 計畫產出，含 3 個 Commit（C1 + C2 + Check）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 2 個 | `tests/test_pdf_processor_timeout.py`、`.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` |
| **修改檔案** | 3 個 | `processor/pdf_processor.py`、`.env.example`、`.claude-logs/TODO.md` |
| **狀態更新** | 1 個 | `.claude-logs/prompts/INDEX.md`（Check 階段追加 Run/Check 提示詞條目） |
| **Commits** | 3 個 | C1 → C2 → Check |
| **baton 歸檔** | 1 次 | Check 收官：`mv` baton plan/tasks/執行報告 → `plans/` / `tasks/` / `executions/` + `git add` |
| **.bak 備份** | 2 份 | C1：`archive/2026-05-27_MODEL-10_C1_pdf_processor.py.bak` + `archive/2026-05-27_MODEL-10_C1_env.example.bak` |

---

## §1 TL;DR（概要）

- **挑戰**：`processor/pdf_processor.py` 的 MinerU HTTP 請求超時（L71）寫死 300 秒，處理大型書籍 PDF 時（10-30 分鐘）必然觸發 `ReadTimeout`；環境變數轉型缺乏防禦性 try/except，非法字串會直接崩潰；`_copy_images` 退回 SSH/SCP 的舊路徑缺少已棄用警告；無運維 SOP 文件。
- **解法**：C1 修改 `pdf_processor.py`（`__init__` 加入 `MINERU_TIMEOUT` 防禦性載入 + L71 `timeout=self.MINERU_TIMEOUT` + Priority 2 fallback 廢棄 `logger.warning`）＋ `.env.example` 新增環境變數說明 ＋ 3 個單元測試覆蓋；C2 建立 `sop/2026-05-27_mineru_SOP_手冊.md`（≤250 行）；Check 執行 TODO.md 結案 ＋ baton/ 全量歸檔。
- **影響範圍**：BE-Refactor（C1 含業務代碼變更）+ DOC-Refactor（C2 + Check 純文件）；零資料庫 Schema 變動；零 runtime 迴歸影響。
- **不可動清單**：見 §7

---

## §2 現況

| 檔案 | 現狀 | 缺失 / 待處理問題 |
|---|---|---|
| `processor/pdf_processor.py` | `__init__` L24-34：無 `MINERU_TIMEOUT`；`process` L71：`timeout=300` 寫死；`_copy_images` L181-183：退回 Priority 2 時用 `logger.info` | 需加防禦性 `MINERU_TIMEOUT` 載入、改 `timeout=self.MINERU_TIMEOUT`、改退回 Priority 2 時為 `logger.warning` 廢棄提示 |
| `.env.example` | 無 `MINERU_TIMEOUT` 條目 | 需補充 `MINERU_TIMEOUT=1800` 及繁體中文說明 |
| `tests/test_pdf_processor_timeout.py` | 不存在 | 需新建 3 個測試（A：預設 1800 / B：自訂 600 / C：防禦性 fallback） |
| `.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` | 不存在 | 需新建（≤250 行、含 §0/§99 治理結構） |
| `.claude-logs/TODO.md` | MODEL-10 在 active 列（L393 ⬜ + L469 🔵） | 需結案移入 ✅ 完成表格 + 清除 active 條目 + 更新索引 |

---

## §3 觀察問題

### 問題 #1：MinerU 超時寫死 300 秒
- **證據**：`processor/pdf_processor.py:71` — `timeout=300`
- **影響**：書籍 PDF（10-30 分鐘）在 300 秒後必然拋出 `ReadTimeout`，導致上傳後 pipeline 中斷失敗

### 問題 #2：環境變數轉型缺乏防禦
- **證據**：`processor/pdf_processor.py:27-33` — 三個 `os.getenv(...)` 直接賦值，不含 try/except
- **影響**：若 `MINERU_TIMEOUT=abc`（非數字），直接 `int(os.getenv(...))` 會拋 `ValueError` 導致服務啟動崩潰

### 問題 #3：Priority 2 SCP fallback 無廢棄標記
- **證據**：`processor/pdf_processor.py:181-183` — `self.logger.info("[copy_images] _tmp 無圖...→ 退回 server 端取圖")`
- **影響**：ZIP 無圖時靜默走舊 SSH/SCP 路徑，運維人員無法察覺此路徑已為 deprecated 遺留機制

### 問題 #4：缺少運維 SOP 文件
- **證據**：`ls .claude-logs/sop/` — 無 mineru SOP
- **影響**：超時設定、SSH Keep-Alive 配置、遠端清檔 cron、容器應急排障均無文件可循

---

## §4 設計方案

### §4.1 C1 — MINERU_TIMEOUT 防禦性載入 + 廢棄 SCP 警告 + 單元測試

在 `__init__` 中新增防禦性環境變數載入，將 `timeout=300` 改為 `timeout=self.MINERU_TIMEOUT`，在 `_copy_images` Priority 2 退回處加入廢棄 `logger.warning`，新增 `.env.example` 說明，並建立 3 個單元測試。

### §4.2 C2 — MinerU SOP 手冊

新建 `.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md`，覆蓋：環境變數設定、超時對策、SSH Keep-Alive 配置（本機 `~/.ssh/config`）、Priority 2 SCP 相容配置規格、遠端清檔 cron、容器應急排障。≤250 行，含 §0/§99 治理結構。

### §4.3 Check — TODO.md 結案 + baton/ 全量歸檔

備份 TODO.md → 結案 MODEL-10（`✅ 已完成` 表格新增、active 清單移除、索引更新）→ 全量 mv baton/ 暫存文件 → 更新 prompts/INDEX.md（補 C1/C2/Check 提示詞條目）。

---

## §5 風險

| 風險 | 等級 | 緩解措施 |
|---|---|---|
| `pdf_processor.py` 修改引發現有 pytest regression | 🟡 中 | C1 落地後立即跑 `venv/bin/pytest tests/ -v`，確認全部 passed（預期 382+ passed） |
| `_copy_images` 的 logger.warning 誤加 exc_info=True | 🟢 低 | Plan §2 明確規定：此路徑為「正常降級」非 Exception，嚴禁 exc_info=True，直接 warning 即合規 |
| SOP 手冊超過 250 行 | 🟢 低 | C2 執行後立即 `wc -l .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` 確認 |
| 硬編碼 IP 洩漏進 SOP | 🟡 中 | SOP 中所有主機 IP 一律使用 `<MINERU_HOST_IP>` 動態佔位符 |
| TODO.md 修改時結案格式不符規範 | 🟢 低 | 參照 OPTIMIZE-1、WORKFLOW-2 等既有結案表格格式 |

---

## §6 測試計畫

### §6.1 C1 驗收

```bash
# 1. 確認 MINERU_TIMEOUT 防禦性載入已寫入
grep -n "MINERU_TIMEOUT" processor/pdf_processor.py
# 預期：__init__ 出現 try...except + self.MINERU_TIMEOUT 賦值

# 2. 確認 timeout 已由 300 改為動態變數
grep -n "timeout=" processor/pdf_processor.py
# 預期：L7x 出現 timeout=self.MINERU_TIMEOUT（300 消失）

# 3. 確認 Priority 2 廢棄 warning 存在
grep -n "Deprecated\|deprecated\|過期" processor/pdf_processor.py
# 預期：_copy_images 內出現 warning 含 "過期" 或 "Deprecated"

# 4. 確認 .env.example 已更新
grep -n "MINERU_TIMEOUT" .env.example
# 預期：出現 MINERU_TIMEOUT=1800 條目

# 5. logging SOP 核查（logger.error 必含 exc_info=True）
grep -n "traceback.format_exc\|logger\.error\|logger\.exception" processor/pdf_processor.py
# 預期：原有 L148 logger.error 仍含 exc_info=True；新增 warning 不含 exc_info=True

# 6. database SOP 核查（無裸 commit）
grep -nE "\.commit\(\)" processor/pdf_processor.py | grep -v "with .*session.*begin\(\)"
# 預期：無命中（本檔無 DB 操作，完全合規）

# 7. 全套測試
venv/bin/pytest tests/test_pdf_processor_timeout.py -v
# 預期：3 passed

venv/bin/pytest tests/ -v
# 預期：全部 passed（含原有 382 個測試零 regression）
```

### §6.2 C2 驗收

```bash
# 1. SOP 檔案存在
ls -la .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md

# 2. 行數符合規格（≤250）
wc -l .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md

# 3. §0/§99 結構存在
grep "^## §0\|^## §99" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
# 預期：出現兩行

# 4. 無硬編碼 IP（動態去寫死核查）
grep -n "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" .claude-logs/sop/2026-05-27_mineru_SOP_手冊.md
# 預期：無命中（一律使用 <MINERU_HOST_IP> 佔位）
```

### §6.3 Check 驗收

```bash
# 1. MODEL-10 已從 TODO.md active 區塊移除
grep -n "MODEL-10" .claude-logs/TODO.md
# 預期：僅出現 ✅ 已完成表格中的條目

# 2. TODO.md 備份存在
ls -la .claude-logs/archive/2026-05-27_MODEL-10_Check_TODO.md.bak

# 3. baton/ 已清空（僅剩 README.md 與其他非 MODEL-10 暫存）
ls .claude-logs/baton/
# 預期：MODEL-10 相關暫存檔已搬移至 plans/ tasks/ executions/
```

---

## §7 不可動清單

明確劃定修改邊界，防止修改邏輯溢出造成 Regression。**以下檔案與邏輯在本次修改中嚴禁任何改動：**

- [ ] `models.py` — 資料庫 Schema 與 `Paper` 表結構（維持 100% 穩定）
- [ ] `processor/pdf_parser.py` — `PDFParser` 抽象類別簽名（`parse(self, pdf_path: str, output_dir: str) -> Path` 語意契約 100% 不變）
- [ ] `pipeline_core.py` — `_stage_pdf_to_md` 階段控制流與 doc-type 分流路由邏輯（100% 不動）
- [ ] `web_server.py` — 所有端點與 FastAPI 路由（100% 不動）
- [ ] `processor/pdf_processor.py` 的 `process()` 方法整體邏輯流（僅改 L71 一處 `timeout=` 參數賦值）
- [ ] `processor/pdf_processor.py` 的 `_copy_images()` Priority 1 路徑（L174-180 ZIP copytree 邏輯 100% 不動）
- [ ] 主 repo 目錄 — 嚴禁讀寫

---

## §8 推薦 Commit 拆分

### C1 — MINERU_TIMEOUT 防禦性載入 + 廢棄 SCP 警告 + 單元測試

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改：`processor/pdf_processor.py`、`.env.example`；新增：`tests/test_pdf_processor_timeout.py`；.bak 備份：`archive/2026-05-27_MODEL-10_C1_pdf_processor.py.bak`、`archive/2026-05-27_MODEL-10_C1_env.example.bak` |
| **安全性** | 🟡 中 — 業務代碼修改（`pdf_processor.py`），但改動範圍極小（`__init__` 新增 4 行、L71 改 1 詞、`_copy_images` 改 1 行 info→warning），零 schema 變動 |
| **可逆性** | 🟢 高 — `git revert C1` 完全回滾；或直接從 `.bak` 備份還原 |
| **驗收 grep 條件** | 見本檔 §6.1 七項 grep 核查 |
| **依賴關係** | 無前置依賴；為 C2 之前置（C2 SOP 手冊需引用 MINERU_TIMEOUT 環境變數說明） |
| **具體實作細節** | **步驟 1 — 備份**：`cp processor/pdf_processor.py .claude-logs/archive/2026-05-27_MODEL-10_C1_pdf_processor.py.bak`；`cp .env.example .claude-logs/archive/2026-05-27_MODEL-10_C1_env.example.bak`<br><br>**步驟 2 — `__init__` 新增防禦性超時載入**：在 `processor/pdf_processor.py` 的 `__init__` 方法，緊接 `self.MINERU_PAPER_NAME = os.getenv("MINERU_PAPER_NAME", "original")` 之後（即原 L33 之後、`self.logger.debug` 之前），插入以下 4 行：<br>```python<br>        try:<br>            self.MINERU_TIMEOUT = int(os.getenv("MINERU_TIMEOUT", "1800"))<br>        except (ValueError, TypeError):<br>            self.logger.warning("MINERU_TIMEOUT 設定值無效，退回預設 1800 秒")<br>            self.MINERU_TIMEOUT = 1800<br>```<br><br>**步驟 3 — `process()` 改動態超時**：將 `process()` 方法中（原 L71）的 `timeout=300` 改為 `timeout=self.MINERU_TIMEOUT`<br><br>**步驟 4 — `_copy_images` 廢棄 warning**：將 `_copy_images` 中 Priority 1 `return` 之後的 `self.logger.info(f"[copy_images] _tmp 無圖（{tmp_images}）→ 退回 server 端取圖")` 改為：<br>```python<br>            self.logger.warning(<br>                "[copy_images] ZIP 無圖，退回已過期 (Deprecated) 的 SCP 遠端取圖機制，"<br>                "請確認 MinerU 服務是否支援 return_images"<br>            )<br>```<br><br>**步驟 5 — `.env.example` 新增說明**：在 `.env.example` 的 MinerU 相關設定區塊後，追加：<br>```bash<br># MinerU HTTP 請求超時（秒）。書籍 PDF 通常需 10-30 分鐘，建議設 1800 以上。<br># 若設為非數字字串，程式自動退回預設 1800 秒（防禦性容錯）。<br>MINERU_TIMEOUT=1800<br>```<br><br>**步驟 6 — 新建 `tests/test_pdf_processor_timeout.py`**：使用 `unittest.mock.patch` 模擬 `requests.post`；含 3 個測試：<br>- `test_default_timeout_is_1800`：不設 MINERU_TIMEOUT env，斷言 `requests.post` 收到 `timeout=1800`<br>- `test_custom_timeout_via_env`：設 `MINERU_TIMEOUT=600`，斷言 `timeout=600`<br>- `test_invalid_env_fallback_to_default`：設 `MINERU_TIMEOUT=abc`，斷言不崩潰且 `timeout=1800`<br><br>**步驟 7 — 驗證**：執行 §6.1 全部 grep 核查 + `venv/bin/pytest tests/test_pdf_processor_timeout.py -v` + `venv/bin/pytest tests/ -v`，確認 3 passed + 全套 passed<br><br>**步驟 8 — 產出執行報告**：寫入 `.claude-logs/baton/2026-05-27_MODEL-10_C1_執行.md`（暫存 baton/）<br><br>**步驟 9 — 產出 §8 baron 執行命令**：git add 清單 + commit message → `/tmp/MODEL-10_C1_msg.txt` |

---

### C2 — MinerU SOP 手冊建立

| 維度 | 內容 |
|---|---|
| **影響範圍** | 新增：`.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md` |
| **安全性** | 🟢 高 — 純文件新建，零 runtime 影響 |
| **可逆性** | 🟢 高 — `git revert C2` 完全回滾 |
| **驗收 grep 條件** | 見本檔 §6.2 四項核查（存在 / 行數 / §0§99 結構 / 無硬編碼 IP） |
| **依賴關係** | C1 之後執行（SOP 需引用 C1 確立的 MINERU_TIMEOUT 預設值 1800） |
| **具體實作細節** | **步驟 1 — 新建 `.claude-logs/sop/2026-05-27_mineru_SOP_手冊.md`**（≤250 行）<br><br>**必含結構**：`## §0 改版規則`、`## §99 治理規格`（含 §99.1 治理規格表 + §99.2 Revision 歷程）<br><br>**必含主題（各節精煉）**：<br>- §1 環境變數配置（`MINERU_API_URL` / `MINERU_HOST` / `MINERU_OUTPUT_DIR` / `MINERU_PAPER_NAME` / `MINERU_TIMEOUT`，含繁體中文說明）<br>- §2 超時對策（書籍 PDF 調整 `MINERU_TIMEOUT`，說明 try/except 自癒機制）<br>- §3 SSH Tunnel Keep-Alive（本機端 `~/.ssh/config` 配置 `ServerAliveInterval 30` + `ServerAliveCountMax 6`，IP 使用 `<MINERU_HOST_IP>` 佔位）<br>- §4 (相容性備用) Priority 2 遠端 SSH/SCP 圖片獲取配置規格（標記 Deprecated，說明 `MINERU_HOST` + SSH 憑證信任 + SCP 連線要求，僅供舊版 MinerU 備援）<br>- §5 定期刪檔維護（遠端宿主機 `/etc/cron.d/mineru-cleanup` 每日清理指令 + `chmod 644` + 驗證命令）<br>- §6 容器卡死釋放（`docker restart mineru` 應急排障指令）<br><br>**動態去寫死**：所有主機 IP 一律使用 `<MINERU_HOST_IP>` 佔位符，不得硬編碼任何 IP 地址<br><br>**步驟 2 — 驗證**：執行 §6.2 全部核查（wc -l / grep §0§99 / grep IP）<br><br>**步驟 3 — 產出執行報告**：寫入 `.claude-logs/baton/2026-05-27_MODEL-10_C2_執行.md`（暫存 baton/）<br><br>**步驟 4 — 產出 §8 baron 執行命令**：git add 清單 + commit message → `/tmp/MODEL-10_C2_msg.txt` |

---

### Check — TODO.md 結案 + baton/ 全量歸檔

| 維度 | 內容 |
|---|---|
| **影響範圍** | 修改：`.claude-logs/TODO.md`；更新：`.claude-logs/prompts/INDEX.md`（追加 C1/C2/Check 提示詞條目）；mv：baton/ MODEL-10 相關暫存文件 → `plans/` / `tasks/` / `executions/`；.bak 備份：`archive/2026-05-27_MODEL-10_Check_TODO.md.bak` |
| **安全性** | 🟢 高 — 純文件歸檔，零 runtime 影響 |
| **可逆性** | 🟢 高 — `git revert Check` 完全回滾；.bak 備份可還原 TODO.md |
| **驗收 grep 條件** | 見本檔 §6.3 三項核查 |
| **依賴關係** | C1 + C2 全部 ship 後才執行 |
| **具體實作細節** | **步驟 1 — 備份 TODO.md**：`cp .claude-logs/TODO.md .claude-logs/archive/2026-05-27_MODEL-10_Check_TODO.md.bak`<br><br>**步驟 2 — 掃描 git log 回填 hash**：`git log --oneline -5`，確認 MODEL-10 C1 / C2 hash<br><br>**步驟 3 — TODO.md 更新（MODEL-10 結案）**：<br>- 在 `## ✅ 已完成` 最前方新增 MODEL-10 結案表格（含 C1 / C2 / Check 三行）<br>- 從 `### 🔴 高優先` active 區塊完全移除 MODEL-10 WIP 條目<br>- 從 `### MODEL（索引區）` 更新 MODEL-10 為 `✅ ~~MODEL-10 MinerU SSH/SCP → HTTP~~`<br><br>**步驟 4 — 全量 mv 歸檔**（五份文件）：<br>- `mv baton/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_plan.md plans/`<br>- `mv baton/2026-05-27_MODEL-10_MinerU_Connection_and_SOP_tasks.md tasks/`<br>- `mv baton/2026-05-27_MODEL-10_C1_執行.md executions/`<br>- `mv baton/2026-05-27_MODEL-10_C2_執行.md executions/`<br>- `mv baton/2026-05-27_MODEL-10_Check_執行.md executions/`（Check 執行報告直接寫入 executions/）<br><br>**步驟 5 — 產出 Check 執行報告**：直接寫入 `.claude-logs/executions/2026-05-27_MODEL-10_Check_執行.md`（已歸檔目錄）<br><br>**步驟 6 — 產出 §8 baron 執行命令**：git add 清單（含所有 mv 後正式目錄檔案 + .bak + TODO.md + INDEX.md）+ commit message → `/tmp/MODEL-10_Check_msg.txt` |

---

## §9 Open Questions

無。（計畫審核三輪後，baron 已拍板所有設計決策：Option 1 防禦性載入 + Option A 保留 Priority 2 + SOP 行數上限 250 行 + exc_info=True 豁免認定。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 MODEL-10 MinerU 連線優化與運作維護 SOP 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 MODEL-10 C1 / C2 / Check 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動不可動清單（§7）；嚴禁跨 Commit 混合不同優先級文件；嚴禁自動 `git commit` / `git push`；`_copy_images` logger.warning 嚴禁附加 `exc_info=True` |
| **改版觸發條件** | 任務計畫（plan）規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複計畫書中的設計脈絡，不重複 CLAUDE.md 中的全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-05-27)：初版拆分完成（依 plan v4 baron 三輪評審後拍板規格）
