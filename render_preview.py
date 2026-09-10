import bpy

scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r"C:\Users\User\.gemini\antigravity\brain\c1caaab7-9f81-4bca-9919-8f82c1bb31b8\blender_3d_render_preview.png"
scene.render.resolution_x = 800
scene.render.resolution_y = 800

# Rotate jacket slightly to show 3D volume clearly in render
jacket = bpy.data.objects.get("Jacket_Lime_3D")
if jacket:
    jacket.rotation_euler = (0.1, 0.45, -0.05)

scene.camera = bpy.data.objects.get("Camera")
bpy.ops.render.render(write_still=True)
print("Rendered preview successfully!")
