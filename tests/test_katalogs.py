"""riki/katalogs.py: kataloga un brīdinājuma salīdzināšana."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("katalogs", ROOT / "riki" / "katalogs.py")
katalogs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(katalogs)

ADVISORY = {"produkts": "PHP", "labotas": {"8.2": "8.2.35", "8.3": "8.3.36"}}


def row(product, version):
    return {"produkts": product, "versija": version}


def test_old_branch_has_no_fix():
    assert katalogs.check(row("PHP", "8.1.31"), ADVISORY)[0] is True


def test_patch_below_fixed_is_affected():
    assert katalogs.check(row("PHP", "8.3.30"), ADVISORY) == (True, "atjaunināt uz 8.3.36")


def test_fixed_version_is_ok():
    assert katalogs.check(row("PHP", "8.2.35"), ADVISORY)[0] is False


def test_unknown_version_is_unknown():
    assert katalogs.check(row("ražotāja programmatūra", ""), ADVISORY)[0] is None


def test_catalogue_summary(capsys):
    code = katalogs.main(["katalogs.py", str(ROOT / "dati" / "katalogs.csv")])
    out = capsys.readouterr().out
    assert code == 1
    assert "Skarti: PHP 8.1: K2 · PHP 8.2: K4 · PHP 8.3: K3" in out
