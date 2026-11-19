"""Text -> structured JSON. Backends: 'rules' (regex) and 'ollama' (local LLM)."""
import json
import re

import requests

FIELDS = ["surname", "given_names", "birth_date", "birth_place", "doc_number", "expiry_date"]
_DATE = r"(\d{1,2})\s*[/.\-]\s*(\d{1,2})\s*[/.\-]\s*(\d{4})"
_PATTERNS = {
    "surname": r"surname\s*[:;]?\s*(.+)",
    "given_names": r"given\s+names?\s*[:;]?\s*(.+)",
    "birth_date": r"date\s+of\s+birth\s*[:;]?\s*" + _DATE,
    "birth_place": r"place\s+of\s+birth\s*[:;]?\s*(.+)",
    "doc_number": r"document\s+no\.?\s*[:;]?\s*([A-Z0-9 ]{6,})",
    "expiry_date": r"expiry\s+date\s*[:;]?\s*" + _DATE,
}


def extract_rules(text):
    out = {}
    for field, pat in _PATTERNS.items():
        m = re.search(pat, text, re.IGNORECASE)
        if not m:
            out[field] = ""
        elif field.endswith("_date"):
            out[field] = f"{int(m.group(1)):02d}/{int(m.group(2)):02d}/{m.group(3)}"
        else:
            out[field] = m.group(1).strip().replace(" ", "") if field == "doc_number" else m.group(1).strip()
    return out


PROMPT = """You are a strict information extractor for identity documents.
Return ONLY a JSON object with exactly these keys (string values):
{keys}
Rules: dates as DD/MM/YYYY; surname in uppercase; copy names exactly as printed;
use "" if a field is missing or uncertain; no prose, no explanation.

OCR_TEXT_START
{text}
OCR_TEXT_END
"""


def ollama_available(url="http://localhost:11434"):
    try:
        return requests.get(f"{url}/api/tags", timeout=1.5).ok
    except requests.RequestException:
        return False


def validate_schema(obj):
    if not isinstance(obj, dict):
        return None
    return {k: str(obj.get(k, "") or "").strip() for k in FIELDS}


def extract_ollama(text, model="llama3.1", url="http://localhost:11434"):
    prompt = PROMPT.format(keys=json.dumps(FIELDS), text=text[:4000])
    r = requests.post(f"{url}/api/generate", timeout=120,
                      json={"model": model, "prompt": prompt, "stream": False, "format": "json"})
    r.raise_for_status()
    s = r.json().get("response", "")
    a, b = s.find("{"), s.rfind("}")
    try:
        return validate_schema(json.loads(re.sub(r",\s*([}\]])", r"\1", s[a:b + 1])))
    except ValueError:
        return None


def extract(text, backend="rules", **kw):
    """Falls back to rules if Ollama is unreachable or returns invalid output."""
    if backend == "ollama" and ollama_available(kw.get("url", "http://localhost:11434")):
        res = extract_ollama(text, **kw)
        if res:
            return res
    return extract_rules(text)
