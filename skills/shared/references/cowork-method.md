# Shared Cowork Method

This file is the method contract shared by every supported host. Public skill entrypoints may add routing and task-specific detail. Host runtime references may map capabilities. They must not redefine this contract.

## Planning model

Use rolling-wave planning.

At roadmap start, define the goal, one product-level intent anchor, a coarse sprint map, dependencies, and approximate completion criteria. Do not fully design later sprints before earlier work has produced the facts they depend on.

Immediately before each sprint, complete this sequence:

1. Research the current code, references, and constraints.
2. Write a Sprint Brief with `Problem`, `Success`, `Out of scope`, `Dependencies`, and `Pre-mortem`.
3. Write the Plan: scope, order, deliverables, WorkList, and completion evidence.
4. Run an independent Plan review for completeness, sizing, sequencing, and the dominant risk. Resolve blockers before Design.
5. Write the Design: interfaces, data and state flow, file ownership, validation seams, and test strategy.
6. Run an independent Design review for implementability and the dominant technical risk. Resolve blockers before Do.
7. Build from the reviewed Design.
8. Run targeted tests for the changed contract and adjacent behavior.
9. Compare the WorkList with the implementation and record gaps.
10. Commit the sprint independently.
11. Persist the checkpoint.

Plan review asks whether the right work is planned. Design review asks whether that plan can be implemented and verified as described. Do not merge the two reviews.

## Core gates

Every sprint runs these gates regardless of risk score:

- Research and Sprint Brief exist.
- Plan and independent Plan review are complete.
- Design and independent Design review are complete.
- Targeted tests execute against changed behavior.
- WorkList-to-implementation gap check is complete.
- The sprint has its own commit.
- The durable checkpoint is updated after the commit.

Every roadmap ends with full regression, final intent review, documentation synchronization, a completion report, and retrospective when the run produced reusable learning or material correction.

Tests do not replace the gap check. Tests ask whether implemented behavior works. The gap check asks whether every promised item exists.

## Risk score and added gates

Score each dimension from 0 to 2 and store the five dimensions plus their sum:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Impact | one local surface | several modules | several systems or platforms |
| Recovery | immediate revert | repair or migration needed | difficult state or data recovery |
| Security/external | none | permissions or network involved | credentials, deployment, or external mutation |
| Contract | internal implementation | internal interface or schema | public API, CLI, format, or compatibility |
| Verification | existing tests suffice | new targeted tests needed | parity, mutation, or real-environment proof needed |

Apply the sum mechanically:

```text
0..3   core gates
4..6   core gates + deeper independent review + adjacent regression
7..10  prior gates + specialist review + applicable parity or mutation
        + intent and rollback checks where the failure mode requires them
```

Risk adds gates. It never waives core gates. External or irreversible actions always require explicit user approval, regardless of score.

## Dynamic role contract

Every delegated task receives exactly these four parts:

1. **Base role**: the reusable capability, such as researcher, implementer, Plan reviewer, Design reviewer, or QA reviewer.
2. **Sprint role delta**: the domain and failure mode that matter for this sprint.
3. **Evidence contract**: the sources, commands, artifacts, and structured result needed to support a verdict.
4. **Explicit exclusions**: adjacent work the role must not pull into the current sprint.

Keep a one-off delta in the dispatch prompt. When the same delta repeatedly produces useful findings, record it as a retrospective promotion candidate. Promote it to a reusable project role only after repeated evidence; do not create a permanent role for every prompt variation.

## QA diff check

After targeted tests and the WorkList gap check, inspect the sprint diff once and ask:

> What is present that no WorkList item requested?

Cut speculative generality and gold plating when a smaller implementation satisfies the reviewed Design. Keep contracts, boundaries, security controls, failure direction, and concise extensibility that the Design explicitly justifies. Record material cuts or one-line keep reasons in the sprint report. This is a concise QA question, not a separate mandatory agent or an additional review phase.

## Execution and safety

Use OODA inside Do and Check when evidence contradicts a reviewed premise. Re-plan only the affected slice and re-run only the review lenses invalidated by the change. New work outside the sprint's success criteria becomes a follow-up instead of silently widening scope.

Quality failures loop within the bounded Check/Act policy. External mutations, destructive actions, release operations, and other irreversible steps stop at an approval boundary. A high quality score cannot authorize a safety-sensitive action.

## Durable outputs

The shared state file stores resume facts, not reports. Detailed research, review findings, QA tables, and resolved decisions belong in plan or report artifacts. Source control remains authoritative for code and commits.

The common outputs are:

- roadmap and intent anchor;
- sprint Brief, Plan, Design, and WorkList;
- targeted verification and gap evidence;
- one commit per sprint;
- minimal durable checkpoint;
- final regression, intent, documentation, and completion reports.

Host-local progress displays and session controls are transient mirrors. They do not replace the shared checkpoint.
