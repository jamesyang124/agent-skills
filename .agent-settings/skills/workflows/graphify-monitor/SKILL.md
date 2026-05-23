---
name: graphify-monitor
description: Installs graphify, builds an initial knowledge graph of the current project, then spawns a background subagent that re-runs graphify every 30 seconds and prints newly-discovered knowledge to the terminal. Use when monitoring a project for structural changes during active development by another coding agent. Supports "stop" argument to terminate the background loop.
argument-hint: "[stop]"
allowed-tools: Bash(uname *), Bash(brew *), Bash(npx *), Bash(diff *), Bash(cp *), Bash(cat *), Bash(ls *), Bash(mkdir *), Bash(touch *), Bash(rm *), Bash(git rev-parse *), Bash(date *), Read, Write, Agent, Skill(graphify)
---

# Graphify Monitor

Builds a live knowledge graph of the current project and maintains a background subagent that detects and reports newly-discovered knowledge every 30 seconds. The monitor is isolated from the user's main session so it does not interfere with other agents or workflows.

## When to Use

Invoke at the start of a session when another coding agent is actively modifying a project and you want to track structural knowledge changes in real time.

- Trigger: `/graphify-monitor`
- Stop: `/graphify-monitor stop`

---

## Stop Mode (argument: "stop")

If invoked with the argument `stop`:

1. Write the stop sentinel:
   ```bash
   touch graphify-out/.monitor-stop
   ```
2. Confirm:
   ```
   Stop signal sent. The background monitor will exit on its next 30-second cycle.
   To restart: /graphify-monitor
   ```
3. Exit — do not proceed to Phase 1.

---

## Phase 1: Dependency Setup

### 1.1 Install Python runtime (macOS only)

```bash
uname -s
```

If output is `Darwin`:
```bash
brew install python@3.12 uv
```

If not Darwin, skip — `uv` and `python3.12` must already be in PATH.

### 1.2 Install the graphify skill

Graphify is a Claude Code skill — it is **not** a shell binary. Install it via the skills registry:

```bash
npx skills@latest add howell5/willhong-skills@graphify
```

This installs the `/graphify` skill into the local project's agent skills directory.

If installation fails, report the error and stop.

### 1.3 Install supporting tools (mattpocock/skills)

These provide useful companion skills for code analysis:

```bash
npx skills@latest add mattpocock/skills
```

If this fails, warn the user but continue — it is not required for graphify to work.

### 1.4 Verify graphify skill is available

Check that the graphify skill is installed:
```bash
ls .agents/skills/graphify/SKILL.md 2>/dev/null || ls ~/.claude/skills/graphify/SKILL.md 2>/dev/null || echo "SKILL_NOT_FOUND"
```

- If found: continue to Phase 2.
- If `SKILL_NOT_FOUND`: tell the user "graphify skill was not installed. Check that npx skills@latest succeeded and the `.agents/skills/graphify/` directory was created." Then stop.

---

## Phase 2: Initial Knowledge Graph Build

### 2.1 Get project root

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

Store as `PROJECT_PATH`.

### 2.2 Build the initial graph

Invoke the graphify skill with the project path as the argument:

```
Skill: graphify
Args: [PROJECT_PATH]
```

Graphify will analyze the project and write its output to `$PROJECT_PATH/graphify-out/`, producing `GRAPH_REPORT.md` and `graph.json`.

Wait for completion. If it fails, report the error and stop.

### 2.3 Verify output

```bash
ls "$PROJECT_PATH/graphify-out/GRAPH_REPORT.md"
```

If missing: "graphify ran but GRAPH_REPORT.md was not produced. Check graphify-out/ for error logs." Stop.

Print:
```
Initial knowledge graph built.
Output: [PROJECT_PATH]/graphify-out/GRAPH_REPORT.md
```

---

## Phase 3: Launch Background Monitor

### 3.1 Write the monitor prompt file

Write the file `$PROJECT_PATH/graphify-out/.monitor-prompt.txt`.

**Critical**: substitute `$PROJECT_PATH` and `$GRAPHIFY_CMD` with their resolved literal values when writing this file. The background subagent has no shell state from this session and must receive concrete paths.

File content template (replace `[PROJECT_PATH]` and `[GRAPHIFY_CMD]` with actual values):

```
You are a background graphify knowledge monitor. Execute these steps exactly, in order:

STEP 1 — Check stop sentinel:
  Run: ls "[PROJECT_PATH]/graphify-out/.monitor-stop" 2>/dev/null
  If the file exists: print "[graphify-monitor] Stop sentinel detected. Monitor exiting." and stop. Do NOT call ScheduleWakeup.

STEP 2 — Snapshot the current report:
  Run: cp "[PROJECT_PATH]/graphify-out/GRAPH_REPORT.md" /tmp/graphify-report-snapshot.md 2>/dev/null || echo "" > /tmp/graphify-report-snapshot.md

STEP 3 — Update the graph:
  Invoke the graphify skill with argument: "[PROJECT_PATH] --update"
  If the skill reports --update is not supported, invoke it again with just "[PROJECT_PATH]"

STEP 4 — Diff for new knowledge:
  Run: diff /tmp/graphify-report-snapshot.md "[PROJECT_PATH]/graphify-out/GRAPH_REPORT.md" 2>/dev/null
  Collect lines that start with "+" but not "+++".
  If any such lines exist: print "[graphify-monitor] New knowledge detected:" then print each line with its leading "+" removed.
  If no such lines: print nothing.

STEP 5 — Reschedule:
  Call ScheduleWakeup with delaySeconds=30 and prompt="Read [PROJECT_PATH]/graphify-out/.monitor-prompt.txt and execute the instructions within it exactly."
  reason="graphify-monitor: checking for new knowledge in [PROJECT_PATH]"
```

### 3.2 Spawn the background subagent

Use the `Agent` tool with `run_in_background: true`. Prompt:

```
Read [PROJECT_PATH]/graphify-out/.monitor-prompt.txt and execute the instructions within it exactly.
```

(Substitute the literal `PROJECT_PATH`.)

The background subagent manages its own rescheduling via ScheduleWakeup. The main skill session needs no further tracking.

### 3.3 Confirm to the user

```
Background monitor launched.

  Project:  [PROJECT_PATH]
  Interval: 30 seconds
  Graph:    [PROJECT_PATH]/graphify-out/GRAPH_REPORT.md

New knowledge will appear in this terminal as it is detected.
To stop: /graphify-monitor stop
```

---

## Design Notes

**Why Agent + ScheduleWakeup instead of /loop:**
`/loop` runs in the caller's session and blocks the user's context. The `Agent(run_in_background: true)` + `ScheduleWakeup` pattern creates a fully isolated subagent that does not compete with other agents or the user's main session.

**Why the prompt file as indirection:**
`.monitor-prompt.txt` keeps the ScheduleWakeup call lightweight (one sentence). The subagent reads the file fresh each 30-second cycle, making the loop inspectable and editable without modifying code.

**Delta reporting is additions only:**
Only new lines (`+` in diff output) are surfaced. Reformatted or removed content is intentional noise and is suppressed.
