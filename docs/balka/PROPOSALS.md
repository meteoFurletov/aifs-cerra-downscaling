# Proposals

The inbox for the reflect step. When a correction to how the loop works repeats,
record it here once, with the evidence, instead of a third time in chat.
`/balka:reflect` reads this file, the change directories and the git history,
and turns the entries into a change list routed to the plugin or kept here.

Format, one entry each:

## <date> — <one line: what should change>

Evidence: <where it happened: change, commit, a quote under fifteen words>.
Route: open | plugin | project | dropped.

## 2026-09-25 — Test's verifier attacks the code with failing tests, not only prose findings

Evidence: `docs/DATA.md` §4 lists eleven traps, each hit once in-session. `pipeline/`
fixes them inline (`RT_PRIORITY`, `zfill`, `drop_vars("valid_time")`) or guards one at
runtime (`LINE_CAP`), but the repo has no tests. `check()` in `dataset.py` checks stored
data, not the code, so a refactor of `pipeline/` can undo a fix silently. Balka's
`commands/test.md` keeps the verifier read-only and the stage file-free, so a trap it
spots becomes a finding that can recur. An independent re-implementation of the
headline numbers was weighed and rejected as too costly and prone to diverge. The owner:
"the better way is to go in GAN like way".
Route: plugin, for 0.7.0. Shape: the builder generates; a fresh-context critic outputs
only failing tests (known-answer, metamorphic, leakage), never prose. The spec referees:
an attack the spec contradicts is dropped, and one it does not settle goes to the owner
as a spec question. A round with no valid failing test ends the loop, and accepted
attacks stay as regression tests. This overturns Test's rules that the verifier runs
nothing and the stage writes no file, so it is the plugin's call.
