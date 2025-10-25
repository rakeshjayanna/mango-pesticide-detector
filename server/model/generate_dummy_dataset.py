"""
Generate a tiny synthetic dataset at ../dataset for pipeline testing.
Creates two classes: organic (green-ish) and pesticide (yellow-ish) with simple shapes.
Usage:
  python server/model/generate_dummy_dataset.py --count 40 --size 96 96
"""
from __future__ import annotations

from pathlib import Path
import argparse
import random
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / 'dataset'


def make_image(color_bg, color_fg, size=(96, 96)):
    w, h = size
    img = Image.new('RGB', (w, h), color_bg)
    draw = ImageDraw.Draw(img)
    # Draw random circles/rectangles
    for _ in range(5):
        x1, y1 = random.randint(0, w//2), random.randint(0, h//2)
        x2, y2 = random.randint(w//2, w-1), random.randint(h//2, h-1)
        if random.random() < 0.5:
            draw.ellipse([x1, y1, x2, y2], outline=color_fg, width=2)
        else:
            draw.rectangle([x1, y1, x2, y2], outline=color_fg, width=2)
    # Light blur/noise
    if random.random() < 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    return img


def gen_class(cls_dir: Path, color_bg, color_fg, n: int, size):
    cls_dir.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        img = make_image(color_bg, color_fg, size=size)
        img.save(cls_dir / f"img_{i:03d}.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=40, help='Images per class')
    ap.add_argument('--size', type=int, nargs=2, default=[96, 96], help='Image size WxH')
    args = ap.parse_args()

    organic_dir = DATASET / 'organic'
    pesticide_dir = DATASET / 'pesticide'

    # Organic: green background, dark green edges
    gen_class(organic_dir, (40, 150, 60), (10, 80, 20), args.count, tuple(args.size))
    # Pesticide: yellow/orange background, darker orange edges
    gen_class(pesticide_dir, (245, 158, 11), (194, 120, 5), args.count, tuple(args.size))

    print(f"Synthetic dataset created under: {DATASET}")


if __name__ == '__main__':
    main()
