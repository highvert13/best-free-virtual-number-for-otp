"""Collect recent App Store reviews for free number apps and summarise what users
say about verification codes.

Source: Apple's public customer-reviews RSS feed (no API key) and the iTunes
Lookup API for overall ratings. Stores: US, Canada, UK, Australia.

Writes data/reviews.json. Run daily (GitHub Actions) before tools/build.py:
    python tools/fetch_reviews.py
"""
import datetime as dt
import json
import pathlib
import re
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "reviews.json"

APPS = [
    {"id": "textnow", "name": "TextNow", "app_id": 314716233},
    {"id": "google-voice", "name": "Google Voice", "app_id": 318698524},
    {"id": "talkatone", "name": "Talkatone", "app_id": 397648381},
    {"id": "textfree", "name": "TextFree", "app_id": 399355755},
    {"id": "nextplus", "name": "Nextplus", "app_id": 920869470},
]
STORES = {"us": "US", "ca": "Canada", "gb": "UK", "au": "Australia"}
PAGES = 3                      # 50 reviews per page, most recent first
WINDOW_DAYS = 30
# Apple returns empty feeds to clients without a "Mozilla/5.0" prefix.
UA = {"User-Agent": "Mozilla/5.0 (compatible; otp-number-lab-reviews/1.0)", "Accept": "application/json"}

# A review "mentions verification" if it talks about codes, OTP or signing in to another app.
VERIFY_RE = re.compile(
    r"\b(verif\w*|verification code|code(s)?|otp|2fa|two[- ]factor|one[- ]time|sign[- ]?up|log[- ]?in|"
    r"whatsapp|telegram|gmail|google account|short ?code)\b", re.I)


def get_json(url, retries=2):
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if attempt == retries:
                return None
            time.sleep(2)


def feed_entries(url):
    entries = (get_json(url) or {}).get("feed", {}).get("entry", [])
    return [entries] if isinstance(entries, dict) else entries


def fetch_reviews(app_id, store):
    reviews, seen = [], set()
    for page in range(1, PAGES + 1):
        entries = feed_entries(f"https://itunes.apple.com/{store}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json")
        # Apple sometimes returns an empty first page; retry, alternating with the
        # plain feed, which lists the same 50 newest reviews.
        for attempt in range(4 if page == 1 else 0):
            if entries:
                break
            time.sleep(2 + attempt * 2)
            url = (f"https://itunes.apple.com/{store}/rss/customerreviews/id={app_id}/json" if attempt % 2 == 0 else
                   f"https://itunes.apple.com/{store}/rss/customerreviews/page=1/id={app_id}/sortby=mostrecent/json")
            entries = feed_entries(url)
        for e in entries:
            rid = e.get("id", {}).get("label")
            if "im:rating" not in e or rid in seen:
                continue
            seen.add(rid)
            reviews.append({
                "date": e["updated"]["label"][:10],
                "rating": int(e["im:rating"]["label"]),
                "title": e["title"]["label"].strip(),
                "text": e["content"]["label"].strip(),
                "store": store,
            })
        if len(entries) < 50:
            break
        time.sleep(0.5)
    return reviews


# What reviews talk about (a review can match several themes).
THEMES = {
    "codes": VERIFY_RE,
    "ads": re.compile(r"\b(ads?|advert\w*|commercials?)\b", re.I),
    "number_lost": re.compile(r"\b(lost|lose|losing|took|taken|reclaim\w*|expired?|recycled?)\b.{0,30}\bnumbers?\b|\bnumbers?\b.{0,30}\b(lost|taken|reclaim\w*|expired?|recycled?|gone)\b", re.I),
    "account_blocked": re.compile(r"\b(banned|ban|suspended|blocked|locked|disabled|deactivated)\b", re.I),
    "call_quality": re.compile(r"\b(call quality|dropped calls?|calls? drop\w*|can'?t hear|echo|static)\b", re.I),
    "pricing": re.compile(r"\b(subscription|premium|paywall|charged?|refund|price|pay(ing)?)\b", re.I),
}

# Never quote reviews that reveal personal details or that come from children.
UNQUOTABLE_RE = re.compile(
    r"(\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b|@[\w-]+\.\w+|\bi'?m\s+\d{1,2}\b|\bi am\s+\d{1,2}\b|\b\d{1,2}\s*(years?|yrs?)\s*old\b|"
    r"\bf+u+c+k|\bs+h+i+t\b)", re.I)


def quotable(review):
    text = review["title"] + " " + review["text"]
    return len(review["text"]) >= 40 and not UNQUOTABLE_RE.search(text)


def excerpt(text, limit=170):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",.;:") + "…"


def summarise(app, today):
    lookup = get_json(f"https://itunes.apple.com/lookup?id={app['app_id']}&country=us") or {}
    meta = (lookup.get("results") or [{}])[0]
    since = (today - dt.timedelta(days=WINDOW_DAYS)).isoformat()

    recent = []
    for store in STORES:
        recent += [r for r in fetch_reviews(app["app_id"], store) if r["date"] >= since]
    recent.sort(key=lambda r: r["date"], reverse=True)

    verify = [r for r in recent if VERIFY_RE.search(r["title"] + " " + r["text"])]
    negative = [r for r in verify if r["rating"] <= 2]
    positive = [r for r in verify if r["rating"] >= 4]

    quotes = []
    for pool in (negative, positive):
        pool = [r for r in pool if quotable(r)]
        if pool:
            r = pool[0]
            quotes.append({"date": r["date"], "rating": r["rating"], "store": STORES[r["store"]],
                           "title": excerpt(r["title"], 70), "text": excerpt(r["text"])})

    themes = {name: sum(1 for r in recent if rx.search(r["title"] + " " + r["text"])) for name, rx in THEMES.items()}

    def avg(rows):
        return round(sum(r["rating"] for r in rows) / len(rows), 1) if rows else None

    return {
        "id": app["id"],
        "name": app["name"],
        "app_id": app["app_id"],
        "rating_all_time": round(meta.get("averageUserRating", 0), 1) or None,
        "ratings_count": meta.get("userRatingCount"),
        "reviews_30d": len(recent),
        "avg_rating_30d": avg(recent),
        "verify_mentions_30d": len(verify),
        "verify_negative_share": round(100 * len(negative) / len(verify)) if verify else None,
        "verify_avg_rating_30d": avg(verify),
        "themes_30d": themes,
        "quotes": quotes,
    }


# --------------------------------------------------------------------------
# Reviews published on a service's own website (web-only services, no App Store app).
# SMSFAST exposes its public review list as JSON: 15 reviews per page.
# --------------------------------------------------------------------------
SITE_SOURCES = [
    {"id": "smsfast", "name": "SMSFAST", "page": "https://smsfast.com/reviews",
     "api": "https://backend.smsfast.com/api/reviews?page={page}"},
]
ENGLISH_RE = re.compile(r"\b(the|and|it|is|for|i|was|but|to|my|not)\b", re.I)


def is_english(text):
    return len(ENGLISH_RE.findall(text)) >= 3 and sum(ord(c) < 128 for c in text) / max(len(text), 1) > 0.95


def summarise_site(src, today):
    first = get_json(src["api"].format(page=1))
    if not first or "reviews" not in first:
        return None
    rows = list(first["reviews"]["data"])
    for page in range(2, first["reviews"]["meta"]["last_page"] + 1):
        data = get_json(src["api"].format(page=page))
        rows += (data or {}).get("reviews", {}).get("data", [])
        time.sleep(0.5)
    reviews = [{"date": r["published_at"][:10], "rating": int(r["rating"]), "title": (r.get("title") or "").strip(),
                "text": (r.get("text") or "").strip(), "negative": r.get("type") == "negative" or int(r["rating"]) <= 2}
               for r in rows if r.get("status", "published") == "published"]
    reviews.sort(key=lambda r: r["date"], reverse=True)
    if not reviews:
        return None

    since = (today - dt.timedelta(days=WINDOW_DAYS)).isoformat()
    recent = [r for r in reviews if r["date"] >= since]
    verify = [r for r in reviews if VERIFY_RE.search(r["title"] + " " + r["text"])]
    negative = [r for r in verify if r["negative"]]
    positive = [r for r in verify if not r["negative"] and r["rating"] >= 4]

    quotes = []
    for pool in (negative, positive):
        pool = [r for r in pool if quotable(r) and is_english(r["title"] + " " + r["text"])]
        if pool:
            r = pool[0]
            quotes.append({"date": r["date"], "rating": r["rating"], "title": excerpt(r["title"], 70), "text": excerpt(r["text"])})

    def avg(rs):
        return round(sum(r["rating"] for r in rs) / len(rs), 1) if rs else None

    dist = {n: sum(1 for r in reviews if r["rating"] == n) for n in range(5, 0, -1)}
    return {
        "id": src["id"], "name": src["name"], "source_url": src["page"],
        "reviews_total": len(reviews),
        "rating_avg": avg(reviews),
        "negative_count": sum(1 for r in reviews if r["negative"]),
        "distribution": {str(k): v for k, v in dist.items()},
        "first_review": reviews[-1]["date"],
        "reviews_30d": len(recent),
        "avg_rating_30d": avg(recent),
        "verify_mentions_30d": len(verify_30d := [r for r in verify if r["date"] >= since]),
        "verify_negative_share_30d": round(100 * sum(r["negative"] for r in verify_30d) / len(verify_30d)) if verify_30d else None,
        "verify_mentions": len(verify),
        "verify_negative_share": round(100 * len(negative) / len(verify)) if verify else None,
        "quotes": quotes,
    }


def main():
    today = dt.date.today()
    previous = json.loads(OUT.read_text(encoding="utf-8-sig")) if OUT.exists() else {}
    old_apps = {a["id"]: a for a in previous.get("apps", [])}
    apps = []
    for app in APPS:
        s = summarise(app, today)
        old = old_apps.get(app["id"])
        if s["reviews_30d"] == 0 and old and old["reviews_30d"] > 0:
            s = old   # an empty feed is almost always an Apple outage, not a month without reviews
            print(f"{app['name']}: feed empty, kept previous data")
        apps.append(s)
        print(f"{app['name']}: {apps[-1]['reviews_30d']} reviews, {apps[-1]['verify_mentions_30d']} mention codes")
    old_sites = {s["id"]: s for s in previous.get("sites", [])}
    sites = []
    for src in SITE_SOURCES:
        s = summarise_site(src, today) or old_sites.get(src["id"])   # keep yesterday's data if the site is down
        if s:
            sites.append(s)
            print(f"{src['name']} (own site): {s['reviews_total']} reviews, avg {s['rating_avg']}")
    OUT.write_text(json.dumps({"updated": today.isoformat(), "window_days": WINDOW_DAYS,
                               "stores": list(STORES.values()), "apps": apps, "sites": sites},
                              ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
