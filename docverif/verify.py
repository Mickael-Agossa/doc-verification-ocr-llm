"""Field-by-field comparison, weighted confidence score, decision."""
import re

from rapidfuzz import fuzz

WEIGHTS = {"surname": 0.2, "given_names": 0.15, "birth_date": 0.2,
           "birth_place": 0.1, "doc_number": 0.25, "expiry_date": 0.1}
FUZZY = {"surname", "given_names", "birth_place"}
ACCEPT, REVIEW = 0.9, 0.6


def _norm(v):
    return re.sub(r"\s+", " ", str(v).strip().lower())


def _norm_exact(v):
    return re.sub(r"[^a-z0-9]", "", str(v).lower())


def field_similarity(field, extracted, declared):
    if not extracted or not declared:
        return 0.0
    if field in FUZZY:
        return fuzz.ratio(_norm(extracted), _norm(declared)) / 100
    return 1.0 if _norm_exact(extracted) == _norm_exact(declared) else 0.0


def decide(score, accept=ACCEPT, review=REVIEW):
    return "accept" if score >= accept else "review" if score >= review else "reject"


def verify(extracted, declared, weights=None, accept=ACCEPT, review=REVIEW):
    w = weights or WEIGHTS
    total = sum(w.values())
    rows, score = [], 0.0
    for f, wt in w.items():
        sim = field_similarity(f, extracted.get(f, ""), declared.get(f, ""))
        score += wt * sim
        rows.append({"field": f, "extracted": extracted.get(f, ""),
                     "declared": declared.get(f, ""), "similarity": round(sim, 3)})
    score = round(score / total, 4)
    return {"score": score, "decision": decide(score, accept, review), "fields": rows}
