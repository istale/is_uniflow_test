# merge_shapes.py
# KLayout JSON I/O Compliant - Merge shapes from layer 100.100 and export to CSV
import sys, json, os

# Add current directory to Python path to resolve klayout_api import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import API helpers if available, otherwise rely on direct pya usage
try:
    from klayout_api import (
        klayout_import_layout,
        klayout_merge_shapes_through_hier_by_input_cell_name_and_list_layers,
    )
except ImportError as e:
    print(f"Warning: Could not import klayout_api: {e}")
    print("Using direct KLayout API instead.")
    import pya
    def klayout_import_layout(input_file):
        layout = pya.Layout()
        layout.read(input_file)
        return layout
    def klayout_merge_shapes_through_hier_by_input_cell_name_and_list_layers(*args, **kwargs):
        raise ImportError("klayout_api module unavailable; helper not defined.")

def main(payload: dict) -> dict:
    """Main function to read GDS, merge shapes from a target layer, and export results"""
    try:
        # Input/output defaults tailored for cell_hierarchy flow
        input_file = payload.get("input_file", "cell_hier.gds")
        
        # Check if input file exists
        if not os.path.exists(input_file):
            return {
                "ok": False,
                "error": f"Input file not found: {input_file}"
            }
        
        print(f"Reading GDS file: {input_file}")
        
        # Use the API to read the layout
        layout = klayout_import_layout(input_file)
        if layout is None:
            return {
                "ok": False,
                "error": f"Failed to read layout file: {input_file}"
            }
        
        print(f"Layout read successfully.")
        
        layer_spec = payload.get("layer_spec") or payload.get("layer")
        if layer_spec:
            normalized = layer_spec.replace(":", "/").replace(".", "/")
            parts = [p.strip() for p in normalized.split("/") if p.strip()]
            if len(parts) == 2:
                payload.setdefault("layer_number", int(parts[0]))
                payload.setdefault("layer_datatype", int(parts[1]))
            else:
                return {
                    "ok": False,
                    "error": f"Invalid layer_spec '{layer_spec}'. Use 'number/datatype'."
                }

        layer_number = payload.get("layer_number", 100)
        layer_datatype = payload.get("layer_datatype", 100)
        cell_name = payload.get("cell_name", "Unit_A")
        include_hierarchy = payload.get("include_hierarchy", bool(cell_name))

        output_layer_spec = payload.get("output_layer_spec")
        if output_layer_spec:
            normalized = output_layer_spec.replace(":", "/").replace(".", "/")
            parts = [p.strip() for p in normalized.split("/") if p.strip()]
            if len(parts) == 2:
                payload.setdefault("output_layer_number", int(parts[0]))
                payload.setdefault("output_layer_datatype", int(parts[1]))
            else:
                return {
                    "ok": False,
                    "error": f"Invalid output_layer_spec '{output_layer_spec}'. Use 'number/datatype'."
                }

        output_layer_number = int(payload.get("output_layer_number", layer_number))
        if "output_layer_datatype" in payload:
            output_layer_datatype = int(payload["output_layer_datatype"])
        else:
            output_layer_datatype = 101 if layer_number == 100 and layer_datatype == 100 else layer_datatype
        
        csv_file = payload.get("output_file", "cell_hier_merge_shapes.csv")
        output_gds = payload.get("output_gds", "cell_hier_merge_shapes.gds")

        input_layers_payload = payload.get("input_list_layers")
        if not input_layers_payload:
            input_layers_payload = [{
                "layer_number": layer_number,
                "layer_datatype": layer_datatype
            }]

        output_layers_payload = (
            payload.get("output_list_of_layers")
            or payload.get("output_list_layers")
        )
        if not output_layers_payload and (
            "output_layer_number" in payload
            or "output_layer_datatype" in payload
            or output_layer_spec
        ):
            output_layers_payload = [{
                "layer_number": output_layer_number,
                "layer_datatype": output_layer_datatype
            }]

        helper_result = klayout_merge_shapes_through_hier_by_input_cell_name_and_list_layers(
            cell_name,
            input_layers_payload,
            output_layers_payload,
            output_gds,
            layout=layout,
            input_file=input_file,
            output_csv_path=csv_file,
            include_hierarchy=include_hierarchy
        )

        return helper_result
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Read input parameter from KLayout -rd flag
    raw = input_parameter
    
    try:
        # Try to parse as JSON first
        payload = json.loads(raw)
    except Exception:
        # Fallback: comma-separated string (for backward compatibility)
        vals = [x.strip() for x in raw.split(",")]
        payload = {
            "input_file": vals[0] if len(vals) > 0 and vals[0] else "cell_hier.gds",
            "output_file": vals[1] if len(vals) > 1 and vals[1] else "cell_hier_merge_shapes.csv",
            "layer_number": int(vals[2]) if len(vals) > 2 and vals[2] else 100,
            "layer_datatype": int(vals[3]) if len(vals) > 3 and vals[3] else 100,
            "cell_name": vals[4] if len(vals) > 4 and vals[4] else "Unit_A",
            "output_gds": vals[5] if len(vals) > 5 and vals[5] else "cell_hier_merge_shapes.gds"
        }
    
    # Execute main function
    result = main(payload)
    
    # Print result as JSON (required by KLayout standard)
    print(json.dumps(result, ensure_ascii=False))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("ok") else 1)
