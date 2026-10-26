"""
Epic Free Grabber - claims this week's free Epic Games Store games.

Usage:
  python claimer.py --login     # first time: log in by hand, session is saved
  python claimer.py             # claim any free games you don't own yet
  python claimer.py --dry-run   # just list the free games, don't claim

Your password is never stored. You log in yourself once in the browser window,
and Playwright keeps the session in the ./profile folder (keep that folder private).
"""

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

FEED_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    "?locale=en-US&country=US&allowCountries=US"
)
STORE_URL = "https://store.epicgames.com/en-US/p/{slug}"
LOGIN_URL = "https://www.epicgames.com/id/login"
PROFILE_DIR = Path(__file__).parent / "profile"
CAPTCHA_WAIT_SECONDS = 300  # how long to wait for you to solve a CAPTCHA


# ---------- 1. Find the free games ----------

def get_free_games():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)

    now = datetime.now(timezone.utc)
    games = []
    for el in data["data"]["Catalog"]["searchStore"]["elements"]:
        if el.get("price", {}).get("totalPrice", {}).get("discountPrice") != 0:
            continue
        promos = (el.get("promotions") or {}).get("promotionalOffers") or []
        active = False
        for group in promos:
            for offer in group.get("promotionalOffers", []):
                start = datetime.fromisoformat(offer["startDate"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))
                if start <= now <= end:
                    active = True
        if not active:
            continue

        slug = find_slug(el)
        if slug:
            games.append({"title": el["title"], "slug": slug})
    return games


def find_slug(el):
    for m in (el.get("catalogNs") or {}).get("mappings") or []:
        if m.get("pageSlug"):
            return m["pageSlug"]
    for m in el.get("offerMappings") or []:
        if m.get("pageSlug"):
            return m["pageSlug"]
    slug = el.get("productSlug") or el.get("urlSlug")
    if slug and slug not in ("[]", "mystery-game"):
        return slug.replace("/home", "")
    return None


# ---------- 2. Browser helpers ----------

def open_browser(p):
    return p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,  # Epic is much more likely to block a hidden browser
        viewport={"width": 1280, "height": 900},
    )


def captcha_visible(page):
    for frame in page.frames:
        url = frame.url or ""
        if "hcaptcha" in url or "talon" in url or "captcha" in url:
            return True
    return False


def wait_for_human_if_captcha(page):
    if not captcha_visible(page):
        return
    print("  CAPTCHA showed up - solve it in the browser window...")
    deadline = time.time() + CAPTCHA_WAIT_SECONDS
    while time.time() < deadline:
        time.sleep(2)
        if not captcha_visible(page):
            print("  CAPTCHA cleared, continuing.")
            return
    raise RuntimeError("CAPTCHA wasn't solved in time")


def click_if_present(locator, timeout=3000):
    try:
        locator.first.click(timeout=timeout)
        return True
    except PWTimeout:
        return False


# ---------- 3. Claim one game ----------

def claim(page, game):
    print(f"- {game['title']}")
    page.goto(STORE_URL.format(slug=game["slug"]), wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Some games have an age check before the store page
    click_if_present(page.get_by_role("button", name="Continue"))

    cta = page.locator('[data-testid="purchase-cta-button"]')
    try:
        cta.wait_for(timeout=15000)
    except PWTimeout:
        print("  Couldn't find the Get button (page layout may have changed).")
        return "failed"

    label = (cta.inner_text() or "").strip().lower()
    if "library" in label or "owned" in label:
        print("  Already in your library.")
        return "owned"
    if "get" not in label:
        print(f"  Button says '{label}', skipping.")
        return "skipped"

    cta.click()
    page.wait_for_timeout(3000)
    wait_for_human_if_captcha(page)

    # Checkout happens inside an iframe
    checkout = page.frame_locator("#webPurchaseContainer iframe")
    if not click_if_present(checkout.get_by_role("button", name="Place Order"), timeout=20000):
        print("  Couldn't find Place Order.")
        return "failed"

    page.wait_for_timeout(2000)
    # Some regions show a refund-policy prompt
    click_if_present(checkout.get_by_role("button", name="I Accept"))
    wait_for_human_if_captcha(page)

    try:
        page.get_by_text("Thanks for your order", exact=False).wait_for(timeout=20000)
        print("  Claimed!")
        return "claimed"
    except PWTimeout:
        # Fall back to re-checking the button
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        label = (page.locator('[data-testid="purchase-cta-button"]').inner_text() or "").lower()
        if "library" in label or "owned" in label:
            print("  Claimed!")
            return "claimed"
        print("  Not sure it worked - check your library.")
        return "unknown"


# ---------- 4. Main ----------

def do_login():
    with sync_playwright() as p:
        ctx = open_browser(p)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(LOGIN_URL)
        input("Log in to Epic in the browser window, then press Enter here...")
        ctx.close()
    print("Session saved to ./profile")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", action="store_true", help="log in and save the session")
    ap.add_argument("--dry-run", action="store_true", help="list free games only")
    args = ap.parse_args()

    if args.login:
        do_login()
        return

    games = get_free_games()
    if not games:
        print("No free games found right now.")
        return
    print("Free this week:", ", ".join(g["title"] for g in games))
    if args.dry_run:
        return

    if not PROFILE_DIR.exists():
        print("No saved login yet. Run: python claimer.py --login")
        sys.exit(1)

    results = {}
    with sync_playwright() as p:
        ctx = open_browser(p)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for g in games:
            try:
                results[g["title"]] = claim(page, g)
            except Exception as e:
                print(f"  Error: {e}")
                results[g["title"]] = "failed"
        ctx.close()

    print("\nSummary:")
    for title, status in results.items():
        print(f"  {status:8} {title}")


if __name__ == "__main__":
    main()
