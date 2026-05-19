#!/bin/bash
# Mad Professor 安裝腳本
# 可重複執行（idempotent）：已建立的 venv / .env 不會被破壞或覆蓋。
set -e

INFO()  { echo "[INFO]  $*"; }
WARN()  { echo "[WARN]  $*"; }
ERROR() { echo "[ERROR] $*" >&2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INFO "=== Mad Professor 安裝開始 ==="

# ── 1. 檢查 Python 版本 >= 3.10 ──
INFO "檢查 Python 版本..."
if ! command -v python3 >/dev/null 2>&1; then
  ERROR "找不到 python3，請先安裝 Python 3.10 或以上版本。"
  exit 1
fi
PY_VER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
PY_OK="$(python3 -c 'import sys; print(1 if sys.version_info[:2] >= (3, 10) else 0)')"
if [ "$PY_OK" != "1" ]; then
  ERROR "目前 Python 版本為 $PY_VER，需 3.10 或以上。請升級後再執行。"
  exit 1
fi
INFO "Python 版本 $PY_VER，符合需求（>= 3.10）。"

# ── 2. 建立 venv（已存在則沿用）──
VENV_DIR="venv"
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
  INFO "偵測到既有虛擬環境 $VENV_DIR/，沿用不重建。"
else
  INFO "建立虛擬環境 $VENV_DIR/ ..."
  python3 -m venv "$VENV_DIR"
fi

# ── 3. 啟用 venv 並安裝依賴 ──
INFO "啟用虛擬環境..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if [ ! -f requirements.txt ]; then
  ERROR "找不到 requirements.txt，無法安裝依賴。"
  exit 1
fi

INFO "升級 pip..."
python -m pip install --upgrade pip >/dev/null

INFO "安裝 requirements.txt 套件（已安裝者會自動略過）..."
pip install -r requirements.txt
INFO "套件安裝完成。"

# ── 4. 確認 .env（不存在才從範例複製，存在則保留）──
if [ -f .env ]; then
  INFO "偵測到既有 .env，保留不覆蓋。"
elif [ -f .env.example ]; then
  cp .env.example .env
  INFO "已從 .env.example 複製產生 .env（尚未填值）。"
else
  WARN "找不到 .env 與 .env.example，請手動建立 .env。"
fi

# ── 5. 建立 data/ 目錄並初始化 DB schema ──
INFO "建立 data/ 目錄（SQLite DB 位置）..."
mkdir -p data

INFO "初始化資料庫 schema（idempotent，不存在才建表）..."
if python -c "from db import init_db; init_db()"; then
  INFO "DB schema 初始化完成（data/mad-professor.db）。"
else
  WARN "DB init 失敗，請啟動前手動執行：python -c \"from db import init_db; init_db()\""
fi

# ── 6 & 7. 提示後續步驟 ──
INFO "=== 安裝完成 ==="
cat <<'EOF'

[INFO]  後續手動步驟：

  1. 編輯 .env，至少填入下列必填項：
       GEMINI_API_KEY        Gemini API 金鑰（必填）
       MINERU_API_URL        MinerU 解析服務端點
       AUTH_USERNAME         登入帳號（預設 admin）
       AUTH_PASSWORD_HASH    登入密碼 bcrypt hash
       SESSION_SECRET        Session cookie 簽章密鑰

  2. 產生登入密碼 hash（互動式輸入兩次）：
       source venv/bin/activate
       python scripts/generate_password_hash.py
     將輸出的 hash 貼到 .env 的 AUTH_PASSWORD_HASH

  3. 產生 SESSION_SECRET 並貼到 .env：
       python -c "import secrets; print(secrets.token_urlsafe(48))"

  4. 建立 admin user（讀取 .env 的 AUTH_USERNAME / AUTH_PASSWORD_HASH）：
       source venv/bin/activate
       python scripts/migrate_to_db.py
     （首次安裝可先跑 python scripts/migrate_to_db.py --dry-run 預覽）

  5. 啟動服務：
       source venv/bin/activate
       python web_server.py

  啟動後開啟瀏覽器： http://localhost:8080

EOF
