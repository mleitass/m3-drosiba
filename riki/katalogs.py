"""Salīdzina IKT resursu katalogu ar ievainojamības brīdinājumu. Bez MI, bez tīkla.

Lietošana: python riki/katalogs.py dati/katalogs.csv [dati/bridinajums.json]

Rīku uzrakstīja Claude Code ārpus slēgtā tīkla; tīklā tas strādā bez MI.
Vērtība ir datos: jūsu katalogā un brīdinājumā (CERT.LV, ražotājs).
Izejas kods 1, ja kāds resurss ir skarts (der konveijera vārtiem).
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

DEFAULT_ADVISORY = Path(__file__).resolve().parent.parent / "dati" / "bridinajums.json"


def parse_version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split(".") if part.isdigit())


def load_catalogue(path: Path) -> tuple[date | None, list[dict]]:
    """Komentāru rindas sākas ar #; rinda '# atjaunināts: GGGG-MM-DD' dod datumu."""
    updated, lines = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            key, _, value = line[1:].partition(":")
            if key.strip() == "atjaunināts":
                updated = date.fromisoformat(value.strip())
        elif line.strip():
            lines.append(line)
    return updated, list(csv.DictReader(lines))


def check(row: dict, advisory: dict) -> tuple[bool | None, str]:
    """(skarts?, ko darīt). None nozīmē: nav zināms."""
    if not row["versija"]:
        return None, "versija nav zināma: jautāt uzturētājam"
    if row["produkts"] != advisory["produkts"]:
        return False, f"nav skarts ({row['produkts']})"
    version = parse_version(row["versija"])
    branch = ".".join(str(part) for part in version[:2])
    fixed = advisory["labotas"].get(branch)
    if fixed is None:
        return True, "labojuma nav: izolēt, ierobežot piekļuvi vai aizstāt"
    if version < parse_version(fixed):
        return True, f"atjaunināt uz {fixed}"
    return False, "labots"


def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(__doc__.strip().splitlines()[2])
        return 2
    updated, rows = load_catalogue(Path(argv[1]))
    advisory_path = Path(argv[2]) if len(argv) == 3 else DEFAULT_ADVISORY
    advisory = json.loads(advisory_path.read_text(encoding="utf-8"))

    print(f"Brīdinājums: {advisory['nosaukums']} ({', '.join(advisory['cve'])})")
    if updated:
        age = months_between(updated, date.today())
        print(f"Katalogs atjaunināts {updated}, pirms {age} mēn.", end="")
        print(" Vecāks par mēnesi: MK 397 30.–31. punkts." if age > 1 else "")
    print()

    affected = {}
    for row in rows:
        hit, advice = check(row, advisory)
        mark = {True: "SKARTS", False: "ok", None: "?"}[hit]
        label = f"{row['produkts']} {row['versija']}".strip()
        print(f"{row['id']:<3} {mark:<7} {label:<28} {row['pieejams_no']:<10} {advice}")
        print(f"    {row['resurss']} · uztur: {row['uztur']}")
        if hit:
            branch = ".".join(row["versija"].split(".")[:2])
            affected.setdefault(f"{row['produkts']} {branch}", []).append(row["id"])

    print()
    if affected:
        summary = " · ".join(f"{k}: {', '.join(v)}" for k, v in sorted(affected.items()))
        print(f"Skarti: {summary}")
    else:
        print("Skartu resursu nav.")
    return 1 if affected else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
