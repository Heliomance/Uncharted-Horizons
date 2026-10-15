`DejaVuSansUH-subset.woff2` is a Latin subset of DejaVu Sans (`/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`), the
font Unciv's desktop build renders with on Linux. The artboards load it under the CSS family name "DejaVu Sans UH", so
that it never collides with an installed DejaVu Sans. Its licence (Bitstream Vera, with DejaVu's changes in the public
domain) allows redistribution and modification; the full text is in `DejaVu-LICENSE.txt`. It is uploaded to the canvas
as an asset, and the artboards name it by the asset's url (`font_url.txt`).

Subset: `pyftsubset DejaVuSans.ttf --unicodes="U+0020-007E,U+00A0-00FF,U+2013,U+2014,U+2018,U+2019,U+201C,U+201D,U+2022,U+2026,U+2190-2193,U+2605,U+2713,U+2717,U+25BE,U+00D7,U+2212" --flavor=woff2 --layout-features='kern,liga'`
