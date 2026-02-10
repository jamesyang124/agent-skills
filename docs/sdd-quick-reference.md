# SDD Quick Reference: Agent Skills Integration

A quick visual guide showing how your agent skills integrate with GitHub Spec-Kit's SDD workflow.

---

## 🔄 The SDD Cycle

```
     ┌─────────────────────────────────────────────────────────┐
     │                                                         │
     │    Constitution → Specify → Plan → Tasks → Iterate     │
     │                      ↑                         ↓        │
     │                      └─────────────────────────┘        │
     │                                                         │
     └─────────────────────────────────────────────────────────┘
```

---

## 🎯 Integration Map

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    GITHUB SPEC-KIT SDD WORKFLOW                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────────────────────────────────────────────┐
│  🏛️  CONSTITUTION PHASE                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━                                       │
│  Define project standards, architecture, and conventions        │
│                                                                 │
│  📂 Outputs:                                                    │
│    • Coding standards                                          │
│    • API conventions                                           │
│    • Architecture guidelines                                   │
│                                                                 │
│  🛠️  Skills:                                                    │
│    • symlink-worktree-ignored-files                            │
│                                                                 │
│  🔌 MCP:                                                        │
│    • Atlassian (Store in Confluence)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  📋 SPECIFY PHASE                                               │
│  ━━━━━━━━━━━━━━━━━                                              │
│  Write specifications for features and APIs                     │
│                                                                 │
│  📂 Outputs:                                                    │
│    • Feature specifications                                    │
│    • Requirements docs                                         │
│                                                                 │
│  🔌 MCP:                                                        │
│    • Atlassian (Create/update Confluence pages)                │
│    • claude-mem (Remember specification patterns)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  📐 SPECIFY → PLAN TRANSITION                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━                                    │
│  Generate Technical Design Document before planning begins      │
│                                                                 │
│  📂 Outputs:                                                    │
│    • Tech Design Document (TDD) in Confluence                  │
│      - Architecture design                                     │
│      - Component design & API contracts                        │
│      - Data models & security considerations                   │
│      - Phased implementation plan                              │
│                                                                 │
│  🛠️  Skills:                                                    │
│    • spec-to-tech-design                                       │
│      └─> Read spec → Generate TDD → Publish to Confluence      │
│                                                                 │
│  🔌 MCP:                                                        │
│    • Atlassian (Create/update TDD page in Confluence)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  🎯 PLAN PHASE                                                  │
│  ━━━━━━━━━━━━━                                                  │
│  Refine and finalize the technical plan                         │
│                                                                 │
│  📂 Outputs:                                                    │
│    • Refined TDD                                               │
│    • Architecture design finalized                             │
│    • Implementation strategy ready for tasking                 │
│                                                                 │
│  🛠️  Skills:                                                    │
│    • spec-to-tech-design (re-run if spec changes)              │
│                                                                 │
│  🔌 MCP:                                                        │
│    • Atlassian (Update Confluence with plans)                  │
│    • claude-mem (Track architectural decisions)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  ✅ TASKS PHASE                                                 │
│  ━━━━━━━━━━━━━                                                  │
│  Break down work and implement                                  │
│                                                                 │
│  📂 Step 1: Create Tasks                                        │
│    └─> Confluence TDD → Jira Tickets                           │
│                                                                 │
│  🛠️  Skills:                                                    │
│    • confluence-to-jira-tickets                                │
│      └─> Convert TDD to actionable tickets                     │
│                                                                 │
│  🔌 MCP:                                                        │
│    • Atlassian (Create Jira tickets)                           │
│                                                                 │
│  ────────────────────────────────────────────────              │
│                                                                 │
│  📂 Step 2: Implement                                           │
│    └─> Write code                                              │
│                                                                 │
│  ────────────────────────────────────────────────              │
│                                                                 │
│  📂 Step 3: Commit                                              │
│    └─> Commit changes                                          │
│                                                                 │
│  🛠️  Skills:                                                    │
│    • git-commit-conventional-strict                            │
│      └─> Semantic commits with SemVer                          │
│                                                                 │
│  ────────────────────────────────────────────────              │
│                                                                 │
│  📂 Step 4: Document committed API                              │
│    └─> Analyze committed code → Publish API docs to Confluence │
│                                                                 │
│  🛠️  Skills:                                                    │
│    • api-spec-to-confluence                                    │
│      └─> Generate API docs from committed code                 │
│                                                                 │
│  🔌 MCP:                                                        │
│    • Atlassian (Publish API docs to Confluence)                │
│                                                                 │
│  ────────────────────────────────────────────────              │
│                                                                 │
│  📂 Step 5: Create PR                                           │
│                                                                 │
│  🛠️  Skills:                                                    │
│    • generate-pr-notes                                         │
│      └─> Comprehensive PR documentation                        │
│                                                                 │
│  🔌 MCP:                                                        │
│    • claude-mem (Track implementation patterns)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  🔄 ITERATE PHASE                                               │
│  ━━━━━━━━━━━━━━━                                                │
│  Review, learn, and improve                                     │
│                                                                 │
│  📂 Outputs:                                                    │
│    • Updated Jira status                                       │
│    • Documented learnings                                      │
│    • New requirements → back to SPECIFY                        │
│                                                                 │
│  🔌 MCP:                                                        │
│    • Atlassian (Sync Jira & Confluence)                        │
│    • claude-mem (Store learnings for future cycles)            │
└─────────────────────────────────────────────────────────────────┘
                    ↓                    ↓                    ↓
              ┌──────────┐        ┌──────────┐        ┌──────────┐
              │  New     │        │ Technical│        │   Bug    │
              │  Specs   │        │  Changes │        │   Fixes  │
              └────┬─────┘        └────┬─────┘        └────┬─────┘
                   │                   │                    │
                   ↓                   ↓                    ↓
              SPECIFY              PLAN                TASKS
```

---

## 🚀 Skill Usage by Phase

| Phase | Command | Purpose |
|-------|---------|---------|
| **Constitution** | `/symlink-worktree-ignored-files` | Set up development environment with worktrees |
| **Specify → Plan** | `/spec-to-tech-design` | Generate Tech Design Document from spec page |
| **Plan** | `/spec-to-tech-design` | Re-generate TDD if the spec changes |
| **Tasks** | `/confluence-to-jira-tickets` | Create Jira tickets from Confluence TDD |
| **Tasks** | `/git-commit-conventional-strict` | Create semantic version commits |
| **Tasks** | `/api-spec-to-confluence` | Generate API docs from committed code |
| **Tasks** | `/generate-pr-notes` | Generate comprehensive PR documentation |

---

## 📊 Data Flow Diagram

```
                           ┌─────────────┐
                           │  CONFLUENCE │
                           │   (Specs)   │
                           └──────┬──────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ↓                ↓                ↓
         ┌────────────┐   ┌────────────┐  ┌────────────┐
         │   JIRA     │   │   GitHub   │  │ claude-mem │
         │  (Tasks)   │   │  (Code)    │  │ (Context)  │
         └─────┬──────┘   └─────┬──────┘  └─────┬──────┘
               │                │               │
               │                │               │
       ┌───────┴────────┬───────┴────────┬──────┴───────┐
       │                │                │              │
       ↓                ↓                ↓              ↓
  Update Status   Git Commits      Pull Request    Learning
  via MCP         via Skill        via Skill        via MCP
       │                │                │              │
       └────────────────┴────────────────┴──────────────┘
                              ↓
                      ┌───────────────┐
                      │   ITERATION   │
                      │   (Feedback)  │
                      └───────────────┘
```

---

## 🎬 Example: "Add New User API Endpoint"

```
Step 1: CONSTITUTION
├─> Review API standards in Confluence (MCP: Atlassian)
└─> Status: ✅ Standards retrieved

Step 2: SPECIFY
├─> Write endpoint specification in Confluence
├─> Use: MCP Atlassian to create Confluence page
│   Title: "User Management API v2 - Create User"
│   Content: Requirements, validation rules, acceptance criteria
└─> Status: ✅ Specification documented

Step 2→3: SPECIFY → PLAN
├─> Generate Tech Design Document
├─> Use: /spec-to-tech-design skill
│   Input: Confluence spec page "User Management API v2 - Create User"
│   • Architecture: REST handler + validation middleware
│   • Component: UserService (new), ValidationMiddleware (extend)
│   • DB change: add email_verified column to users
│   • Implementation plan: 3 phases
│   Output: TDD page "TDD: User Management API v2 - Create User"
└─> Status: ✅ Tech Design Document published

Step 3: PLAN
├─> Review and refine TDD
├─> Use: MCP Atlassian + claude-mem
│   • Finalize architecture decisions
│   • Record key decisions in memory
└─> Status: ✅ Technical plan ready

Step 4: TASKS (Part 1 - Task Creation)
├─> Create actionable tasks
├─> Use: /confluence-to-jira-tickets skill
│   Input: TDD Confluence page
│   Output: Jira tickets
│   • PROJ-123: Implement POST /api/v2/users endpoint
│   • PROJ-124: Add input validation
│   • PROJ-125: Write unit tests
└─> Status: ✅ 3 Jira tickets created

Step 4: TASKS (Part 2 - Implementation)
├─> Implement the endpoint
│   1. Write handler code
│   2. Add validation middleware
│   3. Write tests
│
├─> Commit changes
│   Use: /git-commit-conventional-strict skill
│   Output: feat(api): ✨ add POST /api/v2/users endpoint
│
├─> Generate API documentation from committed code
│   Use: /api-spec-to-confluence skill
│   Input: src/routes/users.js (committed handler)
│   Output: API docs in Confluence
│   • POST /api/v2/users endpoint contract
│   • Request/response schemas
│   • Error handling reference
│
│   Implements user creation with validation and error handling.
│
│   BREAKING CHANGE: Deprecates legacy /api/users endpoint
│
│   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
│
├─> Create Pull Request
│   Use: /generate-pr-notes skill
│   Output: Comprehensive PR with:
│   • Summary of changes
│   • Breaking changes highlighted
│   • Test plan
│   • Links to Jira tickets (PROJ-123, PROJ-124, PROJ-125)
│
└─> Status: ✅ PR #456 created

Step 5: ITERATE
├─> Update Jira ticket status (MCP: Atlassian)
│   PROJ-123: In Review → Merged
│   PROJ-124: In Review → Merged
│   PROJ-125: In Review → Merged
│
├─> Document learnings in Confluence (MCP: Atlassian)
│   "Lessons learned: input validation patterns"
│
├─> Store context (MCP: claude-mem)
│   Decision: Use Joi for validation
│   Pattern: Validation middleware approach
│
└─> Status: ✅ Iteration complete

New feedback: "Add rate limiting"
└─> Cycle back to SPECIFY phase with new requirement
```

---

## 💡 Key Integration Points

### 1️⃣ Confluence as Specification Hub
- **Write once**: Specifications live in Confluence
- **Generate many**: API docs, Jira tickets, technical plans
- **Single source of truth**: All downstream artifacts trace back to specs

### 2️⃣ Automated Task Management
- **From specs to tickets**: confluence-to-jira-tickets skill
- **Structured commits**: git-commit-conventional-strict skill
- **PR documentation**: generate-pr-notes skill

### 3️⃣ Continuous Learning
- **claude-mem MCP**: Remembers decisions, patterns, learnings
- **Improves over time**: Better specs, plans, and implementations
- **Context retention**: No lost knowledge between iterations

### 4️⃣ Bidirectional Sync
- **Confluence ↔ Jira**: MCP Atlassian keeps docs and tickets in sync
- **GitHub → Confluence**: Skills update docs based on code changes
- **Jira → Confluence**: Status updates reflected in documentation

---

## 🎯 Quick Start Commands

```bash
# 1. Set up Atlassian MCP
./.agent-settings/mcps/install-atlassian-mcp.sh --agent claude

# 2. Import skills
./.agent-settings/skills/import-skills.sh claude

# 3. Initialize GitHub Spec-Kit
npm install -g @github/specify-cli
specify init

# 4. Start your first cycle
# In your AI agent:
# → Write spec in Confluence (MCP: Atlassian)
# → /spec-to-tech-design (generate TDD from spec)
# → /confluence-to-jira-tickets (create Jira tickets from TDD)
# → Implement code
# → /git-commit-conventional-strict
# → /api-spec-to-confluence (document the committed API)
# → /generate-pr-notes
```

---

## 📚 Resources

- [Full Integration Guide](./sdd-workflow-integration.md)
- [GitHub Spec-Kit](https://github.com/github/spec-kit)
- [Agent Skills README](../README.md)
- [MCP Setup Guide](../.agent-settings/mcps/README.md)
- [Skills Management](../.agent-settings/skills/README.md)
