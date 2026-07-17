# SEC-HARDEN 後端安全縱深加固 — Tasks

> 本文件為 SEC-HARDEN 的 Commit 拆分清單（階段 2 產出）。
> 依 `.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_plan_v1.md`（v1.1 execution-ready）產出，含 5 個 Commit（C1 → C2 → C3 → C4 → checkout）。

---

## §0 改版規則

- 改版觸發：§1–§8 任一拆分條款變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §0.5 成果盤點（Outcome Inventory）

| 類別 | 數量 | 明細 |
|---|---|---|
| **新增檔案** | 1 個 | `tests/test_sec_harden.py`（5 項守衛測試·逐 commit 追加） |
| **修改檔案** | 2 個 | `web_server.py`（5 點加固：login IP/timing、CORS、error 遮蔽、theme guard）/ `settings.py`（新增 `TRUSTED_PROXIES` / `CORS_ALLOW_ORIGINS`） |
| **目錄初始化** | 0 個 | 無 |
| **狀態更新** | 2 個 | `TODO.md` / `prompts/INDEX.md` |
| **Commits** | 5 個 | C1 → C2 → C3 → C4 → checkout |
| **baton 歸檔** | 1 次 | checkout：`mv` baton plan + tasks + C1-C4 執行報告 → `plans/` + `tasks/` + `executions/` + `git add` |

---

## §1 TL;DR（概要）

- **挑戰**：PROJECT-REVIEW 5 個縱深安全項全在 `web_server.py`（#3 XFF 偽造繞過 rate-limit / #4 CORS `*` / #5 內部例外外洩 client / #6 主題覆寫內建 / #8 login timing oracle）。
- **解法（5 commit）**：
  - **C1 — Login Hardening（登入加固）**：#3 XFF 可信代理白名單 + **右向左**解析（`settings.TRUSTED_PROXIES`）+ #8 錯帳號/未設 hash 跑 dummy bcrypt 等化計時（同 login 函式、同屬反爆破/列舉）。
  - **C2 — CORS Restriction（CORS 收斂）**：#4 `allow_origins` → `settings.CORS_ALLOW_ORIGINS` 顯式清單、不啟用 credentials。
  - **C3 — Error Masking（例外遮蔽）**：#5 broker（`:168`）/ pipeline SSE（`:647`/`:761`）之 broad `Exception` `str(e)` → 通用訊息 + `logger.error(exc_info=True)`；**排除** 3 處 `ValueError` HTTPException。
  - **C4 — Theme Overwrite Guard（主題覆寫守衛）**：#6 `BUILTIN_THEMES` frozenset + `sanitized.lower()` 命中即 400。
  - **checkout — 成果收官歸檔**。
- **影響範圍**：100% BE-Refactor（`web_server.py` + `settings.py` + `tests/`）；零前端、零 DB schema、零渲染管線。
- **不可動清單**：見 §7。

---

## §2 現況

| 檔案 | 現狀 | 缺失 |
|---|---|---|
| `web_server.py:419-457` | login：XFF 最左取 IP（L424-428）、bcrypt 僅正確帳號才跑（L438） | #3 偽造繞過 / #8 timing oracle |
| `web_server.py:277-282` | CORS `allow_origins/methods/headers=["*"]` | #4 萬用字元 |
| `web_server.py:168 / 647 / 761` | broad `except Exception` → `str(e)` 給 client | #5 例外外洩 |
| `web_server.py:1244-1270` | theme 上傳 sanitize + 路徑守衛 + `write_bytes`；內建定義 L1282 | #6 無內建同名守衛 |
| `settings.py` | 無 `TRUSTED_PROXIES` / `CORS_ALLOW_ORIGINS` | 需新增 config |

---

## §3 觀察問題

### 問題 #1（#3+#8）：login handler 反爆破 / 列舉弱點
- **證據**：`web_server.py:424-428`（XFF 最左·可偽造）、`:438`（bcrypt 僅 `username==AUTH_USERNAME` 才跑·timing）。
- **影響**：偽造 XFF 每次換假 IP 繞過 5 次/分鐘鎖定 → 無限爆破；錯帳號回應更快 → 洩有效帳號。

### 問題 #2（#4）：CORS 萬用字元
- **證據**：`web_server.py:279`（`allow_origins=["*"]`）。
- **影響**：縱深防禦缺口（現無 credentials 故衝擊有限）。

### 問題 #3（#5）：內部例外外洩 client
- **證據**：`web_server.py:168`（broker）、`:647`/`:761`（pipeline SSE）皆 broad `except Exception as e` → `str(e)` 給前端。
- **影響**：洩檔案路徑 / schema / 堆疊。（`:1136/:1159/:1223` 捕 `ValueError`＝業務驗證、**排除**。）

### 問題 #4（#6）：主題覆寫內建
- **證據**：`web_server.py:1270`（`write_bytes` 無內建同名守衛）、內建 `mies/kahn/kandinsky/nara`（L1282）。
- **影響**：上傳 `mies.css`（或 `Mies.css`）覆寫內建主題。

---

## §4 設計方案

### §4.1 C1 — Login Hardening（登入加固）
- `settings.py`：新增 `TRUSTED_PROXIES`（env 解析為 set/list、預設**空**）。
- `web_server.py` login（L419-457）：
  - IP 解析改：`peer = request.client.host`；`if peer in settings.TRUSTED_PROXIES:` → **由右向左**遍歷 `X-Forwarded-For` 鏈、剝除屬 `TRUSTED_PROXIES` 的 IP、取第一個非白名單 IP 為 `ip`；否則 `ip = peer`。**嚴禁 `split(",")[0]` 最左值**。
  - #8：定義模組級常數 dummy bcrypt hash（合法 hash 字串）；login 失敗路徑（含 `username != AUTH_USERNAME` 或 `AUTH_PASSWORD_HASH` 未設）**均跑一次 `bcrypt.checkpw(password, DUMMY_HASH)`** 等化計時。
- `tests/test_sec_harden.py`：#3（peer 非可信 → 偽造 XFF 不改 key；peer 可信 → 右向左取真實 client）+ #8（錯帳號/未設 hash 亦跑 bcrypt）。

### §4.2 C2 — CORS Restriction（CORS 收斂）
- `settings.py`：新增 `CORS_ALLOW_ORIGINS`（env 解析清單、預設含應用來源 + `localhost`/`127.0.0.1`）。
- `web_server.py:277-282`：`allow_origins=settings.CORS_ALLOW_ORIGINS`（非 `*`）；`allow_methods`/`allow_headers` 依需收斂；不啟用 `allow_credentials`。
- `tests/test_sec_harden.py`：斷言 CORS 設定非 `*`（讀 middleware 設定或 settings）。

### §4.3 C3 — Error Masking（例外遮蔽）
- `web_server.py:168`：broker `except Exception` → `error_msg = "（生成失敗）處理發生錯誤，請稍後再試"`（通用）；`logger.error("[broker] stream error ...", exc_info=True)`（詳情 server 端）。
- `web_server.py:647`/`:761`：`processing_tasks[...]['error'] = "處理失敗，請稍後再試"`（通用）；對應 `logger.error(..., exc_info=True)`。
- **排除** `:1136/:1159/:1223`（`ValueError` 業務驗證·不動）。
- `tests/test_sec_harden.py`：斷言 client-facing error 值不含 `str(e)`/路徑（以 grep 源碼守衛：`processing_tasks` error 賦值非 `str(e)`）。

### §4.4 C4 — Theme Overwrite Guard（主題覆寫守衛）
- `web_server.py`：模組級 `BUILTIN_THEMES = frozenset({"mies", "kahn", "kandinsky", "nara"})`；theme 上傳於 sanitize 後（L1253 後）加 `if sanitized.lower() in BUILTIN_THEMES: raise HTTPException(400, "不可覆寫內建主題")`（`write_bytes` 前）。
- `tests/test_sec_harden.py`：上傳名 sanitize 後 = `mies`/`Mies` → 400、不寫檔。

### §4.5 checkout — 成果收官歸檔
- `mv` baton plan → `plans/`、tasks → `tasks/`、C1-C4 執行報告 → `executions/`；逐檔 `git add`。
- 產 `executions/2026-07-12_SEC-HARDEN_checkout_執行.md`（Conformance 五維度 + staged 自檢 + §5 SOP 核查彙整 + §7.2 豁免）。

---

## §5 風險

| 風險 | 等級 | 緩解 |
|---|---|---|
| #3 `TRUSTED_PROXIES` 預設空 → 反向代理部署回退 API-PERF C2（鎖死閘道） | 🟡 中 | 預設安全優先；部署文件明文要求反向代理設 `TRUSTED_PROXIES`（plan §5/OQ1）；C1 執行報告標運維提醒 |
| #4 CORS 收斂誤擋合法前端 | 🟢 低 | 應用同源不經 CORS；預設含應用來源 + 本機 |
| #5 通用訊息降可除錯性 | 🟢 低 | 詳情 server log `exc_info`；trace_id 串連 |
| #5 誤遮業務 ValueError | 🟢 低（已規避） | C3 明確**排除** `:1136/:1159/:1223` |
| #6 誤擋合法上傳 | 🟢 低 | 僅擋 4 內建名（含大小寫變體） |
| BE 改動 regression | 🟡 中 | 每 commit 全套件 pytest + §5 SOP 核查（logging/database）；針對性測試 |

---

## §6 測試計畫

> 依「各開發階段測試同步」：`tests/test_sec_harden.py` 於 C1 建立、C2-C4 逐階段追加。

### §6.1 C1 驗收
```bash
grep -n "TRUSTED_PROXIES" settings.py web_server.py          # 期望：config + 右向左解析命中
grep -n "split(\",\")\[0\]" web_server.py || echo "已移除最左值取法"   # 期望：login 區無最左值
grep -n "DUMMY\|checkpw" web_server.py                       # 期望：dummy bcrypt 命中
./venv/bin/python -m pytest tests/test_sec_harden.py -q
```

### §6.2 C2 驗收
```bash
grep -n "CORS_ALLOW_ORIGINS\|allow_origins" web_server.py settings.py   # 期望：非 ["*"]
./venv/bin/python -m pytest tests/test_sec_harden.py -q
```

### §6.3 C3 驗收
```bash
grep -n "processing_tasks\[.*\]\['error'\] = str(e)" web_server.py || echo "已改通用訊息"   # 期望：無命中
grep -n "exc_info=True" web_server.py                        # 期望：#5 sink 新增命中
./venv/bin/python -m pytest tests/test_sec_harden.py -q
```

### §6.4 C4 驗收
```bash
grep -n "BUILTIN_THEMES\|不可覆寫內建" web_server.py           # 期望：守衛命中
./venv/bin/python -m pytest tests/test_sec_harden.py -q
```

### §6.5 全套件迴歸（每 commit）
```bash
./venv/bin/python -m pytest tests/ -q     # 期望：綠燈基線不退化（現 715 passed + 新增守衛）
```

### §6.6 §5 SOP 一致性核查（BE-Refactor·每 commit 執行報告必貼）
```bash
grep -nE "traceback.format_exc|logger\.error|logger\.exception" web_server.py settings.py | grep -v exc_info   # logging：新增 logger.error 須含 exc_info
grep -nE "\.commit\(\)" web_server.py settings.py | grep -v "with .*session.*begin()"   # database：期望無命中（本任務不涉 DB 寫入）
```

---

## §7 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] login **認證結果判定**（bcrypt 正確性、session `auth`/`user` 設定、成功導向）——僅改 IP 解析 + dummy 比對 + error 訊息。
- [ ] theme 上傳既有 **檔名 sanitize + 路徑 traversal 守衛 + 大小限制**（L1251-1268）——僅新增內建同名守衛。
- [ ] 3 處 `except ValueError` 之 `HTTPException(detail=str(e))`（`:1136/:1159/:1223`）——業務驗證訊息、維持原樣。
- [ ] broker / pipeline **SSE 協定欄位與業務流程**——僅改 error 值來源。
- [ ] `settings.py` 既有 config + `SESSION_SECRET` fail-closed（SEC-SECRET）。
- [ ] 前端 `static/**`、DB schema、任何 `.py` 業務邏輯（除 `web_server.py` 本 5 點 + `settings.py` 新增 config + `tests/`）；SEC-SECRET/SEC-XSS 既有落地。

---

## §8 推薦 Commit 拆分

### C1 — Login Hardening（登入加固）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（+`.bak`）、`settings.py`（+`.bak`）、`tests/test_sec_harden.py`（新增）；baton C1 執行報告嚴禁列入 git |
| **安全性** | 🟢 高 — 侷限 login 函式 + config；認證結果判定不動 |
| **可逆性** | 🟢 高 — `git revert C1`；`.bak` |
| **驗收 grep 條件** | 見 §6.1 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `settings.py` 新增 `TRUSTED_PROXIES = <env 解析為 set，預設空>`；② `web_server.py` login（L419-457）IP 解析改：`peer=request.client.host`；peer∈TRUSTED_PROXIES → 由**右向左**遍歷 XFF 剝除可信代理取第一個非白名單 IP，否則 `ip=peer`；**移除 `split(",")[0]` 最左值**；③ 模組級 `DUMMY_BCRYPT_HASH`（合法 bcrypt hash 常數）；login 失敗路徑（錯帳號 / `AUTH_PASSWORD_HASH` 未設）跑 `bcrypt.checkpw(password.encode(), DUMMY_BCRYPT_HASH.encode())` 等化計時；④ `tests/test_sec_harden.py` 建立 + #3/#8 測試；⑤ 改檔先產 `.bak`；⑥ §6.1 + §6.5 + §6.6 SOP 核查貼執行報告 |

### C2 — CORS Restriction（CORS 收斂）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（+`.bak`）、`settings.py`（+`.bak`）、`tests/test_sec_harden.py`（追加）；baton C2 報告嚴禁列入 |
| **安全性** | 🟢 高 — 中介層設定收斂、不啟用 credentials |
| **可逆性** | 🟢 高 — `git revert C2`；`.bak` |
| **驗收 grep 條件** | 見 §6.2 |
| **依賴關係** | 無前置（與 C1 獨立·共改 settings/web_server 不同區） |
| **具體實作細節** | ① `settings.py` 新增 `CORS_ALLOW_ORIGINS = <env 解析清單，預設含應用來源 + localhost/127.0.0.1>`；② `web_server.py:277-282` `allow_origins=settings.CORS_ALLOW_ORIGINS`、`allow_methods`/`allow_headers` 依需收斂、不啟用 `allow_credentials`；③ 測試追加 CORS 非 `*`；④ `.bak`；⑤ §6.2 + §6.5 + §6.6 |

### C3 — Error Masking（例外遮蔽）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（+`.bak`）、`tests/test_sec_harden.py`（追加）；baton C3 報告嚴禁列入 |
| **安全性** | 🟢 高 — 僅改 broad Exception client 出口、業務 ValueError 不動 |
| **可逆性** | 🟢 高 — `git revert C3`；`.bak` |
| **驗收 grep 條件** | 見 §6.3 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `web_server.py:168` broker `error_msg` 改通用訊息 + `logger.error(..., exc_info=True)`；② `:647`/`:761` `processing_tasks[...]['error']` 改通用訊息 + `logger.error(..., exc_info=True)`；③ **不動** `:1136/:1159/:1223`（ValueError）；④ 測試追加（源碼守衛：error 賦值非 `str(e)`）；⑤ `.bak`；⑥ §6.3 + §6.5 + §6.6（logging SOP：新增 logger.error 須 exc_info）|

### C4 — Theme Overwrite Guard（主題覆寫守衛）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `web_server.py`（+`.bak`）、`tests/test_sec_harden.py`（追加）；baton C4 報告嚴禁列入 |
| **安全性** | 🟢 高 — 純新增守衛、不弱化既有 sanitize/traversal |
| **可逆性** | 🟢 高 — `git revert C4`；`.bak` |
| **驗收 grep 條件** | 見 §6.4 |
| **依賴關係** | 無前置 |
| **具體實作細節** | ① `web_server.py` 模組級 `BUILTIN_THEMES = frozenset({"mies","kahn","kandinsky","nara"})`；② theme 上傳 sanitize 後（L1253 後、`write_bytes` L1270 前）加 `if sanitized.lower() in BUILTIN_THEMES: raise HTTPException(400, "不可覆寫內建主題")`；③ 測試追加（`mies`/`Mies` → 400 不寫檔）；④ `.bak`；⑤ §6.4 + §6.5 + §6.6 |

### checkout — 成果收官歸檔（成果歸檔與移出暫存）

| 維度 | 內容 |
|---|---|
| **影響範圍** | `mv` 歸檔：plan → `plans/`、tasks → `tasks/`、C1-C4 + checkout 執行報告 → `executions/`；狀態：`TODO.md`（🟡→✅ 雙層結案）、`prompts/INDEX.md`（已於 tasks 登記） |
| **安全性** | 🟢 高 — 純文件搬移 + 狀態更新 |
| **可逆性** | 🟢 高 — 文件層 `git revert` / `mv` 復位 |
| **驗收 grep 條件** | baton 歸檔後僅剩既有長駐真理源；`git diff --cached --name-only` = 宣告白名單 |
| **依賴關係** | 前置 C1/C2/C3/C4 全綠 |
| **具體實作細節** | ① 產 `executions/2026-07-12_SEC-HARDEN_checkout_執行.md`（Conformance 五維度 + staged 自檢實貼 + §5 SOP 核查彙整 + §7.2 純後端無 handoff 顯式豁免）；② `mv`（**禁 `git mv`**）baton plan/tasks/C1-C4 報告至正式目錄；③ 逐檔顯式 `git add`（plan + tasks + 5 執行報告 + `web_server.py`/`settings.py` `.bak` + `tests/test_sec_harden.py` + `TODO.md` + `prompts/INDEX.md` + SEC-HARDEN 提示詞），**禁 `git add .`/`-A`/`<目錄>`**；④ commit 前 `git diff --cached --name-only` 自檢＝宣告清單；⑤ TODO 雙層結案（active 移除 + `archive/TODO_done_archive.md` 追加表格 + 索引一行 + 類別索引）；⑥ 附一行 commit 指令（baron 手動） |

---

## §9 Open Questions

無。（plan v1.1 §9 OQ1–OQ7 已於 baron review 全數拍板結案：TRUSTED_PROXIES 預設空 / CORS 預設含應用來源+本機 / #5 僅 broad Exception 排除 ValueError / #6 僅擋內建 4 名·大小寫不敏感 / dummy hash 模組常數+未設亦跑 / §7.2 豁免 / BE-Refactor SOP 校正。）

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 SEC-HARDEN 任務的原子 Commit 拆分清單與實作細節，作為執行期 Claude Code 實作的唯一指針 |
| **用途** | 供 baron 審查並交由 Claude Code 按 Commit 序號執行；Antigravity 階段 5 驗證時引用 |
| **權威源** | 本檔 §1–§8 |
| **引用方** | 後續 SEC-HARDEN executions/ 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁改動非本 5 點之業務代碼；嚴禁動 DB schema/前端；嚴禁自動 `git commit` / `git push` |
| **改版觸發條件** | plan 規格變動 / 實作範圍調整 / baron 拍板修正 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務完全收官歸檔，經 baron 同意且移至 archive/ |
| **重複防護** | 僅定義拆分細節與驗收指令，不重複 plan 設計脈絡、不重複 CLAUDE.md 全局硬規則 |

### §99.2 Revision 歷程

- v1 (2026-07-12)：初版拆分完成（依 plan v1.1；5 commit＝C1 Login Hardening〔#3 XFF 右向左 + #8 timing·同 login 函式〕/ C2 CORS Restriction〔#4〕/ C3 Error Masking〔#5 broad Exception·排除 ValueError〕/ C4 Theme Overwrite Guard〔#6 大小寫不敏感〕/ checkout；測試逐 commit 綁定 test_sec_harden；每 commit §6.6 SOP 核查；§7.2 純後端豁免）
