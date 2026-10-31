# Workflow Integration & Example

## Workflow Position

This skill sits at the **Plan → Review** boundary in the SDD workflow:

```
[{configured SDD tool} plan]
    plan.md + requirements.md  (local source of truth)
         │
         ▼
[tech-plan-to-wiki]  ← YOU ARE HERE
    Reads local files → Maps to design review page → Publishes to Confluence
         │
         ▼
[Team Review Loop]
    Team reviews Confluence → Comments → RD refines {configured SDD tool} files → /tech-plan-to-wiki again
         │
         ▼ (consensus reached)
[Plan Finalized — Approved (v1)]
         │
         ▼
[tech-plan-to-ticket]
    Design review page → Jira root ticket + subtasks
```

---

## Worked Example

**User**: "Publish my plan to Confluence for team review"

**Agent**:
1. Scans cwd, finds `spec.md`, `plan.md`, `requirements.md`.
2. Reads all three files.
3. Extracts feature name: "Notification Service Refactor".
4. Maps content: Context from `spec.md`, Proposal from `plan.md`, Requirements from `requirements.md`. Notes no alternatives section in `plan.md` (marks Design Considerations as TODO).
5. Searches Confluence for "Technical Plan: Notification Service Refactor" — no results.
6. Presents summary to user, confirms create.
7. Creates Confluence page titled "Technical Plan: Notification Service Refactor".
8. Reports:
   ```
   ✅ Design review page published:
   https://your-org.atlassian.net/wiki/spaces/ENG/pages/987654321

   Status: Draft

   📌 Save your page ID: 987654321
      Next time you can run: /tech-plan-to-wiki 987654321
   ```

**Later — After team feedback:**

**User**: "/tech-plan-to-wiki 987654321"

**Agent**:
1. Reads updated `plan.md` (RD has incorporated team feedback).
2. Retrieves existing page 987654321.
3. Re-maps content with new material.
4. Updates page, appends Revision History row: `v2 | 2026-03-03 | [author] | Incorporated team feedback on retry strategy`.
5. Reports updated URL.
