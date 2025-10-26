# draw_cell_bbox.py
# KLayout JSON I/O Compliant - Draw cell bounding box on a target layer
import sys, json, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from klayout_api import (
    klayout_import_layout,
    klayout_draw_cell_bbox_shape,
)


def main(payload: dict) -> dict:
    """Generate a bbox polygon for a specific cell/layer combination."""
    input_file = payload.get("input_file", "cell_hier.gds")
    if not os.path.exists(input_file):
        return {"ok": False, "error": f"Input file not found: {input_file}"}

    cell_name = payload.get("cell_name", "Unit_A")
    layer_number_datatype = (
        payload.get("layer_number_datatype")
        or payload.get("layer_spec")
        or payload.get("layer")
        or "10100/0"
    )
    include_descendants = payload.get("include_descendants", True)
    clear_existing = payload.get("clear_existing", True)
    output_gds = payload.get("output_gds", "cell_hier_bbox.gds")

    layout = klayout_import_layout(input_file)
    if layout is None:
        return {"ok": False, "error": f"Failed to read layout: {input_file}"}

    result = klayout_draw_cell_bbox_shape(
        layout,
        cell_name,
        layer_number_datatype,
        include_descendants=include_descendants,
        clear_existing=clear_existing,
    )
    if not result.get("ok"):
        return result

    out_dir = os.path.dirname(output_gds)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    layout.write(output_gds)
    result["result"]["input_file"] = input_file
    result["result"]["output_gds"] = output_gds
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
            "layer_number_datatype": vals[2] if len(vals) > 2 and vals[2] else "10100/0",
            "output_gds": vals[3] if len(vals) > 3 and vals[3] else "cell_hier_bbox.gds",
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)
