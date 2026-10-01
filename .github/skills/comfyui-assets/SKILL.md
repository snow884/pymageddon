---
name: comfyui-assets
description: 'Generate game art (sprites, animated particle-effect flipbooks, edited images, audio) with ComfyUI via app/common_utils/run_comfy_graph.py. Use when: creating or regenerating images, I2V (image-to-video) animations, particle/VFX sprite sheets, image edits, or TTS audio; adding a new ComfyUI workflow; debugging ComfyUI queue/download failures.'
---

# Generating assets with ComfyUI (`run_comfy_graph.py`)

All generated art goes through [run_comfy_graph.py](../../../app/common_utils/run_comfy_graph.py). It loads an **API-format** workflow JSON from `app/common_utils/workflow_files/`, uploads input images, patches nodes, queues the prompt on ComfyUI, waits (WebSocket with `/history` polling fallback), and downloads the first output file of the chosen node.

- Server: `localhost:8080` (`SERVER_ADDRESS`). Check it with `curl -s localhost:8080/system_stats`. ComfyUI runs on a separate Linux GPU box, so these runs are slow (I2V takes minutes). Run batches in the background.
- Run from `app/` with `../.venv/bin/python -m common_utils.<module>`.
- The script calls `/free` before and after each run, so models are reloaded on every call. Expect overhead for each call.
- Optional env vars: `COMFYUI_READY_ATTEMPTS`, `COMFYUI_READY_DELAY_SECONDS`, `COMFYUI_PROMPT_ATTEMPTS`, `COMFYUI_HISTORY_TIMEOUT_SECONDS` (default 3600).

## Workflows

| Workflow | Use | Nodes to patch | Output node |
|---|---|---|---|
| `i_gen.json` | Flux text-to-image | `6` CLIPTextEncode `text`, `25` RandomNoise `noise_seed`, `17` BasicScheduler `steps`, `27`/`30` width/height | `9` |
| `i_gen_sprite.json` | `i_gen.json` + rembg transparent background (built by `generate_object_sprites --build-workflow`) | same as `i_gen.json` | `52` |
| `i_edit_exported.json` | Qwen image edit, 1-3 input images + prompt | `68` positive / `69` negative `prompt`; LoadImage `41`, `74`, `75` | `9` |
| `i2v_exported.json` | **Wan 2.2 image-to-video**, 49 frames, 320x320 | `100` `positive_prompt` / `negative_prompt`, `105`/`106` sampler `seed`, `112` `num_frames`, `60` VHS_VideoCombine `format`; LoadImage `67` | `60` |
| `tts_audio.json` | Text-to-speech | `65` `value` | `15` (FLAC; converted to WAV with local `ffmpeg` if the output ends in `.wav`) |

## Python API

```python
from common_utils.run_comfy_graph import run_comfyui_workflow

mods = {  # node id -> function(node_dict) -> new node_dict
    "100": lambda n: {**n, "inputs": {**n["inputs"], "positive_prompt": prompt}},
    "105": lambda n: {**n, "inputs": {**n["inputs"], "seed": seed}},
    "60": lambda n: {**n, "inputs": {**n["inputs"], "format": "image/webp"}},
}
run_comfyui_workflow(
    "i2v_exported.json", "/tmp/out.webp", mods,
    output_node_id="60",
    input_image_path="/tmp/seed.png", input_image_node_id="67",
)
```

- `input_image_path` without `input_image_node_id` puts the image into **every** `LoadImage` node. For multiple inputs, use `input_image_mappings={"41": a, "74": b}`.
- Convenience wrappers: `generate_image_from_prompt`, `generate_image_from_images_and_prompt`, `generate_video_from_image_and_prompt`, `generate_audio_from_prompt`.
- CLI (only `i_edit_exported.json`, `i2v_exported.json` and `tts_audio.json` are supported): `python -m common_utils.run_comfy_graph --workflow i2v_exported.json --image seed.png --prompt "..." --output out.mp4`.

## I2V tips (particle effects)

- **There's no local `ffmpeg`.** Set node `60` `format` to `image/webp` (or `image/gif`) so that Pillow can read the frames (`ImageSequence`). The default `video/h264-mp4` can't be decoded locally.
- For VFX, start from a seed frame on **pure black** and prompt for "isolated on a pure solid black background ... fully fades out to pure black". Build the alpha from luminance (subtract a black level of ~18), then draw the sheet with additive blending.
- Frame 0 is the seed image itself. Sample frames from 1 onward.
- Reference implementation: [generate_particle_fx.py](../../../app/common_utils/generate_particle_fx.py). It produces 4-column, 160px-per-frame sheets in `app/static/particles/fx/`. Particles reference them with `fx`, `fx_sheet` and `fx_frames` (see `app/type_defs/particles/`), and the client presets live in `FX_PRESETS` in `app/templates/play.html`.
  - New effect: add it to `EFFECTS`, then run `python -m common_utils.generate_particle_fx --only <name>`.
  - Re-roll: add `--force`. Re-pack from cached raw files in `/tmp/pymageddon_fx`: add `--postprocess-only`.

## Rules

- Record every generated asset's prompt, seed and workflow in `images/generated_sprites/manifest.json` (both generators do this). Keep seeds deterministic (they're derived from the asset name) so results can be reproduced.
- Always look at the result (`view_image` on a contact sheet or a preview composited on a dark background) before wiring an asset in.
- Workflows must be exported in ComfyUI **API format** (`{node_id: {class_type, inputs}}`), not the UI graph format. To check the options a node accepts, use `curl localhost:8080/object_info/<ClassType>`.
