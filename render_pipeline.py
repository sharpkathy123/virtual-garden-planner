import bpy
import json
import os
import math

def build_pristine_scene():
    """Wipes out default templates and builds objects explicitly via the Data API."""
    # Clear out any leftover objects from template startup layers
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
        
    scene = bpy.context.scene
    coll = scene.collection

    # 1. Create a Camera and link it to the scene structure
    cam_data = bpy.data.cameras.new("SimCamData")
    cam_obj = bpy.data.objects.new("Sim_Camera", cam_data)
    cam_obj.location = (0.0, -6.5, 6.0)
    cam_obj.rotation_euler = (math.radians(45), 0.0, 0.0) # Look downward at bed
    coll.objects.link(cam_obj)
    scene.camera = cam_obj # Explicitly lock scene viewing frame to this asset

    # 2. Create a clean Light source for raytracing calculations
    light_data = bpy.data.lights.new(name="SunData", type='SUN')
    light_data.energy = 4.0
    light_obj = bpy.data.objects.new("Sim_Sun", light_data)
    light_obj.location = (5.0, -5.0, 8.0)
    coll.objects.link(light_obj)

    return coll

def build_garden_container(collection, config):
    """Draws a baseline primitive container box tracking design configurations."""
    shape = config.get("garden_shape", "Rectangle")
    dims = config.get("dimensions", {"length_ft": 6.0, "width_ft": 4.0})
    
    if shape == "Rectangle":
        length = float(dims.get("length_ft", 6.0))
        width = float(dims.get("width_ft", 4.0))
        
        # Build box
        mesh = bpy.data.meshes.new("BoxMesh")
        box = bpy.data.objects.new("Garden_Bed", mesh)
        collection.objects.link(box)
        
        # Populate geometric coordinates manually to bypass window focus constraints
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(mesh)
        bm.free()
        
        box.scale = (length, width, 0.3)
        box.location = (0.0, 0.0, 0.15)
        
    elif shape == "Circle":
        radius = float(dims.get("radius_ft", 3.0))
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=0.3, vertices=32, location=(0.0, 0.0, 0.15))

def generate_growth_sim(collection, layout_data):
    """Populates explicit cylinder models that stretch upward vertically."""
    for idx, site in enumerate(layout_data):
        coords = site.get("coordinates", {"x": 0.0, "y": 0.0})
        plant = site.get("plant", {})
        
        mesh = bpy.data.meshes.new(f"PlantMesh_{idx}")
        sprout = bpy.data.objects.new(f"Sprout_Marker_{idx}", mesh)
        collection.objects.link(sprout)
        
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.1, radius2=0.04, depth=1.0)
        # Shift vertices up so pivot sits perfectly on the bottom cap flat surface
        for v in bm.verts:
            v.co.z += 0.5
        bm.to_mesh(mesh)
        bm.free()
        
        sprout.location = (float(coords["x"]), float(coords["y"]), 0.3)
        
        germ_frame = int(plant.get("germination_days", 5))
        mature_frame = int(plant.get("days_to_maturity", 60))
        target_height = float(plant.get("max_height_inches", 12.0)) / 12.0
        
        # Append scaling timeline values
        sprout.scale = (0.01, 0.01, 0.01)
        sprout.keyframe_insert(data_path="scale", frame=1)
        sprout.keyframe_insert(data_path="scale", frame=germ_frame)
        
        sprout.scale = (1.0, 1.0, target_height)
        sprout.keyframe_insert(data_path="scale", frame=mature_frame)

def execute_render_pipeline():
    """Forces Cycles pure memory raytracing parameters for headless environments."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 90
    
    # FORCE CYCLES RAY-TRACER Engine (Bypasses all display driver requirements completely)
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    
    # Speed optimization tweaks: Keep quality at exactly 1 sample to minimize calculations
    scene.cycles.samples = 1
    scene.cycles.preview_samples = 1
    scene.cycles.use_denoise = False
    
    scene.render.resolution_x = 640
    scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100
    
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = os.path.join(os.getcwd(), "garden_timelapse.mp4")
    
    print("--- CYCLES HEADLESS RENDER INITIATED ---")
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    active_collection = build_pristine_scene()
    
    default_config = {"garden_shape": "Rectangle", "dimensions": {"length_ft": 6.0, "width_ft": 4.0}}
    default_layout = [
        {"emitterId": 0, "coordinates": {"x": -1.5, "y": 0.0}, "plant": {"germination_days": 5, "days_to_maturity": 45, "max_height_inches": 24}},
        {"emitterId": 1, "coordinates": {"x": 0.0, "y": 0.0}, "plant": {"germination_days": 10, "days_to_maturity": 65, "max_height_inches": 16}},
        {"emitterId": 2, "coordinates": {"x": 1.5, "y": 0.0}, "plant": {"germination_days": 4, "days_to_maturity": 30, "max_height_inches": 8}}
    ]
    
    build_garden_container(active_collection, default_config)
    generate_growth_sim(active_collection, default_layout)
    execute_render_pipeline()
