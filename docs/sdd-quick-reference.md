# SDD Quick Reference: Agent Skills Integration

A quick visual guide showing how your agent skills integrate with GitHub Spec-Kit's spec-kit native SDD workflow.

---

## The SDD Cycle

```mermaid
graph LR
    Constitution --> Specify
    Specify --> Plan
    Plan --> ReviewLoop["Review Loop"]
    ReviewLoop -->|feedback| Plan
    ReviewLoop --> Tasks
    Tasks --> ImplementPR["Implement & PR"]
    ImplementPR --> QAGate["QA Gate"]
    QAGate -->|bug found| Tasks
    QAGate --> Release
    Release --> Iterate
    Iterate --> Specify
```

---

## Workflow Phases & Skills

```mermaid
graph TD
    P1["Phase 1: Constitution
    skill: symlink-worktree-ignored-files"]

    P0["Phase 0 (Pre-Specify, optional)
    skill: confluence-prd-to-sdd-spec
    Confluence PRD → prd-source.md"]

    P2["Phase 2: Specify
    spec-kit specify
    → spec.md"]

    P3["Phase 3: Plan
    spec-kit plan
    → plan.md + requirements.md"]

    P4["Phase 4: Review Loop
    skill: sdd-tech-plan-to-confluence
    → Design Review page (Confluence)"]

    P5["Phase 5: Plan Finalized
    skill: sdd-tech-plan-to-confluence
    → Status: Approved (v1)"]

    P6["Phase 6: Tasks
    skill: confluence-tech-plan-to-jira
    → Jira root ticket + subtasks"]

    P7["Phase 7: Implement & PR
    skills: git-commit-conventional-strict
    api-spec-to-confluence
    generate-pr-notes"]

    P8["Phase 8: QA Gate
    skill: sdd-qa-to-jira
    → BDD sub-tickets for SDET"]

    P9["Phase 9: Iterate
    → back to Specify"]

    P1 --> P0
    P0 --> P2
    P2 --> P3
    P3 --> P4
    P4 -->|"feedback: refine plan.md"| P3
    P4 --> P5
    P5 --> P6
    P6 --> P7
    P7 --> P8
    P8 -->|"bug found"| P6
    P8 --> P9
    P9 --> P2
```

---

## Skill Usage by Phase

| Phase | Command | Purpose |
|-------|---------|---------|
| **Constitution** | `/symlink-worktree-ignored-files` | Set up dev environment with worktrees |
| **Pre-Specify (optional)** | `/confluence-prd-to-sdd-spec` | Fetch Confluence PRD → local `prd-source.md` |
| **Specify** | `spec-kit specify` | AI-assisted discussion → `spec.md` |
| **Plan** | `spec-kit plan` | AI technical planning → `plan.md` + `requirements.md` |
| **Review Loop (first publish)** | `/sdd-tech-plan-to-confluence` | Publish local files to Confluence design review page |
| **Review Loop (re-publish)** | `/sdd-tech-plan-to-confluence [page-id]` | Update page after refining plan based on feedback |
| **Plan Finalized** | `/sdd-tech-plan-to-confluence [page-id]` | Set status to Approved (v1) |
| **Tasks** | `/confluence-tech-plan-to-jira [page-id]` | Create Jira root ticket + subtasks from approved page |
| **Implement & PR** | `/git-commit-conventional-strict` | Semantic version commits |
| **Implement & PR** | `/api-spec-to-confluence` | Document committed API in Confluence |
| **Implement & PR** | `/generate-pr-notes` | Create pull request (phase exit condition) |
| **QA Gate** | `/sdd-qa-to-jira [root-ticket-key]` | RD explicit hand-off → BDD QA sub-tickets in Jira |

---

## Data Flow

```mermaid
graph LR
    LocalFiles["Local spec-kit files
    spec.md / plan.md / requirements.md"]

    Confluence["Confluence
    Design Review Page"]

    Jira["Jira
    Root ticket + impl subtasks"]

    PR["Pull Request"]

    JiraQA["Jira
    QA sub-tickets (BDD)"]

    SDET["SDET
    Owns execution method"]

    JiraBug["Jira
    Bug ticket → back to Tasks"]

    LocalFiles -->|"sdd-tech-plan-to-confluence"| Confluence
    Confluence -->|"confluence-tech-plan-to-jira"| Jira
    Jira -->|"implement & PR"| PR
    PR -->|"sdd-qa-to-jira"| JiraQA
    JiraQA --> SDET
    SDET -->|"bug found"| JiraBug
    JiraBug --> Jira
```

---

## Example: Notification Service Refactor

### Phase 1: Constitution

Review architecture standards in Confluence. Set up dev environment.

```bash
/symlink-worktree-ignored-files
```

### Phase 0 (Pre-Specify, optional)

PO hands off PRD from Confluence. RD imports it locally.

```bash
/confluence-prd-to-sdd-spec
# Fetches Confluence PRD → saves as prd-source.md
```

### Phase 2: Specify

```bash
spec-kit specify
# AI discussion with RD about notification system requirements
# Output: spec.md
# Contains: problem statement (legacy push service is unreliable, no retry logic),
#           goals, constraints
```

### Phase 3: Plan

```bash
spec-kit plan
# AI technical planning session
# Output: plan.md + requirements.md
# plan.md proposes: event-driven architecture with SQS, retry strategy, DLQ
# requirements.md lists: delivery guarantees, retry count, observability
```

### Phase 4 (First Publish — Review Loop)

```bash
/sdd-tech-plan-to-confluence
# Agent publishes spec.md + plan.md + requirements.md to Confluence
# Output: Design Review page (Status: Draft)
# Save the returned page ID: 987654321
```

Team reviews and adds three comments:
1. "Why not use an existing queue service instead of rolling our own?"
2. "What's the max retry count? Not specified."
3. "The dead-letter queue handling is unclear."

### Phase 4 (Review Iteration 1)

```bash
spec-kit plan
# RD incorporates feedback: queue options comparison, max retry=5, DLQ clarification

/sdd-tech-plan-to-confluence 987654321
# Agent updates page + appends revision history row
# v2 | 2026-03-04 | RD | Added queue options comparison, max retry=5, DLQ clarification
```

Team reviews v2. One comment remains: "Can we see the SQS cost estimate?"

### Phase 4 (Review Iteration 2)

```bash
spec-kit plan
# RD adds cost analysis note to plan.md

/sdd-tech-plan-to-confluence 987654321
# v3 | 2026-03-05 | RD | Added cost analysis reference for SQS option
# Team reaches consensus: go with SQS
```

### Phase 5: Plan Finalized

```bash
/sdd-tech-plan-to-confluence 987654321
# Ask agent: "Update the status to Approved (v1)"
# Page status: Approved (v1) — plan locked
```

### Phase 6: Tasks

```bash
/confluence-tech-plan-to-jira 987654321
# Creates:
# NOTIF-101: [PROJECT][NOTIFICATIONS] Notification Service Refactor (root)
# NOTIF-102: [RD] Set up SQS queue and IAM roles
# NOTIF-103: [RD] Implement notification producer
# NOTIF-104: [RD] Implement consumer with retry logic
# NOTIF-105: [RD] Implement DLQ handler and alerts
```

### Phase 7: Implement & PR

```bash
# Implement NOTIF-103
/git-commit-conventional-strict
# → feat(notifications): add notification producer with SQS

/api-spec-to-confluence
# → Documents the notification API endpoint in Confluence

/generate-pr-notes
# → PR #456 "Add notification producer"
# Phase exit condition: PR is open
```

### Phase 8: QA Gate

RD reviews PR #456, confirms implementation is ready for QA, then explicitly triggers the hand-off:

```bash
/sdd-qa-to-jira NOTIF-101
```

Agent derives BDD scenarios from all `*.md` files in the spec-kit folder, presents them for RD review, then creates:

```
NOTIF-101 (root)
  ├── NOTIF-102 ... NOTIF-105  (existing impl sub-tickets)
  ├── NOTIF-106: [QA][NOTIFICATIONS] Successful notification delivery
  ├── NOTIF-107: [QA][NOTIFICATIONS] Retry on transient failure
  ├── NOTIF-108: [QA][NOTIFICATIONS] Dead-letter queue on exhausted retries
  └── NOTIF-109: [QA][NOTIFICATIONS] Duplicate prevention
```

SDET claims sub-tickets and owns execution method and order.

### Phase 9: Iterate

New requirement arrives. Cycle back to Specify.

---

## Key Points

| Concern | Detail |
|---------|--------|
| **Source of truth** | Local spec-kit files (`spec.md`, `plan.md`, `requirements.md`) |
| **Confluence role** | Shared review surface — team comments, does not edit |
| **Jira structure** | Root ticket + impl sub-tickets (Phase 6) + QA sub-tickets (Phase 8) |
| **QA hand-off** | RD explicit decision after PR is open — not automatic |
| **SDET owns** | Execution method, test order, and approach for BDD scenarios |

---

## Quick Start

```bash
# 1. Set up Atlassian MCP
./.agent-settings/mcps/install-atlassian-mcp.sh --agent claude

# 2. Import skills
./.agent-settings/skills/import-skills.sh claude

# 3. Set up dev environment
/symlink-worktree-ignored-files

# 4. (Optional) Import PRD from Confluence
/confluence-prd-to-sdd-spec

# 5. Specify
spec-kit specify

# 6. Plan
spec-kit plan

# 7. Publish for review
/sdd-tech-plan-to-confluence

# 8. After team feedback — re-publish with page ID
/sdd-tech-plan-to-confluence [page-id]

# 9. Finalize plan
# /sdd-tech-plan-to-confluence [page-id]  (ask: "Update status to Approved (v1)")

# 10. Create Jira tickets
/confluence-tech-plan-to-jira [page-id]

# 11. Implement & commit
/git-commit-conventional-strict

# 12. Document API
/api-spec-to-confluence

# 13. Create PR (phase exit condition)
/generate-pr-notes

# 14. QA hand-off (after PR is open — RD explicit decision)
/sdd-qa-to-jira [root-ticket-key]
```

---

## Resources

- [Full Workflow Guide](./sdd-workflow-spec-kit-native.md)
- [SDD Skills Map](./sdd-skills-map.md)
- [GitHub Spec-Kit](https://github.com/github/spec-kit)
- [Agent Skills README](../README.md)
- [MCP Setup Guide](../.agent-settings/mcps/README.md)
- [Skills Management](../.agent-settings/skills/README.md)
