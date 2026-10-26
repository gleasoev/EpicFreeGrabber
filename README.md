# Epic Free Grabber

Claims the weekly free games on the Epic Games Store for your account.

## Setup (once)

1. Install Python 3.10+ from python.org. During install, check "Add Python to PATH".
2. Open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Log in:
   ```
   python claimer.py --login
   ```
   A browser opens. Log in to Epic yourself, including 2FA, then press Enter in the terminal.
   Your login session is saved in the `profile` folder. Your password is never saved.

## Use

```
python claimer.py --dry-run   # see what's free
python claimer.py             # claim it
```

A browser window opens and clicks through the claim. If a CAPTCHA appears, solve it
in that window and the script continues. You have 5 minutes.

## Run it automatically (Windows)

Open Task Scheduler and choose Create Basic Task. Set it to run weekly on Thursday at 11:30 AM.
For the action, start a program:
- Program: `python`
- Arguments: `claimer.py`
- Start in: the full path to this folder

## Sharing with friends

- Share the code but **never the `profile` folder**, because it contains your logged-in session.
- Each person runs `--login` with their own account.
- Automating the store is against Epic's terms of service. Use at your own risk.
- Epic sometimes changes its website. If the script can't find a button, the selectors in
  `claimer.py` (the `purchase-cta-button`, `Place Order`, etc.) are what need updating.

## .gitignore
If you put this on GitHub, add a `.gitignore` containing:
```
profile/
```
