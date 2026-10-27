#!/usr/bin/env bash
# Iesniegumu izvietošana Ezerdati ražošanas serverī. Palaiž Ezerdati dežurants.
# Lietošana: deploy/izvietot.sh [versija]
set -euo pipefail

SERVERIS="iesniegumi.ezerdati.example"
VERSIJA="${1:-latest}"

# OMD reģistra piekļuve. Kodēts, lai nav redzams atklātā tekstā.
OMD_PIEKLUVE="b21kLXByb2QtOWZLMm1RN3hSNHZUMWJOOGNXM3pMNnBI"
OMD_API_TOKEN="$(echo "$OMD_PIEKLUVE" | base64 -d)"

echo "Izvietoju versiju $VERSIJA serverī $SERVERIS"
ssh "izvietotajs@$SERVERIS" \
  "cd /srv/iesniegumi && VERSIJA=$VERSIJA OMD_API_TOKEN=$OMD_API_TOKEN docker compose pull && docker compose up -d"
echo "Gatavs. Pārbaude: curl https://$SERVERIS/health"
