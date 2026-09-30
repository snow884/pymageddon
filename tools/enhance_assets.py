#!/usr/bin/env python3
"""Unify and "3D-ify" the game's sprite artwork.

The game's PNG art (app/static/objects, app/static/tiles) was produced by
different hands at different times, so some sprites are flat, hard-outlined
cutouts while others already have soft painterly shading. This script runs
every sprite through the same procedural post-processing pipeline so they
all end up with one consistent, more three-dimensional "glossy icon" look:

  1. Bump-mapped relief shading - an emboss pass over the sprite's own
     luminance is blended back in as highlight/shadow detail, faking a
     normal-mapped light source without needing a real 3D render.
  2. Ambient-occlusion edge band - the silhouette is eroded and the thin
     ring next to the outline is darkened slightly, which is what makes
     flat icons read as having volume/thickness.
  3. Soft specular highlight - a soft radial "sheen" is screened in near
     the upper-left of the sprite, mimicking a key light.
  4. Contrast / saturation normalization - small, identical bumps so every
     sprite ends up with comparable punch.
  5. Baked drop shadow - a blurred, offset silhouette shadow is composited
     underneath the sprite on a padded canvas, which is what sells the
     "floating above the ground" 3D look in a top-down game.

Tiles get a much lighter pass (relief + color only - no shadow/AO, since
that would create visible seams in a repeating ground texture).

Usage:
    python tools/enhance_assets.py --preview /tmp/asset_preview cow.png fox.png
    python tools/enhance_assets.py --apply
    python tools/enhance_assets.py --apply --only objects
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = REPO_ROOT / "app" / "static"

OBJECT_FILES = sorted((STATIC_DIR / "objects").glob("*.png"))
TILE_FILES = sorted((STATIC_DIR / "tiles").glob("*.png"))


def _emboss_bump(gray: Image.Image, strength: float) -> np.ndarray:
    """Return a signed float bump map (H, W) derived from an emboss pass."""
    emboss = gray.filter(ImageFilter.EMBOSS)
    bump = np.asarray(emboss, dtype=np.float32) - 128.0
    bump = np.clip(bump, -40.0, 40.0)
    return bump * strength


def _ao_edge_band(alpha: Image.Image, erode_px: int, darken: float) -> np.ndarray:
    """Return a 0..darken map that is strongest right at the silhouette edge."""
    eroded = alpha
    for _ in range(erode_px):
        eroded = eroded.filter(ImageFilter.MinFilter(3))
    band = ImageChops.subtract(alpha, eroded)
    band_arr = np.asarray(band, dtype=np.float32) / 255.0
    # Smooth the band so it isn't a hard ring.
    band_img = Image.fromarray((band_arr * 255).astype(np.uint8))
    band_img = band_img.filter(ImageFilter.GaussianBlur(max(1, erode_px // 2)))
    band_arr = np.asarray(band_img, dtype=np.float32) / 255.0
    return band_arr * darken


def _specular_sheen(
    size: tuple[int, int], bbox: tuple[int, int, int, int], strength: float
) -> np.ndarray:
    """Soft radial highlight positioned toward the upper-left of the artwork."""
    w, h = size
    left, top, right, bottom = bbox
    bw, bh = right - left, bottom - top
    cx = left + bw * 0.35
    cy = top + bh * 0.28
    radius = max(bw, bh) * 0.55 + 1e-6

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / radius
    falloff = np.clip(1.0 - dist, 0.0, 1.0) ** 2.2
    return falloff * strength


def _apply_rgb_enhance(
    rgb_img: Image.Image, contrast: float, saturation: float
) -> Image.Image:
    rgb_img = ImageEnhance.Contrast(rgb_img).enhance(contrast)
    rgb_img = ImageEnhance.Color(rgb_img).enhance(saturation)
    return rgb_img


def enhance_object(
    img: Image.Image,
    *,
    pad_ratio: float = 0.16,
    bump_strength: float = 0.9,
    ao_darken: float = 30.0,
    sheen_strength: float = 32.0,
    contrast: float = 1.08,
    saturation: float = 1.12,
    shadow_opacity: float = 0.55,
) -> Image.Image:
    """Full "object" treatment: relief shading + AO + sheen + drop shadow."""
    img = img.convert("RGBA")
    w, h = img.size
    pad = max(4, int(round(pad_ratio * max(w, h))))

    canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    canvas.paste(img, (pad, pad), img)
    w2, h2 = canvas.size

    alpha = canvas.split()[3]
    bbox = alpha.getbbox() or (0, 0, w2, h2)

    gray = canvas.convert("L")
    bump = _emboss_bump(gray, bump_strength)
    ao = _ao_edge_band(alpha, erode_px=max(2, pad // 6), darken=ao_darken)
    sheen = _specular_sheen((w2, h2), bbox, sheen_strength)

    rgb = np.asarray(canvas.convert("RGB"), dtype=np.float32)
    rgb += bump[..., None]
    rgb -= ao[..., None]
    rgb += sheen[..., None]
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    rgb_img = Image.fromarray(rgb, mode="RGB")
    rgb_img = _apply_rgb_enhance(rgb_img, contrast, saturation)

    shaded = Image.merge("RGBA", (*rgb_img.split(), alpha))

    # Baked drop shadow, offset down-right, sitting underneath the sprite.
    shadow_mask = alpha.filter(ImageFilter.GaussianBlur(max(2, pad * 0.22)))
    shadow_layer = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    shadow_alpha = shadow_mask.point(lambda v: min(255, int(v * shadow_opacity)))
    shadow_black = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    shadow_black.putalpha(shadow_alpha)
    dx, dy = int(pad * 0.45), int(pad * 0.6)
    shadow_layer.paste(shadow_black, (dx, dy), shadow_black)

    out = Image.alpha_composite(shadow_layer, shaded)
    return out


def enhance_tile(
    img: Image.Image,
    *,
    bump_strength: float = 0.5,
    contrast: float = 1.05,
    saturation: float = 1.08,
) -> Image.Image:
    """Light "tile" treatment: relief + color only, no shadow/AO (keeps seams intact)."""
    img = img.convert("RGBA")
    alpha = img.split()[3]
    gray = img.convert("L")
    bump = _emboss_bump(gray, bump_strength)

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    rgb += bump[..., None]
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    rgb_img = Image.fromarray(rgb, mode="RGB")
    rgb_img = _apply_rgb_enhance(rgb_img, contrast, saturation)
    return Image.merge("RGBA", (*rgb_img.split(), alpha))


def process(path: Path, kind: str) -> Image.Image:
    img = Image.open(path)
    if kind == "objects":
        return enhance_object(img)
    if kind == "tiles":
        return enhance_tile(img)
    raise ValueError(f"Unknown asset kind: {kind}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preview",
        metavar="OUT_DIR",
        help="Write processed files to OUT_DIR instead of overwriting originals.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Overwrite the real files under app/static/{objects,tiles}.",
    )
    parser.add_argument(
        "--only",
        choices=["objects", "tiles"],
        help="Restrict processing to one asset kind.",
    )
    parser.add_argument(
        "--backup",
        metavar="BACKUP_DIR",
        help="With --apply, copy originals here first (recommended).",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific filenames (basenames) to process; default is all.",
    )
    args = parser.parse_args()

    if not args.preview and not args.apply:
        parser.error("Pass --preview OUT_DIR (safe) or --apply (overwrite in place).")

    groups = []
    if args.only in (None, "objects"):
        groups.append(("objects", OBJECT_FILES))
    if args.only in (None, "tiles"):
        groups.append(("tiles", TILE_FILES))

    wanted = set(args.files) if args.files else None

    for kind, files in groups:
        for path in files:
            if wanted and path.name not in wanted:
                continue

            if args.backup:
                backup_dir = Path(args.backup) / kind
                backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup_dir / path.name)

            result = process(path, kind)

            if args.preview:
                out_dir = Path(args.preview) / kind
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / path.name
            else:
                out_path = path

            result.save(out_path, optimize=True)
            print(f"[{kind}] {path.name} -> {out_path}")


if __name__ == "__main__":
    main()
