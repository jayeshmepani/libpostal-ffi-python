#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$OS" == *"linux"* ]]; then
    bash "$DIR/compile-linux.sh"
elif [[ "$OS" == *"darwin"* ]]; then
    bash "$DIR/compile-macos.sh"
else
    echo "Unsupported OS. Use compile-windows.ps1 for Windows."
    exit 1
fi
