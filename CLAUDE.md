# Cap Mechanics

Static NBA/NFL salary cap site deployed by Vercel from `public/`.

- Site source: `src/app.html`; data in `data/`; build with `python3 scripts/build.py`.
- Never edit anything in `public/` by hand; `scripts/build.py` generates it (one HTML file per page, e.g. `public/nfl/miami-dolphins.html`, plus sitemap.xml and robots.txt).
- Data refreshes follow `REFRESH.md` exactly, and only publish when `scripts/validate.py` passes.
