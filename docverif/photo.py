"""Crop the photo area from the card template (face comparison = future work)."""
from PIL import Image

from .synth import PHOTO_BOX


def crop_photo(path_or_img, box=PHOTO_BOX):
    img = Image.open(path_or_img) if not isinstance(path_or_img, Image.Image) else path_or_img
    return img.crop(box)
