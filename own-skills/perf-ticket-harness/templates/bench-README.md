# {{SLUG}}

Local, repeatable reproduction of `{{flagged SQL / symptom}}` (Jira {{TICKET}}).

**Which stack and why**: {{e.g. "the SQL under test is emitted by Directus, so this runs against the
service's own local stack (CMS + DB + cache), not the shared database-baseline postgres"}}.

## Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Override for the service's local stack: distinct host ports, `pg_stat_statements`, lock-wait logging, feature flags exposed as run params |
| `seed-*.sql` | Idempotent: extension, N bench entities, prod-shaped indexes |
| `snapshot.sql` | One JSON row of DB state (statement stats by pattern, side-effect table sizes, Σ counter, HOT stats) |
| `run.sh` | reset → snapshot → curl/xargs load (+ optional blocker) → snapshot → `runs/run-NN/results.md` + `bench-log.md`. Load generation is deliberately dumb; the DB-side numbers are the product |
| `run-poc.sh`, `poc-*/` | (Phase 4) standalone POC of the chosen design, same reset/snapshot/sampling |
| `runs/`, `bench-log.md` | generated, gitignored |

## Start the stack

```bash
{{compose command with the override}}
{{seed command}}
```

Quirks of the committed local stack worked around here (record every one; the next person hits them too):
- {{stale schema snapshot / missing env vars / port clash / id validation rules}}

## Run

```bash
SCENARIO=uniform N_REQS=300 CONC=10 NOTE=plumbing bash {{path}}/run.sh
```

| env | default | meaning |
|---|---|---|
| `SCENARIO` | `uniform` | `uniform`: spread over `N_ROOMS` entities. `hotspot`: every request on entity 1 |
| `N_ROOMS` / `N_REQS` / `CONC` | | entities seeded, total requests, concurrent curl workers |
| `BLOCKER` / `BLOCK_SEC` / `BLOCK_AT` | `none` | `row` = hold entity 1's row in another session; `index` = hold a table-level lock |
| `NOTE` | | free text for `bench-log.md` |
| {{feature flags}} | | recorded from the running container into `params.env` |

## What results.md answers

- Is the flagged SQL produced by the endpoint? (`UPDATE calls / 200` on the baseline)
- Lost updates: `expected (200s) − actual (Σ delta)`
- Lock queueing: wait-event histogram, max ungranted locks, statement mean/max/stddev
- Side effects per request: audit/revision rows, fan-out SELECT calls, HOT vs non-HOT

Pass criteria and the H0 protocol live in the plan / findings under `docs/{{ticket-lower}}/`.
