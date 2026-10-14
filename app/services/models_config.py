"""RevSight Chat agent configuration.

Defines the data models (NT Performance and STR Comp Set) that are routed
to specific Genie agents and metric views.
"""

from services.settings import CATALOG, SCHEMA, fqn

MODELS = {
    "nt": {
        "key": "nt",
        "label": "NT Performance (daily)",
        "agent_name": "Wyndham NT Performance",
        "metric_view": fqn("mv_nt_performance"),
        "grain": "site x stay date (daily)",
        "space_env": "GENIE_SPACE_NT",
        "field_groups": [
            {
                "label": "Measures",
                "kind": "measure",
                "fields": [
                    {"name": "occupancy", "label": "Occupancy", "kind": "measure", "followup": "Add {label}"},
                    {"name": "adr", "label": "ADR", "kind": "measure", "followup": "Add {label}"},
                    {"name": "revpar", "label": "RevPAR", "kind": "measure", "followup": "Add {label}"},
                    {"name": "room_revenue", "label": "Room revenue", "kind": "measure", "followup": "Add {label}"},
                    {"name": "rooms_sold", "label": "Rooms sold", "kind": "measure", "followup": "Add {label}"},
                    {"name": "rooms_available", "label": "Rooms available", "kind": "measure", "followup": "Add {label}"},
                    {"name": "site_count", "label": "Site count", "kind": "measure", "followup": "Add {label}"},
                ]
            },
            {
                "label": "Time",
                "kind": "dimension",
                "fields": [
                    {"name": "stay_date", "label": "Stay date", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "week_start", "label": "Week", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "month", "label": "Month", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "quarter", "label": "Quarter", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "year", "label": "Year", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "day_of_week", "label": "Day of week", "kind": "dimension", "followup": "Break that down by {label}"},
                ]
            },
            {
                "label": "Property",
                "kind": "dimension",
                "fields": [
                    {"name": "site_id", "label": "Site", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "property_name", "label": "Property name", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "brand", "label": "Brand", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "chain_scale", "label": "Chain scale", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "ownership", "label": "Ownership", "kind": "dimension", "followup": "Break that down by {label}"},
                ]
            },
            {
                "label": "Geography",
                "kind": "dimension",
                "fields": [
                    {"name": "state", "label": "State", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "city", "label": "City", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "market", "label": "Market", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "region", "label": "Region", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "hurricane_market", "label": "Hurricane market", "kind": "dimension", "followup": "Break that down by {label}"},
                ]
            },
        ]
    },
    "str": {
        "key": "str",
        "label": "STR Comp Set (weekly)",
        "agent_name": "Wyndham STR Comp Set",
        "metric_view": fqn("mv_str_compset"),
        "grain": "site x week (complete comp weeks only)",
        "space_env": "GENIE_SPACE_STR",
        "field_groups": [
            {
                "label": "Index measures",
                "kind": "measure",
                "fields": [
                    {"name": "rgi", "label": "RGI", "kind": "measure", "followup": "Add {label}"},
                    {"name": "mpi", "label": "MPI", "kind": "measure", "followup": "Add {label}"},
                    {"name": "ari", "label": "ARI", "kind": "measure", "followup": "Add {label}"},
                ]
            },
            {
                "label": "Own vs comp",
                "kind": "measure",
                "fields": [
                    {"name": "revpar", "label": "RevPAR", "kind": "measure", "followup": "Add {label}"},
                    {"name": "comp_revpar", "label": "Comp RevPAR", "kind": "measure", "followup": "Add {label}"},
                    {"name": "adr", "label": "ADR", "kind": "measure", "followup": "Add {label}"},
                    {"name": "comp_adr", "label": "Comp ADR", "kind": "measure", "followup": "Add {label}"},
                    {"name": "occupancy", "label": "Occupancy", "kind": "measure", "followup": "Add {label}"},
                    {"name": "comp_occupancy", "label": "Comp occupancy", "kind": "measure", "followup": "Add {label}"},
                ]
            },
            {
                "label": "Time",
                "kind": "dimension",
                "fields": [
                    {"name": "week_start", "label": "Week", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "month", "label": "Month", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "year", "label": "Year", "kind": "dimension", "followup": "Break that down by {label}"},
                ]
            },
            {
                "label": "Property",
                "kind": "dimension",
                "fields": [
                    {"name": "site_id", "label": "Site", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "property_name", "label": "Property name", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "brand", "label": "Brand", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "chain_scale", "label": "Chain scale", "kind": "dimension", "followup": "Break that down by {label}"},
                ]
            },
            {
                "label": "Geography",
                "kind": "dimension",
                "fields": [
                    {"name": "state", "label": "State", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "market", "label": "Market", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "region", "label": "Region", "kind": "dimension", "followup": "Break that down by {label}"},
                    {"name": "hurricane_market", "label": "Hurricane market", "kind": "dimension", "followup": "Break that down by {label}"},
                ]
            },
        ]
    }
}

# One-line meaning of each field, shown in the Dimensions/Measures rail so users know what they can ask.
FIELD_DESCRIPTIONS = {
    "occupancy": "Rooms sold / rooms available",
    "adr": "Average daily rate: room revenue / rooms sold",
    "revpar": "Revenue per available room: room revenue / rooms available",
    "room_revenue": "Total room revenue (USD)",
    "rooms_sold": "Room nights sold",
    "rooms_available": "Room nights available",
    "site_count": "Distinct properties reporting",
    "stay_date": "Night of stay (daily grain)",
    "week_start": "Week beginning Sunday",
    "month": "Calendar month",
    "quarter": "Calendar quarter",
    "year": "Calendar year",
    "day_of_week": "Day of week of the stay",
    "site_id": "Property code, e.g. S04217",
    "property_name": "Hotel name",
    "brand": "Wyndham brand (Days Inn, La Quinta, Super 8, ...)",
    "chain_scale": "Economy through Upper Upscale",
    "ownership": "Franchised or managed",
    "state": "US state or Canadian province",
    "city": "Property city",
    "market": "STR-style market, e.g. Tampa",
    "region": "US region or Canada",
    "hurricane_market": "Gulf or Atlantic coastal market flag",
    "rgi": "RevPAR index vs comp set (100 = fair share)",
    "mpi": "Occupancy index vs comp set (100 = fair share)",
    "ari": "ADR index vs comp set (100 = fair share)",
    "comp_revpar": "Comp set RevPAR",
    "comp_adr": "Comp set ADR",
    "comp_occupancy": "Comp set occupancy",
}

MODEL_EXTRAS = {
    "nt": {
        "description": "Daily NT performance for about 9,000 Wyndham sites: occupancy, ADR, RevPAR and revenue.",
        "samples": [
            "RevPAR, ADR and occupancy by chain scale for September 2026 vs September 2025",
            "Which hurricane-market sites had the biggest RevPAR decline in September 2026 vs September 2025?",
            "Anything that looks like a data issue in September?",
        ],
        "starters": {
            "measure": "{label} by chain scale for September 2026 vs September 2025",
            "dimension": "RevPAR, ADR and occupancy by {label} for September 2026 vs September 2025",
        },
    },
    "str": {
        "description": "Weekly STR comp set benchmarks: RGI, MPI, ARI and own vs comp metrics.",
        "samples": [
            "Weekly RGI vs comp set by chain scale, hurricane vs non-hurricane, Aug-Sep 2026",
            "Which sites had the largest RevPAR index drop vs comp set in the last 8 weeks?",
            "RGI by region for September 2026",
        ],
        "starters": {
            "measure": "{label} by chain scale, weekly for Aug-Sep 2026",
            "dimension": "RGI, MPI and ARI by {label} for September 2026",
        },
    },
}

for _key, _cfg in MODELS.items():
    _cfg.update(MODEL_EXTRAS[_key])
    for _group in _cfg["field_groups"]:
        for _field in _group["fields"]:
            _field["description"] = FIELD_DESCRIPTIONS[_field["name"]]


def get_model_config(model_key):
    """Retrieve model configuration by key."""
    if model_key not in MODELS:
        raise ValueError(f"Unknown model: {model_key}")
    return MODELS[model_key]


def get_all_models():
    """Return list of all agents for the /models endpoint."""
    keys = ("key", "label", "agent_name", "metric_view", "grain", "description", "samples", "starters")
    return [{k: cfg[k] for k in keys} for cfg in MODELS.values()]


def get_app_config():
    """Catalog and schema the app reads, for UI text such as Genie One starters."""
    return {"catalog": CATALOG, "schema": SCHEMA, "schema_fqn": f"{CATALOG}.{SCHEMA}"}
