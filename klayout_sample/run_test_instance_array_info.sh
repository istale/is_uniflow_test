#!/usr/bin/env bash
# run_test_instance_array_info.sh
# Wrapper to enumerate instances/arrays for a given cell
set -euo pipefail

KLAYOUT_BIN="/Applications/KLayout.app/Contents/MacOS/klayout"
KLAYOUT_SCRIPT="test_instance_array_info.py"

RAW_ARG="${1:-}"
if [ -z "$RAW_ARG" ]; then
  INPUT_PARAMETER='{"input_file":"cell_hier.gds","cell_name":"Unit_A","start_hier":0,"end_hier":-1,"expand_array":false,"output_csv":"cell_hier_inst_info.csv","debug":true}'
elif [ -f "$RAW_ARG" ]; then
  INPUT_PARAMETER="$(cat "$RAW_ARG")"
else
  INPUT_PARAMETER="$RAW_ARG"
fi

CAPTURE_FILE="${2:-}"

set +e
KLAYOUT_STDOUT="$("$KLAYOUT_BIN" -b -r "$KLAYOUT_SCRIPT" -rd input_parameter="${INPUT_PARAMETER}" 2>&1)"
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
  export KLAYOUT_STDOUT
  export KLAYOUT_EXIT_CODE="$EXIT_CODE"
  python3 - <<'PY'
import json, os
print(json.dumps({
    "ok": False,
    "error": f"KLayout exited with code {os.environ['KLAYOUT_EXIT_CODE']}",
    "stderr": os.environ["KLAYOUT_STDOUT"],
}, ensure_ascii=False))
PY
  exit "$EXIT_CODE"
fi

if [ -n "$CAPTURE_FILE" ]; then
  mkdir -p "$(dirname "$CAPTURE_FILE")"
  printf '%s\n' "$KLAYOUT_STDOUT" > "$CAPTURE_FILE"
fi

printf '%s\n' "$KLAYOUT_STDOUT"
