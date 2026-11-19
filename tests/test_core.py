import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from docverif.extract import extract_rules, validate_schema
from docverif.ocr import ocr_image, tesseract_available
from docverif.synth import generate_cards, make_declaration
from docverif.verify import decide, verify

TEXT = """REPUBLIC OF FICTIONLAND
Surname: VARNEL
Given names: Alda Brenn
Date of birth: 03/07/1984
Place of birth: Northvale
Document No: FL1234567
Expiry date: 15/02/2030
"""


def test_rules_parsing():
    r = extract_rules(TEXT)
    assert r["surname"] == "VARNEL" and r["given_names"] == "Alda Brenn"
    assert r["birth_date"] == "03/07/1984" and r["doc_number"] == "FL1234567"
    assert r["expiry_date"] == "15/02/2030" and r["birth_place"] == "Northvale"


def test_schema_validation():
    assert validate_schema([]) is None
    assert validate_schema({"surname": "A"})["birth_date"] == ""


def test_score():
    r = extract_rules(TEXT)
    assert verify(r, dict(r))["score"] == 1.0
    bad = dict(r, doc_number="FL7654321", birth_date="01/01/1990")
    assert verify(r, bad)["score"] < 1.0


def test_decisions():
    assert decide(0.95) == "accept" and decide(0.7) == "review" and decide(0.2) == "reject"


@pytest.mark.skipif(not tesseract_available(), reason="tesseract missing")
def test_ocr_roundtrip(tmp_path):
    t = generate_cards(1, tmp_path)[0]
    assert extract_rules(ocr_image(tmp_path / "card_000.png"))["doc_number"] == t["doc_number"]
