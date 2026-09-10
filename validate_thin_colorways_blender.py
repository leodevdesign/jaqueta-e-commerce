"""Validate and export final colorways, removing isolated zero-volume contour slivers."""
import bpy,bmesh,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
reports=[]
for color in ['pink','orange','blue']:
    scene=bpy.data.scenes[f'{color.title()} — approved thin profile']
    bpy.context.window.scene=scene
    obj=bpy.data.objects[color.title()+'_Jacket_Thin_Repaired']
    obj.data.validate()
    bm=bmesh.new(); bm.from_mesh(obj.data)
    # A disconnected double-sided boundary triangle has no volume. Blender's
    # validator drops its duplicate; remove that isolated remnant as well.
    isolated=[f for f in bm.faces if all(e.is_boundary for e in f.edges)]
    if isolated: bmesh.ops.delete(bm,geom=isolated,context='FACES')
    loose=[v for v in bm.verts if not v.link_faces]
    if loose: bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free(); obj.data.update()
    assert not obj.data.validate(), 'Unexpected remaining invalid mesh'
    bm=bmesh.new(); bm.from_mesh(obj.data)
    report={'color':color,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'triangles':len(obj.data.polygons),'dimensions':list(obj.dimensions)}
    bm.free()
    assert report['boundary_edges']==report['nonmanifold_edges']==0,report
    out=ROOT/f'assets/{color}-thin'
    (out/'mesh-validation.json').write_text(json.dumps(report,indent=2))
    for ob in bpy.data.objects: ob.select_set(False)
    obj.select_set(True); bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.gltf(filepath=str(out/f'jacket_{color}_thin.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_cameras=False,export_lights=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/f'jacket_{color}_thin.blend'))
    reports.append(report)
result={'models':reports}
