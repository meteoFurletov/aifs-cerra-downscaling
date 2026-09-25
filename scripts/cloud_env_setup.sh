#!/usr/bin/env bash
# Cloud environment SETUP SCRIPT: paste this file's body into the environment's
# "Setup script" field at claude.ai/code. It is kept here only as the record.
#
# AICODE-NOTE: cloud sessions ignore enabledPlugins/extraKnownMarketplaces from
# .claude/settings.json (docs: cloud-environments#what-carries-over-from-your-setup),
# so plugins are installed at user scope here, before Claude Code launches. The
# environment cache keeps them (~7 days, or until this script or the network list changes).
# Never fails: a failed setup script blocks the session; check with `claude plugin list`.
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
command -v jq >/dev/null || apt-get install -y -qq jq || echo "setup: jq install failed"
claude plugin marketplace add meteoFurletov/skills \
  && claude plugin install balka@meteof-skills \
  || echo "setup: balka install failed"
exit 0
