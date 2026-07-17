# SEC-HARDEN C1 — Login Hardening（登入加固）執行報告

> **任務代號**：SEC-HARDEN C1
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Commit C1)
> **落地 Git Hash**：`52ebae8`（baron 已 ship·C2 階段 hash 自癒回填）
> **執行日期**：2026-07-18
> **依據**：`.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md §8 C1` / plan v1.1 §2 #1（XFF）+ #5（timing）
> **本報告為 baton 暫存文件**：嚴禁於本階段 `mv` / `git add`，待 checkout 階段一次性歸檔 `executions/`。

---

## §1 基準與完成狀態

- **基準 Commit**：`31f7500`（docs(governance): 校正 3 下游治理檔殘留已刪除 worktree 路徑）、分支 `gemini-refactor`。
- **完成狀態**：C1 代碼修改 + 測試全數完成、全套件 **729 passed / 3 skipped / 0 failed**（基線 715 + 新增 14）；**未 commit / 未 push**（依 CLAUDE.md §1.3 由 baron 手動執行）。

---

## §2 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C1 | Login Hardening：#3 XFF 可信代理閘控（右向左解析）+ #8 dummy bcrypt timing 等化 + `tests/test_sec_harden.py` | `52ebae8` |

---

## §3 變動檔案清單

| 檔案 | 動作 | 說明 |
|---|---|---|
| `settings.py` | 修改 | 新增 `TRUSTED_PROXIES` config（env 逗號分隔 → frozenset、預設空） |
| `web_server.py` | 修改 | `_DUMMY_BCRYPT_HASH` 常數 + `_resolve_client_ip` 右向左解析 + login IP 解析改呼叫 + 失敗路徑 dummy 比對 |
| `tests/test_sec_harden.py` | 新增 | 14 測試（#3 XFF 閘控 8 + #8 timing 等化 6） |
| `tests/test_api_performance_and_robustness.py` | 修改（**deviation·見 §4.4**） | `test_x_forwarded_for_parsing` 斷言由「最左值取法」更新為 C1 新契約 |
| `.claude-logs/archive/2026-07-18_SEC-HARDEN_C1_web_server.py.bak` | 新增（備份） | 修改前備份·入 git 審計 |
| `.claude-logs/archive/2026-07-18_SEC-HARDEN_C1_settings.py.bak` | 新增（備份） | 修改前備份·入 git 審計 |
| `.claude-logs/archive/2026-07-18_SEC-HARDEN_C1_test_api_performance_and_robustness.py.bak` | 新增（備份） | stale 測試修改前備份·入 git 審計 |
| `.claude-logs/TODO.md` | 修改 | C1 → ✅、C2 → 🟡 WIP、頂部日期戳 |
| `.claude-logs/prompts/2026-07-18_SEC-HARDEN_C1_run_提示詞.md` | 新增 | 提示詞歸檔（§1.2） |
| `.claude-logs/prompts/INDEX.md` | 修改 | 新條目 + SEC-HARDEN 分類節 + 時間列剔舊（FE-PERF-2 plan 移入分類節保留） |

**baton 暫存（嚴禁 git add）**：本執行報告、plan v1、tasks。

`git diff --stat`（業務碼部分·實貼）：

```
 settings.py   | 12 ++++++++++++
 web_server.py | 48 +++++++++++++++++++++++++++++++++++++++---------
 2 files changed, 51 insertions(+), 9 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因

- **#3（MEDIUM）**：login rate-limit 以 `X-Forwarded-For` **最左值**為 key（API-PERF C2 引入·`web_server.py:424-428` 舊碼）。XFF 為 client 可自設 header、最左值即攻擊者注入值 → 每次換假 IP、5 次/分鐘鎖定永不觸發、對單 admin bcrypt 無限爆破。
- **#8（LOW/INFO）**：bcrypt 比對僅在 `username == AUTH_USERNAME` 時執行（`:438`）→ 錯誤帳號回應顯著更快（μs vs ~250ms）、構成「有效帳號」timing oracle；`AUTH_PASSWORD_HASH` 未設時同樣秒回、洩「密碼未初始化」訊號。

### §4.2 修法 — #3 XFF 可信代理閘控（右向左）

`settings.py`（新增 config·預設空＝安全優先）：

```python
TRUSTED_PROXIES = frozenset(
    p.strip() for p in os.getenv("TRUSTED_PROXIES", "").split(",") if p.strip()
)
```

`web_server.py`（模組級 helper·login 內改為單行呼叫）：

```python
def _resolve_client_ip(request: Request) -> str:
    peer = request.client.host if request.client else "unknown"
    if peer in settings.TRUSTED_PROXIES:
        xff = request.headers.get("X-Forwarded-For", "")
        for hop in reversed([p.strip() for p in xff.split(",") if p.strip()]):
            if hop not in settings.TRUSTED_PROXIES:
                return hop
    return peer
```

- peer 非可信（直連 / 未設白名單）→ 完全不採信 XFF、key = socket peer → **偽造 XFF 無法繞過鎖定**。
- peer 可信 → **由右向左**遍歷 XFF 鏈、剝除白名單代理、取第一個非白名單 IP（攻擊者自注入之偽造值恆在最左、永不被採信）；鏈空 / 全可信 → 回退 peer。
- **已移除** `split(",")[0]` 最左值取法（全檔 grep 零殘留）。
- API-PERF C2「反向代理部署不鎖死閘道」目標**保留**：由部署層 `.env` 設 `TRUSTED_PROXIES` 達成。

### §4.3 修法 — #8 timing 等化

```python
_DUMMY_BCRYPT_HASH = "$2b$12$K2ZWmsDRLLhk7THprAwSreP/F05yauUdyV4GjtD4wTZKKUqRI8tzS"  # 模組級常數·合法 hash·cost 12
```

login 失敗路徑（`else` 分支·錯誤帳號 **或** `AUTH_PASSWORD_HASH` 未設）：

```python
    else:
        try:
            bcrypt.checkpw(password.encode("utf-8"), _DUMMY_BCRYPT_HASH.encode("utf-8"))
        except Exception:
            pass
```

- 兩類失敗路徑與「正確帳號錯誤密碼」路徑均恰跑一次 bcrypt（cost 12 同量級）→ 回應時間無 username-valid / hash-initialized 可區分訊號。
- **認證結果判定零改動**：`ok` 之計算分支原樣（不可動清單合規）。

### §4.4 Deviation — stale 測試契約同步（`test_api_performance_and_robustness.py`）

- **現象**：全套件首跑 1 failed——`test_x_forwarded_for_parsing`（API-PERF C2 產物）斷言「XFF 最左值作為鎖定鍵」，**正是 C1 依 plan §2 #1 明令根除的可偽造行為**；行為已改、舊斷言必然紅。
- **裁決**：與 plan 目標同向之必然衍生（先例：TEST-GREEN stale 斷言 repoint）。最小幅度改寫**該單一測試**為新契約三段斷言（peer 非可信 → 偽造 XFF 不採信；peer 可信 → 右向左取真實 IP、閘道不被鎖；無 XFF → client.host），檔內其他測試零觸碰；修改前產 `.bak` 入 git 審計。
- **範圍註**：tasks §8 C1 影響範圍未列此檔——屬執行期發現之 stale 測試、不改則違反 §6.5「綠燈基線不退化」驗收；提請 baron Check 階段確認此 deviation。

---

## §5 測試結果（真實終端輸出）

### §5.1 `git status -s`（節錄本任務相關）

```
 M settings.py
 M tests/test_api_performance_and_robustness.py
 M web_server.py
?? tests/test_sec_harden.py
?? .claude-logs/archive/2026-07-18_SEC-HARDEN_C1_web_server.py.bak
?? .claude-logs/archive/2026-07-18_SEC-HARDEN_C1_settings.py.bak
?? .claude-logs/archive/2026-07-18_SEC-HARDEN_C1_test_api_performance_and_robustness.py.bak
```

（另有 GOV-PATH-FIX checkout 之 staged 檔與 TODO/INDEX/提示詞狀態檔、非本 commit 範圍。）

### §5.2 §6.1 驗收 grep（實貼）

```
$ grep -n "TRUSTED_PROXIES" settings.py web_server.py
settings.py:141:TRUSTED_PROXIES = frozenset(
settings.py:142:    p.strip() for p in os.getenv("TRUSTED_PROXIES", "").split(",") if p.strip()
web_server.py:335:    if peer in settings.TRUSTED_PROXIES:
web_server.py:338:            if hop not in settings.TRUSTED_PROXIES:
（另 4 行為註解說明）

$ grep -n 'split(",")\[0\]' web_server.py || echo "已移除最左值取法"
已移除最左值取法

$ grep -n "DUMMY\|checkpw" web_server.py
323:_DUMMY_BCRYPT_HASH = "$2b$12$K2ZWmsDRLLhk7THprAwSreP/F05yauUdyV4GjtD4wTZKKUqRI8tzS"
461:            ok = bcrypt.checkpw(
473:            bcrypt.checkpw(password.encode("utf-8"), _DUMMY_BCRYPT_HASH.encode("utf-8"))
```

### §5.3 pytest（實貼）

```
$ ./venv/bin/python -m pytest tests/test_sec_harden.py -q
..............                                                           [100%]
14 passed in 1.54s

$ ./venv/bin/python -m pytest tests/test_api_performance_and_robustness.py tests/test_sec_harden.py -q
.........................                                                [100%]
25 passed in 1.98s

$ ./venv/bin/python -m pytest tests/ -q
729 passed, 3 skipped, 3 warnings in 54.05s
```

基線 715 passed → **729 passed**（+14 新守衛）、0 failed、綠燈不退化。

### §5.4 §6.6 SOP 一致性核查（實貼）

```
$ grep -nE "traceback.format_exc|logger\.error|logger\.exception" web_server.py settings.py | grep -v exc_info
web_server.py:170:        logger.error(          ← 多行呼叫·續行有 exc_info=True（既有·合規）
web_server.py:190:        logger.error(          ← 既有 broker DB append（無 exc_info·C1 未觸碰·屬 C3 範圍外既有債）
web_server.py:678:        logger.error(f"論文處理失敗: ...")   ← 既有（C3 #5 目標行·本 commit 不動）
web_server.py:793:        logger.error(          ← 多行呼叫·續行有 exc_info=True（既有·合規）

$ grep -nE "\.commit\(\)" web_server.py settings.py | grep -v "with .*session.*begin()"
無命中（合規）
```

**判定**：C1 **新增 0 個 `logger.error`**（logging SOP 無新增違規）；上列 4 命中皆既有代碼、其中 `:678` 正是 C3（#5 例外遮蔽）之目標行、依拆分留待 C3 處理。database SOP 零裸 commit（本 commit 不涉 DB 寫入）。

---

## §6 不可動清單遵守狀態

- [x] login **認證結果判定**（bcrypt 正確性、session `auth`/`user` 設定、成功導向 `/`）——`ok` 計算與成功分支 byte 未動；僅改 IP 解析 + 新增 `else` dummy 分支（不影響 `ok`）；`test_successful_login_unchanged` 驗證通過。
- [x] theme 上傳 sanitize / traversal / 大小限制——零觸碰（屬 C4）。
- [x] 3 處 `except ValueError` `HTTPException(detail=str(e))`——零觸碰（屬 C3 排除項）。
- [x] broker / pipeline SSE 協定與業務流程——零觸碰（屬 C3）。
- [x] `settings.py` 既有 config + SESSION_SECRET fail-closed——零觸碰、僅追加 `TRUSTED_PROXIES` 區塊。
- [x] 前端 `static/**`、DB schema——零觸碰。
- [x] SEC-SECRET / SEC-XSS 既有落地——零觸碰（`test_session_secret_failclosed` / `test_sec_xss_guard` 全數續綠）。

---

## §7 銜接

- **baton 狀態**：plan v1 / tasks / 本 C1 報告均留 `baton/` 暫存、未 mv 未 git add（收官鐵律遵守）。
- **TODO.md**：C1 → ✅（報告路徑 + hash 待 ship 註記）、C2 → 🟡 WIP、頂部日期戳更新。
- **歷史 Hash 自癒掃描（雙源）**：`grep "待 baron 回填"` 僅 1 命中——GOV-PATH-FIX「Checkout Hash」；`git log` 掃描確認 **GOV-PATH-FIX checkout commit 尚未存在**（其歸檔檔仍 staged 未 commit）→ 無 hash 可回填、佔位符如實保留；`archive/TODO_done_archive.md` 零佔位符。
- **下一步**：等 baron 確認 C1 並 commit 後，下達 **C2 — CORS Restriction（CORS 收斂·#4）** 提示詞。
- **⚠️ 運維提醒（plan §5 風險）**：反向代理（Docker/Nginx/LB）部署**必須**於 `.env` 設 `TRUSTED_PROXIES=<代理IP,逗號分隔>`，否則所有 client 的 rate-limit key 收斂為閘道 IP、一人觸發鎖定即鎖死全部（回退 API-PERF C2 修正之問題）；直連 / 本機開發不受影響。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列 3 個 .bak）

# 2. git add 清單（僅本次 C1 實質改動代碼與備份檔；baton/ 報告與 plan/tasks 不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add web_server.py
git add settings.py
git add tests/test_sec_harden.py
git add tests/test_api_performance_and_robustness.py
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C1_web_server.py.bak
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C1_settings.py.bak
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C1_test_api_performance_and_robustness.py.bak

# 3. commit message 草稿（已寫入 /tmp/SEC-HARDEN_C1_msg.txt）
cat > /tmp/SEC-HARDEN_C1_msg.txt << 'EOF'
BE-Refactor: SEC-HARDEN C1 — Login Hardening（登入加固）

1. 新增 settings.TRUSTED_PROXIES，登入 rate-limit 僅在 Peer 為可信代理時，才由右向左解析 X-Forwarded-For 鏈。
2. 移除 XFF 最左值取法，徹底封堵 IP 偽造繞過漏洞。
3. 引入模組級 dummy bcrypt hash，使無效帳號與未設定密碼 hash 時均執行 dummy 比對，等化登入 timing。
4. 建立 tests/test_sec_harden.py 針對 XFF 代理與 timing 等化進行測試驗證。
5. 同步更新 test_api_performance_and_robustness.py XFF 測試至新契約（原斷言最左值取法·deviation 見 C1 執行報告 §4.4）。
EOF

# 4. baron 手動執行（commit 前建議 git diff --cached --name-only 自檢 = 上列清單）
git commit -F /tmp/SEC-HARDEN_C1_msg.txt
```
