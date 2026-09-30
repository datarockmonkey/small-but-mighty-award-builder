"""Remove only microscopic duplicate boolean slivers from a written STL.

This is deliberately narrow: an arbitrary hole, open edge or larger damaged
surface fails instead of being guessed into a different shape.
"""
import bmesh
import bpy
import os
import sys


args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) != 2 or not os.path.isfile(args[0]):
    raise SystemExit("Provide input and output STL paths")
source, dest = map(os.path.abspath, args)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=source)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if len(meshes) != 1:
    raise RuntimeError(f"Expected one imported mesh, got {len(meshes)}")
obj = meshes[0]
bm = bmesh.new()
bm.from_mesh(obj.data)
before = sum(not edge.is_manifold for edge in bm.edges)
slivers = [
    face for face in bm.faces
    if face.calc_area() < 0.001
    and sum(len(edge.link_faces) == 1 for edge in face.edges) >= 2
    and any(len(edge.link_faces) == 3 for edge in face.edges)
]
if len(slivers) > 20 or sum(face.calc_area() for face in slivers) > 0.02:
    raise RuntimeError(f"Too much boolean damage to repair safely: {len(slivers)} faces")
if slivers:
    bmesh.ops.delete(bm, geom=slivers, context="FACES")
after = sum(not edge.is_manifold for edge in bm.edges)
print(f"[sliver-repair] removed={len(slivers)} bad_edges={before}->{after}")
if after:
    raise RuntimeError("Non-manifold edges remain; no repaired STL exported")
bm.to_mesh(obj.data)
bm.free()
os.makedirs(os.path.dirname(dest), exist_ok=True)
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.wm.stl_export(filepath=dest, export_selected_objects=True, global_scale=1.0)
