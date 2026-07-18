#!/usr/bin/env bash
# Smoke test for the vendored brainstorm visual-companion server (BRAINSTORM-1 C2).
# Starts the server against an isolated temp project-dir, curls the served page
# (expect HTTP 200), then stops it. Zero external deps beyond Node (server) + curl.
# Exit 0 = healthy, non-zero = failure. Does NOT touch the real .claude-logs/baton/.
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PDIR="$(mktemp -d)"
cleanup() { rm -rf "$PDIR" 2>/dev/null; }
trap cleanup EXIT

OUT="$("$SCRIPT_DIR/start-server.sh" --project-dir "$PDIR" --host 127.0.0.1 --background 2>&1)"
URL="$(printf '%s' "$OUT" | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
STATE_DIR="$(printf '%s' "$OUT" | sed -n 's/.*"state_dir"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"

if [[ -z "$URL" ]]; then
  echo "SMOKE FAIL: no url in start-server output:"
  echo "$OUT"
  exit 1
fi

CODE="$(curl -sS -o /dev/null -w '%{http_code}' "$URL" 2>/dev/null)"

# Stop the server (session dir = parent of state_dir)
if [[ -n "$STATE_DIR" ]]; then
  "$SCRIPT_DIR/stop-server.sh" "$(dirname "$STATE_DIR")" >/dev/null 2>&1
fi

if [[ "$CODE" == "200" ]]; then
  echo "SMOKE OK: server served $URL (HTTP $CODE)"
  exit 0
fi

echo "SMOKE FAIL: HTTP $CODE from $URL"
exit 1
