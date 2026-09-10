import bpy
import numpy as np
import math
import os

# Reset Blender factory settings
bpy.ops.wm.read_factory_settings(use_empty=True)

# Paths
base_dir = r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce"
front_color_p = os.path.join(base_dir, "assets", "angulos-3d", "jaq-ver-1.png")
front_depth_p = os.path.join(base_dir, "assets", "angulos-3d", "ver_front_depth.png")
front_norm_p  = os.path.join(base_dir, "assets", "angulos-3d", "ver_front_norm.png")

back_color_p  = os.path.join(base_dir, "assets", "angulos-3d", "jaq-ver-5.png")
back_depth_p  = os.path.join(base_dir, "assets", "angulos-3d", "ver_back_depth.png")
back_norm_p   = os.path.join(base_dir, "assets", "angulos-3d", "ver_back_norm.png")

side_r_p      = os.path.join(base_dir, "assets", "angulos-3d", "jaq-ver-3.png")
side_l_p      = os.path.join(base_dir, "assets", "angulos-3d", "jaq-ver-7.png")

blend_out     = os.path.join(base_dir, "assets", "jacket_lime_3d.blend")
glb_out       = os.path.join(base_dir, "assets", "jacket_lime.glb")

# Load images in Blender
front_col_img = bpy.data.images.load(front_color_p)
front_dep_img = bpy.data.images.load(front_depth_p)
front_nrm_img = bpy.data.images.load(front_norm_p)

back_col_img  = bpy.data.images.load(back_color_p)
back_dep_img  = bpy.data.images.load(back_depth_p)
back_nrm_img  = bpy.data.images.load(back_norm_p)

w_img, h_img = front_dep_img.size[0], front_dep_img.size[1]

# Convert pixel arrays to numpy
f_dep_arr = np.array(front_dep_img.pixels[:], dtype=np.float32).reshape((h_img, w_img, front_dep_img.channels))[:, :, 0]
b_dep_arr = np.array(back_dep_img.pixels[:], dtype=np.float32).reshape((h_img, w_img, back_dep_img.channels))[:, :, 0]

f_col_arr = np.array(front_col_img.pixels[:], dtype=np.float32).reshape((h_img, w_img, front_col_img.channels))
b_col_arr = np.array(back_col_img.pixels[:], dtype=np.float32).reshape((h_img, w_img, back_col_img.channels))

# Combined mask
mask_front = f_col_arr[:, :, 3] > 0.08 if front_col_img.channels >= 4 else np.max(f_col_arr[:, :, :3], axis=2) > 0.05
mask_back  = b_col_arr[:, :, 3] > 0.08 if back_col_img.channels >= 4 else np.max(b_col_arr[:, :, :3], axis=2) > 0.05
combined_mask = mask_front | mask_back

# Grid resolution matching aspect ratio
w_res = 80
h_res = 110

aspect = h_img / w_img # ~1.385
xs = np.linspace(-1.1, 1.1, w_res)
zs = np.linspace(-1.1 * aspect, 1.1 * aspect, h_res)

verts = []
uvs = []
faces = []
mat_indices = []

# Map: (i, j, 'F') -> vert_idx, (i, j, 'B') -> vert_idx
front_vert_map = {}
back_vert_map = {}

# 1. Generate Front Vertices
for j in range(h_res):
    v = j / (h_res - 1)
    py = int(v * (h_img - 1))
    z = zs[j]

    for i in range(w_res):
        u = i / (w_res - 1)
        px = int(u * (w_img - 1))

        d_val = f_dep_arr[py, px] if combined_mask[py, px] else 0.0
        x = xs[i]
        y = -d_val * 0.38 # Forward displacement in Blender

        idx = len(verts)
        verts.append((x, y, z))
        uvs.append((u, v))
        front_vert_map[(i, j)] = idx

# 2. Generate Back Vertices
for j in range(h_res):
    v = j / (h_res - 1)
    py = int(v * (h_img - 1))
    z = zs[j]

    for i in range(w_res):
        # Back UV is mirrored horizontally (1.0 - u) so back texture maps correctly
        u = i / (w_res - 1)
        px = int(u * (w_img - 1))

        d_val = b_dep_arr[py, px] if combined_mask[py, px] else 0.0
        x = xs[i]
        y = +d_val * 0.38 # Backward displacement in Blender

        idx = len(verts)
        verts.append((x, y, z))
        # Mirrored UV for back image
        uvs.append((1.0 - u, v))
        back_vert_map[(i, j)] = idx

# 3. Generate Front Faces
for j in range(h_res - 1):
    for i in range(w_res - 1):
        v_mid = (j + 0.5) / (h_res - 1)
        u_mid = (i + 0.5) / (w_res - 1)
        py = int(v_mid * (h_img - 1))
        px = int(u_mid * (w_img - 1))

        if combined_mask[py, px]:
            idx0 = front_vert_map[(i, j)]
            idx1 = front_vert_map[(i + 1, j)]
            idx2 = front_vert_map[(i + 1, j + 1)]
            idx3 = front_vert_map[(i, j + 1)]
            faces.append((idx0, idx1, idx2, idx3))
            mat_indices.append(0) # Material 0: Front

# 4. Generate Back Faces (Reverse winding for outward normal)
for j in range(h_res - 1):
    for i in range(w_res - 1):
        v_mid = (j + 0.5) / (h_res - 1)
        u_mid = (i + 0.5) / (w_res - 1)
        py = int(v_mid * (h_img - 1))
        px = int(u_mid * (w_img - 1))

        if combined_mask[py, px]:
            idx0 = back_vert_map[(i, j)]
            idx1 = back_vert_map[(i, j + 1)]
            idx2 = back_vert_map[(i + 1, j + 1)]
            idx3 = back_vert_map[(i + 1, j)]
            faces.append((idx0, idx1, idx2, idx3))
            mat_indices.append(1) # Material 1: Back

# 5. Generate Side Seam Ribbons (Connect front and back border edges)
for j in range(h_res - 1):
    for i in range(w_res - 1):
        v_mid = (j + 0.5) / (h_res - 1)
        u_mid = (i + 0.5) / (w_res - 1)
        py = int(v_mid * (h_img - 1))
        px = int(u_mid * (w_img - 1))

        is_curr = combined_mask[py, px]
        # Check right neighbor
        px_r = min(w_img - 1, px + int(w_img / w_res))
        is_r = combined_mask[py, px_r]
        if is_curr != is_r:
            # Boundary at right edge of cell
            f0 = front_vert_map[(i + 1, j)]
            f1 = front_vert_map[(i + 1, j + 1)]
            b0 = back_vert_map[(i + 1, j)]
            b1 = back_vert_map[(i + 1, j + 1)]
            if is_curr:
                faces.append((f0, b0, b1, f1))
            else:
                faces.append((f0, f1, b1, b0))
            mat_indices.append(0)

        # Check top neighbor
        py_t = min(h_img - 1, py + int(h_img / h_res))
        is_t = combined_mask[py_t, px]
        if is_curr != is_t:
            # Boundary at top edge of cell
            f0 = front_vert_map[(i, j + 1)]
            f1 = front_vert_map[(i + 1, j + 1)]
            b0 = back_vert_map[(i, j + 1)]
            b1 = back_vert_map[(i + 1, j + 1)]
            if is_curr:
                faces.append((f0, f1, b1, b0))
            else:
                faces.append((f0, b0, b1, f1))
            mat_indices.append(0)

# Build Mesh in Blender
mesh = bpy.data.meshes.new("Jacket_Watertight_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

# Assign Materials to Polygons
for p_idx, poly in enumerate(mesh.polygons):
    poly.material_index = mat_indices[p_idx]
    poly.use_smooth = True

# Set UVs
uv_layer = mesh.uv_layers.new(name="UVMap")
for poly in mesh.polygons:
    for loop_index in poly.loop_indices:
        vert_idx = mesh.loops[loop_index].vertex_index
        uv_layer.data[loop_index].uv = uvs[vert_idx]

obj = bpy.data.objects.new("Jacket_Lime_3D_Watertight", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Add Subdivision Surface Modifier for smooth organic puffer curves
sub_mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
sub_mod.levels = 1
sub_mod.render_levels = 1

# Material 1: Front PBR Material
mat_front = bpy.data.materials.new(name="Jacket_Front_PBR")
mat_front.use_nodes = True
nodes_f = mat_front.node_tree.nodes
links_f = mat_front.node_tree.links
bsdf_f = nodes_f.get("Principled BSDF")
bsdf_f.inputs["Roughness"].default_value = 0.22
bsdf_f.inputs["Metallic"].default_value = 0.85

tex_f = nodes_f.new('ShaderNodeTexImage')
tex_f.image = front_col_img
links_f.new(tex_f.outputs['Color'], bsdf_f.inputs['Base Color'])

norm_tex_f = nodes_f.new('ShaderNodeTexImage')
norm_tex_f.image = front_nrm_img
norm_node_f = nodes_f.new('ShaderNodeNormalMap')
norm_node_f.inputs['Strength'].default_value = 1.3
links_f.new(norm_tex_f.outputs['Color'], norm_node_f.inputs['Color'])
links_f.new(norm_node_f.outputs['Normal'], bsdf_f.inputs['Normal'])

obj.data.materials.append(mat_front)

# Material 2: Back PBR Material (With real back horizontal baffles texture)
mat_back = bpy.data.materials.new(name="Jacket_Back_PBR")
mat_back.use_nodes = True
nodes_b = mat_back.node_tree.nodes
links_b = mat_back.node_tree.links
bsdf_b = nodes_b.get("Principled BSDF")
bsdf_b.inputs["Roughness"].default_value = 0.22
bsdf_b.inputs["Metallic"].default_value = 0.85

tex_b = nodes_b.new('ShaderNodeTexImage')
tex_b.image = back_col_img
links_b.new(tex_b.outputs['Color'], bsdf_b.inputs['Base Color'])

norm_tex_b = nodes_b.new('ShaderNodeTexImage')
norm_tex_b.image = back_nrm_img
norm_node_b = nodes_b.new('ShaderNodeNormalMap')
norm_node_b.inputs['Strength'].default_value = 1.3
links_b.new(norm_tex_b.outputs['Color'], norm_node_b.inputs['Color'])
links_b.new(norm_node_b.outputs['Normal'], bsdf_b.inputs['Normal'])

obj.data.materials.append(mat_back)

# Studio Lights
key_light_data = bpy.data.lights.new(name="Key_Light_Front", type='POINT')
key_light_data.energy = 900
key_light = bpy.data.objects.new("Key_Light_Front", key_light_data)
key_light.location = (2.5, -2.5, 2.0)
bpy.context.collection.objects.link(key_light)

back_light_data = bpy.data.lights.new(name="Key_Light_Back", type='POINT')
back_light_data.energy = 800
back_light = bpy.data.objects.new("Key_Light_Back", back_light_data)
back_light.location = (-2.5, 2.5, 2.0)
bpy.context.collection.objects.link(back_light)

rim_light_data = bpy.data.lights.new(name="Rim_Light_Blue", type='POINT')
rim_light_data.energy = 600
rim_light_data.color = (0.4, 0.8, 1.0)
rim_light = bpy.data.objects.new("Rim_Light_Blue", rim_light_data)
rim_light.location = (-3.0, 0.0, 1.5)
bpy.context.collection.objects.link(rim_light)

# Camera
cam_data = bpy.data.cameras.new(name="Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
cam_obj.location = (0, -3.2, 0)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.context.collection.objects.link(cam_obj)

# Save .blend
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"Saved complete multi-view 3D .blend to: {blend_out}")

# Export .glb
bpy.ops.export_scene.gltf(
    filepath=glb_out,
    export_format='GLB',
    export_apply=True,
    export_yup=True
)
print(f"Exported complete multi-view .glb to: {glb_out}")
