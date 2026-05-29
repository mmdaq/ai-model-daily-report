# 注册 Windows 任务计划：每天 8:00 自动发送，错过则开机后补发
$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatPath = Join-Path $ProjectDir "静默发送.bat"
$TaskName = "AI模型日报自动发送"

if (-not (Test-Path $BatPath)) {
    Write-Host "错误：找不到 $BatPath" -ForegroundColor Red
    exit 1
}

# 删除旧任务（如存在）
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute $BatPath -WorkingDirectory $ProjectDir

# 每天 8:00 触发
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"

# 错过 8:00 时，电脑开机后尽快补跑；笔记本接电源时也运行
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# 当前用户登录时运行（无需管理员）
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "每天自动采集 AI 模型信息并发送 QQ 邮箱日报" | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  定时任务注册成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "任务名称: $TaskName"
Write-Host "执行时间: 每天 08:00"
Write-Host "补发机制: 若 8 点电脑未开机，开机后自动补发"
Write-Host "日志目录: $ProjectDir\logs\"
Write-Host ""
Write-Host "无需再开「定时守护.bat」，可以关闭那个窗口。"
Write-Host ""
Write-Host "管理任务: Win+R 输入 taskschd.msc 可查看/修改"
Write-Host ""
