#!/usr/bin/env bash
# SessionStart hook: in Claude Code cloud sessions, install deps and pull the data.
# Local sessions (CLAUDE_CODE_REMOTE unset) are left alone.
# Never fails the session: problems are reported so the agent sees them in context.
set -o pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "$(dirname "$0")/.."

uv sync --quiet 2>&1 | tail -5 || echo "cloud_session_start: uv sync failed"
if ! ./scripts/fetch_data.sh 2>&1 | tail -5; then
  echo "cloud_session_start: data fetch failed. Check that huggingface.co, *.huggingface.co"
  echo "and *.hf.co are on the environment's network allowlist and the HF credential is set."
fi
exit 0
