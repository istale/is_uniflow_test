#!/usr/bin/env bash
# run_analyze_array_pitch.sh
# Wrapper to analyze array pitch from CSV
set -euo pipefail

RAW_ARG="${1:-}"
if [ -z "$RAW_ARG" ]; then
  INPUT_PARAMETER='{"input_csv":"layout_from_csv_with_top_shapes.csv","cell_name":"top"}'
elif [ -f "$RAW_ARG" ]; then
  INPUT_PARAMETER="$(cat "$RAW_ARG")"
else
  INPUT_PARAMETER="$RAW_ARG"
fi

python3 analyze_array_pitch.py <<< "$INPUT_PARAMETER"
