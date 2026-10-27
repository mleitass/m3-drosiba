"""Triāža (MI šķirotājs): nosaka, kurai nodaļai nodot iesniegumu.

Zināma vājā vieta: ja MI pakalpojums neatbild, darbinieks klusi izmanto
noklusējumu un iesniegumu nosūta uz Kanceleju.
"""

import logging
from dataclasses import dataclass

from app import config, llm

logger = logging.getLogger("ezermala.triage")

DEPARTMENTS = (
    ("SOCIAL", "Sociālais dienests", ("pabalst", "apkur", "aprūp", "palīdzīb")),
    ("UTILITIES", "Komunālā nodaļa", ("bedr", "atkritum", "konteiner", "ūden")),
    ("BUILDING", "Būvvalde", ("būv", "uzbrauktuv", "fasād", "jumt")),
    ("LANDSCAPING", "Labiekārtošanas nodaļa", ("park", "skvēr", "kok", "soliņ")),
)
DEFAULT_DEPARTMENT = "CHANCERY"
PROMPT = (
    "Nosaki, kurai nodaļai nodot iesniegumu.\n{nodalas}\n"
    "Ja nevari noteikt, atbildi CHANCERY."
)


@dataclass(frozen=True)
class RouteResult:
    department: str
    ok: bool
    detail: str = ""


def build_prompt() -> str:
    lines = [f"- {code} ({name}): {', '.join(words)}" for code, name, words in DEPARTMENTS]
    return PROMPT.replace("{nodalas}", "\n".join(lines))


def route(subject: str, body: str) -> RouteResult:
    settings = config.llm_settings()
    try:
        answer = llm.complete(
            model=settings["model"],
            api_key=settings["api_key"],
            system_prompt=build_prompt(),
            text=f"{subject}\n{body}",
        )
    except llm.ProviderError as exc:
        # Vājā vieta: kļūdas gadījumā sūta uz noklusējuma nodaļu (fail-open).
        logger.warning("Triāža neizdevās: %s", exc)
        return RouteResult(DEFAULT_DEPARTMENT, False, str(exc))
    known = {code for code, _, _ in DEPARTMENTS} | {DEFAULT_DEPARTMENT}
    if answer.text not in known:
        return RouteResult(DEFAULT_DEPARTMENT, True, "nezināms kods")
    return RouteResult(answer.text, True)
