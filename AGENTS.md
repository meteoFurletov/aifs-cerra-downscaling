# AGENTS.md

Entry point for agent sessions on this repo.

Downscaling ECMWF AIFS ENS 2 m temperature (0.25°) to the CERRA 5.5 km grid over
Leningrad Oblast, verified at held-out SYNOP stations. `README.md` has the summary,
`docs/README.md` the full state, and [docs/estate.md](docs/estate.md) the names, facts
and landing steps. **Read estate.md before drafting anything.**

## Conventions

- Python via `uv` (`uv run python ...`). Extras: `grib` for `pipeline/`, `train` for torch.
- Training sets come from `dataset.py` only; `data/` holds the five sources
  (`scripts/fetch_data.sh` pulls them).
- Anchor comments: `AICODE-NOTE:` / `AICODE-TODO:` / `AICODE-QUESTION:`; grep for
  existing `AICODE-` before scanning files.

<!-- balka:begin -->
## Balka

This repo runs the six-stage loop from the `balka` plugin. Artefacts are
plain markdown in git, one directory per change under `docs/balka/`, each on
its own branch with one main agent.

| Stage | Command | Writes |
| --- | --- | --- |
| 1 Plan | `/balka:intent` | `intent.md` |
| 2 Design | `/balka:spec` | `spec.md`, `.feature` files, red bindings |
| 3 Build | `/balka:plan`, then `/balka:build` | `plan.md`, code |
| 4 Test | `/balka:test` | nothing; a fix or a stop, then `Status: built` |
| 5 Deploy | `/balka:deploy` | the pull request, fixes from its review |
| 6 Maintain | `/balka:watch` | `bands.yaml`, the detector |
| any | `/balka:board` | nothing; every change and its next step |

Read `docs/estate.md` before drafting anything: it holds the estate's real names,
the facts the code does not say, and how changes land.

Git is the history. Change artefacts and scenarios in place; never delete,
recreate, rename or copy a file to get past a balka hook or rule. If balka
blocks work that is right, stop and tell the owner: that is a bug in balka.

A correction that
repeats goes to `docs/balka/PROPOSALS.md`, and `/balka:reflect` turns
that inbox into the next version of the loop.

Link upstream, never restate it. Write what is essential and stop. Size comes
from scope: one change is one capability, one or two `.feature` files. An
intent that needs more is split, not cut.

`.feature` files and the Then assertions in their bindings are the contract.
They change at the design transition and nowhere else; hooks block both an edit
and a commit that moves them without `spec.md`. Unit tests and binding glue are
implementation detail, yours to change freely.

The verify commands live under `verify` in `.claude/balka.json`. Build runs them
until green; nothing about them belongs in this file.
<!-- balka:end -->
