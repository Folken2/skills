#!/usr/bin/env bash
#
# Generate a per-hire onboarding checklist + access inventory from the
# employee-onboarding skill's workflow (pre-start -> day 90 + access lifecycle).
#
# The access-inventory CSV it emits is the "source of truth" the skill's step 3
# and step 12 require: every system granted, tracked from day 1 so offboarding
# revocation is a complete, auditable checklist rather than a scramble.
#
# Usage:
#   ./onboarding-checklist.sh "Jordan Lee" "Backend Engineer" "Engineering" 2026-09-01
#   ./onboarding-checklist.sh "Jordan Lee" "Backend Engineer" "Engineering" 2026-09-01 ./out
#
# Args: NAME  ROLE  DEPARTMENT  START_DATE(YYYY-MM-DD)  [OUTPUT_DIR=.]
#
# Writes two files into OUTPUT_DIR:
#   <slug>-onboarding.md    checklist with the skill's phases as checkboxes
#   <slug>-access.csv       access inventory (fill granted/revoked as access changes)

set -euo pipefail

if [ "$#" -lt 4 ]; then
  grep '^#' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

NAME="$1"
ROLE="$2"
DEPT="$3"
START="$4"
OUTDIR="${5:-.}"

if ! printf '%s' "$START" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  echo "error: START_DATE must be YYYY-MM-DD (got '$START')" >&2
  exit 1
fi

# slug: lowercase, spaces/punctuation -> single hyphens
SLUG=$(printf '%s' "$NAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//')
mkdir -p "$OUTDIR"
CHECKLIST="$OUTDIR/$SLUG-onboarding.md"
ACCESS="$OUTDIR/$SLUG-access.csv"

cat > "$CHECKLIST" <<EOF
# Onboarding — $NAME ($ROLE, $DEPT)
Start date: $START
Manager owns ramp; HR owns structure, compliance, and access.

## Pre-start (1–2 weeks before day 1)
- [ ] Signed offer, eligibility/tax forms, policy acknowledgements collected
- [ ] Enrolled in payroll and benefits
- [ ] Hardware ordered/imaged; shipped with buffer (verify arrival before start)
- [ ] Identity, email, role-based access provisioned (least privilege)
- [ ] Every granted system recorded in $SLUG-access.csv
- [ ] Accounts staged to activate on day 1 (not before)
- [ ] Workspace/desk or remote setup ready
- [ ] Warm welcome email sent (start time, location/link, dress, agenda, who to ask)
- [ ] Team briefed that a new person is joining

## Day 1 (essentials only)
- [ ] Orientation: mission, org, policies, tools, where to get help
- [ ] Login + equipment verified working
- [ ] Manager 1:1 held; 30-60-90 expectations given IN WRITING
- [ ] Key introductions made

## First week
- [ ] Onboarding buddy assigned (a peer, not the manager)
- [ ] Role training + shadowing scheduled (focus on context over output)

## 30-60-90 milestones
- [ ] Day 30 (learn): check-in; tools/access complete; early feedback; set 60-day expectations
- [ ] Day 60 (contribute): delivering with less supervision; set 90-day goals
- [ ] Day 90 (own): full-ownership review; transition to employee-engagement lifecycle

## Access lifecycle
- [ ] Access inventory kept current as access changes (source of truth for offboarding)
EOF

cat > "$ACCESS" <<EOF
system,access_level,granted_date,granted_by,justification,revoked_date
# One row per system. Least privilege: grant only what the role needs.
# Keep this current as access changes — at departure it becomes the revocation checklist.
email,standard,$START,,core communication,
sso_identity,standard,$START,,authentication,
EOF

echo "Wrote:"
echo "  $CHECKLIST"
echo "  $ACCESS"
