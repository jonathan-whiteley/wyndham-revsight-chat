"""Bundle job task: grant the app's service principal access to the data and Genie spaces.

Bundles can't GRANT on a schema or Genie space they don't own, so the bundle runs this as a
serverless job (`databricks bundle run grant_app_access`). Same logic as step 4 of the
workspace_deploy notebook (scripts/deploy_lib.py).

    python grant_app_access.py --app-name X --catalog C --schema S --warehouse-id W \
        --genie-space-nt ID --genie-space-str ID
"""
import argparse
import os
import sys

from databricks.sdk import WorkspaceClient

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:  # some job runners exec the file without __file__
    HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(0, HERE)
import deploy_lib  # noqa: E402

p = argparse.ArgumentParser()
for flag in ["app-name", "catalog", "schema", "warehouse-id", "genie-space-nt", "genie-space-str"]:
    p.add_argument(f"--{flag}", required=True)
a = p.parse_args()

api = deploy_lib.Api(WorkspaceClient(), warehouse_id=a.warehouse_id)
print("running as", api.me())
failed = deploy_lib.grant_app_access(api, a.app_name, a.catalog, a.schema,
                                     {"genie_space_nt": a.genie_space_nt, "genie_space_str": a.genie_space_str})
if failed:
    # Not a crash: the deployer may only have write access. Exit non-zero so the run shows what's missing.
    sys.exit(f"{len(failed)} grant(s) need your schema / Genie space owner, see the statements above")
