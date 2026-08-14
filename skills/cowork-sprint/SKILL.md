---
name: cowork-sprint
description: |
  Plan-then-execute sprint orchestrator for multi-part work spanning several areas with sequential dependencies. Trigger on sprint plan, run sprints, plan and execute, /cowork-sprint, or implicit cues like "break this into sprints", "plan it all up front then build the whole thing", or any multi-feature initiative sharing one scope/timeline. Works like a real delivery team: ~1-human-week sprints, concurrent dispatch, leader (main session) dynamically scaffolds project-local agents for ANY domain (dev, marketing, research, ops, data). DO NOT use for single-file edits, one-shot bug fixes, work under ~a few hours, or a single-feature plan (use /pdca-wf instead).
argument-hint: "[goal / feature set / plan-file(s)]  [--auto-plan]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash       # build, test, git, scaffold agent files
  - Agent      # dispatch project-local / plugin agents (delegate pattern)
  - Workflow   # deterministic fan-out (direct-execution pattern)
  - Skill      # /simplify, /cowork-doc-sync, /pdca-wf
  - TodoWrite  # phase checklists become tracked todos (mandatory, not passive lists)
  - WebSearch
  - WebFetch
effort: max
---

# cowork-sprint: Plan-Then-Execute Sprint Orchestrator

> Composite orchestrator skill — exempt from single-responsibility and minimum-tool rules.
> Runs in the **Main Session** as the embodied team **Leader**. One entry (`/cowork-sprint`) covers planning → execution; phases are internal stages, never user-issued sub-commands.

## Mental model — a real delivery team

```
Roadmap            (several Sprints — overall direction & velocity)
  └─ Sprint        (≈1 human-week of work; full cycle: research→plan→design→do→QA→fix→deploy)
       └─ Cycle    (the work inside a sprint, run by the Leader)
            └─ Execution pattern per chunk:
                 ├─ DELEGATE  → autonomous agents (swarm / parallel / council)   [Agent/Task]
                 └─ DIRECT    → Leader does it: inline  |  Workflow (det. script)
```

- **Not dev-only.** Marketing (research→strategy→copy→publish), planning (discovery→PRD→build), ops, data — same skeleton.
- **Leader = the Main Session, embodied.** See *Execution Model* below for the hard rule.

## Prerequisites & execution model (MUST)

- **Main Session only.** The skill IS the Leader. Claude Code blocks `sub-of-sub` agent spawning and disables thinking inside subagents — so the Leader must never be spawned as a subagent.
- ❌ **Anti-pattern:** `Agent(cto-lead)` (or any "delegate the leadership") — that pushes the Leader into a thinking-off subagent and makes its inner dispatches `sub-of-sub`. bypass-pdca does this; cowork-sprint deliberately does NOT.
- ✅ **Leader stays in main**, and from there spawns workers / runs workflows at **1 level**:

```
Main Session = cowork-sprint Leader
  ├─ Agent(worker-A)         -- DELEGATE, 1-level OK (run several in parallel)
  ├─ Agent(worker-B)         -- concurrent dispatch = parallelism (NOT nesting)
  └─ Workflow(...)           -- DIRECT execution, 1-level; its agents are flat workers
```

- ★ **Concurrency ≠ nesting.** Running many sprints "at once" = the Leader firing concurrent dispatches (parallel `Agent` calls ‖ a single fan-out `Workflow`). There is never a sub-leader. Workflow is a *direct-execution* method, not delegation — its spawned agents are flat workers, and that is correct, not a "lost team."
- **Workflow only from main** (1-level — no Workflow inside Workflow; subagents don't author Workflows).
- **pdca-wf runs via `Skill(/pdca-wf)` in main, NEVER as `Agent(subagent)`.** Its Plan/Design assume main-thinking and its Do/Check author Workflows (main-only, 1-level) — inside a subagent both collapse (thinking-off + Workflow forbidden). Feature-to-feature parallelism comes from within-feature Workflow fan-out, not from wrapping pdca-wf in a subagent; pdca-wf runs are main-sequential.
- **Runs autonomously to completion** in PHASE 1 (no per-step confirmation). A decision arising mid-run routes by a 3-tier rule — the flow is never interrupted for a decision:
  1. **Low-risk / easily reversible** → the Leader decides and continues (logs the decision).
  2. **One option is obviously dominant** (clear, large advantage over the alternatives) → decide and continue (log).
  3. **Otherwise** (genuinely ambiguous, OR important but not irreversible) → do NOT pause: take the most reasonable default to keep moving (or skip just that sub-part), record it to `status.json deferredDecisions[]`, and present the whole batch to the user at the END (final report) for review/override.
  - **Clarifying questions belong up front**: batch everything that needs the user at the PHASE 0 approval gate (one round) — the run assumes the user is away (overnight-safe), so no mid-run questions.
  - **The only mid-run hard gates are irreversible/outward actions** (deploy · remote migration · commit/push · mass delete · doc-delete) — those still pause for explicit approval. Distinguish: *decision ambiguity* → defer to the end-batch (keep going); *irreversible execution* → gate mid-run (safety, not a decision).
  - **Progress trail**: ~1 line per gate/phase (light, for an away user) — not a stream.

## Input interpretation

`$ARGUMENTS`:

| Pattern | Behavior |
|---------|----------|
| Goal / feature-set prose (e.g. "ship auth + billing + onboarding") | Enter PHASE 0, co-plan the roadmap |
| Existing plan file(s) / glob (`docs/**/*.plan.md`) | Treat as pre-written sprint plans; confirm/refine, then execute |
| `--auto-plan` flag | Skip collaborative planning — Leader plans the roadmap alone, then executes |
| (resume) `.ww-w-ai/cowork-sprint/status.json` exists | Resume from the first unfinished sprint (see *Resume*) |
| No arguments & no status | Ask the user for the goal, then PHASE 0 |

## PHASE 0 — Sprint Planning  (default: collaborative)

> Goal: produce **all** sprint plans and the roadmap **before any execution**, approved by the user.
> This is the "freeze-before-code" principle: converge in dialogue → freeze plans → those frozen plans are the single input to execution.

```
0. Read the local sprint config (§6A) — docs/CONVENTION.md or a `## cowork-sprint scope`
   section in CLAUDE.md/AGENTS.md. Apply its knob overrides for this run; if absent, use
   defaults and note project-specific knobs are undeclared (offer to scaffold one).
   If the config sets no profile, detect dev markers (package.json/go.mod/Cargo.toml/
   pyproject.toml/…) and SUGGEST `profile: dev` (richer dev verification —
   references/dev-profile.md); apply it only after the step-7 approval gate, never auto.
1. Understand scope (dialogue with the user, one question at a time when ambiguous).
2. ★ PRD-lite (intent anchor) — when multi-feature OR high-uncertainty (knob #2;
   default ≥2 features OR user-flagged uncertainty): fill templates/prd-lite.template.md
   (Problem / Success Metrics / Out-of-scope / Pre-mortem) BEFORE the WorkList — it is
   the input the WorkList/design derive from, and the yardstick the Tier-2 intent-audit
   measures against. Set status.json prdRef. Trivial/single-feature → record
   "PRD-lite skipped" and proceed.
3. Size the work in HUMAN terms (~1 human-week = 1 sprint), then DERIVE the sprint count from that
   estimate — **do NOT default to a fixed 3–6 regardless of size**; state the derivation (N deliverables
   × ~1wk → N sprints). Size-tier anchor: Single 1 · Small 2–4 · Medium 5–8 · Large 9–12 (>12 → split into multiple roadmaps)
   (→ references/sprint-method.md §1). Count is provisional here (the "define"/plan step) and may be
   re-split/merged during step-5 detailing (the "design" step) — re-adjust + log.
   - Build the sprint list + dependency graph (which sprints are independent vs ordered).
   - Decide execution mode per cluster: independent → eligible for concurrent dispatch;
     ordered/high-risk/LIVE → sequential.
4. Identify the ROLES this project needs (dev? QA? researcher? copywriter? analyst?).
   - **Archetype coverage check (not open-ended role-guessing).** Walk the archetype set in
     **`references/agent-archetypes.md`** — the `profile: dev` legion is a SAMPLE of a complete
     team; for each archetype (verifier / critic / design-validator / risk-lens / QA / diagnosis
     / architect / intent-auditor) decide "does THIS domain need it?" and produce the
     **domain-equivalent** (marketing/research/ops/data), or consciously skip (log why).
   - Scaffold project-local agents for missing roles  →  see "Dynamic agents" below.
5. Write a plan per sprint (goal, deliverables, cycle outline, deps, role assignments)
   into docs/  (repo) — these are the durable single input to PHASE 1.
   For every feature chunk that PHASE 1 will execute via /pdca-wf: ALSO converge its
   per-feature design doc + WorkList HERE (pdca-wf Phases 1-3 equivalent). Each WorkList
   item carries { id, description, acceptanceEvidence, priority } (knob #7) so the QA
   Axis-2 gap-analysis can measure matchRate. PHASE 1 invokes pdca-wf execution-only
   (design doc in → Phase 4 直行). Planning is interactive; deferring it would pause
   the autonomous run per feature.
6. Initialize .ww-w-ai/cowork-sprint/status.json  (schema → references/sprint-method.md).
6R. ★ ROADMAP REVIEW (the R in PRDCA) — dispatch an ADVERSARIAL PANEL, not one reviewer.
   - Lenses picked for THIS roadmap; minimum = completeness · sizing · sequencing (add
     authority-fit / scope / reversibility when relevant). One agent per lens, concurrent,
     purpose-fit agentType where one exists. The Leader wrote the plan → the Leader does
     not review it.
   - Each returns {verdict, findings[{severity, claim, where, whyItSinks, fix}]} at ≥80
     confidence only. BLOCKER ⇒ fix the roadmap, re-run only the blocking lenses, re-gate.
     Same finding from 2+ lenses independently ⇒ BLOCKER.
   - Fix BEFORE showing the user: the approval gate should receive a vetted roadmap.
   - Lens table, contract, gate rules → references/plan-review-panel.md
7. ★ APPROVAL GATE: present the roadmap (sprints, order, parallelism, agents) + the panel
   result (lenses run, verdict, findings fixed/waived) and get the user's go.
   Do NOT start execution before approval.
```

- `--auto-plan` → run steps 0-6 autonomously (sensible defaults, no dialogue), still write plans + show the roadmap, then proceed.
- Detailed sizing heuristic, planning-dialogue guidance, and the dependency rules live in **`references/sprint-method.md`**.

## Dynamic local agents (general team-building)

The Leader assembles a team fit for the project's domain — **reuse before rebuild**, scaffold only the gaps. Create-vs-reuse gate (prevents agent sprawl):
- **Create a new agent when** the role is missing from all discovery sources AND is a distinct, recurring responsibility this sprint actually needs.
- **Reuse existing (user-global / plugin / a prior scaffold) when** a discovered agent fits the role — even approximately; refine via the evolution loop rather than re-create.
- **Don't create for** a one-off step the Leader can do inline, a near-duplicate of an existing agent, or a role used only once with no reuse.

Scaffold only after this gate says "create":

```
For each needed role:
  1. DISCOVER existing agents first (reuse > rebuild) — scan in order:
       a. project-local   .claude/agents/*.md
       b. user-global     ~/.claude/agents/*.md
       c. all installed plugins' agents (review, feature-dev, madori, …)
     → a suitable fit exists → REUSE it (do not re-scaffold).
  2. No suitable agent → scaffold one:
       read  templates/agent.template.md   (researched high-performance template)
       write .claude/agents/<role>.md       (project-local, version-controllable)
             — fill role, description(triggers), tools(least-privilege), model
             — body ≤ 1500-word HARD CAP (mechanically checked; compact, don't sprawl)
In PHASE 1 dispatch them:  Agent(subagent_type="<role>")   or   Workflow agentType:"<role>"
NOTE: agents scaffolded MID-SESSION (esp. in a worktree) may be absent from the session's
agent registry ("Agent type not found") — verify with one dispatch; on failure fall back to
subagent_type="general-purpose" with "FIRST read .claude/agents/<role>.md (your role card —
follow exactly)" as the prompt's first step (equivalent behavior; proven 9/9 in practice).
Then EVOLVE them from their output (loop below) — a scaffold is a first draft, not the final agent.
```

- **How to write a strong agent** (frontmatter, description-triggers, system-prompt structure, length, tool scoping) → **`references/agent-authoring.md`** (synthesized from official docs + 36k/21k/12k★ collections). Read it before scaffolding.
- **How to write a strong skill** — when a role needs a **reusable capability or heavy domain knowledge** (not a one-shot role), scaffold a project-local skill (`.claude/skills/<name>/SKILL.md`) instead of bloating an agent body, and reference it via the agent's `skills:` field (which only references — it never auto-creates). → **`references/skill-authoring.md`** (CC official: <500 lines, description=triggers-only, progressive disclosure).
- **Mid-cycle agent evolution is NARROWED to UNBLOCK ONLY.** During a sprint, rewrite an owned scaffolded agent's `.md` **only when that agent is BLOCKING a gate** (its output keeps failing the exit-predicate/QA so the sprint cannot proceed) AND the gap is a DEFINITION defect (would recur — vague role, missing constraint, loose output-format, over-broad scope). Fix exactly that, stay under the **1500-word cap by compaction, never accretion**; if a role keeps failing, **split it**. Max **2** unblock rounds/agent/sprint, then auto-pause `AGENT_EVOLUTION_EXHAUSTED`. Owned = cowork-sprint's own project-local scaffolds **only** — never rewrite borrowed plugin/user-global or fixed shipped agents (`cowork-intent-auditor`, `cowork-facet-extractor`). **All NON-blocking / quality improvements are NOT done mid-cycle — they are deferred to the terminal Retrospective phase (user-gated, see PHASE 2).** Full loop → **`references/agent-authoring.md` § Self-evolution**.
- **Discovery is plugin-agnostic.** Any installed plugin's agents are just sources in the pool above — reuse them like any other; absence changes nothing about the discovery order. The Leader stays in main either way.
- **This plugin ships one fixed agent — `cowork-intent-auditor`** (domain-agnostic Tier-2 intent audit, used by the intent-audit gate), found by the same discovery. Principle: **generic meta-roles ship fixed; domain-specific execution roles are scaffolded.**

## PHASE 1 — Sprint Execution  (autonomous to completion)

```
Leader runs the approved roadmap. For each sprint (sequential clusters one by one;
independent clusters dispatched concurrently):

  WORKTREE SETUP (CONDITIONAL — runs ONCE at execution start, before the first cycle):
    IF this roadmap MUTATES source/code (edits repo files, implements, refactors)
      → the Leader creates a dedicated worktree + branch off the base branch and runs ALL
        source edits (inline + parallel subagents) inside it:
          git worktree add ../<repo>-sprint-<slug> -b sprint/<slug>   (off the base branch)
      WHY: (1) isolates from the user's current working tree; (2) ★ a DIFFERENT independent
        session touching the same repo concurrently won't collide — this session-level isolation
        is the PRIMARY motive. The in-session file-ownership split (one file = one role, see
        INTEGRATION below) only de-conflicts parallel subagents WITHIN one session; the worktree
        is the layer ABOVE it (BETWEEN sessions).
    ELSE (pure research / planning / docs-only / no source mutation)
      → NO worktree (overhead not justified). Work in place.
    Detailed procedure (slug, base-branch detection, agent-registry caveat) → references/sprint-method.md §5c.

  Phase gate: each phase's checklist → actual TodoWrite items (mandatory, not a passive list);
  phase N-1 must be complete (its exit condition met) before phase N starts. → references/sprint-method.md §5

  CYCLE per sprint:
    research → plan-detail → [R panel] → design → [R panel] → do → QA → fix → intent-audit → commit → [adversarial before irreversible] → deploy/deliver
    (then, ONCE after all sprints: → doc-sync. Both commit & doc-sync are mandatory, not optional — see below.)
    · research = gather the facts THIS sprint needs before planning detail (codebase reality,
      external specs, constraints); never start `do` on assumptions (Research-before-Do).
    · MODEL SPLIT (judgment in main, mechanics delegated):
      authoring (plan-detail, design) = the LEADER in main (thinking ON, whatever model the session
        runs — typically Opus). Deep judgment lives here, never in a subagent.
        ★ **Before freezing a design, cross-check its THREE representations of the same work agree:
        the layout/placement description ↔ the test-migration list ↔ the WorkList items.** When these
        drift (e.g. the tier table says field X sits in the base layer, but the migration list only
        touches X's old collapsed section), the implementer gets conflicting signals and picks one —
        producing a deviation that costs a fix round. A one-pass 3-way reconcile at freeze is cheaper
        than a post-implementation correction. (Real case: an S2 design's tier table vs migration list
        disagreed on 2 fields → 2 implementer deviations → an extra fix round.)
      do / QA = delegated to /pdca-wf execution-only (its Workflow; thinking-off is fine, coding is
        mechanical) — not a separate model choice here.
      [R panel] after plan-detail / after design — the R in PRDCA. An ADVERSARIAL PANEL of
        INDEPENDENT fresh-context subagents, one agent per LENS, dispatched concurrently — never a
        single reviewer and never N identical clones. Lenses picked for this sprint; minimum =
        completeness + authority-fit + the sprint's dominant risk. ★ **sizing is a MANDATORY lens
        at roadmap level: each sprint ≈ 1 human-week — over-large → split, trivially small → merge;
        a mis-sized roadmap is a plan defect, not a nit**. Each returns
        {verdict, findings[{severity, claim, where, whyItSinks, fix}]} at ≥80 confidence only.
        BLOCKER (or the same finding from 2+ lenses independently) ⇒ fix the plan, re-run only the
        blocking lenses, re-gate; `do` MUST NOT start while a BLOCKER stands. The panel's value is
        INDEPENDENCE (it catches what the author's context is blind to), NOT reasoning depth —
        subagents run thinking-OFF (CC runAgent.ts:682), so a cheaper model suffices; don't mislabel
        it "Opus deep review". Skip only when the sprint is single-surface + reversible + no new
        pattern + mechanically verifiable (log the skip). Lens table + contract →
        references/plan-review-panel.md
      [adversarial before irreversible] = the safety gate: independent lenses (subagents, thinking-off
        = independence) then the Leader's final judgment in main (thinking) before approving. Never
        approve an irreversible action off a thinking-off review alone.
      Why review at all: a fresh read catches plan-killers (nonexistent tables, SCHEMA_VERSION
        collisions, missing infra) the author glosses over — an independence check, achievable without
        thinking; not a reason to route authoring to a weaker model.
    · choose an execution pattern per work-chunk:
        DELEGATE  (Agent swarm/parallel/council)  — exploratory, judgment, heterogeneous, few
        DIRECT inline                              — small / quick
        DIRECT Workflow (deterministic script)     — structured, bulk, repetitive, wide parallel
    · concurrency = Leader's concurrent dispatch from main (parallel Agents ‖ one fan-out Workflow)
    · INTEGRATION after any parallel fan-out (MANDATORY step, before QA): Leader merges the slices
      AND runs a COMMON-EXTRACTION pass — scan the new/changed files for duplicated/near-duplicate
      helpers, configs, or patterns that parallel workers each rolled on their own → consolidate
      into ONE shared implementation and verify only that one. N copies = N× the defect surface
      (one flawed copy means all copies are flawed), and the consolidated helper is the only
      place a later fix needs to land.
    · Workflow verification panels MUST return a compact schema: confirmed findings + counts only,
      per-finding reasoning capped (~300 chars), no transcript dumps — an oversized panel return
      is unparseable by the Leader and stalls the gate.
    · QA gate per sprint: the phase's **exit predicate** must hold before deploy/deliver, and the
      Leader VERIFIES it by running the check (real exit code) — never by trusting a transcript claim.
    · QA TABLE (MANDATORY — green runners alone are NOT QA): at QA entry the Leader BUILDS a
      feature→check table for THIS sprint (every shipped feature/behavior gets a row: what proves it
      works — test runner, manual probe, live check, or "deferred-to-deploy" with reason), then
      CHECKS OFF each row and includes the table in the sprint report. The user never authors this —
      the Leader derives rows from the sprint plan's deliverables. An unchecked row without an
      explicit deferral reason = QA gate FAIL. (Prevents "35/35 green but features unverified".)
      Persist per-sprint table → status.json `sprints[].qaTable`; consolidated table → final report.
      Mechanical baseline = **detect the stack, run ITS tools** (format-check+lint+type/compile+test;
      tooling differs by language — JS/TS tsc+eslint, Python ruff+mypy+pytest, Go vet+test, …; run only
      what the project has). Engineering target = baseline green + matchRate **100%**, cap **5** fix-rounds.
      Plus a **ship-hygiene mechanical scan** (full set at sprint; cheap subset per-commit) — secrets/keys,
      conflict markers, abs-paths/host·port, manifest/config validity, packaging hygiene → §5.
      3-part predicate contract (end-state + executed check + reward-hack invariants) → references/sprint-method.md §5b.
    · intent-audit gate (Tier-2, before deploy): QA proves *output matches plan*; this proves *output
      serves the INTENT*. Run from a **reset perspective** — dispatch `cowork-intent-auditor` (a fresh
      agent that did NOT do the work) with intent + artifacts + QA result. PASS required → details §5.
    · commit (MANDATORY — via `/cowork-commit`, NOT a bare `git commit`): once a sprint's gate (QA +
      intent-audit) is green, commit its work with `/cowork-commit` (WHY-focused message + Co-Authored-By
      + AI directive-log + the mechanical-hygiene subset). Under the global git-safety gate (explicit user
      request; never push without it). Anti-pattern: settling for a bare `git commit` and skipping the
      directive-log — the cowork-commit step is required, not optional. Stage by name (no `git add .`).
    · agent evolution mid-cycle = UNBLOCK ONLY: refine an OWNED scaffolded agent's `.md` only if it is
      BLOCKING a gate AND the gap is a DEFINITION defect (≤1500-word cap, compact-not-append; split if
      mis-scoped), re-dispatch. Cap 2 rounds/agent → else AGENT_EVOLUTION_EXHAUSTED. Borrowed/fixed
      agents read-only. NON-blocking quality improvements are collected, NOT applied — they surface in
      the terminal Retrospective (PHASE 2, user-gated). → references/agent-authoring.md
    · update status.json as each sprint/cycle-phase completes (record on completion, not batched);
      record any agent evolution → agentEvolutions[]{name, round, reason, wordCount}
    · PROGRESS PING (MANDATORY in autonomous runs): emit ONE line to the user every ~5 minutes of
      wall-clock work OR at every cycle-phase/gate transition, whichever comes first — format:
      `[sprint-id phase] doing X — next Y`. No detail dumps, no questions; just visibility. Long
      silent stretches cause the user to interrupt a healthy run ("is it still working?") — the
      ping is cheaper than a killed run.

After each sprint cluster: **free-perspective augmentation pass** — step outside the plan and scan for
improvements, risks, and out-of-plan impact the plan didn't anticipate (the open lens a plan-bound check
misses); for code, invoke Skill(/simplify).
After all sprints: **consolidated report** — fill **`templates/sprint-report.template.md`** (FIXED structure, do not invent sections: per-sprint results / consolidated QA table from `sprints[].qaTable` / pending gates with unblockers / anticipated-questions preemptively answered / **deferred-decisions batch (from `deferredDecisions[]` — the mid-run ambiguities skipped with a default, each with the default taken + why, for the user to review/override)** / carry / next actions) —
**immediately followed by `/cowork-doc-sync` (MANDATORY closing step, not optional, not a "later" suggestion)**:
align docs/ to the shipped truth in one pass — `01-built` as-built + CLAUDE.md summary + built-complete
plans → FROZEN/`04-legacy`. Anti-pattern: ending the sprint at the report and *proposing* doc-sync as a
separate follow-up — that is exactly the drift this skill exists to prevent. Skipping doc-sync = the sprint
is NOT done (docs left stale). Run it, then — IF a sprint worktree was created (source-mutating roadmap) —
**run the AUTO-MERGE step** (below; automatic once verification is green, no approval pause), **THEN run PHASE 2 — Retrospective** (user-gated) as the true terminal step before declaring completion.
Default = **do NOT defer** — finish in-scope work this run. If something genuinely must carry to a future
sprint, it is **never silently dropped or silently expanded**, AND the report MUST state the **explicit
written reason** it was carried (why it could not finish now). Surface any sprint that paused unresolved.
```

- Pattern-selection heuristic is **encoded here + in `references/sprint-method.md`** (self-contained — do NOT defer to CLAUDE.md at runtime).
- **If a sprint preserves external behavior while changing how the code is built** → read the right ref first (both preserve behavior, so both mandate a characterization/**parity harness** over the changed surface BEFORE editing — else the QA gate is false-green — plus incremental change + adversarial 2-lens review). Distinguisher = *what* changes:
  - **`references/refactoring.md`** — the **internal code structure** changes; substrate stays (rename/extract/restructure).
  - **`references/migration.md`** — the **tech/data substrate** moves (library/framework/version/DB/data/API). Adds data-safety, cutover, rollback, irreversibility, dependency-pinning. *(sooji's Hono swap + session-hash live here.)*
- A sprint's cycle MAY borrow other installed plugins' agents/skills internally (e.g. /simplify for cleanup) — **but never expose another tool's split command flow to the user.** The whole cycle stays one autonomous conversation.

## PHASE 2 — Retrospective  (terminal, user-gated)

> Runs AFTER the consolidated report + `/cowork-doc-sync`, as the sprint's final step. Produces PROPOSALS only — nothing is auto-applied. The user picks what to apply at an apply-gate.

**Hard rule — repo-local outputs ONLY.** This plugin ships to all users, so the retrospective must NOT assume any personal system exists: **never write to CC memory (`~/.claude/.../memory`), `~/.claude/rules`, or any external wiki/vault.** Allowed targets = the project's `docs/` (taxonomy) + project-local `.claude/agents/*.md`.

Four things the retrospective does (A + B + C + E):

```
A. Agent & team review
   - Scorecard per OWNED scaffolded agent from signals already collected
     (QA pass, matchRate, fix-rounds, intent-audit verdict, unblock-evolution rounds).
   - Extract ONLY recurring DEFINITION defects → propose `.md` diffs (compact-not-accrete; split if mis-scoped).
   - Team-shape proposals: retire unused roles / split overloaded ones.
   - Applied (on approval) to project-local .claude/agents/<name>.md only.

B. Self-assessment (balanced + actionability-tagged — MANDATORY structure)
   - MUST list BOTH "what went well" AND "what went poorly / user had to catch" —
     a wins-only retro is self-congratulation, not assessment. Mine the friction signals:
     user corrections/interrupts mid-run, questions the user asked right after the report
     (= what the report failed to answer), gates that fired late or not at all.
   - Tag EVERY "went poorly" item with an actionability class:
       [FIXABLE-PROMPT]  — improvable by editing this skill's SKILL.md / agent .md / dispatch prompt
       [FIXABLE-SCRIPT]  — improvable by editing a script/Workflow template/schema (deterministic layer)
       [PROCESS]         — needs a human decision or external change (not a source edit)
   - FIXABLE-* items become concrete proposals at the apply-gate (with the target file named);
     PROCESS items go to Carry or the report's open questions.

C. Knowledge capture (LOCAL docs only)
   - Non-obvious learnings → docs/00-reference/<topic>.md (or a "Lessons" section of the retro report).
   - Decision log (WHY) → already fed to /cowork-doc-sync.
   - Reusable-asset promotion: prompts/scripts/agents that worked → project-local .claude/agents/ or repo templates/.
   - NEVER to memory/rules/vault.

E. Carry (unfinished) triage
   - Residual/unfinished → new dated docs/02-planned/<dt>-<carry>-plan.md, EACH with an explicit written reason
     it could not finish now. No silent drop, no silent expansion.
```

**The retrospective's center of gravity = SELF-EVOLUTION** — its purpose is not to re-summarize the work (the consolidated report did that; QA table / pending gates / anticipated questions live THERE), but to make the NEXT run better by changing the sources that drive it. Every section must terminate in an evolution proposal or explicitly conclude "no change needed":

Output = one retrospective report `docs/05-reports/<dt>-<sprint>-retrospective.md` — **fill `templates/retrospective.template.md`** (FIXED structure, do not invent sections: ① Agent evolution scorecard — zero-scaffold case must answer "was reuse right?" / ② Self-assessment with `[FIXABLE-PROMPT|FIXABLE-SCRIPT|PROCESS]` tags + target file = the evolution backlog / ③ Lessons with "promote to rule? yes(where)/no(why)" / ④ Carry, execution leftovers only). The template ends with the **APPLY-GATE table** — present it verbatim as numbered choices; only user-approved rows are applied; no response/interrupt → record the table as Carry (never silent-drop).

Parked (NOT in scope, recorded only if surfaced): process/method meta-edits to the skill itself, and risk/cost retrospect — out of the default A+C+E set.

## OODA — tactics inside execution (PRDCA is strategy, this is tactics)

The roadmap says what to do; OODA says what to do when reality disagrees mid-run.
`Observe → Orient → Decide → Act`, then keep moving. **Orient decides everything**: if an
observation contradicts a premise the R panel accepted, the premise loses, not the observation.
The failure to avoid is observing a surprise and executing the existing plan harder.

| Observation | Decide | Autonomy |
|---|---|---|
| mechanical failure (typo, missing dep, flaky env) | adjust-in-plan | keep running |
| same failure 3× or 10+ tool calls with no progress | re-plan that slice → re-run only the affected R lenses | keep running |
| a premise the design rested on is false | re-plan that slice; other slices keep running | keep running |
| real work outside this sprint's goal | defer to `deferredDecisions[]` | keep running — never widen scope mid-run |
| genuine toss-up, no derivable answer | commit an anchor, pick one, log it | keep running |
| the surprise makes an irreversible action look wrong | escalate | **stop at the safety gate, report** |

Only the last row stops the run — the autonomous contract still holds. Log every decision
(observation → decision → why) to `status.json`; repeated re-plans sharing one cause are a
standing plan-authoring defect and belong in the retrospective's Act, not in the next preamble.
Detail → `references/plan-review-panel.md` §5.

## Turn discipline — one perspective per turn

Several short turns beat one long turn that does everything. Test: **"is there exactly one
question this turn must answer?"** If not, split. Split along perspective boundaries —
authoring ≠ review ≠ execution ≠ doc update; non-deterministic generation (copy, images,
browser work) ≠ deterministic assembly (code, build). This buys depth per perspective, isolated
failures, an intervention point for the user, and the previous result available to steer the next.
**Not the same as batching tool calls** — independent lookups serving one perspective still go in
one message. Same mistake at roadmap scale = an over-large sprint, which is why the sizing lens
is mandatory.

## Gates & safety

- **Planning approval gate** (PHASE 0 step 6) — mandatory before execution unless `--auto-plan`.
- **Irreversible / outward actions** (deploy, remote migration, push, mass delete) — pause for confirmation even in autonomous mode; for high-stakes, run an adversarial review first with **risk-selected lenses** (not a fixed count — pick lenses orthogonal to the action's risk; min = correctness + ≥1 dominant-risk lens). **For installable/runnable artifacts (plugins, libs, CLIs, templates), the consumer-environment lens is MANDATORY** — one structured LLM pass (≥high-confidence only, with an exclusion list): portability · undeclared deps · undocumented env/config · public-interface breaks · docs↔behavior drift · install→first-run integrity · new-required-input. The cheap mechanical subset (abs-paths, conflict markers, manifest validity) also runs per-commit (cowork-commit). 7-ask checklist + v1.6.0 case → references/sprint-method.md §5.
- **QA gate** per sprint — must pass before deploy/deliver (includes the mandatory per-sprint QA table; unchecked row without deferral reason = FAIL).
- **Measurable gates (optional, on-demand)** — when the QA / pre-irreversible gate wants a *scored* pass/fail + audit line (not just prose findings), the Leader can reach for the gate catalog in **`references/verification-gates.md`** (`scripts/gates/` — G-BUILD/G-CONTRACT/G-MATCH/G-CRIT/G-MIGRATE/G-INTENT/G-DOCSYNC, thresholds overridable per-repo via `.cowork-gates.json`). Deterministic gates run directly; agent gates emit a structured prompt → dispatch → parse → threshold. **A tool the Leader picks, never a mandatory track.**
- **AUTO-MERGE** (terminal, only if a sprint worktree was created): a LOCAL merge is safe — full git history is retained and any merge is revertible (`git revert`/`reset`), so it runs **automatically once verification passes — no approval pause**. Precondition (gates the auto-merge; verification FAIL = no merge): **ALL** sprints done AND **whole-roadmap verification green** (build/typecheck + full test suite, re-run by the Leader on the integrated worktree — not per-slice trust) AND **intent-audit PASS** AND doc-sync ran. On green → the Leader automatically merges the `sprint/<slug>` branch into the **base branch it forked from** (the base it forked from — main included, since the merge is local), then auto-cleans up: `git worktree remove ../<repo>-sprint-<slug>` + delete the merged `sprint/<slug>` branch. Hard safety rails (NEVER broken even on the automatic path): NO hook-skipping (`--no-verify`/`--no-gpg-sign`), NO force, **NO auto-push** (merge stays LOCAL; remote push always requires explicit user request), verification FAIL → merge SKIPPED, merge **conflict → STOP and report to the user** (never auto/force-resolve). Procedure → references/sprint-method.md §5c.
- **Git**: never commit/push without explicit user request (global rule). Stage by name, WHY-focused message, `Co-Authored-By: Claude`.

### Auto-pause triggers (the autonomous loop's stop contract)

PHASE 1 runs unattended, so "when do I stop and ask the human" must be explicit. After each sprint/cycle-phase, the Leader checks this fixed set and **pauses + reports** if any fires:

- **QUALITY_GATE_FAIL** — QA gate not green (tests failing, critical issue, data-flow broken).
- **ITERATE_EXHAUSTED** — fix-loop hit its cap (**5**) and the predicate still doesn't hold. Never emit a false "done" to escape the loop (truthful-completion); pause and report instead.
- **AGENT_EVOLUTION_EXHAUSTED** — an owned scaffolded agent hit its evolution cap (**2** rounds) and its output still fails the predicate. The role is likely mis-scoped (split it) or the task needs human input — pause and report; don't keep rewriting the agent.
- **BUDGET / TIME_EXCEEDED** — cumulative cost or wall-clock passes the user's stated bound (if any).
- **IRREVERSIBLE_ACTION** — about to deploy/migrate/push/mass-delete (see above). (The terminal local AUTO-MERGE is NOT here — a local merge is revertible, so it runs automatically; only a remote push gates.)
- **MERGE_CONFLICT** — the sprint-branch → base-branch auto-merge conflicts → STOP and report; never auto/force-resolve.

**On resume, re-evaluate the pause reason first** — if it still fires, stop again and report rather than looping back into the same wall. (No event system — this is Leader discipline + `status.json`.)

## Progress tracking & resume

- State file: `.ww-w-ai/cowork-sprint/status.json` (roadmap + sprints[]{cycle phase, pattern, matchRate, status} + executionMode). Schema + update timings → **`references/sprint-method.md`**.
- `mkdir -p .ww-w-ai/cowork-sprint/` if absent; ensure `.gitignore` has `.ww-w-ai/`.
- **Resume**: read status.json → first sprint not in `completed`/`archived`/`failed` → resume its last cycle phase; skip completed sprints.

## Constraints

- Needs a goal or plan input. For a single quick edit with no multi-step scope, just do the work directly — don't spin up a sprint.
- **Single FEATURE (one cohesive feature, multi-step but not multi-sprint) → use `/pdca-wf`** (this plugin): one PDCA cycle with native Workflow as the execution engine (main owns Plan/Design; Research/Do/Check run as Workflow scripts; verify-to-100). cowork-sprint is for MULTI-feature initiatives; PHASE 1 calls pdca-wf **execution-only** (per-feature design doc + WorkList were frozen in PHASE 0 — never let pdca-wf re-enter its interactive Phases 1–3 mid-run).
- Leader never delegates leadership to a subagent (see *Execution Model*).
- Files referenced every run: `templates/agent.template.md`, `templates/sprint-report.template.md`, `templates/retrospective.template.md`, `references/agent-authoring.md`, `references/sprint-method.md`, `references/plan-review-panel.md` (R-panel lenses · OODA · turn discipline) — read them when the relevant step arrives (don't assume from memory). **Templated outputs are filled, never restructured** — fixed sections, fill the slots.
