# Opens the dedicated Chrome (its own saved profile) on Epic's login page so you
# can sign in by hand. Leave the window open, then run `python claimer.py --attach`.
# See README.

$here = $PSScriptRoot
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) {
    $chrome = "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
}
if (-not (Test-Path $chrome)) {
    Write-Host "Couldn't find Google Chrome. Install it from google.com/chrome first."
    exit 1
}

Start-Process $chrome -ArgumentList `
    "--remote-debugging-port=9222", `
    "--user-data-dir=$here\chrome-profile", `
    "https://www.epicgames.com/id/login"

Write-Host "Chrome opened. Sign in to Epic in that window (including 2FA)."
Write-Host "Leave it open, then run:  python claimer.py --attach"
