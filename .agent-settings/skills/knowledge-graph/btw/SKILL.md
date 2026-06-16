---
name: btw
description: Reads graphify-out/graph.json and appends a timestamped knowledge snapshot to KNOWLEDGE_SUMMARY.md in the project root. Entries are always appended, never overwritten — building a chronological evidence log of knowledge graph states. Use after /graphify-monitor has built a graph to record what the graph currently knows.
allowed-tools: Bash(git rev-parse *), Bash(date *), Bash(ls *), Bash(graphify *), Read, Write
---

# btw

Reads the current graphify knowledge graph and appends a timestamped snapshot to `KNOWLEDGE_SUMMARY.md`. All entries stack — the file is append-only and never deduplicated.

## When to Use

After `/graphify-monitor` has built a knowledge graph and you want to capture the current state as a reference point. Call it whenever you want to record what the graph knows — before a big change, after an interesting discovery, or as a periodic checkpoint.

---

## Steps

### Step 1: Locate the project root

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

Store as `PROJECT_ROOT`.

### Step 2: Verify the graph exists

```bash
ls "$PROJECT_ROOT/graphify-out/graph.json"
```

If missing: tell the user "graphify-out/graph.json not found. Run /graphify-monitor first to build the knowledge graph." Then stop.

### Step 3: Extract graph summary

Read `$PROJECT_ROOT/graphify-out/graph.json` and extract:
- `metadata.files` — number of files indexed
- `metadata.nodes` — number of symbols
- `metadata.edges` — number of relationships

If `metadata.nodes` > 0, run a broad symbol query to get a sample:
```bash
graphify query "$PROJECT_ROOT/graphify-out/graph.json" "." 2>/dev/null | head -50
```

If the command fails or returns nothing, set `SYMBOL_SAMPLE` to `(no symbols indexed for this project's file types)`.

Store the result as `SYMBOL_SAMPLE`.

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

**Files indexed:** [metadata.files]
**Symbols:** [metadata.nodes]
**Relationships:** [metadata.edges]

### Symbol Sample

[SYMBOL_SAMPLE]
```

### Step 6: Write to KNOWLEDGE_SUMMARY.md

**If `$PROJECT_ROOT/KNOWLEDGE_SUMMARY.md` does not exist:**
Create the file with this content:

```markdown
# Knowledge Summary

Chronological record of graphify knowledge graph snapshots.
Each entry captures the symbol/relationship counts and a sample of discovered symbols at that point in time.

---

## Knowledge Snapshot — [TIMESTAMP]

**Files indexed:** [metadata.files]
**Symbols:** [metadata.nodes]
**Relationships:** [metadata.edges]

### Symbol Sample

[SYMBOL_SAMPLE]
```

**If the file exists:**
Read the full current contents of `KNOWLEDGE_SUMMARY.md`. Concatenate the existing contents with the formatted entry from Step 5 (new entry at the end). Write the combined result back with the Write tool. Do not modify any existing content — only add the new entry after the last line.

### Step 7: Confirm to the user

```
Appended to KNOWLEDGE_SUMMARY.md

  Timestamp:     [TIMESTAMP]
  Files indexed: [metadata.files]
  Symbols:       [metadata.nodes]
  Relationships: [metadata.edges]
  File:          [PROJECT_ROOT]/KNOWLEDGE_SUMMARY.md

Entry stacked. All previous entries are preserved.
```

---

## Key Rules

- **Append-only**: Never overwrite or rewrite `KNOWLEDGE_SUMMARY.md`. Only ever add to the end.
- **No deduplication**: Each `/btw` invocation creates a new timestamped entry even if nothing changed. The timestamp is the differentiator.
- **Manual-only**: `/btw` is always invoked by the user. The background monitor never calls it automatically.
- **Graphify must have run first**: This skill only reads output — it does not build or update the graph. Run `/graphify-monitor` first.
