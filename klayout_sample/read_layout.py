# read_layout.py
# KLayout JSON I/O Compliant - Read GDS and export shapes to CSV
import sys, json, os

# Add current directory to Python path to resolve klayout_api import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced API library
try:
    from klayout_api import (
        klayout_import_layout,
        klayout_extract_shapes_to_csv
    )
except ImportError as e:
    # Fallback for direct execution - include API functions inline (simplified version)
    print(f"Warning: Could not import klayout_api: {e}")
    print("Using inline implementation...")

def main(payload: dict) -> dict:
    """Read GDS file and extract shape information to CSV using enhanced API"""
    try:
        # Get input file from payload or default to out.gds
        input_file = payload.get("input_file", "out.gds")
        
        # Check if input file exists
        if not os.path.exists(input_file):
            return {
                "ok": False,
                "error": f"Input file not found: {input_file}"
            }
        
        print(f"Reading GDS file: {input_file}")
        
        # Use the enhanced API to read the layout
        layout = klayout_import_layout(input_file)
        if layout is None:
            return {
                "ok": False,
                "error": f"Failed to read layout file: {input_file}"
            }
        
        print(f"Layout read successfully.")
        
        # Prepare CSV output
        csv_file = payload.get("output_file", "layout_shape.csv")
        cell_name = payload.get("cell_name")
        
        # Extract shapes and export to CSV using the enhanced API
        success, shapes_data = klayout_extract_shapes_to_csv(
            layout,
            cell_name=cell_name,
            output_csv_file_name=csv_file
        )
        
        if not success:
            return {
                "ok": False,
                "error": f"Failed to export shapes to CSV: {csv_file}"
            }
        
        total_shapes = len(shapes_data)
        print(f"Total shapes processed: {total_shapes}")
        
        # Return success result
        return {
            "ok": True,
            "result": {
                "message": f"Successfully read {input_file} and exported {total_shapes} shapes to {csv_file}",
                "input_file": input_file,
                "output_file": csv_file,
                "total_shapes": total_shapes
            }
        }
        
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
            "input_file": vals[0] if len(vals) > 0 else "out.gds",
            "output_file": vals[1] if len(vals) > 1 else "layout_shape.csv"
        }
    
    # Execute main function
    result = main(payload)
    
    # Print result as JSON (required by KLayout standard)
    print(json.dumps(result, ensure_ascii=False))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("ok") else 1)
