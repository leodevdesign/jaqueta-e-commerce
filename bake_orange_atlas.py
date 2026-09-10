"""Bake smooth reference projections into a single UV atlas for web rendering."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/orange-test'
surface=np.load(OUT/'surface.npz')
views=json.loads((OUT/'views.json').read_text())
SIZE=2048
position=np.zeros((SIZE,SIZE,3),np.float32)
normal=np.zeros_like(position)
covered=np.zeros((SIZE,SIZE),bool)
points=surface['positions']; normals=surface['normals']
for indices,tex in zip(surface['triangles'],surface['uvs']):
    xy=tex.copy()*SIZE; xy[:,1]=SIZE-xy[:,1]
    lo=np.maximum(np.floor(xy.min(axis=0)).astype(int),0)
    hi=np.minimum(np.ceil(xy.max(axis=0)).astype(int),SIZE-1)
    if np.any(hi<lo): continue
    yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
    xx=xx+.5; yy=yy+.5
    a,b,c=xy
    determinant=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(determinant)<1e-8: continue
    w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/determinant
    w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/determinant
    w2=1-w0-w1
    inside=(w0>=-1e-4)&(w1>=-1e-4)&(w2>=-1e-4)
    weights=np.stack([w0,w1,w2],axis=-1)[inside]
    region=(slice(lo[1],hi[1]+1),slice(lo[0],hi[0]+1))
    position[region][inside]=weights@points[indices]
    normal[region][inside]=weights@normals[indices]
    covered[region][inside]=True

p=position[covered]; n=normal[covered]
n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-8)
color_sum=np.zeros_like(p); weight_sum=np.zeros((len(p),1),np.float32)
for i in [0,2,4,6]:
    view=views[i]; a=view['angle']
    image=np.array(Image.open(OUT/f'projection-{i+1}.png').convert('RGB'),np.float32)/255
    u=(p[:,0]*np.cos(a)+p[:,1]*np.sin(a))*view['scale']+view['cx']
    v=view['cy']-p[:,2]*view['scale']
    sampled=np.stack([ndi.map_coordinates(image[:,:,k],[v,u],order=1,mode='nearest') for k in range(3)],axis=-1)
    direction=np.array([np.sin(a),-np.cos(a),0])
    facing=np.maximum(n@direction,0)
    # Front and back dominate their hemispheres. Side images feather only around
    # grazing surfaces; this avoids moving/duplicating pockets between views.
    transition=np.clip((np.abs(p[:,1])-.12)/.10,0,1)
    transition=transition*transition*(3-2*transition)
    if i in [0,4]:
        hemisphere=(p[:,1]<0 if i==0 else p[:,1]>=0)
        weight=transition*hemisphere
    else:
        hemisphere=(p[:,0]>=0 if i==2 else p[:,0]<0)
        weight=(1-transition)*hemisphere
    weight=weight[:,None]
    color_sum+=sampled*weight; weight_sum+=weight
rgb=color_sum/np.maximum(weight_sum,1e-8)
unmapped=weight_sum[:,0]<1e-5
rgb[unmapped]=(.72,.24,.045)
# The original photos do not expose the inside: shade the actual inner collar
# with a dark orange lining, never stretch a zipper image across the opening.
radial=np.sqrt((p[:,0]/.185)**2+((p[:,1]-.005)/.125)**2)
inward=(p[:,0]*n[:,0]/.185**2+(p[:,1]-.005)*n[:,1]/.125**2)<0
lining=(p[:,2]>.595)&(radial<1.15)&(inward|(p[:,2]<.625))
lining_light=np.clip((p[:,2]-.60)/.34,0,1)
lining_rgb=np.stack([.18+.28*lining_light,.055+.08*lining_light,.014+.025*lining_light],axis=-1)
rgb[lining]=lining_rgb[lining]
atlas=np.zeros((SIZE,SIZE,3),np.float32); atlas[covered]=rgb
nearest=ndi.distance_transform_edt(~covered,return_distances=False,return_indices=True)
atlas[~covered]=atlas[tuple(nearest[:,~covered])]
Image.fromarray(np.uint8(np.clip(atlas,0,1)*255)).save(OUT/'orange-basecolor.png')
roughness=np.full((SIZE,SIZE),124,np.uint8)
dark=atlas.mean(axis=2)<.18
roughness[dark]=168
Image.fromarray(roughness).save(OUT/'orange-roughness.png')
print('ATLAS_COMPLETE',SIZE,'coverage',round(covered.mean(),3),'lining pixels',int(lining.sum()))
