"""OCR with Pillow preprocessing and pytesseract."""
import shutil

from PIL import Image, ImageOps


def tesseract_available():
    return shutil.which("tesseract") is not None


def preprocess(img, threshold=150, scale=2):
    g = ImageOps.grayscale(img)
    g = g.resize((g.width * scale, g.height * scale), Image.LANCZOS)
    return g.point(lambda p: 255 if p > threshold else 0)


def ocr_image(path_or_img):
    import pytesseract
    img = Image.open(path_or_img) if isinstance(path_or_img, (str, bytes)) or hasattr(path_or_img, "__fspath__") else path_or_img
    return pytesseract.image_to_string(preprocess(img), lang="eng", config="--psm 6")
