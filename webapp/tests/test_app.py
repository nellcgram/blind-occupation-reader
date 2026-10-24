import os
os.environ["MOCK_LLM"] = "1"
os.environ["MAX_SCENE_CHARS"] = "1000"
os.environ["RATE_LIMIT"] = "3 per hour"
os.environ["DAILY_REQUEST_CAP"] = "4"

import pytest
import app as appmod


@pytest.fixture()
def client():
    appmod.app.config["TESTING"] = True
    appmod.limiter.reset()
    appmod._daily.update(day=None, count=0)
    return appmod.app.test_client()


def post(c, **body):
    return c.post("/api/infer", json=body)


def test_happy_path(client):
    r = post(client, scenes="He was counting something under his breath, his lips barely moving.", candidates=["paramedic"])
    assert r.status_code == 200
    d = r.get_json()
    assert d["answer"] == {"label": "Emergency department nurse", "count": appmod.VOTES}
    assert d["quotes"][0]["verified"] is True


def test_fabricated_quote_flagged(client):
    r = post(client, scenes="Something else entirely about a lighthouse keeper.")
    assert r.get_json()["quotes"][0]["verified"] is False


def test_text_cap(client):
    r = post(client, scenes="x" * 1001)
    assert r.status_code == 400 and "limit" in r.get_json()["error"]


def test_body_cap_rejected_before_parsing(client):
    r = post(client, scenes="x" * 100_000)
    assert r.status_code == 413


@pytest.mark.parametrize("body", [{}, {"scenes": ""}, {"scenes": 5}, {"scenes": "a", "candidates": "no"},
                                  {"scenes": "a", "candidates": ["x"] * 21}, {"scenes": "a", "character": "n" * 61}])
def test_bad_input(client, body):
    assert post(client, **body).status_code == 400


def test_rate_limit(client):
    codes = [post(client, scenes="a line of text").status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]


def test_daily_cap(client):
    appmod.limiter.enabled = False
    try:
        codes = [post(client, scenes="a line of text").status_code for _ in range(5)]
    finally:
        appmod.limiter.enabled = True
    assert codes == [200, 200, 200, 200, 503]


def test_sample_served(client):
    r = client.get("/sample.txt")
    assert r.status_code == 200 and "Marek" in r.get_data(as_text=True)
