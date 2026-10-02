from html.parser import HTMLParser
from io import BytesIO

import fakeredis
import pytest
import server
from common_utils import generate_website_art as art
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(server, "r", fakeredis.FakeRedis())
    with TestClient(server.app) as test_client:
        yield test_client


@pytest.mark.parametrize("name", art.ART)
def test_seed_uses_game_sprites(name, tmp_path):
    destination = tmp_path / "seed.png"
    art.build_seed(name, destination)
    with Image.open(destination) as image:
        assert image.size == (art.ART[name]["size"],) * 2
        assert image.convert("L").getextrema()[0] < 60


def test_generation_uses_i2v_and_records_recipe(monkeypatch, tmp_path):
    captured = {}
    manifest = {}

    def run_workflow(workflow, output, modifications, **kwargs):
        captured.update(workflow=workflow, output=output, **kwargs)
        captured["nodes"] = {
            node_id: modify({"inputs": {}})["inputs"]
            for node_id, modify in modifications.items()
        }

    monkeypatch.setattr(art, "run_comfyui_workflow", run_workflow)
    monkeypatch.setattr(art, "load_manifest", lambda: manifest)
    monkeypatch.setattr(art, "save_manifest", lambda value: None)
    art.generate("chase", tmp_path / "seed.png", tmp_path / "clip.webp")

    assert captured["workflow"] == "i2v_exported.json"
    assert captured["input_image_node_id"] == "67"
    assert captured["output_node_id"] == "60"
    assert captured["nodes"]["60"]["format"] == "image/webp"
    assert captured["nodes"]["112"]["num_frames"] == art.FRAMES
    assert captured["nodes"]["68"]["width"] == art.ART["chase"]["size"]
    assert captured["nodes"]["106"]["seed"] == art.art_seed("chase") + 1
    assert manifest["website_chase"]["source_sprites"] == ["fox", "cow"]
    assert manifest["website_chase"]["prompt"].endswith(art.STYLE)


@pytest.fixture
def clip(tmp_path):
    path = tmp_path / "clip.webp"
    first = Image.new("RGB", (32, 32), "red")
    second = Image.new("RGB", (32, 32), "blue")
    first.save(path, save_all=True, append_images=[second], lossless=True, duration=100)
    return path


def test_publish_generated_frame_and_transparent_badges(monkeypatch, tmp_path, clip):
    manifest = {"website_cow_badge": {}}
    monkeypatch.setattr(art, "PICS_DIR", tmp_path)
    monkeypatch.setattr(art, "load_manifest", lambda: manifest)
    monkeypatch.setattr(art, "save_manifest", lambda value: None)
    art.publish("cow_badge", clip, 1)

    for filename, size in art.ART["cow_badge"]["outputs"].items():
        with Image.open(tmp_path / filename) as image:
            assert image.size == (size, size)
            assert image.getpixel((0, 0))[3] == 0
            assert image.getpixel((size // 2, size // 2)) == (0, 0, 255, 255)
    assert manifest["website_cow_badge"]["postprocess"]["selected_frame"] == 1


@pytest.mark.parametrize("frame", [-1, 0, 2])
def test_publish_rejects_seed_and_missing_frames(frame, clip):
    with pytest.raises(ValueError, match="generated frame"):
        art.publish("cow_badge", clip, frame)


def test_contact_sheet_handles_short_clips(tmp_path, clip):
    art.preview("short", clip, tmp_path)
    with Image.open(tmp_path / "short_contact.png") as image:
        assert image.size == (768, 436)


def test_chase_preserves_background_outside_generated_vehicles(monkeypatch, tmp_path):
    clip_path = tmp_path / "chase.webp"
    size = art.ART["chase"]["size"]
    first = Image.new("RGB", (size, size), "red")
    second = Image.new("RGB", (size, size), "blue")
    first.save(clip_path, save_all=True, append_images=[second], lossless=True)
    manifest = {"website_chase": {}}
    monkeypatch.setattr(art, "PICS_DIR", tmp_path)
    monkeypatch.setattr(art, "load_manifest", lambda: manifest)
    monkeypatch.setattr(art, "save_manifest", lambda value: None)
    art.publish("chase", clip_path, 1)
    with Image.open(tmp_path / "fox_chasing_cow_image.jpg") as image:
        corner = image.getpixel((0, 0))
        assert all(
            abs(actual - expected) < 5
            for actual, expected in zip(
                corner, art.build_seed("chase").getpixel((0, 0))
            )
        )
        center = image.getpixel((round(size * 0.67), round(size * 0.38)))
        assert center[2] > 240
        assert center[0] < 10


@pytest.mark.parametrize(
    "filename,size",
    [
        (filename, size)
        for spec in art.ART.values()
        for filename, size in spec["outputs"].items()
    ],
)
def test_published_website_assets_are_served(client, filename, size):
    response = client.get(f"/static/website/assets/pics/{filename}?v=i2v-20261002")
    assert response.status_code == 200
    with Image.open(BytesIO(response.content)) as image:
        assert image.size == (size, size)
        assert not getattr(image, "is_animated", False)
        assert image.convert("L").getextrema()[0] < 60
        if filename.endswith(".png"):
            assert image.mode == "RGBA"
            assert image.getpixel((0, 0))[3] == 0
            assert image.getpixel((size // 2, size // 2))[3] == 255


class WebsiteImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag == "img" and "/assets/pics/" in values.get("src", ""):
            self.images.append(values)


@pytest.mark.parametrize(
    "route,filename",
    [
        ("/", "fox_chasing_cow_image.jpg"),
        ("/login_page", "simple_logo.png"),
        ("/create_player_page", "create_player_logo.png"),
        ("/start_game_page", "zoom_blur_logo.png"),
    ],
)
def test_pages_reference_versioned_art_with_dimensions(client, route, filename):
    response = client.get(route)
    assert response.status_code == 200
    parser = WebsiteImages()
    parser.feed(response.text)
    assert any(filename in image["src"] for image in parser.images)
    for image in parser.images:
        assert "?v=i2v-20261002" in image["src"]
        assert int(image["width"]) > 0
        assert int(image["height"]) > 0
        assert client.get(image["src"]).status_code == 200
