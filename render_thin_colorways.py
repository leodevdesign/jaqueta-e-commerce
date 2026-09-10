"""Render front, side and back for all approved-method colorways in a saved blend."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
for color in ['pink','orange','blue']:
    scene=bpy.data.scenes[f'{color.title()} — approved thin profile']
    bpy.context.window.scene=scene
    scene.render.resolution_x=600; scene.render.resolution_y=600
    for name,location in [('front',(0,-6,0)),('three-quarter',(3,-6,.15)),('side',(6,0,0)),('back',(0,6,0))]:
        scene.camera.location=location; scene.camera.rotation_euler=(-scene.camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(ROOT/f'assets/{color}-thin/preview-{name}.png')
        bpy.ops.render.render(write_still=True,scene=scene.name)
