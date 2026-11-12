<#
  知令产品介绍 · 竖版海报 —— 一键导出脚本（Windows / PowerShell）
  导出：1080x1920 PNG(1x) + 2160x3840 PNG(2x) + A3 竖版单页 PDF

  为什么先复制到临时目录：Chrome 命令行在含中文的路径上偶发异常，
  故先把 HTML 复制到 ASCII 临时目录渲染，再把产物拷回交付目录（文件名仍为中文）。

  用法（PowerShell，cwd 任意）：
    pwsh -File "D:\work\zhilingdoc\知令产品介绍-海报\_scripts\export_poster.ps1"

  依赖：Google Chrome（默认 C:\Program Files\Google\Chrome\Application\chrome.exe）
#>
param(
  [string]$Source = "D:\work\zhilingdoc\知令产品介绍-海报\知令产品介绍-海报.html",
  [string]$OutDir = "D:\work\zhilingdoc\知令产品介绍-海报",
  [string]$Chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path $Chrome)) { throw "未找到 Chrome：$Chrome" }
if (-not (Test-Path $Source)) { throw "未找到源 HTML：$Source" }

$tmp = Join-Path $env:TEMP ("zl_poster_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null
$html = Join-Path $tmp "poster.html"
Copy-Item $Source $html -Force
$url = "file:///" + ($html -replace '\\', '/')

function Invoke-Shot([string]$outName, [int]$scale, [string]$profileTag) {
  $ud = Join-Path $tmp ("profile_" + $profileTag)
  & $Chrome --headless=new --no-first-run --no-default-browser-check `
      --user-data-dir="$ud" --disable-gpu --hide-scrollbars `
      --default-background-color=00000000 --force-device-scale-factor=$scale `
      --window-size=1080,1920 --screenshot="$tmp\$outName" $url | Out-Null
}

Write-Host "==> 导出 1080x1920 PNG"
Invoke-Shot "p1.png" 1 "p1"
Write-Host "==> 导出 2160x3840 PNG"
Invoke-Shot "p2.png" 2 "p2"
Write-Host "==> 导出 A3 竖版 PDF"
& $Chrome --headless=new --no-first-run --no-default-browser-check `
    --user-data-dir="$tmp\profile_pdf" --disable-gpu --no-pdf-header-footer `
    --print-to-pdf="$tmp\poster.pdf" $url | Out-Null

Copy-Item "$tmp\p1.png" (Join-Path $OutDir "知令产品介绍-海报-1080x1920.png") -Force
Copy-Item "$tmp\p2.png" (Join-Path $OutDir "知令产品介绍-海报-2160x3840.png") -Force
Copy-Item "$tmp\poster.pdf" (Join-Path $OutDir "知令产品介绍-海报-A3.pdf") -Force
Remove-Item $tmp -Recurse -Force

Write-Host "==> 完成，产物已写入：$OutDir"
Get-ChildItem $OutDir -File | Select-Object Name, Length | Format-Table -AutoSize
