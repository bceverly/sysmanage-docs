#!/usr/bin/env bash
#
# Regenerates the raster brand assets in this directory from their SVG sources.
#
# LinkedIn only accepts PNG/JPEG uploads (3MB max), so the SVGs here are the
# source of truth and the bitmaps are build output. Re-run after editing an SVG.
#
# Requires: google-chrome (headless renderer) and ImageMagick (magick).
#
set -euo pipefail

cd "$(dirname "$0")"

# render <src.svg> <out.png> <width> <height> [transparent] [scale]
# Renders through headless Chrome at <scale>x, then downsamples to the exact
# target size so text edges and curves land clean. Canvases that are already
# very large render at 1x -- Chrome antialiases SVG well and 2x of 4200px wide
# is a needlessly enormous screenshot.
render() {
    local src="$1" out="$2" w="$3" h="$4" transparent="${5:-}" scale="${6:-2}"
    local tmp bg page_bg
    tmp="$(mktemp -d)"

    if [ -n "$transparent" ]; then
        bg="--default-background-color=00000000"
        page_bg="transparent"
    else
        bg="--default-background-color=FFFFFFFF"
        page_bg="#ffffff"
    fi

    cat > "$tmp/page.html" <<HTML
<!doctype html><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;width:${w}px;height:${h}px;overflow:hidden;background:${page_bg}}
  img{display:block;width:${w}px;height:${h}px}
</style>
<img src="$(realpath "$src")">
HTML

    google-chrome --headless --disable-gpu --no-sandbox --hide-scrollbars \
        --force-device-scale-factor="$scale" "$bg" \
        --window-size="${w},${h}" \
        --screenshot="$tmp/raw.png" \
        "file://$tmp/page.html" >/dev/null 2>&1

    magick "$tmp/raw.png" -filter Lanczos -resize "${w}x${h}!" \
        -strip -define png:compression-level=9 "$out"

    rm -rf "$tmp"
    echo "  $out ($(magick identify -format '%wx%h, %b' "$out"))"
}

# to_jpg <in.png> <out.jpg>
# LinkedIn re-encodes uploads and advises a high-resolution JPEG over a PNG for
# cover images. 4:4:4 sampling keeps the coloured OS-list text from smearing.
to_jpg() {
    magick "$1" -quality 92 -sampling-factor 4:4:4 -strip "$2"
    echo "  $2 ($(magick identify -format '%wx%h, %b' "$2"))"
}

echo "Rendering SysManage brand assets..."

# Square logo mark. LinkedIn recommends 400x400 for the Page logo (268x268
# minimum); the larger sizes cover GitHub org avatars, decks, and print.
render sysmanage-mark.svg sysmanage-linkedin-logo-400.png   400  400
render sysmanage-mark.svg sysmanage-linkedin-logo-800.png   800  800
render sysmanage-mark.svg sysmanage-linkedin-logo-1600.png 1600 1600

# Mark for light backgrounds, transparent.
render sysmanage-mark-light.svg sysmanage-mark-light-512.png 512 512 transparent

# LinkedIn Page cover, 4200x700 (their recommended size, and the minimum).
render sysmanage-linkedin-cover.svg sysmanage-linkedin-cover-4200x700.png 4200 700 "" 1
to_jpg sysmanage-linkedin-cover-4200x700.png sysmanage-linkedin-cover-4200x700.jpg

# Wide banner: the personal LinkedIn profile banner spec.
render sysmanage-linkedin-cover-wide.svg sysmanage-linkedin-cover-1584x396.png 1584 396
to_jpg sysmanage-linkedin-cover-1584x396.png sysmanage-linkedin-cover-1584x396.jpg

# Link-share / post card at LinkedIn's 1.91:1 custom image ratio. Also usable as
# the site's og:image.
render sysmanage-social-card.svg sysmanage-social-card-1200x627.png 1200 627

echo "Done."
