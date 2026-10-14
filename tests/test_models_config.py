from services.models_config import MODELS, get_all_models


def test_every_field_has_description():
    for model in MODELS.values():
        for group in model["field_groups"]:
            for field in group["fields"]:
                assert field["description"].strip(), field["name"]


def test_models_payload_has_samples_and_starters():
    models = get_all_models()
    assert [m["key"] for m in models] == ["nt", "str"]
    for m in models:
        assert m["description"].strip()
        assert len(m["samples"]) >= 3
        assert "{label}" in m["starters"]["measure"]
        assert "{label}" in m["starters"]["dimension"]


def test_fields_endpoint_includes_descriptions(client):
    groups = client.get("/api/fields?model=str").json()["groups"]
    rgi = next(f for g in groups for f in g["fields"] if f["name"] == "rgi")
    assert "comp set" in rgi["description"].lower()


def test_unknown_model_is_400(client):
    assert client.get("/api/fields?model=bogus").status_code == 400
