"""Orange reconstruction: clean alpha silhouettes, calibrated framing, open neck."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.measure import marching_cubes

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/orange-test'
OUT.mkdir(exist_ok=True)
views=[]
for i in range(8):
    source=ROOT/f'assets/angulos-3d/jaq-lar-{i+1}.png'
    rgba=np.array(Image.open(source).convert('RGBA'))
    labels,_=ndi.label(rgba[:,:,3]>127)
    counts=np.bincount(labels.ravel()); counts[0]=0
    mask=labels==counts.argmax()
    mask=ndi.binary_fill_holes(mask)
    yy,xx=np.where(mask)
    cx=(xx.min()+xx.max())/2; cy=(yy.min()+yy.max())/2
    scale=(yy.max()-yy.min())/2
    clean=rgba.copy(); clean[:,:,3]=mask.astype(np.uint8)*255
    Image.fromarray(clean).save(OUT/f'reference-{i+1}.png')
    # Texture edge dilation is UV preprocessing, not a new reference image.
    texture_interior=ndi.binary_erosion(mask,iterations=4)
    nearest=ndi.distance_transform_edt(~texture_interior,return_distances=False,return_indices=True)
    rgb=rgba[:,:,:3].copy(); rgb[~texture_interior]=rgb[tuple(nearest[:,~texture_interior])]
    Image.fromarray(rgb).save(OUT/f'projection-{i+1}.png')
    views.append(dict(cx=float(cx),cy=float(cy),scale=float(scale),width=rgba.shape[1],height=rgba.shape[0],angle=i*np.pi/4,mask=mask))

step=.010
axes=[np.arange(-1.05,1.051,step),np.arange(-.65,.651,step),np.arange(-1.06,1.071,step)]
x,y,z=np.meshgrid(*axes,indexing='ij')
field=np.full(x.shape,100.,dtype=np.float32)
for v in views[::2]:
    a=v['angle']; mask=v['mask']
    distance=ndi.distance_transform_edt(mask)-ndi.distance_transform_edt(~mask)
    u=(x*np.cos(a)+y*np.sin(a))*v['scale']+v['cx']
    vv=v['cy']-z*v['scale']
    sampled=ndi.map_coordinates(distance,[vv.ravel(),u.ravel()],order=1,mode='constant',cval=-100).reshape(x.shape)/v['scale']
    # A small tolerance allows for the uncalibrated photographic views.
    field=np.minimum(field,sampled+.004)
field=ndi.gaussian_filter(field,1.25)
# Neck opening: rounded interior down to the upper chest, with real wall thickness.
neck_radial=(np.sqrt((x/.185)**2+((y-.005)/.125)**2)-1)*.125
neck_bottom=.61-z
neck_outside=np.maximum(neck_radial,neck_bottom)
field=np.minimum(field,neck_outside)
verts,faces,_,_=marching_cubes(field,0,spacing=(step,)*3)
verts+=np.array([a[0] for a in axes])
np.savez(OUT/'hull.npz',vertices=verts,faces=faces)
for v in views: del v['mask']
(OUT/'views.json').write_text(json.dumps(views,indent=2))
print(f'ORANGE_HULL {len(verts)} vertices, {len(faces)} triangles')
for height in [.7,.85,.95]:
    section=verts[np.abs(verts[:,2]-height)<.008]
    print('section',height,section.min(axis=0).tolist(),section.max(axis=0).tolist())
