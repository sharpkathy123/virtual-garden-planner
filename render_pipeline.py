import bpy
import json
import os

def setup_scene():
    """Wipes startup meshes and locks down flat viewport rendering properties."""
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
        
    cam = bpy.data.objects.get("Camera")
    if cam:
        cam.location = (0.0, 0.0, 8.0)
        cam.rotation_euler = (0.0, 0.0, 0.0)

def build_garden_container(config):
    """Draws the wooden frame perimeter based on selected geometry specs."""
    shape = config.get("garden_shape", "Rectangle")
    dims = config.get("dimensions", {"length_ft": 6.0, "width_ft": 4.0})
    
    if shape == "Rectangle":
        length = dims.get("length_ft", 6.0)
        width = dims.get("width_ft", 4.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.1))
        box = bpy.context.active_object
        box.scale = (length, width, 0.2)
        
    elif shape == "Circle":
        radius = dims.get("radius_ft", 3.0)
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=0.2, vertices=32, location=(0,0,0.1))

def generate_growth_sim(layout_data):
    """Generates basic geometric cylinders that scale upward over time."""
    for idx, site in enumerate(layout_data):
        coords = site.get("coordinates", {"x": 0.0, "y": 0.0})
        plant = site.get("plant", {})
        
        # Add basic cylinder sprout
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.0, location=(coords["x"], coords["y"], 0.0))
        sprout = bpy.context.active_object
        
        # Shift geometry mesh internally so the base sits perfectly at z=0 origin
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
    """Forces fast workbench rendering profile outputs."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 90
    
    # CRITICAL SPEEDS FIX: Use workbench flat colors engine (takes milliseconds per frame)
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'FLAT'
    scene.display.shading.color_type = 'OBJECT'
    
    # Configure low resolution dimensions to speed up processing
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = os.path.join(os.getcwd(), "garden_timelapse.mp4")
    
    print("--- STARTING SPEED RENDER PIPELINE ---")
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    setup_scene()
    
    default_config = {"garden_shape": "Rectangle", "dimensions": {"length_ft": 6.0, "width_ft": 4.0}}
    default_layout = [
        {"emitterId": 0, "coordinates": {"x": -1.5, "y": -0.5}, "plant": {"germination_days": 7, "days_to_maturity": 60, "max_height_inches": 24}},
        {"emitterId": 1, "coordinates": {"x": 0.0, "y": 0.5}, "plant": {"germination_days": 10, "days_to_maturity": 75, "max_height_inches": 12}},
        {"emitterId": 2, "coordinates": {"x": 1.5, "y": -0.5}, "plant": {"germination_days": 4, "days_to_maturity": 25, "max_height_inches": 6}}
    ]
    
    build_garden_container(default_config)
    generate_growth_sim(default_layout)
    render_output_pipeline()
