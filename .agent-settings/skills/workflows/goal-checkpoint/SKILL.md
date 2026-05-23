---
name: goal-checkpoint
description: General-purpose goal tracking with automatic checkpoint/resume support. Commits current state and writes a GOAL_STATE.md snapshot when context usage approaches 90%, ensuring the next session can fully restore and continue the work.
---

# Goal Checkpoint

This skill provides structured goal tracking across sessions. When context fills up (~90%), it commits a checkpoint so the next session can resume exactly where this one left off.

## When to Use

Invoke at the start of any non-trivial session where:
- The task spans multiple steps or files
- Work may not finish in one context window
- A clean resume in the next session is important

Trigger phrase: "use goal-checkpoint for this" or "/goal-checkpoint"

---

## Phase 1: Goal Declaration (Session Start)

When invoked, immediately:

### 1. Ask for the goal

Ask the user:
> "Describe the goal for this session. What should be accomplished, and what does 'done' look like?"

### 2. Write GOAL_STATE.md

Create (or overwrite) `GOAL_STATE.md` in the repo root:

```markdown
# Goal State

## Goal
[User's stated goal, verbatim]

## Done When
[User's definition of done]

## Started
[ISO date-time]

## Status
in-progress

## Steps
- [ ] [Step 1]
- [ ] [Step 2]
...

## Completed Steps
(none yet)

## Context Notes
(key decisions, blockers, environment state)

## Resume From
(filled in at checkpoint — what to do first in the next session)
```

### 3. Initial commit

Stage and commit `GOAL_STATE.md`:

```
chore(goal): 🎯 start session — [one-line goal summary]
```

---

## Phase 2: Progress Tracking (During Session)

As work progresses:

- **After each significant step completes**, move it from `Steps` to `Completed Steps` in `GOAL_STATE.md` and add a brief note.
- **After any file is substantially changed**, note it under `Context Notes` with a one-line description of its current state.
- Do **not** commit after every update — batch updates until a natural checkpoint.

---

## Phase 3: Checkpoint Protocol (At ~90% Context)

When context approaches 90% (observed via system reminders about context compression, or when the conversation feels dense), trigger a checkpoint **before** responding to the next user message.

### 3.1 Assess current state

Before committing, determine:
- Which steps are complete vs. in-progress
- Which files have been modified and how
- What the very next action should be in the next session
- Any environment or tool state the next session needs to know

### 3.2 Update GOAL_STATE.md

Fill in all fields completely:

```markdown
## Status
checkpoint

## Steps
- [ ] [remaining steps, updated]

## Completed Steps
- [x] [done step 1] — [brief outcome]
- [x] [done step 2] — [brief outcome]

## Context Notes
- [filename]: [current state / what was changed and why]
- [decision made]: [what was decided and why]
- [blocker or constraint]: [what the next session must know]

## Resume From
**Next action**: [Exact first thing to do in the next session]
**File to read first**: [most important file to open]
**Command to run**: [if a command sets up context, e.g. `git log --oneline -5`]
```

### 3.3 Stage and commit everything

```bash
# Stage all modified files
git add -A

# Commit with checkpoint message
git commit -m "chore(goal): 📍 checkpoint — [one-line summary of current state]

- [bullet: what was completed]
- [bullet: what is in progress]
- [bullet: what remains]

Resume: [one-line next action]"
```

### 3.4 Tell the user

After committing, report:

```
📍 Checkpoint saved (commit: <hash>)

Completed: [N] steps
Remaining: [M] steps
Resume: [one-line next action]

Context is near limit. Start a new session and say:
  "resume goal-checkpoint"
```

---

## Phase 4: Resume Protocol (Next Session Start)

When user says "resume goal-checkpoint" (or similar):

### 4.1 Read the checkpoint

```bash
git log --oneline -3
cat GOAL_STATE.md
```

### 4.2 Report state to user

```
📋 Resuming from checkpoint (<commit hash>)

Goal: [goal]
Status: [N of M steps complete]

Completed:
  ✅ [step]
  ✅ [step]

Remaining:
  [ ] [step]
  [ ] [step]

Context notes:
  [key facts]

Next action: [exact first thing to do]
```

### 4.3 Continue immediately

Do not ask for re-confirmation of the goal. Read the listed files, then proceed with the `Resume From` action.

---

## Phase 5: Session Complete

When all steps are done and the goal is met:

### 5.1 Update GOAL_STATE.md

```markdown
## Status
done

## Completed
[ISO date-time]
```

### 5.2 Final commit

```bash
git commit -m "chore(goal): ✅ complete — [goal summary]"
```

### 5.3 Report

```
✅ Goal complete: [goal summary]

All [N] steps finished.
GOAL_STATE.md marked done and committed.
```

---

## GOAL_STATE.md Full Template

```markdown
# Goal State

## Goal
[Goal description]

## Done When
[Definition of done]

## Started
[ISO date-time]

## Completed
(not yet)

## Status
in-progress | checkpoint | done

## Steps
- [ ] Step 1
- [ ] Step 2

## Completed Steps
- [x] Step N — [outcome note]

## Context Notes
- [file or decision]: [current state / rationale]

## Resume From
**Next action**: [exact first thing to do]
**File to read first**: [path]
**Command to run**: [optional setup command]
```

---

## Key Principles

- **Checkpoint early, not at the last moment.** 90% is the trigger, not 99%. Leave room to write the commit message.
- **Resume From must be unambiguous.** The next session agent has no memory of this session — the GOAL_STATE.md must stand alone.
- **Commit everything.** Uncommitted changes are invisible to the next session. Stage all files before the checkpoint commit.
- **One GOAL_STATE.md per repo root.** Overwrite it each session; git history preserves the prior states.
- **Context Notes beat memory.** Any decision, constraint, or discovery that is not obvious from the code belongs in Context Notes.
