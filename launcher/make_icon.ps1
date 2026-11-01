# Draws the Smart Food Analysis logo (bowl with a leaf) and writes assets\smartfood.ico.
Add-Type -AssemblyName System.Drawing

$root = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Force (Join-Path $root "assets") | Out-Null
$icoPath = Join-Path $root "assets\smartfood.ico"

$images = @()
foreach ($size in 16, 24, 32, 48, 64, 128, 256) {
    $s = [single]$size
    $bmp = New-Object System.Drawing.Bitmap $size, $size
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::Transparent)
    $green = [System.Drawing.ColorTranslator]::FromHtml("#1f8a5b")
    $light = [System.Drawing.ColorTranslator]::FromHtml("#9fe0bd")
    $g.FillEllipse((New-Object System.Drawing.SolidBrush $green), $s * 0.03, $s * 0.03, $s * 0.94, $s * 0.94)

    # Leaf above the bowl
    $leaf = New-Object System.Drawing.Drawing2D.GraphicsPath
    $a = New-Object System.Drawing.PointF ($s * 0.40), ($s * 0.50)
    $b = New-Object System.Drawing.PointF ($s * 0.66), ($s * 0.20)
    $leaf.AddBezier($a, (New-Object System.Drawing.PointF ($s * 0.36), ($s * 0.28)), (New-Object System.Drawing.PointF ($s * 0.52), ($s * 0.18)), $b)
    $leaf.AddBezier($b, (New-Object System.Drawing.PointF ($s * 0.72), ($s * 0.36)), (New-Object System.Drawing.PointF ($s * 0.56), ($s * 0.48)), $a)
    $g.FillPath((New-Object System.Drawing.SolidBrush $light), $leaf)

    # Bowl: lower half of an ellipse
    $bowl = New-Object System.Drawing.Drawing2D.GraphicsPath
    $bowl.AddArc($s * 0.18, $s * 0.30, $s * 0.64, $s * 0.48, 0, 180)
    $bowl.CloseFigure()
    $g.FillPath([System.Drawing.Brushes]::White, $bowl)
    $g.Dispose()

    $stream = New-Object System.IO.MemoryStream
    $bmp.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png)
    $images += , @($size, $stream.ToArray())
    $bmp.Dispose()
}

$out = New-Object System.IO.MemoryStream
$w = New-Object System.IO.BinaryWriter $out
$w.Write([UInt16]0); $w.Write([UInt16]1); $w.Write([UInt16]$images.Count)
$offset = 6 + 16 * $images.Count
foreach ($img in $images) {
    $dim = if ($img[0] -ge 256) { 0 } else { $img[0] }
    $w.Write([byte]$dim); $w.Write([byte]$dim); $w.Write([byte]0); $w.Write([byte]0)
    $w.Write([UInt16]1); $w.Write([UInt16]32)
    $w.Write([UInt32]$img[1].Length); $w.Write([UInt32]$offset)
    $offset += $img[1].Length
}
foreach ($img in $images) { $w.Write($img[1]) }
$w.Flush()
[System.IO.File]::WriteAllBytes($icoPath, $out.ToArray())
Write-Output "Icon written: $icoPath"
