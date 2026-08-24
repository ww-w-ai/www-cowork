> Status: LIVING — as-built. Live authority is the linked skill, shared method, runtimes, schema, and scripts.
> Last updated: 2026-08-25

# cowork-sprint — as-built

Multi-feature delivery uses one host-neutral contract with native execution on Claude Code and Codex.

## Authority map

- `../../skills/shared/references/cowork-method.md`: roadmap, sprint gates, risk, clusters, convergence, safety, outputs, and Done.
- `../../skills/cowork-sprint/SKILL.md`: thin capability router and public inputs/outputs.
- `../../skills/cowork-sprint/references/runtime-claude-code.md`: Claude Code mechanisms.
- `../../skills/cowork-sprint/references/runtime-codex.md`: Codex mechanisms.
- `../../skills/cowork-sprint/references/status.schema.json`: minimal durable state.
- `../../skills/cowork-sprint/scripts/state/state.py`: validated optimistic/atomic transitions.
- `../../skills/cowork-sprint/scripts/schedule.py`: dependency and ownership cluster scheduler.

## Invariants

- Both hosts execute the same ordered lifecycle table and Done predicate.
- Plan and Design reviews are separate, independent barriers.
- Only the first unfinished cluster may run. Concurrent members have disjoint ownership and stable integration order.
- Every sprint has targeted tests, gap evidence, intent PASS, its own commit, and a post-commit checkpoint.
- State contains resume facts only. QA tables, resolved decisions, gap detail, and agent evolution belong in Plan or Report artifacts.
- External or irreversible actions always require explicit user approval.
