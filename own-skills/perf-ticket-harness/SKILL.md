---
name: perf-ticket-harness
description: Evidence-first harness for performance / hot-query / lock-contention tickets (usually a Jira ticket citing an SRE or DB report). Drives the whole loop in fixed phases with checkpoints and artifacts — verify the report's claims against code, build a repeatable local bench under docs/perf-poc-shared/<ticket-slug>/ that reproduces the symptom, write a numbers-only findings report (md + html), POC the candidate fix as a standalone program and measure it, draft all solution candidates, then implement via the target repo's spec-kit flow, verify with the same bench, commit, push, open the PR, and self-review it. Use when asked to "reproduce", "bench", "prove the root cause", "make a loop for", or "finish the whole thing" for a perf ticket, or when a DB weekly report names a slow query. Do NOT use for feature work with no measurable symptom.
argument-hint: "<TICKET-ID> [--phase verify|bench|findings|poc|candidates|impl|pr|review|all] [--repo <name>] [--report <path-to-report.html|md>]"
---

# perf-ticket-harness

A harness, not a checklist: every phase has an **entry condition**, a **fixed artifact set**, and an
**exit gate** the next phase depends on. Phases run in order; the user can stop after any gate and
the work so far is complete and committed. The reference run that produced this harness is
CONNECT-6031 (`graphify-knowledge/docs/connect-6031/` + `docs/perf-poc-shared/connect-6031-view-count/`);
when in doubt, copy its shape.

## Arguments

| Token | Meaning |
|---|---|
| `<TICKET-ID>` | required, e.g. `CONNECT-6031`. Drives the slug `connect-6031-<short-topic>`, branch names, commit scopes, PR title |
| `--phase` | run one phase (default `all`, stopping at the first gate the user has not approved) |
| `--repo` | target service repo when the workspace holds several (default: infer from the ticket's code paths) |
| `--report` | the SRE/DB report(s) the ticket cites; copy them into `docs/<ticket-lower>/` first |

## Non-negotiable rules (learned the hard way)

1. **Prove the mechanism before proposing a fix.** Phase 3's report is the deliverable of the first round; fix candidates are names only until the user has read the numbers. Do not expand scope into implementation on your own.
2. **Every claim cites a run number.** No "should", "likely", "probably" in findings.md without `run-NN`.
3. **Local numbers never predict production.** Local runs are 10–100× production rate and exist to reproduce mechanism. Keep prod numbers in a separate section.
4. **Measurement assets go in `docs/perf-poc-shared/<ticket-slug>/`**, one dir per ticket. Shared layer (`bench-utils.sh`, `database-baseline/`, `load.sh`) is borrowed, never modified. Results (`runs/`, `bench-log.md`) are gitignored; scripts and README are committed.
5. **No load-test framework unless asked.** `awk` + `xargs -P` + `curl` is enough; the DB-side numbers (`pg_stat_statements`, `pg_stat_activity` wait sampling) are the product. The user explicitly did not want k6.
6. **Never touch the target repo during bench/POC phases.** POCs are standalone programs in the bench dir using the same library versions as production.
7. **Commit messages: conventional + gitmoji + `[TICKET]`, no AI co-author trailers.** Spec/docs commit first, implementation second (the repo's `git-commit-conventional-strict` convention).
8. **Verify the report, not just the ticket.** AI-written tickets and SRE pipelines are inputs to check, not facts. Arithmetic first: cumulative vs weekly deltas, marginal cost per call, identical max values across weeks = one historical event.

## Phase 0 — Intake (no gate)

- Read the ticket (Jira MCP), the cited reports, and any earlier analysis. Copy reports to `docs/<ticket-lower>/`.
- Record which claims are **attribution** (who writes the query), **volume** (calls/hour), **cost** (avg/max), **trend** (weekly delta). Each becomes a row in Phase 1's table.

## Phase 1 — Verify the report against code (gate: claims table)

Explore agents (read-only), in parallel:
- **Writer search**: every code path that writes the flagged column/table; ops repo (k8s/kustomize) for jobs the report blames; check whether those jobs are even deployed (kustomization comments!).
- **Caller search**: the frontend/clients that hit the endpoint; how often per user journey (effects, remounts, retries).
- **Local infra**: what stack can reproduce the *exact SQL text* (if an ORM/CMS emits it, that layer must be in the loop — a bare Postgres bench is the wrong stack).

Exit artifact: a table `claim | verdict | evidence (file:line / arithmetic)` in the plan or findings draft. Typical verdicts: wrong attribution, cumulative-vs-weekly confusion, exec time inflated by lock waits.

## Phase 2 — Bench loop (gate: symptom reproduced)

Scaffold: `bash scripts/scaffold.sh <ticket-slug> <perf-poc-shared-dir>` creates the dir with `README.md`, `run.sh` skeleton, `snapshot.sql` skeleton, `runs/`, and prints the `.gitignore` lines to add.

Required pieces of `run.sh` (see the reference run's `run.sh`):
1. **Preflight** records what is being measured: repo sha (+dirty), every feature flag / config that affects the path (read from the running container, not from memory), seed applied.
2. **Reset**: counters to zero, audit/revision tables truncated, `pg_stat_statements_reset()`, cache flush.
3. **Snapshot before/after** as one JSON row: statement stats matched by *pattern* (so a candidate's new statement shows up next to the old one), table sizes, HOT/non-HOT counters, Σ of the counter under test.
4. **Wait sampler**: `pg_stat_activity` every ~1 s → `waits.tsv` (`wait_event_type:wait_event` + query prefix + ungranted-lock count).
5. **Load**: URL list from `awk` (deterministic seed), `xargs -P $CONC curl`. Scenarios: `uniform` (spread over N entities) and `hotspot` (one entity). Optional `BLOCKER=row|index` background psql session to prove exec-time inflation.
6. **Diff → `runs/run-NN/results.md`** with a *lost-update check* (`expected = 200s`, `actual = Σ delta`, `lost`), per-200 side-effect counts, wait histogram, statements table. `Verdict:` stays blank — the script never judges.
7. `write_bench_log` appends one block per run to `bench-log.md`.

Pass criteria (write them in the plan **before** running): the exact SQL text appears; calls == requests; the symptom shape (mean/max/stddev, lock %) matches the report's; the side effects (revisions, fan-out SELECTs) are visible. If one is missing, fix the bench, not the story.

Standard H0 set: `uniform`, `hotspot`, `hotspot + row blocker`, `uniform + index blocker`, plus one run per config flag the report might blame (e.g. singleflight on/off).

Stack gotchas are findings too — record them in the bench README (stale schema snapshot, missing env vars, port clashes, validation rules on ids). The next person hits them otherwise.

## Phase 3 — Findings report (gate: user has read it)

`templates/findings.md` → `docs/<ticket-lower>/findings-<topic>.md`. Sections: one-line conclusion; runs table; the three questions (is it that SQL? does it queue? is exec time inflated by external locks?) each answered with run numbers; corrections to send back to the report author; **candidates listed by name only**; prod verification data to request from SRE; bench limitations.

Render HTML for people who won't open the repo: `python3 scripts/md2html.py findings.md > findings.html` (self-contained, no deps; tables and code blocks survive). Commit both.

**Stop here** until the user says which direction to POC. Save state to memory (runs done, gotchas, open questions).

## Phase 4 — POC the chosen design (gate: throughput + correctness numbers)

- Standalone program in `docs/perf-poc-shared/<slug>/poc-<design>/` with its own `go.mod` (or equivalent) pinned to the **same library versions the service uses**; talks to the local stack's DB/Redis directly.
- `run-poc.sh` mirrors `run.sh` (same reset/snapshot/sampler) but drives the POC binary; params for concurrency, scenario, interval, simulated pods, blocker.
- Must measure: throughput absorbed, request-side latency, DB statements per interval, **lost = increments − Σ delta**, leftovers in the store after drain, behaviour under the row blocker, crash-recovery (hand-plant a leftover batch and confirm replay).
- Also measure the simplest competing design (`-mode direct` in the reference POC) so "shorter" vs "removed" contention is a number, not an argument.
- Every surprise is a design rule for Phase 6 (reference: statement timeout must be shorter than the distributed-lock TTL — found only because a run double-counted).

Write `templates/poc-results.md` → `docs/<ticket-lower>/poc-<design>-results.md`.

## Phase 5 — Solution candidates (parallel with Phase 4)

Spawn one agent with the findings + repo pointers to write `templates/solution-candidates.md` → `docs/<ticket-lower>/solution-candidates.md`: every reasonable design (including ones better than the user's), same fields each (mechanism/files, what it fixes, consistency & durability, throughput bound, cache interaction, ops cost, LOC/blast radius, how the bench verifies it), comparison matrix, recommendation, open questions. Verify any gating claim it raises (e.g. "prod has no writer DSN") before relaying it.

Commit bench + POC + docs before moving on.

## Phase 6 — Implement (gate: bench passes through the real service)

- In the target repo, branch from the base the user names (ask if unclear; do not assume `develop`).
- Use the repo's spec workflow (`spec-kit`: `create-new-feature.sh` → spec.md, research.md, data-model.md, contracts/api.md, quickstart.md, plan.md with the constitution-check table, tasks.md, checklists/). research.md cites the Phase 3/4 run numbers; plan.md records the design rules from Phase 4.
- Feature-flag the new path, default off, byte-identical behaviour when off. Fallback to the old path when a dependency is missing.
- Unit tests through the repo's existing harness; inject external clients (Redis) via a package-level seam so handler tests need no server.
- **Verify with the same bench**: point the bench's compose override at the feature branch, flag on → expect the POC numbers; flag off → expect the H0 numbers. Both runs go in the PR description.
- Run the repo's agent-context update script, then **revert** any per-feature tech-stack lines it adds if the repo's constitution forbids stack repetition.
- Pre-existing failing tests: prove they fail on the untouched base (separate `git worktree`), list them in the PR.

## Phase 7 — Commit, push, PR (gate: PR URL)

- Two commits: `docs(<scope>): 📝 [TICKET] specify …` then `feat(<scope>): ✨ [TICKET] …` with the bench numbers in the body. No co-author trailers.
- Push; open the PR with the repo's MCP (Azure DevOps: `repo_pull_request_write`, target = the base branch the user named). Body: summary, changes, verification table (flag off vs on), deployment gate, rollback.

## Phase 8 — Self-review (gate: findings answered)

- Run `/ado-pr-code-review <PR URL>` (or the repo's equivalent). Fix every Medium/Minor that is a code defect in a `fix(<scope>): 🐛 [TICKET] … per self-review` commit, re-run the bench, push, reply on each thread with the sha. Leave product questions (rate limiting, dedupe semantics) open with a reply explaining why.
- Final message to the user: PR URL, numbers, what is left open, and the memory note.

## Artifacts checklist (what "done" looks like)

```
docs/<ticket-lower>/
  <report copies>.html            # inputs
  findings-<topic>.md / .html     # Phase 3
  poc-<design>-results.md         # Phase 4
  solution-candidates.md          # Phase 5
docs/perf-poc-shared/<ticket-slug>/
  README.md docker-compose.yml seed*.sql snapshot.sql run.sh [run-poc.sh] [poc-<design>/]
  runs/ bench-log.md              # gitignored
<target repo>/specs/NNN-<ticket-slug>/  + code + tests + PR
```

## Related skills

`ado-pr-code-review` (Phase 8), `generate-pr-notes` (Phase 7 body), `git-commit-conventional-strict`, `lieflat-charts` (if a charted HTML report is wanted instead of `md2html.py`), `diagram` (mechanism sketch for the findings).
