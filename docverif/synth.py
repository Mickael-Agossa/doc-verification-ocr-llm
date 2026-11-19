"""Synthetic fictional ID cards (fixed seed) with ground truth and faulty declarations."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SURNAMES = ["Varnel", "Torquin", "Belmora", "Quillon", "Draskov", "Mirelle", "Ostrand", "Peltram"]
GIVEN = ["Alda", "Brenn", "Cosmo", "Dessa", "Elio", "Fenna", "Gavro", "Hilda", "Iven", "Jora"]
CITIES = ["Northvale", "Port Ember", "Lakemoor", "Stonehaven", "Redfield", "Aldermere"]
FIELDS = ["surname", "given_names", "birth_date", "birth_place", "doc_number", "expiry_date"]
PHOTO_BOX = (30, 110, 210, 330)  # left, top, right, bottom; shared with photo.py
SIZE = (700, 400)


def _font(size):
    for p in ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _fmt(d):
    return d.strftime("%d/%m/%Y")


def make_truth(n, seed=42):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        birth = date(1950, 1, 1) + timedelta(days=rng.randint(0, 20000))
        exp = date(2027, 1, 1) + timedelta(days=rng.randint(0, 3000))
        out.append({
            "id": f"card_{i:03d}",
            "surname": rng.choice(SURNAMES).upper(),
            "given_names": " ".join(rng.sample(GIVEN, rng.choice([1, 2]))),
            "birth_date": _fmt(birth),
            "birth_place": rng.choice(CITIES),
            "doc_number": "FL" + "".join(str(rng.randint(0, 9)) for _ in range(7)),
            "expiry_date": _fmt(exp),
        })
    return out


def _avatar(draw, seed):
    rng = random.Random(seed)
    l, t, r, b = PHOTO_BOX
    col = tuple(rng.randint(90, 220) for _ in range(3))
    draw.rectangle(PHOTO_BOX, fill=(225, 230, 240), outline=(60, 60, 60), width=2)
    cx = (l + r) // 2
    draw.ellipse((cx - 40, t + 30, cx + 40, t + 110), fill=col)
    draw.polygon([(l + 15, b - 5), (r - 15, b - 5), (cx + 50, t + 125), (cx - 50, t + 125)], fill=col)


def render_card(rec, path):
    img = Image.new("RGB", SIZE, (245, 247, 250))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, SIZE[0], 70), fill=(30, 50, 100))
    d.text((30, 15), "REPUBLIC OF FICTIONLAND", font=_font(30), fill="white")
    d.text((30, 78), "SPECIMEN - FICTIONAL DOCUMENT", font=_font(20), fill=(190, 20, 20))
    _avatar(d, rec["id"])
    rows = [("Surname", rec["surname"]), ("Given names", rec["given_names"]),
            ("Date of birth", rec["birth_date"]), ("Place of birth", rec["birth_place"]),
            ("Document No", rec["doc_number"]), ("Expiry date", rec["expiry_date"])]
    y = 115
    for label, val in rows:
        d.text((240, y), f"{label}: {val}", font=_font(26), fill=(10, 10, 10))
        y += 42
    img.save(path)
    return path


def generate_cards(n, outdir, seed=42):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    truth = make_truth(n, seed)
    for rec in truth:
        render_card(rec, outdir / f"{rec['id']}.png")
    (outdir / "truth.json").write_text(json.dumps(truth, indent=2))
    return truth


def make_declaration(rec, error=None, rng=None):
    """error in {None, 'typo', 'date', 'number'}."""
    rng = rng or random.Random(0)
    dec = {k: rec[k] for k in FIELDS}
    if error == "typo":
        s = dec["surname"]
        i = rng.randrange(1, len(s) - 1)
        dec["surname"] = s[:i] + s[i + 1] + s[i] + s[i + 2:] if s[i] != s[i + 1] else s[:i] + "X" + s[i + 1:]
    elif error == "date":
        d, m, y = dec["birth_date"].split("/")
        dec["birth_date"] = f"{d}/{m}/{int(y) + 1}"
    elif error == "number":
        n = dec["doc_number"]
        dec["doc_number"] = n[:-1] + str((int(n[-1]) + 3) % 10)
    return dec
