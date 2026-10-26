# Starts the dedicated Chrome (if it isn't already running), claims the free
# games with `claimer.py --attach`, then closes the Chrome it started.
# Run it by hand or from Task Scheduler. See README.

$here = $PSScriptRoot
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$port = 9222

function Test-DebugPort {
    try {
        Invoke-WebRequest -UseBasicParsing "http://localhost:$port/json/version" -TimeoutSec 2 | Out-Null
        return $true
    } catch {
        return $false
    }
}

$started = $null
if (-not (Test-DebugPort)) {
    $started = Start-Process $chrome -PassThru -ArgumentList `
        "--remote-debugging-port=$port", `
        "--user-data-dir=$here\chrome-profile", `
        "https://store.epicgames.com/en-US/free-games"
    for ($i = 0; $i -lt 30 -and -not (Test-DebugPort); $i++) { Start-Sleep -Seconds 1 }
}

Set-Location $here
python claimer.py --attach
$code = $LASTEXITCODE

# Only close Chrome if we opened it (closing gracefully so the login is saved)
if ($started -and -not $started.HasExited) {
    $started.CloseMainWindow() | Out-Null
    if (-not $started.WaitForExit(15000)) { $started.Kill() }
}
exit $code
