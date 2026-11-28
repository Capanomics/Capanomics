"""Combine per-team data files into data.json for the site.

Inputs (all under data/):
  meta.json               {"asof": "YYYY-MM-DD", ...}
  nba/<TEAM>.json         roster + tax payroll per NBA team (source: JJNBA team pages)
  nba/_hardcaps.json      hard-cap level and reason per NBA team
  nfl/<TEAM>.json         top cap hits, dead money, unit totals per NFL team (source: Over The Cap team pages)
  nfl/_league.json        team-level 2026/2027 cap space numbers (source: Over The Cap cap-space page)
"""
import json, os, sys
root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(root, "data")
load = lambda *p: json.load(open(os.path.join(D, *p)))

NBA_META = [("ATL","Atlanta Hawks","East","Southeast",0),("BOS","Boston Celtics","East","Atlantic",1),("BKN","Brooklyn Nets","East","Atlantic",0),("CHA","Charlotte Hornets","East","Southeast",0),("CHI","Chicago Bulls","East","Central",0),("CLE","Cleveland Cavaliers","East","Central",0),("DAL","Dallas Mavericks","West","Southwest",0),("DEN","Denver Nuggets","West","Northwest",1),("DET","Detroit Pistons","East","Central",0),("GSW","Golden State Warriors","West","Pacific",1),("HOU","Houston Rockets","West","Southwest",0),("IND","Indiana Pacers","East","Central",0),("LAC","LA Clippers","West","Pacific",1),("LAL","Los Angeles Lakers","West","Pacific",1),("MEM","Memphis Grizzlies","West","Southwest",0),("MIA","Miami Heat","East","Southeast",0),("MIL","Milwaukee Bucks","East","Central",1),("MIN","Minnesota Timberwolves","West","Northwest",0),("NOP","New Orleans Pelicans","West","Southwest",0),("NYK","New York Knicks","East","Atlantic",0),("OKC","Oklahoma City Thunder","West","Northwest",0),("ORL","Orlando Magic","East","Southeast",0),("PHI","Philadelphia 76ers","East","Atlantic",0),("PHX","Phoenix Suns","West","Pacific",1),("POR","Portland Trail Blazers","West","Northwest",0),("SAC","Sacramento Kings","West","Pacific",0),("SAS","San Antonio Spurs","West","Southwest",0),("TOR","Toronto Raptors","East","Atlantic",0),("UTA","Utah Jazz","West","Northwest",0),("WAS","Washington Wizards","East","Southeast",0)]
NFL_META = [("ARI","Arizona Cardinals","NFC","West"),("ATL","Atlanta Falcons","NFC","South"),("BAL","Baltimore Ravens","AFC","North"),("BUF","Buffalo Bills","AFC","East"),("CAR","Carolina Panthers","NFC","South"),("CHI","Chicago Bears","NFC","North"),("CIN","Cincinnati Bengals","AFC","North"),("CLE","Cleveland Browns","AFC","North"),("DAL","Dallas Cowboys","NFC","East"),("DEN","Denver Broncos","AFC","West"),("DET","Detroit Lions","NFC","North"),("GB","Green Bay Packers","NFC","North"),("HOU","Houston Texans","AFC","South"),("IND","Indianapolis Colts","AFC","South"),("JAX","Jacksonville Jaguars","AFC","South"),("KC","Kansas City Chiefs","AFC","West"),("LV","Las Vegas Raiders","AFC","West"),("LAC","Los Angeles Chargers","AFC","West"),("LAR","Los Angeles Rams","NFC","West"),("MIA","Miami Dolphins","AFC","East"),("MIN","Minnesota Vikings","NFC","North"),("NE","New England Patriots","AFC","East"),("NO","New Orleans Saints","NFC","South"),("NYG","New York Giants","NFC","East"),("NYJ","New York Jets","AFC","East"),("PHI","Philadelphia Eagles","NFC","East"),("PIT","Pittsburgh Steelers","AFC","North"),("SF","San Francisco 49ers","NFC","West"),("SEA","Seattle Seahawks","NFC","West"),("TB","Tampa Bay Buccaneers","NFC","South"),("TEN","Tennessee Titans","AFC","South"),("WAS","Washington Commanders","NFC","East")]

meta = load("meta.json"); hc = load("nba", "_hardcaps.json"); lg = load("nfl", "_league.json")
nba = []
for id, name, conf, div, rep in NBA_META:
    d = load("nba", id + ".json")
    nba.append({"id": id, "name": name, "conf": conf, "div": div, "rep": bool(rep), "tp": d["tp"], "p": d["p"], "tw": d["tw"], "exc": d["exc"], "dead": d["dead"], "hc": hc[id], "fa": d.get("fa", {}), "kick": d.get("kick", {})})
nfl = []
for id, name, conf, div in NFL_META:
    d = load("nfl", id + ".json"); L = lg[id]
    nfl.append({"id": id, "name": name, "conf": conf, "div": conf + " " + div, "space": L["space"], "active": L["active"], "dead": L["dead"], "n": L["n"],
                "space27": L["space27"], "eff27": L["eff27"], "active27": L["active27"], "dead27": L["dead27"], "n27": L["n27"],
                "adj": round(L["space"] + L["active"] + L["dead"], 3), "p": d["p"], "deadList": d["dead"], "t": d["t"], "no27": d.get("no27", False)})
out = {"asof": meta["asof"], "nba": sorted(nba, key=lambda t: t["name"]), "nfl": sorted(nfl, key=lambda t: t["name"])}
cp = os.path.join(root, "data", "nba", "_careers.json")
out["careers"] = json.load(open(cp)) if os.path.exists(cp) else {}
import glob as _g
out["nflPlayerData"] = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(_g.glob(os.path.join(root, "data", "nfl", "players", "[A-Z]*.json")))}
json.dump(out, open(os.path.join(root, "data.json"), "w"), separators=(",", ":"), ensure_ascii=False)
print("data.json", os.path.getsize(os.path.join(root, "data.json")), "bytes, asof", meta["asof"])
