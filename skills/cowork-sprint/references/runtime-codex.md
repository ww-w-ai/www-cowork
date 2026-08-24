# Codex runtime for cowork-sprint

<!-- cluster-contract {"admission":"first-unfinished","barrier":"earlier-committed","failure":"stop","integration":"stored-order","stateOwner":"leader"} -->

Read [`../../shared/references/cowork-method.md`](../../shared/references/cowork-method.md) first.

- The root agent is leader. Use an explicitly requested Goal for the roadmap and `update_plan` for transient phases.
- Use explorers for discovery and workers for owned implementation. An approved Claude CLI replacement follows the same ownership allowlist and cannot edit state.
- Run `../scripts/schedule.py` during planning. Dispatch only the first unfinished cluster.
- Concurrent members use flat collaboration calls. Integrate them in stored `integrationOrder`.
- Use the state helper for every durable transition. Workers never edit state or commit.
- The root owns reviews, real tests, per-sprint commits, checkpoints, conflicts, and approvals.

Run adjacent regression after an integrated cluster. A blocked or failed member stops cluster advance. Resume the first unfinished cluster after validating state revision.
