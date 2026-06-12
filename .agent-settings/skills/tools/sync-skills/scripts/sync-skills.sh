#!/usr/bin/env bash
# sync-skills.sh
# Usage: bash <skill-dir>/scripts/sync-skills.sh [--skills-dir <path>] [--registry <url>] [--dry-run]
#
# Fetches all available skills from the registry and installs any not yet
# present in the skills directory.  Already-installed slugs (detected by the
# presence of .clawhub/origin.json inside each subdirectory) are skipped.

set -euo pipefail

# ── Defaults ────────────────────────────────────────────────────────────────
REGISTRY="${CLAWHUB_REGISTRY:-https://skillhub.vrprod.viveport.com}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Skill dir defaults to two levels up from scripts/ (i.e. the skills root)
SKILLS_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DRY_RUN=false
LIMIT=200

# ── Argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skills-dir)   SKILLS_DIR="$2"; shift 2 ;;
    --registry)     REGISTRY="$2";   shift 2 ;;
    --dry-run)      DRY_RUN=true;    shift   ;;
    --limit)        LIMIT="$2";      shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--skills-dir <path>] [--registry <url>] [--dry-run] [--limit <n>]"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

echo "╔════════════════════════════════════════════╗"
echo "║          ClawHub Skill Sync                ║"
echo "╚════════════════════════════════════════════╝"
echo "Registry  : $REGISTRY"
echo "Skills dir: $SKILLS_DIR"
echo "Dry-run   : $DRY_RUN"
echo ""

# ── Ensure node / npx is available ───────────────────────────────────────────
if ! command -v node &>/dev/null; then
  echo "ERROR: node is not installed or not in PATH." >&2
  exit 1
fi

# ── Fetch registry catalog ────────────────────────────────────────────────────
TMP_JSON="$(mktemp /tmp/clawhub_explore_XXXXXX.json)"
trap 'rm -f "$TMP_JSON"' EXIT

echo "▶ Fetching registry catalog (limit=$LIMIT)…"
npx --yes clawhub explore \
  --registry "$REGISTRY" \
  --limit "$LIMIT" \
  --json > "$TMP_JSON"

TOTAL=$(node -e "try{const j=JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'));console.log((j.items||[]).length);}catch(e){console.log(0);}" "$TMP_JSON")
echo "  Found $TOTAL skills in registry."
echo ""

# ── Collect already-installed slugs ──────────────────────────────────────────
TMP_INSTALLED="$(mktemp /tmp/clawhub_installed_XXXXXX.txt)"
trap 'rm -f "$TMP_JSON" "$TMP_INSTALLED"' EXIT

for origin in "$SKILLS_DIR"/*/.clawhub/origin.json; do
  [[ -f "$origin" ]] || continue
  slug=$(node -e "try{const j=JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'));process.stdout.write(j.slug||'');}catch(e){}" "$origin")
  [[ -n "$slug" ]] && echo "$slug" >> "$TMP_INSTALLED"
done

installed_count=$(wc -l < "$TMP_INSTALLED" | tr -d ' ')
echo "▶ Already installed ($installed_count):"
sort "$TMP_INSTALLED" | sed 's/^/    • /'
echo ""

# ── Compute new slugs ─────────────────────────────────────────────────────────
TMP_ALL="$(mktemp /tmp/clawhub_all_XXXXXX.txt)"
trap 'rm -f "$TMP_JSON" "$TMP_INSTALLED" "$TMP_ALL"' EXIT

node -e "const j=JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'));(j.items||[]).forEach(x=>console.log(x.slug));" "$TMP_JSON" > "$TMP_ALL"

# slugs in ALL but not in INSTALLED
TMP_NEW="$(mktemp /tmp/clawhub_new_XXXXXX.txt)"
trap 'rm -f "$TMP_JSON" "$TMP_INSTALLED" "$TMP_ALL" "$TMP_NEW"' EXIT

sort "$TMP_INSTALLED" -o "$TMP_INSTALLED"
sort "$TMP_ALL" -o "$TMP_ALL"
comm -23 "$TMP_ALL" "$TMP_INSTALLED" > "$TMP_NEW"

NEW_SLUGS=()
while IFS= read -r slug; do
  [[ -n "$slug" ]] && NEW_SLUGS+=("$slug")
done < "$TMP_NEW"

if [[ ${#NEW_SLUGS[@]} -eq 0 ]]; then
  echo "✔ All registry skills are already installed. Nothing to do."
  exit 0
fi

echo "▶ New skills to install (${#NEW_SLUGS[@]}):"
for s in "${NEW_SLUGS[@]}"; do echo "    • $s"; done
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry-run mode: skipping actual installation."
  exit 0
fi

# ── Install new skills ────────────────────────────────────────────────────────
ok=0; fail=0; failed_slugs=()

for slug in "${NEW_SLUGS[@]}"; do
  echo "  Installing: $slug"
  if npx --yes clawhub install \
       --no-input \
       --dir "$SKILLS_DIR" \
       "$slug" \
       --registry "$REGISTRY" 2>&1 | sed 's/^/    /'; then
    echo "    ✔ Done"
    ok=$((ok+1))
  else
    echo "    ✘ Failed (registry may not have bundle yet)"
    fail=$((fail+1))
    failed_slugs+=("$slug")
  fi
  echo ""
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo "════════════════════════════════════════════"
echo "Summary"
echo "  Already installed : $installed_count"
echo "  Newly installed   : $ok"
echo "  Failed            : $fail"
if [[ $fail -gt 0 ]]; then
  echo ""
  echo "  Failed slugs (server-side issue, retry later):"
  for s in "${failed_slugs[@]}"; do echo "    ✘ $s"; done
fi
echo "════════════════════════════════════════════"

[[ $fail -eq 0 ]] && exit 0 || exit 1
