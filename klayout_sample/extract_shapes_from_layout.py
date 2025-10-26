# extract_shapes_from_layout.py
# KLayout JSON I/O Compliant - Extract shapes from a layout into CSV
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from klayout_api import klayout_import_layout, klayout_extract_shapes_to_csv


def main(payload):
    input_gds = payload.get("input_gds", "layout_from_csv_with_top.gds")
    output_csv = payload.get("output_csv", "layout_from_csv_with_top_shapes.csv")
    cell_name = payload.get("cell_name")

    if not os.path.exists(input_gds):
        return {"ok": False, "error": f"Input GDS not found: {input_gds}"}

    layout = klayout_import_layout(input_gds)
    if layout is None:
        return {"ok": False, "error": f"Failed to read layout: {input_gds}"}

    success, shapes = klayout_extract_shapes_to_csv(
        layout,
        cell_name=cell_name,
        output_csv_file_name=output_csv,
    )

    if not success:
        return {
            "ok": False,
            "error": f"Failed to export shapes to CSV: {output_csv}",
        }

    return {
        "ok": True,
        "result": {
            "message": "Shapes exported successfully",
            "input_gds": input_gds,
            "output_csv": output_csv,
            "cell_name": cell_name,
            "shape_count": len(shapes),
        },
    }


if __name__ == "__main__":
    raw = input_parameter
    try:
        payload = json.loads(raw)
    except Exception:
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "input_gds": vals[0] if len(vals) > 0 and vals[0] else "layout_from_csv_with_top.gds",
            "output_csv": vals[1] if len(vals) > 1 and vals[1] else "layout_from_csv_with_top_shapes.csv",
            "cell_name": vals[2] if len(vals) > 2 and vals[2] else None,
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)
