#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$DIR")"

ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then
    TARGET="linux-x64"
else
    TARGET="linux-arm64"
fi

echo "Building for $TARGET"
cd "$DIR"
if [ ! -d "libpostal" ]; then
    git clone https://github.com/openvenues/libpostal.git
fi
cd libpostal
./bootstrap.sh
./configure --disable-data-download
make -j4

mkdir -p "$ROOT_DIR/postalkit/libs/$TARGET"
cp src/.libs/libpostal.so "$ROOT_DIR/postalkit/libs/$TARGET/"
echo "Success: Compiled to $ROOT_DIR/postalkit/libs/$TARGET/libpostal.so"
