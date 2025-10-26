# generate_gds_from_csv.py
# KLayout JSON I/O Compliant - Build or augment a layout from CSV definitions
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from klayout_api import (
    klayout_import_layout,
    klayout_create_cell_with_shapes_from_csv,
)


def main(payload):
    input_csv = payload.get("input_csv", "layout_shape_to_generate_gds.csv")
    output_gds = payload.get("output_gds", "layout_from_csv.gds")
    dbu = float(payload.get("dbu", 0.001))
    default_cell = payload.get("default_cell", "top")
    input_gds = payload.get("input_gds")

    layout = None
    if input_gds:
        layout = klayout_import_layout(input_gds)
        if layout is None:
            return {"ok": False, "error": f"Failed to read input GDS: {input_gds}"}

    return klayout_create_cell_with_shapes_from_csv(
        input_csv=input_csv,
        output_gds=output_gds,
        layout=layout,
        dbu=dbu,
        default_cell=default_cell,
        merge_cells=bool(layout),
    )


if __name__ == "__main__":
    raw = input_parameter
    try:
        payload = json.loads(raw)
    except Exception:
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "input_csv": vals[0] if len(vals) > 0 and vals[0] else "layout_shape_to_generate_gds.csv",
            "output_gds": vals[1] if len(vals) > 1 and vals[1] else "layout_from_csv.gds",
            "dbu": float(vals[2]) if len(vals) > 2 and vals[2] else 0.001,
            "default_cell": vals[3] if len(vals) > 3 and vals[3] else "top",
            "input_gds": vals[4] if len(vals) > 4 and vals[4] else None,
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)
