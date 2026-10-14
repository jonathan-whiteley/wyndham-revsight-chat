#!/bin/zsh
# Create the app if it does not exist, then bind its resources and user scopes
# from config.env: SQL warehouse (CAN_USE), both Genie spaces (CAN_RUN) and the
# on-behalf-of user scopes.
#
# Sends everything in ONE update: `apps update` replaces the whole object, so a
# partial update (for example scopes only) silently clears the resources.
# Run scripts/deploy.sh afterwards; the redeploy is what grants the app's
# service principal access and fills the valueFrom env vars.
set -euo pipefail
ROOT=${0:A:h:h}
source "$ROOT/config.env"
PROFILE=(--profile "$DATABRICKS_PROFILE")
SPEC=$(mktemp)

python3 - "$SPEC" <<EOF
import json, sys
spec = {
    "name": "$APP_NAME",
    "description": "RevSight Chat: ask Wyndham revenue data with Genie agents and Genie One",
    "resources": [
        {"name": "sql_warehouse", "sql_warehouse": {"id": "$WAREHOUSE_ID", "permission": "CAN_USE"}},
        {"name": "genie_space_nt", "genie_space": {"space_id": "$GENIE_SPACE_NT", "permission": "CAN_RUN"}},
        {"name": "genie_space_str", "genie_space": {"space_id": "$GENIE_SPACE_STR", "permission": "CAN_RUN"}},
    ],
    "user_api_scopes": "$USER_API_SCOPES".split(),
}
json.dump(spec, open(sys.argv[1], "w"))
EOF

if ! databricks apps get "$APP_NAME" "${PROFILE[@]}" >/dev/null 2>&1; then
  echo "creating app $APP_NAME (waits until its compute is ACTIVE, a few minutes)"
  databricks apps create --json @"$SPEC" "${PROFILE[@]}" >/dev/null
fi

databricks apps update "$APP_NAME" --json @"$SPEC" "${PROFILE[@]}" -o json | python3 -c "
import json, sys
d = json.load(sys.stdin)
names = sorted(r['name'] for r in d.get('resources') or [])
print('resources:', ', '.join(names) or 'NONE')
print('user_api_scopes:', ', '.join(d.get('user_api_scopes') or []) or 'NONE')
print('app service principal:', d.get('service_principal_client_id'))
sys.exit(0 if len(names) == 3 else 'expected 3 resources, check the output above')
"
rm -f "$SPEC"
echo "next: zsh scripts/grant_app_access.sh, then zsh scripts/deploy.sh"
