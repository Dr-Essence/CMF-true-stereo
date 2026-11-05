#!/bin/sh
# Assembles the HAL patch (library loader, fallback swap), runs it in an ARM64 emulator against
# test buffers (harness.c), and checks that the bytes channels.sh writes into
# the HAL are exactly what patch.S assembles to at 0x27b820.
# Needs clang, ld.lld, llvm-objcopy and qemu-aarch64; skipped without them.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
for t in clang ld.lld llvm-objcopy qemu-aarch64; do
  command -v "$t" >/dev/null 2>&1 || { echo "  skip - $t not installed"; exit 0; }
done
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
cd "$HERE"
clang --target=aarch64-linux-gnu -c patch.S -o "$T/patch.o" || exit 1
ld.lld -T link.ld "$T/patch.o" -o "$T/patch.elf" 2>/dev/null || exit 1
llvm-objcopy -O binary --only-section=.text "$T/patch.elf" "$T/patch.bin" || exit 1
clang --target=aarch64-linux-gnu -ffreestanding -nostdlib -static -fno-stack-protector \
  -O1 -fuse-ld=lld harness.c patch.S tramp.S -o "$T/harness" 2>/dev/null || exit 1
qemu-aarch64 "$T/harness" || exit 1
# The module's copy of the bytes, written the way the module writes them.
_body=$(sed -n "s/^HAL_SWAP_BODY='\(.*\)'$/\1/p" ../scripts/channels.sh)
printf "$_body" > "$T/module.bin"
if cmp -s "$T/patch.bin" "$T/module.bin"; then
  echo "  ok   - channels.sh carries exactly the assembled patch ($(wc -c < "$T/patch.bin" | tr -d ' ') bytes)"
else
  echo "  FAIL - channels.sh bytes differ from patch.S"; exit 1
fi
[ "$(wc -c < "$T/patch.bin")" -le 432 ] || { echo "  FAIL - patch overruns the 432 stock bytes channels.sh restores"; exit 1; }
# The branch at 0x2587c0 must land on rotcave as assembled.
_rot=$(llvm-nm "$T/patch.elf" | awk '$3 == "rotcave" { print $1 }')
_ins=$(( 0x14000000 | (((0x$_rot - 0x2587c0) / 4) & 0x3ffffff) ))
_want=$(printf '\\%03o\\%03o\\%03o\\%03o' $((_ins & 255)) $((_ins >> 8 & 255)) $((_ins >> 16 & 255)) $((_ins >> 24 & 255)))
_b=$(sed -n "s/^HAL_SWAP_B='\(.*\)'$/\1/p" ../scripts/channels.sh)
if [ "$_b" = "$_want" ]; then
  echo "  ok   - the setParameters branch lands on rotcave (0x$_rot)"
else
  echo "  FAIL - HAL_SWAP_B is $_b, rotcave needs $_want"; exit 1
fi
