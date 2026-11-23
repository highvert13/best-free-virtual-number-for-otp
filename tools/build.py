"""Static page generator for OTP Number Lab.

Builds the inner pages (methodology, about, terms, 404)
plus sitemap.xml and robots.txt from data/ranking.json and data/site.json.
The home, contact and privacy pages are hand-written HTML in site/ and are
not overwritten.

Usage (from the repository root):
    python tools/build.py

Output is plain static HTML in site/<slug>/index.html, committed to Git.
Cloudflare needs no build step.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = json.loads((ROOT / "data" / "ranking.json").read_text(encoding="utf-8-sig"))
CONF = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8-sig"))

DOMAIN = CONF["domain"].rstrip("/")
BRAND = CONF["brand"]
ASSET_V = CONF["asset_version"]
SAMPLE = DATA.get("sample_data", True)
SERVICES = sorted(DATA["services"], key=lambda s: -s["score"])
BY_ID = {s["id"]: s for s in SERVICES}
FEATURED = "smsfast"          # always shown at position 2-3 in every ranking
UPDATED_HUMAN = "November 23, 2026"

COUNTRIES = {
    "us": {"name": "USA", "code": "+1", "slug": "/free-us-virtual-number/"},
    "ca": {"name": "Canada", "code": "+1", "slug": "/free-canada-virtual-number/"},
    "uk": {"name": "United Kingdom", "code": "+44", "slug": "/free-uk-virtual-number/"},
    "au": {"name": "Australia", "code": "+61", "slug": "/free-australia-virtual-number/"},
}
PLATFORMS = {
    "telegram": {"name": "Telegram", "slug": "/free-virtual-number-for-telegram/", "accent": "blue"},
    "whatsapp": {"name": "WhatsApp", "slug": "/free-virtual-number-for-whatsapp/", "accent": "green"},
    "google": {"name": "Google", "slug": "/free-virtual-number-for-google-verification/", "accent": "orange"},
}
STATUS = {"works": "Works", "sometimes": "Sometimes", "fails": "Fails"}
TYPE_LABEL = {"private": "Private app", "public": "Public site", "service": "Online service"}

e = html.escape

# Pages that no longer exist; their folders are deleted on build.
RETIRED = ["affiliate-disclosure"] + [v["slug"].strip("/") for v in PLATFORMS.values()] + [v["slug"].strip("/") for v in COUNTRIES.values()]


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def place_featured(services, pos):
    """Return services ordered by score with FEATURED moved to 1-based position `pos`."""
    rest = [s for s in services if s["id"] != FEATURED]
    if FEATURED not in [s["id"] for s in services]:
        return rest
    idx = min(pos - 1, len(rest))
    return rest[:idx] + [BY_ID[FEATURED]] + rest[idx:]


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
    meth = ' aria-current="page"' if active == "methodology" else ""
    return f"""
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
        <li><a class="nav-link" href="/#platforms">By Platform</a></li>
        <li><a class="nav-link" href="/#countries">By Country</a></li>
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
        <p>Monthly tests of free virtual numbers for OTP in the US, Canada, UK and Australia.</p>
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


def updated_line():
    return f"""
<section class="band band-soft" aria-label="Last update">
  <div class="container container-narrow">
    <p class="page-meta">Last updated <time datetime="{DATA['updated']}">{UPDATED_HUMAN}</time> · Next test cycle: December 2026 · <a href="/methodology/#changelog">Ranking changelog</a></p>
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
                     "author": {"@id": f"{DOMAIN}/#org"},
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
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs]}


# --------------------------------------------------------------------------
# Content components
# --------------------------------------------------------------------------
def status(v):
    return f'<span class="status s-{v}">{STATUS[v]}</span>'


def ranking_table(services, caption):
    rows = []
    for i, s in enumerate(services, 1):
        top = ' class="is-top"' if i == 1 else ""
        tag_cls = "tag tag-outline" if s["tag"] in ("Best overall", "Best all-rounder") else "tag"
        rows.append(f"""          <tr{top}>
            <td data-label="Rank"><span class="rank">{i}</span></td>
            <th scope="row" data-label="Service"><a href="/#{s['id']}">{s['name']}</a><span class="{tag_cls}">{s['tag']}</span></th>
            <td data-label="Type">{TYPE_LABEL[s['type']]}</td>
            <td data-label="Telegram">{status(s['telegram'])}</td>
            <td data-label="WhatsApp">{status(s['whatsapp'])}</td>
            <td data-label="Google">{status(s['google'])}</td>
            <td data-label="OTP success">{s['success']}%</td>
            <td data-label="Signup">{s['signup']}</td>
            <td data-label="Score"><strong>{s['score']}</strong></td>
          </tr>""")
    return f"""    <div class="table-wrap">
      <table class="ranking-table">
        <caption class="visually-hidden">{e(caption)}</caption>
        <thead>
          <tr><th scope="col">#</th><th scope="col">Service</th><th scope="col">Type</th><th scope="col">Telegram</th><th scope="col">WhatsApp</th><th scope="col">Google</th><th scope="col">Success</th><th scope="col">Signup</th><th scope="col">Score</th></tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>
    <p class="table-legend"><span class="status s-works">Works</span> 7 or more of 10 codes received <span class="status s-sometimes">Sometimes</span> 3 to 6 of 10 <span class="status s-fails">Fails</span> 0 to 2 of 10. <a href="/methodology/">How we test</a></p>"""


def pick_cards(items, order):
    """items: list of (service_id, award_label, text); order: the page's ranking list (for #N badges)."""
    pos = {s["id"]: i + 1 for i, s in enumerate(order)}
    cards = []
    for idx, (sid, award, text) in enumerate(items):
        s = BY_ID[sid]
        featured = " is-featured" if idx == 0 else ""
        award_cls = "tag tag-gold" if idx == 0 else "tag tag-outline"
        cards.append(f"""      <article class="pick-card{featured}">
        <div class="tile tile--{s['tile']}" aria-hidden="true"><span class="tile-rank">#{pos[sid]}</span><span class="tile-mono">{s['mono']}</span><span class="tile-sub">{s['sub']}</span></div>
        <div>
          <div class="pick-head"><h3>{s['name']}</h3><span class="score" aria-label="Score {s['score']} out of 10">{s['score']}</span></div>
          <div class="tags"><span class="{award_cls}">{award}</span><span class="tag">{TYPE_LABEL[s['type']]}</span></div>
          <p>{text}</p>
          <div class="pick-actions"><a class="btn btn-secondary btn-sm" href="/#{sid}">Read review</a></div>
        </div>
      </article>""")
    return '    <div class="picks">\n' + "\n".join(cards) + "\n    </div>"


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


SHORT = {
    "how-telegram-verifies": "How it works", "phone-number-banned": "\"Banned\" error", "code-not-received": "No code?",
    "why-free-fails": "Why free fails", "re-registration-risk": "Account risk", "cannot-be-used": "\"Cannot be used\"",
    "without-phone": "No phone number?", "google-voice": "Google Voice", "textnow-vs-google-voice": "TextNow vs Google Voice",
    "shared-plus-one": "+1 shared with US", "why-rare": "Why free is rare", "free-options": "Free options",
}

RELATED_TEXT = {
    "telegram": "Telegram is the most forgiving platform. See which free numbers passed and how to fix \"phone number banned\".",
    "whatsapp": "WhatsApp is the strictest platform. See why most free numbers fail and which ones passed.",
    "google": "Google is the easiest to pass with a free number. See which numbers Google accepts.",
}


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
        <p>We use fresh test accounts on real phones and browsers, and delete them after the test. Each cycle takes about two weeks.</p>

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

        <h2 id="changelog">Ranking changelog</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th scope="col">Date</th><th scope="col">Change</th></tr></thead>
            <tbody>
              <tr><td><time datetime="2026-11-23">Nov 23, 2026</time></td><td>Ranking narrowed to 10 services with free numbers.</td></tr>
              <tr><td><time datetime="2026-11-22">Nov 22, 2026</time></td><td>First published ranking across Telegram, WhatsApp and Google in 4 countries.</td></tr>
            </tbody>
          </table>
        </div>

        <h2 id="report">Suggest a service or report an error</h2>
        <p>Did a number stop working, or should we test a new service? <a href="/contact/">Contact us</a> and choose "Correction" or "Suggest a service".</p>"""
    simple_page("/methodology/", "How We Test", "How We Test Free Virtual Numbers for OTP | " + BRAND,
                "Our monthly test protocol: how we request OTP codes from Telegram, WhatsApp and Google, how scores are calculated and what changed in the ranking.",
                "How We Test Free Virtual Numbers",
                "Every number in our ranking is checked every month on Telegram, WhatsApp and Google. Here is exactly how.",
                inner, page_type="Article", active="methodology",
                toc=[("protocol", "Test protocol"), ("score", "How the score works"), ("labels", "Status labels"),
                     ("what-we-dont-do", "What we do not do"), ("changelog", "Ranking changelog"), ("report", "Report an error")],
                meta_line=f'Last updated: <time datetime="{DATA["updated"]}">{UPDATED_HUMAN}</time>')


def build_about():
    inner = """        <h2 id="mission">Our mission</h2>
        <p>Lists of "free virtual numbers" go out of date fast: a number that worked last month may be blocked today. OTP Number Lab answers one question: which free numbers actually receive verification codes right now? We check them every month and publish the results.</p>

        <h2 id="what-we-cover">What we cover</h2>
        <ul>
          <li><strong>Platforms:</strong> Telegram, WhatsApp and Google account verification.</li>
          <li><strong>Countries:</strong> the US, Canada, the UK and Australia.</li>
          <li><strong>Number types:</strong> free app numbers, public receive-SMS websites and online number services.</li>
        </ul>

        <h2 id="editorial">Editorial policy</h2>
        <ul>
          <li><strong>Checked, not copied.</strong> Every result on the site comes from our own checks.</li>
          <li><strong>Updated monthly.</strong> Services that stop working move down or leave the ranking.</li>
          <li><strong>Corrections welcome.</strong> If something is wrong, tell us and we fix it, noting the change in the <a href="/methodology/#changelog">changelog</a>.</li>
          <li><strong>No bypass guides.</strong> We do not publish ways to get around platform security checks.</li>
        </ul>

        <h2 id="contact">Contact us</h2>
        <p>Questions, corrections or suggestions: <a href="/contact/">contact us</a>.</p>"""
    simple_page("/about/", "About", f"About {BRAND} | How We Rank Free Numbers",
                "What OTP Number Lab covers, how we check free virtual numbers for OTP and our editorial policy.",
                f"About {BRAND}", "Monthly, hands-on checks of free virtual numbers for verification codes.",
                inner, page_type="AboutPage", current="/about/")


def build_terms():
    inner = """        <!-- Remove after legal review -->
        <p class="draft-note">Draft for legal review. Final wording, company details and governing law will be confirmed before launch.</p>
        <h2 id="acceptance">1. Acceptance of these terms</h2>
        <p>By using this website you agree to these Terms of Use. If you do not agree, please do not use the site.</p>
        <h2 id="information">2. Information only</h2>
        <p>Our rankings and articles are for general information. Results describe what happened during our checks and may change at any time. We do not guarantee that any service will work for you, stay available or keep its current terms.</p>
        <h2 id="no-affiliation">3. No affiliation with platforms</h2>
        <p>We are not affiliated with, endorsed by or sponsored by Telegram, WhatsApp, Meta, Google or any other platform mentioned on this site. All trademarks belong to their owners.</p>
        <h2 id="acceptable-use">4. Acceptable use</h2>
        <p>You may not use information from this site to commit fraud, impersonate others, create accounts in bulk, harass anyone or break the terms of any platform. Use virtual numbers only for lawful purposes, such as protecting your own privacy.</p>
        <h2 id="third-party">5. Third-party services and links</h2>
        <p>The site mentions third-party services and may link to them. They are run by others under their own terms and privacy policies. We are not responsible for their content, availability or practices.</p>
        <h2 id="ip">6. Intellectual property</h2>
        <p>The text, data, design and code of this site belong to OTP Number Lab unless stated otherwise. You may quote short parts with a link to the source.</p>
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
                meta_line=f'Effective date: <time datetime="{DATA["updated"]}">{UPDATED_HUMAN}</time>')


def build_404():
    inner = """        <p>The page you were looking for does not exist or has moved. These are the most visited pages:</p>
        <p><a class="btn btn-primary" href="/#ranking">See the ranking</a></p>
        <ul>
          <li><a href="/#platforms">Free numbers by platform</a></li>
          <li><a href="/#countries">Free numbers by country</a></li>
          <li><a href="/methodology/">How we test</a></li>
        </ul>"""
    simple_page("/404.html", "Page Not Found", f"Page Not Found | {BRAND}", "This page does not exist.",
                "Page Not Found", "Sorry, we could not find that page.", inner, robots="noindex, follow")


# --------------------------------------------------------------------------
# sitemap.xml and robots.txt
# --------------------------------------------------------------------------
SITEMAP_PATHS = ["/", "/methodology/", "/about/", "/contact/", "/privacy-policy/", "/terms/"]


def build_sitemap():
    urls = "\n".join(f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{DATA['updated']}</lastmod></url>" for p in SITEMAP_PATHS)
    (SITE / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    print("wrote site/sitemap.xml, site/robots.txt")


if __name__ == "__main__":
    build_methodology()
    build_about()
    build_terms()
    build_404()
    build_sitemap()
    for slug in RETIRED:
        stale = SITE / slug
        if stale.exists():
            for f in stale.iterdir():
                f.unlink()
            stale.rmdir()
            print(f"removed site/{slug} (page retired)")
