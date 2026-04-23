$ErrorActionPreference = "Stop"
$DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ROOT_DIR = Split-Path -Parent $DIR
$TARGET = "windows-x64"

Write-Host "Building for $TARGET"
Set-Location $DIR
if (-not (Test-Path "libpostal")) {
    git clone https://github.com/openvenues/libpostal.git
}
Set-Location "libpostal"
Copy-Item -Recurse -Force windows\* .\
bash ./bootstrap.sh
bash ./configure --disable-data-download
make -j4

$TARGET_DIR = "$ROOT_DIR\postalkit\libs\$TARGET"
if (-not (Test-Path $TARGET_DIR)) {
    New-Item -ItemType Directory -Force -Path $TARGET_DIR
}
Copy-Item src\.libs\libpostal-1.dll "$TARGET_DIR\postal.dll" -Force
Write-Host "Success: Compiled to $TARGET_DIR\postal.dll"
