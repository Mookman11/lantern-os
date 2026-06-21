# Vendored third-party assets (local-first)

Lantern OS is local-first (see [CLAUDE.md](../../../../CLAUDE.md)) — the frontend must
not pull third-party assets at runtime. Fetching from a CDN breaks offline, leaks every
visitor's IP+UA to the CDN, and is an unpinned supply-chain risk. These assets are
therefore vendored and served from `/vendor/*`. See alex-place/lantern-os#861.

## pdfjs/ — Mozilla pdf.js
- **Version:** `pdfjs-dist@3.11.174` (pinned)
- **Source:** `https://unpkg.com/pdfjs-dist@3.11.174/build/{pdf.min.js,pdf.worker.min.js}`
- **Used by:** `knowledgecenter.html` (`pdf.min.js` + `GlobalWorkerOptions.workerSrc`)
- **Refresh:** re-download both files from the pinned unpkg URLs.

## fonts/ — Google Fonts (self-hosted woff2)
- `dream-journal-fonts.css` — Cormorant Garamond + Inter → `dream-journal.css`
- `ibm-plex.css` — IBM Plex Mono + IBM Plex Sans → `kalshi-terminal.html`, `stock-trader.html`, `trading-news.html`
- woff2 files are named `<set>-<sha1(url)[:8]>.woff2`; each CSS references them by relative path.
- **Refresh:** `python scripts/vendor_fonts.py` (re-fetches the CSS with a desktop UA,
  re-downloads the woff2, and rewrites `src` URLs to local paths).

No remote `unpkg.com` / `fonts.googleapis.com` / `fonts.gstatic.com` references remain in
`apps/lantern-garage/public/`.
