# Epic Free Grabber

Claims the weekly free games on the Epic Games Store for your Epic account (Windows).

Epic and Google block logins inside an automated browser, so this works differently:
**you sign in yourself in a normal Chrome window, and the script then clicks through the
claim in that same window.**

## What you need

- Windows 10 or 11
- [Python 3.10+](https://www.python.org/downloads/). During install, tick **"Add Python to PATH"**.
- [Google Chrome](https://www.google.com/chrome/)
- An Epic account with **2FA turned on** (epicgames.com → Account → Password & Security).
  Epic requires 2FA before it lets you claim free games.

## Install (once)

1. Get the code: click **Code → Download ZIP** on GitHub and unzip it, or run
   `git clone https://github.com/gleasoev/EpicFreeGrabber.git`.
2. Open **PowerShell** in that folder (in File Explorer: click the address bar, type
   `powershell`, press Enter) and run:
   ```
   pip install -r requirements.txt
   ```
3. Check it can see this week's free games:
   ```
   python claimer.py --dry-run
   ```
   You should see a line like `Free this week: ...`. This step buys nothing.

## Sign in (once, and again if your session expires)

1. In the same PowerShell window, run:
   ```
   powershell -ExecutionPolicy Bypass -File .\sign_in.ps1
   ```
2. A Chrome window opens on Epic's login page. **Sign in yourself**, including any security
   check and 2FA. Your Google or email login both work here.
3. Confirm you're signed in (go to store.epicgames.com and look for your name).
   Your login is saved in the `chrome-profile` folder. Your password is never stored.
4. You can close that Chrome window with its normal X button.

## Claim the free games

```
powershell -ExecutionPolicy Bypass -File .\run_weekly.ps1
```

This opens the dedicated Chrome, claims every free game you don't own yet, prints a
summary (`claimed`, `owned`, `skipped`, `aborted`, `failed`), and closes Chrome.
If a CAPTCHA appears, solve it in the window. You have 5 minutes.

Always confirm in your Epic library that new games arrived.

## Run it automatically every week

Epic switches games on Thursdays at 11 AM Eastern. In PowerShell, in this folder, run the
command below after replacing `C:\path\to\EpicFreeGrabber` with this folder's full path
(run `pwd` to see it) and `11:30` with a time shortly after 11 AM in your time zone.
If the path has spaces, ask for help rather than guessing.

```
schtasks /Create /TN "EpicFreeGrabber" /SC WEEKLY /D THU /ST 11:30 /TR "powershell -NoProfile -ExecutionPolicy Bypass -File C:\path\to\EpicFreeGrabber\run_weekly.ps1"
```

Then open **Task Scheduler → EpicFreeGrabber → Properties → Settings** and tick
"Run task as soon as possible after a scheduled start is missed".

Limits of the automatic run:
- The PC must be on and you must be signed in to Windows (Chrome opens visibly).
- Nobody is there to solve a CAPTCHA, so that run fails and you claim by hand.
- If your Epic session expires, repeat **Sign in** above.

## Troubleshooting

| Problem | What to do |
|---|---|
| `Couldn't connect to Chrome at http://localhost:9222` | Run `sign_in.ps1` first, or use `run_weekly.ps1`, which starts Chrome for you. |
| `Couldn't find the Get button` or `Couldn't find Place Order` | Epic changed its page. The selectors in `claimer.py` (`CTA_NAME`, `Place Order`) need updating. |
| `Checkout total isn't verifiably $0 - NOT placing the order` | The safety check refused. Claim that game by hand and report the issue. |
| Sign-in page is blank or loops | Make sure you're using the `sign_in.ps1` window, not another browser. Try again later. |
| `python` is not recognized | Reinstall Python and tick "Add Python to PATH". |

## Safety and sharing

- The script only places an order when the checkout total is verifiably **$0.00**, and only
  for games whose button says "Get".
- **Never share or upload the `chrome-profile` or `profile` folders.** They contain your
  logged-in session. Both are in `.gitignore`.
- Each person signs in with their own account.
- Automating the store is against Epic's terms of service. Use at your own risk.

## Other options

`python claimer.py --login` then `python claimer.py` lets the script open its own browser.
This usually fails at login because of Epic's bot checks, so the steps above are preferred.
