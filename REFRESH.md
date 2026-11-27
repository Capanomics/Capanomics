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
> Extract this page's salary data as one line of minified JSON in this shape: {"p":[[name,cap26,base26,bonus26,cap27,status],...],"dead":[[name,amt],...],"t":{"off":X,"def":X,"st":X,"ps":X,"ir":X}}. p = the 25 largest 2026 cap numbers in the first active roster table (status "A"), plus every IR/PUP/NFI player at $2.5M+ (status "IR"/"PUP"/"NFI", base/bonus null if not shown). bonus26 = prorated signing + option bonus. cap27 = that player's 2027 cap number, or null. dead = every 2026 dead money entry. t = 2026 Offense/Defense/Special Teams/Practice Squad/IR totals. $M, 2 decimals. Return only the JSON.

Long pages can get cut off before the 2027 table, leaving every `cap27` null. If **all** `cap27` values come back null but the existing file had some, copy each player's old `cap27` by name. If the existing file has `"no27": true`, keep that flag.

**OTC pages are longer than one fetch.** Team pages run ~95–115k characters; WebFetch returns only the first ~40k as verbatim text and replaces the rest with a model-written summary, which has mixed 2027 figures into 2026. So read each NFL team page in two passes and never take the active roster from the summary:
1. **Active roster pass** (verbatim only). Prompt:
   > Using ONLY text you can read verbatim (not a model summary), output one line of minified JSON: {"hdr_space":2026_cap_space_in_page_header_M,"p":[[name,cap26,base26,bonus26,null,"A"],...],"t":{"off":X,"def":X,"st":X}}. p = the 25 largest cap numbers in the first (2026) Active Roster table. bonus26 = Signing + Option prorated columns. $M, 2 decimals.
2. **Lower sections pass** (narrow prompt; these come from the summary). Prompt:
   > 2026 season only, figures exactly as printed. Output one line of minified JSON: {"dead":[[name,amt],...],"dead_total":X,"ir":[[name,cap26,status],...],"ir_total":X,"ps_total":X}. dead = every Dead Money row plus the printed table total. ir = every Injured Reserve/PUP/NFI player with status "IR"/"PUP"/"NFI", plus the printed Injured Reserve total. $M, 2 decimals.

Build the file from both: `p` = active rows (cap27 copied from the existing file by name, ignoring punctuation such as "DK"/"D.K.") + IR/PUP/NFI rows at $2.5M+ (base/bonus null); `dead` = **every** dead-money entry, largest first (the site lists them all); `t` = off/def/st from pass 1, ps/ir from pass 2.

**Cross-check before writing:** the pass-2 `dead_total` should match that team's dead money in the cap-space table (step 3) within $0.1M, and the IR rows should sum to `ir_total`. If a team page matches **yesterday's** dead money instead, OTC's team page hasn't caught up with its league table yet: write it anyway and note it in the report (it usually corrects on the next run). If it matches neither, or pass 1 can't be read verbatim, keep that team's existing file and list it in the report. If more than 3 changed teams fail this way, treat it as a broken source layout (section 6).

**Dead-money backfill (every mode, including quick check).** After step 3, for each NFL team where the `dead` entries in `data/nfl/<TEAM>.json` sum to more than $0.5M below `dead` in `_league.json`, run **pass 2 only** for that team, largest shortfall first, every such team in the same run. **Skip a team whose file has `dead_src` within $0.1M of its current `dead` in `_league.json`**: its list was already filled against that total, and Over The Cap doesn't itemize the smallest charges, so re-reading it won't close the gap. Replace only the file's `dead` list, and only if the new rows sum to no more than `dead_total` + $0.1M and to more than the existing rows; otherwise leave the list alone. Either way, set the file's `dead_src` to that team's current `_league.json` `dead`, so the team is retried only after its total changes. Keep `p` and `t` untouched in this step. The site shows any remaining gap as "Not itemized yet", so a partial list is fine. Mention in the report how many teams were backfilled and how many still have gaps.

## 5. Build, check, publish
```
python3 scripts/build.py      # data/ -> data.json -> public/ (one page per team)
python3 scripts/validate.py   # exit 0 = PASS
```
Set `data/meta.json` `asof` to today's date (America/New_York) before building.
- **PASS**: commit `data/` and `public/` (all generated pages, sitemap.xml, robots.txt) with message `Data refresh YYYY-MM-DD: <short summary>` and push to `main`.
- **FAIL**: do not push to `main`. Push the work to a branch `data-held-YYYY-MM-DD` instead, and report which checks failed.

## 6. Stop and ask a human when
- The NBA salary cap on JJNBA is no longer $164.96M (new season: constants in `src/app.html` need updating), or the OTC 2026 base cap is no longer $301.2M.
- A source changed its layout and the JSON can't be extracted.
- Validation fails two days in a row.

## 7. Report
End with a short summary: mode, teams refreshed, notable changes (e.g. a team crossing the tax line or an apron, a big release creating dead money), and PASS/FAIL. Notable changes are content ideas.
