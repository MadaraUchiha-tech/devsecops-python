#!/usr/bin/env bash
# Generate enough API traffic to push backend CPU over the HPA target (60%).
#   URL=http://careslot.local:8080 DURATION=180 CONCURRENCY=40 scripts/load-test.sh
set -euo pipefail
URL="${URL:-http://careslot.local}"
DURATION="${DURATION:-180}"
CONCURRENCY="${CONCURRENCY:-40}"
HOST_HEADER="${HOST_HEADER:-}"   # e.g. careslot.local when URL is http://localhost:8080

hdr=()
[[ -n "$HOST_HEADER" ]] && hdr=(-H "Host: $HOST_HEADER")

echo "Hitting $URL for ${DURATION}s with $CONCURRENCY workers. Watch: kubectl get hpa -n careslot -w"
end=$((SECONDS + DURATION))
worker() {
  while (( SECONDS < end )); do
    curl -s -o /dev/null "${hdr[@]}" "$URL/api/appointments/stats" || true
    curl -s -o /dev/null "${hdr[@]}" "$URL/api/appointments" || true
    curl -s -o /dev/null "${hdr[@]}" "$URL/api/patients?q=a" || true
  done
}
for _ in $(seq "$CONCURRENCY"); do worker & done
wait
echo "Load test finished"
