#!/usr/bin/env bash
# Codespace sagatavošana. Katrs solis ir neatkarīgs: ja viens neizdodas,
# pārējie tomēr izpildās, un Codespace atveras.
cd "$(dirname "$0")/.." || exit 1

echo "1/3 Python pakotnes"
python -m pip install -q --disable-pip-version-check -r requirements-dev.txt \
  || echo "BRĪDINĀJUMS: Python pakotnes neizdevās uzstādīt"

echo "2/3 Claude Code"
curl -fsSL https://claude.ai/install.sh | bash \
  || echo "BRĪDINĀJUMS: Claude Code neizdevās uzstādīt"

echo "3/3 Git noklusējuma zars (origin/HEAD)"
git remote set-head origin -a >/dev/null 2>&1 \
  || echo "BRĪDINĀJUMS: origin/HEAD neizdevās iestatīt"

echo "Gatavs. Terminālī: make parbaude"
