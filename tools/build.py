"""Static page generator for OTP Number Lab.

Builds the inner pages (platforms, countries, methodology, about, terms,
affiliate disclosure, 404) plus sitemap.xml and robots.txt from
data/ranking.json and data/site.json. The home, contact and privacy pages are
hand-written HTML in site/ and are not overwritten.

Usage (from the repository root):
    python tools/build.py

Output is plain static HTML in site/<slug>/index.html, committed to Git.
Cloudflare needs no build step.
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = json.loads((ROOT / "data" / "ranking.json").read_text(encoding="utf-8-sig"))
CONF = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8-sig"))

DOMAIN = CONF["domain"].rstrip("/")
BRAND = CONF["brand"]
ASSET_V = CONF["asset_version"]
SAMPLE = DATA.get("sample_data", True)
SERVICES = DATA["services"]
BY_ID = {s["id"]: s for s in SERVICES}

COUNTRIES = {
    "us": {"name": "USA", "long": "the US", "code": "+1", "slug": "/free-us-virtual-number/"},
    "ca": {"name": "Canada", "long": "Canada", "code": "+1", "slug": "/free-canada-virtual-number/"},
    "uk": {"name": "United Kingdom", "long": "the UK", "code": "+44", "slug": "/free-uk-virtual-number/"},
    "au": {"name": "Australia", "long": "Australia", "code": "+61", "slug": "/free-australia-virtual-number/"},
}
PLATFORMS = {
    "telegram": {"name": "Telegram", "slug": "/free-virtual-number-for-telegram/", "accent": "blue"},
    "whatsapp": {"name": "WhatsApp", "slug": "/free-virtual-number-for-whatsapp/", "accent": "green"},
    "google": {"name": "Google", "slug": "/free-virtual-number-for-google-verification/", "accent": "orange"},
}
STATUS = {"works": "Works", "sometimes": "Sometimes", "fails": "Fails"}
TYPE_LABEL = {"private": "Private app", "public": "Public site", "paid": "Paid"}
STATUS_ORDER = {"works": 0, "sometimes": 1, "fails": 2}
SMSFAST = "https://smsfast.com/"

e = html.escape


def smsfast_link(text):
    return f'<a href="{SMSFAST}" rel="noopener" target="_blank">{text}</a>'


# --------------------------------------------------------------------------
# Shared chrome
# --------------------------------------------------------------------------
def head(title, desc, path, jsonld, robots="index, follow"):
    canonical = f"{DOMAIN}{path}" if robots.startswith("index") else None
    canon_tag = f'<link rel="canonical" href="{canonical}">\n' if canonical else ""
    og = (
        f'<meta property="og:type" content="article">\n'
        f'<meta property="og:title" content="{e(title)}">\n'
        f'<meta property="og:description" content="{e(desc)}">\n'
        f'<meta property="og:url" content="{canonical}">\n'
        f'<meta name="twitter:card" content="summary">\n'
    ) if canonical else ""
    ld = f'<script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=2)}\n</script>\n' if jsonld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{canon_tag}<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0b0b0f">
{og}<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/img/icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@500;700&display=swap">
<link rel="stylesheet" href="/assets/css/main.css?v={ASSET_V}">
{ld}</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


def header(active=None):
    """active: 'telegram' | 'whatsapp' | 'google' | 'us' | ... | 'methodology'"""
    def dd_link(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<li><a href="{href}"{cur}>{label}</a></li>'

    plat_active = " is-active" if active in PLATFORMS else ""
    ctry_active = " is-active" if active in COUNTRIES else ""
    meth = ' aria-current="page"' if active == "methodology" else ""
    proto = ""
    if SAMPLE and active in list(PLATFORMS) + list(COUNTRIES):
        proto = ('<div class="proto-note" role="note">\n  <div class="container">Pre-launch: ranking figures '
                 'and test dates are sample data. Replace them with real test results before publishing.</div>\n</div>\n')
    return proto + f"""
<header class="site-header" id="top">
  <div class="container header-inner">
    <a class="logo" href="/" aria-label="{BRAND} home">
      <span class="logo-mark" aria-hidden="true"></span>OTP Number <span class="logo-accent">Lab</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="nav-toggle-bar" aria-hidden="true"></span>
      <span class="visually-hidden">Menu</span>
    </button>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul class="nav-list">
        <li><a class="nav-link" href="/#ranking">Best Free Numbers</a></li>
        <li class="has-dropdown">
          <button class="nav-link dropdown-toggle{plat_active}" type="button" aria-expanded="false">Platforms</button>
          <ul class="dropdown">
            {dd_link(PLATFORMS['telegram']['slug'], 'Telegram', 'telegram')}
            {dd_link(PLATFORMS['whatsapp']['slug'], 'WhatsApp', 'whatsapp')}
            {dd_link(PLATFORMS['google']['slug'], 'Google', 'google')}
          </ul>
        </li>
        <li class="has-dropdown">
          <button class="nav-link dropdown-toggle{ctry_active}" type="button" aria-expanded="false">Countries</button>
          <ul class="dropdown">
            {dd_link(COUNTRIES['us']['slug'], 'USA', 'us')}
            {dd_link(COUNTRIES['ca']['slug'], 'Canada', 'ca')}
            {dd_link(COUNTRIES['uk']['slug'], 'United Kingdom', 'uk')}
            {dd_link(COUNTRIES['au']['slug'], 'Australia', 'au')}
          </ul>
        </li>
        <li><a class="nav-link" href="/methodology/"{meth}>How We Test</a></li>
      </ul>
      <a class="btn btn-outline-gold nav-cta" href="/#ranking">See the ranking</a>
    </nav>
  </div>
</header>
"""


def breadcrumbs(name):
    return f"""
<nav class="breadcrumbs" aria-label="Breadcrumb">
  <div class="container">
    <ol>
      <li><a href="/">Home</a></li>
      <li><span aria-current="page">{e(name)}</span></li>
    </ol>
  </div>
</nav>
"""


def footer(current=None):
    def li(href, label):
        cur = ' aria-current="page"' if href == current else ""
        return f'<li><a href="{href}"{cur}>{label}</a></li>'

    return f"""
<!-- ============ FOOTER (no links that are already in the main menu) ============ -->
<footer class="site-footer">
  <div class="container">
    <div class="footer-main">
      <div class="footer-brand">
        <p class="logo"><span class="logo-mark" aria-hidden="true"></span>OTP Number <span class="logo-accent">Lab</span></p>
        <p>Independent monthly tests of free virtual numbers for OTP in the US, Canada, UK and Australia.</p>
        <p class="footer-note">Use virtual numbers responsibly.</p>
      </div>
      <nav aria-label="Guides on this site">
        <p class="footer-title">Learn</p>
        <ul>
          <li><a href="/#public-vs-private">Public vs private numbers</a></li>
          <li><a href="/#how-to">How to receive an OTP</a></li>
          <li><a href="/#troubleshooting">OTP not arriving</a></li>
          <li><a href="/#safety">Is it safe?</a></li>
          <li><a href="/#faq">FAQ</a></li>
        </ul>
      </nav>
      <nav aria-label="Trust">
        <p class="footer-title">Trust</p>
        <ul>
          {li('/about/', 'About us')}
          {li('/contact/', 'Contact')}
          {li('/privacy-policy/', 'Privacy Policy')}
          {li('/terms/', 'Terms of Use')}
          {li('/affiliate-disclosure/', 'Affiliate Disclosure')}
        </ul>
      </nav>
    </div>
    <p class="footer-legal">© 2026 {BRAND}. We are not affiliated with Telegram, WhatsApp, Meta or Google. All trademarks belong to their owners.</p>
  </div>
</footer>

<div class="cookie-banner" id="cookie-banner" role="dialog" aria-live="polite" aria-label="Cookie consent" hidden>
  <p>We use analytics cookies to see which rankings are useful. They load only if you accept. <a href="/privacy-policy/">Privacy Policy</a></p>
  <div class="cookie-actions">
    <button class="btn btn-secondary btn-sm" type="button" data-consent="declined">Decline</button>
    <button class="btn btn-primary btn-sm" type="button" data-consent="accepted">Accept</button>
  </div>
</div>

<script src="/assets/js/main.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


def author_box():
    return f"""
<section class="band band-soft" aria-label="About the author">
  <div class="container container-narrow">
    <div class="author-box">
      <div class="author-avatar" aria-hidden="true">AM</div>
      <div>
        <p class="author-name">Written and tested by <a href="/about/#alex-morgan">Alex Morgan</a></p>
        <p class="author-bio">Privacy tools reviewer. Tests virtual number services every month across the US, Canada, UK and Australia.</p>
        <p class="author-meta">Last updated <time datetime="{DATA['updated']}">November 22, 2026</time> · Next test cycle: December 2026 · <a href="/methodology/#changelog">Ranking changelog</a></p>
      </div>
    </div>
  </div>
</section>
"""


# --------------------------------------------------------------------------
# JSON-LD helpers
# --------------------------------------------------------------------------
def ld_base(path, name, page_type="Article", headline=None, extra=None):
    graph = [
        {"@type": "Organization", "@id": f"{DOMAIN}/#org", "name": BRAND, "url": f"{DOMAIN}/"},
        {"@type": "WebSite", "@id": f"{DOMAIN}/#website", "url": f"{DOMAIN}/", "name": BRAND,
         "publisher": {"@id": f"{DOMAIN}/#org"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": f"{DOMAIN}{path}"}]},
    ]
    page = {"@type": page_type, "url": f"{DOMAIN}{path}", "isPartOf": {"@id": f"{DOMAIN}/#website"},
            "dateModified": DATA["updated"]}
    if page_type == "Article":
        page.update({"headline": headline or name, "datePublished": "2026-11-22",
                     "author": {"@type": "Person", "name": "Alex Morgan", "url": f"{DOMAIN}/about/"},
                     "publisher": {"@id": f"{DOMAIN}/#org"}, "mainEntityOfPage": f"{DOMAIN}{path}"})
    else:
        page["name"] = name
    graph.append(page)
    graph.extend(extra or [])
    return {"@context": "https://schema.org", "@graph": graph}


def ld_itemlist(name, services):
    return {"@type": "ItemList", "name": name, "numberOfItems": len(services),
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s["name"],
                                 "url": f"{DOMAIN}/#{s['id']}"} for i, s in enumerate(services)]}


def ld_faq(faqs):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


# --------------------------------------------------------------------------
# Content components
# --------------------------------------------------------------------------
def status(v):
    return f'<span class="status s-{v}">{STATUS[v]}</span>'


def cc(codes):
    return "".join(f'<span class="cc">{c.upper()}</span>' for c in codes)


def ranking_table(services, caption):
    rows = []
    for i, s in enumerate(services, 1):
        top = ' class="is-top"' if i == 1 else ""
        tag_cls = "tag tag-outline" if s["tag"] in ("Best overall", "Best paid pick") else "tag"
        action = ""
        if s["id"] == "smsfast":
            action = f'<a class="btn btn-primary btn-sm" href="{SMSFAST}" rel="noopener" target="_blank">Get number <span class="ext" aria-hidden="true">↗</span></a>'
        rows.append(f"""          <tr{top}>
            <td data-label="Rank"><span class="rank">{i}</span></td>
            <th scope="row" data-label="Service"><a href="/#{s['id']}">{s['name']}</a><span class="{tag_cls}">{s['tag']}</span></th>
            <td data-label="Type">{TYPE_LABEL[s['type']]}</td>
            <td data-label="Countries">{cc(s['countries'])}</td>
            <td data-label="Telegram">{status(s['telegram'])}</td>
            <td data-label="WhatsApp">{status(s['whatsapp'])}</td>
            <td data-label="Google">{status(s['google'])}</td>
            <td data-label="OTP success">{s['success']}%</td>
            <td data-label="Signup">{s['signup']}</td>
            <td data-label="Last tested"><time datetime="{s['tested']}">{fmt_date(s['tested'])}</time></td>
            <td data-label="Score"><strong>{s['score']}</strong></td>
            <td class="actions">{action}</td>
          </tr>""")
    return f"""    <div class="table-wrap">
      <table class="ranking-table">
        <caption class="visually-hidden">{e(caption)}</caption>
        <thead>
          <tr><th scope="col">#</th><th scope="col">Service</th><th scope="col">Type</th><th scope="col">Countries</th><th scope="col">Telegram</th><th scope="col">WhatsApp</th><th scope="col">Google</th><th scope="col">Success</th><th scope="col">Signup</th><th scope="col">Tested</th><th scope="col">Score</th><th scope="col"><span class="visually-hidden">Actions</span></th></tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>
    <p class="table-legend"><span class="status s-works">Works</span> 7 or more of 10 codes received <span class="status s-sometimes">Sometimes</span> 3 to 6 of 10 <span class="status s-fails">Fails</span> 0 to 2 of 10. <a href="/methodology/">How we test</a></p>"""


def fmt_date(iso):
    y, m, d = iso.split("-")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[int(m) - 1]} {int(d)}, {y}"


def pick_cards(items):
    """items: list of (service_id, award_label, text)"""
    cards = []
    for idx, (sid, award, text) in enumerate(items):
        s = BY_ID[sid]
        featured = " is-featured" if idx == 0 else ""
        award_cls = "tag tag-gold" if idx == 0 else "tag tag-outline"
        rank = "PAID" if s["type"] == "paid" else f"#{SERVICES.index(s) + 1}"
        actions = f'<a class="btn btn-secondary btn-sm" href="/#{sid}">Read review</a>'
        if sid == "smsfast":
            actions += f'<a class="btn btn-primary btn-sm" href="{SMSFAST}" rel="noopener" target="_blank">Get number <span class="ext" aria-hidden="true">↗</span></a>'
        countries = " · ".join(c.upper() for c in s["countries"])
        cards.append(f"""      <article class="pick-card{featured}">
        <div class="tile tile--{s['tile']}" aria-hidden="true"><span class="tile-rank">{rank}</span><span class="tile-mono">{s['mono']}</span><span class="tile-sub">{s['sub']}</span></div>
        <div>
          <div class="pick-head"><h3>{s['name']}</h3><span class="score" aria-label="Score {s['score']} out of 10">{s['score']}</span></div>
          <div class="tags"><span class="{award_cls}">{award}</span><span class="tag">{TYPE_LABEL[s['type']]}</span><span class="tag">{countries}</span></div>
          <p>{text}</p>
          <div class="pick-actions">{actions}</div>
        </div>
      </article>""")
    return '    <div class="picks">\n' + "\n".join(cards) + "\n    </div>"


def paid_cards(country=None, platform=None):
    out = []
    for sid in ("smsfast", "hushed", "burner"):
        s = BY_ID[sid]
        if country and country not in s["countries"]:
            continue
        bullets = [", ".join(COUNTRIES[c]["name"] for c in s["countries"])]
        if platform:
            bullets.append(f"{PLATFORMS[platform]['name']}: {STATUS[s[platform]]} in our test")
        else:
            ok = [PLATFORMS[p]["name"] for p in PLATFORMS if s[p] == "works"]
            bullets.append("Worked on " + ", ".join(ok))
        if sid == "smsfast":
            bullets.append("Pay per code or rent from 1 day to 1 year")
            bullets.append("Balance refund if no code arrives")
            btn = f'<a class="btn btn-primary" href="{SMSFAST}" rel="noopener" target="_blank">Get SMSFAST number <span class="ext" aria-hidden="true">↗</span></a>'
            badge = '<span class="badge badge-info">Best paid pick</span>\n        '
            cls = "card card-pricing is-featured"
        else:
            btn, badge, cls = "", "", "card card-pricing"
        lis = "".join(f"<li>{b}</li>" for b in bullets)
        out.append(f"""      <article class="{cls}">
        {badge}<h3>{s['name']}</h3>
        <p class="price">{s['price']}</p>
        <ul>{lis}</ul>
        {btn}
      </article>""")
    cols = "grid-3" if len(out) >= 3 else "grid-2"
    return f'    <div class="grid {cols}">\n' + "\n".join(out) + "\n    </div>"


def faq_block(title, faqs):
    items = "\n".join(
        f"      <details>\n        <summary>{e(q)}</summary>\n        <p>{a}</p>\n      </details>" for q, a in faqs)
    return f"""<section class="band" id="faq" aria-labelledby="faq-title">
  <div class="container container-narrow">
    <p class="eyebrow">FAQ</p>
    <h2 id="faq-title">{title}</h2>
    <div class="faq">
{items}
    </div>
  </div>
</section>"""


def related(cards, title="More Free Number Guides"):
    items = []
    for href, cat, eyebrow, h3, text, link in cards:
        items.append(f"""      <a class="card category-card {cat}" href="{href}">
        <p class="eyebrow-sm">{eyebrow}</p>
        <h3>{h3}</h3>
        <p>{text}</p>
        <span class="link-arrow">{link}</span>
      </a>""")
    return f"""<section class="band band-soft" aria-labelledby="related-title">
  <div class="container">
    <p class="eyebrow">Keep exploring</p>
    <h2 id="related-title">{title}</h2>
    <div class="grid grid-3">
{chr(10).join(items)}
    </div>
  </div>
</section>"""


def steps(items):
    lis = "".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in items)
    return f'<ol class="steps">{lis}</ol>'


def page_header(eyebrow, h1, lead, accent=None, trust=None, actions=True):
    acc = f" accent-{accent}" if accent else ""
    trust_html = ""
    if trust:
        cells = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in trust)
        trust_html = f'\n      <dl class="trust-strip trust-3">{cells}</dl>'
    act = ""
    if actions:
        act = ('\n      <div class="hero-actions"><a class="btn btn-primary" href="#ranking">See test results</a>'
               '<a class="btn btn-secondary" href="/#ranking">Full ranking</a></div>')
    return f"""  <header class="page-header{acc}">
    <div class="container">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>{act}{trust_html}
    </div>
  </header>"""


def jump(items):
    lis = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items)
    return f'<nav class="jump-nav" aria-label="On this page"><div class="container"><ul>{lis}</ul></div></nav>'


def section(sid, eyebrow, h2, body, soft=False, narrow=True):
    cls = "band band-soft" if soft else "band"
    cont = "container container-narrow" if narrow else "container"
    return f"""<section class="{cls}" id="{sid}" aria-labelledby="{sid}-title">
  <div class="{cont}">
    <p class="eyebrow">{eyebrow}</p>
    <h2 id="{sid}-title">{h2}</h2>
{body}
  </div>
</section>"""


def write(path, content):
    out = SITE / path.strip("/") / "index.html" if path != "/404.html" else SITE / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


# --------------------------------------------------------------------------
# Platform pages
# --------------------------------------------------------------------------
def platform_services(p):
    free = [s for s in SERVICES if s["type"] != "paid"]
    paid = [s for s in SERVICES if s["type"] == "paid"]
    if p != "whatsapp":
        free = [s for s in free if s[p] != "fails"]
    free.sort(key=lambda s: (STATUS_ORDER[s[p]], -s["score"]))
    paid.sort(key=lambda s: (STATUS_ORDER[s[p]], -s["score"]))
    return free + paid


PLATFORM_CONTENT = {
    "telegram": {
        "title": "Free Virtual Number for Telegram (2026): Tested Options That Work",
        "desc": "Which free virtual number works for Telegram verification? We tested 12 services in the US, Canada, UK & Australia. Results, errors and safer options.",
        "h1": "Free Virtual Number for Telegram Verification",
        "eyebrow": "Telegram · Tested November 2026 · 120 code requests",
        "lead": "The best free virtual number for Telegram in our tests was <strong>TextNow</strong>: Telegram accepted it in 6 of 10 attempts. Public receive-SMS numbers rarely passed. If you need a number that works every time, the paid option " + smsfast_link("SMSFAST") + " passed all 10 Telegram checks.",
        "trust": [("Services tested", "12"), ("Codes requested", "120"), ("Best free result", "6/10")],
        "picks": [("textnow", "Best free for Telegram", "Passed Telegram in 6 of 10 attempts, the best result of any free number we tested."),
                  ("google-voice", "Stable US number", "Accepted in some attempts. Many apps flag it as VoIP, but it never expires as long as you use it."),
                  ("smsfast", "Works every time", "Passed all 10 Telegram checks in our test, in all four countries.")],
        "ranking_h2": "Best Free Virtual Numbers for Telegram: Test Results",
        "ranking_intro": "Only services that passed at least some Telegram checks are listed. Free numbers come first, paid fallbacks after.",
        "sections": [
            ("how-telegram-verifies", "How it works", "How Telegram Verifies Phone Numbers", """    <p>Telegram sends your login code in a fixed order. If you are already signed in on another device, the code arrives inside the Telegram app. If not, Telegram sends an SMS, and after a timer it can call the number and read the code aloud.</p>
    <p>Before sending anything, Telegram checks the number itself. It looks at the line type (mobile, landline or VoIP) and at the number's history. Numbers that have been used for many accounts, or that belong to ranges known for abuse, are refused before an SMS is ever sent. That is why a free virtual number for Telegram can work for one person and fail for the next.</p>"""),
            ("phone-number-banned", "Common error", "Why Telegram Says \"Phone Number Banned\"", """    <p>The "phone number banned" message means Telegram has blocked that number, not you. With free numbers this usually happens because the number was flagged as VoIP, was used to create many accounts, or was previously blocked for spam.</p>
    <p>There is no reliable way to unblock a shared or recycled number, and trying to get around the block breaks Telegram's rules. The practical options are to use a different type of number, contact Telegram support if the number is genuinely yours, or switch to a private paid number such as """ + smsfast_link("an SMSFAST Telegram number") + """.</p>"""),
            ("code-not-received", "Troubleshooting", "Telegram Code Not Received: What to Try", "    " + steps([
                ("Wait for the timer", "Telegram shows a countdown before it allows a new code. Requesting again early resets nothing."),
                ("Ask for a call", "When the timer ends, choose the call option. Some numbers that cannot receive SMS can still receive a call."),
                ("Check the country code", "Use +1 for the US and Canada, +44 for the UK and +61 for Australia, with no leading zero."),
                ("Do not spam requests", "Many requests in a row trigger a cooldown that can last hours."),
                ("Switch number type", "If a free app number keeps failing, try a different app or a private paid number."),
            ])),
            ("public-vs-private", "Risk", "Public vs Private Numbers for Telegram", """    <p>On a public receive-SMS website, everyone can see the code Telegram sends you. Anyone who copies it in time can sign in to your new account. Later, someone else can use the same number to recover the account.</p>
    <p>If you keep the account, use a private number and turn on <strong>Two-Step Verification</strong> (a cloud password) in Telegram's Privacy and Security settings right after you sign in. With a password set, a code alone is not enough to take over the account.</p>"""),
            ("fragment", "Official option", "Anonymous Telegram Numbers on Fragment", """    <p>Telegram also supports anonymous +888 numbers sold on Fragment, its own marketplace. They work only for Telegram, are paid for in TON cryptocurrency and need no SIM card. They are a good fit if you want a Telegram account that is never tied to a real phone number, but they are not free and cannot receive codes from other apps. Check current prices and terms on Fragment before buying.</p>"""),
        ],
        "paid_h2": "Cheap Paid Numbers That Work on Telegram",
        "faq_title": "Free Virtual Number for Telegram: FAQ",
        "faqs": [
            ("Can I use a free virtual number for Telegram?", "Sometimes. Free app numbers such as TextNow and Google Voice passed some Telegram checks in our tests, but Telegram rejects numbers it identifies as VoIP or overused. Public receive-SMS numbers rarely work."),
            ("Does Telegram accept TextNow or Google Voice numbers?", "In our November 2026 test, Telegram accepted TextNow in 6 of 10 attempts and Google Voice in some attempts. Results change as Telegram updates its checks, so we retest every month."),
            ("Why does Telegram say \"phone number banned\"?", "Telegram has blocked that specific number, usually because it was flagged as VoIP, used for many accounts or reported for spam. Use a different number type or a private number you control."),
            ("What happens if I lose the number used on Telegram?", "You can still use Telegram on devices where you are signed in, but you may not be able to log in on a new device. Set a cloud password and add a recovery email so you are not locked out."),
            ("Can I sign up for Telegram without a phone number?", "Telegram requires a phone number to sign up. The only official alternative is an anonymous +888 number bought on Fragment."),
        ],
    },
    "whatsapp": {
        "title": "Free Virtual Number for WhatsApp (2026): What Actually Works",
        "desc": "Is there a free virtual number for WhatsApp that works? Our tests of 12 services show why most fail, the risks of public numbers and cheap options that pass.",
        "h1": "Free Virtual Number for WhatsApp Verification",
        "eyebrow": "WhatsApp · Tested November 2026 · 120 code requests",
        "lead": "No free virtual number for WhatsApp was reliable in our tests. The best free result came from <strong>Google Voice</strong>, which passed only some attempts. Every public receive-SMS number failed. The number that passed every WhatsApp check was the paid " + smsfast_link("SMSFAST") + ".",
        "trust": [("Services tested", "12"), ("Codes requested", "120"), ("Reliable free numbers", "0")],
        "picks": [("smsfast", "Best for WhatsApp", "Passed every WhatsApp check in our test, with local numbers in the US, Canada, UK and Australia."),
                  ("google-voice", "Best free try", "The only free number that received some WhatsApp codes. US only, and you need a US number to set it up."),
                  ("hushed", "Disposable option", "Private paid numbers in all four countries. WhatsApp accepted it in some attempts.")],
        "ranking_h2": "Free Virtual Numbers for WhatsApp: Test Results",
        "ranking_intro": "We list all 12 services, including the ones that failed, because knowing what does not work on WhatsApp saves you time.",
        "sections": [
            ("why-free-fails", "Why it fails", "Why Most Free Numbers Fail on WhatsApp", """    <p>WhatsApp is the strictest of the three platforms we test. It checks the line type of every number and refuses many VoIP numbers before sending a code. Almost every free virtual number is a VoIP number, so most of them never get as far as an SMS.</p>
    <p>WhatsApp also refuses numbers that have already been used to register many accounts, which rules out public receive-SMS numbers. And it may expect a number that matches the region of your phone and app store. A free US number on a phone set up in the UK is more likely to fail.</p>"""),
            ("re-registration-risk", "Hidden risk", "The Hidden Risk: Someone Else Can Re-Register Your Account", """    <p>A WhatsApp account is tied to its phone number. If you register with a public number, or with a free number that is later recycled, the next person to get that number can request a code and register WhatsApp on it. Your account is then moved to their phone.</p>
    <p>To protect yourself, turn on <strong>Two-step verification</strong> in WhatsApp settings and set a PIN. Better still, use a number you control for the long term: your own SIM, or a number rented for months from a provider such as """ + smsfast_link("SMSFAST") + """, rather than a one-time code."""),
            ("code-not-received", "Troubleshooting", "WhatsApp Code Not Received: What to Try", "    " + steps([
                ("Wait for the timer", "WhatsApp shows a countdown before you can request another code."),
                ("Choose \"Call me\"", "A voice call can reach some numbers that do not receive SMS."),
                ("Check the country code", "Pick the right country in the list and enter the number without a leading zero."),
                ("Avoid repeated requests", "Too many requests lock the number for hours or longer."),
                ("Change the number type", "If a free VoIP number keeps failing, a private paid number is the realistic next step."),
            ])),
            ("whatsapp-business", "Business accounts", "WhatsApp Business and Virtual Numbers", """    <p>WhatsApp Business also needs a number that can receive an SMS or a call to register. Many VoIP numbers are not supported, so the same limits apply. If you run a business account, use a number you will keep for years, because losing it means losing access to the account and its chat history. Check WhatsApp's own help pages for the current rules before you choose a number.</p>"""),
        ],
        "paid_h2": "Paid Numbers That Pass WhatsApp Verification",
        "faq_title": "Free Virtual Number for WhatsApp: FAQ",
        "faqs": [
            ("Is there a free number that works for WhatsApp verification?", "Not reliably. In our tests Google Voice passed some attempts and every other free number failed. For WhatsApp, a cheap private paid number is the realistic choice."),
            ("Why is WhatsApp not sending the code to my virtual number?", "WhatsApp checks the line type and history of the number before sending a code. Most free virtual numbers are VoIP lines or heavily used, so WhatsApp refuses them without sending an SMS."),
            ("Can I verify WhatsApp with a voice call instead of SMS?", "Yes. When the SMS timer ends, choose \"Call me\" and WhatsApp reads the 6-digit code aloud. It helps with some numbers but not with numbers WhatsApp has already refused."),
            ("Is it safe to use a public number for WhatsApp?", "No. Anyone can read the code, and the next person who uses that number can re-register WhatsApp and take over your account."),
            ("Can I use a US number for WhatsApp outside the US?", "Often yes, but WhatsApp may expect a number that matches your region. A local number for your country is more likely to pass."),
        ],
    },
    "google": {
        "title": "Free Virtual Number for Google Verification (2026): Tested",
        "desc": "Free virtual numbers that pass Google account verification in 2026, why Google says \"this number cannot be used\", and how Google Voice fits in.",
        "h1": "Free Virtual Number for Google Account Verification",
        "eyebrow": "Google · Tested November 2026 · 120 code requests",
        "lead": "Google is the easiest of the three platforms to pass with a free number. The best free virtual number for Google verification in our tests was <strong>Google Voice</strong>, accepted every time, followed by <strong>TextNow</strong> at 9 of 10. Public receive-SMS numbers almost always failed.",
        "trust": [("Services tested", "12"), ("Codes requested", "120"), ("Best free result", "10/10")],
        "picks": [("google-voice", "Best for Google", "Accepted by Google in every attempt. US only, and you need an existing US number to claim it."),
                  ("textnow", "Best without a US number", "Passed Google in 9 of 10 attempts and works in the US and Canada with only an email signup."),
                  ("smsfast", "Outside the US", "Passed Google in all four countries when free US numbers are not an option.")],
        "ranking_h2": "Best Free Virtual Numbers for Google: Test Results",
        "ranking_intro": "Only services that passed at least some Google checks are listed. Free numbers first, paid fallbacks after.",
        "sections": [
            ("cannot-be-used", "Common error", "\"This Phone Number Cannot Be Used for Verification\": Why It Happens", """    <p>Google shows this message when a number has already been used too many times, or when its signals look unreliable. Public receive-SMS numbers trigger it almost every time, because hundreds of strangers have used them before you.</p>
    <p>Retrying the same number rarely helps. Use a private number such as Google Voice or TextNow, or a private paid number such as """ + smsfast_link("SMSFAST") + """ if you are outside the US. If Google offers to skip the phone step, take it and add a recovery email instead.</p>"""),
            ("without-phone", "Options", "Can You Create a Google Account Without a Phone Number?", """    <p>Sometimes. Google decides whether to ask for a phone number based on the device, the network and other risk signals. On a phone you already use, the phone step is often optional. On a new browser or a shared network, Google is more likely to require it. There is no setting that guarantees you can skip it, and we do not recommend tricks to avoid it.</p>"""),
            ("google-voice", "Free US number", "Google Voice: Free US Number, With a Catch", """    <p>Google Voice gives you a free US number for calls and texts, linked to your Google account. It is the most stable free number we test: it has no ads and is not recycled as quickly as ad-supported apps, as long as you use it.</p>
    <p>The catch is setup. To claim a Google Voice number you need an existing US phone number to verify, and the service is meant for personal use in the US. If you are in the UK, Canada or Australia without a US number, TextNow or a paid number are the realistic options. See our <a href="/free-us-virtual-number/">free US virtual number</a> page for a full comparison.</p>"""),
            ("how-to", "Step by step", "How to Verify a Google Account With a Virtual Number", "    " + steps([
                ("Get a private number", "Set up Google Voice or TextNow, or buy a paid number if you are outside the US."),
                ("Enter it with the country code", "Use the +1 format for US and Canadian numbers."),
                ("Choose SMS or voice call", "Google can send a text or call with the code."),
                ("Enter the code quickly", "Codes expire after a few minutes."),
                ("Add a recovery email", "Do not rely on the virtual number alone to recover the account later."),
            ])),
            ("keep-safe", "Security", "Keep Your Google Account Safe", """    <p>Never set a public number as your Google recovery phone: whoever has the number can reset your password. After signing up, add a recovery email, turn on 2-Step Verification with an authenticator app or a passkey, and remove any virtual number you might lose.</p>"""),
        ],
        "paid_h2": "Paid Numbers That Pass Google Verification",
        "faq_title": "Free Virtual Number for Google Verification: FAQ",
        "faqs": [
            ("Which free virtual numbers work for Google verification?", "In our tests Google Voice passed every time and TextNow passed 9 of 10 attempts. Talkatone and TextFree passed some attempts. Public receive-SMS numbers almost always failed."),
            ("Why does Google say this phone number cannot be used for verification?", "The number has been used too many times or looks unreliable to Google. It happens most with public receive-SMS numbers. Try a private number instead."),
            ("Can I create a Google account without a phone number?", "Sometimes. Google decides based on your device and other signals. On a familiar device the phone step is often optional."),
            ("How do I get a free Google Voice number?", "Sign in at voice.google.com with your Google account, choose a number and verify it with an existing US phone number. It is available for personal use in the US."),
            ("Should I use a virtual number as my Google recovery phone?", "Only if it is a private number you will keep. Never use a public number, and add a recovery email and an authenticator app as well."),
        ],
    },
}


def build_platform(p):
    c = PLATFORM_CONTENT[p]
    meta = PLATFORMS[p]
    svcs = platform_services(p)
    sections_html = []
    for i, (sid, eyebrow, h2, body) in enumerate(c["sections"]):
        sections_html.append(section(sid, eyebrow, h2, body, soft=(i % 2 == 1)))
    jump_items = [("picks", "Top picks"), ("ranking", "Test results")] + \
                 [(sid, SHORT.get(sid, h2[:24])) for sid, _, h2, _ in c["sections"][:3]] + \
                 [("paid", "Paid options"), ("faq", "FAQ")]
    others = [k for k in PLATFORMS if k != p]
    rel_cards = [(PLATFORMS[k]["slug"], f"cat-{PLATFORMS[k]['accent']}", PLATFORMS[k]["name"],
                  f"Free Virtual Number for {PLATFORMS[k]['name']}", RELATED_TEXT[k], f"Numbers for {PLATFORMS[k]['name']}") for k in others]
    rel_cards.append(("/free-us-virtual-number/", "cat-purple", "Country", "Free US Virtual Number",
                      "TextNow, Google Voice and other free +1 numbers compared.", "Free US numbers"))
    rel_cards = rel_cards[:3]
    body = f"""{head(c['title'], c['desc'], meta['slug'], ld_base(meta['slug'], meta['name'], headline=c['h1'], extra=[ld_itemlist(c['ranking_h2'], svcs), ld_faq([(q, strip_tags(a)) for q, a in c['faqs']])]))}{header(p)}{breadcrumbs(meta['name'])}
<main id="main">
{page_header(c['eyebrow'], c['h1'], c['lead'], accent=meta['accent'], trust=c['trust'])}
{jump(jump_items)}

<section class="band" id="picks" aria-labelledby="picks-title">
  <div class="container">
    <p class="eyebrow">Quick answer</p>
    <h2 id="picks-title">Top Picks for {meta['name']}</h2>
{pick_cards(c['picks'])}
  </div>
</section>

<section class="band band-soft" id="ranking" aria-labelledby="ranking-title">
  <div class="container">
    <p class="eyebrow">Test results</p>
    <h2 id="ranking-title">{c['ranking_h2']}</h2>
    <p class="section-intro">{c['ranking_intro']} For the overall ranking, see the <a href="/">best free virtual number for OTP</a>.</p>
{ranking_table(svcs, c['ranking_h2'])}
  </div>
</section>

{chr(10).join(sections_html)}

<section class="band" id="paid" aria-labelledby="paid-title">
  <div class="container">
    <p class="eyebrow">Paid alternatives</p>
    <h2 id="paid-title">{c['paid_h2']}</h2>
    <p class="section-intro">When free numbers keep failing, a private paid number is the next step. It is not shared with strangers and passes more carrier checks.</p>
{paid_cards(platform=p)}
  </div>
</section>

{faq_block(c['faq_title'], c['faqs'])}

{related(rel_cards)}
{author_box()}
</main>
{footer()}"""
    write(meta["slug"], body)


SHORT = {
    "how-telegram-verifies": "How it works", "phone-number-banned": "\"Banned\" error", "code-not-received": "No code?",
    "why-free-fails": "Why free fails", "re-registration-risk": "Account risk", "cannot-be-used": "\"Cannot be used\"",
    "without-phone": "No phone number?", "google-voice": "Google Voice", "textnow-vs-google-voice": "TextNow vs Google Voice",
    "shared-plus-one": "+1 shared with US", "why-rare": "Why free is rare", "free-options": "Free options",
}

RELATED_TEXT = {
    "telegram": "Telegram is the most forgiving platform. See which free numbers passed and how to fix \"phone number banned\".",
    "whatsapp": "WhatsApp is the strictest platform. See why free numbers fail and which numbers pass.",
    "google": "Google is the easiest to pass with a free number. See which numbers Google accepts.",
}


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


# --------------------------------------------------------------------------
# Country pages
# --------------------------------------------------------------------------
COUNTRY_CONTENT = {
    "us": {
        "title": "Free US Virtual Number for OTP (2026): Tested & Ranked",
        "desc": "The best free US virtual numbers for OTP codes in 2026: TextNow, Google Voice, Talkatone and more, tested on Telegram, WhatsApp and Google.",
        "h1": "Free US Virtual Number for OTP Verification",
        "lead": "The best free US virtual number for OTP in our tests was <strong>TextNow</strong>, followed by <strong>Google Voice</strong>. The US has more free private numbers than any other country we test, so most people can verify Telegram and Google without paying.",
        "picks": [("textnow", "Best free US number", "Free +1 number with an email signup. Passed Google in 9 of 10 attempts and Telegram in 6 of 10."),
                  ("google-voice", "Most stable", "Accepted by Google every time, no ads. Needs an existing US number to activate."),
                  ("smsfast", "For WhatsApp", "No free US number was reliable on WhatsApp. SMSFAST US numbers passed every check.")],
        "format": "US numbers use the country code <strong>+1</strong> followed by a 10-digit number: a 3-digit area code and a 7-digit local number, for example <code>+1 415 555 0142</code>. Mobile and landline numbers look the same, so apps check the line type separately. Enter the number with +1 and no extra zero.",
        "unique": ("textnow-vs-google-voice", "Head to head", "TextNow vs Google Voice: Which Free US Number Is Better?", """    <div class="table-wrap">
      <table class="compare-table">
        <thead><tr><th scope="col">Criterion</th><th scope="col">TextNow</th><th scope="col">Google Voice</th></tr></thead>
        <tbody>
          <tr><th scope="row">Countries</th><td>US, Canada</td><td>US</td></tr>
          <tr><th scope="row">Needs a US number to set up</th><td>No, email signup</td><td>Yes</td></tr>
          <tr><th scope="row">Ads</th><td>Yes</td><td>No</td></tr>
          <tr><th scope="row">Inactivity rule</th><td>Number can be reclaimed if unused</td><td>Number can be reclaimed after long inactivity</td></tr>
          <tr><th scope="row">Telegram</th><td><span class="status s-sometimes">Sometimes</span></td><td><span class="status s-sometimes">Sometimes</span></td></tr>
          <tr><th scope="row">WhatsApp</th><td><span class="status s-fails">Fails</span></td><td><span class="status s-sometimes">Sometimes</span></td></tr>
          <tr><th scope="row">Google</th><td><span class="status s-works">Works</span></td><td><span class="status s-works">Works</span></td></tr>
        </tbody>
      </table>
    </div>
    <p><strong>Choose TextNow if</strong> you do not have a US phone number, you are in Canada, or you need a number in a few minutes. <strong>Choose Google Voice if</strong> you already have a US number and want a stable, ad-free number for the long term.</p>
    <h3>How to keep a free US number active</h3>
    <p>Free numbers go back to the pool when you stop using them, and the next owner can receive your codes. Send a text or make a call regularly: Talkatone, for example, expects activity at least every 30 days. Check each app's current inactivity rules, as they change from time to time.</p>"""),
        "local": "For Telegram and Google, any working number is fine, so a US number can verify an account opened anywhere. Local US services such as banks, delivery apps and some marketplaces may require a US number and will usually reject VoIP lines. WhatsApp may also expect a number that matches your region.",
        "faqs": [
            ("Where can I get a free US number for OTP?", "TextNow, Google Voice, Talkatone, TextFree and Nextplus all offer free US numbers. In our tests TextNow and Google Voice had the best OTP results."),
            ("Is Google Voice free outside the US?", "Google Voice is meant for personal use in the US and needs an existing US number to set up. Outside the US, TextNow or a paid number are easier options."),
            ("Can I get a free US number without a US phone?", "Yes. TextNow and Talkatone sign up with an email address. Google Voice is the one that requires an existing US number."),
            ("Do free US numbers work for WhatsApp?", "Rarely. Only Google Voice passed some WhatsApp checks in our test. For WhatsApp, a paid number is the realistic choice."),
            ("How long does a free US number last?", "As long as you keep using it. Most free apps reclaim numbers after a period of inactivity, so send a text or make a call regularly."),
        ],
    },
    "ca": {
        "title": "Free Canadian Virtual Number for OTP (2026)",
        "desc": "Free Canadian virtual numbers for OTP verification in 2026, tested on Telegram, WhatsApp and Google, plus cheap options when free numbers fail.",
        "h1": "Free Canadian Virtual Number for OTP Verification",
        "lead": "The best free Canadian virtual number for OTP in our tests was <strong>TextNow</strong>, which offers numbers with Canadian area codes. Canada shares the +1 code with the US, so most free US apps work here too, and so do their limits.",
        "picks": [("textnow", "Best free Canadian number", "Free numbers with Canadian area codes. Passed Google in 9 of 10 attempts and Telegram in 6 of 10."),
                  ("talkatone", "Backup app", "Free US and Canadian numbers with an email signup. Keep it active every 30 days."),
                  ("smsfast", "For WhatsApp", "Canadian numbers that passed Telegram, WhatsApp and Google in our test.")],
        "format": "Canadian numbers use the country code <strong>+1</strong>, the same as the US, followed by a 3-digit area code and a 7-digit number, for example <code>+1 416 555 0142</code> (Toronto) or <code>+1 604 555 0142</code> (Vancouver). From the number alone, apps cannot tell a Canadian number from a US one.",
        "unique": ("shared-plus-one", "Good to know", "Canada Shares +1 With the US: What That Means", """    <p>Because Canada and the US share the +1 country code, most apps treat their numbers the same way. A free US number from TextNow or Talkatone can verify Telegram or Google for an account opened in Canada, and a Canadian number works for US services that only check the country code.</p>
    <p>It matters when a service checks the area code. Canadian banks, government services and some delivery apps may require a Canadian area code, and will usually refuse VoIP lines anyway. For those, use your own mobile number. For everything else, compare options on our <a href="/free-us-virtual-number/">free US virtual number</a> page as well.</p>"""),
        "local": "For Telegram and Google, a Canadian or US number is equally fine. For WhatsApp and local Canadian services, a number with a Canadian area code from a provider that passes carrier checks is the safer choice.",
        "faqs": [
            ("Is there a free Canadian virtual number for verification?", "Yes. TextNow, Talkatone and Nextplus offer free Canadian numbers. TextNow had the best OTP results in our test."),
            ("Can I use a US number in Canada for OTP?", "Usually yes. Canada and the US share +1, so most apps accept either. Local Canadian services may require a Canadian area code."),
            ("Does TextNow give Canadian numbers?", "Yes. TextNow offers free numbers in the US and Canada, and you can pick an area code during signup."),
            ("Which Canadian number works for WhatsApp?", "No free Canadian number was reliable on WhatsApp in our test. SMSFAST Canadian numbers passed every WhatsApp check."),
        ],
    },
    "uk": {
        "title": "Free UK Virtual Number for OTP (2026): What Really Works",
        "desc": "Can you get a free UK virtual number for OTP codes? We tested public +44 numbers and cheap private options on Telegram, WhatsApp and Google.",
        "h1": "Free UK Virtual Number for OTP Verification",
        "lead": "Free private UK numbers are rare: the popular free apps only give US and Canadian numbers. The best free UK virtual number for OTP in our tests was the public site <strong>Quackr</strong>, and it only worked for some Telegram codes. For a private +44 number, " + smsfast_link("SMSFAST") + " passed every check.",
        "picks": [("smsfast", "Best private UK number", "+44 numbers that passed Telegram, WhatsApp and Google in our test, from $0.21."),
                  ("quackr", "Best free UK option", "Public +44 numbers with no signup. Some Telegram codes arrived; Google and WhatsApp failed."),
                  ("hushed", "Disposable UK number", "Private paid UK numbers. Worked on Telegram and Google.")],
        "format": "UK numbers use the country code <strong>+44</strong>. Mobile numbers start with 7 after the country code, for example <code>+44 7700 900142</code>. In the UK the same number is written <code>07700 900142</code>: drop the leading 0 when you add +44.",
        "unique": ("why-rare", "The honest answer", "Why Free Private UK Numbers Are Rare", """    <p>The free number apps that work well in North America, such as TextNow and Google Voice, do not offer +44 numbers. In the UK, free numbers come almost only from public receive-SMS websites, where every code is visible to all visitors and numbers are blocked quickly.</p>
    <p>That leaves two realistic options. For a throwaway signup, try a fresh public number on Quackr. For an account you want to keep, or for WhatsApp, use a cheap private UK number from a provider such as """ + smsfast_link("SMSFAST") + """. It costs less than a coffee and is not shared with strangers.</p>"""),
        "local": "Telegram and Google accept foreign numbers, so a free US number from TextNow can verify an account opened in the UK. UK banks, delivery apps and WhatsApp are more likely to want a local +44 number.",
        "faqs": [
            ("How do I get a free UK phone number to receive SMS?", "Public receive-SMS websites such as Quackr, Receive-SMSS and SMS24 list free +44 numbers. They work only for low-risk signups because every message is public."),
            ("Are free UK numbers private?", "No. Free UK numbers come from public websites, so anyone can read the codes. For a private +44 number you need a paid provider."),
            ("Can I use a US number instead of a UK number?", "For Telegram and Google, usually yes. For WhatsApp and UK services, a local +44 number is more likely to work."),
            ("Which UK number works for WhatsApp?", "No free UK number passed WhatsApp in our test. SMSFAST UK numbers passed every WhatsApp check."),
        ],
    },
    "au": {
        "title": "Free Australian Virtual Number for OTP (2026)",
        "desc": "Free Australian (+61) virtual numbers for OTP codes in 2026: what our tests found, why free options are rare and the cheapest numbers that work.",
        "h1": "Free Australian Virtual Number for OTP Verification",
        "lead": "Australia has the fewest free options of the four countries we test. The best free Australian virtual number for OTP was the public site <strong>Quackr</strong>, which passed only some Telegram checks. For a private +61 number that works, " + smsfast_link("SMSFAST") + " passed every test.",
        "picks": [("smsfast", "Best private +61 number", "Australian numbers that passed Telegram, WhatsApp and Google in our test."),
                  ("quackr", "Best free option", "Public +61 numbers with no signup. Some Telegram codes arrived."),
                  ("hushed", "Disposable number", "Private paid Australian numbers. Worked on Telegram and Google.")],
        "format": "Australian numbers use the country code <strong>+61</strong>. Mobile numbers start with 4 after the country code, for example <code>+61 412 345 678</code>. Locally the same number is written <code>0412 345 678</code>: drop the leading 0 when you add +61.",
        "unique": ("free-options", "What exists", "Free Australian Numbers: Public Sites, Trials and Shared Numbers", """    <p>Free +61 numbers come in three forms. Public receive-SMS websites such as Quackr and SMS24 show every message to everyone. Business phone providers sometimes offer short free trials. A few services offer shared numbers that many customers use at once.</p>
    <p>None of these suits an account you want to keep. Public and shared numbers are quickly blocked by Telegram, WhatsApp and Google, and trials end. For a long-term Australian account, use your own mobile number or a private number rented from a provider such as """ + smsfast_link("SMSFAST") + """."""),
        "local": "Telegram and Google accept foreign numbers, so a free US number can verify an account opened in Australia. Australian banks and WhatsApp are more likely to want a local +61 mobile number.",
        "faqs": [
            ("Can I get a free Australian number for OTP?", "Only public ones. Quackr and SMS24 list free +61 numbers, but every code is public and most numbers are blocked by major apps."),
            ("Do free +61 numbers work for Telegram?", "Sometimes. Quackr's Australian numbers passed some Telegram checks in our test. SMS24 failed."),
            ("What is the cheapest Australian number for verification?", "Pay-per-code services are the cheapest. SMSFAST Australian numbers start from $0.21 per code and passed all three platforms in our test."),
            ("Can I use a foreign number for Australian apps?", "Telegram and Google accept foreign numbers. Australian banks, government services and WhatsApp may require a local +61 number."),
        ],
    },
}


def country_services(cc_):
    free = sorted([s for s in SERVICES if s["type"] != "paid" and cc_ in s["countries"]], key=lambda s: -s["score"])
    paid = sorted([s for s in SERVICES if s["type"] == "paid" and cc_ in s["countries"]], key=lambda s: -s["score"])
    return free + paid


def build_country(cc_):
    c = COUNTRY_CONTENT[cc_]
    meta = COUNTRIES[cc_]
    svcs = country_services(cc_)
    free = [s for s in svcs if s["type"] != "paid"]
    best_free = free[0]["name"] if free else "none"
    plat_summary = []
    for p in PLATFORMS:
        ok = [s["name"] for s in free if s[p] != "fails"]
        plat_summary.append(f"<li><strong>{PLATFORMS[p]['name']}:</strong> " +
                            (", ".join(ok) + " passed at least some checks." if ok else "no free number passed.") + "</li>")
    unique_id, unique_eyebrow, unique_h2, unique_body = c["unique"]
    others = [k for k in COUNTRIES if k != cc_]
    rel = [(COUNTRIES[k]["slug"], "cat-purple", COUNTRIES[k]["code"], f"Free {COUNTRIES[k]['name']} Virtual Number",
            f"Free and cheap {COUNTRIES[k]['code']} numbers for OTP, tested on Telegram, WhatsApp and Google.",
            f"Numbers in {COUNTRIES[k]['name']}") for k in others]
    name_short = {"us": "US", "ca": "Canadian", "uk": "UK", "au": "Australian"}[cc_]
    body = f"""{head(c['title'], c['desc'], meta['slug'], ld_base(meta['slug'], meta['name'], headline=c['h1'], extra=[ld_itemlist('Free ' + name_short + ' virtual numbers for OTP', svcs), ld_faq([(q, strip_tags(a)) for q, a in c['faqs']])]))}{header(cc_)}{breadcrumbs(meta['name'])}
<main id="main">
{page_header(f"{meta['name']} · {meta['code']} · Tested November 2026", c['h1'], c['lead'], accent='purple', trust=[('Services with ' + meta['code'] + ' numbers', str(len(svcs))), ('Free options', str(len(free))), ('Best free', best_free)])}
{jump([('picks', 'Top picks'), ('ranking', 'Test results'), ('format', 'Number format'), (unique_id, SHORT.get(unique_id, unique_h2[:24])), ('paid', 'Paid options'), ('faq', 'FAQ')])}

<section class="band" id="picks" aria-labelledby="picks-title">
  <div class="container">
    <p class="eyebrow">Quick answer</p>
    <h2 id="picks-title">Top Picks for {name_short} Numbers</h2>
{pick_cards(c['picks'])}
  </div>
</section>

<section class="band band-soft" id="ranking" aria-labelledby="ranking-title">
  <div class="container">
    <p class="eyebrow">Test results</p>
    <h2 id="ranking-title">Best Free {name_short} Virtual Numbers for OTP</h2>
    <p class="section-intro">Every service below offers {meta['code']} numbers. Free options are ranked first, paid fallbacks after. See the <a href="/">best free virtual number for OTP</a> for all countries.</p>
{ranking_table(svcs, 'Free ' + name_short + ' virtual numbers ranked by test score')}
    <div class="prose">
      <h3>Which free {name_short} numbers work on Telegram, WhatsApp and Google</h3>
      <ul>{''.join(plat_summary)}</ul>
      <p>Platform guides: <a href="{PLATFORMS['telegram']['slug']}">Telegram</a> · <a href="{PLATFORMS['whatsapp']['slug']}">WhatsApp</a> · <a href="{PLATFORMS['google']['slug']}">Google</a></p>
    </div>
  </div>
</section>

{section('format', 'Number format', name_short + ' Phone Number Format', '    <p>' + c['format'] + '</p>')}

{section(unique_id, unique_eyebrow, unique_h2, unique_body, soft=True)}

{section('local-number', 'Do you need one?', f'Do You Need a Local {name_short} Number?', '    <p>' + c['local'] + '</p>')}

<section class="band band-soft" id="paid" aria-labelledby="paid-title">
  <div class="container">
    <p class="eyebrow">Paid alternatives</p>
    <h2 id="paid-title">Paid {name_short} Numbers When Free Ones Fail</h2>
    <p class="section-intro">Private paid numbers are not shared with strangers and pass more carrier checks, especially on WhatsApp.</p>
{paid_cards(country=cc_)}
  </div>
</section>

{faq_block(f'Free {name_short} Virtual Number: FAQ', c['faqs'])}

{related(rel, 'Free Virtual Numbers in Other Countries')}
{author_box()}
</main>
{footer()}"""
    write(meta["slug"], body)


# --------------------------------------------------------------------------
# Trust and legal pages
# --------------------------------------------------------------------------
def simple_page(path, crumb, title, desc, h1, lead, inner, page_type="WebPage", toc=None, current=None,
                active=None, meta_line=None, robots="index, follow"):
    toc_html = ""
    wrap_cls = "container container-narrow"
    if toc:
        lis = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)
        toc_html = f'<nav class="toc" aria-label="Contents"><p class="toc-title">Contents</p><ol>{lis}</ol></nav>'
        wrap_cls = "container with-toc"
    meta_html = f'\n      <p class="page-meta">{meta_line}</p>' if meta_line else ""
    jsonld = ld_base(path, crumb, page_type=page_type, headline=h1) if robots.startswith("index") else None
    crumbs = breadcrumbs(crumb) if path != "/404.html" else ""
    body = f"""{head(title, desc, path, jsonld, robots=robots)}{header(active)}{crumbs}
<main id="main">
  <header class="page-header">
    <div class="container">
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>{meta_html}
    </div>
  </header>
  <div class="page-body">
    <div class="{wrap_cls}">
      {toc_html}
      <article class="legal">
{inner}
      </article>
    </div>
  </div>
</main>
{footer(current)}"""
    write(path, body)


def build_methodology():
    inner = """        <h2 id="protocol">Our test protocol</h2>
        <p>Every month we test each service in our ranking from scratch. For every service we request <strong>10 verification codes per platform</strong> from Telegram, WhatsApp and Google, using numbers from each country the service offers: the US, Canada, the UK and Australia. A request counts as a success when the code arrives within 5 minutes and can be entered.</p>
        <p>We use fresh test accounts on real phones and browsers, and delete them after the test. Each cycle takes about two weeks; the date of the last test is shown next to every service.</p>

        <h2 id="score">How the score is calculated</h2>
        <p>The score out of 10 combines four criteria. OTP delivery has the biggest weight because it is what most people need.</p>
        <div class="table-wrap">
          <table>
            <thead><tr><th scope="col">Criterion</th><th scope="col">Weight</th><th scope="col">What we measure</th></tr></thead>
            <tbody>
              <tr><th scope="row">OTP delivery</th><td>40%</td><td>Share of the 30 code requests (10 per platform) that succeeded</td></tr>
              <tr><th scope="row">Privacy</th><td>20%</td><td>Whether the number is private to you or visible to everyone</td></tr>
              <tr><th scope="row">Ease of use</th><td>20%</td><td>Signup steps, ads, keep-alive rules, how fast you get a number</td></tr>
              <tr><th scope="row">Country coverage</th><td>20%</td><td>Numbers available in the US, Canada, the UK and Australia</td></tr>
            </tbody>
          </table>
        </div>
        <p>Each criterion is rated from 0 to 10, multiplied by its weight and added up. Two services with similar delivery can end up with different scores if one shows your messages to everyone or covers only one country.</p>

        <h2 id="labels">Status labels</h2>
        <ul>
          <li><span class="status s-works">Works</span> 7 or more of 10 codes received on that platform.</li>
          <li><span class="status s-sometimes">Sometimes</span> 3 to 6 of 10 codes received.</li>
          <li><span class="status s-fails">Fails</span> 0 to 2 of 10 codes received.</li>
        </ul>

        <h2 id="what-we-dont-do">What we do not do</h2>
        <p>We do not try to get around platform anti-fraud checks, we do not create accounts in bulk and we do not publish methods for doing so. We only test what an ordinary person can do with each service.</p>

        <h2 id="free-first">Free first, paid second</h2>
        <p>Our ranking lists free services first, because that is what most people look for. Paid services are scored with the same tests and listed after them as fallbacks. Business relationships never change the order of free services. See our <a href="/affiliate-disclosure/">Affiliate Disclosure</a>.</p>

        <h2 id="changelog">Ranking changelog</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th scope="col">Date</th><th scope="col">Change</th></tr></thead>
            <tbody>
              <tr><td><time datetime="2026-11-22">Nov 22, 2026</time></td><td>First published ranking: 12 services tested across Telegram, WhatsApp and Google in 4 countries.</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="report">Suggest a service or report an error</h2>
        <p>Did a number stop working, or should we test a new service? <a href="/contact/">Contact us</a> and choose "Correction" or "Suggest a service".</p>"""
    simple_page("/methodology/", "How We Test", "How We Test Free Virtual Numbers for OTP | " + BRAND,
                "Our monthly test protocol: how we request OTP codes from Telegram, WhatsApp and Google, how scores are calculated and what changed in the ranking.",
                "How We Test Free Virtual Numbers",
                "Every number in our ranking is tested by hand, every month, on Telegram, WhatsApp and Google. Here is exactly how.",
                inner, page_type="Article", active="methodology",
                toc=[("protocol", "Test protocol"), ("score", "How the score works"), ("labels", "Status labels"),
                     ("what-we-dont-do", "What we do not do"), ("free-first", "Free first, paid second"),
                     ("changelog", "Ranking changelog"), ("report", "Report an error")],
                meta_line=f'Last updated: <time datetime="{DATA["updated"]}">November 22, 2026</time>')


def build_about():
    inner = """        <!-- Replace with real author details before launch (TZ 4.2) -->
        <p class="draft-note">Placeholder author profile. Replace with the real author's name, photo, bio and profiles before launch.</p>
        <h2 id="mission">Our mission</h2>
        <p>Most lists of "free virtual numbers" are written by companies that sell numbers. We started OTP Number Lab to answer one question honestly: which free numbers actually receive verification codes today? So we test them, every month, and publish the results.</p>

        <h2 id="team">Who we are</h2>
        <div class="card card-feature" id="alex-morgan">
          <div class="author-box">
            <div class="author-avatar" aria-hidden="true">AM</div>
            <div>
              <h3>Alex Morgan</h3>
              <p class="author-bio">Lead tester. Reviews privacy tools and phone number services, and runs our monthly test cycle across the US, Canada, the UK and Australia.</p>
            </div>
          </div>
        </div>

        <h2 id="editorial">Editorial policy</h2>
        <ul>
          <li><strong>Tested, not copied.</strong> Every result on the site comes from our own tests, with the test date shown.</li>
          <li><strong>Updated monthly.</strong> Services that stop working move down or leave the ranking.</li>
          <li><strong>Corrections welcome.</strong> If something is wrong, tell us and we fix it, noting the change in the <a href="/methodology/#changelog">changelog</a>.</li>
          <li><strong>No bypass guides.</strong> We do not publish ways to get around platform security checks.</li>
        </ul>

        <h2 id="money">How we make money</h2>
        <p>The site links to SMSFAST, a paid number service, and may earn money from it. This never changes the order of free services. Details are in our <a href="/affiliate-disclosure/">Affiliate Disclosure</a>.</p>

        <h2 id="contact">Contact us</h2>
        <p>Questions, corrections or suggestions: <a href="/contact/">contact us</a>.</p>"""
    simple_page("/about/", "About", f"About {BRAND} | Who Tests the Numbers",
                "Who runs OTP Number Lab, how we test free virtual numbers for OTP, our editorial policy and how the site is funded.",
                f"About {BRAND}", "Independent, hands-on tests of free virtual numbers for verification codes.",
                inner, page_type="AboutPage", current="/about/")


def build_terms():
    inner = """        <!-- Remove after legal review -->
        <p class="draft-note">Draft for legal review. Final wording, company details and governing law will be confirmed before launch.</p>
        <h2 id="acceptance">1. Acceptance of these terms</h2>
        <p>By using this website you agree to these Terms of Use. If you do not agree, please do not use the site.</p>
        <h2 id="information">2. Information only</h2>
        <p>Our rankings and articles are for general information. Test results describe what happened during our test cycle and may change at any time. We do not guarantee that any service will work for you, stay available or keep its current prices.</p>
        <h2 id="no-affiliation">3. No affiliation with platforms</h2>
        <p>We are not affiliated with, endorsed by or sponsored by Telegram, WhatsApp, Meta, Google or any other platform mentioned on this site. All trademarks belong to their owners.</p>
        <h2 id="acceptable-use">4. Acceptable use</h2>
        <p>You may not use information from this site to commit fraud, impersonate others, create accounts in bulk, harass anyone or break the terms of any platform. Use virtual numbers only for lawful purposes, such as protecting your own privacy.</p>
        <h2 id="third-party">5. Third-party services and links</h2>
        <p>The site links to SMSFAST and mentions other third-party services. They are run by others under their own terms and privacy policies. We are not responsible for their content, availability or practices.</p>
        <h2 id="ip">6. Intellectual property</h2>
        <p>The text, test data, design and code of this site belong to OTP Number Lab unless stated otherwise. You may quote short parts with a link to the source.</p>
        <h2 id="liability">7. Limitation of liability</h2>
        <p>The site is provided "as is". To the extent the law allows, we are not liable for any loss arising from your use of the site or of any service mentioned on it, including lost accounts or verification codes.</p>
        <h2 id="law">8. Governing law</h2>
        <p>These terms are governed by the laws of <strong>[to be confirmed]</strong>.</p>
        <h2 id="changes">9. Changes</h2>
        <p>We may update these terms. The date at the top of the page shows the latest version.</p>
        <h2 id="contact">10. Contact</h2>
        <p>Questions about these terms: <a href="/contact/">contact us</a>.</p>"""
    simple_page("/terms/", "Terms of Use", f"Terms of Use | {BRAND}",
                "Terms of use for OTP Number Lab: information-only rankings, acceptable use, third-party services and limitation of liability.",
                "Terms of Use", "The rules for using this website and its rankings.", inner,
                toc=[("acceptance", "1. Acceptance"), ("information", "2. Information only"), ("no-affiliation", "3. No affiliation"),
                     ("acceptable-use", "4. Acceptable use"), ("third-party", "5. Third parties"), ("ip", "6. Intellectual property"),
                     ("liability", "7. Liability"), ("law", "8. Governing law"), ("changes", "9. Changes"), ("contact", "10. Contact")],
                current="/terms/",
                meta_line=f'Effective date: <time datetime="{DATA["updated"]}">November 22, 2026</time>')


def build_affiliate():
    inner = """        <!-- Confirm the actual relationship with SMSFAST before launch -->
        <p class="draft-note">Confirm and describe the actual relationship with SMSFAST (partnership, commission or common ownership) before launch.</p>
        <h2 id="summary">Summary</h2>
        <p>OTP Number Lab links to <strong>SMSFAST</strong>, a paid virtual number service. We may receive compensation from SMSFAST when visitors use it. Other services in our ranking are mentioned by name only, without links, and we receive nothing from them.</p>
        <h2 id="ranking">How this affects the ranking</h2>
        <ul>
          <li>Free services are ranked first and are ordered only by our test results.</li>
          <li>SMSFAST is scored with exactly the same monthly tests as every other service.</li>
          <li>We would remove or move down SMSFAST if it stopped passing our tests.</li>
        </ul>
        <h2 id="links">How links are marked</h2>
        <p>Links to SMSFAST are shown as buttons labelled "Get number" or as text links naming SMSFAST, and open in a new tab. No other external service is linked from our ranking.</p>
        <h2 id="rules">Disclosure rules</h2>
        <p>We follow the disclosure principles of the US Federal Trade Commission (FTC) and the UK Competition and Markets Authority (CMA) and Advertising Standards Authority (ASA): relationships that could affect how you read our content are stated clearly.</p>
        <h2 id="questions">Questions</h2>
        <p>If anything here is unclear, <a href="/contact/">contact us</a>.</p>"""
    simple_page("/affiliate-disclosure/", "Affiliate Disclosure", f"Affiliate Disclosure | {BRAND}",
                "How OTP Number Lab is funded, our relationship with SMSFAST and why it never changes the order of free services.",
                "Affiliate Disclosure", "How the site is funded, stated plainly.", inner, current="/affiliate-disclosure/",
                meta_line=f'Last updated: <time datetime="{DATA["updated"]}">November 22, 2026</time>')


def build_404():
    inner = """        <p>The page you were looking for does not exist or has moved. These are the most visited pages:</p>
        <p><a class="btn btn-primary" href="/#ranking">See the ranking</a></p>
        <ul>
          <li><a href="/free-virtual-number-for-telegram/">Free virtual number for Telegram</a></li>
          <li><a href="/free-virtual-number-for-whatsapp/">Free virtual number for WhatsApp</a></li>
          <li><a href="/free-virtual-number-for-google-verification/">Free virtual number for Google</a></li>
        </ul>"""
    simple_page("/404.html", "Page Not Found", f"Page Not Found | {BRAND}", "This page does not exist.",
                "Page Not Found", "Sorry, we could not find that page.", inner, robots="noindex, follow")


# --------------------------------------------------------------------------
# sitemap.xml and robots.txt
# --------------------------------------------------------------------------
SITEMAP_PATHS = ["/"] + [PLATFORMS[p]["slug"] for p in PLATFORMS] + [COUNTRIES[c]["slug"] for c in COUNTRIES] + \
                ["/methodology/", "/about/", "/contact/", "/privacy-policy/", "/terms/", "/affiliate-disclosure/"]


def build_sitemap():
    urls = "\n".join(f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{DATA['updated']}</lastmod></url>" for p in SITEMAP_PATHS)
    (SITE / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    print("wrote site/sitemap.xml, site/robots.txt")


if __name__ == "__main__":
    for p in PLATFORMS:
        build_platform(p)
    for c in COUNTRIES:
        build_country(c)
    build_methodology()
    build_about()
    build_terms()
    build_affiliate()
    build_404()
    build_sitemap()
