# Open-book end-to-end test

On 30 September 2026, an original upright, front-facing open-book image was passed to `make_award.py` in a fresh clone of public commit `96b3f9d475c8ce70df9fa24627228fac58a597e8`. The final complete run exited successfully and wrote the raw GLB, separate top/base STLs, twelve review images, a print handoff, and a checksummed manifest. This same concept was rerun while correcting two workflow bugs before the final successful run; it was not a one-attempt success.

The GPU was accessible inside a fresh Ubuntu Docker container, but the full TRELLIS inference used the existing working Conda environment on Robbin. A new Docker image with TRELLIS was not built or validated. Microsoft TRELLIS and model weights remain separate prerequisites.

| Written file | Dimensions | Inspection |
| --- | --- | --- |
| `top-with-plug.stl` | 38.00 × 24.78 × 31.57 mm | One connected watertight body, zero non-manifold or inconsistent-winding edges, centred diamond cross-section 20.93 × 20.93 mm at the inspection plane. |
| `named-base.stl` | 40.00 × 31.60 × 30.00 mm | One connected watertight body, zero non-manifold or inconsistent-winding edges. |

The automated top repair removed four microscopic duplicate Boolean slivers (12 bad edges to zero) within its strict area cap. The [Drive evidence folder](https://drive.google.com/drive/folders/1srD06FElxI335N2Jff9JZxn8iHdMbUA2) contains the owned input image, both STLs, raw GLB, previews, manifest, and handoff. The input SHA-256 is `c3fcb07c6436e45342745cce28a90bf2eb70d060c13f8e54fa78d042c0375a68`.

Visual review found an upright open book with a central seam in the assembled views. Its pages and side are thick and block-like, with weak page-edge detail. **This is a workflow proof, not a sale-ready token or a print-proven award.** No slicing, physical print, or plug/socket fit test was performed.
