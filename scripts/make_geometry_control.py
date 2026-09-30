"""Create a plain solid control mesh for checking the local toolchain.

This is intentionally not a product design or a substitute for a photo-derived
top. Run with Blender --background --factory-startup --python this-file -- output.stl.
"""
import bpy
import os
import sys

args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args) != 1:
    raise SystemExit('Provide output STL path')
path=os.path.abspath(args[0])
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(0,0,12))
obj=bpy.context.object
obj.scale=(15,12,12)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
os.makedirs(os.path.dirname(path),exist_ok=True)
try:
    bpy.ops.wm.stl_export(filepath=path,export_selected_objects=True)
except Exception:
    bpy.ops.export_mesh.stl(filepath=path,use_selection=True)
print('CONTROL_STL='+path)
