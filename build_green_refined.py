"""Repair the original green front/back construction with aligned textures and closed edges."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import Delaunay
from skimage.measure import find_contours

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/green-refined'; OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'assets/angulos-3d'

def load_reference(number):
    rgba=np.array(Image.open(SOURCE/f'jaq-ver-{number}.png').convert('RGBA'))
    labels,_=ndi.label(rgba[:,:,3]>127)
    counts=np.bincount(labels.ravel()); counts[0]=0
    mask=ndi.binary_fill_holes(labels==counts.argmax())
    inner=ndi.binary_erosion(mask,iterations=3)
    nearest=ndi.distance_transform_edt(~inner,return_distances=False,return_indices=True)
    rgb=rgba[:,:,:3].copy(); rgb[~inner]=rgb[tuple(nearest[:,~inner])]
    yy,xx=np.where(mask)
    return rgb,mask,(xx.min(),yy.min(),xx.max(),yy.max())

front,fmask,fb=load_reference(1)
back,bmask,bb=load_reference(5)
h,w=fmask.shape
yy,xx=np.mgrid[:h,:w]
# Back view is mirrored into the same world-space left/right convention.
back=back[:,::-1].copy(); bmask=bmask[:,::-1].copy()
yb,xb=np.where(bmask); bb=(xb.min(),yb.min(),xb.max(),yb.max())
by=(yy-fb[1])/(fb[3]-fb[1])*(bb[3]-bb[1])+bb[1]
bx=np.zeros_like(by,dtype=float)

def intervals(row):
    edges=np.diff(np.pad(row.astype(np.int8),(1,1)))
    return list(zip(np.where(edges==1)[0],np.where(edges==-1)[0]-1))

for row in range(h):
    source_row=int(np.clip(round(by[row,0]),0,h-1))
    fi=intervals(fmask[row]); bi=intervals(bmask[source_row])
    bx[row]=(np.arange(w)-fb[0])/(fb[2]-fb[0])*(bb[2]-bb[0])+bb[0]
    # Align each sleeve and torso separately where the silhouettes separate.
    if fi and bi:
        if len(fi)==len(bi): pairs=zip(fi,bi)
        else: pairs=[((fi[0][0],fi[-1][1]),(bi[0][0],bi[-1][1]))]
        for (left,right),(bl,br) in pairs:
            cols=np.arange(left,right+1)
            bx[row,cols]=bl+(cols-left)/max(right-left,1)*(br-bl)

aligned=np.stack([ndi.map_coordinates(back[:,:,k].astype(float),[by,bx],order=1,mode='nearest') for k in range(3)],axis=-1)
# Keep interpolation outside the shared silhouette from leaving bright seams.
inner=ndi.binary_erosion(fmask,iterations=2)
nearest=ndi.distance_transform_edt(~inner,return_distances=False,return_indices=True)
aligned[~inner]=aligned[tuple(nearest[:,~inner])]
Image.fromarray(front).save(OUT/'green-front.png')
Image.fromarray(np.uint8(np.clip(aligned,0,255))).save(OUT/'green-back-aligned.png')
Image.fromarray(np.dstack([np.uint8(aligned),fmask.astype(np.uint8)*255])).save(OUT/'back-alignment-check.png')

# Use the original relief maps, with a controlled lower depth and aligned back.
fd=np.array(Image.open(SOURCE/'ver_front_depth.png').convert('L'),float)/255
bd=np.array(Image.open(SOURCE/'ver_back_depth.png').convert('L'),float)/255
bd=bd[:,::-1].copy()
bd=ndi.map_coordinates(bd,[by,bx],order=1,mode='nearest')
fd=ndi.gaussian_filter(fd,1.2); bd=ndi.gaussian_filter(bd,1.2)
distance=ndi.distance_transform_edt(fmask)

# Constrained silhouette boundary plus a regular interior grid. Both surfaces
# share the very same boundary vertices, so there are no floating seam ribbons.
contours=find_contours(np.pad(fmask.astype(float),1),.5)
outline=max(contours,key=len)-1
outline=outline[::2,::-1]
gx,gy=np.meshgrid(np.arange(0,w,3),np.arange(0,h,3))
grid=np.stack([gx.ravel(),gy.ravel()],axis=-1)
grid=grid[distance[grid[:,1],grid[:,0]]>2]
points=np.vstack([outline,grid])
tri=Delaunay(points).simplices
centers=points[tri].mean(axis=1)
midpoints=(points[tri]+np.roll(points[tri],1,axis=1))/2
valid=ndi.map_coordinates(fmask.astype(float),[centers[:,1],centers[:,0]],order=0,mode='constant')>.5
for edge in range(3):
    valid&=ndi.map_coordinates(distance,[midpoints[:,edge,1],midpoints[:,edge,0]],order=1,mode='constant')>.05
tri=tri[valid]
# The planar triangulation's boundary determines shared vertices exactly.
edge_list=np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1)
unique,count=np.unique(edge_list,axis=0,return_counts=True)
boundary=np.unique(unique[count==1])
is_boundary=np.zeros(len(points),bool); is_boundary[boundary]=True
# Split internal diagonals whose endpoints both lie on the silhouette. Without
# this step the front/back weld would put four faces on those internal edges.
split_edges={tuple(edge) for edge in unique[(count==2)&is_boundary[unique[:,0]]&is_boundary[unique[:,1]]]}
if split_edges:
    expanded=points.tolist(); mid_index={}
    for edge in split_edges:
        mid_index[edge]=len(expanded); expanded.append(points[list(edge)].mean(axis=0).tolist())
    refined=[]
    for triangle in tri:
        ring=[]; split=False
        for k in range(3):
            a,b=int(triangle[k]),int(triangle[(k+1)%3]); ring.append(a)
            key=tuple(sorted((a,b)))
            if key in mid_index: ring.append(mid_index[key]); split=True
        if split:
            center=len(expanded); expanded.append(points[triangle].mean(axis=0).tolist())
            refined.extend([[ring[k],ring[(k+1)%len(ring)],center] for k in range(len(ring))])
        else: refined.append(triangle.tolist())
    points=np.array(expanded); tri=np.array(refined)
    is_boundary=np.zeros(len(points),bool); is_boundary[boundary]=True
d=ndi.map_coordinates(distance,[points[:,1],points[:,0]],order=1,mode='nearest')
taper=np.sqrt(np.clip(d/10,0,1)); taper[is_boundary]=0
front_depth=ndi.map_coordinates(fd,[points[:,1],points[:,0]],order=1,mode='nearest')*.245*taper
back_depth=ndi.map_coordinates(bd,[points[:,1],points[:,0]],order=1,mode='nearest')*.215*taper
front_depth[~is_boundary]=np.maximum(front_depth[~is_boundary],.001)
back_depth[~is_boundary]=np.maximum(back_depth[~is_boundary],.001)
unit=2.2/w
xs=(points[:,0]-(fb[0]+fb[2])/2)*unit
zs=((fb[1]+fb[3])/2-points[:,1])*unit
verts=np.stack([xs,-front_depth,zs],axis=-1).tolist()
uvs=np.stack([(points[:,0]+.5)/w,1-(points[:,1]+.5)/h],axis=-1).tolist()
back_indices=np.arange(len(points))
for i in range(len(points)):
    if not is_boundary[i]:
        back_indices[i]=len(verts)
        verts.append([xs[i],back_depth[i],zs[i]]); uvs.append(uvs[i])
faces=[]; materials=[]
for triangle in tri:
    a,b,c=triangle
    ab=points[b]-points[a]; ac=points[c]-points[a]
    cross=ab[0]*ac[1]-ab[1]*ac[0]
    if cross>0: a,c=c,a
    faces.append([int(a),int(b),int(c)]); materials.append(0)
    faces.append([int(back_indices[c]),int(back_indices[b]),int(back_indices[a])]); materials.append(1)
np.savez(OUT/'green-surface.npz',vertices=np.array(verts),faces=np.array(faces),uvs=np.array(uvs),materials=np.array(materials))
report={'method':'aligned original green front/back relief','front_bbox':[int(v) for v in fb],'back_bbox':[int(v) for v in bb],'triangles':len(faces),'dimensions':np.ptp(verts,axis=0).tolist(),'depth_height_ratio':float(np.ptp(np.array(verts)[:,1])/np.ptp(np.array(verts)[:,2]))}
(OUT/'measurements.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
