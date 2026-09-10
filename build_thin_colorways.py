"""Apply the approved green pipeline to pink, orange and blue, preserving green."""
from pathlib import Path
import json
import numpy as np
from process_multiview_maps import generate_maps

ROOT=Path(__file__).resolve().parent
COLORS={'pink':'ros','orange':'lar','blue':'azul'}
TARGET_RATIO=json.loads((ROOT/'assets/green-refined/measurements.json').read_text())['depth_height_ratio']

def build(color,prefix):
    out=ROOT/f'assets/{color}-thin'; out.mkdir(exist_ok=True)
    for view,side in [(1,'front'),(5,'back')]:
        generate_maps(str(ROOT/f'assets/angulos-3d/jaq-{prefix}-{view}.png'),str(out/f'{side}-depth.png'),str(out/f'{side}-normal.png'),is_front=view==1)
    # Reuse the approved algorithm verbatim; only source/output paths vary.
    source=(ROOT/'build_green_refined.py').read_text(encoding='utf-8')
    source=source.replace("'assets/green-refined'",f"'assets/{color}-thin'")
    source=source.replace('jaq-ver-',f'jaq-{prefix}-')
    source=source.replace("SOURCE/'ver_front_depth.png'","OUT/'front-depth.png'")
    source=source.replace("SOURCE/'ver_back_depth.png'","OUT/'back-depth.png'")
    source=source.replace('green-front.png',f'{color}-front.png').replace('green-back-aligned.png',f'{color}-back-aligned.png').replace('green-surface.npz',f'{color}-surface.npz')
    exec(compile(source,str(ROOT/'build_green_refined.py'),'exec'),{'__file__':str(ROOT/'build_green_refined.py')})
    # Avoid dye brightness changing the perceived thickness of the same product.
    with np.load(out/f'{color}-surface.npz') as archive:
        data={key:archive[key] for key in archive.files}
    verts=data['vertices']; dimensions=np.ptp(verts,axis=0)
    verts[:,1]*=TARGET_RATIO*dimensions[2]/dimensions[1]
    np.savez(out/f'{color}-surface.npz',**data)
    report=json.loads((out/'measurements.json').read_text())
    report.update(color=color,method='approved green aligned thin relief',dimensions=np.ptp(verts,axis=0).tolist(),depth_height_ratio=TARGET_RATIO)
    (out/'measurements.json').write_text(json.dumps(report,indent=2))
    print('COLOR_READY',color,flush=True)

if __name__=='__main__':
    for color,prefix in COLORS.items(): build(color,prefix)
