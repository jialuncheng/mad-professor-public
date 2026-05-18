"""產生登入密碼的 bcrypt hash。

用法：
    python scripts/generate_password_hash.py

互動式輸入密碼兩次，輸出 bcrypt hash，貼到 .env 的 AUTH_PASSWORD_HASH。
"""
import getpass
import sys

try:
    import bcrypt
except ImportError:
    print("缺少 bcrypt，請先安裝：pip install bcrypt")
    sys.exit(1)


def main():
    pw1 = getpass.getpass("輸入密碼：")
    if not pw1:
        print("密碼不可為空")
        sys.exit(1)
    pw2 = getpass.getpass("確認密碼：")
    if pw1 != pw2:
        print("兩次輸入不一致")
        sys.exit(1)

    hashed = bcrypt.hashpw(pw1.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    print()
    print("請把以下 hash 貼到 .env 的 AUTH_PASSWORD_HASH：")
    print(hashed)


if __name__ == "__main__":
    main()
