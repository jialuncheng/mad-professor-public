# 2026-05-20 StaticFiles mount 修復（CSS 404）

只動 `web_server.py`，新增 1 行 `app.mount` + 2 行說明註解。未改業務邏輯／
auth_guard／_PUBLIC_PREFIXES／_PUBLIC_PATHS／index.html／login.html／其他檔案。

## 問題
`web_server.py` 未掛 `/static/*` 靜態路由 → 登入後請求
`/static/themes/kahn.css` 等資源回 404（無對應路由匹配）。

## 修法
在 `SessionMiddleware` 之後、`@app.get("/login")` 之前加：
```python
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
```
- `StaticFiles` 既有 import（行 19）；`BASE_DIR` 既有定義（行 76，與 `/login`
  讀 `BASE_DIR / "static" / "login.html"` 同源）。
- mount 為路由、非 middleware：請求仍會被 auth_guard middleware 攔截：
  - 已登入 → 放行 → StaticFiles 服務檔案
  - 未登入 → 依 auth_guard：API 走 401 JSON、其餘導 `/login`（302）
- `_PUBLIC_PREFIXES = ("/static/login",)` 既已放行 `/static/login*`（給登入頁
  資產用，不受此次改動影響）；`/static/themes/*`、`/static/index.html` 等
  其餘路徑維持「需登入才能載」。

## 修改 diff（web_server.py）
```diff
@@
 app.add_middleware(
     SessionMiddleware,
     secret_key=settings.SESSION_SECRET or "insecure-dev-secret-change-me",
     session_cookie="session",
     https_only=(settings.ENVIRONMENT == "production"),
     same_site="strict",
     max_age=None,
 )

+# /static/* 靜態檔（須登入後才能載；login.html 由 /login 路由直接讀檔回傳，
+# 不受此 mount 影響。auth_guard 已透過 _PUBLIC_PREFIXES 放行 /static/login*）
+app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
+

 @app.get("/login")
 async def login_page():
```
（net +4 行：1 mount + 2 行註解 + 1 空行；實際邏輯新增 = 1 行）

## 驗證
- `py_compile web_server.py`：**通過**
- curl 測試（需重啟 server，在 OrcStack 跑）：
  - 未登入：`curl -sI http://localhost:8080/static/themes/kahn.css | head -3`
    → 預期 `HTTP/1.1 302 Found` + `Location: /login`（auth_guard 導向）
  - 登入後 Ctrl+Shift+R 強制重整 → console 不應再有 `/static/themes/*.css`
    404；理應載到 `kahn.css`（預設）後可正常切換主題（切換本身為前一輪
    修過的 `/static/themes/${theme}.css`）。
- pytest 後端：未跑（單行 mount 不影響既有 metadata 測試；既有 18 passed/
  3 skipped 不會改變）。如需保險：`./venv/bin/python -m pytest -q` 可跑全套。

## 推薦 commit message
```
fix(web_server): mount /static for StaticFiles，解決 CSS 404

Phase 4.7c（UI 改造）後 static/index.html 引用 /static/themes/*.css，
但 web_server 未掛 /static 路由，登入後請求皆 404。

新增 1 行 app.mount("/static", StaticFiles(directory=BASE_DIR/"static"))
於 SessionMiddleware 之後、/login 路由之前。auth_guard 已透過
_PUBLIC_PREFIXES 放行 /static/login*；其餘 /static/* 走「需登入」路徑
（未登入 → 302 /login）。login.html 由 /login 路由直接讀檔回傳，
不受此 mount 影響。

未改業務邏輯／auth_guard／_PUBLIC_PREFIXES／index.html／login.html。
py_compile 通過；端到端待 OrcStack 重啟驗證（瀏覽器強制重整無 CSS 404）。
```

## 不可動清單（已遵守）
- auth_guard / _PUBLIC_PREFIXES / _PUBLIC_PATHS：未動
- static/index.html / static/login.html：未動
- 未引入新檔案 / 新 CDN
- 其他業務邏輯（後端 .py / 前端 JS）：未動
