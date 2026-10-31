#!/usr/bin/env bash
# Validate every skills/<name>/SKILL.md against docs/skill-anatomy.md.
# Exit 1 on any error; warnings are printed but do not fail.
set -euo pipefail
cd "$(dirname "$0")/.."

ALLOWED=" name description license compatibility metadata allowed-tools argument-hint disable-model-invocation "
errors=0 warnings=0
err()  { echo "  ERROR $1: $2"; errors=$((errors + 1)); }
warn() { echo "  WARN  $1: $2"; warnings=$((warnings + 1)); }

# Relative markdown links in $1 must resolve (anchors, URLs and code skipped).
check_links() {
  local file=$1 dir target
  dir=$(dirname "$file")
  awk '/^[ ]*```/ {code=!code; next} !code' "$file" | sed 's/`[^`]*`//g' |
    grep -o '\](\([^)#]*\)' | sed 's/^](//' | while read -r target; do
    case $target in http*|mailto:*|"") continue ;; esac
    [ -e "$dir/$target" ] || echo "$target"
  done
}

for dir in skills/*/; do
  name=$(basename "$dir") f="$dir/SKILL.md"
  [ -f "$f" ] || { err "$name" "missing SKILL.md"; continue; }
  [ "$(head -1 "$f")" = "---" ] || { err "$name" "no frontmatter"; continue; }
  fm=$(awk 'NR>1 && /^---$/ {exit} NR>1' "$f")

  for key in $(printf '%s\n' "$fm" | grep -oE '^[A-Za-z_-]+:' | tr -d ':'); do
    [[ $ALLOWED == *" $key "* ]] || err "$name" "frontmatter key '$key' not allowed (put it under metadata)"
  done

  [ "$(printf '%s\n' "$fm" | awk '/^name:/ {print $2}' | tr -d '"')" = "$name" ] || err "$name" "name does not match folder"

  # description: inline value, or a folded/literal block (indented continuation lines)
  desc=$(printf '%s\n' "$fm" | awk '/^description:/ {sub(/^description:[ ]*[>|]?-?[ ]*/, ""); d=$0; on=1; next}
    on && /^[ ]/ {sub(/^[ ]+/, ""); d=d " " $0; next} on {exit} END {print d}' | sed 's/^"//; s/"$//')
  [ -n "$desc" ] || err "$name" "missing description"
  [ ${#desc} -le 1024 ] || err "$name" "description is ${#desc} chars (max 1024)"
  grep -qi "use when" <<<"$desc" || err "$name" "description has no 'Use when' trigger"

  grep -q -- "--skill $name " "$f" || err "$name" "missing install line (npx skills add jamesyang124/agent-skills --skill $name -g)"

  lines=$(wc -l <"$f" | tr -d ' ')
  [ "$lines" -le 500 ] || warn "$name" "SKILL.md is $lines lines (keep under 500)"

  for broken in $(check_links "$f"); do err "$name" "broken link $broken"; done
done

for f in README.md docs/*.md; do
  for broken in $(check_links "$f"); do err "$f" "broken link $broken"; done
done

count=$(ls -d skills/*/ | wc -l | tr -d ' ')
echo "$count skills checked: $errors error(s), $warnings warning(s)"
[ "$errors" -eq 0 ]
