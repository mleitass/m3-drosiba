"""Ārējā MI pakalpojuma "ezer-llm" imitācija (izdomāts). Tīkla izsaukumu nav.

Modelis ir deterministisks. Tas no uzvednes nolasa nodaļu sarakstu un izvēlas
nodaļu, kuras pazīmes iesnieguma tekstā sastopamas visbiežāk. Vienādu punktu
gadījumā uzvar nodaļa, kas uzvednē minēta pirmā. Ja neviena pazīme neder,
modelis atbild ar kodu, ko uzvedne norāda neskaidriem gadījumiem.
"""

import re
from dataclasses import dataclass

_DEPARTMENT_LINE = re.compile(r"^- ([A-Z_]+) \([^)]*\):(.*)$", re.MULTILINE)
_FALLBACK = re.compile(r"atbildi ([A-Z_]+)")
_WORD = re.compile(r"\w+")


class ProviderError(Exception):
    """Pakalpojuma kļūda. Teksts ir īss un saprotams žurnālā."""


@dataclass(frozen=True)
class Completion:
    text: str
    model: str


def _departments(system_prompt: str) -> list[tuple[str, list[str]]]:
    result = []
    for code, keywords in _DEPARTMENT_LINE.findall(system_prompt):
        words = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        result.append((code, words))
    return result


def classify(system_prompt: str, text: str) -> str:
    """Modeļa 'domāšana': pazīmju skaitīšana. Tīra funkcija, bez stāvokļa."""
    fallback = _FALLBACK.search(system_prompt)
    best_code = fallback.group(1) if fallback else "CHANCERY"
    tokens = _WORD.findall(text.lower())
    best_score = 0
    for code, keywords in _departments(system_prompt):
        score = sum(1 for k in keywords if any(t.startswith(k) for t in tokens))
        if score > best_score:
            best_code, best_score = code, score
    return best_code


def complete(model: str, api_key: str, system_prompt: str, text: str) -> Completion:
    """Viens pieprasījums pakalpojumam. Imitācija atslēgu tikai pieprasa, nepārbauda."""
    if not api_key:
        raise ProviderError("nav API atslēgas (HTTP 401)")
    return Completion(classify(system_prompt, text), model)
