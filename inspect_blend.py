import bpy

print("=== BLENDER INSPECT START ===")
for obj in bpy.data.objects:
    print(f"OBJECT: {obj.name} | Type: {obj.type} | Location: {obj.location} | Dimensions: {obj.dimensions}")
    if obj.type == 'MESH':
        mesh = obj.data
        print(f"  MESH DATA: {mesh.name} | Vertices: {len(mesh.vertices)} | Faces: {len(mesh.polygons)}")
        for i, slot in enumerate(obj.material_slots):
            mat_name = slot.material.name if slot.material else "None"
            print(f"  MATERIAL [{i}]: {mat_name}")
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        print(f"    IMAGE NODE: {node.image.name} | Path: {node.image.filepath}")
                    elif node.type == 'BSDF_PRINCIPLED':
                        print(f"    PRINCIPLED BSDF")

for img in bpy.data.images:
    print(f"IMAGE: {img.name} | Size: {img.size[0]}x{img.size[1]} | Filepath: {img.filepath}")
print("=== BLENDER INSPECT END ===")
