"""
weld_plug.py  (run inside Blender)
==================================
Turn a reviewed raw top mesh into a connector-equipped STL candidate:

  1. import the token (OBJ / GLB / STL)
  2. auto-orient: drop it flat onto z=0 and centre it on XY
  3. scale it to a target footprint so it sits nicely on the 40x40 base
  4. weld on the STANDARD plug (connector_std.py) pointing DOWN, with a starter
     chamfer on the leading edge so it self-aligns into the base socket
  5. export the combined top STL for separate mesh, visual and print checks

The plug is centred on XY origin -- exactly where build_base.py puts the socket
-- so every token fits every base.

Run:
  /Applications/Blender.app/Contents/MacOS/Blender --background \
    --python scripts/weld_plug.py -- /path/token.obj /path/out_token.stl [target_mm]
"""
import bpy, sys, os, math
from mathutils import Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
import connector_std as C

argv = sys.argv
args = argv[argv.index("--") + 1:] if "--" in argv else []
IN_PATH = args[0]
OUT_PATH = args[1] if len(args) > 1 else "/tmp/token.stl"
TARGET_MM = float(args[2]) if len(args) > 2 else 38.0   # token footprint target (X/Y max)
LOWPOLY_FACES = int(args[3]) if len(args) > 3 else 0  # off by default; curved objects need their curves
FLAT = len(args) > 4 and args[4].lower() == "flat"      # lay flat for printing (plug horizontal)
# MVP 2026-07-09: tokens are FULL 3D sculptures on the base — the flat-back
# relief slice ("half token emerging") is retired. Pass "relief" as arg[4] only
# if that old style is ever explicitly requested again.
RELIEF = len(args) > 4 and args[4].lower() == "relief"
# riser height fraction of token height (arg[5]); short default so it never pokes
# out of open shapes (crown arches, wineglass stem gap). Raise per-token only if
# the connectivity check fails.
RISER_FRAC = float(args[5]) if len(args) > 5 else 0.18
# optional diagonal pose: tilt about Y (degrees) before seating (arg[6]).
# Wallace 2026-07-09: battery reads as a plain pillar upright — lean it.
TILT_DEG = float(args[6]) if len(args) > 6 else 0.0


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)


def set_active(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def import_mesh(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".stl":
        try: bpy.ops.wm.stl_import(filepath=path)
        except Exception: bpy.ops.import_mesh.stl(filepath=path)
    elif ext == ".obj":
        try: bpy.ops.wm.obj_import(filepath=path)
        except Exception: bpy.ops.import_scene.obj(filepath=path)
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    else:
        raise ValueError(f"unsupported: {ext}")
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def join(objs):
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def world_bounds(o):
    mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mins = Vector((min(mins[i], w[i]) for i in range(3)))
        maxs = Vector((max(maxs[i], w[i]) for i in range(3)))
    return mins, maxs


def add_box(sx, sy, sz, loc, name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    set_active(o)
    bpy.ops.object.transform_apply(scale=True)
    return o


# ------------------------------------------------------------------ build
clear()
token = join(import_mesh(IN_PATH))
set_active(token)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# scale to target HEIGHT (with footprint cap so nothing overhangs the 40mm base)
mins, maxs = world_bounds(token)
dims = maxs - mins
foot = max(dims.x, dims.y) or 1.0
height = dims.z or 1.0
import os as _os
TARGET_H = float(_os.environ.get("AWARD_TARGET_H", "40"))   # standard token body height (mm)
s_foot = TARGET_MM / foot        # never exceed the 38mm base footprint
s_height = TARGET_H / height     # aim every token at the same height
s = min(s_foot, s_height)        # whichever binds first: uniform height, but never overflow base
token.scale = (s, s, s)
set_active(token)
bpy.ops.object.transform_apply(scale=True)

# TRELLIS meshes commonly contain open reconstruction islands. On the public
# photo workflow, an explicit 0.18 mm voxel pass closes small gaps before the
# connector boolean. The standalone script defaults to no remesh, preserving
# already-curated inputs. This cannot rescue lost identity or large gaps.
VOXEL_MM = float(os.environ.get("AWARD_VOXEL_MM", "0"))
if VOXEL_MM > 0:
    token.data.remesh_voxel_size = VOXEL_MM
    set_active(token)
    bpy.ops.object.voxel_remesh()
    if not token.data.polygons:
        raise RuntimeError("Voxel repair produced no faces")
    print(f"[repair] voxel={VOXEL_MM:.3f}mm faces={len(token.data.polygons)}")

# centre on XY, drop flat onto z=0
mins, maxs = world_bounds(token)
center = (mins + maxs) / 2
token.location = (token.location.x - center.x,
                  token.location.y - center.y,
                  token.location.z - mins.z)
set_active(token)
bpy.ops.object.transform_apply(location=True)

# FLAT-BACK RELIEF: slice the rear off at a flat plane (keep the domed 3D front)
# using a mesh BISECT (robust on imported meshes, unlike a boolean) and cap the
# cut so it stays watertight. The flat back becomes the bed face -> full bed
# contact when printed flat. Tokens face -Y, so the back is +Y.
if RELIEF:
    import bmesh
    mins, maxs = world_bounds(token)
    depth = maxs.y - mins.y
    yflat = mins.y + depth * C.RELIEF_FRONT_KEEP
    me = token.data
    bm = bmesh.new(); bm.from_mesh(me)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                 plane_co=(0, yflat, 0), plane_no=(0, 1, 0),
                                 clear_outer=True)           # remove the +Y (back) side
    cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    bmesh.ops.holes_fill(bm, edges=cut_edges)                # cap the flat back
    bm.to_mesh(me); bm.free()
    me.update()

# low-poly facet pass: decimate the TOKEN (not the plug) to a low face count so
# it reads as angular/flat-shaded, matching the low-poly reference style.
if LOWPOLY_FACES > 0:
    set_active(token)
    # weld duplicate verts first so decimate collapses cleanly
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0005)
    bpy.ops.object.mode_set(mode="OBJECT")
    nfaces = len(token.data.polygons)
    if nfaces > LOWPOLY_FACES:
        dec = token.modifiers.new("LowPoly", "DECIMATE")
        dec.decimate_type = "COLLAPSE"
        dec.ratio = max(0.01, LOWPOLY_FACES / nfaces)
        bpy.ops.object.modifier_apply(modifier=dec.name)
    print(f"[lowpoly] {nfaces} -> {len(token.data.polygons)} faces")

if TILT_DEG:
    set_active(token)
    token.rotation_euler = (0, math.radians(TILT_DEG), 0)
    bpy.ops.object.transform_apply(rotation=True)

# re-seat AFTER decimation: collapse can nudge the lowest vertex up, which would
# leave the token floating above the base. Re-centre XY and drop min z back to 0.
mins, maxs = world_bounds(token)
center = (mins + maxs) / 2
token.location = (token.location.x - center.x,
                  token.location.y - center.y,
                  token.location.z - mins.z)
set_active(token)
bpy.ops.object.transform_apply(location=True)

# standard plug: square box from z=0 down to -PLUG_H, centred
plug = add_box(C.PLUG_W, C.PLUG_W, C.PLUG_H, (0, 0, -C.PLUG_H / 2), "Plug")
# starter wedge: chamfer the leading (bottom) edges
set_active(plug)
ch = plug.modifiers.new("Starter", "BEVEL")
ch.width = C.PLUG_TOP_CHAMFER
ch.segments = 1
ch.limit_method = "ANGLE"
ch.angle_limit = math.radians(30)
bpy.ops.object.modifier_apply(modifier=ch.name)
# round the vertical corners a touch (reduces contact stress)
set_active(plug)
rc = plug.modifiers.new("Corner", "BEVEL")
rc.width = C.PLUG_CORNER_R
rc.segments = 2
rc.limit_method = "ANGLE"
rc.angle_limit = math.radians(85)
bpy.ops.object.modifier_apply(modifier=rc.name)

# Raise the plug into the token; configurable for testing boolean seams on
# voxel-repaired inputs. Its 16 mm XY interface is never rescaled.
plug.location.z += float(os.environ.get("AWARD_PLUG_OVERLAP_MM", "0.4"))
set_active(plug)
bpy.ops.object.transform_apply(location=True)
# DIAMOND orientation (see connector_std): rotate the plug 45 deg about Z so the
# socket's matching diamond prints support-free with the base text-face-up.
if getattr(C, "PLUG_DIAMOND", False):
    plug.rotation_euler = (0, 0, math.radians(45))
    # no transform_apply (headless double-apply risk); the boolean union that
    # welds the plug into the token reads the object matrix.

# NECK: a central riser bridging the plug up into the token body. Narrow-bottomed
# shapes (dumbbell, wineglass, flower, battery) have an empty centre-bottom, so a
# bare plug never touches the body and prints as a detached/floating part. The
# riser reaches up to the token's mid-height where the central geometry (stem /
# handle / core) lives, guaranteeing the plug fuses into one solid.
tmn, tmx = world_bounds(token)
tok_h = tmx.z - tmn.z
riser_h = min(RISER_FRAC * tok_h, 20.0)
riser = add_box(C.PLUG_W * 0.45, C.PLUG_W * 0.45, riser_h, (0, 0, riser_h / 2), "Riser")

# union plug + riser -> token (single solid)
for part in (plug, riser):
    set_active(token)
    mod = token.modifiers.new("Weld", "BOOLEAN")
    mod.operation = "UNION"
    mod.object = part
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(part, do_unlink=True)

# ---- CONNECTIVITY CHECK: nothing may levitate; everything must be one solid ----
# (catches e.g. a lid not fused to the box, or the plug not reaching the token).
# Count loose islands; the biggest is the body, any others are floating/detached.
import bmesh
bm = bmesh.new()
bm.from_mesh(token.data)
seen = set()
boxes = []   # bbox per island: [minx,miny,minz,maxx,maxy,maxz]
for v in bm.verts:
    if v.index in seen:
        continue
    comp = [v]; seen.add(v.index)
    bb = [v.co.x, v.co.y, v.co.z, v.co.x, v.co.y, v.co.z]
    while comp:
        cur = comp.pop()
        for k in range(3):
            bb[k] = min(bb[k], cur.co[k]); bb[k+3] = max(bb[k+3], cur.co[k])
        for e in cur.link_edges:
            o = e.other_vert(cur)
            if o.index not in seen:
                seen.add(o.index); comp.append(o)
    boxes.append(bb)
bm.free()

# group islands whose bounding boxes OVERLAP (tol 0.3mm in metres). Overlapping
# solids fuse in the slicer, so they are NOT floating; only a spatially DISJOINT
# island (a real gap) is a true float.
TOL = 0.0003
def overlap(a, b):
    return all(a[k] <= b[k+3] + TOL and b[k] <= a[k+3] + TOL for k in range(3))
parent = list(range(len(boxes)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
for i in range(len(boxes)):
    for j in range(i+1, len(boxes)):
        if overlap(boxes[i], boxes[j]):
            parent[find(i)] = find(j)
groups = len({find(i) for i in range(len(boxes))})
conn_ok = groups <= 1
print(f"[connectivity] {'PASS' if conn_ok else 'FAIL'} islands={len(boxes)} "
      f"groups={groups} (groups>1 = a spatially detached/floating part)")
if not conn_ok:
    raise RuntimeError("Detached mesh islands; export refused. Edit the source mesh and retry.")

# FLAT print orientation: lay the token on its back so the plug points sideways
# (horizontal). Layers then run ALONG the insertion axis = strong against pull-out,
# the flat back gives great bed adhesion, and no supports are needed.
if FLAT:
    set_active(token)
    token.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    fmn, fmx = world_bounds(token)
    token.location = (token.location.x, token.location.y, token.location.z - fmn.z)
    bpy.ops.object.transform_apply(location=True)
    print("[orient] flat print (plug horizontal)")

# ------------------------------------------------------------------ export
os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)
set_active(token)
try:
    bpy.ops.wm.stl_export(filepath=OUT_PATH, export_selected_objects=True,
                          global_scale=1.0)
except Exception:
    bpy.ops.export_mesh.stl(filepath=OUT_PATH, use_selection=True,
                            global_scale=1.0, use_mesh_modifiers=True)
print(f"SAVED {OUT_PATH}  ({os.path.getsize(OUT_PATH)//1024} KB)")
