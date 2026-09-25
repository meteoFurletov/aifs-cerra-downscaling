#!/usr/bin/env bash
# Cloud environment SETUP SCRIPT: paste this file's body into the environment's
# "Setup script" field at claude.ai/code. It is kept here only as the record.
#
# AICODE-NOTE: cloud sessions don't install plugins from enabledPlugins/extraKnownMarketplaces
# in .claude/settings.json and never see ~/.claude on Nikita's machine
# (docs: cloud-environments#what-carries-over-from-your-setup). So user-level setup is
# recreated here, before Claude Code launches: the balka plugin, and a cloud copy of the
# attribution rule from Nikita's local ~/.claude/hooks/git-commit-style.py (the tkb-only
# rules there do not apply in the cloud). The environment cache keeps all of it
# (~7 days, or until this script or the network list changes).
# Once installed here, `claude plugin list` also shows balka at project scope from the
# repo's enabledPlugins: same install, listed twice, harmless.
# Never fails: a failed setup script blocks the session; check with `claude plugin list`.
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
command -v jq >/dev/null || apt-get install -y -qq jq || echo "setup: jq install failed"
claude plugin marketplace add meteoFurletov/skills \
  && claude plugin install balka@meteof-skills \
  || echo "setup: balka install failed"

# --- no Claude attribution in commits, PR titles or PR bodies ---
mkdir -p "$HOME/.claude/hooks"
cat > "$HOME/.claude/hooks/no-attribution.py" <<'HOOK'
#!/usr/bin/env python3
"""PreToolUse: block Claude attribution in `git commit`, `gh pr create/edit`, and the
GitHub tools' PR title/body (mcp__github__create_pull_request / update_pull_request)."""
import json, re, sys

PATTERNS = [
    (r"Co-Authored-By:\s*Claude", "Co-Authored-By: Claude"),
    (r"Generated with \[?Claude", "Generated with [Claude Code]"),
    (r"Claude-Session:", "Claude-Session:"),
]

try:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    if payload.get("tool_name", "").startswith("mcp__github__"):
        text = "\n".join(str(tool_input.get(k) or "") for k in ("title", "body"))
    else:
        text = tool_input.get("command") or ""
        if not re.search(r"\bgit\b(?:\s+\S+)*?\s+commit\b|\bgh\s+pr\s+(?:create|edit)\b", text):
            text = ""
    for pattern, label in PATTERNS:
        if re.search(pattern, text, re.I):
            json.dump({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason":
                    f"Blocked: the text contains `{label}`.\n\n"
                    "Claude attribution is not used in any of Nikita's repos, in "
                    "commit messages or PR titles and bodies. Remove that line and "
                    "re-run; the rest can stay as it is."}}, sys.stdout)
            break
except Exception:
    pass  # a broken guard must never block real work
HOOK
python3 - <<'MERGE' || echo "setup: hook registration failed"
import json, os
path = os.path.expanduser("~/.claude/settings.json")
try:
    settings = json.load(open(path))
except (OSError, ValueError):
    settings = {}
command = 'python3 "$HOME/.claude/hooks/no-attribution.py"'
matcher = "Bash|mcp__github__create_pull_request|mcp__github__update_pull_request"
hooks = settings.setdefault("hooks", {})
# replace, not skip: an entry from an older version of this script has a narrower matcher
entries = [e for e in hooks.get("PreToolUse", [])
           if not any(h.get("command") == command for h in e.get("hooks", []))]
entries.append({"matcher": matcher,
                "hooks": [{"type": "command", "command": command, "timeout": 10}]})
hooks["PreToolUse"] = entries
json.dump(settings, open(path, "w"), indent=2)
MERGE
exit 0
