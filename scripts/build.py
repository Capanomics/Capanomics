"""Build the static site.

Combines team data into data.json, inlines it into src/app.html, and writes one real
HTML file per page so every team has its own URL (e.g. /nfl/miami-dolphins) with its
own title, description and crawlable summary for search engines:

  public/index.html                  home
  public/nba/index.html, nfl/...     league pages
  public/trade.html, deadline.html, compare.html
  public/nba/<team-slug>.html        30 NBA team pages
  public/nfl/<team-slug>.html        32 NFL team pages
  public/404.html, sitemap.xml, robots.txt

The JavaScript app takes over on load and handles navigation without page reloads.
"""
import html as H, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.capmechanics.com"
PUB = os.path.join(ROOT, "public")

subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_data.py"), ROOT], check=True)
app = open(os.path.join(ROOT, "src", "app.html")).read()
data_txt = open(os.path.join(ROOT, "data.json")).read()
DATA = json.loads(data_txt)
app = app.replace("__DATA__", data_txt.replace("</", "<\\/"), 1)
T = dict(re.findall(r"(\w+):([\d.]+)", re.search(r"const NBA_T = \{([^}]*)\}", app).group(1)))
T = {k: float(v) for k, v in T.items()}
DEFAULT_TITLE = "Cap Mechanics — NBA &amp; NFL Salary Cap Explorer"
assert f"<title>{DEFAULT_TITLE}</title>" in app


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def m(v):
    if v is None:
        return "—"
    return ("−$" if v < 0 else "$") + f"{abs(v):.1f}M"


def nba_tier(p):
    if p < T["cap"]:
        return "under the salary cap"
    if p < T["tax"]:
        return "over the cap but under the luxury tax"
    if p < T["a1"]:
        return "a luxury-tax team"
    if p < T["a2"]:
        return "above the first apron"
    return "above the second apron"


def page(path, title, desc, body_html):
    url = SITE + ("/" if path == "/" else path)
    t, d = H.escape(title), H.escape(desc)
    head = (f"<title>{t}</title>\n<meta name=\"description\" content=\"{d}\">\n"
            f"<link rel=\"canonical\" href=\"{url}\">\n"
            f"<meta property=\"og:title\" content=\"{t}\">\n<meta property=\"og:description\" content=\"{d}\">\n"
            f"<meta property=\"og:url\" content=\"{url}\">\n<meta property=\"og:type\" content=\"website\">\n"
            f"<meta name=\"twitter:card\" content=\"summary\">")
    out = app.replace(f"<title>{DEFAULT_TITLE}</title>", head, 1)
    # Crawlable summary inside #app; the app replaces it on load.
    out = out.replace('<main class="wrap" id="app"></main>', f'<main class="wrap" id="app">{body_html}</main>', 1)
    return out


def write(rel, content):
    f = os.path.join(PUB, rel)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w").write(content)


def ul(rows):
    return "<ul>" + "".join(f"<li>{r}</li>" for r in rows) + "</ul>"


asof = DATA["asof"]
pages = []  # (path, title, desc, body, file)

# Home and section pages
pages.append(("/", "Cap Mechanics — NBA & NFL Salary Cap Explorer",
              "Every NBA and NFL team's salary cap situation, contracts, cap space, luxury tax and dead money, plus an NBA trade machine and deadline tracker.",
              f"<h1>NBA &amp; NFL salary cap explorer</h1><p>Cap sheets for all 30 NBA and 32 NFL teams, updated {asof}.</p>", "index.html"))
nba_links = ul(f'<a href="/nba/{slug(t["name"])}">{H.escape(t["name"])} salary cap</a> — {m(t["tp"])} payroll' for t in DATA["nba"])
nfl_links = ul(f'<a href="/nfl/{slug(t["name"])}">{H.escape(t["name"])} salary cap</a> — {m(t["space"])} 2026 cap space' for t in DATA["nfl"])
pages.append(("/nba", "NBA Salary Cap 2026-27: All 30 Team Payrolls — Cap Mechanics",
              f"2026-27 NBA payrolls for all 30 teams vs the ${T['cap']:.1f}M salary cap, ${T['tax']:.1f}M luxury tax and both aprons. Updated {asof}.",
              f"<h1>NBA salary cap 2026-27</h1>{nba_links}", "nba/index.html"))
pages.append(("/nfl", "NFL Salary Cap 2026: All 32 Teams' Cap Space — Cap Mechanics",
              f"2026 NFL cap space, active cap spending and dead money for all 32 teams, plus 2027 projections. Updated {asof}.",
              f"<h1>NFL salary cap 2026</h1>{nfl_links}", "nfl/index.html"))
pages.append(("/trade", "NBA Trade Machine 2026-27 — Cap Mechanics",
              "Check whether an NBA trade works under the 2026-27 CBA salary-matching and apron rules.", "<h1>NBA trade machine</h1>", "trade.html"))
pages.append(("/deadline", "NBA Trade Deadline Tracker 2027 — Cap Mechanics",
              "Countdown and cap context for the NBA trade deadline.", "<h1>NBA trade deadline tracker</h1>", "deadline.html"))
pages.append(("/compare", "NBA vs NFL Salary Cap Compared — Cap Mechanics",
              "How the NBA's soft cap and luxury tax compare with the NFL's hard cap.", "<h1>NBA vs NFL salary cap</h1>", "compare.html"))

for t in DATA["nba"]:
    s, n = slug(t["name"]), t["name"]
    top = sorted(t["p"], key=lambda r: -(r[3] or 0))[:5]
    desc = (f"{n} salary cap 2026-27: {m(t['tp'])} payroll, {nba_tier(t['tp'])}. "
            f"Contracts, luxury tax, apron and hard-cap status. Updated {asof}.")
    body = (f"<h1>{H.escape(n)} salary cap 2026-27</h1>"
            f"<p>The {H.escape(n)} have a 2026-27 payroll of {m(t['tp'])}, {nba_tier(t['tp'])} "
            f"(cap {m(T['cap'])}, tax line {m(T['tax'])}). Data as of {asof}.</p>"
            "<h2>Biggest contracts</h2>" + ul(f"{H.escape(r[0])} — {m(r[3])}" for r in top))
    pages.append((f"/nba/{s}", f"{n} Salary Cap 2026-27 — Payroll & Contracts | Cap Mechanics", desc, body, f"nba/{s}.html"))

for t in DATA["nfl"]:
    s, n = slug(t["name"]), t["name"]
    top = [r for r in t["p"] if r[5] == "A"][:5]
    desc = (f"{n} salary cap 2026: {m(t['space'])} cap space, {m(t['dead'])} dead money, "
            f"{m(t.get('space27'))} projected 2027 space. Player cap hits and dead money. Updated {asof}.")
    body = (f"<h1>{H.escape(n)} salary cap 2026</h1>"
            f"<p>The {H.escape(n)} have {m(t['space'])} in 2026 cap space, {m(t['active'])} in active contracts "
            f"and {m(t['dead'])} in dead money. Projected 2027 cap space: {m(t.get('space27'))}. Data as of {asof}.</p>"
            "<h2>Biggest cap hits</h2>" + ul(f"{H.escape(r[0])} — {m(r[1])}" for r in top) +
            "<h2>Largest dead money</h2>" + ul(f"{H.escape(r[0])} — {m(r[1])}" for r in sorted(t.get("deadList", []), key=lambda r: -r[1])[:5]))
    pages.append((f"/nfl/{s}", f"{n} Salary Cap 2026 — Cap Space & Dead Money | Cap Mechanics", desc, body, f"nfl/{s}.html"))

for path, title, desc, body, rel in pages:
    write(rel, page(path, title, desc, body))
# Unknown URLs fall back to the home view.
p404 = page("/", "Page not found — Cap Mechanics", "Page not found.", "<h1>Page not found</h1>")
p404 = p404.replace('<link rel="canonical" href="https://www.capmechanics.com/">', '<meta name="robots" content="noindex">', 1)
assert 'noindex' in p404
write("404.html", p404)
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{SITE}{'/' if p[0] == '/' else p[0]}</loc><lastmod>{asof}</lastmod></url>\n" for p in pages)
      + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print(f"built {len(pages)} pages into public/ (+404, sitemap.xml, robots.txt)")
