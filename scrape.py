"""Reads the GiveSendGo campaign page and writes data.json for the thermometer overlay.
Runs on a schedule in GitHub Actions. Keeps the previous figure if the page can't be read."""
import json, re, sys, datetime
from playwright.sync_api import sync_playwright

URL = "https://www.givesendgo.com/stand-with-nolan-wells-targeted-friends"
OUT = "data.json"

def parse(text, prev_goal=250000):
    t = re.sub(r"\s+", " ", text)
    low = t.lower()
    def nearest(pos, kw):
        best = float("inf")
        for k in re.finditer(kw, low):
            best = min(best, abs(k.start() - pos))
        return best
    hits = []
    for m in re.finditer(r"\$\s?(\d{1,3}(?:,\d{3})+|\d{3,})(?:\.\d{2})?", t):
        val = int(m.group(1).replace(",", ""))
        dr, dg = nearest(m.start(), r"raised|donated|collected"), nearest(m.start(), r"goal|target")
        hits.append((val, dr < 90 and dr <= dg, dg < 90 and dg < dr))
    if not hits:
        return None
    raised = next((v for v, r, g in hits if r), None)
    goal = next((v for v, r, g in hits if g), None)
    if raised is None and len(hits) >= 2: raised = hits[0][0]
    if goal is None and len(hits) >= 2: goal = max(v for v, _, _ in hits)
    if raised is None or raised > 1e9: return None
    dm = re.search(r"([\d,]{1,9})\s*(?:donations?|donors?|givers?|gifts?|supporters?)\b", t, re.I)
    donors = int(dm.group(1).replace(",", "")) if dm else None
    return {"raised": raised, "goal": goal if goal and goal >= 1000 else prev_goal, "donors": donors}

def main():
    try:
        prev = json.load(open(OUT))
    except Exception:
        prev = {"goal": 250000}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36")
        pg.goto(URL, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(2000)
        text = pg.inner_text("body")
        b.close()
    data = parse(text, prev.get("goal", 250000))
    if not data:
        print("Could not find a figure on the page; keeping previous data.json")
        return 0
    data["updatedAt"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["source"] = "givesendgo"
    json.dump(data, open(OUT, "w"), indent=2)
    print("Updated:", data)
    return 0

if __name__ == "__main__":
    sys.exit(main())
