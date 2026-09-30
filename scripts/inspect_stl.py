"""Run with Blender --background --factory-startup --python scripts/inspect_stl.py -- part.stl.
Reports geometry facts from the written STL. These checks do not certify printability.
"""
import bmesh
import bpy
import json
import os
import sys

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if len(args) != 1 or not os.path.isfile(args[0]):
    raise SystemExit('Provide one existing STL file')
path = os.path.abspath(args[0])
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
try:
    bpy.ops.wm.stl_import(filepath=path)
except Exception:
    bpy.ops.import_mesh.stl(filepath=path)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if len(meshes) != 1:
    raise SystemExit(f'Expected one imported mesh, found {len(meshes)}')
obj = meshes[0]
bm = bmesh.new()
bm.from_mesh(obj.data)
loose_edges = sum(not edge.is_manifold for edge in bm.edges)
bad_winding = sum(edge.is_manifold and not edge.is_contiguous for edge in bm.edges)
unseen = set(bm.verts)
bodies = 0
while unseen:
    bodies += 1
    stack = [unseen.pop()]
    while stack:
        for edge in stack.pop().link_edges:
            for vertex in edge.verts:
                if vertex in unseen:
                    unseen.remove(vertex)
                    stack.append(vertex)
volume = float(bm.calc_volume(signed=False))
bm.free()
xs = [v.co.x for v in obj.data.vertices]
ys = [v.co.y for v in obj.data.vertices]
zs = [v.co.z for v in obj.data.vertices]
dims = [max(a)-min(a) for a in (xs,ys,zs)]
report = {'file':os.path.basename(path),'dimensions_mm':[round(v,3) for v in dims],
          'volume_mm3':round(volume,3),'faces':len(obj.data.polygons),
          'non_manifold_edges':loose_edges,'inconsistent_winding_edges':bad_winding,
          'connected_bodies':bodies,
          'plausible_award_scale':bool(5 <= max(dims) <= 200),
          'basic_mesh_pass':bool(volume>0 and min(dims)>0 and 5<=max(dims)<=200 and loose_edges==0 and bad_winding==0 and bodies==1)}
print('INSPECTION_JSON='+json.dumps(report,sort_keys=True))
if not report['basic_mesh_pass']:
    raise SystemExit(2)
