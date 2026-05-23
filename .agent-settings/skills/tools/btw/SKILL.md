---
name: btw
description: Reads graphify-out/GRAPH_REPORT.md and appends a full timestamped snapshot to KNOWLEDGE_SUMMARY.md in the project root. Entries are always appended, never overwritten — building a chronological evidence log of knowledge graph states. Use after /graphify-monitor has built a graph to save a snapshot of what the graph currently knows.
allowed-tools: Bash(git rev-parse *), Bash(date *), Bash(ls *), Read, Write
---

# btw

Reads the current graphify knowledge graph output and appends a full timestamped snapshot to `KNOWLEDGE_SUMMARY.md`. All entries stack — the file is append-only and never deduplicated.

## When to Use

After `/graphify-monitor` has built a knowledge graph and you want to capture the current state as a reference point. Call it whenever you want to save a snapshot — before a big change, after an interesting discovery, or as a periodic checkpoint.

---

## Steps

### Step 1: Locate the project root

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

Store as `PROJECT_ROOT`.

### Step 2: Verify the graph report exists

```bash
ls "$PROJECT_ROOT/graphify-out/GRAPH_REPORT.md"
```

If missing: tell the user "graphify-out/GRAPH_REPORT.md not found. Run /graphify-monitor first to build the knowledge graph." Then stop.

### Step 3: Read the full graph report

Read the complete contents of `$PROJECT_ROOT/graphify-out/GRAPH_REPORT.md`. Do not truncate or summarize — the full content is required.

### Step 4: Get a UTC timestamp

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
```

Store as `TIMESTAMP`.

### Step 5: Format the entry

Construct the entry exactly as follows:

```markdown

---

## Knowledge Snapshot — [TIMESTAMP]

[FULL CONTENTS OF GRAPH_REPORT.MD]
```

### Step 6: Write to KNOWLEDGE_SUMMARY.md

**If `$PROJECT_ROOT/KNOWLEDGE_SUMMARY.md` does not exist:**
Create the file with this content:

```markdown
# Knowledge Summary

Chronological record of graphify knowledge graph snapshots.
Each entry is a full point-in-time snapshot of graphify-out/GRAPH_REPORT.md.

---

## Knowledge Snapshot — [TIMESTAMP]

[FULL CONTENTS OF GRAPH_REPORT.MD]
```

**If the file exists:**
Append the formatted entry from Step 5 to the end of the file. Do not modify any existing content.

### Step 7: Confirm to the user

```
Appended to KNOWLEDGE_SUMMARY.md

  Timestamp: [TIMESTAMP]
  Source:    graphify-out/GRAPH_REPORT.md
  File:      [PROJECT_ROOT]/KNOWLEDGE_SUMMARY.md

Entry stacked. All previous entries are preserved.
```

---

## Key Rules

- **Append-only**: Never overwrite or rewrite `KNOWLEDGE_SUMMARY.md`. Only ever add to the end.
- **No summarization**: Write the full contents of `GRAPH_REPORT.md` into each entry. Condensed versions lose structural information.
- **No deduplication**: Each `/btw` invocation creates a new timestamped entry even if the content has not changed since the last call. The timestamp is the differentiator.
- **Manual-only**: `/btw` is always invoked by the user. The background monitor never calls it automatically.
- **Graphify must have run first**: This skill only reads output — it does not build or update the graph. Run `/graphify-monitor` first.
