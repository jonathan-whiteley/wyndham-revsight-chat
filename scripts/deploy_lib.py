"""Workspace-side deploy helpers for RevSight Chat.

Shared by the `workspace_deploy` notebook (Option A) and the bundle's grant job
(`scripts/grant_app_access.py`, Option C). Uses plain REST calls through
`WorkspaceClient().api_client` so it works with older preinstalled SDKs.
"""
import base64
import os
import re
import time

SCOPES_DEFAULT = ["sql", "dashboards.genie", "genie"]
METRIC_VIEWS = ["mv_nt_performance", "mv_str_compset"]
SETUP_HINT = ("Build the data and Genie spaces with the wyndham-revsight repo "
              "(https://github.com/jonathan-whiteley/wyndham-revsight), or fix the value in config.env.")


# ---------- config ----------

def read_config(path):
    """Parse config.env (KEY=value lines, # comments, optional quotes)."""
    values = {}
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def check_config(cfg, required):
    problems = [k for k in required if not cfg.get(k)]
    problems += [k for k, v in cfg.items() if re.search(r"<[^>]*>|CHANGE_?ME|your[-_]", v, re.I)]
    if problems:
        raise ValueError(f"Fix these in config.env, then re-run: {', '.join(sorted(set(problems)))}")


# ---------- REST ----------

class Api:
    """Thin REST wrapper around a WorkspaceClient."""

    def __init__(self, w, warehouse_id=None):
        self.w = w
        self.warehouse_id = warehouse_id

    def call(self, method, path, body=None, query=None):
        return self.w.api_client.do(method, path, body=body, query=query) or {}

    def try_call(self, method, path, body=None, query=None):
        try:
            return self.call(method, path, body, query), None
        except Exception as e:  # noqa: BLE001  (callers decide what a failure means)
            return None, str(e)

    def me(self):
        return self.call("GET", "/api/2.0/preview/scim/v2/Me")["userName"]

    def run_sql(self, statement):
        """Run one statement on the warehouse. Returns (ok, error_message)."""
        resp = self.call("POST", "/api/2.0/sql/statements",
                         {"warehouse_id": self.warehouse_id, "statement": statement, "wait_timeout": "50s"})
        while resp["status"]["state"] in ("PENDING", "RUNNING"):
            time.sleep(3)
            resp = self.call("GET", f"/api/2.0/sql/statements/{resp['statement_id']}")
        return resp["status"]["state"] == "SUCCEEDED", resp["status"].get("error", {}).get("message", "")


# ---------- steps ----------

def preflight(api, catalog, schema, genie_spaces):
    """Check warehouse, metric views and Genie spaces. Raises with a fix-it message."""
    failures = []
    wh, err = api.try_call("GET", f"/api/2.0/sql/warehouses/{api.warehouse_id}")
    if err:
        failures.append(f"warehouse {api.warehouse_id}: {err}")
    else:
        ok, err = api.run_sql("SELECT 1")
        print(f"✅ warehouse     {wh.get('name')} ({wh.get('state')})" if ok else f"❌ warehouse     {err}")
        if not ok:
            failures.append(f"warehouse {api.warehouse_id} cannot run queries for you: {err}")
    for mv in METRIC_VIEWS:
        fq = f"{catalog}.{schema}.{mv}"
        t, err = api.try_call("GET", f"/api/2.1/unity-catalog/tables/{fq}")
        print(f"✅ metric view   {fq}" if t else f"❌ metric view   {fq}")
        if not t:
            failures.append(f"{fq}: {err}")
    for name, space_id in genie_spaces.items():
        s, err = api.try_call("GET", f"/api/2.0/genie/spaces/{space_id}")
        print(f"✅ Genie space   {s.get('title')} ({space_id})" if s else f"❌ Genie space   {space_id}")
        if not s:
            failures.append(f"Genie space {space_id} ({name}): {err}")
    if failures:
        raise RuntimeError("Preflight failed:\n  - " + "\n  - ".join(failures) + f"\n\n{SETUP_HINT}")


def app_spec(app_name, warehouse_id, genie_spaces, scopes):
    return {
        "name": app_name,
        "description": "RevSight Chat: ask Wyndham revenue data with Genie agents and Genie One",
        "resources": [{"name": "sql_warehouse", "sql_warehouse": {"id": warehouse_id, "permission": "CAN_USE"}}]
        + [{"name": n, "genie_space": {"space_id": sid, "permission": "CAN_RUN"}} for n, sid in genie_spaces.items()],
        "user_api_scopes": scopes,
    }


def wait_for_compute(api, app_name, timeout_s=1200):
    start = time.time()
    while True:
        app = api.call("GET", f"/api/2.0/apps/{app_name}")
        state = app.get("compute_status", {}).get("state")
        if state == "ACTIVE":
            return app
        if state == "STOPPED":
            print("app compute is stopped, starting it")
            api.call("POST", f"/api/2.0/apps/{app_name}/start")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"app compute still {state} after {timeout_s}s")
        print(f"  compute {state}, waiting...")
        time.sleep(20)


def ensure_app(api, spec):
    """Create the app if missing, then ONE full update (a partial update wipes what it leaves out)."""
    name = spec["name"]
    existing, _ = api.try_call("GET", f"/api/2.0/apps/{name}")
    if existing:
        print(f"app {name} already exists, reusing it")
    else:
        print(f"creating app {name}")
        api.call("POST", "/api/2.0/apps", spec)
    wait_for_compute(api, name)
    app = api.call("PATCH", f"/api/2.0/apps/{name}", spec)
    bound = sorted(r["name"] for r in app.get("resources") or [])
    print("resources        ", ", ".join(bound))
    print("user scopes      ", ", ".join(app.get("user_api_scopes") or []))
    print("app service principal", app["service_principal_client_id"])
    if bound != sorted(r["name"] for r in spec["resources"]):
        raise RuntimeError("resources did not bind, see above")
    if sorted(app.get("user_api_scopes") or []) != sorted(spec["user_api_scopes"]):
        raise RuntimeError("user scopes did not bind, see above")
    return app


def grant_app_access(api, app_name, catalog, schema, genie_spaces):
    """UC grants + Genie CAN_RUN for the app's service principal.

    Returns the statements that failed (for the schema / space owner); never raises on a
    missing privilege, so a deployer with write-only access still gets a working list.
    """
    sp = api.call("GET", f"/api/2.0/apps/{app_name}")["service_principal_client_id"]
    print("app service principal", sp)
    for_owner = []
    for stmt in [f"GRANT USE CATALOG ON CATALOG `{catalog}` TO `{sp}`",
                 f"GRANT USE SCHEMA, SELECT ON SCHEMA `{catalog}`.`{schema}` TO `{sp}`"]:
        ok, err = api.run_sql(stmt)
        print(("✅ " if ok else "⚠️  ") + stmt + ("" if ok else f"\n     {err.splitlines()[0] if err else ''}"))
        if not ok:
            for_owner.append(stmt + ";")
    for space_id in genie_spaces.values():
        _, err = api.try_call("PATCH", f"/api/2.0/permissions/genie/{space_id}",
                              {"access_control_list": [{"service_principal_name": sp, "permission_level": "CAN_RUN"}]})
        print(f"✅ Can run on Genie space {space_id}" if not err else f"⚠️  Genie space {space_id}: {err}")
        if err:
            for_owner.append(f"-- In the Genie space {space_id}: Share > add service principal {sp} > Can run")
    if for_owner:
        print("\nSend these to your schema / Genie space owner, then re-run:\n")
        print("\n".join(for_owner))
    print("\nReminder: Genie One runs as each signed-in user, so every end user also needs their own")
    print(f"SELECT on {catalog}.{schema} and access to both Genie spaces.")
    return for_owner


def runtime_files(app_dir, catalog, schema):
    """Yield (relative_path, bytes) for what the app runs, mirroring scripts/deploy.sh."""
    if not os.path.isfile(f"{app_dir}/frontend/dist/index.html"):
        raise FileNotFoundError("app/frontend/dist is missing: build the frontend (npm run build) and commit dist")
    for top in ["main.py", "requirements.txt"]:
        yield top, open(f"{app_dir}/{top}", "rb").read()
    app_yaml = open(f"{app_dir}/app.yaml", encoding="utf-8").read()
    app_yaml = app_yaml.replace("{{CATALOG}}", catalog).replace("{{SCHEMA}}", schema)
    if re.search(r"\{\{[A-Z_]+\}\}", app_yaml):
        raise ValueError("unfilled placeholder in app.yaml")
    yield "app.yaml", app_yaml.encode()
    for sub in ["api", "services", "frontend/dist"]:
        for dirpath, dirnames, filenames in os.walk(f"{app_dir}/{sub}"):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "node_modules")]
            for f in filenames:
                if not f.endswith(".pyc"):
                    full = os.path.join(dirpath, f)
                    yield os.path.relpath(full, app_dir), open(full, "rb").read()


def upload_and_deploy(api, app_name, app_dir, repo_root, target, catalog, schema):
    """Replace the upload folder with the runtime files, deploy, wait, return the app URL."""
    target = target.rstrip("/")
    if (repo_root.rstrip("/") + "/").startswith(target + "/"):
        raise ValueError(f"APP_SOURCE_PATH {target} contains this repo folder; choose a separate folder")
    status, _ = api.try_call("GET", "/api/2.0/workspace/get-status", query={"path": target})
    if status:
        if not os.path.isfile(f"{target}/app.yaml"):
            raise ValueError(f"{target} exists and is not an app folder (no app.yaml); refusing to overwrite it")
        api.call("POST", "/api/2.0/workspace/delete", {"path": target, "recursive": True})
    files = list(runtime_files(app_dir, catalog, schema))
    for d in sorted({os.path.dirname(p) for p, _ in files}):
        api.call("POST", "/api/2.0/workspace/mkdirs", {"path": f"{target}/{d}".rstrip("/")})
    for rel, data in files:
        api.call("POST", "/api/2.0/workspace/import", {"path": f"{target}/{rel}", "format": "AUTO", "overwrite": True,
                                                       "content": base64.b64encode(data).decode()})
    print(f"uploaded {len(files)} files to {target}")
    dep = api.call("POST", f"/api/2.0/apps/{app_name}/deployments", {"source_code_path": target, "mode": "SNAPSHOT"})
    print("deployment", dep["deployment_id"], "started")
    while True:
        d = api.call("GET", f"/api/2.0/apps/{app_name}/deployments/{dep['deployment_id']}")
        state = d.get("status", {}).get("state")
        if state not in ("IN_PROGRESS", "PENDING", None):
            break
        time.sleep(10)
    print("deployment", state, d.get("status", {}).get("message", ""))
    if state != "SUCCEEDED":
        raise RuntimeError(f"deployment {state}: open Compute > Apps > {app_name} > Logs for details")
    return api.call("GET", f"/api/2.0/apps/{app_name}").get("url")
