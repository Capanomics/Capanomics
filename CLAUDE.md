# Capanomics

Static NBA/NFL salary cap site deployed by Vercel from `public/`.

- Site source: `src/app.html`; data in `data/`; build with `python3 scripts/build.py`.
- Never edit `public/index.html` by hand; it is generated.
- Data refreshes follow `REFRESH.md` exactly, and only publish when `scripts/validate.py` passes.
