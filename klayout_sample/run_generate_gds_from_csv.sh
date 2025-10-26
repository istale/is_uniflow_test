#!/usr/bin/env bash
# run_generate_gds_from_csv.sh
# Wrapper to build GDS from CSV definitions
set -euo pipefail

KLAYOUT_BIN="/Applications/KLayout.app/Contents/MacOS/klayout"
KLAYOUT_SCRIPT="generate_gds_from_csv.py"

RAW_ARG="${1:-}"
if [ -z "$RAW_ARG" ]; then
  INPUT_PARAMETER='{"input_csv":"layout_shape_to_generate_gds.csv","output_gds":"layout_from_csv.gds","dbu":0.001}'
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
