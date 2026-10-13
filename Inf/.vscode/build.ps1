# Builds the active C++ file with g++, wherever MinGW is installed on this PC.
# Called from tasks.json:  build.ps1 <source.cpp> <output.exe>
param([string]$src, [string]$out)

$gpp = $null
$cmd = Get-Command g++.exe -ErrorAction SilentlyContinue
if ($cmd) { $gpp = $cmd.Source }

if (-not $gpp) {
    $candidates = @(
        'C:\mingw64\bin',
        'C:\mingw32\bin',
        'C:\MinGW\bin',
        'C:\msys64\ucrt64\bin',
        'C:\msys64\mingw64\bin',
        'C:\msys64\clang64\bin',
        'C:\Program Files\mingw64\bin',
        'C:\Program Files\mingw-w64\*\mingw64\bin',
        'C:\Program Files (x86)\mingw-w64\*\mingw64\bin',
        'C:\Program Files\CodeBlocks\MinGW\bin',
        'C:\Program Files (x86)\CodeBlocks\MinGW\bin',
        'C:\Program Files (x86)\Dev-Cpp\MinGW64\bin',
        'C:\Program Files\JetBrains\CLion*\bin\mingw\bin',
        "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\BrechtSanders.WinLibs*\mingw64\bin",
        "$env:LOCALAPPDATA\Programs\JetBrains\CLion*\bin\mingw\bin",
        'C:\ProgramData\chocolatey\lib\mingw\tools\install\mingw64\bin'
    )
    foreach ($c in $candidates) {
        $found = Get-ChildItem -Path (Join-Path $c 'g++.exe') -ErrorAction SilentlyContinue |
                 Select-Object -First 1
        if ($found) { $gpp = $found.FullName; break }
    }
}

if (-not $gpp) {
    Write-Host ''
    Write-Host '=================================================='
    Write-Host '  g++ NOT FOUND on this computer.'
    Write-Host '  Install MinGW-w64 (e.g. winget install BrechtSanders.WinLibs.POSIX.UCRT)'
    Write-Host '  or add the folder with g++.exe to PATH, then restart VS Code.'
    Write-Host '=================================================='
    exit 1
}

Write-Host "compiler: $gpp"
# -static: the .exe does not need MinGW's DLLs in PATH to start
& $gpp -fdiagnostics-color=always -g -static $src -o $out
exit $LASTEXITCODE
