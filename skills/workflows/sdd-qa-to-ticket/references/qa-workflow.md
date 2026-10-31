# QA Workflow Reference

## Step 5: Scenario Presentation Template

Before creating any Jira tickets, present all derived scenarios to the RD using this format:

```
Proposed QA scenarios for [Feature Name]
Derived from: spec.md, requirements.md, plan.md, [other files found]

Happy Paths:
1. [SCENARIO] [Short name]
   Given [precondition]
   When [action]
   Then [outcome]
   Source: requirements.md §[section]

Edge Cases:
2. [SCENARIO] [Short name]
   Given [precondition]
   When [action]
   Then [outcome]
   Source: plan.md §[section]

Error Paths:
3. [SCENARIO] [Short name]
   Given [precondition]
   When [action]
   Then [outcome]
   Source: spec.md §[section]

Root ticket: [PROJ-101]
Sub-tickets will be created as: [QA][SERVICE] [Scenario name]

Shall I create these as Jira sub-tickets? (Type y to proceed, n/skip to cancel, or describe any changes to make first.)
```

---

## Scenario Quality Checklist

Before presenting scenarios to the RD, verify each one:

- [ ] "Then" describes an observable outcome (not an internal state)
- [ ] Scenario is independent of other scenarios (can run in isolation)
- [ ] No test steps — only Given/When/Then
- [ ] "Given" describes a realistic precondition (not test setup steps)
- [ ] Scenario maps to at least one requirement or spec section

If a scenario fails this check, either fix it or drop it. Do not create low-quality tickets.

---

## Workflow Position

This skill sits at the **Implement → QA** boundary in the SDD workflow:

```
[/generate-pr-notes]
    PR created (phase exit condition for Phase 8)
         │
         ▼ (RD deliberate decision — not automatic)
[sdd-qa-to-ticket]  ← YOU ARE HERE
    Reads SDD *.md files → Derives BDD scenarios → Creates QA sub-tickets
         │
         ▼
[SDET execution]
    SDET claims sub-tickets → Executes in own order/method → Closes tickets when verified
         │
         ▼ (all QA sub-tickets closed)
[Release ready]
```
