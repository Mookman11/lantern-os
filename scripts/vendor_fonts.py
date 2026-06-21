#!/usr/bin/env python3
"""Vendor Google Fonts locally (local-first; no runtime CDN). See #861.

For each Google Fonts CSS2 stylesheet the app references, this fetches the CSS
with a desktop-Chrome User-Agent (so Google serves woff2), downloads every
referenced gstatic woff2 into public/vendor/fonts/, and rewrites the @font-face
`src` URLs to local relative paths. Output per entry: one `<name>.css` + its
woff2 files. Re-runnable to refresh the pinned assets.

    python scripts/vendor_fonts.py

Why: a local-first app must not phone home — remote Google Fonts leaks every
visitor's IP+UA to Google on each page load, and breaks when offline.
"""
import hashlib
import os
import re
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "apps", "lantern-garage", "public", "vendor", "fonts")

# name -> the exact Google Fonts CSS2 URL the app references (families + weights).
FONTS = {
    # dream-journal.css
    "dream-journal-fonts": (
        "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:"
        "ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap"
    ),
    # kalshi-terminal.html / stock-trader.html / trading-news.html (superset)
    "ibm-plex": (
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600"
        "&family=IBM+Plex+Sans:wght@300;400;500&display=swap"
    ),
}

WOFF2_RE = re.compile(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)")


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def vendor(name, url):
    css = fetch(url)
    os.makedirs(OUT, exist_ok=True)
    urls = list(dict.fromkeys(WOFF2_RE.findall(css)))  # dedup, keep order
    for u in urls:
        # stable, unique filename per weight/subset (sha of the source URL)
        fn = f"{name}-{hashlib.sha1(u.encode()).hexdigest()[:8]}.woff2"
        with open(os.path.join(OUT, fn), "wb") as f:
            f.write(fetch(u, binary=True))
        css = css.replace(u, f"./{fn}")
    with open(os.path.join(OUT, name + ".css"), "w", encoding="utf-8") as f:
        f.write(css)
    print(f"{name}: vendored {len(urls)} woff2 + {name}.css")


if __name__ == "__main__":
    for n, u in FONTS.items():
        vendor(n, u)
    print(f"done -> {OUT}")
