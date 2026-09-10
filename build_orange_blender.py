"""Build the orange working mesh in the visible Blender scene, without resetting it."""
import bpy, math, json
import numpy as np
from pathlib import Path
from mathutils import Vector, Quaternion
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/orange-test'
scene=bpy.context.scene
assert scene.name.startswith('Orange Atelier'), 'Select the dedicated orange working scene first'
collection=bpy.data.collections.new('02 — Orange reconstructed garment')
scene.collection.children.link(collection)
previous=bpy.data.objects.get('Orange_Jacket_Refined')
if previous:
    # Archive this generated iteration for comparison; preserve the user's scene.
    previous.name='Orange_Jacket_Iteration_01'
    previous.hide_render=True
    previous.hide_set(True)
data=np.load(OUT/'hull.npz')
mesh=bpy.data.meshes.new('Orange continuous surface with open collar')
mesh.from_pydata(data['vertices'].tolist(),[],data['faces'].tolist()); mesh.update()
obj=bpy.data.objects.new('Orange_Jacket_Refined',mesh); collection.objects.link(obj)
for ob in bpy.context.selected_objects: ob.select_set(False)
obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
mod=obj.modifiers.new('Relax silhouette','SMOOTH'); mod.factor=.55; mod.iterations=5
bpy.ops.object.modifier_apply(modifier=mod.name)
mod=obj.modifiers.new('Web surface budget','DECIMATE'); mod.ratio=min(1,36000/len(obj.data.polygons))
bpy.ops.object.modifier_apply(modifier=mod.name)
for p in obj.data.polygons: p.use_smooth=True
# One UV atlas permits continuous blending rather than hard material boundaries.
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(72),island_margin=.006)
bpy.ops.object.mode_set(mode='OBJECT')
mesh=obj.data; mesh.calc_loop_triangles()
uv=mesh.uv_layers.active.data
np.savez(OUT/'surface.npz',
    positions=np.array([tuple(v.co) for v in mesh.vertices],dtype=np.float32),
    normals=np.array([tuple(v.normal) for v in mesh.vertices],dtype=np.float32),
    triangles=np.array([tuple(t.vertices) for t in mesh.loop_triangles],dtype=np.int32),
    uvs=np.array([[tuple(uv[li].uv) for li in t.loops] for t in mesh.loop_triangles],dtype=np.float32))
mat=bpy.data.materials.new('Orange coated nylon — continuous atlas'); mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value=(.9,.19,.012,1)
bsdf.inputs['Roughness'].default_value=.46; bsdf.inputs['Metallic'].default_value=0
bsdf.inputs['Coat Weight'].default_value=.16; bsdf.inputs['Coat Roughness'].default_value=.34
obj.data.materials.append(mat)
scene.world=bpy.data.worlds.new('Orange neutral studio'); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
for previous_studio in list(scene.collection.children):
    if previous_studio.name.startswith('03 — Preview studio'):
        previous_studio.hide_render=True; previous_studio.hide_viewport=True
studio=bpy.data.collections.new('03 — Preview studio'); scene.collection.children.link(studio)
for name,loc,power,size in [('Orange Key',(3,-4,4),220,5),('Orange Fill',(-3,-2,1),130,4),('Orange Rim',(1,3,3),230,3)]:
    light=bpy.data.lights.new(name,'AREA'); light.energy=power; light.shape='DISK'; light.size=size
    item=bpy.data.objects.new(name,light); studio.objects.link(item); item.location=loc; item.rotation_euler=(-item.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Orange Camera'); camera=bpy.data.objects.new('Orange Camera',cam); studio.objects.link(camera)
camera.location=(2.7,-5,1); camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler(); cam.type='ORTHO'; cam.ortho_scale=2.65; scene.camera=camera
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.film_transparent=True; scene.view_settings.view_transform='Standard'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active; space.shading.type='MATERIAL'
        space.overlay.show_overlays=False
        space.region_3d.view_location=(0,0,0); space.region_3d.view_distance=4.8
        space.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'jacket_orange_refined.blend'))
result={'object':obj.name,'triangles':len(mesh.loop_triangles),'stage':'UV surface ready for continuous texture atlas'}
