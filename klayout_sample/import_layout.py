# import_layout.py
# KLayout JSON I/O Compliant - Import layout into a new top cell
import sys, json, os

# Allow importing sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _clone_cell_tree(src_layout, dst_layout, src_cell_index, layer_map, cell_map, name_prefix):
    """Clone a cell hierarchy from src_layout into dst_layout."""
    import pya

    if src_cell_index in cell_map:
        return cell_map[src_cell_index]

    src_cell = src_layout.cell(src_cell_index)
    if src_cell is None:
        raise ValueError(f"Source cell index {src_cell_index} not found")

    target_name = f"{name_prefix}{src_cell.name}" if name_prefix else src_cell.name

    dst_cell = dst_layout.cell(target_name)
    if dst_cell is None:
        dst_cell = dst_layout.create_cell(target_name)

    dst_cell_index = dst_cell.cell_index()
    cell_map[src_cell_index] = dst_cell_index

    for layer_index in src_layout.layer_indices():
        src_shapes = src_cell.shapes(layer_index)
        if src_shapes.is_empty():
            continue

        if layer_index not in layer_map:
            layer_info = src_layout.get_info(layer_index)
            li = pya.LayerInfo(layer_info.layer, layer_info.datatype)
            layer_map[layer_index] = dst_layout.layer(li)
        dst_layer_index = layer_map[layer_index]

        dst_shapes = dst_cell.shapes(dst_layer_index)
        for shape in src_shapes.each():
            dst_shapes.insert(shape)

    for inst in src_cell.each_inst():
        child_index = _clone_cell_tree(
            src_layout, dst_layout, inst.cell_index, layer_map, cell_map, name_prefix
        )
        na = getattr(inst, "na", 1)
        nb = getattr(inst, "nb", 1)
        a_vec = getattr(inst, "a", pya.Vector(0, 0))
        b_vec = getattr(inst, "b", pya.Vector(0, 0))
        array = pya.CellInstArray(child_index, inst.trans, na, nb, a_vec, b_vec)
        dst_cell.insert(array)

    return dst_cell_index


def main(payload: dict) -> dict:
    """Create a new layout with a top cell and import instances from an external layout."""
    import pya

    input_file = payload.get("input_file", "out.gds")
    output_file = payload.get("output_file", "layout_main.gds")
    top_cell_name = payload.get("top_cell_name", "top")

    layout_to_be_imported = pya.Layout()
    layout_to_be_imported.read(input_file)

    layout_main = pya.Layout()
    layout_main.dbu = layout_to_be_imported.dbu
    top_cell = layout_main.create_cell(top_cell_name)

    layer_map = {}
    cell_map = {}
    name_prefix = payload.get("import_prefix", "imported_")

    for src_top_cell in layout_to_be_imported.top_cells():
        cloned_index = _clone_cell_tree(
            layout_to_be_imported,
            layout_main,
            src_top_cell.cell_index(),
            layer_map,
            cell_map,
            name_prefix,
        )
        top_cell.insert(pya.CellInstArray(cloned_index, pya.Trans()))

    layout_main.write(output_file)

    return {
        "ok": True,
        "result": {
            "message": f"Imported {len(layout_to_be_imported.top_cells())} top cells into '{top_cell_name}'",
            "input_file": input_file,
            "output_file": output_file,
            "top_cell": top_cell_name,
        },
    }


if __name__ == "__main__":
    raw = input_parameter

    try:
        payload = json.loads(raw)
    except Exception:
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "input_file": vals[0] if len(vals) > 0 else "out.gds",
            "output_file": vals[1] if len(vals) > 1 else "layout_main.gds",
            "top_cell_name": vals[2] if len(vals) > 2 else "top",
        }

    result = main(payload)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)
