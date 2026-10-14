def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_models_lists_both_agents(client):
    r = client.get("/api/models")
    assert r.status_code == 200
    assert [m["key"] for m in r.json()] == ["nt", "str"]


def test_removed_routes_are_gone(client):
    assert client.get("/api/anomalies").status_code == 404
    assert client.get("/api/stats/data-as-of").status_code == 404
