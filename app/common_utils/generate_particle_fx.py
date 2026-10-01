"""Generates animated particle-effect flipbooks with the ComfyUI I2V graph.

Each effect starts from a seed frame on pure black (built here with PIL), is
animated by Wan 2.2 I2V (``i2v_exported.json``), and the frames are packed into a
sprite sheet whose alpha is derived from luminance, so the client can draw it
with additive blending.

Usage (from the ``app`` directory):
    python -m common_utils.generate_particle_fx                  # missing sheets
    python -m common_utils.generate_particle_fx --only death --force
    python -m common_utils.generate_particle_fx --postprocess-only

Prompts and seeds are recorded in ``images/generated_sprites/manifest.json``
under ``fx_<name>`` keys.
"""

import argparse
import hashlib
from pathlib import Path

from common_utils.generate_object_sprites import load_manifest, save_manifest
from common_utils.run_comfy_graph import run_comfyui_workflow
from PIL import Image, ImageDraw, ImageFilter, ImageSequence

APP_DIR = Path(__file__).resolve().parent.parent
PARTICLES_DIR = APP_DIR / "static" / "particles"
FX_DIR = PARTICLES_DIR / "fx"
WORKFLOW = "i2v_exported.json"
OUTPUT_NODE = "60"
SEED_SIZE = 320
FRAME_SIZE = 160
COLUMNS = 4
FRAMES = 16
# Wan decodes "pure black" as a noisy near-black; this is treated as transparent.
BLACK_LEVEL = 18

STYLE = (
    " Stylized 2D game visual effect, centered, static camera, top-down view,"
    " isolated on a pure solid black background, glowing additive light,"
    " the effect fully fades out to pure black by the end."
)
NEGATIVE = (
    "background scenery, ground, floor, texture, text, watermark, camera motion,"
    " zoom, pan, blurry, grey background, white background, people, hands"
)

# name -> seed frame recipe + I2V prompt. Sheets are written to static/particles/fx.
EFFECTS = {
    "death": {
        "seed_frame": {
            "sprite": "skull.png",
            "sprite_size": 0.45,
            "glow": (150, 90, 255),
            "glow_radius": 0.2,
        },
        "prompt": (
            "The glowing skull cracks and dissolves into swirling ghostly"
            " violet and cyan soul smoke and embers that spiral upward and vanish."
        ),
        "frame_range": (6, 40),
    },
    "eat": {
        "seed_frame": {"glow": (120, 255, 90), "glow_radius": 0.12},
        "prompt": (
            "A small glowing green orb bursts into a splash of bright leaf"
            " fragments, juicy droplets and sparkles that fly outward and vanish."
        ),
        "frame_range": (19, 46),
    },
    "hatch": {
        "seed_frame": {
            "sprite": "hetching.png",
            "sprite_size": 0.5,
            "glow": (255, 210, 120),
            "glow_radius": 0.12,
        },
        "prompt": (
            "The eggshell halves burst apart in a warm golden flash of light,"
            " a ring of light expands outward with tiny shell fragments and twinkling"
            " sparkles that drift away and vanish."
        ),
        "frame_range": (1, 30),
    },
    "lay": {
        "seed_frame": {
            "sprite": "laying.png",
            "sprite_size": 0.3,
            "glow": (255, 90, 200),
            "glow_radius": 0.18,
        },
        "prompt": (
            "The glossy pink heart pulses and bursts into many small glowing"
            " pink hearts and soft sparkles that float upward and vanish."
        ),
        "frame_range": (21, 37),
    },
    "score": {
        "seed_frame": {"glow": (255, 200, 60), "glow_radius": 0.1},
        "prompt": (
            "A small golden star ignites into a radiant firework burst of"
            " glittering golden sparks and tiny stars radiating outward in all"
            " directions, then the sparks twinkle and vanish."
        ),
        "frame_range": (2, 44),
    },
}


def fx_seed(name):
    return int(hashlib.sha1(f"fx_{name}".encode()).hexdigest()[:12], 16)


def build_seed_frame(recipe, out_path):
    """Draws a soft colored glow (and optionally a sprite) centered on black."""
    size = SEED_SIZE
    canvas = Image.new("RGB", (size, size), (0, 0, 0))

    c = size // 2
    for radius, color in (
        (recipe["glow_radius"], recipe["glow"]),
        (recipe["glow_radius"] * 0.35, (255, 255, 240)),
    ):
        r = int(size * radius)
        glow = Image.new("L", (size, size), 0)
        ImageDraw.Draw(glow).ellipse((c - r, c - r, c + r, c + r), fill=255)
        glow = glow.filter(ImageFilter.GaussianBlur(r * 0.5))
        canvas.paste(Image.new("RGB", (size, size), color), (0, 0), glow)

    if "sprite" in recipe:
        sprite = Image.open(PARTICLES_DIR / recipe["sprite"]).convert("RGBA")
        sprite = sprite.crop(sprite.getchannel("A").getbbox())
        scale = size * recipe["sprite_size"] / max(sprite.size)
        sprite = sprite.resize(
            (round(sprite.width * scale), round(sprite.height * scale)), Image.LANCZOS
        )
        canvas.paste(
            sprite, ((size - sprite.width) // 2, (size - sprite.height) // 2), sprite
        )

    canvas.save(out_path)


def generate_raw(name, seed_frame_path, out_path):
    prompt = EFFECTS[name]["prompt"] + STYLE
    seed = fx_seed(name)
    mods = {
        "100": lambda n: {
            **n,
            "inputs": {
                **n["inputs"],
                "positive_prompt": prompt,
                "negative_prompt": NEGATIVE,
            },
        },
        "105": lambda n: {**n, "inputs": {**n["inputs"], "seed": seed}},
        "106": lambda n: {**n, "inputs": {**n["inputs"], "seed": seed + 1}},
        # Animated WebP can be decoded by Pillow without ffmpeg.
        "60": lambda n: {
            **n,
            "inputs": {
                **n["inputs"],
                "format": "image/webp",
                "filename_prefix": f"fx_{name}",
            },
        },
    }
    run_comfyui_workflow(
        WORKFLOW,
        str(out_path),
        mods,
        output_node_id=OUTPUT_NODE,
        input_image_path=str(seed_frame_path),
        input_image_node_id="67",
    )
    return prompt, seed


def luminance_to_alpha(frame):
    """Turns a frame on black into RGBA usable with normal or additive blending."""
    rgb = frame.convert("RGB")
    lum = rgb.convert("L").point(
        lambda v: max(0, min(255, (v - BLACK_LEVEL) * 255 // (255 - BLACK_LEVEL)))
    )
    # Fade the edges so I2V border artifacts never show up as hard squares.
    mask = Image.new("L", rgb.size, 0)
    m = rgb.width // 10
    ImageDraw.Draw(mask).ellipse((m, m, rgb.width - m, rgb.height - m), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(m))
    alpha = Image.composite(lum, Image.new("L", rgb.size, 0), mask)

    # Un-premultiply so colors stay saturated where alpha is low.
    px_rgb = rgb.load()
    px_a = alpha.load()
    out = Image.new("RGBA", rgb.size)
    px_out = out.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            a = px_a[x, y]
            if a == 0:
                px_out[x, y] = (0, 0, 0, 0)
                continue
            r, g, b = px_rgb[x, y]
            peak = max(r, g, b, 1)
            px_out[x, y] = (r * 255 // peak, g * 255 // peak, b * 255 // peak, a)
    return out


def build_sheet(name, raw_path, out_path):
    frames = [f.copy() for f in ImageSequence.Iterator(Image.open(raw_path))]
    # Frame 0 is the seed frame; frame_range trims static intros and empty tails.
    first, last = EFFECTS[name].get("frame_range", (1, len(frames) - 1))
    step = (last - first) / (FRAMES - 1)
    picks = [frames[first + round(i * step)] for i in range(FRAMES)]

    rows = (FRAMES + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGBA", (COLUMNS * FRAME_SIZE, rows * FRAME_SIZE))
    for i, frame in enumerate(picks):
        cell = luminance_to_alpha(frame).resize((FRAME_SIZE, FRAME_SIZE), Image.LANCZOS)
        sheet.paste(cell, ((i % COLUMNS) * FRAME_SIZE, (i // COLUMNS) * FRAME_SIZE))
    sheet.save(out_path, optimize=True)


def manifest_entry(name, prompt, seed):
    return {
        "image": f"app/static/particles/fx/{name}_sheet.png",
        "kind": "particle_fx",
        "prompt": prompt,
        "negative_prompt": NEGATIVE,
        "seed_frame": EFFECTS[name]["seed_frame"],
        "seed": seed,
        "workflow": f"app/common_utils/workflow_files/{WORKFLOW}",
        "model": "Wan2.2-I2V-A14B Q5_K_M + 4-step lora",
        "postprocess": {
            "frames": FRAMES,
            "columns": COLUMNS,
            "frame_size": FRAME_SIZE,
            "black_level": BLACK_LEVEL,
            "alpha": "luminance",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="comma separated effect names")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--raw-dir", default="/tmp/pymageddon_fx")
    parser.add_argument(
        "--postprocess-only",
        action="store_true",
        help="rebuild sheets from existing raw animations",
    )
    args = parser.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    FX_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()

    for name, spec in EFFECTS.items():
        if only and name not in only:
            continue
        out_path = FX_DIR / f"{name}_sheet.png"
        raw_path = raw_dir / f"{name}.webp"
        if out_path.exists() and not args.force and not args.postprocess_only:
            continue

        if not args.postprocess_only:
            print(f"=== Generating fx {name}", flush=True)
            seed_frame_path = raw_dir / f"{name}_seed.png"
            build_seed_frame(spec["seed_frame"], seed_frame_path)
            prompt, seed = generate_raw(name, seed_frame_path, raw_path)
            manifest[f"fx_{name}"] = manifest_entry(name, prompt, seed)
            save_manifest(manifest)

        build_sheet(name, raw_path, out_path)
        if f"fx_{name}" in manifest:
            manifest[f"fx_{name}"]["postprocess"]["frame_range"] = spec.get(
                "frame_range"
            )
            save_manifest(manifest)
        print(f"=== Saved {out_path}", flush=True)


if __name__ == "__main__":
    main()
