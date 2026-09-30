# {{TICKET}} — {{symptom}} 修法候選

## 0. 問題與共同約束

| 約束 | 內容 | 影響誰 |
|---|---|---|
| {{sibling path that shares the handler}} | | |
| {{prod connectivity unknowns, e.g. writer DSN}} | | |
| {{cache layer}} | | |
| {{indexes on the hot column}} | | |
| {{response contract}} | | |

## 1..N. Candidates

For each candidate, the same fields:

- **Mechanism** (2–5 lines, exact files/functions touched)
- **Fixes / does not fix**: queueing / lost updates / side-effect growth / fan-out / hot-entity surge
- **Consistency & durability**: crash loss, store loss, staleness, exactly-once vs at-least-once, multi-replica correctness
- **Throughput ceiling** and what bounds it
- **Cache / audit interaction**
- **Ops / observability cost, new infra, config knobs**
- **Code footprint (LOC, new files) and blast radius**
- **Bench acceptance**: which scenario, which numbers

Cover at minimum: the user's design; a per-replica in-memory variant; the single-statement atomic variant; "keep the current layer but shrink the transaction"; separate storage for the hot counter; event stream / async worker outside the request path; store-as-source-of-truth; request-count reduction (client dedupe, server dedupe, sampling); DB-native tricks (lock_timeout, track_planning, fillfactor).

## Comparison matrix

| # | 候選 | 排隊 | 丟計數 | 副作用 | fan-out | surge | crash 損失 | 暫存損失 | 顯示延遲 | 新 infra | LOC | 前提 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Recommended path (tied to findings run numbers)

## Open questions to settle before implementation

## Unverified claims in this document
