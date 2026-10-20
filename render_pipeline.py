import bpy
import json
import os
import math

def build_fresh_scene():
    """Completely purges the startup template and builds a fresh, verified environment."""
    # Delete absolutely every existing object (Meshes, Lights, Cameras)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # 1. Create a pristine Camera from scratch
    bpy.ops.object.camera_add(location=(0.0, -8.0, 7.0))
    new_cam = bpy.context.active_object
    new_cam.name = "Sim_Camera"
    # Rotate 50 degrees on X to point downward, 0 on Y, 0 on Z
    new_cam.rotation_euler = (math.radians(50), 0.0, 0.0)
    bpy.context.scene.camera = new_cam # Force-bind to active render output

    # 2. Create a Sunlight source so Workbench viewport materials render clearly
    bpy.ops.object.light_add(type='SUN', location=(5.0, -5.0, 10.0))
    sun = bpy.context.active_object
    sun.data.energy = 3.0

def create_solid_material(name, rgba_color):
    """Creates a viewport-compatible material profile for flat shading color checks."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = False
    mat.diffuse_color = rgba_color
    return mat

def build_garden_container(config, wood_mat):
    """Draws a solid base container box representing your custom garden frame."""
    shape = config.get("garden_shape", "Rectangle")
    dims = config.get("dimensions", {"length_ft": 6.0, "width_ft": 4.0})
    
    if shape == "Rectangle":
        length = float(dims.get("length_ft", 6.0))
        width = float(dims.get("width_ft", 4.0))
        # Spawn a container structure centered at coordinates (0,0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.1))
        box = bpy.context.active_object
        box.name = "Garden_Bed_Mesh"
        box.scale = (length, width, 0.2)
        box.data.materials.append(wood_mat)
        
    elif shape == "Circle":
        radius = float(dims.get("radius_ft", 3.0))
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=0.2, vertices=64, location=(0.0, 0.0, 0.1))
        circle_bed = bpy.context.active_object
        circle_bed.name = "Garden_Bed_Mesh"
        circle_bed.data.materials.append(wood_mat)

def generate_growth_sim(layout_data, plant_mat):
    """Generates bright plant markers that scale upward over the timeline."""
    for idx, site in enumerate(layout_data):
        coords = site.get("coordinates", {"x": 0.0, "y": 0.0})
        plant = site.get("plant", {})
        
        # Build thick, easily visible cylinder stems
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.0, location=(float(coords["x"]), float(coords["y"]), 0.1))
        sprout = bpy.context.active_object
        sprout.name = f"Sprout_Marker_{idx}"
        sprout.data.materials.append(plant_mat)
        
        # Shift vertices internal offsets so scaling happens strictly upward from soil line
        for vert in sprout.data.vertices:
            vert.co.z += 0.5
            
        germ_frame = int(plant.get("germination_days", 5))
        mature_frame = int(plant.get("days_to_maturity", 60))
        target_height = float(plant.get("max_height_inches", 12.0)) / 12.0
        
        # Bake linear scale keyframes over our 90 frame duration
        sprout.scale = (0.01, 0.01, 0.01)
        sprout.keyframe_insert(data_path="scale", frame=1)
        sprout.keyframe_insert(data_path="scale", frame=germ_frame)
        
        sprout.scale = (1.0, 1.0, target_height)
        sprout.keyframe_insert(data_path="scale", frame=mature_frame)

def execute_render():
    """Forces high visibility workbench rendering parameters out to video disk storage."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 90
    
    # Lock engine variables down tightly to flat color visibility grids
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = os.path.join(os.getcwd(), "garden_timelapse.mp4")
    
    print("--- PIPELINE EXECUTION STARTING: COMPILING VISUAL GEOMETRIES ---")
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    build_fresh_scene()
    
    # Initialize high-contrast materials (Rich Brown vs. Neon Green)
    brown_wood = create_solid_material("WoodSoilMat", (0.28, 0.14, 0.05, 1.0))
    neon_green = create_solid_material("PlantSproutMat", (0.0, 1.0, 0.2, 1.0))
    
    # Hardcoded test payload parameters mirroring our iPad application mapping configurations
    test_config = {"garden_shape": "Rectangle", "dimensions": {"length_ft": 6.0, "width_ft": 4.0}}
    test_layout = [
        {"emitterId": 0, "coordinates": {"x": -1.5, "y": 0.0}, "plant": {"germination_days": 5, "days_to_maturity": 45, "max_height_inches": 24}},
        {"emitterId": 1, "coordinates": {"x": 0.0, "y": 0.0}, "plant": {"germination_days": 10, "days_to_maturity": 65, "max_height_inches": 16}},
        {"emitterId": 2, "coordinates": {"x": 1.5, "y": 0.0}, "plant": {"germination_days": 4, "days_to_maturity": 30, "max_height_inches": 8}}
    ]
    
    build_garden_container(test_config, brown_wood)
    generate_growth_sim(test_layout, neon_green)
    execute_render()
