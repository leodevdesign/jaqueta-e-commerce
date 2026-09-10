"""Create the repaired thin green mesh in the dedicated visible Blender scene."""
import bpy, bmesh, math, json
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/green-refined'
scene=bpy.context.scene
assert scene.name.startswith('Green —'), 'Use the dedicated green scene'
for ob in scene.objects:
    if ob.type=='MESH':
        ob.hide_set(True); ob.hide_render=True
with np.load(OUT/'green-surface.npz') as archive:
    data={key:archive[key] for key in archive.files}
previous=bpy.data.objects.get('Green_Jacket_Thin_Repaired')
if previous: previous.name='Green_Jacket_Working_Iteration'
mesh=bpy.data.meshes.new('Aligned front and back — joined boundary')
mesh.from_pydata(data['vertices'].tolist(),[],data['faces'].tolist()); mesh.update()
obj=bpy.data.objects.new('Green_Jacket_Thin_Repaired',mesh); scene.collection.objects.link(obj)
for ob in bpy.data.objects: ob.select_set(False)
obj.select_set(True); bpy.context.view_layer.objects.active=obj
uv=mesh.uv_layers.new(name='Aligned photographic projection')
for polygon,material in zip(mesh.polygons,data['materials']):
    polygon.material_index=int(material); polygon.use_smooth=True
    for li in polygon.loop_indices:
        uv.data[li].uv=data['uvs'][mesh.loops[li].vertex_index]
for name,filename in [('Green — original front','green-front.png'),('Green — aligned back','green-back-aligned.png')]:
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    nodes=mat.node_tree.nodes; nodes.clear()
    tex=nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(OUT/filename)); tex.image.pack()
    output=nodes.new('ShaderNodeOutputMaterial')
    # Photographs already contain studio lighting. An unlit glTF material avoids
    # adding a second lighting pass or metallic tint to the real product colors.
    mat.node_tree.links.new(tex.outputs['Color'],output.inputs['Surface'])
    obj.data.materials.append(mat)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
mod=obj.modifiers.new('Gentle seam smoothing','SMOOTH'); mod.factor=.25; mod.iterations=2
bpy.ops.object.modifier_apply(modifier=mod.name)
mod=obj.modifiers.new('Web triangle budget','DECIMATE'); mod.ratio=.85
bpy.ops.object.modifier_apply(modifier=mod.name)
bm=bmesh.new(); bm.from_mesh(obj.data)
checks={'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'triangles':len(obj.data.polygons),'dimensions':list(obj.dimensions)}
bm.free()
assert checks['boundary_edges']==0 and checks['nonmanifold_edges']==0,checks
(OUT/'mesh-validation.json').write_text(json.dumps(checks,indent=2))
bpy.ops.export_scene.gltf(filepath=str(OUT/'jacket_green_thin.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_cameras=False,export_lights=False)
camera_data=bpy.data.cameras.new('Green comparison camera'); camera=bpy.data.objects.new('Green comparison camera',camera_data); scene.collection.objects.link(camera)
camera.location=(3,-6,.15); camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler(); camera_data.type='ORTHO'; camera_data.ortho_scale=2.85; scene.camera=camera
scene.render.engine='CYCLES'; scene.cycles.samples=8
scene.render.resolution_x=760; scene.render.resolution_y=760; scene.render.resolution_percentage=100
scene.render.film_transparent=True; scene.view_settings.view_transform='Standard'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
scene.world=bpy.data.worlds.new('Neutral photographic background'); scene.world.color=(.08,.08,.08)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active; space.shading.type='MATERIAL'; space.overlay.show_overlays=False
        space.region_3d.view_location=(0,0,0); space.region_3d.view_distance=4.4; space.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'jacket_green_thin.blend'))
result=checks
