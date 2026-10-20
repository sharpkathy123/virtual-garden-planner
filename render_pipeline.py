import bpy
import json
import os
import math

def build_pristine_scene():
    """Purges the template startup layers and establishes fresh camera assets."""
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
        
    scene = bpy.context.scene
    coll = scene.collection

    # Position camera for a beautifully angled three-quarters view of the garden bed
    cam_data = bpy.data.cameras.new("SimCamData")
    cam_obj = bpy.data.objects.new("Sim_Camera", cam_data)
    cam_obj.location = (0.0, -5.5, 5.0)
    cam_obj.rotation_euler = (math.radians(52), 0.0, 0.0) 
    coll.objects.link(cam_obj)
    scene.camera = cam_obj 

    # Sun light source
    light_data = bpy.data.lights.new(name="SunData", type='SUN')
    light_data.energy = 4.0
    light_obj = bpy.data.objects.new("Sim_Sun", light_data)
    light_obj.location = (5.0, -5.0, 8.0)
    coll.objects.link(light_obj)

    return coll

def create_solid_material(name, rgba_color, roughness=0.8):
    """Creates a basic color material for Cycles rendering."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        principled.inputs['Base Color'].default_value = rgba_color
        principled.inputs['Roughness'].default_value = roughness
    return mat

def build_garden_container(collection, config, mat):
    """Draws a solid base box representing the garden bed framing container."""
    dims = config.get("dimensions", {"length_ft": 6.0, "width_ft": 4.0})
    length, width = float(dims.get("length_ft", 6.0)), float(dims.get("width_ft", 4.0))
    
    mesh = bpy.data.meshes.new("BoxMesh")
    box = bpy.data.objects.new("Garden_Bed", mesh)
    collection.objects.link(box)
    
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    
    box.scale = (length, width, 0.4)
    box.location = (0.0, 0.0, 0.2)
    box.data.materials.append(mat)

def generate_procedural_plant_mesh(idx, asset_type, collection):
    """Generates unique, realistic 3D mesh lookups based on crop assets."""
    mesh = bpy.data.meshes.new(f"PlantMesh_{idx}")
    obj = bpy.data.objects.new(f"Plant_{idx}", mesh)
    collection.objects.link(obj)
    
    import bmesh
    bm = bmesh.new()
    
    if asset_type == "kale_ruffled_leaves":
        # Kale: Multiple interweaving wide scales branching outward
        for i in range(5):
            angle = (i * 72) * (math.pi / 180)
            bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.18, radius2=0.01, depth=0.8)
            # Twist leaves outward slightly
            for v in bm.verts:
                if v.co.z > 0:
                    v.co.x += math.cos(angle) * 0.15
                    v.co.y += math.sin(angle) * 0.15
                    
    elif asset_type == "carrot_top_foliage":
        # Carrots: Fine, narrow, multiple feathery fronds
        for i in range(8):
            angle = (i * 45) * (math.pi / 180)
            bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.03, radius2=0.001, depth=0.6)
            for v in bm.verts:
                if v.co.z > 0:
                    v.co.x += math.cos(angle) * 0.08
                    v.co.y += math.sin(angle) * 0.08
                    
    else: # Default sprout
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.08, radius2=0.02, depth=0.4)

    # Center origin to the absolute base cap surface for clean upward scaling
    for v in bm.verts:
        v.co.z += 0.3
        
    bm.to_mesh(mesh)
    bm.free()
    return obj

def generate_growth_sim(collection, layout_data, kale_mat, carrot_mat, flower_mat):
    """Populates realistic meshes and links timeline keyframe nodes smoothly."""
    for idx, site in enumerate(layout_data):
        coords = site.get("coordinates", {"x": 0.0, "y": 0.0})
        plant = site.get("plant", {})
        asset = plant.get("blender_model_asset", "default")
        
        # Build customized realistic meshes
        sprout = generate_procedural_plant_mesh(idx, asset, collection)
        sprout.location = (float(coords["x"]), float(coords["y"]), 0.4)
        
        # Assign colors based on plant category
        if "kale" in asset:
            sprout.data.materials.append(kale_mat)
        elif "carrot" in asset:
            sprout.data.materials.append(carrot_mat)
        else:
            sprout.data.materials.append(flower_mat)
            
        germ_frame = int(plant.get("germination_days", 5))
        mature_frame = int(plant.get("days_to_maturity", 60))
        target_height = float(plant.get("max_height_inches", 12.0)) / 12.0
        
        # Timeline animations tracking scale dimensions
        sprout.scale = (0.001, 0.001, 0.001)
        sprout.keyframe_insert(data_path="scale", frame=1)
        sprout.keyframe_insert(data_path="scale", frame=germ_frame)
        
        sprout.scale = (1.0, 1.0, target_height)
        sprout.keyframe_insert(data_path="scale", frame=mature_frame)

def execute_render_pipeline():
    """Renders our multi-material procedural shapes."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 90
    
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1
    scene.cycles.preview_samples = 1
    scene.cycles.use_denoise = False
    
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = os.path.join(os.getcwd(), "garden_timelapse.mp4")
    
    print("--- RUNNING ADVANCED MODEL CYCLES GENERATOR ---")
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    active_collection = build_pristine_scene()
    
    # Establish distinct realistic color material profiles
    soil_wood = create_solid_material("SoilWood", (0.22, 0.13, 0.08, 1.0))
    deep_kale_green = create_solid_material("KaleGreen", (0.05, 0.28, 0.12, 1.0))
    feathery_carrot_green = create_solid_material("CarrotGreen", (0.18, 0.48, 0.15, 1.0))
    bright_flower_orange = create_solid_material("FlowerOrange", (0.95, 0.42, 0.05, 1.0))
    
    default_config = {"garden_shape": "Rectangle", "dimensions": {"length_ft": 6.0, "width_ft": 4.0}}
    
    # Fully matched layout linking straight to our expandable database profiles
    default_layout = [
        {"emitterId": 0, "coordinates": {"x": -1.5, "y": -0.5}, "plant": {"plant_name": "Kale", "germination_days": 7, "days_to_maturity": 60, "max_height_inches": 24, "blender_model_asset": "kale_ruffled_leaves"}},
        {"emitterId": 1, "coordinates": {"x": 0.0, "y": 0.6}, "plant": {"plant_name": "Carrots", "germination_days": 10, "days_to_maturity": 75, "max_height_inches": 12, "blender_model_asset": "carrot_top_foliage"}},
        {"emitterId": 2, "coordinates": {"x": 1.5, "y": -0.5}, "plant": {"plant_name": "Calendula", "germination_days": 10, "days_to_maturity": 50, "max_height_inches": 18, "blender_model_asset": "calendula_yellow_orange"}}
    ]
    
    build_garden_container(active_collection, default_config, soil_wood)
    generate_growth_sim(active_collection, default_layout, deep_kale_green, feathery_carrot_green, bright_flower_orange)
    execute_render_pipeline()
