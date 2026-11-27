# Cap Mechanics

NBA and NFL salary cap explorer: every team's cap situation, contracts, a trade machine and a deadline tracker, explained in plain English.

## Structure
- `src/app.html` — the site (HTML/CSS/JS app; real URLs like `/nba`, `/nfl/miami-dolphins`, using the History API)
- `data/nba/*.json`, `data/nfl/*.json` — per-team roster and contract data
- `scripts/build_data.py` — combines team files into `data.json`
- `scripts/build.py` — builds `public/`: one HTML file per page (home, league pages, 62 team pages) with its own title, description and crawlable summary, plus `sitemap.xml` and `robots.txt`
- `public/` — what Vercel serves

## Build
```
python3 scripts/build.py
```
Data sources: JJNBA team cap sheets (NBA), Over The Cap (NFL). Snapshot as of Nov 16, 2026.
