"""Print this repo's Infisical secrets as `export` lines, for Claude Code cloud sessions.

The cloud environment holds only Infisical's machine identity (INFISICAL_CLIENT_ID,
INFISICAL_CLIENT_SECRET). scripts/cloud_session_start.sh runs this and appends the
output to $CLAUDE_ENV_FILE, so every later Bash command sees WN3_GCP_KEY_JSON and the
rest, as `infisical run --env=dev -- <command>` gives them locally. The project comes
from .infisical.json unless INFISICAL_PROJECT_ID overrides it.

    uv run --no-project --with infisicalsdk==1.0.16 python scripts/cloud_secrets.py

Values go to stdout only; stderr carries the secret names, never a value.
"""

import json
import os
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def export_lines(values):
    """`export NAME='value'` per secret, quoted so multi-line JSON survives `source`."""
    return "".join(f"export {k}={shlex.quote(v)}\n" for k, v in sorted(values.items()))


def fetch():
    from infisical_sdk import InfisicalSDKClient  # brought by `uv run --with`

    project_id = (os.environ.get("INFISICAL_PROJECT_ID")
                  or json.loads((ROOT / ".infisical.json").read_text())["workspaceId"])
    client = InfisicalSDKClient(host=os.environ.get("INFISICAL_SITE_URL", "https://app.infisical.com"))
    client.auth.universal_auth.login(client_id=os.environ["INFISICAL_CLIENT_ID"],
                                     client_secret=os.environ["INFISICAL_CLIENT_SECRET"])
    resp = client.secrets.list_secrets(
        project_id=project_id,
        environment_slug=os.environ.get("INFISICAL_ENVIRONMENT", "dev"),
        secret_path=os.environ.get("INFISICAL_SECRET_PATH", "/"),
        expand_secret_references=True,
    )
    return {s.secretKey: s.secretValue for s in getattr(resp, "secrets", resp)}


def main():
    values = fetch()
    if not values:
        sys.exit("cloud_secrets: Infisical returned no secrets. "
                 "Is the machine identity a member of the project, with read access to dev?")
    # AICODE-NOTE: a name that is not a shell identifier would break `source` of the env file.
    skipped = sorted(k for k in values if not k.isidentifier())
    values = {k: v for k, v in values.items() if k.isidentifier()}
    sys.stdout.write(export_lines(values))
    print(f"cloud_secrets: loaded {', '.join(sorted(values))}"
          + (f"; skipped {', '.join(skipped)} (not a shell name)" if skipped else ""),
          file=sys.stderr)


if __name__ == "__main__":
    main()
