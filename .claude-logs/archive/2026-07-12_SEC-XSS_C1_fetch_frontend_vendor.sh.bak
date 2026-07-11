#!/usr/bin/env bash
# fetch_frontend_vendor.sh — 下載並校驗自託管前端數學資產（KaTeX）
# RAG-12 C1。離線/GFW 部署可重現；資產入版控、刷新時重跑本腳本。
set -euo pipefail

KATEX_VERSION="0.16.47"
DEST="static/vendor/katex"

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
