import bpy
from pathlib import Path
OUT=Path(__file__).resolve().parent/'assets/green-refined'
scene=bpy.data.scenes['Green — thin profile refinement']
if bpy.context.window: bpy.context.window.scene=scene
for name,location in [('front',(0,-6,0)),('three-quarter',(3,-6,.15)),('side',(6,0,0)),('back',(0,6,0))]:
    scene.camera.location=location; scene.camera.rotation_euler=(-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/f'preview-{name}.png'); bpy.ops.render.render(write_still=True,scene=scene.name)
