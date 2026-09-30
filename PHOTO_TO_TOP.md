# Image input and automatic gates

The supported route is `make_award.py --image ...` with an installed Microsoft TRELLIS environment. It calls TRELLIS itself, then runs the Blender top, base, inspection and rendering steps. There is no required hand-modelling stage.

Use an image you own or have the right to use. Put one complete subject against a simple background; show front, side and top if possible. Avoid subjects whose identity depends on colour rather than shape, or whose whole weight hangs from a tiny stem. A background or plinth included in the input may become part of the model; this pipeline does not claim to identify and remove arbitrary unwanted geometry.

The run stops if generation fails, a part is spatially detached, a base text fit check fails, or either exported STL is not one watertight body at plausible scale. Those are measurable gates only. The output contact views expose the underside and display angle, but a program cannot confirm that a generated shape looks like the intended subject or survives your slicer and material. Reject an unsuitable result and rerun from a different image or seed; do not describe it as print-proven just because `manifest.json` exists.
