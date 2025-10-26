# add_cell_array.py
# KLayout JSON I/O Compliant - Add/replace a top-cell array referencing a target cell
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from klayout_api import (klayout_import_layout, klayout_create_array, klayout_export_layout)


def main(payload):
    input_gds = payload.get("input_gds", "layout_from_csv.gds")
    output_gds = payload.get("output_gds", input_gds)
    target_cell = payload.get("target_cell", "cell_C")
    top_cell = payload.get("top_cell", "top")
    pitch_x = float(payload.get("array_pitch_x", 0.16))
    pitch_y = float(payload.get("array_pitch_y", 0.24))
    nx = int(payload.get("array_x_number", 4))
    ny = int(payload.get("array_y_number", 3))

    layout = klayout_import_layout(input_gds)
    if layout is None:
        return {"ok": False, "error": f"Failed to read layout: {input_gds}"}

    result = klayout_create_array(
        layout,
        target_cell=target_cell,
        top_cell=top_cell,
        origin_x_um=float(0.0),
        origin_y_um=float(0.0),
        pitch_x_um=pitch_x,
        pitch_y_um=pitch_y,
        nx=nx,
        ny=ny,
        output_gds=output_gds,
    )
    layout = result['layout']
    result = klayout_create_array(
        layout,
        target_cell=target_cell,
        top_cell=top_cell,
        origin_x_um=float(0.1),
        origin_y_um=float(0.1),
        pitch_x_um=pitch_x,
        pitch_y_um=pitch_y,
        nx=nx,
        ny=ny,
        output_gds=output_gds,
    )
    klayout_export_layout(result['layout'], output_gds)
    result.setdefault("result", {}).update({"input_gds": input_gds})
    return result


if __name__ == "__main__":
    raw = input_parameter
    try:
        payload = json.loads(raw)
    except Exception:
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "input_gds": vals[0] if len(vals) > 0 and vals[0] else "layout_from_csv.gds",
            "output_gds": vals[1] if len(vals) > 1 and vals[1] else "layout_from_csv.gds",
            "target_cell": vals[2] if len(vals) > 2 and vals[2] else "cell_C",
        }

    result = main(payload)
    print(json.dumps(result['result'], ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)
