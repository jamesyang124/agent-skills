# SDD Workflow: Spec-Kit Native Path

This document describes the **spec-kit native** variant of the SDD workflow, where spec-kit CLI handles all AI-assisted phases locally and Confluence is used as a **shared review surface** — not the source of truth.

> This is the canonical SDD workflow document covering the spec-kit native path where local files are the source of truth.

---

## Overview

| Concern | Owner |
|---------|-------|
| **Source of truth** | Local spec-kit files (`spec.md`, `plan.md`, `requirements.md`) |
| **AI discussion phases** | spec-kit CLI (runs locally with the RD) |
| **Shared review surface** | Confluence (published by agent skills) |
| **Team feedback channel** | Confluence comments → RD refines local files → re-publishes |
| **Task tracking** | Jira (created from finalized Confluence page) |

**The feedback loop is explicit:** team members review the Confluence page and add comments. They do **not** edit the page. The lead RD takes the comments back to spec-kit, refines `plan.md` / `requirements.md`, then re-runs `/sdd-tech-plan-to-confluence` to publish the updated version. This repeats until the team reaches consensus.

---

## Architecture Diagram

```mermaid
graph TB
    subgraph "👤 PO / PM"
        PRD[Product Requirements Doc]
    end

    subgraph "🧑‍💻 RD — Local spec-kit"
        PRDLOCAL["📄 prd-source.md
(local import)"]
        SPECIFY["spec-kit specify
(AI discussion)"]
        SPECMD["📄 spec.md
(source of truth)"]
        PLAN["spec-kit plan
(AI technical planning)"]
        PLANMD["📄 plan.md
(source of truth)"]
        REQMD["📄 requirements.md
(source of truth)"]
        REFINE["Refine local files
based on feedback"]
    end

    subgraph "🤖 Claude Code Agent"
        PRDIMPORT["/confluence-prd-to-sdd-spec skill"]
        P2W["/sdd-tech-plan-to-confluence skill"]
        C2J["/confluence-tech-plan-to-jira skill"]
        IMPL["Implementation Skills
(commit, PR, API docs)"]
        QAGATE["/sdd-qa-to-jira skill"]
    end

    subgraph "👥 Technical Staff (Reviewers)"
        REVIEWPAGE["☁️ Design Review Page
(Confluence — shared view)"]
        APPROVED["☁️ Design Review Page
Status: Approved (v1)"]
        FEEDBACK["💬 Comments & Feedback"]
    end

    subgraph "🎫 Jira"
        TICKETS["Root ticket + subtasks"]
        QATKT["QA sub-tickets
(BDD scenarios)"]
    end

    subgraph "🧪 SDET"
        SDETEXEC["Verify scenarios
(owns method & order)"]
        RELEASE["✅ Release ready"]
    end

    PRD --> PRDIMPORT
    PRDIMPORT --> PRDLOCAL
    PRDLOCAL --> SPECIFY
    SPECIFY --> SPECMD
    SPECMD --> PLAN
    PLAN --> PLANMD
    PLAN --> REQMD

    PLANMD --> P2W
    REQMD --> P2W
    SPECMD --> P2W
    P2W --> REVIEWPAGE

    REVIEWPAGE --> FEEDBACK
    FEEDBACK -->|"RD takes feedback"| REFINE
    REFINE --> PLANMD
    REFINE --> REQMD
    PLANMD --> P2W
    REQMD --> P2W

    REVIEWPAGE -->|"consensus reached"| APPROVED
    APPROVED --> C2J
    C2J --> TICKETS
    TICKETS --> IMPL
    IMPL --> PR["PR created
(/generate-pr-notes)"]
    PR --> QAGATE
    QAGATE --> QATKT
    QATKT --> SDETEXEC
    SDETEXEC -->|"all pass"| RELEASE
    SDETEXEC -->|"bug found"| TICKETS
```

---

## Sequence Diagram

```mermaid
sequenceDiagram
    actor PO as PO / PM
    actor RD as Lead RD
    participant SK as SpecKit CLI
    participant Agent as Claude Code Agent
    participant CF as Confluence
    participant Jira as Jira
    actor SDET as SDET

    rect rgb(225, 245, 255)
        Note over PO,Jira: 1. CONSTITUTION
        RD->>CF: Document architecture standards, API conventions
    end

    rect rgb(255, 244, 225)
        Note over PO,Jira: 2. SPECIFY — spec-kit specify
        PO->>RD: Share PRD
        RD->>SK: spec-kit specify
        SK-->>RD: AI-assisted discussion
        SK-->>RD: spec.md (committed locally)
    end

    rect rgb(255, 235, 210)
        Note over PO,Jira: 3. PLAN — spec-kit plan
        RD->>SK: spec-kit plan
        SK-->>RD: AI-assisted technical planning
        SK-->>RD: plan.md + requirements.md (committed locally)
    end

    rect rgb(210, 230, 255)
        Note over PO,Jira: 4. SPECIFY→PLAN BRIDGE — /sdd-tech-plan-to-confluence (first publish)
        RD->>Agent: /sdd-tech-plan-to-confluence
        Agent->>Agent: Read spec.md, plan.md, requirements.md
        Agent->>Agent: Map content to design review template
        Agent->>CF: Create page "Technical Plan: [Feature]"
        CF-->>Agent: Page URL + ID
        Agent-->>RD: URL + reminder to save page ID
        RD->>PO: Share review link with team
    end

    rect rgb(255, 245, 210)
        Note over PO,Jira: 5. REVIEW LOOP (iterate until consensus)
        loop Team review cycle
            PO->>CF: Read design review page
            PO->>CF: Add comments / feedback
            CF-->>RD: RD reads comments
            RD->>SK: spec-kit plan (refine based on feedback)
            SK-->>RD: Updated plan.md + requirements.md
            RD->>Agent: /sdd-tech-plan-to-confluence [page-id]
            Agent->>Agent: Re-read updated local files
            Agent->>CF: Update page (append Revision History row)
            CF-->>Agent: Updated page URL
            Agent-->>RD: Confirmed update
        end
    end

    rect rgb(210, 255, 225)
        Note over PO,Jira: 6. PLAN FINALIZED
        RD->>Agent: Update page status to "Approved (v1)"
        Agent->>CF: Update status field
        CF-->>RD: Plan v1 locked
    end

    rect rgb(225, 255, 225)
        Note over PO,Jira: 7. TASKS — /confluence-tech-plan-to-jira
        RD->>Agent: /confluence-tech-plan-to-jira [page-id]
        Agent->>CF: Fetch approved design review page
        CF-->>Agent: Page content
        Agent->>Jira: Create root ticket + subtasks
        Jira-->>Agent: Ticket keys
        Agent-->>RD: Ticket keys (e.g. PROJ-101, PROJ-102)
    end

    rect rgb(200, 245, 215)
        Note over PO,Jira: 8. IMPLEMENT & PR
        RD->>Agent: Implement, commit, API docs
        Note over Agent: git-commit-conventional-strict<br/>api-spec-to-confluence
        RD->>Agent: /generate-pr-notes
        Agent-->>RD: PR created (PR URL)
    end

    rect rgb(255, 225, 245)
        Note over PO,SDET: 9. QA GATE — /sdd-qa-to-jira
        RD->>RD: Confirm PR is open and implementation is ready
        RD->>Agent: /sdd-qa-to-jira [root-ticket-key]
        Agent->>Agent: Read all *.md files in spec-kit folder
        Agent->>Agent: Derive BDD scenarios (happy paths, edge cases, error paths)
        Agent-->>RD: Present proposed scenarios for review
        RD-->>Agent: Confirm (or adjust) scenarios
        Agent->>Jira: Add QA sub-tickets to existing root ticket
        Jira-->>Agent: Sub-ticket keys
        Agent-->>RD: Ticket keys + QA hand-off summary
        RD->>SDET: Share QA sub-tickets for execution
    end
```

---

## Phase-by-Phase Breakdown

### Phase 1: Constitution

**Unchanged from the standard SDD workflow.** Establish project standards, architecture guidelines, and API conventions in Confluence before any feature work begins.

**Skills:** `symlink-worktree-ignored-files`
**MCP:** Atlassian (Confluence)

---

### Phase 2: Specify — `spec-kit specify`

The RD runs spec-kit locally with the PRD as input. spec-kit facilitates an AI conversation to clarify requirements and produces `spec.md`.

```bash
spec-kit specify
```

**Output:** `spec.md` (local — source of truth)
**No agent skill needed** at this phase.

---

### Phase 3: Plan — `spec-kit plan`

The RD runs spec-kit to do AI-assisted technical planning based on `spec.md`. This produces `plan.md` and `requirements.md`.

```bash
spec-kit plan
```

**Output:** `plan.md` + `requirements.md` (local — source of truth)
**No agent skill needed** at this phase.

---

### Phase 4: Specify→Plan Bridge — `/sdd-tech-plan-to-confluence` (first publish)

Once `plan.md` and `requirements.md` exist locally, the agent skill publishes them to Confluence as a **design review page**.

```bash
/sdd-tech-plan-to-confluence
```

**Input:** `spec.md`, `plan.md`, `requirements.md` (local files)
**Output:** Confluence design review page (`Status: Draft`)

The agent:
1. Reads all three local files.
2. Maps content to the design review template (no content invention — gaps become `[TODO]`).
3. Searches for an existing page, or creates a new one.
4. Appends the "source of truth" notice directing reviewers to comment rather than edit.
5. Returns the page URL and reminds the RD to save the page ID for future re-runs.

> **Share the page link with your team for review.** The page title format is: `Technical Plan: [Feature Name]`

---

### Phase 5: Review Loop

This is the iterative heart of the spec-kit native workflow.

```
Team reviews Confluence page
    ↓
Team adds comments (NOT page edits)
    ↓
RD reads comments, takes them to spec-kit
    ↓
spec-kit plan (refine plan.md + requirements.md)
    ↓
/sdd-tech-plan-to-confluence [page-id]  ← re-publish with page ID
    ↓
Confluence page updated + Revision History row added
    ↓
Repeat until consensus
```

**Key rules:**
- Team members **comment** on the Confluence page. They do **not** edit it.
- The RD **never** manually edits the Confluence page. All refinements happen in spec-kit, then re-published.
- Each re-publish appends a row to the Revision History table on the page.
- The page Status stays `Draft` or `Under Review` during this loop.

**Re-run command:**
```bash
/sdd-tech-plan-to-confluence [page-id]
```
Passing the page ID directly skips the search step and ensures the correct page is updated.

---

### Phase 6: Plan Finalized

When the team reaches consensus, the RD marks the page as approved:

```bash
/sdd-tech-plan-to-confluence [page-id]
# Then ask the agent: "Update the status to Approved (v1)"
```

**Status progression:**
```
Draft  →  Under Review  →  Approved (v1)
```

Once `Approved (v1)`, the plan is locked as v1. The local `plan.md` and `requirements.md` are the canonical reference. The Confluence page is now the stable input for Jira ticket creation.

---

### Phase 7: Tasks — `/confluence-tech-plan-to-jira`

With the design review page approved, create Jira tickets from it:

```bash
/confluence-tech-plan-to-jira [page-id]
```

**Input:** Approved Confluence design review page
**Output:** Jira root ticket + subtasks

---

### Phase 8: Implement & PR

Same as the standard SDD workflow. The PR creation is the **explicit exit condition** for this phase — it signals that implementation is committed and reviewable.

```bash
# Commit code
/git-commit-conventional-strict

# Document implemented API
/api-spec-to-confluence

# Create pull request (phase exit condition)
/generate-pr-notes
```

---

### Phase 9: QA Gate — `/sdd-qa-to-jira`

With the PR open, the RD makes a **conscious hand-off decision** to signal the implementation is ready for QA. This is not automatic — the RD decides when the implementation is stable enough, even if the PR already exists.

```bash
/sdd-qa-to-jira [root-ticket-key]
```

**Trigger:** PR is open (after `/generate-pr-notes`), RD explicitly initiates hand-off.
**Input:** All `*.md` files in the spec-kit feature folder + existing root Jira ticket key (from Phase 7).
**Output:** QA sub-tickets added to the existing root ticket (BDD scenario format).

The skill derives end-to-end BDD scenarios from spec-kit files, presents them to the RD for review, then creates sub-tickets under the same root ticket created in Phase 7:

```
[PROJ-101] [PROJECT][SERVICE] Feature Name    ← existing root from Phase 7
  ├── [PROJ-102] [RD] Implement X             ← existing impl sub-tickets
  ├── [PROJ-103] [RD] Implement Y
  ├── [PROJ-104] [QA] [SCENARIO] Happy path   ← NEW: BDD QA sub-tickets
  ├── [PROJ-105] [QA] [SCENARIO] Edge case
  └── [PROJ-106] [QA] [SCENARIO] Error path
```

**Sub-ticket format (BDD — non-prescriptive):**
Sub-tickets describe *what* to verify, not *how*. SDET owns the testing method, order, and approach.

```
Title: [QA][SERVICE] [Short scenario name]
Type: Sub-task
Parent: Root ticket

## Scenario: [Human-readable name]

**Given** [precondition / system state]
**When** [action or trigger]
**Then** [expected observable outcome]

## Context
[One-liner from spec.md or requirements.md]

## Notes
[Optional: known edge cases, data setup hints]
```

**Key design principle:** Scenarios are derived from `prd-source.md`, `spec.md`, `requirements.md`, `plan.md`, and any other `*.md` files in the feature folder (implementation notes, ADRs, discovery notes). The broader the input, the richer the edge cases.

---

## Skill Matrix

| SDD Phase | spec-kit CLI Action | Agent Skill | MCP Tool | Output |
|-----------|-------------------|-------------|----------|--------|
| **Constitution** | — | `symlink-worktree-ignored-files` | Atlassian | Dev environment ready |
| **Specify** | `spec-kit specify` | — | — | `spec.md` (local) |
| **Plan** | `spec-kit plan` | — | — | `plan.md` + `requirements.md` (local) |
| **Plan → Review** | — | `sdd-tech-plan-to-confluence` | Atlassian | Design review page in Confluence |
| **Review Loop** | `spec-kit plan` (refine) | `sdd-tech-plan-to-confluence` (re-publish) | Atlassian | Updated page + Revision History |
| **Plan Finalized** | — | `sdd-tech-plan-to-confluence` (status update) | Atlassian | Page: Approved (v1) |
| **Tasks** | — | `confluence-tech-plan-to-jira` | Atlassian | Jira tickets |
| **Implement** | — | `git-commit-conventional-strict` | — | Semantic commits |
| **Implement** | — | `api-spec-to-confluence` | Atlassian | API docs in Confluence |
| **Implement** | — | `generate-pr-notes` | — | Pull request |
| **QA Gate** | — | `sdd-qa-to-jira` | Atlassian | QA sub-tickets (BDD scenarios) in Jira |

---

## Complete Worked Example

**Scenario:** Notification Service Refactor

### Step 1: Constitution
Review architecture standards in Confluence. Set up dev environment with `/symlink-worktree-ignored-files`.

### Step 2: Specify
```bash
spec-kit specify
# AI conversation with RD about notification system requirements
# Output: spec.md
```
`spec.md` contains: problem statement (legacy push service is unreliable, no retry logic), goals, constraints.

### Step 3: Plan
```bash
spec-kit plan
# AI technical planning session
# Output: plan.md, requirements.md
```
`plan.md` proposes: event-driven architecture with a queue, retry strategy, dead-letter queue. Identifies trade-offs between polling vs push approaches.
`requirements.md` lists: delivery guarantees, retry count, observability requirements.

### Step 4: First Publish
```bash
/sdd-tech-plan-to-confluence
```
Agent output:
```
✅ Design review page published:
https://your-org.atlassian.net/wiki/spaces/ENG/pages/987654321

Status: Draft

📌 Save your page ID: 987654321
   Next time: /sdd-tech-plan-to-confluence 987654321
```
RD shares link with team. Team reviews. Three comments come back:
1. "Why not use an existing queue service instead of rolling our own?"
2. "What's the max retry count? Not specified."
3. "The dead-letter queue handling is unclear."

### Step 5: Review Iteration 1
```bash
spec-kit plan
# RD incorporates feedback:
# - Added comparison of queue options (SQS vs RabbitMQ vs custom)
# - Added explicit max retry = 5 in requirements
# - Clarified DLQ handling process in plan

/sdd-tech-plan-to-confluence 987654321
```
Agent updates page, adds revision history row:
```
v2 | 2026-03-04 | RD | Added queue options comparison, max retry=5, DLQ clarification
```

Team reviews v2. One remaining comment: "Can we see the SQS cost estimate?"

### Step 6: Review Iteration 2
```bash
spec-kit plan
# RD adds cost analysis note to plan.md (links to separate cost spreadsheet)

/sdd-tech-plan-to-confluence 987654321
```
Agent updates page, adds revision history row:
```
v3 | 2026-03-05 | RD | Added cost analysis reference for SQS option
```
Team: consensus reached. Go with SQS.

### Step 7: Finalize Plan
```bash
/sdd-tech-plan-to-confluence 987654321
# Agent: "Update status to Approved (v1)"
```
Page status: `Approved (v1)`. Plan locked.

### Step 8: Create Jira Tickets
```bash
/confluence-tech-plan-to-jira 987654321
```
Agent creates:
- NOTIF-101: Set up SQS queue and IAM roles
- NOTIF-102: Implement notification producer
- NOTIF-103: Implement consumer with retry logic
- NOTIF-104: Implement DLQ handler and alerts
- NOTIF-105: Write integration tests

### Step 9: Implement
```bash
# Implement NOTIF-102
/git-commit-conventional-strict
# → feat(notifications): ✨ add notification producer with SQS

/api-spec-to-confluence
# → Documents the notification API endpoint

/generate-pr-notes
# → PR #456 "Add notification producer"
```

### Step 10: QA Gate
RD reviews PR #456, confirms the implementation is ready for QA, then explicitly triggers the hand-off:
```bash
/sdd-qa-to-jira NOTIF-101
```
Agent output:
```
Proposed QA scenarios (derived from spec.md, requirements.md, plan.md, impl-notes.md):

1. [SCENARIO] Successful notification delivery
   Given a valid user with a confirmed email
   When a notification event is triggered
   Then the notification is delivered within 5 seconds and marked as sent

2. [SCENARIO] Retry on transient failure
   Given SQS delivery fails on first attempt
   When the consumer retries up to 5 times
   Then the notification is eventually delivered and retry count is logged

3. [SCENARIO] Dead-letter queue on exhausted retries
   Given all 5 retry attempts fail
   When the message is moved to the DLQ
   Then an alert is fired and the event is logged with failure reason

4. [SCENARIO] Duplicate prevention
   Given a notification event is received twice (at-least-once delivery)
   When the consumer processes the second delivery
   Then the notification is not sent twice (idempotency check)

Shall I create these as Jira sub-tickets under NOTIF-101? (You can edit before confirming.)
```
RD confirms. Agent creates:
```
✅ QA sub-tickets created under NOTIF-101:
- NOTIF-106: [QA][NOTIFICATIONS] Successful notification delivery
- NOTIF-107: [QA][NOTIFICATIONS] Retry on transient failure
- NOTIF-108: [QA][NOTIFICATIONS] Dead-letter queue on exhausted retries
- NOTIF-109: [QA][NOTIFICATIONS] Duplicate prevention

Root ticket NOTIF-101 updated with QA hand-off note.
SDET can now claim and execute in any order.
```

---

## Comparison: Confluence-Centric vs Spec-Kit Native

| Aspect | Confluence-Centric | Spec-Kit Native |
|--------|-------------------|-----------------|
| **Where specs live** | Confluence | Local files (`spec.md`, `plan.md`) |
| **AI discussion** | Via agent on Confluence content | Via spec-kit CLI locally |
| **Source of truth** | Confluence page | Local spec-kit files |
| **Confluence role** | Primary workspace | Shared review surface |
| **Team edits page?** | Yes (collaborative editing) | No (comment-only) |
| **Skill at Specify→Plan** | `/confluence-prd-to-sdd-spec` | `/sdd-tech-plan-to-confluence` |
| **Re-publishing** | Re-run `/confluence-prd-to-sdd-spec` | Re-run `/sdd-tech-plan-to-confluence [page-id]` |

---

## References

- [SDD Skills Map](./sdd-skills-map.md)
- [sdd-tech-plan-to-confluence Skill](./../.agent-settings/skills/sdd-tech-plan-to-confluence/SKILL.md)
- [GitHub Spec-Kit Repository](https://github.com/github/spec-kit)
- [Spec-Driven Development Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)
