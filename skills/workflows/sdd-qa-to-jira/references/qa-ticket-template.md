# QA Sub-Ticket Template (BDD Format)

Use this template for each QA sub-ticket created by `/sdd-qa-to-jira`.

**Design principle:** Sub-tickets describe *what* to verify, not *how*. SDET owns the testing method, data setup, execution order, and approach. Do not add test steps.

---

## Jira Fields

| Field | Value |
|-------|-------|
| **Issue Type** | Sub-task |
| **Parent** | [Root ticket key, e.g. PROJ-101] |
| **Summary** | `[QA][SERVICE] [Short scenario name]` |
| **Assignee** | (unassigned — SDET claims) |
| **Priority** | Medium (adjust only if explicitly justified) |

---

## Description Body

```
## Scenario: [Human-readable scenario name]

**Given** [precondition — describe the system state or setup context, not test steps]
**When** [action or trigger — what the user or system does]
**Then** [expected observable outcome — what SDET can verify externally]

## Context
[One-liner referencing the requirement or spec section this scenario maps to.
Example: "From requirements.md §3.2: Notifications must be delivered within 5 seconds."]

## Notes
[Optional: known edge cases, data constraints, or environmental hints that affect this scenario.
Do NOT write test steps here. Write "what to watch for", not "how to test".]
```

---

## Example: Successful Delivery (Happy Path)

**Summary:** `[QA][NOTIFICATIONS] Successful notification delivery`

**Description:**
```
## Scenario: Successful notification delivery

**Given** a valid user with a confirmed email address and an active notification subscription
**When** a notification event is triggered by the system
**Then** the notification is delivered within 5 seconds and the event is recorded as "sent" in the audit log

## Context
From requirements.md §3.1: Notification delivery SLA is 5 seconds under normal load.

## Notes
Verify the audit log entry, not just the UI indicator — the UI may cache state.
```

---

## Example: Retry on Transient Failure (Edge Case)

**Summary:** `[QA][NOTIFICATIONS] Retry on transient SQS failure`

**Description:**
```
## Scenario: Retry on transient failure

**Given** SQS is temporarily unavailable (simulated)
**When** the notification producer attempts delivery
**Then** the consumer retries up to 5 times and eventually delivers the notification when SQS recovers

## Context
From plan.md §4.3: Max retry count = 5, exponential backoff.

## Notes
Check that retry count is visible in CloudWatch metrics. Each retry should be logged individually.
```

---

## Example: Dead-Letter Queue (Error Path)

**Summary:** `[QA][NOTIFICATIONS] Dead-letter queue on exhausted retries`

**Description:**
```
## Scenario: Dead-letter queue on exhausted retries

**Given** SQS is permanently unavailable for the duration of all retry attempts
**When** all 5 retry attempts are exhausted
**Then** the message is moved to the dead-letter queue, an alert is triggered, and the failure is logged with reason

## Context
From plan.md §4.4: DLQ handling — move to DLQ after max retries, fire alert via SNS.

## Notes
The SNS alert is the critical observable outcome here. DLQ message presence alone is not sufficient — confirm the alert fires.
```

---

## What NOT to Include

Avoid adding these to sub-tickets — they belong on the root ticket comment:

- PR URL
- Confluence design review page link
- Spec version or revision history
- Cross-ticket dependencies
- Sprint or story point estimates

Keep sub-tickets lean: scenario + context + notes only.
