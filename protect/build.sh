#!/bin/sh
# Builds libcmfstereo.so with the Android NDK (r27c) and checks it against the
# copy the module ships. Needs ANDROID_NDK_HOME (or the NDK under the SDK).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
NDK=${ANDROID_NDK_HOME:-/opt/android-sdk/ndk/27.2.12479018}
CC=$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang
[ -x "$CC" ] || { echo "  skip - NDK not found ($NDK)"; exit 0; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
# -ffile-prefix-map and a fixed build id keep the output the same on any machine.
"$CC" -shared -fPIC -O2 -Wall -Wextra -Werror -fvisibility=hidden \
  -ffile-prefix-map="$HERE"=. -Wl,--build-id=none -Wl,-z,max-page-size=16384 \
  -o "$T/libcmfstereo.so" "$HERE/cmfstereo.c" -lm
if [ "${1:-}" = install ]; then cp "$T/libcmfstereo.so" "$HERE/libcmfstereo.so"; echo "  built $(sha256sum "$HERE/libcmfstereo.so" | cut -c1-16)"; exit 0; fi
if cmp -s "$T/libcmfstereo.so" "$HERE/libcmfstereo.so"; then
  echo "  ok   - libcmfstereo.so rebuilds byte for byte from cmfstereo.c"
else
  echo "  FAIL - libcmfstereo.so differs from a fresh build of cmfstereo.c"; exit 1
fi
