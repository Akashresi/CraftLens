# CraftLens 2.0 - PowerShell Single Command Launcher
param(
    [switch]$Admin,
    [switch]$Mobile
)

$argsList = @()
if ($Admin) { $argsList += "--admin" }
if ($Mobile) { $argsList += "--mobile" }

python "$PSScriptRoot\run.py" @argsList

