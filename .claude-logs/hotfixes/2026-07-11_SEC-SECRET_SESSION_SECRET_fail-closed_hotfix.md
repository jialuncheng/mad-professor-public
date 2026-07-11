# SEC-SECRET hotfix — 緊急熱修復：SESSION_SECRET 硬編碼 fallback 致認證繞過（fail-closed）

> **警示**：本文件為**緊急熱修復 (Hotfix)** 紀錄，修正一個預設即不安全的認證繞過漏洞（PROJECT-REVIEW 安全審查 #1 HIGH）。
> **修復原則**：只改動受災點（`web_server.py` session 密鑰組裝 + `settings.py` 密鑰解析），嚴禁夾帶任何無關功能或重構。
> **工作流**：BE-Hotfix（動 `.py` 後端）；必讀 SOP＝logging + database；§5 SOP 一致性核查見文末。
> **暫存**：本文件依指示暫存 `baton/`；程式碼實檔未於本階段改動，diff 僅記錄於本文件供 baron 落地。

---

## 落地 Commit 表格

| # | Hash | Subject |
|---|---|---|
| **SEC-SECRET-hotfix** | `a7fa87f` | `fix(security): SESSION_SECRET fail-closed — 移除硬編碼 fallback 常數、prod 未設拒啟動、dev 臨時隨機` |

> **基準與完成狀態**：於 `3a71293`（TEST-GREEN checkout）基礎上改動；已落地 `settings.py` + `web_server.py` + 新增 `tests/test_session_secret_failclosed.py`，尚未 commit（§1.3 baron 手動）。
>
> **diff stat（真實）**：
> ```
> settings.py   | 14 +++++++++++++-
> web_server.py | 26 +++++++++++++++++++++++---
> 2 files changed, 36 insertions(+), 4 deletions(-)
> +（新增）tests/test_session_secret_failclosed.py  71 行
> ```

---

## 阻斷性問題與真因

### 1. 阻斷現象 (Block Issue)

- **現象描述**：Session cookie 的簽章金鑰在 `SESSION_SECRET` 未設定時，回退為**寫死在原始碼、且公開於本 repo** 的字串常數 `"insecure-dev-secret-change-me"`。而 `.env.example` 的 `SESSION_SECRET=` 預設為空 → **開箱即用的預設狀態就是用這把公開常數簽 cookie**。
- **受災範圍**：**整個認證體系**。`auth_guard` middleware（`web_server.py:309-317`）僅憑 `request.session.get("auth")` 放行；Starlette `SessionMiddleware` 只**簽章（HMAC via itsdangerous）不加密**，cookie 完整性 100% 依賴 `secret_key`。金鑰一旦公開，攻擊者可自簽任意 session。
- **攻擊情境（未認證 → admin 完全淪陷）**：
  1. 攻擊者取得本 repo（公開）中的常數 `"insecure-dev-secret-change-me"`。
  2. 以該 key + `itsdangerous` 自簽一個 payload 為 `{"auth": true, "user": "admin"}` 的 cookie。
  3. 帶此 cookie 請求任一受保護端點 → `auth_guard` 驗章通過 → **以 admin 身分放行，完全繞過 `bcrypt` 登入**。
- **首發訊號**（非 traceback，而是啟動即存在的靜默弱點；現行僅一行 warning 且**照常啟動服務**）：
  ```
  WARNING  SESSION_SECRET 未設定，使用臨時密鑰（重啟即失效，請於 .env 設定）
  # ↑ 訊息誤導：實際並非「隨機臨時密鑰」，而是回退為公開的硬編碼常數
  ```

### 2. 真因診斷 (Root Cause)

- **技術細節**：
  - `settings.py:132` — `SESSION_SECRET = os.getenv("SESSION_SECRET", "")`：未設定時為**空字串**。
  - `web_server.py:379` — `secret_key=settings.SESSION_SECRET or "insecure-dev-secret-change-me"`：空字串觸發 `or`，落到**可預測的硬編碼常數**。
  - `web_server.py:291-292` — 僅 `logger.warning` 提示，**未 fail-closed**，服務照常啟動並以該常數簽章。
  - 三者疊加：預設路徑（無 `.env` 設定）＝以公開常數簽 cookie＝認證形同虛設。此為典型「不安全的預設值（insecure default）+ 硬編碼密鑰（hardcoded credential, CWE-798）」。
- **定位程式碼**：
  - `settings.py#L132`
  - `web_server.py#L291-292`
  - `web_server.py#L379`
- **grep 鋼鐵證據**：
  ```bash
  $ grep -rn "SESSION_SECRET\|insecure-dev-secret" --include=*.py . | grep -v _deprecated
  settings.py:132:SESSION_SECRET = os.getenv("SESSION_SECRET", "")
  web_server.py:291:if not settings.SESSION_SECRET:
  web_server.py:292:    logger.warning("SESSION_SECRET 未設定，使用臨時密鑰（重啟即失效，請於 .env 設定）")
  web_server.py:379:    secret_key=settings.SESSION_SECRET or "insecure-dev-secret-change-me",
  # → 全庫僅此 3 個消費點，改動面完全封閉
  ```

---

## 熱修復修法 (Minimal Hotfix)

**設計原則（fail-closed）**：
- **絕不落地任何可預測的常數金鑰**（根除硬編碼 fallback）。
- **production 未設 `SESSION_SECRET` → 拒絕啟動**（`RuntimeError`），寧可不啟動也不以弱金鑰對外服務。
- **development 未設 → 每次啟動生成臨時「隨機」金鑰**（`secrets.token_urlsafe(48)`），並明確警告「重啟即失效」。
- **職責切分**：`settings.py` 負責「把密鑰解析為一個安全的非空值 + 標記是否為臨時值」（config 層不 fatal，避免誤傷不用 session 的 CLI 工具）；`web_server.py`（唯一 session 消費入口）負責「fail-closed 政策」——production + 臨時值 → 拒啟動。

### `settings.py` — 最小改動（頂部 import + 密鑰解析）

新增 `import secrets`：
```diff
 from dotenv import load_dotenv
 import os
+import secrets
 from pathlib import Path
```

`# ── 登入 / Session ──` 區塊（L129-132）：
```diff
 # ── 登入 / Session ──
 AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
 AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH", "")
-SESSION_SECRET = os.getenv("SESSION_SECRET", "")
+
+# SEC-SECRET fail-closed：未設定時絕不回退為可預測的硬編碼常數。
+# - 已設定 → 直接採用。
+# - 未設定 → 生成臨時隨機密鑰（config 層不 fatal，防誤傷不用 session 的 CLI 工具）；
+#   production 拒絕啟動之強制由 web_server.py 啟動時執行（唯一 session 消費入口）。
+_raw_session_secret = os.getenv("SESSION_SECRET", "")
+if _raw_session_secret:
+    SESSION_SECRET = _raw_session_secret
+    SESSION_SECRET_IS_EPHEMERAL = False
+else:
+    SESSION_SECRET = secrets.token_urlsafe(48)
+    SESSION_SECRET_IS_EPHEMERAL = True
```

### `web_server.py` — 最小改動（fail-closed 啟動守衛 + 移除硬編碼 fallback）

啟動警告區塊（L291-292）：
```diff
-if not settings.SESSION_SECRET:
-    logger.warning("SESSION_SECRET 未設定，使用臨時密鑰（重啟即失效，請於 .env 設定）")
+if settings.SESSION_SECRET_IS_EPHEMERAL:
+    # SEC-SECRET fail-closed：production 未設 SESSION_SECRET → 拒絕啟動，
+    # 杜絕以臨時/可預測金鑰簽章 cookie 致認證繞過。
+    if settings.ENVIRONMENT == "production":
+        raise RuntimeError(
+            "SESSION_SECRET 未設定：production 環境拒絕啟動（fail-closed）。"
+            '請於 .env 以 `python -c "import secrets; print(secrets.token_urlsafe(48))"` '
+            "產生強隨機值後設定。"
+        )
+    logger.warning(
+        "SESSION_SECRET 未設定，已生成臨時隨機密鑰（重啟即失效；"
+        "production 將直接拒絕啟動，請務必於 .env 設定以持久化 session）"
+    )
+
+# SEC-SECRET fail-closed（弱金鑰）：production 額外拒絕過弱金鑰，
+# 對齊臨時金鑰 secrets.token_urlsafe(48) 的強度基準（≥32 字元），
+# 杜絕 `SESSION_SECRET="123"` 這類已設定但可爆破的弱簽章金鑰。
+if settings.ENVIRONMENT == "production" and len(settings.SESSION_SECRET) < 32:
+    raise RuntimeError(
+        "SESSION_SECRET 長度不足 32 字元：production 環境拒絕啟動（fail-closed）。"
+        '請以 `python -c "import secrets; print(secrets.token_urlsafe(48))"` 產生強隨機值。'
+    )
```

> 註（fail-closed 順序）：先判 `SESSION_SECRET_IS_EPHEMERAL`（未設 → prod 拒啟動 / dev 臨時），再判**已設但過弱**（prod `< 32` 拒啟動）；dev 端不強制長度（開發者自負）、臨時金鑰本即 ≥32 不受影響。

`add_middleware` 金鑰組裝（L379）：
```diff
 app.add_middleware(
     SessionMiddleware,
-    secret_key=settings.SESSION_SECRET or "insecure-dev-secret-change-me",
+    secret_key=settings.SESSION_SECRET,
     session_cookie="session",
     https_only=(settings.ENVIRONMENT == "production"),
     same_site="strict",
     max_age=None,
 )
```

---

## regression 預防與 E2E 驗證

### 1. 受影響模組的單元測試（真實執行結果）

- **落地前綠燈基線**：`705 passed, 3 skipped, 0 failed`（`3a71293`）。
- **新增測試檔定向執行**：
  ```bash
  $ ./venv/bin/python -m pytest tests/test_session_secret_failclosed.py -v
  tests/test_session_secret_failclosed.py::test_dev_unset_generates_ephemeral_non_constant PASSED [ 33%]
  tests/test_session_secret_failclosed.py::test_set_secret_is_used_verbatim              PASSED [ 66%]
  tests/test_session_secret_failclosed.py::test_no_hardcoded_fallback_constant_in_source PASSED [100%]
  ============================== 3 passed in 0.02s ===============================
  ```
- **全套件迴歸（落地後）**：
  ```bash
  $ ./venv/bin/python -m pytest tests/ -q | tail -1
  708 passed, 3 skipped, 3 warnings in 48.74s
  ```
  → 705 + 3 新 = **708 passed / 0 failed**；autouse `_restore_settings_module` fixture 防污染有效、零 regression。
- **行為快檢**：`python -c "import settings; print(settings.SESSION_SECRET_IS_EPHEMERAL, len(settings.SESSION_SECRET))"` → `True 64`（dev 未設 → 臨時 token_urlsafe(48)＝64 字元）。
- **硬編碼常數根除核對**：`grep -rn "insecure-dev-secret" settings.py web_server.py` → **0 命中（已根除）**。

- **新增測試檔內容**（`tests/test_session_secret_failclosed.py`，已落地）：
  ```python
  import importlib, os, pytest

  @pytest.fixture(autouse=True)
  def _restore_settings_module():
      """防測試污染：本檔 reload(settings) 會改 settings 模組單例狀態
      （ENVIRONMENT / SESSION_SECRET），teardown 必須把 env 還原並重新 reload，
      使 settings 回到真實環境狀態，避免污染其後 20+ 個 import settings 的測試檔。"""
      snapshot = {k: os.environ.get(k) for k in ("ENVIRONMENT", "SESSION_SECRET")}
      yield
      for k, v in snapshot.items():
          if v is None:
              os.environ.pop(k, None)
          else:
              os.environ[k] = v
      import settings
      importlib.reload(settings)

  def _reload_settings(monkeypatch, env, secret):
      monkeypatch.setenv("ENVIRONMENT", env)
      if secret is None:
          monkeypatch.delenv("SESSION_SECRET", raising=False)
      else:
          monkeypatch.setenv("SESSION_SECRET", secret)
      import settings
      return importlib.reload(settings)

  def test_dev_unset_generates_ephemeral_non_constant(monkeypatch):
      s = _reload_settings(monkeypatch, "development", None)
      assert s.SESSION_SECRET_IS_EPHEMERAL is True
      assert s.SESSION_SECRET and s.SESSION_SECRET != "insecure-dev-secret-change-me"
      assert len(s.SESSION_SECRET) >= 32           # secrets.token_urlsafe(48)

  def test_set_secret_is_used_verbatim(monkeypatch):
      s = _reload_settings(monkeypatch, "production", "a-strong-real-secret-value-32chars++")
      assert s.SESSION_SECRET == "a-strong-real-secret-value-32chars++"
      assert s.SESSION_SECRET_IS_EPHEMERAL is False

  def test_no_hardcoded_fallback_constant_in_source():
      # 硬編碼 fallback 常數必須從 web_server.py + settings.py 雙檔根除（防未來落回配置檔）
      for filename in ("web_server.py", "settings.py"):
          assert "insecure-dev-secret-change-me" not in open(filename, encoding="utf-8").read()
  ```
  > 註 1：`_restore_settings_module`（autouse）確保 teardown 還原 settings 模組狀態——因 20+ 測試檔 `import settings`，若留在 production/測試金鑰狀態將成潛在地雷（今無測試讀 `settings.ENVIRONMENT`、但 `tests/` 無 conftest.py、執行序不保證、屬防禦性衛生）。
  > 註 2：production 未設 / 過弱 secret 的「拒絕啟動」發生在 `web_server.py` import 期；單元測試以常數根除檢查 + settings 分支覆蓋即足，prod 啟動拒絕由下方手動 E2E 驗。

### 2. 本地 E2E 快速復現與驗證

```bash
# (a) dev 未設 secret：啟動應成功 + 印臨時密鑰警告（不再是硬編碼常數）
$ unset SESSION_SECRET; ENVIRONMENT=development python web_server.py
#   期望 log：WARNING ... 已生成臨時隨機密鑰（重啟即失效 ...）

# (b) production 未設 secret：啟動應「拒絕啟動」（fail-closed）
$ unset SESSION_SECRET; ENVIRONMENT=production python web_server.py
#   期望：RuntimeError: SESSION_SECRET 未設定：production 環境拒絕啟動（fail-closed）...
#   程序非 0 退出、不對外服務

# (b2) production 設過弱 secret：啟動應「拒絕啟動」（弱金鑰 fail-closed）
$ SESSION_SECRET=123 ENVIRONMENT=production python web_server.py
#   期望：RuntimeError: SESSION_SECRET 長度不足 32 字元：production 環境拒絕啟動（fail-closed）...

# (c) 攻擊向量已封死：以舊硬編碼常數自簽 cookie 應被拒（簽章不符）
#   設一個真 secret 啟動後，用 "insecure-dev-secret-change-me" 簽的 {"auth":true} cookie → 401/導向登入
```

---

## 回退與備案

本 hotfix 為單一提交、改動面封閉（僅 2 檔 3 點）。若引發啟動 regression：

```bash
# 回退本 hotfix commit（保留其餘歷史）
git revert <SEC-SECRET-hotfix Hash>

# 或臨時解阻（不建議、僅救急）：於 .env 設定一個真實強隨機值即可正常啟動
python -c "import secrets; print(secrets.token_urlsafe(48))"   # 貼到 .env 的 SESSION_SECRET
```

---

## §5 SOP 一致性核查（BE-Hotfix 落地前強制）

> 核查對象＝本 hotfix 變動區（`settings.py` 密鑰解析區 + `web_server.py` L291-292 / L379）。

### §5.1 logging 核查

```bash
$ grep -nE "traceback.format_exc|logger\.error|logger\.exception" <本 hotfix 變動區>
```
- **結果**：本 hotfix 變動區**無命中（合規）**。新增碼僅 `logger.warning`（config-error 情境、無 exception context，無需 `exc_info`）與 `raise RuntimeError`（fail-closed、由未捕捉例外直接終止啟動，符合預期）。
- 註：`web_server.py:628/743` 等既有 `logger.error(... {str(e)})` 缺 `exc_info` 屬 PROJECT-REVIEW 程式碼品質 #1、歸 **SOP-COMPLY 另案**，**不在本 hotfix 觸及範圍**（最小侵入原則）。

### §5.2 database 核查

```bash
$ grep -nE "\.commit\(\)" web_server.py settings.py | grep -v "with .*session.*begin()"
```
- **結果**：**無命中（合規）**。本 hotfix 不涉及任何資料庫交易。

---

## 附註：影響範圍與相容性

- **改動面**：`settings.py`（+`import secrets`、密鑰解析 4→9 行）、`web_server.py`（L291-292 警告區改 fail-closed 啟動守衛〔未設 + 弱金鑰雙檢查〕、L379 金鑰組裝）；全庫 SESSION_SECRET 消費點僅此，無其他呼叫者受影響（grep 實證）。
- **相容性**：已於 `.env` 設定 `SESSION_SECRET` 的環境（正式部署）→ 行為**完全不變**（走 `_raw_session_secret` 分支）。僅改變「未設定」的預設行為（dev 臨時隨機 / prod 拒啟動）。
- **無 schema / API 簽名變動**；`SESSION_SECRET_IS_EPHEMERAL` 為新增模組級旗標、向後相容。
- **運維提醒（baron）**：各環境 `.env` 若尚未設 `SESSION_SECRET`，**production 部署前必須先設定**（否則落地後拒絕啟動——此即 fail-closed 的預期行為）。

---

## §8 baron 執行命令（§1.3：baron 手動執行）

```bash
# 1. 備份檔案已完成（已存至 .claude-logs/archive/）
#    .claude-logs/archive/2026-07-11_SEC-SECRET_SEC-SECRET-hotfix_settings.py.bak
#    .claude-logs/archive/2026-07-11_SEC-SECRET_SEC-SECRET-hotfix_web_server.py.bak

# 2. git add 清單（逐檔顯式列名，嚴禁 `git add .` / `-A` / `<目錄>`）
#    commit 前以 `git diff --cached --name-only` 自檢 staged 集合＝本清單
git add settings.py
git add web_server.py
git add tests/test_session_secret_failclosed.py
git add .claude-logs/archive/2026-07-11_SEC-SECRET_SEC-SECRET-hotfix_settings.py.bak
git add .claude-logs/archive/2026-07-11_SEC-SECRET_SEC-SECRET-hotfix_web_server.py.bak

# 3. commit message 草稿
cat > /tmp/SEC-SECRET_SEC-SECRET-hotfix_msg.txt << 'EOF'
fix(security): SESSION_SECRET fail-closed — 移除硬編碼 fallback 常數

- settings.py：未設 SESSION_SECRET 時生成臨時隨機密鑰（secrets.token_urlsafe(48)）、
  新增 SESSION_SECRET_IS_EPHEMERAL 旗標；根除以空字串回退為可預測常數
- web_server.py：production 未設 / 過弱（<32）SESSION_SECRET → 拒絕啟動（fail-closed）；
  dev → 臨時隨機 + 警告；add_middleware 移除 `or "insecure-dev-secret-change-me"`
- tests：新增 test_session_secret_failclosed.py（3 測試·含 autouse 防污染 fixture）

修復 PROJECT-REVIEW 安全 #1（HIGH）：公開硬編碼簽章金鑰致 admin 認證繞過（CWE-798）
EOF

# 4. baron 手動執行
git commit -F /tmp/SEC-SECRET_SEC-SECRET-hotfix_msg.txt
```

> ⚠️ **本 hotfix 文件（本檔）暫存 `baton/`，不在上方 commit 內**：依 WORKFLOW_SOP §3 baton 鐵律，須待收官（Checkout）階段由 baron 一次性 `mv .claude-logs/baton/2026-07-11_SEC-SECRET_..._hotfix.md .claude-logs/hotfixes/` + `git add`，不在程式碼 commit 內夾帶。

---

## Revision（文件審查軌跡）

- v1（2026-07-11）：初版——fail-closed 三處修法（settings 臨時隨機 + 旗標 / web_server prod 拒啟動 + 移除硬編碼常數）+ §5 SOP 核查 + commit 草稿。
- v2（2026-07-12）：baron review 補強三項——① 測試加 `_restore_settings_module` autouse fixture 防 settings 模組單例污染（20+ 測試檔 import settings）；② web_server 加 production 弱金鑰守衛（`len < 32` 拒啟動）；③ 常數根除檢查涵蓋 `settings.py`（雙檔）。規格方向不變、僅健壯性補強。
- v3（2026-07-12）：Run 落地——實檔改動 settings.py + web_server.py + 新增 tests/test_session_secret_failclosed.py（3 passed）；全套件 708 passed / 0 failed 零迴歸；§5 SOP 雙核查合規；補真實 diff stat / pytest 輸出 / §8 baron 執行命令（逐檔 git add 含 archive/ 2 .bak）。`.bak` 依 §3 鐵律納入 commit git add 清單。
