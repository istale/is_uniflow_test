#!/usr/bin/env bash
# run_merge_shapes.sh
# Usage: ./run_merge_shapes.sh '<json_payload>' [capture.json]
# Default payload: {"input_file":"cell_hier.gds","cell_name":"Unit_A","layer_spec":"100/100","output_layer_spec":"100/101","output_file":"cell_hier_merge_shapes.csv","output_gds":"cell_hier_merge_shapes.gds"}

set -euo pipefail

# Use specific KLayout path
KLAYOUT_PATH="/Applications/KLayout.app/Contents/MacOS/klayout"

# Resolve payload
RAW_ARG="${1:-}"
if [ -z "$RAW_ARG" ]; then
  PAYLOAD='{"input_file":"cell_hier.gds","cell_name":"Unit_A","layer_spec":"100/100","output_layer_spec":"100/101","output_file":"cell_hier_merge_shapes.csv","output_gds":"cell_hier_merge_shapes.gds"}'
elif [ -f "$RAW_ARG" ]; then
  PAYLOAD="$(cat "$RAW_ARG")"
else
  PAYLOAD="$RAW_ARG"
fi

CAPTURE_FILE="${2:-}"

echo "Running merge shapes script with payload: $PAYLOAD"

# Execute KLayout script
set +e
KLAYOUT_STDOUT="$("$KLAYOUT_PATH" -b -r merge_shapes.py -rd input_parameter="${PAYLOAD}" 2>&1)"
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
  export KLAYOUT_STDOUT
  export EXIT_CODE
  python3 - <<'PY'
import json, os
print(json.dumps({
    "ok": False,
    "error": f"KLayout exited with code {os.environ['EXIT_CODE']}",
    "stderr": os.environ["KLAYOUT_STDOUT"]
}, ensure_ascii=False))
PY
  exit "$EXIT_CODE"
fi

if [ -n "$CAPTURE_FILE" ]; then
  mkdir -p "$(dirname "$CAPTURE_FILE")"
  printf '%s\n' "$KLAYOUT_STDOUT" > "$CAPTURE_FILE"
fi

printf '%s\n' "$KLAYOUT_STDOUT"
