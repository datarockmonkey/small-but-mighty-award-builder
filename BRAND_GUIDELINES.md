# Small But Mighty brand guidelines

This is the practical brand guide for this public award-builder repository: its README, diagrams, example renders, tutorials, and any companion website. It follows the [final Small But Mighty colour branding guideline, 11 September 2026](https://drive.google.com/file/d/12GWyrLFF7M4H44_XDDREt6Vmh4TYNMOE/view?usp=drivesdk). The source guideline is the reference for the logo artwork and exact colour specifications; this document explains how to apply it to the digital award workflow.

## The idea

Small But Mighty makes recognition personal. Show the particular thing someone does or brings to a group, then let the maker put their own words on the base. Keep the voice warm, direct, and specific. Praise the person on their own terms; avoid rankings, comparisons, or language that treats being small as a flaw to overcome.

The product story is simple: **one image becomes a top token; the top gains an integral diamond plug; a personalised base gains the matching socket; the maker prints and tests the two parts before assembly.** A visual can simplify this sequence, but it must not imply that an illustration is a measured STL or a successful physical print.

## Colour

Use these exact sRGB hex values for digital artwork.

| Role | Colour | Hex | Typical use |
| --- | --- | --- | --- |
| Primary | Blue | `#0051FF` | Links, buttons on light backgrounds, main token accent |
| Primary | Lime | `#BEFF85` | Large fields, illustrations, prominent shapes |
| Primary | Butter | `#FFF988` | Large warm fields and highlights |
| Primary | Navy | `#0A1470` | Body copy and small labels on light backgrounds, outlines, dark backgrounds |
| Secondary | Pink | `#E91C98` | Large accents, icons, charts |
| Secondary | Teal | `#188CAB` | Large accents, icons, charts |
| Secondary | Olive | `#5F8321` | Large accents, icons, charts |
| Secondary | Purple | `#873EFF` | Large accents, icons, charts |
| Secondary | Orange | `#D86027` | Large accents, icons, charts |

Navy is the small-text colour on light backgrounds; use light text on Navy. Lime and Butter are surfaces or shapes, not text on white: their white-background contrast ratios in the source guide are only 1.18:1 and 1.10:1. Blue has 5.80:1 contrast on white, but only 2.69:1 on Navy, so do not put Blue links or buttons on a Navy field. The secondary colours clear 3:1 on both white and Navy and are for large text, icons, button fills, or chart marks; keep small text Navy on light backgrounds. Do not use secondary colours as link colours. Blue and Purple are too close to serve as adjacent, distinct categories.

For a new diagram, begin with white or Navy, choose one dominant primary accent, and let Lime or Butter create breathing room. Use the secondary palette sparingly to distinguish a real concept, not to decorate every component. These colours describe **artwork and communication**. STL files do not encode filament colour, and a preview colour is not a print instruction.

## Typography and logo

The source guideline names **CCOverbyteOff** for the logo, **Logic Monospace** for brand type, and **LoRes 9 Plus OT** as a display accent. They are commercial fonts. Do not commit their font binaries, trace them into a substitute logo, or assume that a desktop or Adobe Fonts licence permits redistribution in this repository. If a contributor does not have the licensed fonts, use a legible system monospace for working documents and keep the official logo as approved artwork supplied by the owner.

Use the supplied official logo on dark Navy when appropriate. For small light-background use below about 48 px, the source guide shows a blue monochrome version. The mascot placement in that sheet is not a master wordmark. This repository includes the owner's [standalone mascot artwork](assets/sbm-mascot.png), copied unchanged from the project's Mascot Still source (SHA-256 `c85bd1ed45461cbdda081323d6f592401ce5172f5880490b299d3aa6eee5c94d`). Treat it as a mascot icon, not as an approved logo lockup or a licence to reconstruct the commercial logo type. For new artwork, use the palette values above rather than sampling colours from this raster source.

The repository's [`SBMSoftCounterPrototype-Regular.ttf`](fonts/SBMSoftCounterPrototype-Regular.ttf), also called **SBM Soft Counter Prototype V1**, serves a **different purpose**: it is the sole bundled, [OFL-licensed](fonts/OFL.txt) prototype font for physical base wording. It is not one of the commercial brand fonts and does not replace them in official logo artwork. Its print legibility still needs a real-world check.

## Images and assembly diagrams

- Show the top token and diamond plug as **one continuous part**. Show the base and its recessed socket as the **second part**. Do not draw the plug as a loose third piece.
- Keep the subject recognisable from the front and show the underside or assembly angle when explaining the connector. A floating front-only product render does not prove attachment.
- Use clean, substantial, matte forms and enough contrast to read at README width. A technical concept may use the bright brand palette even when an actual prototype was printed in other colours.
- Mark generated illustrations as **concepts**. Use actual output renders, inspection results, and physical photos only for claims they can support. The [open-book test](examples/OPEN_BOOK_TEST.md) is a workflow proof, not a print-quality claim.
- Use original or licensed input images. Do not copy another seller's product photography or present an AI illustration as a photograph of a printed award.

The [README assembly illustration](assets/award-assembly-concept.png) is an example of this treatment: Blue top, Lime base, Butter backdrop, Navy directional detail. It shows the intended relationship between the two STLs, not their exact measured geometry.

## Writing and release checks

Write for someone making an award at home. Name the input, the two outputs, and the next action in plain language. Distinguish **generated**, **mesh-checked**, **sliced**, and **physically printed**; each is a different claim. Say when a token needs a new input image, a fit test, or a print review. Keep the maker's own message at the centre of the story, and never promise that every photo or printer will give the same result.

Before publishing a new asset or page, check that the palette and type roles match this guide, the assembly is physically understandable, the alternative text describes what the image actually shows, and any claims of successful printing have real print evidence.
