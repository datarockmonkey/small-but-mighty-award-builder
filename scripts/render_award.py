"""Render the two separate STLs seated together as an award candidate."""
import bpy
from mathutils import Vector
import os
import sys


args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if len(args) != 3 or not all(os.path.isfile(p) for p in args[:2]):
    raise SystemExit('Provide top STL, base STL and output prefix')
top_path, base_path, prefix = map(os.path.abspath, args)
os.makedirs(os.path.dirname(prefix), exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def load(path, name, color, smooth):
    bpy.ops.wm.stl_import(filepath=path)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name + ' clay')
    mat.diffuse_color = (*color, 1)
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = smooth
    return obj


base = load(base_path, 'Base', (0.28, 0.34, 0.17), False)
top = load(top_path, 'Book token', (0.64, 0.36, 0.22), True)
base_top_z = max(v.co.z for v in base.data.vertices)
top.location.z = base_top_z
bpy.context.view_layer.update()

objects = (base, top)
points = [o.matrix_world @ Vector(corner) for o in objects for corner in o.bound_box]
mins = [min(p[i] for p in points) for i in range(3)]
maxs = [max(p[i] for p in points) for i in range(3)]
center = Vector([(a + b) / 2 for a, b in zip(mins, maxs)])
span = max(b - a for a, b in zip(mins, maxs))

bpy.ops.object.camera_add()
camera = bpy.context.active_object
camera.data.type = 'ORTHO'
camera.data.ortho_scale = span * 1.55
camera.data.clip_start = 0.001
bpy.context.scene.camera = camera
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.background_type = 'WORLD'
scene.world.color = (0.84, 0.84, 0.82)
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.render.resolution_x = 700
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

for name, direction in {'front': (0, -2, 0.25), 'display': (1.4, -1.8, 1.1)}.items():
    camera.location = center + Vector(direction) * span
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = f'{prefix}-{name}.png'
    bpy.ops.render.render(write_still=True)
    print('RENDER=' + scene.render.filepath)
