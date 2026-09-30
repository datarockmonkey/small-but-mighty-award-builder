# Make a Small But Mighty award at home

This is the free making workflow. Start with a photo you own or have permission to use, turn its subject into a **top charm**, repair and inspect that mesh, add the standard diamond plug, then generate a base with your own wording. Slice the two resulting STLs for **your** printer. The optional paid STL pack is a curated shortcut; this source and these instructions do not require a purchase.

The automated parts here run in [Blender 5.0](https://www.blender.org/download/releases/5-0/). They are source tools, not a one-click promise. The photo-to-3D conversion is a manual handoff to an external image-to-3D tool, and different photos need different modelling repairs. The repository contains no photos, generated model weights, font binaries, machine G-code or printer-control commands.

## What you need

- Blender 5.0.1 was used for the verified example. No pip packages are needed for the included base, connector, geometry inspection or render scripts.
- A photo you may use. Isolate one object against a plain background, show the whole shape and avoid loose or floating parts. A three-quarter view showing front, side and top is easier for image-to-3D than a flat frontal view.
- An image-to-3D generator that exports GLB, OBJ or STL. The studio used [Microsoft TRELLIS](https://github.com/microsoft/TRELLIS) for some runs. Follow its own installation and model terms; it needs a compatible GPU and substantial dependencies, and its outputs often need repair. An external hosted service may charge and has its own usage and commercial terms. No generator or account is bundled here.
- A locally installed font that you have rights to use for your purpose. The verified sample used DejaVu Sans Bold on Linux. The repository does not redistribute a font.
- A slicer configured for your actual machine, nozzle, material and bed. STL is geometry, not printer instructions.

## Step 1 — from photo to raw top mesh

Use your own photo as the image-to-3D input. Export only the intended object to `output/raw-top.glb` (or `.obj`/`.stl`). Inspect the result in a 3D editor from front, side, top and underneath. Remove background, floating pieces and model-generated plinths. A reconstructed colour patch is not structural geometry; check actual thickness. Keep the recognisable silhouette. For round objects, keep the curves round; do not apply low-poly faceting automatically.

This is the one step this repository cannot make reproducible across all owners' photos or GPU setups. A generator output is **not** a release-ready STL. Read [PHOTO_TO_TOP.md](PHOTO_TO_TOP.md) for the edits and rejection criteria.

## Step 2 — attach the standard connector

For a reviewed, solid raw mesh:

```sh
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/weld_plug.py -- output/raw-top.glb output/top-with-plug.stl 38 0
```

The final `0` disables decimation, which preserves round surfaces. The script scales the body to a 38 mm maximum footprint / 40 mm maximum height, centres it, adds an 8 mm deep diamond plug and writes **millimetre STL**. It now refuses spatially detached islands. It does not know where the solid load path belongs: a handle, gap, stem or thin wall needs a manual connector position and likely a different body edit. A visually ugly central riser is a rejection, even if mesh checks pass. Never scale a finished plug.

For a toolchain control unrelated to any photo or product design, run `scripts/make_geometry_control.py` first, then use its output as `raw-top.glb` with `.stl` extension. This confirms that Blender and the connector script execute; it does not prove a real subject or a print.

## Step 3 — make the named base

```sh
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/build_base_named.py -- \
  --name "Alex" --message "Well|Done" \
  --font /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf \
  --out output/alex-base.stl
```

The name is on the back; the front wording is raised. `|` makes an explicit line break. The script rejects wording under a measured 5 mm capital height. It does not guarantee all glyphs, stroke widths or names. Both parts are separate single-colour STLs; colour changes are optional. The socket nominal width is 16.70 mm and the plug nominal width is 16.00 mm. Real fit depends on printer calibration and material.

## Step 4 — inspect the actual written files

```sh
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/inspect_stl.py -- output/top-with-plug.stl
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/inspect_stl.py -- output/alex-base.stl
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/render_views.py -- output/top-with-plug.stl output/top-view
```

Check five generated views, especially the underside and the likely display angle. The inspector measures dimensions, volume, open edges, inconsistent winding and connected bodies. It cannot prove a strong neck, good seat, support removal, bed adhesion, surface quality or physical fit. Edit the raw mesh and rerun if any view fails. Do not silently repair a shape into a different subject.

## Step 5 — slice and test your own setup

Import the top and base as separate STLs into your slicer. Confirm the slicer shows millimetres and a roughly 40 mm base. Choose an orientation with real body-to-bed contact, then decide whether a brim or supports are needed. Keep supports off the display face where practical and inspect the preview layer by layer. A historical K2 control used a 0.4 mm nozzle, PLA, 0.12 mm layers, 15% grid infill and tree supports, but that is **reference evidence only**, not a universal profile. Print one calibration control before a batch. Check the actual fit and surface in hand. No physical print of this public toolchain control was started for this release.

## What was verified for this source snapshot

On Blender 5.0.1, `Alex` / `Well|Done` exported at 40 × 31.6 × 30 mm; the written base STL had one body, no non-manifold or inconsistent-winding edges, and positive volume. A neutral sphere control passed through the top connector script; the written top measured 38 × 30.4 × 38 mm and also had one watertight body. Five top views were rendered and inspected. The first extracted top script mistakenly exported a 0.038 mm width; that scale error was fixed before this snapshot. Neither control was physically printed. They establish tool execution and basic geometry only.

## Licence and scope

The source code in this repository is offered under [MIT](LICENSE) by Dotted Line Studio LTD. Your photo, generated mesh, model service and font each have **separate** rights. This repository grants no right to redistribute anyone else's image, model or font. No paid STL assets are included here. See [SOURCE_SCOPE.md](SOURCE_SCOPE.md).
