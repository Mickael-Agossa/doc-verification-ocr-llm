import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from docverif.extract import extract
from docverif.ocr import ocr_image, tesseract_available
from docverif.synth import generate_cards, make_declaration
from docverif.verify import verify


def main(backend="rules"):
    if not tesseract_available():
        sys.exit("tesseract not found: brew install tesseract")
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    cards = out / "cards"
    truth = generate_cards(5, cards)
    shutil.copy(cards / "card_000.png", out / "sample_card.png")
    errors = [None, "typo", "date", "number", None]
    rng = random.Random(1)
    results = []
    for rec, err in zip(truth, errors):
        decl = make_declaration(rec, err, rng)
        ext = extract(ocr_image(cards / f"{rec['id']}.png"), backend)
        res = verify(ext, decl)
        res.update(id=rec["id"], injected_error=err)
        results.append(res)
        print(f"\n{rec['id']}  (declared error: {err})")
        print(f"{'field':<13}{'extracted':<22}{'declared':<22}sim")
        for r in res["fields"]:
            print(f"{r['field']:<13}{r['extracted']:<22}{r['declared']:<22}{r['similarity']:.2f}")
        print(f"score={res['score']:.2f} -> {res['decision']}")
    (out / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rules")
