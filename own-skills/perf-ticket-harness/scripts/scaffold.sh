#!/usr/bin/env bash
# scaffold.sh — create the per-ticket bench directory for perf-ticket-harness Phase 2.
#   bash scaffold.sh <ticket-slug> <perf-poc-shared-dir>
#   e.g. bash scaffold.sh connect-6031-view-count docs/perf-poc-shared
# Creates <dir>/<slug>/{README.md,run.sh,snapshot.sql,runs/} from the templates next to this
# script and prints the .gitignore lines to add. Idempotent: existing files are left alone.
set -euo pipefail

SLUG="${1:?ticket slug, e.g. connect-6031-view-count}"
BASE="${2:?perf-poc-shared dir, e.g. docs/perf-poc-shared}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TPL="$HERE/../templates"
DIR="$BASE/$SLUG"

mkdir -p "$DIR/runs"

put() { # put <template> <dest>
  if [[ -e "$2" ]]; then echo "keep   $2"; else sed "s/{{SLUG}}/$SLUG/g" "$1" > "$2"; echo "create $2"; fi
}
put "$TPL/bench-README.md" "$DIR/README.md"
put "$TPL/run.sh.tmpl"     "$DIR/run.sh"
put "$TPL/snapshot.sql.tmpl" "$DIR/snapshot.sql"
chmod +x "$DIR/run.sh"

cat <<EOF

Add to .gitignore (results are never committed, scripts are):
!$BASE/$SLUG/
!$BASE/$SLUG/**
$BASE/$SLUG/bench-log.md
$BASE/$SLUG/runs/

Next: fill the TODO blocks in $DIR/run.sh and $DIR/snapshot.sql, write the pass criteria into
the plan BEFORE the first run, then: SCENARIO=uniform N_REQS=300 CONC=10 NOTE=plumbing bash $DIR/run.sh
EOF
