# pr-review-loop

## Overview

Takes the current branch through the whole Azure DevOps pull-request loop: open the PR with the pre-PR review
(`ado-open-pr`), review it (`ado-pr-code-review`), resolve the threads with the author (`ado-pr-resolve-comments`),
and re-review the new commits until no 🔴 Critical thread is left or the round limit is reached.

It keeps state per PR in `.git/pr-review-loop/<prId>.json` (never committed), so a later run continues where it
stopped. It never approves, votes or merges.

## Usage

```
/pr-review-loop                         # open a PR for the current branch, then review and resolve
/pr-review-loop <azure-devops-pr-url>   # continue the loop for an existing PR
/pr-review-loop --max-rounds 2 draft    # other tokens go to ado-open-pr
```

## Prerequisites

- `ado-open-pr`, `ado-pr-code-review` and `ado-pr-resolve-comments` installed next to this skill
- Azure DevOps MCP (`install-azure-devops-mcp`)
- A local checkout of the PR's repository on its source branch (the resolve phase commits and pushes there)
