# SDD Skills & MCP Mapping

Visual reference showing exactly which skills and MCP tools to use at each SDD phase.

---

## 🔄 The Complete Cycle

```
╔════════════════════════════════════════════════════════════════╗
║                  SPEC-DRIVEN DEVELOPMENT CYCLE                 ║
╚════════════════════════════════════════════════════════════════╝


    ┌─────────────────────────────────────────────────────┐
    │                 1. CONSTITUTION                     │
    │              (Project Standards)                    │
    │                                                     │
    │  Skills:  • symlink-worktree-ignored-files         │
    │  MCP:     • Atlassian → Confluence                 │
    └─────────────────────┬───────────────────────────────┘
                          │
                          ↓
    ┌─────────────────────────────────────────────────────┐
    │          0→2. PRE-SPECIFY  (optional)               │
    │         PO hands off PRD from Confluence            │
    │                                                     │
    │  Skills:  • confluence-prd-to-spec                     │
    │               Confluence PRD → prd-source.md       │
    │  MCP:     • Atlassian → Fetch PRD page             │
    └─────────────────────┬───────────────────────────────┘
                          │
                          ↓
    ┌─────────────────────────────────────────────────────┐
    │                   2. SPECIFY                        │
    │              (Define Requirements)                  │
    │                                                     │
    │  spec-kit specify  (ref. prd-source.md if fetched) │
    │  MCP:     • claude-mem → Remember patterns         │
    └──────────────────────┬──────────────────────────────┘
                           │
                           │  [spec-kit native path]
                           ↓
    ┌─────────────────────────────────────────────────────┐
    │              2→3. SPECIFY → PLAN                    │
    │         (spec-kit plan → publish for review)        │
    │                                                     │
    │  spec-kit plan                                     │
    │  → plan.md + requirements.md (local)               │
    │  Skill:  • sdd-tech-plan-to-confluence             │
    │              Local files →                         │
    │              Design Review page + Review Loop      │
    │  MCP:    • Atlassian → Create/update review page   │
    └─────────────────────┬───────────────────────────────┘
                          │
                          ↓
    ┌─────────────────────────────────────────────────────┐
    │                    3. PLAN                          │
    │              (Review & Refine)                      │
    │                                                     │
    │  Skills:  • sdd-tech-plan-to-confluence (re-pub)   │
    │  MCP:     • Atlassian → Confluence                 │
    │           • claude-mem → Track decisions           │
    └─────────────────────┬───────────────────────────────┘
                          │
                          ↓
    ┌─────────────────────────────────────────────────────┐
    │                   4. TASKS                          │
    │             (Execute & Deliver)                     │
    │                                                     │
    │  4a. Create Tasks:                                 │
    │      Skills:  • confluence-tech-plan-to-jira-tickets         │
    │      MCP:     • Atlassian → Jira                   │
    │                                                     │
    │  4b. Implement:                                    │
    │      Skills:  • git-commit-conventional-strict     │
    │               • api-spec-to-confluence             │
    │                   Document committed API code      │
    │               • generate-pr-notes                  │
    │      MCP:     • Atlassian → Confluence (API docs)  │
    │               • claude-mem → Track patterns        │
    └─────────────────────┬───────────────────────────────┘
                          │
                          ↓
    ┌─────────────────────────────────────────────────────┐
    │                  5. ITERATE                         │
    │             (Review & Improve)                      │
    │                                                     │
    │  MCP:     • Atlassian → Jira + Confluence sync     │
    │           • claude-mem → Store learnings           │
    │                                                     │
    │  Next:    → New features? Go to SPECIFY            │
    │           → Tech changes? Go to PLAN               │
    │           → Bug fixes? Go to TASKS                 │
    └─────────────────────┬───────────────────────────────┘
                          │
                          └───────────┐
                                      │
                   ┌──────────────────┼──────────────────┐
                   │                  │                  │
                   ↓                  ↓                  ↓
              SPECIFY              PLAN              TASKS
```

---

## 📋 Skill Invocation Guide

### Constitution Phase
```bash
# Setup development environment
/symlink-worktree-ignored-files

# Store standards
# Use: MCP Atlassian to create Confluence pages
```

### Pre-Specify Phase (PO handoff)
```bash
# Import PO's Confluence PRD as a local source file for spec-kit
/confluence-prd-to-spec

# Fetches PRD from Confluence → Saves as prd-source.md
# RD then references prd-source.md when running spec-kit specify
```

### Specify Phase
```bash
# Run spec-kit with prd-source.md as context (spec-kit native)
spec-kit specify

# Or write spec directly in Confluence (Confluence-centric path)
# Use: MCP Atlassian → Create Confluence page
```

### Specify → Plan Transition
```bash
# Publish local spec-kit artifacts to Confluence for team review
/sdd-tech-plan-to-confluence

# Use: MCP Atlassian → Create/update Design Review page
```

### Plan Phase
```bash
# Re-publish if spec-kit files updated after team feedback
/sdd-tech-plan-to-confluence [page-id]

# Document architecture decisions
# Use: MCP Atlassian → Confluence
# Use: MCP claude-mem → Store decisions
```

### Tasks Phase
```bash
# Step 1: Create Jira tickets
/confluence-tech-plan-to-jira-tickets

# Step 2: Implement code

# Step 3: Commit changes
/git-commit-conventional-strict

# Step 4: Generate API documentation from committed code
/api-spec-to-confluence

# Step 5: Create pull request
/generate-pr-notes
```

### Iterate Phase
```bash
# Sync status across tools
# Use: MCP Atlassian → Update Jira & Confluence

# Record learnings
# Use: MCP claude-mem → Store context
```

---

## 🎯 Phase-Skill Matrix

| SDD Phase | Primary Tool | Purpose | Output |
|-----------|-------------|---------|---------|
| **Constitution** | `symlink-worktree-ignored-files` | Environment setup | Dev environment ready |
| **Constitution** | Atlassian MCP | Document standards | Confluence pages |
| **Pre-Specify (PO handoff)** | `confluence-prd-to-spec` | Fetch PO's Confluence PRD → local `prd-source.md` for spec-kit | `prd-source.md` (local) |
| **Specify** | Atlassian MCP + claude-mem | Write spec & remember | Confluence pages + Context |
| **Specify → Plan (spec-kit native)** | `sdd-tech-plan-to-confluence` | Publish local spec-kit files to Confluence for team review | Design Review page in Confluence |
| **Plan** | Atlassian MCP + claude-mem | Document & track | Plans + Decisions |
| **Tasks** | `api-spec-to-confluence` | Document implemented API | API docs in Confluence |
| **Tasks** | `confluence-tech-plan-to-jira-tickets` | Task creation | Jira tickets |
| **Tasks** | `git-commit-conventional-strict` | Version control | Semantic commits |
| **Tasks** | `generate-pr-notes` | PR documentation | Pull request notes |
| **Iterate** | Atlassian MCP | Sync status | Updated tickets/docs |
| **Iterate** | claude-mem MCP | Learn & improve | Stored context |

---

## 🔍 Decision Tree: Which Tool to Use?

```
Need to... ?
│
├─> Set up development environment?
│   └─> Use: /symlink-worktree-ignored-files
│
├─> Import a PO's Confluence PRD as a local spec-kit source file?
│   └─> Use: /confluence-prd-to-spec
│
├─> Publish spec-kit local artifacts to Confluence for team review?
│   └─> Use: /sdd-tech-plan-to-confluence
│
├─> Create work tickets from specs?
│   └─> Use: /confluence-tech-plan-to-jira-tickets
│
├─> Document API from implemented code?
│   └─> Use: /api-spec-to-confluence
│
├─> Commit code changes?
│   └─> Use: /git-commit-conventional-strict
│
├─> Create a pull request?
│   └─> Use: /generate-pr-notes
│
├─> Store/retrieve documentation?
│   └─> Use: MCP Atlassian (Confluence)
│
├─> Manage tasks/tickets?
│   └─> Use: MCP Atlassian (Jira)
│
└─> Remember context/decisions?
    └─> Use: MCP claude-mem
```

---

## 💼 Real-World Example

**Task:** Add user authentication feature

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Phase 1: CONSTITUTION                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Action: Review security standards
  Tool:   MCP Atlassian
  Query:  "Show me authentication standards from Confluence"
  Result: Retrieved coding standards for auth


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Phase 2: SPECIFY                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Action: Define authentication requirements
  Tool:   MCP Atlassian
  Input:  Requirements doc
  Result: Confluence page "Auth Specification v1"
          Page ID: 123456789


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Phase 2→3: SPECIFY → PLAN                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Action: Generate Tech Design Document from the spec
  Tool:   /confluence-prd-to-spec
  Input:  Confluence page "Auth Specification v1" (ID: 123456789)
  Result: Tech Design Document in Confluence
          • Architecture: JWT + refresh token strategy
          • Components: AuthService, TokenStore, Middleware
          • DB changes: user_sessions table
          • Implementation plan: 3 phases


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Phase 3: PLAN                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Action: Refine TDD based on team review
  Tool:   MCP Atlassian + claude-mem
  Result: Finalized Tech Design Document in Confluence


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Phase 4: TASKS                                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Step 4a: Create Tasks
    Tool:   /confluence-tech-plan-to-jira-tickets
    Input:  Confluence page ID: 123456789
    Result: Created Jira tickets
            • AUTH-101: Implement JWT generation
            • AUTH-102: Add auth middleware
            • AUTH-103: Write integration tests

  Step 4b: Implement AUTH-101
    Tool:   (Manual coding)
    Result: Implemented JWT generation

  Step 4c: Commit Changes
    Tool:   /git-commit-conventional-strict
    Result: feat(auth): ✨ add JWT token generation

  Step 4d: Generate API documentation from committed code
    Tool:   /api-spec-to-confluence
    Input:  src/routes/auth.js (committed handler)
    Result: API documentation in Confluence
            • JWT endpoint contract
            • Request/response schemas
            • Error handling

            Implements JWT signing with RS256 algorithm

            Closes AUTH-101

  Step 4d: Create PR
    Tool:   /generate-pr-notes
    Result: PR #789 "Add JWT Authentication"
            • Summary: 3 files changed
            • Links to AUTH-101, AUTH-102, AUTH-103
            • Test plan included


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Phase 5: ITERATE                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Action: Update Jira status
  Tool:   MCP Atlassian
  Result: AUTH-101: Done
          AUTH-102: In Progress
          AUTH-103: To Do

  Action: Document learnings
  Tool:   MCP Atlassian
  Input:  "Learned: RS256 requires key pair management"
  Result: Added to Confluence "Auth Lessons Learned"

  Action: Store decision
  Tool:   MCP claude-mem
  Input:  "Decision: Use RS256 over HS256 for better security"
  Result: Context stored for future auth work

  Next: Bug reported → Go back to TASKS for fix
```

---

## 🚦 Status Indicators

Use these to track your progress through the SDD cycle:

```
□ Constitution: Standards documented
  └─> Tools ready: symlink-worktree-ignored-files, Atlassian MCP

□ Specify: Requirements defined
  └─> Specs in Confluence: api-spec-to-confluence, Atlassian MCP

□ Plan: Technical approach documented
  └─> Plans in Confluence: api-spec-to-confluence, Atlassian MCP

□ Tasks: Work broken down and assigned
  └─> Tickets created: confluence-tech-plan-to-jira-tickets, Atlassian MCP

□ Implement: Code written and committed
  └─> Commits made: git-commit-conventional-strict

□ PR: Changes documented and submitted
  └─> PR created: generate-pr-notes

□ Iterate: Status synced and learnings captured
  └─> Context stored: Atlassian MCP, claude-mem
```

---

## 📖 Quick Reference Card

```
╔════════════════════════════════════════════════════════════╗
║               SDD WORKFLOW CHEAT SHEET                     ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  1. CONSTITUTION                                           ║
║     /symlink-worktree-ignored-files                        ║
║     MCP: Atlassian (Confluence)                            ║
║                                                            ║
║  PRE-SPECIFY (PO handoff — optional)                       ║
║     /confluence-prd-to-spec                                    ║
║     Confluence PRD → local prd-source.md                  ║
║                                                            ║
║  2. SPECIFY                                                ║
║     spec-kit specify  (reference prd-source.md)           ║
║     MCP: Atlassian (Confluence) + claude-mem               ║
║                                                            ║
║  2→3. SPECIFY → PLAN (spec-kit native)                     ║
║     /sdd-tech-plan-to-confluence                           ║
║     MCP: Atlassian (Confluence)                            ║
║                                                            ║
║  3. PLAN                                                   ║
║     /sdd-tech-plan-to-confluence [page-id]  (re-publish)  ║
║     MCP: Atlassian (Confluence) + claude-mem               ║
║                                                            ║
║  4. TASKS                                                  ║
║     /confluence-tech-plan-to-jira-tickets                            ║
║     → implement code                                       ║
║     /git-commit-conventional-strict                        ║
║     /api-spec-to-confluence  (after commit)                ║
║     /generate-pr-notes                                     ║
║     MCP: Atlassian (Jira + Confluence) + claude-mem        ║
║                                                            ║
║  5. ITERATE                                                ║
║     MCP: Atlassian (Jira + Confluence)                     ║
║     MCP: claude-mem                                        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🔗 Related Documentation

- [Detailed Workflow Guide](./sdd-workflow-spec-kit-native.md)
- [Quick Reference with Examples](./sdd-quick-reference.md)
- [Agent Skills README](../README.md)
- [MCP Setup](../.agent-settings/mcps/README.md)
- [Skills Management](../.agent-settings/skills/README.md)
