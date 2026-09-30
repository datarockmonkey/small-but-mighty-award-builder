"""Run with Blender --background --factory-startup --python scripts/inspect_stl.py -- part.stl.
Reports geometry facts from the written STL. These checks do not certify printability.
"""
import bmesh
import bpy
import json
import os
import sys

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
kind = 'generic'
if len(args) == 3 and args[1] == '--kind' and args[2] in ('top', 'base'):
    kind = args[2]
    args = args[:1]
if len(args) != 1 or not os.path.isfile(args[0]):
    raise SystemExit('Provide one existing STL file, optionally followed by --kind top|base')
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
if kind == 'top':
    # A tiny riser-only export can be manifold and still lack the 16 mm plug.
    # Intersect the written triangle mesh with a plane 2 mm above its bottom.
    plane = min(zs) + 2.0
    section = []
    vertices = obj.data.vertices
    for face in obj.data.polygons:
        indices = list(face.vertices)
        for a, b in ((indices[0], indices[1]), (indices[1], indices[2]),
                     (indices[2], indices[0])):
            va, vb = vertices[a].co, vertices[b].co
            if va.z == vb.z or not (min(va.z, vb.z) <= plane <= max(va.z, vb.z)):
                continue
            t = (plane - va.z) / (vb.z - va.z)
            section.append((va.x + t * (vb.x - va.x), va.y + t * (vb.y - va.y)))
    if section:
        sx = max(p[0] for p in section) - min(p[0] for p in section)
        sy = max(p[1] for p in section) - min(p[1] for p in section)
        cx = (max(p[0] for p in section) + min(p[0] for p in section)) / 2
        cy = (max(p[1] for p in section) + min(p[1] for p in section)) / 2
        plug_pass = 20 <= sx <= 24 and 20 <= sy <= 24 and abs(cx) < 1 and abs(cy) < 1
        report['plug_section_span_mm'] = [round(sx, 3), round(sy, 3)]
    else:
        plug_pass = False
        report['plug_section_span_mm'] = None
    report['diamond_plug_pass'] = bool(plug_pass)
    report['basic_mesh_pass'] = bool(report['basic_mesh_pass'] and plug_pass
                                     and max(dims[0], dims[1]) >= 18 and dims[2] >= 20)
print('INSPECTION_JSON='+json.dumps(report,sort_keys=True))
if not report['basic_mesh_pass']:
    raise SystemExit(2)
