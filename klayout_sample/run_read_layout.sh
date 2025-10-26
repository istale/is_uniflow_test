#!/usr/bin/env bash
# run_read_layout.sh
# Shell wrapper for read_layout.py following KLayout JSON I/O standard

echo "Starting GDS reading script execution..."
echo "Input parameter: $1"

if [ $# -lt 1 ]; then
  echo "Usage: $0 '<json_string_or_path>' [capture.json]" >&2
  exit 1
fi

RAW_ARG="$1"
if [ -f "$RAW_ARG" ]; then
  INPUT_PARAMETER="$(cat "$RAW_ARG")"
else
  INPUT_PARAMETER="$RAW_ARG"
fi

echo "Processing input parameter: $INPUT_PARAMETER"

KLAYOUT_SCRIPT="read_layout.py"
CAPTURE_FILE="${2:-}"

echo "Executing KLayout script: $KLAYOUT_SCRIPT"
# Execute KLayout Python script with verbose output using full path
/Applications/KLayout.app/Contents/MacOS/klayout -b -r "$KLAYOUT_SCRIPT" -rd input_parameter="${INPUT_PARAMETER}" 2>&1
EXIT_CODE=$?

echo "KLayout execution completed with exit code: $EXIT_CODE"

if [ $EXIT_CODE -ne 0 ]; then
  echo "{\"ok\":false,\"error\":\"KLayout exited with code ${EXIT_CODE}\"}"
  exit $EXIT_CODE
fi

echo "Script execution completed successfully!"

# Output the result (assuming it's in stdout)
cat /dev/stdout
