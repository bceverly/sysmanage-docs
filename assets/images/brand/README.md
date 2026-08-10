# SysManage brand assets

Social and brand graphics built from the site's existing visual language — the
palette in `assets/css/style.css` and the convergence concept from the homepage
(`fragmentation-today-tomorrow.svg`, `unified-control-plane.svg`).

**The SVGs are the source of truth. The bitmaps are build output.** Edit an SVG,
then run `./render-brand-assets.sh` to regenerate. LinkedIn accepts only PNG and
JPEG (3MB maximum), which is why the rasters are committed.

## Files

| File | Size | Use |
| --- | --- | --- |
| `sysmanage-mark.svg` | vector | Square brand mark, dark tile. Source for the logo rasters. |
| `sysmanage-mark-light.svg` | vector | Same mark for light backgrounds, transparent. |
| `sysmanage-linkedin-logo-400.png` | 400×400 | **LinkedIn Page logo.** Their recommended size (268×268 minimum). |
| `sysmanage-linkedin-logo-800.png` | 800×800 | Retina / other social profiles. |
| `sysmanage-linkedin-logo-1600.png` | 1600×1600 | GitHub org avatar, decks, print. |
| `sysmanage-mark-light-512.png` | 512×512 | Mark on light surfaces, transparent. |
| `sysmanage-linkedin-cover.svg` | vector | Source for the Page cover. |
| `sysmanage-linkedin-cover-4200x700.jpg` | 4200×700 | **LinkedIn Page cover — upload this one.** LinkedIn advises JPEG over PNG for covers. |
| `sysmanage-linkedin-cover-4200x700.png` | 4200×700 | Lossless version of the same cover. |
| `sysmanage-linkedin-cover-wide.svg` | vector | Source for the wide banner. |
| `sysmanage-linkedin-cover-1584x396.jpg/.png` | 1584×396 | Personal LinkedIn profile banner (a different spec from the Page cover). |
| `sysmanage-social-card.svg` | vector | Source for the share card. |
| `sysmanage-social-card-1200x627.png` | 1200×627 | LinkedIn post / link-share image at their 1.91:1 custom-image ratio. Also suitable as the site's `og:image`. |

Not built: the Life tab images (1128×376 main, 502×282 modules, 900×600 photos).
Those modules require Career Pages, and the compositions here would need
reworking for a 3:1 and a 1.78:1 frame rather than being rescaled.

## Design decisions

**The mark is symbol-only, with no wordmark and no tagline.** LinkedIn renders
the Page logo at roughly 24–48px next to posts, in search results, and in
Experience entries, where fine detail and text disappear. The mark holds up down
to 24px.

**Six satellite nodes, not five.** The mark refines the existing
`sysmanage-icon.svg` hub-and-nodes symbol, raising the node count to six to match
the six supported operating systems and applying the site's colour coding: three
blue nodes (Windows, Linux, macOS) and three green (FreeBSD, OpenBSD, NetBSD).
Spokes were thickened and the hub given a white core so the symbol survives
being scaled down.

**The logo tile carries a faint rim.** LinkedIn displays Page logos on both light
and dark surfaces. The navy tile's lower-right corner is close enough to
LinkedIn's dark-mode grey (`#1b1f23`) that the silhouette dissolved without it.
Tested against `#ffffff`, the feed grey `#f3f2ef`, and `#1b1f23`.

**The logo is deliberately not transparent.** LinkedIn composites transparent
logos onto white, which would strand the light-blue hub on a white field. The
opaque tile renders identically everywhere.

**Covers keep everything centred.** LinkedIn crops Page covers to fit different
screens and specifically warns about the lower-right corner. All text sits
inside the middle ~58% of the width; the lower-right holds nothing but
decorative gradient lines, and the Page logo overlaps the lower-left on desktop.

**The converging lines are the homepage story, simplified.** Lines sweep in from
both edges and land on a single lit node at bottom centre, sitting on the
blue-to-green accent rule. It's the fragmentation-to-one-control-plane concept
reduced to something that still reads at 6:1, and it survives edge cropping
because the payload is in the centre.

## Colours

Taken from `assets/css/style.css`:

- `#0d3d5c` primary-900 — cover background base
- `#1565a0` primary-700 — glow, gradient start
- `#4a9fd8` primary-300 — hub, blue nodes, accents
- `#5fa865` secondary-300 — green nodes, BSD accents
- `#a9d5f0` / `#9fd6ae` — OS list text (blue for Windows/Linux/macOS, green for the BSDs)

Type uses the same stack as the site's other SVG diagrams:
`'Segoe UI', system-ui, -apple-system, Roboto, Helvetica, Arial, sans-serif`.

## Regenerating

```sh
./render-brand-assets.sh
```

Requires `google-chrome` (headless renderer) and ImageMagick (`magick`). Most
assets render at 2x and downsample for clean edges; the 4200px cover renders at
1x, where Chrome's antialiasing is already ample.
