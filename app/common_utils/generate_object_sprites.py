"""Generates sprites for the wildlife catalog with the ComfyUI text-to-image graph.

Usage (from the ``app`` directory):
    python -m common_utils.generate_object_sprites            # missing sprites only
    python -m common_utils.generate_object_sprites --only rabbit,fawn --force
    python -m common_utils.generate_object_sprites --manifest-only
    python -m common_utils.generate_object_sprites --build-workflow

Every generated sprite is recorded (prompt, seed, parameters) in
``images/generated_sprites/manifest.json``.
"""

import argparse
import hashlib
import json
from pathlib import Path

from common_utils.run_comfy_graph import run_comfyui_workflow
from PIL import Image, ImageFilter
from type_defs.objects.wildlife_specs import (
    ANIMALS,
    INANIMATE,
    PLANTS,
)

APP_DIR = Path(__file__).resolve().parent.parent
OBJECTS_DIR = APP_DIR / "static" / "objects"
WORKFLOW_DIR = Path(__file__).resolve().parent / "workflow_files"
MANIFEST_PATH = APP_DIR.parent / "images" / "generated_sprites" / "manifest.json"
CANVAS = 676
STEPS = 28
WORKFLOW = "i_gen_sprite.json"
OUTPUT_NODE = "52"

CAR_TEMPLATE = (
    "Top-down racing game sprite: a {subject}. Seen exactly from directly overhead"
    " (orthographic top view, roof visible, no perspective). Sharp detailed digital"
    " painting, crisp dark outlines, glossy highlights, single object centered on a"
    " plain white background"
)
STATIC_TEMPLATE = (
    "Top-down view game asset of {subject}, seen from directly above, sharp detailed"
    " digital painting, crisp outlines, soft shading, vivid colors, single object"
    " centered on a plain white background"
)

# Longest side of the sprite on the 676px canvas, per kind.
TARGET_SIZE = {
    "adult": 580,
    "juvenile": 430,
    "egg": 300,
    "pupa": 300,
    "seed": 260,
    "sapling": 400,
    "plant": 560,
    "object": 540,
}

# Flux draws top-down cars nose-down; these are rotated so the front faces up.
CAR_KINDS = {"adult", "juvenile"}

# Manual orientation fixes found while reviewing generated sprites (degrees CCW).
ROTATION_OVERRIDES = {
    "calf": 0,
    "chick": 0,
    "deer": 0,
    "caterpillar": 90,
    "tadpole": 0,
}

# Seed offsets for sprites that were regenerated after review.
SEED_OFFSETS = {"snail": 1}


def build_sprite_workflow():
    """Recreates i_gen_sprite.json: i_gen.json + rembg background removal."""
    with open(WORKFLOW_DIR / "i_gen.json", encoding="utf-8") as f:
        wf = json.load(f)
    wf["27"]["inputs"].update(width=768, height=768)
    wf["30"]["inputs"].update(width=768, height=768)
    wf["6"]["inputs"]["text"] = ""
    wf["9"]["inputs"]["filename_prefix"] = "sprite_raw"
    wf["50"] = {
        "class_type": "RemBGSession+",
        "inputs": {"model": "isnet-general-use: general purpose", "providers": "CUDA"},
    }
    wf["51"] = {
        "class_type": "ImageRemoveBackground+",
        "inputs": {"rembg_session": ["50", 0], "image": ["8", 0]},
    }
    # ComfyUI masks are inverted relative to alpha.
    wf["53"] = {"class_type": "InvertMask", "inputs": {"mask": ["51", 1]}}
    wf["54"] = {
        "class_type": "JoinImageWithAlpha",
        "inputs": {"image": ["8", 0], "alpha": ["53", 0]},
    }
    wf[OUTPUT_NODE] = {
        "class_type": "SaveImage",
        "inputs": {"filename_prefix": "sprite", "images": ["54", 0]},
    }
    with open(WORKFLOW_DIR / WORKFLOW, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2)


def sprite_seed(name, extra_offset=0):
    base = int(hashlib.sha1(name.encode()).hexdigest()[:12], 16)
    return base + SEED_OFFSETS.get(name, 0) + extra_offset


def rotation_for(name, kind):
    return ROTATION_OVERRIDES.get(name, 180 if kind in CAR_KINDS else 0)


def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest):
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(dict(sorted(manifest.items())), indent=2) + "\n", encoding="utf-8"
    )


def manifest_entry(name, kind, subject, seed):
    return {
        "image": f"app/static/objects/{name}.png",
        "kind": kind,
        "subject": subject,
        "prompt": build_prompt(kind, subject),
        "seed": seed,
        "steps": STEPS,
        "workflow": f"app/common_utils/workflow_files/{WORKFLOW}",
        "model": "flux1-dev-Q4_K_S.gguf + rembg isnet-general-use",
        "resolution": [768, 768],
        "postprocess": {
            "rotation_ccw": rotation_for(name, kind),
            "longest_side": TARGET_SIZE[kind],
            "canvas": CANVAS,
        },
    }


def sprite_jobs():
    jobs = []
    for spec in ANIMALS.values():
        for stage in spec["stages"]:
            jobs.append((stage["image"], stage["kind"], stage["prompt"]))
    for spec in PLANTS.values():
        jobs.append((spec["seed"]["image"], "seed", spec["seed"]["prompt"]))
        if "sapling" in spec:
            sapling = spec["sapling"]
            jobs.append((sapling["image"], "sapling", sapling["prompt"]))
        jobs.append((spec["plant"]["image"], "plant", spec["plant"]["prompt"]))
    for spec in INANIMATE.values():
        jobs.append((spec["image"], "object", spec["prompt"]))
    return list({job[0]: job for job in jobs}.values())


def build_prompt(kind, subject):
    template = CAR_TEMPLATE if kind in CAR_KINDS else STATIC_TEMPLATE
    return template.format(subject=subject)


def generate_raw(prompt, out_path, seed):
    mods = {
        "6": lambda n: {**n, "inputs": {**n["inputs"], "text": prompt}},
        "25": lambda n: {**n, "inputs": {**n["inputs"], "noise_seed": seed}},
        "17": lambda n: {**n, "inputs": {**n["inputs"], "steps": STEPS}},
    }
    run_comfyui_workflow(WORKFLOW, str(out_path), mods, output_node_id=OUTPUT_NODE)


def postprocess(raw_path, out_path, kind, name):
    """Crops, orients, scales and shadows a sprite to match the existing art."""
    im = Image.open(raw_path).convert("RGBA")

    # Drop faint rembg halo pixels before cropping.
    alpha = im.getchannel("A").point(lambda a: 0 if a < 24 else a)
    im.putalpha(alpha)
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError(f"{raw_path} is fully transparent")
    im = im.crop(bbox)

    rotation = rotation_for(name, kind)
    if rotation:
        im = im.rotate(rotation, expand=True)

    scale = TARGET_SIZE[kind] / max(im.size)
    im = im.resize(
        (max(1, round(im.width * scale)), max(1, round(im.height * scale))),
        Image.LANCZOS,
    )

    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ox = (CANVAS - im.width) // 2
    oy = (CANVAS - im.height) // 2

    # Soft drop shadow to the lower right, like the hand-made sprites.
    shadow_alpha = Image.new("L", (CANVAS, CANVAS), 0)
    shadow_alpha.paste(
        im.getchannel("A").point(lambda a: int(a * 0.45)), (ox + 18, oy + 26)
    )
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(16))
    shadow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    shadow.putalpha(shadow_alpha)

    canvas = Image.alpha_composite(canvas, shadow)
    layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    layer.paste(im, (ox, oy))
    canvas = Image.alpha_composite(canvas, layer)
    canvas.save(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="comma separated image names")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--seed-offset", type=int, default=0)
    parser.add_argument("--raw-dir", default="/tmp/pymageddon_sprites")
    parser.add_argument(
        "--postprocess-only",
        action="store_true",
        help="re-run cropping/shadow on existing raw images",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="record prompts/seeds of existing sprites without generating",
    )
    parser.add_argument(
        "--build-workflow",
        action="store_true",
        help=f"recreate workflow_files/{WORKFLOW} from i_gen.json",
    )
    args = parser.parse_args()

    if args.build_workflow:
        build_sprite_workflow()
        return

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()

    for name, kind, subject in sprite_jobs():
        if only and name not in only:
            continue
        out_path = OBJECTS_DIR / f"{name}.png"
        raw_path = raw_dir / f"{name}.png"
        seed = sprite_seed(name, args.seed_offset)

        if args.manifest_only:
            if out_path.exists() and name not in manifest:
                manifest[name] = manifest_entry(name, kind, subject, seed)
            continue

        if out_path.exists() and not args.force and not args.postprocess_only:
            continue

        if not args.postprocess_only:
            print(f"=== Generating {name} ({kind})", flush=True)
            generate_raw(build_prompt(kind, subject), raw_path, seed)
            manifest[name] = manifest_entry(name, kind, subject, seed)
        elif name in manifest:
            manifest[name]["postprocess"]["rotation_ccw"] = rotation_for(name, kind)

        postprocess(raw_path, out_path, kind, name)
        save_manifest(manifest)
        print(f"=== Saved {out_path}", flush=True)

    save_manifest(manifest)


if __name__ == "__main__":
    main()
