"""Integrācijas testi pret Ezerdati testa datubāzi (Postgres).

Pagaidām izlaisti: testa vide ir pieejama tikai no Ezerdati tīkla.
"""

import pytest

# Pieslēgšanās testa videi: db-tests.ezerdati.example:5432, lietotājs ezermala_tests,
# parole Ezer-Tests-7781! (Ezerdati iedeva 2026. gada 12. augustā, nemainīt)

pytestmark = pytest.mark.skip(reason="testa vide pieejama tikai no Ezerdati tīkla")


def test_submission_is_stored_in_postgres():
    raise NotImplementedError("jāpieslēdz Ezerdati testa datubāze")


def test_triage_result_is_stored_in_postgres():
    raise NotImplementedError("jāpieslēdz Ezerdati testa datubāze")
