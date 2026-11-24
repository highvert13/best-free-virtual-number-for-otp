"""Blog: hub (/blog/), explainer articles, the monthly data story built from App
Store reviews, and the auto-updated home page blocks.

Fix articles are defined in tools/fixes.py and listed here under "Fixes".
Called from tools/build.py:  blog.build_all(build_module)
"""
import math
import re

import fixes

REVIEWS = fixes.REVIEWS
APPS = fixes.APPS
human_date = fixes.human_date

CATEGORIES = {
    "fixes": "Fixes",
    "explainers": "How it works",
    "safety": "Privacy & safety",
    "data": "Data",
}
CAT_ACCENT = {"fixes": "orange", "explainers": "blue", "safety": "green", "data": "purple"}


# --------------------------------------------------------------------------
# Explainer and safety articles
# --------------------------------------------------------------------------
EXPLAINERS = [
    {
        "slug": "what-is-a-voip-number",
        "category": "explainers",
        "date": "2026-11-24",
        "label": "VoIP numbers",
        "card": "What makes a number \"VoIP\", how apps find out, and why so many of them refuse these numbers.",
        "title": "What Is a VoIP Number and Why Do Apps Block It?",
        "desc": "A VoIP number runs over the internet instead of a SIM. Learn how apps detect VoIP numbers, why many block them for verification, and what it means for you.",
        "h1": "What Is a VoIP Number, and Why Do So Many Apps Block It?",
        "answer": "A VoIP number is a phone number that works over the internet rather than through a mobile carrier's SIM. Apps can look up a number's line type before sending a code, and many refuse VoIP numbers because they are cheap and quick to get in bulk, which makes them popular for fake accounts.",
        "sections": [
            ("definition", "What a VoIP number is", """    <p>VoIP stands for Voice over Internet Protocol. A VoIP number is assigned by an internet calling provider instead of a mobile network. Calls and texts reach you through an app or a website, not through a SIM card in your phone.</p>
    <p>Free number apps such as TextNow, Google Voice, Talkatone and TextFree all give you VoIP numbers. So do many business phone systems. The number looks like any other: a US VoIP number still starts with +1 and has ten digits.</p>
    <div class="table-wrap">
      <table class="compare-table">
        <thead><tr><th scope="col">Type</th><th scope="col">What it is</th><th scope="col">Example</th></tr></thead>
        <tbody>
          <tr><th scope="row">Mobile</th><td>A number tied to a SIM from a mobile carrier</td><td>Your phone contract or prepaid SIM</td></tr>
          <tr><th scope="row">Fixed VoIP</th><td>Internet phone service tied to a physical address</td><td>A home phone from a cable provider</td></tr>
          <tr><th scope="row">Non-fixed VoIP</th><td>Internet number you can use from anywhere, often free and created in minutes</td><td>Free number apps</td></tr>
        </tbody>
      </table>
    </div>"""),
            ("detection", "How apps can tell", """    <p>Every phone number belongs to a carrier, and that carrier is recorded in industry databases. Verification providers offer a <strong>line type lookup</strong>: send them a number, and they answer with the carrier name and whether the line is mobile, landline, fixed VoIP or non-fixed VoIP.</p>
    <p>Many apps run this lookup the moment you type your number, before any code is sent. If the answer is "non-fixed VoIP", the app may refuse the number with a vague message such as "This number is not supported", or simply never send the code.</p>"""),
            ("why-block", "Why apps block them", """    <p>Non-fixed VoIP numbers are free or very cheap and can be created in large numbers in a few minutes. That makes them a favourite tool for spam accounts, fake reviews and bonus abuse. For an app, blocking them removes a large share of fake signups at the cost of turning away some honest users.</p>
    <p>Each platform draws the line differently. Messaging apps that tie an account to a phone number, such as WhatsApp, tend to be the strictest. Other services accept VoIP numbers but watch for numbers that have been used for many accounts.</p>"""),
            ("what-to-do", "What it means for you", """    <ul>
      <li><strong>If a code never arrives,</strong> the number type is the most likely reason, not your phone.</li>
      <li><strong>Retrying the same number rarely helps:</strong> the lookup gives the same answer every time.</li>
      <li><strong>A voice-call option</strong> sometimes works where SMS does not, but not if the number was refused outright.</li>
      <li><strong>Compare options</strong> in our <a href="/#ranking">ranking</a>, which notes the number type of every service.</li>
    </ul>"""),
        ],
        "faqs": [
            ("Is a Google Voice number a VoIP number?", "Yes. Google Voice numbers are internet numbers, and line type lookups usually report them as VoIP."),
            ("Can I tell if my number is VoIP?", "Not from the digits alone. A line type lookup shows it, and the app that gave you the number usually says whether it is an internet number."),
            ("Is it illegal to use a VoIP number for verification?", "No. Using a VoIP number for your own accounts is legal. Apps are simply free to refuse them."),
        ],
        "related": ["sms-short-codes-explained", "whatsapp-not-sending-verification-code", "textnow-not-receiving-verification-codes"],
    },
    {
        "slug": "sms-short-codes-explained",
        "category": "explainers",
        "date": "2026-11-24",
        "label": "Short codes",
        "card": "Why some verification texts come from 5- or 6-digit senders, and why those often never reach virtual numbers.",
        "title": "SMS Short Codes: Why Some Codes Never Reach Virtual Numbers",
        "desc": "Many verification codes are sent from 5- or 6-digit short codes. Learn what short codes are, why they often fail on virtual and foreign numbers, and what to try instead.",
        "h1": "SMS Short Codes: Why Some Verification Codes Never Reach Virtual Numbers",
        "answer": "A short code is a 5- or 6-digit number that companies use to send text messages in bulk, including verification codes. Short-code messages travel over carrier routes that many virtual number apps do not receive, and they only work inside one country, so codes sent this way often never arrive on a VoIP or foreign number.",
        "sections": [
            ("what-it-is", "The basics", """    <p>When a bank, retailer or app texts you a code from a number like <code>32665</code> or <code>227898</code>, that sender is a <strong>short code</strong>. In the US, short codes are leased through a central registry and approved by each mobile carrier before use. Companies like them because they can send large volumes of messages quickly and reliably to normal mobile phones.</p>"""),
            ("why-fail", "Why they fail", """    <p>Short codes were built for mobile carrier networks. Delivery depends on agreements between the sender's provider and each carrier, and many internet number providers are not part of those routes. The result: the message is accepted by the sender, then silently dropped before it reaches a VoIP number.</p>
    <p>Short codes are also national. A US short code cannot reach a UK or Australian number, so a service that only sends codes by US short code cannot verify a foreign number at all.</p>
    <div class="table-wrap">
      <table class="compare-table">
        <thead><tr><th scope="col">Sender type</th><th scope="col">Looks like</th><th scope="col">Reaches virtual numbers?</th></tr></thead>
        <tbody>
          <tr><th scope="row">Short code</th><td>5–6 digits</td><td>Often not</td></tr>
          <tr><th scope="row">Long code</th><td>A normal phone number</td><td>Usually, if the app accepts VoIP</td></tr>
          <tr><th scope="row">Toll-free number</th><td>+1 800, 888, 877…</td><td>Varies by provider</td></tr>
          <tr><th scope="row">Voice call</th><td>An automated call</td><td>Usually</td></tr>
        </tbody>
      </table>
    </div>"""),
            ("signs", "How to recognise it", """    <ul>
      <li>Normal texts from friends arrive on the number, but codes from one particular company never do.</li>
      <li>The same service sends codes fine to your mobile number.</li>
      <li>Past messages from that company in your mobile inbox came from a 5- or 6-digit sender.</li>
    </ul>"""),
            ("what-to-do", "What to try", """    <ul>
      <li><strong>Ask for a voice call</strong> if the service offers one.</li>
      <li><strong>Use email or an authenticator app</strong> where the service allows it instead of SMS.</li>
      <li><strong>Use a number in the same country</strong> as the service sending the code.</li>
      <li><strong>Pick a different number</strong> for that service from our <a href="/#ranking">ranking</a> if it keeps failing.</li>
    </ul>"""),
        ],
        "faqs": [
            ("Can Google Voice receive short codes?", "Often not. Many short-code senders do not deliver to Google Voice, which is a common reason codes from banks never arrive there."),
            ("Why do I get normal texts but not verification codes?", "Normal texts come from regular numbers. Verification codes often come from short codes, which use different routes that many virtual numbers do not receive."),
            ("Can a short code reach a number in another country?", "No. Short codes work inside one country only."),
        ],
        "related": ["what-is-a-voip-number", "google-voice-not-receiving-verification-codes", "textnow-not-receiving-verification-codes"],
    },
    {
        "slug": "recycled-phone-numbers-and-your-accounts",
        "category": "safety",
        "date": "2026-11-24",
        "label": "Recycled numbers",
        "card": "Free numbers are reassigned to new users. Here's what that means for accounts still linked to your old number.",
        "title": "Recycled Phone Numbers: What Happens to Your Accounts",
        "desc": "Free virtual numbers are reassigned when you stop using them. Learn the risks of recycled numbers for your accounts and how to protect yourself before you lose a number.",
        "h1": "Recycled Phone Numbers: What Happens to Your Accounts When You Lose a Number",
        "answer": "When you stop using a phone number, the provider eventually gives it to someone else. Any account that still uses that number for login codes or recovery can then be reached by the new owner. Before you let a number go, move every account to another number or, better, to an authenticator app.",
        "sections": [
            ("how", "How recycling works", """    <p>Phone numbers are a limited resource, so carriers and number apps reuse them. Free number apps usually reclaim a number after a period without calls or texts. Mobile carriers reassign numbers after a contract ends. The next person to get the number receives every text sent to it, including verification codes meant for you.</p>
    <p>Researchers at Princeton University looked at recycled mobile numbers in 2021 and found that a large share of them were still linked to the previous owner's online accounts.</p>"""),
            ("risks", "What can go wrong", """    <div class="table-wrap">
      <table class="compare-table">
        <thead><tr><th scope="col">Risk</th><th scope="col">How it happens</th></tr></thead>
        <tbody>
          <tr><th scope="row">Account takeover</th><td>The new owner uses "forgot password" and receives your reset code.</td></tr>
          <tr><th scope="row">Locked out</th><td>You can't sign in on a new device because the code goes to a number you no longer have.</td></tr>
          <tr><th scope="row">Messaging accounts moved</th><td>On WhatsApp, the new owner can register the number and the account moves to their phone.</td></tr>
          <tr><th scope="row">Private messages</th><td>Texts from friends or services keep arriving at the old number.</td></tr>
        </tbody>
      </table>
    </div>"""),
            ("protect", "How to protect yourself", """    <ol class="steps">
      <li><h3>Keep free numbers active</h3><p>Most free apps reclaim numbers after inactivity. Send a text or make a call regularly while you still use the number.</p></li>
      <li><h3>List what uses the number</h3><p>Check messaging apps, email, banking, shopping and social accounts for this phone number.</p></li>
      <li><h3>Switch to an authenticator app</h3><p>Where a service offers it, replace SMS codes with an authenticator app or a passkey.</p></li>
      <li><h3>Update recovery options</h3><p>Change the recovery phone to a number you will keep, and add a recovery email.</p></li>
      <li><h3>Only then let the number go</h3><p>Remove the number from each account before you close the app or cancel the line.</p></li>
    </ol>"""),
        ],
        "faqs": [
            ("How long until a free number is reassigned?", "It depends on the app. Many reclaim numbers after a few weeks or months without activity, so check the app's own rules."),
            ("Can someone get into my accounts with my old number?", "Yes, if the account still uses that number for login codes or password resets."),
            ("Is a public receive-SMS number already recycled?", "Effectively yes: it is shared with everyone who visits the site, all the time."),
        ],
        "related": ["authenticator-apps-vs-sms-codes", "whatsapp-not-sending-verification-code", "telegram-phone-number-banned"],
    },
    {
        "slug": "authenticator-apps-vs-sms-codes",
        "category": "safety",
        "date": "2026-11-24",
        "label": "2FA",
        "card": "Why security agencies call SMS the weakest second factor, and when an authenticator app or passkey is the better choice.",
        "title": "Authenticator Apps vs SMS Codes: Which 2FA Is Safer?",
        "desc": "SMS codes are the most common second factor but also the weakest. Compare SMS codes, authenticator apps and passkeys, and learn when each one makes sense.",
        "h1": "Authenticator Apps vs SMS Codes: Which Two-Factor Method Is Safer?",
        "answer": "SMS codes are better than no second factor, but they can be intercepted through SIM swaps, recycled numbers and lost virtual numbers. Authenticator apps and passkeys are tied to your device instead of a phone number, which makes them safer. Use SMS codes for signup, and switch important accounts to an app or passkey.",
        "sections": [
            ("compare", "Side by side", """    <div class="table-wrap">
      <table class="compare-table">
        <thead><tr><th scope="col">Method</th><th scope="col">Tied to</th><th scope="col">Main weakness</th></tr></thead>
        <tbody>
          <tr><th scope="row">SMS code</th><td>A phone number</td><td>Whoever controls the number gets the code</td></tr>
          <tr><th scope="row">Authenticator app</th><td>A secret stored on your device</td><td>Losing the device without a backup</td></tr>
          <tr><th scope="row">Passkey</th><td>Your device and its screen lock</td><td>Not every service supports it yet</td></tr>
        </tbody>
      </table>
    </div>"""),
            ("why-sms-weak", "Why SMS is the weakest", """    <p>An SMS code proves you control a phone number, not that you are you. Numbers can be moved to a criminal's SIM in a <strong>SIM swap</strong>, reassigned to a new owner when you stop paying, or reclaimed by a free app. In each case the codes go to someone else. The US National Institute of Standards and Technology has treated SMS as a restricted authentication method for this reason.</p>
    <p>Virtual numbers add another risk: if the app reclaims the number, or the number is public, you lose the second factor completely.</p>"""),
            ("when", "When each one fits", """    <ul>
      <li><strong>SMS codes:</strong> creating an account, low-value services, and services that offer nothing else.</li>
      <li><strong>Authenticator app:</strong> email, social media, work accounts and anything you can't afford to lose.</li>
      <li><strong>Passkey:</strong> any service that supports it; it also replaces your password.</li>
    </ul>
    <p>A practical approach with a virtual number: use it to sign up, then turn on an authenticator app and remove the phone number from the account's security settings.</p>"""),
        ],
        "faqs": [
            ("Is SMS two-factor authentication still worth using?", "Yes, it is much better than a password alone. It is just weaker than an authenticator app or a passkey."),
            ("What happens if I lose the phone with my authenticator app?", "Use the backup codes you saved when you set it up, or an app that syncs encrypted backups. Save backup codes for every important account."),
            ("Should I use a virtual number for two-factor authentication?", "Only if it is a private number you will keep. For important accounts an authenticator app is safer."),
        ],
        "related": ["recycled-phone-numbers-and-your-accounts", "what-is-a-voip-number", "google-phone-number-cannot-be-used-for-verification"],
    },
]


# --------------------------------------------------------------------------
# Data story (rebuilt daily from data/reviews.json)
# --------------------------------------------------------------------------
THEME_LABELS = {"codes": "Verification codes", "ads": "Ads", "pricing": "Pricing and payments",
                "number_lost": "Losing the number", "account_blocked": "Account blocked or banned", "call_quality": "Call quality"}


def data_story():
    month = human_date(REVIEWS["updated"]).split(" ")[0] if REVIEWS["updated"] else ""
    year = REVIEWS["updated"][:4] if REVIEWS["updated"] else ""
    apps = [a for a in REVIEWS["apps"] if a["reviews_30d"]]
    apps.sort(key=lambda a: (-a["verify_mentions_30d"], a["name"]))
    top = apps[0] if apps else None
    return {
        "slug": "free-number-app-code-complaints",
        "category": "data",
        "date": REVIEWS["updated"],
        "label": f"{month} {year}",
        "card": f"Which free number app got the most App Store complaints about verification codes in {month}? Updated daily from real reviews.",
        "title": f"Free Number Apps With the Most Code Complaints ({month} {year})",
        "desc": "Daily analysis of App Store reviews for TextNow, Google Voice, Talkatone, TextFree and Nextplus: which apps users complain about most for verification codes, ads and lost numbers.",
        "h1": f"Which Free Number App Gets the Most Complaints About Codes? ({month} {year})",
        "top": top,
        "apps": apps,
    }


def pct(part, whole):
    return round(100 * part / whole) if whole else 0


def build_data_story(s, b):
    path = f"/blog/{s['slug']}/"
    top, apps, w = s["top"], s["apps"], REVIEWS["window_days"]
    if top:
        neg = top["verify_negative_share"]
        answer = (f"In the last {w} days, <strong>{top['name']}</strong> had the most App Store reviews about verification codes: "
                  f"{top['verify_mentions_30d']} of {top['reviews_30d']} recent reviews"
                  + (f", and {neg}% of those were 1–2 stars." if neg is not None else ".")
                  + " More reviews also means more users, so compare the share of reviews, not only the count.")
    else:
        answer = "There were not enough recent reviews to compare apps this month."
    rows = "\n".join(
        f"          <tr><th scope=\"row\">{a['name']}</th><td>{a['reviews_30d']}</td><td>{a['verify_mentions_30d']}</td>"
        f"<td>{pct(a['verify_mentions_30d'], a['reviews_30d'])}%</td>"
        f"<td>{(str(a['verify_negative_share']) + '%') if a['verify_negative_share'] is not None else '—'}</td>"
        f"<td>{a['avg_rating_30d']} / {a['rating_all_time']}</td></tr>" for a in apps)
    theme_keys = ["codes", "ads", "pricing", "number_lost", "account_blocked", "call_quality"]
    theme_rows = "\n".join(
        f"          <tr><th scope=\"row\">{THEME_LABELS[k]}</th>" + "".join(
            f"<td>{pct(a.get('themes_30d', {}).get(k, 0), a['reviews_30d'])}%</td>" for a in apps) + "</tr>" for k in theme_keys)
    theme_head = "".join(f'<th scope="col">{a["name"]}</th>' for a in apps)
    # biggest theme overall
    totals = {k: sum(a.get("themes_30d", {}).get(k, 0) for a in apps) for k in theme_keys}
    biggest = max(totals, key=totals.get) if apps else "codes"
    biggest_line = f"Across all apps, the most common topic in recent reviews was <strong>{THEME_LABELS[biggest].lower()}</strong>."
    small = [a["name"] for a in apps if a["reviews_30d"] < 20]
    small_line = (f" {', '.join(small)} had fewer than 20 recent reviews, so {'its' if len(small) == 1 else 'their'} percentages can swing a lot from day to day." if small else "")
    jsonld = b.ld_base(path, s["label"], headline=s["h1"])
    jsonld["@graph"][2]["itemListElement"] = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{b.DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{b.DOMAIN}/blog/"},
        {"@type": "ListItem", "position": 3, "name": "Code complaints", "item": f"{b.DOMAIN}{path}"}]
    jsonld["@graph"][3]["dateModified"] = REVIEWS["updated"]
    body = f"""{b.head(s['title'], s['desc'], path, jsonld)}{b.header('blog')}
{crumbs('Data')}
<main id="main">
  <header class="page-header accent-purple">
    <div class="container">
      <p class="eyebrow">Data · updated daily · {blog_meta(s, words=900)}</p>
      <h1>{s['h1']}</h1>
      <div class="answer-box">
        <p class="answer-label">Short answer</p>
        <p>{answer}</p>
      </div>
    </div>
  </header>

{b.section("numbers", "The numbers", f"Code Complaints by App, Last {w} Days", f'''    <div class="table-wrap">
      <table class="compare-table">
        <thead><tr><th scope="col">App</th><th scope="col">Recent reviews</th><th scope="col">About codes</th><th scope="col">Share about codes</th><th scope="col">Of those, 1–2★</th><th scope="col">Recent / all-time rating</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p>A review counts as "about codes" when it mentions codes, verification, OTP, 2FA, sign-up, log-in, WhatsApp, Telegram or a Google account.{small_line}</p>''', narrow=False)}

{b.section("themes", "Beyond codes", "What Else Users Complain About", f'''    <p>{biggest_line} Share of recent reviews that mention each topic (a review can mention several):</p>
    <div class="table-wrap">
      <table class="compare-table theme-table">
        <thead><tr><th scope="col">Topic</th>{theme_head}</tr></thead>
        <tbody>
{theme_rows}
        </tbody>
      </table>
    </div>''', soft=True, narrow=False)}

{b.section("meaning", "What it means", "What This Means If You Need a Code", '''    <ul>
      <li><strong>Recent ratings are lower than all-time ratings for every app.</strong> People with a problem are more likely to write a review, so use these numbers to compare apps, not to judge one app in isolation.</li>
      <li><strong>A spike in code complaints</strong> often means a platform started refusing that app's numbers. If your codes stop arriving, check our <a href="/blog/">fixes</a> before you request codes again.</li>
      <li><strong>Pricing complaints</strong> usually mean features moved behind a subscription, not that the free number stopped working.</li>
    </ul>''')}

{b.section("method", "Method", "How We Counted", f'''    <p>We read up to 150 of the newest App Store reviews per app in each of the US, Canadian, UK and Australian stores every day, and count reviews from the last {w} days. Topics are found by keywords. App Store reviews are a small, self-selected sample, and Google Play reviews are not included. Full details and recent quotes are on our <a href="/user-reports/">user reports</a> page.</p>
    <p class="data-note">Last update: <time datetime="{REVIEWS['updated']}">{human_date(REVIEWS['updated'])}</time>.</p>''', soft=True)}

{b.related(related_cards(['textnow-not-receiving-verification-codes', 'recycled-phone-numbers-and-your-accounts', 'what-is-a-voip-number']), "Related Articles")}
</main>
{b.footer()}"""
    b.write(path, body)


# --------------------------------------------------------------------------
# Shared rendering
# --------------------------------------------------------------------------
_B = None


def all_articles():
    items = [dict(a, kind="fix") for a in fixes.ARTICLES] + [dict(a, kind="explainer") for a in EXPLAINERS]
    story = data_story()
    if story["top"]:
        items.append(dict(story, kind="data"))
    return items


def article_by_slug(slug):
    for a in all_articles():
        if a["slug"] == slug:
            return a
    raise KeyError(slug)


def read_minutes(a, words=None):
    if words is None:
        text = " ".join([a.get("answer", "")] + [h for _, h, _ in a.get("sections", [])] + [body for _, _, body in a.get("sections", [])]
                        + [" ".join(c) for c in a.get("causes", [])] + [" ".join(s) for s in a.get("steps", [])]
                        + [" ".join(f) for f in a.get("faqs", [])])
        words = len(re.sub(r"<[^>]+>", " ", text).split())
    return max(2, math.ceil(words / 220))


def blog_meta(a, words=None):
    return f"{fixes.short_date(a['date'])}, {a['date'][:4]} · {read_minutes(a, words)} min read"


def crumbs(label):
    return f"""<nav class="breadcrumbs" aria-label="Breadcrumb">
  <div class="container">
    <ol>
      <li><a href="/">Home</a></li>
      <li><a href="/blog/">Blog</a></li>
      <li><span aria-current="page">{label}</span></li>
    </ol>
  </div>
</nav>"""


def related_cards(slugs):
    out = []
    for slug in slugs:
        r = article_by_slug(slug)
        out.append((f"/blog/{slug}/", f"cat-{CAT_ACCENT[r['category']]}", CATEGORIES[r["category"]],
                    r["h1"].split(":")[0].split("(")[0].strip(), r["card"], "Read article"))
    return out


def build_explainer(a, b):
    path = f"/blog/{a['slug']}/"
    sections = [b.section(sid, CATEGORIES[a["category"]], h2, body, soft=(i % 2 == 1)) for i, (sid, h2, body) in enumerate(
        [(sid, title, body) for sid, title, body in a["sections"]])]
    jsonld = b.ld_base(path, a["label"], headline=a["h1"], extra=[b.ld_faq(a["faqs"])])
    jsonld["@graph"][2]["itemListElement"] = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{b.DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{b.DOMAIN}/blog/"},
        {"@type": "ListItem", "position": 3, "name": a["label"], "item": f"{b.DOMAIN}{path}"}]
    jsonld["@graph"][3]["datePublished"] = a["date"]
    accent = CAT_ACCENT[a["category"]]
    body = f"""{b.head(a['title'], a['desc'], path, jsonld)}{b.header('blog')}
{crumbs(a['label'])}
<main id="main">
  <header class="page-header accent-{accent}">
    <div class="container">
      <p class="eyebrow">{CATEGORIES[a['category']]} · {blog_meta(a)}</p>
      <h1>{a['h1']}</h1>
      <div class="answer-box">
        <p class="answer-label">Short answer</p>
        <p>{a['answer']}</p>
      </div>
    </div>
  </header>

{chr(10).join(sections)}

{b.faq_block("Questions People Ask", a["faqs"])}

{b.related(related_cards(a["related"]), "Related Articles")}
</main>
{b.footer()}"""
    b.write(path, body)


def blog_card(a):
    cat = a["category"]
    return f"""      <a class="card category-card blog-card cat-{CAT_ACCENT[cat]}" href="/blog/{a['slug']}/" data-category="{cat}">
        <p class="eyebrow-sm">{CATEGORIES[cat]}</p>
        <h3>{a['h1'].split(':')[0].split('(')[0].strip() if a['kind'] != 'data' else a['h1']}</h3>
        <p>{a['card']}</p>
        <p class="blog-meta">{blog_meta(a, words=900 if a['kind'] == 'data' else None)}</p>
      </a>"""


def build_hub(b):
    path = "/blog/"
    items = all_articles()
    # data story first, then newest; stable order within a date
    items.sort(key=lambda a: (a["kind"] != "data", a["date"]), reverse=False)
    chips = '<button type="button" class="chip is-active" data-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" class="chip" data-filter="{k}" aria-pressed="false">{v}</button>' for k, v in CATEGORIES.items())
    jsonld = b.ld_base(path, "Blog", page_type="CollectionPage", extra=[{
        "@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": a["h1"], "url": f"{b.DOMAIN}/blog/{a['slug']}/"} for i, a in enumerate(items)]}])
    body = f"""{b.head("Virtual Numbers and OTP Codes: Guides and Fixes | " + b.BRAND,
                     "Fixes for verification code errors, plain-English explainers on VoIP numbers and short codes, privacy guides and monthly data from App Store reviews.",
                     path, jsonld)}{b.header('blog')}{b.breadcrumbs('Blog')}
<main id="main">
  <header class="page-header">
    <div class="container">
      <p class="eyebrow">Blog</p>
      <h1>Virtual Numbers and Verification Codes, Explained</h1>
      <p class="lead">Fixes for specific error messages, plain-English explainers, privacy guides and a monthly look at what App Store users report.</p>
    </div>
  </header>
  <section class="band" aria-label="Articles">
    <div class="container">
      <div class="chips" role="group" aria-label="Filter by topic" hidden>{chips}</div>
      <div class="grid grid-3 blog-grid">
{chr(10).join(blog_card(a) for a in items)}
      </div>
    </div>
  </section>
</main>
{b.footer()}"""
    b.write(path, body)


# --------------------------------------------------------------------------
# Home page blocks
# --------------------------------------------------------------------------
def home_blog_block():
    items = all_articles()
    picks = [a for a in items if a["kind"] == "data"][:1] + [a for a in items if a["kind"] == "explainer"][:1] + \
            [a for a in items if a["kind"] == "fix"][:1]
    cards = "\n".join(blog_card(a) for a in picks)
    return f"""<section class="band" id="blog" aria-labelledby="blog-title">
  <div class="container">
    <p class="eyebrow">From the blog</p>
    <h2 id="blog-title">Fixes, Explainers and Data</h2>
    <div class="grid grid-3">
{cards}
    </div>
    <p class="data-note"><a class="link-arrow" href="/blog/">All articles</a></p>
  </div>
</section>"""


def inject_home(b):
    path = b.SITE / "index.html"
    s = path.read_text(encoding="utf-8")
    for name, block in (("USER-REPORTS", fixes.home_reports_block(b)), ("BLOG", home_blog_block())):
        pattern = re.compile(rf"(<!-- AUTO:{name}:START -->).*?(<!-- AUTO:{name}:END -->)", re.S)
        if not pattern.search(s):
            raise SystemExit(f"Marker AUTO:{name} not found in site/index.html")
        s = pattern.sub(lambda m: m.group(1) + "\n" + block + "\n" + m.group(2), s)
    path.write_text(s, encoding="utf-8", newline="\n")
    print("updated home blocks in site/index.html")


def sitemap_paths():
    return ["/blog/"] + [f"/blog/{a['slug']}/" for a in all_articles()]


def build_all(b):
    b.blog_meta = blog_meta
    fixes.build_all(b)
    for a in EXPLAINERS:
        build_explainer(a, b)
    story = data_story()
    if story["top"]:
        build_data_story(story, b)
    build_hub(b)
    inject_home(b)
