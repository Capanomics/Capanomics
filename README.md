# Capanomics

NBA and NFL salary cap explorer: every team's cap situation, contracts, a trade machine and a deadline tracker, explained in plain English.

## Structure
- `src/app.html` — the site (HTML/CSS/JS, single page with hash routes)
- `data/nba/*.json`, `data/nfl/*.json` — per-team roster and contract data
- `scripts/build_data.py` — combines team files into `data.json`
- `scripts/build.py` — builds `public/index.html` (the deployed page)
- `public/` — what Vercel serves

## Build
```
python3 scripts/build.py
```
Data sources: JJNBA team cap sheets (NBA), Over The Cap (NFL). Snapshot as of Nov 16, 2026.
