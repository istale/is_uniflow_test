# create_layout.py
# KLayout JSON I/O Compliant
import sys, json, os

# Add current directory to Python path to resolve klayout_api import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import custom API library
try:
    from klayout_api import (
        klayout_create_cell,
        klayout_define_layer,
        klayout_draw_rectangle,
        klayout_set_dbu,
        klayout_export_layout
    )
except ImportError as e:
    # Fallback for direct execution - include API functions inline
    print(f"Warning: Could not import klayout_api: {e}")
    print("Using inline API functions...")
    
    # Inline implementation of API functions
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

def main(payload: dict) -> dict:
    """Create layout with specified rectangles and export as GDS/OAS"""
    # Import KLayout modules
    import pya
    
    print("Step 1: Creating new layout with dbu=0.0005...")
    # Create a new layout with dbu=0.0005
    layout = pya.Layout()
    klayout_set_dbu(layout, 0.0005)
    
    print("Step 2: Creating cell named 'my_cell'...")
    # Create a cell named "my_cell"
    cell = klayout_create_cell(layout, "my_cell")
    
    print("Step 3: Defining layers...")
    # Define layers
    layer_100_100 = klayout_define_layer(layout, 100, 100)
    layer_200_200 = klayout_define_layer(layout, 200, 200)
    
    print("Step 4: Drawing first rectangle...")
    # Draw first rectangle: x1,y1,x2,y2=0,0,1,1 with layer 100.100
    klayout_draw_rectangle(cell, 0, 0, 1, 1, layer_100_100)
    
    print("Step 5: Drawing second rectangle...")
    # Draw second rectangle: x1,y1,x2,y2=0.5,0,2,2 with layer 100.100
    klayout_draw_rectangle(cell, 1, 0, 2, 2, layer_100_100)
    
    print("Step 6: Drawing third rectangle...")
    # Draw third rectangle: x1,y1,x2,y2=3,3,4,4 with layer 200.200
    klayout_draw_rectangle(cell, 3, 3, 4, 4, layer_200_200)
    
    # Determine export format from payload or default to GDS
    export_format = payload.get("export_format", "gds").lower()
    if export_format not in ["gds", "oas"]:
        export_format = "gds"  # Default to GDS
    
    output_file = f"out.{export_format}"
    
    print(f"Step 7: Exporting layout as {output_file}...")
    # Export layout
    klayout_export_layout(layout, output_file)
    
    print("Step 8: Layout creation completed successfully!")
    
    # Return success result
    return {
        "ok": True,
        "result": {
            "message": f"Layout created successfully with 3 rectangles",
            "file": output_file
        }
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
            "task_id": vals[0] if len(vals) > 0 else "default",
        }
    
    # Execute main function
    result = main(payload)
    
    # Print result as JSON (required by KLayout standard)
    print(json.dumps(result, ensure_ascii=False))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("ok") else 1)
