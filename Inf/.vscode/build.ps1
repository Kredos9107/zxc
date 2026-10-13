# Builds the active C++ file with g++, wherever MinGW is installed on this PC.
# Called from tasks.json:  build.ps1 <source.cpp> <output.exe>
param([string]$src, [string]$out)

$log = Join-Path $PSScriptRoot 'last-build.log'
"$(Get-Date)  src=$src  out=$out" | Out-File $log -Encoding utf8
"PATH=$env:Path" | Out-File $log -Append -Encoding utf8

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
    'g++ NOT FOUND' | Out-File $log -Append -Encoding utf8
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
"compiler: $gpp" | Out-File $log -Append -Encoding utf8
# g++/ld mangle non-ASCII paths (like the Cyrillic user folder) when run
# from VS Code, so build from the source folder with bare file names.
Set-Location (Split-Path -Parent $src)
$res = & $gpp -g -static (Split-Path -Leaf $src) -o (Split-Path -Leaf $out) 2>&1
$code = $LASTEXITCODE
$res | ForEach-Object { "$_" } | Tee-Object -FilePath $log -Append | Write-Host
"exit=$code" | Out-File $log -Append -Encoding utf8
exit $code
