"""Image-to-mesh adapter. Run with Python from an installed Microsoft TRELLIS environment."""
import argparse
import os
from pathlib import Path

os.environ.setdefault("SPCONV_ALGO", "native")
os.environ.setdefault("ATTN_BACKEND", "xformers")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default="microsoft/TRELLIS-image-large")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"image does not exist: {args.image}")
    args.out.parent.mkdir(parents=True, exist_ok=True)

    from PIL import Image
    from trellis.pipelines import TrellisImageTo3DPipeline
    from trellis.utils import postprocessing_utils

    pipeline = TrellisImageTo3DPipeline.from_pretrained(args.model)
    pipeline.cuda()
    with Image.open(args.image) as source:
        image = source.convert("RGBA")
    outputs = pipeline.run(image, seed=args.seed)
    if not outputs.get("mesh") or not outputs.get("gaussian"):
        raise RuntimeError("TRELLIS returned no mesh or Gaussian output")
    glb = postprocessing_utils.to_glb(
        outputs["gaussian"][0], outputs["mesh"][0],
        simplify=0.95, texture_size=1024,
    )
    glb.export(str(args.out))
    if not args.out.is_file() or args.out.stat().st_size == 0:
        raise RuntimeError("TRELLIS did not write a GLB")
    print(f"RAW_MESH={args.out}")


if __name__ == "__main__":
    main()
