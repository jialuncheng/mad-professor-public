# SEC-HARDEN 後端安全縱深加固 plan

> 目的：關閉 PROJECT-REVIEW 安全審查 5 個 LOW/MEDIUM 縱深項（全在 `web_server.py`）——#3 X-Forwarded-For 可偽造致 login rate-limit 繞過、#4 CORS 萬用字元、#5 內部例外字串外洩給 client、#6 主題上傳可覆寫內建主題、#8 login 使用者名 timing oracle。純後端加固（`web_server.py` + `settings.py` 新增少量 config），零前端、零 DB schema、零渲染。

---

## §0 改版規則

- 改版觸發：§1–§9 任一規格變動
- 改版規則：直接修改對應章節 + §99.2 加 Revision 紀錄
- 完整治理規格 → §99

---

## §1 TL;DR（概要）

- **挑戰**：PROJECT-REVIEW 5 個縱深安全項未修，全落於 `web_server.py`：
  - **#3**（MEDIUM）：login rate-limit 以 `X-Forwarded-For` 最左值為 key（`web_server.py:424-428`），client 可自設 → 每次換假 IP、鎖定永不觸發、對單 admin bcrypt 無限爆破。
  - **#4**（LOW）：`CORSMiddleware allow_origins=["*"]`（`:279-281`）。因未設 `allow_credentials`、cookie 不跨源、衝擊有限，仍應收斂。
  - **#5**（LOW）：內部 `str(e)` 外洩給 client——broker `(生成失敗){str(e)[:200]}`（`:168`·broad `Exception`→串流）、`processing_tasks[...]['error']=str(e)`（`:647/:761`·broad `Exception`→status SSE→前端）→ 洩檔案路徑 / schema / 堆疊上下文。（註：`:1136/:1159/:1223` 之 `HTTPException(detail=str(e))` 捕獲 `ValueError`＝合法業務驗證、非本項範圍。）
  - **#6**（LOW）：主題上傳 sanitize 檔名後未防與內建主題（`mies/kahn/kandinsky/nara`）同名 → `target.write_bytes(content)`（`:1270`）覆寫內建 CSS。
  - **#8**（LOW/INFO）：login 僅 `username == AUTH_USERNAME` 時才跑 bcrypt（`:438`）→ 錯誤使用者名回應顯著更快、洩「有效帳號」timing oracle。
- **解法**（皆最小侵入、侷限 `web_server.py` + `settings.py` 少量 config）：
  - #3：新增可信代理白名單（`settings.TRUSTED_PROXIES`）——僅當直連 peer（`request.client.host`）屬可信代理才採信 XFF、否則用 socket peer；保留 API-PERF C2「不鎖死 LB 閘道」之正當目標、同時堵偽造。
  - #4：`allow_origins` 收斂為 `settings.CORS_ALLOW_ORIGINS`（顯式來源清單），不再萬用；維持不啟用 credentials。
  - #5：**僅** broad-`Exception` client-facing 出口（broker `:168` / pipeline SSE `:647`/`:761`）回**通用訊息**、詳情 server 端 `logger.error(..., exc_info=True)`；**保留** 3 處 `except ValueError` 之 `HTTPException`（業務驗證訊息、無敏感資訊、不動）。
  - #6：新增 `BUILTIN_THEMES` frozenset 守衛——sanitize 後名稱**轉小寫**命中內建集即 400 拒絕（大小寫不敏感）。
  - #8：錯誤使用者名路徑跑一次 dummy `bcrypt.checkpw`（對固定 hash）以等化計時。
- **影響範圍**：BE-Refactor；`web_server.py`（5 點）+ `settings.py`（新增 `TRUSTED_PROXIES` / `CORS_ALLOW_ORIGINS` 2 個 config）；零前端、零 DB schema、零渲染管線。新增 config 有預設值行為變動（見 §5 / §9 OQ）。

---

## §2 目標規格

達成後最終狀態須滿足以下可檢驗條件：

1. **#3 XFF 可信代理閘控（右向左解析）**：僅當 `request.client.host ∈ settings.TRUSTED_PROXIES` 時採信 `X-Forwarded-For`；採信時**必須由右向左（right-to-left）遍歷 XFF 鏈、逐一剝除屬 `TRUSTED_PROXIES` 的代理 IP、取第一個非白名單 IP 為真實 client IP**——**嚴禁取最左值** `split(",")[0]`（攻擊者自注入 `XFF: fake_ip` 時鏈為 `fake_ip, real_client, proxy`、最左即偽造、仍可繞過）。peer 非可信 → rate-limit key = socket peer（`request.client.host`）。偽造 XFF **無法**繞過 5 次/分鐘鎖定。保留「反向代理部署下不鎖死閘道」目標——由部署設定 `TRUSTED_PROXIES` 達成。
2. **#4 CORS 收斂**：`allow_origins` = `settings.CORS_ALLOW_ORIGINS`（顯式清單、非 `*`）；`allow_credentials` 維持未啟用；跨源請求非白名單來源不獲 CORS 放行。
3. **#5 例外不外洩（僅遮蔽 broad `Exception`、保留業務 `ValueError`）**：僅將**捕獲通用 `Exception`** 之 client-facing 出口——broker sentence（`:168`）、pipeline status SSE error（`:647`/`:761`）——之 `str(e)` 改為**通用訊息**（不含路徑/堆疊）、詳情 server 端 `logger.error(..., exc_info=True)`。**排除**捕獲 `except ValueError` 的 3 處 `HTTPException(detail=str(e))`（`:1136`/`:1159`/`:1223`）——此為 `paper_manager` 主動拋之**合法業務驗證訊息**（名稱/深度/同名/上層不存在、無敏感資訊）、遮蔽將破壞 UX、**維持原樣不動**。
4. **#6 內建主題不可覆寫（大小寫不敏感）**：上傳 sanitize 後名稱**轉小寫**後 ∈ `{mies, kahn, kandinsky, nara}` → 回 400 拒絕、**不寫檔**（`sanitized.lower() in BUILTIN_THEMES`；防 macOS 等大小寫不敏感檔案系統以 `Mies.css` 覆寫 `mies.css`）；既有非內建（含 5 支已上傳）行為不變。
5. **#8 login timing 等化**：錯誤使用者名與正確使用者名錯誤密碼路徑**均執行一次 bcrypt 比對**（錯誤帳號跑模組級常數 dummy hash）；**`AUTH_PASSWORD_HASH` 未設時登入失敗亦跑一次 dummy 比對**（不洩「密碼是否已初始化」）；回應時間無顯著可區分之 username-valid 訊號。
6. **零回歸**：既有登入 / CORS 正常請求 / 主題上傳（非內建名）/ 論文處理錯誤回報功能行為正確；全套件綠燈基線不退化（現 715 passed）。
7. **SOP 合規**：#5 所有新增 `logger.error` 帶 `exc_info=True`；無任何裸 DB commit（本任務不涉 DB 寫入）。

### §2.5 候選方案（Diverse Rollout）

僅 #3（XFF）屬機制選型、語意分散候選 ≥2；其餘四項為單一直接修法（無多方案需求）。

| 方案（限 #3） | 核心做法 | trade-offs |
|---|---|---|
| **方案 A（選定）可信代理白名單閘控** | `settings.TRUSTED_PROXIES`；peer 可信才採信 XFF、否則 socket peer | 中；精準區分「可信 LB 轉發」與「直連偽造」；需部署設定；保留 API-PERF C2 目標 |
| 方案 B（否決）完全棄用 XFF、恆用 socket peer | 一律 `request.client.host` | 低工；但反向代理部署下全部 client 收斂成 LB 閘道 IP → 一人失敗鎖死全部（回退 API-PERF C2 修正的問題） |
| 方案 C（否決）取 XFF 最右非可信值 | 依可信代理數回推 | 中高；需精確知代理層數、脆；白名單方案已足 |

- **選定理由**：方案 A 同時滿足「防偽造」與「不鎖死 LB」；以部署層 `TRUSTED_PROXIES` 顯式宣告信任邊界、語意清晰。
- **否決留痕**：B 回退 API-PERF C2 已修問題；C 過脆。

---

## §3 現況與證據

- **`web_server.py`**：
  - login rate-limit（L419-457）：XFF 最左取 IP（L424-428）→ `_login_attempts` key（L432/456）；bcrypt 僅 `username==AUTH_USERNAME` 才跑（L438）。
  - CORS（L277-282）：`allow_origins/methods/headers=["*"]`，無 `allow_credentials`。
  - broker（L144/168/176/181）：`error_msg = f"(生成失敗) {str(e)[:200]}"` → sentence 串流給前端。
  - 處理錯誤（L647/761）：`processing_tasks[...]['error'] = str(e)` → status SSE。
  - HTTPException（L1136/1159/1223）：`detail=str(e)`。
  - 主題上傳（L1227-1275）：sanitize（L1251-1253）+ 路徑守衛（L1266）+ `write_bytes`（L1270）；**無內建同名守衛**；內建主題定義見 L1282（`mies/kahn/kandinsky/nara`）。
- **`settings.py`**：無 `TRUSTED_PROXIES` / `CORS_ALLOW_ORIGINS`（需新增）。

### §3.1 grep 鋼鐵證據

```bash
$ grep -n "X-Forwarded-For\|request.client\|_login_attempts" web_server.py
424:    _xff = request.headers.get("X-Forwarded-For")
426:        ip = _xff.split(",")[0].strip() or "unknown"     # ← 最左·可偽造
428:        ip = request.client.host if request.client else "unknown"
432/456: _login_attempts[ip] ...                             # ← rate-limit key

$ grep -n "allow_origins" web_server.py
279:    allow_origins=["*"],

$ grep -n "str(e)" web_server.py | grep -E "168|647|761|1136|1159|1223"
168:        error_msg = f"(生成失敗) {str(e)[:200]}"           # → 前端
647/761:  processing_tasks[...]['error'] = str(e)             # → status SSE
1136/1159/1223: raise HTTPException(status_code=400, detail=str(e))

$ grep -n "write_bytes\|內建主題" web_server.py
1270:    target.write_bytes(content)                          # ← 無內建同名守衛
1282:    1. 內建主題：mies, kahn, kandinsky, nara

$ grep -n "username == settings.AUTH_USERNAME" web_server.py
438:    if settings.AUTH_PASSWORD_HASH and username == settings.AUTH_USERNAME:   # ← bcrypt 僅正確帳號才跑（timing）

$ grep -n "TRUSTED_PROX\|CORS_ALLOW" settings.py    # 零命中（需新增 config）
```

---

## §4 跨 Phase 接縫契約

無。本任務單一模組（`web_server.py` + `settings.py` config）內改動，無 Phase/模組間資料 handoff。

---

## §5 變動風險與相容性評估

| 風險 | 等級 | 評估 / 緩解 |
|---|---|---|
| **#3 新 config 預設回退 API-PERF C2**：`TRUSTED_PROXIES` 預設空 → 反向代理部署下 client 收斂成 LB IP、一人失敗鎖死全部 | 🟡 中 | 預設**安全優先**（空＝不採信 XFF）；**明文要求**反向代理部署於 `.env` 設 `TRUSTED_PROXIES`（§9 OQ1 拍板 + 部署提醒）；直連 / 本機開發不受影響 |
| #4 CORS 收斂誤擋合法前端 | 🟢 低 | 應用自身前端為同源、不經 CORS；`CORS_ALLOW_ORIGINS` 預設含應用來源 / 本機；跨源 API 使用者需顯式加白名單 |
| #5 通用訊息降低可除錯性 | 🟢 低 | 詳情全保留於 server log（`exc_info=True`）；僅對 client 遮蔽；trace_id 仍可串連 |
| #6 誤擋合法上傳 | 🟢 低 | 僅擋 4 個內建名；既有 5 支已上傳非內建名不受影響 |
| #8 dummy bcrypt 增微小延遲 | 🟢 低 | 每次登入固定一次 bcrypt、可忽略；且為預期（等化計時） |
| BE 改動觸發 regression | 🟡 中 | §8 pytest 全套件 + §5 SOP 核查（logging/database）；新增針對性測試 |

對齊 framework §4.1 #5。

---

## §6 不可動清單

**以下在本次修改中嚴禁任何改動：**

- [ ] login **驗證邏輯本體**（bcrypt 正確性、session 設定 `auth`/`user`、成功導向）——僅改 IP 解析 + 錯帳號 dummy 比對 + 錯誤訊息，不動認證結果判定。
- [ ] 主題上傳既有 **檔名 sanitize + 路徑 traversal 守衛 + 大小限制**（L1251-1268）——僅**新增**內建同名守衛，不弱化既有。
- [ ] 論文處理 / broker 之**業務流程與 SSE 協定欄位**——僅改 error 值來源（str(e)→通用），不動串流結構。
- [ ] `settings.py` 既有 config 與 `SESSION_SECRET` fail-closed（SEC-SECRET）邏輯。
- [ ] 前端 `static/**`、DB schema、任何 `.py` 業務邏輯（除 `web_server.py` 本 5 點 + `settings.py` 新增 config + `tests/`）。
- [ ] SEC-SECRET / SEC-XSS 既有落地。

---

## §7 規格依據

| 依據名稱 | 來源位置 |
|---|---|
| 工作流分類（改 `.py` 業務邏輯、非緊急 → **BE-Refactor**） | `CLAUDE.md §2` / `ref/WORKFLOW_SOP.md §1.2` |
| **BE-Refactor 必讀 SOP** | `sop/2026-05-23_logging_SOP_手冊.md` + `sop/2026-05-23_database_SOP_手冊.md`（落地前強制 §5 核查） |
| plan 結構 SSOT | `templates/template_plan.md` |
| 六階段 / 命名 / §7.2 | `ref/WORKFLOW_SOP.md §3 / §6 / §7.2` |
| 漏洞來源 | PROJECT-REVIEW 安全審查 #3/#4/#5/#6/#8 |
| 前置關聯 | SEC-SECRET（web_server.py 認證加固·已落地）|

> ⚠️ **提示詞所列依據校正**：提示詞列 `sop/2026-07-02_frontend_效能與渲染_SOP_手冊.md`（前端 SOP），但本任務 5 項**全為後端 `web_server.py` 改動 → BE-Refactor**，前端 SOP 不適用。依 WORKFLOW_SOP §1.2，BE-Refactor 必讀 **logging + database SOP**，已於上表列正。此不符已於 §9 OQ 顯式提請 baron 確認。

---

## §8 驗證計畫

### §8.1 自動化單元測試

- **既有測試回歸**：
  ```bash
  ./venv/bin/python -m pytest tests/ -q     # 期望：綠燈基線不退化（現 715 passed）
  ```
- **預計新增測試**（`tests/test_sec_harden.py`）：
  - #3：mock 直連 peer 非可信 → 偽造 XFF 不影響 rate-limit key（同 peer 累計觸發鎖定）；peer 可信 → 採信 XFF。
  - #4：CORS 設定為顯式來源（斷言 middleware 非 `*`）。
  - #5：觸發錯誤路徑 → client 回應不含內部 `str(e)`（通用訊息）；server log 有 `exc_info`。
  - #6：上傳名 sanitize 後 = 內建名（如 `mies`）→ 400、不寫檔。
  - #8：錯誤 username 與錯誤 password 均跑 bcrypt（計時等化，或以呼叫計數斷言 dummy 比對存在）。

### §8.2 手動端到端（E2E）驗證流程（baron）

1. **#3**：直連連續 5 次錯密碼（帶不同偽造 `X-Forwarded-For`）→ 第 6 次仍被鎖（`error=locked`）。設 `TRUSTED_PROXIES` 含本機 + 帶 XFF → 依 XFF 分桶。
2. **#4**：跨源 `fetch` 非白名單來源 → 無 CORS 放行標頭。
3. **#5**：故意觸發論文處理 / API 錯誤 → 前端顯示通用訊息、無檔案路徑；server log 有完整堆疊。
4. **#6**：上傳命名為 `mies.css` 的主題 → 400 拒絕；`static/themes/mies.css` 未被覆寫。
5. **#8**：錯誤 username 與錯誤 password 之回應時間無顯著差異。

> §7.2 跨 Phase 整合測試：單一後端模組、無跨 Phase 資料 handoff（§4 標「無」），依 WORKFLOW_SOP §7.2 不適用；於 §9 OQ 顯式登記豁免。

---

## §9 Open Questions

> **拍板狀態（2026-07-12，baron review）**：OQ1–OQ7 全數採推薦定案 → execution-ready、可拆 tasks。並依 review 補強三項程式碼掃描發現，回灌 §2 #1（XFF 右向左解析）/ §2 #3（#5 排除 ValueError 業務訊息）/ §2 #4（#6 大小寫不敏感）+ OQ5（未設 hash 亦跑 dummy）。

| 開放問題 | 推薦方案（＝拍板結果） | 推薦理由 |
|---|---|---|
| OQ1：`TRUSTED_PROXIES` 預設值？空（安全·但反向代理需設）vs 預設含 loopback | **預設空（安全優先）+ 部署文件明文要求反向代理設定** | fail-safe：未設不誤信任何 XFF；直連/開發不受影響；反向代理部署顯式宣告信任邊界 |
| OQ2：`CORS_ALLOW_ORIGINS` 預設值？ | **預設含應用自身來源 + 本機開發（`localhost`/`127.0.0.1`）；生產由 env 覆寫、拒 `*`** | 應用前端同源不需 CORS；預設不放任意跨源；保留開發便利 |
| OQ3：#5 範圍？ | **僅 client-facing 且捕獲通用 `Exception` 之出口（`:168`/`:647`/`:761`）；排除 `ValueError` 業務訊息（`:1136`/`:1159`/`:1223`）** | 業務驗證訊息無敏感資訊、遮蔽破壞 UX；全 41 處 `logger.error` 補 exc_info 屬 SOP-COMPLY 另案 |
| OQ4：#6 守衛範圍？ | **僅擋內建 4 名（mies/kahn/kandinsky/nara）** | 內建為系統資產不可覆寫；已上傳為使用者內容、同 admin 覆寫可接受 |
| OQ5：#8 dummy bcrypt hash 來源？ | **模組級常數合法 bcrypt hash；且 `AUTH_PASSWORD_HASH` 未設時登入失敗亦跑一次 dummy 比對** | 固定 hash 免每次 gensalt；未設亦跑 dummy → 不洩「密碼是否已初始化」之 timing |
| OQ6：§7.2 跨 Phase 整合測試豁免 | **顯式豁免** | 單一後端模組、無資料 handoff |
| OQ7：工作流 SOP 校正（前端 SOP → logging+database SOP） | **採 BE-Refactor + logging/database SOP** | 5 項全後端 `web_server.py`；提示詞列前端 SOP 為誤（§7 已標） |

---

## §99 治理規格與 Revision

### §99.1 治理規格表

| 維度 | 內容 |
|---|---|
| **目的** | 定義 SEC-HARDEN 後端安全縱深加固的目標規格，作為後續 tasks 拆分與原子執行的唯一基準 |
| **用途** | 供 baron 審查並在 tasks.md 拆分時引用；Antigravity 階段 3 驗證時引用 |
| **權威源** | 本檔 §1–§9 |
| **引用方** | 後續 SEC-HARDEN tasks / 執行報告 |
| **被引用方** | <由 Antigravity 自動掃描注入> |
| **約束事項** | 嚴禁含設計脈絡 / 演進歷史 / 拍板過程；嚴禁含 commit 拆分（屬 tasks 階段） |
| **改版觸發條件** | §1–§9 任一規格變動 |
| **改版規則** | 直接修改對應章節 + §99.2 加 Revision 紀錄 |
| **刪除條件** | 任務全部完成，經 baron 同意且歸檔至 archive/ |
| **重複防護** | 僅定義技術規格，工作目錄與流程規格一律引用 CLAUDE.md / WORKFLOW_SOP.md |

### §99.2 Revision 歷程

- v1 (2026-07-12)：初版建立（PROJECT-REVIEW 安全 #3/#4/#5/#6/#8 衍生；蒐證 5 項現況行號〔XFF L424 / CORS L279 / str(e) L168·647·761·1136·1159·1223 / 主題 L1270·內建 L1282 / timing L438〕；#3 選定可信代理白名單方案 A；工作流校正為 BE-Refactor + logging/database SOP〔提示詞列前端 SOP 為誤〕；§7.2 豁免）
- v1.1 (2026-07-12)：baron review 拍板——OQ1–OQ7 全定案、標 execution-ready；補強三項掃描發現〔① #3 XFF 明確**右向左**遍歷剝除可信代理〔最左值仍可偽造〕→ §2 #1 / ② #5 **排除** `:1136/:1159/:1223` 之 `ValueError` 業務驗證訊息〔grep 實證三處皆 `except ValueError`·遮蔽破壞 UX〕、僅遮 broad `Exception`〔`:168/:647/:761`〕→ §1/§2 #3/§3 / ③ #6 大小寫不敏感 `sanitized.lower()`〔防 macOS 覆寫〕→ §2 #4〕+ OQ5 補「未設 hash 亦跑 dummy」；規格方向未變、僅精準化）
