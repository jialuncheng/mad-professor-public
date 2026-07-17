# SEC-HARDEN C2 — CORS Restriction（CORS 收斂）執行報告

> **任務代號**：SEC-HARDEN C2
> **工作流類別**：BE-Refactor
> **狀態**：Completed (Commit C2)
> **落地 Git Hash**：`a5e2bd4`（baron 已 ship·C3 階段 hash 自癒回填）
> **執行日期**：2026-07-18
> **依據**：`.claude-logs/baton/2026-07-12_SEC-HARDEN_後端安全縱深加固_tasks.md §8 C2` / plan v1.1 §2 #2（CORS）+ OQ2
> **本報告為 baton 暫存文件**：嚴禁於本階段 `mv` / `git add`，待 checkout 階段一次性歸檔 `executions/`。

---

## §1 基準與完成狀態

- **基準 Commit**：`52ebae8`（BE-Refactor: SEC-HARDEN C1 — Login Hardening）、分支 `gemini-refactor`。
- **完成狀態**：C2 代碼修改 + 測試全數完成、全套件 **734 passed / 3 skipped / 0 failed**（C1 後基線 729 + 新增 5）；**未 commit / 未 push**（依 CLAUDE.md §1.3 由 baron 手動執行）。

---

## §2 落地 Commit 表格

| Commit | 內容 | Hash |
|---|---|---|
| C2 | CORS Restriction：`allow_origins=["*"]` → `settings.CORS_ALLOW_ORIGINS` 顯式白名單 + methods/headers 收斂 + 測試追加 | `a5e2bd4` |

---

## §3 變動檔案清單

| 檔案 | 動作 | 說明 |
|---|---|---|
| `settings.py` | 修改 | 新增 `CORS_ALLOW_ORIGINS` config（env 逗號分隔清單、預設本機 8080 兩形態、`"*"` 一律剔除） |
| `web_server.py` | 修改 | CORSMiddleware `allow_origins/methods/headers=["*"]` → 顯式白名單 + 實況 methods + `Content-Type` header；不啟用 `allow_credentials` |
| `tests/test_sec_harden.py` | 修改（追加） | +5 CORS 守衛測試（settings 非 `*` / middleware 對齊 / methods·headers 非萬用 / credentials 未啟用 / env `"*"` 剔除） |
| `.claude-logs/archive/2026-07-18_SEC-HARDEN_C2_web_server.py.bak` | 新增（備份） | 修改前備份·入 git 審計 |
| `.claude-logs/archive/2026-07-18_SEC-HARDEN_C2_settings.py.bak` | 新增（備份） | 修改前備份·入 git 審計 |
| `.claude-logs/TODO.md` | 修改 | C2 → ✅、C3 → 🟡 WIP、C1 hash 自癒 `52ebae8` |
| `.claude-logs/prompts/2026-07-18_SEC-HARDEN_C2_run_提示詞.md` | 新增 | 提示詞歸檔（§1.2） |
| `.claude-logs/prompts/INDEX.md` | 修改 | 新條目 + SEC-HARDEN 分類節追加 + 時間列剔舊（FE-PERF-2 Tasks 移入分類節保留） |

**baton 暫存（嚴禁 git add）**：本執行報告、C1 執行報告（hash 已自癒 `52ebae8`）、plan v1、tasks。

`git diff --stat`（實貼·`tests/test_sec_harden.py` 含 C2 追加）：

```
 settings.py              | 14 ++++++++++++
 tests/test_sec_harden.py | 59 +++++++++++++++++++++++++++++++++++++++++++++++-
 web_server.py            | 11 ++++++---
 3 files changed, 80 insertions(+), 4 deletions(-)
```

---

## §4 真因與修法

### §4.1 真因

**#4（LOW）**：`CORSMiddleware allow_origins=["*"]`（原 `web_server.py:279`）+ `allow_methods/allow_headers=["*"]` 全萬用。因未啟用 `allow_credentials`、cookie 不跨源、實際衝擊有限，但屬縱深防禦缺口——任意來源網頁可對 API 發跨源請求並讀取回應（無認證資料、但暴露 API 面）。

### §4.2 修法

`settings.py`（新增 config·緊接 C1 `TRUSTED_PROXIES` 區塊後）：

```python
_raw_cors_origins = os.getenv(
    "CORS_ALLOW_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080"
)
CORS_ALLOW_ORIGINS = [
    o.strip() for o in _raw_cors_origins.split(",") if o.strip() and o.strip() != "*"
]
```

- **預設值**（OQ2 拍板）：應用自身來源之本機兩形態——`uvicorn` 實跑 `0.0.0.0:8080`（`web_server.py __main__` 實證）→ `http://localhost:8080` + `http://127.0.0.1:8080`；生產由 env 覆寫實際站域。
- **拒 `*`**：解析層一律剔除萬用字元、env 誤設 `"*"` 不回退萬用。

`web_server.py`（middleware 收斂）：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
```

- `allow_methods` 依實際 API 面收斂（grep `@app.<method>` 實況：13 get / 8 post / 2 patch / 2 delete + preflight OPTIONS）。
- `allow_headers` 收斂為 `Content-Type`（跨源 JSON 所需；認證走 session cookie、無 Authorization header 消費者）。
- **不啟用 `allow_credentials`**（不可動清單·維持 cookie 不跨源）。
- 應用自身前端與 API 同源、正常瀏覽不經 CORS → 零使用者可見影響。

---

## §5 測試結果（真實終端輸出）

### §5.1 §6.2 驗收 grep（實貼）

```
$ grep -n "CORS_ALLOW_ORIGINS\|allow_origins" web_server.py settings.py
settings.py:153:    "CORS_ALLOW_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080"
settings.py:155:CORS_ALLOW_ORIGINS = [
web_server.py:283:    allow_origins=settings.CORS_ALLOW_ORIGINS,
（另 4 行為註解說明；全檔已無 allow_origins=["*"]）
```

### §5.2 pytest（實貼）

```
$ ./venv/bin/python -m pytest tests/test_sec_harden.py -q
...................                                                      [100%]
19 passed in 1.17s

$ ./venv/bin/python -m pytest tests/ -q
734 passed, 3 skipped, 3 warnings in 55.00s
```

C1 後基線 729 passed → **734 passed**（+5 CORS 守衛）、0 failed、綠燈不退化。

### §5.3 §6.6 SOP 一致性核查（實貼）

```
$ grep -nE "traceback.format_exc|logger\.error|logger\.exception" web_server.py settings.py | grep -v exc_info
web_server.py:170:        logger.error(          ← 既有多行呼叫·續行有 exc_info=True（合規）
web_server.py:190:        logger.error(          ← 既有（C1 報告已標·屬既有債）
web_server.py:683:        logger.error(f"論文處理失敗: ...")   ← 既有（C3 #5 目標行·本 commit 不動）
web_server.py:798:        logger.error(          ← 既有多行呼叫·續行有 exc_info=True（合規）

$ grep -nE "\.commit\(\)" web_server.py settings.py | grep -v "with .*session.*begin()"
無命中（合規）
```

**判定**：C2 **新增 0 個 `logger.error`**（logging SOP 無新增違規；4 命中皆既有、與 C1 報告一致）；database SOP 零裸 commit（本 commit 不涉 DB 寫入）。

---

## §6 不可動清單遵守狀態

- [x] **僅改 CORS 相關**：`web_server.py` 單一 hunk（middleware 註冊）+ `settings.py` 單一追加區塊；其餘業務邏輯 / 設定零觸碰（`git diff` 實證 3 檔）。
- [x] **嚴禁啟用 `allow_credentials`**——未傳入該參數（維持預設 False）；`test_credentials_not_enabled` 守衛通過。
- [x] login 驗證邏輯 / theme 上傳守衛 / broker·pipeline SSE——零觸碰（分屬 C1 已收、C3/C4 待做）。
- [x] `settings.py` 既有 config + SESSION_SECRET fail-closed——零觸碰、僅追加 `CORS_ALLOW_ORIGINS` 區塊。
- [x] 前端 `static/**`、DB schema——零觸碰。
- [x] SEC-SECRET / SEC-XSS / SEC-HARDEN C1 既有落地——零觸碰（相關測試全數續綠）。

---

## §7 銜接

- **baton 狀態**：plan v1 / tasks / C1 報告 / 本 C2 報告均留 `baton/` 暫存、未 mv 未 git add（收官鐵律遵守）。
- **TODO.md**：C2 → ✅、C3 → 🟡 WIP；**C1 hash 自癒回填 `52ebae8`**（baron 已 ship C1、git log 實證）。
- **歷史 Hash 自癒掃描（雙源）**：`grep "待 baron 回填"` 除本任務註記外僅 1 命中——GOV-PATH-FIX「Checkout Hash」；`git log` 掃描確認該 checkout commit **仍未存在**（歸檔檔 staged 未 commit）→ 無 hash 可回填、如實保留；`archive/TODO_done_archive.md` 零佔位符。
- **下一步**：等 baron 確認 C2 並 commit 後，下達 **C3 — Error Masking（例外遮蔽·#5 broad Exception·排除 ValueError）** 提示詞。
- **運維註**：生產 / 跨源部署時於 `.env` 設 `CORS_ALLOW_ORIGINS=<https://實際站域,...>`；未設時預設僅本機 8080 兩形態。

---

## §8 baron 執行命令

```bash
# 1. 備份檔案已完成（§3 已列 2 個 .bak）

# 2. git add 清單（僅本次 C2 實質改動代碼與備份檔；baton/ 報告與 plan/tasks 不入版控）
# ⚠️ 逐檔顯式列名，嚴禁 `git add .` / `git add -A` / `git add <目錄>`
git add web_server.py
git add settings.py
git add tests/test_sec_harden.py
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C2_web_server.py.bak
git add .claude-logs/archive/2026-07-18_SEC-HARDEN_C2_settings.py.bak

# 3. commit message 草稿（已寫入 /tmp/SEC-HARDEN_C2_msg.txt）
cat > /tmp/SEC-HARDEN_C2_msg.txt << 'EOF'
BE-Refactor: SEC-HARDEN C2 — CORS Restriction（CORS 收斂）

1. 新增 settings.CORS_ALLOW_ORIGINS，將 CORS allow_origins 收斂為顯式白名單，廢除萬用字元 "*"。
2. 白名單預設包含同源、本地 localhost 與 127.0.0.1 開發埠（8080），維持不啟用 allow_credentials 以維持原跨源安全性；解析層一律剔除 "*" 防 env 誤設回退。
3. allow_methods 依實際 API 面收斂（GET/POST/PATCH/DELETE/OPTIONS）、allow_headers 收斂為 Content-Type。
4. 於 tests/test_sec_harden.py 追加 5 個單元測試，斷言 web_server 的 CORS 中介層設定已收斂，非萬用字元。
EOF

# 4. baron 手動執行（commit 前建議 git diff --cached --name-only 自檢 = 上列清單）
git commit -F /tmp/SEC-HARDEN_C2_msg.txt
```
