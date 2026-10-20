import bpy
import json
import os
import math

def setup_scene():
    """Wipes standard default startup meshes and positions a camera overview."""
    # Remove default box
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
        
    # Position the camera directly top-down over the center of the bed
    cam = bpy.data.objects.get("Camera")
    if cam:
        cam.location = (0.0, -0.5, 9.5)
        cam.rotation_euler = (0.0, 0.0, 0.0) # Downward facing orthogonal aspect

def build_garden_container(config):
    """Draws the wooden frame perimeter based on selected geometry specs."""
    shape = config.get("garden_shape", "Rectangle")
    dims = config.get("dimensions", {"length_ft": 6.0, "width_ft": 4.0})
    
    if shape == "Rectangle":
        length = dims.get("length_ft", 6.0)
        width = dims.get("width_ft", 4.0)
        
        # Add basic wood framing primitive box
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.25))
        box = bpy.context.active_object
        box.name = "Garden_Frame"
        box.scale = (length, width, 0.5)
        
    elif shape == "Circle":
        radius = dims.get("radius_ft", 3.0)
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=0.5, vertices=64, location=(0,0,0.25))
        circle_bed = bpy.context.active_object
        circle_bed.name = "Garden_Frame"

def generate_growth_sim(layout_data):
    """Generates plant entities and keyframes their Z scale based on maturity parameters."""
    for site in layout_data:
        coords = site.get("coordinates", {"x": 0.0, "y": 0.0})
        plant = site.get("plant", {"plant_name": "Crop", "germination_days": 5, "days_to_maturity": 60, "max_height_inches": 12})
        
        # Instantiate placeholder cone cylinder as a sprout stem
        bpy.ops.mesh.primitive_cone_add(radius1=0.03, radius2=0.01, depth=1.0, location=(coords["x"], coords["y"], 0.5))
        sprout = bpy.context.active_object
        sprout.name = f"Sprout_{site.get('emitterId', 0)}"
        
        # Set origin point to base of plant geometry for natural upward scaling
        sprout.geometry_set_to_origin()
        
        # Set scale timeline frames
        germ_frame = int(plant.get("germination_days", 5))
        mature_frame = int(plant.get("days_to_maturity", 60))
        target_height_ft = float(plant.get("max_height_inches", 12.0)) / 12.0
        
        # Frame 1 to Germination: Beneath soil profile (invisible scale)
        sprout.scale = (0.001, 0.001, 0.001)
        sprout.keyframe_insert(data_path="scale", frame=1)
        sprout.keyframe_insert(data_path="scale", frame=germ_frame)
        
        # Germination to Maturity: Vertical exponential extrusion scaling upward
        sprout.scale = (1.0, 1.0, target_height_ft)
        sprout.keyframe_insert(data_path="scale", frame=mature_frame)

def render_output_pipeline():
    """Configures environment parameters and renders video frames down to an MP4 video."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 90 # 90 days / 90 frames timelapse duration
    
    # Configure export engine properties
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = os.path.join(os.getcwd(), "garden_timelapse.mp4")
    
    # Trigger headless rendering compilation execution sequence
    print("--- CRITICAL STAGE: Exporting high resolution timeline frames ---")
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    setup_scene()
    
    # Built-in diagnostic fallback dataset array
    default_config = {"garden_shape": "Rectangle", "dimensions": {"length_ft": 6.0, "width_ft": 4.0}}
    default_layout = [
        {"emitterId": 0, "coordinates": {"x": -1.5, "y": -0.5}, "plant": {"plant_name": "Kale", "germination_days": 7, "days_to_maturity": 60, "max_height_inches": 24}},
        {"emitterId": 1, "coordinates": {"x": 0.0, "y": 0.5}, "plant": {"plant_name": "Carrots", "germination_days": 10, "days_to_maturity": 75, "max_height_inches": 12}},
        {"emitterId": 2, "coordinates": {"x": 1.5, "y": -0.5}, "plant": {"plant_name": "Radishes", "germination_days": 4, "days_to_maturity": 25, "max_height_inches": 6}}
    ]
    
    build_garden_container(default_config)
    generate_growth_sim(default_layout)
    render_output_pipeline()
