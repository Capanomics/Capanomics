"""Safety checks run before any data update is published. Exit code 1 = do not publish.

Compares the working data against the last published data.json (git HEAD) and checks internal consistency.
"""
import json, os, subprocess, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors, warnings = [], []
new = json.load(open(os.path.join(root, "data.json")))
try:
    old = json.loads(subprocess.run(["git", "-C", root, "show", "HEAD:public/index.html"], capture_output=True, text=True, check=True).stdout.split("const DATA = ", 1)[1].split(";\n", 1)[0])
except Exception:
    old = None; warnings.append("No previously published data found; skipping change checks.")

if len(new["nba"]) != 30: errors.append(f"NBA team count is {len(new['nba'])}, expected 30")
if len(new["nfl"]) != 32: errors.append(f"NFL team count is {len(new['nfl'])}, expected 32")

for t in new["nba"]:
    s = sum(p[3] for p in t["p"]) + sum(d[1] for d in t["dead"])
    if abs(s - t["tp"]) > 2.0: errors.append(f"NBA {t['id']}: player salaries + dead money = {s:.2f}M but payroll is {t['tp']:.2f}M")
    if not 13 <= len(t["p"]) <= 16: warnings.append(f"NBA {t['id']}: {len(t['p'])} standard contracts")
    if not 100 < t["tp"] < 300: errors.append(f"NBA {t['id']}: implausible payroll {t['tp']}")
    if t["hc"]["level"] not in ("a1", "a2", "none"): errors.append(f"NBA {t['id']}: bad hard-cap level")

for t in new["nfl"]:
    if not 250 < t["adj"] < 400: errors.append(f"NFL {t['id']}: implausible adjusted cap {t['adj']}")
    if t["space"] < -5: errors.append(f"NFL {t['id']}: cap space {t['space']} is impossible in-season")
    if len(t["p"]) < 15: errors.append(f"NFL {t['id']}: only {len(t['p'])} players listed")
    top = max(p[1] for p in t["p"])
    if top > 0.25 * 301.2: errors.append(f"NFL {t['id']}: cap hit {top} looks wrong")

if old:
    o = {("nba", t["id"]): t for t in old["nba"]} | {("nfl", t["id"]): t for t in old["nfl"]}
    for t in new["nba"]:
        d = t["tp"] - o[("nba", t["id"])]["tp"]
        if abs(d) > 40: errors.append(f"NBA {t['id']}: payroll moved {d:+.1f}M in one update; needs a human look")
        elif abs(d) > 0.05: warnings.append(f"NBA {t['id']}: payroll {d:+.2f}M")
    for t in new["nfl"]:
        d = t["space"] - o[("nfl", t["id"])]["space"]
        if abs(d) > 60: errors.append(f"NFL {t['id']}: cap space moved {d:+.1f}M in one update; needs a human look")
        elif abs(d) > 0.05: warnings.append(f"NFL {t['id']}: cap space {d:+.2f}M")

for w in warnings: print("note:", w)
for e in errors: print("ERROR:", e)
print("RESULT:", "FAIL" if errors else "PASS")
sys.exit(1 if errors else 0)
