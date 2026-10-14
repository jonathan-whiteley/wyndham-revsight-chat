#!/bin/zsh
# Deploy RevSight Chat: build the UI, stage only runtime files, upload, deploy.
# Stages into a temp dir so .gitignore never drops frontend/dist and no
# package.json/node_modules reaches the app (that triggers a Node build).
#
#   zsh scripts/deploy.sh               build, upload and deploy (settings from config.env)
#   zsh scripts/deploy.sh --stage-only  build and stage locally, print the folder, stop
set -euo pipefail
ROOT=${0:A:h:h}
source "$ROOT/config.env"
PROFILE=(--profile "$DATABRICKS_PROFILE")
STAGE=$(mktemp -d)

(cd "$ROOT/app/frontend" && npm run build >/dev/null)
rsync -a --exclude '__pycache__' "$ROOT/app/main.py" "$ROOT/app/requirements.txt" "$ROOT/app/api" "$ROOT/app/services" "$STAGE/"
mkdir -p "$STAGE/frontend" && rsync -a "$ROOT/app/frontend/dist" "$STAGE/frontend/"
# app.yaml with this workspace's catalog and schema filled in
sed -e "s/{{CATALOG}}/$CATALOG/" -e "s/{{SCHEMA}}/$SCHEMA/" "$ROOT/app/app.yaml" > "$STAGE/app.yaml"
if grep -q '{{[A-Z_]*}}' "$STAGE/app.yaml"; then echo "unfilled placeholder in app.yaml" >&2; exit 1; fi

if [[ "${1:-}" == "--stage-only" ]]; then
  echo "staged in $STAGE"
  exit 0
fi

if [[ -z "${APP_SOURCE_PATH:-}" ]]; then
  ME=$(databricks current-user me "${PROFILE[@]}" -o json | python3 -c "import json,sys;print(json.load(sys.stdin)['userName'])")
  APP_SOURCE_PATH=/Workspace/Users/$ME/apps/$APP_NAME
fi
databricks workspace delete "$APP_SOURCE_PATH" --recursive "${PROFILE[@]}" 2>/dev/null || true
databricks workspace mkdirs "$APP_SOURCE_PATH" "${PROFILE[@]}"
databricks workspace import-dir "$STAGE" "$APP_SOURCE_PATH" --overwrite "${PROFILE[@]}" >/dev/null
echo "uploaded: $(databricks workspace list "$APP_SOURCE_PATH/frontend/dist/assets" "${PROFILE[@]}" | grep -o 'index-[A-Za-z0-9_-]*\.js')  local: $(ls "$ROOT/app/frontend/dist/assets" | grep '\.js$')"
databricks apps deploy "$APP_NAME" --source-code-path "$APP_SOURCE_PATH" "${PROFILE[@]}" -o json | python3 -c "import sys,json;d=json.load(sys.stdin);print('deployment', d.get('deployment_id'), d.get('status',{}).get('state'), d.get('status',{}).get('message',''))"
rm -rf "$STAGE"
