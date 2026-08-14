---
name: pdca-wf
description: USE for ANY single-feature build request — the default engine whenever the user asks to implement, build, add, or rework ONE feature/capability end-to-end, even without naming this skill. Trigger on "build/implement/add this feature", "rework X", a feature spec or design doc handed over for implementation, or explicit "pdca", "pdca workflow", "verify to 100". Runs one PDCA cycle - Plan/Design in main (thinking), Research/Do/Check as deterministic native Workflow scripts, quality loop to 100 with no mid-run pauses (only irreversible actions gate back). Also invoked execution-only by cowork-sprint per feature. DO NOT use for - multi-feature initiatives sharing one scope/timeline (use cowork-sprint), trivial single-file edits or quick fixes under ~30min (just do them), pure questions/research with no build.
---

# pdca-wf — PDCA as a native Workflow execution engine

## One-line maxim

**Judgment (Plan·Design) stays in main with thinking; structured/bulk/parallel execution (Research·Do·Check) runs as Workflow scripts that drive to 100 — only the irreversible launch is gated back to main.**

This skill's own as-built: `skills/pdca-wf/docs/01-built/pdca-wf.md` (read it if extending the skill).

## Why this shape (hard constraints — do not fight these)

- Workflow agents have **thinking OFF** → Plan/Design (judgment) MUST stay in main, never inside a Workflow.
- Workflow nesting is **1-level** → this skill never nests; cowork-sprint calls it, it does not call itself.
- Workflow runtime is a **sandbox, NOT Node**: `Date.now()`/`new Date()`/`Math.random()` throw; no `fs`. → main stamps timestamps via `date` and injects them through `args`.
- Therefore: **phase boundary = main re-entry point.** Main runs each execution phase as a Workflow, reads the structured result, then decides the next phase.

## Three actors

| Actor | Owns |
|---|---|
| **Main** | judgment: Plan·Design, phase-boundary decisions, irreversible gate, timestamp stamping |
| **Script** | wiring: which agents run in what order/parallelism, when to loop/stop (deterministic, no thinking) |
| **Agent** | work: actual read/write/search/verify |

## Agent lifecycle (discover → reuse / create → use → evolve) — main-owned

Workflow `agent()` accepts `agentType` and resolves it from the **same registry as the Agent tool** (project `.claude/agents/` → user `~/.claude/agents/` → plugins). So scripts can dispatch purpose-fit agents — but selection/creation/evolution judgment stays in main (Workflow sandbox cannot Write files).

| Step | Who | How |
|---|---|---|
| **Discover** | main (may dispatch an Explore agent) | before Do/Check, scan agent registries for a fit |
| **Reuse** (fit exists) | script | `agent(prompt, {agentType:'<name>', schema})` |
| **Create** (no fit + repeatable) | **main** | Write a project-local `.claude/agents/<name>.md` (clear role, least-privilege tools), THEN script uses it via `agentType`. Scripts have no `fs` — they can never create agents. |
| **Don't create** (one-off / near-duplicate) | script | default workflow agent (omit `agentType`) |
| **Evolve** (after a phase) | **main** | read structured results (gaps, residuals, which agent underperformed) → Edit that agent `.md` to improve it. Self-evolution loops in main, never in the sandbox. |

This is the create-vs-reuse gate (agent-skill-authoring rule): create when role absent + repeatable; reuse when discovered agent approximately fits (then evolve); don't create for one-off inline.

## Procedure (each phase = one TodoWrite item; do not skip ahead)

Create a TodoWrite todo per phase. Mark `in_progress` on entry, `completed` only when its exit condition holds.

### Phase 0 — Stamp + scope (main)
1. Run `date '+%Y-%m-%d-%H%M'` → `<dt>`. Pick `<feature>` slug.
2. Confirm this is a **single** feature. Multi-feature → stop, route to `/cowork-sprint`.
3. Ensure target `docs/` exists with cowork-doc-sync taxonomy folders as needed.
4. **Entry-mode check — pre-planned vs interactive.** If the caller (a user pointing at an existing design doc, or `/cowork-sprint` PHASE 1) supplies a **design doc that already contains the WorkList**, this is **execution-only mode**: validate the doc has WorkList + (agentMap | derivable) + verifyCmd decision, derive `fileGroups` (Phase 3 step), then **jump directly to Phase 4**. Phases 1–3 run ONLY in interactive mode (no design doc supplied). Rationale: planning is interactive; re-running it mid-autonomous-flow would pause the caller — pre-planned input means planning already happened.

### Phase 1 — Research (Workflow)
- Invoke `Workflow({script, args:{feature, dt}})` using the Research template in `references/workflow-scripts.md`.
- Script fans out a multi-modal sweep (code / web / entity), returns `ResearchFindings` (schema in `references/schemas.md`).
- Main writes findings → `06-research/<dt>-<feature>.md`.
- Exit: findings file exists.

### Phase 2 — Plan (MAIN, thinking)
- Read findings. Design the approach in the main session (thinking active — never delegate).
- Write `02-planned/<dt>-<feature>-plan.md` (status ACTIVE-PLAN) — fill the Plan skeleton in `references/doc-templates.md` (fixed sections, fill slots).
- Exit: plan file exists.

### Phase 3 — Design (MAIN, thinking) — fixed artifact
- Converge the design into `02-planned/<dt>-<feature>-design.md` (status ACTIVE-PLAN) — fill the Design skeleton in `references/doc-templates.md`. **This doc is the single input to Do.**
- Produce a `WorkList` **as a JSON value** (schema in `references/schemas.md`) held in session AND embedded in the design doc for humans. Items: `{id, file, change, dependsOn}`.
- **Main pre-processes the WorkList before Do**: topo-sort by `dependsOn`; build `fileGroups` (one array per file, dependency-ordered) so same-file items serialize and disjoint files parallelize.
- Build `agentMap` `{[itemId]: agentType, fix: agentType}` from the agent-lifecycle step (discover/reuse/create). Omit entries to use the default workflow agent.
- Detect `verifyCmd` for this stack (e.g. `npm test && npm run lint && tsc --noEmit`), or `null` if non-verifiable.
- Exit: design doc + WorkList(JSON) + fileGroups + agentMap + verifyCmd ready.

### Phase 3R — Plan review (MAIN dispatches an adversarial panel) — the R in PRDCA
- **A plan defect found in Check costs a whole build cycle. Catch it here instead.**
- Pick lenses by what would sink THIS design (min 2 = completeness + dominant risk; typical 3; cap 5). Dispatch **one agent per lens, concurrently, purpose-fit `agentType` where one exists**. Never a fixed clone count. **The design's author does not review it** — fresh-context subagents only.
- Each reviewer returns schema-forced `{verdict, findings[{severity, claim, where, whyItSinks, fix}]}`; findings only at ≥80 confidence, no style/wishlist nits.
- **Exit gate**: BLOCKER present → fix the design, re-run only the blocking lenses, re-gate. 2+ lenses raising the same finding independently = BLOCKER regardless of stated severity. MAJOR → fix if cheap, else record as accepted risk in the design doc. Phase 4 MUST NOT start while a BLOCKER stands.
- Skip the panel only when ALL hold: single file, reversible, no new pattern, verifyCmd exists (self-check one pass instead). A panel on trivial work becomes a rubber stamp.
- Record lenses used + verdict + findings kept/waived in the design doc.
- Lens table, return schema, and full gate rules → **`references/plan-review-panel.md`**.

### Phase 4 — Do (Workflow)
- Invoke `Workflow({script, args:{workList, fileGroups, agentMap, designPath, dt, feature}})` using the Do template. **Inline the real schemas into the script string** (sandbox has no fs).
- Script runs `fileGroups` with `parallel()` across files and serial within a file (no per-item worktree — same-file serialization prevents lost-update).
- Exit: Workflow returns built result.

### Phase 5 — Check/Act (Workflow, loop-to-100)
- Invoke `Workflow({script, args:{designPath, verifyCmd, agentMap, dt, feature}})` using the Check template (schemas inlined).
- **Verifiable work (`verifyCmd` set): the script RUNS the real stack checks first** (exit code, not opinion); matchRate==100 requires executed checks green AND lenses==100. Non-verifiable: lenses only, ≥90 floor.
- Lenses = perspective-diverse verify (correctness / regression / design-fit) vs the design doc; gaps fixed with `parallel()`, loop until 100 or max 5.
- Main re-stamps `date` and writes `05-reports/<dt2>-<feature>-check.md` (Check skeleton in `references/doc-templates.md`; snapshot uses its OWN datetime, not Phase-0 `<dt>`).
- **Quality gate = NO BRANCH**: do not pause on matchRate<100. If max 5 exhausted < 100 → carry residualGaps to Report. Do not stop.
- Exit: GapResult returned (100 or residual recorded).

### Phase 6 — Report + lifecycle (main)
- Re-stamp `date` → `<dt3>`. Write `05-reports/<dt3>-<feature>-report.md` — fill the Report skeleton in `references/doc-templates.md` (incl. QA table + anticipated questions; phaseHistory passed through from Check's returned `iterations`/`testsRun`, NOT LLM-reconstructed).
- Update `01-built/<feature>.md` (LIVING, as-built; section skeleton in `references/doc-templates.md`). See **Document lifecycle** below.
- Hand off to `/cowork-doc-sync` for final taxonomy alignment.
- Exit: report + 01-built updated, planned reconciled.

## OODA — tactical layer inside Do/Check (PRDCA is strategy, this is tactics)

When execution contradicts the plan, do not just push harder along it. `Observe → Orient → Decide → Act`, then keep moving. **Orient is the step that decides everything**: if an observation breaks a premise the R panel accepted, the premise loses, not the observation.

| Observation | Decide |
|---|---|
| mechanical failure (typo, missing import, flaky env) | adjust-in-plan, continue |
| same failure 3× or 10+ tool calls with no progress | re-plan the slice → re-run **only** the affected R lenses |
| a design premise turns out false | re-plan that slice; untouched slices keep running |
| real work outside this feature's goal | defer as a follow-up item — never widen scope mid-run |
| the surprise makes an irreversible action look wrong | escalate — stop before the safety gate, report |

Log each decision (observation → decision → why) into the Check report; repeated re-plans with one cause are a standing defect → fold into Act. Detail → **`references/plan-review-panel.md` §5**.

## Turn discipline — one perspective per turn

Splitting work across several short turns beats executing it all in one long turn. Ask **"is there exactly one question I must answer in this turn?"** — if not, split. Keep authoring, review, and execution in separate turns; keep non-deterministic generation separate from deterministic assembly. This is about *perspectives*, not tool calls — independent lookups serving the same perspective still batch into one message.

## Gate model (two orthogonal axes)

| Gate | Axis | Handling |
|---|---|---|
| No-Go / matchRate<100 | quality | **no branch** — loop-to-100, on miss record residual gaps in report, keep going |
| git push · deploy · vault bulk · remote migration | safety | **gate stays** — Workflow does everything up to it; before the launch the main session runs a thinking adversarial review (Check lenses are thinking-off) and only then approves the launch |

Quality is solved by score; safety is NOT (irreversible even at 100). Never auto-fire irreversible actions inside a Workflow. **Before the irreversible launch, main runs a thinking adversarial review** — risk-selected lenses (correctness + the action's dominant risk). The Workflow's Check lenses ran thinking-OFF (Workflow agents have no thinking), so this is the ONE thinking judgment pass before an irreversible action; only then approve. Safety axis only — it does NOT reopen the matchRate loop.

Verifiable work targets 100%. Non-verifiable work floors at ≥90% (CLAUDE.md PDCA rule).

## Document lifecycle (on build completion)

**DONE predicate (code-checkable, gates the irreversible delete — NOT the raw LLM float):**
`done := every WorkList item present in built result AND no blocker/major gaps in GapResult`. Compute in main. Only `done` triggers design-doc deletion; a hallucinated `matchRate:100` without item-coverage does NOT. **`done` always overrides the ≥90 floor for the delete decision** — non-verifiable work at matchRate 92 with an open `major` gap is `done==false` → KEEP the design doc.

```
done == true (all built):
  01-built/<feature>.md            ← as-built, CLEAN. Section-scoped MERGE: replace only the sections THIS cycle changed; never wipe the whole file (it may cover other features). Old superseded sections are deleted (not struck); git holds history.
  02-planned/<dt>-<feature>-design.md  ← DELETE the file (no strikethrough on a doomed file).
  02-planned/<dt>-<feature>-plan.md    ← also superseded → cowork-doc-sync deletes / moves to 04-legacy.

done == false (residual after max 5):
  01-built/<feature>.md            ← as-built of implemented parts only, CLEAN (section-scoped merge).
  02-planned/<dt>-<feature>-design.md  ← KEEP. Strike through implemented items; un-struck = residual.
                                          **≥50% of items struck AND struck count ≥3 → DELETE the struck
                                          items instead** (keep only residual + one line "implemented →
                                          01-built / git"). Small-doc guard: with <3 struck items the ratio
                                          trips too easily (1 of 2 = 50%) — keep strikethrough there.
                                          100% struck = done case above → delete the file.
  02-planned/<dt>-<feature>-plan.md    ← KEEP (still active).
  05-reports/<dt3>-<feature>-report.md ← residual gap list (re-pursue later as a NEW dated 02-planned plan).
```

Rules:
- **01-built never has strikethrough**, and edits are **section-scoped merges** — replace only this cycle's sections, never whole-file overwrite (protects the single-LIVING authority when one file spans multiple features).
- **Strikethrough lives only in 02-planned** (residual case), marking planned items that got built — cancellation marker, not preservation, kept short/inline. **Noise cap**: once struck items reach ≥50% of the plan AND there are ≥3 of them, delete them (leave residual + a one-line pointer); a doc that is mostly strikethrough misleads more than it informs, and git holds the history. Small-doc guard: below 3 struck items the ratio is meaningless — keep the strikethrough.
- **Deletion is terminal + idempotent.** The design doc must persist through Check; delete only here in Phase 6. **Resume guard**: if the design doc is absent AND `01-built/<feature>.md` exists → the cycle is already complete; do NOT re-run Check.
- Re-pursuing a residual → fresh dated `02-planned` plan (history separated by datetime).

## Structured output (code consumes LLM output → schema-forced, never free-text+regex)

All execution-phase scripts return schema-validated JSON. Full schemas: `references/schemas.md`.
`ResearchFindings` · `WorkList` · `GapResult{matchRate,gaps[]}` · `Report{phaseHistory,matchRate,residualGaps,carryItems}`.

## Red flags — STOP

- About to put Plan/Design logic inside a Workflow script → STOP (thinking is off there; keep it in main).
- About to call `Date.now()`/`new Date()` in a script → STOP (it throws; stamp in main, pass via args).
- About to pause the Workflow on matchRate<100 → STOP (quality gate has no branch; loop-to-100 then report).
- About to auto-run git push / deploy / vault bulk inside a Workflow → STOP (safety gate stays in main).
- Multi-feature scope creeping in → STOP, route to `/cowork-sprint`.
- About to start Do with a BLOCKER open from Phase 3R → STOP (fix the design first).
- About to review your own design, or to spawn N identical reviewers instead of distinct lenses → STOP.
- About to push harder along a plan that execution just contradicted → STOP, run Orient (OODA) before deciding.
- About to batch several unrelated perspectives into one turn → STOP, split them.

## Quick reference

| Phase | Actor | Output | Gate |
|---|---|---|---|
| 0 Stamp | main | `<dt>`, scope check | single-feature only |
| 1 Research | Workflow | `06-research/<dt>-<feature>.md` | — |
| 2 Plan | main (thinking) | `02-planned/<dt>-<feature>-plan.md` | — |
| 3 Design | main (thinking) | `02-planned/<dt>-<feature>-design.md` + WorkList | fixed artifact = Do input |
| 3R Plan review | main → adversarial panel | lenses + verdict recorded in design doc | **BLOCKER ⇒ Do cannot start** |
| 4 Do | Workflow | code | — |
| 5 Check/Act | Workflow loop-to-100 | `05-reports/<dt2>-<feature>-check.md` | quality: no branch |
| 6 Report | main | report + `01-built/<feature>.md` + cowork-doc-sync | safety: thinking review → irreversible gated |

References: `references/workflow-scripts.md` (script templates) · `references/schemas.md` (JSON schemas) · `references/plan-review-panel.md` (Phase 3R lenses + OODA tactics) · `references/taxonomy-map.md` (taxonomy + lifecycle + cowork-doc-sync handoff).
