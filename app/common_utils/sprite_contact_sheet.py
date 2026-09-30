"""Renders labeled contact sheets of object sprites for visual review.

Usage (from the ``app`` directory):
    python -m common_utils.sprite_contact_sheet out.png rabbit,bunny,rabbit_nest
    python -m common_utils.sprite_contact_sheet out.png --all-new
"""

import argparse
from pathlib import Path

from common_utils.generate_object_sprites import OBJECTS_DIR, sprite_jobs
from PIL import Image, ImageDraw

CELL = 170
COLUMNS = 6
# Sand color of the game's ground tiles, so shadows and edges read as in-game.
BACKGROUND = (200, 180, 110, 255)


def contact_sheet(names, out_path):
    rows = (len(names) + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGBA", (COLUMNS * CELL, rows * (CELL + 16)), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for k, name in enumerate(names):
        x, y = (k % COLUMNS) * CELL, (k // COLUMNS) * (CELL + 16)
        path = OBJECTS_DIR / f"{name}.png"
        if path.exists():
            sprite = Image.open(path).convert("RGBA").resize((CELL, CELL))
            sheet.alpha_composite(sprite, (x, y))
        draw.text((x + 4, y + CELL), name, fill=(0, 0, 0, 255))
    sheet.convert("RGB").save(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("names", nargs="?", default="")
    parser.add_argument("--all-new", action="store_true")
    args = parser.parse_args()

    if args.all_new:
        names = [name for name, _, _ in sprite_jobs()]
    else:
        names = [n.strip() for n in args.names.split(",") if n.strip()]
    contact_sheet(names, Path(args.out))


if __name__ == "__main__":
    main()
