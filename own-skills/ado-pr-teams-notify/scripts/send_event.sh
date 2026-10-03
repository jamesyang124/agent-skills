#!/bin/bash
# send_event.sh WEBHOOK_URL payload.json [payload2.json ...]   (sleeps 30 s between files; 202 = accepted)
url="$1"; shift
for f in "$@"; do printf '%-28s ' "$(basename $f)"; curl -s -o /dev/null -w 'http=%{http_code}\n' -H 'Content-Type: application/json' --data @"$f" "$url"; sleep 30; done
