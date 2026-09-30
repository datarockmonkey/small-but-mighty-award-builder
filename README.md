# Small But Mighty award builder

Give the workflow one image and your own wording. It runs image-to-3D generation, attaches the standard diamond plug, makes a named base, checks both written STLs, and renders ten inspection views. There is no hand-modelling handoff in the command. **A passed run produces candidate STLs, not a print-proven award:** shape identity, surface quality, support strategy and physical plug/socket fit still depend on the input and printer.

## One-command workflow

Prerequisites:

1. A Linux machine with an NVIDIA GPU and at least 16 GB VRAM, and a working [Microsoft TRELLIS installation](https://github.com/microsoft/TRELLIS#installation). Install its dependencies and model under [its own licence](https://github.com/microsoft/TRELLIS#license). Model weights are not copied into this repository.
2. [Blender 5.0](https://www.blender.org/download/releases/5-0/) available as `blender`, or pass `--blender /path/to/blender`.
3. A single subject image you own or are licensed to use. A whole object against a plain background works best. Do not use another seller's product photograph as a cloning input.

From this repository, run:

```sh
python3 make_award.py \
  --image /path/to/your-object.png \
  --name "Alex" \
  --message "Well|Done" \
  --trellis-root /path/to/TRELLIS \
  --trellis-python /path/to/trellis-env/bin/python \
  --out output/alex-award
```

TRELLIS may download its model on first use. Use `--dry-run` to see all commands without running the model or Blender. `--model` accepts a local model directory or model ID; `--seed` fixes the generation seed. The output folder must be new or empty, so each run has independent evidence.

The output contains `raw-top.glb`, `top-with-plug.stl`, `named-base.stl`, five views for each STL (`front`, `side`, `top`, `bottom`, `display`), two assembled award views, `PRINT_HANDOFF.md`, and `manifest.json` with the input, font and output checksums plus actual geometry inspection results. The top stage applies a 0.18 mm voxel repair to close small reconstruction gaps, attaches the plug with 1.0 mm overlap, and removes only microscopic boolean slivers. A failed generation, Blender command, mesh inspection or missing output stops the run; it does not write a success manifest. A valid result can still depict the wrong subject or have a weak joint. If so, use another input image or seed and start a new run. The tool does not silently keep repairing a shape until a test passes.

The generated top and base are **separate single-colour millimetre STLs**. Import them into a slicer configured for your nozzle, material and printer. Review the slicer preview, print one fit test and inspect the real part before calling it proven. The nominal plug is 16.00 mm and the socket is 16.70 mm, but a real friction fit depends on machine calibration. This repository does not start a printer or promise a universal G-code file.

## What the command automates

| Stage | Program | Output / gate |
| --- | --- | --- |
| Image → raw mesh | Installed TRELLIS via `scripts/trellis_generate.py` | GLB must be written |
| Raw mesh → top | Blender `scripts/weld_plug.py` and `scripts/repair_boolean_slivers.py` | 0.18 mm voxel repair, standard diamond plug, microscopic sliver cleanup; larger damage refused |
| Name/message → base | Blender `scripts/build_base_named.py` | font measured; undersized wording refused |
| Written-file QA | Blender `scripts/inspect_stl.py` | each STL must be one watertight body at plausible scale; top must show a centred diamond plug section |
| Views and record | Blender `scripts/render_views.py`, `make_award.py` | ten PNGs and checksummed manifest |

These checks are necessary but do not measure every thin feature, visual likeness, surface finish, orientation or physical strength. No arbitrary photo-to-award system can guarantee those without inspecting the result and a physical trial. [PHOTO_TO_TOP.md](PHOTO_TO_TOP.md) describes input choices and failure cases; it is not a mandatory manual modelling step.

## The one bundled font

`fonts/SBMSoftCounterPrototype-Regular.ttf` is the **only font binary** in this repository and is the default for the base. It is a modified version of Poetsen One: the source authors retain their copyright, the modified font has a new name, and it is distributed under the [SIL Open Font License 1.1](fonts/OFL.txt). The repository's [MIT licence](LICENSE) covers our code, **not the font**. Its exact SHA-256 is `7ba873fc63c8bc36730123d227cc19be99ec433c91094a8d6019582b75807252`. This is a print-first prototype; the enlarged counters have been measured, but the `a` aperture and physical print result are not production-validated. Use `--font /path/to/another-licensed-font.ttf` if preferred.

## Evidence and scope

The complete command has now passed one real image-to-STL run from a fresh clone of commit `96b3f9d`: an original upright open-book image produced a one-body, watertight top with a centred diamond plug, a one-body, watertight named base, and review renders. See the [test record](examples/OPEN_BOOK_TEST.md) and [downloadable evidence](https://drive.google.com/drive/folders/1srD06FElxI335N2Jff9JZxn8iHdMbUA2). The result was visually recognisable but thick and lacking page detail. This validates the command path for that input; it does **not** validate print quality, physical fit, or the workflow for every image.

No paid STL pack, private customer data, third-party photographs, model weights, secret keys or machine-control commands are included. See [SOURCE_SCOPE.md](SOURCE_SCOPE.md).
