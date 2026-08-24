# Dual-host cowork roadmap

Status: ACTIVE
Date: 2026-08-25
Branch: `sprint/dual-host`

## Goal

Ship one ai-native-cowork product from one repository for Claude Code and Codex. Both hosts expose the same skills, triggers, phases, gates, durable state, outputs, and completion rules. Only execution mechanisms differ.

## Product success

- Claude Code keeps its current capabilities.
- Codex installs the same six skills from the same source repository.
- `pdca-wf` and `cowork-sprint` implement the same method on both hosts.
- Both hosts read and write one minimal `status.json` contract.
- Sprint work uses rolling-wave planning, separate Plan and Design reviews, dynamic role deltas, targeted sprint tests, and mandatory sprint commits.
- A 0–10 risk score adds verification without removing core gates.
- Transcript consumers accept Claude and Codex sessions through one normalized boundary.
- Automated parity checks reject accidental feature drift between hosts.

## Out of scope

- Publishing, pushing, or creating a release tag.
- Replacing provider-native agent runtimes.
- Giving Codex unsupported hooks or plugin-agent registration.
- Rewriting proven transcript parsing from memory.
- Updating the stale vendored marketplace copy as a second source of truth.

## Risk score

| Dimension | Score | Reason |
|---|---:|---|
| Impact | 2 | Six skills, manifests, agents, scripts, and installation surfaces |
| Recovery | 1 | Git rollback is available, but two hosts may cache different versions |
| Security or external effects | 0 | No production deployment or credential mutation |
| Contract change | 2 | Public skill behavior, manifests, state schema, and transcript inputs |
| Verification difficulty | 2 | Host parity and installation behavior require separate checks |
| **Total** | **7/10** | Heavy verification applies at the roadmap boundary |

External actions remain approval-gated regardless of score.

## Coarse roadmap

| Sprint | Deliverable | Dependencies | Done summary |
|---|---|---|---|
| S1 | Shared method contract, minimal state schema, risk score, host seams | none | Shared contract and deterministic state validation pass |
| S2 | Dual-host `pdca-wf` | S1 | Same phases, gates, WorkList, and outputs on both hosts |
| S3 | Dual-host `cowork-sprint` | S1, S2 | Rolling roadmap, role deltas, risk gates, targeted tests, commits, resume |
| S4 | Remaining skills, agents, manifests, transcript boundary, packaging | S1–S3 | Six-skill parity, both manifests valid, tests and install smoke pass; Codex goal-control messages excluded from user-message views |

Only the active sprint receives detailed Plan and Design. Later sprints remain coarse until their dependencies settle.

### S4 transcript acceptance addition

For Codex transcripts only, a message whose payload is a `<codex_internal_context source="goal">...</codex_internal_context>` control envelope remains available as raw execution history but is not user dialogue. Exclude it from:

- last-five user messages;
- cowork-insights user-prompt summaries;
- cowork-commit directive-log user-turn lists.

Do not apply this source-specific filter to Claude transcripts. Tests must place several goal-continuation envelopes between real user messages and prove the last-five result contains only real user-authored turns in chronological order.

## Shared lifecycle

```text
Roadmap:
  Goal -> one PRD-lite -> coarse sprint map -> roadmap review -> approval

Sprint:
  Research -> Sprint Brief -> Plan -> Plan review
  -> Design -> Design review -> dynamic role execution
  -> targeted test -> WorkList gap check -> sprint commit -> state update

Roadmap close:
  full regression -> final intent audit -> release-readiness check
  -> doc-sync -> local merge -> retrospective
```

## Host execution seam

| Shared concept | Claude Code | Codex |
|---|---|---|
| Durable state | `status.json` | `status.json` |
| Long-running control | session + status | Goal + status |
| Short plan | TodoWrite | `update_plan` |
| Parallel work | Agent / Workflow | collaboration agents |
| Single feature | Workflow-backed `pdca-wf` | root/worker-backed `pdca-wf` |
| Rules | `CLAUDE.md` | `AGENTS.md` |
| Transcript | Claude JSONL | Codex rollout JSONL |

## S1 Sprint Brief

### Problem

Method rules and Claude execution details currently live in the same skill files. State is manually edited and has drifted in real runs. Risk-dependent verification is described with ambiguous labels.

### Success

- One shared contract defines phases, core gates, risk thresholds, outputs, and state.
- Host-specific references define execution without duplicating the method.
- State transitions are validated by a deterministic script.
- Existing uncommitted TRIM work is retained but reconciled with the simplified default flow.

### Out of scope

- Implementing the complete Codex `pdca-wf` or `cowork-sprint` entrypoint.
- Transcript normalization and manifest installation.

### Dependencies

- Existing 1.17.0 Claude implementation.
- Local Codex plugin and transcript-tool references.

### Pre-mortem

- Shared files become an abstract framework no host consumes.
- State schema drops information needed for resume.
- Risk scoring removes core gates at low scores.
- Existing TRIM edits are lost or turned into a mandatory extra agent pass.

## S1 Plan

1. Define the shared phase, gate, risk, dynamic-role, test, commit, and close contracts.
2. Define a minimal status schema that stores resume state, not reports.
3. Add a deterministic validator and transition helper with tests.
4. Add Claude Code and Codex runtime references.
5. Update skill entrypoints only enough to route to the shared contract and preserve current behavior, except for one intentional divergence: retain TRIM as a concise diff question inside QA instead of a mandatory separate agent pass.
6. Run targeted schema, transition, lifecycle-fixture, host-seam, risk, and contract parity checks.
7. Commit S1 independently.

### Plan evidence map

| WorkList | Artifact | Owner step | Deterministic evidence |
|---|---|---|---|
| S1-01 | shared method + two host references | 1, 4, 5 | contract test rejects host tool names in shared text and phase/gate redefinition in host text |
| S1-02 | status schema | 2 | valid CC/Codex lifecycle fixtures pass; unknown/report fields and bad references fail |
| S1-03 | state helper | 3 | unit tests cover start, phase, pause/resume, decision, commit, complete, fail, archive, stale revision |
| S1-04 | risk contract + calculator | 1, 3 | score fixtures prove 0–3/4–6/7–10 and core/safety non-waiver |
| S1-05 | dynamic-role contract | 1 | contract test finds the four required role-delta parts once in shared text |
| S1-06 | reconciled TRIM contract | 5 | focused assertion rejects a mandatory separate trim-agent gate and retains the unrequested-diff question |

Representative lifecycle fixtures model S2 single-feature completion and S3 rolling-sprint pause/resume without implementing either host runtime.

## S1 Plan review contract

- Completeness: every agreed invariant has an owner and output.
- Scope: S1 does not implement host orchestration.
- Sequencing: S2 and S3 can consume S1 without revising its schema.
- Sizing: one cohesive shared-contract deliverable.

## S1 Design

### Files

```text
skills/shared/
  references/cowork-method.md
  references/runtime-claude-code.md
  references/runtime-codex.md

skills/cowork-sprint/
  references/status.schema.json
  scripts/state/state.py
  scripts/state/test_state.py
```

The existing skill folders remain the public entrypoints. Shared references own common semantics. Host references own only tool and path mechanics.

### Minimal status

```text
schemaVersion, revision, runId, goal, roadmapFile
executionMode
git { baseBranch, worktree, sprintBranch, lastCommit }
sprints[] { id, deps, planFile, risk, status, phase, commit, resultFile? }
pause, openDecisions[], updatedAt
```

Reports own full QA tables, review findings, research notes, and resolved decisions.

### Risk score

Five dimensions score 0–2: impact, recovery, security/external, contract, verification.

```text
0–3  core gates only
4–6  deeper independent review and adjacent regression
7–10 specialist review plus applicable parity or mutation and final intent/rollback checks
```

Core gates and external-action approvals never depend on score.

### Dynamic roles

Every delegated task uses:

```text
base role + sprint role delta + evidence contract + explicit exclusions
```

One-off deltas stay in prompts. Repeated, proven deltas become retrospective promotion candidates.

### State semantics

Canonical phases are `pending`, `research`, `brief`, `plan`, `plan-review`, `design`, `design-review`, `do`, `test`, `gap-check`, `commit`, and `done`. Sprint statuses are `pending`, `in-progress`, `blocked`, `failed`, `completed`, and `archived`.

An active sprint has status `in-progress` or `blocked`. In sequential mode, at most one sprint may be active. A sprint can start only when every dependency is completed. Normal phase transitions move one step forward. `blocked` preserves the current phase. `failed` and `archived` are terminal. Completion requires phase `commit`, a non-empty commit identifier, and every dependency completed.

| Command | Allowed source | Result |
|---|---|---|
| `start-sprint` | `pending/pending` with completed deps | `in-progress/research` |
| `set-phase` | `in-progress/<current>` | `in-progress/<next>` |
| `block-sprint` | `in-progress/<any nonterminal phase>` | `blocked/<same phase>` |
| `resume` | matching global pause and `blocked/<same phase>` or `in-progress/<same phase>` | clears pause; blocked sprint becomes `in-progress/<same phase>` |
| `fail-sprint` | `in-progress` or `blocked`, any nonterminal phase | `failed/<same phase>` |
| `set-commit` | `in-progress/commit` | records commit; state remains `in-progress/commit` |
| `complete-sprint` | `in-progress/commit` with commit and completed deps | `completed/done` |
| `archive-sprint` | `completed/done` or `failed/<same phase>` | `archived/<same phase>` |

`completed` and `archived` are terminal for execution. A completed sprint may only be archived. A failed sprint may only be archived; retry creates a new sprint or follows a future explicit retry contract rather than silently reviving failed state.

`pause` is either null or `{code, sprintId, phase, detail, blockedBy, createdAt}`. Codes are the shared auto-pause set. Resume clears pause only after the caller re-evaluates and explicitly supplies the same code. `openDecisions[]` contains `{id, sprintId, question, chosenDefault, reason, status}` where status is `open`; resolved decisions move to reports instead of remaining active state.

### State transitions

The script provides `init`, `start-sprint`, `set-phase`, `set-commit`, `complete-sprint`, `block-sprint`, `fail-sprint`, `archive-sprint`, `pause`, `resume`, `open-decision`, `resolve-decision`, and `validate`.

Every mutation requires `--expected-revision`. The script reads the current document, compares revisions, validates the transition, increments the revision, writes a sibling temporary file, and atomically renames it. Failed validation leaves the prior file unchanged.

It rejects unknown fields and phases, duplicate sprint IDs, missing dependency references, dependency cycles, illegal phase/status combinations, dependency violations, completion without a commit, stale revisions, non-ISO timestamps, absolute plan/report paths, and multiple active sprints in sequential mode.

The atomic-write and declarative-transition baseline is adapted from `/Users/taehyoungkim/Documents/DEV/ww-w-ai/bkit/bkit-claude-code` commit `eec224f3911ad1484295b7837ca88fd013eb540d` (`v2.1.38-2-geec224f`), files `lib/infra/sprint/sprint-state-store.adapter.js` and `lib/pdca/state-transitions.js` (Apache-2.0). The cowork schema and transitions are intentionally smaller; provenance is recorded in `THIRD-PARTY-NOTICES.md`.

### Schema seam

The schema uses JSON Schema draft 2020-12 and recursively closes authored objects with `additionalProperties: false`. Required fields are explicit. Nullable fields use a type union with `null`. IDs are non-empty stable strings. Commit identifiers accept Git hex object IDs of 7–64 characters. Plan/report paths are repository-relative. Semantic checks that JSON Schema cannot express, including dependency cycles and phase transitions, belong to the state helper.

### Risk seam

Each sprint stores `risk: {impact, recovery, securityExternal, contract, verification, total}`. Every dimension is an integer from 0 through 2. `total` is their sum from 0 through 10. The helper validates the sum and derives the level at runtime; the level is not persisted. Risk affects added gates only. Core gates and approval for external or irreversible actions remain mandatory at every score.

## S1 Design review contract

- Schema supports CC-to-Codex resume without host-only fields.
- Transition commands cover every lifecycle mutation needed by the skills.
- Shared references contain no host tool names.
- Host references do not redefine shared phases or gates.
- Tests exercise invalid transitions, not wording.

## S1 WorkList

| ID | Work | Acceptance evidence | Priority |
|---|---|---|---|
| S1-01 | Shared method contract | Both host references point to one phase/gate definition | P0 |
| S1-02 | Minimal state schema | CC single-feature and Codex rolling-resume fixtures pass; unknown/report fields, bad refs, cycles, and invalid paths fail | P0 |
| S1-03 | State transition helper | Transition tests cover start, phase, pause/resume, decision, commit, complete, fail, archive, stale revision, and atomic preservation | P0 |
| S1-04 | Risk score contract | Threshold and non-waivable core/safety tests pass | P0 |
| S1-05 | Dynamic role contract | Base+delta+evidence+exclusions documented once and consumed by both host references | P1 |
| S1-06 | Existing TRIM preservation | Original intent retained as a concise QA diff check; default flow has no mandatory separate trim agent | P1 |
| S1-07 | Host seam parity | Shared text contains no host tools; host references cannot redefine phases/gates | P0 |
| S1-08 | Entrypoint consumption | Current public skills link to shared method/runtime references without implementing S2/S3 orchestration | P1 |
