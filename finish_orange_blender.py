"""Apply the baked material and export only the orange garment."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/orange-test'
obj=bpy.data.objects['Orange_Jacket_Refined']
mat=obj.data.materials[0]; nodes=mat.node_tree.nodes; links=mat.node_tree.links
bsdf=nodes.get('Principled BSDF')
for name,filename,socket,colorspace in [('Orange color atlas','orange-basecolor.png','Base Color','sRGB'),('Orange roughness','orange-roughness.png','Roughness','Non-Color')]:
    tex=nodes.get(name) or nodes.new('ShaderNodeTexImage'); tex.name=name
    tex.image=bpy.data.images.load(str(OUT/filename),check_existing=True); tex.image.reload(); tex.image.colorspace_settings.name=colorspace; tex.image.pack()
    links.new(tex.outputs['Color'],bsdf.inputs[socket])
for ob in bpy.context.selected_objects: ob.select_set(False)
obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.gltf(filepath=str(OUT/'jacket_orange_refined.glb'),export_format='GLB',use_selection=True,export_animations=False,export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'jacket_orange_refined.blend'))
result={'file':str(OUT/'jacket_orange_refined.glb'),'triangles':len(obj.data.polygons)}
