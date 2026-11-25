"""Fix articles (blog category "Fixes"), review widgets and the App Store user reports page.
The blog hub, other article types and home blocks live in tools/blog.py.

Called from tools/build.py:  fixes.build_all(build_module)
`b` is the build module, so this file reuses its head/header/footer helpers.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
REVIEWS_PATH = ROOT / "data" / "reviews.json"
REVIEWS = json.loads(REVIEWS_PATH.read_text(encoding="utf-8-sig")) if REVIEWS_PATH.exists() else {"apps": [], "updated": ""}
APPS = {a["id"]: a for a in REVIEWS["apps"]}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def human_date(iso):
    if not iso:
        return ""
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"


def short_date(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1][:3]} {int(d)}"


# --------------------------------------------------------------------------
# Articles
# --------------------------------------------------------------------------
ARTICLES = [
    {
        "slug": "textnow-not-receiving-verification-codes",
        "accent": "purple",
        "app": "textnow",
        "label": "TextNow",
        "card": "Why TextNow numbers miss codes from Google, Telegram and WhatsApp, and what to try first.",
        "title": "TextNow Not Receiving Verification Codes? Fixes (2026)",
        "desc": "Why your TextNow number is not receiving verification codes from Google, Telegram, WhatsApp or banks, and the fixes that actually work.",
        "h1": "TextNow Not Receiving Verification Codes: Why It Happens and How to Fix It",
        "answer": "Most of the time TextNow is not broken: the app or website sending the code refuses VoIP numbers, or sends the code from a short code that TextNow cannot receive. Check the number format, ask for a voice call, wait out the resend timer, and if the service still refuses, use a different number for that one service.",
        "causes": [
            ("The sender blocks VoIP numbers", "The code is never sent; no error, or \"number not supported\"", "Use a different number for this service; TextNow cannot change how it is classified."),
            ("The code comes from a short code", "Codes from banks or US retailers never arrive, while normal texts do", "Choose a voice call if the service offers it."),
            ("Too many resend requests", "\"Try again later\" or nothing arrives for hours", "Stop requesting codes and wait at least an hour."),
            ("The number was recently recycled", "Codes arrive for someone else's accounts, or the service says the number is in use", "Get a new TextNow number from the app settings."),
            ("Wrong country or format", "The service rejects the number immediately", "Enter +1 and the 10-digit number, without a leading 1 twice."),
            ("App notifications are off", "Codes appear only when you open the app", "Allow notifications and keep the app updated."),
        ],
        "steps": [
            ("Check the number", "In TextNow, open the menu and copy your number. Enter it as +1 followed by 10 digits."),
            ("Open the app and wait", "Keep TextNow open for two minutes after requesting the code; some codes arrive with a delay."),
            ("Ask for a voice call", "If the service offers \"Call me instead\", choose it. TextNow receives calls from numbers that cannot text it."),
            ("Wait before resending", "If nothing arrives, wait an hour. Repeated requests make the sender block the number for longer."),
            ("Try another number for this service", "Some services never accept VoIP numbers. Pick another option from our <a href=\"/#ranking\">ranking</a> for that account."),
        ],
        "dont": ["Do not request codes again and again: it extends the block.", "Do not use public receive-SMS numbers for an account you want to keep.", "Do not rely on a TextNow number for banking or account recovery."],
        "faqs": [
            ("Why does TextNow receive normal texts but not verification codes?", "Normal texts come from regular phone numbers. Many verification codes come from short codes or from systems that check the line type first, and they skip VoIP numbers such as TextNow."),
            ("Does TextNow work for Google verification?", "Usually yes. In our tests Google accepted TextNow numbers in most attempts. Telegram accepted them about half the time, and WhatsApp rejected them."),
            ("Can I get a new TextNow number if mine is blocked?", "Yes. You can change your number in the app settings. A new number has no history, so it is sometimes accepted where the old one was not."),
        ],
        "alternatives": [
            ("smsfast", "Online number service with private numbers in the US, Canada, the UK and Australia. The only option in our ranking that passed Telegram, WhatsApp and Google."),
            ("google-voice", "Free US number from Google. Accepted by Google every time, but you need an existing US number to set it up."),
            ("talkatone", "Free US and Canadian app number with an email signup. Make a call or send a text every 30 days to keep it."),
            ("textfree", "Free US app number. Passed some Google checks; Telegram and WhatsApp refused it."),
        ],
        "related": ["google-voice-not-receiving-verification-codes", "whatsapp-not-sending-verification-code", "google-phone-number-cannot-be-used-for-verification"],
    },
    {
        "slug": "google-voice-not-receiving-verification-codes",
        "accent": "orange",
        "app": "google-voice",
        "label": "Google Voice",
        "card": "Short codes, VoIP checks and account limits that stop Google Voice from receiving codes.",
        "title": "Google Voice Not Receiving Verification Codes? Fixes (2026)",
        "desc": "Why Google Voice is not receiving verification codes from apps and banks, which services block it, and how to get your code.",
        "h1": "Google Voice Not Receiving Verification Codes: Causes and Fixes",
        "answer": "Google Voice is a VoIP number, and many services either refuse VoIP numbers or send codes from short codes that Google Voice does not receive. Make sure messages are going to the Voice app, try a voice call, and if a service keeps refusing, verify that account with a different number.",
        "causes": [
            ("Short-code messages", "Codes from banks, retailers or social apps never arrive", "Ask for a voice call or email code instead."),
            ("The service blocks VoIP", "The site says the number is not supported, or no code is sent", "Use a different number for that service."),
            ("Messages forwarded elsewhere", "Codes go to email or a linked phone, not the Voice app", "In Voice settings, check message forwarding."),
            ("Account or number on hold", "Voice shows a warning about your number", "Open voice.google.com and resolve the warning."),
            ("Too many attempts", "\"Try again later\" from the sending service", "Wait at least an hour before trying again."),
        ],
        "steps": [
            ("Open Voice on the web", "Go to voice.google.com and check Messages. Codes sometimes appear there before the app syncs."),
            ("Check forwarding settings", "In Settings, see where messages are forwarded and turn on notifications for the app."),
            ("Request a voice call", "Choose \"Call me\" if the service offers it. Google Voice receives calls reliably."),
            ("Wait before resending", "Give the sender at least an hour before you ask for another code."),
            ("Use another number for that account", "If a service refuses VoIP, compare other options in our <a href=\"/#ranking\">ranking</a>."),
        ],
        "dont": ["Do not use Google Voice as the recovery number for your main Google account.", "Do not let the number go inactive: Google can reclaim unused numbers.", "Do not keep retrying the same service every few minutes."],
        "faqs": [
            ("Can Google Voice receive short-code texts?", "Often not. Many short-code senders do not deliver to Google Voice, which is why codes from banks and some apps never arrive."),
            ("Does WhatsApp accept Google Voice numbers?", "Sometimes. In our tests WhatsApp accepted Google Voice in some attempts and refused it in others."),
            ("Why did my Google Voice number stop receiving codes?", "The sending service may have started blocking VoIP numbers, or your Voice number may have a warning on the account. Check voice.google.com first."),
        ],
        "related": ["textnow-not-receiving-verification-codes", "google-phone-number-cannot-be-used-for-verification", "telegram-phone-number-banned"],
    },
    {
        "slug": "telegram-phone-number-banned",
        "accent": "blue",
        "app": None,
        "label": "Telegram",
        "card": "What \"phone number banned\" means on Telegram and the legitimate ways to get an account.",
        "title": "Telegram \"Phone Number Banned\": What It Means & Fixes",
        "desc": "Telegram says your phone number is banned? Learn why it happens with virtual numbers, what you can do, and how to avoid it next time.",
        "h1": "Telegram \"This Phone Number Is Banned\": What It Means and What to Do",
        "answer": "The message means Telegram has blocked that phone number, usually because it is a VoIP or recycled number, was used for many accounts, or was reported for spam. If the number is genuinely yours, contact Telegram support. If it is a shared or virtual number, use a different number.",
        "causes": [
            ("The number is a VoIP or flagged range", "Banned right at signup, before any code is sent", "Use a different number type."),
            ("The number was used for spam before", "A recycled number is banned on first try", "Ask your provider for a new number."),
            ("Many accounts on one number", "Public receive-SMS numbers are banned for everyone", "Never use public numbers for Telegram."),
            ("Your own account broke the rules", "The ban follows a period of messaging", "Appeal through Telegram support."),
        ],
        "steps": [
            ("Check if the number is yours", "If it is your own SIM number, the ban is about your account, not the number type."),
            ("Contact Telegram support", "Use the support link shown in the app, or email Telegram's abuse address, and explain the case briefly."),
            ("Do not create new accounts in a loop", "Each new attempt on a flagged number makes recovery less likely."),
            ("Use a different number", "For a new account, pick a number that passed Telegram in our <a href=\"/#ranking\">ranking</a>."),
            ("Protect the new account", "Turn on Two-Step Verification (a cloud password) right after signing in."),
        ],
        "dont": ["Do not try to get around the ban with scripts or modified apps: it breaks Telegram's terms.", "Do not buy numbers from people selling \"unbannable\" accounts.", "Do not use a public number you found on a website."],
        "faqs": [
            ("Is a Telegram number ban permanent?", "Not always. Bans on your own number can sometimes be lifted after contacting support. Bans on shared or VoIP numbers usually stay."),
            ("Why is a brand-new virtual number already banned?", "Virtual numbers are often recycled. Someone may have used it for spam before you got it."),
            ("Can I use Telegram without a phone number?", "No. Telegram requires a phone number at signup."),
        ],
        "related": ["whatsapp-not-sending-verification-code", "textnow-not-receiving-verification-codes", "google-voice-not-receiving-verification-codes"],
    },
    {
        "slug": "whatsapp-not-sending-verification-code",
        "accent": "green",
        "app": None,
        "label": "WhatsApp",
        "card": "Why WhatsApp does not send a code to virtual numbers, and the steps that help.",
        "title": "WhatsApp Not Sending Verification Code? Fixes (2026)",
        "desc": "WhatsApp verification code not arriving? Why WhatsApp refuses many virtual numbers, how to use the voice call option, and what to do next.",
        "h1": "WhatsApp Not Sending a Verification Code: Why and How to Fix It",
        "answer": "WhatsApp checks every number before sending a code and refuses many VoIP numbers and numbers already used for other accounts. Make sure the country and number are correct, wait for the timer, use \"Call me\", and if WhatsApp still refuses, the number type is the problem, not your phone.",
        "causes": [
            ("VoIP number", "No SMS and no call, or \"number not supported\"", "Use a number that passed WhatsApp in our ranking."),
            ("Number used by another account", "WhatsApp asks to verify another device or shows a warning", "Use a number you control long term."),
            ("Wrong country selected", "The code never arrives", "Pick the right country and remove the leading 0."),
            ("Too many requests", "A long countdown before you can retry", "Wait for the timer to end completely."),
            ("Region mismatch", "Numbers from another country fail more often", "Use a local number for the country of your phone."),
        ],
        "steps": [
            ("Check country and number", "Choose the country from the list, then type the number without the leading 0 or country code."),
            ("Wait for the timer", "WhatsApp shows a countdown. Requests before it ends do nothing."),
            ("Choose \"Call me\"", "When the SMS timer ends, ask for a voice call and note the 6-digit code."),
            ("Stop after two tries", "If both SMS and call fail, the number is being refused. More attempts lock it longer."),
            ("Switch to a number that passed", "See which services passed WhatsApp in our <a href=\"/#ranking\">ranking</a>."),
        ],
        "dont": ["Do not register WhatsApp with a public receive-SMS number: anyone can take the account later.", "Do not use unofficial WhatsApp apps to get around verification.", "Do not forget to set a two-step verification PIN after signing in."],
        "faqs": [
            ("Why does WhatsApp not send a code to my virtual number?", "WhatsApp checks the line type and history of the number. Most free virtual numbers are VoIP lines, and WhatsApp refuses them without sending anything."),
            ("How long should I wait before requesting a new code?", "Wait until the countdown ends. After several failed tries the wait can grow to hours."),
            ("Can someone else take my WhatsApp if I use a public number?", "Yes. Whoever gets the number next can request a code and move the account to their phone. Set a two-step PIN to make this harder."),
        ],
        "related": ["telegram-phone-number-banned", "google-voice-not-receiving-verification-codes", "textnow-not-receiving-verification-codes"],
    },
    {
        "slug": "google-phone-number-cannot-be-used-for-verification",
        "accent": "orange",
        "app": None,
        "label": "Google",
        "card": "What Google's \"This phone number cannot be used for verification\" error means and how to get past it legitimately.",
        "title": "Google: \"This Phone Number Cannot Be Used\" for Verification",
        "desc": "Google says \"This phone number cannot be used for verification\"? Why it happens, which numbers Google accepts, and what to do instead.",
        "h1": "Google: \"This Phone Number Cannot Be Used for Verification\" — How to Fix It",
        "answer": "Google shows this error when the number has been used too many times or looks unreliable, which is almost always the case with public receive-SMS numbers. Use a private number that has not been used for Google before, try from a device you normally use, or skip the phone step if Google offers that option.",
        "causes": [
            ("Public or shared number", "Error appears immediately", "Use a private number."),
            ("Number used for many Google accounts", "Worked before, now refused", "Use a number not linked to other Google accounts."),
            ("New device or network", "Google insists on a phone and refuses several numbers", "Try from a device and network you normally use."),
            ("Too many attempts", "Error appears for every number you try", "Wait a few hours before trying again."),
        ],
        "steps": [
            ("Stop retrying the same number", "Google remembers refused numbers. The same number will keep failing."),
            ("Use a private number", "A number only you use, such as a free app number, passes far more often than a public one."),
            ("Try from a familiar device", "Google asks for a phone more often on new browsers and shared networks."),
            ("Look for the skip option", "If Google lets you skip the phone step, skip it and add a recovery email instead."),
            ("Compare numbers that passed", "See which services passed Google in our <a href=\"/#ranking\">ranking</a>."),
        ],
        "dont": ["Do not set a virtual number you might lose as your Google recovery phone.", "Do not use tools that promise to bypass Google's phone check.", "Do not try dozens of public numbers in a row."],
        "faqs": [
            ("Why does Google say this phone number cannot be used for verification?", "The number has been used too many times or looks unreliable to Google. Public receive-SMS numbers trigger it almost every time."),
            ("Which numbers does Google accept?", "Private numbers with little history pass most often. In our tests Google Voice and TextNow were accepted in most attempts."),
            ("Can I create a Google account without a phone number?", "Sometimes. On a device you already use, Google often lets you skip the phone step."),
        ],
        "related": ["google-voice-not-receiving-verification-codes", "textnow-not-receiving-verification-codes", "telegram-phone-number-banned"],
    },
]
for _a in ARTICLES:
    _a.setdefault("category", "fixes")
    _a.setdefault("date", "2026-11-24")
BY_SLUG = {a["slug"]: a for a in ARTICLES}


# --------------------------------------------------------------------------
# Review widgets (from data/reviews.json)
# --------------------------------------------------------------------------
def stars(n):
    return f'<span class="stars" aria-label="{n} out of 5 stars">{"★" * n}{"☆" * (5 - n)}</span>'


def quote_cards(app, b):
    out = []
    for q in app["quotes"]:
        out.append(f"""        <figure class="review-quote">
          <figcaption>{stars(q['rating'])} <span>App Store {q['store']} · {short_date(q['date'])}</span></figcaption>
          <blockquote><p><strong>{b.e(q['title'])}</strong> {b.e(q['text'])}</p></blockquote>
        </figure>""")
    return "\n".join(out)


def app_report(app, b, heading_level="h3"):
    if not app:
        return ""
    neg = app["verify_negative_share"]
    mentions = app["verify_mentions_30d"]
    summary = (f"{mentions} of {app['reviews_30d']} App Store reviews from the last {REVIEWS['window_days']} days mention codes, sign-in or verification"
               + (f", and {neg}% of those are 1–2 stars." if neg is not None else "."))
    quotes = quote_cards(app, b)
    return f"""      <div class="card card-feature app-report">
        <{heading_level}>{app['name']}: what users report</{heading_level}>
        <dl class="report-stats">
          <div><dt>All-time rating</dt><dd>{app['rating_all_time']}</dd></div>
          <div><dt>Last {REVIEWS['window_days']} days</dt><dd>{app['avg_rating_30d'] if app['avg_rating_30d'] is not None else '—'}</dd></div>
          <div><dt>Code-related reviews</dt><dd>{mentions}</dd></div>
          <div><dt>Of those, 1–2 stars</dt><dd>{f'{neg}%' if neg is not None else '—'}</dd></div>
        </dl>
        <p>{summary}</p>
{quotes}
      </div>"""


SITES = {s["id"]: s for s in REVIEWS.get("sites", [])}


def site_report(site, b):
    """Reviews a web-only service publishes on its own website."""
    if not site:
        return ""
    total = site["reviews_total"]
    dist = " · ".join(f"{k}★ {site['distribution'][k]}" for k in ("5", "4", "3", "2", "1"))
    neg = site["verify_negative_share"]
    quotes = "\n".join(f"""        <figure class="review-quote">
          <figcaption>{stars(q['rating'])} <span>smsfast.com · {short_date(q['date'])}</span></figcaption>
          <blockquote><p><strong>{b.e(q['title'])}</strong> {b.e(q['text'])}</p></blockquote>
        </figure>""" for q in site["quotes"])
    return f"""      <div class="card card-feature app-report">
        <h3>{site['name']}: what users report</h3>
        <dl class="report-stats">
          <div><dt>Rating on its site</dt><dd>{site['rating_avg']}</dd></div>
          <div><dt>Reviews</dt><dd>{total}</dd></div>
          <div><dt>Last {REVIEWS['window_days']} days</dt><dd>{site['reviews_30d']}</dd></div>
          <div><dt>Critical reviews</dt><dd>{site['negative_count']}</dd></div>
        </dl>
        <p>{site['verify_mentions']} of {total} reviews mention codes, verification or a specific app{f", and {neg}% of those are critical." if neg is not None else "."} Ratings: {dist}.</p>
{quotes}
        <p class="data-note">Source: <a href="{site['source_url']}" rel="noopener" target="_blank">reviews page on smsfast.com</a>, since {human_date(site['first_review'])}. Each review is marked as from a buyer; the page is run and moderated by the service itself, so the numbers are not comparable with App Store data.</p>
      </div>"""


def reviews_source_note():
    return (f'<p class="data-note">Data: public Apple App Store reviews from the US, Canada, UK and Australia stores, '
            f'refreshed daily. Last update: <time datetime="{REVIEWS["updated"]}">{human_date(REVIEWS["updated"])}</time>. '
            f'"Code-related" means the review mentions codes, verification, OTP, sign-up or log-in. '
            f'<a href="/user-reports/#method">How we count</a></p>')


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
ALT_LINKS = {"smsfast": "https://smsfast.com/"}   # the only external links on the site


def alternatives_section(a, b):
    alts = a.get("alternatives")
    if not alts:
        return ""
    cards = []
    for i, (sid, why) in enumerate(alts, 1):
        s = b.BY_ID[sid]
        chips = "".join(f'<span class="alt-status"><span class="alt-platform">{p}</span>{b.status(s[k])}</span>'
                        for k, p in (("telegram", "Telegram"), ("whatsapp", "WhatsApp"), ("google", "Google")))
        btn = ""
        if sid in ALT_LINKS:
            btn = (f'<a class="btn btn-primary btn-sm" href="{ALT_LINKS[sid]}" rel="noopener" target="_blank">'
                   f'Get a number <span class="ext" aria-hidden="true">↗</span></a>')
        featured = " is-featured" if i == 1 else ""
        cards.append(f"""      <article class="card card-feature alt-card{featured}">
        <div class="alt-head"><span class="rank">{i}</span><h3>{s['name']}</h3><span class="tag">{b.TYPE_LABEL[s['type']]}</span></div>
        <p>{why}</p>
        <div class="alt-statuses">{chips}</div>
        {btn}
      </article>""")
    name = a["label"]
    return b.section("alternatives", "Alternatives", f"Alternatives to {name} for Verification Codes",
                     f"    <p>If {name} keeps failing for one service, use a different number for that account. These options worked best in our <a href=\"/#ranking\">ranking</a>:</p>\n"
                     + '    <div class="alt-list">\n' + "\n".join(cards) + "\n    </div>")


def build_article(a, b):
    path = f"/blog/{a['slug']}/"
    cause_rows = "\n".join(f"          <tr><th scope=\"row\">{c}</th><td>{s}</td><td>{f}</td></tr>" for c, s, f in a["causes"])
    dont = "".join(f"<li>{d}</li>" for d in a["dont"])
    app = APPS.get(a["app"]) if a["app"] else None
    report = ""
    if app:
        report = b.section("user-reports", "From the App Store", f"What {app['name']} Users Report About Codes",
                           app_report(app, b) + "\n    " + reviews_source_note(), soft=True)
    rel_cards = []
    for slug in a["related"]:
        r = BY_SLUG[slug]
        rel_cards.append((f"/blog/{slug}/", f"cat-{r['accent']}", r["label"], r["h1"].split(":")[0], r["card"], "Read the fix"))
    jsonld = b.ld_base(path, a["label"] + " fix", headline=a["h1"], extra=[
        b.ld_faq(a["faqs"]),
        {"@type": "HowTo", "name": a["h1"], "step": [
            {"@type": "HowToStep", "position": i + 1, "name": h, "text": b.strip_tags(t)} for i, (h, t) in enumerate(a["steps"])]},
    ])
    # breadcrumb: Home › Fixes › article
    jsonld["@graph"][2]["itemListElement"] = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{b.DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{b.DOMAIN}/blog/"},
        {"@type": "ListItem", "position": 3, "name": a["label"], "item": f"{b.DOMAIN}{path}"}]
    body = f"""{b.head(a['title'], a['desc'], path, jsonld)}{b.header('blog')}
<nav class="breadcrumbs" aria-label="Breadcrumb">
  <div class="container">
    <ol>
      <li><a href="/">Home</a></li>
      <li><a href="/blog/">Blog</a></li>
      <li><span aria-current="page">{b.e(a['label'])}</span></li>
    </ol>
  </div>
</nav>
<main id="main">
  <header class="page-header accent-{a['accent']}">
    <div class="container">
      <p class="eyebrow">Fixes · {a['label']} · {b.blog_meta(a)}</p>
      <h1>{a['h1']}</h1>
      <div class="answer-box">
        <p class="answer-label">Short answer</p>
        <p>{a['answer']}</p>
      </div>
    </div>
  </header>

{b.section("causes", "Why it happens", "Common Causes and What Each One Looks Like", f'''    <div class="table-wrap">
      <table class="compare-table cause-table">
        <thead><tr><th scope="col">Cause</th><th scope="col">What you see</th><th scope="col">What to do</th></tr></thead>
        <tbody>
{cause_rows}
        </tbody>
      </table>
    </div>''')}

{b.section("fix", "Step by step", "How to Fix It", "    " + b.steps(a["steps"]), soft=True)}

{alternatives_section(a, b)}

{b.section("avoid", "Avoid", "What Not to Do", f'    <ul class="avoid-list">{dont}</ul>', soft=bool(a.get("alternatives")))}

{report.replace('class="band band-soft" id="user-reports"', 'class="band" id="user-reports"') if a.get("alternatives") else report}

{b.faq_block("Questions People Ask", a["faqs"])}

{b.related(rel_cards, "Related Fixes")}
</main>
{b.footer()}"""
    b.write(path, body)


def build_hub(b):
    path = "/fixes/"
    cards = []
    for a in ARTICLES:
        cards.append(f"""      <a class="card category-card cat-{a['accent']}" href="/fixes/{a['slug']}/">
        <p class="eyebrow-sm">{a['label']}</p>
        <h3>{a['h1'].split(':')[0]}</h3>
        <p>{a['card']}</p>
        <span class="link-arrow">Read the fix</span>
      </a>""")
    jsonld = b.ld_base(path, "Fixes", page_type="CollectionPage", extra=[{
        "@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": a["h1"], "url": f"{b.DOMAIN}/fixes/{a['slug']}/"} for i, a in enumerate(ARTICLES)]}])
    body = f"""{b.head("Verification Code Problems: Fixes That Work | " + b.BRAND,
                     "Step-by-step fixes for verification code problems with TextNow, Google Voice, Telegram, WhatsApp and Google.",
                     path, jsonld)}{b.header('fixes')}{b.breadcrumbs('Fixes')}
<main id="main">
  <header class="page-header">
    <div class="container">
      <p class="eyebrow">Fixes</p>
      <h1>Verification Code Problems: Fixes That Work</h1>
      <p class="lead">One page per error. Each fix explains what the message really means, how to tell which cause you have, and the steps that work without breaking any platform's rules.</p>
    </div>
  </header>
  <section class="band" aria-label="All fixes">
    <div class="container">
      <div class="grid grid-3">
{chr(10).join(cards)}
      </div>
    </div>
  </section>
</main>
{b.footer()}"""
    b.write(path, body)


def build_user_reports(b):
    path = "/user-reports/"
    apps = sorted(REVIEWS["apps"], key=lambda a: -a["verify_mentions_30d"])
    rows = "\n".join(f"""          <tr>
            <th scope="row">{a['name']}</th>
            <td data-label="All-time rating">{a['rating_all_time']}</td>
            <td data-label="Ratings">{a['ratings_count']:,}</td>
            <td data-label="Reviews, {REVIEWS['window_days']} days">{a['reviews_30d']}</td>
            <td data-label="Avg, {REVIEWS['window_days']} days">{a['avg_rating_30d'] if a['avg_rating_30d'] is not None else '—'}</td>
            <td data-label="Code-related">{a['verify_mentions_30d']}</td>
            <td data-label="Of those, 1–2★">{f"{a['verify_negative_share']}%" if a['verify_negative_share'] is not None else '—'}</td>
          </tr>""" for a in apps)
    for s in SITES.values():
        neg30 = s.get("verify_negative_share_30d")
        rows += f"""
          <tr class="row-site">
            <th scope="row">{s['name']}<sup>*</sup></th>
            <td data-label="All-time rating">{s['rating_avg']}</td>
            <td data-label="Ratings">{s['reviews_total']:,}</td>
            <td data-label="Reviews, {REVIEWS['window_days']} days">{s['reviews_30d']}</td>
            <td data-label="Avg, {REVIEWS['window_days']} days">{s['avg_rating_30d'] if s['avg_rating_30d'] is not None else '—'}</td>
            <td data-label="Code-related">{s.get('verify_mentions_30d', '—')}</td>
            <td data-label="Of those, 1–2★">{f"{neg30}%" if neg30 is not None else '—'}</td>
          </tr>"""
    site_note = (" <sup>*</sup> SMSFAST has no App Store app: its figures come from the reviews page on smsfast.com, "
                 "which the service runs itself, and its “critical” share counts reviews the site marks as negative."
                 if SITES else "")
    reports = "\n".join(app_report(a, b) for a in apps if a["quotes"])
    site_section = ""
    if SITES:
        site_section = f"""
  <section class="band" id="web-services" aria-labelledby="web-title">
    <div class="container container-narrow">
      <p class="eyebrow">Web services</p>
      <h2 id="web-title">Reviews on the Service's Own Website</h2>
      <p>Web-based services have no App Store page, so we read the reviews they publish themselves.</p>
{chr(10).join(site_report(s, b) for s in SITES.values())}
    </div>
  </section>
"""
    jsonld = b.ld_base(path, "User Reports", page_type="WebPage")
    body = f"""{b.head("Free Number App Reviews: What Users Say About Codes",
                     "Daily summary of reviews for TextNow, Google Voice, Talkatone, TextFree, Nextplus and SMSFAST: ratings and what users say about verification codes.",
                     path, jsonld)}{b.header('user-reports')}{b.breadcrumbs('User Reports')}
<main id="main">
  <header class="page-header">
    <div class="container">
      <p class="eyebrow">User reports · updated daily</p>
      <h1>What App Store Users Say About Free Number Apps</h1>
      <p class="lead">We read the latest App Store reviews of the most popular free number apps every day and count how many talk about verification codes. It is the fastest way to spot when an app stops receiving codes. For web services without an app, we summarise the reviews they publish on their own site.</p>
      <p class="page-meta">Last update: <time datetime="{REVIEWS['updated']}">{human_date(REVIEWS['updated'])}</time> · Stores: US, Canada, UK, Australia</p>
    </div>
  </header>

  <section class="band" aria-labelledby="overview-title">
    <div class="container">
      <p class="eyebrow">Overview</p>
      <h2 id="overview-title">Ratings and Code Complaints, Last {REVIEWS['window_days']} Days</h2>
      <div class="table-wrap">
        <table class="compare-table report-table">
          <thead><tr><th scope="col">App</th><th scope="col">All-time rating</th><th scope="col">Ratings</th><th scope="col">Reviews, {REVIEWS['window_days']} days</th><th scope="col">Avg, {REVIEWS['window_days']} days</th><th scope="col">Code-related</th><th scope="col">Of those, 1–2★</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
      <p class="data-note">The recent average is usually lower than the all-time rating: people who have a problem are more likely to write a review. Compare apps with each other, not with their all-time score.{site_note}</p>
    </div>
  </section>

  <section class="band band-soft" aria-labelledby="quotes-title">
    <div class="container container-narrow">
      <p class="eyebrow">In their words</p>
      <h2 id="quotes-title">Recent Reviews About Codes</h2>
{reports}
    </div>
  </section>
{site_section}
  <section class="band{' band-soft' if SITES else ''}" id="method" aria-labelledby="method-title">
    <div class="container container-narrow">
      <p class="eyebrow">Method</p>
      <h2 id="method-title">How We Count</h2>
      <ul>
        <li><strong>Source:</strong> the public Apple App Store review feed for each app, in the US, Canadian, UK and Australian stores. Up to 150 of the newest reviews per store are read every day. If the feed is temporarily empty, the previous day's figures are kept.</li>
        <li><strong>Window:</strong> only reviews from the last {REVIEWS['window_days']} days are counted.</li>
        <li><strong>Code-related:</strong> the title or text mentions codes, verification, OTP, 2FA, sign-up, log-in, WhatsApp, Telegram or a Google account.</li>
        <li><strong>Quotes:</strong> the newest negative and positive code-related review, shortened. Reviewer names, reviews with personal details and reviews written by children are never shown.</li>
        <li><strong>Which services:</strong> services in our ranking that have an iPhone app in the App Store. Web-based services have no App Store reviews; where a service publishes buyer reviews on its own website, we show those separately and never mix them into the App Store figures. Public receive-SMS websites have no reviews to read.</li>
        <li><strong>Critical:</strong> for App Store reviews, 1–2 stars; for reviews on a service's own site, the reviews that site marks as negative or that give 1–2 stars.</li>
        <li><strong>Limits:</strong> App Store reviews are a small, self-selected sample and do not prove that an app works or fails for you. Google Play reviews are not included.</li>
      </ul>
    </div>
  </section>
</main>
{b.footer()}"""
    b.write(path, body)


# --------------------------------------------------------------------------
# Home page blocks (between AUTO markers in site/index.html)
# --------------------------------------------------------------------------
def home_reports_block(b):
    cards = []
    for a in sorted(REVIEWS["apps"], key=lambda a: -a["verify_mentions_30d"])[:3]:
        neg = a["verify_negative_share"]
        cards.append(f"""        <article class="card card-feature mini-report">
          <h3>{a['name']}</h3>
          <p class="mini-figure">{a['verify_mentions_30d']}<span> code-related reviews</span></p>
          <p>{f"{neg}% of them are 1–2 stars." if neg is not None else "No code-related reviews this month."} Recent average {a['avg_rating_30d']} vs {a['rating_all_time']} all-time.</p>
        </article>""")
    for s in SITES.values():
        cards.append(f"""        <article class="card card-feature mini-report">
          <h3>{s['name']}</h3>
          <p class="mini-figure">{s['rating_avg']}<span> rating on its own site</span></p>
          <p>{s['reviews_total']} buyer reviews on smsfast.com, {s['negative_count']} of them critical. {s['verify_mentions']} mention codes or verification.</p>
        </article>""")
    grid = "grid-4" if len(cards) == 4 else "grid-3"
    return f"""<section class="band band-soft" id="user-reports" aria-labelledby="reports-title">
  <div class="container">
    <p class="eyebrow">User reports · updated daily</p>
    <h2 id="reports-title">What Users Say About Codes This Month</h2>
    <p class="section-intro">Every day we read the newest App Store reviews of free number apps in the US, Canada, UK and Australia, plus the reviews web services publish on their own sites, and count how many talk about verification codes.</p>
    <div class="grid {grid}">
{chr(10).join(cards)}
    </div>
    <p class="data-note">Last update: <time datetime="{REVIEWS['updated']}">{human_date(REVIEWS['updated'])}</time>. <a href="/user-reports/">See all apps and recent reviews</a></p>
  </div>
</section>"""


def home_fixes_block(b):
    items = "\n".join(f'      <li><a href="/fixes/{a["slug"]}/">{a["h1"].split(":")[0]}</a><span>{a["card"]}</span></li>' for a in ARTICLES)
    return f"""<section class="band" id="fixes" aria-labelledby="fixes-title">
  <div class="container container-narrow">
    <p class="eyebrow">Fixes</p>
    <h2 id="fixes-title">Fix a Specific Error</h2>
    <ul class="fix-list">
{items}
    </ul>
    <p><a class="link-arrow" href="/fixes/">All fixes</a></p>
  </div>
</section>"""


def inject_home(b):
    path = b.SITE / "index.html"
    s = path.read_text(encoding="utf-8")
    for name, html_block in (("USER-REPORTS", home_reports_block(b)), ("FIXES", home_fixes_block(b))):
        pattern = re.compile(rf"(<!-- AUTO:{name}:START -->).*?(<!-- AUTO:{name}:END -->)", re.S)
        if not pattern.search(s):
            raise SystemExit(f"Marker AUTO:{name} not found in site/index.html")
        s = pattern.sub(lambda m: m.group(1) + "\n" + html_block + "\n" + m.group(2), s)
    path.write_text(s, encoding="utf-8", newline="\n")
    print("updated home blocks in site/index.html")


def build_all(b):
    for a in ARTICLES:
        build_article(a, b)
    build_user_reports(b)
