#!/usr/bin/env bash
# Pirms nodarbības: vai Codespace ir gatavs? Neko nemaina, izņemot origin/HEAD.
cd "$(dirname "$0")/.." || exit 1

VEIDNE="${VEIDNE:-https://github.com/mleitass/m3-drosiba.git}"
PY="${PY:-python}"
kludas=0

ok() { echo "  ✓ $1"; }
bridinajums() { echo "  ! $1"; }
kluda() { echo "  ✗ $1"; kludas=$((kludas + 1)); }

echo "Pārbaude: m3-drosiba"

if "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then
  ok "Python $("$PY" -c 'import platform; print(platform.python_version())')"
else
  kluda "Vajag Python 3.9 vai jaunāku (spraudnim claude-security). Pārbūvējiet Codespace."
fi

if "$PY" -c 'import fastapi, requests' 2>/dev/null; then
  ok "Python pakotnes"
else
  bridinajums "Python pakotnes nav uzstādītas: pip install -r requirements-dev.txt (nodarbībai nav obligāti)"
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  kluda "Šī mape nav Git repozitorijs. Atveriet Codespace no sava repozitorija."
else
  ok "Git $(git --version | awk '{print $3}')"
  origin="$(git remote get-url origin 2>/dev/null || true)"
  if [[ -z "$origin" ]]; then
    kluda "Nav origin. Atveriet Codespace no sava repozitorija GitHub."
  elif [[ "$origin" == *"mleitass/m3-drosiba"* ]]; then
    kluda "Jūs strādājat veidnē, nevis savā kopijā. Spiediet Use this template → Create a new repository."
  else
    ok "Jūsu repozitorijs: ${origin#https://github.com/}"
  fi
  if ! git rev-parse -q --verify origin/HEAD >/dev/null; then
    git remote set-head origin -a >/dev/null 2>&1 || true
  fi
  if git rev-parse -q --verify origin/HEAD >/dev/null; then
    ok "origin/HEAD → $(git rev-parse --abbrev-ref origin/HEAD)"
  else
    kluda "Nav origin/HEAD. Terminālī: git remote set-head origin -a"
  fi
fi

if command -v gh >/dev/null 2>&1; then
  redzamiba="$(gh repo view --json visibility -q .visibility 2>/dev/null || true)"
  if [[ "$redzamiba" == "PUBLIC" ]]; then
    bridinajums "Repozitorijs ir publisks. Ieteicams Private: Settings → General → Danger Zone."
  elif [[ -n "$redzamiba" ]]; then
    ok "Repozitorijs: $redzamiba"
  fi
fi

if git ls-remote --exit-code -q "$VEIDNE" vesture >/dev/null 2>&1; then
  ok "Veidne sasniedzama (make sagatavot strādās)"
else
  kluda "Nevar sasniegt $VEIDNE. Pārbaudiet tīklu."
fi

if grep -q '"claude-security@claude-plugins-official": true' .claude/settings.json 2>/dev/null; then
  ok "Spraudnis claude-security ieslēgts repozitorija iestatījumos"
else
  kluda "Failā .claude/settings.json nav claude-security. Atjaunojiet to no veidnes."
fi

if command -v claude >/dev/null 2>&1; then
  ok "Claude Code $(claude --version 2>/dev/null | awk '{print $1}')"
else
  bridinajums "Claude Code komanda terminālī nav atrasta. Paplašinājums strādā arī bez tās."
fi

echo
if (( kludas == 0 )); then
  echo "Viss gatavs. Vēl Claude Code paplašinājumā: pieteikties, /plugins rāda claude-security."
  echo "Pēc tam apturiet Codespace (Stop), neizdzēsiet to."
else
  echo "Jālabo: $kludas. Ja nesanāk, rakstiet pasniedzējam un pievienojiet šo izvadi."
  exit 1
fi
