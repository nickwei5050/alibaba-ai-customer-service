# STARGO Alibaba Inquiry AI Assistant — Windows 一键安装
# 用法（在项目根目录 PowerShell 里）：
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
#
# 做的事：建虚拟环境 -> 装依赖 -> 下载浏览器 -> 生成 config.yaml / .env -> 打印下一步。
# 不会覆盖你已存在的 config.yaml / .env。

$ErrorActionPreference = "Stop"

# 切到项目根目录（脚本在 scripts\ 下）
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "项目目录: $root" -ForegroundColor Cyan

# 1) 找 Python
$py = $null
foreach ($c in @("py", "python")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) {
    Write-Host "未找到 Python。请先安装 Python 3.10+：https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
Write-Host "使用 Python 命令: $py" -ForegroundColor Green

# 2) 创建虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host "创建虚拟环境 .venv ..." -ForegroundColor Cyan
    & $py -m venv .venv
}
$pyexe = Join-Path $root ".venv\Scripts\python.exe"

# 3) 装依赖
Write-Host "安装依赖 (requirements.txt) ..." -ForegroundColor Cyan
& $pyexe -m pip install --upgrade pip
& $pyexe -m pip install -r requirements.txt

# 4) 下载 Chromium 浏览器
Write-Host "下载 Chromium 浏览器 ..." -ForegroundColor Cyan
& $pyexe -m playwright install chromium

# 5) 生成 config.yaml / .env（存在则跳过）
if (-not (Test-Path "config\config.yaml")) {
    Copy-Item "config\config.example.yaml" "config\config.yaml"
    Write-Host "已生成 config\config.yaml" -ForegroundColor Green
} else {
    Write-Host "config\config.yaml 已存在，跳过" -ForegroundColor Yellow
}
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "已生成 .env" -ForegroundColor Green
} else {
    Write-Host ".env 已存在，跳过" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ 安装完成。接下来：" -ForegroundColor Green
Write-Host "  1) 编辑 .env，填 EMAIL_USER / EMAIL_PASSWORD(授权码) / NOTION_API_KEY / 微信Key"
Write-Host "  2) 激活环境：  .\.venv\Scripts\Activate.ps1"
Write-Host "  3) 测微信：    python -m src.stargo.cli notify-test"
Write-Host "  4) 同步知识库：python -m src.stargo.cli kb-sync"
Write-Host "  5) 看邮件：    python -m src.stargo.cli mail-check"
Write-Host "  6) 调试页面：  python -m src.stargo.cli debug-url ""真实Alibaba链接"""
Write-Host "  7) 干跑全链路：python -m src.stargo.cli run-once --dry-run"
