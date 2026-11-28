"""Plain-English explainers for Cap Mechanics.

GLOSSARY holds short definitions of cap terms. Summaries mark terms with
<span class="term" data-term="key">, and the site shows the definition when a
reader taps the term. The same HTML goes into the live page and the crawlable
static page, so both always match.

nba_summary(team, T, asof) and nfl_summary(team, asof) return a list of
[label, html] rows for the "short version" card at the top of each team page.
Everything is computed from the team data, so it updates with every refresh.
"""
import html as H
from datetime import date

# key: (term, league, definition). league is "NBA", "NFL" or "Both".
GLOSSARY = {
    # ---------- NBA ----------
    "nba_cap": ("Salary cap (NBA)", "NBA",
                "The NBA's spending limit, $165.0M in 2026-27. It's a \"soft\" cap: teams can go over it to re-sign "
                "their own players, use exceptions and sign minimum contracts. Being under it is what gives a team "
                "cap space to sign outside free agents."),
    "tax": ("Luxury tax", "NBA",
            "A penalty on payrolls above $200.4M in 2026-27. Teams over the line at the end of the regular season pay "
            "a tax on every dollar above it, and the rate climbs the further over they are. The money goes to teams "
            "that stayed under."),
    "apron1": ("First apron", "NBA",
               "A spending line at $209.0M in 2026-27, above the tax. Teams over it lose tools: they can't take back "
               "more salary than they send out in trades, can't acquire players in sign-and-trades, and get a smaller "
               "mid-level exception."),
    "apron2": ("Second apron", "NBA",
               "The NBA's harshest line, $221.7M in 2026-27. Teams over it can't combine salaries in trades, can't "
               "use any mid-level exception or send cash in deals, and a first-round pick seven years out gets frozen "
               "if they finish the season above it."),
    "hard_cap": ("Hard cap (NBA)", "NBA",
                 "Some moves, like using the full mid-level exception or acquiring a player in a sign-and-trade, lock a "
                 "team under the first or second apron for the rest of the season. That apron becomes a hard ceiling "
                 "the team can't go over for any reason."),
    "repeater": ("Repeater tax", "NBA",
                 "Teams that paid the luxury tax in three of the previous four seasons pay much higher rates: an extra "
                 "$2 for every dollar over the line, in every tax bracket."),
    "mle": ("Mid-level exception (MLE)", "NBA",
            "A once-a-year allowance to sign a free agent even when over the cap. In 2026-27 it's worth up to $15.0M "
            "for teams below the first apron, $6.1M for teams above it, and nothing for teams above the second apron."),
    "bird": ("Bird rights", "NBA",
             "Lets a team re-sign its own free agents for any amount up to the max, even if it's over the cap. Named "
             "after Larry Bird. It's the main reason NBA payrolls blow past the cap."),
    "tpe": ("Trade exception (TPE)", "NBA",
            "Created when a team trades away more salary than it takes back. For up to a year, it lets the team "
            "absorb a player's salary in another trade, up to the exception's amount, without sending any salary back."),
    "bae": ("Bi-annual exception", "NBA",
            "A smaller signing allowance (about $5.5M) that teams below the first apron can use every other year to "
            "add a free agent while over the cap."),
    "ufa": ("Unrestricted free agent (UFA)", "NBA",
            "A player whose contract has ended and who can sign with any team. His old team gets no chance to match."),
    "rfa": ("Restricted free agent (RFA)", "NBA",
            "Usually a young player coming off his rookie deal. He can sign an offer sheet with any team, but his "
            "current team can match it and keep him."),
    "trade_kicker": ("Trade kicker", "NBA",
                     "A bonus written into some contracts that pays the player extra, up to 15% of the money left on "
                     "his deal, if he's traded. It can raise his salary for cap and trade-matching purposes."),
    "stretch": ("Stretch provision", "NBA",
                "When a team waives a player during the season, this season's salary stays on the cap as normal, but "
                "the money owed in later seasons can be spread evenly over twice the remaining years plus one. "
                "Expiring deals can't be stretched, and stretched money can't exceed 15% of the cap."),
    "expiring": ("Expiring contract", "NBA",
                 "A contract in its final season. It's valuable in trades: the acquiring team gets matching salary "
                 "now with no long-term commitment."),
    "cap_space_nba": ("Cap space (NBA)", "NBA",
                      "How far a team is under the $165.0M cap. Teams with space can sign outside free agents outright "
                      "or take on salary in trades without sending any back."),
    "salary_match": ("Salary matching", "NBA",
                     "Teams over the cap must send out salary to take salary back in a trade. Below the first apron "
                     "they can take back somewhat more than they send; above it, no more than they send."),
    # ---------- NFL ----------
    "nfl_cap": ("Salary cap (NFL)", "NFL",
                "The NFL's spending limit, $301.2M per team in 2026. It's a hard cap: every team must stay under it, "
                "with no exceptions and no tax to pay instead."),
    "cap_space": ("Cap space (NFL)", "NFL",
                  "How much room a team has left under its adjusted cap. That's what it can use to sign players, absorb "
                  "injury replacements or extend contracts this season."),
    "adjusted": ("Adjusted cap", "NFL",
                 "A team's actual spending limit for the year: the league-wide cap plus unused space rolled over from "
                 "last year and small league adjustments (such as incentive credits)."),
    "rollover": ("Rollover", "NFL",
                 "Unused cap space doesn't disappear. Teams can carry it into next season, raising next year's "
                 "adjusted cap by that amount."),
    "dead": ("Dead money", "NFL",
             "Cap charges for players who are no longer on the team. It's mostly signing-bonus money already paid "
             "out that still has to be counted on the cap after a player is released or traded."),
    "prorated": ("Prorated bonus", "NFL",
                 "A signing bonus is paid up front but counted on the cap evenly over up to five years of the contract. "
                 "Whatever hasn't been counted yet becomes dead money if the player leaves early."),
    "restructure": ("Restructure", "NFL",
                    "Turning part of a player's salary into a signing bonus. It lowers this year's cap hit by "
                    "spreading the money over future years, which creates room now but pushes costs (and potential "
                    "dead money) into later seasons."),
    "eff_space": ("Effective cap space", "NFL",
                  "Cap space after setting money aside to fill out a full roster with minimum-salary players. A "
                  "truer measure of what a team can actually spend on free agents."),
    "cap_hit": ("Cap hit", "Both",
                "How much a player's contract counts against the cap in a given season. In the NFL it's salary plus "
                "the year's share of bonuses, so it can differ a lot from the cash he's paid."),
    "ir": ("Injured reserve (IR)", "NFL",
           "A list for injured players who are out for an extended period. Their contracts still count against the "
           "cap while they're on it."),
}

NBA_DEADLINE = date(2027, 2, 11)


def g(key, text=None):
    """Mark a term so the site can explain it on tap."""
    assert key in GLOSSARY, key
    return f'<span class="term" data-term="{key}" tabindex="0" role="button">{text or GLOSSARY[key][0]}</span>'


def m(v, d=1):
    return ("−$" if v < 0 else "$") + f"{abs(v):.{d}f}M"


def ordinal(n):
    return f"{n}{'th' if 10 < n % 100 < 14 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def nick(name):
    w = name.split()
    return " ".join(w[-2:]) if len(w) > 2 and w[-2] in ("Trail", "Red") else w[-1]


def poss(name):
    return H.escape(name) + ("'" if name.endswith("s") else "'s")


def _nba_tool(exc, room=None):
    """Plain-English version of the team's biggest available exception, or None."""
    import re
    if not exc:
        return None
    mm = re.search(r"largest an? \$([\d.]+)M (.+)$", exc)
    if mm:
        amt, kind = float(mm.group(1)), mm.group(2)
    else:
        mm = re.match(r"(.+?), \$([\d.]+)M?$", exc)
        if not mm:
            return None
        kind, amt = mm.group(1), float(mm.group(2))
    if amt < 3:
        return None
    cav = (f" (though the hard cap lets them use only about {m(room)} of it)"
           if room is not None and amt > room + 0.5 else "")
    tpe = re.search(r"TPE(?: \((.+)\))?", kind)
    if tpe:
        src = f" from the {H.escape(tpe.group(1))} trade" if tpe.group(1) else ""
        return (f"Their biggest tool for adding talent is a {m(amt)} {g('tpe', 'trade exception')}{src}{cav}, which lets "
                "them take in a player's salary without sending any back.")
    if "Bi-Annual" in kind:
        return f"They still have a {m(amt)} {g('bae', 'bi-annual exception')}{cav} to sign a free agent."
    if "Mid-Level" in kind or "MLE" in kind:
        return f"They still have {m(amt)} of {g('mle', 'mid-level exception')} money{cav} to sign a free agent."
    return None


def _nba_tax(p, T, rep):
    over, bill, i = p - T["tax"], 0.0, 0
    base = [3, 3.25, 5.5, 6.75] if rep else [1, 1.25, 3.5, 4.75]
    while over > 1e-9:
        rate = base[i] if i < 4 else base[3] + 0.5 * (i - 3)
        amt = min(over, T["bracket"])
        bill += amt * rate
        over -= amt
        i += 1
    return bill


def nba_summary(t, T, asof, rank):
    """rank: payroll rank, 1 = highest."""
    p, nm, rep = t["tp"], H.escape(nick(t["name"])), t.get("rep")
    hc = {"a1": T["a1"], "a2": T["a2"]}.get((t.get("hc") or {}).get("level"))
    rank_txt = "the biggest payroll in the NBA" if rank == 1 else (
        "the smallest payroll in the NBA" if rank == 30 else f"the {ordinal(rank)}-biggest payroll of 30 teams")

    # 1. Where they stand
    if p < T["cap"]:
        stand = (f"The {nm} are {m(T['cap'] - p)} under the {g('nba_cap', 'salary cap')}, one of the few teams with real "
                 f"{g('cap_space_nba', 'cap space')}. It's {rank_txt}.")
    elif p < T["tax"]:
        stand = (f"The {nm} are over the {g('nba_cap', 'salary cap')} but {m(T['tax'] - p)} under the "
                 f"{g('tax', 'luxury tax')}, the comfortable middle where they pay no penalty. It's {rank_txt}.")
    elif p < T["a1"]:
        stand = (f"The {nm} are {m(p - T['tax'])} into the {g('tax', 'luxury tax')} and {m(T['a1'] - p)} below the "
                 f"{g('apron1', 'first apron')}. It's {rank_txt}.")
    elif p < T["a2"]:
        stand = (f"The {nm} are {m(p - T['a1'])} over the {g('apron1', 'first apron')} and {m(T['a2'] - p)} below the "
                 f"{g('apron2', 'second apron')}. It's {rank_txt}.")
    else:
        stand = (f"The {nm} are {m(p - T['a2'])} over the {g('apron2', 'second apron')}, the most restrictive "
                 f"spending tier in the league. It's {rank_txt}.")

    # 2. What it means
    means = []
    if hc:
        room = hc - p
        which = "first" if hc == T["a1"] else "second"
        if room < 1.3:
            tail = f"leaving just {m(room, 2)}: not enough to add even a minimum contract without sending salary out"
        elif room < 4:
            tail = f"leaving just {m(room)} of room, enough for little more than minimum contracts"
        else:
            tail = f"which leaves {m(room)} of room for the rest of the season"
        means.append(f"They're {g('hard_cap', 'hard-capped')} at the {which} apron ({m(hc)}), {tail}.")
    bill = _nba_tax(p, T, rep) if p > T["tax"] else 0
    if bill:
        means.append(f"If nothing changes, they'll owe about <b>{m(bill)}</b> in {g('tax', 'luxury tax')}, on top of "
                     f"salaries{', at the steeper ' + g('repeater', 'repeater') + ' rates' if rep else ''}.")
    if p < T["cap"]:
        means.append("They can sign free agents outright or absorb a contract in a trade without sending salary back.")
    elif p < T["tax"]:
        means.append("Staying under the tax means no penalty, plus a share of the tax money other teams pay.")
    elif p < T["a1"]:
        means.append("Every dollar they add now costs extra in tax, so even small signings get expensive.")
    elif p < T["a2"]:
        means.append(f"Above the first apron, {g('salary_match', 'trades')} are tighter: they can't take back more "
                     "salary than they send out.")
    else:
        means.append(f"They can't combine salaries in trades or use any {g('mle', 'mid-level exception')}, and a "
                     "future first-round pick gets frozen if they're still here at season's end.")

    tool = _nba_tool(t.get("exc"), (hc - p) if hc else None)
    if tool and p >= T["cap"] and len(means) < 3:
        means.append(tool)

    # 3. What to watch
    watch = []
    before_deadline = date.fromisoformat(asof) < NBA_DEADLINE
    if bill and p - T["tax"] <= 15:
        watch.append(f"Cutting {m(p - T['tax'])} before the end of the regular season would wipe out the tax bill "
                     "entirely.")
    exp = sorted((r for r in t["p"] if r[4] is None and (r[3] or 0) >= 8), key=lambda r: -r[3])
    if exp and before_deadline:
        r = exp[0]
        watch.append(f"{poss(r[0])} {m(r[3])} {g('expiring', 'expiring contract')} is their biggest trade chip "
                     f"before the Feb. 11 deadline.")
    if p < T["cap"] and T["cap"] - p >= 5:
        watch.append("That room makes them a natural landing spot for teams looking to dump salary.")
    if not watch:
        top = max(t["p"], key=lambda r: r[3] or 0)
        watch.append(f"{H.escape(top[0])} is their biggest contract at {m(top[3])}, {top[3] / p * 100:.0f}% of the "
                     f"payroll.")
    return [["Where they stand", stand], ["What it means", " ".join(means)], ["What to watch", " ".join(watch[:2])]]


def nfl_summary(t, rank, rank27):
    """rank: 2026 cap-space rank (1 = most); rank27: 2027 effective-space rank."""
    nm = H.escape(nick(t["name"]))
    sp, dead, adj = t["space"], t["dead"], t["adj"]

    if sp < 8:
        feel = (f"That's tight: adding anyone now means releasing or {g('restructure', 'restructuring')} "
                "someone first.")
    elif sp < 25:
        feel = f"That covers injury signings, and whatever's left {g('rollover', 'rolls over')} into 2027."
    else:
        feel = f"That's plenty of room, and whatever goes unused {g('rollover', 'rolls over')} into 2027."
    stand = (f"The {nm} have <b>{m(sp)}</b> in {g('cap_space', 'cap space')}, {ordinal(rank)} of 32 teams. {feel}")

    pct = dead / adj * 100
    dl = sorted(t.get("deadList", []), key=lambda r: -r[1])
    lead = f", led by {H.escape(dl[0][0])} ({m(dl[0][1])})" if dl and dl[0][1] >= 3 else ""
    if pct >= 20:
        dead_txt = (f"{m(dead)}, <b>{pct:.0f}% of their cap</b>, is {g('dead', 'dead money')} for players no longer "
                    f"on the team{lead}. That's money spent on nobody who will play for them this year.")
    elif pct >= 10:
        dead_txt = (f"{m(dead)} ({pct:.0f}% of their cap) is {g('dead', 'dead money')} for players no longer on the "
                    f"team{lead}. That's a noticeable drag.")
    else:
        dead_txt = (f"Only {m(dead)} is {g('dead', 'dead money')}, so nearly all of their cap goes to players "
                    f"actually on the roster.")

    e27 = t["eff27"]
    if e27 < 0:
        ahead = (f"2027 is a squeeze: they're projected {m(-e27)} short once a full roster is counted. Expect "
                 f"{g('restructure', 'restructures')}, extensions or cuts before free agency opens in March.")
    elif e27 >= 50:
        ahead = (f"2027 looks wide open, with about {m(e27)} of {g('eff_space', 'effective cap space')} "
                 f"({ordinal(rank27)} in the league). Expect them to be big free-agency spenders.")
    elif e27 >= 15:
        ahead = (f"They project about {m(e27)} of {g('eff_space', 'effective cap space')} for 2027 "
                 f"({ordinal(rank27)} of 32): workable, not lavish.")
    else:
        ahead = (f"They project only about {m(e27)} of {g('eff_space', 'effective cap space')} for 2027 "
                 f"({ordinal(rank27)} of 32), so they'll need to clear room to make a big free-agent splash.")
    return [["Where they stand", stand], ["Dead money", dead_txt], ["Looking ahead", ahead]]


NBA_YRS = ["2026-27", "2027-28", "2028-29", "2029-30", "2030-31"]


def pslug(name):
    import unicodedata, re
    a = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", a).strip("-")


def match_in(o, M):
    """Most salary a team below the first apron can take back for o outgoing (2023 CBA bands)."""
    return 2 * o + 0.25 if o <= M["t1"] else (o + M["t1"] if o <= M["t2"] else 1.25 * o + 0.25)


def min_out(S, M):
    lo, hi = 0.0, S
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if match_in(mid, M) >= S else (mid, hi)
    return hi


def nba_player_summary(pl, t, T, M, n_players):
    s, nm = pl["s"], H.escape(pl["n"])
    last = H.escape(pl["n"].split()[-1] if pl["n"].split()[-1] not in ("Jr.", "Jr", "II", "III", "IV") else pl["n"].split()[-2])
    yrs = [i for i, v in enumerate(s) if v is not None]
    n_yrs, total = len(yrs), sum(v for v in s if v is not None)
    end = NBA_YRS[yrs[-1]]
    fa_year = 2027 + yrs[-1]
    fa_t = {"UFA": g("ufa", "an unrestricted free agent"), "RFA": g("rfa", "a restricted free agent")}.get(
        pl.get("fa"), "a free agent")
    if n_yrs == 1:
        deal = (f"{nm} is on an {g('expiring', 'expiring contract')}: {m(s[0])} this season, then he becomes "
                f"{fa_t} in summer {fa_year}.")
    else:
        deal = (f"{nm} is owed {m(total)} over {n_yrs} seasons, running through {end}. He becomes {fa_t} in "
                f"summer {fa_year}.")
    if pl.get("kick"):
        deal += f" His deal includes a {pl['kick']:g}% {g('trade_kicker', 'trade kicker')}."
    rk = pl["rank"]
    rank_txt = ("the biggest salary in the NBA" if rk == 1 else
                f"the {ordinal(rk)}-highest salary of the {n_players} NBA players under contract")
    impact = (f"{m(s[0])} this season is {s[0] / T['cap'] * 100:.1f}% of the {g('nba_cap', 'salary cap')} and "
              f"{s[0] / t['tp'] * 100:.0f}% of the {poss(nick(t['name']))} payroll: {rank_txt}.")
    S = s[0]
    if S < 3:
        trade = (f"At {m(S)}, he's easy to move: almost any team can fit him with a minimum-sized salary going back.")
    else:
        o = min_out(S, M)
        trade = (f"A team over the cap but below the {g('apron1', 'first apron')} would need to send out at least "
                 f"{m(o)} in salary to take him in. Above the first apron, it's dollar for dollar: at least {m(S)}.")
    return [["The deal", deal], ["Cap impact", impact], ["Trade math", trade]]


def nba_players(data, T, M):
    rows = []
    for t in data["nba"]:
        for r in t["p"]:
            if r[3] is None:
                continue
            rows.append({"n": r[0], "tid": t["id"], "pos": r[1], "age": r[2], "s": r[3:8],
                         "fa": t.get("fa", {}).get(r[0]), "kick": t.get("kick", {}).get(r[0])})
    rows.sort(key=lambda p: -p["s"][0])
    seen = {}
    for i, p in enumerate(rows):
        p["rank"] = i + 1
        sl = pslug(p["n"])
        if sl in seen:
            sl = f"{sl}-{p['tid'].lower()}"
        seen[sl] = 1
        p["slug"] = sl
    by_id = {t["id"]: t for t in data["nba"]}
    for p in rows:
        p["sum"] = nba_player_summary(p, by_id[p["tid"]], T, M, len(rows))
    return rows


def add_explainers(data, T, M=None):
    """Attach summaries and the glossary to the site data."""
    nba_rank = {t["id"]: i + 1 for i, t in enumerate(sorted(data["nba"], key=lambda t: -t["tp"]))}
    nfl_rank = {t["id"]: i + 1 for i, t in enumerate(sorted(data["nfl"], key=lambda t: -t["space"]))}
    nfl_rank27 = {t["id"]: i + 1 for i, t in enumerate(sorted(data["nfl"], key=lambda t: -t["eff27"]))}
    for t in data["nba"]:
        t["sum"] = nba_summary(t, T, data["asof"], nba_rank[t["id"]])
    for t in data["nfl"]:
        t["sum"] = nfl_summary(t, nfl_rank[t["id"]], nfl_rank27[t["id"]])
    if M:
        data["nbaPlayers"] = nba_players(data, T, M)
    data["glossary"] = {k: list(v) for k, v in GLOSSARY.items()}
    return data
