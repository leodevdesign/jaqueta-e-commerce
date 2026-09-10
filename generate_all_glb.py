import bpy
import numpy as np
import math
import os

VARIANTS = [
    {
        "name": "jacket_lime",
        "color": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\images\jacket-var-lime.png",
        "glb": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\jacket_lime.glb",
        "save_blend": True,
        "blend": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\jacket_lime_3d.blend"
    },
    {
        "name": "jacket_pink",
        "color": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\images\jacket-var-pink.png",
        "glb": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\jacket_pink.glb",
        "save_blend": False
    },
    {
        "name": "jacket_orange",
        "color": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\images\jacket-var-orange.png",
        "glb": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\jacket_orange.glb",
        "save_blend": False
    },
    {
        "name": "jacket_blue",
        "color": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\images\jacket-var-blue.png",
        "glb": r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\jacket_blue.glb",
        "save_blend": False
    }
]

depth_path = r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\images\jacket-depth.png"
normal_path = r"c:\Users\User\Desktop\Projetos da Next Automatik\jaqueta-e-commerce\assets\images\jacket-normal.png"

for var in VARIANTS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    depth_img_bpy = bpy.data.images.load(depth_path)
    color_img_bpy = bpy.data.images.load(var["color"])
    norm_img_bpy = bpy.data.images.load(normal_path)
    
    dw, dh = depth_img_bpy.size[0], depth_img_bpy.size[1]
    depth_raw = np.array(depth_img_bpy.pixels[:], dtype=np.float32).reshape((dh, dw, depth_img_bpy.channels))
    depth_arr = depth_raw[:, :, 0]
    
    cw, ch = color_img_bpy.size[0], color_img_bpy.size[1]
    color_raw = np.array(color_img_bpy.pixels[:], dtype=np.float32).reshape((ch, cw, color_img_bpy.channels))
    if color_img_bpy.channels >= 4:
        mask_arr = color_raw[:, :, 3] > 0.1
    else:
        mask_arr = np.max(color_raw[:, :, :3], axis=2) > 0.05

    grid_res = 110
    xs = np.linspace(-1.3, 1.3, grid_res)
    ys = np.linspace(-1.3, 1.3, grid_res)

    verts = []
    uvs = []
    faces = []
    vert_index_map = {}

    idx = 0
    for j in range(grid_res):
        v = j / (grid_res - 1)
        py = int(v * (dh - 1))
        z_coord = ys[j]

        for i in range(grid_res):
            u = i / (grid_res - 1)
            px = int(u * (dw - 1))

            is_jacket = mask_arr[py, px]
            d_val = depth_arr[py, px] if is_jacket else 0.0

            x_coord = xs[i]
            y_coord = -d_val * 0.44

            verts.append((x_coord, y_coord, z_coord))
            uvs.append((u, v))
            vert_index_map[(i, j)] = idx
            idx += 1

    for j in range(grid_res - 1):
        for i in range(grid_res - 1):
            v_mid = (j + 0.5) / (grid_res - 1)
            u_mid = (i + 0.5) / (grid_res - 1)
            py = int(v_mid * (dh - 1))
            px = int(u_mid * (dw - 1))

            if mask_arr[py, px]:
                idx0 = vert_index_map[(i, j)]
                idx1 = vert_index_map[(i + 1, j)]
                idx2 = vert_index_map[(i + 1, j + 1)]
                idx3 = vert_index_map[(i, j + 1)]
                faces.append((idx0, idx1, idx2, idx3))

    mesh = bpy.data.meshes.new("Jacket_Sculpt_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    uv_layer = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            vert_idx = mesh.loops[loop_index].vertex_index
            uv_layer.data[loop_index].uv = uvs[vert_idx]

    obj = bpy.data.objects.new("Jacket_3D", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    sol_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    sol_mod.thickness = 0.16
    sol_mod.offset = 1.0
    sol_mod.use_rim = True

    sub_mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    sub_mod.levels = 1
    sub_mod.render_levels = 1

    for poly in mesh.polygons:
        poly.use_smooth = True

    mat = bpy.data.materials.new(name=f"Mat_{var['name']}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.25
    bsdf.inputs["Metallic"].default_value = 0.85

    tex_image = nodes.new('ShaderNodeTexImage')
    tex_image.image = color_img_bpy
    links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])

    norm_image = nodes.new('ShaderNodeTexImage')
    norm_image.image = norm_img_bpy
    norm_node = nodes.new('ShaderNodeNormalMap')
    norm_node.inputs['Strength'].default_value = 1.25
    links.new(norm_image.outputs['Color'], norm_node.inputs['Color'])
    links.new(norm_node.outputs['Normal'], bsdf.inputs['Normal'])

    obj.data.materials.append(mat)

    # Studio Lighting & Camera
    key_light_data = bpy.data.lights.new(name="Key_Light", type='POINT')
    key_light_data.energy = 800
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (2.5, -2.5, 2.5)
    bpy.context.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new(name="Fill_Light", type='POINT')
    fill_light_data.energy = 400
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-2.5, -2.0, 1.5)
    bpy.context.collection.objects.link(fill_light)

    cam_data = bpy.data.cameras.new(name="Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    cam_obj.location = (0, -3.2, 0)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.collection.objects.link(cam_obj)

    if var.get("save_blend"):
        bpy.ops.wm.save_as_mainfile(filepath=var["blend"])
        print(f"Saved .blend to: {var['blend']}")

    bpy.ops.export_scene.gltf(
        filepath=var["glb"],
        export_format='GLB',
        export_apply=True,
        export_yup=True
    )
    print(f"Exported GLB to: {var['glb']}")

print("All 4 GLB models generated successfully!")
