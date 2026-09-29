import json
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent / "static" / "locales"
SUPPORTED_LOCALES = ("en", "pt-BR")

def load_locale(locale: str) -> dict:
  path = LOCALES_DIR / f"{locale}.json"
  with path.open(encoding="utf-8") as handle:
    return json.load(handle)

def load_server_messages() -> dict[str, dict[str, str]]:
    return {locale: load_locale(locale)["server"] for locale in SUPPORTED_LOCALES}