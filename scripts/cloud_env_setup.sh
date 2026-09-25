#!/usr/bin/env bash
# Cloud environment SETUP SCRIPT: paste this file's body into the environment's
# "Setup script" field at claude.ai/code. It is kept here only as the record.
#
# AICODE-NOTE: cloud sessions ignore enabledPlugins/extraKnownMarketplaces from
# .claude/settings.json and never see ~/.claude on Nikita's machine
# (docs: cloud-environments#what-carries-over-from-your-setup). So user-level setup is
# recreated here, before Claude Code launches: the balka plugin, and a cloud copy of the
# attribution rule from Nikita's local ~/.claude/hooks/git-commit-style.py (the tkb-only
# rules there do not apply in the cloud). The environment cache keeps all of it
# (~7 days, or until this script or the network list changes).
# Never fails: a failed setup script blocks the session; check with `claude plugin list`.
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
command -v jq >/dev/null || apt-get install -y -qq jq || echo "setup: jq install failed"
claude plugin marketplace add meteoFurletov/skills \
  && claude plugin install balka@meteof-skills \
  || echo "setup: balka install failed"

# --- no Claude attribution in commits or PR bodies ---
mkdir -p "$HOME/.claude/hooks"
cat > "$HOME/.claude/hooks/no-attribution.py" <<'HOOK'
#!/usr/bin/env python3
"""PreToolUse/Bash: block Claude attribution in `git commit` and `gh pr create/edit`."""
import json, re, sys

PATTERNS = [
    (r"Co-Authored-By:\s*Claude", "Co-Authored-By: Claude"),
    (r"Generated with \[?Claude", "Generated with [Claude Code]"),
    (r"Claude-Session:", "Claude-Session:"),
]

try:
    command = (json.load(sys.stdin).get("tool_input") or {}).get("command") or ""
    if re.search(r"\bgit\b(?:\s+\S+)*?\s+commit\b|\bgh\s+pr\s+(?:create|edit)\b", command):
        for pattern, label in PATTERNS:
            if re.search(pattern, command, re.I):
                json.dump({"hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason":
                        f"Blocked: the command contains `{label}`.\n\n"
                        "Claude attribution is not used in any of Nikita's repos, in "
                        "commit messages or PR bodies. Remove that line and re-run; the "
                        "rest of the message can stay as it is."}}, sys.stdout)
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
entries = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
if not any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
    entries.append({"matcher": "Bash",
                    "hooks": [{"type": "command", "command": command, "timeout": 10}]})
json.dump(settings, open(path, "w"), indent=2)
MERGE
exit 0
