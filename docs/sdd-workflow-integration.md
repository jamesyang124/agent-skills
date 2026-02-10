# SDD Workflow Integration with Agent Skills & MCP Tools

This document illustrates how agent-skills and MCP tools integrate with GitHub's Spec-Kit for Spec-Driven Development (SDD).

## Overview

**Spec-Driven Development Flow:** Constitution → 𝄆 Specify → Plan → Tasks 𝄇

The workflow creates a cycle where specifications drive implementation, with AI agents executing tasks based on well-defined specs and plans.

---

## Integration Architecture Diagram

```mermaid
graph TB
    subgraph "🏛️ Phase 1: CONSTITUTION"
        A[Project Setup] --> A1[Coding Standards]
        A1 --> A2[Architecture Guidelines]
        A2 --> A3[API Conventions]
    end

    subgraph "📋 Phase 2: SPECIFY"
        B[Requirements Analysis] --> B1[Feature Specs]
        B1 --> B2{Spec Storage}
        B2 -->|Write| B3[📄 Confluence Pages]
        B3 -->|MCP: Atlassian| B4[Confluence API]
    end

    subgraph "📐 Phase 2→3: SPECIFY → PLAN"
        T1[Confluence Spec Page] -.->|skill: spec-to-tech-design| T2[📄 Tech Design Doc]
        T2 -->|MCP: Atlassian| T3[Confluence API]
    end

    subgraph "🎯 Phase 3: PLAN"
        C[Technical Planning] --> C1[Architecture Design]
        C1 --> C2[Implementation Strategy]
        C2 --> C3{Documentation}
        C3 -->|Update| C4[📄 Confluence Docs]
        C4 -->|MCP: Atlassian| C5[Confluence API]
    end

    subgraph "✅ Phase 4: TASKS"
        D[Task Breakdown] --> D1{Task Management}
        D1 -->|Create| D2[🎫 Jira Tickets]
        D2 -->|MCP: Atlassian| D3[Jira API]
        D1 -->|Track| D4[GitHub Issues]

        D5[Confluence Docs] -.->|skill: confluence-to-jira-tickets| D2

        D6[Implementation] --> D7[Code Changes]
        D7 --> D8{Version Control}
        D8 -->|Commit| D9[Git Commits]
        D9 -.->|skill: git-commit-conventional-strict| D10[Conventional Commits]

        D10 -.->|skill: api-spec-to-confluence| D13[📄 API Docs in Confluence]
        D13 -->|MCP: Atlassian| D14[Confluence API]

        D8 -->|PR| D11[Pull Requests]
        D11 -.->|skill: generate-pr-notes| D12[PR Documentation]
    end

    subgraph "🔄 Phase 5: ITERATE"
        E[Review & Feedback] --> E1{Status Update}
        E1 -->|Sync| E2[📊 Jira Status]
        E2 -->|MCP: Atlassian| E3[Update Tickets]
        E1 -->|Document| E4[📝 Confluence Updates]
        E4 -->|MCP: Atlassian| E5[Update Docs]

        E6[New Requirements] --> B
        E7[Technical Changes] --> C
        E8[Bug Fixes] --> D
    end

    subgraph "🧠 Context Layer (MCP: claude-mem)"
        M1[Memory Store] -.->|Context| B
        M1 -.->|History| C
        M1 -.->|Decisions| D
        M1 -.->|Learning| E

        B -.->|Record| M1
        C -.->|Record| M1
        D -.->|Record| M1
        E -.->|Record| M1
    end

    subgraph "🛠️ Development Environment"
        DEV1[Worktrees] -.->|skill: symlink-worktree-ignored-files| DEV2[Environment Setup]
    end

    %% Main flow
    A3 --> B
    B3 --> T1
    T2 --> C
    C4 --> D
    D12 --> E
    E8 -.-> D
    E7 -.-> C
    E6 -.-> B

    %% Supporting connections
    DEV2 -.-> D6

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#ffe1f5
    style D fill:#e1ffe1
    style E fill:#f5e1ff
    style M1 fill:#ffe1e1
```

---

## Sequence Diagram

```mermaid
sequenceDiagram
    actor Dev as Developer / Agent
    participant CF as Confluence
    participant Mem as claude-mem
    participant Code as Codebase
    participant Jira as Jira
    participant Git as Git / GitHub

    rect rgb(225, 245, 255)
        Note over Dev,Git: 1. CONSTITUTION
        Dev->>CF: Read architecture standards & API conventions
        CF-->>Dev: Coding standards
        Dev->>Mem: Store constitution context
    end

    rect rgb(255, 244, 225)
        Note over Dev,Git: 2. SPECIFY
        Dev->>CF: Create spec page (requirements, acceptance criteria)
        Dev->>Mem: Remember specification decisions
    end

    rect rgb(210, 220, 255)
        Note over Dev,Git: 2→3. SPECIFY → PLAN  [skill: spec-to-tech-design]
        Dev->>CF: Fetch spec page
        CF-->>Dev: Spec content
        Dev->>Code: Inspect relevant source files
        Code-->>Dev: Existing architecture context
        Note over Dev: Generate Tech Design Document
        Dev->>CF: Create TDD page (architecture, components,<br/>data models, API contracts, impl plan)
        CF-->>Dev: TDD page URL
        Dev->>Mem: Record architectural decisions
    end

    rect rgb(255, 225, 245)
        Note over Dev,Git: 3. PLAN
        Dev->>CF: Review & refine TDD
        Dev->>Mem: Track design decisions
    end

    rect rgb(225, 255, 225)
        Note over Dev,Git: 4a. TASKS — Create tickets  [skill: confluence-to-jira-tickets]
        Dev->>CF: Fetch TDD page
        CF-->>Dev: TDD content
        Dev->>Jira: Create root ticket + subtasks
        Jira-->>Dev: Ticket keys (e.g. PROJ-101, PROJ-102)
    end

    rect rgb(200, 245, 215)
        Note over Dev,Git: 4b. TASKS — Implement
        Dev->>Code: Write implementation
        Code-->>Dev: Code ready
    end

    rect rgb(180, 235, 200)
        Note over Dev,Git: 4c. TASKS — Commit  [skill: git-commit-conventional-strict]
        Dev->>Git: Commit with conventional message + SemVer
        Git-->>Dev: Commit SHA
    end

    rect rgb(160, 225, 190)
        Note over Dev,Git: 4d. TASKS — Document API  [skill: api-spec-to-confluence]
        Dev->>Code: Analyze committed router / handler
        Code-->>Dev: Route definitions & handler logic
        Dev->>CF: Create / update API docs page
        CF-->>Dev: API docs URL
    end

    rect rgb(140, 215, 175)
        Note over Dev,Git: 4e. TASKS — Pull Request  [skill: generate-pr-notes]
        Dev->>Git: Create PR with notes (summary, test plan, ticket links)
        Git-->>Dev: PR URL
        Dev->>Mem: Track implementation patterns
    end

    rect rgb(245, 225, 255)
        Note over Dev,Git: 5. ITERATE
        Dev->>Jira: Update ticket status
        Dev->>CF: Document learnings
        Dev->>Mem: Store learnings for future cycles
    end
```

---

## Integration Points by Phase

### 1. Constitution Phase
**Purpose:** Establish project foundations and standards

**Integration:**
- Document architecture guidelines in Confluence
- Define API conventions and patterns
- Set up development environment

**Skills Used:**
- `symlink-worktree-ignored-files` - Environment setup for multiple worktrees

**MCP Tools:**
- `Atlassian MCP` - Store constitution docs in Confluence

---

### 2. Specify Phase
**Purpose:** Define what needs to be built

**Integration:**
- Write feature specifications
- Store specs in Confluence for team access

**Skills Used:**
- *(none — specs are written directly in Confluence via MCP)*

**MCP Tools:**
- `Atlassian MCP` - Create/update Confluence pages
- `claude-mem` - Remember specification decisions and patterns

**Workflow:**
```
Requirements → Write Spec → Store in Confluence
```

---

### 2→3. Specify → Plan Transition
**Purpose:** Translate the feature spec into a structured Technical Design Document before planning begins

**Integration:**
- Read the approved spec page from Confluence
- Analyze requirements, affected components, and constraints
- Generate a full Tech Design Document (TDD) and publish it to Confluence

**Skills Used:**
- `spec-to-tech-design` - Reads a Confluence spec and produces a TDD covering architecture, components, data models, API contracts, security, testing strategy, and phased implementation plan

**MCP Tools:**
- `Atlassian MCP` - Fetch spec page, create/update TDD page

**Workflow:**
```
Confluence Spec → spec-to-tech-design → Tech Design Doc → Confluence (TDD page)
```

---

### 3. Plan Phase
**Purpose:** Create technical implementation strategy

**Integration:**
- Design architecture based on the TDD produced at the Specify→Plan transition
- Refine and update the TDD as decisions are finalized
- Link plans to specifications

**Skills Used:**
- `spec-to-tech-design` - Re-run to update the TDD if the spec changes

**MCP Tools:**
- `Atlassian MCP` - Update Confluence with technical plans
- `claude-mem` - Track architectural decisions

**Workflow:**
```
Spec → Tech Design Doc (TDD) → Refined Plan → Confluence
```

---

### 4. Tasks Phase
**Purpose:** Break down and execute work

**Integration:**
- Convert plans into actionable tasks
- Create Jira tickets from Confluence docs
- Implement with proper version control
- Document changes in PRs

**Skills Used:**
- `confluence-to-jira-tickets` - Create Jira tickets from Confluence documentation
- `git-commit-conventional-strict` - Structured, semantic commits with SemVer
- `generate-pr-notes` - Comprehensive PR documentation
- `api-spec-to-confluence` - Generate API documentation from the implemented code

**MCP Tools:**
- `Atlassian MCP` - Create/update Jira tickets, publish API docs
- `claude-mem` - Track implementation decisions and patterns

**Workflow:**
```
Confluence TDD → Jira Tickets → Implement Code → Git Commits → API Docs → Pull Request
              ↓                      ↓                ↓              ↓            ↓
  confluence-to-jira-tickets       Code        git-commit  api-spec-to-confluence  generate-pr-notes
```

---

### 5. Iterate Phase
**Purpose:** Review, learn, and improve

**Integration:**
- Update task status in Jira
- Document learnings in Confluence
- Feed insights back into specs/plans

**MCP Tools:**
- `Atlassian MCP` - Sync status across Jira and Confluence
- `claude-mem` - Learn from iterations and improve future cycles

**Workflow:**
```
Review → Update Status → Document Learnings → Next Iteration
   ↓          ↓                ↓                    ↓
 Jira    Atlassian MCP    Confluence          New Specs/Plans
```

---

## Complete Cycle Example

### Scenario: Adding a New API Endpoint

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CONSTITUTION: Review API conventions in Confluence          │
│    └─> MCP: Atlassian (Read existing standards)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. SPECIFY: Define new endpoint requirements                    │
│    └─> Write spec in Confluence                                 │
│    └─> MCP: Atlassian (Create Confluence page)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2→3. SPECIFY → PLAN: Generate Technical Design Document         │
│    └─> Skill: spec-to-tech-design (Read spec → Create TDD)      │
│    └─> MCP: Atlassian (Create TDD page in Confluence)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. PLAN: Design implementation approach                         │
│    └─> Review and refine TDD                                    │
│    └─> MCP: Atlassian (Update Confluence)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. TASKS: Execute implementation                                │
│    ├─> Skill: confluence-to-jira-tickets (Create Jira tasks)    │
│    │   └─> MCP: Atlassian (Create Jira tickets)                 │
│    ├─> Implement code in worktree                               │
│    │   └─> Skill: symlink-worktree-ignored-files (Setup env)    │
│    ├─> Commit changes                                           │
│    │   └─> Skill: git-commit-conventional-strict (SemVer)       │
│    ├─> Generate API docs from committed code                    │
│    │   └─> Skill: api-spec-to-confluence (Publish to Confluence)│
│    └─> Create PR                                                │
│        └─> Skill: generate-pr-notes (PR documentation)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. ITERATE: Review and refine                                   │
│    ├─> Update Jira ticket status                                │
│    │   └─> MCP: Atlassian (Update Jira)                         │
│    ├─> Document learnings in Confluence                         │
│    │   └─> MCP: Atlassian (Update Confluence)                   │
│    └─> Record decisions                                         │
│        └─> MCP: claude-mem (Store context)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skill Mapping Matrix

| Phase | GitHub Spec-Kit Action | Agent Skill | MCP Tool | Output |
|-------|----------------------|-------------|----------|---------|
| **Constitution** | Setup project standards | symlink-worktree-ignored-files | Atlassian | Environment ready |
| **Specify** | Write specifications | *(MCP direct)* | Atlassian | Confluence pages |
| **Specify → Plan** | Generate tech design | spec-to-tech-design | Atlassian | Tech Design Doc in Confluence |
| **Plan** | Refine technical plans | spec-to-tech-design | Atlassian | Updated TDD |
| **Tasks** | Generate API docs from code | api-spec-to-confluence | Atlassian | API documentation in Confluence |
| **Tasks** | Create work items | confluence-to-jira-tickets | Atlassian | Jira tickets |
| **Tasks** | Implement code | - | claude-mem | Code changes |
| **Tasks** | Version control | git-commit-conventional-strict | - | Git commits |
| **Tasks** | Document changes | generate-pr-notes | - | Pull requests |
| **Iterate** | Sync status | - | Atlassian | Updated tickets |
| **Iterate** | Record learnings | - | claude-mem | Context memory |

---

## Benefits of This Integration

### 🎯 Traceability
- Requirements → Specs → Plans → Tasks → Code → PRs
- Every change traces back to a specification
- Bidirectional links between Confluence and Jira

### 🤖 Automation
- Auto-generate API documentation from code
- Convert specs to actionable Jira tickets
- Structured commits with semantic versioning
- Comprehensive PR notes generation

### 🧠 Contextual Intelligence
- claude-mem MCP retains decisions and patterns
- Consistent approach across iterations
- Learning from past implementations

### 📊 Visibility
- Confluence as single source of truth for specs
- Jira for task tracking and progress
- GitHub for code and PR documentation
- Integrated view across all platforms

### 🔄 Iteration-Friendly
- Easy to update specs and regenerate docs
- Sync changes across Confluence, Jira, and GitHub
- Maintain consistency during iterations

---

## Getting Started

### 1. Install GitHub Spec-Kit
```bash
npm install -g @github/specify-cli
specify init
```

### 2. Set Up MCP Integration
```bash
# Install Atlassian MCP
./.agent-settings/mcps/install-atlassian-mcp.sh --agent claude

# Configure credentials in .env.mcp-atlassian
```

### 3. Import Agent Skills
```bash
# For Claude Code (skills are symlinked)
./.agent-settings/skills/import-skills.sh claude

# For Gemini CLI
./.agent-settings/skills/import-skills.sh gemini
```

### 4. Start Your First SDD Cycle
```bash
# 1. Constitution: Document standards in Confluence
# 2. Specify: Write feature spec
# 3. Plan: Use /api-spec-to-confluence skill
# 4. Tasks: Use /confluence-to-jira-tickets skill
# 5. Implement: Use /git-commit-conventional-strict
# 6. PR: Use /generate-pr-notes
```

---

## References

- [GitHub Spec-Kit Repository](https://github.com/github/spec-kit)
- [Spec-Driven Development Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Microsoft Developer Blog: Diving Into Spec-Driven Development](https://developer.microsoft.com/blog/spec-driven-development-spec-kit)
- [Martin Fowler: Understanding Spec-Driven-Development](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- [GitHub Blog: Spec-driven development with AI](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)

---

## License

See [LICENSE](../LICENSE) file for details.
