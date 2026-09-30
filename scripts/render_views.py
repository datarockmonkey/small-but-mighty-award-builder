"""Render five inspection views of a written STL in Blender.

Usage: blender --background --factory-startup --python scripts/render_views.py -- part.stl output/views
"""
import bpy
from mathutils import Vector
import os
import sys

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args)!=2 or not os.path.isfile(args[0]):
    raise SystemExit('Provide input STL and output prefix')
input_path=os.path.abspath(args[0]); prefix=os.path.abspath(args[1])
os.makedirs(os.path.dirname(prefix),exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
try: bpy.ops.wm.stl_import(filepath=input_path)
except Exception: bpy.ops.import_mesh.stl(filepath=input_path)
obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
mat=bpy.data.materials.new('Clay'); mat.diffuse_color=(0.69,0.44,0.29,1); mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.69,0.44,0.29,1)
obj.data.materials.append(mat)
for face in obj.data.polygons: face.use_smooth=True
mins=[min(v.co[i] for v in obj.data.vertices) for i in range(3)]
maxs=[max(v.co[i] for v in obj.data.vertices) for i in range(3)]
center=Vector([(a+b)/2 for a,b in zip(mins,maxs)])
span=max(b-a for a,b in zip(mins,maxs))
bpy.ops.object.light_add(type='AREA',location=(span, -span, span*2))
bpy.context.object.data.energy=1300; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=span*2
bpy.ops.object.camera_add(); camera=bpy.context.object; camera.data.type='ORTHO'; camera.data.ortho_scale=span*1.6
bpy.context.scene.camera=camera
scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
scene.render.resolution_x=600; scene.render.resolution_y=600; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(0.8,0.8,0.8)
views={'front':(0,-2,0.25),'side':(2,0,0.25),'top':(0,0,2),'bottom':(0,0,-2),'display':(1.4,-1.8,1.1)}
for name,direction in views.items():
    camera.location=center+Vector(direction)*span
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=f'{prefix}-{name}.png'
    bpy.ops.render.render(write_still=True)
    print('RENDER='+scene.render.filepath)
