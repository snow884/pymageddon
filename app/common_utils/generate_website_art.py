"""Generate website illustrations from game sprites with Wan I2V.

Run from app/: python -m common_utils.generate_website_art --dry-run
Generate previews, then publish a reviewed frame with --publish --frame N.
"""

import argparse
import hashlib
from pathlib import Path

from common_utils.generate_object_sprites import load_manifest, save_manifest
from common_utils.run_comfy_graph import run_comfyui_workflow
from PIL import Image, ImageDraw, ImageFilter, ImageSequence

APP_DIR = Path(__file__).resolve().parent.parent
PICS_DIR = APP_DIR / "static/website/assets/pics"
WORKFLOW = "i2v_exported.json"
FRAMES = 17
STYLE = (
    " Preserve the reference's top-down orthographic illustrated game art:"
    " animal-shaped cars, crisp dark outlines, glossy highlights, soft painted"
    " shading, vivid colors. Fixed overhead camera, sharp readable silhouettes,"
    " consistent proportions and markings, no text."
)
NEGATIVE = (
    "photograph, photorealism, people, realistic animals, perspective camera,"
    " text, letters, watermark, logo, motion blur, blurry, duplicate cars,"
    " deformed wheels, morphing, cropped vehicles, washed out colors,"
    " flying objects, floating fruit, glowing plants, blooming flowers, debris"
)
ART = {
    "chase": {
        "size": 512,
        "sprites": [("fox", (0.32, 0.64), 0.53, -20), ("cow", (0.67, 0.38), 0.53, -20)],
        "prompt": (
            "An orange fox-shaped car chases a white black-spotted cow-shaped car"
            " along a woodland meadow trail. Both cars roll gently forward,"
            " remaining completely in frame. Preserve the meadow and leafy"
            " shrubs exactly as in the reference, all foliage stays still."
            " Nothing appears or disappears. Soft tire shadows, playful chase."
        ),
        "outputs": {"fox_chasing_cow_image.jpg": 512},
    },
    "cow_badge": {
        "size": 384,
        "sprites": [("cow", (0.5, 0.5), 0.76, -20)],
        "prompt": (
            "A single charming white cow-shaped car with black spots and pink"
            " ears, centered on a clean pale mint background. The headlights"
            " glint softly and the car gently rocks in place. Keep the original"
            " cow car shape unchanged and centered, generous clear margins."
        ),
        "outputs": {
            "simple_logo.png": 256,
            "favicon_logo_small.png": 64,
            "zoom_blur_logo.png": 256,
        },
    },
    "family": {
        "size": 384,
        "sprites": [
            ("cow", (0.36, 0.49), 0.65, -20),
            ("calf", (0.72, 0.55), 0.43, -20),
        ],
        "prompt": (
            "A white cow-shaped car and its smaller calf-shaped car together"
            " on a clean pale mint background. They gently rock side by side,"
            " glossy highlights sparkle. Preserve both cars' spotted paint"
            " and pink ears, full silhouettes, generous clear margins."
        ),
        "outputs": {"create_player_logo.png": 256},
    },
}


def art_seed(name):
    return int(hashlib.sha1(f"website_{name}".encode()).hexdigest()[:12], 16)


def place_sprite(canvas, name, center, extent, rotation):
    sprite = Image.open(APP_DIR / "static/objects" / f"{name}.png").convert("RGBA")
    sprite = sprite.crop(sprite.getchannel("A").getbbox())
    sprite = sprite.rotate(rotation, Image.Resampling.BICUBIC, expand=True)
    sprite.thumbnail((round(canvas.width * extent),) * 2, Image.Resampling.LANCZOS)
    position = (
        round(canvas.width * center[0] - sprite.width / 2),
        round(canvas.height * center[1] - sprite.height / 2),
    )
    shadow = Image.new("RGBA", canvas.size)
    shadow_sprite = Image.new("RGBA", sprite.size, (24, 54, 36, 0))
    shadow_sprite.putalpha(sprite.getchannel("A").point(lambda value: value // 4))
    shadow.alpha_composite(shadow_sprite, (position[0] + 5, position[1] + 9))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)))
    canvas.alpha_composite(sprite, position)


def build_seed(name, destination=None):
    spec = ART[name]
    size = spec["size"]
    canvas = Image.new("RGBA", (size, size), "#e1f2e8")
    if name == "chase":
        canvas = Image.new("RGBA", (size, size), "#709e55")
        draw = ImageDraw.Draw(canvas)
        draw.line(
            (size * 0.15, size, size * 0.85, 0),
            fill="#b7bd9a",
            width=round(size * 0.62),
        )
        draw.line(
            (size * 0.15, size, size * 0.85, 0), fill="#c8ceb2", width=round(size * 0.5)
        )
        for sprite, center, extent in (
            ("grass", (0.10, 0.22), 0.22),
            ("grass", (0.89, 0.79), 0.25),
            ("grass", (0.12, 0.80), 0.18),
            ("grass", (0.90, 0.20), 0.18),
        ):
            place_sprite(canvas, sprite, center, extent, 0)
    for sprite, center, extent, rotation in spec["sprites"]:
        place_sprite(canvas, sprite, center, extent, rotation)
    result = canvas.convert("RGB")
    if destination is not None:
        result.save(destination)
    return result


def generate(name, seed_path, raw_path):
    size = ART[name]["size"]
    seed = art_seed(name)
    prompt = ART[name]["prompt"] + STYLE
    mods = {
        "68": lambda node: {
            **node,
            "inputs": {**node["inputs"], "width": size, "height": size},
        },
        "100": lambda node: {
            **node,
            "inputs": {
                **node["inputs"],
                "positive_prompt": prompt,
                "negative_prompt": NEGATIVE,
            },
        },
        "105": lambda node: {**node, "inputs": {**node["inputs"], "seed": seed}},
        "106": lambda node: {**node, "inputs": {**node["inputs"], "seed": seed + 1}},
        "112": lambda node: {
            **node,
            "inputs": {**node["inputs"], "num_frames": FRAMES},
        },
        "60": lambda node: {
            **node,
            "inputs": {
                **node["inputs"],
                "format": "image/webp",
                "filename_prefix": f"website_{name}",
            },
        },
    }
    run_comfyui_workflow(
        WORKFLOW,
        str(raw_path),
        mods,
        output_node_id="60",
        input_image_path=str(seed_path),
        input_image_node_id="67",
    )
    manifest = load_manifest()
    manifest[f"website_{name}"] = {
        "kind": "website_art",
        "prompt": prompt,
        "negative_prompt": NEGATIVE,
        "seed": seed,
        "workflow": f"app/common_utils/workflow_files/{WORKFLOW}",
        "model": "Wan2.2-I2V-A14B Q5_K_M + 4-step lora",
        "source_sprites": [sprite[0] for sprite in ART[name]["sprites"]],
        "size": size,
        "frames": FRAMES,
    }
    save_manifest(manifest)


def preview(name, raw_path, directory):
    with Image.open(raw_path) as animation:
        frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(animation)]
    sheet = Image.new("RGB", (4 * 192, 2 * 218), "white")
    draw = ImageDraw.Draw(sheet)
    for cell in range(8):
        frame_index = round(cell * (len(frames) - 1) / 7)
        frame = frames[frame_index]
        sheet.paste(frame.resize((192, 192)), ((cell % 4) * 192, (cell // 4) * 218))
        draw.text(
            ((cell % 4) * 192 + 8, (cell // 4) * 218 + 196),
            f"Frame {frame_index}",
            fill="black",
        )
    sheet.save(directory / f"{name}_contact.png")


def publish(name, raw_path, frame_index):
    with Image.open(raw_path) as animation:
        if not 0 < frame_index < animation.n_frames:
            raise ValueError("Select a generated frame after frame 0, within the clip")
        animation.seek(frame_index)
        frame = animation.convert("RGB")
    if name == "chase":
        vehicle_layer = Image.new("RGBA", frame.size)
        for sprite, center, extent, rotation in ART[name]["sprites"]:
            place_sprite(vehicle_layer, sprite, center, extent, rotation)
        mask = vehicle_layer.getchannel("A").filter(ImageFilter.MaxFilter(25))
        mask = mask.filter(ImageFilter.GaussianBlur(6))
        frame = Image.composite(frame, build_seed(name), mask)
    for filename, size in ART[name]["outputs"].items():
        output = frame.resize((size, size), Image.Resampling.LANCZOS)
        if filename.endswith(".png"):
            output = output.convert("RGBA")
            mask_size = size * 4
            mask = Image.new("L", (mask_size, mask_size))
            ImageDraw.Draw(mask).ellipse((4, 4, mask_size - 5, mask_size - 5), fill=255)
            output.putalpha(mask.resize((size, size), Image.Resampling.LANCZOS))
        output.save(PICS_DIR / filename, optimize=True)
    manifest = load_manifest()
    manifest[f"website_{name}"]["postprocess"] = {
        "selected_frame": frame_index,
        "mask": "circle for PNG badges",
        "background": "source meadow outside feathered vehicle masks"
        if name == "chase"
        else "I2V frame",
        "outputs": {
            f"app/static/website/assets/pics/{filename}": size
            for filename, size in ART[name]["outputs"].items()
        },
    }
    save_manifest(manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=ART)
    parser.add_argument("--raw-dir", type=Path, default=Path("/tmp/pymageddon_website"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--frame", type=int, default=9)
    args = parser.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    for name in [args.only] if args.only else ART:
        seed_path = args.raw_dir / f"{name}_seed.png"
        raw_path = args.raw_dir / f"{name}.webp"
        if args.publish:
            publish(name, raw_path, args.frame)
            print(f"Published {name} frame {args.frame}", flush=True)
            continue
        build_seed(name, seed_path)
        print(f"Seed ready: {seed_path}", flush=True)
        if args.dry_run:
            continue
        if not raw_path.exists():
            generate(name, seed_path, raw_path)
        preview(name, raw_path, args.raw_dir)
        print(f"Preview ready: {args.raw_dir / (name + '_contact.png')}", flush=True)


if __name__ == "__main__":
    main()
