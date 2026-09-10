"""Run in the connected Blender, using the approved green finishing pipeline."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parent
results=[]
if bpy.data.is_dirty:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/pink-thin/session-before-colorways.blend'),copy=True)
for color in ['pink','orange','blue']:
    title=color.title()
    previous_scene=bpy.data.scenes.get(f'{title} — approved thin profile')
    if previous_scene: previous_scene.name+=' — previous'
    scene=bpy.data.scenes.new(f'{title} — approved thin profile')
    bpy.context.window.scene=scene
    source=(ROOT/'finish_green_blender.py').read_text(encoding='utf-8')
    source=source.replace('assets/green-refined',f'assets/{color}-thin').replace('Green',title).replace('green',color)
    namespace={'__file__':str(ROOT/'finish_green_blender.py')}
    exec(compile(source,str(ROOT/'finish_green_blender.py'),'exec'),namespace)
    results.append({'color':color,**namespace['result']})
validation_path=ROOT/'validate_thin_colorways_blender.py'
validation_namespace={'__file__':str(validation_path)}
exec(compile(validation_path.read_text(encoding='utf-8'),str(validation_path),'exec'),validation_namespace)
result=validation_namespace['result']
