import pytest

from services import settings
from services.genie_service import GenieService
from services.models_config import get_all_models


def test_config_endpoint_matches_config_env(client):
    cfg = client.get("/api/config").json()
    assert cfg["catalog"] == settings._FILE["CATALOG"]
    assert cfg["schema"] == settings._FILE["SCHEMA"]
    assert cfg["schema_fqn"] == f"{cfg['catalog']}.{cfg['schema']}"


def test_metric_views_live_in_configured_schema():
    prefix = f"{settings.CATALOG}.{settings.SCHEMA}."
    assert [m["metric_view"] for m in get_all_models()] == [prefix + "mv_nt_performance", prefix + "mv_str_compset"]


def test_genie_space_ids_come_from_config_env():
    svc = GenieService()
    assert svc._space("nt") == settings._FILE["GENIE_SPACE_NT"]
    assert svc._space("str") == settings._FILE["GENIE_SPACE_STR"]


def test_environment_overrides_config_env(monkeypatch):
    monkeypatch.setenv("GENIE_SPACE_NT", "space-from-env")
    assert GenieService()._space("nt") == "space-from-env"


def test_missing_setting_names_the_fix(monkeypatch):
    monkeypatch.delenv("NOT_A_SETTING", raising=False)
    with pytest.raises(RuntimeError, match="config.env"):
        settings.get("NOT_A_SETTING")
