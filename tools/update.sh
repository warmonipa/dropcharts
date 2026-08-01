#!/bin/bash
# Full data update pipeline for PSO Drop Charts
#
# Usage:
#   ./tools/update.sh          # Update all (BB + DC + NGC + i18n + ss)
#   ./tools/update.sh bb       # BB complete pipeline
#   ./tools/update.sh dc       # DC complete pipeline
#   ./tools/update.sh ngc      # NGC complete pipeline
#   ./tools/update.sh i18n     # Rebuild translations and derived metadata
#   ./tools/update.sh reorder  # Reorder BB monsters to canonical order
#   ./tools/update.sh align    # Synchronize EN/JA/ZH coordinates
#   ./tools/update.sh ss       # Mark SS rare drops (mark_ss.py)
set -e

cd "$(dirname "$0")/.."
ROOT=$(pwd)
TOOLS="$ROOT/tools"

GREEN='\033[0;32m'
NC='\033[0m'

step() { echo -e "\n${GREEN}==> $1${NC}"; }

TARGET="${1:-all}"

# ---------- Source ingestion ----------
ingest_bb() {
  step "Updating BB data (scraper.py → en.js, ja.js)"
  python3 "$TOOLS/scraper.py"

  python3 "$TOOLS/gen_zh.py"
  step "BB zh.js generated (gen_zh.py)"

  update_reorder
}

ingest_dc() {
  step "Updating DC data (parse_dc.py → en.js)"
  python3 "$TOOLS/parse_dc.py"
}

ingest_ngc() {
  step "Updating NGC data (parse_ngc.py → en.js, ja.js)"
  python3 "$TOOLS/parse_ngc.py"
}

# ---------- Transforms and validation ----------
update_i18n() {
  step "Rebuilding i18n translations"
  python3 "$TOOLS/build_i18n.py" "$@"
}

update_align() {
  step "Synchronizing language-independent coordinates"
  python3 "$TOOLS/sync_coordinates.py" "$@"
}

update_ss() {
  step "Marking SS rare drops"
  python3 "$TOOLS/mark_ss.py" "$@"
}

update_validate() {
  step "Validating generated datasets"
  python3 "$TOOLS/validate_alignment.py" "$@"
}

# ---------- Version-complete pipelines ----------
finalize_versions() {
  update_align "$@"
  update_ss "$@"
  update_validate "$@"
}

update_bb() {
  ingest_bb
  finalize_versions bb
}

update_dc() {
  ingest_dc
  update_i18n dc
  finalize_versions dc
}

update_ngc() {
  ingest_ngc
  update_i18n ngc
  finalize_versions ngc
}

update_reorder() {
  step "Reordering BB monsters to canonical order (reorder.py)"
  python3 "$TOOLS/reorder.py"
}

# ---------- Main ----------
case "$TARGET" in
  all)
    ingest_bb
    ingest_dc
    ingest_ngc
    update_i18n dc ngc
    finalize_versions
    echo -e "\n${GREEN}All data updated!${NC}"
    echo "Push master to deploy with GitHub Actions."
    ;;
  bb)    update_bb ;;
  dc)    update_dc ;;
  ngc)   update_ngc ;;
  i18n)
    update_i18n dc ngc
    finalize_versions dc ngc
    ;;
  align)
    update_align
    update_validate
    ;;
  reorder)
    update_reorder
    finalize_versions bb
    ;;
  ss)
    update_align
    update_ss
    update_validate
    ;;
  *)
    echo "Usage: $0 [all|bb|dc|ngc|i18n|reorder|align|ss]"
    exit 1
    ;;
esac
