# Documentation

This directory contains comprehensive guides for integrating agent skills and MCP tools with GitHub's Spec-Kit for Spec-Driven Development.

---

## 📚 Available Guides

### [SDD Workflow Integration Guide](./sdd-workflow-integration.md)
**Comprehensive overview with detailed architecture**

The complete guide to understanding how your agent skills and MCP tools integrate with GitHub's Spec-Kit. Includes:
- Full workflow architecture with Mermaid diagrams
- Integration points for each SDD phase
- Detailed skill and MCP tool usage
- Complete cycle examples
- Benefits and traceability
- Getting started instructions

**Best for:** Understanding the complete picture and architecture decisions.

---

### [SDD Quick Reference](./sdd-quick-reference.md)
**Fast visual guide with examples**

A scannable reference showing the SDD workflow with ASCII diagrams and real-world examples. Includes:
- Visual SDD cycle representation
- Integration map with all phases
- Skill usage by phase table
- Data flow diagram
- Step-by-step example walkthrough
- Key integration points
- Quick start commands

**Best for:** Quick lookups and understanding the flow with practical examples.

---

### [SDD Skills Map](./sdd-skills-map.md)
**Simple mapping reference**

The simplest guide showing exactly which skills and MCP tools to use at each phase. Includes:
- Complete cycle diagram
- Skill invocation commands
- Phase-skill matrix
- Decision tree for tool selection
- Real-world scenario walkthrough
- Status indicators
- Quick reference cheat sheet

**Best for:** When you just need to know "which skill do I use here?"

---

## 🎯 Which Guide Should I Use?

```
┌─────────────────────────────────────────────────────────────┐
│  I want to...                                               │
├─────────────────────────────────────────────────────────────┤
│  □ Understand the overall architecture                      │
│    → Read: SDD Workflow Integration Guide                   │
│                                                             │
│  □ See practical examples with visuals                      │
│    → Read: SDD Quick Reference                              │
│                                                             │
│  □ Know which skill/tool to use right now                   │
│    → Read: SDD Skills Map                                   │
│                                                             │
│  □ Get started quickly                                      │
│    → Read: All three (start with Skills Map)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Path

**New to SDD with agent skills?** Follow this reading order:

1. **[SDD Skills Map](./sdd-skills-map.md)** (5 min)
   - Get familiar with the cycle and tools

2. **[SDD Quick Reference](./sdd-quick-reference.md)** (10 min)
   - See practical examples and data flow

3. **[SDD Workflow Integration Guide](./sdd-workflow-integration.md)** (20 min)
   - Understand the complete architecture

---

## 📖 SDD Phases Overview

All three guides cover these five phases of Spec-Driven Development:

### 1. 🏛️ Constitution
Define project standards, architecture, and conventions.

**Skills:** `symlink-worktree-ignored-files`
**MCP:** Atlassian (Confluence)

---

### 2. 📋 Specify
Write specifications for features and APIs.

**Skills:** `api-spec-to-confluence`
**MCP:** Atlassian (Confluence), claude-mem

---

### 3. 🎯 Plan
Create technical implementation strategy.

**Skills:** `api-spec-to-confluence`
**MCP:** Atlassian (Confluence), claude-mem

---

### 4. ✅ Tasks
Break down work, implement, and deliver.

**Skills:**
- `confluence-to-jira-tickets` (task creation)
- `git-commit-conventional-strict` (commits)
- `generate-pr-notes` (PRs)

**MCP:** Atlassian (Jira), claude-mem

---

### 5. 🔄 Iterate
Review, learn, and improve for the next cycle.

**MCP:** Atlassian (Jira + Confluence sync), claude-mem

---

## 🛠️ Tools Reference

### Agent Skills

| Skill | Purpose | Used In Phases |
|-------|---------|---------------|
| `symlink-worktree-ignored-files` | Setup dev environment | Constitution |
| `api-spec-to-confluence` | Generate API docs from code | Specify, Plan |
| `confluence-to-jira-tickets` | Create Jira tickets from docs | Tasks |
| `git-commit-conventional-strict` | Semantic version commits | Tasks |
| `generate-pr-notes` | PR documentation | Tasks |

### MCP Tools

| MCP | Purpose | Used In Phases |
|-----|---------|---------------|
| Atlassian (Confluence) | Spec and doc storage | Constitution, Specify, Plan, Iterate |
| Atlassian (Jira) | Task management | Tasks, Iterate |
| claude-mem | Context and learning | Specify, Plan, Tasks, Iterate |

---

## 🔗 External Resources

### GitHub Spec-Kit
- [GitHub Spec-Kit Repository](https://github.com/github/spec-kit)
- [Spec-Driven Development Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Getting Started with Spec-Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)

### Background Reading
- [Microsoft: Diving Into Spec-Driven Development](https://developer.microsoft.com/blog/spec-driven-development-spec-kit)
- [Martin Fowler: Understanding Spec-Driven-Development](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)

### Project Resources
- [Agent Skills Main README](../README.md)
- [Skills Management Guide](../.agent-settings/skills/README.md)
- [MCP Setup Guide](../.agent-settings/mcps/README.md)

---

## 💡 Contributing

Found an issue or have suggestions for improving these guides?

1. Open an issue describing the problem or enhancement
2. Submit a PR with documentation improvements
3. Share your SDD workflow experiences

---

## 📝 License

These documentation files are part of the agent-skills project. See [LICENSE](../LICENSE) for details.
