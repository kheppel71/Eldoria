# mygame/world/map_exporter.py
import os
from PIL import Image, ImageDraw
from evennia import DefaultRoom

def export_world_grid(tile_size=16, output_filename="evennia_world_map.png"):
    """
    Queries Evennia rooms with x, y attributes and builds an offline 
    graphical image overview of the coordinate grid.
    """
    print("Gathering room data from the database...")
    all_rooms = DefaultRoom.objects.all()
    valid_rooms = []

    # 1. Extract coordinate attributes from your rooms
    for room in all_rooms:
        x = room.db.x
        y = room.db.y
        if x is not None and y is not None:
            # Gather terrain or a default type string
            terrain = room.db.terrain_type or "default"
            valid_rooms.append({"room": room, "x": int(x), "y": int(y), "terrain": terrain.lower()})

    if not valid_rooms:
        print("❌ Error: No rooms found with 'db.x' and 'db.y' attributes set.")
        return

    # 2. Track bounds to automatically scale the output canvas
    x_coords = [r["x"] for r in valid_rooms]
    y_coords = [r["y"] for r in valid_rooms]
    
    min_x, max_x = min(x_coords), max_x(x_coords)
    min_y, max_y = min(y_coords), max_y(y_coords)
    
    grid_width = (max_x - min_x) + 1
    grid_height = (max_y - min_y) + 1
    
    canvas_width = grid_width * tile_size
    canvas_height = grid_height * tile_size

    print(f"World Grid Detected: X({min_x} to {max_x}), Y({min_y} to {max_y})")
    print(f"Generating a {canvas_width}x{canvas_height} pixel image canvas...")

    # 3. Create a blank image with a solid dark grey background
    img = Image.new("RGBA", (canvas_width, canvas_height), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)

    # 4. Define your color palette map based on terrain types
    # Format: (Red, Green, Blue, Alpha)
    color_palette = {
        "grass": (34, 139, 34, 255),       # Forest Green
        "forest": (0, 100, 0, 255),         # Dark Green
        "water": (30, 144, 255, 255),       # Dodger Blue
        "ocean": (0, 0, 139, 255),          # Dark Blue
        "mountain": (128, 128, 128, 255),   # Grey
        "stone": (105, 105, 105, 255),      # Dim Grey
        "sand": (244, 164, 96, 255),        # Sandy Brown
        "town": (220, 20, 60, 255),         # Crimson City Blocks
        "default": (160, 160, 160, 255)     # Light Grey fallback
    }

    # 5. Paint each room onto the pixel coordinates
    for r in valid_rooms:
        # Calculate grid position, applying offsets so negative coords shift safely into positive indices
        local_grid_x = r["x"] - min_x
        # Invert the Y-axis so increasing values go 'Up' instead of 'Down' on your output map
        local_grid_y = max_y - r["y"] 

        # Determine exact drawing coordinates for the tile rectangle bounds
        pixel_x1 = local_grid_x * tile_size
        pixel_y1 = local_grid_y * tile_size
        pixel_x2 = pixel_x1 + tile_size - 1
        pixel_y2 = pixel_y1 + tile_size - 1

        # Fetch matching terrain color
        color = color_palette.get(r["terrain"], color_palette["default"])

        # Render the tile rectangle block
        draw.rectangle([pixel_x1, pixel_y1, pixel_x2, pixel_y2], fill=color, outline=(0, 0, 0, 50))

    # 6. Save final file layout to disk
    try:
        img.save(output_filename)
        print(f"🎉 Success! Graphical map safely compiled to: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"❌ Failed to save image: {e}")
