# Award geometry and fit specifications

These are the **default nominal dimensions in millimetres** for `make_award.py` at this repository revision. The executable source of truth is [`scripts/connector_std.py`](scripts/connector_std.py), together with the [top builder](scripts/weld_plug.py), [base builder](scripts/build_base_named.py), and [orchestrator](make_award.py). The output STL and its inspection report are the evidence for any individual run. Environment overrides can change some defaults; remeasure the exported files if you use them.

## Assembly and coordinates

- There are **two STL parts**: `top-with-plug.stl` and `named-base.stl`. The diamond plug is welded into the top; the matching socket is cut into the base. There is no loose connector piece, glue, or magnet in the default design.
- The top's local **Z axis** is vertical when assembled. The plug and socket are centred at X=0, Y=0. Both are square profiles rotated **45° around Z**, making their plan view a diamond. The matching rotation keys the top against turning in the base.
- The top is printed separately from the base. A successful digital mesh check does not prove the two parts will physically fit or hold together on a specific printer.

## Plug, socket, and clearance

| Feature | Default | Meaning |
| --- | ---: | --- |
| Plug profile | 16.00 × 16.00 mm | Square before its 45° rotation; about 22.63 mm across the sharp-corner diamond's X/Y envelope, before corner rounding. |
| Plug body height | 8.00 mm | Nominal solid height before the weld shift. |
| Plug weld overlap | 1.00 mm | `make_award.py` raises the plug into the top by this amount; approximately **7.00 mm remains exposed** below the token. |
| Plug corner bevel | 1.20 mm | Bevel modifier rounds the plug's corners; actual exported profile must be inspected. |
| Plug starter bevel | 1.20 mm | Bevel modifier intended to ease insertion. |
| Socket profile | 16.70 × 16.70 mm | Matching rotated square; about 23.62 mm across its unrounded diamond envelope. |
| Socket depth | 8.60 mm | Nominal cavity depth below the top of the base. |
| Socket bevel | 1.00 mm | Bevel modifier intended to ease the opening. |
| Unribbed lateral clearance | **0.35 mm per side** | `(16.70 − 16.00) / 2`; 0.70 mm across both sides before ribs. |
| Four friction ribs | 0.30 mm projection each | Each rib is 2.50 mm wide along a cavity wall and 5.00 mm tall. |
| Rib-to-rib throat | **16.10 mm** | `16.70 − 2 × 0.30`; nominal gap around a 16.00 mm plug is **0.05 mm per side** at opposing ribs. |
| Rib wall embed | 0.60 mm | Extra material embedded into the socket wall for a robust Boolean union; it does not add to the 0.30 mm cavity-side projection. |
| Nominal socket-bottom gap | about **1.60 mm** | `8.60 − (8.00 − 1.00)` if the top seats against the base. This is derived from the default weld overlap, not a measured physical gap. |

The 0.35 mm wall clearance and 0.05 mm rib clearance are **CAD values, not guaranteed printed clearances**. Bevels, rounded corners, filament shrinkage, slicer contour compensation, and printer calibration change the actual fit. Do a small fit print before relying on friction. The source design suggests changing socket clearance or rib depth in 0.05 mm increments after a measured fit test; do not resize the shared plug to compensate for one printer.

## Part dimensions and lettering

| Feature | Default |
| --- | ---: |
| Base body | 40.00 mm wide × 30.00 mm deep × 30.00 mm tall |
| Base edge bevel | 2.00 mm |
| Nominal un-bevelled wall across the narrow depth at socket's diamond corners | `(30.00 − 16.70 × √2) / 2 ≈ 3.19 mm` per side; this is a plan-view calculation, **not** a measured minimum wall after bevels. |
| Top body target | Up to 40.00 mm high, constrained by a 38.00 mm maximum X/Y dimension; uniform scaling chooses whichever cap is reached first. This **does not guarantee** the top stays within the base's narrower 30 mm depth. |
| Top voxel repair in `make_award.py` | 0.18 mm voxel size before connector welding. |
| Central riser | 7.20 × 7.20 mm plan; height is 18% of the scaled token body height, capped at 20.00 mm, to bridge a narrow or hollow bottom into the plug. |
| Front message | Raised, single-colour, fused to the base; nominal 1.60 mm proud of the original front face after a 0.40 mm overlap. |
| Back recipient name | Engraved 0.80 mm deep by default. |
| Text layout | Auto-wrap target: at most two words and ten characters per line; `|` forces a line break. Font capital-height gate: at least 5.00 mm after shrink-to-fit. |

Raised front wording can make the **overall exported base depth larger than 30.00 mm**. The open-book test base, for example, measured 40.00 × 31.60 × 30.00 mm. The print font is [`SBMSoftCounterPrototype-Regular.ttf`](fonts/SBMSoftCounterPrototype-Regular.ttf), with its separate [OFL licence](fonts/OFL.txt); it is not one of the commercial brand display fonts.

Two values in `connector_std.py` are **not applied in the default public run**: the declared 0.40 mm `PLUG_ROOT_CHAMFER` is reserved, and `RELIEF_FRONT_KEEP = 0.6` belongs to an optional legacy flat-back relief mode. They should not be counted as features of a generated default STL.

## Automated validation and current proof

The written STLs must each have positive volume, one connected body, closed manifold edges, consistent winding, and plausible scale (largest dimension from 5 to 200 mm). The top additionally needs X/Y span of at least 18 mm, Z height of at least 20 mm, and a centred diamond section 2 mm above its lowest point: X and Y section spans each 20–24 mm, centre within 1 mm of the origin. The base builder also refuses lettering below the 5 mm capital-height floor. The sliver cleaner removes only narrowly defined duplicate Boolean faces below 0.001 mm² each, with at most 20 such faces and 0.02 mm² total area; remaining non-manifold edges stop the run.

The [first end-to-end open-book test](examples/OPEN_BOOK_TEST.md) passed those digital checks: top **38.00 × 24.78 × 31.57 mm**, one watertight body, inspected diamond section **20.93 × 20.93 mm**; base **40.00 × 31.60 × 30.00 mm**, one watertight body. These are measured exported-file results for that one input, not universal output dimensions. No physical plug/socket fit, slicing result, strength, or print quality has been verified by that test.
