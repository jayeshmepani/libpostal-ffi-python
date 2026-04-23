#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$DIR")"
TARGET="windows-x64"

echo "Building for $TARGET"
cd "$DIR"
if [ ! -d "libpostal" ]; then
    git clone https://github.com/openvenues/libpostal.git
fi
cd libpostal
cp -rf windows/* ./
./bootstrap.sh
./configure --disable-data-download
make -j4

mkdir -p "$ROOT_DIR/postalkit/libs/$TARGET"
cp src/.libs/libpostal-1.dll "$ROOT_DIR/postalkit/libs/$TARGET/postal.dll"
echo "Success: Compiled to $ROOT_DIR/postalkit/libs/$TARGET/postal.dll"
