# ============================================================
# generate-logo-assets.ps1
# 从项目根目录的 logo.png 生成站点品牌图标资源：
#   - static/img/logo.png     导航栏 Logo（128x128，4 倍超采样保证清晰）
#   - static/img/favicon.ico  浏览器标签/任务栏图标（多尺寸）
# 同一个 favicon.ico 也会被 rebuild-launcher.bat 嵌入启动器 exe。
# 用法：替换根目录 logo.png 后，运行本脚本即可全部重新生成。
# ============================================================

param(
    [string]$Source = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\logo.png')),
    [string]$OutDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\static\img'))
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

if (-not (Test-Path $Source)) {
    Write-Error "未找到源图片：$Source"
    exit 1
}
if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

# 逐级减半再缩放到目标尺寸，避免一次性大幅缩小导致的画质损失
function New-ResizedBitmap {
    param([System.Drawing.Image]$Src, [int]$Size)
    $cur = $Src
    $tmp = New-Object System.Collections.Generic.List[System.Drawing.Bitmap]
    while ($cur.Width -gt $Size * 2) {
        $half = [Math]::Max($Size, [int]($cur.Width / 2))
        $bmp = New-Object System.Drawing.Bitmap($half, $half)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
        $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $g.DrawImage($cur, 0, 0, $half, $half)
        $g.Dispose()
        $tmp.Add($bmp)
        $cur = $bmp
    }
    $final = New-Object System.Drawing.Bitmap($Size, $Size)
    $g2 = [System.Drawing.Graphics]::FromImage($final)
    $g2.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g2.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g2.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g2.DrawImage($cur, 0, 0, $Size, $Size)
    $g2.Dispose()
    foreach ($b in $tmp) { $b.Dispose() }
    return ,$final
}

# 把多张 PNG 打包为 ICO 容器（PNG 帧，Vista+ 系统与现代浏览器均支持）
function New-Ico {
    param([string[]]$PngPaths, [string]$OutPath)
    $frames = New-Object System.Collections.Generic.List[object]
    foreach ($p in $PngPaths) {
        $bytes = [System.IO.File]::ReadAllBytes($p)
        $img = [System.Drawing.Image]::FromFile($p)
        $frames.Add(@{ Bytes = $bytes; Width = $img.Width; Height = $img.Height })
        $img.Dispose()
    }
    $ms = New-Object System.IO.MemoryStream
    $bw = New-Object System.IO.BinaryWriter($ms)
    $bw.Write([UInt16]0)
    $bw.Write([UInt16]1)
    $bw.Write([UInt16]$frames.Count)
    $offset = 6 + 16 * $frames.Count
    foreach ($f in $frames) {
        $w = if ($f.Width -ge 256) { 0 } else { $f.Width }
        $h = if ($f.Height -ge 256) { 0 } else { $f.Height }
        $bw.Write([Byte]$w)
        $bw.Write([Byte]$h)
        $bw.Write([Byte]0)
        $bw.Write([Byte]0)
        $bw.Write([UInt16]1)
        $bw.Write([UInt16]32)
        $bw.Write([UInt32]$f.Bytes.Length)
        $bw.Write([UInt32]$offset)
        $offset += $f.Bytes.Length
    }
    foreach ($f in $frames) { $bw.Write($f.Bytes) }
    $bw.Flush()
    [System.IO.File]::WriteAllBytes($OutPath, $ms.ToArray())
    $bw.Close()
    $ms.Dispose()
}

$src = [System.Drawing.Image]::FromFile($Source)
Write-Host ("源图片：{0}x{1}" -f $src.Width, $src.Height)

# 1. 导航栏 Logo
$logoBmp = New-ResizedBitmap -Src $src -Size 128
$logoBmp.Save((Join-Path $OutDir 'logo.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$logoBmp.Dispose()
Write-Host "已生成 static/img/logo.png（导航栏 Logo，128x128）"

# 2. Favicon 多尺寸 ICO（只生成不超过源图尺寸的档位）
$sizes = @(16, 32, 48, 64, 128, 256) | Where-Object { $_ -le $src.Width }
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("fde-logo-" + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempDir | Out-Null
$pngs = @()
foreach ($s in $sizes) {
    $p = Join-Path $tempDir ("icon-{0}.png" -f $s)
    $b = New-ResizedBitmap -Src $src -Size $s
    $b.Save($p, [System.Drawing.Imaging.ImageFormat]::Png)
    $b.Dispose()
    $pngs += $p
}
New-Ico -PngPaths $pngs -OutPath (Join-Path $OutDir 'favicon.ico')
Write-Host ("已生成 static/img/favicon.ico（包含尺寸：{0}）" -f ($sizes -join ', '))
Remove-Item -Recurse -Force $tempDir

$src.Dispose()
Write-Host "完成。重启开发服务器（或重新双击 FDE一键启动.exe）后生效。"
