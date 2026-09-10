"""Reconstruct an approximate pink jacket visual hull from eight reference views."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.measure import marching_cubes

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'assets/pink-test'
OUT.mkdir(exist_ok=True)
views = []
for i in range(8):
    path = ROOT / f'assets/angulos-3d/jaq-ros-{i+1}.png'
    img = np.array(Image.open(path).convert('RGB'))
    # Pink fabric separates reliably from the neutral photographic background.
    mask = (img[:,:,0].astype(float)-img[:,:,1] > 45) & (img[:,:,2] > 55)
    mask = ndi.binary_fill_holes(ndi.binary_closing(mask, iterations=3))
    labels, n = ndi.label(mask)
    counts = np.bincount(labels.ravel()); counts[0] = 0
    mask = labels == counts.argmax()
    yy, xx = np.where(mask)
    cx = (xx.min()+xx.max())/2
    cy = (yy.min()+yy.max())/2
    scale = (yy.max()-yy.min())/2
    # Pad fabric colors into the background to avoid white edges at UV seams.
    nearest = ndi.distance_transform_edt(~mask, return_distances=False, return_indices=True)
    img[~mask] = img[tuple(nearest[:,~mask])]
    Image.fromarray(img).save(OUT / f'view-{i+1}.png')
    views.append(dict(cx=float(cx), cy=float(cy), scale=float(scale), width=img.shape[1], height=img.shape[0], angle=i*np.pi/4, mask=mask))

step = .014
axes = [np.arange(-1.08,1.081,step),np.arange(-.65,.651,step),np.arange(-1.06,1.061,step)]
x,y,z = np.meshgrid(*axes,indexing='ij')
field = np.full(x.shape, 100., dtype=np.float32)
for view in views:
    a=view['angle']; mask=view['mask']
    distance = ndi.distance_transform_edt(mask)-ndi.distance_transform_edt(~mask)
    u = (x*np.cos(a)+y*np.sin(a))*view['scale']+view['cx']
    v = view['cy']-z*view['scale']
    sampled = ndi.map_coordinates(distance,[v.ravel(),u.ravel()],order=1,mode='constant',cval=-100).reshape(x.shape)/view['scale']
    field = np.minimum(field,sampled)
field = ndi.gaussian_filter(field, .8)
verts, faces, _, _ = marching_cubes(field,0,spacing=(step,step,step))
verts += np.array([a[0] for a in axes])
np.savez(OUT/'hull.npz',vertices=verts,faces=faces)
for v in views: del v['mask']
(OUT/'views.json').write_text(json.dumps(views))
print(f'Hull: {len(verts)} vertices, {len(faces)} triangles')
