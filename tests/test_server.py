import json
import time
from datetime import timedelta

import fakeredis
import pytest
import server
from fastapi.testclient import TestClient
from server import (
    app,
    create_access_token,
    get_password_hash,
    time_ago,
    verify_password,
)


@pytest.fixture
def fake_redis_server(monkeypatch):
    """Patch server.r with fake Redis instance."""
    fake_r = fakeredis.FakeRedis()
    monkeypatch.setattr(server, "r", fake_r)
    return fake_r


@pytest.fixture
def client(fake_redis_server):
    """TestClient for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_header(fake_redis_server):
    """Create a test user and return authorization bearer header."""
    username = "testplayer"
    password = "secretpassword"
    hashed = get_password_hash(password)
    fake_redis_server.set(
        f"player_{username}",
        json.dumps({"username": username, "hashed_password": hashed}),
    )

    token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}, username


class TestAuthHelpers:
    def test_password_hashing_and_verification(self):
        pwd = "MySecretPassword123"
        hashed = get_password_hash(pwd)
        assert hashed != pwd
        assert verify_password(pwd, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_time_ago_intervals(self):
        assert time_ago(30) == "30 seconds ago"
        assert time_ago(120) == "2 minutes ago"
        assert time_ago(7200) == "2 hours ago"
        assert time_ago(172800) == "2 days ago"
        assert time_ago(5184000) == "2 months ago"
        assert time_ago(63072000) == "2 years ago"

    def test_token_creation_and_expiration(self):
        token = create_access_token(
            data={"sub": "adam"}, expires_delta=timedelta(minutes=5)
        )
        assert isinstance(token, str)


class TestAuthEndpoints:
    def test_create_player_success(self, client):
        response = client.post(
            "/create_player",
            json={
                "username": "newuser",
                "password": "mypassword",
                "verify_password": "mypassword",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    def test_create_player_password_mismatch(self, client):
        response = client.post(
            "/create_player",
            json={
                "username": "newuser2",
                "password": "password1",
                "verify_password": "password2",
            },
        )
        assert response.status_code == 400
        assert "match" in response.json()["detail"]

    def test_create_player_duplicate_username(self, client):
        client.post(
            "/create_player",
            json={
                "username": "dupuser",
                "password": "pwd",
                "verify_password": "pwd",
            },
        )
        response = client.post(
            "/create_player",
            json={
                "username": "dupuser",
                "password": "pwd",
                "verify_password": "pwd",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_success(self, client):
        client.post(
            "/create_player",
            json={
                "username": "loginuser",
                "password": "loginpass",
                "verify_password": "loginpass",
            },
        )
        response = client.post(
            "/token",
            json={
                "username": "loginuser",
                "password": "loginpass",
                "is_guest": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client):
        client.post(
            "/create_player",
            json={
                "username": "userfail",
                "password": "correct",
                "verify_password": "correct",
            },
        )
        response = client.post(
            "/token",
            json={
                "username": "userfail",
                "password": "wrong",
                "is_guest": False,
            },
        )
        assert response.status_code == 401

    def test_guest_login(self, client):
        response = client.post(
            "/token",
            json={
                "username": "",
                "password": "",
                "is_guest": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestGameEndpoints:
    def test_me_endpoint(self, client, auth_header):
        headers, username = auth_header
        response = client.get("/me", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"user_name": username}

    def test_new_game_player(self, client, auth_header, fake_redis_server):
        headers, username = auth_header
        response = client.post(
            "/new_game",
            headers=headers,
            json={"spectator_follow_index": None, "spectator_follow_type": None},
        )
        assert response.status_code == 200
        game_data = json.loads(fake_redis_server.get(f"game_{username}"))
        assert game_data["request_type"] == "player"

    def test_new_game_spectator(self, client, auth_header, fake_redis_server):
        headers, username = auth_header
        response = client.post(
            "/new_game",
            headers=headers,
            json={"spectator_follow_index": 5, "spectator_follow_type": "object"},
        )
        assert response.status_code == 200
        game_data = json.loads(fake_redis_server.get(f"game_{username}"))
        assert game_data["request_type"] == "spectator"
        assert game_data["spectator_follow_index"] == 5

    def test_end_game(self, client, auth_header, fake_redis_server):
        headers, username = auth_header
        response = client.post("/end_game", headers=headers)
        assert response.status_code == 200
        game_data = json.loads(fake_redis_server.get(f"game_{username}"))
        assert game_data["request_type"] == "end_game"

    def test_control_keys(self, client, auth_header, fake_redis_server):
        headers, username = auth_header
        keys = {
            "ArrowRight": True,
            "ArrowLeft": False,
            "ArrowDown": False,
            "ArrowUp": False,
        }
        response = client.post("/control", headers=headers, json=keys)
        assert response.status_code == 200
        control_data = json.loads(fake_redis_server.get(f"control_{username}"))
        assert control_data["ArrowRight"] is True

    def test_create_bot(self, client, auth_header, fake_redis_server):
        headers, username = auth_header
        response = client.post(
            "/create_bot",
            headers=headers,
            json={"code_str": "intent = 'MOVE_FORWARD'"},
        )
        assert response.status_code == 200
        bot_data = json.loads(fake_redis_server.get(f"game_{username}"))
        assert bot_data["request_type"] == "spectator"
        assert bot_data["code"] == "intent = 'MOVE_FORWARD'"

    def test_get_map_stopped(self, client, auth_header):
        headers, username = auth_header
        response = client.get("/get_map", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["global_params"]["status"] == "stopped"

    def test_get_map_running(self, client, auth_header, fake_redis_server):
        headers, username = auth_header
        now = time.time()
        map_payload = {
            "global_params": {
                "status": "running",
                "time_interval": 1,
                "map_view_size": 11,
                "map_size_x": 10,
                "epoch": 5,
                "textures": [],
                "timestamp": now,
                "new_map_timestamp": now + 1.0,
                "large_message": None,
                "title_indicative_message": None,
                "dashboard_message": "",
            },
            "player": {"object_id": "1", "object_type": "object"},
            "objects": {},
            "tiles": {},
            "particles": {},
        }
        fake_redis_server.set(f"map_{username}", json.dumps(map_payload))
        response = client.get("/get_map", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["global_params"]["status"] == "running"
        assert "time_left" in data["global_params"]

    def test_ping_and_ping2(self, client, auth_header):
        headers, _ = auth_header
        res_ping = client.get("/ping", headers=headers)
        assert res_ping.status_code == 200
        assert res_ping.json() == {"status": "success"}

        res_ping2 = client.get("/ping2/10")
        assert res_ping2.status_code == 200
        assert res_ping2.json() == "aaaaaaaaaa"

    def test_player_image(self, client):
        response = client.get("/player_image/adam")
        assert response.status_code == 200
        assert "svg" in response.headers["content-type"]
        assert b"<svg" in response.content


class TestHTMLRoutes:
    def test_html_pages(self, client, fake_redis_server):
        summary = {
            "Cow": {
                "type_name": "Cow",
                "image": "cow.png",
                "hp": 50,
                "rgb_map": "(0, 0, 0)",
                "effects": [],
                "description_long": "Long desc",
                "description_short": "Short desc",
                "objects": {},
                "families": {},
            }
        }
        fake_redis_server.set("all_objects_summary", json.dumps(summary))

        for route in [
            "/",
            "/login_page",
            "/create_player_page",
            "/create_bot_page",
            "/start_game_page",
            "/play",
            "/explorer",
            "/explorer/type/Cow/",
            "/players",
            "/world_map",
            "/robots.txt",
            "/sitemap.xml",
        ]:
            resp = client.get(route)
            assert (
                resp.status_code == 200
            ), f"Route {route} failed with {resp.status_code}"


class TestDiscoveryEndpoints:
    def test_discovery_files_without_world_summary(self, client):
        for route, media in [
            ("/robots.txt", "text/plain"),
            ("/sitemap.xml", "application/xml"),
            ("/llms.txt", "text/markdown"),
        ]:
            resp = client.get(route)
            assert resp.status_code == 200, route
            assert resp.headers["content-type"].startswith(media), route

    def test_discovery_files_list_species(self, client, fake_redis_server):
        fake_redis_server.set(
            "all_objects_summary",
            json.dumps({"Cow": {"description_short": "<p>A grazer.</p>"}}),
        )
        sitemap = client.get("/sitemap.xml").text
        assert f"{server.SITE_URL}/explorer/type/Cow/" in sitemap
        assert f"{server.SITE_URL}/players" in sitemap

        llms = client.get("/llms.txt").text
        assert llms.startswith("# Pymageddon")
        assert f"[Cow]({server.SITE_URL}/explorer/type/Cow/): A grazer." in llms

        robots = client.get("/robots.txt").text
        assert f"Sitemap: {server.SITE_URL}/sitemap.xml" in robots
        assert "Disallow: /get_map" in robots

    def test_html_has_seo_metadata(self, client):
        html = client.get("/create_bot_page").text
        assert "<title>Write a Python bot - PyMageddon</title>" in html
        assert (
            f'<link rel="canonical" href="{server.SITE_URL}/create_bot_page">' in html
        )
        assert 'href="/llms.txt"' in html
        assert (
            '<meta property="og:title" content="Write a Python bot - PyMageddon" />'
            in html
        )

        home = client.get("/").text
        assert "application/ld+json" in home
        assert '"VideoGame"' in home

    def test_openapi_metadata(self, client):
        info = client.get("/openapi.json").json()["info"]
        assert info["title"] == "Pymageddon API"
        assert "/llms.txt" in info["description"]
