#!/usr/bin/env bash
# SessionStart hook: in Claude Code cloud sessions, install deps, pull the data and load
# the Infisical secrets. Local sessions (CLAUDE_CODE_REMOTE unset) are left alone; there,
# secrets come from `infisical run --env=dev -- <command>`.
# Never fails the session: problems are reported so the agent sees them in context.
set -o pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "$(dirname "$0")/.."

uv sync --quiet 2>&1 | tail -5 || echo "cloud_session_start: uv sync failed"
if ! ./scripts/fetch_data.sh 2>&1 | tail -5; then
  echo "cloud_session_start: data fetch failed. Check that huggingface.co, *.huggingface.co"
  echo "and *.hf.co are on the environment's network allowlist and the HF credential is set."
fi

# The environment holds only Infisical's machine identity; the WN3 key and the rest reach
# every later Bash command through $CLAUDE_ENV_FILE. Values never go to this hook's output.
if [ -z "${INFISICAL_CLIENT_ID:-}" ] || [ -z "${INFISICAL_CLIENT_SECRET:-}" ]; then
  echo "cloud_session_start: no Infisical machine identity in the environment; secrets not loaded."
elif [ -z "${CLAUDE_ENV_FILE:-}" ]; then
  echo "cloud_session_start: CLAUDE_ENV_FILE is not set; secrets not loaded."
elif exports=$(uv run --quiet --no-project --with infisicalsdk==1.0.16 python scripts/cloud_secrets.py); then
  printf '%s\n' "$exports" >> "$CLAUDE_ENV_FILE"
else
  echo "cloud_session_start: Infisical secrets not loaded. Check INFISICAL_CLIENT_ID/SECRET"
  echo "and that app.infisical.com is on the environment's network allowlist."
fi
exit 0
