import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/orange-test'
scene=bpy.data.scenes['Orange Atelier — Reconstruction']
if bpy.context.window: bpy.context.window.scene=scene
for name,loc in [('front',(0,-5,.12)),('three-quarter',(3,-5,.5)),('back',(0,5,.12)),('side',(5,0,.1)),('collar',(1,-3,3))]:
    scene.camera.location=loc; scene.camera.rotation_euler=(-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/f'preview-{name}.png')
    bpy.ops.render.render(write_still=True,scene=scene.name)
