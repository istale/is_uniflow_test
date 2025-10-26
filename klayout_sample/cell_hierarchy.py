# cell_hierarchy.py
# KLayout JSON I/O Compliant - Build hierarchical layout and export GDS
import sys, json, os

# Allow local module imports if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main(payload: dict) -> dict:
    """Create hierarchical layout with Unit_A and export to cell_hier.gds"""
    import pya

    print("Step 1: Initializing layout with dbu=0.0005")
    layout = pya.Layout()
    layout.dbu = 0.0005

    print("Step 2: Defining layers 100/100 and 200/200")
    layer_100 = layout.layer(pya.LayerInfo(100, 100))
    layer_200 = layout.layer(pya.LayerInfo(200, 200))

    print("Step 3: Creating base cells cell_A and cell_B")
    cell_a = layout.create_cell("cell_A")
    cell_b = layout.create_cell("cell_B")

    print("Step 4: Drawing rectangles on cell_A and cell_B")
    cell_a.shapes(layer_100).insert(pya.Box(0, 0, 1, 1))
    cell_b.shapes(layer_100).insert(pya.Box(1, 0, 2, 2))
    cell_b.shapes(layer_200).insert(pya.Box(3, 3, 4, 4))

    print("Step 5: Creating Unit_A and instantiating cell_A and cell_B")
    unit_a = layout.create_cell("Unit_A")
    unit_a.insert(pya.CellInstArray(cell_a.cell_index(), pya.Trans(pya.Point(0, 0))))
    unit_a.insert(pya.CellInstArray(cell_b.cell_index(), pya.Trans(pya.Point(0, 0))))

    print("Step 6: Creating top cell and inserting Unit_A")
    top_cell = layout.create_cell("top")
    top_cell.insert(pya.CellInstArray(unit_a.cell_index(), pya.Trans(pya.Point(0, 0))))

    output_file = payload.get("output_file", "cell_hier.gds")
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print(f"Step 7: Exporting layout to {output_file}")
    layout.write(output_file)

    print("Step 8: Hierarchical layout creation completed successfully")
    return {
        "ok": True,
        "result": {
            "message": "Hierarchical layout generated successfully",
            "file": output_file,
            "top_cell": "top",
            "unit_cell": "Unit_A"
        }
    }


if __name__ == "__main__":
    raw = input_parameter

    try:
        payload = json.loads(raw)
    except Exception:
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "output_file": vals[0] if len(vals) > 0 and vals[0] else "cell_hier.gds"
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)
