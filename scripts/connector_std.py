"""
connector_std.py
================
THE single source of truth for the modular award connector.

Every BASE socket and every TOKEN plug is built from these numbers, so any
token in the library physically fits any base. Change a value here and both
build_base.py and weld_plug.py update together.

Connector type: compliant FRICTION fit for FDM (no glue, no magnets).
Design follows the friction-fit technique notes:
  - square plug with rounded corners + a top starter chamfer (self-aligning wedge)
  - socket sized with an intentional clearance gap (slicer-safe on FDM)
  - chamfered socket mouth (eases the start of insertion)
  - bottom chamfer on the plug to dodge elephant-foot
  - MINIMAL CONTACT POINTS: 4 internal friction ribs in the socket so the plug
    grips on 4 points, not the whole wall -> consistent, tunable fit.

Tuning the fit after a test print:
  - too tight  -> raise SOCKET_CLEARANCE 0.05 at a time, or lower RIB_DEPTH
  - too loose  -> raise RIB_DEPTH 0.05 at a time
All units are millimetres.
"""

# ---- plug (lives on the underside of every token) ----
# 2026-07-09: plug/socket are rotated 45 deg about Z (DIAMOND orientation).
# Bases print text-face-UP (needed for the white filament swap on the wording),
# which lays the socket sideways -- a square roof then bridges and sags without
# support. A diamond's roof is two 45 deg slopes: self-supporting in ANY print
# orientation, and still keyed against token rotation (unlike a cylinder).
# PLUG_W shrank 20 -> 16 so the diamond diagonal (22.6mm) clears the 30mm base
# depth with real walls. NOT compatible with pre-diamond printed parts.
PLUG_DIAMOND    = True   # both weld_plug.py and build_base.py honour this
PLUG_W          = 16.0   # square plug footprint (X and Y), pre-rotation
PLUG_H          = 8.0    # how far the plug sticks down / into the socket
PLUG_CORNER_R   = 1.2    # rounded vertical corners (reduce contact stress)
PLUG_TOP_CHAMFER = 1.2   # starter wedge on the leading (bottom) edge of the plug
PLUG_ROOT_CHAMFER = 0.4  # chamfer where plug meets token body (anti elephant-foot)

# ---- socket (cut into the top face of every base) ----
SOCKET_CLEARANCE = 0.35  # per-side gap between plug and socket wall (>=0.3 = slicer safe)
SOCKET_W         = PLUG_W + 2 * SOCKET_CLEARANCE   # 20.70
SOCKET_DEPTH     = PLUG_H + 0.6                     # a touch deeper so the plug seats fully
SOCKET_MOUTH_CHAMFER = 1.0                          # funnels the plug in at the opening

# ---- friction ribs (the actual grip; point contact, not full-wall) ----
RIB_DEPTH  = 0.30   # how far each rib protrudes into the cavity (the grip knob)
RIB_WIDTH  = 2.5    # rib width along the wall
RIB_HEIGHT = 5.0    # rib height up the wall (leaves the chamfered mouth clear)

# ---- flat-backed relief ----
# Tokens are cut to a flat back (keeping the domed 3D front) so they print flat
# on the bed with full contact (no warping, no supports). This fraction of the
# token's depth (front side) is kept; the rest is sliced off flat.
RELIEF_FRONT_KEEP = 0.6

# ---- base default geometry ----
# Front face = 40 mm wide x 30 mm tall (per Trophy base.pdf, 2026-06-17), 1 mm margin.
# Depth kept at 30 mm for a balanced plinth that still seats the 20 mm plug.
BASE_W = 40.0
BASE_D = 30.0
BASE_H = 30.0
BASE_BEVEL = 2.0
