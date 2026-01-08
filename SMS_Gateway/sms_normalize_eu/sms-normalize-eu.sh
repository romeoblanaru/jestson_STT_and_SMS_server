#!/usr/bin/env bash
# sms-normalize-eu.sh
# Universal EU/EEA/UK number normalizer for SMSTools3 checkhandler.
# - Converts outgoing SMS "To:" into E.164.
# - Handles +, 00, bare country codes, and common local formats.
# - Defaults are configurable via DEFAULT_CC (env or variable below).
#
# Usage (smsd.conf):
#   checkhandler = /usr/local/bin/sms-normalize-eu.sh
#
# Notes:
# - This is heuristic. It covers main EU/EEA/UK cases well, but not perfect.
# - You can force a default country with DEFAULT_CC="+44" (for UK) or edit below.
# - It only rewrites the first To: header of an outgoing SMS file passed by smsd.
#
# Exit status:
#   0 on success (or no change needed). Non-zero to abort send (not used here).

set -euo pipefail

DEFAULT_CC="${DEFAULT_CC:-+44}"   # Fallback when we cannot infer country (set in env or edit here)

file="$1"
[ -f "$file" ] || exit 0

# Read To: (first occurrence)
orig_to=$(grep -m1 '^To:' "$file" | sed 's/^To:[[:space:]]*//')
[ -z "${orig_to:-}" ] && exit 0

# Sanitize
num=$(echo "$orig_to" | tr -d ' ()-.\t\r')
num="${num#Tel:}"     # tolerate prefixed forms
num="${num#tel:}"

# Helper: prefix '+' if matches any known country code without '+'
has_known_cc() {
  local s="$1"
  case "$s" in
    # Europe / EEA / neighbors (non-exhaustive but broad coverage)
    30*|31*|32*|33*|34*|350*|351*|352*|353*|354*|355*|356*|357*|358*|359*|\
    36*|370*|371*|372*|373*|374*|375*|376*|377*|378*|379*|380*|381*|382*|\
    383*|385*|386*|387*|389*|39*|40*|41*|420*|421*|423*|43*|44*|45*|46*|47*|\
    48*|49*|371*|372*|373*|374*|375*|376*|377*|378*|379*|380*|381*|382*|\
    383*|385*|386*|387*|389*|390*|398*|599*|7*|90*|994*|995*|996*|9955*)
      return 0 ;;
  esac
  return 1
}

# Basic international handling
if [[ "$num" =~ ^\+ ]]; then
  e164="$num"
elif [[ "$num" =~ ^00[1-9] ]]; then
  e164="+${num#00}"
elif has_known_cc "$num" ; then
  e164="+$num"
else
  # National heuristics for key European countries

  # --- UK (+44) ---
  if [[ "$num" =~ ^0?7[0-9]{9}$ ]]; then
    # 07xxxxxxxxx or 7xxxxxxxxx
    n="${num#0}"
    e164="+44${n}"
  # --- Lithuania (+370) ---
  elif [[ "$num" =~ ^8[0-9]{8}$ ]]; then
    e164="+370${num#8}"
  elif [[ "$num" =~ ^6[0-9]{7}$ ]]; then
    # bare mobile 8 digits (rare edge), assume LT
    e164="+370$num"
  # --- Germany (+49) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{9,10}$ ]]; then
    e164="+49${num#0}"
  # --- France (+33) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+33${num#0}"
  # --- Italy (+39) ---
  elif [[ "$num" =~ ^0[0-9]{9,10}$ ]]; then
    e164="+39${num#0}"
  elif [[ "$num" =~ ^3[0-9]{8,10}$ ]]; then
    e164="+39${num}"
  # --- Spain (+34) ---
  elif [[ "$num" =~ ^0?[67][0-9]{8}$ ]]; then
    n="${num#0}"
    e164="+34${n}"
  # --- Netherlands (+31) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+31${num#0}"
  # --- Belgium (+32) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+32${num#0}"
  # --- Ireland (+353) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+353${num#0}"
  # --- Portugal (+351) ---
  elif [[ "$num" =~ ^0?9[0-9]{8}$ ]]; then
    n="${num#0}"
    e164="+351${n}"
  # --- Poland (+48) ---
  elif [[ "$num" =~ ^0?[5-8][0-9]{8}$ ]]; then
    n="${num#0}"
    e164="+48${n}"
  # --- Romania (+40) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+40${num#0}"
  # --- Czechia (+420) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+420${num#0}"
  # --- Slovakia (+421) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+421${num#0}"
  # --- Austria (+43) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8,11}$ ]]; then
    e164="+43${num#0}"
  # --- Denmark (+45) ---
  elif [[ "$num" =~ ^0?[2-9][0-9]{7}$ ]]; then
    n="${num#0}"
    e164="+45${n}"
  # --- Sweden (+46) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,9}$ ]]; then
    e164="+46${num#0}"
  # --- Norway (+47) ---
  elif [[ "$num" =~ ^0?[2-9][0-9]{7}$ ]]; then
    n="${num#0}"
    e164="+47${n}"
  # --- Finland (+358) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,9}$ ]]; then
    e164="+358${num#0}"
  # --- Switzerland (+41) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+41${num#0}"
  # --- Hungary (+36) ---
  elif [[ "$num" =~ ^06[0-9]{8}$ ]]; then
    e164="+36${num#0}"
  # --- Latvia (+371) ---
  elif [[ "$num" =~ ^0?2[0-9]{7}$ ]]; then
    n="${num#0}"
    e164="+371${n}"
  # --- Estonia (+372) ---
  elif [[ "$num" =~ ^0?5[0-9]{7}$ ]]; then
    n="${num#0}"
    e164="+372${n}"
  # --- Greece (+30) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{9}$ ]]; then
    e164="+30${num#0}"
  # --- Bulgaria (+359) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8}$ ]]; then
    e164="+359${num#0}"
  # --- Slovenia (+386) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+386${num#0}"
  # --- Croatia (+385) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+385${num#0}"
  # --- Bosnia & Herzegovina (+387) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+387${num#0}"
  # --- Serbia (+381) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8,9}$ ]]; then
    e164="+381${num#0}"
  # --- Montenegro (+382) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+382${num#0}"
  # --- North Macedonia (+389) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+389${num#0}"
  # --- Ukraine (+380) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8,9}$ ]]; then
    e164="+380${num#0}"
  # --- Belarus (+375) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{8,9}$ ]]; then
    e164="+375${num#0}"
  # --- Cyprus (+357) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7}$ ]]; then
    e164="+357${num#0}"
  # --- Malta (+356) ---
  elif [[ "$num" =~ ^0?[279][0-9]{7}$ ]]; then
    n="${num#0}"
    e164="+356${n}"
  # --- Luxembourg (+352) ---
  elif [[ "$num" =~ ^0?[2456][0-9]{7,9}$ ]]; then
    n="${num#0}"
    e164="+352${n}"
  # --- Iceland (+354) ---
  elif [[ "$num" =~ ^0?[4-9][0-9]{6}$ ]]; then
    n="${num#0}"
    e164="+354${n}"
  # --- Albania (+355) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+355${num#0}"
  # --- Moldova (+373) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{7,8}$ ]]; then
    e164="+373${num#0}"
  # --- Switzerland Liechtenstein (+423) ---
  elif [[ "$num" =~ ^0[1-9][0-9]{6,8}$ ]]; then
    e164="+423${num#0}"
  else
    # Fallback: assume national for DEFAULT_CC
    n="${num#0}"
    # If it already looks like a country code without '+', fix-up
    if has_known_cc "$num"; then
      e164="+$num"
    else
      # bare digits -> default country code
      e164="${DEFAULT_CC}${n}"
      # remove duplicate '+' if DEFAULT_CC already has it
      e164="+${e164#+}"
    fi
  fi
fi

# Update To: header if changed
if [ "$e164" != "$orig_to" ]; then
  awk -v newto="$e164" '
    BEGIN{done=0}
    /^To:[[:space:]]*/ && !done { print "To: " newto; done=1; next }
    { print }
  ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
fi

exit 0
