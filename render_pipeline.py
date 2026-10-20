import bpy
import json
import os
import math

def setup_scene():
    """Wipes default meshes, configures the camera, and binds it to the scene."""
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
        
    cam = bpy.data.objects.get("Camera")
    if cam:
        # Move camera out and angle it directly down at the origin (0,0,0)
        cam.location = (0.0, -6.0, 6.0)
        cam.rotation_euler = (math.radians(45), 0.0, 0.0) # Angle down 45 degrees
        
        # CRITICAL FIX: Explicitly set this camera as the active rendering camera
        bpy.context.scene.camera = cam

def create_material(name, rgba_color):
    """Creates a basic solid color material for rendering."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = False # Simple viewport coloring
    mat.diffuse_color = rgba_color
    return mat

def build_garden_container(config, wood_mat):
    """Draws the wooden frame perimeter based on selected geometry specs."""
    shape = config.get("garden_shape", "Rectangle")
    dims = config.get("dimensions", {"length_ft": 6.0, "width_ft": 4.0})
    
    if shape == "Rectangle":
        length = dims.get("length_ft", 6.0)
        width = dims.get("width_ft", 4.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.1))
        box = bpy.context.active_object
        box.scale = (length, width, 0.2)
        box.data.materials.append(wood_mat)
        
    elif shape == "Circle":
        radius = dims.get("radius_ft", 3.0)
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=0.2, vertices=32, location=(0,0,0.1))
        circle_bed = bpy.context.active_object
        circle_bed.data.materials.append(wood_mat)

def generate_growth_sim(layout_data, plant_mat):
    """Generates basic geometric cylinders that scale upward over time."""
    for site in layout_data:
        coords = site.get("coordinates", {"x": 0.0, "y": 0.0})
        plant = site.get("plant", {})
        
        # Add basic cylinder sprout
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.0, location=(coords["x"], coords["y"], 0.1))
        sprout = bpy.context.active_object
        sprout.data.materials.append(plant_mat)
        
        # Adjust mesh origin to the bottom of the cylinder
        for vert in sprout.data.vertices:
            vert.co.z += 0.5
            
        germ_frame = int(plant.get("germination_days", 5))
        mature_frame = int(plant.get("days_to_maturity", 60))
        target_height = float(plant.get("max_height_inches", 12.0)) / 12.0
        
        # Animate growth scaling metrics
        sprout.scale = (0.001, 0.001, 0.001)
        sprout.keyframe_insert(data_path="scale", frame=1)
        sprout.keyframe_insert(data_path="scale", frame=germ_frame)
        
        sprout.scale = (1.0, 1.0, target_height)
        sprout.keyframe_insert(data_path="scale", frame=mature_frame)

def render_output_pipeline():
    """Forces fast workbench rendering profile outputs with materials active."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 90
    
    # Render with standard lighting and material configurations
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL' # Read actual materials
    
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = os.path.join(os.getcwd(), "garden_timelapse.mp4")
    
    print("--- STARTING RENDER PRODUCTION PIPELINE ---")
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    setup_scene()
    
    # Initialize basic colored materials
    brown_wood = create_material("WoodSoilMat", (0.35, 0.20, 0.10, 1.0))
    green_sprout = create_material("PlantSproutMat", (0.12, 0.55, 0.22, 1.0))
    
    default_config = {"garden_shape": "Rectangle", "dimensions": {"length_ft": 6.0, "width_ft": 4.0}}
    default_layout = [
        {"emitterId": 0, "coordinates": {"x": -1.5, "y": -0.5}, "plant": {"germination_days": 7, "days_to_maturity": 60, "max_height_inches": 24}},
        {"emitterId": 1, "coordinates": {"x": 0.0, "y": 0.5}, "plant": {"germination_days": 10, "days_to_maturity": 75, "max_height_inches": 12}},
        {"emitterId": 2, "coordinates": {"x": 1.5, "y": -0.5}, "plant": {"germination_days": 4, "days_to_maturity": 25, "max_height_inches": 6}}
    ]
    
    build_garden_container(default_config, brown_wood)
    generate_growth_sim(default_layout, green_sprout)
    render_output_pipeline()
