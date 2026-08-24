# Claude Code runtime for cowork-sprint

<!-- cluster-contract {"admission":"first-unfinished","barrier":"earlier-committed","failure":"stop","integration":"stored-order","stateOwner":"leader"} -->

Read [`../../shared/references/cowork-method.md`](../../shared/references/cowork-method.md), then the preserved Claude procedure in [`../SKILL.md`](../SKILL.md).

- The main session is leader; TodoWrite mirrors transient phases.
- Use flat Agent calls or one-level Workflow fan-out. Never nest leaders or run `pdca-wf` inside a subagent.
- Run `../scripts/schedule.py` during planning. Dispatch only the first unfinished cluster.
- Concurrent members receive disjoint ownership allowlists. Integrate them in stored `integrationOrder`.
- Use the state helper for every durable transition. Workers never edit state or commit.
- The leader owns reviews, tests, per-sprint commits, checkpoints, conflicts, and approvals.

Run adjacent regression after an integrated cluster. A blocked or failed member stops cluster advance.
