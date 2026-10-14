# Databricks notebook source
# MAGIC %md
# MAGIC # 🚀 Deploy RevSight Chat from your workspace
# MAGIC
# MAGIC This notebook does everything `scripts/` does, without a laptop or the Databricks CLI.
# MAGIC Run the cells top to bottom (or **Run all**). Every step is safe to re-run.
# MAGIC
# MAGIC | Step | What happens |
# MAGIC |---|---|
# MAGIC | 1 | Read `config.env` from this folder |
# MAGIC | 2 | Check the warehouse, metric views and Genie spaces exist |
# MAGIC | 3 | Create the app (if needed) and bind its resources and user scopes |
# MAGIC | 4 | Grant the app's service principal access to the data and Genie spaces |
# MAGIC | 5 | Upload the app code and deploy it |
# MAGIC
# MAGIC **Before you start:** edit `config.env` in this folder (or ask Genie Code to). Runs on serverless; no cluster needed.
# MAGIC The logic lives in `scripts/deploy_lib.py`, shared with the bundle's grant job.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Read `config.env`
# MAGIC Same file the CLI scripts use. Blank values (other than `APP_SOURCE_PATH`) or placeholders like `<your-schema>` stop here.

# COMMAND ----------

import os
import sys

from databricks.sdk import WorkspaceClient

notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
REPO_ROOT = "/Workspace" + os.path.dirname(notebook_path)
sys.path.insert(0, f"{REPO_ROOT}/scripts")
import deploy_lib  # noqa: E402

cfg = deploy_lib.read_config(f"{REPO_ROOT}/config.env")
deploy_lib.check_config(cfg, ["APP_NAME", "CATALOG", "SCHEMA", "WAREHOUSE_ID",
                              "GENIE_SPACE_NT", "GENIE_SPACE_STR", "USER_API_SCOPES"])

api = deploy_lib.Api(WorkspaceClient(), warehouse_id=cfg["WAREHOUSE_ID"])  # this notebook's own sign-in
ME = api.me()
APP_NAME, CATALOG, SCHEMA = cfg["APP_NAME"], cfg["CATALOG"], cfg["SCHEMA"]
GENIE_SPACES = {"genie_space_nt": cfg["GENIE_SPACE_NT"], "genie_space_str": cfg["GENIE_SPACE_STR"]}
APP_SOURCE_PATH = cfg.get("APP_SOURCE_PATH") or f"/Workspace/Users/{ME}/apps/{APP_NAME}"

print(f"signed in as     {ME}")
print(f"repo folder      {REPO_ROOT}")
for k in ["APP_NAME", "CATALOG", "SCHEMA", "WAREHOUSE_ID", "GENIE_SPACE_NT", "GENIE_SPACE_STR", "USER_API_SCOPES"]:
    print(f"{k:<17}{cfg[k]}")
print(f"{'APP_SOURCE_PATH':<17}{APP_SOURCE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Preflight checks
# MAGIC This app has no data of its own. It reads the metric views and Genie spaces built by the
# MAGIC **[wyndham-revsight](https://github.com/jonathan-whiteley/wyndham-revsight)** repo. Deploy that first if anything below is missing.

# COMMAND ----------

deploy_lib.preflight(api, CATALOG, SCHEMA, GENIE_SPACES)
print("\nAll set. Continue to step 3.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create the app and bind its resources
# MAGIC Creates the app the first time (its compute takes a few minutes to start). Then sends **one** update with the
# MAGIC warehouse, both Genie spaces and the user scopes together: a partial update would wipe whatever it leaves out.

# COMMAND ----------

spec = deploy_lib.app_spec(APP_NAME, cfg["WAREHOUSE_ID"], GENIE_SPACES, cfg["USER_API_SCOPES"].split())
app = deploy_lib.ensure_app(api, spec)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Grant the app access
# MAGIC The app's service principal needs `USE CATALOG`, `USE SCHEMA` and `SELECT`, plus **Can run** on each Genie space.
# MAGIC If you don't own the schema, this cell prints the exact statements to send your schema owner and carries on.

# COMMAND ----------

for_owner = deploy_lib.grant_app_access(api, APP_NAME, CATALOG, SCHEMA, GENIE_SPACES)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Upload and deploy
# MAGIC Copies only what the app runs (`app/` without frontend sources, `package.json` or `node_modules`, plus the prebuilt
# MAGIC `frontend/dist`) to `APP_SOURCE_PATH`, fills in your catalog and schema in `app.yaml`, and deploys.

# COMMAND ----------

url = deploy_lib.upload_and_deploy(api, APP_NAME, f"{REPO_ROOT}/app", REPO_ROOT, APP_SOURCE_PATH, CATALOG, SCHEMA)
print(f"\n🎉 RevSight Chat is live: {url}")
print("First visit asks you to approve access (consent). After a change to USER_API_SCOPES, reload and approve again.")
