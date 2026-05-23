---
name: graphify-monitor
description: Installs graphify, builds an initial knowledge graph of the current project, then spawns a background subagent that re-runs graphify every 30 seconds and prints newly-discovered knowledge to the terminal. Use when monitoring a project for structural changes during active development by another coding agent. Supports "stop" argument to terminate the background loop.
argument-hint: "[stop]"
allowed-tools: Bash(uname *), Bash(brew *), Bash(npm *), Bash(npx *), Bash(graphify *), Bash(diff *), Bash(cp *), Bash(cat *), Bash(ls *), Bash(mkdir *), Bash(touch *), Bash(rm *), Bash(git *), Bash(date *), Read, Write, Agent, Skill(graphify)
---

# Graphify Monitor

Builds a live knowledge graph of the current project and maintains a background subagent that detects and reports newly-discovered structural changes every 30 seconds. The monitor runs in an isolated subagent so it does not compete with the user's main session or other agents.

## When to Use

Invoke when another coding agent is actively modifying a project and you want to track structural knowledge changes in real time.

- Trigger: `/graphify-monitor`
- Stop: `/graphify-monitor stop`

---

## Stop Mode (argument: "stop")

If invoked with the argument `stop`:

1. Resolve the project root (required for correct sentinel path):
   ```bash
   git rev-parse --show-toplevel 2>/dev/null || pwd
   ```
   Store as `STOP_PROJECT_PATH`.

2. Write the stop sentinel using the absolute path:
   ```bash
   touch "$STOP_PROJECT_PATH/graphify-out/.monitor-stop"
   ```
3. Confirm:
   ```
   Stop signal sent. The background monitor will exit on its next 30-second cycle.
   To restart: /graphify-monitor
   ```
4. Exit — do not proceed to Phase 1.

---

## Phase 1: Dependency Setup

### 1.1 Check Python runtime (macOS only)

```bash
uname -s
```

If output is `Darwin`, check whether `uv` and `python3.12` are installed:
```bash
uv --version 2>/dev/null && python3.12 --version 2>/dev/null || echo "MISSING"
```

If `MISSING`, hint the user:
```
python3.12 and uv are required as a graphify runtime dependency.

  Install with: brew install python@3.12 uv

Install now? (y/n)
```
- If `y`: run `brew install python@3.12 uv`
- If `n`: tell the user to install these manually, then stop.

If not Darwin, skip — `uv` and `python3.12` must already be in PATH.

### 1.2 Check and install the graphify-ts CLI

Check whether the CLI is installed:
```bash
graphify --version 2>/dev/null || echo "CLI_NOT_FOUND"
```

**If found**: print `✅ graphify CLI already installed` and continue to 1.3.

**If `CLI_NOT_FOUND`**: hint the user:
```
The graphify CLI is not installed. It is required to build and update the knowledge graph.

  Package: graphify-ts (npm)
  Install: npm i -g graphify-ts

Install now? (y/n)
```
- If `y`: run `npm i -g graphify-ts`. If it fails, report the error and stop.
- If `n`: tell the user to install it manually and stop.

### 1.3 Check and install the graphify skill

Check whether the graphify skill is installed:
```bash
ls .agents/skills/graphify/SKILL.md 2>/dev/null || ls ~/.claude/skills/graphify/SKILL.md 2>/dev/null || echo "SKILL_NOT_FOUND"
```

**If found**: print `✅ graphify skill already installed` and continue to 1.4.

**If `SKILL_NOT_FOUND`**: hint the user:
```
The graphify Claude Code skill is not installed. It wraps the CLI for agent use.

  Source:  howell5/willhong-skills@graphify  (613 installs on skills.sh)
  Install: npx skills@latest add howell5/willhong-skills@graphify

Install now? (y/n)
```
- If `y`: run `npx skills@latest add howell5/willhong-skills@graphify`. If it fails, report the error and stop.
- If `n`: tell the user to install it manually and stop.

### 1.4 Check and install supporting tools (mattpocock/skills)

Check whether mattpocock skills are installed:
```bash
ls .agents/skills/diagnose/SKILL.md 2>/dev/null || echo "NOT_INSTALLED"
```

**If found**: print `✅ mattpocock/skills already installed` and continue to Phase 2.

**If `NOT_INSTALLED`**: hint the user:
```
mattpocock/skills adds useful code analysis companions (diagnose, tdd, grill-me, etc.).
Not required for graphify, but recommended for full knowledge monitoring.

  Install: npx skills@latest add mattpocock/skills

Install now? (y/n)  — type n to skip
```
- If `y`: run `npx skills@latest add mattpocock/skills`. If it fails, warn but continue.
- If `n`: skip silently and continue to Phase 2.

---

## Phase 2: Initial Knowledge Graph Build

### 2.1 Get project root

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

Store as `PROJECT_PATH`.

### 2.1a Ensure graphify-out/ is git-ignored

Check if `graphify-out` is already in `.gitignore`:
```bash
grep -q "graphify-out" "$PROJECT_PATH/.gitignore" 2>/dev/null || echo "NOT_IGNORED"
```

If `NOT_IGNORED`, append it:
```bash
echo "graphify-out/" >> "$PROJECT_PATH/.gitignore"
```

Print: `✅ graphify-out/ added to .gitignore`

### 2.2 Check for existing graph

```bash
ls "$PROJECT_PATH/graphify-out/graph.json" 2>/dev/null || echo "NOT_BUILT"
```

- If `graph.json` exists: print `✅ Existing graph found — running auto-update` then run `graphify auto-update "$PROJECT_PATH"` and skip to 2.3.
- If `NOT_BUILT`: build fresh with `graphify build "$PROJECT_PATH"`.

Wait for completion. If either command fails, report the error and stop.

### 2.3 Verify output

```bash
ls "$PROJECT_PATH/graphify-out/graph.json"
```

If missing: "graphify ran but graph.json was not produced. Check graphify-out/ for error logs." Stop.

Read `graphify-out/graph.json` and extract the `metadata` field. Report to the user:
```
Initial knowledge graph built.

  Files:         [metadata.files]
  Symbols:       [metadata.nodes]
  Relationships: [metadata.edges]
  Output:        [PROJECT_PATH]/graphify-out/graph.json
```

---

## Phase 3: Launch Background Monitor

### 3.1 Write the monitor prompt file

Write `$PROJECT_PATH/graphify-out/.monitor-prompt.txt`.

**Critical**: substitute `[PROJECT_PATH]` with its resolved literal value when writing — the background subagent has no shell state from this session.

```
You are a background graphify knowledge monitor. Execute these steps exactly, in order:

STEP 1 — Check stop sentinel:
  Run: ls "[PROJECT_PATH]/graphify-out/.monitor-stop" 2>/dev/null
  If the file exists: print "[graphify-monitor] Stop sentinel detected. Monitor exiting." and stop. Do NOT call ScheduleWakeup.

STEP 2 — Snapshot current node/edge counts:
  Read "[PROJECT_PATH]/graphify-out/graph.json" and extract metadata.nodes and metadata.edges.
  Store as SNAPSHOT_NODES and SNAPSHOT_EDGES.

STEP 3 — Update the graph:
  Run: graphify auto-update [PROJECT_PATH]
  This re-extracts any files changed since the last build (via git diff + untracked).

STEP 4 — Detect new knowledge:
  Read "[PROJECT_PATH]/graphify-out/graph.json" again and extract metadata.nodes and metadata.edges.
  If nodes > SNAPSHOT_NODES or edges > SNAPSHOT_EDGES:
    Run: graphify query [PROJECT_PATH]/graphify-out/graph.json "" 2>/dev/null | head -30
    Print:
      [graphify-monitor] New knowledge detected (+[delta_nodes] symbols, +[delta_edges] relationships):
      [query output]
  If no change: print nothing.

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

### 3.3 Confirm to the user

```
Background monitor launched.

  Project:  [PROJECT_PATH]
  Interval: 30 seconds
  Graph:    [PROJECT_PATH]/graphify-out/graph.json

New symbols and relationships will appear here as they are detected.
To stop: /graphify-monitor stop
```

---

## Design Notes

**Why Agent + ScheduleWakeup instead of /loop:**
`/loop` blocks the caller's session. `Agent(run_in_background: true)` + `ScheduleWakeup` runs fully isolated — it does not compete with other agents or the user's session.

**Why graph.json, not a report file:**
graphify-ts outputs `graphify-out/graph.json`. Delta detection uses the `metadata.nodes` / `metadata.edges` counters — a numeric increase means new structural knowledge was extracted. New symbols are surfaced via `graphify query`.

**Why the prompt file as indirection:**
`.monitor-prompt.txt` keeps each ScheduleWakeup call to one sentence. The subagent reads it fresh each cycle — making the loop inspectable and editable without code changes.
