#!/usr/bin/env bash
# fetch_frontend_vendor.sh — 下載並校驗自託管前端資產（KaTeX + DOMPurify）
# RAG-12 C1（katex）+ SEC-XSS C1（dompurify）。離線/GFW 部署可重現；資產入版控、刷新時重跑本腳本。
set -euo pipefail

KATEX_VERSION="0.16.47"
DOMPURIFY_VERSION="3.1.6"
DEST="static/vendor/katex"
DEST_DP="static/vendor/dompurify"

cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "→ 下載 katex@${KATEX_VERSION} (npm pack)..."
( cd "$TMP" && npm pack "katex@${KATEX_VERSION}" >/dev/null && tar -xzf katex-*.tgz )

mkdir -p "$DEST/fonts"
cp "$TMP/package/dist/katex.min.css" "$DEST/"
cp "$TMP/package/dist/katex.min.js"  "$DEST/"
# 僅取 woff2（現代瀏覽器全支援、瘦身；CSS @font-face 以 woff2 為首選 src）
cp "$TMP/package/dist/fonts/"*.woff2 "$DEST/fonts/"

echo "→ SHA-256 校驗："
( cd "$DEST" && find . -type f \( -name '*.css' -o -name '*.js' -o -name '*.woff2' \) | sort | xargs sha256sum )
echo "✓ 完成：$DEST （katex ${KATEX_VERSION}）"

# === [SEC-XSS C1] DOMPurify 自託管（HTML 消毒引擎·markdown 輸出消毒防 stored XSS） ===
echo "→ 下載 dompurify@${DOMPURIFY_VERSION} (npm pack)..."
TMP_DP="$(mktemp -d)"
trap 'rm -rf "$TMP" "$TMP_DP"' EXIT
( cd "$TMP_DP" && npm pack "dompurify@${DOMPURIFY_VERSION}" >/dev/null && tar -xzf dompurify-*.tgz )

mkdir -p "$DEST_DP"
cp "$TMP_DP/package/dist/purify.min.js" "$DEST_DP/"

echo "→ SHA-256 校驗（dompurify·與 static/vendor/README.md 登記指紋比對）："
( cd "$DEST_DP" && sha256sum purify.min.js )
echo "✓ 完成：$DEST_DP （dompurify ${DOMPURIFY_VERSION}）"
