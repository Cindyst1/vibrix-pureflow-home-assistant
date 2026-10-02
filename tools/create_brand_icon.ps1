Add-Type -AssemblyName System.Drawing

$outputPath = Join-Path $PSScriptRoot `
    '..\custom_components\vibrix_pureflow\brand\icon.png'
$outputDirectory = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null

$bitmap = [System.Drawing.Bitmap]::new(256, 256)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.Clear([System.Drawing.Color]::Transparent)

$backgroundBrush = [System.Drawing.SolidBrush]::new(
    [System.Drawing.Color]::FromArgb(255, 25, 125, 145)
)
$graphics.FillEllipse($backgroundBrush, 8, 8, 240, 240)

function New-RoundedRectanglePath {
    param(
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius
    )

    $diameter = $Radius * 2
    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $path.AddArc($X, $Y, $diameter, $diameter, 180, 90)
    $path.AddArc($X + $Width - $diameter, $Y, $diameter, $diameter, 270, 90)
    $path.AddArc(
        $X + $Width - $diameter,
        $Y + $Height - $diameter,
        $diameter,
        $diameter,
        0,
        90
    )
    $path.AddArc($X, $Y + $Height - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()
    return $path
}

$purifierPath = New-RoundedRectanglePath 55 30 146 196 28
$purifierBrush = [System.Drawing.SolidBrush]::new(
    [System.Drawing.Color]::FromArgb(255, 247, 252, 252)
)
$outlinePen = [System.Drawing.Pen]::new(
    [System.Drawing.Color]::FromArgb(255, 18, 54, 67),
    8
)
$graphics.FillPath($purifierBrush, $purifierPath)
$graphics.DrawPath($outlinePen, $purifierPath)

$ventPen = [System.Drawing.Pen]::new(
    [System.Drawing.Color]::FromArgb(255, 18, 54, 67),
    6
)
$ventPen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$ventPen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
foreach ($yPosition in @(58, 74, 90)) {
    $graphics.DrawLine($ventPen, 89, $yPosition, 167, $yPosition)
}

$airPen = [System.Drawing.Pen]::new(
    [System.Drawing.Color]::FromArgb(255, 37, 170, 190),
    8
)
$airPen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$airPen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
foreach ($xPosition in @(101, 128, 155)) {
    $airPath = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $airPath.AddBezier(
        $xPosition - 10,
        128,
        $xPosition + 15,
        142,
        $xPosition - 15,
        160,
        $xPosition + 10,
        176
    )
    $graphics.DrawPath($airPen, $airPath)
    $airPath.Dispose()
}

$indicatorBrush = [System.Drawing.SolidBrush]::new(
    [System.Drawing.Color]::FromArgb(255, 37, 170, 190)
)
$graphics.FillEllipse($indicatorBrush, 120, 197, 16, 16)

$bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)

$indicatorBrush.Dispose()
$airPen.Dispose()
$ventPen.Dispose()
$outlinePen.Dispose()
$purifierBrush.Dispose()
$purifierPath.Dispose()
$backgroundBrush.Dispose()
$graphics.Dispose()
$bitmap.Dispose()
