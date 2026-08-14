# Plan-review panel (PRDCA "R") + OODA tactical layer

Read when running **Phase 3R** (plan review) or when execution hits a surprise (OODA).

The cycle this skill runs is **P → R → D → C → A**:

| Step | Owner | Question it answers |
|---|---|---|
| Plan / Design | main (thinking) | what should be built |
| **Review (R)** | **main dispatches an adversarial panel** | **is this plan wrong before we pay to build it** |
| Do | Workflow | build it |
| Check (C) | Workflow | axis-1 built-as-designed · axis-2 does it meet the intent |
| Act (A) | main | fold the lesson into docs/rules so it cannot recur |

A plan defect costs one full build cycle if it is found in Check. The cheapest place to
catch it is immediately before Do.

---

## 1. When R runs (and when it does not)

Run the panel when ANY holds:

- the design touches more than one file group, or introduces a new layer/pattern/dependency
- the work is irreversible or user-facing (schema/API/deploy/external send)
- an existing standard, architecture doc, or prior decision governs this area
- the WorkList has ≥ 8 items, or any item has no acceptance evidence

Skip the panel (self-check only, one pass) when ALL hold: single file, reversible,
no new pattern, verifyCmd exists. Running a panel on trivial work turns the gate into a
rubber stamp — that failure mode is worse than skipping it.

## 2. Panel composition — lenses, not a headcount

Pick lenses by what would actually sink THIS plan; never a fixed number of clones.
Minimum = 2 (**completeness** + the dominant risk lens). Typical = 3. Cap = 5.

| Lens | Hunts for |
|---|---|
| completeness | steps/files/deps the plan omits; WorkList items with no acceptance evidence; "already implemented" assumptions that were never verified |
| authority-fit | conflicts with an existing standard, architecture doc, prior decision, or public contract this plan silently bypasses |
| scope | over-build (work the goal does not require) and under-build (goal not reachable from this WorkList) |
| reversibility | where this becomes irreversible, whether a checkpoint precedes it, and how to roll back |
| assumption | premises the plan treats as fact but never verified, and the cheapest way to verify each |
| integration | ordering/dependency errors, same-file collisions, contract surfaces that must change together |

Dispatch each lens as a **separate agent** with a purpose-fit `agentType` when one exists
(discover → reuse → create, per the skill's agent-lifecycle rule). One agent = one lens.
Run them concurrently in a single message.

**The plan's author never reviews it.** The main session wrote the design; a fresh-context
subagent must read it. Self-review inherits the author's rationalizations.

## 3. What each reviewer receives and returns

Give each reviewer: the design doc path, the WorkList JSON, the research findings path, and
the paths of the governing docs it must check against. Ask for **findings, not approval**.

Required return shape (schema-forced; `references/schemas.md` holds the JSON schema):

```
{ verdict: "GO" | "FIX-FIRST",
  findings: [ { severity: "BLOCKER"|"MAJOR"|"MINOR",
                claim: "...", where: "design §/WorkList item id",
                whyItSinks: "concrete failure this causes",
                fix: "smallest change that removes it" } ] }
```

Discipline that keeps the panel signal-dense:

- report only findings the reviewer would defend at ≥80 confidence
- **do NOT report**: style/naming preference, restatements of the plan, "consider also…"
  wishlist items, anything a linter or the verifyCmd already catches
- every finding names the concrete failure it causes — a finding with no failure mode is a nit

## 4. Exit gate

```
BLOCKER present            → fix the design, re-run ONLY the lenses that raised blockers, then re-gate
MAJOR only                 → fix now if cheap; otherwise record in the design doc as an accepted risk with rationale
MINOR only                 → note and proceed
2+ lenses raise the same finding independently → treat as BLOCKER regardless of stated severity
```

Phase 4 (Do) MUST NOT start while a BLOCKER stands. Record the panel result (lenses used,
verdict, findings kept/waived) in the design doc so Check and Report can reference it.

## 5. OODA — the tactical layer inside Do/Check

PRDCA is the strategy: what to build, in what order. OODA is what to do **when reality
disagrees mid-flight**. Loop speed is the point: a wrong plan corrected in one cycle beats a
perfect plan defended for three.

```
Observe  gate output, agent returns, error text, timing — the raw signal, not your summary of it
Orient   ★ the step that decides everything: does this observation break a premise of the plan?
Decide   adjust-in-plan | re-plan | defer | escalate  (see the table below)
Act      do it, and record what changed and why
```

**Orient is where runs go wrong.** The common failure is observing a surprise and moving
faster along the existing plan instead of asking whether the plan still holds. If an
observation contradicts a premise the panel accepted in R, the premise loses — not the
observation.

Decision table (keeps the autonomous run moving; only the last row stops it):

| Observation | Decide |
|---|---|
| a step fails on a mechanical cause (typo, missing import, flaky env) | adjust-in-plan — fix and continue, no re-plan |
| the same failure recurs 3× or 10+ tool calls pass with no progress | re-plan — the approach is wrong; return to Design, then re-run R on the changed part only |
| a premise the design relied on turns out false | re-plan that slice; leave untouched slices running |
| new work surfaces that is real but outside this feature's goal | defer — record it as a follow-up item, do not widen scope mid-run |
| the surprise makes an irreversible action look wrong | escalate — stop before the safety gate and report; never auto-fire |

Cost discipline: re-running R after a mid-flight re-plan covers **only the changed slice**.
Re-reviewing the whole design on every adjustment converts the tactical layer into churn.

Log every OODA decision (observation → decision → why) into the Check report. That log is
what makes Act (A) possible: repeated re-plans with the same cause are a standing defect in
how plans get written, and belong in a rule, not in the next plan's preamble.
