$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatPath = Join-Path $ProjectDir "send_silent.bat"
$TaskName = "AI_Model_Daily_Report"

if (-not (Test-Path $BatPath)) {
    Write-Host "ERROR: batch file not found: $BatPath"
    exit 1
}

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute $BatPath -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "AI model daily report email" | Out-Null

Write-Host "OK: Scheduled task registered: $TaskName"
Write-Host "Time: daily 08:00, catch-up on boot if missed"
Write-Host "Logs: $ProjectDir\logs\"
