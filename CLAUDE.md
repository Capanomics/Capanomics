# Cap Mechanics

Static NBA/NFL salary cap site deployed by Vercel from `public/`.

- Site source: `src/app.html`; data in `data/`; build with `python3 scripts/build.py`.
- Never edit anything in `public/` by hand; `scripts/build.py` generates it (one HTML file per page, e.g. `public/nfl/miami-dolphins.html`, plus sitemap.xml and robots.txt).
- Data refreshes follow `REFRESH.md` exactly, and only publish when `scripts/validate.py` passes.
- Team-page "short version" summaries and the glossary come from `scripts/explain.py` (run by build.py), so they update with every data refresh.
- Each data refresh saves its report to `reports/YYYY-MM-DD.md`; read those to see what recent runs did.
