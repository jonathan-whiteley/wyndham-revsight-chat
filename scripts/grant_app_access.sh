#!/bin/zsh
# Give the app's service principal read access to the data and the Genie spaces.
# Run by someone who can GRANT on CATALOG/SCHEMA (the schema owner) and who has
# CAN_MANAGE on both Genie spaces. Safe to re-run.
#
#   Unity Catalog: USE CATALOG, USE SCHEMA, SELECT on the schema
#   Genie spaces:  CAN_RUN on each space's own ACL (added with PATCH, nothing removed)
set -euo pipefail
ROOT=${0:A:h:h}
source "$ROOT/config.env"
PROFILE=(--profile "$DATABRICKS_PROFILE")

SP=$(databricks apps get "$APP_NAME" "${PROFILE[@]}" -o json | python3 -c "import json,sys;print(json.load(sys.stdin)['service_principal_client_id'])")
echo "app service principal: $SP"

run_sql() {
  local body
  body=$(python3 -c "import json,sys;print(json.dumps({'warehouse_id':sys.argv[1],'statement':sys.argv[2],'wait_timeout':'50s'}))" "$WAREHOUSE_ID" "$1")
  databricks api post /api/2.0/sql/statements --json "$body" "${PROFILE[@]}" | python3 -c "
import json, sys
st = json.load(sys.stdin)['status']
print(' ', st['state'], sys.argv[1], st.get('error', {}).get('message', ''))
sys.exit(0 if st['state'] == 'SUCCEEDED' else 1)
" "$1"
}

run_sql "GRANT USE CATALOG ON CATALOG \`$CATALOG\` TO \`$SP\`"
run_sql "GRANT USE SCHEMA, SELECT ON SCHEMA \`$CATALOG\`.\`$SCHEMA\` TO \`$SP\`"

for SPACE in "$GENIE_SPACE_NT" "$GENIE_SPACE_STR"; do
  databricks api patch "/api/2.0/permissions/genie/$SPACE" "${PROFILE[@]}" \
    --json "{\"access_control_list\":[{\"service_principal_name\":\"$SP\",\"permission_level\":\"CAN_RUN\"}]}" >/dev/null
  echo "  CAN_RUN on Genie space $SPACE"
done
