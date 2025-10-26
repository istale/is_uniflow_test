# klayout_api.py
# Custom KLayout API Library
import os
import pya

def klayout_create_cell(layout, cell_name):
    """Create a cell with the given name, handling existing cells gracefully"""
    try:
        # Try to get existing cell
        cell = layout.cell(cell_name)
        if cell is not None:
            print(f"Cell '{cell_name}' already exists, using existing cell")
            return cell
        else:
            # Create new cell
            print(f"Creating new cell '{cell_name}'")
            return layout.create_cell(cell_name)
    except Exception as e:
        print(f"Error creating/getting cell '{cell_name}': {e}")
        # Create new cell as fallback
        return layout.create_cell(cell_name)

def klayout_define_layer(layout, layer_number, layer_datatype):
    """Define a layer, handling existing layers gracefully"""
    try:
        # Try to get existing layer
        layer = layout.layer(layer_number, layer_datatype)
        print(f"Layer {layer_number}.{layer_datatype} already exists")
        return layer
    except Exception as e:
        print(f"Creating new layer {layer_number}.{layer_datatype}")
        # Create new layer
        return layout.layer(layer_number, layer_datatype)

def klayout_draw_rectangle(cell, x1, y1, x2, y2, layer):
    """Draw a rectangle in the specified cell and layer"""
    try:
        rect = pya.Box(x1, y1, x2, y2)
        cell.shapes(layer).insert(rect)
        print(f"Drawn rectangle ({x1}, {y1}, {x2}, {y2}) on layer {layer}")
        return True
    except Exception as e:
        print(f"Error drawing rectangle: {e}")
        return False

def klayout_set_dbu(layout, dbu_value):
    """Set the database unit for the layout"""
    try:
        layout.dbu = dbu_value
        print(f"Set database unit to {dbu_value}")
        return True
    except Exception as e:
        print(f"Error setting database unit: {e}")
        return False

def klayout_export_layout(layout, filename):
    """Export the layout to the specified file format (GDS or OAS)"""
    try:
        layout.write(filename)
        print(f"Exported layout to {filename}")
        return True
    except Exception as e:
        print(f"Error exporting layout: {e}")
        return False

def klayout_import_layout(input_file):
    """
    Read a GDS layout file and return the layout object.
    
    Args:
        input_file (str): Path to the GDS file to read
        
    Returns:
        pya.Layout: Layout object containing the GDS data
        
    Example:
        layout = klayout_import_layout("input.gds")
    """
    try:
        layout = pya.Layout()
        layout.read(input_file)
        print(f"Layout read successfully from {input_file}")
        return layout
    except Exception as e:
        print(f"Error reading layout file {input_file}: {e}")
        return None

def klayout_extract_shapes(layout, cell_name=None):
    """
    Extract shape information from a layout.
    
    Args:
        layout (pya.Layout): The layout object to extract shapes from
        cell_name (str, optional): Specific cell name to extract shapes from. 
                                   If None, extracts from all cells.
        
    Returns:
        list: List of shape dictionaries with structure:
            [
                {
                    "cell_name": str,
                    "layer_number": int,
                    "layer_datatype": int,
                    "x1": float,
                    "y1": float,
                    "x2": float,
                    "y2": float
                },
                ...
            ]
            
    Example:
        shapes = klayout_extract_shapes(layout)
        # Returns: [{"cell_name": "my_cell", "layer_number": 100, "layer_datatype": 0, "x1": 0, "y1": 0, "x2": 1, "y2": 1}]
    """
    shapes_data = []
    
    try:
        root_cell = layout.cell(cell_name) if cell_name else None
        if cell_name and root_cell is None:
            print(f"Error extracting shapes: cell '{cell_name}' not found")
            return shapes_data

        cells = [root_cell] if root_cell else list(layout.each_cell())
        
        for cell in cells:
            if cell is None:
                continue
                
            print(f"Processing cell: {cell.name}")
            
            for layer in layout.layer_indices():
                try:
                    layer_info = layout.get_info(layer)
                    layer_number = getattr(layer_info, "layer", None)
                    if layer_number is None:
                        layer_number = layer_info.layer
                    layer_datatype = layer_info.datatype
                    
                    print(f"  Processing layer {layer}: number={layer_number}, datatype={layer_datatype}")
                    
                    if root_cell:
                        iterator = cell.begin_shapes_rec(layer)
                        while not iterator.at_end():
                            shape_proxy = iterator.shape()
                            trans = iterator.trans()
                            iterator.next()
                            if shape_proxy is None or not hasattr(shape_proxy, "bbox"):
                                continue
                            bbox = shape_proxy.bbox().transformed(trans)
                            x1, y1, x2, y2 = bbox.left, bbox.bottom, bbox.right, bbox.top
                            
                            shapes_data.append({
                                "cell_name": cell.name,
                                "layer_number": layer_number,
                                "layer_datatype": layer_datatype,
                                "x1": x1,
                                "y1": y1,
                                "x2": x2,
                                "y2": y2
                            })
                            
                            print(f"    Shape: ({x1}, {y1}, {x2}, {y2}) on layer {layer_number}.{layer_datatype}")
                    else:
                        shapes = cell.shapes(layer)
                        for shape in shapes.each():
                            if hasattr(shape, 'bbox'):
                                bbox = shape.bbox()
                                x1, y1, x2, y2 = bbox.left, bbox.bottom, bbox.right, bbox.top
                                
                                shapes_data.append({
                                    "cell_name": cell.name,
                                    "layer_number": layer_number,
                                    "layer_datatype": layer_datatype,
                                    "x1": x1,
                                    "y1": y1,
                                    "x2": x2,
                                    "y2": y2
                                })
                                
                                print(f"    Shape: ({x1}, {y1}, {x2}, {y2}) on layer {layer_number}.{layer_datatype}")
                            
                except Exception as e:
                    print(f"  Error processing layer {layer}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error extracting shapes: {e}")
        
    return shapes_data

def klayout_extract_shapes_to_csv(layout, cell_name=None, output_csv_file_name="layout_shape.csv"):
    """
    Extract shape data from a layout and export it to CSV format.
    
    Args:
        layout (pya.Layout): Layout object to extract shapes from.
        cell_name (str, optional): Specific cell to extract. Defaults to all cells.
        output_csv_file_name (str): Path to output CSV file.
        
    Returns:
        tuple: (success_flag (bool), shapes_data (list))
        
    Example:
        success, shapes = klayout_extract_shapes_to_csv(layout, cell_name="top", output_csv_file_name="output.csv")
    """
    shapes_data = klayout_extract_shapes(layout, cell_name)
    
    dbu = layout.dbu
    try:
        # Write CSV header and rows
        with open(output_csv_file_name, 'w') as f:
            f.write("cell_name,layer,bbox_x1,bbox_y1,bbox_x2,bbox_y2,is_rectangle,polygon_vertices\n")
            
            for shape in shapes_data:
                layer_str = f"{shape['layer_number']}.{shape['layer_datatype']}"
                bbox_x1 = shape["x1"]
                bbox_y1 = shape["y1"]
                bbox_x2 = shape["x2"]
                bbox_y2 = shape["y2"]
                is_rectangle = int((bbox_x2 - bbox_x1) > 0 and (bbox_y2 - bbox_y1) > 0)
                polygon_vertices = _bbox_vertices_string(bbox_x1, bbox_y1, bbox_x2, bbox_y2, dbu)
                csv_x1 = klayout_format_dimension(bbox_x1, dbu)
                csv_y1 = klayout_format_dimension(bbox_y1, dbu)
                csv_x2 = klayout_format_dimension(bbox_x2, dbu)
                csv_y2 = klayout_format_dimension(bbox_y2, dbu)
                f.write(
                    f"{shape['cell_name']},{layer_str},"
                    f"{csv_x1},{csv_y1},{csv_x2},{csv_y2},"
                    f"{is_rectangle},{polygon_vertices}\n"
                )
        
        print(f"Exported {len(shapes_data)} shapes to {output_csv_file_name}")
        return True, shapes_data
    except Exception as e:
        print(f"Error exporting shapes to CSV: {e}")
        return False, shapes_data


def _parse_layer_spec(spec):
    """Normalize a layer specification into (layer_number, layer_datatype)."""
    if isinstance(spec, str):
        normalized = spec.replace(":", "/").replace(".", "/")
        parts = [p.strip() for p in normalized.split("/") if p.strip()]
        if len(parts) != 2:
            raise ValueError(f"Invalid layer spec '{spec}'. Use 'number/datatype'.")
        return int(parts[0]), int(parts[1])
    if isinstance(spec, dict):
        number_keys = (
            "layer_number",
            "layer",
            "number",
            "layer_num",
        )
        datatype_keys = (
            "layer_datatype",
            "datatype",
        )

        # Backward compatibility with old layer_datatype/layer_purpose naming
        if "layer_datatype" in spec and "layer_purpose" in spec:
            return int(spec["layer_datatype"]), int(spec["layer_purpose"])

        layer_number = None
        layer_datatype = None

        for key in number_keys:
            if key in spec:
                layer_number = int(spec[key])
                break
        if layer_number is None and "layer_datatype" in spec and "layer_purpose" not in spec:
            layer_number = int(spec["layer_datatype"])

        for key in datatype_keys:
            if key in spec:
                layer_datatype = int(spec[key])
                break
        if layer_datatype is None and "layer_purpose" in spec:
            layer_datatype = int(spec["layer_purpose"])

        if layer_number is None or layer_datatype is None:
            raise ValueError(f"Layer spec dict missing keys: {spec}")
        return layer_number, layer_datatype
    if isinstance(spec, (list, tuple)):
        if len(spec) != 2:
            raise ValueError(f"Layer tuple must have two items: {spec}")
        return int(spec[0]), int(spec[1])
    if isinstance(spec, (int, float)):
        raise ValueError(f"Cannot infer layer datatype from single number: {spec}")
    raise ValueError(f"Unsupported layer spec type: {spec}")


def _normalize_layer_list(layer_list):
    """Ensure input is a list of (layer_number, layer_datatype) tuples."""
    if layer_list is None:
        return []
    if isinstance(layer_list, (str, dict)) or (
        isinstance(layer_list, (list, tuple))
        and layer_list
        and not isinstance(layer_list[0], (list, tuple, dict))
        and not isinstance(layer_list[0], str)
    ):
        items = [layer_list]
    else:
        items = layer_list
    normalized = []
    for item in items:
        normalized.append(_parse_layer_spec(item))
    return normalized


DIMENSION_UNIT_FACTORS = {
    "um": 1.0,
    "µm": 1.0,
    "nm": 1000.0,
    "mm": 0.001,
}


def klayout_convert_dimension(value, dbu, target_unit="um"):
    """
    Convert a coordinate in DBU to the requested unit.
    target_unit supports: "dbu", "um"/"µm", "nm", "mm".
    """
    if value is None:
        return None
    unit = (target_unit or "um").lower()
    if unit in ("dbu", "internal"):
        return float(value)
    um_value = float(value) * dbu
    factor = DIMENSION_UNIT_FACTORS.get(unit, 1.0)
    return um_value * factor


def klayout_format_dimension(value, dbu, target_unit="um", precision=6):
    converted = klayout_convert_dimension(value, dbu, target_unit)
    if converted is None:
        return ""
    fmt = f"{{:.{precision}f}}"
    return fmt.format(converted)


def _dedupe_polygon_points(points):
    unique = []
    for pt in points:
        current = pya.Point(pt.x, pt.y)
        if not unique or current != unique[-1]:
            unique.append(current)
    if len(unique) > 1 and unique[0] == unique[-1]:
        unique.pop()
    return unique


def _normalize_polygon_vertices(points):
    pts = _dedupe_polygon_points(points)
    if len(pts) < 3:
        return pts

    area = 0
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        area += pts[i].x * pts[j].y - pts[j].x * pts[i].y
    if area < 0:
        pts = list(reversed(pts))

    start_idx = min(range(len(pts)), key=lambda i: (pts[i].y, pts[i].x))
    return pts[start_idx:] + pts[:start_idx]


def _points_to_vertex_string(points, dbu=None, unit="um", precision=6):
    if not points:
        return ""
    unit_lower = (unit or "um").lower()
    segments = []
    for pt in points:
        if dbu is None or unit_lower in ("dbu", "internal"):
            x_val = pt.x
            y_val = pt.y
        else:
            x_val = klayout_format_dimension(pt.x, dbu, unit_lower, precision)
            y_val = klayout_format_dimension(pt.y, dbu, unit_lower, precision)
        segments.append(f"{x_val}_{y_val}")
    return "_".join(segments)


def _is_axis_aligned_rectangle(points):
    if len(points) != 4:
        return False
    xs = {pt.x for pt in points}
    ys = {pt.y for pt in points}
    if len(xs) != 2 or len(ys) != 2:
        return False
    combos = {(x, y) for x in xs for y in ys}
    return combos == {(pt.x, pt.y) for pt in points}


def _bbox_vertices_string(x1, y1, x2, y2, dbu, unit="um", precision=6):
    if x2 == x1 or y2 == y1:
        return ""
    points = [
        pya.Point(x1, y1),
        pya.Point(x2, y1),
        pya.Point(x2, y2),
        pya.Point(x1, y2),
    ]
    normalized = _normalize_polygon_vertices(points)
    return _points_to_vertex_string(normalized, dbu, unit, precision)


def _compose_trans(t1, t2):
    return t1 * t2


def _call_or_value(obj, attr, default=None):
    ref = getattr(obj, attr, None)
    if ref is None:
        return default
    if callable(ref):
        return ref()
    return ref


def _cell_inst_array_is_array(cia):
    for attr in ("is_regular_array", "is_array"):
        ref = getattr(cia, attr, None)
        if callable(ref):
            try:
                return bool(ref())
            except TypeError:
                continue
        if isinstance(ref, bool):
            return ref
    return False


def _rot_from_trans(t: pya.Trans) -> int:
    val = _call_or_value(t, "rot", 0)
    return int(val) * 90


def _mirror_from_trans(t: pya.Trans) -> bool:
    fn = getattr(t, "is_mirror", None)
    if callable(fn):
        return bool(fn())
    mx = getattr(t, "mx", None)
    if callable(mx):
        return bool(mx())
    mag = getattr(t, "mag", None)
    if mag is not None:
        return float(mag) < 0
    return False


def _to_um(value, dbu):
    return float(value) * dbu


def _box_to_um_tuple(box: pya.Box, dbu):
    return (
        _to_um(box.left, dbu),
        _to_um(box.bottom, dbu),
        _to_um(box.right, dbu),
        _to_um(box.top, dbu),
    )


def _offset_from_trans_um(t: pya.Trans, dbu):
    disp = t.disp() if callable(getattr(t, "disp", None)) else t.disp
    return (_to_um(disp.x, dbu), _to_um(disp.y, dbu))


def _inst_array_overall_bbox_in_root(
    child_bbox: pya.Box,
    t_root_to_parent: pya.Trans,
    t_parent_to_child: pya.Trans,
    nx: int,
    ny: int,
    dx: int,
    dy: int,
) -> pya.Box:
    t_root = t_root_to_parent
    t_child = t_parent_to_child

    corners = []
    idxs = [(0, 0)]
    if nx > 1:
        idxs.append((nx - 1, 0))
    if ny > 1:
        idxs.append((0, ny - 1))
    if nx > 1 and ny > 1:
        idxs.append((nx - 1, ny - 1))

    for ix, iy in idxs:
        t_elt = _compose_trans(t_child, pya.Trans(ix * dx, iy * dy))
        t_total = _compose_trans(t_root, t_elt)
        corners.append(child_bbox.transformed(t_total))

    if not corners:
        return child_bbox.transformed(_compose_trans(t_root, t_child))

    bb = pya.Box(corners[0])
    for c in corners[1:]:
        bb = bb + c
    return bb


def _emit_instance_record(
    depth,
    path_names,
    parent_cell,
    child_cell,
    is_array,
    bbox_um,
    origin,
    rot_deg,
    mirror,
    array_params=None,
):
    record = {
        "depth": depth,
        "path": list(path_names),
        "parent_cell": parent_cell,
        "child_cell": child_cell,
        "xform_in_root": {
            "origin": {"x": float(origin[0]), "y": float(origin[1])},
            "rot_deg": int(rot_deg),
            "mirror_x": bool(mirror),
        },
        "is_array": bool(is_array),
        "bbox_in_root_um": {
            "x1": float(bbox_um[0]),
            "y1": float(bbox_um[1]),
            "x2": float(bbox_um[2]),
            "y2": float(bbox_um[3]),
        },
    }
    if is_array and array_params:
        record["array"] = {
            "nx": int(array_params.get("nx", 1)),
            "ny": int(array_params.get("ny", 1)),
            "dx_um": float(array_params.get("dx_um", 0.0)),
            "dy_um": float(array_params.get("dy_um", 0.0)),
        }
    return record


def klayout_get_instance_array_info_of_this_cell(
    layout,
    cell_name,
    start_hier=1,
    end_hier=-1,
    expand_array=False,
    output_csv_path=None,
    verbose=False,
):
    cell = layout.cell(cell_name)
    if cell is None:
        return {
            "ok": False,
            "error": f"Cell '{cell_name}' not found in layout",
        }

    dbu = layout.dbu
    summary = {
        "root_cell": cell.name,
        "start_hier": start_hier,
        "end_hier": end_hier,
        "expand_array": bool(expand_array),
        "count": 0,
        "by_depth": {},
        "cycle_detected": False,
    }
    records = []

    stack = [
        (cell, 0, pya.Trans(), (cell.cell_index(),), (cell.name,))
    ]

    if verbose:
        print(f"[DEBUG] Enumerating instances under '{cell.name}' (start={start_hier}, end={end_hier}, expand_array={expand_array})")

    while stack:
        parent_cell, depth, t_root_to_parent, path_idx, path_names = stack.pop()
        next_depth = depth + 1

        if verbose:
            print(f"[DEBUG] Visiting '{parent_cell.name}' at depth {depth}. Stack size={len(stack)}")

        for cia in parent_cell.each_inst():
            try:
                child_idx = cia.cell_index()
                child_cell = layout.cell(child_idx)
                if child_cell is None:
                    if verbose:
                        print(f"[DEBUG] Skipping inst with invalid child index {child_idx}")
                    continue

                if child_idx in path_idx:
                    summary["cycle_detected"] = True
                    allow_descend = False
                    if verbose:
                        print(f"[DEBUG] Cycle detected for child '{child_cell.name}', skipping descend")
                else:
                    allow_descend = True

                t_parent_to_child = cia.trans()
                t_root_to_child = _compose_trans(t_root_to_parent, t_parent_to_child)
                child_bbox = child_cell.bbox()

                is_array = _cell_inst_array_is_array(cia)
                if verbose:
                    kind = "array" if is_array else "instance"
                    print(f"[DEBUG] Found {kind} '{child_cell.name}' under '{parent_cell.name}' at depth {next_depth}")

                if is_array:
                    nx = max(int(_call_or_value(cia, "nx", 1) or 1), 1)
                    ny = max(int(_call_or_value(cia, "ny", 1) or 1), 1)
                    dx = int(_call_or_value(cia, "dx", 0) or 0)
                    dy = int(_call_or_value(cia, "dy", 0) or 0)

                    if expand_array:
                        for ix in range(nx):
                            for iy in range(ny):
                                t_elt = _compose_trans(t_parent_to_child, pya.Trans(ix * dx, iy * dy))
                                t_total = _compose_trans(t_root_to_parent, t_elt)
                                elt_bbox = child_bbox.transformed(t_total)
                                rec_bbox_um = _box_to_um_tuple(elt_bbox, dbu)
                                rec_off_um = _offset_from_trans_um(t_total, dbu)
                                rec_rot = _rot_from_trans(t_total)
                                rec_mir = _mirror_from_trans(t_total)

                                if (start_hier <= next_depth) and (end_hier < 0 or next_depth <= end_hier):
                                    rec = _emit_instance_record(
                                        depth=next_depth,
                                        path_names=path_names,
                                        parent_cell=parent_cell.name,
                                        child_cell=child_cell.name,
                                        is_array=True,
                                        bbox_um=rec_bbox_um,
                                        origin=rec_off_um,
                                        rot_deg=rec_rot,
                                        mirror=rec_mir,
                                        array_params={"nx": 1, "ny": 1, "dx_um": 0.0, "dy_um": 0.0},
                                    )
                                    records.append(rec)
                                    summary["by_depth"][str(next_depth)] = summary["by_depth"].get(str(next_depth), 0) + 1
                    else:
                        bb_root = _inst_array_overall_bbox_in_root(
                            child_bbox, t_root_to_parent, t_parent_to_child, nx, ny, dx, dy
                        )
                        rec_bbox_um = _box_to_um_tuple(bb_root, dbu)
                        rec_off_um = _offset_from_trans_um(t_root_to_child, dbu)
                        rec_rot = _rot_from_trans(t_root_to_child)
                        rec_mir = _mirror_from_trans(t_root_to_child)

                        if (start_hier <= next_depth) and (end_hier < 0 or next_depth <= end_hier):
                            rec = _emit_instance_record(
                                depth=next_depth,
                                path_names=path_names,
                                parent_cell=parent_cell.name,
                                child_cell=child_cell.name,
                                is_array=True,
                                bbox_um=rec_bbox_um,
                                origin=rec_off_um,
                                rot_deg=rec_rot,
                                mirror=rec_mir,
                                array_params={
                                    "nx": nx,
                                    "ny": ny,
                                    "dx_um": _to_um(dx, dbu),
                                    "dy_um": _to_um(dy, dbu),
                                },
                            )
                            records.append(rec)
                            summary["by_depth"][str(next_depth)] = summary["by_depth"].get(str(next_depth), 0) + 1
                else:
                    bb_root = child_bbox.transformed(t_root_to_child)
                    rec_bbox_um = _box_to_um_tuple(bb_root, dbu)
                    rec_off_um = _offset_from_trans_um(t_root_to_child, dbu)
                    rec_rot = _rot_from_trans(t_root_to_child)
                    rec_mir = _mirror_from_trans(t_root_to_child)

                    if (start_hier <= next_depth) and (end_hier < 0 or next_depth <= end_hier):
                        rec = _emit_instance_record(
                            depth=next_depth,
                            path_names=path_names,
                            parent_cell=parent_cell.name,
                            child_cell=child_cell.name,
                            is_array=False,
                            bbox_um=rec_bbox_um,
                            origin=rec_off_um,
                            rot_deg=rec_rot,
                            mirror=rec_mir,
                        )
                        records.append(rec)
                        summary["by_depth"][str(next_depth)] = summary["by_depth"].get(str(next_depth), 0) + 1

                if allow_descend and (end_hier < 0 or next_depth < end_hier):
                    stack.append(
                        (
                            child_cell,
                            next_depth,
                            t_root_to_child,
                            tuple(list(path_idx) + [child_idx]),
                            tuple(list(path_names) + [child_cell.name]),
                        )
                    )
            except Exception as exc:
                if verbose:
                    print(f"[DEBUG] Error while processing instance in '{parent_cell.name}': {exc}")
                continue

    summary["count"] = len(records)
    if verbose:
        print(f"[DEBUG] Enumeration complete. Found {summary['count']} records.")
    result = {
        "ok": True,
        "summary": summary,
        "records": records,
    }
    if output_csv_path:
        try:
            if records:
                directory = os.path.dirname(output_csv_path)
                if directory:
                    os.makedirs(directory, exist_ok=True)
            with open(output_csv_path, "w") as csv_file:
                csv_file.write(
                    "depth,path,parent_cell,child_cell,is_array,"
                    "origin_x,origin_y,rot_deg,mirror_x,"
                    "bbox_x1_um,bbox_y1_um,bbox_x2_um,bbox_y2_um,"
                    "array_nx,array_ny,array_dx_um,array_dy_um\n"
                )
                for rec in records:
                    xform = rec["xform_in_root"]
                    bbox = rec["bbox_in_root_um"]
                    array_info = rec.get("array", {})
                    csv_file.write(
                        f"{rec['depth']},\"{'/'.join(rec['path'])}\",{rec['parent_cell']},{rec['child_cell']},"
                        f"{int(rec['is_array'])},"
                        f"{xform['origin']['x']:.6f},{xform['origin']['y']:.6f},"
                        f"{xform['rot_deg']},{int(xform['mirror_x'])},"
                        f"{bbox['x1']:.6f},{bbox['y1']:.6f},{bbox['x2']:.6f},{bbox['y2']:.6f},"
                        f"{array_info.get('nx','')},{array_info.get('ny','')},"
                        f"{array_info.get('dx_um','')},{array_info.get('dy_um','')}\n"
                    )
            result["csv"] = output_csv_path
        except Exception as exc:
            result.setdefault("warnings", []).append(f"CSV export failed: {exc}")
    return result


def klayout_create_cell_with_shapes_from_csv(
    input_csv,
    output_gds=None,
    *,
    layout=None,
    dbu=0.001,
    default_cell="top",
    merge_cells=False,
    strict=True,
    include_summary=False,
):
    if not os.path.exists(input_csv):
        return {"ok": False, "error": f"Input CSV not found: {input_csv}"}

    import csv

    target_layout = layout or pya.Layout()
    if layout is None or not merge_cells:
        target_layout.dbu = float(dbu)

    cell_cache = {}

    def get_cell(name):
        name = (name or default_cell).strip() or default_cell
        if name in cell_cache:
            return cell_cache[name]
        cell = target_layout.create_cell(name)
        cell_cache[name] = cell
        return cell

    def parse_layer(value):
        if value is None or value == "":
            return 0, 0
        txt = str(value).strip().replace(":", "/").replace(".", "/")
        parts = [p for p in txt.split("/") if p]
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        if len(parts) == 1:
            return int(parts[0]), 0
        raise ValueError(f"Invalid layer spec '{value}'")

    def bool_from(value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        txt = str(value).strip().lower()
        return txt in ("1", "true", "yes", "y")

    def to_units(value):
        return int(round(float(value) / target_layout.dbu))

    total_rows = 0
    shapes_written = 0
    errors = []

    with open(input_csv, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total_rows += 1
            try:
                cell_name = row.get("cell_name") or default_cell
                layer_number, layer_datatype = parse_layer(row.get("layer"))
                is_rectangle = bool_from(row.get("is_rectangle"))
                polygon_vertices = (row.get("polygon_vertices") or "").strip()

                cell = get_cell(cell_name)
                layer_index = target_layout.layer(pya.LayerInfo(layer_number, layer_datatype))

                if is_rectangle or not polygon_vertices:
                    bbox_x1 = to_units(row.get("bbox_x1", 0))
                    bbox_y1 = to_units(row.get("bbox_y1", 0))
                    bbox_x2 = to_units(row.get("bbox_x2", 0))
                    bbox_y2 = to_units(row.get("bbox_y2", 0))
                    if bbox_x1 == bbox_x2 or bbox_y1 == bbox_y2:
                        raise ValueError("Rectangle has zero width or height")
                    box = pya.Box(bbox_x1, bbox_y1, bbox_x2, bbox_y2)
                    cell.shapes(layer_index).insert(box)
                else:
                    coords = polygon_vertices.split("_")
                    numbers = [float(c) for c in coords if c]
                    if len(numbers) < 6 or len(numbers) % 2 != 0:
                        raise ValueError("Invalid polygon_vertices entry")
                    points = [
                        pya.Point(to_units(numbers[i]), to_units(numbers[i + 1]))
                        for i in range(0, len(numbers), 2)
                    ]
                    if len(points) < 3:
                        raise ValueError("Polygon needs at least 3 points")
                    polygon = pya.Polygon(points)
                    cell.shapes(layer_index).insert(polygon)

                shapes_written += 1
            except Exception as exc:
                errors.append(f"Row {total_rows}: {exc}")
                if strict:
                    raise

    if output_gds:
        directory = os.path.dirname(output_gds)
        if directory:
            os.makedirs(directory, exist_ok=True)
        target_layout.write(output_gds)

    result = {
        "ok": True,
        "result": {
            "input_csv": input_csv,
            "output_gds": output_gds,
            "dbu": target_layout.dbu,
            "cells": list(cell_cache.keys()),
            "shapes": shapes_written,
            "rows": total_rows,
        }
    }
    if errors:
        result["result"]["errors"] = errors
    if include_summary:
        result["result"]["layout"] = target_layout
    return result


def klayout_create_array(
    layout,
    *,
    target_cell,
    top_cell="top",
    origin_x_um,
    origin_y_um,
    pitch_x_um,
    pitch_y_um,
    nx,
    ny,
    clear_top=False,
    output_gds=None,
):
    if layout is None:
        return {"ok": False, "error": "Layout object is required"}

    base_cell = layout.cell(target_cell)
    if base_cell is None:
        return {"ok": False, "error": f"Cell '{target_cell}' not found"}

    dbu = layout.dbu
    if dbu <= 0:
        return {"ok": False, "error": "Invalid layout DBU"}

    top = layout.cell(top_cell) or layout.create_cell(top_cell)
    if clear_top:
        top.clear()

    pitch_x = int(round(float(pitch_x_um) / dbu))
    pitch_y = int(round(float(pitch_y_um) / dbu))
    origin_x = int(round(float(origin_x_um) / dbu))
    origin_y = int(round(float(origin_y_um) / dbu))
    array = pya.CellInstArray(
        base_cell.cell_index(),
        pya.Trans(origin_x, origin_y),
        pya.Vector(pitch_x, 0),
        pya.Vector(0, pitch_y),
        int(nx),
        int(ny),
    )
    top.insert(array)

    # if output_gds:
    #     directory = os.path.dirname(output_gds)
    #     if directory:
    #         os.makedirs(directory, exist_ok=True)
    #     layout.write(output_gds)

    return {
        "ok": True,
        "result": {
            "message": f"Created array of '{target_cell}' in '{top_cell}'",
            "top_cell": top_cell,
            "target_cell": target_cell,
            "array_origin_x_um": float(origin_x_um),
            "array_origin_y_um": float(origin_y_um),
            "array_pitch_x_um": float(pitch_x_um),
            "array_pitch_y_um": float(pitch_y_um),
            "array_x_number": int(nx),
            "array_y_number": int(ny),
            "output_gds": output_gds,
        },
        "layout" : layout
    }


def merge_layer_shapes(
    layout,
    layer_number=100,
    layer_datatype=100,
    cell_name=None,
    include_hierarchy=False,
    capture_vertices=False
):
    """
    Merge shapes on a specified layer using KLayout's Region class.

    Returns a tuple of (merged_shapes, original_shape_count).
    """
    layer_info = pya.LayerInfo(layer_number, layer_datatype)
    layer_index = layout.find_layer(layer_info)
    if layer_index < 0:
        return [], 0
    dbu = layout.dbu

    target_cells = [layout.cell(cell_name)] if cell_name else list(layout.each_cell())
    merged_shapes = []
    original_shape_count = 0

    for cell in target_cells:
        if cell is None:
            continue

        if include_hierarchy:
            region = pya.Region(cell.begin_shapes_rec(layer_index))
        else:
            shapes_accessor = cell.shapes(layer_index)
            if shapes_accessor.is_empty():
                continue
            region = pya.Region(shapes_accessor)

        if region.is_empty():
            continue

        original_shape_count += region.size()
        merged_region = region.merged()
        for polygon in merged_region.each():
            bbox = polygon.bbox()
            raw_points = [pya.Point(pt.x, pt.y) for pt in polygon.each_point_hull()]
            normalized_points = _normalize_polygon_vertices(raw_points)
            vertex_string = _points_to_vertex_string(
                normalized_points,
                dbu=dbu,
                unit="um",
                precision=6
            )
            is_rectangle = int(_is_axis_aligned_rectangle(normalized_points))
            polygon_points = [[pt.x, pt.y] for pt in normalized_points]
            merged_shapes.append({
                "cell_name": cell.name,
                "layer_number": layer_number,
                "layer_datatype": layer_datatype,
                "bbox_x1": bbox.left,
                "bbox_y1": bbox.bottom,
                "bbox_x2": bbox.right,
                "bbox_y2": bbox.top,
                "is_rectangle": is_rectangle,
                "polygon_vertices": vertex_string,
                "polygon_points": polygon_points
            })

    return merged_shapes, original_shape_count


def _box_from_any(bbox, dbu):
    """Convert a Box/DBox to an integer Box."""
    if isinstance(bbox, pya.Box):
        return bbox
    if isinstance(bbox, pya.DBox):
        return pya.Box(
            int(round(bbox.left / dbu)),
            int(round(bbox.bottom / dbu)),
            int(round(bbox.right / dbu)),
            int(round(bbox.top / dbu)),
        )
    raise ValueError("Unsupported bbox type")


def klayout_draw_cell_bbox_shape(
    layout,
    cell_name,
    layer_number_datatype,
    *,
    include_descendants=True,
    clear_existing=True
):
    """
    Create a rectangular shape matching the bounding box of the specified cell.

    Args:
        layout (pya.Layout): Layout containing the target cell.
        cell_name (str): Name of the cell whose bbox will be drawn.
        layer_number_datatype (Union[str, tuple, dict]): Layer specification for the bbox polygon.
        include_descendants (bool): If True, bbox covers hierarchical contents via cell.dbbox().
        clear_existing (bool): If True, clears existing shapes on that layer in the cell before drawing.
    """
    cell = layout.cell(cell_name)
    if cell is None:
        return {"ok": False, "error": f"Cell '{cell_name}' not found"}

    resolved_spec = (
        layer_number_datatype
        or {}
    )
    try:
        layer_number, layer_datatype = _parse_layer_spec(resolved_spec)
    except ValueError:
        try:
            layer_number, layer_datatype = _parse_layer_spec(
                {"layer_number": resolved_spec, "layer_datatype": 0}
            )
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}

    bbox = cell.dbbox() if include_descendants else cell.bbox()
    if bbox is None or bbox.width() <= 0 or bbox.height() <= 0:
        return {"ok": False, "error": f"Cell '{cell_name}' has no geometries for bbox computation"}

    int_box = _box_from_any(bbox, layout.dbu)
    if int_box.width() <= 0 or int_box.height() <= 0:
        return {"ok": False, "error": "Computed bounding box is void"}

    layer_index = layout.layer(pya.LayerInfo(layer_number, layer_datatype))
    if clear_existing:
        cell.shapes(layer_index).clear()

    cell.shapes(layer_index).insert(int_box)

    return {
        "ok": True,
        "result": {
            "cell_name": cell_name,
            "layer": f"{layer_number}.{layer_datatype}",
            "bbox": {
                "x1": int_box.left,
                "y1": int_box.bottom,
                "x2": int_box.right,
                "y2": int_box.top
            },
            "include_descendants": include_descendants
        }
    }


def klayout_merge_shapes_through_hier_by_input_cell_name_and_list_layers(
    input_cell_name,
    input_list_layers,
    output_list_of_layers=None,
    output_gds_file_name="cell_hier_merge_shapes.gds",
    *,
    layout=None,
    input_file=None,
    output_csv_path=None,
    include_hierarchy=True
):
    """
    Merge shapes from multiple layers through the hierarchy beneath input_cell_name.

    If output_list_of_layers is omitted, each layer number is mapped by adding 10000
    while keeping the original datatype (e.g., 100/100 -> 10100/100).
    """
    source_file = input_file or "cell_hier.gds"
    if layout is None:
        if not os.path.exists(source_file):
            return {"ok": False, "error": f"Input file not found: {source_file}"}
        layout = klayout_import_layout(source_file)
        if layout is None:
            return {"ok": False, "error": f"Failed to read layout file: {source_file}"}

    try:
        input_layers = _normalize_layer_list(input_list_layers)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    if not input_layers:
        return {"ok": False, "error": "input_list_layers must contain at least one layer"}

    if output_list_of_layers:
        try:
            output_layers = _normalize_layer_list(output_list_of_layers)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        if len(output_layers) != len(input_layers):
            return {
                "ok": False,
                "error": "output_list_of_layers length must match input_list_layers length"
            }
    else:
        output_layers = [(number + 10000, datatype) for number, datatype in input_layers]

    target_cell = layout.cell(input_cell_name)
    if target_cell is None:
        return {"ok": False, "error": f"Cell '{input_cell_name}' not found in layout"}

    cleared_layers = set()
    csv_rows = []
    summary = []
    total_original = 0
    total_merged = 0

    for (src_number, src_datatype), (dst_number, dst_datatype) in zip(input_layers, output_layers):
        merged_shapes, original_count = merge_layer_shapes(
            layout,
            layer_number=src_number,
            layer_datatype=src_datatype,
            cell_name=input_cell_name,
            include_hierarchy=include_hierarchy,
            capture_vertices=True
        )

        layer_info = pya.LayerInfo(dst_number, dst_datatype)
        dst_layer_index = layout.layer(layer_info)
        cache_key = (dst_number, dst_datatype)

        if cache_key not in cleared_layers:
            target_cell.shapes(dst_layer_index).clear()
            cleared_layers.add(cache_key)

        written = 0
        for shape in merged_shapes:
            point_pairs = shape.get("polygon_points")
            if point_pairs:
                points = [pya.Point(int(x), int(y)) for x, y in point_pairs]
            else:
                vertices = shape.get("polygon_vertices")
                if isinstance(vertices, str) and layout.dbu:
                    coords = vertices.split("_")
                    if len(coords) % 2 != 0:
                        continue
                    points = [
                        pya.Point(
                            int(round(float(coords[i]) / layout.dbu)),
                            int(round(float(coords[i + 1]) / layout.dbu))
                        )
                        for i in range(0, len(coords), 2)
                    ]
                else:
                    points = []
            if len(points) < 3:
                continue
            polygon = pya.Polygon(points)
            target_cell.shapes(dst_layer_index).insert(polygon)
            written += 1
            csv_rows.append({
                "cell_name": input_cell_name,
                "src_layer": f"{src_number}.{src_datatype}",
                "dst_layer": f"{dst_number}.{dst_datatype}",
                "bbox_x1": shape["bbox_x1"],
                "bbox_y1": shape["bbox_y1"],
                "bbox_x2": shape["bbox_x2"],
                "bbox_y2": shape["bbox_y2"],
                "is_rectangle": shape.get("is_rectangle", 0),
                "polygon_vertices": shape.get("polygon_vertices")
            })

        summary.append({
            "source_layer": f"{src_number}.{src_datatype}",
            "destination_layer": f"{dst_number}.{dst_datatype}",
            "original_shapes": original_count,
            "merged_shapes": written
        })
        total_original += original_count
        total_merged += written

    gds_dir = os.path.dirname(output_gds_file_name)
    if gds_dir:
        os.makedirs(gds_dir, exist_ok=True)
    layout.write(output_gds_file_name)

    if output_csv_path:
        csv_dir = os.path.dirname(output_csv_path)
        if csv_dir:
            os.makedirs(csv_dir, exist_ok=True)
        with open(output_csv_path, "w") as csv_file:
            csv_file.write(
                "cell_name,src_layer,dst_layer,bbox_x1,bbox_y1,bbox_x2,bbox_y2,is_rectangle,polygon_vertices\n"
            )
            for row in csv_rows:
                csv_x1 = klayout_format_dimension(row["bbox_x1"], layout.dbu)
                csv_y1 = klayout_format_dimension(row["bbox_y1"], layout.dbu)
                csv_x2 = klayout_format_dimension(row["bbox_x2"], layout.dbu)
                csv_y2 = klayout_format_dimension(row["bbox_y2"], layout.dbu)
                csv_file.write(
                    f"{row['cell_name']},{row['src_layer']},{row['dst_layer']},"
                    f"{csv_x1},{csv_y1},{csv_x2},{csv_y2},"
                    f"{row['is_rectangle']},{row['polygon_vertices']}\n"
                )

    message = (
        f"Merged {total_original} shapes into {total_merged} polygons across {len(input_layers)} layer pairs"
        if total_merged
        else "No shapes were found on the specified layers; outputs were created without polygons"
    )

    return {
        "ok": True,
        "result": {
            "message": message,
            "input_file": source_file,
            "output_file": output_csv_path,
            "output_gds": output_gds_file_name,
            "cell_name": input_cell_name,
            "layers": summary,
            "total_input_shapes": total_original,
            "total_merged_shapes": total_merged,
            "include_hierarchy": include_hierarchy
        }
    }
