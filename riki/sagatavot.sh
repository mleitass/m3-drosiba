#!/usr/bin/env bash
# Sagatavo jūsu kopiju nodarbībai: pievieno 2 Ezerdati izmaiņas no veidnes.
# Veidne ("Use this template") izmaiņu vēsturi nekopē, tāpēc tās ielādē šeit.
# Drīkst palaist atkārtoti: otrreiz tas neko nemaina.
set -euo pipefail
cd "$(dirname "$0")/.."

VEIDNE="${VEIDNE:-https://github.com/mleitass/m3-drosiba.git}"
ZARS="vesture"
PEDEJA="noņemu atslēgu"

if git log --format=%s | grep -qxF "$PEDEJA"; then
  echo "Jau sagatavots."
  git log --oneline -3
  exit 0
fi

# Codespaces to iestata pats; citur vajag kaut ko, lai var izveidot izmaiņu.
git config user.name >/dev/null || git config user.name "M3 dalībnieks"
git config user.email >/dev/null || git config user.email "dalibnieks@m3.example"

echo "Ielādēju Ezerdati izmaiņas no veidnes..."
if ! git fetch -q --no-tags "$VEIDNE" "$ZARS"; then
  echo "KĻŪDA: neizdevās sazināties ar $VEIDNE. Pārbaudiet tīklu un mēģiniet vēlreiz."
  exit 1
fi
if ! git cherry-pick FETCH_HEAD~1 FETCH_HEAD >/dev/null; then
  git cherry-pick --abort 2>/dev/null || true
  echo "KĻŪDA: izmaiņas neizdevās pievienot. Saglabājiet savus labojumus un mēģiniet vēlreiz."
  exit 1
fi

echo "Gatavs. git log --oneline:"
git log --oneline -3
