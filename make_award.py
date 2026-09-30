"""One-command photo-to-award-STLs pipeline. Requires installed TRELLIS and Blender."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
DEFAULT_FONT = ROOT / "fonts" / "SBMSoftCounterPrototype-Regular.ttf"


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command, *, cwd=None, capture=False, dry_run=False, extra_env=None):
    shown_env = " ".join(f"{key}={value}" for key, value in (extra_env or {}).items())
    print("+", shown_env, " ".join(map(str, command)), flush=True)
    if dry_run:
        return ""
    result = subprocess.run(
        list(map(str, command)), cwd=cwd, check=True, text=True,
        env={**os.environ, **(extra_env or {})},
        stdout=subprocess.PIPE if capture else None,
    )
    if capture:
        print(result.stdout, end="")
    return result.stdout or ""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True, help="one owned/licensed subject photo")
    parser.add_argument("--name", required=True, help="recipient name on the back")
    parser.add_argument("--message", required=True, help="front text; | forces a line break")
    parser.add_argument("--out", type=Path, required=True, help="new or empty output folder")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--blender", default="blender")
    parser.add_argument("--trellis-python", default=sys.executable,
                        help="Python executable in the installed TRELLIS environment")
    parser.add_argument("--trellis-root", type=Path, required=True,
                        help="checkout of microsoft/TRELLIS used as working directory")
    parser.add_argument("--model", default="microsoft/TRELLIS-image-large")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true", help="show every command without generating files")
    args = parser.parse_args(argv)

    image = args.image.expanduser().resolve()
    font = args.font.expanduser().resolve()
    trellis_root = args.trellis_root.expanduser().resolve()
    out = args.out.expanduser().resolve()
    for label, path, file_expected in (("image", image, True), ("font", font, True),
                                       ("TRELLIS checkout", trellis_root, False)):
        if (path.is_file() if file_expected else path.is_dir()) is False:
            parser.error(f"{label} missing: {path}")
    if not args.name.strip() or not args.message.strip():
        parser.error("name and message must contain visible text")
    if out == ROOT or out == ROOT / "fonts" or out == ROOT / "scripts":
        parser.error("output folder cannot overwrite repository source or fonts")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error("output folder must be empty; choose a new run folder")
    if not args.dry_run:
        out.mkdir(parents=True, exist_ok=True)

    raw = out / "raw-top.glb"
    top = out / "top-with-plug.stl"
    base = out / "named-base.stl"
    blender = [args.blender, "--background", "--factory-startup", "--python-exit-code", "1", "--python"]
    run([args.trellis_python, ROOT / "scripts/trellis_generate.py", "--image", image,
         "--out", raw, "--model", args.model, "--seed", args.seed], cwd=trellis_root,
        extra_env={"PYTHONPATH": str(trellis_root) + os.pathsep + os.environ.get("PYTHONPATH", "")},
        dry_run=args.dry_run)
    run(blender + [ROOT / "scripts/weld_plug.py", "--", raw, top, 38, 0],
        extra_env={"AWARD_VOXEL_MM": "0.18"}, dry_run=args.dry_run)
    run(blender + [ROOT / "scripts/build_base_named.py", "--", "--name", args.name,
                   "--message", args.message, "--font", font, "--out", base], dry_run=args.dry_run)
    reports = {}
    for label, part in (("top", top), ("base", base)):
        output = run(blender + [ROOT / "scripts/inspect_stl.py", "--", part],
                     capture=True, dry_run=args.dry_run)
        if not args.dry_run:
            lines = [line.removeprefix("INSPECTION_JSON=") for line in output.splitlines()
                     if line.startswith("INSPECTION_JSON=")]
            if len(lines) != 1:
                raise RuntimeError(f"{label} inspection did not return one report")
            reports[label] = json.loads(lines[0])
            if not reports[label]["basic_mesh_pass"]:
                raise RuntimeError(f"{label} failed mesh checks")
        run(blender + [ROOT / "scripts/render_views.py", "--", part, out / f"{label}-view"],
            dry_run=args.dry_run)

    if args.dry_run:
        return 0
    expected = [raw, top, base] + [out / f"{label}-view-{angle}.png"
                                    for label in ("top", "base")
                                    for angle in ("front", "side", "top", "bottom", "display")]
    missing = [str(p) for p in expected if not p.is_file() or p.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"output missing or empty: {', '.join(missing)}")
    handoff = out / "PRINT_HANDOFF.md"
    handoff.write_text(
        "# Print handoff — candidate, not print-proven\n\n"
        f"- Photo SHA-256: `{checksum(image)}`\n"
        f"- Top STL SHA-256: `{checksum(top)}`\n"
        f"- Base STL SHA-256: `{checksum(base)}`\n"
        "- Connector: 16.00 mm diamond plug; axis is the top's vertical Z axis in assembly.\n"
        "- Base socket: nominal 16.70 mm; physical clearance needs a printer fit test.\n"
        "- Protected display face: determine from the five top views before slicing.\n"
        "- Fragile features and load direction: unknown for this generated subject; inspect before printing.\n"
        "- Top orientation candidates: upright with plug on the bed, or side/back on the bed with supports as needed. "
        "Compare real body contact, display-face damage and layer-direction strength in the slicer.\n"
        "- Base orientation: choose a stable face that preserves the raised front wording and socket.\n"
        "- Material, colour and nozzle: choose for the actual machine; no universal profile is bundled.\n"
    )
    manifest = {
        "status": "mesh checks passed; visual and physical print quality unverified",
        "input_photo": str(image), "input_sha256": checksum(image),
        "font": font.name, "font_sha256": checksum(font),
        "model": args.model, "seed": args.seed,
        "name": args.name, "message": args.message,
        "inspection": reports,
        "files_sha256": {p.name: checksum(p) for p in expected + [handoff]},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"AWARD_OUTPUT={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
