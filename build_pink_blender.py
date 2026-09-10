"""Run in a separate Blender process; preserves the user's open scene."""
import bpy, numpy as np, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/pink-test'
bpy.ops.wm.read_factory_settings(use_empty=True)
data=np.load(OUT/'hull.npz')
mesh=bpy.data.meshes.new('Pink_Eight_View_Hull')
mesh.from_pydata(data['vertices'].tolist(),[],data['faces'].tolist()); mesh.update()
obj=bpy.data.objects.new('Pink_Jacket',mesh); bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active=obj; obj.select_set(True)
# Orient normals consistently and simplify the reconstruction for web delivery.
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
mod=obj.modifiers.new('Smooth reconstructed silhouette','SMOOTH'); mod.factor=.6; mod.iterations=4
bpy.ops.object.modifier_apply(modifier=mod.name)
mod=obj.modifiers.new('Web polygon budget','DECIMATE'); mod.ratio=min(1,26000/len(mesh.polygons))
bpy.ops.object.modifier_apply(modifier=mod.name)
views=json.loads((OUT/'views.json').read_text())
for i,v in enumerate(views):
    mat=bpy.data.materials.new(f'Pink_reference_{i+1}'); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value=.48; bsdf.inputs['Metallic'].default_value=0
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(OUT/f'view-{i+1}.png')); tex.image.pack()
    mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    obj.data.materials.append(mat)
uv=obj.data.uv_layers.new(name='ReferenceProjection')
directions=[Vector((math.sin(v['angle']),-math.cos(v['angle']),0)) for v in views]
for poly in obj.data.polygons:
    # Broad front/back projection avoids repeated pockets across photographic views
    # whose camera framing is approximate. Side references cover grazing surfaces.
    idx = (0 if poly.normal.y < 0 else 4)
    if abs(poly.normal.y) < .22 and abs(poly.normal.x) > .85:
        idx = 2 if poly.normal.x > 0 else 6
    v=views[idx]; a=v['angle']
    poly.material_index=idx; poly.use_smooth=True
    for li in poly.loop_indices:
        co=obj.data.vertices[obj.data.loops[li].vertex_index].co
        u=((co.x*math.cos(a)+co.y*math.sin(a))*v['scale']+v['cx'])/v['width']
        vv=1-(v['cy']-co.z*v['scale'])/v['height']
        uv.data[li].uv=(u,vv)
bpy.ops.export_scene.gltf(filepath=str(OUT/'jacket_pink_test.glb'),export_format='GLB',use_selection=True,export_animations=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.world=bpy.data.worlds.new('Pink Studio'); scene.world.color=(.3,.3,.3)
for name,loc,power,size in [('Key',(3,-4,4),450,5),('Fill',(-3,-2,1),220,4),('Rim',(1,3,3),350,3)]:
    light=bpy.data.lights.new(name,'AREA'); light.energy=power; light.shape='DISK'; light.size=size
    item=bpy.data.objects.new(name,light); scene.collection.objects.link(item); item.location=loc; item.rotation_euler=(-item.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Pink_preview'); camera=bpy.data.objects.new('Pink_preview',cam); scene.collection.objects.link(camera)
camera.location=(0,-5,.15); camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler(); cam.type='ORTHO'; cam.ortho_scale=2.65; scene.camera=camera
scene.render.resolution_x=650; scene.render.resolution_y=650; scene.render.resolution_percentage=100
scene.render.film_transparent=True; scene.view_settings.view_transform='Standard'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'jacket_pink_test.blend'))
for name,loc in [('front',(0,-5,.15)),('three-quarter',(3,-5,.3)),('back',(0,5,.15))]:
    camera.location=loc; camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/f'preview-{name}.png'); bpy.ops.render.render(write_still=True)
print('PINK_TEST_COMPLETE',len(obj.data.polygons))
