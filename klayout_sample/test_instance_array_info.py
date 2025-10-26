# test_instance_array_info.py
# KLayout JSON I/O Compliant - Enumerate instances/arrays for a target cell
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from klayout_api import (
    klayout_import_layout,
    klayout_get_instance_array_info_of_this_cell,
)


def main(payload: dict) -> dict:
    input_file = payload.get("input_file", "cell_hier.gds")
    cell_name = payload.get("cell_name", "Unit_A")
    start_hier = int(payload.get("start_hier", 1))
    end_hier = int(payload.get("end_hier", -1))
    expand_array = bool(payload.get("expand_array", False))
    output_csv = payload.get("output_csv")
    debug = bool(payload.get("debug", False))

    if not os.path.exists(input_file):
        return {"ok": False, "error": f"Input file not found: {input_file}"}

    layout = klayout_import_layout(input_file)
    if layout is None:
        return {"ok": False, "error": f"Failed to read layout: {input_file}"}

    result = klayout_get_instance_array_info_of_this_cell(
        layout,
        cell_name=cell_name,
        start_hier=start_hier,
        end_hier=end_hier,
        expand_array=expand_array,
        output_csv_path=output_csv,
        verbose=debug,
    )
    return result


if __name__ == "__main__":
    raw = input_parameter
    try:
        payload = json.loads(raw)
    except Exception:
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "input_file": vals[0] if len(vals) > 0 and vals[0] else "cell_hier.gds",
            "cell_name": vals[1] if len(vals) > 1 and vals[1] else "Unit_A",
            "start_hier": int(vals[2]) if len(vals) > 2 and vals[2] else 0,
            "end_hier": int(vals[3]) if len(vals) > 3 and vals[3] else -1,
            "expand_array": vals[4].lower() in ("1", "true", "yes") if len(vals) > 4 and vals[4] else False,
            "debug": vals[5].lower() in ("1", "true", "yes") if len(vals) > 5 and vals[5] else False,
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)
