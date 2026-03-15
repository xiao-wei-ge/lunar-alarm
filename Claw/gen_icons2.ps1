Add-Type -AssemblyName System.Drawing

$outDir = "C:\Users\lin\WorkBuddy\Claw\icons"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$sizes = @(72, 96, 128, 144, 152, 192, 384, 512)

function Draw-Icon([int]$s) {
    $bmp = New-Object System.Drawing.Bitmap($s, $s)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias

    # Rounded background
    $corner = [int]($s * 0.2)
    $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
    $gp.AddArc(0, 0, $corner*2, $corner*2, 180, 90)
    $gp.AddArc($s-$corner*2, 0, $corner*2, $corner*2, 270, 90)
    $gp.AddArc($s-$corner*2, $s-$corner*2, $corner*2, $corner*2, 0, 90)
    $gp.AddArc(0, $s-$corner*2, $corner*2, $corner*2, 90, 90)
    $gp.CloseFigure()
    $bgBr = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 15, 6, 0))
    $g.FillPath($bgBr, $gp)

    [int]$cx = $s / 2
    [int]$cy = $s / 2
    [int]$lw = $s * 0.46
    [int]$lh = $s * 0.54
    [int]$lx = $cx - $lw / 2
    [int]$ly = $cy - $lh / 2

    # Lantern gradient - use SolidBrush for reliability
    $lgb = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 192, 57, 43))
    $g.FillEllipse($lgb, $lx, $ly, $lw, $lh)
    # Highlight
    $hlBr = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60, 255, 100, 80))
    [int]$hlW = $lw / 2
    [int]$hlH = $lh / 2
    $g.FillEllipse($hlBr, $lx, $ly, $hlW, $hlH)

    # Gold border
    [int]$penW = [Math]::Max(2, [int]($s * 0.022))
    $goldPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 212, 160, 23), $penW)
    $g.DrawEllipse($goldPen, $lx, $ly, $lw, $lh)

    # Top and bottom caps
    [int]$capW = $lw * 0.6
    [int]$capH = [Math]::Max(3, [int]($s * 0.07))
    [int]$capX = $cx - $capW / 2
    $goldBr = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 212, 160, 23))
    $g.FillRectangle($goldBr, $capX, $ly - $capH, $capW, $capH)
    $g.FillRectangle($goldBr, $capX, $ly + $lh, $capW, $capH)

    # Vertical stripes
    [int]$stripePenW = [Math]::Max(1, [int]($s * 0.01))
    $stripePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(100, 212, 160, 23), $stripePenW)
    for ($i = -2; $i -le 2; $i++) {
        [int]$px = $cx + $i * ($lw / 5)
        $ratio = [Math]::Abs(($px - $cx) / ($lw / 2.0))
        if ($ratio -lt 0.98) {
            [int]$halfH = [Math]::Sqrt(1 - $ratio * $ratio) * ($lh / 2.0)
            $g.DrawLine($stripePen, $px, $cy - $halfH, $px, $cy + $halfH)
        }
    }

    # Chinese char
    [int]$fsize = [Math]::Max(8, [int]($s * 0.26))
    try   { $fnt = New-Object System.Drawing.Font("SimSun", $fsize, [System.Drawing.FontStyle]::Bold) }
    catch { $fnt = New-Object System.Drawing.Font("Arial",  $fsize, [System.Drawing.FontStyle]::Bold) }
    $txtBr = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 224, 102))
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment     = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
    $charStr = [char]0x519C  # Unicode for char
    $g.DrawString($charStr, $fnt, $txtBr, (New-Object System.Drawing.RectangleF(0, 0, $s, $s)), $sf)

    # Tassels
    if ($s -ge 96) {
        [int]$tasselY = $ly + $lh + $capH
        [int]$tasselL = [int]($s * 0.09)
        $tasselPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(200, 212, 160, 23), [Math]::Max(1,[int]($s*0.012)))
        $offsets = @(-0.25, -0.12, 0, 0.12, 0.25)
        foreach ($off in $offsets) {
            [int]$tx = $cx + [int]($lw * $off)
            $g.DrawLine($tasselPen, $tx, $tasselY, $tx, $tasselY + $tasselL)
        }
    }

    $g.Dispose()
    return $bmp
}

foreach ($s in $sizes) {
    $bmp = Draw-Icon $s
    $outPath = $outDir + "\icon-" + $s + ".png"
    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Host ("Saved: " + $outPath)
}

Write-Host "All icons done!"
