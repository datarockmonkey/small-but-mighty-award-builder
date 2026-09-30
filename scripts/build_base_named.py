"""Portable Small But Mighty named-base builder (review candidate).
Derived from the project build_base_named.py, 2026-09-30.
Preserves socket/rib/base construction. Exports millimetres. No fonts bundled.
Run with Blender; see README.md. Generated outputs require print validation.
"""
import argparse
import math
import os
import sys

import bpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, SCRIPT_DIR)
import connector_std as C   # noqa: E402  (authoritative connector geometry)

EMBOSS = 2.0            # Blender curve `extrude` -- letters stand 1.6 mm proud
FACE_SINK = 0.4         # letter roots sink into the face (weld overlap)
CAP_RATIO = None        # measured from the selected font capital H
CAP_FLOOR = 5.0         # FONT_AND_BASE_STANDARD sec.2 -- hard readability floor


def parse_args():
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--font", required=True, help="Path to a font you are permitted to use")
    p.add_argument("--name", default="SAMPLE NAME",
                   help="recipient name -- goes on the BACK face")
    p.add_argument("--message", default="Always Up|For A Chat",
                   help="front wording; '|' forces line breaks")
    p.add_argument("--out", default="/tmp/award_base.stl")
    p.add_argument("--back-mode", default="engrave",
                   choices=["engrave", "emboss", "none"])
    p.add_argument("--engrave-depth", type=float, default=0.80)
    p.add_argument("--front-name", action="store_true",
                   help="legacy: ALSO put the name on the front face")
    p.add_argument("--twocolor", default="",
                   help="write PREFIX_body.stl + PREFIX_text.stl instead of a "
                        "single solid, for the K2/CFS white-wording print. The "
                        "BACK name always stays in the BODY solid -- see the "
                        "toolchange note in the module docstring.")
    p.add_argument("--mm", action="store_true",
                   help="compatibility flag; this package always exports millimetres")
    result = p.parse_args(args)
    if not result.message.strip() or not result.message.replace("|", "").strip():
        p.error("--message must contain visible text")
    if not os.path.isfile(result.font):
        p.error("--font must name an existing font file")
    result.mm = True
    return result


A = parse_args()
W = float(os.environ.get("AWARD_BASE_W", C.BASE_W))
D = float(os.environ.get("AWARD_BASE_D", C.BASE_D))
H = float(os.environ.get("AWARD_BASE_H", C.BASE_H))


# ------------------------------------------------------------------ helpers
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)


def set_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def load_font():
    font = bpy.data.fonts.load(os.path.abspath(A.font))
    probe = bpy.data.curves.new("CapHeightProbe", type="FONT")
    probe.body = "H"; probe.size = 1.0; probe.font = font
    obj = bpy.data.objects.new("CapHeightProbe", probe)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.update()
    ratio = float(obj.dimensions.y)
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.curves.remove(probe)
    if ratio <= 0:
        raise ValueError("Selected font has no measurable capital H")
    global CAP_RATIO
    CAP_RATIO = ratio
    print(f"[font] measured capital H / em = {ratio:.6f}")
    return font


def wrap_two_words(text):
    """<=2 words and <=10 chars per line (FONT_AND_BASE_STANDARD sec.4)."""
    max_words = int(os.environ.get("AWARD_WRAP_MAX_WORDS", "2"))
    max_chars = int(os.environ.get("AWARD_WRAP_MAX_CHARS", "10"))
    out, w = [], text.split()
    i = 0
    while i < len(w):
        line = w[i]; i += 1; n = 1
        while (i < len(w) and n < max_words
               and len(line) + 1 + len(w[i]) <= max_chars):
            line += " " + w[i]; i += 1; n += 1
        out.append(line)
    return out


def boolean(target, cutter, op):
    set_active(target)
    mod = target.modifiers.new("Bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def add_box(sx, sy, sz, loc, name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    set_active(o)
    bpy.ops.object.transform_apply(scale=True)
    return o


from mathutils import Vector   # noqa: E402


def grp_bbox(objs):
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector((min(mn[i], w[i]) for i in range(3)))
            mx = Vector((max(mx[i], w[i]) for i in range(3)))
    return mn, mx


def build_text_block(lines, size, font, face, extrude, y_at, tag):
    """Build one stacked, shrink-to-fit text block on the -Y or +Y face.

    face: 'front' (-Y, reads from -Y) or 'back' (+Y, reads from +Y).
    Returns (object, final_cap_mm, fit_ok).
    """
    MARGIN = max(3.5, C.BASE_BEVEL + 1.0)
    BUDGET_W = W - 2 * MARGIN
    BUDGET_H = H - 2 * MARGIN
    z = 0.0
    objs = []
    for txt in lines:
        bpy.ops.object.text_add()
        t = bpy.context.active_object
        t.data.body = txt
        t.data.size = size
        t.data.extrude = extrude
        t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
        t.data.font = font
        t.data.space_word = 1.15
        t.data.space_character = 1.04
        # stand the text up in the XZ plane; the back face is turned 180 deg
        # about Z so it READS from +Y instead of being mirrored.
        t.rotation_euler = (math.radians(90), 0,
                            math.radians(180) if face == "back" else 0)
        bpy.ops.object.convert(target="MESH")
        rmn = min((t.matrix_world @ v.co).z for v in t.data.vertices)
        rmx = max((t.matrix_world @ v.co).z for v in t.data.vertices)
        rh = rmx - rmn
        z -= rh / 2
        t.location = (0, y_at, z)
        set_active(t)
        bpy.ops.object.transform_apply(location=True)
        objs.append(t)
        z -= rh / 2 + size * 0.35

    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    grp = bpy.context.view_layer.objects.active
    mn, mx = grp_bbox([grp])
    tw, th = mx.x - mn.x, mx.z - mn.z
    fit = min(BUDGET_W / tw, BUDGET_H / th, 1.0)     # shrink only, never grow
    grp.scale = (fit, 1.0, fit)
    set_active(grp); bpy.ops.object.transform_apply(scale=True)
    mn, mx = grp_bbox([grp])
    c = (mn + mx) / 2
    grp.location = (grp.location.x - c.x, grp.location.y,
                    grp.location.z - c.z + H / 2)
    set_active(grp); bpy.ops.object.transform_apply(location=True)

    mn, mx = grp_bbox([grp])
    fw, fh = mx.x - mn.x, mx.z - mn.z
    cap = size * fit * CAP_RATIO
    within = (fw <= BUDGET_W + 0.05 and fh <= BUDGET_H + 0.05
              and mn.x >= -W / 2 + MARGIN - 0.05 and mx.x <= W / 2 - MARGIN + 0.05
              and mn.z >= MARGIN - 0.05 and mx.z <= H - MARGIN + 0.05)
    ok = within and cap >= CAP_FLOOR
    print(f"[fitcheck:{tag}] {'PASS' if ok else 'FAIL'} rows={len(lines)} "
          f"em={size*fit:.1f}mm CAP={cap:.1f}mm (floor {CAP_FLOOR:.0f}) "
          f"blockW={fw:.1f}/{BUDGET_W:.0f} blockH={fh:.1f}/{BUDGET_H:.0f} "
          f"lines={lines}")
    for ln in lines:
        if len(ln) > 10:
            print(f"[fitcheck:{tag}] WARN line '{ln}' is {len(ln)} chars "
                  f"(standard is <=10)")
    return grp, cap, ok


# ---------------------------------------------------------------- build
clear_scene()
base = add_box(W, D, H, (0, 0, H / 2), "AwardBase")

set_active(base)
bev = base.modifiers.new("Bevel", "BEVEL")
bev.width = C.BASE_BEVEL
bev.segments = 3
bev.limit_method = "ANGLE"
bev.angle_limit = math.radians(55)
bpy.ops.object.modifier_apply(modifier=bev.name)

# friction socket (diamond) + 4 ribs -- identical to scripts/build_base.py
cav = add_box(C.SOCKET_W, C.SOCKET_W, C.SOCKET_DEPTH + 2,
              (0, 0, H - C.SOCKET_DEPTH / 2 + 1), "SocketCavity")
set_active(cav)
m = cav.modifiers.new("MouthBevel", "BEVEL")
m.width = C.SOCKET_MOUTH_CHAMFER
m.segments = 1
m.limit_method = "ANGLE"
m.angle_limit = math.radians(30)
bpy.ops.object.modifier_apply(modifier=m.name)
if getattr(C, "PLUG_DIAMOND", False):
    cav.rotation_euler = (0, 0, math.radians(45))
boolean(base, cav, "DIFFERENCE")

inner = C.SOCKET_W / 2
rib_z = H - C.SOCKET_DEPTH + C.RIB_HEIGHT / 2 + 1.0

# ---- RIB_EMBED: the H>=38 rib-detach fix (2026-07-29) -------------------
# The rib used to be exactly RIB_DEPTH thick with its outer face COPLANAR
# with the socket wall -- zero overlap for the UNION to bite on. Coplanar
# EXACT-boolean contact is a 1-ULP coin flip, and the coin flips with H
# (the wall vertices come out of the previous cavity DIFFERENCE, whose
# float rounding moves as H moves): H<=37 unioned, H>=38 left all 4 ribs as
# free-floating islands in the cavity -- a socket with ZERO grip.
# Each rib is now RIB_EMBED thicker and shifted RIB_EMBED/2 outward, so it
# bites RIB_EMBED into solid wall. Cavity-side geometry is IDENTICAL:
# inner face still at inner - RIB_DEPTH, rib gap still SOCKET_W - 2*RIB_DEPTH
# = 16.10. connector_std.py is deliberately untouched (hard rule).
RIB_EMBED = float(os.environ.get("AWARD_RIB_EMBED", "0.6"))
_t = C.RIB_DEPTH + RIB_EMBED          # rib thickness through the wall
_o = inner - C.RIB_DEPTH / 2 + RIB_EMBED / 2   # centre, pushed into the wall
rib_specs = [
    (_t, C.RIB_WIDTH,  _o, 0),
    (_t, C.RIB_WIDTH, -_o, 0),
    (C.RIB_WIDTH, _t, 0,  _o),
    (C.RIB_WIDTH, _t, 0, -_o),
]
for i, (sx, sy, cx, cy) in enumerate(rib_specs):
    rib = add_box(sx, sy, C.RIB_HEIGHT, (cx, cy, rib_z), f"Rib{i}")
    if getattr(C, "PLUG_DIAMOND", False):
        rib.rotation_euler = (0, 0, math.radians(45))
    boolean(base, rib, "UNION")
print(f"[ribs] embed={RIB_EMBED:.2f}mm thickness={_t:.2f} centre={_o:.4f} "
      f"protrusion={C.RIB_DEPTH:.2f} rib_gap={C.SOCKET_W - 2*C.RIB_DEPTH:.2f} "
      f"rib_z={rib_z:.2f}")

font = load_font()

# ---- FRONT (-Y): the message. The name row is gone unless --front-name.
front_lines = ([s.strip() for s in A.message.split("|") if s.strip()]
               if "|" in A.message else wrap_two_words(A.message))
if A.front_name and A.name.strip():
    front_lines = wrap_two_words(A.name) + front_lines
grp, front_cap, front_ok = build_text_block(
    front_lines, 11.0, font, "front", EMBOSS, -D / 2 + FACE_SINK, "front")
if not A.twocolor:
    boolean(base, grp, "UNION")

# ---- BACK (+Y): the recipient name.
back_cap, back_ok, back_lines = None, True, []
if A.back_mode != "none" and A.name.strip():
    back_lines = wrap_two_words(A.name)
    if A.back_mode == "emboss":
        print("[back] WARNING: raised back text cannot be printed in the "
              "proven TEXT-FACE-UP orientation -- the back face lies on the "
              "bed. Only use this file if you print the base BACK-face-up.")
        grpb, back_cap, back_ok = build_text_block(
            back_lines, 11.0, font, "back", EMBOSS, D / 2 - FACE_SINK, "back")
        boolean(base, grpb, "UNION")
    else:
        # cutter spans [D/2 - depth, D/2 + depth] -> exactly `depth` into the face
        grpb, back_cap, back_ok = build_text_block(
            back_lines, 11.0, font, "back", A.engrave_depth, D / 2, "back")
        boolean(base, grpb, "DIFFERENCE")
        print(f"[back] engraved {A.engrave_depth:.2f} mm into the +Y face")

# ---- island gate: one connected solid
set_active(base)
_me = base.data
_par = list(range(len(_me.vertices)))


def _find(i):
    while _par[i] != i:
        _par[i] = _par[_par[i]]; i = _par[i]
    return i


for _e in _me.edges:
    _a, _b = _e.vertices
    _par[_find(_a)] = _find(_b)
_n = len({_find(v.index) for v in _me.vertices})
print(f"[baseislands] {'PASS' if _n == 1 else 'FAIL'} islands={_n}")

# ---- per-face poly audit: prove the two extremes are DIFFERENT bands.
ys = [v.co.y for v in _me.vertices]
ymin, ymax = min(ys), max(ys)
n_front = sum(1 for p in _me.polygons if p.center.y <= ymin + 0.8)
n_back = sum(1 for p in _me.polygons if p.center.y >= ymax - 0.8)
print(f"[faceaudit] y extremes {ymin:.2f} .. {ymax:.2f} mm | "
      f"polys within 0.8 mm of -Y (front, WHITE band) = {n_front} | "
      f"within 0.8 mm of +Y (back) = {n_back} | total {len(_me.polygons)}")

print(f"[summary] front cap {front_cap:.1f} mm {'OK' if front_ok else 'FAIL'}"
      + (f" | back cap {back_cap:.1f} mm {'OK' if back_ok else 'FAIL'} "
         f"({A.back_mode})" if back_cap else " | no back text"))

if not front_ok or not back_ok or _n != 1:
    raise RuntimeError("Refusing export: text readability or connected-body check failed")
scale = 1.0


def export(obj, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    set_active(obj)
    try:
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True,
                              global_scale=scale)
    except Exception:
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True,
                                global_scale=scale, use_mesh_modifiers=True)
    print(f"SAVED {path}  ({os.path.getsize(path)//1024} KB)  "
          f"units={'mm' if A.mm else 'metre-scale (legacy)'}")


if A.twocolor:
    # TWO SOLIDS at the same world position, exactly like build_base_2color.py.
    # The FRONT letters are the white part. The BACK name is NOT in the text
    # solid: with one CFS toolchange only one Z band can change colour, and the
    # back face is on the BED in the proven face-up orientation, so it can only
    # ever print in the body colour. Putting it in the text solid would produce
    # a file that slices into a second toolchange nobody asked for.
    export(base, A.twocolor + "_body.stl")
    export(grp, A.twocolor + "_text.stl")
else:
    export(base, A.out)
