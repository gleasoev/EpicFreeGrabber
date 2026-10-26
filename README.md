# Epic Free Grabber

Claims the weekly free games on the Epic Games Store for your account.

## Setup (once)

1. Install Python 3.10+ from python.org. During install, check "Add Python to PATH".
2. Install Google Chrome.
3. Open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   playwright install chromium
   ```

## Use

```
python claimer.py --dry-run   # see what's free
```

### Recommended: sign in yourself, then attach (`--attach`)

Epic and Google block logins inside an automated browser. So you sign in by hand in a
normal Chrome window, and the script then drives that same window.

1. Start a dedicated Chrome (its own profile, with a control port):
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\path\to\EpicFreeGrabber\chrome-profile
   ```
2. In that window, log in to Epic yourself, including any security check and 2FA.
   The login is saved in `chrome-profile`, so you only repeat this when the session expires.
3. In a terminal, run:
   ```
   python claimer.py --attach
   ```

If a CAPTCHA appears, solve it in the window. You have 5 minutes.

### Alternative: let the script open its own browser

```
python claimer.py --login     # sign in once; session saved in ./profile
python claimer.py             # claim
```

This often fails at the login step because of Epic's bot checks.

## Run it automatically (Windows)

`run_weekly.ps1` starts the dedicated Chrome if needed, runs `claimer.py --attach`, and
closes the Chrome it started. Do steps 1-2 above once first so the login is saved, then
create a weekly task (Epic rotates games Thursdays at 11 AM Eastern; set your local time):

```
schtasks /Create /TN "EpicFreeGrabber" /SC WEEKLY /D THU /ST 11:30 /TR "powershell -NoProfile -ExecutionPolicy Bypass -File C:\path\to\EpicFreeGrabber\run_weekly.ps1"
```

Limits: the PC must be on and you must be signed in to Windows (Chrome opens visibly),
and nobody is there to solve a CAPTCHA, so that run will fail and you claim by hand.

## Safety

- The script only places an order when the checkout total is verifiably $0.00.
- It only treats a game as claimable when the button says "Get".

## Sharing with friends

- Share the code but **never the `profile` or `chrome-profile` folders**, because they contain
  your logged-in session. Both are in `.gitignore`.
- Each person signs in with their own account.
- Automating the store is against Epic's terms of service. Use at your own risk.
- Epic sometimes changes its website. If the script can't find a button, the selectors in
  `claimer.py` (`CTA_NAME`, `Place Order`, etc.) are what need updating.
