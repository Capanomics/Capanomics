# Capanomics data refresh procedure

This is the procedure the scheduled refresh follows. A human can run it too.
Goal: keep `data/` current, publish only when `scripts/validate.py` passes.

## 0. Setup
- Repo: `Capanomics/Capanomics`, branch `main`. Pushing to `main` redeploys capanomics.com on Vercel.
- Work in a fresh clone. Commit as `Capanomics Data Bot <noreply@capanomics.com>`.

## 1. Pick the mode
- **Full refresh** (re-read every team page): on Sundays, and every day during hot periods:
  NBA trade deadline week (Feb 4–12), NFL league-year start (Mar 9–20), NBA free agency (Jun 29–Jul 10).
- **Quick check** (default): read league summary pages, then refresh only teams that changed.

## 2. Reach the sources
WebFetch only opens URLs that appeared in a search result in the same session. Search first:
- NBA: WebSearch `jjnba NBA salary cap sheets 2026-27 all 30 teams payroll` → use the `https://jjnba.com/` and `https://jjnba.com/trade/` results. After one jjnba.com page is fetched, team pages like `https://jjnba.com/team/chicago-bulls/` open too.
- NFL: WebSearch `"overthecap.com/salary-cap-space"` → fetch the result URL (it may be `https://overthecap.com:443/salary-cap-space/`). Team pages `https://overthecap.com/salary-cap/<team-slug>` then open.
If a source can't be reached, do not guess: skip that league, note it in the summary, and still publish the other league if it passes.

## 3. League summaries (both modes)
**NBA payrolls** — fetch `https://jjnba.com/` with prompt:
> Output ONLY minified JSON, no prose: {"cap":salary_cap_M,"t":{"ATL":payroll_M,...}} with all 30 teams' 2026-27 payroll in $ millions with 2 decimals, keys = standard abbreviations ATL BOS BKN CHA CHI CLE DAL DEN DET GSW HOU IND LAC LAL MEM MIA MIL MIN NOP NYK OKC ORL PHI PHX POR SAC SAS TOR UTA WAS.

An NBA team "changed" if its payroll differs from `tp` in `data/nba/<TEAM>.json` by more than $0.05M.

**NBA hard caps** — fetch `https://jjnba.com/trade/` with prompt:
> Output ONLY minified JSON, no prose: {"hc":{"ATL":"None|1st Apron|2nd Apron",...}} for all 30 teams from the Hard Cap column, keys = standard abbreviations.

Update `data/nba/_hardcaps.json`: set `level` to `a1`/`a2`. **Never lower or remove an existing hard cap during a season** (it lasts the full league year); if JJNBA says "None" for a team we have as capped, keep ours. For a newly capped team use the reason "Hard-capped at the first|second apron per JJNBA's hard-cap tracking".

**NFL cap space** — fetch the Over The Cap cap-space page with prompt:
> Output ONLY minified JSON, no prose: {"y26":{"Team":[cap_space,effective_space,players,active_cap,dead_money],...},"y27":{"Team":[cap_space,effective_space,players,active_cap,dead_money],...}} for all 32 teams in the 2026 table (Base Salary Cap $301,200,000) and the 2027 table (the next table after it). Team keys = team nickname as shown (e.g. "Titans"). Money in $ millions with 3 decimals; negatives (shown in parentheses) as negative numbers.

Map nicknames to IDs (ARI Cardinals, ATL Falcons, BAL Ravens, BUF Bills, CAR Panthers, CHI Bears, CIN Bengals, CLE Browns, DAL Cowboys, DEN Broncos, DET Lions, GB Packers, HOU Texans, IND Colts, JAX Jaguars, KC Chiefs, LV Raiders, LAC Chargers, LAR Rams, MIA Dolphins, MIN Vikings, NE Patriots, NO Saints, NYG Giants, NYJ Jets, PHI Eagles, PIT Steelers, SF 49ers, SEA Seahawks, TB Buccaneers, TEN Titans, WAS Commanders).
An NFL team "changed" if, versus the current `data/nfl/_league.json`, active cap moved more than $2M or dead money moved more than $0.5M. Compare **before** overwriting `_league.json`, then write the new values (keys: space, eff, n, active, dead, space27, eff27, n27, active27, dead27).

## 4. Team pages (changed teams in quick mode; all teams in full mode)
**NBA** — `https://jjnba.com/team/<slug>/` (slugs: atlanta-hawks, boston-celtics, brooklyn-nets, charlotte-hornets, chicago-bulls, cleveland-cavaliers, dallas-mavericks, denver-nuggets, detroit-pistons, golden-state-warriors, houston-rockets, indiana-pacers, los-angeles-clippers, los-angeles-lakers, memphis-grizzlies, miami-heat, milwaukee-bucks, minnesota-timberwolves, new-orleans-pelicans, new-york-knicks, oklahoma-city-thunder, orlando-magic, philadelphia-76ers, phoenix-suns, portland-trail-blazers, sacramento-kings, san-antonio-spurs, toronto-raptors, utah-jazz, washington-wizards). Prompt:
> Output ONLY one line of minified JSON, no prose, no code fence: {"tp":TAX_PAYROLL_M,"p":[[name,pos,age,s2627,s2728,s2829,s2930,s3031],...],"tw":[two-way player names],"exc":"exceptions/TPEs short text","dead":[[name,amount_M]]}. Salaries in $ millions with 2 decimals. For future seasons use the number only if the player is under contract; use null if the cell is UFA/RFA/cap hold or blank. Skip the separate cap-hold table entirely. Two-way players go only in "tw".

Write it to `data/nba/<TEAM>.json` unchanged.

**NFL** — `https://overthecap.com/salary-cap/<slug>` (slugs: arizona-cardinals, atlanta-falcons, baltimore-ravens, buffalo-bills, carolina-panthers, chicago-bears, cincinnati-bengals, cleveland-browns, dallas-cowboys, denver-broncos, detroit-lions, green-bay-packers, houston-texans, indianapolis-colts, jacksonville-jaguars, kansas-city-chiefs, las-vegas-raiders, los-angeles-chargers, los-angeles-rams, miami-dolphins, minnesota-vikings, new-england-patriots, new-orleans-saints, new-york-giants, new-york-jets, philadelphia-eagles, pittsburgh-steelers, san-francisco-49ers, seattle-seahawks, tampa-bay-buccaneers, tennessee-titans, washington-commanders). Prompt:
> Extract this page's salary data as one line of minified JSON in this shape: {"p":[[name,cap26,base26,bonus26,cap27,status],...],"dead":[[name,amt],...],"t":{"off":X,"def":X,"st":X,"ps":X,"ir":X}}. p = the 25 largest 2026 cap numbers in the first active roster table (status "A"), plus every IR/PUP/NFI player at $2.5M+ (status "IR"/"PUP"/"NFI", base/bonus null if not shown). bonus26 = prorated signing + option bonus. cap27 = that player's 2027 cap number, or null. dead = 6 largest 2026 dead money entries. t = 2026 Offense/Defense/Special Teams/Practice Squad/IR totals. $M, 2 decimals. Return only the JSON.

Long pages can get cut off before the 2027 table, leaving every `cap27` null. If **all** `cap27` values come back null but the existing file had some, copy each player's old `cap27` by name. If the existing file has `"no27": true`, keep that flag.

## 5. Build, check, publish
```
python3 scripts/build.py      # data/ -> data.json -> public/index.html
python3 scripts/validate.py   # exit 0 = PASS
```
Set `data/meta.json` `asof` to today's date (America/New_York) before building.
- **PASS**: commit `data/`, `public/index.html` with message `Data refresh YYYY-MM-DD: <short summary>` and push to `main`.
- **FAIL**: do not push to `main`. Push the work to a branch `data-held-YYYY-MM-DD` instead, and report which checks failed.

## 6. Stop and ask a human when
- The NBA salary cap on JJNBA is no longer $164.96M (new season: constants in `src/app.html` need updating), or the OTC 2026 base cap is no longer $301.2M.
- A source changed its layout and the JSON can't be extracted.
- Validation fails two days in a row.

## 7. Report
End with a short summary: mode, teams refreshed, notable changes (e.g. a team crossing the tax line or an apron, a big release creating dead money), and PASS/FAIL. Notable changes are content ideas.
