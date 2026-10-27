"""Iestatījumi. MI pakalpojuma iestatījumi ir config.ini, pārējie nāk no vides."""

import configparser
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.ini"

OMD_BASE_URL = os.getenv("OMD_BASE_URL", "http://localhost:8001")
OMD_API_TOKEN = os.getenv("OMD_API_TOKEN", "")
DB_PATH = os.getenv("EZERMALA_DB", "iesniegumi.db")


def llm_settings() -> dict:
    """MI šķirotāja iestatījumi no config.ini sadaļas [llm]."""
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE, encoding="utf-8")
    section = parser["llm"] if parser.has_section("llm") else {}
    return {
        "endpoint": section.get("endpoint", ""),
        "model": section.get("model", "ezer-llm-2026-06"),
        "api_key": section.get("api_key", ""),
        "timeout_seconds": float(section.get("timeout_seconds", "5")),
    }
