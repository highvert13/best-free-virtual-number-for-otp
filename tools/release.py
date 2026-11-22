"""Open the site for search engines.

Run this once the ranking contains real test results and the domain is connected:

    python tools/release.py --domain https://your-domain.com

What it does:
  1. Replaces the placeholder domain (https://example.com) in every HTML file,
     sitemap.xml, robots.txt and data/site.json.
  2. Removes the "X-Robots-Tag: noindex" line from site/_headers.
  3. Removes the yellow "Pre-launch" sample-data banner from all pages
     and sets "sample_data": false in data/ranking.json.

Add --keep-banner to skip step 3 (for example, to test the domain first).
Then commit and push the changed files; Cloudflare redeploys automatically.
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PLACEHOLDER = "https://example.com"

BANNER_RE = re.compile(
    r'(?:<!-- Remove before launch[^>]*-->\s*)?<div class="proto-note" role="note">.*?</div>\s*</div>\s*', re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, help="e.g. https://bestfreeotpnumber.com (no trailing slash)")
    ap.add_argument("--keep-banner", action="store_true")
    args = ap.parse_args()
    domain = args.domain.rstrip("/")
    if not domain.startswith("https://"):
        raise SystemExit("Domain must start with https://")

    changed = 0
    for path in list(SITE.rglob("*.html")) + [SITE / "sitemap.xml", SITE / "robots.txt"]:
        text = path.read_text(encoding="utf-8")
        new = text.replace(PLACEHOLDER, domain)
        if not args.keep_banner:
            new = BANNER_RE.sub("", new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} files")

    conf_path = ROOT / "data" / "site.json"
    conf = json.loads(conf_path.read_text(encoding="utf-8-sig"))
    conf["domain"] = domain
    conf_path.write_text(json.dumps(conf, indent=2) + "\n", encoding="utf-8")

    if not args.keep_banner:
        data_path = ROOT / "data" / "ranking.json"
        data = data_path.read_text(encoding="utf-8")
        data_path.write_text(data.replace('"sample_data": true', '"sample_data": false'), encoding="utf-8")

    headers = SITE / "_headers"
    lines = headers.read_text(encoding="utf-8").splitlines(keepends=True)
    headers.write_text("".join(l for l in lines if "X-Robots-Tag" not in l), encoding="utf-8")
    print("Removed X-Robots-Tag: noindex from site/_headers")
    leftovers = [str(p.relative_to(ROOT)) for p in SITE.rglob("*.html")
                 if 'data-domain="example.com"' in p.read_text(encoding="utf-8")]
    if leftovers:
        print("WARNING: placeholder email addresses (…@example.com) are still in:", ", ".join(leftovers))
    print("Done. Commit and push; then submit sitemap.xml in Google Search Console.")


if __name__ == "__main__":
    main()
